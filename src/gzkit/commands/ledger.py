"""`gz ledger merge-driver` — git merge driver for append-only JSONL (GHI #811).

Git invokes this, not an operator. It is registered as a merge driver in
`.gitattributes` plus local git config, and git passes it the three sides of a
conflict; the merged result must be written back over the "ours" path.

Its reason to exist is that resolving a ledger conflict by hand is the action
`AGENTS.md` § Never #2 prohibits, and no `gz` verb could do it instead. The
merge itself lives in `gzkit.ledger_merge`; this module is the git-facing
adapter — file IO and exit status, no ordering logic.
"""

from pathlib import Path

from gzkit.commands.common import console
from gzkit.ledger_merge import merge_append_only
from gzkit.utils import git_cmd

MERGE_DRIVER_NAME = "gzkit-jsonl"
_DRIVER_COMMAND = "uv run gz ledger merge-driver %O %A %B"


def ensure_jsonl_merge_driver(project_root: Path) -> bool:
    """Register the append-only merge driver in local git config if absent.

    Returns True when this call installed it, False when it was already there.

    Registration cannot ride in `.gitattributes` with the rest of the rule: git
    reads the driver *command* from config only, and config is per-clone and
    uncommittable. So the attribute ships in the repo and the command has to be
    seeded by something that runs in the clone — `gz init` for new ones, and
    `gz git-sync` for every clone that already exists, which is also the exact
    moment the driver is about to be needed.
    """
    key = f"merge.{MERGE_DRIVER_NAME}.driver"
    rc_read, existing, _err = git_cmd(project_root, "config", "--get", key)
    if rc_read == 0 and existing.strip() == _DRIVER_COMMAND:
        return False

    git_cmd(project_root, "config", key, _DRIVER_COMMAND)
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
            "The sides are not disjoint appends — a row was edited, removed, or "
            "carries no sortable `ts`. Left as a conflict for you to resolve; "
            "resolve it as a timestamp-ordered union, never by appending one "
            "side to the other."
        )
        raise SystemExit(1)

    # LF regardless of platform: `.gitattributes` pins `* text=auto eol=lf`, so
    # the working tree is LF and a CRLF write here would dirty every row.
    ours_path.write_text("\n".join(merged) + "\n", encoding="utf-8", newline="\n")
