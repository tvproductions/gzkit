"""Step-4b vocabulary, cross-vendor receipt proof and ledger event.

The refusal itself lives in the acceptance reducer
(``acceptance_store.completion_review`` and ``acceptance_blockers``) since GHI
#985. This module keeps what that path still reads: the verdict vocabulary, the
argv-based cross-vendor proof ``acceptance_store.review_from_receipt`` applies,
and the ``adversarial_validation`` event ``gz obpi complete`` writes. The verdict
gate that once lived here was removed under GHI #1163 after it lost its last
production caller.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from gzkit.ledger import LEDGER_SCHEMA, LedgerEvent

__all__ = [
    "ADVERSARY_VERDICTS",
    "_build_adversarial_event",
    "_is_cross_vendor_adversary",
    "_receipt_binary_name",
    "_receipt_proves_cross_vendor",
]


ADVERSARY_VERDICTS: tuple[str, ...] = (
    "refuted",
    "not-refuted",
    "refuted-with-caveats",
    "degraded-human-only",
)

# Step-4b tier order (GHI #678). Codex (a different vendor) is REQUIRED first
# because a Claude validating Claude shares this agent's blind spots — the exact
# failure 4b exists to break. A named non-Claude vendor is proof of the cross-vendor
# tier-1 property; the set is an explicit allowlist so an unrecognized adversary
# fails CLOSED (must justify the fallback) rather than passing by ambiguity.
_CROSS_VENDOR_ADVERSARY_PREFIXES: tuple[str, ...] = (
    "codex",
    "gpt",
    "openai",
    "gemini",
    "google",
    "grok",
    "xai",
    "llama",
    "meta",
    "mistral",
    "deepseek",
    "qwen",
)


def _is_cross_vendor_adversary(adversary: str) -> bool:
    """Return True when the adversary names a different-vendor (non-Claude) model.

    Cross-vendor is the tier-1 property Step 4b requires: it shares none of this
    agent's blind spots. Detection is an explicit allowlist of vendor prefixes —
    an unrecognized name is treated as NOT cross-vendor so the gate fails closed
    (the caller must justify why Codex was unavailable), never open by ambiguity.
    """
    name = adversary.strip().lower()
    return any(name.startswith(prefix) for prefix in _CROSS_VENDOR_ADVERSARY_PREFIXES)


# Runtime wrappers a dispatch may legitimately front the real binary with. The
# operator's 2026-08-25 directive makes the Codex PLUGIN the only permitted tier-1
# surface and FORBIDS `codex exec`, so every conforming tier-1 run is argv
# ['node', '.../codex-companion.mjs', ...] — and a scan reading argv[0] alone sees
# 'node' and refuses the claim. Both rules landed the same day, which made a tier-1
# claim structurally unclaimable for any OBPI following the directive.
#
# The set is PERMISSIVE — membership needs no individual mandate — but it is no
# longer unwitnessed (GHI #895). `data/mandated_tier1_dispatch.json` declares which
# dispatch surfaces doctrine MANDATES, and every argv it names must resolve through
# this walk; a future directive naming a runtime absent from here fails closed at
# that coupling. The coupling is what makes the set falsifiable: on its own it
# enumerated interpreters with nothing declaring the universe they came from, and
# under-coverage does not fail open — the walk stops at the first non-wrapper, so an
# absent member REFUSES a conforming claim, which is GHI #884's symptom recurring.
# Over-inclusion is fenced from the other side: no member may itself be a vendor
# prefix, or the walk would skip the binary that proves the tier.
_RUNTIME_WRAPPERS: frozenset[str] = frozenset(
    {"node", "nodejs", "npx", "python", "python3", "uv", "uvx", "bun", "bunx", "deno"}
)


def receipt_binary_name(argv_head: str) -> str:
    """Return the bare binary name from a recorded argv head.

    Handles both separators explicitly rather than via ``Path``: the receipt may
    have been written on a different platform than the one reading it, and
    ``PurePosixPath`` does not split a Windows head (`.claude/rules/cross-platform.md`).
    """
    return argv_head.replace("\\", "/").rsplit("/", 1)[-1]


def receipt_proves_cross_vendor(receipt: dict[str, Any]) -> bool:
    """Return True when the receipt records a cross-vendor binary that actually ran.

    The proof is ``step.command`` — the argv ARB executed — never a caller-supplied
    display name. It is NOT anchored at position 0: the scan walks past
    ``_RUNTIME_WRAPPERS`` to the binary they front, because reading position 0 alone saw
    ``node`` and refused every conforming plugin dispatch (GHI #884). This is the
    distinction the name channel cannot make by construction:
    a name can MENTION a vendor while describing its absence (two adversary names in
    `.gzkit/ledger.jsonl` read "codex-unavailable"), and any scan admitting a mentioned
    vendor would classify those degraded Claude-family runs as tier 1 — failing OPEN on
    the exact substitution Step 4b exists to catch. An argv cannot mention; it ran.

    Malformed receipts return False rather than raising: an unreadable proof is an
    absent proof, and the caller fails closed on it (GHI #765).
    """
    step = receipt.get("step")
    if not isinstance(step, dict):
        return False
    command = step.get("command")
    if not isinstance(command, list) or not command:
        return False
    # Walk past a runtime wrapper to the binary it fronts, then STOP at the first
    # non-wrapper. Stopping is load-bearing: the adversary's PROMPT is also in argv
    # and routinely names vendors, so a scan that kept walking would let a mentioned
    # vendor satisfy the gate — reopening the fail-open this function exists to
    # close. One hop past `node` reaches `codex-companion.mjs`; nothing reaches the
    # prompt.
    for arg in command:
        name = _receipt_binary_name(str(arg))
        if name.lower().removesuffix(".exe") in _RUNTIME_WRAPPERS:
            continue
        return _is_cross_vendor_adversary(name)
    return False


_receipt_binary_name = receipt_binary_name
_receipt_proves_cross_vendor = receipt_proves_cross_vendor


def _build_adversarial_event(
    *,
    obpi_id: str,
    verdict: str | None,
    adversary: str | None,
    job_id: str | None,
    refuted_claim: str | None,
    resolution: str | None,
    tier: int | None = None,
    receipt: str | None = None,
) -> LedgerEvent | None:
    """Render the Step-4b verdict as an ``adversarial_validation`` ledger event.

    Returns ``None`` when no verdict or adversary is supplied. Optional detail
    fields are omitted rather than emitted as null, matching
    ``_EventBase._serialize``.
    """
    if not verdict or not adversary:
        return None
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "schema": LEDGER_SCHEMA,
        "event": "adversarial_validation",
        "id": f"ADV-{obpi_id}-{now.strftime('%Y%m%dT%H%M%SZ')}",
        "obpi_id": obpi_id,
        "verdict": verdict,
        "adversary": adversary,
    }
    for key, value in (
        ("job_id", job_id),
        ("refuted_claim", refuted_claim),
        ("resolution", resolution),
        ("adversary_tier", tier),
        ("adversary_receipt", receipt),
    ):
        if value:
            payload[key] = value
    return LedgerEvent.model_validate(payload)
