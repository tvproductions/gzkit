---
id: OBPI-0.0.65-04-orientation-single-location-scan
parent: ADR-0.0.65-handoff-system-consolidation
item: 4
lane: Heavy
status: Completed
req_atomic:
  - REQ-0.0.65-04-01  # The single ~5-line collapse of `_candidate_handoff_dirs()` to one path is one indivisible edit — no labor unit below the REQ.
  - REQ-0.0.65-04-02  # Proven by that same collapse via the existing `render(...)` harness (newest-wins over the single surface) — no separate labor.
  - REQ-0.0.65-04-03  # The GHI #529 workaround block + comment deletion IS the same single edit — the absence assertion carries no independent labor.
---

# OBPI-0.0.65-04-orientation-single-location-scan: **orientation-single-location-scan** — Collapse `_candidate_handoff_dirs()` in `scripts/session_orientation.py` to a single-surface scan of `.gzkit/handoffs/`. Delete the GHI #529 dual-scan workaround. Update orientation tests. (Depends on OBPI-01 completion: cannot collapse the scan until the per-ADR sources are empty.)

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.65-handoff-system-consolidation/ADR-0.0.65-handoff-system-consolidation.md`
- **Checklist Item:** #4 - "OBPI-0.0.65-04: **orientation-single-location-scan** — Collapse `_candidate_handoff_dirs()` in `scripts/session_orientation.py` to a single-surface scan of `.gzkit/handoffs/`. Delete the GHI #529 dual-scan workaround. Update orientation tests. (Depends on OBPI-01 completion: cannot collapse the scan until the per-ADR sources are empty.)"

**Status:** Completed

## Objective

Collapse `scripts/session_orientation.py::_candidate_handoff_dirs()` to scan only `.gzkit/handoffs/`, deleting the GHI #529 dual-scan workaround that united that surface with per-ADR `handoffs/` directories. This OBPI implements ADR-0.0.65 § Decision item 4 ("Align the orientation reader with the resolved canonical location") and requires OBPI-0.0.65-01 to complete first — until the migration runs, the per-ADR directories still hold handoff files and collapsing the scan would hide them.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `scripts/session_orientation.py` — collapse `_candidate_handoff_dirs()` to a single-element sequence containing `Path(".gzkit/handoffs")`; delete the dual-scan workaround and its GHI #529 comment marker
- `tests/scripts/test_session_orientation.py` — extend existing test module with single-scan behavioral assertions

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `.gzkit/skills/gz-session-handoff/SKILL.md` — OBPI-0.0.65-01 scope (skill doctrine amendment)
- `.gzkit/handoffs/` (content) — OBPI-0.0.65-01 scope (migration); OBPI-04 reads the directory but does not modify its contents
- `docs/design/adr/**/handoffs/` — OBPI-0.0.65-01 scope (sources to be migrated); OBPI-04 assumes these directories are empty by the time it runs
- `src/gzkit/handoff_api.py` — OBPI-0.0.65-02 scope (programmatic API)
- `src/gzkit/cli/**`, `src/gzkit/commands/**` — OBPI-0.0.65-03 scope (the future handoff CLI verb)
- `src/gzkit/handoff_validation.py` — validator-logic stays out of scope
- New runtime dependencies
- CI files, lockfiles
- All other paths not enumerated under Allowed Paths

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. ALWAYS: `_candidate_handoff_dirs()` returns a sequence containing exactly one path — `.gzkit/handoffs/` resolved against the project root.
2. NEVER: Reference per-ADR `handoffs/` directories from inside `scripts/session_orientation.py` (no `rglob("handoffs/*.md")`, no `docs/design/adr` traversal, no union of source surfaces).
3. ALWAYS: The GHI #529 dual-scan workaround comment block and its accompanying code are removed; the file post-edit reads as if the union scan was never introduced.
4. STOP-on-BLOCKERS: this OBPI requires OBPI-0.0.65-01 to be `attested_completed`. If the per-ADR `handoffs/` directories still hold `.md` files at implementation time, HALT and surface the blocker — do not proceed with the scan collapse.
5. ALWAYS: Existing orientation tests under `tests/scripts/test_session_orientation.py` remain green; new tests assert the single-scan invariant directly.
6. ALWAYS: The orientation script's output shape, character budget, and section ordering remain stable (no visible regression to operators reading the SessionStart injection).
7. NEVER: Touch `.gzkit/skills/gz-session-handoff/SKILL.md`, `src/gzkit/handoff_api.py`, or any CLI parser surface — those are sibling OBPI scopes.
8. ALWAYS: Verification commands stay shell-less (no `&&`, `||`, `|`, `;`, `$(...)`, or redirects per GHI #415).

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.65-handoff-system-consolidation/ADR-0.0.65-handoff-system-consolidation.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Parent ADR exists: `docs/design/adr/foundation/ADR-0.0.65-handoff-system-consolidation/ADR-0.0.65-handoff-system-consolidation.md`
- [ ] Source file exists: `scripts/session_orientation.py` (currently 421 lines; the workaround sits inside `_candidate_handoff_dirs()`)
- [ ] Test file exists: `tests/scripts/test_session_orientation.py`
- [ ] OBPI-0.0.65-01 status is `attested_completed` — confirmed via `uv run gz status`; this OBPI is blocked until the migration lands
- [ ] Per-ADR `handoffs/` directories are empty: a clean check via `find docs/design/adr -name "*.md" -path "*/handoffs/*"` must return zero results before scan collapse

**Existing Code (understand current state):**

- [ ] Read `scripts/session_orientation.py::_candidate_handoff_dirs` — locate the dual-scan workaround block and the GHI #529 comment marker; understand the current path-yielding behavior
- [ ] Read `scripts/session_orientation.py::collect_handoff` — confirm the consumer that calls `_candidate_handoff_dirs()` and the `adr_id`-frontmatter filter that excludes the `.gzkit/handoffs/AGENTS.md` rules file (GHI #529 fix #2)
- [ ] Read `tests/scripts/test_session_orientation.py` — establish the existing test patterns and assertion style to extend with new single-scan tests
- [ ] Read `tests/governance/test_orientation_freshness.py` — confirm freshness-bucket tests remain orthogonal to the scan-collapse change
- [ ] Read commit `2ab33914` (`fix(orientation): … (GHI #529)`) — understand the original union-scan intent so the deletion is principled rather than blind

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. These are CONSTRUCTION HOUSEKEEPING (lint, type,
     test, mkdocs) — they prove the codebase is healthy, not what the OBPI
     yielded. The yielded product belongs in the `## Demo` section below.

     AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. The
     OBPI-pipeline verify stage executes commands via shlex.split + shell=False
     (GHI #415); compound commands are blocked at authoring time by
     gz validate --brief-command-shape and rejected at the verify stage.
     Write multi-step verification as separate uv run ... lines. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.scripts.test_session_orientation
uv run -m unittest tests.governance.test_orientation_freshness
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
uv run python scripts/session_orientation.py
grep -n "docs/design/adr" scripts/session_orientation.py
grep -n "GHI #529" scripts/session_orientation.py
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.65-04-01 [BEHAVIOR]: `_candidate_handoff_dirs()` returns a sequence of length 1 containing exactly `Path(".gzkit/handoffs")` resolved against the project root, regardless of whether `docs/design/adr/**/handoffs/` directories exist. Asserted by `@covers("REQ-0.0.65-04-01")` in `tests/scripts/test_session_orientation.py`.
- [ ] REQ-0.0.65-04-02 [BEHAVIOR]: When the orientation script runs against a project state where `.gzkit/handoffs/` contains valid handoffs and `docs/design/adr/**/handoffs/` is empty, the rendered "Most-recent handoff" section correctly reports the newest `.gzkit/handoffs/` entry. Asserted by `@covers("REQ-0.0.65-04-02")` in `tests/scripts/test_session_orientation.py` via the existing `render(...)` test harness.
- [ ] REQ-0.0.65-04-03 [BEHAVIOR]: `scripts/session_orientation.py` contains zero references to `docs/design/adr` and zero references to the literal string `GHI #529` (the workaround marker comment). Asserted by `@covers("REQ-0.0.65-04-03")` in `tests/scripts/test_session_orientation.py` via file-read + substring check, robust to both the contiguous literal and the segmented `repo_root / "docs" / "design" / "adr"` reconstruction.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof


Single-location scan proven three ways:

    $ grep -n "docs/design/adr\|GHI #529" scripts/session_orientation.py
    # (no output, exit 1 — both dual-scan markers removed)

    $ uv run gz covers OBPI-0.0.65-04-orientation-single-location-scan --json
    # by_obpi: total_reqs=3 covered=3 uncovered=0 behavior_uncovered=0

    $ uv run -m unittest tests.scripts.test_session_orientation
    # Ran 36 tests ... OK

Receipts: arb-step-unittest-cbbffaf182da4295a0b12cc64990b9f1, arb-ruff-4855a3166f4540f2b4e84fcc7ffe8715, arb-step-typecheck-acff906fbe8d4eb8886411ed0da1df3c, arb-step-mkdocs-1846f1dd5b4f4ad9b0dfdf408894f318.

### Step 4b — Independent Adversarial Validation

- **Adversary:** Codex (tier 1, `codex-cli 0.144.4`, different vendor) — availability
  checked `ready: true`, so the tier-2 Claude subagent was forbidden (GHI #678).
- **Verdict:** `REFUTED-WITH-CAVEATS`. The adversary confirmed the production behavior
  is correct (`_candidate_handoff_dirs()` returns only `.gzkit/handoffs/`;
  `collect_handoff()` has no alternate discovery route; both semantic tests are
  falsifiable; the real orientation run renders the single-surface handoff), but named
  three evidence holes, each fixed before attestation:
  1. **REQ-02 coverage overstated** — the covering test asserted on `collect_handoff()`'s
     dict but never called `render()`, though the REQ names the *rendered* "Most-recent
     handoff" section. **Resolved:** `test_ignores_adr_package_handoffs_single_scan` now
     drives `render()` and asserts the rendered section reports the `.gzkit/handoffs/`
     entry and omits the newer off-surface ADR handoff.
  2. **REQ-03 assertion weak** — the grep caught the contiguous literal `docs/design/adr`
     but missed the *segmented* form `repo_root / "docs" / "design" / "adr"` that the
     removed code actually used. **Resolved:** the test now squeezes out quotes/whitespace/
     slashes and asserts `docsdesignadr` absent, plus the `**/handoffs` glob fingerprint.
  3. **Duplicate `REQ-0.0.65-04-03`** in the brief made `gz covers` report `total_reqs: 4`
     with a duplicated entry. **Resolved:** the stray untyped duplicate line was removed;
     parity is now honest `total_reqs: 3`.
- **Re-validation:** all three strengthened tests re-witnessed at
  `failure_class=assertion` via `gz arb red`; scoped suite 36/36 green; lint + typecheck
  clean; `gz covers` now `3/3` covered, `0` uncovered.

### Implementation Summary


- Change: collapsed `scripts/session_orientation.py::_candidate_handoff_dirs()` to return a single-element list `[repo_root / ".gzkit" / "handoffs"]`, deleting the GHI #529 dual-scan union with per-ADR `docs/design/adr/**/handoffs/` directories (OBPI-0.0.65-01 had migrated all handoffs into the canonical store).
- Tests: replaced the dual-scan union test with three `@covers`-decorated single-scan tests in `tests/scripts/test_session_orientation.py`; REQ-02's test drives `render()` and asserts the rendered "Most-recent handoff" section; REQ-03's test is robust to the segmented path reconstruction and the `**/handoffs` glob.
- Files modified: `scripts/session_orientation.py`, `tests/scripts/test_session_orientation.py`.
- REQ coverage: REQ-0.0.65-04-01/-02/-03 (all BEHAVIOR), 3/3 covered, each RED-witnessed at `failure_class=assertion`.
- Date completed: 2026-07-14.
- Attestation: g0 (operator-verbatim "attest completed"), Heavy lane Gate 5.
- Defects: the duplicate `REQ-0.0.65-04-03` acceptance-criteria line was removed during closeout (Step-4b Codex adversary caveat); parity now honest 3/3.

## Tracked Defects

- REQ-count drift (RESOLVED 2026-07-14): the duplicate `REQ-0.0.65-04-03` acceptance-criteria line (an untyped "evidence is recorded" boilerplate reusing the ID) was removed during closeout after the Step-4b Codex adversary flagged it as blocking honest 3-REQ parity. Acceptance Criteria now carries exactly three BEHAVIOR REQs, consistent with `req_atomic:`.

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.65-04 orientation single-location scan: `_candidate_handoff_dirs()` collapsed to `.gzkit/handoffs/` only (GHI #529 dual-scan deleted); 3/3 BEHAVIOR REQs covered and RED assertion-class, scoped suite 36/36 green, mkdocs --strict clean; Step-4b Codex tier-1 adversary returned REFUTED-WITH-CAVEATS, all three caveats fixed and re-validated before attestation. Receipts arb-step-unittest-cbbffaf182da4295a0b12cc64990b9f1, arb-ruff-4855a3166f4540f2b4e84fcc7ffe8715, arb-step-typecheck-acff906fbe8d4eb8886411ed0da1df3c, arb-step-mkdocs-1846f1dd5b4f4ad9b0dfdf408894f318.
- Date: 2026-07-15

---

**Date Completed:** 2026-07-15

**Evidence Hash:** -
