# Plan: OBPI-0.0.37-21 — Authoring-Time Compression Composer Tool + Skill

**OBPI:** OBPI-0.0.37-21-authoring-time-compression-composer-tool-skill
**Parent ADR:** ADR-0.0.37-constitutional-invariant-composition
**Lane:** Heavy | **Kind:** Foundation

## Context

This plan delivers the **compress** stage of the CMS pipeline
(`corpus → compress → rendition → playback`). The key invariant:
- The **tool is deterministic** — no LLM, no network I/O
- The **skill** is the LLM surface — the agent wielding the skill supplies
  the drop/combine/rewrite judgment on the compressible-tier corpus
- The candidate rendition lives in `.gzkit/renditions/<surface>/<consumer>.candidate.md`
- No rendered surface (AGENTS.md, CLAUDE.md, mirrors) is ever written

Pattern: mirror `remember.py` / `_register_remember` for command shape;
mirror `CompositionRenderedEvent` / `composition_rendered_event` for event shape.

## Files

**Created:**
- `src/gzkit/commands/content/compose.py`
- `src/gzkit/content/composer.py`
- `src/gzkit/content/rendition.py`
- `.gzkit/skills/gz-content-compose/SKILL.md`
- `tests/commands/test_content_compose.py`
- `tests/content/test_composer.py`
- `docs/user/skills/gz-content-compose.md`
- `features/content_compose.feature`

**Modified:**
- `src/gzkit/commands/content/__init__.py` — register `_register_compose`
- `src/gzkit/events.py` — add `CompositionCandidateEmittedEvent`
- `src/gzkit/ledger_events.py` — add `composition_candidate_emitted_event`
- `src/gzkit/schemas/ledger.json` — register event type
- `src/gzkit/governance/trust_audits/events.py` — `_NO_GRAPH_IMPACT` waiver
- `tests/test_schemas.py` — add `composition_candidate_emitted` to `_EVENT_MODELS`
- `tests/content/test_tui_affordances.py` — admit `compose` in content-subcommand fence
- `config/doc-coverage.json` — declare `content compose`
- `docs/user/manpages/content.md` — add `### compose` subsection
- `docs/user/runbook.md` — operator runbook entry
- `docs/user/skills/index.md` — link new skill manpage
- `.gzkit/skills/gz-context/SKILL.md` — route gz-content-compose
- `data/distribution_baseline_manifest.json` — regenerate

## Steps

### Step 1: Read sibling sources + TDD RED — author test stubs

Read these before writing tests:
- `src/gzkit/events.py` — `CompositionRenderedEvent` / `CorpusEntryAppendedEvent` patterns
- `src/gzkit/ledger_events.py` — factory shape
- `src/gzkit/schemas/ledger.json` — `corpus_entry_appended` entry shape
- `src/gzkit/content/corpus_store.py` — `load_corpus` API
- `src/gzkit/content/models/corpus.py` — `CorpusEntry`, `Corpus` models
- `src/gzkit/content/vendors.py` — `temperature_for`, `SETPOINT_TOKENS`

Then author the test stubs (REQ-derived, RED first):

**`tests/commands/test_content_compose.py`** — 5 behavior tests:
- `TestContentComposeCmd.test_compose_produces_candidate_and_byte_evidence`
  → @covers REQ-0.0.37-21-01 — success path, candidate written + byte evidence
- `TestContentComposeCmd.test_compose_exits_nonzero_on_absent_corpus`
  → @covers REQ-0.0.37-21-04 — absent corpus → exit 1, no candidate
- `TestContentComposeCmd.test_compose_exits_nonzero_on_undeclared_setpoint`
  → @covers REQ-0.0.37-21-04 — undeclared (surface, consumer) → exit 1
- `TestContentComposeCmd.test_compose_refuses_invariant_floor_violation`
  → @covers REQ-0.0.37-21-03 and REQ-0.0.37-21-04 — candidate drops invariant → exit 1
- `TestContentComposeCmd.test_compose_does_not_modify_rendered_surfaces`
  → @covers REQ-0.0.37-21-05 — byte-unchanged check on AGENTS.md, CLAUDE.md

**`tests/content/test_composer.py`** — 2 behavior tests:
- `TestComposerEngine.test_deterministic_output`
  → @covers REQ-0.0.37-21-02 — identical inputs → identical byte evidence, no network call
- `TestComposerEngine.test_invariant_tier_verbatim_presence`
  → @covers REQ-0.0.37-21-03 — invariant-tier entries present verbatim in candidate

### Step 2: Create `src/gzkit/content/rendition.py`

Pydantic models (frozen, extra=forbid):
```python
class ByteEvidence(BaseModel):
    invariant_bytes: int
    compressible_bytes_before: int
    compressible_bytes_after: int
    total_bytes: int
    setpoint_bytes: int

class CandidateRendition(BaseModel):
    surface: str
    consumer: str
    setpoint_bytes: int
    candidate_text: str
    byte_evidence: ByteEvidence
```

Staging path helper:
```python
def candidate_path(root: Path, surface: str, consumer: str) -> Path:
    # .gzkit/renditions/<surface>/<consumer>.candidate.md
    return root / ".gzkit" / "renditions" / surface / f"{consumer}.candidate.md"
```

### Step 3: Create `src/gzkit/content/composer.py`

Deterministic compose engine (no LLM, no network):
```python
def compose(
    root: Path,
    surface: str,
    consumer: str,
    candidate_text: str,
) -> CandidateRendition:
    """
    - Load corpus via corpus_store.load_corpus(root, surface)
    - Resolve setpoint via temperature_for(surface_content_type, consumer)
      (raises ValueError when undeclared → caller maps to exit 1)
    - Partition entries by tier (invariant vs compressible)
    - Compute byte evidence (invariant bytes, compressible bytes before/after from candidate)
    - Validate invariant-tier verbatim presence in candidate_text
      (raises ValueError when violated → caller maps to exit 1)
    - Return CandidateRendition (does NOT write — caller writes)
    """
```

Also: `load_corpus` raises `FileNotFoundError` when no corpus store exists → caller maps to exit 1.

### Step 4: Create `src/gzkit/commands/content/compose.py` + register it

**compose.py** (mirror remember.py pattern):
```python
def content_compose_cmd(*, surface: str, consumer: str) -> None:
    root = get_project_root()
    # 1. load_corpus → exit 1 if FileNotFoundError
    # 2. temperature_for → exit 1 if ValueError (undeclared setpoint)
    # 3. Read candidate_text from stdin or accept as param (operator supplies the LLM output)
    # 4. compose() → exit 1 if ValueError (invariant-floor violation)
    # 5. Write candidate to candidate_path(root, surface, consumer) — only this path written
    # 6. Emit composition_candidate_emitted ledger event
    # 7. Print byte evidence to stdout (or TTY status line)
```

Note: The operator (agent wielding the skill) provides the candidate_text via
`--candidate` flag (path to a candidate file) or stdin. The tool validates; it
does not generate.

**__init__.py** — add `_register_compose` call in `register_content_parsers`,
following `_register_remember` pattern.

### Step 5: Wire events and ledger schema

**`src/gzkit/events.py`** — add after `CorpusEntryAppendedEvent`:
```python
class CompositionCandidateEmittedEvent(BaseModel):
    event_type: Literal["composition_candidate_emitted"]
    surface: str
    consumer: str
    setpoint_bytes: int
    invariant_bytes: int
    compressible_bytes_before: int
    compressible_bytes_after: int
    total_bytes: int
```
Register in `TypedLedgerEvent` union.

**`src/gzkit/ledger_events.py`** — add `composition_candidate_emitted_event(...)` factory
(mirror `composition_rendered_event` shape).

**`src/gzkit/schemas/ledger.json`** — add `composition_candidate_emitted` entry
with required fields: `surface`, `consumer`, `setpoint_bytes`, `invariant_bytes`,
`compressible_bytes_before`, `compressible_bytes_after`, `total_bytes`.

**`src/gzkit/governance/trust_audits/events.py`** — add `composition_candidate_emitted`
to the `_NO_GRAPH_IMPACT` set (Layer-2 authoring witness, no artifact-graph edge).

### Step 6: Fix test coverage surfaces

**`tests/test_schemas.py`** — add `"composition_candidate_emitted"` entry to `_EVENT_MODELS`
dict (same shape as sibling entries).

**`tests/content/test_tui_affordances.py`** — find the content-subcommand fence
(the test that lists valid `content` subcommands) and add `"compose"` explicitly.

### Step 7: Docs and config

**`config/doc-coverage.json`** — add entry:
```json
"content compose": {"manpage": false}
```
(matching sibling content subcommands covered by the group `content.md`)

**`docs/user/manpages/content.md`** — add `### compose` subsection with a real
EXAMPLES block:
```
gz content compose AGENTS.md --consumer codex --candidate /tmp/candidate.md
```

**`docs/user/runbook.md`** — add operator runbook entry for the compose flow
(corpus → compose → candidate → attest → promote).

**`docs/user/skills/gz-content-compose.md`** — skill manpage (create).

**`docs/user/skills/index.md`** — link the new skill manpage (add row).

### Step 8: Author compose skill

**`.gzkit/skills/gz-content-compose/SKILL.md`** — the compose skill:
- Frontmatter: `gz_command: gz content compose`
- Purpose: the LLM-as-compression-judgment surface; operator wields this after
  reading the corpus and making drop/combine/rewrite decisions
- Procedure: read corpus → draft candidate → run `gz content compose` to validate
  + write candidate + emit ledger event → stage for advisor-QC (OBPI-24) and
  operator attestation (OBPI-22)
- Output Contract: byte evidence table + candidate artifact path
- DO NOT: call Anthropic API in tool code; auto-promote candidate to committed rendition

### Step 9: Update context router + regenerate distribution manifest

**`.gzkit/skills/gz-context/SKILL.md`** — add `gz-content-compose` routing entry,
bump version.

**`data/distribution_baseline_manifest.json`** — run:
```bash
uv run gz agent sync control-surfaces
```
This regenerates the manifest including the new skill.

### Step 10: BDD scenarios

**`features/content_compose.feature`** — Heavy-lane BDD scenarios:
```gherkin
@REQ-0.0.37-21-01
Scenario: Compose produces candidate rendition with byte evidence
  Given a surface corpus with compressible and invariant entries
  When I run gz content compose with a valid candidate
  Then the candidate artifact exists and byte evidence is reported

@REQ-0.0.37-21-02
Scenario: Compose is deterministic
  ...

@REQ-0.0.37-21-03
Scenario: Invariant-tier entries appear verbatim in candidate
  ...

@REQ-0.0.37-21-04
Scenario: Compose fails closed on absent corpus
  ...

@REQ-0.0.37-21-05
Scenario: Compose does not modify rendered surfaces
  ...
```

### Step 11: Present OBPI Acceptance Ceremony

Universal Gate 5 — human attestation required.

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --documents
uv run gz validate --ledger
uv run gz validate --surfaces
uv run gz validate --cli-alignment
uv run gz covers OBPI-0.0.37-21-authoring-time-compression-composer-tool-skill --json
uv run -m behave features/content_compose.feature
```

## Notes

- The `compose` command takes a `--candidate <file>` arg (or stdin) — the operator
  (agent wielding skill) supplies the candidate_text; the tool validates and records
- `candidate_path` creates parent dirs as needed (`mkdir(parents=True, exist_ok=True)`)
- `temperature_for` in vendors.py returns token count; convert to bytes via
  `SETPOINT_TOKENS * AVG_BYTES_PER_TOKEN` or expose a `setpoint_bytes` helper —
  check vendors.py for the actual API first
- The 8 REQs map to req_atomic (all single-unit); seq=01 per REQ
- Destination-in-mind: `compose.py` + `composer.py` modeled directly on `remember.py` +
  `corpus_store.py` — minimal new surface, maximum pattern reuse
- Rejected alternatives: (a) storing candidate text in ledger directly — too large,
  ledger is for events not artifacts; (b) auto-generating candidate via LLM in tool code —
  explicitly rejected by ADR Alternative #11 and STDLIB-FIRST doctrine
