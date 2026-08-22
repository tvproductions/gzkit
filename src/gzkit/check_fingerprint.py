"""Content fingerprint of the working tree, so a passing gate is not re-run (GHI #835).

``gz check`` costs ~148s, and a fix pays it TWICE: once when the agent verifies,
then again when ``git push`` fires the pre-push gate over a tree that has not
changed since. The second run cannot reach a different verdict — same content,
same commands — so it is pure latency on every commit.

The fingerprint is the INDEX tree — deliberately neither ``HEAD`` nor the
working tree, and both alternatives were tried:

* ``HEAD`` fails because a commit is created between verify and push, so it
  always differs while the files do not, and the skip would never fire.
* The WORKING tree fails for the mirror reason. ``pre-commit`` stashes unstaged
  changes while hooks execute, so a pre-push hook observes HEAD-plus-staged and
  never the working tree. Measured 2026-08-22 against this repo, where
  ``.gzkit/ledger.jsonl`` is dirty on essentially every run because governance
  commands append to it: the first cut of this module fingerprinted the working
  tree, passed all its own tests on clean fixtures, and skipped exactly zero
  real pushes.

The index is what survives the stash and what a commit will carry, so it is the
object both sides can agree on. The real index is never mutated — it is copied
to a throwaway path and read there.

Fail-open by construction: any git failure returns ``None``, and a ``None``
fingerprint never matches, so the gate runs. A fingerprint mechanism that fails
CLOSED would refuse pushes on a repo it merely could not read.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

#: Gitignored per `.gitignore` (`.gzkit/cache/`), so the receipt never ships.
_RECEIPT_REL = Path(".gzkit") / "cache" / "check-verified.json"

_GIT_TIMEOUT_S = 120


def _git_raw(args: list[str], cwd: Path, env: dict[str, str] | None = None) -> str | None:
    """Return stdout of ``git <args>`` VERBATIM, or None when git fails.

    Column-significant output (``status --porcelain``) must not be stripped.
    """
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            timeout=_GIT_TIMEOUT_S,
            env=env,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout if result.returncode == 0 else None


def _git(args: list[str], cwd: Path, env: dict[str, str] | None = None) -> str | None:
    """Return stripped stdout of ``git <args>``, or None when git fails or is absent."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            timeout=_GIT_TIMEOUT_S,
            env=env,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def tree_is_fully_staged(project_root: Path) -> bool:
    """Return True when nothing is unstaged or untracked — the tree IS the index.

    The recorded claim must be exact. ``gz check`` runs against the WORKING tree,
    while the fingerprint names the INDEX tree, and those are the same object only
    when nothing is outstanding. Recording otherwise would attest a tree that was
    never the one tested.
    """
    # NOT via `_git`: it strips, and porcelain's first column is a SPACE for an
    # unstaged modification (" M path"). Stripping shifts the columns left, so an
    # unstaged edit reads as staged and the tree is wrongly declared recordable.
    status = _git_raw(["status", "--porcelain"], project_root)
    if status is None:
        return False
    for line in status.splitlines():
        if not line.strip():
            continue
        # Column 2 is the worktree-vs-index state; "??" is untracked.
        if line.startswith("??") or (len(line) > 1 and line[1] != " "):
            return False
    return True


def staged_fingerprint(project_root: Path) -> str | None:
    """Return the tree hash of the INDEX — the content a commit would carry.

    Deliberately the index and not the working tree. ``pre-commit`` STASHES
    unstaged changes while hooks execute, so the tree a pre-push hook observes is
    HEAD-plus-staged, never the working tree. A working-tree fingerprint therefore
    never matches at push time in any repository with routine churn — measured
    2026-08-22 against this repo, where ``.gzkit/ledger.jsonl`` is dirty on
    essentially every run because governance commands append to it. The skip
    simply never fired.

    Also not ``HEAD``: a commit is created between verify and push, so a
    HEAD-keyed check would miss for the opposite reason.

    The real index is never mutated — it is copied to a throwaway path and read
    there — so taking a fingerprint can never stage the operator's work.
    """
    git_dir = _git(["rev-parse", "--git-dir"], project_root)
    if git_dir is None:
        return None
    real_index = (project_root / git_dir / "index").resolve()
    if not real_index.is_file():
        return None

    tmp_dir = Path(tempfile.mkdtemp(prefix="gzkit-fp-"))
    tmp_index = tmp_dir / "index"
    try:
        shutil.copy2(real_index, tmp_index)
        env = {**os.environ, "GIT_INDEX_FILE": str(tmp_index)}
        # Drop the receipt so it can never perturb the hash it is recording.
        # `.gitignore` normally covers `.gzkit/cache/`, but relying on that would
        # make the mechanism fail SILENTLY wherever the ignore file differs.
        _git(
            ["rm", "--cached", "--quiet", "--ignore-unmatch", "--", _RECEIPT_REL.as_posix()],
            project_root,
            env=env,
        )
        return _git(["write-tree"], project_root, env=env)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def record_verified(project_root: Path, fingerprint: str | None, *, scope: str) -> None:
    """Record that the FULL gate passed over *fingerprint*. Best-effort.

    Only a full-scope pass is recordable. A scoped run skips the expensive steps
    by design, so recording one would let a partial verification satisfy the gate
    — the presence-check failure ``AGENTS.md`` names, in a new costume.

    Callers pass :func:`staged_fingerprint`, and it is recorded only when
    :func:`tree_is_fully_staged` holds, so the recorded tree is exactly the one
    the gate ran against.
    """
    if fingerprint is None or scope != "full":
        return
    receipt = project_root / _RECEIPT_REL
    try:
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text(
            json.dumps({"fingerprint": fingerprint, "scope": "full"}, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except OSError:
        return


def verified_fingerprint(project_root: Path) -> str | None:
    """Return the fingerprint the last full-scope pass covered, or None."""
    try:
        raw = (project_root / _RECEIPT_REL).read_text(encoding="utf-8")
    except OSError:
        return None
    try:
        payload: Any = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict) or payload.get("scope") != "full":
        return None
    recorded = payload.get("fingerprint")
    return recorded if isinstance(recorded, str) and recorded else None


def already_verified(project_root: Path) -> str | None:
    """Return the fingerprint when THIS tree already passed the full gate.

    Both sides must be present and equal. A missing receipt, an unreadable tree,
    or any difference returns None and the caller runs the gate.
    """
    current = staged_fingerprint(project_root)
    if current is None:
        return None
    return current if current == verified_fingerprint(project_root) else None


__all__ = [
    "already_verified",
    "record_verified",
    "staged_fingerprint",
    "tree_is_fully_staged",
    "verified_fingerprint",
]
