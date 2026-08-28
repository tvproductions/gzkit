"""Step-4b adversarial-validation gate for ``gz obpi complete``.

Extracted from ``obpi_complete`` under the module-size shrink-only ratchet
(`.gzkit/chores/module-sloc-cap-radon/`): the GHI #765/#780 receipt requirement
grew that module past the ceiling its grandfather entry records, and this family
is the cohesive unit that grew. Nothing here changed in the move -- the gate's
behavior is pinned by ``tests/test_adversarial_validation_gate.py``, which
imports these symbols through ``obpi_complete`` and still does.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, NoReturn

from gzkit.ledger import LEDGER_SCHEMA, LedgerEvent


def _fail(msg: str, *, exit_code: int, as_json: bool, obpi_id: str) -> NoReturn:
    """Delegate to ``obpi_complete._fail``.

    Imported at call time, not module scope: ``obpi_complete`` imports this
    module, so a top-level import back would close a cycle. `.gzkit/rules/pythonic.md`
    § Imports names cycle avoidance as one of the two carve-outs to the
    top-level-imports rule. Delegating rather than duplicating also keeps the
    error surface on ``obpi_complete``'s console, which its tests patch.
    """
    from gzkit.commands.obpi_complete import _fail as _delegate  # noqa: PLC0415

    _delegate(msg, exit_code=exit_code, as_json=as_json, obpi_id=obpi_id)


__all__ = [
    "ADVERSARY_VERDICTS",
    "_build_adversarial_event",
    "_enforce_adversarial_validation",
    "_enforce_adversary_receipt",
    "_is_cross_vendor_adversary",
    "_load_adversary_receipt",
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


def _receipt_binary_name(argv_head: str) -> str:
    """Return the bare binary name from a recorded argv head.

    Handles both separators explicitly rather than via ``Path``: the receipt may
    have been written on a different platform than the one reading it, and
    ``PurePosixPath`` does not split a Windows head (`.claude/rules/cross-platform.md`).
    """
    return argv_head.replace("\\", "/").rsplit("/", 1)[-1]


def _receipt_proves_cross_vendor(receipt: dict[str, Any]) -> bool:
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
        if name.lower() in _RUNTIME_WRAPPERS:
            continue
        return _is_cross_vendor_adversary(name)
    return False


def _load_adversary_receipt(run_id: str, *, root: Path) -> dict[str, Any] | None:
    """Read the ARB step receipt named by *run_id*, or None when unresolvable.

    Unresolvable covers every way the id can fail to name a real receipt: no such
    file, unreadable, non-JSON, or a JSON scalar. Each collapses to the same
    governance meaning — the corroborating artifact is not there.
    """
    try:
        raw = (root / f"{run_id}.json").read_text(encoding="utf-8")
    except OSError:
        return None
    try:
        receipt = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return receipt if isinstance(receipt, dict) else None


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

    Returns ``None`` when no verdict was supplied — the lite lane, where the gate
    does not fire. Optional detail fields are omitted rather than emitted as null,
    matching ``_EventBase._serialize``.
    """
    if not verdict or not adversary:
        return None
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "schema": LEDGER_SCHEMA,
        "event": "adversarial_validation",
        "id": f"ADV-{obpi_id}-{now.strftime('%Y%m%dT%H%M%SZ')}",
        "ts": now.isoformat(),
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


def _enforce_adversary_receipt(
    *,
    obpi_id: str,
    receipt: str,
    receipts_root: Path | None,
    tier: int | None,
    as_json: bool,
) -> bool:
    """Resolve the cited ARB receipt and report whether it proves a cross-vendor run.

    Fails closed — never returning — when the receipt does not resolve, records a
    non-zero exit, or contradicts a declared tier 1. Split out of
    ``_enforce_adversarial_validation`` to hold that gate under the C complexity
    ceiling (`.pre-commit-config.yaml` xenon) rather than to add a seam (GHI #765).
    """
    loaded = (
        _load_adversary_receipt(receipt, root=receipts_root) if receipts_root is not None else None
    )
    if loaded is None:
        _fail(
            f"Completion blocked: Step 4b for {obpi_id} cites adversary receipt "
            f"'{receipt}', which does not resolve to a readable ARB step receipt. "
            "A receipt id naming no artifact is an assertion wearing the shape of "
            "proof. Run the adversary under ARB so the receipt exists: "
            "uv run gz arb step --name codexadversary -- codex exec '<refute prompt>', "
            "then cite the run_id it prints with --adversary-receipt.",
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )
    if loaded.get("exit_status") != 0:
        _fail(
            f"Completion blocked: Step 4b for {obpi_id} cites adversary receipt "
            f"'{receipt}', which records exit_status={loaded.get('exit_status')!r} — "
            "the adversary run did not succeed. A failed run cannot have re-derived "
            "the completion claim. Re-run the adversary under ARB (uv run gz arb step "
            "--name codexadversary -- codex exec '<refute prompt>') and cite the "
            "successful run_id.",
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )
    proven = _receipt_proves_cross_vendor(loaded)
    if tier == 1 and not proven:
        _fail(
            f"Completion blocked: Step 4b for {obpi_id} declares --adversary-tier 1 "
            f"(cross-vendor) but its receipt '{receipt}' records an argv that did not "
            "invoke a recognized different-vendor binary. The receipt is the proof "
            "channel precisely because it records what RAN — a declaration that "
            "contradicts it is asserting against the caller's own evidence. Either "
            "cite the receipt of the cross-vendor run, or declare the tier that "
            "actually ran (--adversary-tier 2) with --adversary-fallback-reason "
            "'<observed Codex unavailability>'.",
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )
    return proven


def _enforce_adversarial_validation(
    *,
    obpi_id: str,
    parent_lane: str,
    verdict: str | None,
    adversary: str | None,
    resolution: str | None,
    as_json: bool,
    fallback_reason: str | None = None,
    tier: int | None = None,
    receipt: str | None = None,
    receipts_root: Path | None = None,
) -> None:
    """Fail closed unless Step 4b's adversary verdict is recorded (GHI #676).

    Step 4b is already a fail-closed gate in the pipeline skill: no OBPI reaches
    attestation without an independent adversary re-deriving the completion claim
    under instruction to REFUTE. Nothing enforced it at the chokepoint, so an agent
    that skipped 4b and one that was refuted and attested anyway left indistinguishable
    durable records — the verdict lived only in a transcript or a vendor cache.

    Heavy lane only, matching the lane that already carries fail-closed Gate 3/4.
    A ``refuted`` verdict with no recorded resolution is itself blocking: a known
    refutation must never be handed to the operator dressed as clean.
    """
    if parent_lane.lower() != "heavy":
        return

    if not verdict or not adversary:
        _fail(
            "Completion blocked: Step 4b independent adversarial validation is not "
            f"recorded for {obpi_id}. The heavy lane forbids attestation on evidence "
            "the authoring agent produced alone (GHI #643/#676) — an adversary "
            "prompted to REFUTE must re-derive the completion claim, and its verdict "
            "must land in the ledger, not a transcript. Re-run with "
            "--adversary-verdict <" + "|".join(ADVERSARY_VERDICTS) + "> "
            "--adversary <vendor/model>. If neither a different-vendor adversary nor "
            "an independent subagent could run, record the degraded floor explicitly: "
            "--adversary-verdict degraded-human-only --adversary human.",
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )

    if verdict == "refuted" and not resolution:
        _fail(
            f"Completion blocked: the adversary refuted {obpi_id} and no resolution is "
            "recorded. A known refutation must never be handed to the operator dressed "
            "as clean. Fix the refuted claim, re-verify against the adversary's own "
            "check, then re-run with --adversary-resolution '<what was fixed and how "
            "the adversary's check was re-run>'.",
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )

    # Tier order (GHI #678): Codex (tier 1, different vendor) is REQUIRED first. A
    # Claude-family adversary shares this agent's blind spots — the exact failure 4b
    # exists to break — so it is admissible only when Codex was genuinely unavailable,
    # and that reason must be recorded. The human degraded floor is exempt (its verdict
    # already flags it); a proven cross-vendor adversary needs no justification.
    is_human_floor = verdict == "degraded-human-only" or adversary.strip().lower() == "human"
    if is_human_floor:
        return

    # A DECLARED tier governs; the name scan is only the fallback for callers predating
    # the flag. Inference alone was the hole: tier was read off a caller-supplied string
    # with nothing behind it, so "codex-shaped name" and "ran on Codex" were the same
    # claim. Declaring a tier that contradicts the name is a contradiction the name scan
    # cannot see by construction — it fails closed here rather than passing silently.
    # Precedence: PROVEN (receipt) > DECLARED (tier) > INFERRED (name). A receipt is
    # written by ARB at invocation time and records the argv that actually ran, so it
    # is the only channel here not authored by the agent making the claim (GHI #765).
    proven_cross_vendor: bool | None = None
    if receipt:
        proven_cross_vendor = _enforce_adversary_receipt(
            obpi_id=obpi_id,
            receipt=receipt,
            receipts_root=receipts_root,
            tier=tier,
            as_json=as_json,
        )

    name_is_cross_vendor = _is_cross_vendor_adversary(adversary)
    if proven_cross_vendor is None and tier == 1 and not name_is_cross_vendor:
        _fail(
            f"Completion blocked: Step 4b for {obpi_id} declares --adversary-tier 1 "
            f"(cross-vendor) but names adversary '{adversary}', which is not a recognized "
            "different-vendor model. Tier 1 is the claim that a DIFFERENT vendor re-derived "
            "the completion — a Claude validating Claude shares this agent's blind spots. "
            "Either name the cross-vendor adversary that actually ran, or declare the tier "
            "that did (--adversary-tier 2) with --adversary-fallback-reason '<observed Codex "
            "unavailability>'.",
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )

    if proven_cross_vendor is not None:
        is_cross_vendor = proven_cross_vendor
    elif tier is not None:
        is_cross_vendor = tier == 1
    else:
        is_cross_vendor = name_is_cross_vendor

    # A cross-vendor claim is admissible ONLY on receipt proof (GHI #780). GHI #765
    # made the receipt authoritative when cited and optional when absent, which closed
    # nothing: the gate cannot tell "no receipt because the adversary could not be
    # wrapped" from "no receipt because none was run", so the honest and the hollow
    # completion stayed the same input. Both rungs below `proven` are strings the
    # claiming agent typed, and their agreement is self-agreement.
    #
    # Scope is the RESOLVED claim, not the declared one. Gating `--adversary-tier 1`
    # alone would fence a path no completion has used: of 17 recorded
    # adversarial_validation events, zero declare a tier and 14 resolved cross-vendor
    # through the name scan. The tier-2 path below stays reachable without a receipt
    # so an unavailable Codex remains recordable rather than pushed into a false tier 1.
    if is_cross_vendor and proven_cross_vendor is None:
        claimed_by = "--adversary-tier 1" if tier == 1 else f"the adversary name '{adversary}'"
        _fail(
            f"Completion blocked: Step 4b for {obpi_id} claims a cross-vendor (tier-1) "
            f"adversary via {claimed_by}, with no ARB receipt proving one ran. Tier 1 is "
            "the claim that a DIFFERENT vendor re-derived the completion, and a name and "
            "a declared tier are both typed by the agent making that claim — their "
            "agreement is self-agreement, not corroboration (GHI #765/#780). A receipt is "
            "written by ARB at invocation time and records the argv that actually ran. "
            "Wrap the adversary run and cite it: uv run gz arb step --name codexadversary "
            "-- codex exec '<refute prompt>', then re-run with --adversary-receipt "
            "<RUN_ID>. If Codex was genuinely unavailable, record the degraded run "
            "honestly instead: --adversary-tier 2 --adversary-fallback-reason '<observed "
            "Codex unavailability>'.",
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )

    if not is_cross_vendor and not (fallback_reason and fallback_reason.strip()):
        _fail(
            f"Completion blocked: Step 4b for {obpi_id} used a non-cross-vendor "
            f"(tier-2 Claude-family) adversary '{adversary}' with no recorded reason "
            "Codex was unavailable. Codex (tier 1) shares none of this agent's blind "
            "spots and is REQUIRED first (a Claude validating Claude shares failure "
            "modes). Run codex:setup: if it reports ready=true, re-run Step 4b through "
            "Codex. If Codex is genuinely unavailable, record why with "
            "--adversary-fallback-reason '<observed Codex unavailability, e.g. setup "
            'ready=false / not authenticated>\'. "It was convenient" is not a reason.',
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )
