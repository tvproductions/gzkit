"""gz permitted-entry command — the airlock's third door (ADR-0.33.0, OBPI-05).

The ad-hoc/spurious entry: reconnaissance for comprehension with light repair at
most. This door CONSUMES the SHARED airlock primitive extracted by OBPI-02/03 —
it imports ``gzkit.airlock.enter.airlock_enter`` / ``gzkit.airlock.exit.airlock_exit``
and CALLS them, never forking a private variant (parent ADR § Boundary Invariants
#3). It closes the silent-bypass hole (§ Consequences #2): an ad-hoc entry that
formerly crossed NO membrane now crosses the airlock and leaves an ``airlock_in`` /
``airlock_out`` L2 record.

Door principle (parent ADR BI-2): the acknowledge-and-decide gate fires on EVERY
transit — the reason/door selects ceremony WEIGHT (this door is permissive), never
*whether* the gate fires. The gate is realized now by the door ALWAYS CALLING the
shared primitive; per-door ceremony-weight calibration is the attested deferred
frontier. Diagnostic-only: a NO-GO is surfaced (``build_refusal``), never a block.

The door NEVER performs a repair itself — it is a membrane, not an editor. A
within-ceiling light-repair intent is ADMITTED (crosses the gate, logged); an
intent BEYOND the light-repair ceiling is REFUSED for inline execution and routed
as a FRESH transit through the pipeline door (intentional change) or the mx door
(defect repair) — parent ADR BI-5, never smuggle real work into a reconnaissance.
"""

from __future__ import annotations

import enum
import glob
import shutil
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

from rich.markup import escape

from gzkit.airlock.enter import airlock_enter, build_refusal
from gzkit.airlock.exit import Door, airlock_exit
from gzkit.airlock.model import Decision, SeamMap
from gzkit.commands.common import console, get_project_root
from gzkit.ledger import Ledger

# Ledger path relative to project root (parallel to mx_cmd.py's _LEDGER_RELPATH).
_LEDGER_RELPATH = (".gzkit", "ledger.jsonl")

# ADR/OBPI artifact tree — when --target names an on-disk artifact, that artifact
# is the airlock's real DECLARE input (mirroring the pipeline/mx doors). Otherwise
# the door synthesizes a minimal DECLARE so the gate ALWAYS fires (REQ-01).
_ADR_RELPATH = ("docs", "design", "adr")

# Structural-work verbs that exceed the light-repair ceiling. This is a best-effort
# HEURISTIC TRIPWIRE, NOT a semantic guarantee — it recommends a fresh transit
# diagnostically, it never hard-blocks the operator's judgment. Reliable free-text
# scope-classification is the deferred calibration frontier (parent ADR); a keyword
# the set does not name may still be genuinely structural, so the captain decides.
_BEYOND_CEILING_VERBS = frozenset(
    {
        "refactor",
        "redesign",
        "rewrite",
        "migrate",
        "schema",
        "restructure",
        "overhaul",
        "rearchitect",
        "delete",
        "remove",
        "replace",
        "implement",
        "gut",
        "extend",
        "subsystem",
    }
)


class RepairScope(enum.StrEnum):
    """How much repair an ad-hoc entry declares, measured against the light ceiling."""

    NONE = "none"  # reconnaissance only — no repair intent
    LIGHT = "light"  # within the light-repair ceiling — admitted, crosses the gate
    BEYOND = "beyond"  # exceeds the ceiling — refused inline, trips a fresh transit


def _intent_tokens(repair: str) -> set[str]:
    """Whitespace-split, lowercased, punctuation-normalized word set of an intent.

    Each token is reduced to its alphanumeric core — surrounding AND internal
    punctuation removed — so a structural verb is recognized regardless of quoting,
    bracketing, or hyphenation: ``rewrite``, ``"rewrite"``, ``[rewrite]`` and
    ``re-write`` all normalize to ``rewrite`` (Codex Step-4b, GHI #678). It remains a
    best-effort heuristic — synonyms and unlisted structural verbs are the deferred
    calibration frontier, not a semantic guarantee (parent ADR, option-c reconcile).
    """
    normalized = {"".join(ch for ch in token.lower() if ch.isalnum()) for token in repair.split()}
    return normalized - {""}


def classify_repair(repair: str | None) -> RepairScope:
    """Classify a repair intent against the light-repair ceiling.

    ``None``/blank → ``NONE`` (recon-only); an intent naming a structural-work verb
    → ``BEYOND`` (exceeds the ceiling); otherwise ``LIGHT`` (within the ceiling).
    The ceiling is a heuristic tripwire (diagnostic), not a semantic guarantee.
    """
    if not repair or not repair.strip():
        return RepairScope.NONE
    if _intent_tokens(repair) & _BEYOND_CEILING_VERBS:
        return RepairScope.BEYOND
    return RepairScope.LIGHT


def _resolve_declare(
    target: str, repair: str | None, project_root: Path
) -> tuple[str, Path, Path | None]:
    """Resolve the DECLARE input for the ad-hoc entry.

    Returns ``(declare_id, brief_path, tmp_root)``. When ``target`` names an on-disk
    ADR/OBPI artifact, that artifact is the real DECLARE (``tmp_root`` is ``None``).
    Otherwise a minimal DECLARE is SYNTHESIZED (naming ``target`` as the sole declared
    Allowed Path + the intent) so ``airlock_enter`` is ALWAYS callable (REQ-01); the
    returned ``tmp_root`` must be cleaned up by the caller. Brief-less DECLARE
    RICHNESS is the deferred calibration frontier; CALLING the primitive is realized
    now.
    """
    adr_root = project_root.joinpath(*_ADR_RELPATH)
    if adr_root.is_dir():
        # Resolve to a real artifact ONLY on an EXACT, UNAMBIGUOUS id match: the file
        # stem must equal the target (no trailing prefix wildcard) and there must be
        # exactly one such file. A loose prefix-glob would silently bind a vague target
        # like "ADR" to an arbitrary real artifact via matches[0], forging the declared
        # footprint (Codex Step-4b, GHI #678). glob.escape neutralizes metacharacters;
        # the ".md" (not "*.md") + single-match guard forbid the misbinding.
        matches = sorted(adr_root.glob(f"**/{glob.escape(target)}.md"))
        if len(matches) == 1:
            return target, matches[0], None
    # Synthesize a minimal DECLARE. The ``target`` is used LOSSLESSLY for both the
    # declared body and ``declare_id``/ledger identity — the handler already rejected
    # targets carrying a backtick/newline, so it renders exactly as ``- `target` `` and
    # ``extract_allowed_paths`` yields it verbatim. Only the free-text INTENT is sanitized
    # (it is descriptive, never an identity), so an injected ``\n- `evil.py` `` cannot
    # forge a declared body (Codex Step-4b, GHI #678).
    raw_intent = repair.strip() if repair and repair.strip() else "reconnaissance for comprehension"
    safe_intent = _sanitize_for_brief(raw_intent)
    tmp_root = Path(tempfile.mkdtemp(prefix="gzkit-permitted-entry-"))
    brief = tmp_root / "declare.md"
    brief.write_text(
        f"# Permitted-Entry DECLARE\n\n## Allowed Paths\n\n- `{target}`\n\n"
        f"Ad-hoc entry intent: {safe_intent}\n",
        encoding="utf-8",
    )
    return f"permitted-entry:{target}", brief, tmp_root


def _sanitize_for_brief(text: str) -> str:
    """Collapse whitespace/newlines and strip backticks from free-text intent.

    The synthetic DECLARE embeds the intent into Markdown that ``extract_allowed_paths``
    parses for ``- `path` `` bullets. Newlines would let an injected ``\\n- `evil.py` ``
    forge a declared body, and a backtick would break a quoted path — both neutralized
    here. Applied ONLY to the descriptive intent, NEVER to the target (whose identity
    must stay lossless; unrepresentable targets are rejected upstream) — Codex Step-4b,
    GHI #678.
    """
    return " ".join(text.split()).replace("`", "")


def _render_comprehension(seam_map: SeamMap, declare_id: str) -> str:
    """Render the non-empty seam/comprehension report for a recon entry (REQ-02).

    Names the declared bodies (footprint) and any push/pull edges (the join). Always
    non-empty — it names the entry and at minimum the declared footprint.
    """
    footprint = ", ".join(seam_map.bodies) or "(none declared)"
    lines = [f"permitted-entry recon: {declare_id}"]
    lines.append(f"  footprint (declared bodies): {footprint}")
    lines.append(f"  push edges (reach): {len(seam_map.push_edges)}")
    lines.append(f"  pull edges (invariants): {len(seam_map.pull_edges)}")
    lines.append(f"  un-accounted seams: {len(seam_map.unaccounted)}")
    return "\n".join(lines)


def permitted_entry_cmd(
    target: str,
    recon: bool = False,
    repair: str | None = None,
    dry_run: bool = False,
    project_root: Path | None = None,
    *,
    _airlock_reach: Callable[[str], list[str] | None] | None = None,
) -> None:
    """Cross the permitted-entry airlock door for an ad-hoc/spurious entry.

    ALWAYS fires the acknowledge-and-decide gate (calls the shared ``airlock_enter``
    / ``airlock_exit`` primitive — REQ-01, BI-2). Reconnaissance is the default; a
    within-ceiling light repair is ADMITTED; a beyond-ceiling intent is REFUSED for
    inline execution and routed as a FRESH transit (REQ-03/04, BI-5). The door NEVER
    mutates ``target`` (REQ-02) and NEVER forks a private airlock (REQ-05). On a
    non-dry-run, both edges book their L2 encounter (``airlock_in`` / ``airlock_out``
    — REQ-06), closing the silent-bypass hole. The gate is NEVER a completion
    attestation (REQ-07, BI-3).
    """
    # A blank/whitespace target is REJECTED before any airlock entry — an empty target
    # would book anonymous, misbound airlock_in/airlock_out L2 records (REQ-06
    # accountability) and glob-select an unrelated ADR (Codex Step-4b, GHI #678).
    if not target.strip():
        console.print(
            "[red]ERROR:[/red] --target must name a non-empty file or region — "
            "an empty target would book an anonymous, unaccountable airlock transit."
        )
        sys.exit(1)
    # A target carrying a backtick or newline cannot be represented EXACTLY as a declared
    # path in the synthetic DECLARE — rewriting it (lossy) would collapse distinct targets
    # to one identity, destroying transit accountability (Codex Step-4b, GHI #678). Reject
    # rather than rewrite, so declare_id/ledger ids stay lossless.
    if any(ch in target for ch in ("`", "\n", "\r")):
        console.print(
            "[red]ERROR:[/red] --target must not contain backticks or newlines — "
            "it must be representable exactly as a declared path."
        )
        sys.exit(1)

    root = project_root if project_root is not None else get_project_root()
    reach = _airlock_reach if _airlock_reach is not None else (lambda _node: [])
    ledger = None if dry_run else Ledger(root.joinpath(*_LEDGER_RELPATH))

    # --recon (reconnaissance-only) and --repair (a repair intent) are contradictory
    # and MUTUALLY EXCLUSIVE. Fail fast on the conflict rather than silently dropping
    # the repair — a silently-dropped repair would let a beyond-ceiling intent evade
    # the ceiling (REQ-03) and fresh-transit routing (REQ-04) by adding --recon (Codex
    # Step-4b, GHI #678). Reconnaissance is the default when no repair is given.
    if recon and repair is not None and repair.strip():
        console.print(
            "[red]ERROR:[/red] --recon and --repair are mutually exclusive. "
            "--recon is reconnaissance-only; drop --recon to declare a repair intent."
        )
        sys.exit(1)
    declare_id, brief_path, tmp_root = _resolve_declare(target, repair, root)
    try:
        # airlock-IN ALWAYS fires — the gate crosses on EVERY entry (BI-2, REQ-01).
        # Diagnostic-only FOR NOW: a NO-GO is surfaced rather than blocking — a staged
        # posture per parent ADR § Calibration frontier, not the declared end state
        # (BI-4 blocks). § Negative #5 governs refusal legibility, not blocking.
        preflight = airlock_enter(declare_id, brief_path, reach_fn=reach, ledger=ledger)
        try:
            # Operator-controlled text (target via declare_id, repair) is ESCAPED before
            # it enters Rich markup — an unescaped '[...]' would corrupt the diagnostic
            # output or crash on a malformed tag like '[/rewrite]' (Codex Step-4b, GHI #678).
            console.print(escape(_render_comprehension(preflight.seam_map, declare_id)))
            if preflight.decision is not Decision.PROCEED:
                console.print(
                    f"[yellow]airlock-IN (permitted-entry, diagnostic):[/yellow] "
                    f"{escape(build_refusal(preflight.seam_map, declare_id))}"
                )

            # Light repair is the CEILING (REQ-03), not the default. A beyond-ceiling
            # intent is NOT admitted inline and TRIPS a fresh transit (REQ-04, BI-5) —
            # the door NEVER performs the work inline. It does NOT authoritatively guess
            # the door: defect-vs-intentional cannot be reliably inferred from free text
            # (Codex Step-4b, GHI #678), so it PRESENTS BOTH doors with their criteria
            # and the captain chooses. BI-5's binding requirement is "route as a fresh
            # transit, never smuggle inline" — not auto-selecting the door.
            scope = classify_repair(repair)
            if scope is RepairScope.BEYOND and repair is not None:
                console.print(
                    f"[yellow]permitted-entry: intent exceeds the light-repair ceiling — "
                    f"not admitted inline (the door never edits).[/yellow] Route a fresh "
                    f"transit and choose the door — {Door.PIPELINE.value} (intentional "
                    f"change) or {Door.MX.value} (defect repair): {escape(repair.strip())}"
                )
            elif scope is RepairScope.LIGHT:
                console.print(
                    f"[green]permitted-entry: light repair admitted (within ceiling) — "
                    f"crosses the gate:[/green] {escape((repair or '').strip())}"
                )
        finally:
            # airlock-OUT (co-equal exit membrane) ALWAYS fires once airlock-IN did —
            # a PAIRED transit is guaranteed even if the between-beats surfacing raises
            # (Codex Step-4b, GHI #678). Both edges book their L2 encounter, closing the
            # silent-bypass hole (REQ-06). The door never mutates target.
            airlock_exit(declare_id, brief_path, reach_fn=reach, ledger=ledger)
    finally:
        if tmp_root is not None:
            shutil.rmtree(tmp_root, ignore_errors=True)
