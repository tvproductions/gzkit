---
id: OBPI-0.0.70-02-session-correction-mining
parent: ADR-0.0.70-turn-end-feedback-and-correction-mining
item: 2
lane: Lite
status: Completed
# req_atomic (GHI #590): every REQ is one indivisible acceptance facet of a
# single cohesive deliverable — one read-only stdlib miner module + its chore
# package. The labor was authoring one miner (clustering, scrub, fail-soft,
# idempotency, dry-run) + one chore package, not eight separable efforts; each
# REQ maps to one test class / proof channel with no multi-step labor below it.
req_atomic:
  - REQ-0.0.70-02-01  # cluster >=3 -> proposal — TestClustering
  - REQ-0.0.70-02-02  # below-threshold -> nothing — TestClustering
  - REQ-0.0.70-02-03  # fail-soft — TestFailSoft
  - REQ-0.0.70-02-04  # email scrub (quote + cluster_key) — TestScrubbing
  - REQ-0.0.70-02-05  # idempotency — TestIdempotency
  - REQ-0.0.70-02-06  # chore package — gz validate --chores-layout (SUPPORT)
  - REQ-0.0.70-02-07  # read-only/candidates-only — parent ADR Boundary Invariants 2&4
  - REQ-0.0.70-02-08  # --dry-run writes nothing — TestDryRun
---

# OBPI-0.0.70-02-session-correction-mining: Session Correction Mining

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining/ADR-0.0.70-turn-end-feedback-and-correction-mining.md`
- **Checklist Item:** #2 - "Session-correction-mining chore — stdlib miner over `~/.claude/projects` transcripts in `src/gzkit/insights/`; corrective-marker heuristics; recurrence >= 3 clustering; PII-scrubbed proposal records to `.gzkit/chores/session-correction-mining/proofs/`; CHORE.md + acceptance criteria + registry entry; `gz validate --chores-layout` green; unit tests"

**Status:** Completed

## Objective

A read-only stdlib miner (`src/gzkit/insights/correction_mining.py`) walks Claude Code
session transcripts under `~/.claude/projects/`, detects operator-correction patterns
(corrective-marker user messages following assistant turns), clusters recurrences >= 3
across distinct sessions, and emits PII-scrubbed, idempotent proposal records into
`.gzkit/chores/session-correction-mining/proofs/` as candidates for the advisory-scorecard
Promotable→Mechanical ladder; the chore package (CHORE.md + acceptance.json + registry
row) mirrors eval-feedback-cluster and `gz validate --chores-layout` stays green.

## Lane

**Lite** - This OBPI remains internal to the promoted ADR implementation scope.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining/ADR-0.0.70-turn-end-feedback-and-correction-mining.md` — parent ADR for intent and scope
- `src/gzkit/insights/correction_mining.py` **CREATE** — NEW: miner module
- `tests/chores/test_session_correction_mining.py` **CREATE** — NEW: unit tests
- `.gzkit/chores/session-correction-mining/` **CREATE** — NEW: chore package (CHORE.md, acceptance.json, proofs/)
- `.gzkit/chores/registry.json` — registry row
- `src/gzkit/chores/session-correction-mining/` **CREATE** — NEW: pkg copy, written ONLY by `gz agent sync control-surfaces`

> The transcript directory under the user home (Claude Code projects store) is a
> READ-ONLY input surface outside the repository — the miner reads it, never writes it.
- `docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining/obpis/OBPI-0.0.70-02-session-correction-mining.md` — this brief (evidence recording)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: The miner MUST be read-only everywhere except `.gzkit/chores/session-correction-mining/proofs/` (parent ADR § Boundary Invariants, Invariant 2).
1. REQUIREMENT: Emitted proposals MUST quote at most one line of operator text and MUST scrub email addresses; the operator-PII rule binds every record.
1. REQUIREMENT: Malformed or absent transcripts MUST yield zero proposals — never an exception escaping the miner.
1. REQUIREMENT: Proposals MUST be idempotent by content hash over (cluster_key, sorted session ids) — re-runs never duplicate (eval-feedback-cluster precedent).
1. REQUIREMENT: The module MUST import stdlib only (parent ADR § Boundary Invariants, Invariant 3); the recurrence threshold defaults to 3 and is a function parameter.
1. REQUIREMENT: The initial corrective-marker lexicon is pinned as a module-level constant for TDD — leading-position markers ("no,", "no.", "don't", "stop", "wrong", "not what i", "i said", "again", "actually", "never", "undo", "revert") matched case-insensitively at the start of an operator message that follows an assistant turn; lexicon refinement is itself a candidate the chore mines.
1. REQUIREMENT: Output is candidates only — the miner NEVER mutates ledger, rules, or validator scopes (parent ADR § Boundary Invariants, Invariant 4).
1. ALWAYS: TDD (RED→GREEN) against fixture transcripts; tests assert REQ semantics, not incidental output strings.
1. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining/ADR-0.0.70-turn-end-feedback-and-correction-mining.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining/ADR-0.0.70-turn-end-feedback-and-correction-mining.md`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

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
uv run gz test
uv run gz validate --chores-layout

# Specific verification for this OBPI
test -f src/gzkit/insights/correction_mining.py
test -f .gzkit/chores/session-correction-mining/CHORE.md
uv run -m unittest tests.chores.test_session_correction_mining -q
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Mines the real local transcripts read-only and prints the cluster summary
# without writing proposals; drop --dry-run to write proposal records to proofs/.
uv run python -m gzkit.insights.correction_mining --dry-run
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.70-02-01 [behavior]: Given fixture transcripts containing an operator-correction pattern recurring >= 3 times across distinct sessions, when the miner runs, then it emits one proposal record per cluster carrying recurrence count, session ids, normalized pattern key, and a <=1-line scrubbed quote. (@covers test)
- [ ] REQ-0.0.70-02-02 [behavior]: Given patterns recurring below the threshold, when the miner runs, then no proposal is emitted for them. (@covers test)
- [ ] REQ-0.0.70-02-03 [behavior]: Given malformed JSONL, empty files, or an absent transcript directory, when the miner runs, then it returns zero proposals without raising. (@covers test)
- [ ] REQ-0.0.70-02-04 [behavior]: Given operator text containing an email address, when a proposal is emitted, then the quote is scrubbed of the address. (@covers test)
- [ ] REQ-0.0.70-02-05 [behavior]: Given a second run over unchanged transcripts, when the miner writes proposals, then no duplicate records are produced (content-hash idempotency). (@covers test)
- [ ] REQ-0.0.70-02-06 [support]: The chore package lands (CHORE.md, acceptance.json, proofs/, registry.json row) and canonical→pkg propagation runs. Proof: `gz validate --chores-layout` exit 0 + `gz agent sync control-surfaces` run + `artifact_edited` ledger events.
- [ ] REQ-0.0.70-02-07 [structural-fence]: The miner is read-only outside its proofs directory and emits candidates only — never mutating ledger, rules, or validator scopes. Verified at ADR-0.0.70 closeout via the parent ADR `## Boundary Invariants` (Invariants 2 and 4).
- [ ] REQ-0.0.70-02-08 [behavior]: Given `--dry-run`, when the module entrypoint runs, then it prints the cluster summary and writes nothing anywhere. (@covers test)

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
RED observed 2026-06-12: uv run -m unittest tests.chores.test_session_correction_mining -q
  -> ModuleNotFoundError (tests authored first)
GREEN: Ran 11 tests OK (REQs 02-01..05, 02-08 covered; incl. real-transcript-shape
  regression tests pinned against observed shapes from 280 real transcripts)
GREEN receipt: `arb-step-unittest-721f7a2b9dc34c24a7246422592f7c64` exit_status=0 (full suite)
```

### Code Quality

```text
Lint: `arb-ruff-891d4ff9d22045769631d134d5de49f2` exit_status=0
Typecheck: `arb-step-typecheck-9ad2c564358d443f97119b315b57acc1` exit_status=0
gz validate --chores-layout exit 0
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

Before: correction capture was compliance-dependent — Behavior Rule 11 relies on the
agent recognizing it was corrected and self-reporting to agent-insights.jsonl; the
corrections an agent vibes past left no record, and no surface read the ground-truth
transcripts. Now: a read-only stdlib miner walks `~/.claude/projects/` transcripts,
detects leading-marker operator corrections after assistant activity (meta/sidechain/
tag-injected messages excluded), clusters recurrence across sessions, and emits
PII-scrubbed idempotent proposal records — the third sensor feeding the
advisory-scorecard Promotable→Mechanical ladder (after eval-feedback-cluster and
arb-pattern-extraction).

### Key Proof


Read-only probe (observed 2026-06-12; exit 0):

    $ uv run python -m gzkit.insights.correction_mining --dry-run
    session-correction-mining: 0 cluster(s) at threshold 3 from /Users/jeff/.claude/projects/-Users-jeff-Documents-Code-gzkit

0 clusters at threshold 3 is honest null output (corrections are lexically distinct; clustering fires when phrasings repeat).

Verification receipts (Stage 3, this session):
- arb-step-unittest-eb6af3bf81c043dea15cd2250ec30b7a — 6079 tests, exit_status=0
- arb-step-unittestscoped-edf0bd63a24c4fac87ef0dc8fe0740f0 — 14 OBPI tests, exit_status=0
- arb-ruff-6e7724621ca146f79e64dcade6fe84a6 — exit_status=0
- arb-step-typecheck-167a3fd2588d4243a03067afc424c7d2 — exit_status=0
- gz validate --chores-layout exit 0; gz covers behavior_uncovered_reqs=0
Defect fixes verified end-to-end: cluster_key PII-free ('ahuimanu' absent); non-UTF-8 transcript fails soft (returns []).

### Implementation Summary


- Parent ADR Decision item 2 (verbatim): read-only stdlib miner in src/gzkit/insights/ over ~/.claude/projects transcripts; corrective-marker heuristics; recurrence>=3 clustering; PII-scrubbed proposals to chore proofs/; CHORE.md + acceptance + registry; chores-layout green; unit tests.
- Regularized rogue-committed work (commit 863250d6) through the skipped pipeline ceremony per operator ruling 2026-06-12. Three audit-found defects fixed TDD RED->GREEN: (1) _cluster_key scrubs emails before tokenizing so the git-tracked cluster_key field + proposal hash carry no operator local-part [MAJOR PII fix]; (2) _iter_corrections catches UnicodeDecodeError so non-UTF-8 transcripts fail soft, not raise [REQ-02-03]; (3) authored the missing chore README.md, synced to pkg copy.
- Files (this pass): src/gzkit/insights/correction_mining.py, tests/chores/test_session_correction_mining.py (+3 tests, now 14), .gzkit/chores/session-correction-mining/README.md (synced to src/gzkit/chores/).
- req_atomic (GHI #590): all 8 REQs atomic — one cohesive miner module + chore package.
- Date completed: 2026-06-12. Attestation: operator Gate 5 received ("attest completed").

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — session-correction-mining miner regularized through the ceremony that was skipped on the rogue run. Three audit-found defects fixed TDD RED->GREEN: cluster_key PII scrub (operator local-part no longer reaches the git-tracked field or proposal hash), UnicodeDecodeError fail-soft (REQ-02-03), and the missing chore README. 14/14 OBPI tests pass (arb-step-unittestscoped-edf0bd63a24c4fac87ef0dc8fe0740f0), full suite 6079 green (arb-step-unittest-eb6af3bf81c043dea15cd2250ec30b7a), lint+typecheck clean, chores-layout exit 0, behavior_uncovered_reqs=0. Attestor: g0, 2026-06-12.
- Date: 2026-06-12

---

**Date Completed:** 2026-06-12

**Evidence Hash:** -
