---
id: OBPI-0.0.21-06-rule-and-doc-updates
parent: ADR-0.0.21-chores-as-gzkit-surface
item: 6
lane: Heavy
status: Draft
---

# OBPI-0.0.21-06-rule-and-doc-updates: Rule and Documentation Updates

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.21-chores-as-gzkit-surface/ADR-0.0.21-chores-as-gzkit-surface.md`
- **Checklist Item:** #6 — Rule and documentation updates: `.gzkit/rules/chores.md`, runbook, manpage, root `CLAUDE.md`/`AGENTS.md`; migrate `ops/chores/CLAUDE.md` content into `src/gzkit/chores/README.md`.

**Status:** Draft

## Objective

Update every operator-facing doc and rule surface that references the pre-migration layout (`ops/chores/`, `config/gzkit.chores.json`) to reflect the new `.gzkit/chores/` + `src/gzkit/chores/` canonical layout, author a new `gz-chores` manpage, and author `src/gzkit/chores/README.md` as the canonical agent contract for the shipped chores surface. All doc changes propagate through `gz agent sync control-surfaces` to vendor mirrors.

## Lane

**Heavy** — Gate 3 (docs) is load-bearing for this ADR per the parent's Lane Justification. Runbook and manpage changes are external contracts per `.gzkit/rules/gate5-runbook-code-covenant.md`.

## Allowed Paths

- `.gzkit/rules/chores.md` — canonical source; frontmatter `paths:` list + body
- `docs/user/runbook.md` — operator workflow prescriptions
- `docs/user/manpages/gz-chores.md` — NEW manpage (per ground-truth check: no chores manpage currently exists; only `arb.md`, `closeout.md`, `gz-justify.md`, `gz-personas.md`, `patch-release.md`)
- `docs/user/concepts/` — if a concepts page for chores exists, update it; otherwise no-op
- `CLAUDE.md` — project root; update the `Local Agent Rules` references if they mention chores layout
- `AGENTS.md` — project root; update any `ops/chores/` references in the Attestation or DO IT RIGHT sections
- `src/gzkit/chores/README.md` — NEW agent contract (migrated from `ops/chores/CLAUDE.md` in OBPI-01; author the final shape here)
- `docs/governance/GovZero/gzkit-structure.md` — if it diagrams the repo layout, update

## Denied Paths

- `.claude/rules/chores.md`, `.claude/skills/**`, `.github/skills/**`, `.github/instructions/**` — these are vendor mirrors; **never edit directly** per `.claude/rules/skill-surface-sync.md`. Edit `.gzkit/rules/chores.md`, bump `skill-version`, run `gz agent sync control-surfaces`.
- `src/gzkit/**/*.py` — code changes are OBPIs 02-05, 08-09
- `tests/**`, `features/**` — test/BDD are OBPIs 04-05, 07-09
- `pyproject.toml` — packaging is OBPI-03
- `ops/chores/**`, `config/gzkit.chores.json` — removed by OBPI-01; referencing them is a defect

## Requirements (FAIL-CLOSED)

1. `.gzkit/rules/chores.md` MUST have its frontmatter `paths:` list updated to reference `.gzkit/chores/**` and `src/gzkit/chores/**` instead of any `ops/chores/**` or `config/chores/**` patterns. Body MUST describe the two-surface layout (canonical + scaffolded).
2. Every rule file under `.gzkit/rules/` that mentions `ops/chores/` or `config/gzkit.chores.json` in its body MUST be grepped and updated. Scope verification: `grep -rn "ops/chores\\|config/gzkit\\.chores" .gzkit/rules/` MUST return zero hits after this OBPI.
3. `docs/user/runbook.md` MUST prescribe `uv run gz chores {list,show,plan,advise,run}` with examples showing the new resolution order (project-first, package-fallback) where relevant. Existing `gz chores` examples already in the runbook MUST continue to resolve per the invariants in `.gzkit/rules/governance-core.md` § Operator-doc verb resolution.
4. A new manpage `docs/user/manpages/gz-chores.md` MUST exist covering: synopsis, description, every subcommand (`list`, `show`, `plan`, `advise`, `run`, and the NEW `doctor` from OBPI-09), the `--explain` flag (OBPI-04), exit codes (0/1/2/3 per `.gzkit/rules/cli.md`), examples, and a "Files" section naming both `.gzkit/chores/` and `importlib.resources("gzkit.chores")` as resolution sources.
5. `src/gzkit/chores/README.md` (migrated from `ops/chores/CLAUDE.md` in OBPI-01) MUST be the canonical agent contract for chores authoring: what belongs in `CHORE.md`, what belongs in `acceptance.json`, what goes in `proofs/` (and that proofs are project-local, not canonical). The OBPI-01 migration moved the file; this OBPI authors the final shape.
6. Every `gz <verb>` string in the updated docs MUST resolve to a registered CLI verb per `.gzkit/rules/governance-core.md` § Operator-doc verb resolution. `uv run gz validate --cli-alignment` MUST exit 0 after this OBPI.
7. The `.gzkit/rules/chores.md` `skill-version` (or equivalent version marker at the top of the rule file) MUST be bumped per `.claude/rules/skill-surface-sync.md` § Version discipline.
8. After canonical edits, `uv run gz agent sync control-surfaces` MUST be run and the resulting mirror updates committed in the same PR. Mirror drift at merge time is a defect.
9. `uv run mkdocs build --strict` MUST pass. Every cross-reference in edited docs MUST resolve.
10. `uv run gz validate --documents --surfaces --brief-headings` MUST pass.

> STOP-on-BLOCKERS:
> - If the sibling OBPIs introducing `doctor` (OBPI-09), `--explain` (OBPI-04), or the layout validator (OBPI-08) have not yet defined their exact CLI shapes, STOP and wait — documenting a shape that later drifts is the canonical GHI #141-class defect.
> - If editing `.claude/rules/chores.md` directly would be faster, STOP and re-route through `.gzkit/rules/chores.md` + sync. Editing the mirror is explicitly forbidden.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.claude/rules/skill-surface-sync.md` — canonical-first edit + mirror sync protocol
- [ ] `.gzkit/rules/gate5-runbook-code-covenant.md` — docs-track-behavior covenant
- [ ] `.gzkit/rules/governance-core.md` § Operator-doc verb resolution — every `gz <verb>` must resolve
- [ ] Parent ADR ADR-0.0.21 § Decision #11, #12

**Context:**

- [ ] Sibling OBPIs 04, 08, 09 — confirm CLI shapes are stable before documenting
- [ ] `.gzkit/rules/chores.md` current content — preserve invariants that still apply

**Prerequisites:**

- [ ] `src/gzkit/chores/README.md` exists (OBPI-01 migrated `ops/chores/CLAUDE.md` here)
- [ ] New CLI surfaces (`--explain`, `doctor`, `gz validate --chores-layout`) defined by their OBPIs

**Existing Code:**

- [ ] Read `.gzkit/rules/chores.md` whole — identify every `ops/chores/` reference
- [ ] Read `docs/user/runbook.md` and grep `gz chores` — list every example that needs review
- [ ] Read an existing manpage like `docs/user/manpages/gz-personas.md` for shape parity
- [ ] Read `CLAUDE.md` and `AGENTS.md` — grep `ops/chores\\|config/gzkit\\.chores`

## Quality Gates

### Gate 1 (ADR)
- [ ] Intent recorded

### Gate 2 (TDD — Red-Green-Refactor)
- [ ] N/A at the code level — this OBPI is docs-only. Test parity is enforced by `gz validate --documents --surfaces --brief-headings --cli-alignment` treated as the gate.

### Code Quality
- [ ] `uv run gz lint` — docs lint (markdownlint) green
- [ ] `uv run gz validate --documents --surfaces --brief-headings --cli-alignment` — all green

### Gate 3 (Docs) — Heavy
- [ ] `uv run mkdocs build --strict` green
- [ ] `gz agent sync control-surfaces` run; mirrors regenerated without drift

### Gate 4 (BDD) — Heavy
- [ ] Deferred to OBPI-07

### Gate 5 (Human) — Heavy + Foundation
- [ ] Brief-level human attestation

## Verification

```bash
# No stale references survive
grep -rn "ops/chores\|config/gzkit\.chores" .gzkit/rules/ docs/ CLAUDE.md AGENTS.md 2>&1 | grep -v "^Binary" | grep -v ".gzkit/ledger.jsonl" | head
# Expected: empty (or only intentional historical references in ADR-0.0.21 evidence)

# Manpage exists and covers the required sections
test -f docs/user/manpages/gz-chores.md
grep -E "^##? (Synopsis|Description|Options|Examples|Exit Codes|Files)" docs/user/manpages/gz-chores.md

# CLI alignment — every gz <verb> in docs resolves
uv run gz validate --documents --surfaces --brief-headings --cli-alignment

# Docs build
uv run mkdocs build --strict

# Mirror sync shows no drift
uv run gz agent sync control-surfaces 2>&1 | tail -10
```

## Acceptance Criteria

- [ ] REQ-0.0.21-06-01: `grep -rn "ops/chores\\|config/gzkit\\.chores" .gzkit/rules/ docs/ CLAUDE.md AGENTS.md` returns zero hits.
- [ ] REQ-0.0.21-06-02: `docs/user/manpages/gz-chores.md` exists with Synopsis, Description, Options (including `--explain` and `doctor`), Exit Codes (0/1/2/3), Examples, and Files sections.
- [ ] REQ-0.0.21-06-03: `src/gzkit/chores/README.md` documents the canonical agent contract for chores authoring and states that `proofs/` is project-local, never canonical.
- [ ] REQ-0.0.21-06-04: `uv run gz validate --documents --surfaces --brief-headings --cli-alignment` exits 0.
- [ ] REQ-0.0.21-06-05: `uv run mkdocs build --strict` exits 0.
- [ ] REQ-0.0.21-06-06: `uv run gz agent sync control-surfaces` reports no drift after running; vendor mirrors (`.claude/rules/chores.md`, `.github/instructions/**`) are byte-identical to the canonical post-sync.
- [ ] REQ-0.0.21-06-07: `.gzkit/rules/chores.md` has its version marker bumped.

## Completion Checklist

- [ ] **Gate 1:** Intent recorded
- [ ] **Gate 2:** N/A (docs OBPI); validators serve as the mechanical gate
- [ ] **Code Quality:** lint + validate passes
- [ ] **Gate 3:** docs build green; mirrors synced
- [ ] **Gate 5:** human attestation
- [ ] **Value Narrative:** before — docs pointed operators at deleted paths; after — docs match the shipped layout and the manpage surfaces the new `--explain` and `doctor` verbs.
- [ ] **Key Proof:** `grep -rn ops/chores .gzkit/rules/ docs/` returns zero hits.

## Evidence

### Gate 1 (ADR)
- [ ] Intent recorded

### Gate 2 (TDD)
```text
N/A — docs OBPI; validators replace TDD gate per § Quality Gates.
```

### Code Quality
```text
# paste lint output and validate-scope output
```

### Gate 3 (Docs)
```text
# paste mkdocs build --strict and sync output
```

### Gate 5 (Human)
```text
# attestation text
```

### Value Narrative
Before: `.gzkit/rules/chores.md` and the runbook referenced `ops/chores/` paths that no longer existed; operators reading the docs would have tried to write to a deleted tree. After: every operator-facing surface points at the canonical `.gzkit/chores/` overlay and `src/gzkit/chores/` package-shipped source; the new manpage covers `--explain`, `doctor`, and the layout validator.

### Key Proof
```bash
$ grep -rn "ops/chores\|config/gzkit\.chores" .gzkit/rules/ docs/ CLAUDE.md AGENTS.md
$ echo "zero hits"
zero hits
```

### Implementation Summary
- Files created/modified: `.gzkit/rules/chores.md`, `docs/user/runbook.md`, `docs/user/manpages/gz-chores.md` (new), `src/gzkit/chores/README.md`, `CLAUDE.md`, `AGENTS.md`, vendor mirrors via sync
- Tests added: N/A
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>`
- Attestation: `<verbatim user words> — <session-grounded enrichment>`
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
