# ADR-pool.wave-dependency-execution

- **Status:** Pool
- **Lane:** Heavy
- **Date:** 2026-04-05
- **Origin:** GSD v1 comparative analysis — wave-based parallelism adaptation

## Intent

Add dependency-ordered wave execution to the OBPI pipeline, enabling independent
OBPIs within an ADR to run in parallel while respecting logical dependencies between
them. Currently, SVFR enables concurrent OBPI execution based on non-overlapping
file paths, but it has no concept of execution ordering — all SVFR OBPIs are treated
as equally independent. In practice, OBPIs often have logical dependencies: OBPI-01
creates the data model, OBPI-02 and OBPI-03 build features on that model, OBPI-04
integrates both features. Wave execution makes these dependencies explicit and
orchestrates parallel execution within each wave.

## Target Scope

### Wave Analysis

`gz waves --adr ADR-X.Y.Z` analyzes OBPI briefs and produces a wave execution plan:

- **Dependency signals parsed from briefs:**
  - Allowed paths overlap (file-level dependency)
  - Explicit `depends_on:` frontmatter field in OBPI briefs (logical dependency)
  - Import/module dependencies inferred from allowed paths (e.g., OBPI touching `models.py` must precede OBPI touching `views.py` that imports from it)
- **Wave assignment (deterministic):**
  - Wave 1: OBPIs with no dependencies (foundational work)
  - Wave 2: OBPIs whose dependencies are all in Wave 1
  - Wave N: OBPIs whose dependencies are all in Waves 1..N-1
  - Circular dependencies are flagged as errors — human must break the cycle
- **Output:** Wave plan document showing execution order, parallelism opportunities,
  and estimated wall-clock savings vs. sequential execution

### Wave Execution

`gz execute-waves --adr ADR-X.Y.Z` orchestrates multi-agent wave execution:

- **Wave 1:** Launch parallel agent sessions for all Wave 1 OBPIs (using SVFR + `gz-obpi-lock`)
- **Sync barrier:** Wait for all Wave 1 OBPIs to complete and sync before starting Wave 2
- **Wave 2+:** Launch parallel sessions for next wave, repeat
- **Failure handling:** If an OBPI in Wave N fails, dependent OBPIs in Wave N+1 are held. Independent OBPIs in Wave N+1 proceed.
- **Progress reporting:** `gz waves --status --adr ADR-X.Y.Z` shows wave completion state

### Brief Frontmatter Extension

Add optional `depends_on` field to OBPI brief frontmatter:

```yaml
depends_on:
  - OBPI-0.25.0-01  # data model must exist first
  - OBPI-0.25.0-03  # shared utility created here
```

When absent, dependencies are inferred from path overlap analysis. Explicit
declarations take precedence over inference.

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No automatic agent session spawning in initial implementation — wave plan is
  advisory, human launches sessions manually. Automated orchestration is a future
  extension.
- No cross-ADR wave dependencies — waves operate within a single ADR.
- No runtime reordering — wave plan is computed at analysis time, not adjusted
  during execution.

## Dependencies

- **Prerequisite:** SVFR execution mode (already implemented)
- **Prerequisite:** OBPI lock mechanism (already implemented)
- **Complements:** ADR-pool.svfr-quick-adhoc (quick OBPIs are always Wave 1 — no dependencies)
- **Complements:** ADR-pool.agent-execution-intelligence CAP-22 (`gz next` within a wave respects wave boundaries)
- **Related:** ADR-pool.pause-resume-handoff-runtime (wave sync barriers need handoff awareness for long-running waves)

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Dependency inference heuristics are validated against at least 3 real ADRs with
   5+ OBPIs — confirm wave assignments match human intuition.
3. Wave sync barrier mechanism is defined — how does the system detect "all Wave N
   OBPIs are complete" across independent agent sessions?
4. OBPI brief frontmatter schema extension (`depends_on`) is accepted.
5. Failure propagation rules are defined — when does a Wave N failure block Wave N+1
   vs. allow independent OBPIs to proceed?

## Inspired By

- [GSD](https://github.com/gsd-build/get-shit-done) wave-based execution in `/gsd-execute-phase` — analyzes task dependencies and runs independent work in parallel waves. Wave 1 (independent foundational tasks), Wave 2 (tasks dependent on Wave 1), Wave N (final integrations). Each plan gets a fresh 200k-token context.
- Make/build system dependency graphs — topological sort of tasks with parallel execution within each level.

## Notes

- Wave execution is most valuable for large ADRs (8+ OBPIs). For small ADRs (3-4
  OBPIs), sequential SVFR is likely faster than the overhead of wave analysis.
- Consider: minimum OBPI count threshold before wave analysis is offered.
- The sync barrier is the hardest design problem — independent agent sessions don't
  share state beyond the filesystem and ledger. File-based completion markers
  (similar to lock files) are the simplest mechanism.
- GSD gives each plan a fresh 200k context window. gzkit's equivalent: each wave
  agent session starts clean with `gz onboard --adr ADR-X.Y.Z` context.
- Risk: wave execution introduces coordination complexity. If the wave plan is wrong
  (missed dependency), Wave 2 OBPIs fail in confusing ways. The explicit `depends_on`
  field is the primary mitigation — human declares dependencies, system verifies them.
