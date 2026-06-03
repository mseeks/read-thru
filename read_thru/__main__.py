"""Enable ``python -m read_thru`` as an alias for the ``read-thru`` CLI."""

from __future__ import annotations

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
