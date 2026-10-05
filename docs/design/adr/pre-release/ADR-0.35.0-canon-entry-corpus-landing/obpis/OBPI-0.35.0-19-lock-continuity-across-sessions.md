---
id: OBPI-0.35.0-19-lock-continuity-across-sessions
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 19
lane: Heavy
sensitivity: security
status: Draft
allowlist:
  - src/gzkit/commands/obpi_lock.py
  - src/gzkit/cli/parser_obpi.py
  - src/gzkit/lock_manager.py
  - src/gzkit/exchange_records.py
  - src/gzkit/governance/trust_audits/lock_exchange_coupling.py
  - src/gzkit/commands/obpi_cmd.py
  - src/gzkit/commands/obpi_complete.py
  - src/gzkit/commands/obpi_precomplete.py
  - src/gzkit/pipeline_runtime.py
  - tests/governance/test_lock_continuity.py
  - tests/governance/test_lock_exchange_coupling_validator.py
  - tests/governance/test_token_block_discipline.py
  - tests/governance/test_obpi_complete_lock_release.py
  - tests/test_obpi_lock_cmd.py
  - tests/commands/test_obpi_pipeline.py
  - features/obpi_lock_continuity.feature
  - features/steps/obpi_lock_continuity_steps.py
  - docs/user/manpages/obpi-lock-claim.md
  - docs/user/manpages/obpi-lock-release.md
  - docs/user/manpages/obpi-lock-list.md
  - docs/user/manpages/obpi-lock-check.md
  - docs/user/manpages/obpi-pipeline.md
  - docs/user/manpages/validate.md
  - docs/user/runbook.md
  - .gzkit/rules/token-block-discipline.md
  - src/gzkit/rules/token-block-discipline.md
  - .claude/rules/token-block-discipline.md
  - docs/governance/rule-version-history.md
  - docs/governance/advisory-rules-audit.md
  - docs/governance/token-block-doctrine.md
  - .gzkit/skills/gz-obpi-lock/SKILL.md
  - src/gzkit/skills/gz-obpi-lock/SKILL.md
  - .claude/skills/gz-obpi-lock/SKILL.md
  - .agents/skills/gz-obpi-lock/SKILL.md
  - .gzkit/skills/gz-obpi-pipeline/SKILL.md
  - src/gzkit/skills/gz-obpi-pipeline/SKILL.md
  - .claude/skills/gz-obpi-pipeline/SKILL.md
  - .agents/skills/gz-obpi-pipeline/SKILL.md
  - docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-19-lock-continuity-across-sessions.md
reqs:
  - REQ-0.35.0-19-01
  - REQ-0.35.0-19-02
  - REQ-0.35.0-19-03
  - REQ-0.35.0-19-04
  - REQ-0.35.0-19-05
  - REQ-0.35.0-19-06
  - REQ-0.35.0-19-07
  - REQ-0.35.0-19-08
  - REQ-0.35.0-19-09
  - REQ-0.35.0-19-10
  - REQ-0.35.0-19-11
  - REQ-0.35.0-19-12
  - REQ-0.35.0-19-13
verification:
  - uv run -m unittest tests.governance.test_lock_continuity tests.governance.test_lock_exchange_coupling_validator tests.governance.test_token_block_discipline tests.governance.test_obpi_complete_lock_release tests.test_obpi_lock_cmd tests.commands.test_obpi_pipeline
  - uv run -m behave features/obpi_lock_continuity.feature features/obpi_lock.feature features/lock_exchange_coupling.feature
  - uv run gz validate --lock-exchange-coupling
  - uv run gz validate --documents --req-kind-discipline --cli-alignment
  - uv run gz validate --sensitivity
  - uv run gz validate --rule-version-markers
  - uv run gz cli audit
  - uv run gz skill audit
  - uv run mkdocs build --strict
  - uv run gz check
---

# OBPI-0.35.0-19-lock-continuity-across-sessions: Lock Continuity Across Sessions

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #19 - "Lock continuity across sessions -- a session continuing an OBPI another session holds leaves a register entry naming both occupants, or is refused with the recovery named. Repair assignment against `ADR-0.0.41` (GHI #1176, amendment 2026-10-04)"
- **Decision Item:** § Decision item 15, verbatim - "A CHANGE OF OCCUPANT BETWEEN SESSIONS LEAVES A REGISTER ENTRY (operator-ruled 2026-10-04, GHI #1176; repair assignment). A session that continues an OBPI another session holds either leaves a register entry naming both occupants, or is refused with the recovery named. Obligation repaired: `ADR-0.0.41`, "intermediate handovers without register entries lose intent at exactly the boundaries this ADR exists to protect". No abandon category is added; a run that aborts after failed verification is answered by continuity."

**Status:** Draft

## Objective

A session that continues an OBPI whose work lock another session holds either leaves an exchange record under `.gzkit/locks/exchange/` that carries the four Sub-Invariant 2 fields and both occupants' identities and is checked by `gz validate --lock-exchange-coupling`, or is refused with the recovery command named. A run that aborted after failed verification with its lock still held can be continued by the next session on that record, without a new abandon category and without waiting for the lock's TTL.

## Repair Assignment

This brief is a repair assignment, not an extension of ADR-0.35.0's corpus intent (parent § Intent, amendment 2026-10-04). It repairs an obligation that `ADR-0.0.41-token-block-lock-discipline` stated and whose shipped surface does not meet. That ADR is `Validated` and is not reopened; the obligation keeps its original identity.

The obligation, quoted from `ADR-0.0.41`:

- § Alternatives Considered 4: "a single OBPI may span multiple lock claim/release cycles across sessions, and intermediate handovers without register entries lose intent at exactly the boundaries this ADR exists to protect."
- § Comparator Uplift: "before a compacted or resumed session continues, the lock release must prove which intent, artifact set, and handoff-register entry survived."

The REQs below are this brief's local acceptance criteria. They do not renumber or replace any REQ of ADR-0.0.41 or ADR-0.0.14.

**Current state (code reading, 2026-10-04; a dated record, line numbers as of that date):**

- A Claude Code session's lock identity includes its session id: `resolve_agent` returns `claude-code-<first 8 of CLAUDE_CODE_SESSION_ID>` (`src/gzkit/lock_manager.py:109-111`). A new session is a different agent.
- A claim by a different agent on an unexpired lock prints `CONFLICT` and exits 1 (`src/gzkit/commands/obpi_lock.py:65-74`). A release by a non-holder prints `OWNERSHIP ERROR … Use --force to override.` and exits 1 (`obpi_lock.py:186-203`). Neither message names a route by which the second session may lawfully continue: `--force` reaches only the ownership check, and the release then exits 3 for want of a register entry (`obpi_lock.py:222-247`).
- The pipeline launch reads no lock. `obpi_pipeline_cmd` (`src/gzkit/commands/obpi_cmd.py:796-982`) checks markers, the plan-audit receipt, the reconcile receipt and the operator block, then writes the marker and `pipeline_launched`. The same function serves every `--from` entry. A second session can therefore launch or re-enter under the first session's lock, and nothing records it.
- Subagents share the orchestrator's identity because they inherit its environment: a dispatched subagent's shell carries the parent's `CLAUDE_CODE_SESSION_ID`, so `resolve_agent` returns the same string (observed 2026-10-04: a subagent of session `0b94f0b0` resolved `claude-code-0b94f0b0`). No gzkit code grants this; it holds only while the harness exports that variable.
- The coupling validator replays `obpi_lock_released` events only (`src/gzkit/governance/trust_audits/lock_exchange_coupling.py:61-63`). A change of occupant that emits no release is invisible to it.
- After GHI #1167 the pipeline skill tells an agent whose abort no abandon category describes to leave the lock held. That lock then blocks the next session until its TTL, which is the wait this brief removes.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

The contract changes are a continuation route on the lock CLI, new refusal text and a recovery field on existing refusals, a pipeline launch that reads the lock, a new kind of exchange record, and a wider `gz validate --lock-exchange-coupling`.

**Sensitivity: security.** The Allowed Paths overlap three registered security surfaces in `data/security_surfaces.json`: `src/gzkit/lock_manager.py` (`subprocess_user_input`), and `src/gzkit/commands/obpi_cmd.py` and `src/gzkit/commands/obpi_complete.py` (`auth_boundaries`). `.gzkit/rules/security-sensitivity.md` therefore requires `sensitivity: security` in the frontmatter, and completion runs the heightened Gate 5 walkthrough with an `arb-step-security-scan-*` receipt. The overlap is not incidental: which session may act on a block is an identity boundary.

## Allowed Paths

This list covers the recommended rulings in § Open Design Questions. A different ruling on question 1, 3 or 6 amends it before the plan is written.

Source:

- `src/gzkit/commands/obpi_lock.py` — claim and release: the refusals name the recovery; the continuation route
- `src/gzkit/cli/parser_obpi.py` — the lock subparsers: the continuation route's registration, help text and exit codes
- `src/gzkit/lock_manager.py` — the lock data layer (registered security surface); changed only as the ruled route needs
- `src/gzkit/exchange_records.py` — the continuity record's writer, and the admit predicate that keeps it from discharging a later surrender
- `src/gzkit/governance/trust_audits/lock_exchange_coupling.py` — the validator: both identities and the four fields on a continuity record
- `src/gzkit/commands/obpi_cmd.py` — the pipeline launch and every `--from` entry read the lock (registered security surface)
- `src/gzkit/commands/obpi_complete.py`, `src/gzkit/commands/obpi_precomplete.py` — changed only if question 6(i) rules completion by a non-holder into this brief; otherwise read by the REQ-09 control tests and left untouched
- `src/gzkit/pipeline_runtime.py` — READ-ONLY import of the REQ-10 control test (the helper listing OBPIs locked by the current agent); never modified by this OBPI

Tests and scenarios:

- `tests/governance/test_lock_continuity.py` — **CREATE**, following `tests/governance/test_token_block_discipline.py`
- `tests/governance/test_lock_exchange_coupling_validator.py`
- `tests/governance/test_token_block_discipline.py`
- `tests/governance/test_obpi_complete_lock_release.py`
- `tests/test_obpi_lock_cmd.py`
- `tests/commands/test_obpi_pipeline.py`
- `features/obpi_lock_continuity.feature` — **CREATE**, following `features/obpi_lock.feature`
- `features/steps/obpi_lock_continuity_steps.py` — **CREATE**, following `features/steps/obpi_lock_steps.py`, whose existing steps it reuses unchanged

Operator documentation (Gate 3):

- `docs/user/manpages/obpi-lock-claim.md` — the refusal's recovery and the continuation route
- `docs/user/manpages/obpi-lock-release.md` — the ownership refusal's recovery; the continuity record beside the abandon and reaping records
- `docs/user/manpages/obpi-lock-list.md`, `docs/user/manpages/obpi-lock-check.md` — updated only where their output changes under the question 1 ruling
- `docs/user/manpages/obpi-pipeline.md` — the launch's behavior when another session holds the lock
- `docs/user/manpages/validate.md` — the `--lock-exchange-coupling` section: what it checks on a continuity record
- `docs/user/runbook.md` — the lock-handling passages (completion surrender, the lock verb list) gain the continuation step

Rule (canonical text; wording and version bump are operator-ruled, question 5):

- `.gzkit/rules/token-block-discipline.md` — the continuity rule, edited here and never in a mirror
- `src/gzkit/rules/token-block-discipline.md`, `.claude/rules/token-block-discipline.md` — generated mirrors, written only by `uv run gz agent sync control-surfaces`, never hand-edited
- `docs/governance/rule-version-history.md` — the superseded rule-version line
- `docs/governance/advisory-rules-audit.md` — the rule's version cell and the Coverage Ledger row for the new binding clause
- `docs/governance/token-block-doctrine.md` — the rationale, so the rule body carries one sentence and a pointer

Skills (the wielding surfaces):

- `.gzkit/skills/gz-obpi-lock/SKILL.md` — Lock Rules, Release and Integration: what a second session does on a conflict
- `src/gzkit/skills/gz-obpi-lock/SKILL.md`, `.claude/skills/gz-obpi-lock/SKILL.md`, `.agents/skills/gz-obpi-lock/SKILL.md` — generated mirrors, never hand-edited
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` — Stage 1 step 9, § Abort surrender and § Error Recovery
- `src/gzkit/skills/gz-obpi-pipeline/SKILL.md`, `.claude/skills/gz-obpi-pipeline/SKILL.md`, `.agents/skills/gz-obpi-pipeline/SKILL.md` — generated mirrors, never hand-edited

This brief:

- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-19-lock-continuity-across-sessions.md`

## Denied Paths

- `src/gzkit/ledger_events.py`, `src/gzkit/events.py`, `src/gzkit/schemas/ledger.json` — no new ledger event type and no new payload key. The ruling on question 1 (A, 2026-10-04) is expressible with the existing `obpi_lock_released` and `obpi_lock_claimed` events, and the `handoff_path` key is frozen on the wire (GHI #763). `ledger_events.py` is a registered security surface; a ruling that needs a new event type amends this list first.
- `src/gzkit/handoff_api.py`, `src/gzkit/handoff_validation.py`, `src/gzkit/session_exit.py`, `.gzkit/skills/gz-session-handoff/**`, `.gzkit/handoffs/**` — the session system. A change of occupant is an exchange matter (`.gzkit/rules/token-block-discipline.md` § Three subjects); a session handoff is never the continuity record and never its evidence.
- `scripts/session_orientation.py`, `src/gzkit/commands/preflight.py` — the SessionStart and preflight reapers. A TTL reap behaves as it does now.
- `.claude/hooks/**`, `src/gzkit/hooks/**` — the pipeline gate's lock-keyed arm reads the same per-agent helper and is not changed. This holds under the ruling on question 1 (A, 2026-10-04): the continuing session becomes the holder.
- `src/gzkit/pipeline_markers.py`, `src/gzkit/commands/obpi_stages.py` — marker shape and stage records belong to checklist items 15-18 of the parent ADR. This brief reads the lock at launch and writes no marker field.
- `.gzkit/ledger.jsonl`, `.gzkit/locks/**` — live locks, exchange records and ledger rows are written only by `gz` commands run for real work. Fixtures live in temporary directories.
- `docs/design/adr/foundation/ADR-0.0.41-token-block-lock-discipline/**`, `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md` — the repaired ADR is `Validated` and unamendable; the parent ADR is not edited by this OBPI.
- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: A change of occupant is a session whose resolved identity differs from the holder of an unexpired lock on the same OBPI. It MUST end in exactly one of two states: a continuity record exists (Requirement 2), or the command was refused and wrote nothing (Requirement 4). No path through lock claim, lock release, the pipeline launch or a `--from` re-entry leaves work proceeding under another session's lock with no record.
2. REQUIREMENT: The continuity record is an exchange record under `.gzkit/locks/exchange/`, written by an exchange writer in `src/gzkit/exchange_records.py` and by nothing else. It carries, on the structured channel the validator reads, the four Sub-Invariant 2 fields (`last_lock_event_timestamp` equal to the prior occupant's claim time, `last_commit_sha`, `branch`, and a `## Decisions Made` section) and both identities: the prior occupant and the continuing occupant. `## Decisions Made` states who continued from whom and why. Free-body prose does not satisfy the identity requirement.
3. REQUIREMENT: The record is written BEFORE any lock, marker or ledger change that depends on it. If it cannot be written, nothing else changes and the command reports the failure. This is the order Sub-Invariants 3 and 6 already use.
4. REQUIREMENT: Every refusal emits three-part recovery prose (`.gzkit/rules/guardrail-feedback-prose.md`): what was refused (the holder, its claim time, the remaining TTL), why (token-block discipline: a change of occupant needs a register entry), and the runnable continuation command. A refusal never names `--force` alone or an `--abandon` category that misdescribes the situation (GHI #1167). Each refusing surface asserts its own prose in its covering test.
5. REQUIREMENT: `gz validate --lock-exchange-coupling` reaches a continuity record from the ledger replay and fails closed (exit 3), naming the OBPI, when the record is absent from disk, is not in git's index, lacks any Sub-Invariant 2 field, or lacks either identity. It imposes nothing on events recorded before this brief lands: it stays green over the real ledger.
6. NEVER add an abandon category. `ABANDON_CATEGORIES` and `parse_abandon_spec` are unchanged, and the continuity record carries no `abandoned: true` and no category. The rule says "A new category needs ADR-backed rationale and a checklist item in the next maintenance ADR"; parent Decision item 15 answers the failed-verification abort by continuity instead.
7. NEVER let a `CHECKPOINT` handoff, a session handoff under `.gzkit/handoffs/`, or a continuity record discharge a later surrender. `is_exchange_register_entry` stays default-deny. A continuity record accounts for the one change of occupant it records; the continuing session's own release still needs its own register entry or `--abandon`.
8. NEVER change the controls: a same-agent re-claim, a TTL reap by `reap_expired_locks`, and the holder's completion surrender behave as they do now. The exit codes and `--json` `status` values of today's refusals stay (`conflict`, exit 1; `ownership_error`, exit 1); the recovery is added to them. Every attested REQ of ADR-0.0.14 and ADR-0.0.41 keeps passing.
9. NEVER treat a process that resolves to the holder's own identity as a change of occupant. Subagents dispatched under the orchestrator's session keep claiming, launching and writing without a refusal and without a continuity record.
10. NEVER perform a continuation as a side effect of a command that only reads lock state: `gz obpi lock check`, `gz obpi lock list`, and SessionStart orientation change no occupant.
11. ALWAYS land the coupled surfaces in the same change set: the rule (wording and version bump as the operator rules them, the superseded version line lifted to the history, the scorecard row), the manpages, the runbook, both skills, and the mirrors via `uv run gz agent sync control-surfaces`. The rule edit stays inside its budget in `data/instructions_files_budget.json`. The pipeline skill body is within a few lines of its ceiling in `src/gzkit/skill_body_grandfather.json` (measured 2026-10-04), so its edit replaces and compresses text and never takes the body past that ceiling.
12. ALWAYS settle § Open Design Questions before the plan. A plan that picks an option the operator has not ruled does not pass plan audit. Each ruling is recorded verbatim in this brief's Change Log, and Allowed Paths, the Demo and any added REQ are amended to match before Stage 2.
13. ALWAYS disclose the named residual: the runtime cannot prove that the prior session has ended (the lock's `pid` is the claim command's own process, `obpi_lock.py:86`), and an occupant's identity is what its environment or its `--agent` flag asserts. The record makes a continuation visible and attributable; it does not make a wrongful one impossible.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Open Design Questions (operator rules before plan)

Each question names a choice the GHI leaves open. The REQs below are written to hold under any ruling; the recommendation is the drafter's and decides nothing.

1. **Does a continuation TRANSFER the lock or RECORD a second occupant?**
   - (A) Transfer: the prior occupancy ends against the continuity record and the continuing session becomes the holder.
   - (B) Record: the prior session's lock stays; the record names the second occupant.
   - Recommendation: A. Every reader keys on the holder being the current agent: the claim conflict (`obpi_lock.py:65`), the release ownership check (`obpi_lock.py:186`) and the per-agent helper that arms the pipeline gate (`pipeline_runtime.py:122-133`). Under B the continuing session is never the holder, its gate arm never arms, its own abort needs `--force`, and the TTL still runs from the first claim. A is expressible as an existing `obpi_lock_released` citing the record followed by an existing `obpi_lock_claimed`, so the validator sees it with no new event type; B needs one, in a registered security surface.
   - Cost of A: `gz obpi precomplete` counts ARB receipts "since the lock claim". A new claim time puts the first session's receipts out of scope, so the continuing session re-runs them.
   - **RULED 2026-10-04: A, transfer.** Asked "when a new session continues an OBPI another session holds, what happens to the lock?", the operator answered, verbatim: "A". The cost above was stated with the question and is accepted.
2. **Does the pipeline launch REFUSE, or RECORD the continuation itself?**
   - Recommendation: refuse and name the continuation command. `ADR-0.0.41` § Alternatives Considered 1 places the invariant at "the lock-release CLI verb itself, where the operator and agent share an explicit synchronous decision point"; a launch that takes over a block as a side effect hides the act.
   - Unchanged either way: a launch with no lock at all proceeds today and is caught only by `gz obpi precomplete` at Stage 5.
   - **RULED 2026-10-04: refuse.** Asked what the pipeline launch does when another session holds the lock, the operator answered, verbatim: "A". The launch exits non-zero, writes no marker and no `pipeline_launched` event, and names the continuation command. Option (C) of question 3 is thereby closed.
3. **What verb performs a continuation?** Any answer is a CLI contract change.
   - (A) An option on `gz obpi lock claim`. (B) A new subcommand under `gz obpi lock`. (C) No new surface: the launch does it (only with question 2 = record).
   - Recommendation: A. The claim is where the second session is refused today. An option carries the New Flag obligations of `.gzkit/rules/cli.md`; a subcommand carries all seven New Subcommand obligations and widens Allowed Paths (a new manpage, `docs/user/manpages/index.md`, `config/doc-coverage.json`, `docs/governance/governance_runbook.md`).
4. **What must a continuation show before it displaces an unexpired holder?** Two live sessions on one OBPI is what the lock prevents, and the runtime cannot tell that the first has ended. Sub-Invariant 4 already requires "the operator's explicit `--force`" to reap before expiry.
   - (A) The continuing agent's explicit act with a required, non-empty reason, recorded in `## Decisions Made`. (B) A plus the operator's direction, carried verbatim in the record.
   - Recommendation: A as the mechanism, with the rule stating that continuing while the holder may be live needs the operator's direction, on the same standing as an early reap.
5. **Does `.gzkit/rules/token-block-discipline.md` gain a new Sub-Invariant?** A rule change needs the operator's ruling.
   - (A) A new Sub-Invariant 8 for continuity. (B) An amendment inside Sub-Invariant 5. (C) No rule change.
   - Recommendation: A, with a minor version bump and wording the operator rules from a draft presented at plan time. C is not available: the rule describes how a block changes hands, and code that adds a way the rule does not state is doctrine drift.
6. **Three further routes change the occupant with no register entry (code reading, 2026-10-04). Are they in this brief?** The GHI's boundary names claim, release, launch and `--from` re-entry.
   - (i) Completion by a non-holder. `gz obpi precomplete` passes `lock_held` on any lock file for the OBPI (`obpi_precomplete.py:284-305`), and completion then deletes that lock and emits a release naming only the completing session (`obpi_complete.py:1430-1459`).
   - (ii) A claim over an EXPIRED lock held by another agent deletes it with no reaping record and no release event (`obpi_lock.py:65-79`), unlike `reap_expired_locks`.
   - (iii) Identity is asserted, not proven: `--agent NAME` lets a session claim or release as the holder, and every Codex session resolves to the constant `codex` (`lock_manager.py:112-113`), so two Codex sessions are one occupant.
   - Recommendation: (i) and (ii) in, each adding one BEHAVIOR REQ (numbered from REQ-0.35.0-19-14) before the plan; (ii) is Sub-Invariant 3 applied to the claim path. (iii) stays a named residual (Requirement 13), with the record carrying both sessions' `session_id` beside the agent names. Rekeying occupancy to the session id is not recommended here: `resolve_session_id` falls back to the process id (`lock_manager.py:117-123`), which would make every command of a harness without a session variable a change of occupant.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary: § Decision item 15, "A CHANGE OF OCCUPANT BETWEEN SESSIONS LEAVES A REGISTER ENTRY".
- [ ] Parent ADR § Intent — the amendment "AMENDED 2026-10-04". It says what a repair assignment is and why this ADR carries five of them.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] `.gzkit/rules/token-block-discipline.md` — Sub-Invariants 1-7, whole file. Binding: the abandon categories are closed, a register entry needs four fields, a `CHECKPOINT` never satisfies surrender, completion surrender is mechanical.
- [ ] `docs/design/adr/foundation/ADR-0.0.41-token-block-lock-discipline/ADR-0.0.41-token-block-lock-discipline.md` — whole file; the two quoted passages are in § Alternatives Considered 4 and § Comparator Uplift.
- [ ] `.gzkit/rules/security-sensitivity.md` and `data/security_surfaces.json` — why this brief is `sensitivity: security`.

**Context:**

- [ ] GHI #1176 — the finding and its closure contract (invariant, boundary, acceptance evidence, exit condition, known uncertainties).
- [ ] GHI #1167 and its closing comment — it left the failed-verification abort holding its lock, for this design.
- [ ] `docs/governance/context-phase-review-2026-10-04-evidence/README.md` — finding 4, proposal 5.
- [ ] The operator's rulings on § Open Design Questions, recorded in this brief's Change Log.

**Prerequisites (check existence, STOP if missing):**

- [ ] Every question in § Open Design Questions has a recorded operator ruling.
- [ ] Required path exists: `src/gzkit/commands/obpi_lock.py`
- [ ] Required path exists: `src/gzkit/exchange_records.py`
- [ ] Required path exists: `src/gzkit/governance/trust_audits/lock_exchange_coupling.py`
- [ ] Required path exists: `src/gzkit/commands/obpi_cmd.py`
- [ ] Required path is intentionally created in this OBPI: `tests/governance/test_lock_continuity.py`
- [ ] Required path is intentionally created in this OBPI: `features/obpi_lock_continuity.feature`
- [ ] Required path is intentionally created in this OBPI: `features/steps/obpi_lock_continuity_steps.py`

**Existing Code (understand current state):**

- [ ] `src/gzkit/lock_manager.py` — `resolve_agent`, `resolve_session_id`, `LockData`, the exclusive-creation write, `reap_expired_locks` and its reaping record (the one writer that already records a `previous_agent`)
- [ ] `src/gzkit/commands/obpi_lock.py` — the claim's conflict branch and its delete-then-write for a same-agent or expired lock; the release's ownership check, abandon path and fail-closed path
- [ ] `src/gzkit/exchange_records.py` — the two writers, `is_exchange_register_entry` (default-deny) and `find_exchange_for_release` (admits any non-abandoned `CREATE` record for the OBPI that postdates the claim)
- [ ] `src/gzkit/governance/trust_audits/lock_exchange_coupling.py` — the replay keys on `obpi_lock_released`; the minimum-information, timestamp, mode and git-index checks
- [ ] `src/gzkit/commands/obpi_cmd.py` — `obpi_pipeline_cmd`: the check order before the marker write, and the one function behind every `--from` entry
- [ ] `src/gzkit/commands/obpi_complete.py` and `src/gzkit/commands/obpi_precomplete.py` — the completion surrender and the `lock_held` and receipt-scoping checks
- [ ] `src/gzkit/pipeline_runtime.py` — the per-agent lock helper the pipeline gate reads
- [ ] `tests/test_obpi_lock_cmd.py`, `tests/governance/test_token_block_discipline.py`, `tests/governance/test_lock_exchange_coupling_validator.py` — fixture conventions (`_make_lock`, `_setup_project`, the cutover ledger)
- [ ] `features/obpi_lock.feature` and `features/steps/obpi_lock_steps.py` — two agents are simulated with `--agent`; the steps keep stdout and stderr apart
- [ ] `.gzkit/skills/gz-obpi-pipeline/SKILL.md` § Abort surrender and Stage 1 step 9; `.gzkit/skills/gz-obpi-lock/SKILL.md`

## Quality Gates

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

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated: the lock manpages, `docs/user/manpages/obpi-pipeline.md`, `docs/user/manpages/validate.md`, `docs/user/runbook.md`, the rule and both skills

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/obpi_lock_continuity.feature`
- [ ] Each scenario carries the `@REQ-0.35.0-19-NN` tag of the criterion it walks

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded
- [ ] Security walkthrough completed with its `arb-step-security-scan-*` receipt

## Verification

```bash
uv run -m unittest tests.governance.test_lock_continuity tests.governance.test_lock_exchange_coupling_validator tests.governance.test_token_block_discipline tests.governance.test_obpi_complete_lock_release tests.test_obpi_lock_cmd tests.commands.test_obpi_pipeline
uv run -m behave features/obpi_lock_continuity.feature features/obpi_lock.feature features/lock_exchange_coupling.feature
uv run gz validate --lock-exchange-coupling
uv run gz validate --documents --req-kind-discipline --cli-alignment
uv run gz validate --sensitivity
uv run gz validate --rule-version-markers
uv run gz cli audit
uv run gz skill audit
uv run mkdocs build --strict
uv run gz check
```

## Demo

The continuation command's spelling is operator-ruled (§ Open Design Questions 2 and 3), so this section cannot yet show it. Until the ruling, the runnable demonstration is the acceptance feature. In a throwaway workspace it seeds session A's lock, shows session B refused with the recovery named, performs the continuation, reads the record's four fields and two identities, and runs the coupling validator over the result. It exits non-zero if any of those outcomes fails.

```bash
uv run -m behave features/obpi_lock_continuity.feature
```

Authoring obligation before Stage 2 (Requirement 12): replace this block with the ruled command run in a `mktemp -d` project, asserting three outcomes: the refusal's exit code and recovery line, the continuity record on disk, and `gz validate --lock-exchange-coupling` exiting 0. Demo commands run in a disposable copy of the working tree (GHI #1093); the Demo still seeds its own project so no real lock is touched.

## Acceptance Criteria

<!-- REQ kinds per ADR-0.0.59; enforced by gz validate --req-kind-discipline. -->

- [ ] REQ-0.35.0-19-01 [BEHAVIOR]: Given an unexpired work lock on an OBPI held by agent A and a session that resolves to a different agent B, when B continues the OBPI by the continuation route, then an exchange record for that OBPI exists under `.gzkit/locks/exchange/` whose frontmatter carries `last_lock_event_timestamp` equal to A's claim time, `last_commit_sha`, `branch` and both identities (A as the prior occupant, B as the continuing occupant), whose body has a `## Decisions Made` section naming the continuation and its reason, and which carries no `abandoned: true` and no abandon category
- [ ] REQ-0.35.0-19-02 [BEHAVIOR]: Given a ledger and exchange directory that hold a continuation, when `gz validate --lock-exchange-coupling` runs, then it exits 0 for a complete continuity record, and it exits 3 naming the OBPI when the record is absent from disk, lacks any one of the four Sub-Invariant 2 fields, or lacks either identity
- [ ] REQ-0.35.0-19-03 [BEHAVIOR]: Given an unexpired lock held by agent A, when agent B runs `gz obpi lock claim` or `gz obpi lock release` for that OBPI without the continuation route, then the command exits 1 with the `--json` status it has today (`conflict`; `ownership_error`), the lock file is unchanged, no exchange record and no ledger event is written, and both the human output and the `--json` payload name the holder and the runnable continuation command
- [ ] REQ-0.35.0-19-04 [BEHAVIOR]: Given an unexpired lock held by agent A and no continuity record for agent B, when B runs `gz obpi pipeline` for that OBPI as a full launch or with `--from=verify`, `--from=ceremony` or `--from=sync`, then the launch exits non-zero having written no pipeline marker and no `pipeline_launched` event, and names the continuation command (question 2, ruled). Once B has continued by the continuation route, the same launch proceeds
- [ ] REQ-0.35.0-19-05 [BEHAVIOR]: Given a run by session A that stopped at verify with blockers recorded and its lock still held, when session B continues by the continuation route before A's TTL has elapsed and runs `gz obpi pipeline` with `--from=verify`, then the re-entry proceeds, the REQ-0.35.0-19-01 record exists, and no abandon record was written for that OBPI
- [ ] REQ-0.35.0-19-06 [BEHAVIOR]: Given B has continued A's OBPI, when B later runs `gz obpi lock release` with neither `--abandon` nor an exchange record written after the continuation, then the release exits 3 `FAIL-CLOSED` as it does today: the continuity record is not accepted as B's surrender. A `CHECKPOINT` document for the same OBPI is still refused by `find_exchange_for_release`, still fails `gz validate --lock-exchange-coupling` when a release cites it, and is not accepted in place of the continuity record
- [ ] REQ-0.35.0-19-07 [BEHAVIOR]: Given the closed abandon enum, when `gz obpi lock release` is run with an `--abandon` category outside `network_loss`, `external_blocker`, `wrong_obpi_claimed`, `tool_failure` and `reaping` (for example one naming a failed verification or a continuation), then it exits 1 with status `invalid_abandon` and writes nothing
- [ ] REQ-0.35.0-19-08 [BEHAVIOR]: Given a lock held by agent A, when A claims it again, then the lock is refreshed and no exchange record is written; and given a lock past its TTL, when `reap_expired_locks` runs, then a `category: reaping` record naming `previous_agent` is written before the lock is deleted and any agent may then claim with no continuity record. Both behave as they do before this OBPI
- [ ] REQ-0.35.0-19-09 [BEHAVIOR]: Given the lock's holder completes the OBPI, when `gz obpi complete` succeeds, then it writes the completion exchange record and emits `obpi_lock_released` citing it, as it does before this OBPI; and given B continued A's OBPI and then completes it, then the ledger replay over the continuation and the completion passes `gz validate --lock-exchange-coupling`
- [ ] REQ-0.35.0-19-10 [BEHAVIOR]: Given the orchestrator's session holds the lock, when a process that resolves to the same agent identity (a dispatched subagent carrying the same session id) claims the lock or launches the pipeline, then it is not refused and no continuity record is written, and the per-agent lock helper in `src/gzkit/pipeline_runtime.py` still returns that OBPI for it
- [ ] REQ-0.35.0-19-11 [SUPPORT]: The lock manpages, `docs/user/manpages/obpi-pipeline.md`, `docs/user/manpages/validate.md` and `docs/user/runbook.md` describe the refusal and its recovery, the continuation route, the continuity record's fields and location, and what the coupling validator checks on it, in the words the code prints. Witnessed by `artifact_edited` citing `docs/user/manpages/obpi-lock-claim.md` + `gz validate --cli-alignment`.
- [ ] REQ-0.35.0-19-12 [SUPPORT]: The canonical rule states, in the form and wording the operator rules (question 5), that a change of occupant between sessions leaves a register entry naming both occupants or is refused, that no abandon category is added for it, and that a continuity record discharges no later surrender; its version is bumped, the superseded version line is lifted to `docs/governance/rule-version-history.md`, and the scorecard carries the clause. Witnessed by `artifact_edited` citing `.gzkit/rules/token-block-discipline.md` + `gz validate --rule-version-markers`.
- [ ] REQ-0.35.0-19-13 [SUPPORT]: The pipeline skill's Stage 1 lock step, § Abort surrender and § Error Recovery, and the lock skill's Lock Rules and pipeline integration, tell a session that meets another session's lock to continue by the continuation route, and tell an aborting session that a lock left held is continued by the next session, with the pipeline skill's body kept within its ceiling. Witnessed by `artifact_edited` citing `.gzkit/skills/gz-obpi-pipeline/SKILL.md` + `gz validate --skill-alignment`.

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

### Change Log

<!-- Keep substantive implementation, test, documentation, and evidence
     corrections within this OBPI. Reuse existing finding identities and cite
     the affected REQ or contract clause, change, and proof/closure references.
     Group related repairs; do not log every edit or duplicate transcripts.
     This is an index to evidence, not a second acceptance ledger. Record approved
     amendments in their normative sections and reference the ruling here.
     Create a GHI only when independent work or disposition is needed, or the
     operator explicitly requests an issue; link it back to the owning work.
     Keep this subsection under Evidence so history is not treated as contract. -->

- 2026-10-04 — Open Design Question 1 ruled before the plan (Requirement 12). Operator, verbatim: "A". A continuation transfers the lock: the prior occupancy ends against the continuity record and the continuing session becomes the holder. Allowed Paths already cover this ruling and are unchanged.
- 2026-10-04 — Open Design Question 2 ruled before the plan (Requirement 12). Operator, verbatim: "A". The pipeline launch refuses when another session holds the lock and names the continuation command; it never records a continuation itself. REQ-0.35.0-19-04 is amended to the refusal. Allowed Paths are unchanged. Questions 3 to 6 are open.

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

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Link independently routed GitHub defects, one bullet per issue so status
     surfaces preserve traceability. Within-OBPI corrections belong in the
     Change Log above; they do not need a GHI. An issue link does not discharge
     an unmet acceptance obligation. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
