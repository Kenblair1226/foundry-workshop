# Workshop Slides

The presentation deck for **Building AI Applications with Azure AI Foundry** is
written in [Marp](https://marp.app/) — Markdown that renders to slides. The
source is [`foundry-workshop.md`](./foundry-workshop.md).

## What's in the deck

What is Azure AI Foundry · architecture (hubs/projects/connections) · model
catalog · SDK overview · prompt flow & evaluation · the RAG pattern · the Agent
Service · Responsible AI · wrap-up. **Speaker notes** are embedded as HTML
comments (`<!-- ... -->`) on each slide.

## Prerequisites

- **Node.js 18+** (for the Marp CLI via `npx`), or
- The **Marp for VS Code** extension for live preview.

No install is required if you use `npx` — it fetches the CLI on demand.

## Render to PDF

```bash
npx @marp-team/marp-cli slides/foundry-workshop.md --pdf
```

Produces `slides/foundry-workshop.pdf`.

## Render to HTML

```bash
npx @marp-team/marp-cli slides/foundry-workshop.md --html
```

Produces `slides/foundry-workshop.html` (self-contained; open in any browser).

## Render to PowerPoint (PPTX)

```bash
npx @marp-team/marp-cli slides/foundry-workshop.md --pptx
```

## Presenter notes & live preview

- **Speaker notes**: exported into the PDF/PPTX notes and shown in Marp's
  presenter view. In the source they are the `<!-- ... -->` comment blocks.
- **Live preview while editing**: install the
  [Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode)
  extension and open `foundry-workshop.md`; toggle the preview pane.
- **Watch mode** (auto-rebuild on save):

  ```bash
  npx @marp-team/marp-cli slides/foundry-workshop.md --watch --html
  ```

- **Serve a local slideshow** with speaker/presenter mode:

  ```bash
  npx @marp-team/marp-cli --server slides/
  ```

## Notes

- The front-matter (`marp: true`, `theme: default`, `paginate: true`,
  `size: 16:9`) is at the top of `foundry-workshop.md`. Swap `theme` for
  `gaia` or `uncover` for a different look, or point to a custom theme CSS.
- PDF/PPTX export uses a headless Chromium that Marp downloads automatically the
  first time. If you're offline or behind a proxy, set `CHROME_PATH` to a local
  Chrome/Chromium binary.
