<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Disagreements — Agent 0 and Agent 1

> **Meaningful disagreement is preserved here, not resolved into consensus.** A
> disagreement that is merely unresolved is more useful to a future investigator
> than an agreement that was manufactured.
>
> Agent 1 is **not epistemically subordinate** to Agent 0. Agent 0 leads
> reconciliation; that is a procedural role, not the authority to win an
> argument. Where Agent 1's challenge is stronger, the corresponding row in
> [`FINDINGS.md`](FINDINGS.md) moves to `QUALIFIED` or `REJECTED` and says so.

---

## Status: no entries — report received, reconciliation deferred

**Astra's Phase 2 report arrived 2026-09-22** and is at
[`gzkit-engineering-assessment-adversarial-review.md`](gzkit-engineering-assessment-adversarial-review.md).
Its §1 verdict and §2 challenge table have been read; **the full reconciliation
pass is deferred by operator decision and has not been run.**

This file is not empty because Agent 0 and Agent 1 agree. **It is empty because
the reconciliation has not happened yet.** A reader must not infer consensus.

What the challenge table already shows, un-reconciled: of 25 rows,
**9 REJECT, 3 DOWNGRADE TO HYPOTHESIS, 11 CONFIRM WITH QUALIFICATION, 1 CONFIRM,
1 NEEDS MORE EVIDENCE.** The rejects reach load-bearing findings, including the
claim that no persistent system model exists and the claim that independent
requirement identity is the remedy. **These verdicts are Astra's, not adopted** —
each gets the same scrutiny Agent 0's findings did.

Until this file is populated:

- every reconciled row in `FINDINGS.md` stays `OPEN`;
- no row may be promoted to `CONFIRMED`;
- Phase 3 cannot reach its stop condition.

---

## Entry schema

Each disagreement is recorded as:

```text
### D-NN — <the issue, stated neutrally>

- Findings touched:   F-0xx, F-0yy
- Agent 0 position:   what Phase 1 concluded, and on what basis
- Agent 1 challenge:  what Phase 2 asserts against it, in Agent 1's terms
- Evidence for A0:    repository references
- Evidence for A1:    repository references
- Disposition:        A0 CONCEDES | A1 CONCEDES | UNRESOLVED | MISSING EVIDENCE
- To resolve:         the specific observation that would settle it, and who can make it
```

**`MISSING EVIDENCE` is distinct from `UNRESOLVED`**, and the distinction is the
point of this file. `UNRESOLVED` means both positions are supported and the
evidence does not choose between them — a real disagreement. `MISSING EVIDENCE`
means neither is yet supported and the argument is premature. Recording the
second as the first would manufacture a dispute where there is only an unmeasured
question; those belong in `OPEN-QUESTIONS.md` or the measurement program.

Where a challenge lands, the disposition is recorded here **and** the status is
changed on the finding itself. The two must not drift.

---

## Amendments

- **2026-09-22 — Act 1 cold-read repair pass; challenge tally corrected.** The
  un-reconciled tally read *"roughly 26 rows, 8 REJECT"*. Counted directly from
  § 2 of the report: **25 data rows — 11 CONFIRM WITH QUALIFICATION, 9 REJECT,
  3 DOWNGRADE TO HYPOTHESIS, 1 CONFIRM, 1 NEEDS MORE EVIDENCE.** The contested
  share is **9/25**, not 8/26, and the prior enumeration summed to 24 against a
  stated 26. The "Created empty" entry below records the Phase 2 report as
  awaited; it is left standing as the dated record it is, and the report's
  arrival is stated in § Status above. **Unresolved:** the nine `REJECT` rows are
  still not mapped to `F-###` ids — that mapping is what the reconciliation pass
  produces, and until it exists a reader can tell that roughly a third of the
  register is contested but not which third. Separately, this file gates
  promotion to `CONFIRMED` on *"until this file is populated"* while
  `README.md` § Currently prohibited gates it on the Phase 2 report *"being
  read"*; two conditions on one act, for the operator to settle.
- **2026-09-22 — Created empty (Phase 3).** Schema fixed; no entries. Awaiting
  the Phase 2 report.
