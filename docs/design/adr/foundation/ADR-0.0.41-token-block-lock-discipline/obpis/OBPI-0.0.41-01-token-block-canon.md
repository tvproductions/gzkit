---
id: OBPI-0.0.41-01-token-block-canon
parent: ADR-0.0.41-token-block-lock-discipline
item: 1
lane: Lite
status: Draft
---

# OBPI-0.0.41-01-token-block-canon: Token Block Canon

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.41-token-block-lock-discipline/ADR-0.0.41-token-block-lock-discipline.md`
- **Checklist Item:** #1 - "OBPI-0.0.41-01: Token-block doctrine canon — author `.gzkit/rules/token-block-discipline.md` and `docs/governance/token-block-doctrine.md` (railway-historical reference). Specify the binding sub-invariants the structural enforcement alone does not close: (a) auditable `--abandon` reason categories (rejecting free-text-only reasons; categories include `network_loss`, `external_blocker`, `wrong_obpi_claimed`, `tool_failure`, with extension protocol); (b) minimum-information requirements for the register entry (last lock-event timestamp, last commit SHA, named decisions, branch state) so structurally-valid-but-semantically-empty handoffs are also rejected; (c) lock-takeover / reaping register-entry rule (the railway-analogue lost-token procedure: a reaping by agent-B emits an `abandoned_by_reaper` register entry recording agent-A's last-known state); (d) **time-bound discipline (TTL canon and reaping cadence): default TTL value with rationale, escalation policy (warn-then-reap windows), who-may-reap (any agent at next session-start; explicit operator override), and the attestation requirement that the reaping agent MUST produce the `abandoned_by_reaper` register entry as a precondition of the reap — mirroring the rule for ordinary release, so reaping is not a doctrine-bypass**; (e) cross-link from AGENTS.md § Behavior Rules and `docs/governance/state-doctrine.md`. Establishes vocabulary (token, register entry, traversal, abandonment, reaping) before any code change."

**Status:** Draft

## Objective

Author the canonical rule file `.gzkit/rules/token-block-discipline.md` that specifies the binding sub-invariants of the token-block discipline (auditable abandon categories, register-entry minimum-information rules, reaping register-entry protocol, and TTL canon), establishing the governance vocabulary before structural enforcement lands.

## Lane

**Lite** - This OBPI remains internal to the promoted ADR implementation scope.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `.gzkit/rules/token-block-discipline.md` — **PRIMARY:** the rule file being authored in this OBPI; contains binding sub-invariants
- `docs/governance/token-block-doctrine.md` — already exists; read-only reference to railway-historical context and mapping
- `docs/design/adr/foundation/ADR-0.0.41-token-block-lock-discipline/ADR-0.0.41-token-block-lock-discipline.md` — parent ADR § Decision, Checklist item #1, and Consequences sections

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `.gzkit/rules/token-block-discipline.md` MUST exist and specify the five binding sub-invariants: (a) `--abandon` reason category enum (with extension protocol); (b) register-entry minimum-information rules; (c) reaping register-entry protocol (`abandoned_by_reaper` format); (d) TTL canon (default value, escalation policy, who-may-reap, reaping-attestation rule); (e) vocabulary cross-links to AGENTS.md and state-doctrine.md.
2. REQUIREMENT: The rule file MUST follow `.gzkit/rules/` structure (YAML frontmatter, rule-version body comment, visible version block quote) per `.gzkit/rules/skill-surface-sync.md`.
3. REQUIREMENT: `--abandon` reason categories MUST have an extension protocol. The base enum MUST include: `network_loss`, `external_blocker`, `wrong_obpi_claimed`, `tool_failure`. Future additions require ADR-backed rationale.
<!-- gz-validate-skip: brief-cross-references -->
4. REQUIREMENT: Register-entry minimum-information rule MUST specify: last lock-event timestamp, last commit SHA, named decision context, branch state. Entries lacking these fields MUST fail OBPI-0.0.41-04 validator.
5. REQUIREMENT: TTL canon MUST specify: default TTL value with rationale; warn-then-reap escalation windows; agent-authorization rule (any agent at next session-start; explicit operator override); attestation requirement (reaping agent MUST produce `abandoned_by_reaper` register entry before reap succeeds, mirroring ordinary release rule).
6. REQUIREMENT: Vocabulary section MUST define: token (= OBPI lock), issue (= obpi_lock_claimed event), register entry (= handoff document), traversal (= OBPI session), abandonment (= degenerate handoff), reaping (= lock-takeover by different agent).

> STOP-on-BLOCKERS: if `.gzkit/rules/` directory structure is unfamiliar, read `.gzkit/rules/skill-surface-sync.md` (body-level version marking for rules) and an existing rule file (e.g., `.gzkit/rules/models.md`) before authoring.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item** — Quote: "Couple lock-release to a handoff register entry. The binding invariant: A token cannot be surrendered without a register entry." Mapped to this OBPI: establishes doctrine vocabulary before structural code changes land.
- [ ] Parent ADR § Intent (lines 23-47) — why the lock primitive needed audit-coupling, the railway antecedent, and the 5/5/0 empirical failure that surfaced the gap.
- [ ] Parent ADR § Consequences › Negative (lines 104-121) — the backwards-incompatible flip and staging strategy (OBPI-02 warning-only, OBPI-03 fail-closed).
- [ ] Parent ADR § Checklist item #1 — all sub-clauses (a) through (e) and the vocabulary section.

> **STOP:** If you cannot articulate the five binding sub-invariants and the railway analogy grounding, STOP and re-read the parent ADR § Intent.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/skill-surface-sync.md` (lines 1-40) — rule file structure, body-level `<!-- rule-version: X.Y.Z -->` marker, and visible version block quote requirement.
- [ ] `.gzkit/rules/models.md` — existing rule file showing canonical structure and examples.
- [ ] `docs/governance/token-block-doctrine.md` — the railway-historical mapping and rationale (already authored; read-only reference).

**Prerequisites (check existence, STOP if missing):**

- [ ] `.gzkit/rules/` directory exists (confirmed by reading an existing rule file).
- [ ] Parent ADR file exists: `docs/design/adr/foundation/ADR-0.0.41-token-block-lock-discipline/ADR-0.0.41-token-block-lock-discipline.md`
- [ ] `docs/governance/token-block-doctrine.md` exists and contains railway mapping and acknowledgement section.

**Existing Code (understand current state):**

- [ ] At least one existing `.gzkit/rules/` file (e.g., `models.md`, `cli.md`) examined for structure, formatting, and version-marker pattern.
- [ ] `.claude/rules/` mirroring mechanism understood (via `skill-surface-sync.md` § Surface layout).

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
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. -->

```bash
# File existence: primary artifact
test -f .gzkit/rules/token-block-discipline.md && echo "✓ Rule file exists"

# Structure validation
test -f .gzkit/rules/token-block-discipline.md && grep -q "^---$" .gzkit/rules/token-block-discipline.md && echo "✓ YAML frontmatter present"
test -f .gzkit/rules/token-block-discipline.md && grep -q "<!-- rule-version:" .gzkit/rules/token-block-discipline.md && echo "✓ Body-level rule-version comment present"

# Content validation: five binding sub-invariants
test -f .gzkit/rules/token-block-discipline.md && grep -qE "(--abandon|reason.*category|network_loss|external_blocker)" .gzkit/rules/token-block-discipline.md && echo "✓ --abandon categories documented"
test -f .gzkit/rules/token-block-discipline.md && grep -qE "(minimum-information|timestamp|commit SHA|branch state)" .gzkit/rules/token-block-discipline.md && echo "✓ Register-entry min-info rules documented"
test -f .gzkit/rules/token-block-discipline.md && grep -qE "(abandoned_by_reaper|reaping)" .gzkit/rules/token-block-discipline.md && echo "✓ Reaping protocol documented"
test -f .gzkit/rules/token-block-discipline.md && grep -qE "(TTL|time-bound|default.*value)" .gzkit/rules/token-block-discipline.md && echo "✓ TTL canon documented"
test -f .gzkit/rules/token-block-discipline.md && grep -qE "(vocabulary|token|register entry|traversal)" .gzkit/rules/token-block-discipline.md && echo "✓ Vocabulary section present"

# Cross-link validation
test -f .gzkit/rules/token-block-discipline.md && grep -q "AGENTS.md" .gzkit/rules/token-block-discipline.md && echo "✓ AGENTS.md cross-link present"
test -f .gzkit/rules/token-block-discipline.md && grep -q "state-doctrine.md" .gzkit/rules/token-block-discipline.md && echo "✓ State-doctrine cross-link present"

# Overall lint and validation
uv run gz validate --documents
uv run gz lint
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.41-01-01: `.gzkit/rules/token-block-discipline.md` exists, follows rule-file structure (YAML frontmatter, body-level rule-version comment, visible version block quote), and passes `uv run gz validate --documents`.
- [ ] REQ-0.0.41-01-02: The rule file specifies the `--abandon` reason category enum (base: `network_loss`, `external_blocker`, `wrong_obpi_claimed`, `tool_failure`) with extension protocol documented.
- [ ] REQ-0.0.41-01-03: The rule file specifies register-entry minimum-information requirements (timestamp, commit SHA, decision context, branch state) in fail-closed language.
- [ ] REQ-0.0.41-01-04: The rule file specifies TTL canon (default value with rationale, warn-then-reap escalation policy, reaping authorization rule, reaping-attestation requirement).
- [ ] REQ-0.0.41-01-05: The rule file defines vocabulary section (token, issue, register entry, traversal, abandonment, reaping) aligned with railway antecedent mapping.
- [ ] REQ-0.0.41-01-06: The rule file cross-links to AGENTS.md § Behavior Rules and `docs/governance/state-doctrine.md` § Layer-2 audit-coupling rule.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [x] **Gate 1 (ADR):** Intent recorded in brief; parent ADR § Decision item quoted verbatim
- [x] **Gate 2 (TDD):** N/A for doctrine canon (non-executable); structural enforcement tested in OBPI-02/03/04
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem (5 lock releases with 0 register entries) leading to solution (token-block discipline) documented in ADR § Intent
- [x] **Key Proof:** Rule file exists with five binding sub-invariants fully specified; lexically validated
- [x] **OBPI Acceptance:** Evidence recorded; all requirements (REQ-0.0.41-01-01 through 06) satisfied

> **Lane: Lite** — process/governance documentation work with no CLI/API/schema changes. No Gate 5 human attestation required for self-closure.

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

### Implementation Summary

Parent ADR § Decision item (quoted verbatim):

> Couple lock-release to a handoff register entry. The binding invariant: A token cannot be surrendered without a register entry.

**Implementation:** Authored `.gzkit/rules/token-block-discipline.md` specifying five binding sub-invariants before any structural code changes land:

1. Auditable abandon categories: `--abandon <category>:<reason>` enum (base: network_loss, external_blocker, wrong_obpi_claimed, tool_failure; extension protocol via ADR)
2. Register-entry minimum-information rule: timestamp, commit SHA, decision context, branch state required for validator acceptance
3. Reaping register-entry rule: agent-B abandonment by reaper creates `abandoned_by_reaper` degenerate handoff before release succeeds
4. TTL canon and reaping discipline: 24h default, 12h warn threshold, any-agent authorization, reaping-agent-attestation-before-release
5. Release fail-closed precondition: lock-release refuses without register entry (or --abandon flag)

Vocabulary section (token, issue, register entry, traversal, abandonment, reaping) establishes shared semantics before code changes. Cross-links to AGENTS.md, state-doctrine.md, and ADR-0.0.41.

### Key Proof

Rule file exists and contains all five binding sub-invariants in fail-closed language:

```bash
$ test -f .gzkit/rules/token-block-discipline.md && wc -l .gzkit/rules/token-block-discipline.md
229 .gzkit/rules/token-block-discipline.md

$ grep -E "^## Binding" .gzkit/rules/token-block-discipline.md
## Binding Sub-Invariant 1: Auditable Abandon Categories
## Binding Sub-Invariant 2: Register-Entry Minimum-Information Rule
## Binding Sub-Invariant 3: Reaping Register-Entry Rule
## Binding Sub-Invariant 4: TTL Canon and Reaping Discipline
## Binding Sub-Invariant 5: Release Fail-Closed Precondition
```

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [x] Intent and scope recorded in OBPI brief and rule file § Doctrine Foundation section
- [x] Parent ADR § Decision item quoted verbatim in Implementation Summary
- [x] All five sub-invariants mapped to rule file sections (5 x § Binding Sub-Invariant)

### Gate 2 (TDD — No tests for doctrine canon)

<!-- gz-validate-skip: brief-cross-references -->
Doctrine canon is non-executable rule content; TDD gate is N/A for this OBPI. Structural enforcement (fail-closed release, validator, reaping logic) is tested in OBPI-0.0.41-02, 03, 04.

### Code Quality

```text
Running linters...
All checks passed!

ADR path contract check passed.
No Path(__file__).parents[N] violations found.
Lint passed.

Validated: documents
✓ All validations passed (1 scopes).
```

### Verification Commands

```bash
✓ Rule file exists with proper structure and content
✓ All validations passed (1 scopes).
✓ Lint checks passed
```

### Closing Argument

<!-- gz-validate-skip: brief-cross-references -->
OBPI-0.0.41-01 establishes the governance vocabulary and binding sub-invariants that gzkit will enforce structurally in OBPI-02/03/04. The rule file is authoritative for the entire discipline: five fail-closed invariants (abandon categories, minimum-information, reaping protocol, TTL canon, release precondition) grounded in railway absolute-block working and adapted to governance work. No code changes; pure documentation. All validation passes. Ready for OBPI-0.0.41-02 (structural enforcement implementation).

## Human Attestation

- Attestor: Jeffry
- Attestation: OBPI-0.0.41-01 completes doctrine canon: `.gzkit/rules/token-block-discipline.md` authored with five binding sub-invariants (auditable abandon categories, register-entry minimum-information, reaping protocol, TTL canon, release precondition), vocabulary section, and cross-links to AGENTS.md and state-doctrine.md. Lite lane, self-closeable. All validations pass (commit 3c5f1d54).
- Date: 2026-05-07
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

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
