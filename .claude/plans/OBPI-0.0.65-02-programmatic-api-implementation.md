# Plan: OBPI-0.0.65-02-programmatic-api-implementation

**OBPI:** OBPI-0.0.65-02-programmatic-api-implementation
**ADR:** ADR-0.0.65-handoff-system-consolidation (Checklist item #2)
**Lane:** Heavy

## Context

The `gz-session-handoff` skill documents a programmatic API (`create_handoff`,
`scaffold_handoff`, `list_handoffs`, `resume_handoff`, `load_handoff_chain`) importable
from `tests.governance.test_session_handoff` — a module that does not exist. Only
`src/gzkit/handoff_validation.py` is real. Handoffs are therefore hand-authored, bypassing
the validation gate. This OBPI ships the real API wrapping the validator, with
`scaffold_handoff` deterministically pre-filling factual sections from observed state.

## Creates These Files

- `src/gzkit/handoff_api.py` **CREATE**
- `tests/governance/test_handoff_api.py` **CREATE**

## Files

**Edits:**
- `src/gzkit/handoff_validation.py` — widen `_OBPI_ID_RE` to accept full slug
- `.gzkit/skills/gz-session-handoff/SKILL.md` — references + remove disclaimers + version bump
- `data/behave_coverage_waivers.json` — OBPI-level behave waiver

## Steps

### Step 1 — Prove REQ-07 with a covering test (regex already widened)

**Correction (2026-07-13):** `_OBPI_ID_RE` at `handoff_validation.py:66` **already**
accepts the full slug form (`^OBPI-\d+\.\d+\.\d+-\d{2}(?:-[a-z0-9-]+)?$`) — it was
widened by OBPI-0.0.72-02 (Jul 6), after this plan was first authored. The brief's
"widen the regex" instruction is therefore stale drift. REQ-07 is code-satisfied;
it needs a **covering test** proving a `create_handoff`-produced full-slug
release-pairing handoff validates AND is found by `find_handoff_for_release` — not
a redundant regex edit. If (and only if) that test fails against the current regex,
widen as a contingency. Brief-reconcile note to be recorded during Stage 5.

### Step 2 — CREATE `src/gzkit/handoff_api.py` (REQ-01..05)

Public functions (stdlib + Pydantic, NO LLM/network):

- `create_handoff(adr_id, branch, agent, slug, sections, *, obpi_id=None, continues_from=None, session_id=None, base_path=Path("."), timestamp=None) -> Path` — render frontmatter + body (sections dict keyed by REQUIRED_SECTIONS), run `validate_handoff_document`; raise `HandoffValidationError` with the violation list when non-empty (fail-closed, no write); else write `.gzkit/handoffs/<fs-ts>-<slug>.md` and return the path.
- `scaffold_handoff(adr_id, *, obpi_id=None, base_path=Path("."), now=None) -> dict[str,str]` — return a sections dict with deterministically pre-filled `Current State Summary`, `Evidence / Artifacts`, `Verification Checklist` from observed state: ledger events (`.gzkit/ledger.jsonl`), completion/ARB receipts (`artifacts/receipts/`), and `git diff --name-only` since the lock-claim timestamp. NO LLM. Identical inputs → byte-identical sections (sort deterministically; no wall-clock in section bodies except the passed `now`).
- `list_handoffs(adr_id=None, *, base_path=Path(".")) -> list[HandoffInfo]` — scan `.gzkit/handoffs/*.md`, parse frontmatter, keep only files carrying `adr_id`, optional `adr_id` filter, sort newest-first by timestamp.
- `load_handoff_chain(handoff_path, *, base_path=Path(".")) -> list[Path]` — traverse `continues_from` oldest→newest, depth ≤20, cycle-safe (track visited set).
- `resume_handoff(adr_id, *, expected_branch=None, base_path=Path(".")) -> ResumeResult` — select newest, classify staleness (Fresh <24h / Slightly-Stale 24-72h / Stale 72h-7d / Very-Stale >7d), set `requires_human_verification` for Stale/Very-Stale, extract first next step from "Immediate Next Steps".

Models: `HandoffInfo` (path, adr_id, obpi_id, timestamp), `ResumeResult` (path, staleness, requires_human_verification, first_next_step, chain), `StalenessLevel` (str enum). Pydantic `BaseModel`, frozen.

Reuse `gzkit.handoff_validation`: `validate_handoff_document`, `parse_frontmatter`, `REQUIRED_SECTIONS`, `HandoffFrontmatter`.

### Step 3 — CREATE `tests/governance/test_handoff_api.py` (all REQs)

Unittest + tempfile. One `@covers("REQ-0.0.65-02-NN")` test class per REQ:
- create_handoff writes valid / raises on invalid (fail-closed, no file written)
- scaffold_handoff determinism (call twice, assert byte-identical factual sections; assert no socket via `patch("socket.socket")`)
- list_handoffs filtering + newest-first ordering
- load_handoff_chain traversal + cycle fixture (A→B→A terminates)
- resume_handoff staleness buckets + requires_human_verification + first next step
- full-slug frontmatter accepted (REQ-07): a full-slug `obpi_id` handoff validates

### Step 4 — EDIT `.gzkit/skills/gz-session-handoff/SKILL.md` (REQ-06)

Repoint import references `tests.governance.test_session_handoff` → `gzkit.handoff_api`.
Remove the `NOT IMPLEMENTED` / `DESIGN TARGET` disclaimer blocks. Bump `skill-version`
(minor) + `last_reviewed` to today. Run `uv run gz agent sync control-surfaces`.

### Step 5 — EDIT `data/behave_coverage_waivers.json`

Add `waivers` entry + `default_rationale` code for OBPI-0.0.65-02 (API unit-proven;
CLI behave is OBPI-03).

### Step 6 — Verify

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_handoff_api -v
uv run gz covers OBPI-0.0.65-02-programmatic-api-implementation --json
uv run gz validate --documents --surfaces
uv run mkdocs build --strict
```

## Verification

```bash
uv run gz validate --brief-reconcile
uv run gz lint
uv run gz typecheck
uv run gz test
```

## Notes

- `scaffold_handoff` is the anti-vibe core: factual sections deterministic from observed
  state; only Decisions Made / Important Context remain author-supplied.
- The SKILL.md edit is a coupled surface requiring `gz agent sync control-surfaces`.
- `_OBPI_ID_RE` is already widened (OBPI-0.0.72-02); REQ-07 is proven by a covering test, not a code edit (Step 1 correction 2026-07-13).
- Plan-before-exploration disclosure: destination-in-mind was a thin wrapper over `validate_handoff_document` mirroring the two existing writers (`write_completion_handoff`/`write_degenerate_handoff`); rejected alternatives — (a) re-widening the already-correct regex, (b) `scaffold_handoff` reaching for ledger/git internally (breaks determinism + hexagonal core-purity; observed state is injected as parameters instead).
