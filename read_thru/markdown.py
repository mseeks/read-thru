"""A small, safe markdown subset plus the prose/callout/table block helpers.

The renderer never trusts authored text to be HTML; everything outside fenced
inline-code spans is escaped exactly once. The supported surface is deliberately
tiny: paragraphs, ``-``/``*`` and ``1.`` lists, blockquotes, ``###``/``####``
headings, ``---`` rules, and the inline forms below.
"""

from __future__ import annotations

import html
import re

# ── Inline markdown forms ────────────────────────────────────────────────────
_INLINE_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITAL = re.compile(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_KBD = re.compile(r"\+\+([^+]+)\+\+")
# List-item markers, compiled out of the f-strings below (a backslash inside an
# f-string expression is a syntax error before Python 3.12).
_UL_ITEM = re.compile(r"^\s*[-*] ")
_OL_ITEM = re.compile(r"^\s*\d+\. ")


def _inline(text: str) -> str:
    """Render inline markdown to HTML, escaping everything outside code spans
    exactly once (code spans are escaped separately and never re-processed)."""
    out: list[str] = []
    pos = 0
    for m in _INLINE_CODE.finditer(text):
        out.append(_inline_nocode(text[pos:m.start()]))
        out.append("<code>" + html.escape(m.group(1), quote=False) + "</code>")
        pos = m.end()
    out.append(_inline_nocode(text[pos:]))
    return "".join(out)


def _inline_nocode(text: str) -> str:
    """Escape, then apply links, bold, kbd, and italics — in that order."""
    text = html.escape(text, quote=False)
    text = _LINK.sub(r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
    text = _BOLD.sub(r"<strong>\1</strong>", text)
    text = _KBD.sub(r"<kbd>\1</kbd>", text)
    text = _ITAL.sub(r"<em>\1</em>", text)
    return text


def md(text: str) -> str:
    """Render the markdown subset (paragraphs, lists, blockquotes, headings,
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
        elif all(_UL_ITEM.match(ln) for ln in lines if ln.strip()):
            items = "".join(
                f"<li>{_inline(_UL_ITEM.sub('', ln))}</li>"
                for ln in lines if ln.strip()
            )
            html_blocks.append(f"<ul>{items}</ul>")
        elif all(_OL_ITEM.match(ln) for ln in lines if ln.strip()):
            items = "".join(
                f"<li>{_inline(_OL_ITEM.sub('', ln))}</li>"
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
    """A flowing prose block (the markdown subset)."""
    return f'<div class="prose">{md(text)}</div>'


def raw(html_str: str) -> str:
    """Pass-through raw HTML, for the rare hand-authored block."""
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
    """A highlighted aside. ``kind`` selects an icon/title from ``_CALLOUTS``
    (why, insight, security, gotcha, counter, principle, trace, note)."""
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
    """An HTML table. Cells and headers run through inline markdown."""
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
