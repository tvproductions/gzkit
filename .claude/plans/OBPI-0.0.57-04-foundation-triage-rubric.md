# Plan: OBPI-0.0.57-04-foundation-triage-rubric

**OBPI:** `OBPI-0.0.57-04-foundation-triage-rubric`
**Parent ADR:** `ADR-0.0.57-foundation-adr-nominal-id-triage`
**Lane:** Heavy
**Brief:** `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/obpis/OBPI-0.0.57-04-foundation-triage-rubric.md`

## Context

OBPI-03 (foundation-triage-skill) is Completed. Its `triage.py` composer
defers all rubric scoring to `src/gzkit/foundation/rubric.py`, which this
OBPI implements. The signal dimensions are:

- `insights_signal_count` — rows in agent-insights.jsonl mentioning the ADR ID
- `ghi_occurrence_count` — unique GHI references in insights rows mentioning the ADR ID
- `feature_unblocking_count` — pool/feature ADR files with `depends_on` frontmatter listing the foundation ID

Output is a frozen Pydantic `FoundationTriageRankEntry` with
`evidence: tuple[EvidenceRef, ...]` (min_length=1).

The PRD already has the `governance-triage` section with ADR-0.0.57
provenance, but `feature-unblocking-count` is only referenced in the
`triage-rubric` definition, not as a standalone term — plan adds it.

## Approach

TDD: write fixture + failing tests first, then implement rubric.py, then generate the JSON schema from the model.

## Allowed Paths (from brief)

- `src/gzkit/foundation/rubric.py`
- `src/gzkit/schemas/foundation_triage_rank_input.json`
- `docs/governance/foundation-triage-rubric.md`
- `docs/design/prd/PRD-GZKIT-1.0.0.md`
- `tests/test_foundation_triage_rubric.py`
- `tests/fixtures/foundation_triage_rubric/`
- `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/obpis/OBPI-0.0.57-04-foundation-triage-rubric.md` (evidence only)

## Steps

### Step 1: Create test fixtures

Create fixture files under `tests/fixtures/foundation_triage_rubric/`:

- `backlog/ADR-0.0.90-fixture-alpha.md` — Draft foundation ADR fixture
- `backlog/ADR-0.0.91-fixture-beta.md` — Draft foundation ADR fixture
- `pool_adrs/ADR-pool.feature-x.md` — pool ADR with `depends_on` listing `ADR-0.0.90`
- `pool_adrs/ADR-pool.feature-y.md` — pool ADR with `depends_on` listing `ADR-0.0.90`
- `pool_adrs/ADR-pool.feature-z.md` — pool ADR with no `depends_on` (control)
- `insights.jsonl` — 3 rows mentioning ADR-0.0.90 (2 with GHI references), 1 mentioning ADR-0.0.91

### Step 2: Write tests (RED — derive from REQs, not implementation)

Create `tests/test_foundation_triage_rubric.py` covering all 6 REQs:

- `TestFoundationTriageRankEntry.test_valid_construction` — REQ-01 success path
- `TestFoundationTriageRankEntry.test_empty_evidence_raises` — REQ-01 ValidationError
- `TestFoundationTriageRankEntry.test_extra_field_raises` — REQ-03 extra="forbid"
- `TestRubricSignals.test_three_dimensions_computed` — REQ-02 all three dimensions in evidence
- `TestRubricSignals.test_feature_unblocking_count` — REQ-06 depends_on counting
- `TestStructuralOnly.test_no_prose_fields` — REQ-03 keys are only id/priority_score/evidence
- `TestPrdRegistration.test_governance_triage_vocabulary` — REQ-04 PRD has section + provenance
- `TestJsonSchema.test_schema_validates_pydantic_output` — REQ-05 schema/model parity

### Step 3: Implement `src/gzkit/foundation/rubric.py` (GREEN)

Module contents:
- `EvidenceRef` — frozen BaseModel (extra="forbid"): `source: str`, `signal_type: str`, `count: int`
- `FoundationTriageRankEntry` — frozen BaseModel (extra="forbid"): `id: str`, `priority_score: int`, `evidence: tuple[EvidenceRef, ...] = Field(min_length=1)`
- `_count_insights_signal(project_root, foundation_id, insights_path)` → `(int, EvidenceRef)`
- `_count_ghi_occurrence(project_root, foundation_id, insights_path)` → `(int, EvidenceRef)`
- `_count_feature_unblocking(project_root, foundation_id)` → `(int, EvidenceRef)`
- `score_foundation(project_root, foundation_id, *, insights_path=None)` → `FoundationTriageRankEntry`
- `__main__` block: parse `--foundation-root`, `--insights`, `--format json`, emit `{"rank_input": [...]}`

Signal counting notes:
- `insights_signal_count`: count lines in insights_path (or project_root/.gzkit/insights/agent-insights.jsonl) containing the ADR ID
- `ghi_occurrence_count`: count unique GHI numbers (pattern `GHI\s*#\d+`) across insights rows mentioning the ADR ID
- `feature_unblocking_count`: walk pool/ and pre-release/ ADR files, parse `depends_on` frontmatter (list or str), count files referencing the foundation ID

### Step 4: Generate `src/gzkit/schemas/foundation_triage_rank_input.json`

Run `FoundationTriageRankEntry.model_json_schema()` and write as JSON file.
Do not hand-craft the schema; emit from the canonical Pydantic model.

```bash
uv run python -c "
from gzkit.foundation.rubric import FoundationTriageRankEntry
import json, pathlib
schema = FoundationTriageRankEntry.model_json_schema()
pathlib.Path('src/gzkit/schemas/foundation_triage_rank_input.json').write_text(json.dumps(schema, indent=2) + '\n', encoding='utf-8')
print('Schema written')
"
```

### Step 5: Create `docs/governance/foundation-triage-rubric.md`

Documentation covering:
- Purpose and scope
- Signal dimensions (definitions matching PRD vocabulary)
- How `priority_score` is computed (weighted sum: insights × 3 + ghi × 2 + unblocking × 5)
- `FoundationTriageRankEntry` model fields
- Example invocation

### Step 6: Add `feature-unblocking-count` term to PRD

In `docs/design/prd/PRD-GZKIT-1.0.0.md` § 2.1 → ### Governance Triage, add after the `ghi-occurrence-count` entry:

```
- **term:** `feature-unblocking-count` · **scope:** governance-triage · **provenance:** ADR-0.0.57-foundation-adr-nominal-id-triage
  **definition:** Count of pool or feature ADRs whose `depends_on` frontmatter references the candidate foundation ADR; measures how many downstream items are blocked by this foundation's absence.
```

Unique heading anchor constraint from REQ-04: the Governance Triage section already exists under a unique H3 heading, so no new heading is needed — only a new bullet in the existing list.

### Step 7: Run quality checks

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.test_foundation_triage_rubric -v
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --documents
uv run mkdocs build --strict
```

## Verification

From the brief:
```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q tests.test_foundation_triage_rubric
test -f src/gzkit/foundation/rubric.py
test -f src/gzkit/schemas/foundation_triage_rank_input.json
test -f docs/governance/foundation-triage-rubric.md
grep -q "governance-triage" docs/design/prd/PRD-GZKIT-1.0.0.md
grep -q "ADR-0.0.57" docs/design/prd/PRD-GZKIT-1.0.0.md
```

## Notes

- Do NOT touch `src/gzkit/foundation/triage.py` (OBPI-03's surface, Completed)
- Do NOT touch `.gzkit/skills/gz-foundation-triage/SKILL.md` (OBPI-03's surface, Completed)
- JSON schema must be emitted from Pydantic model, never hand-crafted (REQ-05)
- All relative paths in EvidenceRef `source` field via `.as_posix()` (REQ-08 / cross-platform rule)
- `priority_score` = `insights_signal_count * 3 + ghi_occurrence_count * 2 + feature_unblocking_count * 5`
- Present OBPI Acceptance Ceremony (Stage 4 human gate — universal per ADR-0.0.36)
