# Plan: OBPI-0.0.72-02-handoff-frontmatter-reconcile

**OBPI:** OBPI-0.0.72-02-handoff-frontmatter-reconcile
**ADR:** ADR-0.0.72-meta-governance-coherence (Checklist item #2 — ADAPTER C1/C2/C3)
**Lane:** Heavy

## Context

`HandoffFrontmatter` (`src/gzkit/handoff_validation.py:87`) uses bare `extra="forbid"` and
declares only mode/adr_id/branch/timestamp/agent/obpi_id/session_id/continues_from. This
REJECTS:
- **C3:** slug-bearing `obpi_id` (the reaping writer emits `lock.obpi_id` = full slug; `_OBPI_ID_RE` only allows `-\d{2}$`)
- **C1:** consumer-required min-info fields `last_lock_event_timestamp`, `last_commit_sha` (`_MIN_INFO_FRONTMATTER_FIELDS`)
- **C2:** its own writers' degenerate/reaping fields `abandoned`, `category`, `abandoned_by`, `abandoned_at`, `previous_agent`, `reason`

`validate_handoff_document` is wired to no gate (enforcement asymmetry: strict consumer, toothless authoring model).

## Plan-before-exploration disclosures (Step 6a)

- **Destination-in-mind:** widen `_OBPI_ID_RE` to the `obpi.json` pattern; declare the superset fields on `HandoffFrontmatter` while KEEPING `extra="forbid"`; add `run_handoff_document_audit` to `quality.py` + register in `_build_check_steps`; TDD tests.
- **Rejected alternatives:** dropping `extra="forbid"` entirely (kills typo-defense — REQ-1 forbids); editing the read-only coherence targets `lock_manager.py`/`lock_handoff_coupling.py`/`obpi.json` (REQ-6 forbids — the model reconciles TO them).

## Creates These Files

- `tests/test_handoff_frontmatter_coherence.py` **CREATE**

## Files

**Edits:**
- `src/gzkit/handoff_validation.py` — widen `_OBPI_ID_RE`; declare superset fields on `HandoffFrontmatter`
- `src/gzkit/quality.py` — new `run_handoff_document_audit`
- `src/gzkit/commands/quality.py` — register the audit in `_build_check_steps`

## Steps

### Step 1 — TDD RED: author `tests/test_handoff_frontmatter_coherence.py` (all REQs)

Unittest. Tests derived from the brief's acceptance criteria:
- **REQ-01:** full-slug `obpi_id` (`OBPI-0.0.72-02-handoff-frontmatter-reconcile`) validates via `HandoffFrontmatter` AND `find_handoff_for_release` exact-matches a handoff carrying it.
- **REQ-02:** `last_lock_event_timestamp` + `last_commit_sha` accepted (alongside existing `branch`).
- **REQ-03:** `abandoned`, `category`, `abandoned_by`, `abandoned_at`, `previous_agent`, `reason` accepted.
- **REQ-04:** a misspelled key (`last_commmit_sha`) STILL raises `ValidationError` (typo-defense preserved).
- **REQ-05:** the exact frontmatter from `write_degenerate_handoff` and `_write_reaping_handoff` round-trips through `validate_handoff_document` with zero violations.
- **REQ-06:** `run_handoff_document_audit` exists and is registered in `_build_check_steps`.

Run; confirm RED (writer output + slug obpi_id currently rejected).

### Step 2 — GREEN: reconcile `HandoffFrontmatter` (`src/gzkit/handoff_validation.py`)

- Widen `_OBPI_ID_RE` to `re.compile(r"^OBPI-\d+\.\d+\.\d+-\d{2}(?:-[a-z0-9-]+)?$")` (matches `obpi.json:16`; additive — short form still validates).
- Declare the superset fields on `HandoffFrontmatter`, KEEPING `model_config = ConfigDict(extra="forbid", frozen=True)` (this IS the explicit superset — every real field declared, unknown keys still raise):
  - `last_lock_event_timestamp: str | None = None`
  - `last_commit_sha: str | None = None`
  - `abandoned: bool | None = None`
  - `category: str | None = None`
  - `abandoned_by: str | None = None`
  - `abandoned_at: str | None = None`
  - `previous_agent: str | None = None`
  - `reason: str | None = None`

### Step 3 — GREEN: gate-wire `validate_handoff_document` (REQ-06)

- Add `run_handoff_document_audit(project_root=...)` to `src/gzkit/quality.py` — runs `validate_handoff_document` over `.gzkit/handoffs/*.md`, mirroring the sibling `run_*_audit` runners; returns the standard audit result shape.
- Register it in `src/gzkit/commands/quality.py` `_build_check_steps` (the `gz check` bundle).

### Step 4 — REFACTOR + verify

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.test_handoff_frontmatter_coherence -v
uv run gz covers OBPI-0.0.72-02-handoff-frontmatter-reconcile --json
uv run gz validate --lock-handoff-coupling
uv run gz validate --documents
uv run mkdocs build --strict
```

## Verification

```bash
uv run gz validate --brief-reconcile
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --lock-handoff-coupling
```

## Notes

- Keeping `extra="forbid"` + declaring all fields = the explicit-superset model (REQ-1). Do NOT drop the guard.
- Do NOT edit `lock_manager.py`, `lock_handoff_coupling.py`, `obpi.json` — read-only coherence targets (REQ-6).
- REQ-06 is SUPPORT (gate wiring + `artifact_edited`); REQ-01..05 are BEHAVIOR (`@covers`).
- This OBPI subsumes the REQ-07 I had drafted in OBPI-0.0.65-02 — that REQ will be removed from 65-02.
