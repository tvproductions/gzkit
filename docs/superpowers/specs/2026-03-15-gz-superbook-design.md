# gz superbook: Superpowers → GovZero Governance Booking

**Date**: 2026-03-15
**Status**: Design approved, pending implementation plan

## Problem

Superpowers' plan/task framework produces high-quality implementation artifacts (specs, plans, commits) but these exist outside GovZero's governance ledger. Work completed through superpowers has no ADR, no OBPI briefs, no ledger events, and no formal attestation trail. This creates a governance gap where significant architectural work is invisible to `gz status`, `gz state`, and audit workflows.

## Goals

1. **Bridge superpowers and GovZero** — translate superpowers specs/plans into ADR + OBPI artifacts automatically
2. **Support retroactive booking** — formalize already-completed superpowers work into governance artifacts with evidence from git history
3. **Support forward booking** — create governance artifacts from approved specs/plans before implementation begins
4. **Deterministic Python-driven generation** — no agent interpretation variance; Pydantic models, testable pipeline
5. **Human review before commit** — auto-generate drafts, present for approval, book on confirmation

## Architecture

### Command Interface

```bash
# Retroactive — book completed superpowers work into GovZero
gz superbook retroactive \
  --spec docs/superpowers/specs/2026-03-15-agents-md-tidy-design.md \
  --plan docs/superpowers/plans/2026-03-15-agents-md-tidy.md

# Forward — book governance before implementation begins
gz superbook forward \
  --spec docs/superpowers/specs/2026-03-15-foo-design.md \
  --plan docs/superpowers/plans/2026-03-15-foo.md
```

**Flags:**
- `--spec` (required): path to superpowers spec document
- `--plan` (required): path to superpowers plan document
- `--semver` (optional): override auto-assigned semver
- `--lane` (optional): override auto-classified lane (`lite`, `heavy`)
- `--dry-run` (default): show draft without writing
- `--apply`: write artifacts and emit ledger events

### Artifact Mapping

| Superpowers artifact | GovZero artifact | Mapping |
|---------------------|-----------------|---------|
| Spec (design doc) | ADR | 1:1 — spec becomes ADR intent + decision sections |
| Plan chunk | OBPI brief | 1:1 — each chunk becomes one OBPI brief |
| Chunk acceptance criteria | REQ IDs | 1:1 — each criterion gets a deterministic REQ identifier |
| Plan tasks | OBPI work breakdown | Nested — tasks become implementation steps within the OBPI |
| Task commits (retroactive) | OBPI completion evidence | Populated from git log |

### Analysis Pipeline

Both modes follow the same six-step pipeline:

```
Step 1: Parse superpowers artifacts
Step 2: Auto-classify lane
Step 3: Compute decomposition scorecard
Step 4: Map chunks → OBPIs
Step 5: Generate draft
Step 6: Present for human review → Book on approval
```

#### Step 1: Parse superpowers artifacts

Read spec and plan markdown, extracting structured data:

- **From spec**: title, goal, architecture summary, design decisions, implementation scope (files to modify)
- **From plan**: goal, tech stack, chunks (name + tasks), per-task file paths, per-task acceptance criteria
- **From git log (retroactive only)**: commits between plan creation date and now, files changed per commit, commit messages

#### Step 2: Auto-classify lane

Scan the plan's file paths and spec's design decisions against lane classification rules:

```python
HEAVY_SIGNALS = [
    "src/gzkit/cli.py",           # CLI contract change
    ".gzkit/schemas/",             # Schema changes
    "src/gzkit/templates/",        # Control surface templates
    "**/api/**",                    # API surface
]
```

Classification logic:
- If semver starts with `0.0.` → **Foundational**
- If any file path matches a HEAVY_SIGNAL → **Heavy**
- Otherwise → **Lite**

Result: `LaneClassification` with inferred lane + triggering signals. Presented to human for confirmation or override.

#### Step 3: Compute decomposition scorecard

Score 5 dimensions (0-2 each) from the plan's scope:

| Dimension | Scoring basis |
|-----------|--------------|
| Data/State | Touches ledger, schemas, config, manifests |
| Logic/Engine | Adds new functions, algorithms, pipelines |
| Interface | Changes CLI, API, control surface documents |
| Observability | Adds validation, logging, audit checks |
| Lineage | Changes artifact linkage, traceability |

Map total score to baseline OBPI range per existing `gz plan` logic. If the computed target OBPI count differs from the plan's chunk count, flag the discrepancy for human review (the chunk count takes precedence — the scorecard is advisory).

#### Step 4: Map chunks → OBPIs

For each plan chunk:
- Chunk heading → OBPI objective (single narrative, no "and")
- Chunk tasks → OBPI work breakdown (task list with file paths)
- Task file paths (union across tasks in chunk) → OBPI allowed paths
- Task assertions/expected outcomes → OBPI acceptance criteria → REQ IDs

REQ ID format: `REQ-<semver>-<obpi_item>-<criterion_index>`

Example: Chunk 1 "Categorized Skill Catalog" with 3 verifiable outcomes →
- `REQ-0.17.0-01-01`: Category extraction from frontmatter
- `REQ-0.17.0-01-02`: Categorized renderer with uncategorized fallback
- `REQ-0.17.0-01-03`: All 49 SKILL.md files have category field

#### Step 5: Generate draft

Produce in-memory Pydantic models:

- `ADRDraft`: title, semver, lane, intent (from spec goal/problem), decision (from spec architecture), feature checklist (from chunk names), decomposition scorecard
- `list[OBPIDraft]`: one per chunk, with objective, parent ADR, item number, lane, allowed/denied paths, acceptance criteria with REQ IDs, work breakdown
- `list[LedgerEvent]`: `adr_created` + N × `obpi_created`

For **retroactive** mode additionally:
- OBPI status set to `Completed` (not `Draft`)
- ADR status set to `Completed`
- Evidence sections populated from git commits (SHA, message, files changed)
- Gate check events generated from quality gate outputs

For **forward** mode:
- OBPI status set to `Draft`
- ADR status set to `Draft`
- Evidence sections left empty (template placeholders)

#### Step 6: Present for human review

Display the draft as a structured summary:

```
═══════════════════════════════════════════
  gz superbook — Governance Booking Draft
═══════════════════════════════════════════

ADR: ADR-0.17.0 — AGENTS.md Tidy: Control Surface Schema and Rules Mirroring
Lane: Heavy (signals: .gzkit/schemas/, src/gzkit/templates/)
Scorecard: 7/10 → 5 OBPIs (matches plan: 5 chunks)

Feature Checklist:
  1. Categorized Skill Catalog (3 REQs)
  2. Rules Mirroring (3 REQs)
  3. Slim CLAUDE.md (2 REQs)
  4. Schemas and Validation (3 REQs)
  5. Manifest and Integration (2 REQs)

Mode: retroactive — evidence populated from 12 commits
Status: Completed (all evidence present)

Run with --apply to book, or adjust with --semver/--lane.
```

Human reviews and either:
- Approves → `--apply` writes files + ledger events
- Adjusts → re-run with `--semver` or `--lane` overrides
- Asks questions → agent explains classification rationale

### Generated Artifact Structure

Example output for our just-completed work:

```
docs/design/adr/pre-release/ADR-0.17.0-agents-md-tidy/
├── ADR-0.17.0-agents-md-tidy.md
├── obpis/
│   ├── OBPI-0.17.0-01-categorized-skill-catalog.md
│   ├── OBPI-0.17.0-02-rules-mirroring.md
│   ├── OBPI-0.17.0-03-slim-claude-md.md
│   ├── OBPI-0.17.0-04-schemas-and-validation.md
│   └── OBPI-0.17.0-05-manifest-and-integration.md
└── audit/
```

### Ledger Events

```jsonl
{"schema":"gzkit.ledger.v1","event":"adr_created","id":"ADR-0.17.0","lane":"heavy","ts":"...","source":"gz-superbook-retroactive"}
{"schema":"gzkit.ledger.v1","event":"obpi_created","id":"OBPI-0.17.0-01","parent":"ADR-0.17.0","ts":"...","source":"gz-superbook-retroactive"}
{"schema":"gzkit.ledger.v1","event":"obpi_created","id":"OBPI-0.17.0-02","parent":"ADR-0.17.0","ts":"...","source":"gz-superbook-retroactive"}
{"schema":"gzkit.ledger.v1","event":"obpi_created","id":"OBPI-0.17.0-03","parent":"ADR-0.17.0","ts":"...","source":"gz-superbook-retroactive"}
{"schema":"gzkit.ledger.v1","event":"obpi_created","id":"OBPI-0.17.0-04","parent":"ADR-0.17.0","ts":"...","source":"gz-superbook-retroactive"}
{"schema":"gzkit.ledger.v1","event":"obpi_created","id":"OBPI-0.17.0-05","parent":"ADR-0.17.0","ts":"...","source":"gz-superbook-retroactive"}
```

The `source` field distinguishes superbook-generated events from manually-created ones.

## Implementation Architecture

### New files

| File | Responsibility |
|------|---------------|
| `src/gzkit/superbook.py` | Core pipeline: classify, score, map, generate, present, apply |
| `src/gzkit/superbook_parser.py` | Markdown parsing for superpowers specs and plans |
| `tests/test_superbook.py` | Unit tests for pipeline |
| `tests/test_superbook_parser.py` | Unit tests for markdown parsing |
| `.gzkit/skills/gz-superbook/SKILL.md` | Thin skill wrapper for agent invocation |

### Modified files

| File | Change |
|------|--------|
| `src/gzkit/cli.py` | Register `gz superbook` subcommand with `retroactive`/`forward` modes |

### Module breakdown

**`superbook_parser.py`** — Pure functions, no side effects:

| Function | Input | Output |
|----------|-------|--------|
| `parse_spec(path)` | Spec markdown path | `SpecData` (title, goal, architecture, decisions, file_scope) |
| `parse_plan(path)` | Plan markdown path | `PlanData` (goal, tech_stack, chunks with tasks, file_paths, criteria) |
| `extract_commits(plan_path, project_root)` | Plan path + project root | `list[CommitData]` (SHA, message, files, date) |

**`superbook.py`** — Pipeline orchestration:

| Function | Purpose |
|----------|---------|
| `classify_lane(spec, plan)` | Rules-based lane classification with signal reporting |
| `compute_scorecard(plan)` | 5-dimension decomposition scoring |
| `map_chunks_to_obpis(plan, semver)` | Chunk → OBPI mapping with REQ ID generation |
| `generate_adr_draft(spec, plan, scorecard, lane, semver)` | ADR markdown generation from spec |
| `populate_evidence(obpis, commits)` | Fill evidence sections from git history (retroactive) |
| `present_draft(adr, obpis)` | Human-readable summary for review |
| `apply_draft(adr, obpis, project_root)` | Write files + emit ledger events |

### Data models (Pydantic)

```python
class SpecData(BaseModel):
    title: str
    goal: str
    architecture: str
    decisions: list[str]
    file_scope: list[str]

class ChunkData(BaseModel):
    name: str
    tasks: list[TaskData]
    file_paths: list[str]
    criteria: list[str]

class PlanData(BaseModel):
    goal: str
    tech_stack: str
    chunks: list[ChunkData]

class TaskData(BaseModel):
    name: str
    file_paths: list[str]
    steps: list[str]

class CommitData(BaseModel):
    sha: str
    message: str
    files: list[str]
    date: str

class LaneClassification(BaseModel):
    lane: str  # "lite", "heavy", "foundational"
    signals: list[str]
    confidence: str  # "auto", "override"

class REQData(BaseModel):
    id: str  # REQ-X.Y.Z-NN-CC
    description: str

class OBPIDraft(BaseModel):
    id: str
    objective: str
    parent: str
    item: int
    lane: str
    status: str
    allowed_paths: list[str]
    reqs: list[REQData]
    work_breakdown: list[str]
    evidence: list[str]  # populated in retroactive mode

class ADRDraft(BaseModel):
    id: str
    title: str
    semver: str
    lane: str
    status: str
    intent: str
    decision: str
    checklist: list[str]
    scorecard: dict[str, int]
    obpis: list[OBPIDraft]
```

## Scope Exclusions

- **TASK-level governance**: Pool ADR dependency — not implemented here. Tasks remain as OBPI work breakdown items.
- **Automatic attestation**: Retroactive mode sets status to `Completed` but does NOT emit attestation events. Human must still run `gz attest` after reviewing the booked artifacts.
- **Superpowers workflow modification**: `gz superbook` wraps superpowers, does not modify its spec/plan/task workflow.

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Markdown parsing fragility | Parser uses heading-level extraction (## Chunk N), not line-by-line parsing. Tolerant of format variations. Test with actual superpowers output. |
| Lane misclassification | Auto-classification is always presented for human review. `--lane` override available. |
| Semver collision with existing ADRs | Check ledger for existing ADR with same semver before booking. Suggest next available. |
| Scorecard/chunk count mismatch | Advisory warning — chunk count takes precedence. Human decides. |
| Retroactive evidence gaps | If git commits can't be mapped to chunks cleanly, flag unmapped commits for human assignment. |

## References

- Superpowers framework: brainstorming → spec → plan → subagent execution
- GovZero ADR lifecycle: `docs/governance/GovZero/adr-lifecycle.md`
- OBPI decomposition matrix: `docs/governance/GovZero/obpi-decomposition-matrix.md`
- Ledger schema: `docs/governance/GovZero/ledger-schema.md`
- Pool ADRs for REQ/TASK tiers: `ADR-pool.spec-triangle-sync`, `ADR-pool.tests-for-spec`, `ADR-pool.task-level-governance`
- Prior art: the AGENTS.md tidy work (spec + plan + 12 commits) is the first candidate for retroactive booking
