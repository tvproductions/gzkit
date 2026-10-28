"""The repair tagging scheme on GitHub (drydock RO-5 tranche 3).

`docs/governance/harbor-ro5-work-packages.md` ruling 7: every issue attached to a
repair package carries the one `repair` label, and the attaching verb comments the
package id on it, aliases in parentheses (`WP-07-astral-toolchain (RO-9)`). The
label is created when the repository lacks it (operator, 2026-10-28: "Verb ensures
it (Recommended)"). This module is the one adapter over `gh`; the store and the
ledger writers never name it.
"""

import json
import subprocess

from gzkit.executables import resolve_executable

REPAIR_LABEL = "repair"
_LABEL_DESCRIPTION = "Carried by a repair work package (RO-5)"
_LABEL_COLOR = "b60205"


class WorkPackageGithubError(RuntimeError):
    """A `gh` call failed; the caller writes nothing on it."""


def package_mark(work_package: str, aliases: tuple[str, ...]) -> str:
    """Return the package id with its aliases, as ruling 7 spells it.

    Returns:
        `WP-<NN>-<slug>`, followed by `(RO-n, ...)` when the package has aliases.

    """
    return f"{work_package} ({', '.join(aliases)})" if aliases else work_package


def _gh(*args: str) -> str:
    """Run one `gh` call.

    Returns:
        Its standard output.

    Raises:
        WorkPackageGithubError: The call failed or `gh` is not installed.

    """
    try:
        result = subprocess.run(  # noqa: S603 - gh with fixed subcommands and the package's fields
            [resolve_executable("gh"), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except FileNotFoundError as exc:
        msg = "gh is not on PATH; install the GitHub CLI and run `gh auth login`."
        raise WorkPackageGithubError(msg) from exc
    if result.returncode != 0:
        msg = f"`gh {' '.join(args[:3])}` failed: {result.stderr.strip() or result.returncode}"
        raise WorkPackageGithubError(msg)
    return result.stdout


def _ensure_repair_label() -> None:
    listed = json.loads(_gh("label", "list", "--search", REPAIR_LABEL, "--json", "name") or "[]")
    if REPAIR_LABEL not in {label["name"] for label in listed}:
        _gh(
            "label", "create", REPAIR_LABEL,
            "--description", _LABEL_DESCRIPTION, "--color", _LABEL_COLOR,
        )  # fmt: skip


def tag_issues(work_package: str, aliases: tuple[str, ...], issues: tuple[int, ...]) -> None:
    """Label each issue `repair` and comment the package's mark on it.

    A failed `gh` call, or `gh` missing, stops the run with `WorkPackageGithubError`.
    """
    if not issues:
        return
    _ensure_repair_label()
    body = f"Attached to repair work package {package_mark(work_package, aliases)}."
    for issue in issues:
        _gh("issue", "edit", str(issue), "--add-label", REPAIR_LABEL)
        _gh("issue", "comment", str(issue), "--body", body)
