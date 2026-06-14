---
id: OBPI-0.0.37-21-authoring-time-compression-composer-tool-skill
parent: ADR-0.0.37-constitutional-invariant-composition
item: 21
lane: Heavy
status: Draft
# req_atomic: each REQ is a single indivisible labor unit — one behavior/support
# surface apiece (emit, determinism, invariant-verbatim, fail-closed, no-rendered-
# write, ledger event, skill, docs); none decomposes into parallel seq=02+ sub-tasks
# (ADR-0.0.64 task-envelope exemption).
req_atomic:
  - REQ-0.0.37-21-01
  - REQ-0.0.37-21-02
  - REQ-0.0.37-21-03
  - REQ-0.0.37-21-04
  - REQ-0.0.37-21-05
  - REQ-0.0.37-21-06
  - REQ-0.0.37-21-07
  - REQ-0.0.37-21-08
---

# OBPI-0.0.37-21-authoring-time-compression-composer-tool-skill: Authoring-Time Compression Composer Tool + Skill

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
<!-- gz-validate-skip: command-shape -->
- **Checklist Item:** #21 - "OBPI-0.0.37-21 — Authoring-time compression composer tool + skill (LLM compresses compressible-tier corpus toward the setpoint — drop/combine/rewrite; emits candidate rendition + per-tier byte evidence; wielded by a compose skill; NO LLM in the render path)"

**Status:** Draft

## Objective

<!-- gz-validate-skip: command-shape -->
Deliver the **compress** stage of the re-aligned CMS pipeline (`corpus → compress → rendition → playback`): a `content compose <surface> [--consumer <vendor>]` subcommand on the existing `gz content` group, plus the `gz-content-compose` skill that wields it. The composer reads the append-only corpus store (OBPI-19) for a surface, partitions entries by tier, resolves the declared compression setpoint (OBPI-20 `temperature_for`), and produces a **candidate rendition artifact** together with **per-tier byte evidence** (invariant bytes, compressible bytes before→after, total vs setpoint target).

The compression judgment — drop / combine / rewrite of `compressible`-tier content toward the setpoint, maximizing information retained per byte reduced — is performed by the **agent wielding the skill**, never by an in-code LLM call. The **tool is deterministic**: it assembles the compose input packet, validates the candidate against the corpus (invariant-tier verbatim preservation), computes byte evidence, writes the candidate artifact, and emits a ledger event. This is the load-bearing anti-vibing seam (parent ADR Alternative #11/#16): the non-deterministic step happens at authoring time; the render path (OBPI-22 playback) carries NO LLM. The candidate is graded by the advisor-QC loop (OBPI-24) and operator-attested before promotion to a committed rendition (OBPI-22).

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

A new `content compose` subcommand + a new ledger event + a new skill are runtime-contract additions → Heavy. Gate 5 human attestation is mandatory (foundation/heavy; no self-close).

## Allowed Paths

- `src/gzkit/commands/content/compose.py` **CREATE** — the `compose` subcommand handler (sibling to `remember.py`, `import_.py`, `render.py`; `content_compose_cmd(*, ...)`, exit 0/1/2)
- `src/gzkit/commands/content/__init__.py` — EDIT: register `_register_compose` in `register_content_parsers`
- `src/gzkit/content/composer.py` **CREATE** — deterministic compose engine: partition corpus by tier, resolve setpoint, compute per-tier byte evidence, assemble/validate the candidate rendition (NO LLM; pure stdlib + Pydantic)
- `src/gzkit/content/rendition.py` **CREATE** — the candidate-rendition value model (Pydantic, frozen) + candidate staging path helper (`.gzkit/renditions/<surface>/<consumer>.candidate.md`); the committed-store + playback half is OBPI-22 (boundary note in § Tracked Defects)
- `src/gzkit/events.py` — EDIT: add the typed `CompositionCandidateEmittedEvent` read-path model + register it in the `TypedLedgerEvent` union (sibling to `CompositionRenderedEvent`, `CorpusEntryAppendedEvent`)
- `src/gzkit/ledger_events.py` — EDIT: add the `composition_candidate_emitted_event(...)` write-path factory (sibling to `composition_rendered_event`)
- `src/gzkit/schemas/ledger.json` — EDIT: register the `composition_candidate_emitted` event type with its required-fields schema (the REAL registry `gz validate --ledger` reads — see OBPI-19 Tracked Defects)
- `src/gzkit/governance/trust_audits/events.py` — EDIT: `_NO_GRAPH_IMPACT` waiver for `composition_candidate_emitted` (Layer-2 authoring witness, no artifact-graph edge)
- `.gzkit/skills/gz-content-compose/SKILL.md` **CREATE** — the compose skill that wields the tool (canonical edit surface; the LLM-compression judgment surface)
- `tests/commands/test_content_compose.py` **CREATE** — command-level BEHAVIOR tests (`@covers`)
- `tests/content/test_composer.py` **CREATE** — engine-level BEHAVIOR tests (`@covers`)
- `tests/test_schemas.py` — EDIT: add the `composition_candidate_emitted` entry to `_EVENT_MODELS` (schema↔model alignment)
- `tests/content/test_tui_affordances.py` — EDIT: admit `compose` in the content-subcommand fence (named, not silently relaxed)
- `config/doc-coverage.json` — EDIT: declare `content compose` (manpage:false, matching sibling content subcommands covered by the group `content.md`)
- `docs/user/manpages/content.md` — EDIT: add a `### compose` subsection with a real EXAMPLES block
- `docs/user/runbook.md` — EDIT: operator runbook entry for the compose flow
- `docs/user/skills/gz-content-compose.md` **CREATE** — skill manpage
- `docs/user/skills/index.md` — EDIT: link the new skill manpage
- `.gzkit/skills/gz-context/SKILL.md` — EDIT: route `gz-content-compose` under the gz-context router (version bump per skill-surface-sync)
- `data/distribution_baseline_manifest.json` — EDIT: regenerate to include the new canonical skill (ADR-0.0.31)
- `features/content_compose.feature` **CREATE** — Heavy-lane BDD scenarios tagged `@REQ-0.0.37-21-*`
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-21-authoring-time-compression-composer-tool-skill.md` — active brief and evidence record
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md` — parent ADR (read-only, for intent and the 1:1 checklist sync)

## Denied Paths

- Paths not listed in Allowed Paths
- `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, and every rendered/spliced control surface — the composer MUST NOT write a rendered surface (the load-bearing invariant: NO LLM in the render path)
- `src/gzkit/content/models/corpus.py` — the OBPI-18 corpus MODEL is consumed read-only, never modified here
- `src/gzkit/content/vendors.py` — the OBPI-20 setpoint accessor (`temperature_for`) is consumed read-only
- `src/gzkit/sync_surfaces.py`, the committed-rendition store, and deterministic playback — that is OBPI-22 scope
- `.gzkit/ledger.jsonl` — never hand-edited; events are emitted via the CLI's ledger writer
- Any Anthropic / LLM SDK or network client in tool code — the tool is deterministic; the LLM surface is the skill (stdlib-first, no dependency departure)
- New runtime dependencies; CI files; lockfiles

## Creates These Files

Net-new paths this OBPI creates (exempt from the brief-path existence gate per GHI #419; they exist in contract before they exist on disk):

- `src/gzkit/commands/content/compose.py`
- `src/gzkit/content/composer.py`
- `src/gzkit/content/rendition.py`
- `.gzkit/skills/gz-content-compose/SKILL.md`
- `tests/commands/test_content_compose.py`
- `tests/content/test_composer.py`
- `docs/user/skills/gz-content-compose.md`
- `features/content_compose.feature`
- `.gzkit/renditions/<surface>/<consumer>.candidate.md` (candidate staging artifact, created at first compose run)

All other Allowed Paths reference existing files modified in place.

**Sync-generated mirrors (written by `gz agent sync control-surfaces`, not hand-edited):** `src/gzkit/skills/gz-content-compose/SKILL.md`, `.claude/skills/gz-content-compose/SKILL.md`, `.github/skills/gz-content-compose/SKILL.md`, `.agents/skills/gz-content-compose/SKILL.md` — propagated from the canonical `.gzkit/skills/` source per `.gzkit/rules/skill-surface-sync.md`.

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: [BEHAVIOR] The `compose` subcommand of `gz content` (`content compose <surface> [--consumer <vendor>]`) MUST read the append-only corpus for `<surface>` (`.gzkit/corpus/<surface>.jsonl`), partition entries by `tier`, resolve the declared setpoint via `temperature_for(<surface-content-type>, <consumer>)`, and emit (a) a candidate rendition artifact and (b) a per-tier byte-evidence report carrying invariant-tier bytes, compressible-tier bytes (before and after), total bytes, and the setpoint target — exiting 0 on success.
1. REQUIREMENT: [BEHAVIOR] The composer tool MUST be deterministic — it performs NO LLM call and NO network I/O; given identical corpus + setpoint + candidate inputs it produces identical byte-evidence output. The drop/combine/rewrite compression judgment is supplied by the wielding skill (the agent), never by the tool.
1. REQUIREMENT: [BEHAVIOR] `tier: invariant` entries MUST appear verbatim in the candidate rendition at every setpoint; the composer MUST refuse (fail closed) any candidate in which an invariant-tier entry's text is dropped, combined, or rewritten (the 0-Kelvin floor; presence enforcement deepened by OBPI-23).
1. REQUIREMENT: [BEHAVIOR] The composer MUST fail closed (non-zero exit, no candidate written) when `<surface>` has no corpus store, when the `(surface, consumer)` setpoint is undeclared (`temperature_for` raises `ValueError`), or when an offered candidate violates invariant-tier verbatim preservation. (`content compose` is the invoked verb.)
1. REQUIREMENT: [BEHAVIOR] The composer MUST NOT modify any rendered surface — after a compose run, `AGENTS.md`, `CLAUDE.md`, and all mirrors are byte-unchanged; only the candidate rendition artifact under `.gzkit/renditions/` and the ledger are written.
1. REQUIREMENT: [SUPPORT] A successful compose MUST emit a `composition_candidate_emitted` ledger event carrying at least `surface`, `consumer`, `setpoint`, and the per-tier byte counts — proven by `uv run gz validate --ledger` plus the emitted `composition_candidate_emitted` event.
1. REQUIREMENT: [SUPPORT] The compose skill MUST exist at `.gzkit/skills/gz-content-compose/SKILL.md` and propagate byte-equal to its mirrors — proven by `uv run gz validate --surfaces` plus the `artifact_edited` event for the skill.
1. REQUIREMENT: [SUPPORT] The `compose` verb MUST be documented in `docs/user/manpages/content.md` and `docs/user/runbook.md`, and the reference MUST resolve — proven by `uv run gz validate --documents` plus the `artifact_edited` event for the doc surfaces.
1. NEVER: Add an Anthropic/LLM SDK or network client to tool code, write a rendered surface, edit the corpus MODEL, or hand-edit the ledger.
1. ALWAYS: Reconcile the brief with the parent ADR (`uv run gz validate --brief-reconcile`) before implementation begins.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

<!-- gz-validate-skip: command-shape -->
- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The contract: "Authoring-time compression composer tool + skill (LLM compresses compressible-tier corpus toward the setpoint — drop/combine/rewrite; emits candidate rendition + per-tier byte evidence; wielded by a compose skill; NO LLM in the render path)" (Checklist item #21; § Decision Re-Alignment 2026-06-03, point 3 "Authoring-time compression composer").
- [ ] Parent ADR § Decision Re-Alignment points 3 + 4 + 5 — the compress → rendition step, the "NO LLM in the render path" determinism seam, and the invariant-tier 0-Kelvin floor.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § STDLIB-FIRST DOCTRINE — the binding rationale for keeping the LLM out of tool code (no dependency departure for an Anthropic SDK)
- [ ] `.gzkit/rules/skill-surface-sync.md` — canonical-edit-then-sync discipline for the new skill
- [ ] `.gzkit/rules/cli.md` — exit-code map and new-subcommand (Heavy) requirements

**Context:**

- [ ] OBPI-0.0.37-19 (corpus capture) — the `.gzkit/corpus/AGENTS.md.jsonl` store layout + `corpus_store.load_corpus` API this composer reads
- [ ] OBPI-0.0.37-20 (setpoint) — `temperature_for` accessor + `SETPOINT_TOKENS` the composer drives toward
- [ ] OBPI-0.0.37-22 (committed rendition + playback) — the consumer of this OBPI's candidate; the candidate→committed boundary (§ Tracked Defects)
- [ ] OBPI-0.0.37-23 (invariant tier) + OBPI-0.0.37-24 (advisor-QC) — the verbatim-floor deepening and the candidate grader

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/content/corpus_store.py` exists with `load_corpus(root, surface)` / `corpus_path` (OBPI-19, attested-complete)
- [ ] `src/gzkit/content/models/corpus.py` exists with `CorpusEntry` (`tier`, `classification`, `text`, `section`) and `Corpus` (OBPI-18, attested-complete)
- [ ] `src/gzkit/content/vendors.py` exists with `temperature_for(...)` fail-closed accessor + `SETPOINT_TOKENS` (OBPI-20, attested-complete)
- [ ] `src/gzkit/commands/content/__init__.py` exists with `register_content_parsers` + a `content_command` subparsers action
- [ ] `.gzkit/corpus/AGENTS.md.jsonl` exists (OBPI-19 store seed)

**Existing Code (understand current state):**

- [ ] `src/gzkit/commands/content/remember.py` — the closest sibling command (arg parsing, `get_project_root`, exit codes, fail-closed-before-write discipline, ledger emission)
- [ ] `src/gzkit/commands/content/__init__.py` `_register_remember` — the `_register_<verb>` + `set_defaults(func=lambda a: _content(...))` pattern to mirror for `_register_compose`
- [ ] `src/gzkit/events.py` `CompositionRenderedEvent` / `CorpusEntryAppendedEvent` — the `_EventBase` + `Literal[...]` pattern for `CompositionCandidateEmittedEvent`
- [ ] `src/gzkit/ledger_events.py` `composition_rendered_event` — the factory shape to mirror
- [ ] `src/gzkit/schemas/ledger.json` `corpus_entry_appended` entry — the `events.<name>` required-fields shape
- [ ] `.gzkit/skills/gz-content-remember/SKILL.md` — the tool+skill split the compose skill follows (frontmatter `gz_command`, workflow, Output Contract)
- [ ] `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/renditions/agentcontract-codex-root-interim.md` — the OBPI-26 interim rendition; the candidate-rendition format reference

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
- [ ] `docs/user/manpages/content.md` + `docs/user/runbook.md` updated; `gz validate --cli-alignment` resolves the verb

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave --tags=@REQ-0.0.37-21-01,@REQ-0.0.37-21-02,@REQ-0.0.37-21-03,@REQ-0.0.37-21-04,@REQ-0.0.37-21-05 features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded (mandatory; foundation/heavy; no self-close)

## Verification

```bash
uv run gz validate --brief-reconcile
uv run gz validate --documents
uv run gz validate --ledger
uv run gz validate --surfaces
uv run gz validate --cli-alignment
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

# Specific verification for this OBPI
test -f src/gzkit/commands/content/compose.py
test -f src/gzkit/content/composer.py
test -f .gzkit/skills/gz-content-compose/SKILL.md
uv run -m unittest tests.commands.test_content_compose -v
uv run -m unittest tests.content.test_composer -v
uv run -m behave features/content_compose.feature
```

## Demo

<!-- gz-validate-skip: command-shape -->
```bash
# Compose a candidate rendition for the AGENTS.md corpus toward the Codex setpoint
uv run gz content compose AGENTS.md --consumer codex

# The candidate landed in the rendition staging area, not the rendered surface
test -s .gzkit/renditions/AGENTS.md/codex.candidate.md

# AGENTS.md itself is byte-unchanged (NO LLM in the render path)
git diff --exit-code AGENTS.md

# The compose is witnessed in the ledger with per-tier byte evidence
uv run gz ledger tail --event composition_candidate_emitted
```

## Acceptance Criteria

- [ ] REQ-0.0.37-21-01 [BEHAVIOR]: Given a surface with a populated corpus and a declared setpoint, when the `compose` subcommand runs (`content compose <surface> [--consumer <vendor>]`), then it emits a candidate rendition artifact plus a per-tier byte-evidence report (invariant bytes, compressible bytes before/after, total, setpoint target) and exits 0. Proof: `@covers`-decorated test in `tests/commands/test_content_compose.py`.
- [ ] REQ-0.0.37-21-02 [BEHAVIOR]: Given identical corpus + setpoint + candidate inputs, when the composer engine runs twice, then the byte-evidence output is byte-identical and no network/LLM call is made (the tool is deterministic; compression judgment is the skill's). Proof: `@covers`-decorated determinism test in `tests/content/test_composer.py`.
- [ ] REQ-0.0.37-21-03 [BEHAVIOR]: Given a corpus containing `tier: invariant` entries, when the composer emits the candidate at the leanest setpoint, then every invariant-tier entry's text appears verbatim; a candidate dropping/rewriting an invariant entry is refused. Proof: `@covers`-decorated test.
- [ ] REQ-0.0.37-21-04 [BEHAVIOR]: Given an absent corpus, an undeclared `(surface, consumer)` setpoint, or an invariant-floor-violating candidate, when the `compose` subcommand runs, then it fails closed (non-zero exit) and writes no candidate. Proof: `@covers`-decorated test.
- [ ] REQ-0.0.37-21-05 [BEHAVIOR]: Given any successful compose, when it completes, then no rendered surface (`AGENTS.md`, `CLAUDE.md`, mirrors) is modified — only the candidate rendition artifact and ledger change. Proof: `@covers`-decorated byte-unchanged test.
- [ ] REQ-0.0.37-21-06 [SUPPORT]: Given the ledger schema, when the OBPI is complete, then `composition_candidate_emitted` is registered in `src/gzkit/schemas/ledger.json` and emitted on a successful compose — proven by `uv run gz validate --ledger` plus the `composition_candidate_emitted` event.
- [ ] REQ-0.0.37-21-07 [SUPPORT]: Given the skill surface, when the OBPI is complete, then `.gzkit/skills/gz-content-compose/SKILL.md` exists and mirrors are byte-equal — proven by `uv run gz validate --surfaces` plus the `artifact_edited` event for the skill.
- [ ] REQ-0.0.37-21-08 [SUPPORT]: Given the operator docs, when the OBPI is complete, then `docs/user/manpages/content.md` and `docs/user/runbook.md` document the verb and the reference resolves — proven by `uv run gz validate --documents` plus the `artifact_edited` event for the docs.

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

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- REQ-count drift: 0 declared vs 8 acceptance criteria (brief reconcile, attestor g0)

- REQ-count drift: 0 declared vs 8 acceptance criteria (brief reconcile, attestor g0)

**Candidate ↔ committed boundary (21 ↔ 22), flagged for operator confirmation at Gate 5:** This OBPI emits a *candidate* rendition (`<consumer>.candidate.md`) — an authoring artifact the advisor-QC loop (OBPI-24) grades and the operator attests. The *committed* rendition (`<consumer>.md`), the durable store, and deterministic playback are OBPI-22 scope. The promotion candidate→committed happens at operator attestation. If implementation reveals the staging path or model belongs more naturally in OBPI-22, surface it at Stage 1 brief-reconcile rather than silently shifting scope.

_No further defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
