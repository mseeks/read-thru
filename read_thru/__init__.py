"""read-thru — turn a codebase into a self-contained, code-level reading guide.

Author a content module that builds a list of :class:`Section`s out of block
helpers, then render it to one standalone HTML file:

    from read_thru import Section, prose, code, callout, table, build

    SECTIONS = [
        Section("What changed", [
            prose("A short narrative."),
            code("src/thing.py", peek=[(10, 40)]),
            callout("why", "The reason this shape was chosen."),
        ]),
    ]

The CLI (`read-thru build content.py`) sets the engine paths and calls
:func:`build` for you; see :mod:`read_thru.cli`.
"""

from __future__ import annotations

from . import config
from .code import code, diagram
from .markdown import callout, md, prose, raw, table
from .model import Section
from .page import build

__all__ = [
    "Section",
    "prose",
    "callout",
    "table",
    "code",
    "diagram",
    "raw",
    "md",
    "build",
    "config",
]
