"""Refuse a push whose commit messages carry a GitHub closing keyword (GHI #1327).

A GHI closes only after a reviewer that did not do the fix confirms it on the issue
(AGENTS.md § Defect-fix routing). GitHub closes an issue as soon as a pushed commit
says ``close``, ``fix`` or ``resolve`` (or a variant) followed by its reference:
``d0a9b2ffe`` read ``direct fix: #1318, #1321, #1324`` and closed all three
unreviewed on 2026-11-13. The house subject shape ``fix(<scope>): … (GHI #N)`` stays
legal, since GitHub needs the reference right after the keyword.

It runs at pre-push, over the commits being pushed (pre-commit's
``PRE_COMMIT_FROM_REF``..``PRE_COMMIT_TO_REF``), because GitHub acts only on pushed
commits and the pre-push stage is installed in every clone.

Mode contract (``.gzkit/rules/mode-contract.md``): on at the operational condition,
the hangar and the drydock alike; it never routes through ``gzkit.mx.alarms``,
because a wrongly closed issue is outside the repository and no exit re-run can
restore it. MEL: none (no bypass); self-test: ``tests/hooks/test_closing_keywords.py``
on every change that touches it.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

from gzkit.executables import resolve_executable

#: A closing keyword followed, after an optional colon, by an issue reference:
#: ``#N``, ``owner/repo#N`` or an issue URL (GitHub's linking-keyword grammar).
_CLOSING = re.compile(
    r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\b:?[ \t]+"
    r"(?:[\w.-]+/[\w.-]+#\d+|#\d+|https://github\.com/[\w.-]+/[\w.-]+/issues/\d+)",
    re.IGNORECASE,
)
_NO_COMMIT = "0" * 40


def closing_references(message: str) -> list[str]:
    """Return each closing keyword and reference *message* carries, in order.

    Returns:
        The matched text of each closing reference; empty when there is none.

    """
    return [match.group(0) for match in _CLOSING.finditer(message)]


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(  # noqa: S603 — fixed git argv over refs pre-commit supplies
        [resolve_executable("git"), *args],
        cwd=repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    ).stdout


def _pushed_range() -> list[str]:
    """Return the ``git log`` arguments naming the commits being pushed.

    With no starting ref (a new branch, or a run outside pre-commit), the commits
    are those on no remote, never the whole reachable history, which already
    holds commits pushed before this check existed.

    Returns:
        The revision arguments for ``git log``.

    """
    to_ref = os.environ.get("PRE_COMMIT_TO_REF") or "HEAD"
    from_ref = os.environ.get("PRE_COMMIT_FROM_REF") or ""
    if from_ref and from_ref != _NO_COMMIT:
        return [f"{from_ref}..{to_ref}"]
    return [to_ref, "--not", "--remotes"]


def main(repo: Path | None = None) -> int:
    """Check the commits being pushed; print each offender to stderr.

    Returns:
        1 when any pushed commit message carries a closing reference, else 0.

    """
    root = repo or Path.cwd()
    log = _git(root, "log", "--format=%H%x00%B%x1e", *_pushed_range())
    offenders = []
    for record in filter(None, (chunk.strip() for chunk in log.split("\x1e"))):
        sha, _, message = record.partition("\x00")
        offenders += [(sha[:12], found) for found in closing_references(message)]
    for sha, found in offenders:
        print(f"{sha}: '{found}' would close the issue on push (GHI #1327)", file=sys.stderr)  # noqa: T201
    if offenders:
        print(  # noqa: T201
            "A GHI closes only after a reviewer confirms it on the issue (AGENTS.md § Defect-fix "
            "routing), and GitHub would close these on push. Reword each message, writing "
            "'(GHI #N)' in place of the keyword: `git commit --amend` for the latest commit, "
            "`git rebase -i <sha>^` for an earlier one; then push again.",
            file=sys.stderr,
        )
    return 1 if offenders else 0


if __name__ == "__main__":
    raise SystemExit(main())
