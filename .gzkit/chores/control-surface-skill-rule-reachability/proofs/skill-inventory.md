# Skill Inventory — Control Surface Skill ↔ Rule Reachability Audit (Pass B)

**Generated:** 2026-05-10
**Scope:** every `SKILL.md` under `.gzkit/skills/**`
**Source-of-truth:** YAML frontmatter (name, `skill-version`, `gz_command`) + body grep for `.gzkit/rules/**` citations
**Vendor mirrors not audited:** `.claude/skills/`, `.agents/skills/`, `.github/skills/`

Counts: **67 skills total** — 50 active, 17 archived (description prefixed `ARCHIVED:` / `RENAMED:`). Archived skills are listed once at the bottom with their consolidation target; they are excluded from the reachability matrix (no live procedure to violate).

## Active skills

| Skill slug | skill-version | gz_command (frontmatter) | Allowed paths (inferred) | Body-cited rules |
|---|---|---|---|---|
| airlineops-parity-scan | 1.1.1 | (none) | `../airlineops/**` (canon read), `.gzkit/**` (gzkit overlay), `docs/governance/parity/**` | (none) |
| complexity-advisor | 0.1.0 | `complexity advise` | `src/gzkit/complexity/**`, `.gzkit/rules/complexity-thresholds.md` (preview only) | (none cited) |
| complexity-guide | 0.1.0 | `complexity guide` | `src/gzkit/complexity/**` (read), authoring diff (read) | (none cited) |
| ghi-author | 1.2.0 | (none) | `.github/**` (issue body via gh CLI), `data/security_surfaces.json` (read) | `.claude/rules/gh-cli.md`, `.gzkit/rules/security-sensitivity.md` |
| ghi-close | 2.4.0 | (none) | repo-wide (fix scope varies); `tests/**`, `.gzkit/insights/**`, `.github/**` | `.gzkit/rules/tests.md` (Red-Green-Refactor + Tests assert semantics), `.claude/rules/tool-skill-runbook-alignment.md`, `.claude/rules/gh-cli.md` |
| ghi-triage | 5.1.0 | (none) | read-only across GHIs; render under operator stdout | `.claude/rules/gh-cli.md` |
| git-sync | 1.2.3 | (none — wraps `gz git-sync`) | repo-wide commit/push; pre-commit invokes lint/test | (none cited) |
| gz-adr-audit | 6.7.1 | `audit` | `docs/design/adr/**`, `tests/**` (during evidence remediation), `.gzkit/ledger.jsonl` (read) | `.gzkit/rules/tests.md` (Red-Green-Refactor + REQ semantics) |
| gz-adr-closeout-ceremony | 7.9.0 | (none — orchestrates `gz adr emit-receipt`, `gz attest`) | `docs/design/adr/**`, `.gzkit/ledger.jsonl` (via CLI), commit messages | (none cited in body) |
| gz-adr-create | 6.2.0 | (none — wraps `gz plan create` + `gz obpi specify`) | `docs/design/adr/**`, `.gzkit/ledger.jsonl` | (none cited) |
| gz-adr-emit-receipt | 1.0.1 | (none) | `.gzkit/ledger.jsonl` (via CLI) | (none cited) |
| gz-adr-evaluate | 6.3.0 | (none) | `docs/design/adr/**` (read-only score) | (none cited) |
| gz-adr-map | 1.2.0 | `state` | repo-wide (grep traceability) | (none cited) |
| gz-adr-promote | 1.2.0 | (none — wraps `gz adr promote`) | `docs/design/adr/pool/**` → `docs/design/adr/{foundation,pre-release}/**` | (none cited) |
| gz-adr-status | 1.12.0 | `adr status` | `docs/design/adr/**` (read), `.gzkit/ledger.jsonl` (read) | (none cited) |
| gz-adr-sync | 7.0.0 | `register-adrs` | `docs/design/adr/**`, `docs/governance/GovZero/adr-status.md`, `.gzkit/ledger.jsonl` | (none cited) |
| gz-agent-sync | 1.1.1 | (none — wraps `gz agent sync control-surfaces`) | `.gzkit/skills/**`, `.gzkit/rules/**`, `.claude/**`, `.agents/**`, `.github/**` | (none cited; rule referenced via anti-pattern table) |
| gz-arb | 1.0.2 | `arb advise` | `.gzkit/arb/**`, `.gzkit/ledger.jsonl` (via CLI) | (none cited; arb.md cited in revival note as historical context) |
| gz-check | 1.4.0 | (none — wraps `gz check`) | repo-wide (lint, typecheck, test, format) | (none cited) |
| gz-check-config-paths | (none) | (none — wraps `gz check-config-paths`) | `.gzkit/manifest.json`, `pyproject.toml` (read) | (none cited) |
| gz-chore-runner | 1.1.2 | (none — wraps `gz chores`) | `src/gzkit/chores/**`, `.gzkit/chores/**` | (none cited; chore registry doctrine implicit) |
| gz-cli-audit | (none) | (none — wraps `gz cli audit`) | `src/gzkit/commands/**`, `src/gzkit/cli/**`, `docs/user/manpages/**` | (none cited) |
| gz-competitor-radar | 1.0.0 | (none) | `data/competitors/**`, `docs/governance/competitor-radar/**` | (none cited) |
| gz-complexity-distill | 0.2.0 | `complexity distill` | `data/exemplar_corpus.json`, `docs/governance/complexity/**`, `.gzkit/rules/complexity-doctrine.md` | `.gzkit/rules/complexity-doctrine.md`, `.gzkit/rules/skill-surface-sync.md`, `.gzkit/rules/tool-skill-runbook-alignment.md` |
| gz-constitute | (none) | (none — wraps `gz constitution create`) | `docs/governance/constitution/**` | (none cited) |
| gz-context-diet | 1.0.0 | `chores show instructions-files-diet` | `AGENTS.md`, `CLAUDE.md`, `.claude/rules/**`, `docs/governance/**` | (none cited) |
| gz-deps-upgrade | 1.0.0 | (none) | `pyproject.toml`, `uv.lock` | (none cited) |
| gz-design | 1.2.1 | (none — collaborative dialogue) | `docs/design/adr/pool/**`, `docs/design/adr/**` | (none cited) |
| gz-gates | 1.0.0 | (none — wraps `gz gates`) | `.gzkit/ledger.jsonl` (read), `docs/design/adr/**` (read) | (none cited) |
| gz-implement | (none) | (none — wraps `gz implement`) | `.gzkit/ledger.jsonl` (via CLI), `tests/**` (read) | (none cited) |
| gz-init | 6.0.1 | `init` | `.gzkit/**`, `.claude/**`, `.github/**`, root-level scaffolds | (none cited) |
| gz-issue-file | 1.0.0 | (none — wraps `gz issue file`) | `.github/**` (gh CLI), `src/gzkit/schemas/**` (referenced surface), `.gzkit/rules/**` (referenced) | `.gzkit/rules/gh-cli.md` § Cross-repo filing, `.gzkit/rules/agent-failure-modes.md` § Safeguard circumvention |
| gz-justify | 6.1.0 | `justify` | `.gzkit/justify/**`, GHI/OBPI evidence anchors | (none cited) |
| gz-migrate-semver | (none) | (none — wraps `gz migrate-semver`) | `docs/design/adr/**`, `.gzkit/ledger.jsonl` | (none cited) |
| gz-obpi-lock | 6.0.2 | (none — wraps `gz obpi lock`) | `.gzkit/locks/obpi/**`, `.gzkit/handoffs/**` | (none cited; token-block-discipline implicit) |
| gz-obpi-pipeline | 6.14.3 | (none — wraps `gz obpi pipeline`) | `docs/design/adr/**/obpis/**`, `.gzkit/ledger.jsonl`, repo-wide via stages | (none cited inline; ARB invocation discipline implicit) |
| gz-obpi-reconcile | 3.0.3 | (none — wraps `gz obpi reconcile`) | `docs/design/adr/**/obpis/**`, `.gzkit/ledger.jsonl` | (none cited) |
| gz-obpi-simplify | 6.0.4 | (none) | brief's Allowed Paths (varies per OBPI) | (none cited) |
| gz-obpi-specify | 1.5.0 | (none — wraps `gz obpi specify`) | `docs/design/adr/**/obpis/**` | (none cited; brief-heading-conventions implicit) |
| gz-patch-release | 1.4.0 | (none) | `pyproject.toml`, `RELEASE_NOTES.md`, `src/gzkit/__init__.py`, `README.md`, `.github/**` | (none cited) |
| gz-plan | 1.1.1 | (none — wraps `gz plan create`) | `docs/design/adr/**` | (none cited; defect-fix-routing implicit) |
| gz-plan-audit | 6.2.0 | (none — wraps `gz plan audit`) | `.gzkit/plan-audit/**`, `.gzkit/ledger.jsonl` | (none cited) |
| gz-prd | (none) | (none — wraps `gz prd create`) | `docs/governance/prd/**` | (none cited) |
| gz-pythonic-pattern-apply | 1.0.0 | `chores run pythonic-design-pattern-application` | `.gzkit/chores/pythonic-design-pattern-application/proofs/**`, target `src/**/*.py`, `tests/**/*.py` | `.gzkit/rules/tests.md` § Tests assert semantics + Red-Green-Refactor (invariant 6f) |
| gz-pythonic-pattern-detect | 1.0.0 | `chores run pythonic-design-pattern-detection` | `.gzkit/chores/pythonic-design-pattern-detection/proofs/**`, target `src/**/*.py` | `.gzkit/rules/tests.md` § Tests assert semantics |
| gz-session-handoff | 6.3.0 | (none — wraps `gz session-handoff`) | `.gzkit/handoffs/**` | (none cited; token-block-discipline implicit) |
| gz-skill-router | 6.0.3 | (none) | `.gzkit/skills/**` (read), `.gzkit/manifest.json` (read) | (none cited) |
| gz-state | (none) | (none — wraps `gz state`) | `.gzkit/ledger.jsonl` (read), `docs/design/adr/**` (read) | (none cited) |
| gz-status | (none) | (none — wraps `gz status`) | `.gzkit/ledger.jsonl` (read), `docs/design/adr/**` (read) | (none cited) |
| gz-tech-debt-review | 1.2.1 | (none) | repo-wide (`src/**/*.py`, `tests/**/*.py`, `docs/**`) | `.claude/rules/pythonic.md` (referenced in worked example) |
| gz-tidy | 1.1.1 | (none — wraps `gz tidy`) | repo-wide hygiene | (none cited) |
| gz-validate | (none) | (none — wraps `gz validate --<scope>`) | governance artifacts across `.gzkit/**`, `docs/**`, `src/**` | (none cited inline) |

## Archived skills (consolidated; excluded from matrix)

| Skill | Consolidated into |
|---|---|
| format | gz-check |
| gz-adr-check | gz-adr-audit |
| gz-adr-manager | gz-adr-create |
| gz-adr-autolink | gz-adr-sync |
| gz-adr-recon | gz-adr-sync |
| gz-adr-verification | gz-adr-audit |
| gz-attest | gz-adr-closeout-ceremony |
| gz-audit | gz-adr-closeout-ceremony |
| gz-closeout | gz-adr-closeout-ceremony |
| gz-interview | gz-adr-create (Step 0) |
| gz-obpi-audit | gz-obpi-reconcile |
| gz-obpi-brief | gz-obpi-specify |
| gz-obpi-sync | gz-obpi-reconcile |
| gz-register-adrs | gz-adr-sync |
| gz-specify | gz-obpi-specify (renamed) |
| gz-typecheck | gz-check |
| lint | gz-check |
| test | gz-check |

## Rule corpus reference

For convenience, the 20 canonical rules under `.gzkit/rules/` (with `paths:` frontmatter):

| Rule | `paths:` frontmatter |
|---|---|
| `adr-audit.md` | `docs/design/adr/**` |
| `agent-failure-modes.md` | `AGENTS.md`, `.gzkit/rules/**`, `docs/governance/**` |
| `brief-heading-conventions.md` | `docs/design/adr/**/obpis/**` |
| `chores.md` | `src/gzkit/chores/**`, `.gzkit/chores/**` |
| `cli.md` | `src/gzkit/commands/**` |
| `complexity-doctrine.md` | `docs/governance/complexity/**`, `data/exemplar_corpus.json`, `src/gzkit/complexity/**`, `.gzkit/rules/complexity-doctrine.md` |
| `complexity-thresholds.md` | `.gzkit/rules/complexity-thresholds.md`, `.gzkit/rules/complexity-thresholds.json`, `src/gzkit/complexity/thresholds.py`, `src/gzkit/schemas/complexity_thresholds.json`, `docs/governance/complexity/**` |
| `cross-platform.md` | `src/**/*.py`, `tests/**/*.py` |
| `gate5-runbook-code-covenant.md` | `docs/**`, `src/gzkit/**` |
| `gh-cli.md` | `.github/**`, `docs/design/adr/**`, `src/gzkit/commands/issue_cmd.py` |
| `governance-core.md` | `**/*` |
| `model-selection.md` | `src/gzkit/pipeline_runtime.py`, `.gzkit/skills/**/SKILL.md`, `.claude/agents/**` |
| `models.md` | `src/**/*.py` |
| `pythonic.md` | `**/*.py` |
| `security-sensitivity.md` | `docs/design/adr/**/obpis/**`, `docs/design/adr/**/briefs/**`, `data/security_surfaces.json` |
| `skill-surface-sync.md` | `.claude/**`, `.gzkit/skills/**`, `.gzkit/rules/**`, `.github/skills/**`, `.github/instructions/**` |
| `tests.md` | `tests/**` |
| `token-block-discipline.md` | `src/gzkit/lock_manager.py`, `src/gzkit/commands/obpi_lock.py`, `.gzkit/handoffs/**`, `scripts/session_orientation.py` |
| `tool-skill-runbook-alignment.md` | `src/gzkit/commands/**`, `src/gzkit/cli/**`, `.gzkit/skills/**` |

Notes:

- `gh-cli.md` is the only rule cited by three or more skills (ghi-author, ghi-close, ghi-triage, gz-issue-file).
- `tests.md` is the only rule whose Red-Green-Refactor / "Tests assert semantics, not strings" invariant is cited by name (ghi-close, gz-adr-audit, gz-pythonic-pattern-apply, gz-pythonic-pattern-detect).
- 41 of 50 active skills cite **zero** `.gzkit/rules/**` files in their body — the baseline reachability gap surface.
