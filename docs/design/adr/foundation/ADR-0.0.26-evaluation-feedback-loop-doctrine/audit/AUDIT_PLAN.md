# AUDIT PLAN — ADR-0.0.26-evaluation-feedback-loop-doctrine

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.0.26-evaluation-feedback-loop-doctrine |
| ADR Title | Evaluation Feedback-Loop Doctrine |
| SemVer | 0.0.26 |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.26-evaluation-feedback-loop-doctrine |
| Audit Date | 2026-05-03 |
| Auditor(s) | Jeffry Babb (operator), main-session (agent) |

## Purpose

Confirm ADR-0.0.26 implementation is complete by validating each of its five
Decision claims with reproducible CLI evidence, then transition lifecycle
from `Completed` → `Validated`.

**Audit Trigger:** Post-implementation Gate-5 validation. All 5 OBPIs
(`OBPI-0.0.26-01`..`05`) reached `attested_completed` on 2026-05-03;
`gz adr audit-check ADR-0.0.26` reports PASS with 24/24 REQs covered.
Closeout phase is `attested`, closeout_ready=true. Layer-2 ledger proof
is complete; this audit consumes that proof and demonstrates the delivered
feedback loop end-to-end before emitting the `validated` receipt.

## Scope & Inputs

**Primary contract surfaces (the five Decisions of ADR-0.0.26):**

1. **Persistence** — `gz adr evaluate` emits canonical `adr-evaluation`
   ledger events with `{artifact_id, dimensions, scores,
   red_team_challenges_fired, timestamp}` payload. Validated by:
   - `uv run gz validate --documents` (event shape recognized)
   - Inspection of `.gzkit/ledger.jsonl` `adr-evaluation` events

2. **Auto-trigger / fail-closed gate** — `gz validate
   --evaluation-justify-binding` fails closed when any `gz-adr-evaluate`
   dimension scores < 3.0 OR ≥3 red-team challenges fire and no
   `gz-justify` artifact exists for the parent artifact. Validated by:
   - `uv run gz validate --evaluation-justify-binding --help` (flag
     registered)
   - `data/eval_feedback_thresholds.json` (configurable thresholds present)
   - `src/gzkit/governance/trust_audits/evaluation_justify_binding.py`
     (validator module present)

3. **Clustering chore** — `eval-feedback-cluster` chore runs over recent
   `adr-evaluation` events and `gz-justify` artifacts, groups by recurring
   weak-dimension/confusion-shape patterns, emits structured proposals when
   a pattern recurs ≥3 times across distinct artifacts. Validated by:
   - `uv run gz chores show eval-feedback-cluster` (chore registered)
   - `uv run gz chores validate eval-feedback-cluster` (layout valid)

4. **Rule-promotion path** — Each cluster produces an *advisory GHI
   proposal* (not an automatic edit) labeled `enhancement` +
   `eval-feedback`, with provenance trailers. Validated by:
   - `uv run gz chores propose-ghi eval-feedback-cluster --help` (verb
     registered)
   - `uv run gz chores propose-ghi eval-feedback-cluster --dry-run`
     (proposal payload renders)

5. **Provenance trailer** — Rule edits closing eval-feedback work carry a
   `Eval-feedback-source: <event-id-or-artifact-path>` commit trailer,
   mechanically validated by `gz validate --commit-trailers`. Validated by:
   - `uv run gz validate --commit-trailers --help` (flag accepts
     trailer)
   - Behave scenarios in `features/evaluation_feedback_loop.feature`
     exercising trailer happy/sad paths

**System-health surfaces (relied on for ledger trust):**

- `uv run gz adr audit-check ADR-0.0.26` (Layer-2 ledger proof)
- `uv run gz adr report ADR-0.0.26` (lifecycle status)
- `uv run gz adr status ADR-0.0.26 --json` (closeout readiness)

## Planned Checks

| # | Check | Command | Expected Signal | Status |
|---|-------|---------|-----------------|--------|
| C1 | Ledger proof complete | `uv run gz adr audit-check ADR-0.0.26` | `PASS All linked OBPIs are completed with evidence`; 24/24 REQ coverage | Planned |
| C2 | Lifecycle pre-state | `uv run gz adr report ADR-0.0.26` | Lifecycle=Completed, OBPI=5/5, Closeout=READY, QC=READY | Planned |
| C3 | D1 — `adr-evaluation` event family present | grep `.gzkit/ledger.jsonl` for `"event": "adr-evaluation"` | ≥1 event with payload schema (`artifact_id`, `dimensions`, `scores`, …) | Planned |
| C4 | D1 — validator recognizes event shape | `uv run gz validate --documents` | `Validated: documents` (zero errors) | Planned |
| C5 | D2 — justify-binding flag registered | `uv run gz validate --help \| grep evaluation-justify-binding` | Flag listed with description | Planned |
| C6 | D2 — thresholds config present | `cat data/eval_feedback_thresholds.json` | `low_score_threshold` + `red_team_count_threshold` keys | Planned |
| C7 | D2 — validator module present | `ls src/gzkit/governance/trust_audits/evaluation_justify_binding.py` | File exists | Planned |
| C8 | D3 — clustering chore registered | `uv run gz chores show eval-feedback-cluster` | Chore metadata renders (description, owner, paths) | Planned |
| C9 | D3 — chore layout valid | `uv run gz validate --chores-layout` | `Validated: chores_layout` | Planned |
| C10 | D4 — propose-ghi verb registered | `uv run gz chores propose-ghi --help` | Verb listed with `eval-feedback-cluster` accepted | Planned |
| C11 | D4 — proposal renders dry-run | `uv run gz chores propose-ghi eval-feedback-cluster --dry-run` | Proposal body includes `Eval-feedback-source:` trailer + `enhancement` + `eval-feedback` labels | Planned |
| C12 | D5 — commit-trailers validator covers Eval-feedback-source | `uv run gz validate --commit-trailers --help` (and inspect implementation) | `Eval-feedback-source` recognized as known trailer | Planned |
| C13 | D5 — BDD scenarios pass | `uv run -m behave features/evaluation_feedback_loop.feature` | 20/20 scenarios pass, 114/114 steps pass | Planned |
| C14 | REQ coverage parity | `uv run gz covers ADR-0.0.26 --json` | `uncovered_reqs: 0`, `coverage_percent: 100.0` (24/24) | Planned |
| C15 | Heavy gates green | `uv run gz gates --adr ADR-0.0.26` | All 5 gates pass | Planned |
| C16 | Documents validator clean | `uv run gz validate --documents` | Zero errors | Planned |

## Risk Focus

- **Goodhart drift** — the loop is observational (chore emits proposals,
  not edits) and rule promotion is human-attested. The audit verifies the
  observational/advisory shape of the chore output (proposal vs. edit) at
  C11.
- **GHI #394 — solo-handler exit-code drift** — `gz validate
  --evaluation-justify-binding` exits 1 instead of 3 when invoked alone;
  documented workaround in OBPI-05 BDD scenarios assert `exits non-zero`.
  Not blocking for VALIDATED — the gate fires correctly; only the exit
  code drifts. Tracked open defect.
- **GHI #395 — REQ-coverage gate dispatches behave refs through unittest** —
  surfaced during OBPI-05 Stage-5; documented workaround applied
  (traceability shim). Not blocking for VALIDATED — REQ coverage is
  satisfied. Tracked open defect.
- **Ledger schema growth** — new `adr-evaluation` event family. Validated
  by C4 (`gz validate --documents` accepts shape) and C16 (no schema
  errors).
- **Threshold tuning** — clustering threshold (≥3) lives in
  `data/eval_feedback_thresholds.json` for empirical calibration; C6
  verifies the file is the source of truth.

## Findings Placeholder

Captured in `AUDIT.md` after execution.

## Acceptance Criteria

- All 16 Planned Checks executed; results recorded in `audit/AUDIT.md`
  with ✓/✗/⚠.
- Proof logs saved under
  `docs/design/adr/foundation/ADR-0.0.26-evaluation-feedback-loop-doctrine/audit/proofs/`
  and referenced in `AUDIT.md`.
- Feature Demonstration (Step 3) shows each of the five Decisions running
  end-to-end with live output.
- Tracked defects (GHI #394, #395) noted with workaround status — both
  carry forward as known issues, neither blocks VALIDATED.
- `uv run gz adr report ADR-0.0.26` shows `Validated` after receipt
  emission.

## Attestation Placeholder

Operator's verbal `accept audit` / `verify audit` ack relayed by agent into
the `validated` receipt via the `gz adr audit-begin` /
`gz adr audit-end` ceremony pair (GHI #292 agent-relayed branch).
