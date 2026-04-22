"""Module entry point so ``python -m gzkit <verb>`` mirrors ``gz <verb>``.

Delegates to :func:`gzkit.cli.main`. Satisfies REQ-0.0.19-02-06 and REQ-08's
invocation shape (``uv run -m gzkit justify <anchor>``).
"""

from __future__ import annotations

from gzkit.cli import main

raise SystemExit(main())
