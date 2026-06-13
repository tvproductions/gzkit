# Plan — OBPI-0.0.70-03-guardrail-feedback-prose-rule (retrospective regularization)

- **OBPI:** OBPI-0.0.70-03-guardrail-feedback-prose-rule
- **Parent ADR:** ADR-0.0.70-turn-end-feedback-and-correction-mining (Decision item #3)
- **Lane:** Lite
- **Plan kind:** RETROSPECTIVE. The implementation already exists, committed in
  the rogue bundled git-sync `863250d6` (Fable plow-through of all four
  ADR-0.0.70 OBPIs). This plan is authored after the fact, under operator
  authorization, to regularize the work through the OBPI pipeline `--from=verify`
  and produce the plan-audit alignment artifact the rogue run never created. It
  documents the approach that *was* taken and audits its alignment with the ADR
  and brief — it is not a forward plan for unwritten code.

## Context

ADR-0.0.70 Decision item #3 calls for a binding **guardrail-feedback-prose** rule:
every fail-closed hook and validator emits agent-actionable three-part recovery
prose — what failed / why it is forbidden (cited) / the governed next step
(runnable) — with the OBPI-0.0.70-01 Stop hook as the first enforcement consumer,
an advisory-rules-audit scorecard entry, and `gz agent sync control-surfaces`
propagation. The deliverable exists on disk and was re-verified green this
session (full suite, lint, typecheck, `gz validate --unscoped-rules`,
`gz validate --advisory-scorecard` all PASS).

## Files (all within the brief Allowed Paths)

- `.gzkit/rules/guardrail-feedback-prose.md` — canonical rule (rule-version 0.1.0,
  scoped frontmatter, three-part bar table, Do-Not, promotion path)
- `src/gzkit/rules/guardrail-feedback-prose.md` + vendor mirrors
  (`.claude/rules/`, `.github/instructions/`) — written only by sync
- `docs/governance/advisory-rules-audit.md` — scorecard classification entry
- `data/distribution_baseline_manifest.json` — wheel-distribution registration
- `data/surface_weight_waivers.json` — instruction-files char-budget bridge waiver
- `tests/hooks/test_stop_turn_feedback.py` — shared covering test; `@covers REQ-0.0.70-03-02`

## Steps (as executed / regularized)

1. Author canonical rule `.gzkit/rules/guardrail-feedback-prose.md` with the
   version markers and three-part bar (REQ-03-01, REQ-03-04).
2. Assert the Stop hook's block prose satisfies the bar via the shared covering
   test (`@covers REQ-0.0.70-03-02`) (REQ-03-02).
3. Add the advisory-rules-audit scorecard entry classifying the rule (REQ-03-03).
4. Run `gz agent sync control-surfaces` to propagate canonical → pkg + vendor
   mirrors byte-equivalently (REQ-03-05).
5. Register the rule in the wheel-distribution baseline manifest (REQ-03-06).
6. Regularization this session: clear brief-reconcile drift (req_count → 6
   acceptance criteria matching 6 REQUIREMENT lines; allowlist amended with
   attested `traceability.py` and the two `data/*.json` coupled surfaces), verify
   green, then run the pipeline `--from=verify` to attestation.

## Verification

```bash
uv run gz validate --unscoped-rules
uv run gz validate --advisory-scorecard
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
```

## Step 6a — Plan-before-exploration disclosure (required, narrative)

- **Destination-in-mind:** Before authoring this plan I had already concluded the
  approach: regularize the existing, verified-green rogue implementation through
  the OBPI pipeline `--from=verify` rather than re-implement it — identical to the
  governed remediation applied to sibling OBPI-0.0.70-02. The plan reconstructs a
  destination already chosen; I disclose that explicitly rather than present it as
  fresh planning.
- **Rejected alternatives:**
  1. *Re-implement from scratch* — rejected; the deliverable exists and is sound
     (no latent defects, unlike OBPI-02).
  2. *Edit the brief to silence the reconcile drift / "fix the validator"* —
     rejected after diagnosis proved the req_count drift was a **real brief defect**
     (6 REQUIREMENT lines vs 3 acceptance criteria, violating the 1:1 convention
     OBPI-01 follows), not a validator false-positive; the legitimate fix was to
     author the missing acceptance criteria.
  3. *Withdraw / re-specify OBPI-03* — rejected; the work fulfills ADR Decision
     item #3's declared intent and is verified green.

## Notes

- This is regularization of rogue work, not greenfield. The plan-audit it
  satisfies is an alignment artifact (ADR ↔ brief ↔ plan), authored under
  operator authorization, not a claim that forward planning preceded the code.
