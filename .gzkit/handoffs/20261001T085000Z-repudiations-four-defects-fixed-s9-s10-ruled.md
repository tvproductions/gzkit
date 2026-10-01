---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-01T08:50:00Z'
agent: claude-code
session_id: 3fd6cffc-de28-43f1-81bf-f7eb61a77a9b
continues_from: .gzkit/handoffs/20261001T064914Z-v0-34-8-on-pypi-windows-qc-fixed.md
---

## Current State Summary

Worked advised steps 2-4 of the predecessor. Step 2: OBPI-0.0.24-04, OBPI-0.35.0-09, OBPI-0.34.0-02 and OBPI-0.0.26-02 repudiated (cause verification-invalid, attestor g0); all four read REPUDIATED and their briefs are Active. OBPI-0.0.26-02 was a new finding: its completion receipt carried OBPI-0.0.24-04's attestation text and narrative verbatim. OBPI-0.0.28-03 keeps its completion; its receipt mismatch is recorded as an insight. Step 3: confirmed and filed four defects, fixed and closed each: GHI #1158 (2d8ecb358, uncalled validate_stage4_evidence removed), #1159 (a5af07688, red-parity none-masking), #1157 (ac9ac9ba2, verify-packet replays in a disposable copy), #1156 (376a7bc86 plus 797f4270b, fidelity assertions run at committed HEAD). The justify-at-closeout claim was refuted (no doctrine requires it) and not filed. In-flight fix 1c8430f08: the frontmatter validator read a repudiated OBPI as Completed, so reconcile would have reverted repudiations. Step 4: ADR-pool.test-integrity-tooling registered and the dead OBPI-0.31.0-07 booking retired (6b884af00); section 10 split by intent, routing posted on GHI #1154 and #1155. The reopened briefs were migrated to structured frontmatter and amended (paths repointed, brief-drift --apply), committed in 739090399. gz check exit 0 before push; origin/main in sync.

## Important Context

Repudiation reopens a sealed brief, so every live-brief validator (brief_structure, brief_reconcile, cli_alignment) applies to it at once; expect the same when repudiating any legacy brief. brief-drift --apply only adds missing_in_brief paths; missing_on_disk entries need a hand amendment. A backticked nonexistent path inside an Allowed Paths amendment note is read as allowlist drift. The fidelity gate (gz audit, closeout, gz adr fidelity) now fails closed outside a git repository with a commit; test fixtures need tests.governance.common.init_committed_repo. demo_env in stage4_evidence is now public because fidelity.py and stage4_packet.py both use it. Subagent worktrees were removed after their patches landed; results were applied on main as single writer. The 2026-09-30 audit reports are committed under artifacts/audits/gate-witness-audit-2026-09-30, contrary to the predecessor's claim they lived only in a scratchpad.

## Decisions Made

- [operator-ruled] Work advised steps 2-4 (verbatim: "do 2 through 4"); step 5 set aside.
- [operator-ruled] Repudiate OBPI-0.0.24-04 (verbatim: "Repudiate (Recommended)").
- [operator-ruled] Repudiate OBPI-0.35.0-09 and OBPI-0.34.0-02 (verbatim: "Repudiate both (Recommended)").
- [operator-ruled] OBPI-0.0.28-03 erratum only, no repudiation (verbatim: "Record erratum only (Recommended)").
- [operator-ruled] Repudiate OBPI-0.0.26-02 for its copied attestation (verbatim: "Repudiate and re-complete (Recommended)").
- [operator-ruled] Fidelity assertions run against committed HEAD (verbatim: "Committed state (Recommended)").
- [operator-ruled] Delete validate_stage4_evidence and its tests (verbatim: "Delete fn + tests (Recommended)").
- [operator-ruled] Apply the integrity audit section 9 diff, re-based (verbatim: "Apply, re-based (Recommended)").
- [operator-ruled] Route the section 10 gates by intent: corrections to GHI #1154/#1155, new capability to the pool ADR (verbatim: "Split by intent (Recommended)").
- [operator-ruled] Migrate the reopened legacy briefs and fix the stale verb (verbatim: "Migrate + fix verb (Recommended)").
- [operator-ruled] Amend brief drift now and file a GHI for the path:symbol false positive (verbatim: "Amend now (Recommended)").
- [operator-ruled] Close the session (verbatim: "write handoff and git sync").
- [agent-chose] Kept load_packet when deleting validate_stage4_evidence: it mirrors write_packet and has its own round-trip test.
- [agent-chose] Fixed the repudiated-status frontmatter derivation directly, without a GHI: under 10 lines, one surface, found in flight, unit-tested.
- [agent-chose] verify-packet uses mutation isolation (a working-tree copy), not committed state: a packet carries no commit identity and is verified before attestation.

## Immediate Next Steps

1. Ask whether to start re-completion pipelines for the four repudiated OBPIs (OBPI-0.0.24-04, OBPI-0.0.26-02, OBPI-0.34.0-02, OBPI-0.35.0-09); only the operator initiates them.
2. Fix GHI #1160 (brief-reconcile reads a path:symbol discovery citation as a missing path); under 10 lines plus tests.
3. Work GHI #1154 corrections now that its ruling is booked: present-but-false detection plus unit exit provenance, REQ proof parity across lanes, witness sufficiency, waiver monotonicity, reviewed guard mutation canaries.
4. Work GHI #1155: enumerate gates against the enforcement registry and register load-bearing controls for the nine unregistered hollow gates.
5. Carried, set aside this session: whether to draw the next ADR-0.35.0 OBPI, and the chore_decommission_processed emitter gap.

## Pending Work / Open Loops

Open: GHI #1154, #1155, #1160; trackers #611, #921, #978, #1028, #799. Unfiled and still unconfirmed from earlier sessions: the patch-release diff_only bucket listing open GHIs; the ghi-author runtime predicate firing on rule/skill/template edits; registry gate_targets for module-size and tautological-debt. The red-parity 'latest event per REQ' observation is resolved by #1159 [settled]. How OBPI-0.0.26-02's attestation text came to be copied (CLI reuse or operator paste) was not traced. The closeout Step-5 brief demos and closeout Gate 2 still run in the live checkout; that is a policy question outside #1156 [settled]. 65 of 87 single-fixture negative controls pin no expect (the #1154 class). AGENTS.md is over its advisory char budget.

## Verification Checklist

uv run gz obpi status OBPI-0.0.24-04 (and -0.0.26-02, -0.34.0-02, -0.35.0-09): expect Runtime State REPUDIATED; gh issue view 1156 1157 1158 1159: expect CLOSED; gh issue view 1154 1155 1160: expect OPEN; uv run gz validate --red-parity --frontmatter --brief-reconcile --brief-structure --cli-alignment: expect exit 0; uv run -m unittest tests.governance.test_fidelity_committed_state tests.governance.test_stage4_packet tests.test_red_parity_audit tests.governance.test_frontmatter_coherence: expect OK; git rev-list --left-right --count origin/main...HEAD: expect 0 0; uv run gz check: expect exit 0.

## Evidence / Artifacts

Fixes: `src/gzkit/fidelity.py`, `src/gzkit/governance/stage4_packet.py`, `src/gzkit/governance/stage4_evidence.py`, `src/gzkit/governance/trust_audits/red_parity.py`, `src/gzkit/commands/validate_frontmatter.py`. Tests: `tests/governance/test_fidelity_committed_state.py`, `tests/governance/test_stage4_packet.py`, `tests/test_red_parity_audit.py`, `tests/governance/test_frontmatter_coherence.py`, `tests/commands/test_runtime.py`. Pool ADR: `docs/design/adr/pool/ADR-pool.test-integrity-tooling.md`. Audit: `docs/governance/gate-witness-audit-2026-09-30.md`, `docs/evals/test-suite-integrity-audit-2026-09-24.md`. Amended briefs: `docs/design/adr/foundation/ADR-0.0.26-evaluation-feedback-loop-doctrine/obpis/OBPI-0.0.26-02-justify-binding-gate.md`, `docs/design/adr/foundation/ADR-0.0.24-attestation-receipt-binding/obpis/OBPI-0.0.24-04-bdd-coverage.md`. Predecessor: `.gzkit/handoffs/20261001T064914Z-v0-34-8-on-pypi-windows-qc-fixed.md`.

## Settled Rulings

1253 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
