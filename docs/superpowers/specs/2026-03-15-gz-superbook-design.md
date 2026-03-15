# gz superbook: Superpowers → GovZero Governance Booking

**Date**: 2026-03-15
**Status**: Design approved, pending implementation plan

## Background: Superpowers Framework

[Superpowers](https://github.com/obra/superpowers) is a Claude Code plugin that provides a structured methodology for AI-assisted software engineering. It enforces a disciplined workflow:

1. **Brainstorming** — Socratic dialogue to explore intent, constraints, and alternatives before committing to a design. Produces multiple-choice questions, trade-off comparisons, and approach recommendations.
2. **Spec writing** — The approved design is captured as a formal spec document (`docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`). Specs go through an automated review loop (subagent reviewer identifies gaps, author fixes, re-review until approved) followed by human review.
3. **Plan writing** — The spec is decomposed into an implementation plan (`docs/superpowers/plans/YYYY-MM-DD-<topic>.md`). Plans are structured as **chunks** (logical groupings, ~1000 lines max) containing **tasks** (2-5 minute atomic units) containing **steps** (individual actions: write test, run test, implement, verify, commit). Plans specify exact file paths, complete code, and expected command outputs. Plans also go through automated review.
4. **Execution** — Plans are executed via subagent-driven development: a fresh subagent per task, with two-stage review (spec compliance, then code quality) after each. Implementation follows TDD: write failing test → verify failure → implement → verify pass → commit.
5. **Completion** — Branch finishing with verification gates before merge/PR.

**Key principles:** TDD always, YAGNI ruthlessly, DRY, bite-sized tasks, evidence before assertions, fresh context per task (subagents prevent context pollution).

**Artifacts produced:**
- Spec document (design decisions, architecture, trade-offs)
- Plan document (chunks, tasks, steps, file paths, complete code)
- Git commits (one per task, with meaningful messages)
- Test suite (written before implementation per TDD)

## Problem

Superpowers' plan/task framework produces high-quality implementation artifacts (specs, plans, commits) but these exist outside GovZero's governance ledger. Work completed through superpowers has no ADR, no OBPI briefs, no ledger events, and no formal attestation trail. This creates a governance gap where significant architectural work is invisible to `gz status`, `gz state`, and audit workflows.

The two frameworks are complementary, not competing:
- **Superpowers** provides behavioral methodology — *how* work is done (TDD, decomposition, review discipline)
- **GovZero** provides governance infrastructure — *that* work is tracked (ledger, gates, attestation, audit trail)

`gz superbook` bridges them: it reads superpowers artifacts and books them into GovZero's governance ledger.

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
- `--apply`: write artifacts and emit ledger events. Without this flag, the command runs in dry-run mode (shows draft without writing).

**Semver auto-assignment:** When `--semver` is not provided, superbook scans the ledger for the highest existing `adr_created` semver and increments the minor version. Example: if the highest is `ADR-0.16.0`, the next assigned is `0.17.0`. Foundation semver (`0.0.x`) is never auto-assigned — it requires explicit `--semver 0.0.x`. If the ledger is empty, defaults to `0.1.0`. Collisions are checked before booking — if the semver already exists, the command errors with a suggestion for the next available.

**Slug generation:** The ADR slug is derived from the spec title by lowercasing, replacing spaces with hyphens, and stripping non-alphanumeric characters (matching existing `gz plan` slug logic). Example: "AGENTS.md Tidy: Control Surface Schema and Rules Mirroring" → `agents-md-tidy-control-surface-schema-and-rules-mirroring`, truncated to 50 chars.

**Directory bucket:** ADRs with semver `0.0.x` go to `docs/design/adr/foundation/`. All others go to `docs/design/adr/pre-release/`. This matches the existing directory convention.

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

**Commit-to-chunk mapping algorithm (retroactive only):**

Each commit is assigned to a chunk by file-path overlap. For each commit, compute the set of changed files and intersect with each chunk's file-path set (union of all task file paths in that chunk). The chunk with the highest overlap score wins. Ties are broken by commit chronological order (earlier chunks first). Commits that match no chunk are collected as "unmapped" and presented to the human during review for manual assignment. The mapping is deterministic given the same plan and git history.

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
- OBPI status set to `Pending-Attestation` (not `Completed` — human must still run `gz attest`)
- ADR status set to `Pending-Attestation`
- Evidence sections populated from git commits (SHA, message, files changed)
- Gate 2 (tests) and Gate 3 (lint) are verified by running `gz test` and `gz lint` during booking. Pass/fail results are recorded in the evidence sections. If gates fail, status is set to `Draft` with a warning, not `Pending-Attestation`.
- Gate 5 (human attestation) is never auto-set — the human must run `gz attest` after reviewing the booked artifacts

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

The `source` field is carried in the existing `LedgerEvent.extra` dict (not a new field). Superbook passes `extra={"source": "gz-superbook-retroactive"}` to the existing factory functions (`adr_created_event`, `obpi_created_event`). No ledger schema changes required.

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
    scorecard: dict[str, int]  # {dimension: score} — rendered to text for ADR, not stored as DecompositionScorecard
    obpis: list[OBPIDraft]
```

**Note on model types**: These are the first Pydantic models in the codebase (existing models use stdlib `dataclass`). This is intentional per the ADR-0.15.0 Pydantic migration. Superbook models are internal to the pipeline — they do not replace existing dataclasses. Where interop is needed (e.g., ledger events), superbook calls the existing factory functions which return dataclasses.

## Scope Exclusions

- **TASK-level governance**: Pool ADR dependency — not implemented here. Tasks remain as OBPI work breakdown items.
- **Automatic attestation**: Retroactive mode sets status to `Pending-Attestation`, not `Completed`. Human must run `gz attest` after reviewing the booked artifacts.
- **Superpowers workflow modification**: `gz superbook` wraps superpowers, does not modify its spec/plan/task workflow.

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Markdown parsing fragility | Parser uses heading-level extraction (## Chunk N), not line-by-line parsing. Tolerant of format variations. Test with actual superpowers output. |
| Lane misclassification | Auto-classification is always presented for human review. `--lane` override available. |
| Semver collision with existing ADRs | Check ledger for existing ADR with same semver before booking. Suggest next available. |
| Scorecard/chunk count mismatch | Advisory warning — chunk count takes precedence. Human decides. |
| Retroactive evidence gaps | If git commits can't be mapped to chunks cleanly, flag unmapped commits for human assignment. |
| Duplicate booking | `--apply` checks ledger for existing `adr_created` event with the same semver AND checks filesystem for existing ADR directory. If either exists, the command errors with "already booked" and the existing artifact path. No `--force` flag — if re-booking is needed, delete the artifacts and ledger entries first. |
| Foundational lane interop | "Foundational" is not a formal lane in `GzkitConfig` — it maps to `heavy` with a metadata note `foundation: true` in the ledger event `extra` dict. Auto-classification flags `0.0.x` semvers as foundational for the human review display, but the actual lane field is `heavy`. |

## Relationship to Existing Commands

`gz superbook` creates both ADR and OBPIs in a single operation, unlike the existing two-step `gz plan` + `gz specify` workflow. The generated artifacts are fully interchangeable — they use the same templates, the same ledger events, and are validated by the same `gz validate` and `gz obpi audit` commands. `gz superbook` is a batch-booking shortcut, not a separate artifact type.

## Module Placement

CLI registration lives in `src/gzkit/commands/superbook.py` (thin wrapper matching the `commands/plan.py` pattern). Domain logic lives in root-level modules `src/gzkit/superbook.py` and `src/gzkit/superbook_parser.py`. The parser can reuse `extract_markdown_section` from `src/gzkit/decomposition.py` for heading-based extraction.

## References

- Superpowers framework: brainstorming → spec → plan → subagent execution
- GovZero ADR lifecycle: `docs/governance/GovZero/adr-lifecycle.md`
- OBPI decomposition matrix: `docs/governance/GovZero/obpi-decomposition-matrix.md`
- Ledger schema: `docs/governance/GovZero/ledger-schema.md`
- Pool ADRs for REQ/TASK tiers: `ADR-pool.spec-triangle-sync`, `ADR-pool.tests-for-spec`, `ADR-pool.task-level-governance`
- Prior art: the AGENTS.md tidy work (spec + plan + 12 commits) is the first candidate for retroactive booking
