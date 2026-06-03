"""Build the froot explainer — the worked example for read-thru.

This points the engine at the froot source (which lives at projects/froot in the
surrounding zo workspace), then renders one of the two content modules:

    python build.py            # full edition  (content.py)     -> froot-explained.html
    python build.py lite       # essential cut (content_lite.py) -> froot-explained.html

Diagrams are pre-rendered in svg/. To regenerate them:

    python make_diagrams.py
    ../../tools/render_diagrams.sh diagrams svg     # needs mermaid-cli + a browser

Needs a Python with pygments on the path (see the project README / pyproject).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # .../read-thru/examples/froot
PROJECT = HERE.parents[1]                        # .../read-thru  (engine lives here)
WORKSPACE = HERE.parents[3]                      # the zo worktree (froot is at projects/froot)

sys.path.insert(0, str(PROJECT))                 # so `import gen` resolves
sys.path.insert(0, str(HERE))                    # so `import content[_lite]` resolves

import gen  # noqa: E402  (must follow the sys.path setup above)

# Point the engine at the codebase being explained and where to write the output.
gen.SOURCE_ROOT = WORKSPACE
gen.SVG_DIR = HERE / "svg"
gen.OUT = HERE / "froot-explained.html"

TITLE = "froot — a code-level reading"
TOC_TITLE = "froot, read top to bottom"

which = sys.argv[1] if len(sys.argv) > 1 else "full"
if which == "lite":
    import content_lite as c
    gen.build(c.SECTIONS, [], title=TITLE, toc_title=TOC_TITLE)
else:
    import content as c
    gen.build(c.SECTIONS, c.ALL_FILES, title=TITLE, toc_title=TOC_TITLE)
