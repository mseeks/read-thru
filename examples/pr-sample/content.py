"""Golden PR-sized guide (tier S–M).

It documents one real change to read-thru itself: replacing the old
`gen.py` + per-example `build.py` boilerplate with a small CLI and a lighter
`Section` API. Build it against the read-thru repo root:

    read-thru build examples/pr-sample/content.py \
        --source <read-thru repo root> --out examples/pr-sample/sample.html

Read this for the *shape* of a PR guide: a tight overview, one section per
meaningful changed file with a `peek` at the lines that matter, and a callout
exactly where a reviewer would be skeptical. ~4 sections, snippets not full files.
"""
from __future__ import annotations

from read_thru import Section, callout, code, prose

TITLE = "Add the read-thru CLI — a code-level reading"

SECTIONS = [
    Section("What changed, and why", [
        prose("""
This change turns read-thru from a library you wire up by hand into a tool you
run with one command. Before, every guide needed a `build.py` that set three
module globals and called `build()`; the engine lived in a single 400-line
`gen.py`. Now the engine is a small package and a `read-thru build` command does
the wiring, so authoring a guide is just: write `SECTIONS`, run one line.

Two changes carry the weight. The CLI loads your content module and points the
engine at the code being explained. And the `Section` API drops its required
ceremony, so a short guide — a PR, a snippet — no longer pays for fields only a
50-section epic needs. Read those two below.
"""),
    ]),

    Section("One command, with the paths set for you", [
        prose("""
`build` resolves where the code lives, then imports your content module. Order
matters here: `SECTIONS` is built at import time, and each `code()` call reads a
file off `SOURCE_ROOT` as it runs. So the command sets `config.SOURCE_ROOT`
*before* importing the module, not after — otherwise the first `code()` would
read against the wrong root.
"""),
        code("read_thru/cli.py", peek=[(88, 114)],
             note="The build subcommand: resolve paths, then import, then render."),
        callout("why", """
Defaults keep the common case to one line. `--source` falls back to the git root
of the working directory, `--out` to `<content>.html`, and the title to the
module's `TITLE`. A PR guide is usually just `read-thru build doc.py`.
"""),
    ]),

    Section("Section: only title and blocks are required", [
        prose("""
The old `Section` forced an `id`, `act`, `num`, and `technique` on every
section. That suited the froot guide, which is organised into numbered acts, but
it's dead weight for a four-section PR. Now only `title` and `blocks` are
required; `id` defaults to a slug of the title, and the rest default to empty.
"""),
        code("read_thru/model.py", peek=[(20, 38)],
             note="A slug for the anchor id, and every ceremony field optional."),
        prose("""
The slug is deterministic, so anchors are stable across rebuilds: the same title
always yields the same `#id`. Nothing else about a section's rendering changes —
when `act` and `num` *are* set, the eyebrow and grouped TOC render exactly as
before.
"""),
    ]),

    Section("A flat table of contents when there are no acts", [
        prose("""
The TOC adapts to the guide. If any section sets an `act`, sections group under
their act headings, the way froot does. If none do — the normal case for a small
guide — the list is flat, with no empty group chrome.
"""),
        code("read_thru/page.py", peek=[(26, 46)],
             note="One branch on whether any section declares an act."),
        callout("insight", """
This is why the same engine serves a one-file fix and a whole-repo tour: the
heavyweight structure appears only when an author asks for it. Pick the smallest
shape that lets a reviewer vouch for the change (see references/depth-and-scope.md).
"""),
    ]),
]
