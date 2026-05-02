"""gz issue file — cross-repo defect/enhancement filing wrapper.

Routes issues at ``tvproductions/gzkit`` regardless of the consuming repo's
``git remote``, auto-stamps a provenance trailer naming the consumer slug and
the gzkit version, and hard-rejects bodies that reference no gzkit-owned
surface (closing the misrouting failure class — see GHI #316 and the
``Safeguard circumvention`` pattern in `.gzkit/rules/agent-failure-modes.md`).

REQ-0.0.23-04-04 (provenance trailer), REQ-0.0.23-04-05 (cross-repo routing),
REQ-0.0.23-04-06 (hard-reject misrouted bodies),
REQ-0.0.23-04-07 (subprocess boundary mocked in unit tests).
"""

from __future__ import annotations

import re
import subprocess
import sys

from gzkit import __version__
from gzkit.commands.common import console

GZKIT_REPO = "tvproductions/gzkit"

_SURFACE_MARKERS: tuple[tuple[str, str], ...] = (
    (r"\bgz\s+\w", "`gz <verb>`"),
    (r"\.gzkit/", "`.gzkit/`"),
    (r"src/gzkit/", "`src/gzkit/`"),
    (r"\bgzkit\.\w", "`gzkit.<module>`"),
)


class IssueValidationError(Exception):
    """Raised when an issue body fails the gzkit-surface reference check."""


def derive_gzkit_version() -> str:
    """Return the canonical ``gz vX.Y.Z`` shape used in the provenance trailer."""
    return f"gz v{__version__}"


def derive_consumer_slug() -> str:
    """Resolve the consuming repository's owner/repo slug from ``git remote -v``.

    Picks ``origin`` when present; falls back to the first remote otherwise.
    Strips a trailing ``.git`` suffix. Handles SSH (``git@github.com:owner/repo``)
    and HTTPS (``https://github.com/owner/repo``) URL forms.
    """
    result = subprocess.run(
        ["git", "remote", "-v"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise ValueError(
            "no git remote found in current working tree — cannot derive consumer slug"
        )

    remotes: dict[str, str] = {}
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        remote_name, url = parts[0], parts[1]
        remotes.setdefault(remote_name, url)

    if not remotes:
        raise ValueError(
            "no git remote found in current working tree — cannot derive consumer slug"
        )

    chosen = remotes.get("origin") or next(iter(remotes.values()))
    slug = _extract_slug_from_url(chosen)
    if slug is None:
        raise ValueError(f"git remote URL has unexpected shape: {chosen!r}")
    return slug


def _extract_slug_from_url(url: str) -> str | None:
    """Parse ``owner/repo`` out of an SSH or HTTPS GitHub URL."""
    candidate = url.removesuffix(".git")
    ssh_match = re.match(r"^git@[^:]+:(?P<slug>[^/]+/[^/]+)$", candidate)
    if ssh_match:
        return ssh_match.group("slug")
    https_match = re.match(r"^https?://[^/]+/(?P<slug>[^/]+/[^/]+)$", candidate)
    if https_match:
        return https_match.group("slug")
    return None


def compose_body(body: str, slug: str, version: str) -> str:
    """Prepend the provenance trailer; preserve the user body verbatim."""
    return f"Filed from {slug} running {version}\n\n{body}"


def validate_gzkit_surface_reference(body: str) -> None:
    """Hard-reject bodies that reference no gzkit-owned surface.

    Raises ``IssueValidationError`` with a diagnostic naming every checked
    marker so an operator who hits the rejection knows exactly which shape to
    add. This closes the misrouting class structurally per
    `.gzkit/rules/agent-failure-modes.md` § Safeguard circumvention.
    """
    for pattern, _label in _SURFACE_MARKERS:
        if re.search(pattern, body):
            return
    marker_list = ", ".join(label for _pattern, label in _SURFACE_MARKERS)
    raise IssueValidationError(
        "issue body references no gzkit-owned surface — expected at least one of: "
        f"{marker_list}. file at the consuming repo's tracker if the defect is in "
        "consumer code; otherwise edit the body to name the gzkit surface."
    )


def issue_file_cmd(
    *,
    title: str,
    body: str,
    label: str,
    dry_run: bool,
) -> None:
    """Compose, validate, then file (or preview) the issue against gzkit's tracker.

    Exit codes follow `.claude/rules/cli.md`: 0 success, 1 user/config error
    (including hard-rejected bodies), 2 system/IO error (gh subprocess
    failure). Non-zero exits raise ``SystemExit`` so the CLI dispatcher in
    ``gzkit/cli/main.py`` propagates them.
    """
    slug = derive_consumer_slug()
    version = derive_gzkit_version()
    composed = compose_body(body, slug, version)

    try:
        validate_gzkit_surface_reference(body)
    except IssueValidationError as exc:
        console.print(f"[red]error:[/red] {exc}")
        raise SystemExit(1) from exc

    if dry_run:
        console.print(f"Target: {GZKIT_REPO}")
        console.print(f"Label: {label}")
        console.print(f"Title: {title}")
        console.print("Body:")
        console.print(composed)
        return

    result = subprocess.run(
        [
            "gh",
            "issue",
            "create",
            "--repo",
            GZKIT_REPO,
            "--title",
            title,
            "--body",
            composed,
            "--label",
            label,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    if result.returncode != 0:
        raise SystemExit(2)
