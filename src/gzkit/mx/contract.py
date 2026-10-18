"""Pin the safe-mode contract in the ledger: at entry, and on every amendment.

Operator ruling 2026-10-18, selecting "Hash at entry + amend event" (requirements model
§ 11, maxim 14: "A stop has an entry condition, a named set of rules switched off, and an
exit condition, all in one ledger record"). The 2026-10-17 entry recorded the contract's
path only, and the contract was rewritten three hours later, so the ledger could not say
which suspensions and exit conditions were in force. Entry now carries the contract's
hash and the bodies of its § What is suspended and § Exit sections; a committed edit
while the session is open books ``mx_contract_amended`` with the new hash. Edits stay
allowed; each is recorded.

The commit is the locus, as for ``gzkit.hooks.commit_ledger``: an edit never committed
has no state to observe and is not booked.
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

from gzkit.ledger import Ledger, LedgerEvent
from gzkit.mx import marker

AMENDED_EVENT = "mx_contract_amended"
_OPENED_EVENT = "mx_session_opened"
_LEDGER_RELPATH = (".gzkit", "ledger.jsonl")
_SUSPENDED_HEADING = "## What is suspended"
_EXIT_HEADING = "## Exit"


def contract_section(text: str, heading_prefix: str) -> str:
    """Return the body of the first ``## `` section whose heading starts with the prefix."""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith(heading_prefix):
            body: list[str] = []
            for following in lines[index + 1 :]:
                if following.startswith("## "):
                    break
                body.append(following)
            return "\n".join(body).strip()
    return ""


def contract_pin(text: str) -> dict[str, str]:
    """Return the fields that pin one version of a contract: its hash and two bodies."""
    return {
        "contract_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "contract_suspended": contract_section(text, _SUSPENDED_HEADING),
        "contract_exit": contract_section(text, _EXIT_HEADING),
    }


def contract_pin_for(path: Path) -> dict[str, str]:
    """Pin the contract file at ``path`` as it reads now (the entry pin)."""
    return contract_pin(path.read_text(encoding="utf-8"))


def _pinned_digest(ledger: Ledger, session_id: str) -> str | None:
    """Return the hash last pinned for the session: its entry or latest amendment."""
    pinned: str | None = None
    for event in ledger.read_all():
        if event.extra.get("session_id") != session_id:
            continue
        if event.event in (_OPENED_EVENT, AMENDED_EVENT):
            pinned = event.extra.get("contract_sha256") or pinned
    return pinned


def book_contract_amendment(root: Path, text: str, *, commit: str | None = None) -> bool:
    """Book ``mx_contract_amended`` when ``text`` differs from the session's pinned contract.

    Returns ``True`` when an amendment was booked. Nothing is booked unless a valid
    safe-mode session is open under a contract.
    """
    held = marker.read(root)
    if held is None or held.mode != "safe" or not held.contract or not marker.is_valid(root):
        return False
    ledger = Ledger(root.joinpath(*_LEDGER_RELPATH))
    pin = contract_pin(text)
    previous = _pinned_digest(ledger, held.session_id)
    if previous == pin["contract_sha256"]:
        return False
    extra: dict[str, str] = {
        "session_id": held.session_id,
        "contract": held.contract,
        **pin,
        "previous_sha256": previous or "",
    }
    if commit is not None:
        extra["commit"] = commit
    ledger.append(LedgerEvent(event=AMENDED_EVENT, id=held.session_id, extra=extra))
    return True


def _git(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError:
        return None
    return result.stdout if result.returncode == 0 else None


def book_committed_contract_amendment(root: Path, rev: str = "HEAD") -> bool:
    """Book the open session's contract as committed at ``rev``, when it changed."""
    held = marker.read(root)
    if held is None or held.mode != "safe" or not held.contract:
        return False
    text = _git(root, "show", f"{rev}:{held.contract}")
    if text is None:
        return False
    commit = (_git(root, "rev-parse", rev) or "").strip() or None
    return book_contract_amendment(root, text, commit=commit)
