---
id: ADR-pool.convergence-moment-cross-family-critic
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.convergence-moment-cross-family-critic: Convergence-Moment Cross-Family Critic

## Status

Pool

## Intent

Give the operator an independent, cross-family second opinion at the moment an
agent converges on a design — the moment it presents analyzed options and asks
the operator to choose. Operator statement of need, verbatim (2026-08-06):

> we are trying to jump in when you offer analyzed and considered design options
> in the same structed way - you've achieved convergence, within that session,
> when you do so, I need a 2nd opinion in that exact moment

And the standing goal for the work, verbatim: *"retain cross-family review for
consequential decisions."*

The gap is real and measured. The 7 artifact-authoring skills carry a
`> Self-Escalation (opus-tier)` directive that escalates **same-family** — a
Claude main session consulting a Claude subagent, which shares training priors
and therefore confirms shared antecedents rather than applying independent
pressure. `gz-obpi-pipeline` Step 4b already codifies cross-family independence
for the *implementation* gate (*"a Claude validating Claude shares failure
modes"*). The **design** phase has no equivalent.

### Why this ADR exists rather than a GHI comment

The design converged across three sessions and was carried only in handoff
narrative (`20260807T021138Z` → `20260807T030745Z` → `20260807T073627Z`), so each
session re-derived it from prose. Operator ruling, verbatim (2026-08-07):

> maybe the askuserquestion work should have been made into a pool adr - the
> handoff to handoff method seems to be diluting its design

`ghi-author` § Doctrine already prescribed this: an architectural-absence finding
routes to a pool ADR, and *"a GHI that waits around to mirror the destination's
status is duplicate state."* GHI #670 is the routing artifact; this ADR is the
destination.

## Decision

Fire a **cross-family critic at the convergence moment** via a `PreToolUse` hook
on `AskUserQuestion`, and retire the same-family `Self-Escalation` blocks it
subsumes.

| Element | Decision | Provenance |
|---|---|---|
| Trigger | The convergence moment — `PreToolUse` on `AskUserQuestion`. Explicitly **not** an Airlock Jr. | operator-ruled |
| Transport | `type: "command"`. Neither `type: "agent"` nor `type: "prompt"` reaches a non-Anthropic vendor, so a cross-family critic must shell out. | measured |
| Injection shape | Preamble **always**; plus one appended option when the base question carries ≤3 options. Critic's PREMISE-ATTACK/VERDICT → preamble; its UNASKED line → the appended option label. | operator-ruled |
| Passthrough | Via `updatedInput`. Operator ruling: *"it is a 2nd opinion, not a usurped opinion."* This proved **stronger** than the ruling required — the harness enforces the passthrough, so the critique never enters the agent's context before the operator sees it. | operator-ruled |
| Information to the critic | Maximum (*"we should pass max information to the hook"*). Already satisfied: `transcript_path` hands the critic the entire session. | operator-ruled |
| Latency | **Measured, not estimated**: 11.62–15.50s bare (mean 13.9s); 19.62s carrying a 50KB transcript slice read agentically at xhigh. A synchronous `command` hook is viable — no escalation ladder, no lag-by-one gating. | measured |
| Vendor posture | Deliberately concrete, not generic: *"The US Air Force, the Chinese Air Force, etc. we can refactor to generics once we have platform stability."* Claude is the daily driver; Codex is the named adversary; lock-in accepted knowingly (*"I need forward momentum, not design niceties"*). | operator-ruled |
| Calibration | *"we can experimentally refine this moving forward"* — a calibrated pilot satisfies the ruling; a universal fail-closed gate on day one is not required. | operator-ruled |
| Constraint acceptance | *"we can work with 4 options, and other limitations - contraints usually strengthen designs"* (spelling preserved). | operator-ruled |

### Boundary — the OBPI pipeline is untouched

Operator ruling, verbatim: *"we will NOT alter the OBPI process, at all! This is
a broader and per-session tool need"*, and *"it is possible we generalize from
the existing skills/tooling for obpi 4b, but I am hesitant to alter anything
about the obpi pipeline as it is the most enduringly stable part of gzkit."*

Generalizing **from** Step 4b's tooling is permitted; altering Step 4b is not.
A concrete casualty of ignoring this boundary is already on record: a
7-to-8-minute latency figure imported from OBPI-pipeline mechanism was ~20x
high and had to be withdrawn after direct measurement.

### Movement C posture

The hook is the 19th (18 exist under `.claude/hooks/`). It nonetheless **reduces**
instruction surface: it retires the `Self-Escalation` block in 7 skills, and
skills mirror across 4 vendor surfaces — ~28 copies removed to add one hook.
Reduction is a stated pre-1.0 gate (campaign Movement C); this lands on its side.

## Alternatives Considered

1. **Amend the 7 `Self-Escalation` blocks (GHI #670's original deliverable).**
   Rejected: it fires on *skill invocation*, and the operator's trigger is the
   *convergence moment*. Those diverge — the session that authored this ADR
   reached convergence through no skill on that list. The persona-plus-7-edits
   plan cannot reach the moment it was filed to cover.

2. **Extend `adversarial_validation` with a phase discriminator, reusing Step 4b.**
   Rejected by explicit operator ruling (*"we will NOT alter the OBPI process, at
   all"*). Attractive on paper — the ledger event and tier ladder already exist —
   which is exactly why the boundary is recorded rather than left to judgment.

3. **Keep the same-family opus self-escalation (status quo).** Rejected: the two
   share training priors and blind spots, so the subagent's pushback tends to
   confirm shared antecedents. This is the same reasoning Step 4b already
   codified one layer down; the design phase inherits it.

4. **Asynchronous or lag-by-one critic (critique the *previous* question).**
   Rejected on measurement: round-trip is 11.62–19.62s, well inside a synchronous
   hook's tolerance. Lag-by-one was designed against a withdrawn 7–8 minute
   figure and became unnecessary the moment the real number was observed. It also
   breaks the stated trigger — a critique arriving one question late is not
   *"a 2nd opinion in that exact moment."*

5. **`permissionDecision: "deny"` instead of `updatedInput`.** Rejected as the
   primary mechanism: denying usurps the agent's question rather than
   accompanying it, contradicting *"a 2nd opinion, not a usurped opinion."*
   Retained as an open question — deny was never tested, and whether it blocks
   cleanly or wedges the picker is unknown.

## Notes

### Open, unresolved at pool time

- `permissionDecision: "deny"` on `AskUserQuestion` untested; only `updatedInput`
  was exercised.
- Base rate to re-measure after any mechanism ships (seed `20260807`, same
  five-class taxonomy), recorded via `gz insights remember --type discovery`.
  State the ceiling honestly: **68.3%** is the share of defect GHIs whose root
  cause is a design decision — an UPPER bound, since most such decisions were
  never surfaced as an `AskUserQuestion` at all. The tighter read is **23%**
  (explicit overconfident-premise signature in the GHI body).
- The critic must engage the premise. Operator observation, verbatim: *"the
  option you always provide is 'discuss this' (approximating): the critic needs
  to engage your premise. You almost always equivocate and hedge in the narrative
  that follows. easly a discernible majority of the time."* (spelling preserved).

### Relationship to existing artifacts

| Artifact | Relationship |
|---|---|
| GHI #670 | The routing artifact. Closes `superseded` against this ADR. |
| GHI #765 | Sibling in the adversarial-evidence family, distinct surface: #765 governs OBPI *completion* evidence; this governs the *design* moment. Its lesson transfers — prefer a runtime artifact over a self-assertion. |
| `gz-obpi-pipeline` Step 4b | Doctrinal source for the tier ladder. Generalize **from**, never alter. |
| ADR-0.33.0 (airlock) | Explicitly NOT the pattern here — this is not an Airlock Jr. |

### Promotion plan (when pulled)

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree is performed via `gz adr promote`, which rewrites
the frontmatter with the chosen taxonomy. Expected shape on promotion: `feature`
kind, `heavy` lane (the hook changes what a human sees at a decision point), with
OBPIs splitting roughly as (1) critic invocation adapter + decision module,
(2) the `PreToolUse` hook and its injection shape, (3) retirement of the 7
`Self-Escalation` blocks plus `gz agent sync control-surfaces`.

Per campaign § 7 the pool backlog is post-1.0, and Architectural Boundary 1
forbids promoting post-1.0 pool ADRs into active work. Authoring this ADR homes
the design; it does not queue it.
