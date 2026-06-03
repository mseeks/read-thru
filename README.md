# read-thru

*Turn a codebase into a self-contained, code-level reading guide you can hand to
a reviewer.*

read-thru generates a single HTML page that walks a codebase top to bottom:
authored narrative interleaved with the **verbatim source** (foldable, GitHub-PR
style), inline diagrams, tables, and callouts. The output is one standalone file
with no network dependencies — embedded fonts, inline CSS/JS, pre-rendered SVG
diagrams, a sticky scroll-spy table of contents, a reading-progress bar, a
light/dark toggle, and a prose linter in the loop.

The [froot](https://github.com/mseeks/froot) guides under its
[`docs/`](https://github.com/mseeks/froot/tree/main/docs) were built with it.
Their source is the worked example in [`examples/froot/`](./examples/froot/).

> **Status:** extracted from a one-off build into a reusable project. The engine
> is generic; the froot example shows the full workflow.

## What the output gives you

- **Every line, foldable.** Source is highlighted at build time by Pygments and
  split into per-line rows. Boilerplate folds behind `⋯ N lines hidden` stubs;
  key lines get a spotlight gutter. Cut-down editions show focused *snippets*
  with the rest folded but still present.
- **Diagrams as inline SVG.** Mermaid sources are pre-rendered with mermaid-cli
  and embedded, so they need no runtime JS and are validated at build time.
- **Truly self-contained.** Cascadia Code is embedded as base64; CSS, JS, and all
  diagrams are inline. Open the file anywhere, offline.
- **Built to be navigated.** Sticky TOC with scroll-spy and a filter, a progress
  bar, deep-linkable lines, light/dark themes, hidden scrollbars.

## Layout

```
read-thru/
  gen.py             the engine: foldable highlighted code, markdown subset,
                     callouts, tables, diagram embedding, the self-contained build
  style.css          the theme (cool slate, light/dark)
  app.js             interactivity: scroll-spy TOC, progress, theme toggle, folds
  fonts.css          @font-face with base64 Cascadia Code (400/700)
  fonts/             the woff2 sources (latin subset)
  tools/
    render_diagrams.sh   mermaid (.mmd) -> inline-ready .svg via mermaid-cli
    screenshot.js        headless-Chrome screenshots, for visual QA
    lint_prose.py        run the unsloppable prose linter over a built HTML
  examples/
    froot/           the worked example (full + essential editions)
  PROCESS.md         the end-to-end methodology used to author the froot guides
```

## Setup

```sh
uv sync                       # the engine needs only pygments
npm install                   # mermaid-cli + puppeteer, for diagrams + screenshots
```

The prose linter uses [unsloppable](https://github.com/mseeks/unsloppable) (pure
stdlib); it is found automatically in a sibling `projects/` dir, or via
`UNSLOPPABLE_PATH`.

## Build the example

```sh
# Diagrams are pre-rendered in examples/froot/svg. To rebuild them:
uv run python examples/froot/make_diagrams.py
./tools/render_diagrams.sh examples/froot/diagrams examples/froot/svg

# Render the guide (full edition, or `lite` for the essential cut):
uv run python examples/froot/build.py            # -> examples/froot/froot-explained.html
uv run python examples/froot/build.py lite

# Lint the prose:
uv run python tools/lint_prose.py examples/froot/froot-explained.html
```

## Explain a different codebase

1. Write a `content.py` next to a `build.py` (copy `examples/froot/build.py`).
2. In `build.py`, set the three engine paths before importing your content:
   ```python
   import gen
   gen.SOURCE_ROOT = Path("/path/to/the/code")   # what code() paths resolve against
   gen.SVG_DIR     = Path("svg")                   # your rendered diagrams
   gen.OUT         = Path("explained.html")        # output
   import content
   gen.build(content.SECTIONS, content.ALL_FILES,
             title="my-project — a code-level reading")
   ```
3. In `content.py`, build a list of `Section`s out of `prose()`, `callout()`,
   `table()`, `diagram()`, and `code()` blocks. `code("rel/path.py", peek=[(a,b)])`
   shows a focused snippet; omit `peek` to show the whole file folded.

See **[PROCESS.md](./PROCESS.md)** for how to author a guide that a reviewer will
actually trust — the narrative techniques, the adversarial fact-check pass, and
the prose-quality gate.

## License

MIT — see [LICENSE](./LICENSE).
