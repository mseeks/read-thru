# Content DSL cheatsheet

A guide is one Python module that defines `SECTIONS` (and optionally `TITLE`,
`TOC_TITLE`, `ALL_FILES`). You build sections out of block helpers imported from
`read_thru`. Then:

```sh
read-thru build content.py --source <repo-root> --out guide.html
```

## Module shape

```python
from read_thru import Section, prose, code, callout, table, diagram, raw

TITLE = "My change — a code-level reading"   # page <title>; --title overrides
# TOC_TITLE = "..."                          # heading atop the TOC (defaults to TITLE)

SECTIONS = [
    Section("Overview", [ prose("..."), code("a.py", peek=[(1, 30)]) ]),
    Section("The seam", [ prose("..."), callout("why", "...") ]),
]

# ALL_FILES = ["a.py", "b.py"]   # whole-repo guides: assert each renders in full
```

## `Section(title, blocks, ...)`

Only `title` and `blocks` are required. `id` defaults to a slug of the title.

| field | purpose |
|---|---|
| `title` | section heading (required) |
| `blocks` | ordered list of block-helper strings (required) |
| `id` | anchor id (default: slug of title) |
| `subtitle` | one line under the heading |
| `act` | TOC group label (e.g. "Act I"). **If any section sets `act`, the TOC groups by it; otherwise it's a flat list.** |
| `num` | display number in the eyebrow (e.g. "1.3") |
| `technique` | focus-technique badge (e.g. "spotlight") |
| `files` | filename chips shown under the heading |

Small docs (a PR, a snippet) usually set only `title`/`blocks` → a clean flat
TOC. Reach for `act`/`num`/`technique` only on long, multi-act guides.

## Block helpers

- **`prose(text)`** — flowing prose. Markdown subset: `**bold**`, `*italic*`,
  `` `code` ``, `[link](url)`, `++kbd++`, `-`/`1.` lists, `> quotes`, `###`
  headings, `---` rules.
- **`code(path, ...)`** — a foldable, syntax-highlighted file. Options:
  - `peek=[(a,b), ...]` — fold everything **except** these line ranges (spotlight a slice).
  - `fold=[(a,b), ...]` — fold these ranges (show the rest).
  - `spotlight=[(a,b), ...]` — visually emphasise these lines.
  - `collapsed=True` — start the whole block collapsed.
  - `title=`, `note=` — header label and a short markdown note above the block.
  - `lang=` — force a Pygments lexer; otherwise inferred from the filename.
  - `logical=` — completeness-key / id namespace when one logical file has two blocks.
- **`callout(kind, text, title=None)`** — a highlighted aside. `kind` ∈
  `why · insight · security · gotcha · counter · principle · trace · note`.
- **`table(headers, rows, caption=None)`** — cells run through inline markdown.
- **`diagram(name, caption=None)`** — embed `<name>.svg` from `--svg-dir`
  (pre-render Mermaid first; see [`../extras/README.md`](../extras/README.md)). Optional.
- **`raw(html)`** — pass-through HTML for the rare hand-built block.

## `code()` line ranges — when to use which

- **`peek`** is the workhorse for PRs/snippets: show the 10–40 lines that matter,
  keep the rest present but folded.
- **omit `peek`/`fold`** to show a whole short file folded behind its header.
- **`spotlight`** layers emphasis on top of either, for the one or two key lines.

Line numbers are 1-based and refer to the file at `--source`.
