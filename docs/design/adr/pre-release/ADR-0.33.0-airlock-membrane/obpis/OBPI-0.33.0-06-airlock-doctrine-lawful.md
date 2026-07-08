---
id: OBPI-0.33.0-06-airlock-doctrine-lawful
parent: ADR-0.33.0-airlock-membrane
item: 6
lane: Heavy
status: Draft
req_atomic:
  # Each REQ is one indivisible unit of labor, no sub-step below it — 01 the
  # two-doc Draft->binding promotion (one edit sweep), 02 the §2 seam
  # BODY-and-BOUNDARY widening carried in the SAME promotion, 03 the doctrinal
  # binding assertion (the lawful doctrine names OBPI-02's already-registered
  # §5 claim as its teeth; no code), 04 the §8 campaign-gate checkbox
  # discharge. No labor subdivided below any REQ.
  - REQ-0.33.0-06-01
  - REQ-0.33.0-06-02
  - REQ-0.33.0-06-03
  - REQ-0.33.0-06-04
---

# OBPI-0.33.0-06-airlock-doctrine-lawful: Airlock Doctrine Lawful

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/ADR-0.33.0-airlock-membrane.md`
- **Checklist Item:** #6 - "Doctrine made lawful (section-8 gate): promote work-phases-and-airlock.md + four-phases-of-work.md from Draft North Star to binding, including the section-2 seam = BODY-and-BOUNDARY widening; register the section-5 @enforces claim binding. [STRUCTURAL-FENCE; the one-way door -- sequenced last, behind the proven NC]"

**Status:** Draft

## Objective

Discharge the campaign's section-8 "work-phase theories lawful" 1.0 gate by promoting `docs/governance/work-phases-and-airlock.md` and `docs/governance/four-phases-of-work.md` from "Draft North Star" / "Draft theory" to BINDING doctrine — carrying, in the SAME promotion, the section-2 seam-definition widening (from "a seam is therefore not a node-type but an edge" to "a seam is both a BODY and a BOUNDARY; the airlock reasons about both", operator refinement) — where the now-lawful doctrine names the already-registered, floor-member `airlock-in-unaccounted-seam` claim (OBPI-02's landing keystone) as its enforcement teeth. This OBPI ships ONLY the doctrine-status transition, the section-2 widening, and the Phase-3 campaign checkbox — it registers no code and edits no runtime surface. It is the ONE-WAY DOOR of the airlock ADR: un-drafting a lawful North Star is costly, so it is sequenced LAST and does not fire until OBPI-02's section-5 negative control bites in live production (verified green through the existing `gz validate --qc-binding` meta-validator).

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

Heavy is inherited from the parent ADR (Heavy lane) and from the weight of the
change: this is the one-way STRUCTURAL-FENCE door that makes two North Star docs
BINDING governance doctrine — a governance-contract surface that later
validators and skills ground against, and an irreversible-costly transition
(un-drafting a lawful North Star). No runtime code is registered here (the
section-5 claim and its floor-wiring are owned by OBPI-02, the landing keystone
that lands FIRST); this OBPI's surface is the two docs, the campaign checkbox,
and a one-way-door regression test.

## Allowed Paths

<!-- First backtick token on each bullet is the path; **CREATE** marks net-new
     files (existence-gate exempt, GHI #419). -->

- `docs/governance/work-phases-and-airlock.md` — promote the `**Status:**` line from "Draft North Star" to binding AND apply the section-2 seam widening (the single "a seam is therefore not a node-type but an **edge**" line becomes the BODY-and-BOUNDARY statement)
- `docs/governance/four-phases-of-work.md` — promote the `**Status:**` line from "Draft theory" to binding (companion doctrine; no body change beyond status)
- `docs/governance/build-to-1.0-campaign-2026-06-30.md` — check the section-7 Phase 3 (HATCH) checklist checkbox `- [ ]` -> `- [x]` as the section-8-gate lawful-making evidence
- `tests/test_airlock_doctrine_lawful.py` — **CREATE**: the one-way-door regression guard — asserts neither doc carries a "Draft North Star" / "Draft theory" status line, the section-2 BODY-and-BOUNDARY widening string is present, and the Phase 3 campaign checkbox is checked; a tripwire against silent un-drafting of the lawful North Star
- `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/ADR-0.33.0-airlock-membrane.md` — parent ADR `## Boundary Invariants` #2 and #4 are the STRUCTURAL-FENCE anchors (read-only reference, no edit)
- `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/obpis/OBPI-0.33.0-06-airlock-doctrine-lawful.md` — this brief (evidence)

## Denied Paths

<!-- OBPI-01..03 (behavior spine), OBPI-04 (mx door), OBPI-05 (permitted-entry)
     are sibling OBPIs — their surfaces are out of scope here. -->

- `src/gzkit/enforcement.py` — the section-5 claim's registration AND its floor-wiring (`_ensure_airlock_claims_registered()` into `_ensure_production_claims_registered()`) are OWNED by OBPI-02, the landing keystone that lands FIRST and proves the NC bites through the floor. This OBPI lands LAST and cannot be the registrar; it never edits this file.
- `src/gzkit/airlock/**` — the airlock primitive and the section-5 claim's fixture/entrypoint are OBPI-01/02/03; this OBPI ships no airlock behavior and registers no claim
- `src/gzkit/mx/**` — the mx door is OBPI-04
- `src/gzkit/commands/permitted_entry.py`, any permitted-entry surface — OBPI-05
- The parent ADR `## Boundary Invariants` section — read-only anchor; this OBPI never edits the parent ADR
- New runtime dependencies, CI files, lockfiles
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. NEVER/ALWAYS language. -->

1. REQUIREMENT: Deliver ONLY the doctrine-lawful transition — promote both North Star docs Draft->binding, carry the section-2 seam BODY-and-BOUNDARY widening in the SAME promotion, and check the Phase 3 campaign checkbox. No code registration and no runtime-surface edit: the section-5 `airlock-in-unaccounted-seam` claim is already a registered floor member (OBPI-02); this OBPI only makes the doctrine that NAMES it lawful.
2. NEVER: promote the doctrine lawful until OBPI-02's section-5 live negative control (`gz validate --qc-binding`) bites un-forced in production. This is the one-way-door discipline (parent ADR § Consequences Negative #6, § Decision "gated-breadth OBPIs that do not begin until the NC bites live"): un-drafting a lawful North Star is costly, so this OBPI is sequenced LAST behind the proven live NC and must STOP if that precondition is unmet.
3. ALWAYS: carry the section-2 seam widening in the SAME promotion commit that flips the status line — the widening (BODY-and-BOUNDARY) and the Draft->binding transition are one atomic doctrine change; landing the status flip without the widening ships an incomplete lawful doctrine (a correction, not an enhancement).
4. NEVER: edit the parent ADR, `src/gzkit/enforcement.py`, any `src/gzkit/airlock/**` surface, the mx door, or the permitted-entry door — the section-5 claim's fixture/entrypoint AND its floor-wiring are owned by OBPI-02 (the landing keystone, lands first); this OBPI registers nothing and touches no runtime surface.
5. NEVER: re-register, fork, or re-slug the section-5 claim — the lawful doctrine references the SINGLE canonical `airlock-in-unaccounted-seam` floor member routed through the EXISTING `gz validate --qc-binding` meta-validator (parent ADR Boundary Invariant #6 — one enforcement-claim surface, not two; no new scope is forked). The doctrine names the claim as its teeth; it never mints a second one.
6. ALWAYS: reconcile this brief with the parent ADR § Decision and § Boundary Invariants before implementation, and confirm the section-5 NC precondition (OBPI-02 landed, NC bites live) is satisfied.

> STOP-on-BLOCKERS: if the OBPI-02 section-5 live NC has not yet bitten in production, print a BLOCKERS list and HALT — the one-way door does not open early.

## Discovery Checklist

<!-- Read the structured input (parent ADR § Decision) before the unstructured
     one (allowed paths, prerequisites). Order matters (GHI #321). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into `### Implementation Summary`. Checklist item #6 IS the contract: "Doctrine made lawful (section-8 gate): promote work-phases-and-airlock.md + four-phases-of-work.md from Draft North Star to binding, including the section-2 seam = BODY-and-BOUNDARY widening; register the section-5 @enforces claim binding. [STRUCTURAL-FENCE; the one-way door -- sequenced last, behind the proven NC]".
- [ ] Parent ADR § Decision — the sequencing precondition, verbatim: "mx, permitted-entry, and the doctrine-lawful promotion are gated-breadth OBPIs that do not begin until the NC bites live" — and § Consequences Negative #6: "The doctrine-lawful promotion (FC-6) is the one true one-way door ... sequenced LAST and does not fire until the tracer + live NC have earned it".
- [ ] Parent ADR § Boundary Invariants #2 (the gate fires on every entry) and #4 (an un-accounted seam makes GO structurally unreachable) — the STRUCTURAL-FENCE anchors for REQ-01 and REQ-02.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/ADR-0.33.0-airlock-membrane.md`

> **STOP:** If you cannot quote the parent ADR § Decision item #6 that this OBPI implements, OR if the OBPI-02 section-5 live NC has not yet bitten in production, STOP. The one-way door is sequenced LAST behind the proven live NC — do not proceed to Allowed Paths, Prerequisites, or implementation until both the Decision quote is in hand and the NC precondition is confirmed.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § "Every REQ … [kind]" (ADR-0.0.59) — the REQ-kind discipline the Acceptance Criteria below obey (STRUCTURAL-FENCE proves via a parent-ADR `## Boundary Invariants` entry; SUPPORT proves via a ledger event + a structural validator).
- [ ] `.claude/rules/brief-heading-conventions.md` — evidence sections stay H3.
- [ ] The two North Star docs being made lawful: `docs/governance/work-phases-and-airlock.md` (§2 two-graph / seam definition; §3 same-shape airlock) and `docs/governance/four-phases-of-work.md`.

**Context:**

- [ ] Sibling OBPI-0.33.0-01/02/03 (the airlock spine) — OBPI-02 (the landing keystone) authors the `airlock-in-unaccounted-seam` claim's fixture + entrypoint, wires it into the enforcement floor, and routes the section-5 NC through the existing `gz validate --qc-binding` meta-validator. This OBPI is the LAST in the ADR; it only makes the doctrine that names that claim lawful.
- [ ] `docs/governance/build-to-1.0-campaign-2026-06-30.md` §7 Movement III Phase 3 (HATCH) — the checklist line whose checkbox this OBPI checks as the §8-gate discharge.

**Prerequisites (check existence, STOP if missing):**

- [ ] `docs/governance/work-phases-and-airlock.md` present and still carrying its "Draft North Star" status line (the promotion source state).
- [ ] `docs/governance/four-phases-of-work.md` present and still carrying its "Draft theory" status line.
- [ ] OBPI-02 landed and attested: the `airlock-in-unaccounted-seam` claim is a registered floor member and `gz validate --qc-binding` runs green with that claim among the verified set, i.e. the section-5 live NC has bitten un-forced in production (the one-way-door precondition).
- [ ] Parent ADR present, registered in `gz state`, and carrying a `## Boundary Invariants` section with entries #2 and #4 (the STRUCTURAL-FENCE anchors).

**Existing Code (read; do NOT modify — establishes the conventions this OBPI grounds against):**

- [ ] `src/gzkit/req_kind.py` `resolve_fence_proof` / `resolve_support_proof` — how STRUCTURAL-FENCE and SUPPORT proofs mechanically resolve, so the Acceptance Criteria citations (parent-ADR `## Boundary Invariants` anchor; `gz validate --qc-binding` + `enforcement_claim_verified` ledger event; `gz validate --documents`) are genuine.
- [ ] `src/gzkit/enforcement.py` `run_meta_validator` + `_emit_verified_receipts` — READ-ONLY reference: confirms the `airlock-in-unaccounted-seam` claim (registered by OBPI-02) emits an `enforcement_claim_verified` ledger event on a clean floor run, the SUPPORT ledger arm REQ-03 cites. This OBPI never edits this file.
- [ ] `docs/governance/work-phases-and-airlock.md` §2 and its `**Status:**` line — the exact "a seam is therefore not a node-type but an **edge**" text REQ-02 widens and the "Draft North Star" status REQ-01 promotes.
- [ ] `docs/governance/build-to-1.0-campaign-2026-06-30.md` §7 Phase 3 (HATCH) checkbox line — the exact `- [ ]` REQ-04 flips to `- [x]`.

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] The two North Star docs render clean under `--strict` after promotion

### Gate 4: BDD (Heavy only)

<!-- gz-validate-skip: command-shape -->
- [ ] No new operator-visible behavior surface in this OBPI — the airlock behavior (`gz airlock` verbs, the `--qc-binding` meta-validator routing) is owned by OBPI-01/02/03 and discharged by their BDD; this OBPI ships a doctrine-status transition + the §2 widening + a doctrinal binding assertion, all proven structurally (STRUCTURAL-FENCE anchor / SUPPORT ledger+validator), and contributes no `features/` scenario.

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded (universal, ADR-0.0.36)

## Verification

<!-- CONSTRUCTION HOUSEKEEPING (lint, type, test) proving the codebase is healthy.
     AUTHORING CONTRACT: single-program, shell-less invocations only — no &&, ||,
     |, ;, $(...), or redirects (GHI #415). One command per line. -->

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI (the one-way door — runs only after
# OBPI-02's section-5 NC bites live in production)
uv run gz validate --qc-binding
uv run -m unittest tests.test_airlock_doctrine_lawful -v
```

## Demo

<!-- THE YIELDED PRODUCT: two North Star docs now BINDING, the §2 seam widened
     to BODY-and-BOUNDARY, the §8 campaign gate discharged, and the §5 claim a
     meta-validated floor member. Concrete, runnable invocations (not --help). -->

```bash
# The North Star docs are now BINDING — neither carries a Draft status line
grep -c "Draft North Star" docs/governance/work-phases-and-airlock.md
grep -c "Draft theory" docs/governance/four-phases-of-work.md

# The section-2 seam-definition widening is present (BODY + BOUNDARY, both senses)
grep -n "a seam is both a BODY" docs/governance/work-phases-and-airlock.md

# The section-8 campaign gate is discharged — the Phase 3 (HATCH) checkbox is checked
grep -n "x] \*\*Phase 3 — HATCH" docs/governance/build-to-1.0-campaign-2026-06-30.md

# The doctrine's enforcement teeth: the section-5 airlock-in-unaccounted-seam
# claim (registered by OBPI-02) is a verified floor member — its live NC bites,
# green through the EXISTING meta-validator (no new scope forked, BI #6)
uv run gz validate --qc-binding
```

## Acceptance Criteria

<!-- Each REQ carries exactly one [kind] tag (ADR-0.0.59): BEHAVIOR proves via a
     @covers test; SUPPORT via a ledger event + structural validator; STRUCTURAL-FENCE
     via a parent-ADR ## Boundary Invariants entry. -->

- [ ] REQ-0.33.0-06-01 [STRUCTURAL-FENCE]: `docs/governance/work-phases-and-airlock.md` and `docs/governance/four-phases-of-work.md` are promoted from Draft to BINDING — after this OBPI neither doc carries a "Draft North Star" or "Draft theory" status line, and both stand as the airlock's lawful North Star doctrine. This one-way doctrine transition is the structural fence the whole airlock membrane rests on — that every entry into the project ecosystem crosses the same in/out gate — and maps to parent ADR-0.33.0 `## Boundary Invariants` #2 (the gate fires on every entry; the reason/door selects ceremony weight, never whether the gate fires); anchored there and audited at ADR closeout, not by a per-OBPI behavior test.
- [ ] REQ-0.33.0-06-02 [STRUCTURAL-FENCE]: the section-2 seam-definition widening is carried in the SAME promotion — `work-phases-and-airlock.md` §2 no longer reads "a seam is therefore not a node-type but an edge" (the boundary-only sense) but "a seam is both a BODY (a contiguous region of similarity) and a BOUNDARY (the join between regions); the airlock reasons about both" (operator refinement). This widened seam definition is the doctrine of what a "seam" quantifies over, and maps to parent ADR-0.33.0 `## Boundary Invariants` #4 (an un-accounted seam makes GO structurally unreachable — the widened body-and-boundary seam-set is exactly what that fence ranges over); anchored there and audited at ADR closeout.
- [ ] REQ-0.33.0-06-03 [SUPPORT]: the now-lawful North Star doctrine names, as its enforcement teeth, the already-registered floor-member `airlock-in-unaccounted-seam` claim (the airlock's "refuses GO on an un-accounted seam" guard, registered by OBPI-02 and routed through the EXISTING meta-validator — one enforcement-claim surface, not a forked scope, parent ADR Boundary Invariant #6). This OBPI registers no code; it asserts the doctrinal binding is coherent and live. Proven by `uv run gz validate --qc-binding` exiting 0 with that claim among the verified floor set (post-OBPI-02, the live NC bites un-forced) AND an `enforcement_claim_verified` ledger event citing the `airlock-in-unaccounted-seam` claim emitted by the meta-validator on a clean floor run.
- [ ] REQ-0.33.0-06-04 [SUPPORT]: the campaign's section-8 "work-phase theories lawful" 1.0 gate is discharged — the Movement III Phase 3 (HATCH) checkbox in `docs/governance/build-to-1.0-campaign-2026-06-30.md` is checked (`- [ ]` -> `- [x]`) as the lawful-making evidence, coherent with the two docs now being binding. Proven by `uv run gz validate --documents` exiting 0 AND an `artifact_edited` ledger event citing `docs/governance/build-to-1.0-campaign-2026-06-30.md`.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
</content>
</invoke>
