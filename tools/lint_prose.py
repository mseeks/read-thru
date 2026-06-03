"""Run the unsloppable prose linter over a built read-thru HTML, per section.

Lints only flowing prose (the .prose and .callout-b blocks); skips code, tables,
diagrams, and chrome. Reports a per-section score and flags anything that reads
as AI-written (score >= 3.0), so you can revise before shipping.

    python lint_prose.py ../examples/froot/froot-explained.html

unsloppable is pure-stdlib (Layer 1). Point UNSLOPPABLE_PATH at a checkout, or
this script walks up looking for a sibling `projects/unsloppable`.
"""
from __future__ import annotations

import html
import os
import re
import sys
from pathlib import Path


def _find_unsloppable() -> Path | None:
    env = os.environ.get("UNSLOPPABLE_PATH")
    if env:
        return Path(env)
    for parent in Path(__file__).resolve().parents:
        cand = parent / "projects" / "unsloppable"
        if (cand / "unsloppable").is_dir():
            return cand
    return None


us = _find_unsloppable()
if us is None:
    sys.exit("unsloppable not found; set UNSLOPPABLE_PATH=/path/to/unsloppable")
sys.path.insert(0, str(us))
import unsloppable  # noqa: E402

SECTION = re.compile(r'<section class="sec" id="([^"]+)">(.*?)</section>', re.S)
PROSE = re.compile(r'<div class="prose">(.*?)</div>', re.S)
CALLOUT = re.compile(r'<div class="callout-b">(.*?)</div>', re.S)


def _text(fragment: str) -> str:
    t = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def main() -> int:
    if len(sys.argv) < 2:
        sys.exit("usage: lint_prose.py <built-explainer.html>")
    doc = Path(sys.argv[1]).read_text()
    print(f"{'section':18} {'score':>6} {'words':>6}  verdict")
    print("-" * 64)
    corpus, flagged = [], []
    for sid, body in SECTION.findall(doc):
        parts = PROSE.findall(body) + CALLOUT.findall(body)
        prose = " ".join(_text(p) for p in parts).strip()
        if len(prose.split()) < 25:
            continue
        corpus.append(prose)
        r = unsloppable.lint(prose)
        mark = "  FLAGGED" if r.score >= 3.0 else ""
        print(f"{sid:18} {r.score:>6.1f} {r.word_count:>6}  {r.verdict}{mark}")
        if r.score >= 3.0:
            flagged.append(sid)
    whole = unsloppable.lint("\n\n".join(corpus))
    print("-" * 64)
    print(f"{'WHOLE DOC':18} {whole.score:>6.1f} {whole.word_count:>6}  {whole.verdict}")
    print(f"flagged sections: {flagged or 'none'}")
    return 1 if flagged else 0


if __name__ == "__main__":
    raise SystemExit(main())
