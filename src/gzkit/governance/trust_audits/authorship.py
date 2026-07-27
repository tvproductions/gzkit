"""Commit-authorship policy audit (GHI #725).

``AGENTS.md`` § Local Agent Rules forbids the operator's personal email in any
repo-bound artifact and prices a breach at a filter-repo rewrite plus a
force-push. Before this audit the only enforcement was a hand-added ``--local``
git config override living in one clone — machine state the repository can
neither see, provision, nor verify. A fresh clone, a worktree, a second machine,
or a CI checkout that commits reverts to global config, and the rule breaks with
no signal until the commit already exists.

Two deliberate design choices:

**Detect, do not configure.** The audit never writes git config.
``commands/init_cmd.py:467`` already declines to touch an operator's git config
("Unsetting an operator's git config is not init's call"), and reaching into a
developer's machine to set an identity is a bigger intrusion than refusing to
push. Refusing is also strictly stronger — it binds every clone, including the
ones a provisioning step never ran in.

**Opt-in, not imposed.** With no ``authorship.required_email_suffix`` declared
the audit is a no-op. gzkit ships to adopters, and a gzkit-shaped identity rule
enforced on every adopter is precisely the dogfooding-leak complaint open at
GHI #607. Projects that want the guard declare it in ``.gzkit.json``.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.core.validation_rules import ValidationError

_AUDIT_TYPE = "authorship_policy"
_ARTIFACT = "git config user.email"


def evaluate_authorship(
    effective_email: str | None, required_suffix: str | None
) -> list[ValidationError]:
    """Judge an effective git identity against a declared policy.

    Pure: takes the resolved address and the policy as parameters rather than
    naming git or the config file (hexagonal § Operative rule 4), so the
    decision is exercisable without a repository, a subprocess, or a machine
    whose global config happens to be set one way.

    Args:
        effective_email: The address git would stamp on a commit, or ``None``
            when no identity resolves at all.
        required_suffix: The declared policy, or ``None`` when the project
            declares none — in which case every address is admitted.

    Returns:
        Zero or one ``ValidationError``. Never echoes ``effective_email``: a
        finding that reproduces the address writes the PII it exists to contain
        into CI logs and ARB receipts.

    """
    if required_suffix is None:
        return []
    if effective_email is not None and effective_email.endswith(required_suffix):
        return []

    observed = "no git identity resolves" if not effective_email else "does not end with it"
    return [
        ValidationError(
            type=_AUDIT_TYPE,
            artifact=_ARTIFACT,
            message=(
                f"Commit authorship policy requires an address ending '{required_suffix}' "
                f"({observed}; the address is withheld here rather than reprinted into "
                "logs and receipts). AGENTS.md § Local Agent Rules forbids the operator's "
                "personal email in any repo-bound artifact — commits, trailers, "
                "attestation text — and a leak needs a filter-repo rewrite plus a "
                "force-push to recover. Next step: "
                f"`git config --local user.email '<handle>{required_suffix}'` in this "
                "clone, then re-run `uv run gz validate --authorship`."
            ),
        )
    ]


def _effective_email(project_root: Path) -> str | None:
    """Return the address git would stamp here, honoring local > global > system."""
    try:
        result = subprocess.run(
            ["git", "config", "--get", "user.email"],
            cwd=project_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None


def audit_authorship(project_root: Path) -> list[ValidationError]:
    """Assert this clone's git identity satisfies the project's declared policy.

    Adapter around :func:`evaluate_authorship`: resolves the policy from
    ``.gzkit.json`` and the effective address from git, then delegates the
    judgment.
    """
    config = GzkitConfig.load(project_root / ".gzkit.json")
    required = config.authorship.required_email_suffix
    if not required:
        return []
    return evaluate_authorship(_effective_email(project_root), required)
