"""BDD steps for gz issue file (ADR-0.0.23 / OBPI-0.0.23-04).

Initializes a real git repo with a configurable remote in the
per-scenario tempdir so derive_consumer_slug() can resolve the slug
against actual `git remote -v` output. All scenarios use --dry-run so
the gh subprocess is never invoked — the live tracker is never
contacted from BDD.

Reuses the canonical ``When I run the gz command "..."`` /
``Then the command exits with code N`` / ``Then the output contains "..."``
step pair from gz_steps.py.
"""

from __future__ import annotations

import subprocess

from behave import given


@given('a fixture git remote "{remote_url}"')
def step_fixture_git_remote(_context, remote_url: str) -> None:
    """Initialize a git repo with the supplied URL as its origin remote."""
    subprocess.run(
        ["git", "init", "--quiet"],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "remote", "add", "origin", remote_url],
        check=True,
        capture_output=True,
        text=True,
    )
