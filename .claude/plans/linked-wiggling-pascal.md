# Plan — Build OBPI-0.0.37-18: Append-Only Corpus Model

## Context

**Why this change.** Root `AGENTS.md` is ~28 KB and the gzkit governance surface collapses Codex's 258K
window (GHI #519). The durable cure (GHI #533) is the operator-designed **Context-Load CMS** booked in
ADR-0.0.37 §Decision Re-Alignment (2026-06-03): an append-only **corpus** (source of truth) →
authoring-time compression toward a setpoint → committed rendition → deterministic playback. Items 18–27
decompose it; all are `Draft`. **OBPI-18 is the foundation: the corpus data layer** that every later
OBPI (capture/19, setpoint/20, compressor/21, playback/22, invariant-tier/23) builds on. The brief is
authored and passes `gz obpi validate --authored` + `gz validate --req-kind-discipline`.

**Scope of this OBPI:** model + schema + append-only contract + section conformance. It captures nothing,
renders nothing, adds no CLI verb and no ledger event (those are 19+). Lane: **Heavy / foundation →
Gate 5 human attestation required** (I cannot self-sign; I stop at Gate 5 for the operator).

**Risk on record (advisor flag #3):** ADR-0.0.37 §Decision Re-Alignment is still `Draft`
(Attestation Block `0.0.37 | Pending`). OBPI-18 lands the entry *shape* all of 19–27 inherit, so shape
correctness matters more than usual. Operator chose "Start CMS" over "Evaluate design first" — proceeding
per that call.

## Approach (recommended)

TDD (RED→GREEN per REQ), driven through the OBPI pipeline. Four net-new artifacts + one export edit.

### Design decisions (resolves the brief's flagged OPEN DECISION)

- **`CorpusEntry` is a plain frozen `BaseModel`** (`ConfigDict(frozen=True, extra="forbid")`) with **exactly
  the ten ADR-named fields** — mirroring `ConstitutionalInvariant` ([invariants.py:28](src/gzkit/governance/invariants.py#L28)),
  the closest store-record precedent. It does **NOT** inherit `BaseContentModel` (that would add an 11th
  `schema_version` field, breaking "exactly ten", and implies render-surface membership). "Reuse the
  AgentContract/Pillar substrate" is honored through *conformance* (below), not inheritance.
- **Not registered in `CONTENT_MODELS`.** That dict ([models/__init__.py](src/gzkit/content/models/__init__.py))
  is the parse/render dispatch registry for top-level surfaces; a corpus entry is a store record. Precedent:
  `Pillar` is exported in `__all__` but absent from `CONTENT_MODELS`. Corpus/CorpusEntry follow suit —
  exported for ergonomics, not registered.
- **Section conformance is deferred-aware.** `Corpus.validate_against(contract)` checks only that each
  `entry.section` resolves to a `Pillar.id` in the contract. Invariant-tier *presence* enforcement is
  **OBPI-23** (`Pillar.tier` is `lite|medium|heavy` today — no `invariant` value exists to compute against;
  do not hardcode a section list to fake it).

### Files

1. **`src/gzkit/content/models/corpus.py`** — **CREATE** (net-new).
   - `CorpusEntry(BaseModel)` frozen/extra=forbid: `id, surface, section, anchor: str|None=None,
     tier: Literal["invariant","compressible"], classification: Literal["Mechanical","Promotable","Judgment","Ambiguous"],
     witness: str|None=None, text, origin, ts`. (Reuse the classification enum literal from `bullet.py`.)
   - `Corpus(BaseModel)` frozen/extra=forbid: `entries: tuple[CorpusEntry, ...] = ()`. Methods:
     - `append(entry) -> Corpus` — returns a NEW `Corpus`; the only mutation surface; no edit/remove.
     - `dumps() -> str` / `loads(text) -> Corpus` — JSONL via `model_dump_json()` per line
       (precedent: `events.py` ledger JSONL); round-trips to an equal `Corpus`.
     - `validate_against(contract: AgentContract) -> None` — raises `ValueError` when any
       `entry.section ∉ {p.id for p in contract.pillars}`.

2. **`src/gzkit/schemas/corpus_entry.json`** — **CREATE** (net-new). JSON Schema mirror shaped on
   [constitutional_invariant.json](src/gzkit/schemas/constitutional_invariant.json): `additionalProperties:false`;
   `required` = the 8 non-optional fields; `tier`/`classification` enums; `anchor`/`witness` optional.

3. **`src/gzkit/content/models/__init__.py`** — EDIT. Add `Corpus`, `CorpusEntry` imports + `__all__`
   entries. **Do not** add to `CONTENT_MODELS`.

4. **`tests/content/test_corpus_model.py`** — **CREATE** (net-new). stdlib `unittest`,
   `from gzkit.traceability import covers`, semantic assertions (cf. `test_round_trip_agent_contract.py`):
   - `@covers("REQ-0.0.37-18-01")` — ten fields present; `extra="forbid"` rejects unknown field; out-of-enum `tier` raises.
   - `@covers("REQ-0.0.37-18-02")` — `append` yields new Corpus, original unchanged; no mutate/remove method; `entries` is a tuple; `Corpus.loads(c.dumps()) == c`.
   - `@covers("REQ-0.0.37-18-03")` — `validate_against` raises on a section that is no `Pillar.id`; passes for a conformant corpus.
   - `@covers("REQ-0.0.37-18-04")` — load `corpus_entry.json`, `jsonschema.validate` accepts a conformant entry, rejects unknown-property + out-of-enum tier; assert schema-property set == model-field set (parity).

5. **`features/constitutional_invariants.feature`** (+ `features/steps/constitutional_invariants_steps.py` if
   steps don't already cover) — Gate 4 BDD scenarios tagged `@REQ-0.0.37-18-01`..`-04` exercising append +
   conformance + schema reject. (behave REQ-tags enforced on Completed/Validated briefs.)

### Reuse (don't reinvent)

- Classification enum literal — `bullet.py` `_Classification`.
- Schema-mirror shape + `jsonschema.validate` loader pattern — `invariants.py` `load_invariants`.
- JSONL serialize pattern — `events.py`.
- Conformance source — `AgentContract.pillars[*].id` ([agent_contract.py:16](src/gzkit/content/models/agent_contract.py#L16)).

## Execution path (after approval)

`uv run gz obpi pipeline OBPI-0.0.37-18` — the runtime owns stage sequencing (mint TASK → TDD → verify →
ceremony → guarded `gz git-sync --apply --lint --test` → completion). I follow `gz-obpi-pipeline`. Commits
carry a `Task:` trailer (minted by the pipeline). **At Gate 5 I STOP and present attestation commands; the
operator executes + attests. No self-close.**

## Verification (end-to-end)

```bash
uv run -m unittest tests.content.test_corpus_model -v          # Gate 2: all REQ tests GREEN
uv run python -c "from gzkit.content.models import CorpusEntry, Corpus; print('import ok')"
uv run gz lint && uv run gz typecheck                          # clean
uv run gz validate --documents --req-kind-discipline
uv run mkdocs build --strict                                   # Gate 3
uv run -m behave features/constitutional_invariants.feature    # Gate 4
uv run gz test                                                 # full suite, no regression
```

Then Gate 5: present the above evidence + receipts to the operator for human attestation.

## Out of scope (fenced to later OBPIs)

Capture CLI + `corpus_entry_appended` event → **19**; setpoint map → **20**; compressor → **21**;
committed-rendition store + deterministic playback + `--invariant-coherence` move → **22**;
invariant-tier designation + presence enforcement → **23**. No edits to `AGENTS.md`, `compose.py`,
`sync_surfaces.py`, the monolith template, `events.py`, `vendor-manifest.json`, or `Pillar`.
