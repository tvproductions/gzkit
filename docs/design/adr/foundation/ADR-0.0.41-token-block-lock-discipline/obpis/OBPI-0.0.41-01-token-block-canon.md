---
id: OBPI-0.0.41-01-token-block-canon
parent: ADR-0.0.41-token-block-lock-discipline
item: 1
lane: Lite
status: Completed
---

# OBPI-0.0.41-01-token-block-canon: Token Block Canon

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.41-token-block-lock-discipline/ADR-0.0.41-token-block-lock-discipline.md`
- **Checklist Item:** #1 - "OBPI-0.0.41-01: Token-block doctrine canon — author `.gzkit/rules/token-block-discipline.md` and `docs/governance/token-block-doctrine.md` (railway-historical reference). Specify the binding sub-invariants the structural enforcement alone does not close: (a) auditable `--abandon` reason categories (rejecting free-text-only reasons; categories include `network_loss`, `external_blocker`, `wrong_obpi_claimed`, `tool_failure`, with extension protocol); (b) minimum-information requirements for the register entry (last lock-event timestamp, last commit SHA, named decisions, branch state) so structurally-valid-but-semantically-empty handoffs are also rejected; (c) lock-takeover / reaping register-entry rule (the railway-analogue lost-token procedure: a reaping by agent-B emits an `abandoned_by_reaper` register entry recording agent-A's last-known state); (d) **time-bound discipline (TTL canon and reaping cadence): default TTL value with rationale, escalation policy (warn-then-reap windows), who-may-reap (any agent at next session-start; explicit operator override), and the attestation requirement that the reaping agent MUST produce the `abandoned_by_reaper` register entry as a precondition of the reap — mirroring the rule for ordinary release, so reaping is not a doctrine-bypass**; (e) cross-link from AGENTS.md § Behavior Rules and `docs/governance/state-doctrine.md`. Establishes vocabulary (token, register entry, traversal, abandonment, reaping) before any code change."

**Status:** Completed

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
# Each command below is a single-program invocation; the pipeline runtime
# executes verification commands without shell wrapping, so compound `&&`
# expressions fail with `test: unexpected operator`. Bare `grep` returns
# exit 0 on match, non-zero on miss or missing file — sufficient signal.

# File existence + structure
grep -q . .gzkit/rules/token-block-discipline.md
grep -q "^---$" .gzkit/rules/token-block-discipline.md
grep -q "<!-- rule-version:" .gzkit/rules/token-block-discipline.md

# Five binding sub-invariants
grep -qE "(--abandon|reason.*category|network_loss|external_blocker)" .gzkit/rules/token-block-discipline.md
grep -qE "(minimum-information|timestamp|commit SHA|branch state)" .gzkit/rules/token-block-discipline.md
grep -qE "(abandoned_by_reaper|reaping)" .gzkit/rules/token-block-discipline.md
grep -qE "(TTL|time-bound|default.*value)" .gzkit/rules/token-block-discipline.md
grep -qE "(vocabulary|token|register entry|traversal)" .gzkit/rules/token-block-discipline.md

# Cross-link validation
grep -q "AGENTS.md" .gzkit/rules/token-block-discipline.md
grep -q "state-doctrine.md" .gzkit/rules/token-block-discipline.md

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

> **Lane: Lite** — process/governance documentation work with no CLI/API/schema changes. Lite-lane scope determines which gates fire (no Gate 3 docs scope, no Gate 4 BDD scope, no Gate 5 security walkthrough), but per ADR-0.0.36 universal attestation, Gate 5 brief-level human attestation is REQUIRED regardless of lane — there is no self-close path.

> For ceremony steps and universal-attestation rules, see `AGENTS.md` section `Universal OBPI Attestation (ADR-0.0.36, GHI #342)`.

### Implementation Summary


- Rule authored: .gzkit/rules/token-block-discipline.md on 2026-05-07 with all 5 binding sub-invariants per parent ADR § Decision item
- Abandon enum: network_loss, external_blocker, wrong_obpi_claimed, tool_failure (extension protocol via published ADR; free-text-only rejection)
- Register-entry minimum-info: last lock-event timestamp, last commit SHA, named decision context, branch state — entries lacking any of these fail validator
- Reaping protocol: abandoned_by_reaper degenerate handoff created BEFORE release_lock() succeeds (mirrors ordinary release fail-closed precondition)
- TTL canon: 24h default; 12h warn-then-reap escalation; any-agent authorization at SessionStart; operator override via --force; reaping-attestation-before-release universal rule
- Vocabulary section: token (OBPI lock), issue (claim event), register entry (handoff doc), traversal (OBPI session), abandonment (degenerate handoff), reaping (lock takeover by other agent) — railway-historical mapping to absolute-block working
- Brief drift corrections in this session: verification commands rewritten from shell-compound to bare single-program greps (test -f X && grep && echo failed with unexpected-operator under shell-less runtime); line-183 prose updated to reflect ADR-0.0.36 universal Gate-5 attestation
- Ceremony exercises authored doctrine: lock claimed agent=claude-code-fffb69b5 at session-start; register-entry handoff to follow at release per token-block sub-invariant 5

### Key Proof


- REQ coverage: 6/6 covered (REQ-0.0.41-01-01 through 06) via SUPPORT-kind proof channel (ledger artifact_edited events 2026-05-07/10 + structural validator gz validate --documents admitting rule-file shape)
- Verification checks: 16/16 PASS including precomplete
- Canonical ARB receipts: arb-ruff-790611fd5d1349b59b4888b9b2e50787, arb-step-typecheck-18f81962b9874950bffbf7d7a80cb8b1, arb-step-unittest-2d40900ae9d24e829e8ca253cd91e337, arb-step-mkdocs-75182a2ef39a48d4863fa07584a21e26
- Precomplete preconditions: 7/7 met (lock_held, plan_audit_receipt, brief_readiness, reconcile_idempotent, arb_receipts, brief_headings, behave_req_coverage)
- Plan-audit advisory: ADR-0.0.42 OBPI-04 sibling-overlap on parent ADR file (non-blocking)

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

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.41-01 token-block canon: .gzkit/rules/token-block-discipline.md specifies all 5 binding sub-invariants per parent ADR § Decision item (abandon-category enum with extension protocol, register-entry minimum-info rule, reaping protocol via abandoned_by_reaper, TTL canon with 24h default + 12h warn-then-reap, vocabulary section grounding token/issue/register-entry/traversal/abandonment/reaping). 6/6 REQs covered (REQ-0.0.41-01-01 through 06) via SUPPORT-kind proof channel (ledger artifact_edited + structural validator) per REQ Scope Discipline (ADR-0.0.59); 16/16 verification checks PASS including precomplete (7/7 preconditions). Canonical ARB receipts: arb-ruff-790611fd5d1349b59b4888b9b2e50787, arb-step-typecheck-18f81962b9874950bffbf7d7a80cb8b1, arb-step-unittest-2d40900ae9d24e829e8ca253cd91e337, arb-step-mkdocs-75182a2ef39a48d4863fa07584a21e26. Closeout exercises the doctrine the OBPI authored: lock claimed at session-start (agent=claude-code-fffb69b5); register-entry handoff to follow at release.
- Date: 2026-05-27
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

**Date Completed:** 2026-05-27

**Evidence Hash:** -
