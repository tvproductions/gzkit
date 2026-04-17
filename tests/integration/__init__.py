"""Integration test tier — real subprocess, real filesystem init.

Tests in this package spawn real ``uv sync`` / ``git`` subprocesses and run
the full ``gz init`` flow under ``CliRunner().isolated_filesystem()``. They
cover end-to-end CLI contracts that the unit tier intentionally skips.

Tier gating uses a ``load_tests`` protocol: when ``unittest discover`` is
invoked from ``tests/`` (the unit tier default), this package returns an
empty suite. When invoked from ``tests/integration/`` directly, or with the
``GZKIT_TIER=integration`` env var, the discovered suite is returned intact.

Run with:
    uv run gz test --integration
    uv run -m unittest discover tests/integration
"""

from __future__ import annotations

import os
import sys
import unittest


def load_tests(
    loader: unittest.TestLoader,
    standard_tests: unittest.TestSuite,
    pattern: str | None,
) -> unittest.TestSuite:
    """Gate integration-tier discovery on explicit opt-in.

    Returns the discovered suite when either:
    - ``GZKIT_TIER=integration`` is set in the environment, OR
    - The discovery command targets ``tests/integration`` directly
      (detected via ``sys.argv`` containing the path or module name).

    Otherwise returns an empty suite so ``unittest discover tests`` picks
    up unit-tier tests only.
    """
    if os.environ.get("GZKIT_TIER") == "integration":
        return standard_tests

    argv_str = " ".join(sys.argv)
    if "tests/integration" in argv_str or "tests.integration" in argv_str:
        return standard_tests

    return unittest.TestSuite()
