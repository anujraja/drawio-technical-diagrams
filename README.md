# Draw.io Technical Diagrams

A reusable Codex skill for clear, source-backed architecture, data-flow, runtime, and code-map documentation. Outputs native `.drawio` files and PNGs with embedded editable objects.

## Install

Clone this repository into your Codex skills directory:

```sh
git clone https://github.com/anujraja/drawio-technical-diagrams.git ~/.codex/skills/drawio-technical-diagrams
```

On Windows PowerShell:

```powershell
git clone https://github.com/anujraja/drawio-technical-diagrams.git "$env:USERPROFILE/.codex/skills/drawio-technical-diagrams"
```

If `CODEX_HOME` is customized, use its `skills` directory instead. Preserve an existing installation before cloning; to update a clean clone, run `git pull --ff-only` inside it. Start a new Codex session if the skill is not yet listed.

## Use

Ask Codex:

> Use $drawio-technical-diagrams to document this project's architecture and data flow. Inspect the implementation, create editable draw.io sources and PNGs, and review every rendered diagram.

The skill selects views that answer useful reader questions; it does not impose a fixed diagram count. It distinguishes implementation evidence from runtime verification and keeps publishing within your authorization.

## Requirements and helpers

- Python 3.10+ for the standard-library authoring helper and PNG validator.
- Official draw.io Desktop for rendering. Windows export helper requires PowerShell 7.2+; other platforms can use the Desktop CLI described in the rendering reference.
- An agent that can inspect source files and review rendered images. Automated metadata validation does not prove architecture correctness or visual clarity.

```powershell
./scripts/Export-Drawio.ps1 -InputPath ./docs/diagrams/context.drawio -OutputDirectory ./docs/diagrams/png -DrawioExecutable C:/path/draw.io.exe
python ./scripts/validate_png.py ./docs/diagrams/context.drawio ./docs/diagrams/png/context.drawio.png
```

Open either format in draw.io to edit native objects. Keep the `.drawio` source: image hosts may strip PNG metadata. Sources can also be authored manually; the Python builder is optional.

## Real project example

[Grounded Support Assistant's editable guide](https://github.com/anujraja/grounded-support-assistant/tree/main/docs/diagrams) demonstrates source inspection, separate runtime/data-flow views, human approval boundaries, and embedded-PNG verification. Its [review record](https://github.com/anujraja/grounded-support-assistant/blob/main/docs/diagrams/REVIEW.md) describes checks and limits. These are project-specific examples, not required templates.

## Contributing

Keep the instructions focused on technical diagrams. For helper changes, verify real Desktop exports and exact embedded native-tree matches, then visually inspect the result. Demonstrate improvements on a small source-backed example; do not add universal rules solely to match one project's wording.

MIT licensed. draw.io Desktop and other external tools retain their own licenses; they are not bundled here.
