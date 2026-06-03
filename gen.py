"""read-thru reading-doc generator — the engine.

Renders a single self-contained HTML page (no CDN) from:
  * verbatim source files, syntax-highlighted at build time by Pygments, split
    into foldable per-line rows (GitHub-PR style) — every line is in the DOM.
  * authored prose (a small markdown subset), callouts, tables.
  * Mermaid diagrams pre-rendered to inline SVG by mermaid-cli.

Public surface used by content.py: Section, prose, callout, table, code,
diagram, raw, and build().
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from pathlib import Path

from pygments import lex
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name, get_lexer_for_filename
from pygments.token import STANDARD_TYPES

# ── Paths ────────────────────────────────────────────────────────────────────
# ENGINE_DIR is where the shared assets (style.css, app.js, fonts.css) live; it
# is fixed next to this module. The other three are CONFIGURABLE: a build script
# sets them (before importing its content module) to point at the codebase being
# explained, the rendered-diagram SVGs, and the desired output file. See
# examples/froot/build.py.
ENGINE_DIR = Path(__file__).resolve().parent
SOURCE_ROOT = Path.cwd()                    # root that code()/src() paths resolve against
SVG_DIR = ENGINE_DIR / "svg"                # where rendered diagram SVGs live
OUT = Path.cwd() / "explained.html"         # output HTML path

# Files that must each be fully present in the document (completeness contract).
_RENDERED: dict[str, int] = {}   # logical path -> number of code rows emitted


# ── Token → CSS class (per-line, multi-line-token safe) ──────────────────────
def _css_class(ttype) -> str:
    t = ttype
    cls = STANDARD_TYPES.get(t)
    while cls is None and t.parent is not None:
        t = t.parent
        cls = STANDARD_TYPES.get(t)
    return cls or ""


def _highlight_lines(source: str, lexer) -> list[str]:
    """Return one HTML string per source line. Tokens spanning newlines are
    split so no <span> ever crosses a line boundary."""
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


# ── Minimal, safe markdown subset ────────────────────────────────────────────
_INLINE_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITAL = re.compile(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_KBD = re.compile(r"\+\+([^+]+)\+\+")


def _inline(text: str) -> str:
    """Inline markdown → HTML, escaping everything outside code spans once."""
    out: list[str] = []
    pos = 0
    for m in _INLINE_CODE.finditer(text):
        out.append(_inline_nocode(text[pos:m.start()]))
        out.append("<code>" + html.escape(m.group(1), quote=False) + "</code>")
        pos = m.end()
    out.append(_inline_nocode(text[pos:]))
    return "".join(out)


def _inline_nocode(text: str) -> str:
    text = html.escape(text, quote=False)
    text = _LINK.sub(r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
    text = _BOLD.sub(r"<strong>\1</strong>", text)
    text = _KBD.sub(r"<kbd>\1</kbd>", text)
    text = _ITAL.sub(r"<em>\1</em>", text)
    return text


def md(text: str) -> str:
    """Render a small markdown subset (paragraphs, lists, blockquotes, headings,
    horizontal rules) to HTML."""
    text = text.strip("\n")
    blocks = re.split(r"\n\s*\n", text)
    html_blocks: list[str] = []
    for block in blocks:
        lines = [ln.rstrip() for ln in block.split("\n")]
        first = lines[0].strip()
        if first == "---":
            html_blocks.append("<hr/>")
        elif first.startswith("#### "):
            html_blocks.append(f"<h4>{_inline(first[5:])}</h4>")
        elif first.startswith("### "):
            html_blocks.append(f"<h3>{_inline(first[4:])}</h3>")
        elif all(re.match(r"^\s*[-*] ", ln) for ln in lines if ln.strip()):
            items = "".join(
                f"<li>{_inline(re.sub(r'^\\s*[-*] ', '', ln))}</li>"
                for ln in lines if ln.strip()
            )
            html_blocks.append(f"<ul>{items}</ul>")
        elif all(re.match(r"^\s*\d+\. ", ln) for ln in lines if ln.strip()):
            items = "".join(
                f"<li>{_inline(re.sub(r'^\\s*\\d+\\. ', '', ln))}</li>"
                for ln in lines if ln.strip()
            )
            html_blocks.append(f"<ol>{items}</ol>")
        elif all(ln.strip().startswith(">") for ln in lines if ln.strip()):
            inner = " ".join(
                re.sub(r"^\s*>\s?", "", ln) for ln in lines if ln.strip()
            )
            html_blocks.append(f"<blockquote>{_inline(inner)}</blockquote>")
        else:
            html_blocks.append(f"<p>{_inline(' '.join(lines))}</p>")
    return "\n".join(html_blocks)


# ── Block helpers (each returns an HTML string) ──────────────────────────────
def prose(text: str) -> str:
    return f'<div class="prose">{md(text)}</div>'


def raw(html_str: str) -> str:
    return html_str


_CALLOUTS = {
    "why":          ("🧭", "Why it's built this way"),
    "insight":      ("💡", "Insight"),
    "security":     ("🔒", "Security"),
    "gotcha":       ("⚠️", "Gotcha"),
    "counter":      ("🧪", "Counterfactual"),
    "principle":    ("⚖️", "Principle"),
    "trace":        ("🔬", "Trace"),
    "note":         ("📝", "Note"),
}


def callout(kind: str, text: str, title: str | None = None) -> str:
    icon, default_title = _CALLOUTS.get(kind, ("📝", "Note"))
    title = title or default_title
    return (
        f'<aside class="callout c-{kind}">'
        f'<div class="callout-h"><span class="callout-i">{icon}</span>'
        f'<span class="callout-t">{html.escape(title)}</span></div>'
        f'<div class="callout-b">{md(text)}</div></aside>'
    )


def table(headers: list[str], rows: list[list[str]], caption: str | None = None,
          klass: str = "") -> str:
    thead = "".join(f"<th>{_inline(h)}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in row) + "</tr>"
        for row in rows
    )
    cap = f"<figcaption>{_inline(caption)}</figcaption>" if caption else ""
    return (
        f'<figure class="tablewrap {klass}"><table>'
        f"<thead><tr>{thead}</tr></thead><tbody>{body}</tbody></table>"
        f"{cap}</figure>"
    )


def diagram(name: str, caption: str | None = None, klass: str = "") -> str:
    svg = (SVG_DIR / f"{name}.svg").read_text()
    # Strip the XML prolog if present; keep the <svg> root.
    svg = re.sub(r"^<\?xml[^>]*\?>\s*", "", svg)
    # Give each diagram a unique id namespace so multiple SVGs don't collide.
    cap = f"<figcaption>{_inline(caption)}</figcaption>" if caption else ""
    return f'<figure class="diagram {klass}">{svg}{cap}</figure>'


def _ranges_to_set(ranges: list[tuple[int, int]]) -> set[int]:
    out: set[int] = set()
    for a, b in ranges:
        out.update(range(a, b + 1))
    return out


def code(path: str, *, lang: str | None = None,
         fold: list[tuple[int, int]] | None = None,
         peek: list[tuple[int, int]] | None = None,
         spotlight: list[tuple[int, int]] | None = None,
         collapsed: bool = False,
         title: str | None = None,
         note: str | None = None,
         logical: str | None = None) -> str:
    """Render a source file as a foldable, highlighted code block.

    path:     path relative to SOURCE_ROOT (the codebase being explained).
    fold:     line ranges collapsed by default into a stub.
    peek:     if given, fold EVERYTHING except these ranges (spotlight a slice).
    spotlight:line ranges to visually emphasise.
    collapsed:start the whole block collapsed.
    """
    fp = (SOURCE_ROOT / path)
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
    _RENDERED[logical or path] = n

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


# ── Section model ────────────────────────────────────────────────────────────
@dataclass
class Section:
    id: str
    act: str            # e.g. "Act I" or "Prologue"
    num: str            # e.g. "1.3"
    title: str
    technique: str      # focus-technique badge
    files: list[str] = field(default_factory=list)
    blocks: list[str] = field(default_factory=list)
    subtitle: str = ""

    def html(self) -> str:
        files = ""
        if self.files:
            chips = "".join(f'<code class="filechip">{html.escape(f)}</code>'
                            for f in self.files)
            files = f'<div class="sec-files">{chips}</div>'
        sub = f'<p class="sec-sub">{_inline(self.subtitle)}</p>' if self.subtitle else ""
        badge = (f'<span class="technique">🎬 {html.escape(self.technique)}</span>'
                 if self.technique else "")
        body = "\n".join(self.blocks)
        return (
            f'<section class="sec" id="{self.id}">'
            f'<div class="sec-head">'
            f'<div class="sec-eyebrow"><span class="sec-act">{html.escape(self.act)}</span>'
            f'<span class="sec-num">{html.escape(self.num)}</span>{badge}</div>'
            f"<h2>{_inline(self.title)}</h2>{sub}{files}</div>"
            f'<div class="sec-body">{body}</div></section>'
        )


# ── TOC + page assembly ──────────────────────────────────────────────────────
def _toc(sections: list[Section], toc_title: str) -> str:
    groups: list[tuple[str, list[Section]]] = []
    for s in sections:
        if not groups or groups[-1][0] != s.act:
            groups.append((s.act, []))
        groups[-1][1].append(s)
    out = [f'<nav id="toc"><div class="toc-title">{html.escape(toc_title)}</div>']
    out.append('<input id="toc-filter" placeholder="filter sections…" autocomplete="off"/>')
    out.append('<ul class="toc-list">')
    for act, secs in groups:
        out.append(f'<li class="toc-act">{html.escape(act)}</li>')
        for s in secs:
            out.append(
                f'<li class="toc-item" data-target="{s.id}">'
                f'<a href="#{s.id}"><span class="toc-num">{html.escape(s.num)}</span>'
                f'<span class="toc-name">{_inline(s.title)}</span></a></li>'
            )
    out.append("</ul></nav>")
    return "".join(out)


def _style_defs(style: str, scope: str) -> str:
    """Token color rules for a Pygments style, scoped to ``scope`` — with the
    base-selector rule (which would force its own container background/color)
    stripped, so our own --code-bg / ink theming stays in control."""
    defs = HtmlFormatter(style=style).get_style_defs(scope)
    # Drop the bare `{scope} { ... }` rule (background + default fg on .hl).
    defs = re.sub(r"(?m)^" + re.escape(scope) + r"\s*\{[^}]*\}\n?", "", defs)
    return defs


def _pygments_styles() -> str:
    light = _style_defs("tango", ".theme-light .hl")
    try:
        dark = _style_defs("one-dark", ".theme-dark .hl")
    except Exception:
        dark = _style_defs("monokai", ".theme-dark .hl")
    return light + "\n" + dark


def build(sections: list[Section], all_files: list[str], *,
          title: str = "A code-level reading",
          toc_title: str | None = None) -> None:
    """Render the sections to a single self-contained HTML file at OUT.

    title:     the page <title> (browser tab / bookmarks).
    toc_title: heading shown atop the table of contents; defaults to `title`.
    """
    css = (ENGINE_DIR / "style.css").read_text()
    js = (ENGINE_DIR / "app.js").read_text()
    fonts_path = ENGINE_DIR / "fonts.css"
    fonts = fonts_path.read_text() if fonts_path.exists() else ""
    pyg = _pygments_styles()
    toc = _toc(sections, toc_title or title)
    body = "\n".join(s.html() for s in sections)
    doc = f"""<!doctype html>
<html lang="en" class="theme-light">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{html.escape(title)}</title>
<style>
{fonts}
{pyg}
{css}
</style>
</head>
<body>
<div id="progress"></div>
<button id="menu-btn" aria-label="menu">☰</button>
<button id="theme-btn" aria-label="theme">◐</button>
{toc}
<main id="main">
{body}
</main>
<script>
{js}
</script>
</body>
</html>"""
    OUT.write_text(doc)

    # Completeness contract: every file must be fully rendered.
    missing = [f for f in all_files if f not in _RENDERED]
    print(f"Wrote {OUT} ({len(doc):,} bytes, {len(sections)} sections)")
    if missing:
        print(f"!! MISSING {len(missing)} files from the doc:")
        for m in missing:
            print(f"   - {m}")
    else:
        total = sum(_RENDERED.values())
        print(f"OK: all {len(all_files)} files rendered "
              f"({total:,} code rows present).")
