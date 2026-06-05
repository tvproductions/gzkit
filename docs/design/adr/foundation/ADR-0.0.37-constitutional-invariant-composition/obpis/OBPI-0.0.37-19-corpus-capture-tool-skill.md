---
id: OBPI-0.0.37-19-corpus-capture-tool-skill
parent: ADR-0.0.37-constitutional-invariant-composition
item: 19
lane: Heavy
status: Draft
---

# OBPI-0.0.37-19-corpus-capture-tool-skill: Corpus Capture Tool Skill

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
<!-- gz-validate-skip: command-shape -->
- **Checklist Item:** #19 - "OBPI-0.0.37-19 — Corpus capture tool + skill (`gz content remember <surface> --section <id> [--tier]` tool appends an entry + `corpus_entry_appended` ledger event, never edits a rendered surface; wielding capture skill; replaces prior OBPI-12 renderer)"

**Status:** Draft

## Objective

<!-- gz-validate-skip: command-shape -->
Deliver the **corpus capture tool + wielding skill**: a `gz content remember <surface> --section <id> --text <text> [--tier invariant|compressible]` subcommand on the existing `gz content` group that appends an addressed, provenanced `CorpusEntry` (OBPI-18 model) to the append-only per-surface corpus store at `.gzkit/corpus/<surface>.jsonl`, emits a `corpus_entry_appended` ledger event, and **never edits a rendered surface** (AGENTS.md, CLAUDE.md, or any mirror). This is the write-path half of the ADR-0.0.37 § Decision Re-Alignment pipeline (`corpus → compress → rendition → playback`): capture appends to the source of truth; deterministic playback (OBPI-22) remains the sole writer of rendered surfaces. Replaces the prior OBPI-12 renderer path.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/commands/content/remember.py` **CREATE** — the `remember` subcommand implementation (sibling to `import_.py`, `list.py`, `render.py`, `edit.py`, `show.py`)
- `src/gzkit/commands/content/__init__.py` — EDIT: register the `remember` subparser in `register_content_parsers`
- `src/gzkit/content/corpus_store.py` **CREATE** — append-only per-surface corpus persistence (load/append/save `.gzkit/corpus/<surface>.jsonl`); consumes the OBPI-18 `CorpusEntry`/`Corpus` model read-only
- `src/gzkit/events.py` — EDIT: add the `CorpusEntryAppendedEvent` factory (sibling to `ArtifactEditedEvent`, `ObpiCreatedEvent`)
- `.gzkit/schemas/ledger_events.json` — EDIT: register the `corpus_entry_appended` event type with its required-fields schema
- `.gzkit/skills/gz-content-remember/SKILL.md` **CREATE** — the capture skill that wields the tool (canonical edit surface)
- `tests/commands/test_content_remember.py` **CREATE** — command-level BEHAVIOR tests (`@covers`)
- `tests/content/test_corpus_store.py` **CREATE** — store-level BEHAVIOR tests (`@covers`)
- `docs/user/manpages/gz-content.md` **CREATE** — manpage for the `gz content` group documenting the `remember` verb with a real EXAMPLES block
- `docs/user/runbook.md` — EDIT: operator runbook entry for the capture flow
- `features/content_remember.feature` **CREATE** — Heavy-lane BDD scenario tagged `@REQ-0.0.37-19-*`
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-19-corpus-capture-tool-skill.md` — active brief and evidence record
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md` — parent ADR (read-only, for intent and the 1:1 checklist sync)

**Sync-generated mirrors (written by `gz agent sync control-surfaces`, not hand-edited):** `src/gzkit/skills/gz-content-remember/SKILL.md`, `.claude/skills/gz-content-remember/SKILL.md`, `.github/skills/gz-content-remember/SKILL.md`, `.agents/skills/gz-content-remember/SKILL.md` — these are propagated from the canonical `.gzkit/skills/` source per `.gzkit/rules/skill-surface-sync.md`; the sync run is a ceremony step, not a manual edit.

## Denied Paths

- Paths not listed in Allowed Paths
- `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, and every rendered/spliced control surface — capture MUST NOT write any rendered surface (the load-bearing invariant of this OBPI)
- `src/gzkit/content/models/corpus.py` — the OBPI-18 corpus MODEL is consumed, never modified here
- `src/gzkit/render/**`, `src/gzkit/sync_surfaces.py` — the render/playback path is OBPI-22 scope
- `.gzkit/ledger.jsonl` — never hand-edited; events are emitted via the CLI's ledger writer
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT [BEHAVIOR]: The `remember` subcommand of `gz content` (invoked as `content remember <surface> --section <id> --text <text> [--tier]`) MUST append exactly one `CorpusEntry` to `.gzkit/corpus/<surface>.jsonl` (creating the file/dir on first use) and exit 0, with the appended entry carrying populated `id`, `surface`, `section`, `tier`, `classification`, `text`, `origin`, and `ts` fields.
2. REQUIREMENT [BEHAVIOR]: The command MUST NOT modify any rendered surface — after a successful `remember`, `AGENTS.md`, `CLAUDE.md`, and all skill/rule mirrors are byte-unchanged; only `.gzkit/corpus/<surface>.jsonl` is written.
3. REQUIREMENT [BEHAVIOR]: A successful append MUST emit a `corpus_entry_appended` ledger event carrying at least `surface`, `section`, `entry_id`, and `tier`.
4. REQUIREMENT [BEHAVIOR]: The command MUST fail closed (non-zero exit, no append) when `<surface>` is unknown or `--section <id>` does not resolve to a real template-defined section of that surface's `AgentContract` — an unaddressable entry is never written.
5. REQUIREMENT [SUPPORT]: The `corpus_entry_appended` event type MUST be registered in `.gzkit/schemas/ledger_events.json` with its required-fields schema — proven by `uv run gz validate --ledger` plus the `corpus_entry_appended` ledger event emitted by the command.
6. REQUIREMENT [SUPPORT]: The capture skill MUST exist at `.gzkit/skills/gz-content-remember/SKILL.md` and propagate byte-equal to its mirrors — proven by `uv run gz validate --surfaces` plus the `artifact_edited` event accounting for the skill.
7. REQUIREMENT [SUPPORT]: The `remember` verb (on `gz content`) MUST be documented in `docs/user/manpages/gz-content.md` and `docs/user/runbook.md` — proven by `uv run gz validate --documents` plus the `artifact_edited` event accounting for the doc surfaces.
8. NEVER: Write to a rendered surface, the corpus MODEL (`corpus.py`), the ledger file directly, or any path outside Allowed Paths.
9. ALWAYS: Reconcile the brief with the parent ADR (`uv run gz validate --brief-reconcile`) before implementation begins.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

<!-- gz-validate-skip: command-shape -->
- [ ] **Parent ADR § Decision Re-Alignment item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The contract: "Corpus capture tool + skill (`gz content remember <surface> --section <id> [--tier]` tool appends an entry + `corpus_entry_appended` ledger event, never edits a rendered surface; wielding capture skill; replaces prior OBPI-12 renderer)" (Checklist item #19; § Decision Re-Alignment 2026-06-03, point 1 "Append-only corpus").
- [ ] Parent ADR § Decision Re-Alignment point 1 (Append-only corpus) — the addressed-entry shape `id, surface, section, anchor?, tier (invariant|compressible), classification, witness?, text, origin, ts` and the "nothing is hand-edited at the rendered location" binding claim.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/skill-surface-sync.md` — the canonical-edit-then-sync discipline for the new skill
- [ ] `AGENTS.md` § STDLIB-FIRST + § OBPI Acceptance Protocol — stdlib JSONL I/O; universal Gate 5

**Context:**

- [ ] OBPI-0.0.37-18 (append-only corpus model) — the `CorpusEntry`/`Corpus` API this tool consumes
- [ ] OBPI-0.0.37-20/21/22 briefs — the setpoint/composer/playback consumers that inherit the `.gzkit/corpus/<surface>.jsonl` store layout

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/content/models/corpus.py` exists with `CorpusEntry`, `Corpus`, `Corpus.append`, `Corpus.validate_against` (OBPI-18, attested-complete)
- [ ] `src/gzkit/commands/content/__init__.py` exists with `register_content_parsers` and a `content_command` subparsers action
- [ ] `src/gzkit/events.py` exists with `_EventBase` and the established event-factory pattern
- [ ] `.gzkit/schemas/ledger_events.json` exists with an `event_types` list

**Existing Code (understand current state):**

- [ ] `src/gzkit/commands/content/import_.py` + `edit.py` — local convention for a `gz content` subcommand (arg parsing, project-root resolution, exit codes)
- [ ] `src/gzkit/content/models/corpus.py` — `CorpusEntry` fields and `Corpus.append`/`dumps`/`loads`/`validate_against` signatures before writing the store
- [ ] `src/gzkit/events.py` `ArtifactEditedEvent` / `ObpiCreatedEvent` — the `_EventBase` subclass + `Literal["..."]` pattern to mirror for `CorpusEntryAppendedEvent`
- [ ] `.gzkit/schemas/ledger_events.json` `composition_rendered` entry — the `event_types` list shape (`id`, `name`, `schema.required`, `required_fields`) to mirror

## Quality Gates

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

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] `docs/user/manpages/gz-content.md` + `docs/user/runbook.md` updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave --tags=@REQ-0.0.37-19-01,@REQ-0.0.37-19-02,@REQ-0.0.37-19-03,@REQ-0.0.37-19-04 features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --brief-reconcile
uv run gz validate --documents
uv run gz validate --ledger
uv run gz validate --surfaces
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -f src/gzkit/commands/content/remember.py
test -f src/gzkit/content/corpus_store.py
test -f .gzkit/skills/gz-content-remember/SKILL.md
uv run -m unittest tests.commands.test_content_remember -v
uv run -m unittest tests.content.test_corpus_store -v
```

## Demo

<!-- gz-validate-skip: command-shape -->
```bash
# Forward-reference demo (gz content remember lands in this OBPI; verb not yet registered)
# Capture a compressible entry into the AGENTS.md corpus (never touches AGENTS.md itself)
uv run gz content remember AGENTS.md --section "Behavior Rules" --text "Prefer stdlib JSONL for append-only stores." --tier compressible

# The append landed in the corpus store, not the rendered surface
test -s .gzkit/corpus/AGENTS.md.jsonl

# The append is witnessed in the ledger
uv run gz ledger tail --event corpus_entry_appended
```

## Acceptance Criteria

- [ ] REQ-0.0.37-19-01 [BEHAVIOR]: Given a known surface and a template-resolvable section, when the `remember` subcommand of `gz content` runs (`content remember <surface> --section <id> --text <text> [--tier]`), then exactly one `CorpusEntry` is appended to `.gzkit/corpus/<surface>.jsonl` with all addressed/provenanced fields populated and the command exits 0.
- [ ] REQ-0.0.37-19-02 [BEHAVIOR]: Given any successful `remember`, when it completes, then no rendered surface (`AGENTS.md`, `CLAUDE.md`, mirrors) is modified — only the corpus store file changes.
- [ ] REQ-0.0.37-19-03 [BEHAVIOR]: Given a successful append, when it completes, then a `corpus_entry_appended` ledger event is emitted carrying `surface`, `section`, `entry_id`, and `tier`.
- [ ] REQ-0.0.37-19-04 [BEHAVIOR]: Given an unknown surface or a section that does not resolve to a real template-defined section, when `remember` runs, then it fails closed (non-zero exit) and writes no entry.
- [ ] REQ-0.0.37-19-05 [SUPPORT]: Given the ledger schema, when the OBPI is complete, then `corpus_entry_appended` is registered in `.gzkit/schemas/ledger_events.json` — proven by `uv run gz validate --ledger` plus the `corpus_entry_appended` event.
- [ ] REQ-0.0.37-19-06 [SUPPORT]: Given the skill surface, when the OBPI is complete, then `.gzkit/skills/gz-content-remember/SKILL.md` exists and mirrors are byte-equal — proven by `uv run gz validate --surfaces` plus the `artifact_edited` event for the skill.
- [ ] REQ-0.0.37-19-07 [SUPPORT]: Given the operator docs, when the OBPI is complete, then `docs/user/manpages/gz-content.md` and `docs/user/runbook.md` document the verb — proven by `uv run gz validate --documents` plus the `artifact_edited` event for the docs.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

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

<!-- One concrete usage example, command, or before/after behavior. -->

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

**Date Completed:** -

**Evidence Hash:** -
