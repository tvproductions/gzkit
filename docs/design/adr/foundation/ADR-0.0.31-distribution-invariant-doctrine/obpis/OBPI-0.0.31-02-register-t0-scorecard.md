---
id: OBPI-0.0.31-02-register-t0-scorecard
parent: ADR-0.0.31-distribution-invariant-doctrine
item: 2
lane: Lite
status: Completed
---

# OBPI-0.0.31-02-register-t0-scorecard: Register T0 Scorecard Entry

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/ADR-0.0.31-distribution-invariant-doctrine.md`
- **Checklist Item:** #2 — "Add T0 scorecard entry in `docs/governance/advisory-rules-audit.md` classifying as **Promotable**, citing ADR-0.0.32 as the tracking promotion ADR; reconcile with the existing Promotable→Mechanical promotion-tracking convention (e.g. how previous Promotable entries record the landing GHI/ADR for their mechanical enforcement)"

**Status:** Draft

## Objective

Register the T0 distribution invariant in `docs/governance/advisory-rules-audit.md` as a **Promotable** scorecard row, naming ADR-0.0.32 as the tracking ADR for mechanical enforcement promotion. Before authoring the row, audit the existing Promotable rows to confirm the column shape (rule name, classification, current state, tracking artifact, landing receipt-id pattern, etc.) and reconcile T0's row with that convention so the scorecard schema stays uniform. The OBPI-0.0.32-07 landing will flip this row from Promotable to Mechanical; this OBPI registers the entry in the Promotable state so that flip has a real row to mutate.

## Lane

**Lite** — single-file documentation entry. Foundation-kind so brief-level Gate 5 still applies per § Lane & Kind Attestation Matrix; foundation-lite OBPIs are NOT self-closeable.

## Allowed Paths

- `docs/governance/advisory-rules-audit.md` — add the T0 Promotable row, conformant with the existing Promotable column shape

## Denied Paths

- `docs/governance/trust-doctrine.md` — T0 doctrine paragraph belongs to OBPI-0.0.31-01
- `docs/governance/distribution_invariant_catalog.md` — failure-mode catalog belongs to OBPI-0.0.31-03
- `src/gzkit/governance/trust_audits.py` — the validator scope that flips this row to Mechanical belongs to OBPI-0.0.32-07
- `src/**`, `pyproject.toml`, `tests/**`, `features/**` — no source / build / test surface in this OBPI
- `docs/design/adr/foundation/ADR-0.0.32-*` — ADR-0.0.32 cross-references should flow forward, not backward through this OBPI

## Requirements (FAIL-CLOSED)

1. The T0 row in `docs/governance/advisory-rules-audit.md` MUST classify T0 as **Promotable** (not Mechanical, not Judgment, not Ambiguous).
2. Before authoring, the operator MUST read at least three existing Promotable rows in the audit to extract the canonical column shape (which fields each row carries: rule name, current classification, tracking ADR/GHI, landing receipt-id pattern, validator scope name pattern, etc.). The T0 row MUST conform to that shape — no novel fields, no missing fields.

   **Representative Promotable row (row 53, lock-handoff-coupling) for shape reference:**

   ```markdown
   | # | Rule | Score | Notes |
   |---|------|-------|-------|
   | 53 | Lock release is coupled to a handoff/register entry: abandon categories are closed, register entries carry minimum information, reaping creates a degenerate register entry, TTL/reap discipline is explicit, and release becomes fail-closed when no valid handoff exists. | **Promotable** | Doctrine exists in the rule file and parent ADR-0.0.41, but OBPI-0.0.41-02/03/04 are still pending for runtime warning/fail-closed enforcement and `gz validate --lock-handoff-coupling`. Until those land, this is a promotable rule with a clear mechanical path rather than already-mechanical enforcement. |
   ```

   Schema extracted from this row: four columns — `#` (sequential rule number), `Rule` (one-sentence rule statement), `Score` (bolded classification), `Notes` (current state + tracking ADR/GHI + future validator scope name + Promotable→Mechanical landing condition). The T0 row MUST carry the same four columns and the same Notes-field pattern (current state + tracking ADR-0.0.32 + future `gz validate --distribution` scope + the OBPI-0.0.32-07 landing condition that flips Promotable → Mechanical). Read at least two more Promotable rows (e.g. rows 23, 29, 30, 49) to confirm the schema generalizes before authoring.
3. The T0 row MUST cite **ADR-0.0.32-canonical-surface-packaging** as the tracking ADR for mechanical-enforcement promotion. Specifically OBPI-0.0.32-07 (`gz validate --distribution`) is the landing point that flips Promotable → Mechanical.
4. The row MUST name the future validator-scope name (`--distribution`) and the future receipt-id prefix (e.g. `arb-distribution-` or whatever the canonical pattern dictates) so OBPI-0.0.32-07 lands against a registered placeholder rather than authoring the row mid-flight.
5. NO doctrine prose (the why-and-what of T0) is permitted in the audit — that lives in `trust-doctrine.md` per OBPI-0.0.31-01. The audit row is a one-line scorecard entry.
6. NO source code, schema, test, or `pyproject.toml` change is permitted. Doctrine-only OBPI.
7. After authoring, `uv run gz validate --documents` MUST exit 0; `uv run mkdocs build --strict` MUST exit 0; `uv run gz validate --advisory-scorecard` (per `AGENTS.md` § Governance doctrine surfaces) MUST exit 0 — the scorecard is self-testing.

> STOP-on-BLOCKERS:
> - If `docs/governance/advisory-rules-audit.md` does not exist or does not contain a Promotable classification (sanity check), STOP — the row this OBPI authors must conform to an existing schema.
> - If the existing Promotable rows differ from each other on column shape (schema drift), STOP — surface the inconsistency as a defect GHI before adding T0 (otherwise this OBPI codifies further drift).
> - If OBPI-0.0.32-07 has been authored differently than expected (the validator scope name or receipt-id pattern was changed in OBPI-0.0.32-07's authored brief), STOP and reconcile — this OBPI's row must match what OBPI-0.0.32-07 actually delivers.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into Implementation Summary
- [ ] Parent ADR § Decision — Mechanical-enforcement contract subsection (gives the validator-scope name and the three-item contract the row references)
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/ADR-0.0.31-distribution-invariant-doctrine.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `docs/governance/advisory-rules-audit.md` — the entire current document; specifically every existing Promotable row to extract the column shape
- [ ] `AGENTS.md` § Governance doctrine surfaces — names the scorecard's role and `gz validate --advisory-scorecard` self-test
- [ ] `AGENTS.md` § Lane & Kind Attestation Matrix — foundation-lite still requires brief-level Gate 5

**Context — sibling OBPIs:**

- [ ] OBPI-0.0.31-01 — author T0 doctrine paragraph (the upstream artifact this row points at)
- [ ] OBPI-0.0.32-07 — `gz validate --distribution` (the future Mechanical-promotion landing point this row tracks)

**Prerequisites (check existence, STOP if missing):**

- [ ] `docs/governance/advisory-rules-audit.md` exists
- [ ] At least three existing Promotable rows in the audit (otherwise the column shape is not yet established as a convention)
- [ ] OBPI-0.0.31-01 is at minimum Draft (so the T0 doctrine paragraph it points at exists conceptually); landing order is OBPI-01 → -02 but authoring can proceed in parallel
- [ ] OBPI-0.0.32-07 is at minimum Draft so the row's future-landing-target is named, not invented

**Existing Code:**

- [ ] Read three existing Promotable rows end-to-end before drafting T0's row
- [ ] If the audit uses a markdown table, read the header row to extract column names; if it uses bullet lists, read the structure of three sibling entries

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded
- [ ] Parent ADR checklist item #2 quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] No code change → no unit-test red→green cycle. Documentation-only.
- [ ] `uv run gz validate --documents` passes after edits
- [ ] `uv run gz validate --advisory-scorecard` passes (the scorecard is self-testing per AGENTS.md § Governance doctrine surfaces)
- [ ] `uv run gz lint` passes
- [ ] `uv run mkdocs build --strict` passes

### Code Quality

- [ ] Lint clean: `uv run gz lint`

### Gate 5: Human (Foundation lite — brief-level)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz validate --documents
uv run gz validate --advisory-scorecard
uv run mkdocs build --strict

grep -q "T0" docs/governance/advisory-rules-audit.md
grep -q "Promotable" docs/governance/advisory-rules-audit.md
grep -q "ADR-0.0.32" docs/governance/advisory-rules-audit.md
```

## Acceptance Criteria

- [ ] REQ-0.0.31-02-01: `docs/governance/advisory-rules-audit.md` contains a T0 row classified **Promotable**
- [ ] REQ-0.0.31-02-02: T0 row conforms to the column shape established by at least three existing Promotable rows (no novel fields, no missing fields)
- [ ] REQ-0.0.31-02-03: T0 row cites ADR-0.0.32-canonical-surface-packaging as the tracking ADR; OBPI-0.0.32-07 named as the Promotable→Mechanical landing point
- [ ] REQ-0.0.31-02-04: T0 row names the future validator-scope (`--distribution`) and receipt-id prefix so OBPI-0.0.32-07 lands against a registered placeholder
- [ ] REQ-0.0.31-02-05: No doctrine prose authored in the audit — the row is a scorecard entry only; doctrine remains in trust-doctrine.md
- [ ] REQ-0.0.31-02-06: `uv run gz validate --advisory-scorecard` exits 0 (self-test of the scorecard schema)
- [ ] REQ-0.0.31-02-07: `uv run gz validate --documents` and `uv run mkdocs build --strict` both exit 0

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent + Decision quote in Implementation Summary
- [ ] **Gate 2 (TDD):** Documentation-only; validation gates exit 0; advisory-scorecard self-test passes
- [ ] **Code Quality:** `gz lint` clean
- [ ] **Value Narrative:** T0 has a registered scorecard entry; OBPI-0.0.32-07 lands against a real row, not authors one mid-flight
- [ ] **Key Proof:** `grep "T0" docs/governance/advisory-rules-audit.md` returns the new row
- [ ] **OBPI Acceptance:** Evidence recorded below
- [ ] **Gate 5 (Foundation lite-lane brief-level human attestation):** Human witness recorded

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste `gz validate --documents`, `gz validate --advisory-scorecard`, and `mkdocs build --strict` output
```

### Code Quality

```text
# Paste `gz lint` output
```

### Gate 5 (Human)

```text
# Record attestation text here when ceremony fires
```

### Value Narrative

Before this OBPI: T0 doctrine exists (per OBPI-0.0.31-01) but has no registered scorecard entry. The scorecard's purpose — every advisory rule has a tracking entry stating its current Promotable/Mechanical/Judgment/Ambiguous classification and the artifact tracking its mechanical promotion — is silently incomplete. After this OBPI: T0 has a registered Promotable row that OBPI-0.0.32-07 mutates to Mechanical at landing time, closing the doctrine → enforcement traceability loop.

### Key Proof


```bash
grep -A 1 "^.*T0.*Promotable" docs/governance/advisory-rules-audit.md
# Expected: T0 row in scorecard format with Promotable classification + ADR-0.0.32 tracking
```

### Implementation Summary


Audit row 57 (the T0 Promotable scorecard entry) registered in `docs/governance/advisory-rules-audit.md`; row notes cite `ADR-0.0.32-canonical-surface-packaging` as the tracking ADR and `OBPI-0.0.32-07` (`gz validate --distribution`) as the Promotable→Mechanical landing point, with `arb-distribution-` reserved as the receipt-id prefix. Summary footer at line 247 records the registration ("Counts updated 2026-05-10 after Distribution Invariant (T0) registered as a Promotable rule (ADR-0.0.31 / OBPI-0.0.31-02)") and the prose narrative at line 256 names OBPI-0.0.32-07 as the mechanical-enforcement landing point. Brief stale references to OBPI-0.0.32-05 corrected to OBPI-0.0.32-07 (the actual landing OBPI on disk). Doctrine-only OBPI; no source / test / schema / `pyproject.toml` change.

- Files created/modified: `docs/governance/advisory-rules-audit.md` (row 57 added under § Distribution Invariant Doctrine (T0); summary counts and narrative updated); `docs/design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/obpis/OBPI-0.0.31-02-register-t0-scorecard.md` (this brief).
- Tests added: n/a (documentation-only; `gz validate --advisory-scorecard` self-test covers the schema invariant)
- Date completed: 2026-05-10
- Attestation status: Foundation-lite brief-level Gate 5 attestation recorded (Jeffry Babb)
- Defects noted: stale OBPI-0.0.32-05 references in this brief corrected to OBPI-0.0.32-07 during completion (authoring-time error, no doctrine impact).

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: Completed - T0 scorecard row registered Promotable per row 57 of docs/governance/advisory-rules-audit.md; ADR-0.0.32 / OBPI-0.0.32-07 cited as the mechanical-enforcement tracking artifacts. Receipts: arb-ruff-11f7666553924096a93e047d7566efc2, arb-step-typecheck-a250586a5a9f486cbba384d01b70aa91, arb-step-unittest-0d7f4e6b558942429fac259135b57bf5, arb-step-mkdocs-d1c04140e5ab433794e513c859685a27. 7 REQs covered by gz validate --advisory-scorecard self-test (REQ-06), advisory-scorecard self-test green.
- Date: 2026-05-10

---

**Brief Status:** Completed

**Date Completed:** 2026-05-10

**Evidence Hash:** -
