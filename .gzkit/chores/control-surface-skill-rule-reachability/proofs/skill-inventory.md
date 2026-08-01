# Skill Inventory — Control Surface Skill ↔ Rule Reachability Audit (Pass B)

**Generated:** 2026-08-01 (re-run; supersedes the 2026-05-10 pass)
**Scope:** every `SKILL.md` under `.gzkit/skills/**` — the canonical surface.
**Vendor mirrors NOT audited:** `.claude/skills/`, `.agents/skills/`, `.github/skills/` are derivatives.
**Catalogs:** `uv run gz skill list` (68 active, retired hidden); `ls .gzkit/rules/` (26 entries → 25 rules + 1 generated subtree map).
**Method:** YAML frontmatter (`name`, `metadata.skill-version`, `last_reviewed`, `model`, `gz_command`) + body regex for `.gzkit/rules/**` and `.claude/rules/**` citations.

## Headline

- **68 active skills** (was 50 at the 2026-05-10 pass; +18).
- **18 skills cite at least one rule file**; **50 of 68 (73.5%) cite none.**
- **4 of those 18 cite the vendor mirror path `.claude/rules/…` rather than canonical `.gzkit/rules/…`** — `skill-surface-sync.md` § Non-negotiable rules #1/#4 names `.gzkit/rules/` canonical and `.claude/rules/` a generated output.
- Retired/consolidated skills no longer ship a tombstone (`skill-surface-sync.md` § Retirement policy — delete-on-retire), so the prior run's 17-row "archived skills" table has no successor: those directories are gone from disk.

## Active skills

| Skill | ver | last_reviewed | model | `gz_command` | Body-cited rules |
|---|---|---|---|---|---|
| `airlineops-parity-scan` | 1.1.1 | 2026-07-12 | haiku | `—` | **none** |
| `ghi-author` | 1.3.1 | 2026-07-25 | sonnet | `—` | `gh-cli.md`, `security-sensitivity.md` |
| `ghi-close` | 2.6.0 | 2026-07-26 | opus | `—` | `tests.md`, `arb.md` (mirror), `gh-cli.md` (mirror), `tool-skill-runbook-alignment.md` (mirror) |
| `ghi-triage` | 5.2.0 | 2026-07-25 | sonnet | `—` | `gh-cli.md` (mirror) |
| `git-sync` | 1.2.4 | 2026-07-25 | haiku | `—` | **none** |
| `gz-adr-audit` | 6.13.0 | 2026-07-26 | opus | `audit` | `tests.md` |
| `gz-adr-closeout-ceremony` | 7.16.0 | 2026-07-26 | opus | `—` | **none** |
| `gz-adr-create` | 6.6.3 | 2026-07-26 | opus | `—` | `governance-core.md` (mirror) |
| `gz-adr-emit-receipt` | 1.0.2 | 2026-07-18 | haiku | `—` | **none** |
| `gz-adr-evaluate` | 6.4.1 | 2026-07-21 | sonnet | `—` | **none** |
| `gz-adr-map` | 1.2.1 | 2026-07-25 | haiku | `state` | **none** |
| `gz-adr-promote` | 1.6.0 | 2026-06-07 | sonnet | `—` | **none** |
| `gz-adr-status` | 1.12.1 | 2026-06-10 | haiku | `adr status` | **none** |
| `gz-adr-sync` | 7.1.0 | 2026-06-07 | haiku | `register-adrs` | **none** |
| `gz-advisor-qc` | 0.1.0 | 2026-06-15 | sonnet | `gz content advise-rendition` | **none** |
| `gz-agent-sync` | 1.1.1 | 2026-07-12 | haiku | `—` | **none** |
| `gz-airlock` | 1.1.0 | 2026-07-28 | haiku | `airlock` | **none** |
| `gz-arb` | 1.1.0 | 2026-06-07 | haiku | `arb advise` | **none** |
| `gz-check` | 1.5.0 | 2026-07-27 | haiku | `—` | `tests.md` |
| `gz-check-config-paths` | 0.1.1 | 2026-07-25 | haiku | `—` | **none** |
| `gz-chore-runner` | 1.3.0 | 2026-07-21 | sonnet | `—` | **none** |
| `gz-chores` | 0.1.1 | 2026-07-25 | haiku | `—` | **none** |
| `gz-cli-audit` | 0.1.1 | 2026-07-25 | haiku | `—` | **none** |
| `gz-competitor-radar` | 1.0.1 | 2026-07-25 | opus | `—` | **none** |
| `gz-complexity-advisor` | 0.1.2 | 2026-07-25 | opus | `complexity advise` | **none** |
| `gz-complexity-distill` | 0.2.1 | 2026-07-25 | opus | `complexity distill` | `complexity-doctrine.md`, `skill-surface-sync.md`, `tool-skill-runbook-alignment.md` |
| `gz-complexity-guide` | 0.1.2 | 2026-07-25 | sonnet | `complexity guide` | **none** |
| `gz-constitute` | 0.1.1 | 2026-07-25 | opus | `—` | **none** |
| `gz-content-compose` | 1.0.0 | 2026-06-14 | sonnet | `gz content compose` | **none** |
| `gz-content-remember` | 0.1.0 | 2026-06-05 | haiku | `gz content remember` | **none** |
| `gz-context` | 0.5.0 | 2026-07-13 | haiku | `—` | **none** |
| `gz-context-diet` | 1.1.1 | 2026-07-25 | sonnet | `chores show instructions-files-diet` | **none** |
| `gz-deps-upgrade` | 1.1.0 | 2026-06-22 | haiku | `—` | **none** |
| `gz-design` | 1.4.0 | 2026-07-28 | opus | `—` | **none** |
| `gz-flighttest` | 0.1.0 | 2026-07-05 | sonnet | `—` | **none** |
| `gz-foundation-triage` | 1.0.1 | 2026-06-27 | sonnet | `—` | **none** |
| `gz-governance` | 0.7.0 | 2026-07-26 | haiku | `—` | **none** |
| `gz-implement` | 0.1.1 | 2026-07-25 | haiku | `—` | **none** |
| `gz-init` | 6.0.1 | 2026-07-15 | sonnet | `init` | **none** |
| `gz-insights-remember` | 0.1.0 | 2026-07-13 | haiku | `gz insights remember` | **none** |
| `gz-issue-file` | 1.0.1 | 2026-07-25 | sonnet | `—` | `agent-failure-modes.md`, `gh-cli.md` |
| `gz-justify` | 6.1.1 | 2026-07-21 | opus | `justify` | **none** |
| `gz-manage` | 0.5.0 | 2026-07-12 | haiku | `—` | **none** |
| `gz-migrate-semver` | 0.1.1 | 2026-07-25 | haiku | `—` | **none** |
| `gz-mx` | 1.0.1 | 2026-07-24 | haiku | `mx` | `mx-mode.md` |
| `gz-obpi-brief-drift` | 0.5.0 | 2026-07-26 | haiku | `gz obpi brief-drift` | **none** |
| `gz-obpi-lock` | 6.2.0 | 2026-07-26 | haiku | `—` | **none** |
| `gz-obpi-pipeline` | 6.32.0 | 2026-07-26 | sonnet | `—` | **none** |
| `gz-obpi-simplify` | 6.1.0 | 2026-07-26 | sonnet | `—` | **none** |
| `gz-obpi-specify` | 1.8.0 | 2026-07-26 | opus | `—` | **none** |
| `gz-obpi-sync` | 3.3.0 | 2026-07-26 | sonnet | `—` | `skill-surface-sync.md` |
| `gz-ontology` | 0.1.0 | 2026-07-06 | haiku | `—` | **none** |
| `gz-patch-release` | 1.9.0 | 2026-07-25 | sonnet | `—` | `changelog-release-notes.md` |
| `gz-plan` | 1.3.3 | 2026-07-25 | opus | `—` | **none** |
| `gz-plan-audit` | 6.4.0 | 2026-07-26 | sonnet | `—` | **none** |
| `gz-prd` | 0.1.1 | 2026-07-25 | opus | `—` | **none** |
| `gz-project` | 0.3.1 | 2026-07-25 | haiku | `—` | **none** |
| `gz-pythonic-pattern-apply` | 1.0.1 | 2026-07-25 | sonnet | `chores run pythonic-design-pattern-application` | `tests.md` |
| `gz-pythonic-pattern-detect` | 1.0.1 | 2026-07-25 | sonnet | `chores run pythonic-design-pattern-detection` | `tests.md` |
| `gz-quality` | 0.3.1 | 2026-07-25 | haiku | `—` | **none** |
| `gz-session-handoff` | 6.20.0 | 2026-07-29 | sonnet | `—` | **none** |
| `gz-skill-router` | 6.3.0 | 2026-07-26 | haiku | `—` | **none** |
| `gz-state` | 0.1.1 | 2026-07-25 | haiku | `—` | **none** |
| `gz-status` | 1.1.0 | 2026-06-07 | haiku | `—` | **none** |
| `gz-tech-debt-review` | 1.3.0 | 2026-07-09 | sonnet | `—` | `pythonic.md` (mirror) |
| `gz-tidy` | 1.1.1 | 2026-07-12 | haiku | `—` | **none** |
| `gz-validate` | 0.1.1 | 2026-07-25 | haiku | `—` | **none** |
| `gz-workflow` | 0.2.1 | 2026-07-25 | haiku | `—` | **none** |

## Rule corpus reference (live, 2026-08-01)

`ls .gzkit/rules/` returns 26 entries. One (`complexity-thresholds.json`) is data;
one (`AGENTS.md`) is a **generated** subtree-instructions map, not a rule —
`uv run gz validate --unscoped-rules` confirms the rule population: *"25 rule
file(s) checked"*.

| Rule | body `rule-version` | `paths:` frontmatter |
|---|---|---|
| `adr-audit.md` | 0.2.0 | `docs/design/adr/**` |
| `agent-failure-modes.md` | 0.4.0 | `AGENTS.md`, `.gzkit/rules/**`, `docs/governance/**` |
| `agents-md-map-doctrine.md` | 0.3.0 | `AGENTS.md`, `CLAUDE.md`, `.claude/rules/*.md` |
| `brief-heading-conventions.md` | 0.1.0 | `docs/design/adr/**/obpis/**` |
| `changelog-release-notes.md` | 1.1.0 | `CHANGELOG.md`, `RELEASE_NOTES.md` |
| `chores.md` | 0.3.0 | `src/gzkit/chores/**`, `.gzkit/chores/**` |
| `cli.md` | 0.3.0 | `src/gzkit/commands/**` |
| `complexity-doctrine.md` | 0.3.1 | `docs/governance/complexity/**`, `data/exemplar_corpus.json`, `src/gzkit/complexity/**`, self |
| `complexity-thresholds.md` | 0.4.0 | self, `complexity-thresholds.json`, `src/gzkit/complexity/thresholds.py`, `src/gzkit/schemas/complexity_thresholds.json`, `docs/governance/complexity/**` |
| `cross-platform.md` | 0.5.0 | `src/**/*.py`, `tests/**/*.py` |
| `gate5-runbook-code-covenant.md` | 0.2.0 | `docs/**`, `src/gzkit/**` |
| `gh-cli.md` | 0.3.0 | `.github/**`, `docs/design/adr/**`, `src/gzkit/commands/issue_cmd.py` |
| `governance-core.md` | 0.7.0 | `**/*` |
| `guardrail-feedback-prose.md` | 0.1.0 | `src/gzkit/hooks/**`, `src/gzkit/governance/**`, `.claude/hooks/**` |
| `hexagonal-architecture.md` | 0.2.0 | `**/*.py` |
| `model-selection.md` | 0.3.0 | `src/gzkit/pipeline_runtime.py`, `.gzkit/skills/**/SKILL.md`, `.claude/agents/**` |
| `models.md` | 0.1.0 | `src/**/*.py` |
| `mx-mode.md` | 1.0.1 | `src/gzkit/mx/**`, `.gzkit/skills/gz-mx/**`, `.claude/hooks/mx-awareness.py`, `src/gzkit/mx/awareness.py` |
| `pythonic.md` | 0.2.0 | `**/*.py` |
| `security-sensitivity.md` | 0.5.1 | `docs/design/adr/**/obpis/**`, `data/security_surfaces.json` |
| `skill-surface-sync.md` | 0.10.0 | `.claude/**`, `.gzkit/skills/**`, `.gzkit/rules/**`, `.github/skills/**`, `.github/instructions/**` |
| `task-discovery.md` | 0.5.0 | `src/gzkit/**`, `docs/design/adr/**`, `.gzkit/**` |
| `tests.md` | 0.13.0 | `tests/**` |
| `token-block-discipline.md` | 0.3.0 | `src/gzkit/lock_manager.py`, `src/gzkit/commands/obpi_lock.py`, `src/gzkit/commands/obpi_complete.py`, `.gzkit/handoffs/**`, `scripts/session_orientation.py` |
| `tool-skill-runbook-alignment.md` | 0.2.0 | `src/gzkit/commands/**`, `src/gzkit/cli/**`, `.gzkit/skills/**` |

### Rules new since the 2026-05-10 pass (6)

`agents-md-map-doctrine.md`, `changelog-release-notes.md`, `guardrail-feedback-prose.md`,
`hexagonal-architecture.md`, `mx-mode.md`, `task-discovery.md`. **None of the six is cited
by more than one skill; four are cited by none.**

### Citation counts by rule (canonical + mirror paths, exact filename match)

| Rule | # skills citing | Citing skills |
|---|---|---|
| `tests.md` | 5 | `gz-adr-audit`, `ghi-close`, `gz-check`, `gz-pythonic-pattern-detect`, `gz-pythonic-pattern-apply` |
| `gh-cli.md` | 4 | `ghi-author`, `ghi-close`, `ghi-triage`, `gz-issue-file` |
| `skill-surface-sync.md` | 2 | `gz-complexity-distill`, `gz-obpi-sync` |
| `tool-skill-runbook-alignment.md` | 2 | `ghi-close`, `gz-complexity-distill` |
| `agent-failure-modes.md` | 1 | `gz-issue-file` |
| `changelog-release-notes.md` | 1 | `gz-patch-release` |
| `complexity-doctrine.md` | 1 | `gz-complexity-distill` |
| `governance-core.md` | 1 | `gz-adr-create` |
| `mx-mode.md` | 1 | `gz-mx` |
| `pythonic.md` | 1 | `gz-tech-debt-review` |
| `security-sensitivity.md` | 1 | `ghi-author` |
| `adr-audit.md` · `agents-md-map-doctrine.md` · `brief-heading-conventions.md` · `chores.md` · `cli.md` · `complexity-thresholds.md` · `cross-platform.md` · `gate5-runbook-code-covenant.md` · `guardrail-feedback-prose.md` · `hexagonal-architecture.md` · `model-selection.md` · `models.md` · `task-discovery.md` · `token-block-discipline.md` | **0** | — |

**14 of 25 rules (56%) are named by no skill body.** Note `hexagonal-architecture.md`
scores zero despite two apparent hits: `gz-design:137` and `gz-patch-release:65`
both cite **`docs/governance/hexagonal-architecture.md`**, a same-named file that
is not the rule. See `reachability-matrix.md` § Name-collision hazard.
