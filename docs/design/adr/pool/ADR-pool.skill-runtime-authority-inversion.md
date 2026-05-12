---
id: ADR-pool.skill-runtime-authority-inversion
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.skill-runtime-authority-inversion: Skill Runtime Authority Inversion

## Status

Pool

## Intent

`.gzkit/skills/<slug>/SKILL.md` bodies that document a runtime's procedure
in granular detail train the orchestrating agent to execute the procedure
rather than delegate to the runtime. The canonical example is
`gz-obpi-pipeline/SKILL.md` (~7,000 words of stage tables, transition
rules, error-recovery matrices, hook contracts) whose single load-bearing
sentence — *"The canonical runtime launch surface is `uv run gz obpi
pipeline`. … This skill remains the wrapper/operator ritual around that
runtime rather than a second stage engine."* — sits buried under
thousands of words of procedural prose describing what the runtime does.
**Token weight beats explicit directive.** The agent reads the procedure
description and executes the procedure, bypassing the runtime that owns
sequencing.

The pattern is catalog-wide. Preliminary survey of skills that wrap a
runtime procedure:

- `gz-obpi-pipeline` — wraps `gz obpi pipeline` (surfacing skill)
- `gz-plan-audit` — wraps `gz plan audit`
- `gz-adr-create` — wraps `gz plan create` / `gz adr promote`
- `gz-adr-evaluate` — wraps `gz adr evaluate`
- `gz-check` — wraps `gz check`
- `gz-obpi-reconcile` — wraps `gz obpi reconcile`
- `gz-validate` — wraps `gz validate`
- `gz-arb` — wraps `gz arb step / ruff / typecheck`

(Catalog total ~70+ skills; the audit scope in Alternative C produces the
exhaustive list.)

Architectural absence: gzkit treats SKILL.md bodies as agent-facing
context regardless of whether their content is *operator documentation*
(what the runtime does, why) or *agent instructions* (what to do now).
The two categories load into agent context with the same weight. When
the body is procedural prose describing runtime internals, the agent
learns to execute those internals rather than invoke the runtime that
owns them.

This is structurally the same failure
`ADR-pool.obpi-pipeline-mandate-enforcement` names at the
`gz-obpi-pipeline`-specific layer (skill-mandate-to-mechanical-enforcement
gap at lock-claim and runtime-launch entry points), generalized one layer
up. That sibling ADR closes the upstream gate for a single skill; this
ADR addresses the catalog-wide surface that produces the gate-avoidance
behavior in the first place.

**Shortening is rejected as the fix.** Operator framing (verbatim, GHI
#460): *"new ghi, i don't trust shortening though."* Replacing 7,000
words of procedural prose with 20 words of *"run the runtime, do the
right thing"* trades procedure-execution failure for under-specified
vibing where the agent fills the gap from training corpus. Length is
not the load-bearing variable; **structure is**. The agent's behavior
should NOT depend on the skill author's discipline (write a short
skill, write the perfect skill). It should depend on a mechanical
surface that makes the runtime authoritative regardless of skill body
content.

Surfaced in: GHI #460 (catalog-wide structural defect; rejects the
shortening band-aid). Adjacent surfacing: GHI #459 (same failure class
at the `gz-obpi-pipeline` Stage 2 dispatch + persona adoption layer —
doctrine declaring two-stage spec/quality review dispatch with no
mechanical fail-close).

## Decision

(Deferred — pool entry. Operator-discretion promotion to foundation /
feature when the design conversation is ready to land.)

When promoted, this ADR will choose among the three structural surfaces
in § Alternatives Considered (or a hybrid), specify the runtime / CLI /
SKILL / hook changes that implement the chosen strategy, and decompose
into OBPIs under the standard kind=foundation lane=heavy gate covenant.
Skills that legitimately need procedural body content — dialogue-shaped
skills like `gz-design`, `ghi-author`, `gz-justify` where the agent's
role is composition / interview rather than procedure-execution — are
out of scope and remain author-written.

## Alternatives Considered

Each surface was proposed in GHI #460's body. None is intrinsically
dominant; promotion will pick (possibly hybrid) based on operator design
judgment and the cross-vendor harness capability matrix.

**A. Skill becomes a runtime-stdout proxy.** When the agent invokes
`/gz-obpi-pipeline OBPI-X.Y.Z-NN`, a PreToolUse hook runs
`uv run gz obpi pipeline <OBPI-ID> --next-step` (or equivalent) and
emits its stdout as the skill body's effective content. The
author-written SKILL.md collapses to a ~5-line stub: *"Invoke the
runtime. The runtime's output is your next-step contract."* The
procedural prose (Iron Law, stage tables, transition rules) moves to
`docs/governance/<runtime>.md` where it lives as operator-facing
documentation, NOT as agent-execution context. The runtime's
`--next-step` mode emits exactly the prompt the agent needs at this
moment — Stage-1 evidence-gathering instructions, Stage-4
evidence-presentation template, Stage-5 attestation-text request — and
nothing else. *Largest structural change; most aggressive at making
the runtime authoritative; eliminates the failure mode where the
agent reads stage tables out of context and starts walking them
before the runtime is launched.* Trade-off: requires
PreToolUse-hook cooperation from each vendor harness (Claude Code,
Codex, Copilot, OpenCode); loops back to the hooks-as-vendor-coupled
named exception in ADR-0.0.32 § Named exceptions Exception 1; needs
the runtime to support a `--next-step` mode that emits
context-appropriate prompts; substantial doc migration burden
(per-runtime governance pages).

**B. PreToolUse hook on procedural skills that fail-closes when the
runtime isn't authoritative.** For every skill whose body documents a
runtime procedure, a hook checks: has the matching `uv run gz
<runtime>` invocation produced a ledger event within the last N
seconds? If not, the hook routes the agent to invoke the runtime first;
the skill body is not loaded into context until the runtime has emitted
its bootstrap event. This is the same gate proposed in GHI #459's fix
item 2 (`pre-stage2-gate.py` on source edits), generalized: every
skill that wraps a runtime gets a corresponding pre-skill-render gate.
The skill's prose becomes inert if the runtime isn't already engaged.
*Smaller diff than Surface A; preserves author-written skill bodies;
makes them mechanically inert when the runtime is absent rather than
mechanically irrelevant always.* Trade-off: same vendor-harness coupling
as Surface A (PreToolUse hooks are not uniformly cross-vendor); the
"matching ledger event within N seconds" predicate is per-runtime and
needs a registry mapping each procedural skill to its authoritative
runtime + event name; agents may invoke the runtime, see the gate
clear, and then drift away from runtime sequencing mid-skill (gate is
upstream-only, not continuous).

**C. Skill catalog audit identifying procedural skills.**
Author a `gz validate --skill-procedural-drift` scope that fingerprints
each SKILL.md: word count, stage-table count, "MUST" / "DO NOT" /
"NEVER" density, sub-step enumeration count, runtime-procedure-mirroring
density. Skills exceeding thresholds are flagged as candidates for the
Surface-A inversion or the Surface-B gate-wiring. Output is a
remediation list, not an automatic rewrite — the structural fix lands
one skill at a time under attested ADR work, not as a mechanical
mass-trim. *Smallest immediate surface change; pure read-only audit;
produces the inventory needed to scope Surface A or B; deterministic
and cross-vendor (no hook coupling).* Trade-off: an audit alone closes
no failure modes — it surfaces candidates but does not constrain
behavior; needs operator follow-through to convert each flagged skill
under its own attested ADR work; threshold-tuning is itself a design
question (false positives on legitimately procedural skills like
`gz-design` interview prose).

**Hybrid C → A** is the natural sequencing: Surface C runs first to
produce the authoritative remediation inventory, then Surface A
converts each flagged skill one at a time under its own
foundation/feature ADR. Surface B is the catch-all backstop while
conversions are in flight — every procedural skill that has not yet
been inverted gets the gate-wiring as an interim defense.
Defense-in-depth at the catalog level, the per-skill level, and the
audit-evidence level.

## Acceptance criteria (carried from GHI #460, refined for pool entry)

When promoted, the implementing ADR(s) must land:

- New validator scope `gz validate --skill-procedural-drift` emitting
  the per-skill fingerprint + remediation flag (Surface C). Audit
  output is read-only and operator-skim shape.
- One concrete skill converted to Surface-A form under an attested
  ADR. Procedural prose migrated to `docs/governance/<runtime>.md`;
  PreToolUse hook from Surface B wired for that skill's runtime
  invocation. `gz-obpi-pipeline` is the natural first candidate
  because it is the surfacing skill and because
  `ADR-pool.obpi-pipeline-mandate-enforcement` already scopes the
  runtime-authority gate at its lock-claim entry point.
- The conversion is demonstrably non-regressing: a new OBPI run
  through the converted skill succeeds end-to-end without the
  orchestrator walking runtime sub-steps manually. The non-regression
  receipt is captured under the implementing OBPI's Stage 4 evidence.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

### Related GHIs (routed-here)

- **GHI #460** — primary surfacing GHI; closed `superseded` against this
  pool ADR. Documents the catalog-wide pattern, rejects the shortening
  band-aid, and proposes Surfaces A/B/C captured above.
- **GHI #459** — adjacent surfacing; same failure class observed at
  `gz-obpi-pipeline` Stage 2 (two-stage spec/quality review dispatch
  + `pipeline-orchestrator` persona adoption are doctrine-only with no
  T2 mechanical fail-close). May route here as a sibling-cut close if
  the operator agrees on the same destination; alternatively to
  `ADR-pool.obpi-pipeline-mandate-enforcement` whose scope is
  `gz-obpi-pipeline`-specific.

### Related ADRs

- **`ADR-pool.obpi-pipeline-mandate-enforcement`** — sibling pool ADR
  scoped to `gz-obpi-pipeline` specifically (lock-claim + marker +
  runtime-launch gate). This ADR addresses the catalog-wide surface
  that produces the gate-avoidance behavior; the sibling closes the
  per-skill gate. Together they form upstream + downstream coverage.
- **`ADR-pool.skill-control-surface-contract`** — defines canonical
  `SKILL.md` structural contract as an agent-control surface (role,
  layout, CLI commands, output format, forbidden behavior). This ADR
  is downstream of that contract: the runtime-authority inversion is
  one specific structural pattern the contract should require for
  procedural skills.
- **`ADR-pool.skill-behavioral-hardening`** — anti-rationalization
  defenses at the skill-prose layer (rationalization tables, circuit
  breakers, RED-GREEN-REFACTOR strictness). Complementary axis: that
  pool ADR hardens what the skill body *says* against rationalization;
  this ADR removes the *opportunity* to rationalize by inverting the
  body's authority entirely.
- **`ADR-0.0.32` § Named exceptions Exception 1** — hooks-as-vendor-
  coupled named exception. Surfaces A and B intersect this exception
  because PreToolUse hooks are not uniformly cross-vendor; promotion
  must address the vendor-harness capability matrix.
- **`AGENTS.md` § MAKE LLM STOCHASTIC VIBES INERT** operative claim 3
  (*"Doctrine drift is invariant drift. Silent rule/threshold changes
  without a witness are the root failure."*) — this ADR names the
  cross-cutting mechanism by which skill bodies drift into doctrine
  without a witness.
- **`AGENTS.md` § OBPI Acceptance Protocol § Pipeline mandate** —
  canonical directive (*"After plan approval, agents MUST run
  `uv run gz obpi pipeline <OBPI-ID>`"*) currently advisory at the
  skill-body layer; this ADR's mechanical surfaces would make that
  directive load-bearing.
- **`docs/governance/trust-doctrine.md` § T1/T2/T3** — names the layer
  the failure lives on (T1 operator-recorded canon → T2 mechanical
  fail-close); this ADR closes the T1→T2 gap for skill-body procedural
  drift.

### Out of scope for this pool ADR

- Dialogue-shaped skills (`gz-design`, `ghi-author`, `gz-justify`,
  `gz-prd`, `gz-constitute`) whose body content is operator interview
  prose rather than runtime procedure-mirroring. The inversion
  predicate is *"does the body describe what a runtime does?"*, not
  *"is the body long?"*. Length is a candidate signal (Surface C) but
  not the decision rule.
- Cross-vendor PreToolUse hook portability. Surfaces A and B assume
  Claude Code as the reference harness; cross-vendor parity is
  scoped under `ADR-0.0.32` and the vendor-alignment pool ADR series.
- Shortening pass on existing skills as a substitute for the
  structural inversion. The operator framing rejects this explicitly
  (GHI #460); any "diet pass" on a procedural skill that does not
  invert authority is a band-aid this ADR's promotion must not adopt.
