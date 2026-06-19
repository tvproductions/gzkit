---
anchor_id: draft-adr-0-0-73-verification-layer-binding-audit
anchor_kind: draft
generated_at: 2026-06-19T14:22:32.273120+00:00
scaffold_version: 1.0
---

# Walkthrough: draft-adr-0-0-73-verification-layer-binding-audit

## 1. What I see (the problem)

**Prompt:** *What did I observe that motivates this change? What hurts if nothing happens?*

**Evidence:**

- ADR-0.0.73

The `gz validate --evaluation-justify-binding` gate (ADR-0.0.26) fires for
`ADR-0.0.73-verification-layer-binding-audit` because the latest
`adr-evaluation` ledger event for that artifact-id
(`.gzkit/ledger.jsonl`, ts `2026-06-19T10:19:36.398648+00:00`) records
`Feature Checklist: 1.0` — below the `low_score_threshold` of `3.0` in
`data/eval_feedback_thresholds.json`. With a sub-threshold dimension and
no qualifying `gz-justify` artifact, the binding fires fail-closed. The
manual `EVALUATION_SCORECARD.md` (Codex, 2026-06-19) corroborates the 1
with the finding: "Checklist and OBPI set drifted repeatedly; the
scorecard itself missed OBPI-09 and the transcript still describes 6
OBPIs." This walkthrough is the REASONED disposition the gate demands —
not a rubber stamp. The honest question is: is the 1.0 still true of the
shipped artifact, or is it a stale snapshot?

## 2. Per-instance severity

**Prompt:** *How bad is each occurrence? One incident, a pattern, or a class of failure?*

**Evidence:**

- ADR-0.0.73 `## Checklist` (lines 236–248): 9 items, sequential, no gaps
- `obpis/` directory: 9 brief files, OBPI-0.0.73-01 … -09

**Verdict: STALE, single dimension, not a class of failure.** The 1.0 was
true of an *intermediate* package state and is no longer true of the
shipped artifact. The drift the scorers caught (six-OBPI transcript vs.
nine-OBPI decomposition; a manual scorecard that miscounted OBPI-09) was a
real authoring-time inconsistency during the 6→9 expansion, but it has
since been reconciled. The current `## Checklist` carries exactly 9 items
(lines 240–248) and the `obpis/` directory holds exactly 9 brief files
(OBPI-0.0.73-01 through -09) — the 1:1 OBPI Decomposition Mandate is
satisfied, not violated. The package authoring even states the invariant
inline (line 233: "The 1:1 mandate holds: checklist (9) <-> OBPI files
(9)"). Severity of the *residual* condition: cosmetic/stale, not
substantive.

## 3. Why this scope

**Prompt:** *Why is the change boundary drawn here and not wider or narrower?*

**Evidence:**

- ADR-0.0.73 `## Q&A Transcript` supersession note (lines 254–257)

The disposition is scoped to authoring a grounded justify record for the
Feature-Checklist dimension only — the one dimension under threshold. No
narrower scope clears the gate (the binding requires a justify artifact
matching the artifact-id slug); no wider scope is warranted because every
other dimension scored ≥3.0 in the same ledger event (Problem Clarity 4,
Decision Justification 4, OBPI Decomposition 4, Lane 4, Scope 4, Evidence
4, Architectural Alignment 4). The only authoring already done to close
the underlying drift — the `## Q&A Transcript` supersession note (lines
254–257) declaring the six-OBPI transcript "historical context, not the
current contract" — belongs to the ADR package itself, not to this record.
This record's boundary is exactly: document the stale-vs-real verdict and
its evidence.

## 4. What it proposes

**Prompt:** *In one paragraph, what is the change?*

**Evidence:**

- ADR-0.0.73 line 233 (1:1 mandate assertion)

This record proposes no change to the ADR. It asserts that the Feature
Checklist 1.0 is a stale-evaluation artifact and that the shipped package
already satisfies the Feature-Checklist criterion: a 9-item checklist in
1:1 sync with 9 OBPI briefs, sequential and gapless, with the transcript
drift explicitly superseded. The proposal is therefore "no corrective
action on the artifact; clear the gate with a grounded justification of
why the low score does not reflect the shipped state."

## 5. Routing decision

**Prompt:** *Direct fix, OBPI ceremony, or new ADR? Cite the threshold that routed it.*

**Evidence:**

- GHI #628 (justify sweep, defect repair)
- AGENTS.md § Defect-fix routing thresholds

Routed as a **direct authoring task under GHI #628** (the justify sweep),
touching only `artifacts/justify/`. No code, schema, or CLI surface
changes; no brief boundary crossed. Under AGENTS.md § Defect-fix routing,
OBPI ceremony is required only when a change crosses brief boundaries or
adds/changes a contract surface — neither holds. The work is a single
governance artifact authored to clear a fail-closed gate, which is the
canonical direct-fix shape. No new ADR is warranted: the underlying ADR is
already Validated (9/9 OBPIs attested per `gz adr status`).

## 6. Why this design is right-sized

**Prompt:** *Why isn't this bigger or smaller? What does this shape defend against?*

**Evidence:**

- `gz adr status ADR-0.0.73-verification-layer-binding-audit`: 9/9 OBPI, Lifecycle Validated, Closeout READY, QC READY

It is not smaller because the gate is fail-closed: without a justify
artifact whose filename matches the slug, `gz check` cannot pass for this
artifact-id — a stub or a deletion would not clear it. It is not bigger
because re-opening the ADR to "fix" a checklist that is already 1:1 with
its OBPIs would be fabricated work: `gz adr status` shows 9/9 OBPIs
attested, Lifecycle Validated, Closeout READY, QC READY. Re-scoring would
also be theater — the deterministic Feature-Checklist heuristic that
produced the 1.0 is the very dim-1/dim-2 shape-grading that
OBPI-0.0.73-07 itself demoted to "structurally complete / substance
UNGRADED" (ledger `obpi_receipt_emitted`, OBPI-0.0.73-07, ts
2026-06-19T10:40:21). This shape defends against the inverse failure: an
agent silencing a real drift by editing the checklist to match a stale
number. Here the checklist is already correct; the record says so with
evidence.

## 7. What convinces me (evidence)

**Prompt:** *Which rules, ledger events, and commits ground this decision?*

**Evidence:**

- cross-platform (.gzkit/rules/cross-platform.md)
- governance-core (.gzkit/rules/governance-core.md)
- models (.gzkit/rules/models.md)
- pythonic (.gzkit/rules/pythonic.md)

1. **Checklist/OBPI 1:1**: ADR `## Checklist` lines 240–248 (9 items)
   one-to-one with `obpis/OBPI-0.0.73-01…-09` (9 files). The mandate is
   stated inline at line 233.
2. **Drift was reconciled, not ignored**: supersession note at lines
   254–257 reclassifies the six-OBPI transcript as historical context.
3. **Artifact is shipped/attested**: `gz adr status
   ADR-0.0.73-verification-layer-binding-audit` → 9/9 OBPI, Validated,
   Closeout READY, QC READY.
4. **The 1.0 is heuristic, not substantive**: the three 2026-06-19 ledger
   evals (08:55:08, 08:55:15, 10:19:36) all record an identical frozen
   score vector, and the Feature-Checklist heuristic that emits it is the
   shape-grading channel OBPI-0.0.73-07 demoted (ledger
   `obpi_receipt_emitted` OBPI-0.0.73-07, 2026-06-19T10:40:21; cause for
   the prior repudiation recorded 2026-06-19T09:57:05). Per
   `.gzkit/rules/governance-core.md`, the ledger — not a derived score —
   is Layer-2 truth, and the ledger shows a complete, attested, 1:1
   package.

## 8. Residual uncertainty

**Prompt:** *What am I not sure about? What would change my mind?*

**Evidence:**

- EVALUATION_SCORECARD.md findings (manual, 2026-06-19)

What would change my mind: if a fresh `gz adr evaluate` run (post the
OBPI-07 honest-structural rework) still emitted Feature Checklist <3.0
*after* re-reading the reconciled 9-item checklist, that would signal a
genuine residual gap rather than a stale snapshot. I have not re-run the
evaluator here because the latest ledger eval (10:19:36) postdates the
checklist reconciliation and still reflects the demoted heuristic, so a
re-run would not be authoritative on substance. The one honest residual:
the manual scorecard's broader findings (e.g., transcript still naming six
OBPIs at the time of scoring) were real authoring defects; my claim is
narrowly that they are now reconciled in the shipped files, not that the
package never drifted. If a reader finds a checklist item with no matching
OBPI brief (or vice versa), that would falsify the 1:1 claim — I checked
both directories and found exact 9↔9 correspondence.
