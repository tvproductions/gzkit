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

## Status: no entries

**The Phase 2 adversarial review has not been received.** It is not in this
repository, and it was not in the reconciling agent's context when this workspace
was created on 2026-09-22. See [`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md) `Q-13`.

This file is not empty because Agent 0 and Agent 1 agree. **It is empty because
the challenge has not been read.** A reader must not infer consensus from it.

Until it is populated:

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

- **2026-09-22 — Created empty (Phase 3).** Schema fixed; no entries. Awaiting
  the Phase 2 report.
