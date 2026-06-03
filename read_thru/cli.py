"""The ``read-thru`` command line.

Two subcommands:

    read-thru new  [path]                 scaffold a starter content module
    read-thru build content.py [options]  render a content module to one HTML file

``build`` loads the content module (so it can ``from read_thru import ...``),
points the engine at the code being explained, and calls
:func:`read_thru.build`. The only thing an author writes is the content module
— a list of ``SECTIONS`` plus an optional ``TITLE``/``TOC_TITLE``/``ALL_FILES``.
"""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

from . import build, config

_STARTER = '''"""read-thru content. Edit SECTIONS, then build:

    read-thru build {name} --source <repo-root>

Docs: references/dsl.md (block helpers), references/depth-and-scope.md (sizing).
"""
from read_thru import Section, prose, code, callout, table  # noqa: F401

TITLE = "My change — a code-level reading"

SECTIONS = [
    Section("Overview", [
        prose("What this change is and why it matters. Lead with the point; "
              "keep it tight and concrete."),
    ]),
    Section("The key file", [
        prose("What to look at here, and what to notice about it."),
        code("path/to/file.py", peek=[(1, 40)]),
        callout("why", "Why it is built this way."),
    ]),
]

# Whole-repo guides only: list every file you intend to render in full, and the
# build will error if any is missing and report the total code-row count.
# ALL_FILES = ["path/to/file.py"]
'''


def _git_root(start: Path) -> Path | None:
    """The git top-level containing ``start``, or None if not in a repo."""
    try:
        r = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=False,
        )
        if r.returncode == 0:
            return Path(r.stdout.strip())
    except Exception:
        pass
    return None


def _load_content(path: Path):
    """Import a content module from a file path, with its directory on sys.path
    so it can import sibling helpers."""
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"read-thru: cannot load content module {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    spec.loader.exec_module(mod)
    return mod


def _cmd_new(args: argparse.Namespace) -> int:
    out = Path(args.path)
    if out.exists() and not args.force:
        raise SystemExit(f"read-thru: {out} exists (use --force to overwrite)")
    out.write_text(_STARTER.format(name=out.name))
    print(f"Wrote starter content to {out}")
    print("Edit SECTIONS, then: read-thru build " + str(out))
    return 0


def _cmd_build(args: argparse.Namespace) -> int:
    content = Path(args.content).resolve()
    if not content.exists():
        raise SystemExit(f"read-thru: content module not found: {content}")

    # Resolve paths BEFORE importing the content module — SECTIONS is built at
    # import time and its code() calls read files relative to SOURCE_ROOT.
    source = Path(args.source).resolve() if args.source else (
        _git_root(Path.cwd()) or Path.cwd())
    svg_dir = (Path(args.svg_dir).resolve() if args.svg_dir
               else content.parent / "svg")
    config.SOURCE_ROOT = source
    config.SVG_DIR = svg_dir

    mod = _load_content(content)
    sections = getattr(mod, "SECTIONS", None)
    if not sections:
        raise SystemExit(f"read-thru: {content} defines no SECTIONS")
    all_files = list(getattr(mod, "ALL_FILES", []) or [])
    title = args.title or getattr(mod, "TITLE", None) or "A code-level reading"
    toc_title = args.toc_title or getattr(mod, "TOC_TITLE", None)

    out = Path(args.out).resolve() if args.out else (
        Path.cwd() / f"{content.stem}.html")
    config.OUT = out

    build(sections, all_files, title=title, toc_title=toc_title)
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="read-thru",
        description="Turn a codebase into a self-contained code-level reading guide.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pn = sub.add_parser("new", help="scaffold a starter content module")
    pn.add_argument("path", nargs="?", default="content.py",
                    help="where to write the starter (default: content.py)")
    pn.add_argument("--force", action="store_true", help="overwrite if it exists")
    pn.set_defaults(func=_cmd_new)

    pb = sub.add_parser("build", help="render a content module to one HTML file")
    pb.add_argument("content", help="path to the content module (defines SECTIONS)")
    pb.add_argument("--source", help="root that code() paths resolve against "
                    "(default: the git root of the cwd, else the cwd)")
    pb.add_argument("--out", help="output HTML path (default: <content>.html)")
    pb.add_argument("--title", help="page <title> (default: module TITLE or generic)")
    pb.add_argument("--toc-title", dest="toc_title",
                    help="heading atop the TOC (default: the title)")
    pb.add_argument("--svg-dir", dest="svg_dir",
                    help="pre-rendered diagram SVGs (default: <content dir>/svg)")
    pb.set_defaults(func=_cmd_build)

    args = p.parse_args(argv)
    return args.func(args)
