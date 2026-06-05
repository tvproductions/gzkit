# Plan — OBPI-0.0.37-19: Corpus Capture Tool + Skill

## Context

ADR-0.0.37 § Decision Re-Alignment (2026-06-03) re-aimed CIC-1 onto a corpus pipeline:
`corpus (append-only source) → compress toward setpoint → committed rendition → deterministic playback → rendered surface`.

OBPI-18 landed the **model** (`CorpusEntry`/`Corpus`, attested-complete). This OBPI delivers the
**write-path half**: a `gz content remember` subcommand that appends an addressed, provenanced
`CorpusEntry` to an append-only per-surface store, emits a `corpus_entry_appended` ledger event,
and **never edits a rendered surface** (AGENTS.md/CLAUDE.md/mirrors stay byte-unchanged — deterministic
playback in OBPI-22 remains the sole writer). It replaces the superseded OBPI-12 renderer path.
Lane: **Heavy** (new CLI verb + new schema + new ledger-event family member).

---

## ⚠️ Brief Corrections (ratified by approving this plan)

The pre-flight audit + brief's own mandated witnesses (`gz validate --brief-reconcile`, `gz cli audit`,
filesystem read) surfaced two **allowlist defects** and three **design clarifications**. Approving this plan
ratifies them (the attested `gz brief reconcile --apply` path is OBPI-06, unlanded — so corrections land by
editing the brief's Allowed Paths, which is itself in the allowlist). These will also be written into the
brief's `## Tracked Defects` + `### Implementation Summary`.

**Allowlist correction A — add `src/gzkit/ledger_events.py`.**
The ledger-event pattern is two-representation: a typed read-path model in `src/gzkit/events.py` (brief ✓)
**and** a named write-path factory in `src/gzkit/ledger_events.py` (brief ✗ — omitted). Proof:
`composition_rendered` has both `CompositionRenderedEvent` (events.py:398) and `composition_rendered_event(...)`
(ledger_events.py:471). `Ledger.append()` takes the generic `LedgerEvent` the factory returns, not the typed
model. A faithful `corpus_entry_appended` cannot land without the factory. `--brief-reconcile` passed (exit 0) —
this is a code-convention coupling below its dimension resolution; the finding is code-level and stands.

**Allowlist correction B — `docs/user/manpages/gz-content.md` CREATE → `docs/user/manpages/content.md` EDIT.**
The `gz content` group manpage **already exists** as `content.md` (`# gz content`; documents
import/list/show/render/edit). Creating a new `gz-content.md` would orphan a duplicate and leave
`gz cli audit`'s content-group resolution pointing at the real file, which would still lack `remember`.
The faithful action is to add a `### remember` subsection to existing `content.md`. (Bonus: editing an
existing page is mkdocs-nav-neutral, dissolving the new-page-nav risk.)

**Design clarification 1 — add `--classification` flag (default `Ambiguous`).**
`CorpusEntry.classification` is required (`Literal[Mechanical|Promotable|Judgment|Ambiguous]`, no default) but
the checklist signature omits it. Add an optional `--classification` flag defaulting to `Ambiguous` (the
"unclassified-yet" bucket). All within the new command — no allowlist impact.

**Design clarification 2 — normalize `--section` through `_kebab()`.**
`Pillar.id = _kebab(title)` (markdown_parser.py:183), so `## Behavior Rules` → `behavior-rules`. The brief demo's
`--section "Behavior Rules"` must be normalized to match. The command kebab-normalizes `--section` (reusing the
existing helper), validates the normalized id against the parsed surface's pillars, and stores the kebab id.

**Design clarification 3 — emit inline in the command (no new events-helper module).**
`governance/events.py` is governance-domain; corpus is content-domain. The command constructs
`Ledger(root/".gzkit"/"ledger.jsonl").append(corpus_entry_appended_event(...))` inline (mirrors plan.py:310).
Only cross-module add is the factory in `ledger_events.py` (correction A). No governance/events.py edit.

---

## Implementation (TDD RED → GREEN per behavior increment)

### 1. Ledger event family member (`corpus_entry_appended`)
- **`src/gzkit/events.py`** — add `CorpusEntryAppendedEvent(_EventBase)`: `event: Literal["corpus_entry_appended"]`,
  `surface: str`, `section: str`, `entry_id: str`, `tier: str`. Register in the `TypedLedgerEvent` union (events.py:427).
- **`src/gzkit/ledger_events.py`** *(allowlist correction A)* — add `corpus_entry_appended_event(surface, section, entry_id, tier) -> LedgerEvent`,
  mirroring `composition_rendered_event` (ts-stamped id `corpus-entry-appended-{ts}`, payload in `extra=`).
- **`.gzkit/schemas/ledger_events.json`** — add an `event_types` entry: `id`/`name` = `corpus_entry_appended`,
  `schema.required` + `required_fields` = `["surface","section","entry_id","tier"]`, with `properties` typed string.
  Validated by `gz validate --ledger` (trust_audits/events.py).

### 2. Append-only store — **`src/gzkit/content/corpus_store.py`** (CREATE)
Consumes OBPI-18 `Corpus`/`CorpusEntry` read-only. Stdlib I/O, UTF-8, `pathlib`, `.as_posix()` per cross-platform rule.
- `corpus_path(root, surface) -> Path` → `root/.gzkit/corpus/<surface>.jsonl`
- `load_corpus(root, surface) -> Corpus` (empty `Corpus()` if file absent; `Corpus.loads` otherwise)
- `append_entry(root, surface, entry) -> None` (load → `Corpus.append` → write `dumps()` + trailing newline; mkdir parents)

### 3. Command handler — **`src/gzkit/commands/content/remember.py`** (CREATE)
Sibling of `edit.py`. `content_remember_cmd(*, surface, section, text, tier, classification, origin)`:
1. `root = get_project_root()`; resolve `surface_path = root/surface`. Missing file → stderr + `exit 1` (unknown surface, **no write**).
2. Parse surface → `AgentContract` via `parse(surface_path.read_text(), "AgentContract", file_path=...)`.
3. Normalize `section` via `_kebab` (import from markdown_parser); build candidate `CorpusEntry`
   (id `corpus-{surface}-{ts}`, ts `datetime.now(UTC).isoformat()`, anchor/witness `None`, origin default `"cli:content-remember"`).
4. Validate: `Corpus(entries=(entry,)).validate_against(contract)`; `ValueError` → stderr + `exit 1` (**no write**) — satisfies REQ-04 ordering (validate before append).
5. `corpus_store.append_entry(root, surface, entry)`; IO error → `exit 2`.
6. Emit: `Ledger(root/".gzkit"/"ledger.jsonl").append(corpus_entry_appended_event(surface, section, entry.id, tier))`.
7. `exit 0`; human status line on TTY (mirror edit.py's `render_status_line`).

### 4. Parser registration — **`src/gzkit/commands/content/__init__.py`** (EDIT)
Add `_register_remember(content_commands)` (mirror `_register_edit`, __init__.py:218) wired into `register_content_parsers`.
Flags: positional `surface`; `--section` (required), `--text` (required), `--tier {invariant,compressible}` (default `compressible`),
`--classification {Mechanical,Promotable,Judgment,Ambiguous}` (default `Ambiguous`), `--origin` (default `cli:content-remember`).
`set_defaults(func=lambda a: _content("remember","content_remember_cmd")(...))`.

### 5. Capture skill — **`.gzkit/skills/gz-content-remember/SKILL.md`** (CREATE, canonical)
Frontmatter mirroring an existing skill (name, description, category `content-authoring`, `metadata.skill-version: "0.1.0"`,
`lifecycle_state: active`, `owner`, `last_reviewed: 2026-06-05`, `model: haiku`, `gz_command: gz content remember`).
Body: Purpose / Persona / Procedure / Validation / Example. Then **`gz agent sync control-surfaces`** propagates to
`src/gzkit/skills/` + `.claude/`/`.github/`/`.agents/` mirrors (never hand-edit mirrors). Validated by `gz validate --surfaces`.

### 6. Docs *(allowlist correction B)*
- **`docs/user/manpages/content.md`** (EDIT) — add `### remember` under `## Subcommands` + an EXAMPLES entry with real output.
- **`docs/user/runbook.md`** (EDIT) — operator capture-flow entry.
- Satisfy `gz cli audit` for the new `content remember` command across manpage + command-doc + index (author whatever it flags).

### 7. Tests (RED first, derived from REQs not implementation)
- **`tests/content/test_corpus_store.py`** (CREATE) — `corpus_path`/`load_corpus`/`append_entry` round-trip; append-only (prior entries preserved); file/dir created on first use.
- **`tests/commands/test_content_remember.py`** (CREATE) — mirror `tests/commands/test_content_cli.py` (`CliRunner.invoke(main, [...])`, temp project root, `@covers` from `gzkit.traceability`). One method per REQ below.
- **`features/content_remember.feature`** (CREATE) + steps — scenarios tagged `@REQ-0.0.37-19-01..04`.

---

## REQ → proof mapping

| REQ | Kind | Proof |
|-----|------|-------|
| 19-01 | BEHAVIOR | `test_remember_appends_one_entry_all_fields_populated` + `@covers` |
| 19-02 | BEHAVIOR | `test_remember_leaves_rendered_surfaces_byte_unchanged` (snapshot AGENTS.md/CLAUDE.md bytes around call) |
| 19-03 | BEHAVIOR | `test_remember_emits_corpus_entry_appended_event` (assert surface/section/entry_id/tier in ledger) |
| 19-04 | BEHAVIOR | `test_remember_fails_closed_on_unknown_surface` + `test_remember_fails_closed_on_unaddressable_section` (non-zero, no write) |
| 19-05 | SUPPORT | `gz validate --ledger` + emitted event |
| 19-06 | SUPPORT | `gz validate --surfaces` + `artifact_edited` for the skill |
| 19-07 | SUPPORT | `gz validate --documents` + `artifact_edited` for the docs |

---

## Verification (gates)

```bash
uv run gz validate --brief-reconcile      # re-run after brief Allowed-Paths correction
uv run gz validate --ledger --surfaces --documents
uv run gz cli audit                        # new content remember covered 3 ways
uv run gz lint && uv run gz typecheck && uv run gz test
uv run mkdocs build --strict               # Gate 3
uv run -m behave --tags=@REQ-0.0.37-19-01,@REQ-0.0.37-19-02,@REQ-0.0.37-19-03,@REQ-0.0.37-19-04 features/   # Gate 4
uv run -m unittest tests.commands.test_content_remember tests.content.test_corpus_store -v
# Demo (proves no rendered-surface write):
uv run gz content remember AGENTS.md --section "Behavior Rules" --text "Prefer stdlib JSONL for append-only stores." --tier compressible
test -s .gzkit/corpus/AGENTS.md.jsonl
```

Then **Gate 5 human attestation** (universal, Heavy/foundation) via the OBPI pipeline closeout.

## Execution route

This is contract-bearing OBPI work → **`uv run gz obpi pipeline OBPI-0.0.37-19`** owns stage sequencing
(verify → ceremony → guarded git-sync → completion) after this plan is approved. Not the direct-fix path.
