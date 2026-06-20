# gzkit Maintenance Guide (MX)

> **Status: DRAFT v0.1** — design-review, not ratified, not wired to enforcement.
> Companion to the operator's guides (`quickstart.md`, `runbook.md`,
> `governance_runbook.md`). Where the operator's guides tell you how to *fly*
> gzkit, this tells you how to *maintain* it when it is misaligned or ailing.

**Core maxim — Loose in the bay, hard at the door.** You may realign freely
inside a maintenance session; you may not return the aircraft to service until
every lock re-runs clean.

**Second maxim — Doctrine and rule are inseparable.** For a *human*, doctrine
alone can suffice: they internalize the *why* and self-govern. For a stochastic
*agent* it cannot — naked doctrine gets rationalized away, or worse, mimicked as
a vibed facade that *looks* like compliance (a pattern visible all over gzkit's
GHIs). In this guide, doctrine is the *why* of every shackle; the coupled rule is
the shackle itself. **Neither ships without the other.** An agent may offer
insight *post hoc*, but never rationalize away from doctrine and never build
something that resembles it without being it.

---

## 0. Why this guide exists

The operator's guides assume an airworthy airframe. They have no answer for "a
lock is red and the part it guards is not trued yet," for "a later finding
invalidates a prior ADR," or for "I need to realign governance without its own
constraints slapping me at every step." That gap — no maintenance doctrine — is
why gzkit spent ~60 days torquing untrued bolts: too many hastily-applied tight
locks on misaligned parts, with no sanctioned way to loosen, true, and re-torque.

This is the maintenance manual that gap was missing.

---

## 1. The three roles (read first — this dissolves the dogfooding confusion)

gzkit plays three roles at once. Conflating them is the root of the confusion.

| Role | Who | Does |
|---|---|---|
| **Manufacturer** | the agents | Engineers the airframe — drafts ADRs/OBPIs, diagnoses defects, writes the fix (the Service Bulletin). |
| **Regulator (FAA)** | the human operator, **by writ** | Issues mandates, certifies airworthiness, signs the certificate. |
| **Operator (airline)** | whoever flies gzkit — gzkit dogfooding itself, or an adopting project | Operates the aircraft to prosecute SDLC work. |

The separation of **Manufacturer** from **Regulator** is the entire safety
mechanism — a manufacturer may not certify its own product safe. In gzkit that
separation is preserved by exactly one fact: **agents engineer; only the human
regulator certifies airworthiness.**

This reframes Gate 5. It is **not** "approval of work." It is **the regulator
signing the airworthiness certificate** — a categorically different act, which
is precisely why it can never be delegated to an agent, a TTY, or any mechanism.
Attestation sanctity *is* regulatory independence.

### 1.1 The writ has two manifestations

The operator's FAA authority is carried by two coupled surfaces — **not** the
live attestation alone:

1. **Operator attestations** — the live regulatory act (Gate 5): the signature on
   *this* airworthiness certificate, now.
2. **Versioned doctrinal canon** — the standing regulation: the versioned
   documentation that *canonizes* what is lawful. This is what makes the writ
   durable across sessions rather than re-litigated each time.

### 1.2 Governance documents have types (agents must be able to tell them apart)

Agents currently cannot reliably tell a binding law from an explanatory rationale
from a procedure — so they vibe across the seam. The governance docs need a
declared, legible classification (proposed; candidate for its own doctrine doc):

| Type | Aviation analogue | Nature | Binding? |
|---|---|---|---|
| **Doctrinal** | Advisory Circular | The *why* — principle and rationale | Authoritative as intent; not mechanically checkable |
| **Lawful (Law)** | Federal Aviation Regulation | The *must* — mandatory, mechanically enforced where possible | Yes; violation grounds the aircraft |
| **Ordinance** | Local/operator rule under the law | Scoped, more-specific binding rule (project/subsystem) | Yes, within its scope; stricter-only vs. Law |
| **Ops spec** | Operations Specifications | The *how* — authorized procedures, runbooks, skills | Binding as method, descriptive of procedure |

> **Open:** this taxonomy likely deserves its own governance-doc-classification
> doctrine, with each existing governance doc tagged by type. The MX guide itself
> is **Doctrinal + Ops spec**; the mx-mode rules it couples to (§5, §7) are **Law**.

**Boundary (keep the metaphor honest):** gzkit-as-FAA regulates the **airframe**
— the governance apparatus. It does not regulate the airline's **payload** (the
product code an adopting project builds). The airline flies its own cargo under
its own operational control.

---

## 2. The governance spine = the design hierarchy

| Artifact | Aviation analogue |
|---|---|
| Constitution | The plan for developing & operating types |
| PRD | The plan for a *type* |
| ADR | The plan for a *part / subsystem* |
| OBPI / REQ / TASK | The design & build of that part |
| GHI / ARB / insight | A **squawk** — a logged defect noted on acceptance |

- A **flight** = any agentic prosecution of SDLC work (dogfooding or adopter use).
- A **release** = **ADR completion + validation** — the true revenue-flight
  milestone. OBPI completions are advances toward it.

---

## 3. The dispatch decision (the central reconciliation)

Every red lock asks one question: **can we dispatch?** Three answers.

- **Airworthy** — `gz check` green. Fly.
- **Dispatchable with limitation (MEL/CDL)** — the defect is real but mitigable;
  fly under documented limits with a ticking repair clock (§4).
- **AOG — grounded** — the defect makes the airframe unsound or the instruments
  untrustworthy. Do not dispatch. Fix in place, or pull to the hangar (§5).

**The carve:**

- **AOG** iff the lock is the *sole guarantor of a sound airframe or honest
  instruments* and no mitigation compensates. The bright lines (§6) are always AOG.
- **MEL/CDL-able** iff redundancy or a feasible (O)/(M) mitigation makes the
  flight safe. For the singleton-lock majority (one guarantor, no redundancy),
  the decider is **(O)/(M) feasibility**, not redundancy.

---

## 4. The MEL/CDL binder (dispatch-with-limitation)

> **Phase 1 folds MEL and CDL into one binder.** MEL = "installed but
> inoperative" (a failing check). CDL = "missing entirely" (e.g. a REQ with no
> test — flying with a coverage drag-penalty). Hold the distinction; split when
> the mitigations diverge (MEL → redundancy / lockout; CDL → performance penalty).

**MMEL vs operator MEL.** gzkit-core ships the **MMEL** — the ADR-backed baseline
of which locks are *ever* deferrable and under what conditions, delivered in the
wheel. An adopting project's config is its **operator MEL**: it may be *more*
restrictive, **never** less. No agent and no project may invent a deferral the
MMEL does not sanction. This is the anti-vibing railroad for deferral.

**An entry carries:** the lock by stable scope-ID (its "ATA chapter"); number
installed / required-for-dispatch; remarks; and its mitigation —

- **(O) Operational procedure** — a runtime behavioral limitation the
  operator/agent must observe while deferred.
  *Example:* floor-coherence deferred → "agents read the corpus directly; treat
  the rendered surface as untrusted."
- **(M) Maintenance procedure** — a structural safing / placard action, recorded.
  *Example:* "placard the stale rendition with a header naming the waiver ID."

**Repair intervals (the ticking clock), enforced by `gz validate --waiver-ratchet`:**

| Category | Deadline (clock starts the day *after* discovery) |
|---|---|
| **A** | By the next flight (next agentic use), or the interval named in remarks |
| **B** | 3 days |
| **C** | 10 days |
| **D** | 120 days |

No deferral is permanent. **A deferral with no clock is itself a defect.**

---

## 5. MX mode — the hangar (a teleport, because this is software)

Because gzkit is software, the metaphor relaxes in our favor: there is no
physical hangar to taxi to. **MX mode is a teleport** — you erect the hangar
around the aircraft wherever it is, instantly, and close the door. As a mode, it
**drops most guards** so you can direct-fix. Most of gzkit's trashing has been
*immature or incomplete implementation hitting torqued-down but improperly-seated
governance* — MX mode is the bay where you reseat the governance without it
slapping you at every step.

The teleport also dissolves the old "can't ferry to the hangar" worry: you do not
need a flyable aircraft to enter MX mode — entering MX mode is precisely what
drops the guards that would otherwise block you. (The entry sentinel must still be
**near-stdlib and dumb** so it opens even when `gz` itself is the patient — but
there is no ferry flight to survive.)

### 5.1 When to ground
Squawk velocity is the instrument: a rising rate of GHIs / ARBs / insights
against the same subsystem — **and the operator's own fatigue and frustration,
which is a real sensor.** This call is the **operator's discretion, not an
automated threshold.** Instrumenting it now would be one more untrued tight lock;
we earn the threshold later, if ever.

### 5.2 The MX-mode cycle
Erect the hangar, close the door, and run the cycle:

1. **Enter** — teleport into MX mode on the **token rail** (`token-block-doctrine`
   / `lock_manager`), human-claimed and reasoned. Opens the **MX log** (a
   ledger-stamped record: reason, operator, timestamp). Most guards drop to
   advisory ("loose in the bay"); the **bright lines (§6) stay hard.**
2. **Diagnose** — run the gates, read the reds. **Inspection reveals the scope**
   (which is why we erect a *global* hangar first, not a pre-scoped one).
3. **Specify** — name the fixes and the parts they touch (ADRs / OBPIs / REQs);
   issue Airworthiness Directives as needed (§7).
4. **Prosecute** — apply the fixes (the Service Bulletins).
5. **Evaluate** — re-run the locks.
6. **Certify** — the operator-as-FAA signs (Gate 5).
7. **Log + exit** — the MX log records *all* fixes and which ADRs/OBPIs/REQs they
   affect; then roll out (§5.3).

### 5.3 Exit — roll out the door (the hard gate)
To return to revenue service, **re-run every lock fail-closed. You cannot roll
out dirty.** Exit *is* the torque-and-verify step. Anything still red at exit must
be either fixed or explicitly MEL'd with an (O)/(M) and a repair clock. Exit
couples to a handoff / register entry (ADR-0.0.41), and the MX log is its receipt.

---

## 6. Bright lines — never relax, even in the hangar

These are not "alignment" states to be trued. They are bright lines with no
legitimate reason to cross during repair. **A fair starting set (expected to
grow as we learn):**

- **Gate-5 authenticity** — no fabricated human attestation, ever (regulatory independence).
- **Secrets** — no secret reaches a commit.
- **Operator-PII** — the personal-email prohibition holds.
- **Ledger integrity** — the ledger stays append-only and parseable; the
  instruments must not lie.

---

## 7. Airworthiness Directives — superseding a prior design

The pain this section kills: gzkit fumbles when a later finding invalidates a
prior ADR, because it treats supersession as a sanctity-of-design crisis.

**Doctrine AND mechanism, tightly coupled — both, inseparably** *(operator
ruling: for a human, AD-as-doctrine alone could suffice; for a dogfooding agent
it cannot — naked doctrine is rationalized away, or faked as a facade).*

**The doctrine (the *why*):** issuing an AD against your own prior ADR is
**routine airworthiness management, not a failure.** Stop mourning superseded
designs. Aircraft types take ADs constantly; it is how a fleet stays airworthy.
This is the rationale for the shackle — it tells the agent *why* supersession is
sanctioned, so it is not rationalized into a crisis or a shortcut.

**The mechanism (the shackle):** a real **AD artifact** — not a doc that merely
*says* "AD issued." It is structurally distinguishable from a facade by what it
requires:

- The **Service Bulletin (SB)** = the corrective OBPI — the engineering fix,
  incorporated *by reference*.
- The **AD** = the mandate + deadline, naming the unsafe ADR, the corrective
  OBPI, and the compliance interval: "ADR-X has an unsafe condition; apply
  corrective OBPI-Y by `<interval>`." **Emergency AD** = before next flight
  (effectively grounded); **Standard AD** = a window.
- It is **issued by the regulator** (operator, Gate 5), rides the existing
  `gz obpi repudiate` + corrective-OBPI rails, and is discharged only when the
  corrective OBPI passes the MX-mode exit gate (§5.3). An AD that skips the
  regulator signature or the exit gate is a facade by construction.

The coupling is the point: doctrine without mechanism gets vibed; mechanism
without doctrine gets cargo-culted. **Ship both or neither.**

---

## 8. Chores — scheduled line maintenance

Chores are the **walk-around + procedure-flow + checklist** — routine line
maintenance, and the inspection-interval cadence. The habit: **a chore run
between completed ADRs** (i.e. at each release).

A grounded or limping airframe starves this cadence. gzkit has been out of both
the chore cadence and the patch-release cadence for ~60 days because it has been
too un-airworthy to fly the normal rhythm. **Restoring the cadence is itself a
sign of returned airworthiness:** when chores-between-ADRs and patch-releases
resume, the aircraft is flying the line again.

---

We true the design with this doc *first*, but — per the Second Maxim — the
doctrine does not ship alone and then wait. **MX mode (the mechanism) is the
coupled Phase-1 build**, because a doctrine left naked is precisely the gap an
agent fills with a facade.

- **Phase 1 (now):** this doctrine **+ its coupled mechanism** — MX mode (the
  teleport hangar: enter → diagnose → specify → prosecute → evaluate → certify →
  log → exit), the MX log on the existing ledger / token rail, and the exit hard
  gate. Doctrine and mechanism land together.
- **Phase 2:** formalize **MEL-on-the-line** (waivers → real
  dispatch-with-limitation carrying (O)/(M) + an A/B/C/D clock); **split CDL**
  from MEL when their mitigations diverge; the **AD artifact** (§7) as a
  first-class, regulator-issued mandate.
- **Phase 3:** typed, scoped checks (A/B/C/D heavy-check analogues); instrumented
  squawk-velocity grounding *only if* observed patterns justify the threshold;
  the governance-doc-type taxonomy (§1.2) as its own doctrine with every doc tagged.

> "Do not build ahead of need" still governs *scope* (no MEL maturity, no scoped
> checks, no auto-grounding until earned) — but it never licenses shipping
> doctrine without its shackle.

---

> **Glossary of mappings** — MMEL: core deferral baseline (in the wheel) · MEL:
> project deferral policy (stricter-only) · CDL: missing-artifact deferral ·
> (O): runtime mitigation · (M): structural safing/placard · AD: mandate+deadline
> for a corrective · SB: the corrective OBPI · squawk: GHI/ARB/insight · flight:
> agentic SDLC use · release: ADR completion + validation · hangar: maintenance
> mode · bright line: never-relaxed lock.
