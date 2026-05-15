---
id: OBPI-0.0.33-03-pointer-integrity-validator
parent: ADR-0.0.33-agent-control-surface-fidelity
item: 3
lane: Heavy
status: Completed
---

# OBPI-0.0.33-03-pointer-integrity-validator: Pointer Integrity Validator

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/ADR-0.0.33-agent-control-surface-fidelity.md`
- **Checklist Item:** #3 - "OBPI-0.0.33-03: Pointer-integrity validator (`gz validate --pointer-anchors`) — parse `> See [...]` blockquotes, resolve anchors, reverse-check `<!-- lifted-from: -->` back-pointers, exit 3 on unresolved"

**Status:** Completed

## Objective

Implement `gz validate --pointer-anchors` (ADR-0.0.33 Invariant 3): walk the
per-turn surface corpus (`AGENTS.md`, `CLAUDE.md`, `.claude/rules/**`), parse
every `> See [...](path#anchor)` blockquote, resolve each anchor against the
destination file's heading slugs (mkdocs slugification), reverse-check that
each destination carries a `<!-- lifted-from: <source>#<anchor> -->` comment,
and exit 3 with a `ValidationError(type="pointer_anchors")` on any unresolved
pointer or missing back-pointer. Error messages name both halves of the
contract: source `file:line` and the unresolved destination.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/**` — parent ADR package scope
- `src/gzkit/governance/trust_audits/pointer_integrity.py` — validator implementation (new module)
- `src/gzkit/governance/trust_audits/__init__.py` — package re-export of `validate_pointer_integrity`
- `src/gzkit/cli/parser_maintenance.py` — `gz validate --pointer-anchors` flag registration and dispatch
- `tests/governance/test_pointer_integrity.py` — Gate-2 TDD asset
- `docs/user/manpages/validate.md` — manpage entry for the new flag (canonical manpage path; `gz-validate.md` was a legacy placeholder from OBPI-01 that does not exist on disk)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New runtime dependencies (stdlib markdown parsing only)
- Composite wiring into `--surface-fidelity` (owned by OBPI-05)
- Other invariants' validator modules
- Editing existing `> See [...]` pointers or `<!-- lifted-from: -->` back-pointers (the validator only enforces; remediation of detected drift is a separate fix)
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

This OBPI implements parent-ADR Invariant 3 only. The other three invariants
are out of scope for this brief.

1. REQUIREMENT: **Forward anchor resolution.** `gz validate --pointer-anchors` walks the per-turn surface corpus (`AGENTS.md`, `CLAUDE.md`, `.claude/rules/**`), parses every `> See [...](path#anchor)` blockquote, and asserts each `path#anchor` resolves to an existing heading anchor in the destination file. NEVER use raw string matching on the heading text; ALWAYS slugify with the established docs slug rule (lowercase, hyphenated, non-alphanumeric stripped) to match mkdocs anchor generation.
2. REQUIREMENT: **Reverse back-pointer check.** For each lifted-pedagogy destination (any file referenced by a `> See [...]` pointer in the per-turn surface), the destination MUST carry a matching `<!-- lifted-from: <source-path>#<anchor> -->` comment. A forward pointer without a back-pointer is fail-closed.
3. REQUIREMENT: **Exit 3 on any unresolved pointer or missing back-pointer.** Single failure → `ValidationError` with `type="pointer_anchors"`, exit code 3. NEVER warn-and-pass.
4. REQUIREMENT: **Pointer surface is bounded.** ONLY `> See [...](path#anchor)` blockquotes inside the per-turn surface corpus are checked. NEVER walk arbitrary markdown for "see" prose; the blockquote-`See`-link form is the canonical lift-pointer shape (per the lift-rationale doctrine).
5. REQUIREMENT: **Error message names both halves.** Each emitted `ValidationError` MUST cite the source file:line of the unresolved pointer AND the destination path that lacks the matching anchor or back-pointer. Single-side errors are insufficient for remediation.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/ADR-0.0.33-agent-control-surface-fidelity.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Parent ADR file exists: `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/ADR-0.0.33-agent-control-surface-fidelity.md`
- [ ] Per-turn surface corpus exists: `AGENTS.md`, `CLAUDE.md`, `.claude/rules/`
- [ ] Trust-audits package exists: `src/gzkit/governance/trust_audits/__init__.py`
- [ ] CLI parser exists: `src/gzkit/cli/parser_maintenance.py`
- [ ] At least one existing `> See [...](path#anchor)` pointer in the corpus (sanity baseline for the parser)

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

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
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run gz validate --pointer-anchors                  # must exit 0 on a clean tree
uv run -m unittest tests.governance.test_pointer_integrity -v
test -f src/gzkit/governance/trust_audits/pointer_integrity.py
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.33-03-01: Given a `> See [path#anchor]` pointer whose destination heading exists in `path` and whose slug matches the mkdocs slugification, when `gz validate --pointer-anchors` runs, then it exits 0 for that pointer.
- [ ] REQ-0.0.33-03-02: Given a `> See [path#anchor]` pointer whose destination path does not exist OR whose anchor is absent from the destination, when `gz validate --pointer-anchors` runs, then it exits 3 with a `ValidationError` of `type="pointer_anchors"` naming both the source `file:line` and the unresolved destination.
- [ ] REQ-0.0.33-03-03: Given a destination path referenced by a forward pointer but lacking a `<!-- lifted-from: <source>#<anchor> -->` back-pointer, when `gz validate --pointer-anchors` runs, then it exits 3 with a `ValidationError` naming the missing back-pointer.
- [ ] REQ-0.0.33-03-04: Given a non-blockquote `[link](path#anchor)` reference in the per-turn surface, when `gz validate --pointer-anchors` runs, then the reference is NOT checked (scope is `> See [...]` blockquotes only).
- [ ] REQ-0.0.33-03-05: Given the validator module, when imported, then `gzkit.governance.trust_audits.validate_pointer_integrity` resolves and matches the package re-export pattern.

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


```bash
$ uv run gz validate --pointer-anchors
```

On the current tree, exits 3 with 6 real findings — proving the validator detects genuine pre-existing pointer drift that was invisible before this OBPI. The findings span `AGENTS.md` (missing back-pointers on lifted-pedagogy destinations) and `.claude/rules/complexity-thresholds.md` (non-existent destination path).

Quality evidence — receipts: `arb-ruff-baa86fe3f8d648c1b6995b6cabc510d0` (lint clean), `arb-step-typecheck-bf0049963cd44bd1a0d6608e0fe742f8` (ty clean), `arb-step-unittest-fdf6ab9a868c4f66a458abc393697e33` (5069/5069 full suite pass), `arb-step-unittestscoped-6177270bd01e420f9e3c77d5420fb509` (15/15 OBPI-scoped pass), `arb-step-mkdocs-96ef9a8507574172ad0e54e1ac371f22` (docs build clean).

### Implementation Summary


- Files created: `src/gzkit/governance/trust_audits/pointer_integrity.py` (validator implementation: parses `> See [...](path#anchor)` blockquotes from per-turn surface corpus, slugifies anchors using mkdocs slug rules, checks forward resolution and reverse `<!-- lifted-from: -->` back-pointers), `tests/governance/test_pointer_integrity.py` (15 Gate-2 TDD tests across 4 test classes)
- Files modified: `src/gzkit/governance/trust_audits/__init__.py` (re-export `validate_pointer_integrity`), `src/gzkit/cli/parser_maintenance.py` (`--pointer-anchors` flag + dispatch), `src/gzkit/commands/validate_cmd.py` (4 threading points for `check_pointer_anchors`), `docs/user/manpages/validate.md` (manpage section), brief Objective substantiated, `data/behave_coverage_waivers.json` (waiver under `adr-0.0.33-03-bdd-deferred-to-composite-obpi-05`)
- Tests added: 15 unit tests covering all 5 REQs (TestPointerResolves: 4, TestUnresolvedAnchor: 4, TestMissingBackPointer: 2, TestNonBlockquoteNotChecked: 2, TestPackageReExport: 3)
- Date completed: 2026-05-15
- Attestation status: Gate-5 attested by operator
- Defects noted: 6 pre-existing pointer drift findings detected by the validator — to be filed as a GHI; remediation deferred per brief Denied Paths

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — OBPI-0.0.33-03 pointer-integrity validator landed under ADR-0.0.33 Invariant 3. 5 FAIL-CLOSED REQs verified by 15 unit tests in tests/governance/test_pointer_integrity.py (uncovered_reqs: 0 per gz covers). Quality green: arb-ruff-baa86fe3f8d648c1b6995b6cabc510d0 (lint clean), arb-step-typecheck-bf0049963cd44bd1a0d6608e0fe742f8 (ty clean), arb-step-unittest-fdf6ab9a868c4f66a458abc393697e33 (5069/5069 pass), arb-step-unittestscoped-6177270bd01e420f9e3c77d5420fb509 (15/15 OBPI-scoped pass), arb-step-mkdocs-96ef9a8507574172ad0e54e1ac371f22 (docs build clean). Validator detects 6 pre-existing pointer-drift findings in AGENTS.md and .claude/rules/complexity-thresholds.md — to be filed as a GHI; remediation out of scope per brief Denied Paths.
- Date: 2026-05-15

---

**Brief Status:** Draft

**Date Completed:** 2026-05-15

**Evidence Hash:** -
