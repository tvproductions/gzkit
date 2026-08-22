"""Content fingerprint of the working tree, so a passing gate is not re-run (GHI #835).

``gz check`` costs ~148s, and a fix pays it TWICE: once when the agent verifies,
then again when ``git push`` fires the pre-push gate over a tree that has not
changed since. The second run cannot reach a different verdict — same content,
same commands — so it is pure latency on every commit.

The fingerprint is the tree's CONTENT, deliberately not ``HEAD``. Between the two
runs a commit is created, so ``HEAD`` always differs while the files do not;
keying on it would make the skip never fire. It is computed by staging the
worktree into a THROWAWAY index and taking that index's tree hash:

* ``.gitignore`` is honoured, so build noise and receipts do not perturb it.
* Staged, unstaged, and untracked content all land in it identically — the same
  property the commit-locus guards rely on (GHI #844/#847).
* The real index is never touched. The temp index is SEEDED from it so git can
  reuse cached stat information instead of re-hashing every file.

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


def _git(args: list[str], cwd: Path, env: dict[str, str] | None = None) -> str | None:
    """Return stdout of ``git <args>``, or None when git fails or is absent."""
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


def worktree_fingerprint(project_root: Path) -> str | None:
    """Return a content hash of the working tree, or None when it cannot be taken.

    None is the honest answer for "not a git repo", "git missing", or any failure
    — and because None never compares equal to a recorded fingerprint, the caller
    falls through to running the gate.
    """
    git_dir = _git(["rev-parse", "--git-dir"], project_root)
    if git_dir is None:
        return None
    real_index = (project_root / git_dir / "index").resolve()

    tmp_dir = Path(tempfile.mkdtemp(prefix="gzkit-fp-"))
    tmp_index = tmp_dir / "index"
    try:
        # Seed from the real index so `add -A` re-hashes only what changed.
        if real_index.is_file():
            shutil.copy2(real_index, tmp_index)
        env = {**os.environ, "GIT_INDEX_FILE": str(tmp_index)}
        if _git(["add", "-A"], project_root, env=env) is None:
            return None
        # Drop the receipt from the temp index so it can never perturb the hash
        # it is recording. `.gitignore` normally covers `.gzkit/cache/`, but
        # relying on that would make the whole mechanism fail SILENTLY in any
        # project whose ignore file differs: writing the receipt would change the
        # tree, the next fingerprint would never match, and the skip would simply
        # never fire with nothing to see. Excluding it explicitly is what makes
        # the property hold by construction rather than by configuration.
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
    current = worktree_fingerprint(project_root)
    if current is None:
        return None
    return current if current == verified_fingerprint(project_root) else None


__all__ = [
    "already_verified",
    "record_verified",
    "verified_fingerprint",
    "worktree_fingerprint",
]
