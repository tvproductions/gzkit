---
id: OBPI-0.47.0-02-owasp-chore-runner
parent: ADR-0.47.0-owasp-top10-2025-scan
item: 2
lane: Heavy
sensitivity: security
status: Draft
---

# OBPI-0.47.0-02-owasp-chore-runner: OWASP chore runner

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.47.0-owasp-top10-2025-scan/ADR-0.47.0-owasp-top10-2025-scan.md`
- **Checklist Item:** #2 — `OBPI-0.47.0-02-owasp-chore-runner: Chore runner — ruff-S invocation + AST visitors + chore-reuse adapters`

**Status:** Draft

## Objective

Land the `.gzkit/chores/owasp-top10-2025-scan/` chore: a runner that invokes `ruff check --select S<rules>` (rule list drawn from `mapping.json` authored by OBPI-01), drives stdlib-AST visitors for the gzkit-specific patterns named in the parent ADR (chmod 0o777, `verify=False`, `shell=True` literal, hardcoded crypto keys, `random.*` for tokens, f-string interpolation into `execute()` / `eval()` / `exec()` / `os.system()`, secret-shaped strings in log format strings), and adapters that reuse the existing `dependency-currency` and `exceptions-and-logging-rationalization` chores rather than duplicating their analyzers. The runner emits an `OwaspScanReport`-shaped JSON proof to `proofs/`.

This brief lands no CLI surface (OBPI-03's job) and no skill (OBPI-04's job). It is the mechanical analyzer floor.

## Lane

**Heavy** — adds runtime contract: a chore registered in `.gzkit/chores/registry.json` whose JSON output schema is consumed by OBPI-03's CLI and OBPI-04's skill.

> Sensitivity: `security`. The runner spawns subprocesses (`ruff check ...`)
> against the consuming repo's source tree. Per
> `.gzkit/rules/security-sensitivity.md` § Invariant, security work needs
> heightened review regardless of lane or kind. The brief escalates
> sensitivity to `security` even though `.gzkit/chores/owasp-top10-2025-scan/`
> does not yet appear in `data/security_surfaces.json` (escalate-not-escape;
> escalation without overlap is permitted). OBPI-05 may register the chore's
> source modules in `data/security_surfaces.json` as part of dogfood.

## Allowed Paths

- `.gzkit/chores/owasp-top10-2025-scan/CHORE.md` — chore manifest (objective, scope, evidence)
- `.gzkit/chores/owasp-top10-2025-scan/README.md` — operator-facing rationale
- `.gzkit/chores/owasp-top10-2025-scan/acceptance.json` — acceptance contract
- `.gzkit/chores/owasp-top10-2025-scan/runner.py` — orchestrator: ruff invocation + AST drive + reuse adapters + report assembly
- `.gzkit/chores/owasp-top10-2025-scan/visitors.py` — stdlib `ast` visitor implementations
- `.gzkit/chores/owasp-top10-2025-scan/adapters.py` — adapters into `dependency-currency` and `exceptions-and-logging-rationalization` chore outputs
- `.gzkit/chores/owasp-top10-2025-scan/proofs/` — proof output directory (created at first run)
- `.gzkit/chores/registry.json` — register the chore (one JSON entry append; no other reordering)
- `tests/scan/test_owasp_chore_runner.py` — runner integration tests
- `tests/scan/test_owasp_visitors.py` — per-pattern AST visitor tests
- `tests/scan/test_owasp_adapters.py` — chore-reuse adapter tests
- `tests/scan/fixtures/sources/` — fixture .py files exercising each AST pattern (positive + negative)

## Denied Paths

- `src/gzkit/scan/models.py`, `src/gzkit/scan/mapping.py` — schema lives in OBPI-01 and is consumed read-only here
- `src/gzkit/cli/**` — CLI plumbing belongs to OBPI-03
- `.gzkit/skills/gz-owasp-scan/**` — skill authoring belongs to OBPI-04
- `docs/user/manpages/**`, `docs/user/runbook.md`, `docs/governance/governance_runbook.md` — runbook + manpage updates belong to OBPI-03 / OBPI-05
- `pyproject.toml`, `uv.lock` — stdlib-first; no new runtime deps (`ruff` already in toolchain)
- `data/security_surfaces.json` — registry edit (if any) belongs to OBPI-05

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The runner MUST invoke `ruff check --select S110,S112,S301,S302,S303,S304,S305,S306,S307,S324,S501,S502,S503,S504,S505,S506,S507,S508,S509,S605,S606,S607,S608,S609 --output-format json <scope>` with the exact `S`-rule set named in the parent ADR § Decision § Analyzer floor; the rule list MUST be sourced from `mapping.json` (no hardcoded duplicate).
2. REQUIREMENT: All subprocess invocations MUST use `subprocess.run(..., shell=False, check=False)` with list-form `args`; `shell=True` is forbidden (cross-platform binding + security sensitivity).
3. ALWAYS: Each AST visitor named in the ADR (chmod 0o777, `verify=False`, `shell=True` literal, hardcoded crypto keys, `random.*` for tokens, f-string-into-`execute()`/`eval()`/`exec()`/`os.system()`, secret-shaped strings in log format strings) MUST be implemented as a `ast.NodeVisitor` subclass with a positive-case fixture and a negative-case fixture under `tests/scan/fixtures/sources/`.
4. REQUIREMENT: The runner MUST NOT duplicate `dependency-currency` or `exceptions-and-logging-rationalization` analyzers — A03 and A09/A10 reuse those chores via adapters that read their existing proof outputs.
5. ALWAYS: The emitted proof at `.gzkit/chores/owasp-top10-2025-scan/proofs/owasp-scan-report-<commit>.json` MUST validate against `OwaspScanReport.model_validate_json(...)` from OBPI-01; a failing validation is a chore failure.
6. ALWAYS: A category whose `mapping.json` source is `judgment-only` MUST emit `coverage[CAT] == "not-mechanical"` and contribute no `OwaspFinding` from this chore (A06 honesty; anti-vibing binding claim 4).
7. ALWAYS: A category whose `mapping.json` source is `not-applicable` (A07) MUST emit `coverage[CAT] == "not-applicable"`.
8. NEVER: The runner MUST NOT write to any path outside `.gzkit/chores/owasp-top10-2025-scan/proofs/` — proofs are the only side effect.
9. REQUIREMENT: The chore MUST register in `.gzkit/chores/registry.json` with `slug: "owasp-top10-2025-scan"`, `lane: "heavy"`, `allowNetwork: false` (no network egress in the analyzer floor).
10. ALWAYS: The runner MUST be invokable via `uv run gz chore run owasp-top10-2025-scan` (existing chore-runner verb) and via direct `python -m` for test isolation.

> STOP-on-BLOCKERS: if `ruff` is not callable from the project venv, halt and report.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote verbatim into Implementation Summary:** "Mechanical chore at `.gzkit/chores/owasp-top10-2025-scan/` — runs ruff `S`-rules + AST visitors + reused-chore adapters; writes `proofs/`; emits ledger receipt." plus the full `Analyzer floor` block listing every ruff `S`-rule and every AST visitor.
- [ ] Parent ADR § Intent — stdlib-first; no bandit/semgrep.
- [ ] Parent ADR § A01–A10 coverage map — which categories are mechanical / partial / not-mechanical / not-applicable.

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/pythonic.md` — module/function size limits; no bare `except`.
- [ ] `.gzkit/rules/cross-platform.md` — `shell=False` binding; list-form subprocess.
- [ ] `.gzkit/rules/security-sensitivity.md` — escalation discipline.
- [ ] `AGENTS.md` § Stdlib-First doctrine — no third-party security tools.

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.47.0-01 lands first — `src/gzkit/scan/models.py`, `mapping.json`, `mapping.schema.json` are imports for this brief.
- [ ] `.gzkit/chores/dependency-currency/` exists (it does) — adapter must read its proof shape.
- [ ] `.gzkit/chores/exceptions-and-logging-rationalization/` exists (it does) — adapter must read its proof shape.
- [ ] `.gzkit/chores/registry.json` exists (it does).

**Existing Code (understand current state):**

- [ ] `.gzkit/chores/dependency-currency/CHORE.md` + `acceptance.json` — sibling layout convention.
- [ ] `.gzkit/chores/exceptions-and-logging-rationalization/` — sibling for proof-shape inspection.
- [ ] `src/gzkit/chores/__init__.py` — chore-package fallback path per ADR-0.0.21.
- [ ] One existing chore runner that calls `subprocess.run` — confirm list-form pattern.

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded
- [ ] Parent ADR Decision quote in Implementation Summary
- [ ] Mapping.json rule list matches ADR § Analyzer floor exactly (no add, no drop)

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Per-visitor positive + negative fixtures land RED → GREEN
- [ ] Adapter tests prove `dependency-currency` / `exceptions-and-logging-rationalization` outputs round-trip into `OwaspFinding`s
- [ ] `uv run gz arb step --name unittest -- uv run -m unittest -q tests/scan` passes
- [ ] Coverage floor: `uv run gz arb coverage run -m unittest discover -s tests/scan -t .`

### Code Quality

- [ ] `uv run gz arb ruff` clean (the chore's own code passes its own analyzer)
- [ ] `uv run gz arb typecheck` clean

### Gate 3: Docs (Heavy)

- [ ] `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict`
- [ ] `CHORE.md` + `README.md` author the operator-facing contract; no manpage / runbook in this brief

### Gate 4: BDD (Heavy)

- [ ] N/A — chore behaviour is unit-tested; end-to-end BDD lands in OBPI-05 dogfood

### Gate 5: Human (Heavy + Security)

- [ ] Human attestation recorded — heavy lane forces; sensitivity:security force-binds the heightened walkthrough (`arb-step-security-scan-*` receipt)

## Verification

```bash
uv run gz validate --documents
uv run gz validate --briefs
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q tests/scan
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict

# Specific verification for this OBPI
test -f .gzkit/chores/owasp-top10-2025-scan/CHORE.md
test -f .gzkit/chores/owasp-top10-2025-scan/runner.py
uv run gz chore run owasp-top10-2025-scan --dry-run
```

## Demo

```bash
# Real chore run against gzkit itself
uv run gz chore run owasp-top10-2025-scan

# Inspect the emitted proof
ls .gzkit/chores/owasp-top10-2025-scan/proofs/
uv run python -c "
from gzkit.scan.models import OwaspScanReport
import glob
latest = sorted(glob.glob('.gzkit/chores/owasp-top10-2025-scan/proofs/owasp-scan-report-*.json'))[-1]
report = OwaspScanReport.model_validate_json(open(latest).read())
print(f'A06 coverage: {report.coverage[\"A06\"]}')  # MUST be not-mechanical
print(f'A07 coverage: {report.coverage[\"A07\"]}')  # MUST be not-applicable
print(f'Findings: {len(report.findings)}')
"
```

## Acceptance Criteria

- [ ] REQ-0.47.0-02-01: Given a fixture `.py` file with `subprocess.run(cmd, shell=True)`, when the runner executes, then an `OwaspFinding` is emitted with `category == "A02"`, `source == "stdlib-ast"`, `rule_id == "gzkit-ast-shell-true-literal"`; `tests/scan/test_owasp_visitors.py::test_shell_true_detected` covers.
- [ ] REQ-0.47.0-02-02: Given a fixture with `os.chmod(p, 0o777)`, when the runner executes, then an `OwaspFinding` is emitted with `category == "A02"`, `rule_id == "gzkit-ast-chmod-world-writable"`; `tests/scan/test_owasp_visitors.py::test_chmod_world_writable_detected` covers.
- [ ] REQ-0.47.0-02-03: Given a fixture with `requests.get(url, verify=False)`, when the runner executes, then an `OwaspFinding` is emitted with `category == "A02"`, `rule_id == "gzkit-ast-requests-verify-false"`; `tests/scan/test_owasp_visitors.py::test_verify_false_detected` covers.
- [ ] REQ-0.47.0-02-04: Given a fixture with `random.choice(...)` used to build a token-shaped variable, when the runner executes, then an `OwaspFinding` is emitted with `category == "A04"`, `rule_id == "gzkit-ast-random-for-tokens"`; `tests/scan/test_owasp_visitors.py::test_random_for_tokens_detected` covers.
- [ ] REQ-0.47.0-02-05: Given a fixture with `cursor.execute(f"SELECT * FROM t WHERE id={user_id}")`, when the runner executes, then an `OwaspFinding` with `category == "A05"`, `source == "ruff-S"` (S608) is emitted (ruff catches this) AND `tests/scan/test_owasp_visitors.py::test_fstring_into_execute_detected` exercises the AST visitor as defense-in-depth.
- [ ] REQ-0.47.0-02-06: Given the chore runs against any scope, when complete, then the emitted proof JSON validates via `OwaspScanReport.model_validate_json`; `tests/scan/test_owasp_chore_runner.py::test_proof_validates_against_schema` covers.
- [ ] REQ-0.47.0-02-07: Given the runner emits a report, when `coverage["A06"]` is read, then its value is exactly `"not-mechanical"`; `tests/scan/test_owasp_chore_runner.py::test_a06_never_graded_mechanically` covers (anti-vibing claim 4 mechanically enforced).
- [ ] REQ-0.47.0-02-08: Given the `dependency-currency` chore has emitted a proof, when the OWASP runner's adapter executes, then A03 findings round-trip into `OwaspFinding(source="chore-reused")` with `rule_id` carrying the upstream chore's identifier; `tests/scan/test_owasp_adapters.py::test_dependency_currency_adapter` covers.
- [ ] REQ-0.47.0-02-09: Given `subprocess.run` is invoked anywhere in the runner, when grep'd, then `shell=True` MUST NOT appear; `tests/scan/test_owasp_chore_runner.py::test_no_shell_true_in_runner` covers (eats own dogfood).

## Completion Checklist

- [ ] **Gate 1 (ADR):** Decision quote in Implementation Summary; rule list parity with ADR
- [ ] **Gate 2 (TDD):** Per-visitor RGR; nine REQ-derived tests pass; coverage receipt captured
- [ ] **Code Quality:** `arb-ruff-*`, `arb-step-typecheck-*` receipts captured
- [ ] **Value Narrative:** Mechanical floor stands up; reuse-not-duplicate honored
- [ ] **Key Proof:** Proof JSON validates against schema; A06 stays `not-mechanical`
- [ ] **OBPI Acceptance:** Human attestation recorded (heavy + security)

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` § OBPI Acceptance Protocol.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded; Decision-quote present in Implementation Summary

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Receipts expected:
# arb-step-unittest-<sha>     (uv run -m unittest -q tests/scan)
# arb-step-coverage-<sha>     (coverage discover -s tests/scan)
```

### Code Quality

```text
# arb-ruff-<sha>
# arb-step-typecheck-<sha>
```

### Gate 3 (Docs)

```text
# arb-step-mkdocs-<sha>
```

### Gate 4 (BDD)

```text
# N/A in this brief
```

### Gate 5 (Human)

```text
# arb-step-security-scan-<sha> (sensitivity:security heightened walkthrough)
# Attestation text recorded at completion. Receipt via `gz adr emit-receipt`.
```

### Value Narrative

Before this OBPI: ADR-0.47.0 names a stdlib-first analyzer floor in prose; nothing executes. After this OBPI: a chore runs the floor end-to-end, emits a schema-valid proof, refuses to grade A06 mechanically, and reuses two existing chores instead of duplicating their analyzers. The CLI (OBPI-03) and skill (OBPI-04) get a single mechanical surface to wrap.

### Key Proof

`uv run gz chore run owasp-top10-2025-scan` produces `proofs/owasp-scan-report-<sha>.json` whose `coverage["A06"] == "not-mechanical"` — the A06-honesty doctrine from the ADR is enforced in the proof, not the prose.

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
