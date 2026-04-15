"""Resolve ARB receipt paths from gzkit configuration."""

from __future__ import annotations

import os
from pathlib import Path

from gzkit.config import GzkitConfig

_ENV_OVERRIDE = "GZKIT_ARB_RECEIPTS_ROOT"


def receipts_root(
    *,
    config: GzkitConfig | None = None,
    project_root: Path | None = None,
) -> Path:
    """Return the configured ARB receipts root, creating it on demand.

    Resolution order:
    1. GZKIT_ARB_RECEIPTS_ROOT environment variable (absolute path; used by tests)
    2. `config.arb.receipts_root` interpreted relative to *project_root*
    3. Default: `<project_root>/artifacts/receipts`

    Args:
        config: Optional loaded GzkitConfig; if omitted, loaded from .gzkit.json
            in the current working directory.
        project_root: Optional project root; if omitted, defaults to the
            current working directory. Ignored when the environment override is
            set to an absolute path.

    Returns:
        The resolved receipts directory (created if missing).

    Raises:
        OSError: If the directory cannot be created.
    """
    override = os.environ.get(_ENV_OVERRIDE)
    if override:
        root = Path(override)
    else:
        cfg = config if config is not None else GzkitConfig.load()
        base = project_root if project_root is not None else Path.cwd()
        root = base / cfg.arb.receipts_root

    root.mkdir(parents=True, exist_ok=True)
    return root


__all__ = ["receipts_root"]
