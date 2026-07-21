---
name: gz-flighttest
persona: flight-test-engineer
description: Drive one flight-test sortie against a target substrate to prove a gzkit workflow end-to-end. Use when running the flight-test program, when the user says "fly sortie S<N>", "run a flight test", "prove gzkit against <target>", or to advance a flight-test campaign. Executes one sortie per run — author card, obtain human Go/No-Go, fly the governed-path chain, collect black-box evidence, dispatch an independent Chase, debrief, and route squawks.
category: governance-infrastructure
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-07-05
metadata:
  skill-version: "0.1.0"
model: sonnet
---

# gz-flighttest

Drive **one sortie** of the [Flight-Test Program](../../../docs/flighttest/README.md)
against a target substrate. A sortie is one flight flown in a single sitting —
a chained run of test points that proves a gzkit workflow behaves as designed,
with the target repo's ledger and receipts as the flight-data recorder.

**This skill operates *inside the target repo*, where gzkit is the
system-under-test.** It is authored and versioned in gzkit and ships via
distribution, but it runs on the ground in the target — flying gzkit's own
workflows there. ("Operate in" ≠ "live in.")

**The product is feedback that refines gzkit — not a built target.** A sortie's
yield is proving-outcomes about gzkit's design; the target is scaffolding.
Because the skill runs in the target, that feedback reaches gzkit **cross-repo**:
gzkit-directed squawks are filed via `gz issue file` (the `gz-issue-file`
skill), which routes to the gzkit repo regardless of the target's git remote —
never `/ghi-author`, which would file in the target (the wrong tracker).

The **program** (target-agnostic doctrine) lives in gzkit `docs/flighttest/`.
The **campaign instance** and **flight log** live in the *target repo*
(scaffolded from `docs/flighttest/templates/`). This skill is the propellant
that flies a sortie and writes its evidence to the target's flight log.

Flight-test campaigns are a **distinct work-stream**: they govern flight-test
engagements against a target, and never contend with the Build-to-1.0 Magna
Carta, which rules gzkit's own build sessions.

## Persona

**Active driver:** `flight-test-engineer` — read `.gzkit/personas/flight-test-engineer.md`
and adopt its behavioral identity before flying. Falsifier-precommitment,
black-box-evidence, and chase-deference are not rules you follow; they are who
you are in the air.

## Roles (who does what)

| Role | Who | This skill's relationship |
|---|---|---|
| **Test director** | **Human operator** | Authorizes each sortie (Go/No-Go); witnesses Gate-5; rules on squawk disposition. **Never an agent.** The skill *pauses* for these decisions — it does not make them. |
| **Flight-test engineer** | This skill (agent) | Authors the card, flies the chain, collects evidence, drafts the debrief. |
| **Chase** | `spec-reviewer` / `quality-reviewer` subagent | Confirms the pass from the black box alone; never flew the sortie. |

## The Iron Law

```
A SORTIE IS NOT COMPLETE UNTIL ITS DEBRIEF IS RULED ON AND ITS SQUAWKS TRACKED.
A PASS IS NEVER SELF-DECLARED — THE CHASE VERDICTS; THE HUMAN AUTHORIZES.
```

"The commands ran" is not completion. "It worked when I flew it" is not a pass.
The sortie runs through its debrief, and the pass/fail verdict is authored by an
independent Chase reading evidence you did not narrate. Soliciting the human's
Go before the card is frozen, or claiming a pass before the Chase has read the
black box, is a gate bypass.

### Rationalization Prevention

| Thought | Reality |
|---|---|
| "The chain ran clean, let me mark it passed" | You do not grade your own landing. Freeze evidence, dispatch the Chase. |
| "The hook blocked me — let me hand-write the marker to keep flying" | The block IS the finding. Record it; never route around it (that is the vibing you were sent to catch). |
| "I'll write the expected observables from what I just saw" | The falsifier is authored *before* the flight, from the design. Post-hoc expectations are worthless. |
| "This corner sortie is interesting, let me fly it first" | Build up the envelope. A corner sortie with no spine baseline is unreadable data. |
| "I'll ask for Go/No-Go and Gate-5 together to save a round-trip" | Go/No-Go gates entry; Gate-5 gates completion. Bundling them is the bundled-attestation anti-pattern. |

## Preconditions

1. A **target substrate** satisfying `docs/flighttest/README.md` §7 (boring &
   bounded, real-buildable, greenfield/near-cold, separate repo).
2. A **campaign instance** in the target repo (scaffold from
   `docs/flighttest/templates/campaign-instance.md` on first run) and a
   **flight log** (from `flight-log.md`).
3. Green floor: the target's `uv run gz check` is not red at sortie open (a
   sortie does not fly into a broken baseline).

## The sortie sequence (one run = one sortie)

### Stage 1 — Resolve the topmost sortie
- Read the target's campaign instance. Identify the **topmost unflown sortie
  whose entry gate is met** (build-up order; a sortie whose `DEPENDS ON` has not
  passed is not eligible). Do not reorder by interest.
- Confirm the target's baseline is green (`uv run gz check`).

### Stage 2 — Author the flight card (freeze the falsifier)
- Draw the card from `docs/flighttest/manifest.md` for this sortie and the
  template in `docs/flighttest/flight-card-template.md`.
- Author **expected observables from the workflow's design**, not from a trial
  run: the exact ledger event kinds/counts, receipt name prefixes, and
  `gz state`/`gz status` assertions that constitute a pass, plus the
  pre-registered falsifiers (including the "passed only by leaving the governed
  path" tripwire).
- Freeze the card into the flight log as a `CARD` entry.

### Stage 3 — Go/No-Go (human gate)
- Present the frozen card to the **test director** and pause for explicit
  Go/No-Go. Record the ruling (verbatim) to the flight log.
- No Go → the sortie does not open. This pause is not optional.

### Stage 4 — Fly the chain
- Execute each test point **in order, through its governed path** (the matching
  skill or `gz` verb named in the manifest). Feed each point's output into the
  next — the chain is the point.
- A blocking hook or failing gate is a **squawk**, recorded, never defeated. If
  the governed path cannot carry a test point, halt per the card's abort
  criteria; do not hand-craft the artifact.
- Collect the black box: the target's ledger slice for the sortie window and all
  emitted receipts.

### Stage 5 — Chase (independent verdict)
- Dispatch a `spec-reviewer` (evidence-to-card tracing) and/or `quality-reviewer`
  (integrity of the run) subagent. Hand them **the ledger slice and receipts —
  not your narrative.** Include a `Why` in the subagent prompt (filter signal
  from noise).
- The Chase authors PASS/FAIL against the card's pre-registered falsifiers,
  reachable from evidence alone. If the Chase cannot reach PASS from the black
  box, the sortie has not passed.

### Stage 6 — Debrief & route squawks
- Draft the debrief (dispatch `narrator` for operator-value framing if useful):
  black box vs. card, each squawk, and the design signal
  (sound / awkward-but-correct / wrong — with the why).
- Route every squawk — **untracked squawk = nonexistent squawk**. Because the
  sortie flies in the target repo, gzkit-directed feedback goes **cross-repo**:
  - **gzkit defect (the product)** → file **against gzkit** via `gz issue file`
    (the `gz-issue-file` skill) — routes to the gzkit repo regardless of the
    target's remote. **Never `/ghi-author`**, which files in the target. This is
    the engagement's yield.
  - **gzkit correct-but-wrong-design** → also `gz issue file` against gzkit; a
    gap between shipped surface and declared intent is a **correction** to the
    owning gzkit ADR, not an enhancement (operator doctrine).
  - **Target/substrate-local defect** → fix in the target or track it there; it
    gates the sortie only if it blocks the workflow under test.
  - **Bad card** → amend the card in the target's flight log; re-fly.
- Present the debrief to the test director for a ruling.

### Stage 7 — Record & advance
- Append the sortie's full record (card, Go/No-Go, black box, Chase verdict,
  debrief, squawk dispositions) to the target's flight log — the append-only
  Layer-2 of the engagement.
- Tick the campaign checkbox **only with the Chase verdict + ledger evidence
  cited** (the checkbox is Layer-3; the flight log is truth).
- Surface the next eligible sortie; do not auto-open it (each sortie is
  human-authorized).

## Validation

- The flight log carries a complete record for the sortie (card frozen before
  fly; Go/No-Go verbatim; black-box slice; Chase verdict; debrief; squawk
  routes).
- Every squawk has a tracked home — gzkit-directed ones as a **cross-repo**
  `gz issue file` against gzkit (never a target-local `/ghi-author`); a
  target-local defect or a card amendment otherwise.
- The campaign checkbox change cites Chase verdict + ledger evidence, never
  narrative.
- No test point passed by leaving the governed path.

## Anti-patterns

- Flying a sortie before its dependency sortie has passed (envelope violation).
- Authoring expected observables after seeing the output (falsifier inversion).
- Marking a pass without an independent Chase verdict (self-attestation).
- Hand-writing a marker / using `--no-verify` to get past a block (path-defeating —
  the block was the finding).
- Bundling Go/No-Go with Gate-5, or ticking a checkbox on prose (Layer-3 as truth).
