# Governance Graph Rot Audit — 2026-04-15

**GHI:** #160 Phase 1
**Scope:** Every ADR under `docs/design/adr/**`
**Method:** `gz covers --json` global scan + per-ADR section inspection + `scan_briefs()` direct invocation
**Raw data:** `artifacts/audits/governance-graph-rot-audit-2026-04-15-raw.json`

## Headline numbers

| Metric                                        | Count |
|-----------------------------------------------|-------|
| ADR directories on disk                       | 55    |
| ADRs visible to `gz covers` (`by_adr`)        | 26    |
| ADRs invisible to `gz covers` (zero code-REQs)| 29    |
| ADRs whose REQs scan correctly but are doc-only | 1   |
| Total testable REQs in graph (all ADRs)       | 767   |
| Total testable REQs covered by tests          | 482   |
| Aggregate REQ coverage                        | 62.8% |

The umbrella GHI #160 anticipated this rot but undercounted. The umbrella named ADR-0.23.0 as the single canonical "zero-REQ" example. The actual graph has **29 ADRs** in that state, not one.

## Failure-mode taxonomy

Every "missing" ADR fits one of six modes. The remediation Phase depends on the mode.

### Mode A — Doc-only REQs, correctly excluded by `compute_coverage`

Not a defect in the brief. `compute_coverage` (`src/gzkit/traceability.py:407`) intentionally drops `[doc]` REQs because tests are for code. ADR-0.9.0 has 16 well-formed REQ identifiers — every one tagged `[doc]`. The ADR is correctly invisible to `gz covers` because none of its REQs is testable.

| ADR        | OBPIs | REQ IDs | All `[doc]`? |
|------------|-------|---------|--------------|
| ADR-0.9.0  | 5     | 16      | yes          |

**Phase 3 action:** none — ADR-0.9.0 is not rot. Note in audit report and move on.

### Mode B — `## ACCEPTANCE NOTES` legacy heading (foundational template)

The very first foundation ADR uses the all-uppercase "(Foundational)" template. Heading is `## ACCEPTANCE NOTES`, which `extract_reqs_from_brief` does not match (it requires literal `## Acceptance Criteria`).

| ADR        | OBPIs | Sections                                        |
|------------|-------|-------------------------------------------------|
| ADR-0.0.1  | 8     | `## ACCEPTANCE NOTES`, `## REQUIREMENTS (FAIL-CLOSED — Foundational)` |

**Phase 3 action:** convert each OBPI to canonical `## Acceptance Criteria` with `REQ-0.0.1-NN-MM` identifiers derived from the existing ACCEPTANCE NOTES + REQUIREMENTS prose.

### Mode C — Skeleton OBPIs with no Acceptance section at all

Minimal early-pre-release OBPIs that pre-date the entire REQ framework. Have only ADR Item / Objective / Human Attestation sections.

| ADR        | OBPIs | Notes                                           |
|------------|-------|-------------------------------------------------|
| ADR-0.7.0  | 4     | only 1 of 4 has an Acceptance section at all    |

**Phase 3 action:** decide whether to retro-spec these or accept them as historical artifacts (Phase 2 operator decision).

### Mode D — Acceptance Criteria sections present but no REQ-IDs (informal `- [ ]` format)

The 0.x.0 pre-release ADRs have proper `## Acceptance Criteria` sections, but the criteria are bare informal checkboxes:

```
- [x] `gz init test-project` creates all directories
```

The extractor reads these lines and skips them silently because they don't match `_AC_LINE_PATTERN` (no `REQ-X.Y.Z-NN-MM` token).

| ADR       | OBPIs | Acceptance Criteria sections | REQ IDs |
|-----------|-------|------------------------------|---------|
| ADR-0.1.0 | 10    | 10                           | 0       |
| ADR-0.2.0 | 3     | 3                            | 0       |
| ADR-0.3.0 | 5     | 5                            | 0       |
| ADR-0.4.0 | 4     | 4                            | 0       |
| ADR-0.5.0 | 5     | 5                            | 0       |
| ADR-0.6.0 | 3     | 3                            | 0       |
| ADR-0.8.0 | 3     | 3                            | 0       |

**Phase 3 action:** rewrite each acceptance line as `- [x] REQ-X.Y.Z-NN-MM: <existing description>`. Mechanical transformation; no semantic invention.

### Mode E — Legacy `## REQUIREMENTS (FAIL-CLOSED)` template, no Acceptance Criteria section

The ADR-0.16.0 → ADR-0.39.0 family adopted a different template that uses `## REQUIREMENTS (FAIL-CLOSED)` with informal numbered requirements and **no Acceptance Criteria section at all**. This is the template ADR-0.23.0 uses (the umbrella's canonical example).

| ADR        | OBPIs | Acceptance | Requirements | Notes                  |
|------------|-------|------------|--------------|------------------------|
| ADR-0.16.0 | 5     | 0          | 5            |                        |
| ADR-0.18.0 | 8     | 0          | 8            |                        |
| ADR-0.23.0 | 4     | 0          | 4            | umbrella example       |
| ADR-0.24.0 | 5     | 0          | 5            |                        |
| ADR-0.27.0 | 13    | 0          | 13           |                        |
| ADR-0.28.0 | 19    | 0          | 19           |                        |
| ADR-0.29.0 | 7     | 0          | 7            |                        |
| ADR-0.30.0 | 8     | 0          | 8            |                        |
| ADR-0.31.0 | 10    | 0          | 10           |                        |
| ADR-0.32.0 | 25    | 0          | 25           |                        |
| ADR-0.33.0 | 10    | 0          | 10           |                        |
| ADR-0.34.0 | 13    | 0          | 13           |                        |
| ADR-0.35.0 | 20    | 0          | 20           |                        |
| ADR-0.36.0 | 13    | 0          | 13           |                        |
| ADR-0.37.0 | 23    | 0          | 23           |                        |
| ADR-0.38.0 | 10    | 0          | 10           |                        |
| ADR-0.39.0 | 6     | 0          | 6            |                        |
| ADR-0.40.0 | 5     | 0          | 5            | uses `briefs/` not `obpis/` |

**Phase 3 action:** add `## Acceptance Criteria` sections to each OBPI with `- [x] REQ-X.Y.Z-NN-MM: <criterion>` lines derived from the existing REQUIREMENTS prose. The REQUIREMENTS section can stay; it's the prose context for the formal criteria.

**Total Mode E OBPIs:** 199.

### Mode F — Container ADRs with no OBPIs at all

| ADR        | Notes                                |
|------------|--------------------------------------|
| ADR-0.0.2  | only `ADR-0.0.2-stdlib-cli-and-agent-sync.md`; no `obpis/` directory |

**Phase 3 action:** Phase 2 operator decision — does ADR-0.0.2 need OBPIs at all, or is it a meta-ADR that records architectural intent without decomposable work?

## Visible-but-incomplete ADRs (Phase 4 territory, not Phase 3)

These ADRs already have REQ identifiers — the rot is missing `@covers` decorators in tests, not missing IDs in briefs. Phase 4 closes the gap.

| ADR         | Coverage     | Total REQs | Covered | Missing |
|-------------|--------------|------------|---------|---------|
| ADR-0.26.0  | 0.0%         | 60         | 0       | 60      |
| ADR-0.0.9   | 10.0%        | 20         | 2       | 18      |
| ADR-0.25.0  | 15.2%        | 165        | 25      | 140     |
| ADR-0.0.10  | 22.2%        | 18         | 4       | 14      |
| ADR-0.0.15  | 40.7%        | 27         | 11      | 16      |
| ADR-0.0.13  | 51.6%        | 31         | 16      | 15      |
| ADR-0.0.7   | 56.2%        | 16         | 9       | 7       |
| ADR-0.0.11  | 65.0%        | 20         | 13      | 7       |
| ADR-0.0.8   | 82.9%        | 41         | 34      | 7       |
| ADR-0.0.12  | 95.5%        | 22         | 21      | 1       |

**Total under-covered REQs:** 285 (the 37.2% gap).

The four orphan ceremony test files from GHI #158 do not appear in this list because none of the REQs they would cover exist yet — that work is blocked by Phase 3 backfill of ADR-0.23.0 and the cluster of ceremony-adjacent ADRs.

## Mode summary

| Mode | Description                                          | ADRs | Phase | Workload                                        |
|------|------------------------------------------------------|------|-------|-------------------------------------------------|
| A    | Doc-only REQs (correct exclusion)                    | 1    | none  | none                                            |
| B    | Foundational uppercase template                      | 1    | 3     | 8 OBPIs to convert                              |
| C    | Skeleton OBPIs                                       | 1    | 2     | operator decision required                      |
| D    | `## Acceptance Criteria` informal `- [ ]`            | 7    | 3     | ~33 OBPIs to retro-id                           |
| E    | `## REQUIREMENTS (FAIL-CLOSED)` legacy template      | 18   | 3     | ~199 OBPIs to retro-id (the bulk of the work)   |
| F    | Container ADRs with no OBPIs                         | 1    | 2     | operator decision required                      |
| —    | Visible but under-covered (`@covers` gap)            | 10   | 4     | ~285 tests to decorate                          |

## Operator decisions required (Phase 2)

The umbrella's Phase 2 question — *"is editing a Validated ADR's OBPI in place acceptable, or does it require an amendment ADR?"* — applies to **every** Mode B/D/E ADR, including the 16 already-Validated ones. Concretely:

1. **Mode B/D/E retroactive in-place edits.** May the agent edit `## REQUIREMENTS` sections of Validated ADR OBPIs to add a sibling `## Acceptance Criteria` section with REQ identifiers? The criteria are derived 1:1 from the existing REQUIREMENTS prose — no semantic change, only formal identification.
   - **In favor:** smallest faithful remedy; preserves intent; mechanical transformation.
   - **Against:** writes against `lifecycle: Validated` documents, which the closeout ceremony just declared "done."

2. **Mode C/F historical artifacts.** ADR-0.7.0 (skeleton OBPIs) and ADR-0.0.2 (no OBPIs at all) pre-date the OBPI brief contract entirely. Should the agent:
   - (a) author retroactive briefs to fit them into the contract, or
   - (b) mark them as "historical, exempt from REQ coverage" via some new flag, or
   - (c) leave them and document the exception in this audit only?

3. **REQ-ID granularity for legacy REQUIREMENTS lines.** Some `## REQUIREMENTS (FAIL-CLOSED)` entries are coarse (one numbered line ~= "Closeout ceremony skill blocks on missing product proof") while others are fine-grained. Should the agent split coarse requirements into multiple REQ IDs (one per testable claim) or preserve the 1:1 mapping (one REQ per existing numbered line)?

4. **Mode-A handling.** ADR-0.9.0 has 16 doc-kind REQs and is correctly excluded from coverage — but it's also invisible to operators looking at the graph. Should `gz covers` grow a `--include-doc` flag, or is the current behavior the intended contract?

## Recommended Phase 3 sequencing

If operator approves in-place edits for Modes B/D/E:

1. **First:** ADR-0.23.0 (4 OBPIs) — unblocks GHI #158 and Phase 4 ceremony-test decoration. Highest-leverage starting point because the umbrella explicitly named it.
2. **Second:** the cluster of ceremony-adjacent ADRs that govern the closeout surface — ADR-0.18.0, ADR-0.19.0 (already covered), ADR-0.22.0 (already covered), ADR-0.24.0. Establishes a coherent governance neighborhood for the ceremony test layer.
3. **Third:** the 0.27.0–0.40.0 absorption family (199 OBPIs). Mechanical bulk work; can be parallelized via subagents per-ADR if the operator approves.
4. **Fourth:** Mode D (the early 0.x.0 pre-release ADRs).
5. **Fifth:** ADR-0.0.1 (Mode B, foundational).

## What this audit does not do

- It does not edit any brief. The remediation is Phase 3, not Phase 1.
- It does not file new GHIs. The umbrella tracks the work and blocks the rest of the program.
- It does not decide whether to add `gz validate` enforcement. Phase 6 covers that.
- It does not address the underlying agent behavior (test-dump theater, TASK bypass). GHI #157 and Phase 6 cover that separately.

## Next step

Present this report to the operator. Pause Phase 3 until the operator answers the four Phase 2 questions above.
