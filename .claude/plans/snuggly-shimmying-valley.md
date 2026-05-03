# Plan — OBPI-0.0.26-05-bdd-coverage

**OBPI:** OBPI-0.0.26-05-bdd-coverage
**Parent ADR:** ADR-0.0.26-evaluation-feedback-loop-doctrine (foundation, heavy lane)
**Lane:** Heavy
**Brief:** `docs/design/adr/foundation/ADR-0.0.26-evaluation-feedback-loop-doctrine/obpis/OBPI-0.0.26-05-bdd-coverage.md`

## Context

ADR-0.0.26 codifies the evaluation-feedback loop. OBPIs 01–04 are
`attested_completed` and shipped:

- **01** — `adr-evaluation` ledger event emission via `gz adr evaluate`;
  `gz validate --documents` recognizes the new event shape.
- **02** — `gz validate --evaluation-justify-binding` fail-closed gate
  (low score < 3.0 OR ≥3 red-team challenges fired ⇒ require justify
  artifact).
- **03** — `eval-feedback-cluster` chore that reads recent
  `adr-evaluation` events, clusters by weak dimension, emits
  `ProposalRecord` JSON when a cluster recurrence ≥3.
- **04** — `gz chores propose-ghi` (TTY + `PROPOSE` confirm files GHI;
  headless = advisory-only) and `Eval-feedback-source:` commit-trailer
  validator (rule-edit commit closing an `eval-feedback`-labeled GHI must
  carry the trailer).

OBPI-05 closes the heavy-lane gate: author behave scenarios that exercise
the full loop end-to-end and tag each upstream REQ with
`@REQ-0.0.26-NN-MM` so `gz validate --behave-req-tags` exits 0. The audit
at `src/gzkit/governance/trust_audits/briefs.py:203` enumerates heavy
OBPI briefs from ADR-0.0.26 and asserts every REQ in their Acceptance
Criteria has a matching `@REQ-X.Y.Z-NN-MM` tag somewhere under
`features/**`. Without this OBPI, the audit would fail closed for every
REQ in OBPIs 01–04 and Gate 4 cannot fire on ADR-0.0.26.

`STOP-on-BLOCKERS` clause satisfied: OBPIs 01–04 are all
`attested_completed` per `uv run gz adr status ADR-0.0.26`.

## Files

### Created (in scope)

- `features/evaluation_feedback_loop.feature` — heavy-lane behave feature
  with `@REQ-0.0.26-NN-MM` scenario tags covering all REQs from OBPIs
  01–05. Top-level feature tag `@adr-0.0.26 @heavy @foundation`.
- `features/steps/evaluation_feedback_loop_steps.py` — step definitions.
  Mocks `gh` via `subprocess.run` patching at the call sites in
  `gzkit.commands.chores_propose_ghi_cmd` and
  `gzkit.commands.validate_cmd._validate_eval_feedback_trailer`. Mocks
  `sys.stdin.isatty` / `sys.stdout.isatty` and `builtins.input` for the
  TTY+PROPOSE path. Reuses canonical `When I run the gz command "..."`
  and `Then the command exits with code N` from `features/steps/gz_steps.py`.
- `tests/fixtures/evaluation/justify-scaffold.md` — minimal complete
  `gz-justify` walkthrough used by binding-gate scenarios to satisfy the
  "qualifying justify artifact" condition.
- `tests/fixtures/evaluation/proposal-template.json` — `ProposalRecord`
  fixture for propose-ghi scenarios; mirrors the shape in
  `tests/commands/test_chores_propose_ghi.py::_write_proposal`.

### Modified (in scope)

- `docs/design/adr/foundation/ADR-0.0.26-evaluation-feedback-loop-doctrine/obpis/OBPI-0.0.26-05-bdd-coverage.md` —
  fill `### Implementation Summary` and `### Key Proof` H3 evidence
  sections (per `.claude/rules/brief-heading-conventions.md`), tick
  Discovery Checklist, set frontmatter `status: Completed` at Stage 5.

### Read-only references

- `src/gzkit/governance/trust_audits/briefs.py:113-245` — `audit_behave_req_tags`
  and waiver loader.
- `src/gzkit/governance/trust_audits/evaluation_justify_binding.py` —
  binding-gate validator (OBPI-02).
- `src/gzkit/chores/eval_feedback_cluster_lib.py:53-69` —
  `ProposalRecord` schema (OBPI-03).
- `src/gzkit/commands/chores_propose_ghi_cmd.py:42-126` — TTY/headless
  branches (OBPI-04).
- `src/gzkit/commands/validate_cmd.py:178-231` —
  `_validate_eval_feedback_trailer` (OBPI-04).
- `src/gzkit/ledger_events.py:241` — `adr_evaluation_event` factory.
- `src/gzkit/events.py:436` — `AdrEvaluationEvent` typed model.
- `data/eval_feedback_thresholds.json` — read for REQ-02-05 dynamic
  threshold scenario.
- `data/behave_coverage_waivers.json` — read-only; no waiver added for
  OBPI-0.0.26-NN.
- `features/environment.py` — already runs each scenario in a fresh
  tempdir; no changes needed.
- `features/steps/gz_steps.py` — reused canonical When/Then steps and
  `_invoke()` helper.
- `tests/commands/common.py:258` — `_quick_init(mode="heavy")` already
  used by other heavy-lane features.

## Scenario design (24 upstream REQs + 3 OBPI-05 REQs = 27 tag coverage)

REQ tags by scenario (each scenario carries one or more `@REQ-0.0.26-NN-MM`
tags above the `Scenario:` line):

| # | Scenario | REQ tags |
|---|----------|---------|
| 1 | adr-evaluation event is appended on successful evaluation | REQ-0.0.26-01-01 |
| 2 | malformed evaluation does not emit an event | REQ-0.0.26-01-02 |
| 3 | gz validate --documents accepts the adr-evaluation event shape | REQ-0.0.26-01-03 |
| 4 | repeated evaluations append distinct timestamps (no upsert) | REQ-0.0.26-01-04 |
| 5 | binding gate fails closed on low score with no justify artifact | REQ-0.0.26-02-01 |
| 6 | binding gate fails closed on ≥3 red-team challenges fired | REQ-0.0.26-02-02 |
| 7 | binding gate exits 0 when justify artifact is present | REQ-0.0.26-02-03 |
| 8 | binding gate exits 0 when scores ≥3.0 and <3 challenges | REQ-0.0.26-02-04 |
| 9 | binding gate behavior follows updated thresholds.json | REQ-0.0.26-02-05 |
| 10 | eval-feedback-cluster appears in gz chores list | REQ-0.0.26-03-01 |
| 11 | clustering chore emits no proposal below recurrence threshold | REQ-0.0.26-03-02 |
| 12 | clustering chore emits one proposal at recurrence threshold | REQ-0.0.26-03-03 |
| 13 | clustering chore re-run is idempotent (content-hash dedup) | REQ-0.0.26-03-04 |
| 14 | gz validate --chores-layout passes for eval-feedback-cluster | REQ-0.0.26-03-05 |
| 15 | TTY + PROPOSE files GHI via gh issue create (mocked) | REQ-0.0.26-04-01, REQ-0.0.26-04-12 |
| 16 | headless propose-ghi marks proposal advisory-only | REQ-0.0.26-04-02 |
| 17 | propose-ghi re-run does not refile proposals (idempotent) | REQ-0.0.26-04-03 |
| 18 | rule-edit commit closing eval-feedback GHI without trailer fails validator | REQ-0.0.26-04-04, REQ-0.0.26-05-03 |
| 19 | rule-edit commit with Eval-feedback-source: trailer passes validator | REQ-0.0.26-04-05 |
| 20 | ProposalRecord deserializes with default optional fields | REQ-0.0.26-04-10 |
| 21 | full evaluation-feedback loop end-to-end traverses every transition | REQ-0.0.26-05-01, REQ-0.0.26-05-02 |

Scenario 21 is the spine of the brief's REQ-05-02: synthesizes a
low-score `adr-evaluation` event → runs binding gate → exits 3 → writes
justify scaffold from fixture → re-runs gate → exits 0 → runs chore →
asserts proposal record file exists → patches gh+TTY → runs propose-ghi
→ asserts proposal record `filed=true` and `ghi_url` set.

## Mocking discipline

| Surface | Mock | Where |
|--------|------|-------|
| `gh` subprocess | `unittest.mock.patch("...subprocess.run", side_effect=fake_run)` | At each call site (`chores_propose_ghi_cmd`, `validate_cmd`) |
| `sys.stdin.isatty` / `sys.stdout.isatty` | `patch("...chores_propose_ghi_cmd.sys")` mock | Per scenario |
| `builtins.input` | `patch("builtins.input", return_value="PROPOSE")` | TTY scenarios only |
| `git` | Real `subprocess.run` to `git init` / `git commit` in per-scenario tempdir | Trailer scenarios only |
| Ledger | `gzkit.ledger.Ledger.append(adr_evaluation_event(...))` | All scenarios that need synthetic events |
| ADR fixtures | Skip — exercise validators directly against synthetic ledger events; do **not** call the real `gz adr evaluate` (avoids needing a full ADR fixture tree) | All OBPI-01 scenarios |

Patches started in step bodies must stop in `after_scenario` to avoid
leaking into the next scenario. Use `setattr(context, "_patchers", [...])`
list pattern from `features/steps/justify_steps.py:43-46`.

## Step composition

Reused (no changes):

- `When I run the gz command "{command}"` — `gz_steps.py:209`
- `Then the command exits with code {expected:d}` — `gz_steps.py:220`
- `Then the command exits non-zero` — `gz_steps.py:215`
- `Then the output contains "{text}"` — `gz_steps.py:225`
- `Then the file "{path}" exists` / `... contains "{text}"` — `gz_steps.py:230-238`
- `Then ledger event "{event}" has field "{key}" equal to "{value}"` — `gz_steps.py:255`

New (in `evaluation_feedback_loop_steps.py`):

- `Given the workspace is initialized for the evaluation-feedback loop` — calls `_quick_init("heavy")` plus seeds `data/eval_feedback_thresholds.json` from project source
- `Given an adr-evaluation event for "{artifact_id}" with dimension "{dim}" scoring {score:f}` — appends event via `Ledger.append(adr_evaluation_event(...))`
- `Given an adr-evaluation event for "{artifact_id}" fired challenges {challenges}` — same factory, populated `red_team_challenges_fired`
- `Given a complete justify scaffold exists for "{artifact_id}"` — writes `artifacts/justify/<artifact_id>-*.md` from `tests/fixtures/evaluation/justify-scaffold.md`
- `Given the eval-feedback threshold "low_score_threshold" is set to {value:f}` — writes `data/eval_feedback_thresholds.json`
- `Given a proposal record exists for cluster "{key}"` — writes file from `tests/fixtures/evaluation/proposal-template.json` into `.gzkit/chores/eval-feedback-cluster/proofs/`
- `Given gh issue create returns "{url}"` — patches `chores_propose_ghi_cmd.subprocess.run`
- `Given gh issue view labels for {number} include "{label}"` — patches `validate_cmd.subprocess.run` for label lookup
- `Given the environment is interactive (TTY)` / `Given the environment is headless` — patches `sys.stdin.isatty`
- `Given the operator confirms with "PROPOSE"` — patches `builtins.input`
- `Given a git repo with a rule-edit commit closing GHI {number}` — `git init`, write file under `.gzkit/rules/`, commit
- `Given the commit body includes a "Eval-feedback-source: {value}"` — extends prior commit message via amend
- `Then the proposal record at "{path}" has "{key}" equal to "{value}"` — JSON path assertion
- `Then the proposal record at "{path}" has "{key}" equal to true` (boolean variant)
- `Then a proposal record exists under ".gzkit/chores/eval-feedback-cluster/proofs/"` — glob assertion

## Brief evidence section update (Stage 5)

Per `.claude/rules/brief-heading-conventions.md`, evidence sections must
be H3 (`###`). The current brief has `### Implementation Summary` and
`### Key Proof` slots — populate them with:

- ARB receipt IDs (lint, typecheck, unittest, behave, mkdocs)
- `gz validate --behave-req-tags` output (exit 0)
- `gz covers OBPI-0.0.26-05 --json` output (uncovered_reqs == 0)
- Files created/modified, scenarios added (21), date, attestation status

Set `status: Completed` in frontmatter at Stage 5 via `gz obpi complete`.

## Verification (Stage 3)

```bash
# Phase 1 — baseline ARB receipts (always)
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q

# Phase 1 — heavy lane additions
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz arb step --name behave -- uv run -m behave features/evaluation_feedback_loop.feature
uv run gz validate --documents
uv run gz validate --behave-req-tags

# Phase 1b — REQ → @covers parity gate
uv run gz covers OBPI-0.0.26-05 --json   # uncovered_reqs == 0

# Phase 2 — brief-specific verification
uv run -m behave features/evaluation_feedback_loop.feature   # exit 0
```

## Risks and mitigations

- **Behave step state leak.** Each scenario runs in a fresh tempdir
  (`features/environment.py`), but `unittest.mock.patch` patches persist
  across scenarios unless explicitly stopped. Mitigation: store patcher
  list on `context`, stop them all in a custom `after_scenario` hook in
  the step file (or extend `features/environment.py:18` with a
  loop-local cleanup).
- **`gz adr evaluate` invocation cost.** Running the real evaluate
  command would require a full ADR fixture tree. Mitigation: scenarios
  exercise downstream validators (`--documents`, `--evaluation-justify-binding`)
  directly against synthetic `adr-evaluation` ledger events seeded via
  `Ledger.append` + `adr_evaluation_event` factory. The emission contract
  itself is already pinned by `tests/governance/test_evaluation_event.py`
  unit tests (OBPI-01); behave covers the read-side validators and the
  cross-OBPI loop.
- **Trailer-validator commit lookup.** `_validate_eval_feedback_trailer`
  reads HEAD via `_head_commit_message_and_files`. Mitigation: scenarios
  18–19 do real `git init` + `git commit` in the per-scenario tempdir
  (existing pattern in `features/steps/gz_steps.py:142-156`); `gh issue
  view` for label lookup is the only mock.
- **`gz chores run` requires real chore registration.** Mitigation: a
  workspace initialized via `_quick_init("heavy")` includes the package
  resource resolution path; the chore is registered in
  `src/gzkit/chores/registry.json` and resolves via package fallback.
- **`features/environment.py` may need extension.** If patcher cleanup
  needs to be feature-wide, the step file's own `after_scenario` is not
  guaranteed to fire. Confirmed: `features/environment.py:18`'s
  `after_scenario` is the global hook; per-feature cleanup belongs in a
  dedicated `before_scenario`/`after_scenario` pair inside the step file
  using `behave.use_fixture` or by storing patchers on `context` and
  iterating in a step-file-level helper called from a final
  `Given`/`Then`. Plan: keep patchers on `context._patchers` list, stop
  in a `before_scenario`-style helper invoked at start of each scenario
  via a `Given the workspace is initialized for the evaluation-feedback
  loop` step. This mirrors the pattern at `justify_steps.py:139-143`.

## Out of scope (denied paths from brief)

- `src/**` — all production code already landed in OBPIs 01–04
- `tests/**` (unit tier) — unit coverage already landed in OBPIs 01–04
- Any path not in Allowed Paths

## Stage 5 sync sketch

Two-sync pattern per `gz-obpi-pipeline` skill:

1. Closure-narrative gate (preview Implementation Summary + Key Proof to operator)
2. `uv run gz obpi precomplete OBPI-0.0.26-05-bdd-coverage`
3. `uv run gz obpi complete OBPI-0.0.26-05-bdd-coverage --attestor "g0" --attestation-text "<verbatim>" --attestor-present --implementation-summary "..." --key-proof "..."` (Heavy + foundation ⇒ TTY-equivalent gate; `--attestor-present` satisfies co-presence proxy via active pipeline marker)
4. `uv run gz obpi lock release OBPI-0.0.26-05-bdd-coverage`
5. Pipeline marker cleanup
6. `uv run gz git-sync --apply` (commit #1 — governance edits)
7. `uv run gz obpi reconcile OBPI-0.0.26-05-bdd-coverage`
8. `uv run gz adr status ADR-0.0.26 --json`
9. `uv run gz git-sync --apply` (commit #2 — reconcile output)
