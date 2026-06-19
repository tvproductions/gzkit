# Plan: OBPI-0.0.73-09-waiver-ratchet-honesty-contract

**OBPI:** OBPI-0.0.73-09-waiver-ratchet-honesty-contract
**Parent ADR:** ADR-0.0.73-verification-layer-binding-audit
**Lane:** Heavy (new `gz validate --waiver-ratchet` CLI/runtime contract)
**Authorization:** operator directive 2026-06-19 — "DO THE WORK." The verification-layer port is repaired (OBPI-02 repaired, OBPI-07/08 complete); the recovery freeze on OBPI-09 is lifted by operator direction.

## Context

An unratcheted waiver launders "not built" into "attested green" — the facade class one layer up. Boundary Invariant #8: every registered waiver/grandfather/baseline surface that gates a `gz check` step MUST carry exactly one of three honesty mechanisms:
1. **closed-set lock** — every entry carries `added_under` (the set is frozen; new entries forbidden). Proven by `data/historical_self_close_waivers.json`.
2. **ledger-derived dated cutover** — a cutover date after which the waiver no longer applies. Proven by `lock_handoff_coupling`.
3. **monotonic shrink-ratchet** — a committed baseline count the list can only decrease against. Proven by `tautological_test_baseline` / `distribution_baseline_manifest`.

Ground-truth waiver surfaces (from `data/`): `behave_coverage_waivers.json` (worst — 216KB, hundreds of entries, no lock → assign **shrink-ratchet**), `historical_self_close_waivers.json` (**closed-set lock** already), `sensitivity_floor_grandfather.json`, `tautological_test_waivers.json` + `tautological_test_baseline.json`, `interview_transcript_waivers.json`, `chores_layout_waivers.json`, `surface_weight_waivers.json`, `req_kind_grandfathering.json`, `fidelity_presence_grandfather.json` (OBPI-08).

The decomposition concern ("too broad") is resolved by a **registry-driven uniform design**: each surface declares its mechanism once in `data/waiver_ratchet_registry.json`; the validator enforces declared-vs-actual. No bespoke per-surface code — the retrofit is data, not logic.

## Destination-in-mind disclosure

Chosen approach: registry-driven meta-validator templatized from the two proven patterns. Rejected: (1) splitting OBPI-09 into validator-core + retrofit-sweep — rejected: the registry design makes the retrofit uniform data, so the law is one coherent unit and a split is ceremony without engineering benefit; (2) per-entry `added_under` backfill on `behave_coverage_waivers` (hundreds of entries) — rejected in favor of the shrink-ratchet mechanism, which is the honest fit for a large legacy list.

## Files

- `src/gzkit/governance/trust_audits/waiver_ratchet.py` **CREATE** — the `--waiver-ratchet` audit: read the registry, for each surface verify its declared mechanism is actually satisfied (closed-set: all entries have `added_under`; cutover: a past dated cutover declared; shrink-ratchet: current count <= committed baseline). Fail-closed (exit 3) on any registered surface lacking/violating its mechanism.
- `src/gzkit/governance/trust_audits/__init__.py` — register `audit_waiver_ratchet`.
- `src/gzkit/commands/validate_cmd.py` — `check_waiver_ratchet` param, `_run_waiver_ratchet_scope`, dispatch.
- `src/gzkit/cli/parser_maintenance.py` — `--waiver-ratchet` argument + dispatch kwarg.
- `src/gzkit/quality.py` — `run_waiver_ratchet_audit()` runner + wire `("Waiver ratchet", run_waiver_ratchet_audit)` into the `gz check` step list.
- `src/gzkit/qc_binding.py` — add `"Waiver ratchet"` to `_STEP_CLASSIFICATION` as `bound`.
- `src/gzkit/governance/trust_audits/qc_binding.py` — register an honest negative control for the new step (so it cannot ship green-by-emptiness).
- `data/waiver_ratchet_registry.json` **CREATE** — the registry: each waiver surface → its declared honesty mechanism + (for shrink-ratchet) the committed baseline count.
- `tests/governance/test_waiver_ratchet_scope.py` **CREATE** — a fixture per mechanism + a green-by-emptiness negative-control case + the behave_coverage_waivers fail-closed-on-growth case.
- `tests/commands/test_skills.py` — add `run_waiver_ratchet_audit` stub to the all-steps-stubbed `gz check` test.
- `docs/user/manpages/validate.md` — document `--waiver-ratchet`.
- ADR-0.0.73 `## Fidelity Assertions` — the `--waiver-ratchet` row goes green.
- `docs/design/adr/foundation/.../obpis/OBPI-0.0.73-09-waiver-ratchet-honesty-contract.md` — brief (evidence).

## Steps

1. **Read surfaces fully**: `historical_self_close_waivers` (closed-set lock exemplar), `lock_handoff_coupling.py` (cutover exemplar), `tautological_test_baseline.json` (shrink-ratchet exemplar), a `validate_cmd.py` scope + its parser wiring, `quality.py` check-step list, `qc_binding.py` classification + a negative control.
2. **Registry + model (TDD)**: author `data/waiver_ratchet_registry.json` declaring each surface's mechanism; a frozen Pydantic model for a registry entry. RED: registry parses; every gate-bearing waiver surface in `data/` is registered (no silent omission).
3. **Validator (TDD)**: RED — an unratcheted surface (no mechanism / violated mechanism) → flagged + exit 3; a surface satisfying its mechanism → pass; `behave_coverage_waivers` growth beyond baseline → fail-closed. GREEN: implement `waiver_ratchet.py`.
4. **Retrofit (data)**: declare the right mechanism for each unratcheted surface in the registry; commit shrink-ratchet baselines where chosen. Make `gz validate --waiver-ratchet` green over the real `data/`.
5. **Wire + self-bind (TDD)**: validate_cmd + parser + quality (gz check) + qc_binding classification + negative control. RED: gz check includes the step; qc-binding lists "Waiver ratchet" bound; negative control fails honestly.
6. **Docs**: manpage; ADR fidelity-assertion row; brief evidence.
7. **Verify**: full bundle below.

## Verification

```bash
uv run gz validate --waiver-ratchet
uv run gz validate --qc-binding
uv run gz validate --cli-alignment
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
```

Expected: `--waiver-ratchet` green over current `data/` (every gate-bearing surface ratcheted), fail-closed (exit 3) the moment a surface goes unratcheted or a shrink-ratchet list grows.

## Notes

- The validator's own green-by-emptiness guard: if the registry is empty or a `data/*waiver*` file exists but is unregistered, that is itself a fail-closed finding (an unregistered waiver surface is the silent-bypass the law closes).
- `data/*_waivers.json` content edits that ADD exemptions are denied — the retrofit adds ratchet metadata/registry declarations only, never widens waiver populations.
