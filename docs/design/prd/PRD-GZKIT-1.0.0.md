# Product Requirements Document: gzkit 1.0.0

## 1. Document Information

- Product/Feature Name: gzkit (GovZero Kit) 1.0.0
- Author(s): JB
- Date Created: 2026-01-13
- Last Updated: 2026-01-13
- Version: 0.2 (Draft)
- Constitution: [gzkit Charter](../../user/charter.md)
- Lane: Heavy (external CLI contract)

---

## 2. Overview

### Summary

gzkit is a Python CLI that implements the GovZero development covenant methodology. It provides spec-kit-inspired phase commands (constitute, specify, plan, implement, analyze) with Five Gates enforcement, enabling humans to maintain architectural authority over AI-assisted development.

### Problem Statement

AI-assisted development creates a drift problem: humans approve work they didn't verify, attest to artifacts they didn't read, and gradually become rubber stamps for agent-generated output. Existing tools either ignore governance entirely or bury it in ceremony that agents route around.

gzkit exists to keep the human at index zero—first in priority, final in authority.

### Goals & Objectives

- Provide a daily-driver CLI for managing development covenants
- Implement spec-kit phase model with GovZero Five Gates
- Support Lite (Gates 1-2) and Heavy (Gates 1-5) lanes
- Scaffold and validate governance artifacts (constitutions, briefs, ADRs, audits)
- Enforce human attestation as non-bypassable closeout
- Enable effective project/product design, execution, and ongoing governance

### Non-Goals

- AI/ML framework or model integration
- Automated attestation or approval
- Replacement for human judgment
- Multi-agent orchestration
- Full spec-kit feature parity (gzkit is GovZero-native, not a spec-kit clone)

---

## 3. Context & Background

### Business Context

gzkit is the extracted governance methodology from AirlineOps, intended as a standalone tool for any project adopting the GovZero discipline.

### Lineage

| Source | Contribution |
|--------|--------------|
| **Spec-kit** (GitHub) | Phase model: constitute → specify → plan → implement → analyze |
| **GovZero Charter** | Five Gates, Lane Doctrine, Attestation Terms |
| **Zero Doctrine** | Human as index zero, Q&A imperative, ceremony-as-debt |
| **BEADS** (Yegge) | JSONL ledger, dependency tracking, queryable state |
| **GSD** (glittercowboy) | STATE.md pattern, persistent context across sessions |
| **airlineops/opsdev** | Ledger append patterns, governance guards |

### Target Users

| Persona | Need |
|---------|------|
| **Architect** | Maintain design authority while leveraging AI assistance |
| **Student** | Learn governance-aware development methodology |
| **Team Lead** | Establish covenant discipline across a team |
| **Solo Developer** | Self-impose rigor on AI-assisted projects |

---

## 4. Scope

### In Scope (1.0.0)

**Phase Commands:**

- `gz init` — scaffold project structure, `.gzkit.json`, and ledger
- `gz prd` — create/manage PRD from template (Major intent carrier)
- `gz constitute` — create/validate constitution artifacts
- `gz specify <brief>` — create brief from template
- `gz plan <adr>` — create ADR linked to brief
- `gz implement` — verify gates (tests, docs, BDD)
- `gz analyze` — generate audit artifacts
- `gz attest` — record human attestation

**State & Inspection:**

- `gz state` — render current state from ledger (human-readable)
- `gz state --json` — dump current state (machine-readable)
- `gz state --blocked` — show blocked items and why
- `gz state --ready` — show items ready for work
- `gz status` — display gate status for current work
- `gz gates` — run gate checks and report results

**Ledger System:**

- `.gzkit/ledger.jsonl` — append-only event log
- Implicit writes from all `gz` commands
- Event schema versioning (`gzkit.ledger.v1`)
- Dependency tracking (parent, blocks, blocked_by)

**Claude Hooks Integration:**

- `.claude/settings.json` — hook configuration
- `.claude/hooks/` — hook scripts
- PostToolUse hooks for governance artifact edits
- PreToolUse hooks for constraint enforcement

**Configuration:**

- `.gzkit.json` configuration with Lite/Heavy mode
- Template customization
- Path configuration for artifacts

### Out of Scope (1.0.0)

- CI/CD pipeline integration (documented but not automated)
- GitHub Actions workflows
- Remote/cloud governance storage
- Multi-repo governance
- IDE plugins

---

## 5. User Stories & Use Cases

### User Stories

| ID | Story |
|----|-------|
| US-001 | As an architect, I want to initialize a project with governance structure, so that I have a covenant from day one. |
| US-002 | As an architect, I want to create a constitution, so that I have a north star to reference. |
| US-003 | As an architect, I want to create briefs from templates, so that work is scoped before implementation. |
| US-004 | As an architect, I want to create ADRs linked to briefs, so that design decisions trace to requirements. |
| US-005 | As an architect, I want to see gate status at a glance, so that I know what's blocking closeout. |
| US-006 | As an architect, I want to run gate checks, so that I can verify compliance before attestation. |
| US-007 | As an architect, I want to record attestation explicitly, so that my approval is non-repudiable. |
| US-008 | As an architect, I want to generate audit artifacts, so that governance is traceable. |

### Primary Use Case: Daily Driving

**Scenario**: Architect uses gzkit throughout a feature lifecycle.

```
gz init my-project                    # Day 0: scaffold
gz constitute                         # Day 0: establish north star
gz specify add-user-auth              # Day 1: scope the work
gz plan ADR-0.1.0 --brief add-user-auth   # Day 1: design decision
# ... implement feature ...
gz status                             # Day N: check progress
gz gates                              # Day N: verify compliance
gz attest                             # Day N: human closeout
gz analyze                            # Day N: generate audit
```

**Outcome**: Complete traceability from intent to attestation.

---

## 6. Functional Requirements

### FR-001: Project Initialization

`gz init [project-name]` SHALL:

- Create `.gzkit.json` configuration file with sensible defaults
- Create `.gzkit/ledger.jsonl` (empty ledger file)
- Create `.claude/settings.json` with hook configuration
- Create `.claude/hooks/` directory with ledger-writer script
- Create `docs/constitutions/` directory
- Create `docs/briefs/` directory
- Create `docs/adr/` directory
- Create `docs/audit/` directory
- Create `docs/prd/` directory
- Append `project_init` event to ledger
- Fail with clear error if structure already exists (no silent overwrite)

### FR-002: PRD Management

`gz prd [name]` SHALL:

- Create PRD from hardened template if not exists
- Validate PRD structure if exists
- Link PRD to constitution
- Append `prd_created` event to ledger
- Support `--template` flag for custom templates

### FR-003: Constitution Management

`gz constitute [name]` SHALL:

- Create constitution from template if not exists
- Validate constitution structure if exists
- Report validation errors with file:line references
- Append `constitution_created` event to ledger
- Support `--template` flag for custom templates

### FR-004: Brief Creation

`gz specify <brief-name>` SHALL:

- Create brief from template in configured briefs directory
- Insert constitution reference automatically
- Generate unique brief ID
- Append `brief_created` event to ledger with `parent` reference
- Fail if constitution does not exist

### FR-005: ADR Creation

`gz plan <adr-name>` SHALL:

- Create ADR from template in configured ADR directory
- Link to specified brief(s) via `--brief` flag
- Insert gate evidence placeholders
- Determine lane (Lite/Heavy) from scope declaration
- Append `adr_created` event to ledger with `parent` and `blocks` references
- Fail if referenced brief does not exist

### FR-006: Gate Verification

`gz implement` SHALL:

- Run Gate 2 (TDD): execute test suite, report coverage
- Run Gate 3 (Docs): validate markdown, check links (Heavy only)
- Run Gate 4 (BDD): execute acceptance scenarios (Heavy only)
- Append `gate_checked` events to ledger for each gate
- Report gate status with pass/fail and evidence references
- Exit non-zero if any required gate fails

`gz gates` SHALL:

- Run all applicable gates for current lane
- Display results in terminal
- Append `gate_checked` events to ledger
- Support `--gate <n>` to run specific gate

### FR-007: State Management

`gz state` SHALL:

- Parse `.gzkit/ledger.jsonl` and compute current state
- Display dependency graph of artifacts (PRD → Brief → ADR)
- Support `--json` for machine-readable output
- Support `--blocked` to show items with unresolved dependencies
- Support `--ready` to show items ready for work
- NOT write to ledger (read-only operation)

### FR-008: Status Display

`gz status` SHALL:

- Display current lane (Lite/Heavy)
- Display active ADR(s) and their gate status
- Display blocking issues with file:line references
- Support `--json` for machine-readable output

### FR-009: Attestation Recording

`gz attest` SHALL:

- Prompt for attestation term (Completed / Partial / Dropped)
- Validate required gates are passing (per lane)
- Record attestation with timestamp and identity in ADR
- Append `attested` event to ledger with term and identity
- Refuse to attest if gates failing (without `--force`)
- Support `--reason` for Partial/Dropped rationale

### FR-010: Audit Generation

`gz analyze` SHALL:

- Generate audit artifact from ADR and gate evidence
- Include attestation record
- Include gate results with evidence links
- Append `audit_generated` event to ledger
- Write to configured audit directory

### FR-011: Ledger System

The ledger system SHALL:

- Store events in `.gzkit/ledger.jsonl` as append-only JSONL
- Use schema versioning (`gzkit.ledger.v1`)
- Include `ts` (ISO 8601 UTC), `event`, `id`, and event-specific fields
- Support `parent` field for dependency tracking
- Support `blocks` and `blocked_by` fields for work coordination
- Be implicitly written by all `gz` commands (no explicit ledger calls)
- Be queryable via `gz state` command

**Event types:**

| Event | Fields | Trigger |
|-------|--------|---------|
| `project_init` | `id`, `ts` | `gz init` |
| `prd_created` | `id`, `parent`, `ts` | `gz prd` |
| `constitution_created` | `id`, `ts` | `gz constitute` |
| `brief_created` | `id`, `parent`, `ts` | `gz specify` |
| `adr_created` | `id`, `parent`, `blocks`, `ts` | `gz plan` |
| `gate_checked` | `adr`, `gate`, `status`, `evidence`, `ts` | `gz implement`, `gz gates` |
| `attested` | `adr`, `term`, `by`, `ts` | `gz attest` |
| `audit_generated` | `adr`, `path`, `ts` | `gz analyze` |
| `artifact_edited` | `path`, `session`, `ts` | Claude hook (PostToolUse) |

### FR-012: Claude Hooks Integration

`gz init` SHALL scaffold Claude hooks:

- `.claude/settings.json` with PostToolUse hook configuration
- `.claude/hooks/ledger-writer.py` script

The ledger-writer hook SHALL:

- Fire on PostToolUse for Edit and Write tools
- Match governance artifact patterns:
  - `docs/adr/**/*.md`
  - `docs/briefs/**/*.md`
  - `docs/prd/**/*.md`
  - `docs/constitutions/**/*.md`
  - `docs/audit/**/*.md`
- Append `artifact_edited` event to ledger
- Include session ID for traceability
- Exit 0 on success (non-blocking)

PreToolUse hooks MAY:

- Block edits to closed/attested ADRs
- Warn on edits to constitution without explicit flag
- Enforce constraint violations

---

## 7. Non-Functional Requirements

### Performance

- All commands SHALL complete in <5 seconds on standard hardware
- No network calls required for core functionality

### Determinism

- Same inputs SHALL produce same outputs
- Template rendering SHALL be reproducible
- Only attestation timestamps are non-deterministic (by design)

### Explainability

- Every gate failure SHALL trace to specific file:line evidence
- Every attestation SHALL record human identity and timestamp
- Every audit SHALL link to source artifacts

### Accessibility

- CLI SHALL support `--no-color` for accessibility
- CLI SHALL support `--quiet` for scripting
- All output SHALL be screen-reader compatible (no ASCII art)

---

## 8. Dependencies

### Runtime

| Dependency | Purpose |
|------------|---------|
| Python 3.13.x | Runtime |
| Click | CLI framework |
| Pydantic | Configuration validation |
| json (stdlib) | JSON parsing |

### Development

| Dependency | Purpose |
|------------|---------|
| uv | Package management |
| ruff | Linting and formatting |
| ty | Type checking |
| unittest | Testing |

### External

- None (no network dependencies for core functionality)

---

## 9. Risks & Assumptions

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Scope creep | Delays 1.0.0 | Strict In Scope enforcement; defer to 2.0.0 |
| Template complexity | User confusion | Start minimal; iterate based on feedback |
| Adoption friction | Low usage | One-screen docs; graduate course validation |
| Over-ceremony | User rejection | Lite lane as default; Heavy only when needed |

### Assumptions

- Users have Python 3.13.x and uv installed
- Users accept Markdown as primary artifact format
- Users understand (or will learn) basic governance concepts
- Terminal/CLI interaction is acceptable (no GUI required)

---

## 10. Acceptance Criteria

### AC-001: Initialization

- [ ] `gz init test-project` creates all required directories and `.gzkit.json`
- [ ] `gz init` in existing gzkit project fails with clear error
- [ ] Generated `.gzkit.json` is valid and parseable

### AC-002: Constitution

- [ ] `gz constitute` creates constitution from template
- [ ] `gz constitute --validate` reports errors for malformed constitution
- [ ] Constitution contains required sections (per template)

### AC-003: Brief Creation

- [ ] `gz specify my-feature` creates brief in configured directory
- [ ] Brief contains constitution reference
- [ ] Brief has unique ID
- [ ] Command fails if no constitution exists

### AC-004: ADR Creation

- [ ] `gz plan ADR-0.1.0 --brief my-feature` creates ADR
- [ ] ADR contains brief linkage
- [ ] ADR contains gate evidence placeholders
- [ ] ADR declares lane (Lite/Heavy)
- [ ] Command fails if referenced brief does not exist

### AC-005: Gate Verification

- [ ] `gz implement` runs applicable gates
- [ ] Gate failures include file:line evidence
- [ ] Exit code reflects gate status
- [ ] `gz gates --gate 2` runs only Gate 2

### AC-006: Status Display

- [ ] `gz status` shows lane and gate status
- [ ] `gz status --json` outputs valid JSON
- [ ] Blocking issues show file:line references

### AC-007: Attestation

- [ ] `gz attest` prompts for term
- [ ] Attestation records timestamp and identity
- [ ] `gz attest` fails if gates not passing (without `--force`)
- [ ] `gz attest --force` overrides with warning

### AC-008: Audit Generation

- [ ] `gz analyze` generates audit artifact
- [ ] Audit includes attestation record
- [ ] Audit includes gate evidence links

### AC-009: PRD Management

- [ ] `gz prd PRD-GZKIT-1.0.0` creates PRD from hardened template
- [ ] PRD contains all hardened sections (invariants, gate mapping, Q&A, attestation)
- [ ] `prd_created` event appended to ledger
- [ ] PRD links to constitution

### AC-010: State Management

- [ ] `gz state` parses ledger and displays current state
- [ ] `gz state --json` outputs valid JSON
- [ ] `gz state --blocked` shows items with unresolved dependencies
- [ ] `gz state --ready` shows items ready for work
- [ ] State display shows dependency graph (PRD → Brief → ADR)

### AC-011: Ledger System

- [ ] `.gzkit/ledger.jsonl` created by `gz init`
- [ ] All `gz` commands append events to ledger
- [ ] Events include `schema`, `event`, `ts` fields
- [ ] Ledger is append-only (no modifications)
- [ ] Events are valid JSONL (one JSON object per line)

### AC-012: Claude Hooks

- [ ] `gz init` creates `.claude/settings.json` with hook config
- [ ] `gz init` creates `.claude/hooks/ledger-writer.py`
- [ ] Hook fires on Edit/Write to governance artifacts
- [ ] Hook appends `artifact_edited` event to ledger
- [ ] Hook includes session ID in event

---

## 11. Success Metrics

| Metric | Target |
|--------|--------|
| Commands functional | 11/11 (init, prd, constitute, specify, plan, implement, gates, state, status, attest, analyze) |
| Ledger operational | All commands append events |
| Hooks operational | PostToolUse fires on governance artifact edits |
| Test coverage | ≥40% |
| Docs build | Passes |
| Type check | Passes (ty strict) |
| Demo workflow | Completable by student unassisted |

---

## 12. Rollout & Release Plan

### Phase 1: MVP (0.1.0)

Target: Graduate course demo

- `gz init` with ledger and hooks scaffolding
- `gz prd`, `gz constitute`, `gz specify`, `gz plan`
- `gz state`, `gz status`, `gz attest`
- Minimal templates (PRD, constitution, brief, ADR)
- Ledger system (append-only JSONL)
- Claude hooks (PostToolUse ledger-writer)
- One-screen docs per command

### Phase 2: Gates (0.2.0)

- `gz implement` with Gate 2 (TDD)
- `gz gates` command
- Gate evidence linking
- `gate_checked` events in ledger

### Phase 3: Heavy Lane (0.3.0)

- Gate 3 (Docs) verification
- Gate 4 (BDD) verification
- Lane detection and enforcement
- PreToolUse hooks for constraint enforcement

### Phase 4: Audit (0.4.0)

- `gz analyze` with audit generation
- Audit templates
- Evidence aggregation from ledger
- `audit_generated` events

### Phase 5: Release (1.0.0)

- All 11 commands functional
- Templates hardened
- Ledger fully operational
- Hooks fully operational
- Documentation complete
- Graduate course validated

---

## 13. Open Questions

- [ ] Should `gz status` read from git state or explicit markers?
- [ ] What's the minimum viable constitution template?
- [ ] Should attestation support GPG signing?
- [ ] Should `gz implement` run tests directly or defer to configured command?
- [ ] How should multi-ADR projects display status?

---

## 14. References

| Document | Purpose |
|----------|---------|
| [gzkit Charter](../../user/charter.md) | Constitution |
| [RFC-GZKIT-FOUNDATION](../../user/sources/RFC-GZKIT-FOUNDATION-airlineops.md) | Origin RFC |
| [GovZero Release Doctrine](../../user/sources/govzero-release-doctrine-airlineops.md) | SemVer governance |
| [GitHub Spec-kit](https://github.com/github/spec-kit) | Phase model lineage |
| [BEADS](https://github.com/steveyegge/beads) | Ledger/state tracking lineage |
| [GSD](https://github.com/glittercowboy/get-shit-done) | Context engineering lineage |
| [Claude Code Hooks](https://docs.anthropic.com/en/docs/claude-code/hooks) | Hook integration reference |

---

## 15. Invariants

These constraints are non-negotiable. Agents MUST reason against them.

| ID | Invariant |
|----|-----------|
| INV-001 | Human attestation CANNOT be automated or bypassed |
| INV-002 | Gate 5 REQUIRES explicit human action |
| INV-003 | Briefs MUST reference constitution |
| INV-004 | ADRs MUST link to briefs |
| INV-005 | Attestation terms MUST be canonical (Completed / Partial / Dropped) |
| INV-006 | All commands MUST be deterministic (same input → same output, except timestamps) |
| INV-007 | Lite lane MUST enforce Gates 1-2; Heavy lane MUST enforce Gates 1-5 |
| INV-008 | Gate failures MUST include file:line evidence |
| INV-009 | Ledger MUST be append-only; existing events CANNOT be modified |
| INV-010 | All `gz` commands MUST append events to ledger implicitly |
| INV-011 | Ledger events MUST include ISO 8601 UTC timestamp |
| INV-012 | Claude hooks MUST NOT block on ledger write failure (best-effort) |
| INV-013 | PRDs MUST be bound to Major versions |
| INV-014 | ADRs MUST link to parent PRD or Brief |

---

## 16. Gate Mapping

This PRD is verified through the following gates:

| Gate | Evidence |
|------|----------|
| Gate 1 (ADR) | This PRD + downstream ADRs |
| Gate 2 (TDD) | `uv run -m unittest discover tests` passes; ≥40% coverage |
| Gate 3 (Docs) | `uv run mkdocs build` passes; command docs present |
| Gate 4 (BDD) | CLI contract scenarios pass (Heavy lane) |
| Gate 5 (Human) | Attestation block below completed by human |

---

## 17. Q&A Record

Q&A that shaped this PRD (per Human Discipline):

| Date | Question | Answer | Questioner |
|------|----------|--------|------------|
| 2026-01-13 | Does 0.1.0 need a PRD or is RFC sufficient? | PRD required; RFC is source material | Agent |
| 2026-01-13 | What's minimum viable for grad course demo? | 6 commands: init, constitute, specify, plan, status, attest | Human |
| 2026-01-13 | Is Charter the constitution? | Yes; Charter = Constitution, North Star = Spec/PRD | Human |
| 2026-01-13 | Should PRD be Major-bound? | Yes; PRD-GZKIT-1.0.0 defines the Major target | Human |
| 2026-01-13 | How do PRDs work across Majors? | Expand TOWARDS next Major; shipped PRD becomes baseline | Human |
| 2026-01-13 | Should gzkit have a `gz prd` command? | Yes; PRD is part of covenant, should scaffold like other artifacts | Human |
| 2026-01-13 | Should gzkit track state like BEADS/GSD? | Yes; JSONL ledger with `gz state` to query | Human |
| 2026-01-13 | How to prevent agent forgetting ledger? | Implicit writes from all `gz` commands + Claude hooks | Agent |
| 2026-01-13 | Should we use SQLite cache like BEADS? | Uncertain; JSONL sufficient for MVP, SQLite optional | Human |
| 2026-01-13 | How to track ADR/OBPI/GHI closure? | Claude hooks (PostToolUse) append to ledger on artifact edits | Human |

---

## 18. Attestation Block

**Status**: Draft

| Field | Value |
|-------|-------|
| Attestation Term | — |
| Attested By | — |
| Attested At | — |
| Evidence | — |

Human attestation required before promotion to Accepted.
