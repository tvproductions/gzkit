# CHORE: Dependency Currency (Daily Check and Upgrade)

**Lane:** Lite
**Slug:** `dependency-currency`

> **Version 2.0.0 (2026-10-27, operator ruling):** the chore runs daily and brings
> dependencies up to date when it checks. The rung moves from propose to repair;
> the apply step is the `gz-deps-upgrade` procedure. Operator, verbatim: *"the gobal
> rule was wrong... in an environment where AI swarms are always active, a daily
> check of deps is wise. we should bring deps up-to-date when we check."*
>
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
against upstream latest releases, record the drift, and bring every
dependency up to date in the same run.

**Mode: check and upgrade.** Each run writes the drift report, then applies
the `gz-deps-upgrade` procedure: `uv lock --upgrade`, `==` pins moved to
latest, `>=` floors raised to what locked, `.python-version` moved to the
newest patch of the floor's minor, verified by `uv run gz check --full`. A
bump that turns the gate red is pinned at its last-known-good version and
filed as a GHI for the migration; the rest of the upgrade still lands. A floor
is never lowered to make the gate pass.

**Out of scope (hard rules):** Never touches gzkit's own `version` line in
`pyproject.toml`, `src/gzkit/__init__.py`, or the README badge — those are
release artifacts under a different governance path. Never proposes a
`requires-python` floor change — that's an operator-authorized decision.

## Source

Operator request 2026-04-24: keep tooling current without rolling into the
gzkit release cadence. Run between OBPI implementations as a hygiene
checkpoint.

Amended 2026-10-27 (operator ruling, recorded in
`.gzkit/insights/agent-insights.jsonl`): the 2026-04-24 deferral of
auto-application is retired. AI agents change the tree continuously, so a
30-day scan let drift accumulate between reads; the chore now checks daily and
applies what it finds.

## Policy and Guardrails

- **Lane:** Lite — edits `pyproject.toml` dependency entries, `uv.lock` and
  `.python-version` only; `uv run gz check --full` gates the result
- **Network:** Required (queries GitHub releases API and PyPI)
- **Stays out of:** `src/gzkit/`, `tests/`, `docs/`, gzkit's own version
  surfaces, the `requires-python` floor, and the `[tool.uv] required-version`
  floor (a floor by GHI #1283; raised only when the repo needs a newer uv
  feature)
- **One commit per run:** `chore(deps): daily upgrade YYYY-MM-DD`, carrying the
  ARB unittest receipt the `gz-deps-upgrade` skill emits

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

### 4. Upgrade — repair

Apply `.gzkit/skills/gz-deps-upgrade/SKILL.md` steps 3–10 (the uv binary and
global tools are kept current outside the repository). Note each major bump in
the drift report's Notes column with its changelog link.

- **Gate red:** find the offending package, pin it at last-known-good with a
  comment naming the GHI, file the GHI through `ghi-author`, and re-run the
  gate. Never lower a floor to make it pass.
- **Upstream not yet installable** (a release uv cannot resolve, a yanked
  version): hold it, and say why in the Notes column.

## Acceptance Criteria

Criteria live in `acceptance.json`, which `gz chores run` executes; render them with `uv run gz chores plan dependency-currency`. This section explains them and does not restate them (GHI #1002).

The acceptance criteria witness the repaired state: the lock agrees with
`pyproject.toml`, the Python version is declared once and passes the
discipline check, and lint and typecheck hold on the upgraded toolchain (the
gzkit-wrapped commands honor configured exclusions).

## Evidence Commands

```bash
uv self version > .gzkit/chores/dependency-currency/proofs/uv-version.txt
uv tree --outdated --depth 1 > .gzkit/chores/dependency-currency/proofs/outdated-YYYY-MM-DD.txt
gh api repos/astral-sh/uv/releases/latest --jq .tag_name > .gzkit/chores/dependency-currency/proofs/uv-latest.txt
```

## Known Gaps

- The registry's staleness declaration takes one signal, so the chore is
  scheduled on elapsed time (1 day). The dependency-change trigger is the
  instruction above, not a scheduled signal.
- Chores announce, never gate: the daily cadence makes the chore due on the
  chores board each day; something still has to run it.

---

**End of CHORE: Dependency Currency**
