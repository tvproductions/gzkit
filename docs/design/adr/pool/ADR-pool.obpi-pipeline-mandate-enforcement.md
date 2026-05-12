---
id: ADR-pool.obpi-pipeline-mandate-enforcement
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.obpi-pipeline-mandate-enforcement: OBPI Pipeline Mandate Mechanical Enforcement

## Status

Pool

## Intent

The `gz-obpi-pipeline` SKILL declares `uv run gz obpi pipeline <OBPI-ID>` as the
**mandatory** post-plan runtime invocation — "agents MUST run `gz obpi pipeline`"
— but the mandate is *advisory in practice*. There is no mechanical link between
the SKILL's mandate text and the downstream gates that depend on a runtime-written
pipeline marker (nonce + matching `pipeline_launched` ledger event). An agent who
reads the SKILL body and executes Stages 2/3/4 freeform (claiming the lock via
`gz obpi lock claim`, writing markers by hand, running ARB receipts inline)
produces a malformed Stage-1 state: a hand-rolled marker without nonce, no
`pipeline_launched` ledger event, no canonical `current_stage`.

When such an agent reaches Stage 5 and invokes `gz obpi complete --attestor-present`
(the GHI #292 / GHI #434 agent-relayed Gate-5 path), the CLI's hardened gate
(GHI #412) correctly refuses the malformed marker. The agent falls back to the
SKILL-documented PTY relay path, which Claude Code's auto-classifier denies as
"Gate-5 bypass." The operator is bounced back to type `ATTEST` in a TTY despite
having attested in conversation at Stage 4.

This is the **same recurring class** the operator named in GHIs #290/#292/#434,
each of which fixed a specific node in the chain but did not close the
class-of-failure: **the skill-mandate-to-mechanical-enforcement gap remains open
at the lock-claim and runtime-launch entry points**, so agents who execute
freeform continue to reach the friction class through a different door.

Architectural absence: gzkit has hardened the *downstream* attestation gate
(GHI #412 marker validation, GHI #434 foundation-kind agent-relayed re-allowance)
but has not closed the *upstream* enforcement that ensures every foundation+heavy
OBPI's Stage 1 is mediated by the runtime. The SKILL body asks the agent to
"claim OBPI lock" and "create pipeline markers" as if these were independent
operations the agent owns; the runtime treats the lock+marker pairing as a
trust-rooted invariant; the mismatch is the class-of-failure.

Surfaced in: GHI #458 (skill-mandate is advisory; freeform-stage execution
re-triggers Stage-5 TTY/PTY friction). Lived impact captured in that GHI's
body — single session producing ~3 extra rounds of evidence presentation, 2
PTY-denial bounces, multi-paragraph apologetic-surface-back messages, and an
operator outburst about waste.

## Decision

(Deferred — pool entry. Operator-discretion promotion to foundation/feature
when the design conversation is ready to land.)

When promoted, this ADR will choose among the four mechanical-enforcement
strategies in § Alternatives Considered (or a hybrid), specify the runtime/CLI/
SKILL changes that implement the chosen strategy, and decompose into OBPIs
under the standard kind=foundation lane=heavy gate covenant.

## Alternatives Considered

Each of the four was proposed in GHI #458's body as a candidate mechanical fix.
None is intrinsically dominant; promotion will pick (possibly hybrid) based on
operator design judgment.

**A. Pre-commit / pre-tool hook that blocks `gz obpi complete` when the marker
is absent OR was not written by the runtime.** Extends the existing
`--attestor-present` rejection earlier — surface it at lock-claim time, not
mid-Stage-5. *Smallest diff; CLI-side only; reuses existing gate.* Trade-off:
the friction still surfaces *at* the gate-time, just earlier; the agent has
already committed to the freeform path by that point.

**B. Hard-fail `gz obpi lock claim` for foundation-kind + heavy-lane OBPIs
unless the caller is the pipeline runtime.** Carry a runtime-provenance signal
(env var `GZKIT_PIPELINE_RUNTIME=1` set by the runtime when subprocess'ing the
lock-claim, OR refactor so the runtime calls `lock_manager.write_lock` directly
and the public `gz obpi lock claim` CLI is gated). *Most upstream gate; forces
agents into the runtime path for the scopes where the friction class hurts
most.* Trade-off: behavior change to a foundation surface (the lock manager);
intersects with ADR-0.0.41 token-block discipline (binding sub-invariants 1–5);
breaks existing test fixtures that claim locks directly without the runtime;
needs the runtime to itself own the Stage 1 lock-claim step (a refactor of the
current SKILL ↔ runtime split where the agent owns lock-claim and the runtime
owns marker).

**C. SKILL execution-trace receipt.** When an agent invokes the
`gz-obpi-pipeline` SKILL via Claude Code's `Skill` tool, write a receipt to
`.claude/plans/.skill-invocation-{OBPI-ID}.json` that `gz obpi pipeline` later
validates (matching nonce relationship). *Most auditable; preserves the SKILL
↔ runtime split; distinguishes "agent invoked the SKILL" from "agent
freelanced."* Trade-off: requires Claude Code harness cooperation gzkit
does not fully control; SKILL invocations across vendor harnesses (Codex,
Copilot, OpenCode) may not emit equivalent receipts; loops back to the
hooks-as-vendor-coupled named exception in ADR-0.0.32 § Named exceptions
Exception 1.

**D. Stage 5 self-check in `gz obpi pipeline` runtime.** Entering `--from=verify`,
`--from=ceremony`, or `--from=sync` finds no prior pipeline-launched marker;
refuse with a clear remediation pointing at "no Stage 1 was ever run by the
runtime; restart with `gz obpi pipeline <OBPI-ID>`." *Smallest-surface-area
defensive check; runtime-side only.* Trade-off: catches the failure
mid-traversal rather than at lock-claim entry; the agent has already done the
freeform Stage 2/3/4 work by the time `--from=ceremony` is invoked, so the
remediation may force re-runs the operator considers waste.

**Hybrid B+D** was the operator-economy recommendation in GHI #458's body:
defense-in-depth at the two natural entry points (lock-claim upstream and
runtime `--from=*` resumption mid-stream). The CLI-side completion gate
(GHI #412/#434) is the third backstop. Three independent gates means an
agent who fails one still hits the next; today only the third (completion
gate) is mechanical.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

### Related GHIs (routed-here)

- **GHI #458** — primary surfacing GHI; closed `superseded` against this pool
  ADR. Documents the lived impact and proposes the four alternatives captured
  in § Alternatives Considered.

### Related ADRs

- **ADR-0.0.41** (token-block-lock-discipline) — defines the lock-release ↔
  handoff coupling invariant. This pool ADR's Alternative B intersects
  ADR-0.0.41's lock-claim authorization model: gating lock-claim by runtime
  provenance is a complementary invariant ("who may issue a token") to
  ADR-0.0.41's existing ("how must a token be surrendered"). Promotion of this
  pool ADR will need to confirm consistency with ADR-0.0.41's binding
  sub-invariants 1–5.
- **GHI #290 / #292 / #434** — the agent-relayed Gate-5 chain. This pool ADR
  closes the *upstream* enforcement that those GHIs did not address; together
  they would form a complete trust chain (skill-mandate → lock-claim → runtime
  marker → CLI completion gate).
- **ADR-0.0.32 § Named exceptions Exception 1** (hooks vendor coupling) —
  Alternative C above intersects this exception; harness-side SKILL-invocation
  receipts cannot be uniformly cross-vendor under the current vendor-harness
  capability matrix.

### Out of scope for this pool ADR

The Claude Code auto-classifier denying the SKILL-documented PTY fallback as
"Gate-5 bypass" is a separate harness-side issue (filed in GHI #458's "Out of
scope" section). Even with this pool ADR's mechanical fixes landed, the PTY
fallback path's value drops to zero whenever it's needed because the harness
blocks it. Worth filing at the Claude Code repo or via the harness team — not
a gzkit-tracker concern.
