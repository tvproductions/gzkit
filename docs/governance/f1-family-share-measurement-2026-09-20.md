# Measurement — is the doctrine-declared-without-mechanism family shrinking in share?

> **This is a dated record, measured 2026-09-20.** It states a measurement and its method;
> it amends no plan and ratifies no sequencing. The figures below are the record of one
> pass, not a live value: re-run the evidence scripts rather than transcribing a number
> from this file. Evidence and re-run instructions:
> [`f1-family-share-2026-09-20-evidence/`](f1-family-share-2026-09-20-evidence/README.md).

## Why this was taken

`docs/rnd/ghi-landscape-reorganization.md` closed on 2026-09-20 naming exactly one
measurement it did not take, and the session handoff carried it forward as the single
highest-value open loop. The R&D record's own words:

> The campaign records 19 of 32 (59%) on 2026-09-02; this pass counts 14 of 57 (~25%).
> Different readers, different dates, no shared method.

Two judgments by different readers are not a measurement, and the active campaign's
sequencing — Movement C's `Close the doctrine-declared-without-mechanism family` box, pulled
to NEXT-IN-PRIORITY on 2026-09-02 — rests on the older figure. Taken on the operator's
work selection, 2026-09-20.

## Method

The defect in the prior figures is **method**, not arithmetic. This pass fixes the three
variables that were free: one reader, one criterion, one day, applied to **both** cohorts.

**The criterion** is the family's own, from GHI #537 as the campaign box quotes it:

> Layer X declares a discipline that Layer X does not mechanically enforce.

Applied operationally. An issue is a member when its body establishes **both**:

- **(a) a declared discipline** — a binding claim, contract, mandate or doctrine stated in
  some layer (rule text, docstring, skill mandate, doctrine document, CLI contract, REQ);
- **(b) a witness gap** — nothing observes that claim, or the witness's subject is narrower
  than the claim, or the mechanism exists and is never invoked.

Excluded, with the reason each exclusion is principled rather than taste:

| Excluded shape | Why |
|---|---|
| missing capability, nothing previously declared | no (a) — nothing was promised |
| two witnesses disagreeing | the campaign's own `#877` exclusion precedent: a coherence defect, not an unwitnessed discipline |
| plain code defect (wrong branch, import cycle, hardcoded literal) | no (a) |
| forward edge with no governed reversal | no declared discipline goes unenforced |
| a mandate already **demoted to advisory in its own text** | the family's completion criterion names this as discharged — *"no third state"* |

**The cohorts** are reconstructed from GitHub rather than assumed. The 2026-09-02 cohort is
every issue open at that pass's own measurement instant, pinned to `2026-09-02T05:00:45Z` —
the creation time of `#933`, the youngest issue that pass named, so the instant is a lower
bound the campaign's own evidence fixes. Today's cohort is the 56 issues open on 2026-09-20.

**Self-declaration is not the criterion.** 56 of 56 open bodies carry a `Class of failure`
section, extracted mechanically as an input. It is evidence a reader weighs, not a verdict:
`#998` self-describes as *"the inverse of the doctrine-declared-without-mechanism family"*
and is a member under the criterion, because a witness that gates volume while coverage dies
is precisely a witness whose subject is narrower than its claim.

## The campaign's figure: numerator sound, denominator wrong

The 2026-09-02 pass is reproducible, because it stated its criterion and listed its 19
members. Both halves were checked.

- **Numerator — verified.** All 19 named issues were open at that instant.
- **Denominator — wrong by 5.** The open queue held **37** issues at that instant, not 32.
  The queue never held 32 on that date; it passed through 32 around 2026-08-25/26, a week
  earlier. The claim as written is **19 of 37 = 51.4%**, not 59.4%.

The pass's own section heading — *"Half the open GHI queue is this family"* — survives the
correction. The stated percentage does not.

Five surfaces carry the uncorrected figure. Two are immutable historical records and are
correct as records (`docs/reports/big-picture/2026-09-19.md`, the 2026-09-20 handoff). Three
are live: `build-to-1.0-campaign-2026-08-16.md` (three places),
`capability-control-review-2026-09-12.md:410`, and `docs/rnd/ghi-landscape-reorganization.md`
(twice, quoting it).

## Result

One reader, one criterion, both cohorts, 2026-09-20:

| | 2026-09-02 | 2026-09-20 | change |
|---|---:|---:|---|
| open queue | 37 | 56 | +19 |
| family members | 28 | 38 | **+10 (+36%)** |
| **share** | **75.7%** | **67.9%** | **−7.8 points** |

**Sensitivity.** Eleven calls were borderline. Flipping every one of them, in either
direction, does not change the finding:

| borderline treatment | 2026-09-02 | 2026-09-20 | change |
|---|---:|---:|---|
| as judged | 75.7% | 67.9% | −7.8 pts |
| all lean-includes excluded | 67.6% | 57.1% | −10.4 pts |
| all lean-excludes included | 81.1% | 76.8% | −4.3 pts |

Under every treatment the family is **between 57% and 81% of the open queue at both dates**,
the share declines by 4 to 10 points, and the absolute count rises.

**Flow over the 18 days.** 10 members closed; 20 new members were filed. The class
discharges instances and produces them at twice the rate.

## What this answers

**The hypothesis is not supported.** The R&D record's suggested direction — the family
*"shrinking in share while the queue grows"*, 59% → ~25% — does not survive a shared method.
The apparent collapse was reader variance, not a trend: a 34-point drop measured across two
readers becomes a 7.8-point drift when one reader applies one criterion to both dates.

**The campaign's sequencing premise holds, and holds more strongly than the campaign claimed
it.** The box was pulled to NEXT-IN-PRIORITY on the strength of *"19 of 32"* and *"instances
close same-session, the class keeps producing."* The first figure was overstated as a share
and understated as a fact: the family is roughly two-thirds to three-quarters of the open
queue, at both dates. The second is confirmed and quantified — 10 closed against 20 produced.

**The share decline is real but small, and it is not discharge.** Share fell 7.8 points while
the stock grew 36%. The family is not shrinking; the queue is growing slightly faster than
the family is, and the growth arriving from elsewhere is what moves the ratio.

## What this does not do

This record amends no plan. Correcting the three live surfaces that carry `19 of 32`, and
deciding whether a 7.8-point share drift warrants any change to the box's position, are
operator rulings: campaign sequencing is operator-ratified, and a silent change to a ratified
threshold is the doctrine drift `AGENTS.md` names. The routing facts are here; the ruling is not.
