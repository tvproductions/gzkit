Feature: Distribution invariant T0 smoke test
  Heavy-lane Gate 4 proof for ADR-0.0.32 OBPI-06.
  Builds the wheel via uv build, installs it into a fresh temp venv,
  runs gz init in a clean tempdir using the installed binary, and
  asserts byte-equivalence of the resulting .gzkit/ tree against the
  frozen data/distribution_baseline_manifest.json. Detects drift in
  both directions: missing baseline entries AND extra installed
  artifacts not in the baseline.

  Runtime cost: 3.3s measured 2026-08-22 with a warm `uv build` cache -- a
  DATED RECORD, not a budget. The "30-90s" this header used to claim was
  never re-measured; the whole Behave step is 29.8s and this scenario is
  about a tenth of it, so the wheel build was never the cost it was taken
  for (GHI #860). It runs in the
  pre-push `gz check` gate and is NOT excluded by a tag: `gz check --fast`,
  the inner-loop scope, drops the whole Behave step (_FAST_SKIPPED_STEPS),
  and `--reuse-verified` stops one tree paying for it twice. Run this
  scenario alone with:
    uv run -m behave features/distribution_invariant.feature

  This header carried an `@slow` tag and a claim that it excluded the
  scenario from "the standard gz test smoke run" (GHI #860). Neither held:
  nothing anywhere filtered on `@slow`, and `gz test` runs unittest, never
  behave. Do not re-add it — a tier expressed as a tag is the third test
  tier GHI #182 removed, and `gz validate --test-tiers` now fails closed
  on one.

  @REQ-0.0.32-06-01
  @REQ-0.0.32-06-02
  @REQ-0.0.32-06-04
  @REQ-0.0.32-06-06
  @REQ-0.0.32-06-07
  @REQ-0.0.32-06-08
  @REQ-0.0.32-06-09
  @REQ-0.0.32-06-10
  Scenario: Build, install, init, assert byte-equivalence vs baseline
    Given an empty distribution-test project directory
    And the gzkit baseline manifest at "data/distribution_baseline_manifest.json"
    When I build the wheel with uv build
    And I install the built wheel into a fresh temporary venv
    And I run "gz init" in the project directory using the venv's gz binary
    Then every baseline manifest entry is present in the project's .gzkit tree
    And no installed .gzkit artifact under a tracked surface is absent from the baseline manifest

  @REQ-0.0.32-06-03
  @REQ-0.0.32-06-05
  Scenario: Baseline manifest validates against frozen schema
    Given the gzkit baseline manifest at "data/distribution_baseline_manifest.json"
    Then the manifest has schema_version "1.0"
    And the manifest surfaces include "skills"
    And the manifest surfaces include "rules"
    And the manifest surfaces include "personas"
    And the manifest surfaces include "templates"
    And each "skills" entry resolves to a real file under "src/gzkit/skills/"
    And each "rules" entry resolves to a real file under "src/gzkit/rules/"
