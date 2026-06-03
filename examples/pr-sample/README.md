# Golden: a PR-sized guide (tier S–M)

The calibration example for the common case — documenting **one PR**. It explains
a real read-thru change (adding the CLI) against read-thru's own source.

| | |
|---|---|
| **Tier** | S–M (a PR) — see [`../../references/depth-and-scope.md`](../../references/depth-and-scope.md) |
| **Sections** | 4 — overview + one per meaningful changed file |
| **Code** | `peek` snippets (the changed lines + just enough context), never whole files |
| **TOC** | flat (no `act`s) — the normal shape for a small guide |
| **Prose** | plain, varied sentences, sparse em-dashes; a `callout` exactly where a reviewer is skeptical |

Read [`content.py`](./content.py) for the shape and the prose level. Open
[`sample.html`](./sample.html) in a browser to see the rendered target — fold/
expand code, toggle the theme, click the TOC.

Rebuild it:

```sh
read-thru build examples/pr-sample/content.py --source <read-thru repo root> \
    --out examples/pr-sample/sample.html
```

This is the bar a PR guide should clear: a reviewer can read it top to bottom and
come away able to vouch for the change.
