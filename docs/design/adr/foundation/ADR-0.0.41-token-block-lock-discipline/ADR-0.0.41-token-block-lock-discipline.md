---
id: ADR-0.0.41-token-block-lock-discipline
status: Draft
kind: foundation
semver: 0.0.41
lane: heavy
parent:
date: 2026-05-07
---

# ADR-0.0.41-token-block-lock-discipline: Token-Block Lock Discipline — Lock-Release Coupled to Handoff Register Entry

## Persona

`main-session` — craftsperson, governance-aware, whole-file-reasoning, direct.
This ADR works on the gzkit governance spine; the agent who advances it must
treat the lock-and-handoff primitive as identity-shaping (every OBPI and
multi-session handover composes it) and refuse the temptation to ship a half
mechanism whose write-side is judgment-driven while the read-side is
mechanical. Anti-vibing mantra (AGENTS.md) applies sharply here:
"smallest-vibing-surface" framing, never maintenance-burden framing.

## Why foundation tier?

Without this ADR, multi-agent coordination has no lock discipline — two agents can claim the same OBPI simultaneously, lock release is decoupled from handoff/register entries, and the abandon path can leak claims into orphan locks.

This ADR authors a port: the token-block lock-discipline contract every claim/release/abandon surface (and the validator that audits them) binds to.

## Intent

Reframe the gzkit OBPI lock as the kit's equivalent of railway absolute-block
working — a **token-block primitive** in which exclusive authority over a
section of work transfers via a physical instrument (the lock), and every
issue and surrender of that instrument is paired with a **register entry**
(the handoff document). The token enforces mutual exclusion; the register
entry makes the transfer auditable. Without the coupling, the lock is a
mutex with no audit trail — the wrong primitive for governance work, and
the immediate cause of the asymmetry GHI #410 surfaced (5 token surrenders
in 24h, 0 register entries).

The doctrine is named directly after its railway antecedent because the
railway invariant is the one we want exactly: a token cannot be returned
without a register entry, full stop, regardless of how short the
traversal felt or whether the driver "remembers" what happened in the
section. Memory is not a substitute for explicit verification (cf.
`gz-session-handoff` SKILL.md § Common Rationalizations).

The full historical credit, mapping, and references to the railway
corpus that produced this doctrine are documented in
[`docs/governance/token-block-doctrine.md`](../../../../governance/token-block-doctrine.md).
Agents and operators new to the canon should read that document first;
this ADR records the *decision* to import the discipline, not the
intellectual debt itself.

## Decision

Couple lock-release to a handoff register entry. The binding invariant:

> A token cannot be surrendered without a register entry.

Translated to gzkit:

1. **`obpi_lock_release_cmd` (and any code path that emits
   `obpi_lock_released`) MUST refuse to release the lock unless** a
   handoff document exists whose frontmatter timestamp is later than the
   matching `obpi_lock_claimed` event for the same `(obpi_id, agent)`
   pair, OR the caller provides `--abandon <reason>` which records a
   degenerate handoff with `abandoned: true` frontmatter.

2. **`obpi_lock_released_event` payload includes a `handoff_path`
   reference** (the on-disk path of the register entry that authorized
   the surrender). Replay over the ledger then trivially verifies every
   token surrender is paired with a register entry.

3. **Handoff storage is consolidated to a single canonical location.**
   Resolve the existing drift between `.gzkit/handoffs/` (read by
   `scripts/session_orientation.py:263`) and `{ADR-package}/handoffs/`
   (written by `gz-session-handoff` SKILL.md:83). Canonical: `.gzkit/handoffs/`
   (top-level, ADR-agnostic, mirrors ledger placement). ADR-package mirrors
   may exist as derived views but are not source-of-truth (Layer-3 per
   `docs/governance/state-doctrine.md`).

4. **`gz-session-handoff` skill CREATE trigger is mechanical, not
   judgment.** The trigger is `obpi_lock_release_cmd` invocation —
   the skill is the agent's tool for satisfying the release precondition,
   not "when an agent pauses work."

5. **A new validator scope `gz validate --lock-handoff-coupling`** replays
   the ledger and fail-closes on any `obpi_lock_released` event missing a
   `handoff_path` payload field, or referencing a path that does not
   exist or whose frontmatter timestamp predates the matching claim.

## Comparator Uplift (2026-05-07)

Spec Kit/GSD-style long workflows and compaction-prone sessions make lock
discipline more important. This ADR should treat token-block locks as the
front-door/compounding safety net: before a compacted or resumed session
continues, the lock release must prove which intent, artifact set, and
handoff-register entry survived. A failed compact cannot silently erase the
governance witness.

## Consequences

### Positive

- Closes the asymmetry between mechanical read-side (orientation hook) and
  judgment-driven write-side (skill trigger) that produced 5/5/0 in 24h.
- Establishes the **decoupled-lifecycle anti-pattern** as a named failure
  family, applicable to any future primitive that emits ledger events for
  state transitions without a coupled artifact write.
- Makes lock-release a CLI verb that itself enforces the invariant — no
  separate `Stop` hook, no parallel "must remember to handoff" rule.
- Aligns with state-doctrine.md Layer-2: the ledger now carries the full
  audit-coupling, not just the transition events.
- Provides foundation for downstream OBPI state-machine work: when that
  arrives, lock-edges are already coupled to register entries, so the
  state machine composes a primitive that already enforces the invariant.

### Negative

- Backwards incompatible at the release-edge once OBPI-03 lands (release
  fail-closed). Mitigated by OBPI-02 staging (warning-only precondition)
  giving operators a window to adopt the discipline before flip.
- Adds a precondition step to every OBPI completion. The cost is bounded
  (the skill exists; the form is fixed) but it is real friction at the
  closeout edge — by design (see anti-vibing mantra: 5:1 governance ratio
  is the product, not overhead).
- Storage consolidation deletes one of two existing handoff stores
  (`{ADR-package}/handoffs/` becomes a derived mirror, not a write target).
  Existing register entries under that path migrate during OBPI-03;
  history is preserved.
- The `--abandon` flag is a load-bearing override; misuse (claiming
  abandonment to skip the register entry) is a doctrine-drift attack
  surface. Mitigated by recording `abandoned: true` + reason text in the
  degenerate handoff, which the validator then audits as part of normal
  ledger-replay coverage.

## Boundary Invariants

Cross-OBPI invariants binding multiple OBPIs under this ADR. Each invariant
is the contract that a STRUCTURAL-FENCE REQ points at; it can only be
audited at ADR closeout, not within a single OBPI.

1. **Audit-coupling invariant.** Every `obpi_lock_released` event in
   `.gzkit/ledger.jsonl` emitted on or after the OBPI-02 closeout cutover
   carries a valid `handoff_path` payload; the referenced handoff exists
   on disk, postdates its matching `obpi_lock_claimed` event, and
   satisfies the Sub-Invariant 2 minimum-information rule
   (`.gzkit/rules/token-block-discipline.md`). This invariant binds
   OBPI-02 (additive `handoff_path` field), OBPI-03 (mandatory at every
   emission site; warning flipped to fail-closed; reaping emits
   `abandoned_by_reaper` handoff before delete), and OBPI-04 (mechanical
   enforcement via `gz validate --lock-handoff-coupling`, wired into the
   default `gz check` pipeline) into a single audit-coupling guarantee.
   Enforced by: `uv run gz validate --lock-handoff-coupling` (OBPI-04).

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 1
- Lineage: 2
- Dimension Total: 9
- Baseline Range: 5+
- Baseline Selected: 5
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 5

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.41-01: Token-block doctrine canon — author `.gzkit/rules/token-block-discipline.md` and `docs/governance/token-block-doctrine.md` (railway-historical reference). Specify the binding sub-invariants the structural enforcement alone does not close: (a) auditable `--abandon` reason categories (rejecting free-text-only reasons; categories include `network_loss`, `external_blocker`, `wrong_obpi_claimed`, `tool_failure`, with extension protocol); (b) minimum-information requirements for the register entry (last lock-event timestamp, last commit SHA, named decisions, branch state) so structurally-valid-but-semantically-empty handoffs are also rejected; (c) lock-takeover / reaping register-entry rule (the railway-analogue lost-token procedure: a reaping by agent-B emits an `abandoned_by_reaper` register entry recording agent-A's last-known state); (d) **time-bound discipline (TTL canon and reaping cadence): default TTL value with rationale, escalation policy (warn-then-reap windows), who-may-reap (any agent at next session-start; explicit operator override), and the attestation requirement that the reaping agent MUST produce the `abandoned_by_reaper` register entry as a precondition of the reap — mirroring the rule for ordinary release, so reaping is not a doctrine-bypass**; (e) cross-link from AGENTS.md § Behavior Rules and `docs/governance/state-doctrine.md`. Establishes vocabulary (token, register entry, traversal, abandonment, reaping) before any code change.
- [ ] OBPI-0.0.41-02: Claim/release safety primitives. (a) **Interlock the claim sequence: rewrite `lock_manager.write_lock` to use exclusive-creation (`open(path, "x")`) and update `obpi_lock_claim_cmd` to treat `FileExistsError` as a claim conflict, closing the current check-then-write race in `obpi_lock.py:40-64` that violates the load-bearing exclusion property of the token primitive. The railway analogue is the galvanic interlock between paired Tyer's tablet instruments (1878) — the very mechanism the patent existed to provide. Token-block without atomic claim is exclusive in name only.** (b) Add `--abandon <category>:<reason>` flag to `obpi_lock_release_cmd` (category from the OBPI-01 enum; reason free-text within category) and the degenerate-handoff format. Register entry is required at the API level but not yet enforced — emit a warning when release proceeds without a handoff. Operators see the invariant before it bites.
- [ ] OBPI-0.0.41-03: Flip release precondition to fail-closed. `obpi_lock_release_cmd` rejects release without a register entry (or `--abandon`). Update `lock_manager.py:reap_expired_locks` to emit the OBPI-01-specified `abandoned_by_reaper` degenerate handoff per reaped lock. Storage consolidation: `.gzkit/handoffs/` becomes the canonical write target; ADR-package mirror is regenerated as Layer-3 derived view. Migrate existing register entries.
- [ ] OBPI-0.0.41-04: Implement `gz validate --lock-handoff-coupling` validator. Replay `.gzkit/ledger.jsonl`; fail-close on any `obpi_lock_released` event lacking a valid `handoff_path` payload, referencing a path whose frontmatter timestamp predates the matching claim, OR whose register entry violates the OBPI-01 minimum-information rule. **Binding wiring:** the validator MUST be added to the default `gz check` chain (not on-demand-only) — an enforcement floor agents can skip is no enforcement floor.
- [ ] OBPI-0.0.41-05: Update `gz-session-handoff` SKILL.md (CREATE trigger = `obpi_lock_release_cmd` invocation, not "when an agent pauses work"), `scripts/session_orientation.py` (single canonical store), `docs/user/runbook.md`, `docs/governance/governance_runbook.md`, and the per-turn agent contract surfaces. Bump skill version, run `gz agent sync control-surfaces`.

## Q&A Transcript

The doctrine emerged from a session-orientation observation:

- Operator: "I don't think the handoff routine is working as an effective regular tool, what triggers its use?"
- Investigation showed the SessionStart and PreCompact hooks both run `scripts/session_orientation.py`, which reads the newest handoff and injects freshness/path/first-action into context — but no hook (`Stop`, `SessionEnd`, or otherwise) triggers handoff CREATE. The skill's CREATE workflow is operator-judgment-driven ("when an agent pauses work").
- Operator: "Lacking a state machine, other than the lock mechanism, we only have the lock mechanism — like a token or block system like on early train systems."
- Mapping established: the lock is the token, lock-claim is token issue, lock-release is token surrender. The asymmetry — token surrender without an accompanying register entry — is the railway equivalent of a driver dropping the token at the signal box and walking off without logging the section's condition. The 24h ledger (5 claims, 5 releases, 0 handoffs) confirmed empirically.
- Doctrine name resolved as **token-block discipline** (the umbrella railway principle for "token issued at one signal box, surrendered at the next, register entry on both edges"). Adjacent terms surveyed: absolute block working (broader principle), train staff / Tyer's electric tablet / electric train staff (specific instruments), train register (the bound book of entries). Token-block names the doctrine; register-entry names the missing coupling.
- Operator framed this as **incomplete design, not new design**: the lock primitive was specified with claim/release symmetry and ledger-event emission but without the audit-coupling that makes the transfer meaningful. Foundation territory because the lock primitive is identity-shaping (every OBPI composes it). Pool stage skipped per Architectural Boundary 6.

## Evidence

- [ ] Tests: `tests/governance/test_token_block_discipline.py` (asserts release fail-closed without register entry; exercises `--abandon` happy path; ledger-replay validator coverage)
- [ ] Tests: `tests/governance/test_lock_handoff_coupling_validator.py` (per OBPI-04)
- [ ] Docs: `.gzkit/rules/token-block-discipline.md` (per OBPI-01) — binding-bullets rule
- [x] Docs: [`docs/governance/token-block-doctrine.md`](../../../../governance/token-block-doctrine.md) — railway-historical doctrine and citations (authored alongside this ADR)
- [ ] Docs: `docs/governance/state-doctrine.md` (extension citing this ADR as Layer-2 audit-coupling rule)
- [ ] Docs: `docs/user/runbook.md`, `docs/governance/governance_runbook.md` (OBPI-completion flow updated per OBPI-05)
- [x] GHI: [#410](https://github.com/tvproductions/gzkit/issues/410) — superseded by this ADR
- [ ] Related GHI: #326 (SessionStart auto-load — read-side counterpart that exposed this asymmetry)
- [ ] Related ADR: ADR-0.0.9 (state doctrine — the Layer-2 source-of-truth rule this ADR extends)

## Alternatives Considered

1. **SessionEnd-hook-fires-handoff-CREATE.** Attach a `Stop` hook to `.claude/settings.json` that calls the skill's CREATE workflow at session end, gated on "active OBPI lock with no handoff written since the last `obpi_lock_claimed` event." Rejected: this is read-side judgment (the hook decides whether a handoff is needed) masquerading as a mechanism. The same drift class as the existing skill trigger ("when an agent pauses work") at a different layer. The right place to enforce the invariant is the lock-release CLI verb itself, where the operator and agent share an explicit synchronous decision point.
2. **Time-cadence-based handoff requirement.** Require a handoff every N hours, or whenever the orientation hook classifies the most-recent handoff as Stale/Very-Stale. Rejected: calibrates to wall-clock, not to traversal. The railway invariant is per-traversal — one register entry per token surrender — not per-hour. Wall-clock cadence produces a metronome of handoffs whose contents are not bound to specific token transfers; the audit trail loses the structural property "each entry corresponds to exactly one section traversal."
3. **State-machine-first redesign.** Define the OBPI state machine canonically (states, transitions, invariant monitor) and re-derive lock and handoff semantics as projections. Rejected as the *immediate* path; correct as eventual direction. The lock+handoff coupling is the smallest mechanical primitive that closes the immediate failure (5/5/0 in 24h). A full state machine is downstream foundation work that composes this primitive — when it arrives, lock-edges already enforce the register-entry invariant, so the state machine inherits the discipline rather than re-inventing it. Premature state-machine work without locking the lock-edge primitive first risks repeating the asymmetry at a higher layer.
4. **Coupling enforced only at OBPI completion (not per lock-release).** Require a handoff at `gz obpi complete` but allow intermediate lock claim/release cycles to proceed without coupling. Rejected: too late. The failure surface is per-traversal, not per-OBPI — a single OBPI may span multiple lock claim/release cycles across sessions, and intermediate handovers without register entries lose intent at exactly the boundaries this ADR exists to protect. The railway analogue holds: a register entry is required at every signal box, not only at the train's terminal station.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.41 | Pending | | | |
