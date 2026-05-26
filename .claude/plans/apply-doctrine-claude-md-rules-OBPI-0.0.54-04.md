# Plan: OBPI-0.0.54-04-apply-doctrine-claude-md-rules

**OBPI:** OBPI-0.0.54-04-apply-doctrine-claude-md-rules
**Parent ADR:** ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine
**Lane:** Heavy
**Context:** Apply map-not-encyclopedia doctrine to CLAUDE.md and `.gzkit/rules/*.md`.
Pre-audit found CLAUDE.md clean (1,443 chars, zero prohibited shapes). Six rule
files have prohibited headings; two need Rationale prose lifted to expansion docs.

## Pre-audit findings (govern task scope)

**CLAUDE.md — CLEAN:**
- 1,443 chars (budget: 4,000 ✓)
- Zero prohibited shapes, zero prohibited titles, zero "Why X" blockquotes
- Deliverable: audit receipt recorded in Implementation Summary; no edits

**`.gzkit/rules/*.md` violations:**

| File | Issue | Fix |
|------|-------|-----|
| `models.md` | `## Anti-Patterns (DO NOT USE)` heading | Rename → `## Do Not` |
| `security-sensitivity.md` | `## Anti-patterns` heading | Rename → `## Do Not` |
| `gate5-runbook-code-covenant.md` | `## Anti-patterns` heading | Rename → `## Do Not` |
| `complexity-doctrine.md` | `## Corpus Anti-Patterns (binding — any disqualifies)` heading | Rename → `## Corpus Disqualifiers (binding — any disqualifies)` |
| `model-selection.md` | `## Anti-patterns` heading + `## Rationale` prose | Rename + lift prose to expansion doc |
| `skill-surface-sync.md` | `## Anti-patterns` heading + `## Rationale` prose | Rename + lift prose to expansion doc |

**Budget:** `.claude/rules/*.md` glob at 16,000; max file after lifts ~14,317 → tighten to 15,500.

## Files

**Allowed paths (from OBPI brief):**
- `CLAUDE.md` (audit only — no edits expected)
- `.gzkit/rules/` (canonical — edit surface)
- `docs/governance/` (expansion docs for lifted prose)
- `data/instructions_files_budget.json`
- `docs/user/runbook.md`
- `docs/governance/governance_runbook.md`
- `docs/design/adr/foundation/ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine/**`

**Do NOT edit:**
- `AGENTS.md`
- `.gzkit/rules/agents-md-map-doctrine.md` (OBPI-01)
- OBPI-02 lift targets (prime-directive.md, behavior-rules.md, etc.)
- `src/gzkit/governance/trust_audits/agents_md_map_conformance.py` (OBPI-03)
- `.claude/rules/` (mirror — propagate via `gz agent sync control-surfaces` only)

## Steps

### Step 1: Record CLAUDE.md clean audit

Record the CLAUDE.md audit receipt in the Implementation Summary.
No file edits. CLAUDE.md (1,443 chars) passes all five prohibited-shape checks:
(i) no multi-paragraph rationale, (ii) no anti-pattern/worked-example headings,
(iii) no "Why X is canon" blockquotes, (iv) no pedagogical sections,
(v) no operative-claims expansions.

Files touched: none (audit receipt only).

### Step 2: Fix heading-only violations in simple rule files

Rename prohibited headings in three files — content under the headings is
binding bullets and remains unchanged:

- `.gzkit/rules/models.md`: `## Anti-Patterns (DO NOT USE)` → `## Do Not`
- `.gzkit/rules/security-sensitivity.md`: `## Anti-patterns` → `## Do Not`
- `.gzkit/rules/gate5-runbook-code-covenant.md`: `## Anti-patterns` → `## Do Not`
- `.gzkit/rules/complexity-doctrine.md`:
  `## Corpus Anti-Patterns (binding — any disqualifies)` →
  `## Corpus Disqualifiers (binding — any disqualifies)`

Files touched: 4 rule files.

### Step 3: Fix model-selection.md (rename + lift Rationale)

1. Rename `## Anti-patterns` → `## Do Not` (content unchanged: 5 binding bullets)
2. Lift `## Rationale` prose to new expansion doc:
   - Create `docs/governance/model-selection-rationale.md` containing the verbatim
     prose under a `## Rationale` heading with proper governance header
   - Replace `## Rationale` + prose in `.gzkit/rules/model-selection.md` with:
     `See [Model-Selection Rationale](../../docs/governance/model-selection-rationale.md)`
     as a one-line pointer after the decision matrix

Files touched: `.gzkit/rules/model-selection.md`, `docs/governance/model-selection-rationale.md` (new)

### Step 4: Fix skill-surface-sync.md (rename + lift Rationale)

1. Rename `## Anti-patterns` → `## Do Not` (content unchanged: 7 binding bullets)
2. Lift `## Rationale` prose to new expansion doc:
   - Create `docs/governance/skill-surface-sync-rationale.md` containing verbatim prose
   - Replace `## Rationale` + prose in `.gzkit/rules/skill-surface-sync.md` with
     one-line pointer: `See [Skill-Surface-Sync Rationale](../../docs/governance/skill-surface-sync-rationale.md)`

Files touched: `.gzkit/rules/skill-surface-sync.md`, `docs/governance/skill-surface-sync-rationale.md` (new)

### Step 5: Finalize data/instructions_files_budget.json

Update `.claude/rules/*.md` glob budget: 16,000 → 15,500 chars.
Rationale: largest file post-lift is ~14,317 chars; 15,500 gives 1,183 chars buffer.
AGENTS.md stays at 32,000 (set by OBPI-0.0.54-03; 5k destination deferred to ADR-0.0.37).
Update `_doc` field to record this OBPI-04 tightening.

Files touched: `data/instructions_files_budget.json`

### Step 6: Update runbooks

Per `.claude/rules/gate5-runbook-code-covenant.md` — runbook updates land in
the same patch set as the doctrine application.

**`docs/user/runbook.md` § Recovery flows:**
Add the canonical recovery path:
```
- **Instruction-file shape drift** → Run `/gz-context-diet` (or
  `uv run gz chores show instructions-files-diet`). Validator:
  `uv run gz validate --agents-md-map-conformance`.
```

**`docs/governance/governance_runbook.md` § Instruction files:**
Add or update section naming map-not-encyclopedia doctrine as the resting state:
```
CLAUDE.md and `.gzkit/rules/*.md` MUST conform to map-not-encyclopedia shape
(ADR-0.0.54). Shape is enforced by `gz validate --agents-md-map-conformance`.
Recovery: `/gz-context-diet`. Prohibited shapes: multi-paragraph rationale prose,
anti-pattern/worked-example headings, "Why X is canon" blockquotes, pedagogical
sections, operative-claims expansions.
```

Files touched: `docs/user/runbook.md`, `docs/governance/governance_runbook.md`

### Step 7: Cross-link trust-doctrine

Add `gz validate --agents-md-map-conformance` to the promoted-scope catalogue in
`docs/governance/trust-doctrine.md`.

Find the promoted-scope catalogue section and add:
```
| `--agents-md-map-conformance` | CLAUDE.md + `.gzkit/rules/*.md` map-not-encyclopedia shape (ADR-0.0.54-03) |
```

Files touched: `docs/governance/trust-doctrine.md`

### Step 8: Propagate mirror surfaces

After all `.gzkit/rules/*.md` edits are complete:
```bash
uv run gz agent sync control-surfaces
```
This regenerates `.claude/rules/*.md` mirrors from canonical sources. Verify
the renamed headings appear correctly in the mirror files.

Files touched: `.claude/rules/*.md` (generated mirrors)

## Verification

```bash
uv run gz validate --agents-md-map-conformance
uv run gz validate --instructions-files-budget
uv run gz validate --documents --surfaces
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
grep -q "gz-context-diet" docs/user/runbook.md
grep -q "Instruction files" docs/governance/governance_runbook.md
grep -q "agents-md-map-conformance" docs/governance/trust-doctrine.md
```

## Notes

- `.gzkit/rules/AGENTS.md` is a generated composite (do not edit directly; regenerated by `gz agent sync control-surfaces` from individual rule files)
- NEVER include operator's personal email in any artifact
- No pytest — use `uv run -m unittest` per `.gzkit/rules/tests.md`
- No direct edit of `.claude/rules/` mirrors — only via `gz agent sync control-surfaces`

### Step 6b: Stage-4 acceptance ceremony

Present evidence packet for human attestation. (Universal per ADR-0.0.36.)
