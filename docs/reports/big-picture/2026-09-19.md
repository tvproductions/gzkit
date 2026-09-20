# gzkit — Big-Picture Assessment

**Date:** 2026-09-19 · **Report:** baseline (first in the `big-picture` series)
**Evidence cutoff:** 2026-09-19, `main` at `85c857263`, working tree clean
**Comparison points:** the project's own *State of gzkit* reckoning (2026-06-20)
and the campaign re-cut of 2026-08-17. No prior report in this series exists.

---

## The assessment

Eight months in, gzkit has built the thing it set out to build, and has not yet
shown that it works for anyone but itself.

The verification substrate is real and it bites. 10,539 unit tests pass in 96
seconds. All 62 registered quality checks pass today. The specific failure the
project's June reckoning called its worst — two integrity gates that warned
instead of blocking, with tests that certified the warning — is repaired; I
confirmed it by resolving the live enforcement posture rather than reading the
claim, and both now return `BLOCK_GHI_FIX`, fail-closed. Twice during this
assessment a project hook refused one of my own shell commands, named the binding
rule, and printed the corrected command. That is enforcement observed rather than
asserted, and it is rarer than it sounds.

Against that, three numbers describe the last seven weeks better than any
narrative. The governing campaign has not checked a box since **2026-08-08**. The
open issue queue has gone **9 → 32 → 55** since mid-August while issues close at a
median age of **3.7 hours**. And **453 commits** sit unreleased since v0.34.7,
of which 197 are `fix` and 9 are `feat`.

Those are not the marks of a stalled project. They are the marks of a project in
a **defect-absorption equilibrium**: producing self-knowledge and repairs faster
than it produces governed capability, with a queue that grows despite being
drained within hours. The constraint is not repair latency. It is that
self-inspection generates real findings faster than they can be discharged, and
gzkit has no consumer but its own construction to arbitrate which findings
matter.

The operator reached this conclusion first, on 2026-09-15, and the campaign
records it verbatim:

> *"the rate at which new GHIs grow in gzkit far outstretches getting any feature
> work done. this is dismaying."*

This report's contribution is not that observation. It is the measurement behind
it, and the argument that the dynamic is structural rather than a matter of
diligence — more diligence makes it worse, because every inspection pass finds
real defects. The campaign already names the escape: an external forcing
function. That remedy is currently sequenced last, and costs about a quarter.

---

## What is being built, and why it would be worth something

gzkit is a governance meta-harness. It does not run agents; it wraps the
harnesses that do — Claude Code, Codex, Copilot — with deterministic governance
surfaces, evidence capture, gate enforcement, and human attestation.

The README frames the problem as a mismatch between context-bound agents and
unscalable human judgment. The PRD frames it more sharply, and more usefully, as
a problem about the human:

> "AI-assisted development creates a drift problem: humans approve work they
> didn't verify, attest to artifacts they didn't read, and gradually become
> rubber stamps for agent-generated output."

That is the value proposition, and it is a real one. It is also unusually hard to
demonstrate, because the thing being prevented is a slow decay in a person's
engagement with their own codebase — not something a sprint can A/B test. The
project's answer is to make the decay structurally impossible rather than merely
discouraged: every completion claim witnessed by a ledger event, every "enforced"
claim backed by a live negative control that constructs a real violation and
proves the gate fails on it, and no agent permitted to attest on a human's
behalf.

Each mechanism carries its own causal claim:

| Mechanism | The claim it makes |
|---|---|
| Append-only ledger (L2) | Runtime truth must be witnessed, not asserted — frontmatter is a lazy mirror, the ledger wins |
| ADR → OBPI → REQ | Intent decomposed to a unit small enough that completion is *provable*, with a declared path allowlist so scope creep is mechanically visible |
| Five gates | Verification staged and non-skippable, because a single end-of-work check is exactly where rubber-stamping happens |
| Human attestation | At closeout the agent becomes a passive presenter — paths and commands only, never outcomes or summaries |
| Corpus → rendition | A hand-edited control surface is the same failure class as a hand-written ledger row, so the per-turn agent surface is deterministic playback of an append-only corpus |
| Airlock | An agent cannot hold a complex system resident, so hand it a bounded seam-set on entry and make it account for exactly that set on exit |

The architecture is coherent; each layer answers a question the layer below
cannot. That coherence is the asset, and it is why the project deserves continued
attention.

---

## What is actually delivered

This is a real, released product, which is easy to lose sight of from inside the
governance record.

- **56 releases on PyPI** as `py-gzkit`, first 2026-03-22, latest `0.34.7` on
  2026-08-29, published through GitHub trusted publishing on tag. 574 downloads
  last month.
- **A frozen distribution contract**: 240 canonical surfaces the wheel must
  deliver to a fresh adopter, enforced in both directions.
- **A substantial verification surface**: 97 registered validator scopes, 62
  checks in `gz check`, 467 BDD scenarios, 5,359 `@covers` annotations binding
  tests to 1,971 distinct requirements, 65.8% REQ coverage (1,794 / 2,728), 88%
  line coverage.
- **A genuinely queryable governance record**: 16,970 ledger events across 66
  event types, every one written through a governed verb.
- **Five feature ADRs closed and released** between 2026-06-29 and 2026-07-31
  (`0.30.0` through `0.34.0`), 27 OBPIs attested complete.

The most adopter-relevant work of the whole period is release `v0.34.6`
(2026-08-29): gzkit discovering that its own first hour was broken in nine
distinct ways — a scaffold failing its own surface gate with 58 missing files,
rules scoped to gzkit's directory layout so an adopter's first audit reported
findings about gzkit rather than themselves, and the maintainer's personal name
in 92 `--help` examples. Finding and fixing that is exactly the right work. That
it was found in month eight by inspection, rather than by an adopter complaining,
is the point this report keeps returning to.

---

## The quarter: one thing repaired, one thing widened

The June 2026 reckoning — commissioned with the words *"gzkit is in utter
shambles, totally off the rails"* — named three headline problems. Their status
today, measured rather than relayed:

| June 2026 finding | Today | Verdict |
|---|---|---|
| Two corpus→rendition integrity gates inert by default; tests certify the inertness | Both resolve `BLOCK_GHI_FIX`, `fail_closed=True` | **Repaired** (verified live) |
| A hollow "antibody" audit passed Gate 5 on a green self-check | Enforcement-claim meta-validator built; a later hand audit found 32 of 47 claims still under-scoped or trivial while `gz check` reported 47/47 | **Partly repaired, honestly disclosed** |
| Measurable accretion: 33 oversized modules, 70 validate scopes, 10,913 ledger events, 116 handoffs, a 1,589-line campaign | 66 oversized modules, 97 scopes, 16,970 events, 740 handoffs, a 1,923-line campaign | **Widened, roughly 2×** |

The first row is a genuine win and should be read as one. The third is the
concern, and it needs care, because "the codebase grew" is not by itself a
finding. What makes it one is that reduction is a *declared pre-1.0 Movement* —
the project ruled in July that accretion was what blocked 1.0 and moved reduction
ahead of post-1.0 — and the measured surface has roughly doubled since.

One instance shows the shape of the problem rather than a moral about size. The
module-size debt list reads empty today. It was emptied on 2026-08-26 not by
shrinking modules but by moving the block threshold from the corpus p95 (1,032
SLOC) to p99 (3,144), after which every remaining entry fell under the new band
and surrendered under the shrink-only rule. Eight modules still sit above the
retired band. Nothing is in violation, the move was operator-ratified and
recorded, and the ratchet worked as designed. But the number that says "debt:
zero" now means something different from what it meant in July, and only the
dated history inside the JSON says so.

---

## What the architecture reveals

Three readings, in descending order of confidence.

### 1. The work migrated to the cheapest governed channel

Start with the throughput numbers, because they are widely misread and the
correction matters.

OBPI completions per month fell from 306 in March to 4 in September. Over the
same period commit volume hit its all-time high (727 in August). September's
commit mix is 185 `fix` and 170 `chore` against 7 `feat`. ADR-level gate checks
and attestations both stop on 2026-07-31.

The naive reading — "delivery collapsed" — is wrong, and the arithmetic says so.
During the active `ADR-0.35.0` window (2026-08-21 → 2026-09-12) the project
completed 7 OBPIs in 22 days: **3.7 calendar days each**, against the campaign's
own planning assumption of 3.8. When the pipeline runs, it runs at precisely the
rate the plan assumes. The ADR-level gates stopped firing because no ADR has
reached *closeout* since `0.34.0`, not because gates broke.

So the finding is duty cycle, not rate. There was a 20-day gap with zero
completions (2026-07-31 → 2026-08-21) and a 10-day gap inside the active window.
Meanwhile 1,071 commits reference a GHI, 481 of them in the last two months, and
1,001 of the project's 1,061 issues are closed at a **median age of 0.154 days**,
with **71.2% closed the same day they are opened**.

The campaign's own 2026-09-15 amendment supplies the causal step, and it is the
right one:

> "That amendment raised the family-closure box because it is *'drawable without
> the operator'*. Every session could draw it, and **GHI repair was the cheapest
> arm to draw.**"

Doctrine authorizes GHI-routed direct repair without an ADR, without operator
initiation, without gates, and without attestation. It is the cheapest governed
channel; the work is real; it absorbs the available session time. The structural
consequence is the part worth holding onto: **the channel that absorbs most of
the work is the one channel that does not exercise the ADR → OBPI → gate →
attestation spine the product exists to sell.** The spine gets less exercise as
the project matures — the opposite of what a system needs before asking anyone
else to adopt it.

Two further measurements make this an equilibrium rather than a phase. First, the
open queue is *growing* despite the 3.7-hour median close: 9 in mid-August, 32 on
2026-09-02, **55 today**, of which 93% are labelled `defect`. Second, the
project's own insight store shows self-observed defects quadrupling — 17 in July,
26 in August, **67 in the first 19 days of September** — inside a record 208
entries for the month. More inspection produces more real findings, which
produces more cheapest-channel repair, which consumes the sessions that would
otherwise run a pipeline.

That is a system-dynamics problem, not a diligence problem. Diligence is what
drives it.

### 2. The witnesses are strong artifact-to-artifact and absent prose-to-code

The project's dominant recurring defect has a name and a definition: *"Layer X
declares a discipline that Layer X does not mechanically enforce."* Its two
deepest recurrence chains in the entire corpus — depth 12 and depth 7 — are both
this family, and in a 2026-09-02 measurement 19 of 32 open issues belonged to it.
Instances close same-session; the class keeps producing.

The reason is stated by the project itself, in the most load-bearing sentence in
the campaign:

> "gzkit's witnesses compare **artifact↔artifact** and **claim↔receipt**
> exhaustively and **doctrine↔code** not at all… A general doctrine↔code witness
> is NOT built and is not scheduled here. The honest statement of the residual:
> gzkit does not today know how to mechanize 'this prose binds that code.'"

This is why the family is generative rather than finite. Every new doctrine
document is a new unwitnessed claim, and doctrine is the surface growing fastest:
22.3 MB of markdown under `docs/` against 6.3 MB of Python under `src/`. The
recursion is visible in the governance scorecard — of 71 rows scored
"Mechanical," **64 are frozen on a shrink-ratchet as unwitnessed**, because the
claim that a row is mechanically enforced was itself unwitnessed doctrine until a
ruling in August forced it into a register. The instrument that measures
mechanism had no mechanism. To the project's credit that is now tracked,
shrink-only debt with a number on it rather than an assumption.

The project draws the right comparison itself: the one family measurably
*closing* — layer drift, 10 → 7 → 6 → 1 across May to August — closed because it
got three things: a doctrine, a regenerator, and a fail-close. The doctrine
family has the first two at best.

### 3. A well-designed mechanism can be vacuously open

The airlock is the clearest single instance, and it is instructive because the
design is sound and the *input set* is empty. Across 71 transits the ledger
records 53 `proceed` decisions, and **every one of the 53 computed an empty
seam-map**. All 18 `hold` decisions have non-empty maps (2 to 21 seams). The root
cause is prosaic: no caller passes `parent_invariants`, and a leaf OBPI has no
transitive dependents, so both edge sets return empty — and a fail-closed
decision over an empty input is vacuously open.

The trajectory here is genuinely improving and deserves credit. September
transits tripled to 34, the entry/exit accounting gap narrowed sharply (July 23
in / 5 out; September 34 in / 22 out), and the bite rate rose from 13% to 25%.
The repair is designed: `ADR-0.37.0` exists precisely for this, and its first
proposed fix was *withdrawn on its own measurement* when it turned out to convert
an empty seam-map into a constant one. That withdrawal is a good sign about the
project's epistemics. But `ADR-0.37.0` was authored 36 days ago and has 6 OBPIs
at 0% REQ coverage. Nothing is built.

The same holds one ADR over: `ADR-0.36.0`, authored 41 days ago, carries 9
fully-drafted briefs and has landed nothing.

---

## The central uncertainty

Everything above is second-order next to one question: **does this work for
anyone who is not building it?**

The evidence is thin, and the project knows it.

- **Flight tests: 0 of 6 sorties flown.** The manifest, templates, and skill
  exist; there is no flight log, no sortie record, no ledger event. The project
  states this itself in two separate documents.
- **`rhea`**, the named proving ground: real, bootstrapped from the published
  wheel (`py-gzkit>=0.34.1`), 13 working sessions, 12 numbered defects filed back
  — then stopped. 20 ledger events total, **0 OBPIs ever completed**, no
  attestation ever recorded, last commit 2026-07-26. Its findings were never
  routed back into gzkit's governance record.
- **One genuine external adopter event**: a private repository filed GHI #607
  from inside itself in June running `gz v0.28.1` — an opinionated Pydantic rule
  leaking across the adopter boundary and failing their pre-existing dataclasses.
  Fixed. That repository has been dormant since July.
- **Community signal**: 9 stars, 0 forks, and all 1,056 issues ever opened have
  exactly one author.
- **Evaluations**: numerous, recent, methodologically careful, and including
  several that return honest negatives which are then acted on. But every subject
  is gzkit itself, a synthetic fixture, or a fresh agent reading gzkit's own
  instructions. **No evaluation measures a real operator outcome in an adopting
  project.**

The sequencing is the crux. External validation is a declared 1.0 gate, carried
by `ADR-0.38.0`, which by operator ruling cannot be authored until `0.35.0`,
`0.36.0`, and `0.37.0` land. That is 21 remaining OBPIs (6 + 9 + 6). At the
observed active rate of 3.7 days each that is roughly 78 days of pipeline time;
at the observed 60-day calendar rate of 6.0 days each, roughly 126 calendar days.
Either way the first external signal arrives no earlier than Q1 2027 — consistent
with the declared ≈2027-04 target. **The plan is not lying to itself about the
date.**

But it means roughly 21 more governed increments will be built on internal
judgment before anything outside the project pushes back. The campaign states
this cost on the record: the forcing function *"certifies rather than informs."*
That is a defensible choice, deliberately made and recorded. It is also the
single largest risk in the portfolio, because every interim design decision goes
unfalsified by contact with a different substrate — and the one time gzkit did
meet a different substrate, the finding was a category of mistake that five
months of self-inspection had not surfaced.

There is a second-order cost worth naming. The campaign is now a 1,923-line
document in its fifth edition, carrying 28 amendments of which only four record a
box being checked; the other 24 are sequencing rulings, count corrections, scope
expansions, and corrections of the plan's own prose. Of the ten amendments
written since the current edition was created on 2026-08-16, **none has checked a
box**. The plan says this about itself, at line 49: *"two amendments were spent
explaining that split rather than removing it."* Steering has become a work item
competing with the work.

---

## What would move this assessment

These are observations that would change the reading, in either direction — not
recommendations. Work selection is the operator's.

**Would strengthen it materially:** any completed governed unit of work in a
repository that is not gzkit — one OBPI, one attestation, one flight-test sortie.
A single such event resolves more uncertainty than another quarter of
self-inspection. Second: `ADR-0.37.0` landing, followed by a transit computing a
non-empty seam-map on a real OBPI, which would convert the airlock from designed
to operating.

**Would weaken it:** a further quarter in which the accretion figures grow while
Movement C stays open; the open queue holding above 55 through another
measurement; or `ADR-0.36.0` and `ADR-0.37.0` still at zero landed OBPIs at 90
days from authoring.

**Untested either way:** whether the covenant's central value claim — that this
prevents an operator's slow slide into rubber-stamping — is true. No instrument
in the repository measures it, and eight months of one operator's experience is a
sample of one who is also the author. That is not a criticism; it is the hardest
measurement in the project and nobody has solved it. But it should not be quietly
counted as demonstrated.

---

## In summary

The craft is not in doubt. Over eight months and 3,756 commits, one operator has
built a governance system with a verification substrate most funded teams never
achieve, and — more unusually — a standing habit of commissioning honest
diagnostics against itself and publishing the unflattering results. The June
reckoning, the enforcement-claim audit, the August architecture review, the
three-pillars evaluations that returned null and were acted on as null: these are
the behaviors of a project that wants to be right more than it wants to look
right. That is the asset that most justifies continued investment, and it is not
common.

The risk is equally clear, and the project named it first. A self-governing
system inspecting itself finds real defects forever, which is what makes the loop
seductive rather than obviously wasteful. The machine is now excellent at proving
things about itself and has never been asked to prove anything about anyone else.
The escape is already identified, already designed, and sequenced last.

---

## Evidence appendix

All figures observed 2026-09-19 against `main` at `85c857263` unless dated
otherwise. Where a document states a number, the JSON or command authority was
consulted instead and is named.

### Commands run for this report

| Observation | Source |
|---|---|
| 10,539 unit tests pass, 4 skipped, 96.2s | `uv run gz test` |
| All 62 registered checks pass, exit 0 | `uv run gz check` |
| REQ coverage 1,794 / 2,728 = 65.8% | `uv run gz covers` |
| `ADR-0.35.0` at 7/13 OBPIs, closeout BLOCKED on 6 briefs | `uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` |
| Rendition gates fail-closed (`BLOCK_GHI_FIX`) | `gzkit.mx.checkpoint.resolve` on `rendition-freshness`, `rendition-floor-coherence`, `invariant-coherence` |
| AGENTS.md 19,872 B against a 50,000 B budget | `uv run gz validate --instructions-files-budget`; authority `data/instructions_files_budget.json` |
| 56 PyPI releases, latest `0.34.7` 2026-08-29, 574 downloads/month | pypi.org and pypistats.org APIs |
| 55 open issues; 1,001 closed, median age 0.154 d, 71.2% same-day | `gh issue list` |
| 453 commits since `v0.34.7` — 197 `fix`, 183 `chore`, 52 `docs`, 9 `feat` | `git log v0.34.7..HEAD` |

### Ledger-derived (`.gzkit/ledger.jsonl`, 16,970 events, 2026-01-22 → 2026-09-20)

- OBPI completions are recorded as `obpi_receipt_emitted` with `receipt_event: "completed"` — 659 total. By month: Mar 306, Apr 109, May 134, Jun 74, Jul 28, Aug 3, Sep 4.
- Rate windows: last 30 d, 7 completions (4.3 d each); last 60 d, 10 (6.0 d); last 90 d, 59 (1.5 d). Active `ADR-0.35.0` window 2026-08-21 → 2026-09-12: 7 completions in 22 days = **3.7 d each**. Longest gap 20 days (2026-07-31 → 2026-08-21).
- `gate_checked` (943) and `attested` (103) both last fired 2026-07-31, at `ADR-0.34.0` closeout.
- Airlock: 71 `airlock_in`, 29 `airlock_out`; decisions 53 `proceed` / 18 `hold`. **All 53 proceeds carry an empty `unaccounted` set**; holds range 2–21 seams. Entries by month: Jul 23, Aug 14, Sep 34. Exits: Jul 5, Aug 2, Sep 22.
- `obpi_parked` 377 against `obpi_unparked` 6.
- `artifact_edited` 5,232 — the largest single event class.

### Repository scale

- 3,756 commits since 2026-01. By month: Mar 523, Apr 516, May 516, Jun 531, Jul 448, Aug 727, Sep 426.
- September commit mix: 185 `fix`, 170 `chore`, 52 `docs`, 7 `feat`. 1,071 commits reference a GHI; 481 in Aug–Sep.
- `src/gzkit`: 512 modules, 155,638 lines / 6.3 MB. Tests: 692 files, 226,823 lines / 9.6 MB. `docs/`: 1,761 markdown files / 22.3 MB. `.gzkit/`: 36 MB (15 MB ledger, 12 MB handoffs).
- 66 modules over 600 lines (largest `commands/content/unown.py`, 2,910). 73 skills, 26 rules, 74 feature files, 467 BDD scenarios, 740 handoffs, 972 booked rulings, 367 corpus entries, 205 pool ADRs.
- Feature ADR ages and landed counts: `0.35.0` authored 2026-07-21 (60 days, 7/13); `0.36.0` authored 2026-08-09 (41 days, 0/9); `0.37.0` authored 2026-08-14 (36 days, 0/6). Last feature ADR to reach `Validated`: `0.34.0`, 2026-07-31.
- Campaign: 1,923 lines, fifth edition, 7 of 25 boxes checked — all 7 between 2026-07-18 and 2026-08-08. 28 amendments, 4 recording work landing.
- Insights store: 784 entries (510 `improvement`, 158 `defect`, 84 `discovery`, 32 `defect-resolution`). By month: May 128, Jun 147, Jul 131, Aug 150, **Sep 208 in 19 days**. Defects by month: Jul 17, Aug 26, **Sep 67**.

### Document sources

- `docs/governance/state-of-gzkit-2026-06-20.md` — the June reckoning; source of the three compared findings and the June baselines.
- `docs/governance/build-to-1.0-campaign-2026-08-16.md` — governing plan. §1 identity and the self-consumption diagnosis; §5 the nine 1.0 gates and the ≈2027-04 target; the `doctrine-declared-without-mechanism` box and the doctrine↔code residual; the 2026-09-15 amendment quoted above at line 489.
- `docs/design/prd/PRD-GZKIT-1.0.0.md` — the rubber-stamp framing; status `Draft`.
- `README.md` — product framing and the meta-harness boundary.
- `docs/governance/enforcement-claim-nc-audit-2026-07-18.md` — 32 of 47 enforcement claims under-scoped or trivial while `gz check` reported 47/47.
- `docs/evals/gzkit-campaign-architecture-review-2026-08-17.md` — self-consumption finding and the August measured baseline.
- `docs/evals/three-pillars-*-2026-09-19/` — most recent evaluation set, including published null results.
- `docs/governance/external-proving-ground-note-2026-06-24.md` — names `rhea`; "Explicitly deferred."
- `data/mechanical_witness_grandfather.json` — 64 unwitnessed "Mechanical" rows, shrink-only.
- `data/module_size_grandfather.json` — empty list; `ceilings_tightened` records the 2026-08-26 p95 → p99 band move.

### Material limitations

1. **This is a baseline.** No prior report in this series exists, so trend claims
   draw on the project's own dated diagnostics (June and August 2026) rather than
   an earlier report in this format. Those diagnostics were authored in-repo; I
   re-measured the figures I rely on and say so where I did.
2. **The rate arithmetic is elapsed time, not effort.** 3.7 days per OBPI is
   calendar time inside an active window. It is not a measure of operator hours
   and must not be read as one.
3. **Two chains treated as one family.** The ~19-member
   `doctrine-declared-without-mechanism` figure spans two recurrence chains no
   author has linked; the project records this as operator judgment rather than
   measurement, and the 19-of-32 ratio has not been re-measured since 2026-09-02.
4. **The failure-class index has never recorded a passing run**, so the numbers
   it produced are the most stale in this report.
5. **Adopter evidence is partly unobservable.** `wtcis-pvecob/cob_reports` is
   private; I can confirm the defect filing and its version, not that
   repository's current state.
6. **`gz check` measures the staged tree.** It passed on a clean tree at
   `85c857263`; it is not a statement about uncommitted work.
7. **Parts of the evidence were gathered by delegated read-only agents.** Every
   figure this report's argument rests on was re-measured directly before use;
   figures carried from those reports without independent re-measurement are the
   scorecard row counts, the chore registry totals, and the eval summaries.
