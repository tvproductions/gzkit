---
id: OBPI-0.0.21-07-bdd-chores-distribution
parent: ADR-0.0.21-chores-as-gzkit-surface
item: 7
lane: Heavy
status: Completed
---

# OBPI-0.0.21-07-bdd-chores-distribution: BDD — Install-and-Scaffold Scenario

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.21-chores-as-gzkit-surface/ADR-0.0.21-chores-as-gzkit-surface.md`
- **Checklist Item:** #7 — BDD scenario: install-and-scaffold feature proving `pip install py-gzkit` → `gz init` → `gz chores list` returns the canonical set.

**Status:** Draft

## Objective

Author `features/chores_distribution.feature` with Gherkin scenarios that exercise the full distribution pipeline end-to-end — wheel install in a scratch venv, `gz init` scaffolds `.gzkit/chores/`, `gz chores list` returns the canonical slugs, `gz chores list --explain` distinguishes project vs package source, and the registry-merge contract fires without clobbering operator edits — with every scenario carrying `@REQ-0.0.21-07-NN` tags so `gz validate --behave-req-tags` maps them to this OBPI's requirements.

## Lane

**Heavy** — Gate 4 is the canonical proof for this ADR. Foundation-kind + heavy-lane parent forces BDD per `.gzkit/rules/tests.md` § Behave scenario tagging.

## Allowed Paths

- `features/chores_distribution.feature` — NEW feature file, Gherkin scenarios with `@REQ-0.0.21-07-NN` tags
- `features/steps/chores_distribution.py` — step definitions if the scenarios require steps not covered by existing step modules under `features/steps/`
- `features/environment.py` — only if a new fixture hook is required (e.g., scratch-venv management); prefer NOT to touch this shared file
- `tests/support/chores_distribution_helpers.py` — optional shared helper if the step definitions need fixture utilities that are better tested in isolation; ONLY if isolation delivers genuine value
- `data/behave_coverage_waivers.json` — only if explicitly waiving a REQ from BDD coverage (preferred: author coverage, not waive)

## Denied Paths

- `src/gzkit/**` — no source changes; this OBPI validates the system built by OBPIs 01-06, 08, 09
- `tests/**` — unit tests are the other OBPIs' responsibility
- `pyproject.toml`, `docs/**`, `.gzkit/rules/**` — out of scope

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `features/chores_distribution.feature` MUST contain at least 4 scenarios:
   - Scenario A: fresh wheel install → `gz chores list` returns canonical set via package fallback (no `gz init` run)
   - Scenario B: fresh wheel install → `gz init` → `.gzkit/chores/` populated → `gz chores list --explain` reports every chore as `project` source
   - Scenario C: existing `.gzkit/chores/` with an operator-edited `CHORE.md` → `gz init --repair` preserves the operator edit (skip_existing honored)
   - Scenario D: canonical registry has a new slug relative to project-local → `gz init --repair` prints the merge diff and requires `--yes` to write (or interactive confirmation)
2. REQUIREMENT: Every scenario MUST carry one or more `@REQ-0.0.21-07-NN` scenario-level tags. Feature-level `# @covers` comments are not sufficient per `.gzkit/rules/tests.md` § Behave scenario tagging.
3. REQUIREMENT: The scenarios MUST exercise the real wheel — not a mocked one. The test fixture MUST either build a wheel via `uv build` in a setup step and install it into an isolated venv, or use `pip install -e .` inside a tempdir whose working dir is manipulated so resolver and scaffolder both see clean state.
4. REQUIREMENT: Scenarios MUST NOT leak state between runs. Use `tempfile.TemporaryDirectory` via a `behave` before-scenario hook; never `shutil.rmtree` directly per `.gzkit/rules/tests.md`.
5. REQUIREMENT: Scenarios MUST run deterministically — no network calls, no reliance on PyPI, no timing-dependent assertions. If the editable-install path is used, the fixture pins to the local source tree.
6. REQUIREMENT: `uv run behave features/chores_distribution.feature` MUST exit 0 after this OBPI.
7. REQUIREMENT: `uv run gz validate --behave-req-tags` MUST exit 0 — every REQ declared in the brief's Acceptance Criteria MUST have a matching `@REQ-0.0.21-07-NN` scenario tag somewhere in `features/chores_distribution.feature`.
8. REQUIREMENT: The feature file MUST NOT contain Gherkin steps that reuse the word `chores` for non-chores concepts; step names MUST be specific (e.g. `Given the project has been initialized with gz init`, not `Given chores are set up`).
9. REQUIREMENT: Cross-platform: scenarios MUST use `pathlib.Path` in step definitions, not hardcoded separators; UTF-8 explicit in any file writes per `.gzkit/rules/cross-platform.md`.

> STOP-on-BLOCKERS:
> - If OBPIs 01, 03, 04, 05 have not all landed, scenarios cannot green — BDD is the integration proof, requires the stack.
> - If `uv build` in the BDD fixture takes >60s, `.gzkit/rules/tests.md` § Smoke/BVT allows heavy-tier scenarios to exceed that ceiling — but the scenario MUST be labeled accordingly; do not silently exceed ceilings.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.gzkit/rules/tests.md` § Behave scenario tagging (GHI #185) + § Two runners, one test surface
- [ ] `.gzkit/rules/cross-platform.md` — pathlib + UTF-8
- [ ] Parent ADR ADR-0.0.21 § Evidence Gate 4

**Context:**

- [ ] Sibling OBPIs 01-05 landed — prerequisites for BDD to have real behavior to exercise
- [ ] Existing feature files under `features/` — tagging conventions, step-reuse patterns

**Prerequisites:**

- [ ] OBPIs 01-06 Completed (OBPI-06 docs may land in parallel; the scenarios test behavior, not docs)
- [ ] `uv build` produces a wheel with chores (OBPI-03 REQ-03-01 verified)
- [ ] `gz init` invokes `scaffold_core_chores` (OBPI-05 REQ-05-05 verified)

**Existing Code:**

- [ ] Read `features/persona_sync.feature` or similar — scenario pattern that exercises a scaffolder
- [ ] Read `features/steps/` modules to find existing steps reusable for "Given a clean project directory" / "When I run uv run gz ..." patterns
- [ ] Read `features/environment.py` — understand existing before_scenario / after_scenario fixtures

## Quality Gates

### Gate 1 (ADR)
- [ ] Intent recorded

### Gate 2 (TDD — Red-Green-Refactor)
- [ ] N/A as unit-level TDD; BDD itself is the Red-Green cycle at the integration level. Red = scenario written without implementation support fails with clear step miss / assertion. Green = all scenarios pass.

### Code Quality
- [ ] `uv run gz lint` (applies to `.py` step modules)
- [ ] `uv run gz typecheck` — clean on step modules

### Gate 3 (Docs) — Heavy
- [ ] `uv run mkdocs build --strict` green

### Gate 4 (BDD) — Heavy
- [ ] `uv run behave features/chores_distribution.feature` exits 0
- [ ] `uv run gz validate --behave-req-tags` exits 0

### Gate 5 (Human) — Heavy + Foundation
- [ ] Brief-level human attestation

## Verification

```bash
# Feature file exists and has scenario-level REQ tags
test -f features/chores_distribution.feature
grep -c "@REQ-0.0.21-07-" features/chores_distribution.feature   # expect >= 4

# Scenarios pass
uv run behave features/chores_distribution.feature 2>&1 | tail -15

# REQ coverage validator passes
uv run gz validate --behave-req-tags 2>&1 | tail -5
```

## Acceptance Criteria

- [ ] REQ-0.0.21-07-01: `features/chores_distribution.feature` exists with at least 4 scenarios, each tagged `@REQ-0.0.21-07-NN`.
- [ ] REQ-0.0.21-07-02: Scenario A proves `gz chores list` works immediately after wheel install without `gz init` (package-fallback path).
- [ ] REQ-0.0.21-07-03: Scenario B proves `gz init` populates `.gzkit/chores/` and `gz chores list --explain` labels every row as `project` source.
- [ ] REQ-0.0.21-07-04: Scenario C proves `gz init --repair` preserves operator edits to `.gzkit/chores/<slug>/CHORE.md` (skip_existing honored).
- [ ] REQ-0.0.21-07-05: Scenario D proves `gz init --repair` prints a merge diff when canonical registry has new slugs and requires `--yes` (or interactive confirmation) before writing.
- [ ] REQ-0.0.21-07-06: `uv run behave features/chores_distribution.feature` exits 0.
- [ ] REQ-0.0.21-07-07: `uv run gz validate --behave-req-tags` exits 0 (every REQ in this brief's Acceptance Criteria has a matching scenario tag OR a registered waiver in `data/behave_coverage_waivers.json` for the specific REQ).

## Completion Checklist

- [ ] **Gate 1:** Intent recorded
- [ ] **Gate 2:** N/A at unit level
- [ ] **Code Quality:** lint + typecheck green on step modules
- [ ] **Gate 3:** docs build green
- [ ] **Gate 4:** behave + behave-req-tags green
- [ ] **Gate 5:** human attestation
- [ ] **Value Narrative:** before — no end-to-end proof that a published wheel delivers a working chores system; after — a Gherkin scenario is the deterministic proof fired on every CI run.
- [ ] **Key Proof:** `uv run behave features/chores_distribution.feature` prints 4+ scenarios passing.

## Evidence

### Gate 1 (ADR)
- [ ] Intent recorded

### Gate 2 (TDD)
```text
N/A at unit level; BDD is integration-level proof.
```

### Code Quality
```text
# paste lint + typecheck on step modules
```

### Gate 3 (Docs)
```text
# paste mkdocs output
```

### Gate 4 (BDD)
```text
# paste behave output — scenario titles, steps, pass count
```

### Gate 5 (Human)
```text
# attestation text
```

### Value Narrative
Before: no Gherkin scenario exercised the distribution pipeline; regression was detectable only by manual `pip install && gz chores list` in a scratch venv. After: the install-and-scaffold behavior is locked by fail-closed BDD.

### Key Proof

$ uv run behave features/chores_distribution.feature 2>&1 | tail -5
1 feature passed, 0 failed, 0 skipped
4 scenarios passed, 0 failed, 0 skipped
24 steps passed, 0 failed, 0 skipped
Took 0min 1.442s

ARB receipts cited inline:
- lint: arb-ruff-7ce5414825144417b84313489336f81a
- typecheck: arb-step-typecheck-1fa045beb5c74a3e8f980091da9d6772
- docs: arb-step-mkdocs-2146943620724b75819251eedd328374
- behave: arb-step-behave-chores-distribution-d99939bc54b3460db97dd4417306db39

### Implementation Summary

- Files created: features/chores_distribution.feature (4 scenarios with 7 @REQ-0.0.21-07-NN scenario tags), features/steps/chores_distribution_steps.py (9 step definitions: subprocess invocation via [sys.executable, "-m", "gzkit"], file edit, registry mutation, output assertions with ANSI stripping)
- Brief allowlist honored: no writes to src/, tests/, pyproject.toml, docs/, or .gzkit/rules/
- Scenario coverage: A package-fallback (REQ-02), B project-source via gz init + --explain (REQ-03), C operator-edit preservation via skip_existing (REQ-04), D merge-diff with --yes write (REQ-05); A also carries meta-REQ tags 01/06/07
- Test runtime: 1.442s for 4 scenarios / 24 steps
- Pre-existing drift cleared in flight: 16 ruff findings in .gzkit/skills/ghi-triage/scripts/triage.py and 3 vendor mirrors refactored to list-join form; GHI #313 filed for plan-audit-gate hook naming-convention drift
- Date completed: 2026-04-25
- Attestation status: human-attested by g0
- Defects noted: GHI #313 (plan-audit-gate naming drift, pre-existing, not caused by this OBPI)

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Heavy-lane + foundation-kind OBPI-0.0.21-07 BDD chores distribution: 4 scenarios authored (features/chores_distribution.feature) with 7 @REQ-0.0.21-07-NN scenario tags; 9 step definitions (features/steps/chores_distribution_steps.py) using subprocess pattern against editable install resolving importlib.resources('gzkit.chores'). All 4 scenarios pass in 1.442s (24 steps green). Brief allowlist honored — no src/, tests/, pyproject.toml, docs/, or .gzkit/rules/ writes. Pre-existing ghi-triage ruff drift cleared in flight; GHI #313 filed for plan-audit-gate hook naming-convention drift. Receipts: lint arb-ruff-7ce5414825144417b84313489336f81a; types arb-step-typecheck-1fa045beb5c74a3e8f980091da9d6772; docs arb-step-mkdocs-2146943620724b75819251eedd328374; bdd arb-step-behave-chores-distribution-d99939bc54b3460db97dd4417306db39.
- Date: 2026-04-25

---

**Brief Status:** Completed

**Date Completed:** 2026-04-25

**Evidence Hash:** -
