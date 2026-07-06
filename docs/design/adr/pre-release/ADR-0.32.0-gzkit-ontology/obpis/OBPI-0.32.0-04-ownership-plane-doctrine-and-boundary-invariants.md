---
id: OBPI-0.32.0-04-ownership-plane-doctrine-and-boundary-invariants
parent: ADR-0.32.0-gzkit-ontology
item: 4
lane: Lite
status: Completed
# req_atomic (task-discovery subdivision sub-invariant): authoring-only OBPI;
# each REQ is one indivisible declaration unit. REQ-01 is the single
# doctrine-authoring unit (ownership/plane + Harness-Purity written together);
# REQ-02..06 are five negative/state-property STRUCTURAL-FENCE declarations,
# one per parent-ADR Boundary Invariant, each carrying no production labor
# beyond anchoring to an existing ADR entry. No REQ subdivides into seq=02+,
# so seq=01-only is honest, not coarse-bucketing.
req_atomic:
  - REQ-0.32.0-04-01
  - REQ-0.32.0-04-02
  - REQ-0.32.0-04-03
  - REQ-0.32.0-04-04
  - REQ-0.32.0-04-05
  - REQ-0.32.0-04-06
---

# OBPI-0.32.0-04-ownership-plane-doctrine-and-boundary-invariants: Ownership/plane doctrine surface + this ADR's Boundary Invariants as STRUCTURAL-FENCE

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/ADR-0.32.0-gzkit-ontology.md`
- **Checklist Item:** #4 — "ownership/plane doctrine surface + this ADR's ## Boundary Invariants (rebuild-fidelity fence; Tier-B derived-never-authority; sense images structural-only) as STRUCTURAL-FENCE, audited at closeout. [MVP spine]"

**Status:** Completed

## Objective

Author one governance doctrine document — `docs/governance/ontology-ownership-plane-doctrine.md` — that states the ontology's two-axis type separation (ownership `harness|product` × plane `product|process`) and the Harness-Purity Invariant, and record the parent ADR's five already-authored `## Boundary Invariants` (rebuild-fidelity; derived-never-authority; `sense` images structure only; harness-purity; OKF-absorption-open) as STRUCTURAL-FENCE claims that the existing ADR-closeout proof channel audits. This OBPI ships the doctrine surface and the fence declarations only — it adds no ontology model, substrate, CLI verb, JSON schema, validator scope, or runtime contract (those are OBPIs 01–03, 05–07).

## Lane

**Lite** — this OBPI ships only a governance doctrine document and declares the parent ADR's already-authored Boundary Invariants as STRUCTURAL-FENCE claims; it adds no command, JSON schema, validator scope, or runtime contract.

> Lane rationale (decided honestly, AGENTS.md § Lane Rules): the Lite/Heavy
> axis turns on external-contract exposure — command/API/schema/runtime-contract
> changes used by humans or external systems. This OBPI's entire deliverable is
> (a) a documentation surface under `docs/governance/` and (b) STRUCTURAL-FENCE
> REQs that anchor to the parent ADR's `## Boundary Invariants`, which are
> **already authored** in the ADR. The closeout audit is performed by the
> *existing* `gz validate --closeout-proof` machinery (ADR-0.0.69) —
> `resolve_fence_proof` resolves a state-property fence to `pass` when the
> parent ADR carries the `## Boundary Invariants` heading. This OBPI wires **no
> new closeout-audit check, no new validator scope, no CLI, no schema**. Per
> the lane rule, documentation/process-only work stays Lite unless it changes
> an external surface — it does not. (Contrast: had this OBPI implemented a new
> `gz validate --ontology-*` closeout check, that would be a validator/CLI
> contract → Heavy. It does not.)
>
> Gate 5 is NOT waived by Lite: brief-level human attestation is universal
> (ADR-0.0.36), and the completion path resolves lane from the parent ADR
> (Heavy) — so Gate-5 attestation fires at completion regardless of this
> OBPI's own Lite classification.

## Allowed Paths

- `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/obpis/OBPI-0.32.0-04-ownership-plane-doctrine-and-boundary-invariants.md` — this brief (evidence recording)
- `docs/governance/ontology-ownership-plane-doctrine.md` — the ownership/plane + Harness-Purity doctrine surface. **CREATE**

## Denied Paths

- `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/ADR-0.32.0-gzkit-ontology.md` — parent ADR body is REFERENCE ONLY; its five `## Boundary Invariants` are already authored (the STRUCTURAL-FENCE REQs anchor to them; do NOT rewrite)
- `src/gzkit/schemas/**`, `src/gzkit/**` — the Pydantic ontology model, two-axis classification, and Harness-Purity validator are OBPI-0.32.0-01; no code or schema change here
- `src/gzkit/commands/**`, `src/gzkit/cli/**` — the ontology CLI verb group (sense/trace/resense/seams/reach) is OBPI-0.32.0-03; no CLI surface change here
- The networkx substrate + corpus projection (OBPI-02), OKF open-absorption (OBPI-05), work-domain L2 event schema (OBPI-06), source-domain tree-sitter anchors (OBPI-07)
- `mkdocs.yml`, `.gzkit/manifest.json`, CI files, lockfiles, new dependencies
- `.claude/**`, `.agents/**`, `.github/**` generated vendor mirrors (edit canonical surfaces only)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: A governance doctrine document MUST exist at `docs/governance/ontology-ownership-plane-doctrine.md` and MUST state the two-axis separation — ownership (`harness|product`) × plane (`product|process`) — and the Harness-Purity Invariant (`ownership:harness` admits only GovZero-universal object types; gzkit's own product objects are `ownership:product`). [→ REQ-01, SUPPORT]
2. REQUIREMENT: The doctrine MUST record parent ADR `## Boundary Invariants` #1 (rebuild-fidelity — the Tier-B projection reconstructs from L1 canon + L2 ledger with no missed event type, and `sense` self-reports replay completeness and freshness) as a STRUCTURAL-FENCE claim audited at ADR closeout, mapping 1:1 to the ADR entry. [→ REQ-02, STRUCTURAL-FENCE]
3. REQUIREMENT: The doctrine MUST record parent ADR `## Boundary Invariants` #2 (derived-never-authority — the graph is a Tier-B projection that never gates) as a STRUCTURAL-FENCE claim, and MUST itself remain an orientation surface that is not consumed as governance authority by any `gz validate` scope, gate, or closeout step — audited at closeout, never a gate against the current corpus. [→ REQ-03, STRUCTURAL-FENCE]
4. REQUIREMENT: The doctrine MUST record parent ADR `## Boundary Invariants` #3 (`sense` images STRUCTURAL seams only and never claims semantic completeness; semantic-seam recall is deferred to RECALL/Phase-4, L3-advisory) as a STRUCTURAL-FENCE claim audited at closeout, mapping 1:1 to the ADR entry. [→ REQ-04, STRUCTURAL-FENCE]
5. REQUIREMENT: The doctrine MUST record parent ADR `## Boundary Invariants` #4 (harness purity — `ownership:harness` admits only GovZero-universal types; gzkit's product objects CliVerb/Validator/Skill/Chore are `ownership:product` and never enter the harness subgraph) as a STRUCTURAL-FENCE claim audited at closeout, mapping 1:1 to the ADR entry. [→ REQ-05, STRUCTURAL-FENCE]
6. REQUIREMENT: The doctrine MUST record parent ADR `## Boundary Invariants` #5 (OKF absorption stays open — Doc `subtype` = OKF `type` verbatim; no consumer rejects a Doc for an unknown `type`; no OKF frontmatter or link read as authority) as a STRUCTURAL-FENCE claim audited at closeout, mapping 1:1 to the ADR entry. [→ REQ-06, STRUCTURAL-FENCE]

**Guardrails** (constraints on the work, enforced by the Denied Paths and Discovery Checklist below — not separately-numbered REQs): this OBPI must not add, rename, or change any CLI verb, JSON schema, validator scope, or runtime contract (the ontology model/substrate/CLI are OBPIs 01–03); it must not rewrite the parent ADR `## Boundary Invariants` section (those five entries are already authored — the doctrine references them and the fences anchor to them); work stays inside the Allowed Paths, with the doctrine document the only net-new artifact; and this brief is reconciled against the parent ADR `## Boundary Invariants` before authoring so each STRUCTURAL-FENCE REQ maps to a real ADR entry.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the Implementation Summary: "MVP is corpus-first (model + corpus projection + gz ontology sense/trace + doctrine/Boundary-Invariants) ... A two-axis type model classifies every object: ownership (harness|product; a Harness-Purity Invariant admits only GovZero-universal types into ownership:harness ...) x plane (product|process ...)."
- [ ] Parent ADR § Intent — the why-frame: governance work proceeds "in the dark"; the ontology images the actual shape so silent reversals light up instead of slipping through as corrections.
- [ ] Parent ADR § Boundary Invariants — all five entries are the contract this doctrine writes down and the STRUCTURAL-FENCE REQs anchor to.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/ADR-0.32.0-gzkit-ontology.md`

> **STOP:** If you cannot quote the parent ADR § Decision item this OBPI implements AND enumerate the five `## Boundary Invariants`, STOP and re-read. Do not author the doctrine until the Decision quote and the five invariants are in hand.

**Governance (read once, cache):**

- [ ] `docs/governance/state-doctrine.md` — the three-layer model and Rule 5 (Layer-3 derived views never source-of-truth); the Tier-B / derived-never-authority posture this doctrine complements
- [ ] `AGENTS.md` § Governance doctrine surfaces + § req-kind discipline (ADR-0.0.59) — the STRUCTURAL-FENCE proof channel (parent-ADR `## Boundary Invariants` entry) and SUPPORT proof channel (ledger event + validator)
- [ ] `AGENTS.md` / `CLAUDE.md` — agent operating contract

**Context:**

- [ ] `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/` — the closest doctrine + STRUCTURAL-FENCE exemplar (OKF `## Boundary Invariants` + the content-boundary doctrine OBPI-0.30.0-06)
- [ ] Sibling OBPIs 01–03 (model, substrate/projection, ontology CLI verb group) — the surfaces this OBPI's Denied Paths fence off

**Prerequisites (check existence, STOP if missing):**

- [ ] Parent ADR exists: `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/ADR-0.32.0-gzkit-ontology.md`
- [ ] Parent ADR `## Boundary Invariants` section is present with all five entries (rebuild-fidelity; derived-never-authority; `sense` images structure only; harness-purity; OKF-absorption-open)
- [ ] Target doctrine path is net-new, intentionally created here: `docs/governance/ontology-ownership-plane-doctrine.md`

**Existing Code (understand current state):**

- [ ] `docs/governance/state-doctrine.md` reviewed for doctrine-doc shape and tone (a Tier-B posture the ownership/plane doctrine sits beside)
- [ ] `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/obpis/OBPI-0.30.0-06-content-boundary-doctrine.md` reviewed — the doctrine-authoring + STRUCTURAL-FENCE pattern (SUPPORT REQ proven by ledger event + validator; fences audited at ADR closeout)
- [ ] Confirmed no validator consumes the doctrine doc as governance authority today — the boundary is doctrine + closeout-audited (parent ADR Boundary Invariant #2), not a gate against current state

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] No BEHAVIOR REQs in this OBPI (governance-surface deliverable): the doctrine surface proves via the SUPPORT channel (ledger event + `gz validate --documents`); the five fences prove via the STRUCTURAL-FENCE channel (parent-ADR `## Boundary Invariants`, audited at closeout). No `@covers` tests are introduced.
- [ ] Three-channel proof recorded in evidence with real outputs (`gz validate --req-kind-discipline`, `gz validate --closeout-proof`)

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Lite — not required)

- [ ] Not required for Lite lane. The doctrine document is validated for structure by `uv run gz validate --documents` (Gate-2 housekeeping); no `mkdocs --strict` gate fires for this OBPI.

### Gate 4: BDD (Lite — not required)

- [ ] Not required for Lite lane. This OBPI adds no CLI verb or behavior surface; there is no scenario to exercise.

### Gate 5: Human (REQUIRED — universal)

- [ ] Human attestation recorded. Gate 5 is universal (ADR-0.0.36) and the completion path resolves lane from the parent ADR (Heavy); brief-level attestation fires at completion regardless of this OBPI's Lite classification.

## Verification

<!-- CONSTRUCTION HOUSEKEEPING (proves the codebase is healthy) plus the
     OBPI-specific proof commands. AUTHORING CONTRACT: every command is a
     single-program, shell-less `uv run ...` invocation — no &&, ||, |, ;,
     $(...), or redirects. -->

```bash
uv run gz obpi validate --authored
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz validate --closeout-proof
uv run gz covers OBPI-0.32.0-04-ownership-plane-doctrine-and-boundary-invariants
uv run gz lint
uv run gz test
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. -->

```bash
# THE YIELDED PRODUCT: the ownership/plane + Harness-Purity doctrine surface, homed in the governance docs corpus
cat docs/governance/ontology-ownership-plane-doctrine.md
# The five ADR Boundary Invariants resolve as STRUCTURAL-FENCE proof at ADR closeout (existing machinery, no new check wired)
uv run gz validate --closeout-proof
# Every REQ in this brief maps 1:1 to its proof channel (1 SUPPORT + 5 STRUCTURAL-FENCE)
uv run gz covers OBPI-0.32.0-04-ownership-plane-doctrine-and-boundary-invariants
```

## Acceptance Criteria

<!--
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Kind ∈ {BEHAVIOR (@covers test), SUPPORT (ledger event + structural validator),
STRUCTURAL-FENCE (parent-ADR ## Boundary Invariants entry)} — ADR-0.0.59.
The five STRUCTURAL-FENCE REQs map 1:1 to the parent ADR's five ## Boundary Invariants.
-->

- [ ] REQ-0.32.0-04-01 [SUPPORT]: The ownership/plane doctrine document exists at `docs/governance/ontology-ownership-plane-doctrine.md`, states the ownership (`harness|product`) × plane (`product|process`) separation and the Harness-Purity Invariant, and is discoverable in the governance docs corpus — proven by `uv run gz validate --documents` passing AND an `artifact_edited` ledger event citing `docs/governance/ontology-ownership-plane-doctrine.md` emitted at OBPI completion.
- [ ] REQ-0.32.0-04-02 [STRUCTURAL-FENCE]: Rebuild fidelity — the Tier-B ontology projection reconstructs from L1 canon + L2 ledger with no missed event type, and `sense` self-reports its replay completeness and freshness; the load-bearing structural fence recorded as parent ADR `## Boundary Invariants` #1, audited at ADR closeout.
- [ ] REQ-0.32.0-04-03 [STRUCTURAL-FENCE]: Derived-never-authority — the ontology graph is a Tier-B derived projection that never gates and is never read as governance authority; truth lives in L1 canon and L2 ledger, and writeback reaches the graph only by rebuild; recorded as parent ADR `## Boundary Invariants` #2, audited at ADR closeout.
- [ ] REQ-0.32.0-04-04 [STRUCTURAL-FENCE]: `sense` images structure only — the sweep enumerates STRUCTURAL seams and never claims semantic completeness (pre-registered falsifier: "no un-accounted STRUCTURAL seam"), with semantic-seam recall out of scope (RECALL/Phase-4, L3-advisory); recorded as parent ADR `## Boundary Invariants` #3, audited at ADR closeout.
- [ ] REQ-0.32.0-04-05 [STRUCTURAL-FENCE]: Harness purity — `ownership:harness` admits only GovZero-universal object types, and gzkit's own product objects (CliVerb/Validator/Skill/Chore) are `ownership:product` and never appear in the harness subgraph; the Harness-Purity Invariant recorded as parent ADR `## Boundary Invariants` #4, audited at ADR closeout.
- [ ] REQ-0.32.0-04-06 [STRUCTURAL-FENCE]: OKF absorption stays open — Doc `subtype` = OKF `type` verbatim, no consumer rejects a Doc for an unknown `type`, and no OKF frontmatter or link is read as governance authority (preserving OKF ADR-0.30.0 BI-1 and BI-3); recorded as parent ADR `## Boundary Invariants` #5, audited at ADR closeout.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Three-channel proof recorded (SUPPORT ledger+validator; STRUCTURAL-FENCE closeout); no BEHAVIOR REQs, no `@covers` tests introduced
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

### Gate 2 (TDD — three-channel proof)

```text
# Paste `gz validate --req-kind-discipline`, `gz validate --closeout-proof`, and `gz covers` output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Lite lane — Gate 3 not required. Doctrine structure validated by `gz validate --documents` (Gate 2).
```

### Gate 4 (BDD)

```text
# Lite lane — Gate 4 not required (no CLI/behavior surface).
```

### Gate 5 (Human)

```text
# Record attestation text here when required (universal per ADR-0.0.36; parent ADR is Heavy).
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof


`uv run gz validate --closeout-proof` → exit 0 (five STRUCTURAL-FENCE claims resolve against ADR-0.32.0 `## Boundary Invariants`). `uv run gz covers OBPI-0.32.0-04-ownership-plane-doctrine-and-boundary-invariants --json` → all 6 REQs `proof_status=pass`, `behavior_uncovered_reqs=0` (REQ-01 SUPPORT → ledger+validator; REQ-02..06 STRUCTURAL-FENCE → parent-ADR-invariant). ARB receipts: arb-ruff-43c30432134f4c3da94764a8f6e6332d, arb-step-typecheck-0ec2b1dd281c47a8b76b51967e50f6b8, arb-step-unittest-96d23b578ee7498ca3dbf749ec48f84a (6834/6834 pass).

### Implementation Summary


- Files created: `docs/governance/ontology-ownership-plane-doctrine.md` — two-axis (ownership × plane) type model + Harness-Purity Invariant + five Boundary Invariants recorded as STRUCTURAL-FENCE
- Files modified: OBPI brief — FAIL-CLOSED requirements realigned to 6 (1 SUPPORT + 5 STRUCTURAL-FENCE) per operator ratification, restoring sibling-OBPI convention; evidence recorded
- Tests added: none — authoring OBPI with no BEHAVIOR REQs; proves via SUPPORT (ledger + `gz validate --documents`) and STRUCTURAL-FENCE (parent-ADR Boundary Invariants) channels
- Date completed: 2026-07-06
- Attestation status: operator-attested (g0, verbatim "attest completed")
- Defects noted: none; brief req_count drift resolved pre-implementation with operator approval

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.32.0-04 authored docs/governance/ontology-ownership-plane-doctrine.md (two-axis ownership×plane type model + Harness-Purity Invariant + five Boundary Invariants recorded as STRUCTURAL-FENCE, mapping 1:1 to ADR-0.32.0 BI#1–#5); Stage 3 green (ruff arb-ruff-43c30432134f4c3da94764a8f6e6332d, typecheck arb-step-typecheck-0ec2b1dd281c47a8b76b51967e50f6b8, unittest 6834/6834 arb-step-unittest-96d23b578ee7498ca3dbf749ec48f84a, mkdocs --strict clean, closeout-proof + req-kind-discipline + documents pass); all 6 REQs proof_status=pass (behavior_uncovered=0); independent adversarial validation returned NOT-REFUTED.
- Date: 2026-07-06

---

**Date Completed:** 2026-07-06

**Evidence Hash:** -
