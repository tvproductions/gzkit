---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-18T22:51:02Z'
agent: claude-code
session_id: c0d62a11-d764-4f30-9f34-95f27eba758e
continues_from: .gzkit/handoffs/20261018T204922Z-drydock-register-folded-token-block-landed.md
---

## Current State Summary

Since the last handoff (b2dc7bdb2), working its advised steps 1 to 3 in order. Step 1: advisory debt now ages per contract, so a safe-mode session cycle renews the lease but keeps the debt (GHI #1258, closed; bf44feed3, eda48b323); live debt reads WARNING from 2026-10-17T08:36Z. Step 2: the maxim-13 recurrence rule landed as RO-1 act (g): data/recurrence_threshold.json (3), `gz insights recurrence` (cited insight ts or GHI, each pair a session lease apart; exit 0 met, 3 not met), failure_classes reading the threshold, manpages for gz insights, and the doc-coverage scan fixed to see flat registrars (153 commands, was 151) (44a7f4cb9, 1f9799143). Step 3: RO-2 specified in docs/governance/harbor-ro2-identity-seam.md (e89b30089) after an inventory found about 118 grammar copies, 28 spelling-derived parents and about 14 resolver paths, not the nine RO-2 first named; its two live defects were fixed directly (d111c1259 obpi-audit parent derivation; f1a88ca54 gz task short-id resolution past parked siblings, with two attested REQ-0.35.0-15-02 tests re-seated). Every act has a driven or sweep-proven red witness and a passage-log row. Tree clean, origin/main level.

## Important Context

Safe mode is open as session e6800367 under docs/governance/harbor-pilotage-candidate-2026-10-15.md; its lease runs to about 2026-10-19T16:50Z, and debt now ages from the contract's first open, so a cycle no longer silences it. The RO-2 spec is the brief for tranche 1: read its § The seam, § The witness and § Known uncertainties before touching code; the baseline file it names (data/id_seam_baseline.json) is the authority over the hand counts, keyed by file and enclosing symbol, registered as a shrink-ratchet in data/waiver_ratchet_registry.json. The seam extends core/models.py's AdrId/ObpiId/ReqId/TaskId (attested by ADR-0.0.10): repair at the surface, never delete; core/models ReqId is loose where triangle.ReqId is strict, and a width change that would reject a live id goes to the operator. The verifier-pipe-gate hook matches verifier names inside heredoc commit messages; write the message to a file and commit -F in its own call. gz arb red --commit grades only the commit's own test modules; nominate expected_tests when running run_mutation_sweep or every mutant reads inconclusive.

## Decisions Made

- [operator-ruled] Proceed on the resumed handoff's step 1, verbatim: 'Proceed with step 1: put the debt-aging question to me with context.' (booked by gz handoff decide).
- [operator-ruled] Advisory debt ages per contract, verbatim selection: 'Per contract (Rec.)'; then 'Land the repair now as a drydock act: GHI through ghi-author, failing test first, one commit with trailer and passage-log row.'
- [operator-ruled] The maxim-13 recurrence threshold, verbatim selection: '3 occurrences (Rec.)'.
- [operator-ruled] The recurrence counting unit, verbatim selection: 'Cited records (Rec.)'.
- [operator-ruled] Distinctness of cited records, verbatim: 'why not full timestamp?', then 'One lease apart (Rec.)'.
- [operator-ruled] The check's home, verbatim selection: 'gz insights recurrence (Rec.)'; landed as an RO-1 act per 'Land it now as an RO-1 act: threshold JSON declared in config_registry, a count-and-distinctness check with a failing test first, requirements-model § 11 and RO-1/RO-7 text amended, passage-log row, one commit.'
- [operator-ruled] RO-2's shape, verbatim selection: 'One RO, tranches (Rec.)'.
- [operator-ruled] RO-2's witness, verbatim selection: 'Ratchet to zero (Rec.)'.
- [operator-ruled] The task-resolver fix against attested REQ-0.35.0-15-02, verbatim selection: 'Re-seat the fixture (Rec.)'.
- [agent-chose] Filed the debt-aging repair under RO-0 (the drydock itself), since debt aging is safe-mode machinery.
- [agent-chose] Homed RO-2's seam in the attested ADR-0.0.10 identity layer of core/models.py rather than a new module, on hexagonal-architecture rule 8 (subsumption over a parallel model).
- [agent-chose] Landed undriven-hunk tests as follow-up commits (eda48b323, 1f9799143) proved by run_mutation_sweep, not amends, because the contract pin had already booked each SHA.
- [agent-chose] Fixed in flight, inside the RO-1 act: the doc-coverage scan could not see flat commands/<name>.py registrars, which hid gz insights from gz cli audit; and failure_classes counted chains at a literal 3 under a label naming --min-depth.

## Immediate Next Steps

1. Start RO-2 tranche 1 per docs/governance/harbor-ro2-identity-seam.md: resolve its three known uncertainties first, then the seam (grammar bodies per kind, resolve, parent_of), the JSON schemas tied to it, the id-seam validator scope with its seeded baseline and registry entry, and the resolution check; one act, failing test first, passage-log row with the baseline count.
2. Once tranche 1 lands, propose tranches 2 to 5 as cheaper sessions, one per tranche, each brief citing the spec's tranche row.
3. Specify RO-3 as re-scoped to requirements-model.md (data/catalog/ families, outcomes, REQs with statement and pass/fail criteria, proof, derives_from, applies_to; the freeze lock; the BDD alignment of user-facing outcomes).
4. Put the RO-2/RO-3 compatibility path (requirements-model.md § Step 5, half reached) to the operator for approval once tranche 1 and the RO-3 spec exist.

## Pending Work / Open Loops

Open defects recorded as insights and not yet repaired: the first contract pin naming rewritten commit 640629757 (mx-contract-pin); gz mx and gz context have no tagged scenarios and ADR-0.28.0 took the lite lane for a human-facing verb (bdd-coverage); the reused 0.28.0 slot (identifier-migration), now constrained by the RO-2 resolver's fail-closed rule. RO-2 tranche 3 owns the separator-less first-match brief finders (pipeline_markers.find_obpi_brief, obpi_precomplete.resolve_brief_path). The session orientation is over its 4000-byte budget; thirty chores are overdue. The semver-order work ruling still binds legacy ADR work until retired. The handback amendment waits for the drydock's exit conditions.

## Verification Checklist

git log --oneline -10 (expect f1a88ca54, d111c1259, e89b30089, 1f9799143, 44a7f4cb9, eda48b323, bf44feed3 among them); git rev-list --left-right --count origin/main...HEAD reads 0 0; uv run gz insights recurrence --help exits 0; uv run gz cli audit reports 153/153 covered; uv run python -c "from gzkit.mx import hardening; print(hardening.debt_aging_status().emitted_level)" prints 30 (WARNING) while e6800367 is open; read the harbor contract's RO-2 row and the last five passage-log rows; read docs/governance/harbor-ro2-identity-seam.md; gh issue view 1258 --json state reads CLOSED.

## Evidence / Artifacts

- `docs/governance/harbor-ro2-identity-seam.md`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `docs/governance/ieee/requirements-model.md`
- `docs/governance/attested-req-subject-retirement.md`
- `src/gzkit/mx/hardening.py`
- `src/gzkit/insights/recurrence.py`
- `src/gzkit/commands/insights.py`
- `src/gzkit/insights/failure_classes.py`
- `src/gzkit/doc_coverage/scanner.py`
- `src/gzkit/commands/obpi_audit_cmd.py`
- `src/gzkit/commands/task.py`
- `data/recurrence_threshold.json`
- `docs/user/manpages/insights-recurrence.md`
- `tests/mx/test_hardening.py`
- `tests/commands/test_insights_recurrence.py`
- `tests/test_pipeline_position.py`

## Settled Rulings

1615 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
