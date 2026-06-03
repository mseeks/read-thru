# extras — optional tooling

None of this is needed for a normal guide. The core engine is pure Python
(pygments only): prose + foldable highlighted code + callouts + tables render
with zero Node and no extra setup. These add polish at the cost of heavier
dependencies, so they live here, off the default path.

| Tool | Adds | Needs |
|---|---|---|
| `render_diagrams.sh` | Mermaid `.mmd` → inline-ready `.svg` for `diagram()` | `npx` (fetches `@mermaid-js/mermaid-cli`) + a browser |
| `screenshot.js` | headless-Chrome screenshots for visual QA | `npx`/`node` + Puppeteer + a browser |
| `lint_prose.py` | the [unsloppable](https://github.com/mseeks/unsloppable) prose-quality gate | `unsloppable` on `UNSLOPPABLE_PATH` or a sibling `projects/unsloppable` |
| `puppeteer.json` | browser config for the two Node tools (defaults to macOS Chrome) | — |

## Render diagrams

```sh
extras/render_diagrams.sh <diagrams_dir> <svg_out_dir>
# then reference them in content: diagram("name"), with --svg-dir <svg_out_dir>
```

## Prose gate

```sh
uv run python extras/lint_prose.py <built.html>
```
Flags prose that reads as AI-written, per section. See `process.md` step 7.

## Screenshots

```sh
node extras/screenshot.js <built.html> out light "0,#some-section-id"
```
