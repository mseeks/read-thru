"""The :class:`Section` — one unit of the reading guide.

A section is a titled run of pre-rendered block strings (from ``prose``,
``code``, ``callout``, ``table``, ``diagram``, ``raw``). Only ``title`` and
``blocks`` are required; the rest is optional ceremony that richer guides use:
an ``act`` to group sections in the table of contents, a ``num`` and
``technique`` badge in the eyebrow, a ``subtitle``, and ``files`` chips. When no
section sets ``act``, the TOC renders as a flat list (see :mod:`read_thru.page`).
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field

from .markdown import _inline


def _slug(text: str) -> str:
    """A URL/id-safe slug from a title: lowercase, non-alphanumerics to hyphens."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"


@dataclass
class Section:
    title: str
    blocks: list[str] = field(default_factory=list)
    id: str = ""                 # anchor id; defaults to a slug of `title`
    technique: str = ""          # focus-technique badge (optional)
    act: str = ""                # TOC group, e.g. "Act I" / "Prologue" (optional)
    num: str = ""                # display number, e.g. "1.3" (optional)
    subtitle: str = ""
    files: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.id:
            self.id = _slug(self.title)

    def html(self) -> str:
        files = ""
        if self.files:
            chips = "".join(f'<code class="filechip">{html.escape(f)}</code>'
                            for f in self.files)
            files = f'<div class="sec-files">{chips}</div>'
        sub = f'<p class="sec-sub">{_inline(self.subtitle)}</p>' if self.subtitle else ""
        badge = (f'<span class="technique">🎬 {html.escape(self.technique)}</span>'
                 if self.technique else "")
        num = (f'<span class="sec-num">{html.escape(self.num)}</span>'
               if self.num else "")
        act = (f'<span class="sec-act">{html.escape(self.act)}</span>'
               if self.act else "")
        eyebrow = (f'<div class="sec-eyebrow">{act}{num}{badge}</div>'
                   if (act or num or badge) else "")
        body = "\n".join(self.blocks)
        return (
            f'<section class="sec" id="{self.id}">'
            f'<div class="sec-head">{eyebrow}'
            f"<h2>{_inline(self.title)}</h2>{sub}{files}</div>"
            f'<div class="sec-body">{body}</div></section>'
        )
