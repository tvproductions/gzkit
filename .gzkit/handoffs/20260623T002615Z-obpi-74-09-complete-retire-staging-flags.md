---
mode: CREATE
adr_id: ADR-0.0.74
branch: main
timestamp: "2026-06-23T00:26:15Z"
agent: claude-code
obpi_id: OBPI-0.0.74-09-mx-retire-staging-flags
last_lock_event_timestamp: "2026-06-22T23:31:54.719717+00:00"
last_commit_sha: 9e6a66db
session_id:
continues_from:
---

<!-- Handoff document for ADR-0.0.74 — created by claude-code at 2026-06-23T00:26:15Z -->

## ⚠️ This handoff ADVISES next moves — it is NOT authorization to execute them

**Read this before anything else.** A handoff records a *proposed* plan and its
context. It is **NOT** a clearance to unilaterally execute that plan. On resume —
at **every** freshness level, Fresh included — you MUST:

1. Present the advised next steps and current state to the operator.
2. **Obtain explicit operator authorization before executing any of them** — no
   file mutation, no `gz` ceremony, no migration until the operator says go.
3. Treat the human-as-final-witness doctrine as binding from the first step: you
   advise; the operator rules; you note variance and stop.

Barreling into execution from this document is the exact failure this handoff
exists to prevent. The plan is the destination; operator authorization is the
ignition.

## Current State Summary

OBPI-0.0.74-09-mx-retire-staging-flags is **attested-complete and fully synced**
(Gate 5 operator attestation "attest completed" by g0, recorded via
`gz obpi complete`, completion type `operator-verbatim-conversational`). The
full pipeline ran to Stage 5: completion receipt emitted, lock released
(this handoff is its register entry), pipeline markers cleaned, both git-sync
cycles done, `gz obpi reconcile` PASS. Branch `main` is clean and synced to
`origin/main` at HEAD `9e6a66db`.

The two hand-set staging flags are gone: `_FRESHNESS_FAIL_CLOSED`
(`rendition_freshness.py`) and `_FLOOR_FAIL_CLOSED`
(`rendition_floor_coherence.py`) were deleted and both gates now resolve their
effective severity through the shared leveled MX checkpoint via
`_checkpoint.is_advisory("<guard-name>", root)` — advisory inside the hangar
(marker present), fail-closed at full strength outside.

Verification at completion: 23/23 scoped tests pass
(`arb-step-unittest-fdd6331d99df481baa170005ba047f45`), lint clean
(`arb-ruff-8c1128b368364fff9900b6d4f1e9c530`), typecheck clean
(`arb-step-typecheck-db8d74cd54834733848cb66121c6aa83`), docs clean
(`arb-step-mkdocs-87db927daa64446ba806b405da7edf60`). **Full `gz check` is now
green (exit 0)** and behave is fully green (368 scenarios, 0 failed).

**Repair work landed in the same session (operator-authorized).** Removing the
staging flags surfaced pre-existing `AGENTS.md` corpus drift at the pre-push
gate. Per operator decision ("Repair corpus drift now"), the drift was repaired,
not deferred — see § Decisions Made and § Important Context.

## Important Context

**Expected consequence — pre-existing corpus drift surfaced, then REPAIRED.**
The staging flags were hiding pre-existing `AGENTS.md` corpus drift:
`AGENTS.md/codex` and `AGENTS.md/claude` renditions had no provenance sidecar.
With the flags gone, `gz validate --rendition-freshness` and
`--rendition-floor-coherence` became fail-closed outside the MX hangar, so the
pre-push `gz check` gate blocked. This was the honest generalization the ADR
intended — the drift was always there; the staging flag suppressed it; it is NOT
a regression introduced by this OBPI.

**Repair (operator-authorized, done):** Recomposed both renditions from the
current corpus (the staged Jun-20 candidates already carried all 45/45
invariant-tier entries verbatim) and committed them under operator attestation
via `gz content commit`, which froze provenance sidecars
(`AGENTS.md/codex.corpus.json`, `AGENTS.md/claude.corpus.json`,
corpus_fingerprint `aed354ac9f09…`, 46 entries). Both rendition gates are now
green. Additionally, one coupled behave scenario
(`features/rendition_playback.feature:47`) tested the removed warn-staging
contract and was rewritten to the new fail-closed-outside-the-hangar contract
(the BDD analog of the deleted `TestRenditionFreshnessWarnStaging` unit class) —
coupled-surface coherence (AGENTS.md DO IT RIGHT 1a).

## Decisions Made

- **Decision:** Wire severity via `checkpoint.is_advisory()` rather than
  `checkpoint.resolve()` with a `GZ_<LEVEL>` constant.
  **Rationale:** `is_advisory()` directly answers the bool the `closed` variable
  needs; these two gates do not otherwise emit a level constant.
  **Alternatives rejected:** (a) hard-default `fail_closed=True` without
  checkpoint — loses hangar advisory demotion, defeats the OBPI's purpose;
  (b) `resolve()` with a level constant — introduces a level these gates don't
  emit; (c) new `guard_level` parameter — speculative complexity.

- **Decision:** Delete the obsolete staging-test classes
  (`TestRenditionFreshnessWarnStaging`, `TestStagedWarn`) rather than retrofit
  them.
  **Rationale:** they tested the `_*_FAIL_CLOSED = False` warn-default behavior
  that the checkpoint supersedes; the new `TestCheckpointWiring*` classes encode
  the replacement semantics (no marker → fail-closed; marker → advisory).

- **Decision:** Replace the `**` glob allowed-path with the explicit brief file
  path (brief amendment) rather than override the reconcile gate.
  **Rationale:** the brief was right and the tool has a known glob-guard gap;
  fixing the brief surgically is cleaner than carrying an override.

- **Decision:** Repair the pre-existing corpus drift now (operator ruling
  "Repair corpus drift now") rather than leave the commits local as follow-up.
  **Rationale:** the existing Jun-20 staged candidates already carried all 45/45
  invariant entries verbatim, so the repair was a clean compose+commit under
  attestation — not a from-scratch rendition authoring.
  **Alternatives rejected:** (a) leave commits local and defer — would strand
  the attested OBPI unpushed; (b) enter MX mode to demote gates and push — MX
  enter/exit (OBPI-04/05) is not yet built, so not viable.

## Immediate Next Steps

*(ADVISORY — present to operator, await authorization before acting.)*

OBPI-09 and its coupled repair work are fully done, synced, and green. There is
no remaining work specific to this OBPI. The next propellants are parent-ADR
work:

1. **Continue the ADR-0.0.74 checklist.** Per the Build-to-1.0 campaign, the
   remaining MX kernel items are the next propellants toward `0.29.0`:
   OBPI-04 (`gz mx enter`), OBPI-05 (`gz mx exit` hard gate / no-force /
   live exit negative-control), OBPI-06 (MX log), OBPI-07 (awareness hook),
   OBPI-08 (gz-mx skill + AGENTS.md rule), OBPI-13 (proxy-reality detector),
   OBPI-14 (MX hardening: TTL/max-open, ledger debt-aging, dangling-state
   detector). ADR closeout is BLOCKED until these land.
2. **Then the enforcement-claim meta-validator** (Magna Carta Movement I item 3
   — the general §5 mechanism, the floor's teeth).

## Pending Work / Open Loops

- ADR-0.0.74 closeout will audit REQ-0.0.74-09-03 (STRUCTURAL-FENCE) against
  parent ADR § Boundary Invariants #2 ("the checkpoint is the single LEVELED
  severity authority … no per-gate hand-set staging flag survives anywhere in
  the codebase"). OBPI-09 contributes to that invariant; it is proven at the ADR
  closeout layer, not per-OBPI.
- Corpus drift (`AGENTS.md/codex`, `AGENTS.md/claude`) — **RESOLVED** this
  session; both renditions recommitted with provenance sidecars under operator
  attestation. No open loop.
- Coupled behave scenario (`rendition_playback.feature:47`) — **RESOLVED** this
  session; rewritten to the post-OBPI-09 fail-closed contract. No open loop.
- No OBPI-09-specific open loops remain. Parent-ADR OBPIs (04–08, 12–14) are the
  remaining ADR-0.0.74 work (see Immediate Next Steps).

## Verification Checklist

- [ ] `uv run gz obpi status OBPI-0.0.74-09-mx-retire-staging-flags` → ATTESTED COMPLETED
- [ ] `uv run -m unittest tests.governance.test_rendition_freshness tests.governance.test_rendition_floor_coherence` passes (23 tests)
- [ ] `uv run gz validate --qc-binding` passes (negative controls bind)
- [ ] `grep -rn "_FRESHNESS_FAIL_CLOSED\|_FLOOR_FAIL_CLOSED" src/` returns nothing
- [ ] `uv run gz check` exits 0 (full gate green, incl. rendition gates + behave)
- [ ] `git status -sb` → `## main...origin/main` (clean, synced)

## Evidence / Artifacts

- `src/gzkit/governance/trust_audits/rendition_freshness.py` — flag deleted, checkpoint wired
- `src/gzkit/governance/trust_audits/rendition_floor_coherence.py` — flag deleted, checkpoint wired
- `tests/governance/test_rendition_freshness.py` — `TestCheckpointWiringFreshness` added; staging class removed
- `tests/governance/test_rendition_floor_coherence.py` — `TestCheckpointWiringFloor` added; staging class removed
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-09-mx-retire-staging-flags.md` — brief, status Completed, evidence sections populated
- `.claude/plans/retire-staging-flags-OBPI-0.0.74-09.md` — approved plan
- `.claude/plans/.plan-audit-receipt-OBPI-0.0.74-09-mx-retire-staging-flags.json` — PASS receipt
- `.gzkit/renditions/AGENTS.md/codex.md` + `.gzkit/renditions/AGENTS.md/codex.corpus.json` — recommitted rendition + provenance sidecar (corpus repair)
- `.gzkit/renditions/AGENTS.md/claude.md` + `.gzkit/renditions/AGENTS.md/claude.corpus.json` — recommitted rendition + provenance sidecar (corpus repair)
- `features/rendition_playback.feature` — scenario at line 47 rewritten to the post-OBPI-09 fail-closed contract (coupled-surface fix)

## Environment State

Python 3.13, uv-managed. No new dependencies introduced.
