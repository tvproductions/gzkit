# gzkit Flight-Test Program

> **Purpose:** A repeatable, target-agnostic methodology for proving gzkit's
> governance *design* under real execution — and for harvesting the design
> feedback that proof generates. This document specifies **how to fly**, not
> **what to fly against**. The substrate is chosen separately (§7).

---

## 1. What this is — and what it is not

A **flight test** is one end-to-end execution of a gzkit workflow against a
live substrate, flown from a **pre-registered flight card**, with the ledger
and receipts as the flight-data recorder.

This program exists because gzkit is a *governance* system whose correctness is
behavioral: you cannot prove it by reading it. You prove it by flying its
workflows and reading the black box afterward.

| This program IS | This program is NOT |
|---|---|
| A methodology to **prove design** under execution | A unit-test suite (that is `gz test`) |
| A generator of **design feedback** (squawks feed back into gzkit) | A pass/fail scoreboard |
| **Target-agnostic** — flies against any qualifying substrate | Coupled to any one project |
| Evidence-first: the **ledger is truth** | Narrative-first: "it worked when I ran it" |

**The primary product of a flight is data, not a green checkmark.** A flight
that surfaces an anomaly has *succeeded* — it found a design gap before release.
A flight that "passes" but records no evidence has *failed*, regardless of how
it felt.

---

## 2. Doctrine (binding on every flight)

These five rules are non-negotiable and are what separate a flight test from a
demo.

1. **Pre-register the falsifier.** Before a flight begins, its card states the
   exact ledger events, receipts, and `gz` state assertions that constitute a
   pass, and the observations that constitute a failure. Declaring success
   *after* reading the output is the flight-test face of vibing — structurally
   forbidden. (Mirrors the airlock-in "pre-register the falsifier" discipline.)
2. **The black box is truth.** A pass is proven from Layer-2 (`.gzkit/ledger.jsonl`)
   and receipts, never from an agent's prose or from Layer-3 derived views
   (`gz status`, reconciliation caches). Frontmatter `status: Completed` is not
   evidence of anything.
3. **Build up the envelope.** Fly the benign center first (the happy-path
   spine), then expand outward to the loops, then to the adversarial corners.
   Never open a flight at the corner of the envelope. Each series earns the
   next.
4. **Fly the design, not around it.** A flight executes the workflow through its
   **governed path** (the matching skill / `gz` verb), never via hand-authored
   marker files, direct ledger writes, or `--no-verify`. If the governed path
   blocks the flight, the block is a data point — write it up, do not defeat it.
5. **Independent observation.** A flight's pass is confirmed by an observer that
   did not fly it (a `spec-reviewer` / `quality-reviewer` subagent, or the
   operator), reading the black box cold. The pilot does not grade their own
   landing.

---

## 3. Roles

| Role | Aviation analog | Who | Responsibility |
|---|---|---|---|
| **Test director** | Program authority | Operator (human) | Authorizes each flight; owns go/no-go; witnesses Gate-5 attestations; rules on squawk disposition |
| **Flight-test engineer** | FTE | Agent (main session) | Authors flight cards, flies the sortie through governed paths, reads the black box, drafts debriefs |
| **Chase** | Chase plane / independent observer | Reviewer subagent | Confirms the pass from evidence alone; never flew the sortie |
| **Flight-data recorder** | Black box | `.gzkit/ledger.jsonl` + receipts | Records what actually happened; the sole source of pass/fail truth |

The Test director *rules*; the FTE *advises and flies*. This is the same
operator-authority contract as the rest of gzkit: the agent never self-attests a
completion.

---

## 4. Anatomy of a flight — the flight card

Every flight is flown from a card authored **before** the flight and frozen at
go. The card is the pre-registered falsifier. Template:

```
FLIGHT <SERIES><N> — <short name>
─────────────────────────────────────────────
WORKFLOW UNDER TEST : <the gzkit workflow this sortie proves>
DESIGN CLAIM        : <the one-sentence design property we assert holds>
GOVERNED PATH       : <skill / gz verbs that MUST carry the flight>

ENTRY CONDITIONS (go/no-go)
  - <state the substrate must be in before the flight opens>
  - <prior flights that must have passed>

TEST POINTS (the maneuvers, in order)
  1. <gz invocation>            → expect <observable>
  2. <gz invocation>            → expect <observable>
  ...

INSTRUMENTATION (what the black box must record for a PASS)
  - ledger: <event kinds / count / fields that must appear>
  - receipts: <receipt name prefixes that must be emitted>
  - state: <gz state / gz status assertions>

PRE-REGISTERED FALSIFIERS (any one ⇒ FAIL)
  - <observation that proves the design claim is false>
  - <missing evidence that proves the workflow did not hold>

ABORT CRITERIA
  - <condition under which the flight is halted rather than failed>

DEBRIEF CAPTURE
  - squawks: <where anomalies are logged>
  - feedback: <what design signal this flight feeds back>
```

A test point that produces an *unexpected* observable is a **squawk**, not a
silent fail — see §6.

---

## 5. The flight manifest (build-up order)

Full coverage of gzkit's main workflows — the canonical spine plus the
auxiliary and integrity loops — sequenced as an envelope expansion. Each flight
names the design claim it proves. Later series depend on earlier ones.

### Series A — Cold start & canonical spine *(envelope center — benign)*

| Flight | Workflow under test | Design claim proven |
|---|---|---|
| **A1** | `gz init` cold start | A virgin repo materializes byte-equivalent canonical surfaces; distribution invariant holds |
| **A2** | PRD authoring | Project intent is captured as a linked, first-class artifact |
| **A3** | Constitution | Constitution artifact anchors downstream lineage |
| **A4** | ADR authoring & booking | `kind`/`lane`/`semver` consistency + taxonomy validation are enforced at authoring time |
| **A5** | OBPI decomposition | ADR checklist ↔ OBPI briefs stay 1:1; REQ kinds (BEHAVIOR/SUPPORT/STRUCTURAL-FENCE) are disciplined |
| **A6** | Implementation increment | Gate 2 tests + REQ-coverage gate hold before completion |
| **A7** | Gate progression & Gate-5 attestation | Gates 1–5 fire correctly; human attestation via `--attestation-text` IS Gate 5 |
| **A8** | ADR closeout ceremony | An ADR closes only with the full attested gate chain recorded to the ledger |

### Series B — Auxiliary loops *(envelope expansion)*

| Flight | Workflow under test | Design claim proven |
|---|---|---|
| **B1** | GHI direct-fix | A tracked defect routes to `fix(<scope>): … (GHI #N)` and closes citing its SHA — no ceremony inflation |
| **B2** | Defect-fix routing | The routing thresholds mechanically choose direct-fix vs OBPI, not intuition |
| **B3** | Brief reconcile | Induced brief drift is detected and amended under attestation |
| **B4** | Release ceremony | A version bump becomes a released `gh` artifact; no version left unreleased |
| **B5** | Guarded git-sync | `gz git-sync --apply --lint --test` lands a clean tree only with gates green |

### Series C — Integrity & adversarial corners *(corner of the envelope)*

| Flight | Workflow under test | Design claim proven |
|---|---|---|
| **C1** | Repudiate | A fraudulent/mistaken Gate-5 is reversed without retiring the OBPI; history preserved, re-completable |
| **C2** | Withdraw | A superseded/phantom OBPI is permanently retired and hidden from roll-ups |
| **C3** | Hook-block integrity | A bypass attempt (drifted commit / `--no-verify`) **fails closed** and cannot be worked around |
| **C4** | Layer-3 ≠ truth | A desynced derived view is caught fail-closed by `gz validate` and regenerated from canon |
| **C5** | Invariant coherence | A mutated rendered surface is caught against its corpus source of truth |

> The manifest is the coverage contract. A workflow gzkit ships that is not on
> this manifest is untested design surface — adding it here is how coverage
> grows.

---

## 6. Evidence, squawks, and disposition

**Pass/fail is computed from the black box, by the Chase, against the card's
pre-registered falsifiers — never narrated.** The FTE presents evidence
(ledger slices, receipt IDs, `gz state` output) *before* claiming an outcome.

A **squawk** is any observed behavior that diverges from the card. Squawks are
the program's yield and are dispositioned, never discarded:

| Squawk class | Disposition |
|---|---|
| gzkit behaved incorrectly (defect) | File a GHI via `/ghi-author`; route per defect-fix thresholds |
| gzkit behaved correctly but the *design* is wrong/unclear | Log as **design feedback** (§7) — this is the point of the program |
| The card was wrong (bad falsifier) | Amend the card; re-fly |
| Substrate-specific noise | Note and move on; does not gate the flight |

An **untracked squawk is a nonexistent squawk.** Every anomaly gets a GHI, a
feedback entry, or an explicit card amendment.

---

## 7. Choosing a substrate (target selection)

The program is target-agnostic. A flight substrate is selected per campaign
against these criteria — the substrate is *scaffolding for the flights*, and its
domain must never become the thing under test:

1. **Boring & bounded.** A small, teachable domain so the flights exercise
   gzkit's machinery, not accidental complexity in the subject.
2. **Real-buildable.** Each flight's ADR/OBPI can deliver a genuine, working
   slice — the substrate ends the program as real software, so the spine is
   proven on real change rather than synthetic motion.
3. **Greenfield or near-cold.** So Flight A1 can prove the *cold start* rather
   than retrofitting governance.
4. **Separate repo from gzkit.** Keeps the prover and the proven-against
   isolated; gzkit's own ledger never contaminates flight evidence.

The chosen substrate and its build-order payload are recorded in the campaign's
flight log, not here.

---

## 8. The feedback loop (why this exists)

The program closes on **design feedback**, not on a passed manifest. After each
flight the FTE drafts a debrief; the Test director rules on it:

1. **Debrief** — what the black box showed vs. what the card predicted.
2. **Design signal** — did the workflow's *design* prove sound, awkward, or
   wrong under real execution? Awkward-but-correct is still signal.
3. **Route the signal** — defect → GHI; design gap → the owning ADR as a
   correction (per the operator's *correction-vs-enhancement* doctrine: a gap
   between shipped surface and declared intent is a correction, not an
   enhancement); doctrine gap → the corpus.
4. **Re-fly on change** — any gzkit design change prompted by a flight re-opens
   the affected flight so the fix is itself proven.

A flight is *complete* when its debrief is ruled on and its squawks are tracked
— not when it "passes."

---

## Appendix — one-line glossary

- **Flight** — one end-to-end execution of a gzkit workflow against the substrate.
- **Flight card** — the pre-registered plan + falsifier for one flight (§4).
- **Test point** — one maneuver (`gz` invocation) with an expected observable.
- **Squawk** — an observed divergence from the card; the program's yield (§6).
- **Black box** — the ledger + receipts; the sole pass/fail truth.
- **Envelope expansion** — flying benign → loops → adversarial, in build-up order.
- **Chase** — an independent observer that confirms a pass from evidence alone.
