param(
    [Parameter(Mandatory)][string]$InputPath,
    [Parameter(Mandatory)][string]$OutputDirectory,
    [string]$DrawioExecutable = '',
    [ValidateRange(0.5,4)][double]$Scale = 2,
    [ValidateRange(10,600)][int]$TimeoutSeconds = 120,
    [switch]$Recurse,
    [switch]$Force
)
# Uses the real draw.io Desktop renderer; PNGs retain editable diagram XML.
$ErrorActionPreference = 'Stop'
function Confirm-EditablePng([string]$Path) {
    $bytes = [IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -lt 8 -or [Convert]::ToHexString($bytes[0..7]) -ne '89504E470D0A1A0A') { throw 'Renderer output is not a PNG.' }
    $offset = 8
    while ($offset + 12 -le $bytes.Length) {
        $length = ([uint32]$bytes[$offset] -shl 24) -bor ([uint32]$bytes[$offset+1] -shl 16) -bor ([uint32]$bytes[$offset+2] -shl 8) -bor [uint32]$bytes[$offset+3]
        if ($length -gt $bytes.Length - $offset - 12) { throw 'Renderer output has an invalid PNG chunk.' }
        $type = [Text.Encoding]::ASCII.GetString($bytes,$offset+4,4)
        if ($type -eq 'zTXt') {
            $data = $bytes[($offset+8)..($offset+7+$length)]
            $separator = [Array]::IndexOf($data,[byte]0)
            if ($separator -gt 0 -and [Text.Encoding]::Latin1.GetString($data,0,$separator) -eq 'mxGraphModel') {
                $memory = [IO.MemoryStream]::new([byte[]]$data[($separator+2)..($data.Length-1)])
                $stream = [IO.Compression.ZLibStream]::new($memory,[IO.Compression.CompressionMode]::Decompress)
                $reader = [IO.StreamReader]::new($stream,[Text.Encoding]::UTF8)
                try { [xml]$embedded = [Uri]::UnescapeDataString($reader.ReadToEnd()) }
                finally { $reader.Dispose(); $stream.Dispose(); $memory.Dispose() }
                if ($embedded.DocumentElement.Name -ne 'mxfile' -or -not $embedded.mxfile.diagram) { throw 'Embedded PNG XML contains no editable draw.io diagram.' }
                return
            }
        }
        $offset += $length + 12
    }
    throw 'PNG lacks embedded editable draw.io XML.'
}
if (-not $DrawioExecutable) {
    $command = Get-Command draw.io.exe -CommandType Application -ErrorAction SilentlyContinue
    if ($command) { $DrawioExecutable = $command.Source }
    else {
        $tools = Join-Path $env:LOCALAPPDATA 'DevTools'
        $DrawioExecutable = Get-ChildItem -LiteralPath $tools -Directory -ErrorAction SilentlyContinue |
            Where-Object {$_.Name -like 'drawio-*'} | Sort-Object Name -Descending |
            ForEach-Object { Join-Path $_.FullName 'windows\draw.io.exe' } |
            Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    }
}
if (-not $DrawioExecutable) { throw 'Provide -DrawioExecutable with the official draw.io Desktop Windows executable.' }
$executable = (Resolve-Path -LiteralPath $DrawioExecutable).Path
$inputItem = Get-Item -LiteralPath $InputPath
$files = if ($inputItem.PSIsContainer) {
    @(Get-ChildItem -LiteralPath $inputItem.FullName -Filter '*.drawio' -File -Recurse:$Recurse | Sort-Object FullName)
} else {
    if ($inputItem.Extension -ne '.drawio') { throw 'Input must be a .drawio file or a directory containing .drawio files.' }
    @($inputItem)
}
if (-not $files.Count) { throw 'No .drawio files found.' }
$outputRoot = [IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Path $outputRoot -Force | Out-Null
$planned = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
foreach ($file in $files) {
    [xml]$diagram = Get-Content -LiteralPath $file.FullName -Raw
    $pages = if ($diagram.DocumentElement.Name -eq 'mxfile') { @($diagram.mxfile.diagram).Count } else { 1 }
    if ($pages -lt 1) { throw "No diagram pages found: $($file.Name)" }
    for ($page = 0; $page -lt $pages; $page++) {
        $suffix = if ($pages -gt 1) { '.page-' + ($page+1) } else { '' }
        $output = Join-Path $outputRoot ($file.BaseName + $suffix + '.drawio.png')
        if (-not $planned.Add($output)) { throw "Output filename collision: $output. Use separate output directories." }
        if ((Test-Path -LiteralPath $output) -and -not $Force) { throw "Output exists: $output. Use -Force to replace rendered output." }
        $temporary = Join-Path $outputRoot ($file.BaseName + $suffix + '.' + [guid]::NewGuid().ToString('N') + '.drawio.png')
        $start = [Diagnostics.ProcessStartInfo]::new($executable)
        $start.UseShellExecute = $false
        $start.CreateNoWindow = $true
        $start.RedirectStandardOutput = $true
        $start.RedirectStandardError = $true
        $start.Environment['DRAWIO_DISABLE_UPDATE'] = 'true'
        foreach ($argument in @('--export','--format','png','--embed-diagram','--scale',$Scale.ToString([Globalization.CultureInfo]::InvariantCulture),'--border','20','--page-index',($page+1).ToString(),'--output',$temporary,$file.FullName)) {
            $start.ArgumentList.Add($argument)
        }
        $process = [Diagnostics.Process]::Start($start)
        try {
            $stdout = $process.StandardOutput.ReadToEndAsync()
            $stderr = $process.StandardError.ReadToEndAsync()
            if (-not $process.WaitForExit($TimeoutSeconds*1000)) {
                $process.Kill($true)
                throw "draw.io export timed out: $($file.Name) page $($page+1)."
            }
            $null = $stdout.GetAwaiter().GetResult()
            $diagnostic = $stderr.GetAwaiter().GetResult()
            if ($process.ExitCode -ne 0) { throw "draw.io export failed with exit $($process.ExitCode): $diagnostic" }
            if (-not (Test-Path -LiteralPath $temporary) -or (Get-Item -LiteralPath $temporary).Length -lt 100) { throw 'draw.io exited without a rendered PNG.' }
            Confirm-EditablePng $temporary
            [IO.File]::Move($temporary,$output,[bool]$Force)
            Write-Output $output
        } finally {
            $process.Dispose()
            if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary }
        }
    }
}
