"""Lock-handoff coupling validator (ADR-0.0.41 / OBPI-04).

Replays `.gzkit/ledger.jsonl` via the canonical `Ledger.read_all()` surface
and fail-closes on any `obpi_lock_released` event (post-OBPI-02 cutover)
whose `handoff_path` payload is missing, references a nonexistent file,
predates the matching claim, or whose register entry violates Sub-Invariant 2's
minimum-information rule (last_lock_event_timestamp, last_commit_sha, branch,
## Decisions Made section).

Cutover detection: the timestamp of the `obpi_receipt_emitted` event whose `id`
matches `OBPI-0.0.41-02-*`; derived from ledger at init, never hardcoded.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

from gzkit.core.validation_rules import ValidationError
from gzkit.handoff_validation import CHECKPOINT_MODE

# Use the latest of OBPI-02 (additive/warning) or OBPI-03 (fail-closed) as the
# effective enforcement cutover. This grandfathers the warning-only transition
# period between OBPI-02 and OBPI-03 when handoff_path was not yet required.
_CUTOVER_ID_PREFIXES = ("OBPI-0.0.41-02-", "OBPI-0.0.41-03-")
_DECISIONS_RE = re.compile(r"^##\s+Decisions\s+Made", re.MULTILINE | re.IGNORECASE)
_MIN_INFO_FRONTMATTER_FIELDS = ("last_lock_event_timestamp", "last_commit_sha", "branch")


def validate_lock_handoff_coupling(project_root: Path) -> list[ValidationError]:
    """Replay the ledger and fail-close on broken release/handoff couplings."""
    from gzkit.ledger import Ledger  # noqa: PLC0415

    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.exists():
        return []

    events = Ledger(ledger_path).read_all()
    cutover_ts = _find_cutover_ts(events)
    if cutover_ts is None:
        return []

    claims = _index_claims(events)
    index = _git_index_paths(project_root)
    errors: list[ValidationError] = []
    for ev in events:
        if ev.event != "obpi_lock_released":
            continue
        ev_ts = _parse_ts(ev.ts)
        if ev_ts is None or ev_ts < cutover_ts:
            continue
        obpi_id = ev.id
        agent = str(ev.extra.get("agent", ""))
        handoff_path_rel = ev.extra.get("handoff_path")
        if not handoff_path_rel:
            errors.append(
                ValidationError(
                    type="lock_handoff_coupling",
                    artifact=obpi_id,
                    message=(
                        f"obpi_lock_released event for {obpi_id!r} (agent={agent!r}, "
                        f"ts={ev.ts!r}) is missing required handoff_path payload. "
                        f"Run gz-session-handoff before releasing the lock."
                    ),
                )
            )
            continue
        handoff_abs = project_root / str(handoff_path_rel)
        if not handoff_abs.exists():
            errors.append(
                ValidationError(
                    type="lock_handoff_coupling",
                    artifact=obpi_id,
                    message=(
                        f"obpi_lock_released event for {obpi_id!r} (agent={agent!r}, "
                        f"ts={ev.ts!r}) references handoff_path {handoff_path_rel!r} "
                        f"which does not exist on disk."
                    ),
                )
            )
            continue
        if index is not None and str(handoff_path_rel).replace("\\", "/") not in index:
            errors.append(
                ValidationError(
                    type="lock_handoff_coupling",
                    artifact=obpi_id,
                    message=(
                        f"obpi_lock_released event for {obpi_id!r} (agent={agent!r}, "
                        f"ts={ev.ts!r}) references handoff_path {handoff_path_rel!r} "
                        f"which exists on disk but is NOT in git's index. A register "
                        f"entry that lives only in one working tree is the 'memory is "
                        f"not evidence' clause this validator enforces — it vanishes "
                        f"with the checkout and cannot be read by any other party. "
                        f"Stage it (`git add`) or commit it (GHI #759)."
                    ),
                )
            )
            continue
        try:
            handoff_content = handoff_abs.read_text(encoding="utf-8")
        except OSError:
            errors.append(
                ValidationError(
                    type="lock_handoff_coupling",
                    artifact=obpi_id,
                    message=(
                        f"obpi_lock_released event for {obpi_id!r}: handoff at "
                        f"{handoff_path_rel!r} could not be read."
                    ),
                )
            )
            continue
        claim_ts = _concluded_claim_ts(claims.get(obpi_id, []), ev_ts)
        errors.extend(_check_timestamp(obpi_id, agent, ev.ts, handoff_content, claim_ts))
        errors.extend(_check_min_info(obpi_id, agent, ev.ts, handoff_content))
        errors.extend(_check_mode(obpi_id, agent, ev.ts, handoff_content))

    return errors


def _git_index_paths(project_root: Path) -> frozenset[str] | None:
    """Every path in git's index, or None when git cannot answer (GHI #759).

    "In the index" is the durability test, not "on disk". A file that exists only
    in one working tree is exactly what token-block § Doctrine Foundation excludes
    when it says *"memory is not evidence"* — it vanishes with the checkout and no
    second party or later audit can read it. The `Path.exists()` test this sits
    beside cannot see that difference, which is how a `handoff_path` was committed
    to the ledger with no referent in a fresh clone while `gz check` exited 0.

    STAGED counts, by operator ruling 2026-08-05 (*"staged counts as durable"*).
    `git ls-files` lists index entries, so a `git add`-ed file is reported before
    any commit — which is precisely what makes the exit beat's staging sufficient.

    Returns None rather than an empty set when git is unavailable, and the caller
    SKIPS the check on None instead of failing every path. Distinguishing them is
    the point: an empty set means git answered "nothing is tracked" and every
    reference is genuinely undurable; None means we do not know, and failing a
    whole governance run because git is missing would be a false alarm of the kind
    that gets a check disabled. The `exists()` arm still binds either way.
    """
    from gzkit.utils import git_cmd  # noqa: PLC0415 — avoids an import cycle at module load

    try:
        rc, out, _ = git_cmd(project_root, "ls-files")
    except (OSError, ValueError):
        return None
    if rc != 0:
        return None
    return frozenset(line.strip() for line in out.splitlines() if line.strip())


def _find_cutover_ts(events: list) -> datetime | None:
    """Return the latest OBPI-02 or OBPI-03 completion receipt timestamp, or None."""
    cutover: datetime | None = None
    for ev in events:
        if ev.event != "obpi_receipt_emitted":
            continue
        if not any(ev.id.startswith(p) for p in _CUTOVER_ID_PREFIXES):
            continue
        ts = _parse_ts(ev.ts)
        if ts is not None and (cutover is None or ts > cutover):
            cutover = ts
    return cutover


def _index_claims(events: list) -> dict[str, list[datetime]]:
    """Build per-OBPI ascending-sorted claim timestamps for concluded-claim matching.

    Keyed by ``obpi_id`` only (not ``(obpi_id, agent)``): a release concludes the
    active claim regardless of which agent claimed it, so a cross-agent force-reap
    must pair against the reaped claim, not the reaper's own later claim.
    """
    index: dict[str, list[datetime]] = {}
    for ev in events:
        if ev.event != "obpi_lock_claimed":
            continue
        ts = _parse_ts(ev.ts)
        if ts is None:
            continue
        index.setdefault(ev.id, []).append(ts)
    for claim_tss in index.values():
        claim_tss.sort()
    return index


def _concluded_claim_ts(claim_tss: list[datetime], release_ts: datetime) -> datetime | None:
    """Return the claim a release concludes — the latest at or before the release timestamp.

    Pairing by concluded claim (not the releasing agent's newest claim) keeps
    abandon-then-reclaim and cross-agent force-reap sequences valid, while still
    flagging a handoff that genuinely predates the claim it concluded.
    """
    prior = [ts for ts in claim_tss if ts <= release_ts]
    return prior[-1] if prior else None


def _check_timestamp(
    obpi_id: str,
    agent: str,
    release_ts: str,
    content: str,
    claim_ts: datetime | None,
) -> list[ValidationError]:
    """Return an error when handoff frontmatter timestamp predates the matching claim."""
    if claim_ts is None:
        return []
    handoff_ts_str = _parse_frontmatter_field(content, "timestamp")
    if handoff_ts_str is None:
        return []
    handoff_ts = _parse_ts(handoff_ts_str)
    if handoff_ts is None:
        return []
    if handoff_ts < claim_ts:
        return [
            ValidationError(
                type="lock_handoff_coupling",
                artifact=obpi_id,
                message=(
                    f"obpi_lock_released event for {obpi_id!r} (agent={agent!r}, "
                    f"ts={release_ts!r}): handoff timestamp {handoff_ts_str!r} "
                    f"predates the matching claim at {claim_ts.isoformat()!r}."
                ),
            )
        ]
    return []


def _check_min_info(
    obpi_id: str,
    agent: str,
    release_ts: str,
    content: str,
) -> list[ValidationError]:
    """Return one ValidationError per missing Sub-Invariant 2 minimum-information field."""
    errors: list[ValidationError] = []
    for field in _MIN_INFO_FRONTMATTER_FIELDS:
        value = _parse_frontmatter_field(content, field)
        if not value:
            errors.append(
                ValidationError(
                    type="lock_handoff_coupling",
                    artifact=obpi_id,
                    message=(
                        f"obpi_lock_released event for {obpi_id!r} (agent={agent!r}, "
                        f"ts={release_ts!r}): handoff missing Sub-Invariant 2 field "
                        f"{field!r}."
                    ),
                )
            )
    if not _DECISIONS_RE.search(content):
        errors.append(
            ValidationError(
                type="lock_handoff_coupling",
                artifact=obpi_id,
                message=(
                    f"obpi_lock_released event for {obpi_id!r} (agent={agent!r}, "
                    f"ts={release_ts!r}): handoff missing '## Decisions Made' "
                    f"section (Sub-Invariant 2 decision context field)."
                ),
            )
        )
    return errors


def _check_mode(
    obpi_id: str,
    agent: str,
    release_ts: str,
    content: str,
) -> list[ValidationError]:
    """Return an error when the cited register entry is a mid-flight bookmark.

    A ``CHECKPOINT`` handoff records that a session paused, not that it
    surrendered its token (GHI #756). ``find_handoff_for_release`` refuses one
    at the live gate; this is the ledger-replay backstop for a release whose
    ``handoff_path`` was resolved by any other route.
    """
    mode = (_parse_frontmatter_field(content, "mode") or "").upper()
    if mode != CHECKPOINT_MODE:
        return []
    return [
        ValidationError(
            type="lock_handoff_coupling",
            artifact=obpi_id,
            message=(
                f"obpi_lock_released event for {obpi_id!r} (agent={agent!r}, "
                f"ts={release_ts!r}) cites a {CHECKPOINT_MODE} handoff. A "
                "mid-flight bookmark is not a token surrender (token-block "
                "discipline § Sub-Invariant 5). Author a departure handoff via "
                "the `gz-session-handoff` skill, or surrender explicitly with "
                "`gz obpi lock release --abandon <category>:<reason>`."
            ),
        )
    ]


def _parse_frontmatter_field(content: str, key: str) -> str | None:
    """Extract one key from YAML frontmatter block."""
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    in_block = False
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            if not in_block:
                in_block = True
                continue
            break
        if ":" not in line:
            continue
        raw_key, _, raw_value = line.partition(":")
        if raw_key.strip() != key:
            continue
        return raw_value.strip().strip("\"'")
    return None


def _parse_ts(value: str | None) -> datetime | None:
    """Parse ISO-8601 timestamp (accepting Z or +00:00 suffix) to aware UTC."""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed
