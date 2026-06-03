# read-thru

*Turn code into a self-contained, code-level reading guide you can hand to a
reviewer.*

read-thru generates a single HTML page that walks code top to bottom: authored
narrative interleaved with the **verbatim source** (foldable, GitHub-PR style),
inline diagrams, tables, and callouts. The output is one standalone file with no
network dependencies — embedded fonts, inline CSS/JS, pre-rendered SVG diagrams,
a sticky scroll-spy table of contents, a reading-progress bar, and a light/dark
toggle.

It's **agent-driven** and ships as a **Claude Code skill** (`make-read-thru`):
an agent points it at a PR, a snippet, or a whole repo and authors the guide. The
repo is also the skill — see [`SKILL.md`](./SKILL.md).

## Install as a skill

Drop the directory into your skills folder (or symlink it to keep one source of
truth):

```sh
cp -r read-thru ~/.claude/skills/make-read-thru
# or, from a workspace that vendors it as a submodule:
ln -s ../../projects/read-thru .claude/skills/make-read-thru
```

The engine runs through `uv` with one dependency (Pygments); the first build
creates a `.venv` automatically. Nothing else to install.

## Use it directly (without the skill)

```sh
read-thru new doc.py                                  # scaffold a content module
read-thru build doc.py --source <repo> --out guide.html
```

`doc.py` defines `SECTIONS` (and optional `TITLE`) out of the block helpers
`prose`, `code`, `callout`, `table`, `diagram`. The whole DSL is one page:
[`references/dsl.md`](./references/dsl.md).

## What the output gives you

- **Every line, foldable.** Source is highlighted at build time by Pygments and
  split into per-line rows. Boilerplate folds behind `⋯ N lines hidden` stubs;
  `peek` ranges spotlight a focused slice with the rest folded but present.
- **Truly self-contained.** Cascadia Code is embedded as base64; CSS, JS, and any
  diagrams are inline. Open the file anywhere, offline.
- **Built to be navigated.** Sticky TOC with scroll-spy and a filter (grouped by
  act, or flat for small guides), a progress bar, deep-linkable lines, themes.
- **A completeness contract.** Whole-repo guides declare `ALL_FILES`; the build
  errors if any is missing and reports the total code-row count.

## Layout

```
read-thru/
  SKILL.md           the skill: when to use it + the two-step workflow
  read_thru/         the engine (pure-Pygments package)
    model.py         the Section
    markdown.py      the markdown subset + prose/callout/table helpers
    code.py          foldable highlighted source + diagram embedding
    page.py          TOC + the self-contained build()
    cli.py           `read-thru build` / `read-thru new`
    assets/          style.css, app.js, fonts.css, fonts/ (inlined into output)
  references/        process.md · dsl.md · depth-and-scope.md · deploy.md
  examples/          pr-sample/ (S) · froot-uv-pr/ (M) · froot/ (L) — the goldens
  extras/            optional Node/QA/prose-lint tooling (off the default path)
```

## Methodology

For the full playbook behind a guide a reviewer will *trust* — planning the arc,
the focus-technique palette, the adversarial fact-check pass, and the prose gate
— see [`references/process.md`](./references/process.md). Size a guide to its
scope with [`references/depth-and-scope.md`](./references/depth-and-scope.md).

## License

MIT — see [LICENSE](./LICENSE).
