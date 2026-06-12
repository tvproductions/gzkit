---
id: OBPI-0.0.65-05-handoff-archive-retention
parent: ADR-0.0.65-handoff-system-consolidation
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.0.65-05-handoff-archive-retention: Handoff Archive Retention

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.65-handoff-system-consolidation/ADR-0.0.65-handoff-system-consolidation.md`
- **Checklist Item:** #5 - "OBPI-0.0.65-05: **handoff-archive-retention** — Add a governed `gz handoff archive` subcommand that moves handoffs older than a threshold from `.gzkit/handoffs/` to `.gzkit/handoffs/archive/` (move-not-delete; audit trail preserved), honoring three mechanical guards: the migration-floor test (count canonical + archive ≥ floor), `continues_from:` chain integrity (chains may cross into the archive subdir), and lock-handoff coupling (never archive a handoff referenced by an `obpi_lock_released` ledger event). Extend `tests/governance/test_handoff_migration.py` to count the archive subdir. Add manpage + behave coverage. Surface-boundary split from OBPI-03 (distinct retention semantics + guard coupling). Depends on OBPI-03 (the `gz handoff` verb must exist). Closes GHI #585."

**Status:** Draft

> **Build sequencing (Magna Carta coupling).** This brief is **booked now,
> built in Phase C** per the Build-to-1.0 campaign
> (`docs/governance/build-to-1.0-campaign-2026-06-10.md`), which homes GHI #585
> to Phase C (MOTD / C.4 continuity-hybrid) and explicitly fences ADR-0.0.65
> against a standalone build. Do NOT pull this OBPI into a pipeline ahead of
> Phase C without an operator-ratified campaign amendment. It also has a hard
> code dependency on **OBPI-0.0.65-03** (the `gz handoff` verb must exist
> before the `archive` subcommand can attach).

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

**handoff-archive-retention** — Add a governed `gz handoff archive` subcommand that moves handoffs older than a threshold from `.gzkit/handoffs/` to `.gzkit/handoffs/archive/` (move-not-delete; audit trail preserved), honoring three mechanical guards: the migration-floor test (count canonical + archive ≥ floor), `continues_from:` chain integrity (chains may cross into the archive subdir), and lock-handoff coupling (never archive a handoff referenced by an `obpi_lock_released` ledger event). Extend `tests/governance/test_handoff_migration.py` to count the archive subdir. Add manpage + behave coverage. Surface-boundary split from OBPI-03 (distinct retention semantics + guard coupling). Depends on OBPI-03 (the `gz handoff` verb must exist). Closes GHI #585.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.65-handoff-system-consolidation/ADR-0.0.65-handoff-system-consolidation.md` — parent ADR for intent and scope
- `src/gzkit/handoff_archive.py` — **new** runtime module: archive-eligibility selection honoring the three guards (sibling to `src/gzkit/handoff_validation.py`)
- `src/gzkit/commands/handoff_archive.py` — **new** command wrapper backing `gz handoff archive` (sibling `.py` command modules under `src/gzkit/commands/`)
- `src/gzkit/cli/parser_maintenance.py` — register the `archive` subcommand under the `gz handoff` verb established by OBPI-0.0.65-03
- `tests/governance/test_handoff_archive.py` — **new** BEHAVIOR tests for the archive verb and its three guards
- `tests/governance/test_handoff_migration.py` — extend the migration floor to count the `archive/` subdir (canonical + archive ≥ floor)
- `docs/user/manpages/handoff-archive.md` — **new** manpage for the verb (sibling `.md` manpages)
- `features/handoff_archive.feature` — **new** behave coverage (sibling `.feature` files)
- `.gzkit/handoffs/archive/` — runtime archive destination (created by the verb)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/lock_manager.py`, `src/gzkit/handoff_validation.py`, `src/gzkit/ledger*.py` — **registered security surfaces** (`data/security_surfaces.json`); the archive logic IMPORTS and reads their existing public functions but MUST NOT edit them. Editing any would force `sensitivity: security` and is out of this brief's scope.
- The `gz handoff` verb scaffolding and its `create`/`resume`/`list` subcommands — owned by OBPI-0.0.65-03
- The canonical-location migration of legacy handoffs — owned by OBPI-0.0.65-01
- Existing handoffs' content/frontmatter — archive MOVES files; it never rewrites them
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. ALWAYS: Archive MOVES handoffs (`.gzkit/handoffs/` → `.gzkit/handoffs/archive/`); it MUST NEVER delete a handoff. The audit trail is preserved by relocation, not removal.
2. NEVER: Archive a handoff referenced by an `obpi_lock_released` ledger event's `handoff_path` (lock-handoff coupling guard — these are non-deletable audit artifacts per `.claude/rules/token-block-discipline.md` / ADR-0.0.41).
3. NEVER: Archive a handoff that is the `continues_from:` target of a handoff still resident in `.gzkit/handoffs/` (chain-integrity guard); resume-chain resolution MUST continue to resolve across the canonical + archive boundary.
4. ALWAYS: Keep the counted total (canonical + archive) at or above `_MIGRATION_BASELINE_FLOOR`; archiving MUST NOT drop the floor count.
5. NEVER: Edit a registered security surface (`lock_manager.py`, `handoff_validation.py`, `ledger*.py`) — read their public functions only. Editing forces `sensitivity: security`, which this brief does not declare.
6. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.
7. ALWAYS: Reconcile the brief with the parent ADR before implementation begins, and confirm OBPI-0.0.65-03 has landed the `gz handoff` verb (hard dependency).

> STOP-on-BLOCKERS: if prerequisites are missing — notably the `gz handoff` verb from OBPI-0.0.65-03 — print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.65-handoff-system-consolidation/ADR-0.0.65-handoff-system-consolidation.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Parent ADR exists: `docs/design/adr/foundation/ADR-0.0.65-handoff-system-consolidation/ADR-0.0.65-handoff-system-consolidation.md`
- [ ] Canonical store exists: `.gzkit/handoffs/`
- [ ] **Hard dependency — OBPI-0.0.65-03 landed:** the `gz handoff` verb is registered (run `uv run gz handoff --help`). STOP if absent.

**Existing Code (understand current state):**

- [ ] `tests/governance/test_handoff_migration.py` — the migration floor (`_MIGRATION_BASELINE_FLOOR`) and `continues_from`-chain assertions the new archive subdir must not violate
- [ ] `src/gzkit/handoff_validation.py` — `parse_frontmatter` / chain helpers to reuse (read-only; security surface)
- [ ] `src/gzkit/lock_manager.py` + ledger readers — how `obpi_lock_released` events record `handoff_path` (read-only; security surface)
- [ ] `src/gzkit/cli/parser_maintenance.py` — the parser the OBPI-03 `gz handoff` verb registers under, where the `archive` subcommand attaches
- [ ] A sibling manpage under `docs/user/manpages/` and a sibling `features/*.feature` for shape conventions

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
     outputs into Evidence. These are CONSTRUCTION HOUSEKEEPING (lint, type,
     test, mkdocs) — they prove the codebase is healthy, not what the OBPI
     yielded. The yielded product belongs in the `## Demo` section below.

     AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. The
     OBPI-pipeline verify stage executes commands via shlex.split + shell=False
     (GHI #415); compound commands are blocked at authoring time by
     gz validate --brief-command-shape and rejected at the verify stage.
     Write multi-step verification as separate uv run ... lines. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run -m unittest tests.governance.test_handoff_archive -v
uv run -m unittest tests.governance.test_handoff_migration -v
uv run -m behave features/handoff_archive.feature
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# (Build lands in Phase C; these are the intended product invocations.)
# Preview what would move — no filesystem mutation:
uv run gz handoff archive --older-than 30d --dry-run
# Move eligible handoffs into .gzkit/handoffs/archive/ (move-not-delete):
uv run gz handoff archive --older-than 30d
# Lock-coupled and continues_from-referenced handoffs are reported as SKIPPED, left in place.
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
Each REQ carries exactly one kind tag [BEHAVIOR|SUPPORT|STRUCTURAL-FENCE] (ADR-0.0.59).
-->

- [ ] REQ-0.0.65-05-01 [BEHAVIOR]: Given handoffs older than the threshold with no coupling, when `gz handoff archive --older-than <N>d` runs, then each eligible handoff exists under `.gzkit/handoffs/archive/` and no longer exists under `.gzkit/handoffs/` (move-not-delete; byte content unchanged)
- [ ] REQ-0.0.65-05-02 [BEHAVIOR]: Given a handoff referenced by an `obpi_lock_released` event's `handoff_path`, when archive runs, then that handoff is SKIPPED and remains in `.gzkit/handoffs/` (lock-coupling guard)
- [ ] REQ-0.0.65-05-03 [BEHAVIOR]: Given a handoff that is the `continues_from:` target of a still-canonical handoff, when archive runs, then it is not orphaned — either skipped or the chain resolver follows into `.gzkit/handoffs/archive/` (chain-integrity guard)
- [ ] REQ-0.0.65-05-04 [BEHAVIOR]: Given any archive run, when `test_handoff_migration.py` counts canonical + archive, then the total stays `>= _MIGRATION_BASELINE_FLOOR` (floor guard)
- [ ] REQ-0.0.65-05-05 [BEHAVIOR]: Given `gz handoff archive --older-than <N>d --dry-run`, when it runs, then it reports the would-move set and mutates nothing on disk
- [ ] REQ-0.0.65-05-06 [SUPPORT]: The verb is documented in `docs/user/manpages/handoff-archive.md` (verb, flags, three guards) — proven by `gz validate --documents` + an `artifact_edited` ledger event

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

**Before:** `.gzkit/handoffs/` grows monotonically — 67 handoffs as of 2026-06-12, up from 43 six days earlier (GHI #585). The store is append-only by design: the `gz-session-handoff` skill exposes only CREATE/RESUME, no source-level retention exists, and three mechanical guards (migration floor, `continues_from` chains, lock-coupling) make hand-`rm` a fail-close risk. Operators cannot safely declutter.

**After:** `gz handoff archive --older-than <N>d` provides a governed move-not-delete path that honors all three guards mechanically, relocating only safe-to-archive handoffs into `.gzkit/handoffs/archive/` while preserving the full audit trail.

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

`uv run gz handoff archive --older-than 30d --dry-run` lists the would-move set with lock-coupled and chain-referenced handoffs marked SKIPPED; the non-dry run moves the eligible set and the migration-floor test still passes (canonical + archive ≥ floor).

### Implementation Summary

**Parent ADR § Decision item this OBPI implements (GHI #321 pin):** ADR-0.0.65 § Decision #3 — *"Add a `gz handoff` CLI verb (the original GHI #529 ask) exposing create/resume/list, so handoff authoring routes through the validation gate instead of hand-authored markdown."* This OBPI extends that verb with an `archive` subcommand (surface-boundary split — retention semantics + guard coupling are distinct from authoring), the booked Checklist item #5.

- Files created/modified: _[build-time]_
- Tests added: _[build-time]_
- Date completed: _[build-time]_
- Attestation status: _[build-time]_
- Defects noted: _[build-time]_

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

- GHI #585 (`defect`, `tech-debt`) — "gz handoff: governed archive/retention verb for accumulated handoffs". This OBPI is its routed destination; #585 closes `superseded` → OBPI-0.0.65-05.

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
