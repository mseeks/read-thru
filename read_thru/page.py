"""Page assembly: table of contents, Pygments theme CSS, and the self-contained
:func:`build` that inlines fonts, styles, JS, and every section into one file.
"""

from __future__ import annotations

import html
import re

from pygments.formatters.html import HtmlFormatter

from . import config
from .model import Section


# ── Table of contents ────────────────────────────────────────────────────────
def _toc_item(s: Section) -> str:
    num = f'<span class="toc-num">{html.escape(s.num)}</span>' if s.num else ""
    return (
        f'<li class="toc-item" data-target="{s.id}">'
        f'<a href="#{s.id}">{num}'
        f'<span class="toc-name">{html.escape(s.title)}</span></a></li>'
    )


def _toc(sections: list[Section], toc_title: str) -> str:
    """Render the sidebar TOC. Sections are grouped under their ``act`` headings
    when any section sets one; otherwise the list is flat."""
    out = [f'<nav id="toc"><div class="toc-title">{html.escape(toc_title)}</div>']
    out.append('<input id="toc-filter" placeholder="filter sections…" autocomplete="off"/>')
    out.append('<ul class="toc-list">')
    if any(s.act for s in sections):
        groups: list[tuple[str, list[Section]]] = []
        for s in sections:
            if not groups or groups[-1][0] != s.act:
                groups.append((s.act, []))
            groups[-1][1].append(s)
        for act, secs in groups:
            out.append(f'<li class="toc-act">{html.escape(act)}</li>')
            out.extend(_toc_item(s) for s in secs)
    else:
        out.extend(_toc_item(s) for s in sections)
    out.append("</ul></nav>")
    return "".join(out)


# ── Pygments theme CSS ───────────────────────────────────────────────────────
def _style_defs(style: str, scope: str) -> str:
    """Token color rules for a Pygments style, scoped to ``scope`` — with the
    base-selector rule (which would force its own container background/color)
    stripped, so our own --code-bg / ink theming stays in control."""
    defs = HtmlFormatter(style=style).get_style_defs(scope)
    defs = re.sub(r"(?m)^" + re.escape(scope) + r"\s*\{[^}]*\}\n?", "", defs)
    return defs


def _pygments_styles() -> str:
    light = _style_defs("tango", ".theme-light .hl")
    try:
        dark = _style_defs("one-dark", ".theme-dark .hl")
    except Exception:
        dark = _style_defs("monokai", ".theme-dark .hl")
    return light + "\n" + dark


# ── The build ────────────────────────────────────────────────────────────────
def build(sections: list[Section], all_files: list[str], *,
          title: str = "A code-level reading",
          toc_title: str | None = None) -> None:
    """Render the sections to a single self-contained HTML file at ``config.OUT``.

    title:     the page <title> (browser tab / bookmarks).
    toc_title: heading shown atop the table of contents; defaults to ``title``.

    After writing, the completeness contract reports any file in ``all_files``
    that no ``code()`` call rendered, and the total code-row count.
    """
    css = (config.ASSETS_DIR / "style.css").read_text()
    js = (config.ASSETS_DIR / "app.js").read_text()
    fonts_path = config.ASSETS_DIR / "fonts.css"
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
    config.OUT.write_text(doc)

    # Completeness contract: every declared file must be fully rendered.
    missing = [f for f in all_files if f not in config.RENDERED]
    print(f"Wrote {config.OUT} ({len(doc):,} bytes, {len(sections)} sections)")
    if missing:
        print(f"!! MISSING {len(missing)} files from the doc:")
        for m in missing:
            print(f"   - {m}")
    elif all_files:
        total = sum(config.RENDERED.values())
        print(f"OK: all {len(all_files)} files rendered "
              f"({total:,} code rows present).")
