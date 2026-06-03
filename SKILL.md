---
name: make-read-thru
description: >-
  Generate a self-contained HTML reading guide for code: authored narrative
  interleaved with verbatim, foldable, syntax-highlighted source, callouts, and
  tables — one standalone file, no network. Use this whenever opening or
  reviewing a PR (produce a guide of the PR's content and link it from the PR),
  or when asked to explain, walk through, document, or "read through" a change,
  a file or snippet, a module, or a whole codebase so a reviewer can vouch for
  it. Reach for it even when the user doesn't say "read-thru" — any "help me
  explain/review this code/PR/repo to someone" task qualifies.
---

# make-read-thru

You turn code into a guide a reviewer can read top to bottom and come away able
to **vouch** for it: the narrative explains *why*, and every line of the
**verbatim source** is right there, foldable. Output is one self-contained HTML
file (embedded fonts, inline CSS/JS) — open it anywhere, offline.

The interface is two steps: **author a content module, then run one command.**

## 1. Author the content module

Write a Python module that defines `SECTIONS` (and optionally `TITLE`). Scaffold
a starter:

```sh
read-thru new doc.py
```

Build `SECTIONS` out of block helpers — `prose`, `code`, `callout`, `table`
(`diagram` is optional). The one that carries the guide is `code`:

```python
from read_thru import Section, prose, code, callout

TITLE = "What changed — a code-level reading"

SECTIONS = [
    Section("Overview", [ prose("The change in a few tight sentences: what, why, blast radius.") ]),
    Section("The key file", [
        prose("What to notice here and why it's safe."),
        code("src/thing.py", peek=[(12, 40)]),     # spotlight the lines that matter, fold the rest
        callout("why", "The reason a reviewer would ask about, answered from the code."),
    ]),
]
```

Full block + `Section` reference: **[`references/dsl.md`](./references/dsl.md)**.

## 2. Build

Run the engine via `uv` from this skill's own directory (so it's installed once,
no PATH setup). Replace `<SKILL_DIR>` with the path to this skill:

```sh
uv run --project "<SKILL_DIR>" read-thru build doc.py --source <repo-root> --out guide.html
```

`--source` defaults to the git root of the cwd, `--out` to `<doc>.html`, the
title to the module's `TITLE`. So inside the repo you're documenting it's often
just `... read-thru build doc.py`.

## Pick a scope and depth

Same command for all three; only what you write differs. Size the guide to the
change — **smallest tier that lets a reviewer vouch.** Details + word/section
budgets: **[`references/depth-and-scope.md`](./references/depth-and-scope.md)**.

- **Snippet / file** — a few sections; `code(path, peek=[(a,b)])` on the ranges that matter.
- **PR (the common case)** — `git diff --name-only <base>...<head>` to find changed
  files; one section each at HEAD + just enough context; a `callout` where a
  reviewer is skeptical. ~3–8 sections.
- **Whole repo** — plan an arc, set `ALL_FILES` to enforce the completeness
  contract, optionally a lite cut. Follow **[`references/process.md`](./references/process.md)**.

## Make it trustworthy

A guide is only worth it if the reader can trust it. Two things earn that:

1. **Tight prose.** Short, varied sentences; sparse em-dashes; plain words. Lead
   with the point. (Optional gate: `extras/lint_prose.py`.)
2. **Fact-check every claim against the source.** Re-read the lines each section
   cites and fix any wrong line range, over-claim, or absolute ("never", "only").
   For repo-scale guides, fan out one skeptic per section — see `references/process.md`.

## Calibrate against the goldens

Read these before authoring — they set the target for content, prose, and depth:

- **[`examples/pr-sample/`](./examples/pr-sample/)** — a tight PR guide. Read
  `content.py`; open `sample.html` to see the rendered result. **Start here.**
- **[`examples/froot-uv-pr/`](./examples/froot-uv-pr/)** — a meatier real PR.
- **[`examples/froot/`](./examples/froot/)** — the whole-repo exemplar.

## When the guide is for a PR: publish & link it

After building a PR guide, deploy it to the static site and drop a bare link
(no preamble, clean URL without `.html`) into the PR. Full steps, naming, and
the URL scheme: **[`references/deploy.md`](./references/deploy.md)**.
