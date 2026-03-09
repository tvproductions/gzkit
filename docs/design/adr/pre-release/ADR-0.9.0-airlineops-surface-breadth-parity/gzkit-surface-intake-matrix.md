# ADR-0.9.0 `.gzkit/**` Surface Intake Matrix

## Metadata

- Date: 2026-03-09
- Canonical source: `../airlineops/.gzkit/`
- Extraction target: `.gzkit/`
- Rule: `GovZero = AirlineOps - product capabilities`
- Rubric: `docs/governance/parity-intake-rubric.md`
- OBPI: `OBPI-0.9.0-03-gzkit-breadth-parity-intake-tranche-plan`

## Decisions

| Item | Canonical Path | Decision | Severity | Rationale |
| --- | --- | --- | --- | --- |
| A | `governance/ontology.json` | Import with Compatibility (process-plane only) / Exclude (product-plane) | P2 | Process-plane doctrines (D-FLAG-DEFECTS, D-GATE-ATTESTATION, D-OBPI-DISCIPLINE) are GovZero governance primitives portable to any governed repo. Product-plane doctrines (D-CONFIG-FIRST, D-SUBSYSTEM-ISOLATION, D-STDLIB-FIRST, D-DB-ISOLATION, D-CROSS-PLATFORM, D-SQL-HYGIENE, D-NO-SECRETS) reference `src/airlineops/` paths and AirlineOps-specific subsystems — exclude. |
| B | `governance/ontology.schema.json` | Import Now | P2 | Pure GovZero tooling schema with no product references. Enables future ontology validation. Verbatim import. |
| C | `lessons/` (with `.gitkeep`) | Import Now | P3 | Empty governance scaffolding. Matches existing `insights/` pattern already at parity. |
| D | `locks/obpi/` | Defer (Tracked) | P3 | Lock acquisition/release runtime absent in gzkit. No concurrent agent sessions requiring OBPI locks. Track to future post-1.0 ADR. |
| E | `README.md` | Import with Compatibility | P3 | Canonical README references AirlineOps-specific ADR paths (`ADR-0.0.25`) and directory structure (`lessons/` subdirectory not yet present). Create gzkit-specific variant reflecting actual structure. |

## Ontology Doctrine Classification

Process-plane doctrines (portable to gzkit):

| Doctrine ID | Title | Category | Import? |
| --- | --- | --- | --- |
| D-FLAG-DEFECTS | Flag Defects Never Excuse | process | Yes — governance discipline |
| D-GATE-ATTESTATION | Human Gate Attestation | process | Yes — attestation boundary |
| D-OBPI-DISCIPLINE | One Brief Per Item | process | Yes — OBPI structure |

Product-plane doctrines (AirlineOps-specific, exclude):

| Doctrine ID | Title | Category | Why Exclude |
| --- | --- | --- | --- |
| D-CONFIG-FIRST | Config-First | configuration | References `src/airlineops/` config loader, registry.json |
| D-SUBSYSTEM-ISOLATION | Subsystem Isolation | architecture | References warehouse/librarian boundary |
| D-STDLIB-FIRST | Stdlib-First | dependencies | AirlineOps dependency policy |
| D-DB-ISOLATION | DB Isolation | testing | References TempDBMixin, warehouse DB paths |
| D-CROSS-PLATFORM | Cross-Platform | portability | AirlineOps cross-platform instructions |
| D-SQL-HYGIENE | SQL Hygiene | data-access | AirlineOps SQL patterns |
| D-NO-SECRETS | No Secrets in Code | security | AirlineOps security scope |

Policies, rules, and actions follow doctrine plane — process-plane policies/rules/actions
are imported with their parent doctrines; product-plane items are excluded.

### Process-Plane Policies (import)

| Policy ID | Parent Doctrine | Scope |
| --- | --- | --- |
| P-ATTEST-OBPI-CEREMONY | D-GATE-ATTESTATION | `docs/design/adr/**/*.md` |

### Process-Plane Rules (import)

| Rule ID | Parent Policy | Severity |
| --- | --- | --- |
| R-ATTEST-OBPI-001 | P-ATTEST-OBPI-CEREMONY | blocking |

### Process-Plane Actions (import)

| Action ID | Title | Authorization |
| --- | --- | --- |
| A-READ-FILES | Read any repository file | autonomous |
| A-RUN-UNIT-TESTS | Run unit tests | autonomous |
| A-RUN-LINT | Run lint and format | autonomous |
| A-EDIT-IN-SCOPE | Create or edit files within brief scope | autonomous |
| A-SEARCH-CODEBASE | Search codebase | autonomous |
| A-GIT-PUSH | Push to remote repository | human-gated |
| A-GIT-COMMIT | Create git commits | human-gated |
| A-UV-ADD | Add new dependencies | human-gated |
| A-FILE-DELETE | Delete files | human-gated |
| A-MARK-OBPI-COMPLETED | Mark OBPI as Completed | human-gated |
| A-RUN-FULL-SUITE | Run full test suite or BDD | human-gated |
| A-GIT-NO-VERIFY | Bypass pre-commit hooks | prohibited |

Note: Actions are plane-agnostic in the schema (no `plane` field). All actions are imported
since they govern agent behavior universally. Product-scoped rules referenced by
`rules_enforced` links (e.g., R-TEST-DB-001 in A-RUN-UNIT-TESTS) will be adapted to
gzkit equivalents when product-plane ontology is reconsidered.

## gzkit-Native Items (no parity action)

| Path | Purpose | Status |
| --- | --- | --- |
| `manifest.json` | Governance manifest (skills, paths) | gzkit-native, no canonical equivalent |
| `ledger.jsonl` | Governance event ledger | gzkit-native, no canonical equivalent |
| `skills/` (45 dirs) | Skill definitions | gzkit-native, no canonical equivalent |
| `insights/agent-insights.jsonl` | Agent insight ledger | Already at parity |

## Evidence Commands

```bash
# Canonical structure
cd ../airlineops && ls -Ra .gzkit/ | head -30

# gzkit structure
ls -Ra .gzkit/ | head -30

# Ontology doctrine planes
cd ../airlineops && python3 -c "
import json
with open('.gzkit/governance/ontology.json') as f:
    data = json.load(f)
for did, d in data['doctrines'].items():
    print(f\"{did}: plane={d['plane']}, category={d['category']}\")
"

# Verify no product paths in process-plane doctrines
cd ../airlineops && python3 -c "
import json
with open('.gzkit/governance/ontology.json') as f:
    data = json.load(f)
process = {k: v for k, v in data['doctrines'].items() if v['plane'] == 'process'}
for did, d in process.items():
    sources = [d['canonical_source']] + d.get('also_stated_in', [])
    airlineops_refs = [s for s in sources if 'airlineops' in s.lower()]
    print(f\"{did}: airlineops_refs={airlineops_refs or 'none'}\")
"
```

## OBPI-04 Tranche Plan (defined by this intake)

### Scope

Items A (process-plane only), B, C, E from the decisions table above.

### Steps

1. Create `.gzkit/governance/` directory
2. Import `ontology.schema.json` verbatim from canonical
3. Create process-plane-only `ontology.json` containing:
   - Doctrines: D-FLAG-DEFECTS, D-GATE-ATTESTATION, D-OBPI-DISCIPLINE
   - Policies: P-ATTEST-OBPI-CEREMONY (with gzkit-adapted scope)
   - Rules: R-ATTEST-OBPI-001 (with gzkit-adapted enforcement/traceability)
   - Actions: all (plane-agnostic, adapted `rules_enforced` references)
   - Paths adapted from `src/airlineops/` to `src/gzkit/` where applicable
4. Create `.gzkit/lessons/.gitkeep`
5. Create gzkit-specific `.gzkit/README.md` reflecting actual structure
6. Run `gz agent sync control-surfaces`

### Acceptance Criteria for OBPI-04

- [ ] `.gzkit/governance/ontology.schema.json` exists and matches canonical verbatim
- [ ] `.gzkit/governance/ontology.json` contains only process-plane doctrines
- [ ] `.gzkit/governance/ontology.json` contains no `src/airlineops/` references
- [ ] `.gzkit/lessons/.gitkeep` exists
- [ ] `.gzkit/README.md` reflects actual gzkit `.gzkit/` structure
- [ ] `gz agent sync control-surfaces` completes without error
- [ ] Quality gates pass (lint, format, typecheck, tests)

## Deferred Items

| Item | Path | Rationale | Follow-up |
| --- | --- | --- | --- |
| D | `locks/obpi/` | No lock acquisition/release runtime; no concurrent agent sessions in gzkit | Future post-1.0 ADR when multi-agent concurrency is needed |
| Product-plane ontology | 7 doctrines + their policies/rules | Reference AirlineOps-specific subsystems, paths, and tools | Permanent exclude unless gzkit develops equivalent product domain |
| Ontology runtime loader | `gz ontology validate` / `gz ontology check` | No runtime consumer exists in gzkit | Future ADR when ontology-driven enforcement is implemented |

## Tranche History

### Tranche 1 (OBPI-0.9.0-01): `.claude/hooks` — Import

See `claude-hooks-intake-matrix.md` § Tranche 1 Result.

### Tranche 2 (OBPI-0.9.0-02): `.claude/hooks` — Completion Validator

See `claude-hooks-intake-matrix.md` § Tranche 2 Result.

### Tranche 3 (OBPI-0.9.0-03): `.gzkit/**` — Intake and Plan

This document. Classifies 5 canonical deltas, defines OBPI-04 import tranche.
