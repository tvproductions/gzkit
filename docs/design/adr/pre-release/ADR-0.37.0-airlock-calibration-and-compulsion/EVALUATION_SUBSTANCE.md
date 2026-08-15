# ADR-0.37.0 — Substance Evaluation

**ADR:** ADR-0.37.0-airlock-calibration-and-compulsion
**Evaluated:** 2026-08-14
**Framework:** `.gzkit/skills/gz-adr-evaluate/assets/ADR_EVALUATION_FRAMEWORK.md`

> **DISPATCH MODE: SINGLE-DRIVER.** None of the three mandated personas
> (`spec-reviewer`, `quality-reviewer`, `narrator`) produced receipted independent
> input. **This is not an independent review.** Declared per the degraded-mode
> clause (GHI #770) rather than skipped silently: subagent dispatch was not
> available to this session. Treat every score below as one driver's judgment.

## CLI pre-screen (traceability only — never composited, GHI #624)

`uv run gz adr evaluate ADR-0.37.0` → **STRUCTURALLY COMPLETE**, structural
score **3.75/4.0**, 6 OBPIs scored, substance **0 graded / 2 UNGRADED**.

The CLI grades structural completeness only. Its scores are recorded per
dimension below for divergence tracking; this file is the substance authority.

## Part 1 — ADR dimensions (manual, authoritative)

| # | Dimension | Weight | CLI | Manual | Weighted | Basis |
|---|-----------|--------|-----|--------|----------|-------|
| 1 | Problem Clarity | 15% | 4 | **4** | 0.60 | Problem is *measured*, not asserted: `push: 0, pull: 0, unaccounted: 0, decision: proceed` captured live from `gz airlock in --json` on a real OBPI, plus 20/23 transits and 525 fix-commits/90d. Agree with CLI, independently arrived at. |
| 2 | Decision Justification | 15% | 4 | **4** | 0.60 | D1–D4 each name the mechanism they change and why. Seven rejected alternatives, each with a concrete rejection reason rather than a dismissal. Agree with CLI. |
| 3 | Feature Checklist | 15% | 4 | **4** | 0.60 | Six items, sequential, no gaps, 1:1 with six briefs on disk (`ls obpis/ \| wc -l` = 6). Agree with CLI. |
| 4 | OBPI Decomposition | 15% | 3 | **3** | 0.45 | **Same score, different reason — see divergence note.** |
| 5 | Lane Assignment | 10% | 4 | **4** | 0.40 | `heavy` is correct on the rule's own terms: the ADR adds a CLI-visible refusal, a new commit-trailer contract, and changes ledger event semantics — three external surfaces. Agree with CLI. |
| 6 | Scope Discipline | 10% | 4 | **4** | 0.40 | Three explicit out-of-scope items, each with a stated reason rather than a bare exclusion; the 23/5 exclusion is additionally justified as belonging to a named cross-cutting family. Agree with CLI. |
| 7 | Evidence Requirements | 10% | 4 | **4** | 0.40 | Three fidelity assertions, all runnable, all RED today, each bound to an owning OBPI; two live negative controls named (bounded non-empty seam-map; un-triggered entry fails the claim). Agree with CLI. |
| 8 | Architectural Alignment | 10% | 3 | **3** | 0.30 | **Same score, different reason — see divergence note.** |

**WEIGHTED TOTAL: 3.75 / 4.0 → GO** (threshold 3.0).

### Divergence notes (mandatory per dimension where reasoning differs)

**Dimension 4 — the CLI finding is right by accident and wrong in substance.**
CLI finding: *"OBPI allowed paths overlap significantly."* Verified: all six
briefs carry **byte-identical** scaffold-default Allowed Paths (the parent ADR
package, twice). The overlap is therefore 100% and is a measurement of the
`gz specify` template, not of this decomposition — the heuristic fired on
unauthored scaffolds and would fire identically on any freshly-scaffolded ADR.

The manual score is nonetheless also 3, for a defect the CLI **could not** see:
**OBPI-02 and OBPI-03 both modify `_reconcile` in `src/gzkit/airlock/enter.py`.**
OBPI-02 changes which edges enter it; OBPI-03 changes how it decides `accounted`.
The brief boundary runs through one function. This is workable because the two
are strictly sequential, but it is a genuine seam and must be stated in both
briefs' Allowed Paths at authoring time so the second does not silently
re-litigate the first.

**Dimension 8 — CLI heuristic misfire, but the score survives on other grounds.**
CLI finding: *"No anti-pattern guidance."* That is a keyword miss: the ADR
carries substantial anti-pattern content — override-theater as Negative #1, the
persona's *"an instrument that reports green is not thereby working"*, and
Boundary Invariant 2 forbidding a second forked door. Per this skill's own
constraint, the fix for a keyword miss is **not** to reword for the matcher.

The manual 3 stands for a different, real weakness: that guidance is **scattered
across Persona, Negative Consequences, and Boundary Invariants** rather than
seated where an implementing agent looks. An implementer opening OBPI-05 will not
naturally read the ADR's Persona section. Action item A3 addresses this at brief
authoring rather than by padding the ADR.

## Part 2 — OBPI dimensions

**All six briefs are unauthored scaffolds.** They are scored as they exist, not
as intended — scoring the intent would be the confirmation bias this rubric
exists to prevent. `Testability` and `Clarity` are consequently low across the
board: neither acceptance criteria nor REQ sets have been written.

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|:---:|:---:|:---:|:---:|:---:|:---:|
| 01 ontology-inverse-reach | 4 | 2 | 4 | 4 | 2 | **3.2** |
| 02 airlock-seam-calibration | 2 | 2 | 4 | 3 | 2 | **2.6** |
| 03 seam-accounting-predicate | 2 | 2 | 3 | 4 | 2 | **2.6** |
| 04 transit-trailer-stamp | 3 | 2 | 4 | 3 | 2 | **2.8** |
| 05 session-entry-door | 3 | 2 | 4 | 3 | 2 | **2.8** |
| 06 transit-gate-flip | 2 | 2 | 4 | 4 | 2 | **2.8** |

Scoring notes:

- **No dimension scores 1**, so no brief triggers the mandatory-revision rule.
- **Independence 2 on 02, 03 and 06 is by design, not decomposition failure.**
  02 requires 01's traversal; 03 touches the function 02 rewires; 06 flips the
  gate 04 installs. The operator ruling sequenced this ADR deliberately
  (calibrate → compel), so sequential dependency is the intended shape. It is
  scored honestly rather than excused, but it is not an action item.
- **Testability 2 and Clarity 2 across all six is the authoring gap**, and it is
  the single reason this evaluation is not a clean GO.
- The CLI reported 3.6–3.8 averages for the same six scaffolds. Six
  near-identical scores across six substantively different briefs is itself the
  tell that the pre-screen was measuring the template.

**OBPI average: 2.80** — below the 3.0 threshold.

## Verdict

**CONDITIONAL GO.**

- **ADR: GO** at 3.75/4.0. The decision, its justification, its rejected
  alternatives, its evidence, and its fences are in place. The ADR is ready for
  proposal/defense review as a decision.
- **OBPIs: below threshold** at 2.80 average, entirely attributable to the briefs
  being scaffolds. This blocks *implementation*, not the decision.

The honest reading: **the design is sound and the work is not yet specified.**
Implementation must not begin from these scaffolds.

## Action items

| # | Item | Owner | Blocking |
|---|------|-------|----------|
| A1 | Author all six briefs via `gz-obpi-specify` — acceptance criteria, REQ sets with `[BEHAVIOR]`/`[SUPPORT]`/`[STRUCTURAL-FENCE]` kind tags, real Allowed Paths. Re-run this evaluation after. | next session | **implementation** |
| A2 | At authoring, state the `_reconcile` seam explicitly in OBPI-02 and OBPI-03 Allowed Paths, so the shared function is a declared boundary rather than a discovered collision. | A1 | no |
| A3 | Seat the override-theater anti-pattern (Negative #1) directly in OBPI-02's brief, where the bounded-seam-map negative control lives — not only in the ADR's Persona/Negative sections. | A1 | no |
| A4 | The OBPI-06 flip criterion must be written into the ADR body before OBPI-04 lands, not after. GHI #804 owns it independently; this is the in-ADR half. | before OBPI-04 | **OBPI-06** |

## Red-team

Not run (`--red-team` not requested). Note that the ADR's own Forcing Functions
section already carries an operator-attested pre-mortem, WWHTBT with the shakiest
condition named (ancestor-reach is a dependency proxy, not a disturbance
predictor), constraint archaeology distinguishing real from inherited from
assumed, and an assumption-surfacing entry that argues *against* one of the ADR's
own scoping decisions. A red-team pass should start by attacking that WWHTBT
condition, which is where this ADR is thinnest by its own admission.
