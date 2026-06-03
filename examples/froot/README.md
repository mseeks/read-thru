# Example: the froot guide

The worked example for read-thru — the source that produced the two froot
guides committed to the [froot repo](https://github.com/mseeks/froot) under
[`docs/`](https://github.com/mseeks/froot/tree/main/docs).

| File | What it is |
|---|---|
| `content.py` | The **full edition**: 50 sections that walk every one of froot's 2,986 source lines, plus tests, infra, and CI. |
| `content_lite.py` | The **essential cut**: ~12 reviewer-focused sections with code shown as snippets. |
| `make_diagrams.py` | The 15 Mermaid diagram sources (writes `diagrams/*.mmd`). |
| `diagrams/`, `svg/` | Diagram sources and their pre-rendered, build-ready SVG. |
| `build.py` | Configures the engine and renders one edition to `froot-explained.html`. |

## Build

```sh
# from the read-thru project root, with `uv sync` done:
uv run python examples/froot/build.py            # full edition
uv run python examples/froot/build.py lite       # essential cut
```

`build.py` sets `gen.SOURCE_ROOT` to a parent workspace, because `content.py`
references the froot source by the path `projects/froot/...`. So this example
only renders in full where a [froot](https://github.com/mseeks/froot) checkout
sits at `projects/froot` relative to that root — the example is included as a
reference for *how* a guide is authored, not as a one-command demo. To explain
your own codebase, copy `build.py` and point `SOURCE_ROOT` at that code.

## Regenerate the diagrams

```sh
uv run python examples/froot/make_diagrams.py
./tools/render_diagrams.sh examples/froot/diagrams examples/froot/svg
```

## Lint the prose

```sh
uv run python tools/lint_prose.py examples/froot/froot-explained.html
```
