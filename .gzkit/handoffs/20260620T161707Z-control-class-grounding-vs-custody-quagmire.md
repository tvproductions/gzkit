---
mode: CREATE
adr_id: ADR-0.0.74
branch: main
timestamp: "2026-06-20T16:17:07Z"
agent: claude-code
obpi_id:
session_id:
continues_from: .gzkit/handoffs/20260620T153123Z-obpi-0.0.74-01-completion.md
---

<!-- Handoff document for ADR-0.0.74-mx-mode-maintenance-hangar — created by claude-code at 2026-06-20T16:17:07Z -->

## ⚠️ This handoff ADVISES next moves — it is NOT authorization to execute them

**Read this before anything else.** A handoff records a *proposed* plan and its
context. It is **NOT** a clearance to unilaterally execute that plan. On resume —
at **every** freshness level, Fresh included — you MUST:

1. Present the advised next steps and current state to the operator.
2. **Obtain explicit operator authorization before executing any of them** — no
   file mutation, no `gz` ceremony, no migration until the operator says go.
3. Treat the human-as-final-witness doctrine as binding from the first step: you
   advise; the operator rules; you note variance and stop.

This handoff is mostly a **design-dialogue capture**, not an implementation plan.
The operator explicitly asked that the whole dialogue be preserved here ("take
your whole dialog up there and place it into the handoff") because the context
window is full and the in-context richness must not be lost. Do not execute the
proposed fix without ratifying its shape with the operator first.

## Current State Summary

**Register-entry facts:** last commit SHA `53171934` (git-sync #1 of the
OBPI-0.0.74-01 completion; pushed to `origin/main`); branch `main`, 0 ahead /
0 behind, **working tree CLEAN**; **no active OBPI locks** (OBPI-0.0.74-01's lock
was claimed `2026-06-20T14:10:31.428588+00:00` and released cleanly at Stage 5).

**OBPI-0.0.74-01-mx-marker-file is COMPLETE and synced** (Layer-2:
`attested_completed`, attestor `g0`, operator-verbatim "attest completed").
ADR-0.0.74 (MX Mode — Maintenance Hangar, foundation/heavy, topmost P0) is now
**1/10**. The marker module `gzkit.mx.marker` shipped (Marker BaseModel,
is_active / read / write / is_valid, marker_path; no gzkit-internal imports;
12 tests; full suite green at receipt `arb-step-unittest-8c36eb010f774eadb9944bc84d6ed1de`).

**What this handoff is really about:** completing that one OBPI tripped ~9
fail-closed gates one at a time, and the operator's reaction opened a
foundational design thread — *the lock quagmire and the single class of control
underneath all of gzkit's "dialects of control."* That dialogue (diagnosis,
per-control review, proposed PRIME-DIRECTIVE-level fix, open decisions) is the
payload below. It is unratified; it is the resume point.

## Important Context

This section is the verbatim-faithful capture of the design dialogue, in order.

### Trigger — the lock cascade one OBPI tripped

OBPI-0.0.74-01 is a ~190-line module plus a test file. Landing it required
satisfying, in sequence, one at a time, these fail-closed gates (most fired not
because the work was wrong but because the gate was strict and un-batched):

1. Stage-2 entry gate — needed a `brief_reconciled` receipt
2. brief allowlist — needed `tests/mx/__init__.py` added
3. `audit_pydantic_models` — forced the `Marker` design (a real correction, below)
4. `--insights-shape` schema — evidence-as-list, not string
5. `@covers` resolution — docstring refs do not run; needed method decorators
6. **`behave_req_coverage` (precomplete) vs `waiver-ratchet`** — the deadlock
7. receipt-binding — rejected truncated receipt IDs; needs full 32-hex IDs
8. reconcile-freshness — stale after each edit, re-reconcile each time
9. lock-handoff coupling — releasing the lock on a COMPLETED OBPI required
   authoring a full handoff register entry first (already open as GHI #619)

### Operator framings (verbatim)

- "the new mx mode should get rid of bullshit like that. too many locks. we
  need to discuss that."
- "I want some PRIME DIRECTIVE-level fix to this nonsense."
- "this is the worst possible quagmire hell I can imagine. what is the class of
  control these dialects of control are trying to achieve?"
- "okay, but they are not quite all the same, let's review them one by one and
  tell me which are the current issue."
- "take your whole dialog up there and place it into the handoff"

### The diagnosis — one class of control: GROUNDING

Strip the costumes off and there is one control class under nearly all of them:

> **A claim of state must be bound to evidence the claimant cannot fabricate —
> so that recorded state never outruns verified reality.**

Motive = the anti-vibing doctrine (a stochastic agent, and a tired human, will
assert things that are not true). Every gate is the same defense: do not trust
the asserter; bind the assertion to an independent witness. The dialects all
collapse to one shape — `claim -> witness -> verdict`:

| Dialect | The claim it doubts | The witness it demands |
|---|---|---|
| `gz validate` (exit 3) | "this surface is valid" | re-derive from canonical source |
| ARB receipt | "QA ran green" | `exit_status` captured at run time |
| Gate 5 attestation | "the work is truly done" | a human |
| `@covers` | "this REQ is satisfied" | a test that exercises it |
| `gz brief reconcile` | "the brief describes the work" | byte-compare brief vs tree |
| ledger (append-only) | "this event happened" | the immutable record itself |
| waiver / grandfather / ratchet | "this exception is legitimate" | a bounded, monotonic, recorded baseline |
| token-block / handoff coupling | "surrender is legitimate" | a register entry |

gzkit did not build many controls. It built ONE control many times, each with
its own syntax and its own bespoke escape hatch — and the escape hatches
(waivers, grandfathers, flags) then became locks themselves. The quagmire is not
"too many locks"; it is **one primitive, un-unified, fractally re-expressed.**

### The correction the operator made — they are NOT all the same

Two refinements to the over-unification:

**(A) One dialect is a different CLASS entirely: custody.** The OBPI lock is not
grounding — it is **mutual exclusion** (so two agents do not clobber the same
work). Grounding asks "is this claim true?"; custody asks "who holds this right
now?" Orthogonal. The session's most absurd moment — authoring a full handoff to
release a lock on an already-completed OBPI — is exactly that category error: a
custody lease forced to carry grounding machinery. Custody is near-vacuous for a
single operator (no second agent to exclude), so the full grounding tax was paid
on a control whose real job was empty.

**(B) Among the grounding controls, only SOME are the current issue.** The tell:
the problem controls are control-on-a-control, kind-blind, miscategorized, or
freshness-coupled. The healthy ones are direct, single-purpose, kind-aware.

#### RED — the acute quagmire (these are what hurt)

| Control | Class | Why it is the issue |
|---|---|---|
| **waiver-ratchet** (shrink-only) | grounding ON a control | The escape hatch became a lock. Grounds the *exception valve* ("waivers may only shrink") — a control on a control. Forbade the waiver the behave-gate demanded. Fractal re-expression in its purest form. |
| **behave_req_coverage** (precomplete) | grounding, kind-BLIND | Demands a behave scenario (or waiver) for every REQ — even structural-fence and no-CLI-surface ones. Redundant with `@covers`; its only valve is ratchet-forbidden -> the deadlock. |
| **OBPI lock + handoff coupling** | CUSTODY miscategorized as grounding | The category error. A mutual-exclusion lease forced to carry handoff-as-evidence. Near-vacuous for a single operator. (GHI #619.) |
| **self-decided severity / staging flags** | the architectural root | Each gate sets its own strictness (`_FRESHNESS_FAIL_CLOSED`, etc.). No single authority. This is why the others proliferate. |

#### YELLOW — partial (principle sound; implementation bites — soften, do not remove)

| Control | Why it bites |
|---|---|
| reconcile-freshness | Receipt must postdate every touched file -> re-reconcile after each edit. |
| receipt-binding freshness + exit-code masking | Forces re-running full sweeps after any edit; the piped-exit-0 trap masked two RED runs (GHI #589). |
| `@covers` resolution | Docstring vs decorator silently resolve to different runnability — "covered" per `gz covers` yet "failing-cover" at complete. A footgun, not a wrong principle. |
| serial stage firing | 9 gates, one round-trip each. Should be one batched clearance (GHI #463, closed — reopen candidate). |

#### GREEN — not the issue (load-bearing — preserve, and copy the good ones)

| Control | Verdict |
|---|---|
| Gate 5 attestation | Sacrosanct. The floor. Never relax. |
| ledger (append-only) | The source of truth everything else grounds against. |
| kind-discipline (REQ kind -> proof channel) | The MODEL to emulate — it is kind-aware. behave_req_coverage is the issue precisely because it is not this. |
| audit_pydantic_models | Did its job — caught the real `Marker` design question the operator ruled on. |
| insights-shape / validate --documents / brief allowlist | Cheap, correct, single-purpose grounding. |

### The proposed PRIME-DIRECTIVE-level fix (UNRATIFIED — resume point)

Not "fewer controls" (that re-opens vibing). The fix: **no control-on-a-control;
every grounding control kind-aware; custody modeled as custody; one severity
authority.** Concretely, two moves:

1. **One grounding primitive.** `(claim, evidence-source, witness) -> grounded |
   ungrounded | relaxed(recorded-reason)`. Severity (block vs warn), the floor
   (`gate5_invariants` = claims that may never be relaxed), and every exception
   valve (waiver / grandfather / ratchet / freshness) become **parameters of the
   one primitive**, not separate machines. Express every gate as an instance; the
   bespoke dialect files (waiver registries, grandfather baselines, staging flags)
   mostly DELETE. This is the elevation of ADR-0.0.74's Boundary Invariant #2
   ("the checkpoint is the single severity authority") from a hangar feature to
   the governing law of the whole guard surface, made un-proliferable by a fence
   validator (any exit-3 path outside the checkpoint fails the fence).
2. **Custody as a separate, smaller class.** Model the OBPI lock as a lease; make
   it near-free for a single operator; stop making it pay grounding's tax (no
   handoff-as-evidence required to release a completed OBPI).

Earlier framing ("single severity authority") was one layer too shallow — it
managed the locks. The real shape is below it: there is one grounding primitive,
and severity is just one knob on it.

## Decisions Made

- **Conceptual model (agreed in dialogue, not yet booked):** the dialects are
  one control class — *grounding* (recorded state may never outrun verified
  reality) — with the OBPI lock as a separate *custody* class miscategorized as
  grounding. The quagmire is one primitive fractally re-expressed plus one
  category error.
- **The behave/waiver-ratchet GHI is ON HOLD, reframed.** Do NOT file it as a
  standalone E.5 drainage band-aid. It is exemplar #1 of the bigger fix and
  should close `superseded` into whatever artifact carries the grounding-primitive
  elevation (likely an ADR-0.0.74 amendment). Step-0 prior-art lookup was done
  this session: no exact-duplicate open GHI; nearest neighbors are the CLOSED
  #463 (batched gate contract) and OPEN #619 (completed-OBPI lock-release).
- **OBPI-0.0.74-01 completion decisions** (recorded in the completion handoff
  `20260620T153123Z-obpi-0.0.74-01-completion.md` and the brief): Marker is a
  Pydantic BaseModel (operator-ratified correction of the confused "stdlib-only"
  premise -> the real invariant is "no gzkit-internal imports"); the marker is
  `.gzkit/mx.json`; `tests/mx/__init__.py` added to the allowlist; behave waiver
  was added then REVERTED (it violated the waiver-ratchet) and completion
  proceeded via the `@covers` chokepoint.

## Immediate Next Steps

<!-- ADVISORY ONLY — present to operator, await authorization before executing. -->

1. **Resume the design dialogue at the floor-membership decision.** The single
   gating question for the whole fix: is `gate5_invariants` exactly {faked
   attestation, secrets, operator-PII, ledger integrity}? Everything outside it
   becomes relaxable, so this list is the whole ballgame. Then: episodic
   (hangar-only) vs always-on relaxation for the two pure-friction gates
   (reconcile-freshness, behave_req_coverage).
2. **Route the fix through the governed spine (operator-ratified, not freehand).**
   Recommended: run a `gz-design` dialogue that elevates **ADR-0.0.74** from "a
   hangar mode" to "the severity architecture of the whole guard surface" —
   amend its Intent, expand OBPI-02 (checkpoint) to inventory *every* extant
   fail-closed funnel, add a fence-validator OBPI (no exit-3 outside the
   checkpoint) and a batched-clearance OBPI (fold in closed GHI #463), and
   generalize OBPI-09 (retire staging flags) to the whole waiver/grandfather/
   ratchet/freshness sprawl. Model custody (the lock) as a separate lease.
3. **Capture the doctrine to the AGENTS.md corpus** via `gz content remember`
   so it renders into the agent contract — a top-level invariant alongside the
   anti-vibing mantra: "Governance must never slap its own repair; one grounding
   primitive; one severity authority; one floor; custody is not grounding."
4. **Book a Magna Carta amendment** (operator-verbatim) recording the elevation,
   then close the behave/waiver finding `superseded` into the ADR.
5. **Only after the above:** continue ADR-0.0.74 with OBPI-0.0.74-02
   (mx-shared-checkpoint), which under the elevated framing IS the grounding
   primitive's home.

## Pending Work / Open Loops

- **The grounding-primitive elevation is unbuilt and unbooked** (Steps 1-4) —
  the core resume thread.
- **behave/waiver-ratchet deadlock** — ON HOLD, to be absorbed (not standalone
  GHI). Blocks `precomplete` clean-exit for every unit-only OBPI in ADR-0.0.74
  (the remaining 9) until the fix lands; `gz obpi complete` still works via the
  `@covers` chokepoint, so completion is possible, precomplete just cannot go
  green.
- **OBPI-0.0.74-07 brief drift** — carries the pre-correction "stdlib-only marker
  read" framing; its `awareness.py` reuses the now-pydantic marker. Reconcile to
  "no gzkit-internal imports" when OBPI-07 is pulled (tracked in OBPI-01 brief
  Tracked Defects).
- **Parent ADR-0.0.74 scaffold gaps** (owned by ADR closeout): the `{persona}`
  token is unfilled; `## Fidelity Assertions` table is still the example row
  (`uv run gz --version` expects 0) and will fail `gz validate --fidelity-presence`
  at closeout.
- **Lock-class GHIs already open** to fold into the custody half: #619
  (completed-OBPI lock release has no register path), #606 (lock claimed + no
  pipeline = src writes pass), #604 (token-block TTL canon 24h vs CLI 120m).
- **#463 (CLOSED)** — batched gate contract at plan time — reopen candidate for
  the batched-clearance OBPI.
- **OBPIs 0.0.74-02 through -10 unbuilt** (the remaining ADR decomposition).
- **Pre-existing, cosmetic:** malformed HEAD message on commit `465d2863` (raw
  git template); on `origin/main`, rewrite needs force-push (operator call).

## Verification Checklist

- [ ] `git rev-parse --short HEAD` -> `53171934` (until new work commits)
- [ ] `git status --short` -> empty (tree clean)
- [ ] `uv run gz obpi status OBPI-0.0.74-01-mx-marker-file` -> `attested_completed`
- [ ] `uv run gz obpi lock list` -> "No active locks."
- [ ] `uv run -m unittest tests.mx.test_marker -q` -> 12 tests OK
- [ ] `uv run gz validate --waiver-ratchet` -> exit 0 (522 entries; behave waiver was reverted)
- [ ] `uv run gz adr status ADR-0.0.74-mx-mode-maintenance-hangar` -> OBPI-01 complete, 02-10 pending, closeout BLOCKED (expected)

## Evidence / Artifacts

- `src/gzkit/mx/marker.py` — the MX marker module (the grounding/custody dialogue's trigger)
- `src/gzkit/mx/__init__.py` — the mx package init
- `tests/mx/test_marker.py` — 12 @covers-decorated tests
- `tests/mx/__init__.py` — test package init
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — the ADR to elevate (carries the checkpoint + Boundary Invariant #2 kernel)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-01-mx-marker-file.md` — the completed brief (Tracked Defects records OBPI-07 drift)
- `.gzkit/handoffs/20260620T153123Z-obpi-0.0.74-01-completion.md` — predecessor (OBPI-01 completion register entry)
- `docs/governance/build-to-1.0-campaign-2026-06-10.md` — Magna Carta (the amendment home)
