"""`gz ledger merge-driver` — git merge driver for append-only JSONL (GHI #811).

Git invokes this, not an operator. It is registered as a merge driver in
`.gitattributes` plus local git config, and git passes it the three sides of a
conflict; the merged result must be written back over the "ours" path.

Its reason to exist is that resolving a ledger conflict by hand is the action
`AGENTS.md` § Behavior Rules prohibits ("Write the ledger only through `gz`
commands"), and no `gz` verb could do it instead. The
merge itself lives in `gzkit.ledger_merge`; this module is the git-facing
adapter — file IO and exit status, no ordering logic.
"""

from pathlib import Path

from gzkit.commands.common import console
from gzkit.ledger_merge import merge_append_only
from gzkit.utils import git_cmd

MERGE_DRIVER_NAME = "gzkit-jsonl"
_DRIVER_COMMAND = "uv run gz ledger merge-driver %O %A %B"

#: The append-only JSONL gzkit writes, each routed to the driver by a
#: `.gitattributes` line. gzkit's own `.gitattributes` carries the same set;
#: `tests/test_ledger_merge_driver.py` holds the two together.
JSONL_MERGE_PATTERNS = (
    ".gzkit/ledger.jsonl",
    ".gzkit/insights/agent-insights.jsonl",
    ".gzkit/corpus/*.jsonl",
)


def _routes_to_driver(line: str, pattern: str) -> bool:
    """Whether one `.gitattributes` line routes `pattern` to the driver.

    A pattern containing a slash is matched from the repository root, so a
    leading `/` names the same file. The match is textual: a later line that
    overrides this one is the adopter's rule and stands.

    Returns:
        True when the line's pattern is `pattern` and it sets `merge=gzkit-jsonl`.

    """
    fields = line.split()
    return (
        bool(fields)
        and fields[0].removeprefix("/") == pattern
        and f"merge={MERGE_DRIVER_NAME}" in fields[1:]
    )


def ensure_jsonl_merge_attributes(project_root: Path, *, dry_run: bool = False) -> list[str]:
    """Route gzkit's append-only JSONL to the merge driver in `.gitattributes` (GHI #1363).

    The driver registered in local config does nothing until a `.gitattributes`
    line routes a file to it, and an adopter's repository carries no such line
    of gzkit's. Each missing routing line is appended; the existing bytes are
    never rewritten or re-encoded, so the adopter's own rules stand, and a second
    call adds nothing.

    Returns:
        The patterns whose routing line this call added, or would add on a dry run.

    """
    path = project_root / ".gitattributes"
    existing = path.read_bytes() if path.is_file() else b""
    # Decoding only reads the patterns; the write below appends and never re-encodes.
    lines = existing.decode("utf-8", errors="replace").removeprefix("\ufeff").splitlines()
    missing = [
        pattern
        for pattern in JSONL_MERGE_PATTERNS
        if not any(_routes_to_driver(line, pattern) for line in lines)
    ]
    if missing and not dry_run:
        newline = b"\r\n" if b"\r\n" in existing else b"\n"
        separator = newline if existing and not existing.endswith(b"\n") else b""
        added = b"".join(
            f"{pattern} merge={MERGE_DRIVER_NAME}".encode() + newline for pattern in missing
        )
        with path.open("ab") as handle:
            handle.write(separator + added)
    return missing


def jsonl_merge_driver_missing(project_root: Path) -> bool:
    """Whether a git worktree here lacks the driver command, read without writing.

    Returns:
        True inside a git worktree whose local config lacks the driver command;
        False when it is configured or `project_root` is not a git worktree.

    """
    rc_tree, inside, _err = git_cmd(project_root, "rev-parse", "--is-inside-work-tree")
    if rc_tree != 0 or inside.strip() != "true":
        return False
    rc_read, existing, _err = git_cmd(
        project_root, "config", "--get", f"merge.{MERGE_DRIVER_NAME}.driver"
    )
    return rc_read != 0 or existing.strip() != _DRIVER_COMMAND


def ensure_jsonl_merge_driver(project_root: Path) -> bool:
    """Register the append-only merge driver in local git config if absent.

    Returns True when this call installed it, False when it was already there.

    Registration cannot ride in `.gitattributes` with the rest of the rule: git
    reads the driver *command* from config only, and config is per-clone and
    uncommittable. So the attribute is committed (`ensure_jsonl_merge_attributes`
    writes it) and the command has to be seeded by something that runs in the
    clone — `gz init` for new ones, and `gz git-sync` for every clone that
    already exists, which is also the exact moment the driver is about to be needed.

    Returns:
        True when this call installed the driver; False when it was already
        configured or the write failed, as outside a git repository.

    """
    key = f"merge.{MERGE_DRIVER_NAME}.driver"
    rc_read, existing, _err = git_cmd(project_root, "config", "--get", key)
    if rc_read == 0 and existing.strip() == _DRIVER_COMMAND:
        return False

    rc_write, _out, _err = git_cmd(project_root, "config", key, _DRIVER_COMMAND)
    if rc_write != 0:
        return False
    git_cmd(
        project_root,
        "config",
        f"merge.{MERGE_DRIVER_NAME}.name",
        "gzkit append-only JSONL union (timestamp-ordered)",
    )
    return True


def _read_rows(path: Path) -> list[str]:
    """Read a JSONL side as rows, tolerating a missing trailing newline."""
    text = path.read_text(encoding="utf-8")
    return [line for line in text.split("\n") if line.strip()]


def ledger_merge_driver_cmd(ancestor: str, ours: str, theirs: str) -> None:
    """Reconcile a conflicted append-only JSONL file in place.

    Writes the merged rows over `ours` (git's output path) and returns normally
    on success. Raises SystemExit(1) when the merge is outside the append-only
    contract, which tells git to leave the conflict for a human — the safe
    direction, since refusing never destroys evidence.
    """
    ours_path = Path(ours)
    merged = merge_append_only(
        _read_rows(Path(ancestor)),
        _read_rows(ours_path),
        _read_rows(Path(theirs)),
    )

    if merged is None:
        console.print(
            "[yellow]gz ledger merge-driver: cannot merge automatically.[/yellow]\n"
            "A side did more than add rows — an ancestor row was edited or "
            "removed, a row carries no sortable `ts`, or the ancestor's own rows "
            "are not ts-ordered. An addition never lands here, wherever in the "
            "file it sits. Left as a conflict for you to resolve; resolve it as "
            "a timestamp-ordered union, never by appending one side to the other."
        )
        raise SystemExit(1)

    # LF regardless of platform: `.gitattributes` pins `* text=auto eol=lf`, so
    # the working tree is LF and a CRLF write here would dirty every row.
    ours_path.write_text("\n".join(merged) + "\n", encoding="utf-8", newline="\n")
