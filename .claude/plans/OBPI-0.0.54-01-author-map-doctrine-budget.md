# OBPI-0.0.54-01-author-map-doctrine-budget Implementation Plan

## OBPI Reference

OBPI-0.0.54-01-author-map-doctrine-budget

## Parent ADR

ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine (Heavy, Foundation)

## Context

This OBPI authors the map-not-encyclopedia doctrine contract. No code changes.
No content moved from AGENTS.md (that is OBPI-02 scope). Four deliverables:

1. `.gzkit/rules/agents-md-map-doctrine.md` — the rule file (version 0.1.0)
2. `docs/governance/agents-md-doctrine.md` — the canonical doctrine expansion
3. `data/instructions_files_budget.json` — AGENTS.md 40000→15000, CLAUDE.md 40000→4000
4. `docs/governance/advisory-rules-audit.md` — one new scorecard row (Mechanical)

AGENTS.md will be over the new 15000 budget until OBPI-02 lifts sections.
This transitional over-budget window is by design per ADR § Sequencing.

## Files

- `.gzkit/rules/agents-md-map-doctrine.md` (NEW)
- `docs/governance/agents-md-doctrine.md` (NEW)
- `data/instructions_files_budget.json` (EDIT — two value changes)
- `docs/governance/advisory-rules-audit.md` (EDIT — one scorecard row)

## Steps

### Step 1: Author `.gzkit/rules/agents-md-map-doctrine.md`

Create the rule file at version `0.1.0` with:
- `id:`, `paths:` (AGENTS.md, CLAUDE.md, .claude/rules/*.md), `description:` frontmatter
- `<!-- rule-version: 0.1.0 -->` marker in body (matches existing rule-file conventions)
- The invariant verbatim from ADR § Decision canonical statement:
  *AGENTS.md MUST contain only (a) binding bullet rules, (b) structured tables,
  (c) canonical-link references. AGENTS.md MUST NOT contain (i)-(v).*
- The five prohibited shapes: (i) multi-paragraph rationale prose, (ii) worked
  examples / anti-pattern catalogs, (iii) "Why this is canon" coda blockquotes,
  (iv) narrative pedagogical sections, (v) operative-claims expansions whose
  binding-bullet form already states the rule.

### Step 2: Author `docs/governance/agents-md-doctrine.md`

Create the canonical doctrine expansion. Fresh authoring — not a paraphrase of
AGENTS.md. Structured as the encyclopedia entry the AGENTS.md `Why this contract
is not minimal` link will eventually resolve to. Content derives from:
- ADR § Intent: OpenAI four-failure-mode framing + target TOC table
- ADR § Decision: invariant, five prohibited shapes, budget targets, port/adapter framing
- ADR § Consequences (positive): the mechanical-default graduation path

### Step 3: Update `data/instructions_files_budget.json`

Edit: `AGENTS.md` 40000 → 15000; `CLAUDE.md` 40000 → 4000.
Leave per-rule-file 16000 and `_doc` string unchanged.

### Step 4: Add scorecard entry to `docs/governance/advisory-rules-audit.md`

Add a row for `.gzkit/rules/agents-md-map-doctrine.md`:
- Classification: **Mechanical** (for shape invariant)
- Notation: per-section size targets remain **Judgment** (ADR-0.0.54 § Intent TOC)

### Step 5: Verify

```bash
test -f .gzkit/rules/agents-md-map-doctrine.md
grep -q "0.1.0" .gzkit/rules/agents-md-map-doctrine.md
test -f docs/governance/agents-md-doctrine.md
uv run python -c "import json; b = json.load(open('data/instructions_files_budget.json')); assert b['files']['AGENTS.md'] == 15000; assert b['files']['CLAUDE.md'] == 4000; print('budget OK')"
grep -q "agents-md-map-doctrine" docs/governance/advisory-rules-audit.md
uv run gz validate --documents --advisory-scorecard
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Notes

- Gate 4 BDD waiver: no BDD scenario applies — this OBPI ships a rule file +
  doctrine doc + budget value, not an operator-facing CLI behavior. The
  behavior-bearing surface (conformance validator) lands in OBPI-03.
- Scope boundary: `AGENTS.md` is in the Denied Paths list — zero content moves
  out of AGENTS.md in this OBPI.
- Operator PII: never include the operator's personal email in any created file.
