# CHORE: Dependency Currency (Tooling Stack Drift Scan)

**Lane:** Lite
**Slug:** `dependency-currency`

> **Version 1.3.0 (2026-10-23, RO-9 tranche 4):** complexipy is retired; cognitive
> complexity is gzkit's own score over CPython's `ast`, so the analyzers read are
> Lizard and cohesion, and the parser-support signal is the ceiling gate alone.
>
> **Version 1.2.0 (2026-10-22, RO-9 tranche 4, GHI #1183):** the inventory is
> every declared dependency through `uv tree --outdated --depth 1`, not six
> hand-picked tools (the Overview promised all of `pyproject.toml`; the workflow
> queried six). A new step reads the health of the complexity analyzers the
> gates rest on (Lizard, complexipy, cohesion): a stale release is told apart
> from an abandoned project, and parser support for the `requires-python`
> floor is read, never assumed. Run monthly, and after any change to
> `pyproject.toml` or `uv.lock`.

---

## Overview

Scan gzkit's external tooling stack — uv, ruff, ty, pre-commit hook pins,
runtime/dev dependencies in `pyproject.toml`, GitHub Actions runner pins —
against upstream latest releases and surface drift as a markdown report.

**Mode: scan and recommend.** This chore prints a drift report with a
recommendation per surface; the operator applies bumps. Auto-bump is intentionally not in this chore's scope —
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

### 1. Inventory every declared dependency — observe

```bash
uv self version
uv tree --outdated --depth 1
grep -E '^\s*-\s*repo:|^\s*rev:' .pre-commit-config.yaml
grep -rE 'runs-on:|uses: ' .github/workflows/
grep '^requires-python' pyproject.toml
```

`uv tree --outdated --depth 1` lists every runtime, `dev` and `docs`
dependency once, from the same declaration the lock reads, with
`(latest: …)` beside each one that has moved. No list in this chore restates
them.

### 2. Query the rest of upstream — observe

```bash
gh api repos/astral-sh/uv/releases/latest --jq .tag_name
# Pre-commit hooks: for each `repo:` URL in .pre-commit-config.yaml, query that repo's latest release
# GHA actions and runners: compare each `uses:` pin and `runs-on:` image against its latest release
```

### 2a. Read the complexity analyzers' health — observe

The C/C/C ceiling and the corpus measurement rest on Lizard and cohesion
(GHI #1183); cognitive complexity is gzkit's own, over CPython's `ast`, and has no
analyzer to read. For each:

```bash
curl -s https://pypi.org/pypi/<name>/json | uv run python -c "import json,sys; d=json.load(sys.stdin); r=d['releases'][d['info']['version']]; print(d['info']['version'], r[-1]['upload_time'] if r else 'no files', d['info'].get('requires_python'))"
```

- **Stale or abandoned.** A release older than a year is *stale*; it is
  *abandoned* only on evidence (an archived repository, a maintainer's
  notice), never on age alone. Record which, with the evidence.
- **Parser support.** The tool must parse the `requires-python` floor's
  syntax. `uv run gz validate --complexity-ceiling` refusing a function as
  unmeasured is the observed signal; record any, and never lower a ceiling to
  compensate.

### 3. Build drift report — observe

Markdown table written to
`.gzkit/chores/dependency-currency/proofs/drift-report-YYYY-MM-DD.md`:

| Surface | Current | Latest | Delta | Notes |
|---------|---------|--------|-------|-------|
| uv | … | … | major/minor/patch | … |
| (one row per `uv tree --outdated` dependency, hook, action) | | | | |
| lizard / cohesion | … | … | … | stale or abandoned, with evidence; parser support for the floor |

### 4. Recommend per surface — propose

Add a recommendation to each drift row: **bump now** (patch or minor, no
breaking note in the changelog), **read the changelog first** (major, or a
breaking note), or **hold** (with the reason). The operator applies bumps
through the `gz-deps-upgrade` skill, bump by bump:

- Read upstream changelog before bumping
- Bump one tool per commit (`chore(deps): bump <tool> <old>→<new>`)
- Run `uv sync && uv run gz check` after each bump
- Do not bundle multiple bumps unless they're related and individually
  green

## Acceptance Criteria

Criteria live in `acceptance.json`, which `gz chores run` executes; render them with `uv run gz chores plan dependency-currency`. This section explains them and does not restate them (GHI #1002).

The chore itself does not gate on the drift report's content — drift is
informational. The acceptance criteria pin that the chore did not
accidentally regress the project's lint/typecheck baseline (the
gzkit-wrapped commands honor configured exclusions).

## Evidence Commands

```bash
uv self version > .gzkit/chores/dependency-currency/proofs/uv-version.txt
uv tree --outdated --depth 1 > .gzkit/chores/dependency-currency/proofs/outdated-YYYY-MM-DD.txt
gh api repos/astral-sh/uv/releases/latest --jq .tag_name > .gzkit/chores/dependency-currency/proofs/uv-latest.txt
```

## Known Gaps

- The registry's staleness declaration takes one signal, so the chore is
  scheduled on elapsed time (30 days). The dependency-change trigger is the
  instruction above, not a scheduled signal.

---

**End of CHORE: Dependency Currency**
