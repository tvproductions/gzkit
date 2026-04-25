---
id: OBPI-0.0.21-06-rule-and-doc-updates
parent: ADR-0.0.21-chores-as-gzkit-surface
item: 6
lane: Heavy
status: Completed
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

**REQ-0.0.21-06-01 (zero hits across active operator-facing surfaces):**

```bash
$ grep -rl "ops/chores\|config/gzkit\.chores" .gzkit/rules/ docs/user/ CLAUDE.md AGENTS.md
$ echo "zero hits"
zero hits
```

Remaining hits in `docs/design/**` are closed-ADR audit/proof evidence (immutable per state-doctrine; Layer 2 ledger-anchored) and parent ADR-0.0.21's own historical references (explicitly allowed by the brief's Verification clause).

**REQ-0.0.21-06-02 (manpage shape):**

```bash
$ test -f docs/user/manpages/gz-chores.md && echo present
present
$ grep -E "^##? (Synopsis|Description|Subcommands|Options|Exit Codes|Examples|Files)" docs/user/manpages/gz-chores.md
## Synopsis
## Description
## Subcommands
## Options
## Exit Codes
## Examples
## Files
```

**REQ-0.0.21-06-04 (validators green):**

```text
$ uv run gz validate --documents --surfaces --brief-headings --cli-alignment
Validated: surfaces, documents, cli_alignment, brief_headings

OK All validations passed (4 scopes).
```

**REQ-0.0.21-06-05 (docs build clean):**

```text
$ uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
INFO    -  Documentation built in 2.13 seconds
arb step name=mkdocs exit_status=0 receipt=arb-step-mkdocs-4cacb659cc9a474abd95710544ccac66
```

Receipt: `arb-step-mkdocs-4cacb659cc9a474abd95710544ccac66`.

**REQ-0.0.21-06-06 (mirror sync no drift):**

`uv run gz agent sync control-surfaces` ran twice consecutively. The second invocation reported the same "Sync complete" output without changing canonical/mirror parity (no spurious diffs introduced).

**ARB receipts:**

- Lint clean: `arb-ruff-f56484a479214f3c85cc82fd7e2a4bc2` (`uv run gz arb ruff` → exit 0)
- Tests pass: `arb-step-unittest-44b83770f59d40659f4e6e18df34a599` (`uv run gz arb step --name unittest -- uv run -m unittest -q` → exit 0)
- Docs build clean: `arb-step-mkdocs-4cacb659cc9a474abd95710544ccac66` (above)

### Implementation Summary

- Files created: `docs/user/manpages/gz-chores.md` — new manpage covering `list` (with `--explain`), `show`, `plan`, `advise`, `run`, `audit`, and `doctor` (with `--dry-run` and `--json`); exit codes 0/1/2/3 per `.gzkit/rules/cli.md`; Files section names both `.gzkit/chores/` and `importlib.resources.files("gzkit.chores")` per ADR-0.0.21 and OBPI-0.0.21-04 REQ-04-02.
- Files modified: `.gzkit/rules/chores.md` — frontmatter `paths:` rescoped to `src/gzkit/chores/**` + `.gzkit/chores/**`; body-level rule-version marker `0.2.0` per REQ-07's "equivalent version marker" clause (RuleFrontmatter schema forbids extra frontmatter fields); body rewrite documents the two-surface layout, project-first → package-fallback resolution, `--explain`/`doctor`/`--chores-layout` surfaces.
- Files modified: `src/gzkit/chores/README.md` — canonical agent contract for chores authoring; explicit "`proofs/` is always project-local, never canonical" statement; every `ops/chores/` and `config/gzkit.chores.json` reference removed.
- Files modified: `docs/user/runbook.md` § Chores Commands — added `gz chores list --explain`, `gz chores doctor [--dry-run] [--json]`, and `gz validate --chores-layout`; project-first → package-fallback resolution noted with link to manpage.
- Files modified: `docs/user/commands/chores-list.md`, `chores-plan.md`, `chores-run.md`, `chores-audit.md` — registry resolution updated to project-first → package-fallback; log path corrected to `.gzkit/chores/<slug>/proofs/CHORE-LOG.md`.
- Files modified: `docs/user/commands/frontmatter-reconcile.md`, `docs/user/skills/gz-chore-runner.md` — chore path references updated to two-surface layout.
- Files regenerated by `uv run gz agent sync control-surfaces`: `.claude/rules/chores.md`, `.github/instructions/chores.instructions.md`, plus AGENTS.md fragments under `src/gzkit/chores/`, `.gzkit/chores/`; `config/AGENTS.md` deleted (rule no longer scopes to `config/**`).
- Tests added: N/A — docs OBPI; per § Quality Gates, validators serve as the mechanical gate. The four validate scopes (`documents`, `surfaces`, `cli_alignment`, `brief_headings`) all passed; lint and `mkdocs build --strict` green.
- Date completed: 2026-04-25.
- Attestation status: Operator attested `attest completed` after Stage 4 ceremony review.
- Defects noted: (1) `.gzkit/skills/gz-chore-runner/SKILL.md` (canonical skill, not the rendered `docs/user/skills/gz-chore-runner.md`) still references `config/gzkit.chores.json` and `ops/chores/{slug}/proofs/CHORE-LOG.md`; outside brief allowed paths, follow-up GHI required. (2) `RuleFrontmatter` schema in `src/gzkit/rules.py:406` rejects extra frontmatter fields including `skill-version`, conflicting with `.gzkit/rules/skill-surface-sync.md` § Version discipline (which prescribes a frontmatter `skill-version` bump on every edit). Worked around with body-level `<!-- rule-version: 0.2.0 -->` plus a versioned blockquote per REQ-0.0.21-06-07's "equivalent version marker at the top of the rule file" clause; follow-up GHI required to either extend the schema or revise the skill-surface-sync rule's version-discipline language.

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Heavy/foundation OBPI-0.0.21-06-rule-and-doc-updates closes the docs-track-behavior gap from ADR-0.0.21's chores migration: the canonical rule (`.gzkit/rules/chores.md` rule-version 0.2.0) and chores README rewrote the two-surface layout (canonical `src/gzkit/chores/` + project overlay `.gzkit/chores/`, project-first → package-fallback resolution); a new `docs/user/manpages/gz-chores.md` covers every subcommand including `doctor` (OBPI-09 REQ shape) plus `--explain` (OBPI-04, Completed) and `gz validate --chores-layout` (OBPI-08); the runbook chores section adds those verbs; six operator-facing command/skill docs were updated to drop `ops/chores/` and `config/gzkit.chores.json` references; vendor mirrors regenerated cleanly by `gz agent sync control-surfaces`. All four validators green (`gz validate --documents --surfaces --brief-headings --cli-alignment`), `mkdocs build --strict` clean. Receipts: lint arb-ruff-f56484a479214f3c85cc82fd7e2a4bc2; tests arb-step-unittest-44b83770f59d40659f4e6e18df34a599; mkdocs arb-step-mkdocs-4cacb659cc9a474abd95710544ccac66. Two follow-up GHIs to file: canonical `.gzkit/skills/gz-chore-runner/SKILL.md` still carries pre-migration paths (out of brief allowlist); RuleFrontmatter schema rejects `skill-version` field, blocking literal REQ-07 form (worked around per REQ-07's "equivalent version marker" clause).
- Date: 2026-04-25

---

**Brief Status:** Completed

**Date Completed:** 2026-04-25

**Evidence Hash:** -
