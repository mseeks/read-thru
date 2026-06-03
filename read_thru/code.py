"""Verbatim source rendering: Pygments highlighting split into foldable
per-line rows (GitHub-PR style), plus the inline-SVG ``diagram`` helper.

Every source line lands in the DOM as its own row; runs of folded lines collapse
into ``<details>`` stubs but are never dropped, so the completeness contract in
:func:`read_thru.build` can assert that a file rendered in full.
"""

from __future__ import annotations

import html
import re

from pygments import lex
from pygments.lexers import get_lexer_by_name, get_lexer_for_filename
from pygments.token import STANDARD_TYPES

from . import config
from .markdown import _inline, md


# ── Token → CSS class (per-line, multi-line-token safe) ──────────────────────
def _css_class(ttype) -> str:
    """Map a Pygments token type to its short CSS class, walking up to parent
    token types when the exact type has no standard class."""
    t = ttype
    cls = STANDARD_TYPES.get(t)
    while cls is None and t.parent is not None:
        t = t.parent
        cls = STANDARD_TYPES.get(t)
    return cls or ""


def _highlight_lines(source: str, lexer) -> list[str]:
    """Return one HTML string per source line. Tokens spanning newlines are
    split so no ``<span>`` ever crosses a line boundary."""
    lines: list[str] = [""]
    for ttype, value in lex(source, lexer):
        cls = _css_class(ttype)
        parts = value.split("\n")
        for i, part in enumerate(parts):
            if i:
                lines.append("")
            if part:
                esc = html.escape(part, quote=False)
                lines[-1] += f'<span class="{cls}">{esc}</span>' if cls else esc
    # `lex` yields a trailing newline → drop the empty final element.
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def _ranges_to_set(ranges: list[tuple[int, int]]) -> set[int]:
    """Flatten inclusive (start, end) line ranges into a set of line numbers."""
    out: set[int] = set()
    for a, b in ranges:
        out.update(range(a, b + 1))
    return out


def diagram(name: str, caption: str | None = None, klass: str = "") -> str:
    """Embed a pre-rendered diagram ``<name>.svg`` from ``config.SVG_DIR`` inline."""
    svg = (config.SVG_DIR / f"{name}.svg").read_text()
    # Strip the XML prolog if present; keep the <svg> root.
    svg = re.sub(r"^<\?xml[^>]*\?>\s*", "", svg)
    cap = f"<figcaption>{_inline(caption)}</figcaption>" if caption else ""
    return f'<figure class="diagram {klass}">{svg}{cap}</figure>'


def code(path: str, *, lang: str | None = None,
         fold: list[tuple[int, int]] | None = None,
         peek: list[tuple[int, int]] | None = None,
         spotlight: list[tuple[int, int]] | None = None,
         collapsed: bool = False,
         title: str | None = None,
         note: str | None = None,
         logical: str | None = None) -> str:
    """Render a source file as a foldable, highlighted code block.

    path:      path relative to ``config.SOURCE_ROOT`` (the code being explained).
    lang:      force a Pygments lexer by name; otherwise inferred from the filename.
    fold:      line ranges collapsed by default into a stub.
    peek:      if given, fold EVERYTHING except these ranges (spotlight a slice).
    spotlight: line ranges to visually emphasise.
    collapsed: start the whole block collapsed.
    title:     header label (defaults to ``path``).
    note:      a short markdown note shown above the block.
    logical:   completeness-contract key + line-id namespace (defaults to ``path``).
    """
    fp = (config.SOURCE_ROOT / path)
    source = fp.read_text()
    raw_lines = source.split("\n")
    if raw_lines and raw_lines[-1] == "":
        raw_lines.pop()
    n = len(raw_lines)

    if lang:
        lexer = get_lexer_by_name(lang)
    else:
        try:
            lexer = get_lexer_for_filename(fp.name, source)
        except Exception:
            lexer = get_lexer_by_name("text")
    hlines = _highlight_lines(source, lexer)
    while len(hlines) < n:
        hlines.append("")
    hlines = hlines[:n]

    if peek:
        keep = _ranges_to_set(peek)
        fold_set = {i for i in range(1, n + 1) if i not in keep}
    else:
        fold_set = _ranges_to_set(fold or [])
    spot_set = _ranges_to_set(spotlight or [])

    key = re.sub(r"[^A-Za-z0-9]+", "-", (logical or path)).strip("-")
    config.RENDERED[logical or path] = n

    def row(i: int) -> str:
        cls = "row" + (" spot" if i in spot_set else "")
        return (
            f'<div class="{cls}" id="L-{key}-{i}">'
            f'<a class="ln" href="#L-{key}-{i}">{i}</a>'
            f'<span class="cl">{hlines[i-1] or "&nbsp;"}</span></div>'
        )

    # Build the row stream, grouping folded runs into <details> stubs.
    parts: list[str] = []
    i = 1
    while i <= n:
        if i in fold_set:
            j = i
            while j + 1 <= n and (j + 1) in fold_set:
                j += 1
            count = j - i + 1
            folded = "".join(row(k) for k in range(i, j + 1))
            label = (f"⋯ {count} line{'s' if count != 1 else ''} hidden "
                     f"(lines {i}–{j})")
            parts.append(
                f'<details class="fold"><summary>{label}</summary>'
                f'<div class="foldrows">{folded}</div></details>'
            )
            i = j + 1
        else:
            parts.append(row(i))
            i += 1
    rows_html = "".join(parts)

    head_title = title or path
    note_html = f'<div class="code-note">{md(note)}</div>' if note else ""
    body = (
        f'<div class="code-head">'
        f'<span class="code-path">{html.escape(head_title)}</span>'
        f'<span class="code-meta">{n} lines · {lexer.name}</span>'
        f'<button class="code-toggle" data-act="expand">expand all</button>'
        f"</div>"
        f'<div class="code-body hl">{rows_html}</div>'
    )
    open_attr = "" if collapsed else " open"
    return (
        f'<div class="codefile" data-key="{key}">{note_html}'
        f'<details class="codewrap"{open_attr}>'
        f'<summary class="code-summary">{html.escape(head_title)} '
        f'<span class="muted">· {n} lines</span></summary>'
        f"{body}</details></div>"
    )
