# Plan: OBPI-0.0.57-03-foundation-triage-skill

## Context

ADR-0.0.57 § Decision item 2: "A gz-foundation-triage on-demand skill ranks the
in-flight foundation backlog by priority: cross-references agent-insights.jsonl
signal count, GHI occurrence count, and declared invariants; flags foundation
gaps blocking waiting pool features and port/adapter reclassification candidates;
diagnosis only, ephemeral ranked report."

This OBPI authors the skill body, bundled triage helper script, and the
`gzkit.foundation` composer subpackage. Rubric scoring stays out (OBPI-04).
Pattern: mirrors ghi-triage (three-step: mechanical pre-pass → agent cognitive
pass → deterministic rendering) and the pool-triage-cognitive-pass port/adapter
reclassification check.

**OBPI:** OBPI-0.0.57-03 (foundation-triage-skill)
**ADR:** ADR-0.0.57-foundation-adr-nominal-id-triage
**Lane:** Heavy (Gates 1–5 + docs build)

## Files

**Create:**
- `.gzkit/skills/gz-foundation-triage/SKILL.md` — canonical skill body
- `.gzkit/skills/gz-foundation-triage/scripts/triage.py` — bundled deterministic helper
- `src/gzkit/foundation/__init__.py` — new subpackage
- `src/gzkit/foundation/triage.py` — composer module (diagnosis-only)
- `tests/test_foundation_triage_skill.py` — REQ-derived tests
- `src/gzkit/skills/gz-foundation-triage/SKILL.md` — wheel copy (via sync)

## Steps

### Task 1: Write failing tests (TDD Red)

Create `tests/test_foundation_triage_skill.py`. Each class covers one REQ. All
must FAIL before implementation.

```
from gzkit.skills import _parse_frontmatter   # frontmatter validation
import importlib.util                          # dynamic script load
from gzkit.foundation.triage import ...       # composer module (will fail until Task 4)
```

- **TestREQ01** `@covers("REQ-0.0.57-03-01")`: Read `.gzkit/skills/gz-foundation-triage/SKILL.md`, parse frontmatter, assert `name == "gz-foundation-triage"` and `description` contains "rank the in-flight foundation backlog by priority". Call `uv run gz validate --surfaces` via subprocess; assert exit 0.
- **TestREQ02** `@covers("REQ-0.0.57-03-02")`: Read SKILL.md body; assert "Step 1" appears before "Step 2" appears before "Step 3" in that exact order.
- **TestREQ03** `@covers("REQ-0.0.57-03-03")`: Call `list_skills()` from `gzkit.skills` or subprocess `uv run gz skill list`; assert `gz-foundation-triage` in output.
- **TestREQ04** `@covers("REQ-0.0.57-03-04")`: Run `triage.py --format json` against the live repo via subprocess; assert `git status --porcelain docs/design/adr/foundation/ .gzkit/ledger.jsonl` is empty afterwards.
- **TestREQ05** `@covers("REQ-0.0.57-03-05")`: Read SKILL.md body; assert "port/adapter reclassification" phrase appears within the Step 2 section.
- **TestREQ06** `@covers("REQ-0.0.57-03-06")`: After `gz agent sync control-surfaces` runs (subprocess), assert byte-equality of canonical vs `src/gzkit/skills/gz-foundation-triage/SKILL.md`, `.claude/skills/gz-foundation-triage/SKILL.md`, `.github/skills/gz-foundation-triage/SKILL.md`, `.agents/skills/gz-foundation-triage/SKILL.md`.

### Task 2: Author canonical SKILL.md

Create `.gzkit/skills/gz-foundation-triage/SKILL.md`.

**Frontmatter:**
```yaml
name: gz-foundation-triage
persona: main-session
description: Rank the in-flight foundation backlog by priority — cross-references
  agent-insights.jsonl signal count, GHI occurrence count, and declared invariants;
  flags port/adapter reclassification candidates; diagnosis only, ephemeral ranked report.
category: adr-lifecycle
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-05-23
metadata:
  skill-version: "1.0.0"
model: sonnet
```

**Body (three-step structure, names all three headings):**

- **Invocation:** `/gz-foundation-triage`
- **Step 1 — Mechanical pre-pass:** Run `triage.py --format json` from `.gzkit/skills/gz-foundation-triage/scripts/`. Output: one record per in-flight foundation ADR with `id`, `status`, `title`, `insight_count`, `ghi_count`, `invariant_mentions`. No rubric scoring (rubric at `src/gzkit/foundation/rubric.py` is the next OBPI's surface).
- **Step 2 — Cognitive pass:** For each record, read the ADR's `§ Intent` and `§ Decision`. Apply the port/adapter reclassification check (mirroring the pool-triage cognitive-pass pattern: "flag any candidate whose scope authors an invariant or prerequisite without which downstream features cannot exist"). Emit rank-input JSON `{id, severity: "urgent"|"next-quarter"|"latent"}` for ranked items; emit `{id, reclassify: "foundation"}` for any pool ADR flagged for reclassification. These two lists are mutually exclusive.
- **Step 3 — Deterministic rendering:** Pass rank-input JSON to `triage.py --format rank`. Output is the deliverable — do not restate it in prose.

**Constraints (diagnos-only invariant):**
- MUST NOT mutate any foundation ADR, ledger entry, or registry
- MUST NOT promote, complete, or change status on any artifact

### Task 3: Author bundled triage.py script

Create `.gzkit/skills/gz-foundation-triage/scripts/triage.py`.

Self-contained stdlib-only script. Parallel structure to `.gzkit/skills/ghi-triage/scripts/triage.py`.

- **`--format json`:** Walk `docs/design/adr/foundation/*/ADR-*.md`. Parse YAML frontmatter. Filter where `status` in `{Draft, Proposed}`. For each, count: insights references in `.gzkit/insights/agent-insights.jsonl` (grep for ADR ID string), invariant mentions in `AGENTS.md` and `.gzkit/rules/*.md`. Output JSON list.
- **`--format rank`:** Accept `--rank-input <path>`. Load rank-input JSON. Join with the `--format json` records for titles. Render a deterministic markdown deliverable: numbered rows, each `N. [severity] ADR-ID: title`.
- **No file mutations** under any code path.
- No rubric scoring calls (rubric doesn't exist until OBPI-04).

### Task 4: Author gzkit.foundation subpackage

Create `src/gzkit/foundation/__init__.py`:
```python
"""gzkit.foundation — in-flight foundation ADR discovery and triage."""
from gzkit.foundation.triage import gather_in_flight_foundations, run_foundation_triage
__all__ = ["gather_in_flight_foundations", "run_foundation_triage"]
```

Create `src/gzkit/foundation/triage.py`:
- `gather_in_flight_foundations(project_root: Path) -> list[dict]` — reads foundation ADR frontmatter, returns Draft/Proposed entries
- `count_signals(project_root: Path, adr_id: str) -> dict` — counts insights and GHI mentions
- `run_foundation_triage(project_root: Path) -> None` — calls `gather_in_flight_foundations` + `count_signals`, prints report to stdout, zero file mutations
- Comment at top: `# Rubric scoring: src/gzkit/foundation/rubric.py (foundation-triage-rubric OBPI)`
- All type annotations; no third-party imports

### Task 5: TDD Green — Make tests pass

After Tasks 2–4, run `uv run -m unittest tests.test_foundation_triage_skill -v`. Fix until all pass.

Run `uv run ruff check . --fix && uv run ruff format .` after each edit.

### Task 6: Run gz agent sync control-surfaces

```bash
uv run gz agent sync control-surfaces
```

This populates:
- `src/gzkit/skills/gz-foundation-triage/SKILL.md`
- `.claude/skills/gz-foundation-triage/SKILL.md`
- `.github/skills/gz-foundation-triage/SKILL.md`
- `.agents/skills/gz-foundation-triage/SKILL.md`

Verify byte-equivalence: `diff .gzkit/skills/gz-foundation-triage/SKILL.md src/gzkit/skills/gz-foundation-triage/SKILL.md`

## Verification

```bash
# Gate 2
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q

# OBPI-scoped
uv run gz arb step --name unittest -- uv run -m unittest tests.test_foundation_triage_skill -v

# Gate 3 (Heavy lane)
uv run mkdocs build --strict

# Surface checks
uv run gz validate --surfaces
uv run gz validate --documents
test -f .gzkit/skills/gz-foundation-triage/SKILL.md
uv run gz skill list | grep '^gz-foundation-triage'

# Mirror parity
diff .gzkit/skills/gz-foundation-triage/SKILL.md src/gzkit/skills/gz-foundation-triage/SKILL.md
diff .gzkit/skills/gz-foundation-triage/SKILL.md .claude/skills/gz-foundation-triage/SKILL.md

# Ephemeral invariant
git status --porcelain docs/design/adr/foundation/ .gzkit/ledger.jsonl
# Expected: empty output
```
