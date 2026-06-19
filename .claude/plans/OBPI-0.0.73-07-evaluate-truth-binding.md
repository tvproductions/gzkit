# Plan: OBPI-0.0.73-07-evaluate-truth-binding — comprehensively eradicate the shape-as-substance defect in `gz adr evaluate`

**OBPI:** OBPI-0.0.73-07-evaluate-truth-binding
**Parent ADR:** ADR-0.0.73-verification-layer-binding-audit
**Lane:** Heavy (CLI/runtime-contract + ADR Boundary Invariant change)
**Authorization:** operator directive 2026-06-19 — "comprehensively eradicate the shape-as-substance defect in gzkit's ADR evaluator." OBPI-07's prior completion was repudiated 2026-06-19 (`verification-invalid`, attestor g0) after a multi-agent verification-layer audit found the GHI #624 fix cosmetic (docstrings claim substance; bodies still grade by keyword regex / word-count).

## Context

The defect (audit-confirmed, localized to ONE module): `src/gzkit/adr_eval_scoring.py` renders authoritative 1-4 quality scores and a GO/NO-GO verdict for ADR decision SUBSTANCE (dim-1 Problem Clarity, dim-2 Decision Justification) computed from keyword regex (`_REJECTION_RE`, `_NEGATIVE_CONSEQUENCE_RE`, `_CONCRETE_REF_RE`) and word-counts. The PRIOR (repudiated) plan's "fix" was to swap keyword checks for OTHER shape checks (`_word_count > 150`, ref regex) while still calling it "substance grading" — the exact cosmetic trap. The seventh `shape-graded-not-substance` theater signature is inert because `theater_flags=[]` on every registered step, so `_check_theater_signatures` cannot fire.

Judge-subsystem reality (explorer-confirmed): gzkit's judge machinery makes ZERO live LLM calls — it is a deterministic record-and-validate framework. The proven seam exists in `src/gzkit/advisor_qc.py` (`record_verdict` → ARB judge receipt `arb-step-judge-*` → ledger event → read-back), explanation-first disciplined. The heavier ADR-0.0.39/40 judge governance (JudgeInvocation model, leakage/output-discipline/meta-eval validators) is mostly UNBUILT — a named forced-downstream dependency, NOT in OBPI-07 scope.

The fix is three composing parts:
- **A (eradication):** the deterministic evaluator stops presenting shape as authoritative substance — its dim-1/dim-2 checks are relabeled honest structural-completeness signals with decoupled dimension names; NO deterministic score (keyword OR word-count OR regex) is ever a "substance"/"quality" verdict.
- **B (genuine substance):** real substance scores for dim-1/dim-2 come ONLY from a recorded, explanation-first judge verdict read from the receipt store; absent a verdict, substance is reported UNGRADED, never faked by any deterministic proxy.
- **C (self-binding):** the seventh theater signature fires live so `--qc-binding` fail-closes on any future shape-as-substance regression — including a regression back to word-count-as-substance.

## Destination-in-mind disclosure

Approach chosen before authoring: demote-and-decouple (A) + record-and-validate judge channel (B) reusing `advisor_qc`. Rejected alternatives: (1) replace keyword checks with word-count/regex "substance" checks (the PRIOR plan) — rejected, that is shape-as-substance under a new disguise and is precisely what was repudiated. (2) Live LLM call in the evaluator — rejected, violates gzkit's deterministic/stdlib ethos; the judge subsystem is record-and-validate by design. (3) Build all of ADR-0.0.39/40 inside OBPI-07 — rejected as scope explosion / new-capability beyond this ADR.

## Files (OBPI-07 allowed-path scope)

- `src/gzkit/adr_eval_scoring.py` — relabel dim-1/dim-2 (and OBPI dims) as structural-completeness; strip substance-claiming docstrings; route substance to recorded judge verdict; UNGRADED fallback.
- `src/gzkit/adr_eval.py` — demote `EvalVerdict`/`compute_verdict` from quality verdict to a structural-completeness summary; add a separate substance channel to `AdrEvalResult`.
- `src/gzkit/adr_eval_substance.py` **CREATE** — `get_substance_verdict_for_adr()` read-back + the minimal ADR-substance verdict model + explanation-first discipline, modeled on `advisor_qc`.
- `src/gzkit/commands/adr_promote.py` — `adr_eval_cmd` rendering: structural-completeness vs substance channels, decoupled labels, scorecard header disclaimer.
- `src/gzkit/qc_binding.py` — keep `ADR Evaluate` advisory registration; theater-flag plumbing.
- `src/gzkit/governance/trust_audits/qc_binding.py` — wire the seventh `shape-graded-not-substance` signature to fire + its negative-control fixture.
- `tests/governance/fixtures/facade_corpus/shape_graded_not_substance.json` **CREATE** — the calibration fixture.
- `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md` — reword Boundary Invariant #6 to the honest contract.
- `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/obpis/OBPI-0.0.73-07-evaluate-truth-binding.md` — repoint REQs/objective to A+B; record evidence.
- `docs/user/manpages/adr-evaluate.md` — document structural-completeness vs substance channels.
- `tests/` — structural-completeness scoring tests, judge-verdict record/read/discipline tests, seventh-theater-signature firing test, negative-control test.

## Steps

1. **Read the surfaces fully** before editing: `adr_eval_scoring.py`, `adr_eval.py`, `adr_promote.py` (`adr_eval_cmd`), `advisor_qc.py`, `trust_audits/qc_binding.py`, `qc_binding.py`. Trace how the scorecard + verdict render end-to-end.
2. **A — relabel + demote (TDD).** RED: tests asserting (a) no dim emits a "substance"/"quality" label from any deterministic score; (b) deterministic dims carry structural-completeness names distinct from the human rubric; (c) the verdict is framed as structural completeness, not authoritative quality. GREEN: rename dims, strip substance docstrings, reframe `EvalVerdict`/`compute_verdict`/scorecard header.
3. **B — substance channel (TDD).** RED: a recorded explanation-first judge verdict for an ADR dim is read back and reported as the substance score; absent a verdict → UNGRADED, never proxy-faked; explanation-first discipline enforced (non-empty, explanation before verdict). GREEN: `adr_eval_substance.py` + read seam in `adr_eval.py`/`adr_promote.py`.
4. **C — self-binding (TDD).** RED: an evaluator step presenting any deterministic score as authoritative substance is flagged by `--qc-binding` via the seventh signature + negative control. GREEN: firing path in `trust_audits/qc_binding.py` + fixture.
5. **D — governance.** Reword BI #6; repoint OBPI-07 brief REQs/objective; update manpage; `gz cli audit` green.
6. **Verify** the full bundle (below); reconcile the brief.

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --qc-binding
uv run gz validate --cli-alignment
uv run gz adr evaluate ADR-0.0.73-verification-layer-binding-audit
```

Expected after the fix: `gz adr evaluate` separates a structural-completeness summary (deterministic, honestly labeled, decoupled names) from a substance channel (judge-verdict or UNGRADED) — and re-running it on this ADR no longer presents a keyword/word-count-derived GO as a quality verdict.

## Notes

- Forced downstream (named, tracked, NOT done here): full judge governance (leakage / output-discipline / meta-eval validators, JudgeInvocation model) is ADR-0.0.40's unbuilt scope; B reuses the existing `advisor_qc` record-and-validate seam only.
- One-way-door: the BI #6 reword is load-bearing — it changes the invariant's letter (from "grade substance" to "never present shape as authoritative substance; substance comes from a disciplined judge verdict or is UNGRADED") to fulfill its intent. Operator-authorized 2026-06-19.
