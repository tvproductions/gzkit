---
id: OBPI-0.0.43-06-domain-cascade-validators-check-pipeline
parent: ADR-0.0.43
item: 6
lane: Heavy
status: Draft
---

# OBPI-0.0.43-06-domain-cascade-validators-check-pipeline: cascade integrity + view-freshness validators

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.43-ddd-domain-cascade/ADR-0.0.43-ddd-domain-cascade.md`
- **Checklist Item:** #6 — "gz validate `--domain-cascade` + `--domain-views-fresh` + wire into gz check — Cascade integrity validator (BC resolution, glossary marker resolution, context-map entry presence for cross-context ADRs); freshness validator for Layer-3 derived views."

**Status:** Draft

## Objective

Land two new validator scopes on `gz validate`: `--domain-cascade` (structural cascade integrity) and `--domain-views-fresh` (Layer-3 derived view staleness). Both fail-closed exit 3 with a `Resolve:` line on every failure. Both wired into `gz check` default pipeline. This is the document-validation-time gate that complements OBPI-04's authoring-time gate.

## Lane

**Heavy** — adds two new validator scopes that become required in CI / local pre-merge pipelines.

## Allowed Paths

- `src/gzkit/governance/trust_audits/domain_cascade.py` — NEW; cascade integrity validator
- `src/gzkit/governance/trust_audits/domain_views_fresh.py` — NEW; freshness validator
- `src/gzkit/cli/validate.py` — EXTEND with `--domain-cascade` and `--domain-views-fresh` scopes
- `src/gzkit/cli/check.py` — EXTEND `gz check` default pipeline to include both new scopes
- `tests/governance/test_domain_cascade_validator.py` — NEW
- `tests/governance/test_domain_views_fresh.py` — NEW
- `docs/user/manpages/validate.md` — EXTEND with new scope documentation

## Denied Paths

- `src/gzkit/governance/domain_models.py` — OBPI-01 / 02 (consume only)
- Other schemas — other OBPI scopes
- `src/gzkit/governance/legacy_mapping.py` — OBPI-07 (this OBPI calls into legacy-mapping resolution; does not author it)
- `src/gzkit/governance/cascade_import_check.py` — OBPI-11
- `src/gzkit/cli/domain.py` — OBPI-03
- `src/gzkit/ledger/**` — OBPI-05 (validator may call emit-helpers; not author event types)
- `.gzkit/skills/**` — OBPI-08 / 09 / 10
- Runtime dependencies

## Requirements (FAIL-CLOSED)

1. **REQUIREMENT (`--domain-cascade` scope — BC resolution).** Every non-pool ADR / GHI declaring `bounded_context: <slug>` MUST resolve `<slug>` to either (a) a PRD § 2.2 entry OR (b) an entry in `docs/design/domain/legacy-adr-bc-mapping.yaml`. Unresolved = exit 3 with `Resolve:` line naming the PRD § 2.2 or legacy-mapping path.
2. **REQUIREMENT (`--domain-cascade` scope — glossary marker resolution).** Every backticked token matching `gz-glossary-<term>` in ADR / GHI / OBPI prose MUST resolve to a PRD § 2.1 entry whose slugified term matches `<term>`. Unresolved = exit 3 with `Resolve:` line. Tokens matching registered skill names (`gz-design`, `ghi-author`, etc.) are skipped per the validator rule.
3. **REQUIREMENT (`--domain-cascade` scope — context-map presence).** Every ADR declaring `crosses_contexts: [a, b]` MUST have a corresponding PRD § 2.3 context-map entry covering the `(a, b)` or `(b, a)` pair. Missing entry = exit 3 with `Resolve:` line.
4. **REQUIREMENT (`--domain-cascade` scope — DM resolution).** Every ADR declaring `domain_model: DM-<slug>` MUST have a corresponding file at `docs/design/domain/DM-<slug>.md`. Missing file = exit 3 with `Resolve:` line.
5. **REQUIREMENT (`--domain-cascade` scope — inbound/outbound contract symmetry).** Every DM `## Inbound Contracts` entry pointing at `other_bc: X` MUST have a corresponding `X`'s DM `## Outbound Contracts` entry pointing back. Asymmetry = exit 3 with `Resolve:` line. (Skipped if the counterparty BC has no DM yet.)
6. **REQUIREMENT (`--domain-views-fresh` scope).** Compare on-disk `docs/design/domain/{glossary,bounded-contexts,context-map}.md` content against what `gz domain regenerate --check` would produce. Drift = exit 3 with `Resolve:` line naming `gz domain regenerate` as the recovery command. Parallels GHI #322 `--adr-status-fresh` pattern.
7. **REQUIREMENT (`gz check` wiring).** Both new scopes added to `gz check` default pipeline. Failure of either fails the overall check.
8. **REQUIREMENT (Resolve: line discipline — binding).** Every failure emitted by either validator MUST carry a `Resolve:` line naming the path to fix. No bare error messages. This is the 2am-operator affordance commitment from parent ADR § Decision.
9. **REQUIREMENT (`--accept-undefined-term` flag).** `gz validate --domain-cascade --accept-undefined-term <term> --accept-reason <REASON>` bypasses fail-closed on the named undefined glossary term and emits `cascade_debt_acknowledged` event via OBPI-05 emitter. Multiple `--accept-undefined-term` flags allowed.
10. **REQUIREMENT (`--skip-legacy` flag).** `gz validate --domain-cascade --skip-legacy` skips legacy-mapping fallback resolution; only frontmatter `bounded_context` is honored. Emergency triage path when legacy YAML is unparseable.

> STOP-on-BLOCKERS: if OBPI-04 (frontmatter schemas) or OBPI-07 (legacy mapping) are not landed, halt — the validator has nothing to resolve against.

## Discovery Checklist

**Parent ADR:**

- [ ] Parent ADR § Decision item #6 quoted
- [ ] Parent ADR § Intent
- [ ] Parent ADR file

**Governance:**

- [ ] `AGENTS.md` § Behavior Rules
- [ ] `.gzkit/rules/governance-core.md` § Operator-doc verb resolution (precedent for cascade-resolution pattern)
- [ ] `docs/governance/state-doctrine.md` — Layer-3 freshness
- [ ] `docs/governance/trust-doctrine.md` — T1/T2/T3 invariants

**Context:**

- [ ] OBPI-04 (frontmatter schemas) landed
- [ ] OBPI-07 (legacy mapping) landed (or in-flight; this OBPI's tests may stub the legacy-mapping resolver)
- [ ] OBPI-03 (`gz domain regenerate`) landed
- [ ] Existing validator scopes in `src/gzkit/governance/trust_audits/` (e.g., `adr_status_fresh.py`, `advisory_scorecard.py`)

**Prerequisites:**

- [ ] OBPI-04 landed (cascade frontmatter keys schema-validated)
- [ ] OBPI-03 landed (`gz domain regenerate` available for freshness comparison)
- [ ] PRD § 2.2 has at least one entry (test fixture acceptable)

**Existing Code:**

- [ ] `src/gzkit/governance/trust_audits/adr_status_fresh.py` — Layer-3 freshness precedent
- [ ] `src/gzkit/cli/validate.py` scope-dispatch pattern

## Quality Gates

### Gate 1: ADR

- [ ] Parent ADR checklist item #6 quoted
- [ ] Intent recorded

### Gate 2: TDD

- [ ] `--domain-cascade`: BC resolution — happy path + unresolved BC = exit 3 with Resolve: line
- [ ] `--domain-cascade`: glossary marker resolution — happy path + unresolved term = exit 3
- [ ] `--domain-cascade`: skill-name token skipped (false-negative test)
- [ ] `--domain-cascade`: context-map presence — happy path + missing entry = exit 3
- [ ] `--domain-cascade`: DM resolution — happy path + missing DM = exit 3
- [ ] `--domain-cascade`: inbound/outbound symmetry — happy path + asymmetric = exit 3
- [ ] `--domain-views-fresh`: drift detected = exit 3; no drift = exit 0
- [ ] `--accept-undefined-term`: bypass works; `cascade_debt_acknowledged` event emitted
- [ ] `--skip-legacy`: legacy fallback skipped
- [ ] `gz check` invokes both new scopes
- [ ] Every failure carries `Resolve:` line (regex-asserted)
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint / typecheck clean

### Gate 3: Docs (Heavy only)

- [ ] mkdocs build --strict clean
- [ ] `gz-validate.md` manpage updated with new scopes

### Gate 4: BDD (Heavy only)

- [ ] At least one BDD scenario: operator creates ADR with unresolved BC → `gz check` fails → operator adds BC to PRD § 2.2 → `gz check` passes

### Gate 5: Human (Heavy + Foundation)

- [ ] Attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

uv run gz validate --domain-cascade
uv run gz validate --domain-views-fresh
uv run gz check  # both scopes invoked
```

## Demo

```bash
# Try cascade validator with an intentionally-broken artifact
echo "---
id: ADR-DEMO
bounded_context: nonexistent-bc
---
# Demo" > /tmp/demo-adr.md
uv run gz validate --domain-cascade --target /tmp/demo-adr.md || echo "exit 3 (expected); Resolve: line printed"

# Freshness check
uv run gz validate --domain-views-fresh

# Bypass with debt acknowledgment
uv run gz validate --domain-cascade --accept-undefined-term frob --accept-reason "hotfix-debt"
```

## Acceptance Criteria

- [ ] REQ-0.0.43-06-01: Given ADR with `bounded_context: foo` and no PRD entry / legacy mapping for `foo`, when `gz validate --domain-cascade`, then exit 3 with `Resolve:` line naming PRD § 2.2 or legacy mapping path
- [ ] REQ-0.0.43-06-02: Given GHI body with `` `gz-glossary-frob` `` and no PRD § 2.1 entry for `frob`, when validator runs, then exit 3 with `Resolve:` line
- [ ] REQ-0.0.43-06-03: Given GHI body with `` `gz-design` `` (registered skill), when validator runs, then no glossary-resolution failure (skill-name skip works)
- [ ] REQ-0.0.43-06-04: Given ADR with `crosses_contexts: [a, b]` and no PRD § 2.3 entry pairing them, then exit 3
- [ ] REQ-0.0.43-06-05: Given ADR with `domain_model: DM-foo` and no `docs/design/domain/DM-foo.md`, then exit 3
- [ ] REQ-0.0.43-06-06: Given DM-a with `## Inbound Contracts` from BC `b`, and DM-b without symmetric `## Outbound Contracts`, then exit 3
- [ ] REQ-0.0.43-06-07: Given `docs/design/domain/glossary.md` content differs from what `gz domain regenerate --check` would produce, when `gz validate --domain-views-fresh`, then exit 3 with `Resolve: run gz domain regenerate`
- [ ] REQ-0.0.43-06-08: Given `gz check` invoked, when domain-cascade or domain-views-fresh would fail standalone, then `gz check` also fails
- [ ] REQ-0.0.43-06-09: Given every failure emitted by either validator, when inspected, then a `Resolve:` line is present (regex-asserted)
- [ ] REQ-0.0.43-06-10: Given `gz validate --domain-cascade --accept-undefined-term frob --accept-reason "hotfix"`, when invoked on a body with `gz-glossary-frob`, then exit 0 and `cascade_debt_acknowledged` event emitted to ledger

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** RGR followed
- [ ] **Code Quality:** Clean
- [ ] **Gate 3 (Docs):** mkdocs + manpage clean
- [ ] **Gate 4 (BDD):** Scenarios pass
- [ ] **Gate 5 (Human):** Attestation recorded
- [ ] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [ ] Intent recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/typecheck output here
```

### Gate 3 (Docs)

```text
# Paste mkdocs + manpage output here
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
