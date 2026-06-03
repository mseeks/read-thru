"""Runtime configuration for the read-thru engine.

These module-level values are read *at call time* by the renderer, so a build
script (or the CLI) can point the engine at a codebase and an output path by
reassigning them before calling :func:`read_thru.build`:

    from read_thru import config, build
    config.SOURCE_ROOT = Path("/path/to/the/code")
    config.OUT = Path("guide.html")
    build(SECTIONS, ALL_FILES)

Always reassign the attributes (``config.SOURCE_ROOT = ...``); other modules
reference them as ``config.SOURCE_ROOT`` so they observe the latest value.
"""

from __future__ import annotations

from pathlib import Path

# Where the engine's own assets live (style.css, app.js, fonts.css, fonts/).
# Fixed next to this package; inlined into every build.
PACKAGE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = PACKAGE_DIR / "assets"

# ── Configurable: set these before build() ───────────────────────────────────
SOURCE_ROOT = Path.cwd()              # root that code()/path args resolve against
SVG_DIR = Path.cwd() / "svg"          # where pre-rendered diagram SVGs live
OUT = Path.cwd() / "read-thru.html"   # output HTML path

# Completeness contract: logical path -> number of code rows emitted. Populated
# by code() as files are rendered; checked by build() against the caller's
# declared file list.
RENDERED: dict[str, int] = {}
