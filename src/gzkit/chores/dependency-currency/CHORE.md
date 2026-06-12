# CHORE: Dependency Currency (Tooling Stack Drift Scan)

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `dependency-currency`

---

## Overview

Scan gzkit's external tooling stack — uv, ruff, ty, pre-commit hook pins,
runtime/dev dependencies in `pyproject.toml`, GitHub Actions runner pins —
against upstream latest releases and surface drift as a markdown report.

**Mode: scan-only.** This chore prints a drift report; the operator
applies bumps. Auto-bump is intentionally not in this chore's scope —
dependency bumps deserve case-by-case judgment (changelogs, breaking
changes, security advisories) before landing on `main`.

**Out of scope (hard rules):** Never touches gzkit's own `version` line in
`pyproject.toml`, `src/gzkit/__init__.py`, or the README badge — those are
release artifacts under a different governance path. Never proposes a
`requires-python` floor change — that's an operator-authorized decision.

## Source

Operator request 2026-04-24: keep tooling current without rolling into the
gzkit release cadence. Run between OBPI implementations as a hygiene
checkpoint; defer auto-application until the operator sees enough no-drift
runs to trust the scanner.

## Policy and Guardrails

- **Lane:** Lite — read-only scan, no source edits, no test gates triggered
- **Network:** Required (queries GitHub releases API and PyPI)
- **Stays out of:** `src/gzkit/`, `tests/`, `docs/`, gzkit's own version
  surfaces

## Workflow

### 1. Inventory installed versions

```bash
uv self version
uv run ruff --version
uvx ty --version
uv run python -c "from importlib.metadata import version; \
    print('pydantic', version('pydantic')); \
    print('rich', version('rich')); \
    print('behave', version('behave'))"
grep -E '^\s*-\s*repo:|^\s*rev:' .pre-commit-config.yaml
grep -rE 'runs-on:' .github/workflows/
grep '^requires-python' pyproject.toml
```

### 2. Query upstream latest

```bash
gh api repos/astral-sh/uv/releases/latest --jq .tag_name
gh api repos/astral-sh/ruff/releases/latest --jq .tag_name
gh api repos/astral-sh/ty/releases/latest --jq .tag_name 2>/dev/null || echo "no-releases"
gh api repos/pydantic/pydantic/releases/latest --jq .tag_name
gh api repos/Textualize/rich/releases/latest --jq .tag_name
gh api repos/behave/behave/releases/latest --jq .tag_name
# Pre-commit hooks: for each `repo:` URL in .pre-commit-config.yaml, query that repo's latest release
# GHA runners: compare `runs-on: ubuntu-XX.YY` against GitHub Actions documented current default
```

### 3. Build drift report

Markdown table written to
`.gzkit/chores/dependency-currency/proofs/drift-report-YYYY-MM-DD.md`:

| Surface | Current | Latest | Delta | Notes |
|---------|---------|--------|-------|-------|
| uv | … | … | major/minor/patch | … |
| ruff | … | … | … | … |
| (etc.) | | | | |

### 4. Operator action (out-of-chore)

The operator reviews the drift report and decides bump-by-bump:

- Read upstream changelog before bumping
- Bump one tool per commit (`chore(deps): bump <tool> <old>→<new>`)
- Run `uv sync && uv run gz check` after each bump
- Do not bundle multiple bumps unless they're related and individually
  green

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run gz lint` | 0 |
| exitCodeEquals | `uv run gz typecheck` | 0 |

The chore itself does not gate on the drift report's content — drift is
informational. The acceptance criteria pin that the chore did not
accidentally regress the project's lint/typecheck baseline (the
gzkit-wrapped commands honor configured exclusions).

## Evidence Commands

```bash
uv self version > .gzkit/chores/dependency-currency/proofs/uv-version.txt
uv run ruff --version > .gzkit/chores/dependency-currency/proofs/ruff-version.txt
uvx ty --version > .gzkit/chores/dependency-currency/proofs/ty-version.txt
gh api repos/astral-sh/uv/releases/latest --jq .tag_name > .gzkit/chores/dependency-currency/proofs/uv-latest.txt
gh api repos/astral-sh/ruff/releases/latest --jq .tag_name > .gzkit/chores/dependency-currency/proofs/ruff-latest.txt
```

## Known Gaps (Baseline 2026-04-24)

None — chore is freshly registered. First run will establish the
baseline drift snapshot.

---

**End of CHORE: Dependency Currency**
