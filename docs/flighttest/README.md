# gzkit Flight-Test Program

> **Purpose:** A repeatable, target-agnostic methodology for proving gzkit's
> governance *design* under real execution — and for harvesting the design
> feedback that proof generates. This document specifies **how to fly**, not
> **what to fly against**. The substrate is chosen separately (§7).

**Program files**

| File | Contents |
|---|---|
| `README.md` (this file) | Charter — doctrine, roles, terminology, squawks, substrate criteria, feedback loop |
| [`flight-card-template.md`](flight-card-template.md) | The reusable sortie flight-card template |
| [`manifest.md`](manifest.md) | The sortie manifest + all-systems coverage matrix |

---

## 1. What this is — and what it is not

A **sortie** is one flight flown in a single sitting, from one pre-registered
**flight card**, chaining many **test points** end-to-end against a live
substrate, with the ledger and receipts as the flight-data recorder.

This program exists because gzkit is a *governance* system whose correctness is
behavioral: you cannot prove it by reading it. You prove it by flying its
workflows and reading the black box afterward. And because gzkit's central
design claim is that artifacts **chain** — each gating the next — a sortie flies
the whole chain in one sitting. Testing the links individually would never test
the chain.

| This program IS | This program is NOT |
|---|---|
| A methodology to **prove design** under execution | A unit-test suite (that is `gz test`) |
| A generator of **design feedback** (squawks feed back into gzkit) | A pass/fail scoreboard |
| **Target-agnostic** — flies against any qualifying substrate | Coupled to any one project |
| Evidence-first: the **ledger is truth** | Narrative-first: "it worked when I ran it" |

**The primary product of a sortie is data, not a green checkmark.** A sortie
that surfaces an anomaly has *succeeded* — it found a design gap before release.
A sortie that "passes" but records no evidence has *failed*, regardless of how
it felt.

---

## 2. Doctrine (binding on every sortie)

These five rules are what separate a flight test from a demo.

1. **Pre-register the falsifier.** Before a sortie begins, its card states the
   exact ledger events, receipts, and `gz` state assertions that constitute a
   pass, and the observations that constitute a failure. Declaring success
   *after* reading the output is the flight-test face of vibing — structurally
   forbidden. (Mirrors the airlock-in "pre-register the falsifier" discipline.)
2. **The black box is truth.** A pass is proven from Layer-2
   (`.gzkit/ledger.jsonl`) and receipts, never from an agent's prose or from
   Layer-3 derived views (`gz status`, reconciliation caches). Frontmatter
   `status: Completed` is not evidence of anything.
3. **Build up the envelope.** Fly the benign center first (the canonical spine),
   then expand to the loops, then to the adversarial corners. Never open a
   sortie at the corner of the envelope. Each sortie earns the next.
4. **Fly the design, not around it.** A test point executes its workflow through
   the **governed path** (the matching skill / `gz` verb), never via
   hand-authored marker files, direct ledger writes, or `--no-verify`. If the
   governed path blocks the flight, the block is a data point — write it up, do
   not defeat it.
5. **Independent observation.** A sortie's pass is confirmed by a **Chase** that
   did not fly it (a `spec-reviewer` / `quality-reviewer` subagent, or the
   operator), reading the black box cold. The pilot does not grade their own
   landing.

---

## 3. Roles

| Role | Aviation analog | Who | Responsibility |
|---|---|---|---|
| **Test director** | Program authority | Operator (human) | Authorizes each sortie; owns go/no-go; witnesses Gate-5 attestations; rules on squawk disposition |
| **Flight-test engineer** | FTE | Agent (main session) | Authors flight cards, flies the sortie through governed paths, reads the black box, drafts debriefs |
| **Chase** | Chase plane / independent observer | Reviewer subagent | Confirms the pass from evidence alone; never flew the sortie |
| **Flight-data recorder** | Black box | `.gzkit/ledger.jsonl` + receipts | Records what actually happened; the sole source of pass/fail truth |

The Test director *rules*; the FTE *advises and flies*. The agent never
self-attests a completion — the same operator-authority contract as the rest of
gzkit.

---

## 4. Terminology

| Term | Meaning |
|---|---|
| **Sortie** | The unit of execution: one flight flown in a single sitting, from one card, chaining test points end-to-end |
| **Test point** | One maneuver — a `gz` invocation exercising one system — with an expected observable |
| **Flight card** | The pre-registered plan + falsifier for one sortie. Template: [`flight-card-template.md`](flight-card-template.md) |
| **Squawk** | An observed divergence from the card; the program's yield (§5) |
| **Black box** | The ledger + receipts; the sole pass/fail truth |
| **Envelope expansion** | Flying benign → loops → adversarial, in build-up order |
| **Chase** | An independent observer that confirms a pass from evidence alone |

Every sortie is flown from a card authored **before** the flight and frozen at
go. The card *is* the pre-registered falsifier. A test point that produces an
*unexpected* observable is a squawk, not a silent fail.

---

## 5. Squawks, evidence, and disposition

**Pass/fail is computed from the black box, by the Chase, against the card's
pre-registered falsifiers — never narrated.** The FTE presents evidence (ledger
slices, receipt IDs, `gz state` output) *before* claiming an outcome.

A **squawk** is any observed behavior that diverges from the card. Squawks are
the program's yield and are dispositioned, never discarded:

| Squawk class | Disposition |
|---|---|
| gzkit behaved incorrectly (defect) | File a GHI via `/ghi-author`; route per defect-fix thresholds |
| gzkit behaved correctly but the *design* is wrong/unclear | Log as **design feedback** (§8) — this is the point of the program |
| The card was wrong (bad falsifier) | Amend the card; re-fly |
| Substrate-specific noise | Note and move on; does not gate the sortie |

An **untracked squawk is a nonexistent squawk.** Every anomaly gets a GHI, a
feedback entry, or an explicit card amendment.

---

## 6. Manifest

The sortie manifest is the **coverage contract** — it must span every gzkit
system (§ *all systems*). See [`manifest.md`](manifest.md) for the full sortie
list, per-sortie test points, and the systems→sortie coverage matrix.

Summary (build-up order):

| Sortie | Envelope | Proves |
|---|---|---|
| **S1 — Cold Start & Spine** | Center | The full canonical chain: `gz init` → PRD → Constitution → ADR → OBPI → implement → Gate-5 attest → closeout → sync |
| **S2 — Promotion & Decomposition** | Center-out | Pool→promote, the decomposition matrix, the contract-bearing OBPI pipeline, traceability |
| **S3 — Defect & Issue Loops** | Expansion | GHI author/close/triage, defect-fix routing, brief & OBPI reconcile, simplify |
| **S4 — Integrity & Adversarial** | Corner | Repudiate, withdraw, hook fail-closed, Layer-3≠truth, invariant coherence, corpus round-trip, validator sweep |
| **S5 — Quality & Maintenance** | Expansion | `gz check`, ARB, complexity, pythonic patterns, tech-debt, evaluate, tidy, mx hangar |
| **S6 — Release & Continuity** | Center-out | Release ceremony, `gh` release, session-handoff create/resume, context load |

A gzkit system not reachable by any sortie is untested design surface — adding
it to the manifest is how coverage grows.

---

## 7. Choosing a substrate (target selection)

The program is target-agnostic. A flight substrate is selected per campaign
against these criteria — the substrate is *scaffolding for the flights*, and its
domain must never become the thing under test:

1. **Boring & bounded.** A small, teachable domain so the sorties exercise
   gzkit's machinery, not accidental complexity in the subject.
2. **Real-buildable.** Each test point's ADR/OBPI can deliver a genuine, working
   slice — the substrate ends the program as real software, so the spine is
   proven on real change rather than synthetic motion.
3. **Greenfield or near-cold.** So Sortie 1 can prove the *cold start* rather
   than retrofitting governance.
4. **Separate repo from gzkit.** Keeps the prover and the proven-against
   isolated; gzkit's own ledger never contaminates flight evidence.

The chosen substrate and its build-order payload are recorded in the campaign's
flight log, not here.

---

## 8. The feedback loop (why this exists)

The program closes on **design feedback**, not on a passed manifest. After each
sortie the FTE drafts a debrief; the Test director rules on it:

1. **Debrief** — what the black box showed vs. what the card predicted.
2. **Design signal** — did the workflow's *design* prove sound, awkward, or
   wrong under real execution? Awkward-but-correct is still signal.
3. **Route the signal** — defect → GHI; design gap → the owning ADR as a
   correction (per the operator's *correction-vs-enhancement* doctrine: a gap
   between shipped surface and declared intent is a correction, not an
   enhancement); doctrine gap → the corpus.
4. **Re-fly on change** — any gzkit design change prompted by a sortie re-opens
   the affected sortie so the fix is itself proven.

A sortie is *complete* when its debrief is ruled on and its squawks are tracked
— not when it "passes."
