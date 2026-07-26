---
id: OBPI-0.0.42-02-storybook-cli
parent: ADR-0.0.42-storybook-doctrine
item: 2
lane: Heavy
status: Draft
allowlist:
- src/gzkit/
- src/gzkit/cli/
- src/gzkit/ledger_events.py
- tests/
- tests/storybook/
- tests/cli/test_storybook_cli.py
- docs/user/manpages/
reqs:
- REQ-0.0.42-02-01
- REQ-0.0.42-02-02
- REQ-0.0.42-02-03
- REQ-0.0.42-02-04
- REQ-0.0.42-02-05
- REQ-0.0.42-02-06
- REQ-0.0.42-02-07
verification:
- uv run gz validate --documents
- uv run gz lint
- uv run gz typecheck
- uv run gz test
- uv run gz cli audit
- uv run mkdocs build --strict
- uv run gz storybook --help
- uv run gz storybook list
- uv run gz storybook derive --arc from-init-to-first-attested-release
- 'uv run gz storybook derive --arc from-init-to-first-attested-release   # second run: no-op, no ledger event'
- uv run gz storybook derive --arc from-init-to-first-attested-release
---

# OBPI-0.0.42-02-storybook-cli: gz storybook CLI surface

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.42-storybook-doctrine/ADR-0.0.42-storybook-doctrine.md`
- **Checklist Item:** #2 — "`gz storybook` CLI surface — Implements list/show/derive/new verbs with v0 minimum (`derive --arc` + `list`) and v1 deferrable surfaces (show, new, --dry-run, --all, --accept-stale-storybook). Emits `storybook_derived` ledger events."

**Status:** Draft

## Objective

Land the `gz storybook` CLI surface (v0 minimum: `list`, `derive --arc <slug>`; v1 deferrable: `show`, `new`, `--dry-run`, `--all`, `--accept-stale-storybook`) and the underlying `src/gzkit/storybook/` runtime module. The deriver refreshes the Layer-3 anchor block of an arc by reading anchored-ADR frontmatter directly and rewriting only the marker-bounded region. Emits `storybook_derived` ledger events with arc slug, diff hash, and source artifact set.

## Lane

**Heavy** — new top-level CLI verb, new ledger event type, new runtime module. External-contract changes per AGENTS.md.

## Allowed Paths

- `src/gzkit/` — directory exists; OBPI creates new `storybook/` runtime module subdirectory inside (deriver, anchor parser, frontmatter reader, atomic write helpers)
- `src/gzkit/cli/` — directory exists; OBPI adds storybook subcommand surface module + parser registration + register storybook subcommand into existing `__init__.py`
- `src/gzkit/ledger_events.py` — exists; OBPI registers `storybook_derived` event type
- `tests/` — directory exists; OBPI creates `tests/storybook/` and `tests/cli/test_storybook_cli.py`
- `docs/user/manpages/` — directory exists; OBPI authors `gz-storybook.md`, `gz-storybook-derive.md`, `gz-storybook-list.md` and updates the manpage `index.md`

## Denied Paths

- `docs/user/storybook/` — arc files are OBPI-01 scope; CLI does not author arcs (only refreshes anchor blocks)
- `src/gzkit/schemas/storybook.json` — schema is OBPI-01 scope; CLI consumes but does not modify it
- `src/gzkit/governance/trust_audits.py` — validator is OBPI-03 scope
- `.gzkit/skills/gz-adr-create/**` — STORY.md scaffolding is OBPI-04 scope
- `gz check` wiring — OBPI-03 scope
- New runtime dependencies, lockfiles, CI configuration

## Requirements (FAIL-CLOSED)

1. **REQUIREMENT (v0 verb set):** `gz storybook list` and `gz storybook derive --arc <slug>` MUST be functional and tested. v1 verbs (`show`, `new`, `--dry-run`, `--all`, `--accept-stale-storybook`) MAY be deferred to a follow-up but their argparse flags SHOULD be reserved (parser stubs that exit with "not yet implemented" until landed).
2. **REQUIREMENT (deriver Layer-1 inviolability):** The deriver MUST NOT modify any byte outside the `<!-- BEGIN ANCHOR BLOCK -->` ... `<!-- END ANCHOR BLOCK -->` marker pair. A test MUST exercise this by computing a hash of the file's content outside the marker region before and after derive; the hashes MUST match.
3. **REQUIREMENT (Layer-1 frontmatter source):** The deriver MUST read ADR title and status by parsing on-disk ADR frontmatter directly from `docs/design/adr/{foundation,pre-release}/ADR-X.Y.Z-*/ADR-X.Y.Z-*.md`. The deriver MUST NOT read from `docs/governance/GovZero/adr-status.md` (which is itself Layer 3, would chain derived-on-derived staleness).
4. **REQUIREMENT (atomic writes):** The deriver MUST write arc updates atomically (write-temp-then-rename). An interrupted derive MUST NOT leave partial state on disk.
5. **REQUIREMENT (ledger event):** Every successful derive that produced changes MUST emit a `storybook_derived` ledger event with at minimum `{arc_slug, diff_hash, source_adrs, source_skills, source_runbooks, source_manpages, timestamp}`. A no-op derive (anchor block already current) MUST NOT emit an event.
6. **REQUIREMENT (deriver error format):** When an anchored artifact is missing, renamed, or superseded, the deriver MUST exit non-zero with an error that names: arc slug, anchor identifier, failure reason (`missing` | `superseded` | `renamed`), and recovery hint (`rename-anchor` | `archive-arc` | `file-ghi`).
7. **REQUIREMENT (manpage parity):** Every CLI verb registered MUST have a corresponding manpage under `docs/user/manpages/gz-storybook*.md` per ADR-0.0.6 documentation cross-coverage. `gz cli audit` MUST pass after this OBPI lands.

> STOP-on-BLOCKERS: if OBPI-01 has not landed (no `docs/user/storybook/` directory, no schema), halt — this OBPI depends on OBPI-01's artifacts.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim.
- [ ] Parent ADR § Intent.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.42-storybook-doctrine/ADR-0.0.42-storybook-doctrine.md`

> **STOP:** If you cannot quote the parent ADR § Decision item this OBPI implements, STOP and re-read.

**Governance:**

- [ ] `AGENTS.md` § Lane Rules
- [ ] `.gzkit/rules/governance-core.md` § Operator-doc verb resolution
- [ ] `docs/governance/state-doctrine.md` — Layer 1/2/3 doctrine

**Context:**

- [ ] `src/gzkit/cli/__init__.py` — existing subcommand registration pattern (use `gz adr` or `gz validate` as model)
- [ ] `src/gzkit/ledger.py` — ledger event registration pattern
- [ ] OBPI-01 outputs (the schema and arc files this CLI consumes)

**Prerequisites:**

- [ ] OBPI-01 landed: `docs/user/storybook/` exists with strawman + receipts arc, `src/gzkit/schemas/storybook.json` exists
- [ ] At least two arc files with marker-bounded anchor blocks present for testing

**Existing Code:**

- [ ] Existing argparse subparser conventions across `src/gzkit/cli/`
- [ ] Existing ledger event registration (see `gz adr emit-receipt` for a working example)
- [ ] Existing atomic-write helpers (if any) under `src/gzkit/io/` or equivalent

## Quality Gates

### Gate 1: ADR

- [ ] Parent ADR checklist item #2 quoted in Implementation Summary
- [ ] Intent and scope recorded

### Gate 2: TDD

- [ ] Tests cover: list verb, derive verb (changed), derive verb (no-op), atomic write under interruption simulation, marker-region inviolability, missing-anchor error format, ledger event emission shape
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Manpages for `gz storybook list` and `gz storybook derive` exist and pass `gz cli audit`

### Gate 4: BDD (Heavy)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`
- [ ] At minimum: scenario exercising deriver against a stale arc and confirming ledger event emission

### Gate 5: Human (Heavy + foundation)

- [ ] Human attestation recorded — foundation parent kind requires brief-level attestation

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz cli audit
uv run mkdocs build --strict

uv run gz storybook --help
uv run gz storybook list
uv run gz storybook derive --arc from-init-to-first-attested-release
uv run gz storybook derive --arc from-init-to-first-attested-release   # second run: no-op, no ledger event

sha256sum docs/user/storybook/from-init-to-first-attested-release.md
uv run gz storybook derive --arc from-init-to-first-attested-release

grep storybook_derived .gzkit/ledger.jsonl
```

## Demo

```bash
uv run gz storybook list

uv run gz storybook derive --arc receipts-capability

uv run gz storybook derive --arc broken-arc-with-missing-adr
# Expected: exit 3, error names arc, anchor, reason, recovery

grep storybook_derived .gzkit/ledger.jsonl | tail -1
```

## Acceptance Criteria

- [ ] REQ-0.0.42-02-01: Given OBPI-01's strawman arc, when `gz storybook derive --arc from-init-to-first-attested-release` runs, then the marker-bounded anchor block is rewritten with current ADR titles and statuses; the rest of the file is byte-identical.
- [ ] REQ-0.0.42-02-02: Given an arc whose anchored ADRs have not changed since last derive, when the deriver runs again, then no ledger event is emitted (no-op exits 0 silently).
- [ ] REQ-0.0.42-02-03: Given an arc anchoring an ADR that no longer exists at the expected path, when the deriver runs, then the deriver exits non-zero with an error naming `arc=<slug> anchor=<ADR-ID> reason=missing recovery=<hint>`.
- [ ] REQ-0.0.42-02-04: Given a successful derive that mutated the anchor block, when the ledger is inspected, then a `storybook_derived` event exists with `{arc_slug, diff_hash, source_adrs, source_skills, source_runbooks, source_manpages, timestamp}`.
- [ ] REQ-0.0.42-02-05: Given a derive run interrupted mid-write (simulated by killing the process during write), when the file system is inspected, then the arc file is either fully updated or unchanged — never partially written.
- [ ] REQ-0.0.42-02-06: Given the registered CLI verbs, when `gz cli audit` runs, then every storybook verb has a corresponding manpage under `docs/user/manpages/gz-storybook*.md`.
- [ ] REQ-0.0.42-02-07: Given the deriver, when it reads ADR title/status, then it parses on-disk ADR frontmatter at `docs/design/adr/{foundation,pre-release}/ADR-X.Y.Z-*/ADR-X.Y.Z-*.md` directly — never `docs/governance/GovZero/adr-status.md` (test exercises both paths and confirms the deriver reads only the former).

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** Full test suite covering deriver invariants
- [ ] **Code Quality:** Lint, type check clean
- [ ] **Gate 3 (Docs):** mkdocs --strict + cli audit clean
- [ ] **Gate 4 (BDD):** Acceptance scenarios pass
- [ ] **Gate 5 (Human):** Attestation recorded (foundation parent requires)
- [ ] **Value Narrative:** Documented below
- [ ] **Key Proof:** Concrete derive run output below
- [ ] **OBPI Acceptance:** Evidence recorded

## Evidence

### Gate 1 (ADR)

- [ ] Intent recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste deriver test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste mkdocs + cli audit output here
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

<!-- Before: arc files exist as static documents; refresh of anchored ADR titles/statuses requires hand-editing or risks staleness. After: `gz storybook derive --arc <slug>` mechanically refreshes the Layer-3 region and emits a ledger event, while the marker-bounded discipline guarantees Layer-1 narrative is never mutated by automation. -->

### Key Proof

```text
# Paste actual derive run output, ledger event, and before/after diff demonstrating Layer-1 inviolability
```

### Implementation Summary

- Files created/modified: `src/gzkit/storybook/` (new module), `src/gzkit/cli/storybook.py` (new), `src/gzkit/cli/parser_storybook.py` (new), `src/gzkit/cli/__init__.py` (registration), `src/gzkit/ledger/events.py` (event type), manpages under `docs/user/manpages/gz-storybook*`, tests under `tests/storybook/` and `tests/cli/`
- Tests added: deriver invariants, atomic write, marker inviolability, missing-anchor error, ledger event shape
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
