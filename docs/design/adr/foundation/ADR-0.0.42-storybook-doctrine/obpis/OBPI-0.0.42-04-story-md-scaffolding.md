---
id: OBPI-0.0.42-04-story-md-scaffolding
parent: ADR-0.0.42-storybook-doctrine
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.42-04-story-md-scaffolding: gz-adr-create STORY.md scaffolding integration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.42-storybook-doctrine/ADR-0.0.42-storybook-doctrine.md`
- **Checklist Item:** #4 — "`gz-adr-create` STORY.md scaffolding integration — Per-ADR STORY.md stub scaffolded inside ADR package directory at ADR creation time. Pool ADRs exempt. `--skip-story-scaffold` emergency flag with `story_scaffold_skipped` ledger event."

**Status:** Draft

## Objective

Extend `gz plan create` (and the `gz-adr-create` skill template) to scaffold a `STORY.md` stub inside each newly-created non-pool ADR package directory at ADR creation time. Pool ADRs are exempt (no STORY.md scaffolded for `gz adr promote --kind pool`). Provide `--skip-story-scaffold` emergency flag for 2am-operator continuity, with `story_scaffold_skipped` ledger event leaving an audit trail. Backfill stubs for existing non-pool ADRs that don't yet have STORY.md (one-time migration step inside this OBPI).

## Lane

**Heavy** — modifies `gz plan create` runtime contract (new file scaffolded per ADR creation), adds new ledger event type, modifies skill template. External-contract change per AGENTS.md.

## Allowed Paths

- `src/gzkit/commands/plan.py` — exists; OBPI adds STORY.md scaffolding hook on `gz plan create`
- `src/gzkit/commands/` — directory exists; OBPI may extend ADR promote logic for pool exemption
- `src/gzkit/cli/` — directory exists; OBPI registers `--skip-story-scaffold` flag in the plan parser surface
- `src/gzkit/templates/` — directory exists; OBPI authors new `story.md` template
- `src/gzkit/ledger_events.py` — exists; OBPI registers `story_scaffold_skipped` and `story_scaffold_backfilled` event types
- `.gzkit/skills/gz-adr-create/` — directory exists; OBPI updates SKILL.md and adds assets/STORY-template.md
- `tests/` — directory exists; OBPI authors scaffolding tests under `tests/commands/` and extends `tests/cli/`
- `docs/user/manpages/` — exists; OBPI updates the plan-create manpage
- `docs/design/adr/foundation/` and `docs/design/adr/pre-release/` — existing directories; OBPI backfills `STORY.md` stubs for non-pool ADRs (creates new files inside existing ADR packages, never edits existing ADR bodies)

## Denied Paths

- `docs/user/storybook/` — arc files are OBPI-01 scope
- `src/gzkit/schemas/storybook.json` — schema is OBPI-01 scope
- `src/gzkit/storybook/` — runtime module is OBPI-02 scope
- `src/gzkit/governance/storybook_audits.py` — validator is OBPI-03 scope
- ADR markdown bodies (`ADR-X.Y.Z-slug.md` files) — backfill creates new STORY.md files only; no edits to existing ADR bodies
- New runtime dependencies, lockfiles, CI configuration

## Requirements (FAIL-CLOSED)

1. **REQUIREMENT (scaffolding on ADR creation):** Every successful `gz plan create` for a non-pool ADR (kind in `{foundation, feature}`) MUST also create `STORY.md` inside the new ADR package directory unless `--skip-story-scaffold` is passed. The scaffolded stub MUST contain (a) frontmatter with `parent: <ADR-ID>`, (b) a value-claim placeholder section, (c) a plumbing-class fallback shape ("If this ADR is plumbing for capability X, see [arc-X]"), (d) a 100–200-word soft-hint comment.
2. **REQUIREMENT (pool exemption):** `gz adr promote --kind pool` and any direct pool ADR creation MUST NOT scaffold STORY.md. Pool stubs already capture intent at value-claim altitude per the doctrine.
3. **REQUIREMENT (skip flag with audit trail):** `gz plan create --skip-story-scaffold` MUST be honored; when used, a `story_scaffold_skipped` ledger event MUST be emitted naming `{adr_id, skip_reason_argument_value, timestamp}`. The flag MUST require `--skip-story-scaffold-reason <REASON>` with a non-empty reason string.
4. **REQUIREMENT (backfill for existing non-pool ADRs):** As a one-time migration step inside this OBPI, every existing non-pool ADR package without a STORY.md MUST receive a backfilled stub using the same template. The backfill MUST emit one ledger event per ADR (`story_scaffold_backfilled`) so the migration is auditable.
5. **REQUIREMENT (skill template parity):** `.gzkit/skills/gz-adr-create/SKILL.md` MUST document the scaffolding behavior in its Procedure section so agent-driven ADR creation produces STORY.md by default. The `gz-adr-create` skill mirror sync (`gz agent sync control-surfaces`) MUST propagate the update to vendor mirrors (`.claude/skills/`, `.agents/skills/`, `.github/skills/`).
6. **REQUIREMENT (interaction with OBPI-03 validator):** After this OBPI lands and the backfill completes, OBPI-03's warn-only phase for STORY.md presence MUST flip to fail-closed. This OBPI's closeout MUST verify the flip occurs cleanly (no spurious failures from ADRs the backfill missed).
7. **REQUIREMENT (template consistency with arc-type):** The STORY.md stub template MUST NOT carry an `arc-type` field — STORY.md is per-ADR raw material for arc authoring, not an arc itself. Stubs are scoped to one decision; arcs span many decisions.

> STOP-on-BLOCKERS: if OBPI-01 has not landed (no doctrine), this OBPI's scaffolded stubs reference an undefined contract. If OBPI-03 has not landed, the warn-only-to-fail-closed transition cannot be exercised.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim.
- [ ] Parent ADR § Intent.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.42-storybook-doctrine/ADR-0.0.42-storybook-doctrine.md`

> **STOP:** If you cannot quote the parent ADR § Decision item this OBPI implements, STOP and re-read.

**Governance:**

- [ ] `AGENTS.md` § Lane Rules
- [ ] `.gzkit/rules/governance-core.md`
- [ ] `.gzkit/skills/gz-adr-create/SKILL.md` § Procedure (current shape)

**Context:**

- [ ] OBPI-01 outputs (doctrine, arc-type schema)
- [ ] OBPI-03 validator behavior (warn-only phase semantics)
- [ ] Existing template placement conventions in `src/gzkit/templates/`

**Prerequisites:**

- [ ] OBPI-01 landed (doctrine, schema, initial canon)
- [ ] OBPI-03 landed (validator can be flipped to fail-closed)

**Existing Code:**

- [ ] Existing template loading in `src/gzkit/commands/plan_cmd.py`
- [ ] Existing `--kind` handling in `gz plan create` and `gz adr promote`
- [ ] Existing skill mirror sync (`gz agent sync control-surfaces`)
- [ ] Existing ledger event registration

## Quality Gates

### Gate 1: ADR

- [ ] Parent ADR checklist item #4 quoted in Implementation Summary
- [ ] Intent and scope recorded

### Gate 2: TDD

- [ ] Tests cover: scaffolding fires for foundation ADR, scaffolding fires for feature ADR, scaffolding skipped for pool ADR, `--skip-story-scaffold` flag honored, `story_scaffold_skipped` event emitted with reason, backfill creates one stub per missing non-pool ADR, backfill emits `story_scaffold_backfilled` events, post-backfill OBPI-03 validator flips to fail-closed cleanly
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Manpage `gz-plan-create.md` updated with new flag and behavior
- [ ] `gz-adr-create` SKILL.md documents the scaffolding step
- [ ] `gz agent sync control-surfaces` propagates the skill update; mirror parity verified

### Gate 4: BDD (Heavy)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`
- [ ] At minimum: scenario where new ADR is created and STORY.md is scaffolded; scenario where `--skip-story-scaffold` is exercised and ledger event is emitted

### Gate 5: Human (Heavy + foundation)

- [ ] Human attestation recorded — foundation parent kind requires brief-level attestation

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run gz agent sync control-surfaces

uv run gz plan create test-storybook-scaffold --kind foundation --semver 0.0.99 --lane lite --dry-run
# Expected: dry-run shows STORY.md will be scaffolded

uv run gz plan create test-storybook-scaffold --kind foundation --semver 0.0.99 --lane lite --skip-story-scaffold --skip-story-scaffold-reason "test"
# Expected: ADR created without STORY.md, ledger event emitted

# Backfill verification:
find docs/design/adr/foundation docs/design/adr/pre-release -name "ADR-*-*" -type d | while read d; do
  test -f "$d/STORY.md" || echo "missing STORY.md: $d"
done
# Expected: empty output (all non-pool ADRs have STORY.md after backfill)

uv run gz validate --storybook-fresh   # passes (validator now in fail-closed mode)
```

## Demo

```bash
# Create a fresh ADR and observe STORY.md scaffolded:
uv run gz plan create demo-story --kind foundation --semver 0.0.98 --lane lite
ls docs/design/adr/foundation/ADR-0.0.98-demo-story/

# Inspect the scaffolded stub:
head -30 docs/design/adr/foundation/ADR-0.0.98-demo-story/STORY.md

# Demonstrate the skip flag with audit trail:
uv run gz plan create demo-skip --kind foundation --semver 0.0.97 --lane lite --skip-story-scaffold --skip-story-scaffold-reason "emergency hotfix"
grep story_scaffold_skipped .gzkit/ledger.jsonl | tail -1

# Demonstrate pool exemption:
uv run gz adr promote ADR-pool.example --kind pool   # if applicable
test ! -f docs/design/adr/pool/ADR-pool.example/STORY.md   # no STORY.md scaffolded for pool
```

## Acceptance Criteria

- [ ] REQ-0.0.42-04-01: Given `gz plan create <slug> --kind foundation`, when it succeeds, then a `STORY.md` file is created inside the new ADR package directory with frontmatter naming the parent ADR and a value-claim placeholder section.
- [ ] REQ-0.0.42-04-02: Given `gz plan create <slug> --kind feature`, when it succeeds, then a `STORY.md` file is created with the same shape as foundation ADRs.
- [ ] REQ-0.0.42-04-03: Given `gz adr promote --kind pool` (or any pool-targeted ADR creation), when it succeeds, then no `STORY.md` is created — pool ADRs are exempt.
- [ ] REQ-0.0.42-04-04: Given `gz plan create --skip-story-scaffold --skip-story-scaffold-reason "<text>"`, when invoked, then the ADR is created without `STORY.md` and a `story_scaffold_skipped` ledger event is emitted with `{adr_id, skip_reason, timestamp}`.
- [ ] REQ-0.0.42-04-05: Given `gz plan create --skip-story-scaffold` without a `--skip-story-scaffold-reason` value, when invoked, then it exits non-zero with a diagnostic requiring the reason.
- [ ] REQ-0.0.42-04-06: Given the existing non-pool ADR corpus at OBPI start, when the migration step inside this OBPI completes, then every non-pool ADR package directory contains a `STORY.md` file and one `story_scaffold_backfilled` ledger event was emitted per backfilled stub.
- [ ] REQ-0.0.42-04-07: Given the OBPI-03 validator in warn-only phase prior to this OBPI, when this OBPI completes its backfill, then the validator is flipped to fail-closed and `gz validate --storybook-fresh` passes against the now-fully-scaffolded corpus.
- [ ] REQ-0.0.42-04-08: Given the `gz-adr-create` skill SKILL.md prior to this OBPI, when this OBPI completes, then the SKILL.md Procedure section names the STORY.md scaffolding step and the skill mirror sync propagates the update to all vendor mirrors (verified via `gz agent sync control-surfaces` clean exit).
- [ ] REQ-0.0.42-04-09: Given a freshly scaffolded STORY.md, when inspected, then the stub contains no `arc-type` frontmatter field — STORY.md is per-ADR raw material, not an arc itself.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** Full test suite covering scaffolding, exemptions, skip flag, backfill, validator flip
- [ ] **Code Quality:** Lint, type check clean
- [ ] **Gate 3 (Docs):** mkdocs --strict + skill mirror parity + manpage update clean
- [ ] **Gate 4 (BDD):** Acceptance scenarios pass
- [ ] **Gate 5 (Human):** Attestation recorded (foundation parent requires)
- [ ] **Value Narrative:** Documented below
- [ ] **Key Proof:** Concrete scaffold-on-creation + skip-flag-with-event output below
- [ ] **OBPI Acceptance:** Evidence recorded

## Evidence

### Gate 1 (ADR)

- [ ] Intent recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste scaffolding test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste mkdocs + skill sync output here
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

<!-- Before: per-ADR raw material for arc authoring did not exist; new arcs had to derive value claims from raw ADR text on demand. After: every non-pool ADR carries a STORY.md stub authored at creation time (or backfilled), accumulating a corpus of value-claim raw material; the --skip-story-scaffold flag preserves operational continuity at 2am with a ledger audit trail. -->

### Key Proof

```text
# Paste actual scaffold-on-creation output, skip-flag exercise with ledger event, and OBPI-03 validator flip from warn-only to fail-closed
```

### Implementation Summary

- Files created/modified: `src/gzkit/commands/plan_cmd.py` (scaffolding), `src/gzkit/commands/adr_promote.py` (pool exemption), `src/gzkit/cli/parser_plan.py` (--skip-story-scaffold), `src/gzkit/templates/story.md` (new template), `src/gzkit/ledger/events.py` (event registration), `.gzkit/skills/gz-adr-create/SKILL.md` (procedure update), `.gzkit/skills/gz-adr-create/assets/STORY-template.md` (skill template), backfilled `STORY.md` stubs across existing non-pool ADR packages, manpage update, tests
- Tests added: scaffolding, exemption, skip flag, backfill, validator flip
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked at brief authoring time._

## Human Attestation

- Attestor: `<name>` (foundation parent kind requires)
- Attestation: substantive attestation text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
