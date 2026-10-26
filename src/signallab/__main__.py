"""Allow ``python -m signallab`` to behave like the installed console script."""

from __future__ import annotations

from signallab.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
