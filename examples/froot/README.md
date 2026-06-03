# Golden: the froot guide (tier L — whole repo)

The whole-repo exemplar — the source that produced the two froot guides committed
to the [froot repo](https://github.com/mseeks/froot) under
[`docs/`](https://github.com/mseeks/froot/tree/main/docs).

| File | What it is |
|---|---|
| `content.py` | The **full edition**: 50 sections that walk every one of froot's 2,986 source lines, plus tests, infra, and CI. |
| `content_lite.py` | The **essential cut**: ~13 reviewer-focused sections with code shown as snippets. |
| `make_diagrams.py` | The 15 Mermaid diagram sources (writes `diagrams/*.mmd`). |
| `diagrams/`, `svg/` | Diagram sources and their pre-rendered, build-ready SVG. |

Read `content.py` to see tier-L craft: an arc ordered by dependencies, a focus
technique per section, and the completeness contract (`ALL_FILES`). For the
common PR-sized case, see [`../pr-sample/`](../pr-sample/) instead.

## Build

`content.py` references the froot source by the path `projects/froot/...`, so
`--source` must be a workspace where a [froot](https://github.com/mseeks/froot)
checkout sits at `projects/froot`. From the read-thru project root:

```sh
read-thru build examples/froot/content.py --source <workspace> \
    --out /tmp/froot.html --title "froot — a code-level reading" \
    --toc-title "froot, read top to bottom" --svg-dir examples/froot/svg

read-thru build examples/froot/content_lite.py --source <workspace> \
    --out /tmp/froot-lite.html --svg-dir examples/froot/svg   # essential cut
```

(Prefix with `uv run --project <skill-dir>` if `read-thru` isn't on your PATH.)
The build is included as a reference for *how* a whole-repo guide is authored,
not as a one-command demo — it needs the froot source present.

## Regenerate the diagrams (optional)

```sh
uv run python examples/froot/make_diagrams.py
../../extras/render_diagrams.sh examples/froot/diagrams examples/froot/svg
```

## Lint the prose (optional)

```sh
uv run python ../../extras/lint_prose.py /tmp/froot.html
```
