# Reliable draw.io export and human review

## Output contract

Deliver a native `.drawio` source and an actual Desktop-rendered `.drawio.png` with diagram data embedded. Use individual sources for convenient image links or a multipage source when that helps navigation. Preserve both formats.

The Windows helper requires PowerShell 7.2 or newer. It supports a file/directory, multipage export, scale, timeout, and an explicit `-DrawioExecutable`. It preserves existing output unless `-Force` is passed. Do not force replacements before deciding how user edits or historical versions should be preserved.

```powershell
./scripts/Export-Drawio.ps1 -InputPath ./docs/diagrams/context.drawio `
  -OutputDirectory ./docs/diagrams/png -DrawioExecutable C:/path/draw.io.exe
```

Desktop CLI equivalents include `--export --format png --embed-diagram --scale 2 --output PATH SOURCE`. Current Desktop 32.4.1 uses **one-based** `--page-index`; older releases differed. Check the installed version's help/source when adapting the command.

## Authoring pitfalls demonstrated in real exports

- Automatic wrapping on an edge label can turn a sentence into a one-word vertical column. Use short intentional lines with `whiteSpace=nowrap`, or an explicitly sized editable label placed in a clear corridor. Keep the diagram label short and put the full contract in prose.
- Auto-routing can cross nodes or other captions. Use explicit ports/waypoints and inspect the raster output, not just the coordinates.
- Cylinder `size` is a proportional shape parameter. Values such as `18` can distort curves outside the node; a small fraction such as `0.08` works in the tested renderer. Leave space between the ellipse and text, or use a simpler typed-store symbol.
- Place sequence fragment guards and messages on separate rows. Larger canvases or split scenarios are preferable to illegibly small text.
- Keep captions/keys outside relationship corridors. Check that a label's white background does not hide another arrow or word.
- Scope boundaries and optional relationships can both be dashed; the key must explain their distinct meanings.

## Validation

`validate_png.py` checks PNG chunks/CRC, recovers embedded diagram XML (compressed or uncompressed models), and compares native cell trees, attributes, labels, endpoints and geometry with the source. Multipage IDs are scoped per page. It reports image-shaped cells so a diagram accidentally flattened into a picture can be noticed. A logo image is legitimate; image cells do not establish diagram editability by themselves.

Then view every PNG at a realistic reading size. Ask: can a reader name the scope, identify element types, follow direction, read each relationship, distinguish data from control, locate persistence, and understand the evidence limits? Fix issues and re-export until the particular views pass. Metadata tests do not answer these questions.

For source moves, update Markdown links, regeneration paths, source-root calculations and export validation paths. Keep archives tracked when the user wants history on GitHub. Private GitHub image-viewer links require login; transient signed raw-image URLs are unsuitable as permanent phone links.

Primary references: [editable PNG data](https://www.drawio.com/docs/manual/export/xml-in-png/), [PNG export](https://www.drawio.com/docs/manual/export/export-to-png/), and [Desktop CLI 32.4.1 option definitions](https://github.com/jgraph/drawio-desktop/blob/v32.4.1/src/main/args.js).
