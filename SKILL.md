---
name: drawio-technical-diagrams
description: Create or improve human-readable, source-backed architecture, data-flow, runtime, and code-map diagrams as editable draw.io files and PNGs containing diagram data. Use for technical project documentation, not decorative artwork or general presentation design.
---

# Draw.io Technical Diagrams

Produce diagrams a reader can understand without guessing and edit as individual objects in draw.io. Keep the work grounded in the selected project's implementation and the user's requested scope.

## Select the view before drawing

Identify the audience, the question each view answers, the implementation/version it describes, and the evidence available. Inspect the relevant source and existing documentation; record unknowns rather than inventing behavior. Keep secrets, private recordings, and runtime data out of published diagrams.

Choose only useful views, not a fixed-size atlas. Use C4 context for neighboring systems, containers for applications/data stores, and components for responsibilities inside one container. Use data-flow views for payloads and storage, sequence views for execution order, and state views for actual states and transitions. Read [diagram-types.md](references/diagram-types.md) for the applicable conventions and accuracy checks.

For a substantial guide, provide a beginner reading path and a builder/operator path. Keep explanation separate from detailed interfaces/source reference. Include a glossary where abbreviations would slow the reader.

## Author editable objects

Create native mxGraph shapes, text, boundaries, connectors, lifelines, and fragments. Do not flatten a generated picture into an image-shaped cell and call it editable. A reused logo may be an image; the diagram itself must remain objects. The optional [diagram_builder.py](scripts/diagram_builder.py) provides a small standard-library authoring helper; adapt its layout to the project rather than copying a prior project's names or topology.

Each page needs a title, diagram type, scope, reader question, and a key. Give elements a type, purpose, and relevant technology. Label relationships with their intent or payload and, for process boundaries, their transport. Explain direction, dashed lines, shapes, and color; color alone must not carry meaning.

Use generous spacing, readable fonts, short intentional line breaks, and controlled routing. Read [rendering-and-review.md](references/rendering-and-review.md) before exporting or troubleshooting geometry. Complex diagrams usually need separate views rather than smaller text.

## Render and verify

Export with the actual draw.io Desktop renderer and embedded diagram data. On Windows, use [Export-Drawio.ps1](scripts/Export-Drawio.ps1) with an explicit or discovered executable. On another supported host, use the installed Desktop CLI's equivalent flags; check its help rather than assuming page-index behavior. Do not substitute another raster renderer for an editable draw.io PNG.

Verify every PNG against its source:

```text
python <skill-folder>/scripts/validate_png.py <source.drawio> <export.drawio.png>
```

For a selected page from a multipage source, pass `--page N` (one-based). Metadata can contain the full document or only that page; the validator checks the appropriate native cell trees. It verifies editability/integrity, not architecture correctness or visual legibility.

View every exported image. Fix clipping, overlaps, label columns, unclear arrow direction, distorted symbols, and incorrect scope. Re-export affected pages, rerun metadata checks, and review them again. For a substantial set, use independent review when available and authorized. Do not claim completion from valid XML or a passing renderer alone.

## Deliver and maintain

Keep the latest accurate set at a stable active path such as `docs/diagrams/`. When replacing existing tracked versions, preserve them under a clearly labelled archive unless the user or repository specifies another policy. Repair links and generators after moves. Do not silently delete historical material or change archive tracking rules.

Provide an index with PNG previews first, editable source links, reading order, source/version references, and a clear distinction between implemented, verified, user-assisted, unverified, and planned behavior. Mention that image services can strip embedded XML; retain the `.drawio` sources. A generator can overwrite manual edits, so state how lasting edits should be maintained.

Publish or push only when the user authorizes that destination. Return clickable links suited to the user's device. Use standards-informed descriptions; do not claim certification or formal conformance without the relevant audit. If the Desktop renderer is unavailable, preserve the editable source and report that PNG rendering remains incomplete.
