"""Commit-authorship policy audit (GHI #725).

``AGENTS.md`` § Execution Rules forbids the operator's personal email in any
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

import re
import subprocess
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.core.validation_rules import ValidationError
from gzkit.executables import resolve_executable

_AUDIT_TYPE = "authorship_policy"
_ARTIFACT = "git config user.email"

#: The two identities git stamps on a commit, each read through ``git var``, which
#: resolves them as the commit will: ``--author``, an amended commit's author and
#: the ``GIT_AUTHOR_*`` / ``GIT_COMMITTER_*`` variables before config (GHI #1340).
_STAMPED_IDENTITIES = (("author", "GIT_AUTHOR_IDENT"), ("committer", "GIT_COMMITTER_IDENT"))
_IDENT_EMAIL = re.compile(r"<([^<>]*)>")


def evaluate_authorship(
    effective_email: str | None, required_suffix: str | None, *, artifact: str = _ARTIFACT
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
        artifact: The identity judged, named in the finding.

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
            artifact=artifact,
            message=(
                f"Commit authorship policy requires the {artifact} address to end "
                f"'{required_suffix}' ({observed}; the address is withheld here rather "
                "than reprinted into logs and receipts). AGENTS.md § Execution Rules "
                "forbids the operator's personal email in any repo-bound artifact — "
                "commits, trailers, attestation text — and a leak needs a filter-repo "
                "rewrite plus a force-push to recover. Next step: drop any `--author` "
                "or GIT_AUTHOR_EMAIL / GIT_COMMITTER_EMAIL override; when amending a "
                "commit whose author violates the policy, re-author it with "
                "`git commit --amend --reset-author`; and set "
                f"`git config --local user.email '<handle>{required_suffix}'` in this "
                "clone. Then commit again."
            ),
        )
    ]


def _effective_email(project_root: Path, variable: str = "GIT_AUTHOR_IDENT") -> str | None:
    """Return the address git will stamp for *variable*'s identity, or None if none resolves.

    ``git var`` resolves the identity the way the commit will, so an override that
    never touches config is read, not missed (GHI #1340). Inside a pre-commit hook
    git has already exported ``--author`` and an amended commit's author into the
    ``GIT_AUTHOR_*`` variables ``git var`` reads.

    Returns:
        The email of the resolved identity; None when git resolves none or cannot run.

    """
    try:
        result = subprocess.run(  # noqa: S603 — git with a fixed subcommand; executable resolved
            [resolve_executable("git"), "var", variable],
            cwd=project_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError, subprocess.SubprocessError:
        return None
    if result.returncode != 0:
        return None
    match = _IDENT_EMAIL.search(result.stdout)
    return (match.group(1).strip() or None) if match else None


def audit_authorship(project_root: Path) -> list[ValidationError]:
    """Assert the identities a commit here would stamp satisfy the declared policy.

    Adapter around :func:`evaluate_authorship`: resolves the policy from
    ``.gzkit.json`` and the author and committer addresses from ``git var``, then
    delegates the judgment for each (GHI #1340).

    Returns:
        The ``evaluate_authorship`` findings for the author and the committer; empty when no
        email suffix is required.

    """
    config = GzkitConfig.load(project_root / ".gzkit.json")
    required = config.authorship.required_email_suffix
    if not required:
        return []
    return [
        error
        for role, variable in _STAMPED_IDENTITIES
        for error in evaluate_authorship(
            _effective_email(project_root, variable), required, artifact=f"commit {role}"
        )
    ]
