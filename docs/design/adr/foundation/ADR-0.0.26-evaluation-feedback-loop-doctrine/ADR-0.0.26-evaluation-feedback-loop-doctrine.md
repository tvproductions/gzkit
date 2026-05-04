---
id: ADR-0.0.26-evaluation-feedback-loop-doctrine
status: Draft
kind: foundation
semver: 0.0.26
lane: heavy
parent:
date: 2026-04-25
---

# ADR-0.0.26-evaluation-feedback-loop-doctrine: Evaluation Feedback-Loop Doctrine

## Persona

`main-session` + `implementer`. Heavy-lane runtime contract change to the
ledger schema, the evaluation surface, and the rule-authoring flow. The work
is the work; the loop the doctrine codifies is observational, not
prescriptive.

## Intent

Close the open feedback loop between gzkit's two reasoning surfaces
(`gz-adr-evaluate` and `gz-justify`) and the rule corpus they should be
informing. Today both surfaces produce structured artifacts — evaluation
scores, red-team challenges, 8-section reasoning scaffolds — and both
artifacts terminate at "agent reasoned and proceeded." Nothing harvests
recurring weak dimensions, recurring red-team-found gaps, or recurring
confusion shapes back into proposed rule edits.

This is the same epistemology as the Opus 4.7 § 6.1.3 "Claude reviews its
own alignment section" pattern: the agent's own structured reasoning
artifacts are a load-bearing source of evidence about where the contract
needs to tighten. gzkit currently exports that evidence into files that
nothing reads.

The doctrine names the loop as canonical and gates each stage on
observational discipline (Layer-2 ledger events, not Layer-1 narrative
recall) per the trust-doctrine T1/T2/T3 invariants.

External evidence: GPT-5.5 § 9.2 (Apollo) reports verbalized eval-awareness
at 22.1% — up from 17.3% / 11.7% on prior checkpoints. The implication for
gzkit is that any feedback loop the agent knows is feeding rule authoring
risks Goodhart drift; the loop's design must treat artifacts as
observational and gate rule promotion on human approval.

## Decision

1. **Persistence.** `gz-adr-evaluate` invocations emit a canonical
   `adr-evaluation` ledger event with payload `{artifact_id, dimensions,
   scores, red_team_challenges_fired, timestamp}`. Today scores terminate at
   stdout; the doctrine binds them to T2 ledger truth.
2. **Auto-trigger.** When any `gz-adr-evaluate` dimension scores < 3.0, OR
   when ≥3 red-team challenges fire, `gz-justify` invocation is required
   before the parent artifact's lifecycle can advance to `Pending` (or the
   next gate). The skill description already prescribes this advisory
   discipline (`gz-justify` triggers when score is < 3.0); the doctrine
   makes the trigger mechanical via a new `gz validate
   --evaluation-justify-binding` scope.
3. **Clustering chore.** A new chore `eval-feedback-cluster` runs
   periodically over recent `adr-evaluation` events and `gz-justify`
   artifacts, groups by recurring weak-dimension or confusion-shape
   patterns, and emits a structured proposals report when a pattern recurs
   ≥3 times across distinct artifacts.
4. **Rule-promotion path.** Each cluster the chore identifies produces an
   *advisory GHI proposal* (not an automatic edit) labeled
   `enhancement` + `eval-feedback`, with provenance trailers naming the
   source `adr-evaluation` event IDs and `gz-justify` artifact paths. The
   GHI is the operator's review surface; rule promotion happens via the
   normal gh-cli + gz-plan path with explicit human approval (Gate 5
   discipline preserved end-to-end).
5. **Provenance trailer convention.** Any rule edit that lands as a result
   of the loop carries a `Eval-feedback-source: <event-id-or-path>` commit
   trailer alongside the existing `Task:` / `Ceremony:` trailer
   (per `.claude/rules/tests.md` § Governance-intent trailers). The trailer
   is mechanically validated by `gz validate --commit-trailers` — the
   provenance is auditable.

## Consequences

### Positive

- Closes the trust-doctrine T2-to-rule-corpus gap: evaluation evidence and
  reasoning artifacts now have a mechanical path back into the rule
  corpus, gated on human approval.
- Aligns gzkit with the Opus 4.7 § 6.1.3 pattern (model reviews own
  outputs as evidence) at the governance layer.
- Surfaces recurring weak dimensions across the ADR corpus that today are
  invisible — a single low-score is noise, but ≥3 instances of the same
  weak dimension across distinct ADRs is a signal the rule corpus is
  missing guidance.
- Provides the prefill ADR (ADR-0.45.0) and the captured-stdout ADR
  (ADR-0.46.0) with a place to land their feedback signals.

### Negative

- Goodhart risk: agents who know `gz-justify` artifacts feed rule
  proposals may write justifications they think will produce rules they
  want. Mitigation: the loop is observational, not prescriptive (the chore
  emits proposals, not edits), and the rule-promotion gate is human
  attestation. Eval-awareness probe research (Opus 4.7 § 6.5.2) is the
  named external evidence that this risk is real and the gating
  discipline is the right shape.
- Adds a new ledger event family. The ledger is the system-of-record, so
  this is the right home — but it grows the schema and `gz validate
  --documents` must be extended to recognize the new event shape.
- Clustering threshold (≥3) is a tuning parameter; too low and the loop
  produces noise, too high and the loop misses signal. Mitigation: the
  threshold lives in `data/eval_feedback_thresholds.json`, calibrated
  empirically over time per the trust-doctrine "Cutoffs are notional
  defaults and should be calibrated over time from project evidence"
  principle.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 1
- Observability: 2
- Lineage: 1
- Dimension Total: 8
- Baseline Range: 4-5
- Baseline Selected: 5
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 5

## Checklist

- [ ] OBPI-0.0.26-01: Persist `gz-adr-evaluate` scores as `adr-evaluation` ledger events; extend `gz validate --documents` to recognize the new event shape
- [ ] OBPI-0.0.26-02: Implement `gz validate --evaluation-justify-binding` — fail-closed when score < 3.0 or ≥3 red-team challenges fire and no `gz-justify` artifact exists for the parent artifact
- [ ] OBPI-0.0.26-03: Author the `eval-feedback-cluster` chore — periodic clustering over `adr-evaluation` events and `gz-justify` artifacts; emits structured proposals report
- [ ] OBPI-0.0.26-04: Wire cluster output into automatic `enhancement` GHI authoring with `Eval-feedback-source` provenance trailer; extend `gz validate --commit-trailers` to validate the new trailer
- [ ] OBPI-0.0.26-05: BDD coverage — heavy-lane `@REQ-…`-tagged scenarios for the full loop (low-score → justify-required → clustering → proposal GHI → human-approved rule edit)

## Q&A Transcript

Authored 2026-04-25 from a session-card review session that surfaced two
related observations: (a) the GPT-5.5 + Opus 4.7 cards both treat the
agent's own structured reasoning as load-bearing evidence; (b) gzkit
already produces structured reasoning via `gz-adr-evaluate` and
`gz-justify` but does not feed it back into the rule corpus. Anthropic's
Prompt Engineering 101 talk (Hannah Moran + Christian Ryan) treated CoT
as an inspectable scratch pad to mine for system-prompt improvements —
the same epistemology this doctrine encodes at the governance layer.

## Evidence

- [ ] Ledger: new `adr-evaluation` event family in `.gzkit/ledger.jsonl`
- [ ] Validator: `gz validate --evaluation-justify-binding`, `gz validate --commit-trailers` extension
- [ ] Chore: `chores/eval-feedback-cluster/`
- [ ] Tests: `tests/governance/test_evaluation_feedback_loop.py`
- [ ] BDD: `features/evaluation_feedback_loop.feature`
- [ ] Docs: AGENTS.md § Behavior Rules; `.claude/rules/tests.md` § Governance-intent trailers

## Alternatives Considered

1. **Make the chore emit edits directly, not GHI proposals** — rejected.
   Direct edits bypass Gate 5 human attestation; the trust doctrine
   requires Layer-2 evidence to flow through human approval before
   becoming Layer-1 canon. Auto-edits would also amplify the Goodhart
   risk (the loop's signal would directly shape the loop's input).
2. **Persist `gz-justify` artifacts only, not `gz-adr-evaluate` scores** —
   rejected. Scores are the cheaper signal (numeric, structured); waiting
   for a `gz-justify` artifact loses the "≥3 instances of same weak
   dimension across the corpus" pattern that scores alone surface.
3. **Tighten thresholds (require all dimensions ≥4.0 to avoid the loop
   firing)** — rejected. The threshold's job is to fire the loop, not
   suppress it; raising the bar to "loop never fires" defeats the
   purpose. Empirical calibration via the data file is the right shape.
4. **Defer until corpus is meaningful** — rejected because two ADRs
   currently in flight (ADR-0.45.0 prefill, ADR-0.46.0 captured-stdout)
   already produce signals this loop should harvest. Authoring the
   doctrine now lets those ADRs land with the loop integrated rather
   than retrofitting it later.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.26 | Completed | Jeffry Babb | 2026-05-03 | Completed - ADR-0.0.26 evaluation feedback loop doctrine: 5/5 OBPIs attested_completed, 24/24 REQs covered (gz adr audit-check PASS); canonical ARB receipts green: arb-ruff-c2d484dd4d3143ba840add9d1f073393, arb-step-typecheck-e840d9b03a5c46d3891881789efbf47d, arb-step-unittest-022716b2c905401cabc78d589b5577c1 (4047 tests OK), arb-step-mkdocs-043d2598003543b892c719dcd477e8ad (strict); 20/20 behave scenarios pass in evaluation_feedback_loop.feature; gz validate --documents clean; tracked defects #394 (validate evaluation-justify-binding solo handler exit-code drift) and #395 (obpi-complete REQ-coverage behave dispatch) carry forward with documented workarounds applied in OBPI-05. |
