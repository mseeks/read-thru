"""Build the uv-ecosystem PR walkthrough — a second worked example.

Points the readthrough engine at the froot source (at projects/froot in the
surrounding zo workspace) and renders the PR walkthrough straight into froot's
committed docs dir:

    python build.py            # -> projects/froot/docs/uv-ecosystem-explained.html

Diagrams are pre-rendered in svg/. To regenerate them:

    python make_diagrams.py
    ../../tools/render_diagrams.sh diagrams svg     # needs mermaid-cli + a browser

Needs a Python with pygments on the path (the readthrough project venv).
"""
from __future__ import annotations

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent          # .../readthrough/examples/froot-uv-pr
PROJECT = HERE.parents[1]                        # .../readthrough  (engine lives here)
WORKSPACE = HERE.parents[3]                      # the zo worktree (froot is at projects/froot)

sys.path.insert(0, str(PROJECT))                 # so `import gen` resolves
sys.path.insert(0, str(HERE))                    # so `import content` resolves

import gen

gen.SOURCE_ROOT = WORKSPACE
gen.SVG_DIR = HERE / "svg"
gen.OUT = WORKSPACE / "projects" / "froot" / "docs" / "uv-ecosystem-explained.html"

import content as c

gen.build(c.SECTIONS, [])

# The engine hard-codes a "froot, read top to bottom" identity (it was extracted
# from the full-codebase guide). This walkthrough is a single PR, so retitle the
# page and the TOC header in the finished file — a contained post-step, no engine
# fork.
doc = gen.OUT.read_text()
doc = doc.replace(
    "<title>froot — a code-level reading</title>",
    "<title>froot — Python (uv) support, explained</title>",
)
doc = doc.replace(
    '<div class="toc-title">froot, read top to bottom</div>',
    '<div class="toc-title">froot · the uv ecosystem PR</div>',
)
gen.OUT.write_text(doc)
print(f"retitled {gen.OUT}")
