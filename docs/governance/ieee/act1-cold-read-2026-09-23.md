<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Agent 2 — Act 1 cold read of the canonical register

**Read 2026-09-23. Tier: historical — raw record, frozen at its date.** This is
what one agent reported, not a canonical finding. It binds nothing. Where its
observations have since been acted on, § Disposition says so; the body above that
section is left as reported and is **not** edited to match what the register
looks like now.

**Subject: the register, not gzkit.** Pieces 01 and 02 assess the repository;
Astra's Phase 2 report assesses piece 01. This assesses whether
[`FINDINGS.md`](FINDINGS.md) and its companions stand on their own for a reader
who arrives with nothing — the falsifiability test [`README.md`](README.md)
§ Agent 2 sequencing constraint describes.

## Method, and its one caveat

Run as an isolated agent holding no prior context, dispatched by the main
session after the operator ruled the cold read ahead of the Phase 3
reconciliation pass. Reading was bounded to the five canonical files —
`README.md`, `FINDINGS.md`, `DISAGREEMENTS.md`, `OPEN-QUESTIONS.md`,
`consequence-bands.md`. The numbered pieces, `raw/`, Astra's report and
`.gzkit/handoffs/**` were not opened. Files outside `docs/governance/ieee/` were
opened **only** to test whether a cited anchor resolves, never to supply
investigation substance. The reader wrote nothing.

**The caveat, recorded because it bounds the result.** The main session was by
then anchored — it had read the resumed handoff chain, which carries Astra's
verdict and the Agent-0 discipline failure. It was therefore **not** eligible to
give this reading, and dispatched an unanchored agent instead. That is the
correct application of the sequencing constraint, but it means the reading was
taken by an agent the operator did not directly instruct. **The reading is
evidence, not authority**, in the same sense as Astra's report.

---

## Verdict

> **It stands with qualifications — and the qualifications are load-bearing.**

Reported in full:

> I can state what this investigation *is*, what it *holds*, what it *prohibits*
> and most of what it *ruled*, from the five files alone, and the architecture of
> the register (tiers, status vocabulary, class vocabulary, the "canonical is not
> normative" guard, the anti-convergence warnings) is unusually well built and
> survived a cold read intact. But I cannot state two things the register itself
> treats as central. First, **I cannot say which findings are under challenge**
> […] so I know roughly a quarter of the register is contested and cannot tell
> you which quarter, which is the one fact that governs how much weight any row
> can carry today. Second, **I cannot state the forward plan**, because eight
> findings route their disposition to `M-A`…`M-H`, and the register deliberately
> holds those definitions only in piece 01 § 12 — a file the same register
> forbids Act 1 to open. […] It does not fail; it leaks at exactly the joints
> Phase 3 was supposed to close.

**Where the attempt broke down.** Asked to state the investigation's position in
its own words, the reader completed every part except one:

> I cannot complete the sentence "what happens next." README says the next
> permitted step is "Receive the Phase 2 adversarial review (`Q-13`), then
> reconcile it row by row" — but `Q-13` is ruled and the report is received, so
> the first clause is already done, and the second is "deferred by operator
> decision" with no statement anywhere of what un-defers it, who resumes it, or
> why it was deferred. A newcomer inheriting this directory today would not know
> whether to wait, and for what.

---

## Gaps, as ranked by the reader

1. **Which findings Astra rejected.** `DISAGREEMENTS.md` gave a tally and a prose
   hint and no `F-###` mapping. *"It is the worst gap because it is the one fact
   that changes how every other row is read."*
2. **`M-A` … `M-H` are undefined inside the boundary.** Cited as the disposition
   of F-001, F-002, F-003, F-006, F-013, F-019, F-021, F-025 and of `Q-04`, and
   held only in piece 01 § 12. Consequence: F-021 calls `M-D` *"Highest-risk item
   in the program"* and a newcomer cannot evaluate the claim. **`M-F` is never
   cited anywhere in the five files**, so its existence cannot be determined.
3. **Whether an operator ruling changes a row's status.** `OPEN` is defined as
   *"disposition not yet settled"*, yet F-008 and F-015 read *"is settled"* on
   `OPEN` rows. The register uses *settled* in two senses — evidence-settled and
   operator-settled — and never separates them.
4. **Why the reconciliation was deferred, and what resumes it.** Stated as fact
   in three places; never given a reason, an owner or a trigger.
5. **Provenance of thirteen of sixteen consequence-band rows.** The PROVISIONAL
   block names three findings, then asserts *"Every `D2` score in this file is
   derived from a Phase 1 finding."* Seven `D2` rows name no finding.
6. **What the IRON LAW is.** Cited four times, never stated or pointed at.
7. **What Architectural Boundaries 1 and 2 say.** Binding at `Q-03`, `Q-09` and
   F-006; never quoted.
8. **Re-derivation is unavailable to the cold reader.** Group-B re-derivations
   route to `02-requirements-vs-release-evidence/measure.py`, inside the
   prohibited tier — structural, and probably unavoidable.

## Internal contradictions, as reported

- **Has the Phase 2 report been read?** README § Handoff said *"has not been
  read"*; `DISAGREEMENTS.md` § Status and README's own phase table said it had.
  **Two different gate conditions on the same act**: README barred promotion to
  `CONFIRMED` *"before the Phase 2 report is read"*, `DISAGREEMENTS.md` barred it
  *"until this file is populated."*
- **Is `F-###` ratified?** `Q-11` ruled it ratified; `FINDINGS.md`
  § Identifier convention, `FINDINGS.md` § Amendments and README § What must not
  be assumed all said it was not. *"Three of five files contradict the ruling."*
- **`Q-12` rules and un-rules itself in one entry** — headed **RULED**, ending
  *"Unratified."* four lines later.
- **Where Astra deposits.** README § Roles said `raw/`; the file table and `Q-13`
  said the directory root. The file is at the root.
- **Nine vs. ten `D2` surfaces.** `consequence-bands.md` said nine; its own table
  scores ten. Replicated into F-019.
- **The challenge tally does not sum.** *"of roughly 26 rows, 8 REJECT, 3
  DOWNGRADE TO HYPOTHESIS, 11 CONFIRM WITH QUALIFICATION, 1 CONFIRM, 1 NEEDS MORE
  EVIDENCE"* = 24.
- **Orphaned conditional.** README § Current gate: *"Until then no finding may be
  promoted to `CONFIRMED`"* — no antecedent, in a binding paragraph.
- **Change logs deny their own bodies.** `DISAGREEMENTS.md` § Amendments recorded
  the Phase 2 report as *"Awaiting"*; `FINDINGS.md`'s single amendment described
  a ruling-free file carrying eight operator-ruling blocks. *"Since every event is
  dated 2026-09-22, the change logs cannot disambiguate order."*

## Anchors checked

**Resolved as cited**, verified by opening the line: `adr_demote.py:475`;
`obpi_lifecycle.py:256-260`; `triangle.py:24-31`; `arb/validator.py:279`;
`.claude/hooks/pipeline-gate.py:156-158`; `airlock/enter.py:158-170`;
`commands/airlock.py:14-18`; `session_start.py:185` and `handoff_api.py:1181`;
`tautological_tests.py:108-134`; `enforcement-claim-nc-audit-2026-07-18.md:50`;
`RELEASE_NOTES.md:1226`; `adr_promote.py:156`;
`Ledger.get_post_validation_failed_gates`; `data/mechanical_witness_grandfather.json`;
ADR-0.0.20; `ADR-pool.feature-adr-semver-discipline.md`; `gz validate
--unscoped-rules` and `--invariant-coherence`.

<!-- gz-validate-skip: command-shape -->
F-034's residue claim was verified true: the parking verb it says does not exist
still does not exist, though `parser_obpi.py`'s own docstring claims it is
registered.

**Did not resolve as cited:** `src/gzkit/gates.py` (no such path; and at the real
path the line numbers land on Gate 4's PASS/FAIL, not `_run_gate_5`);
`src/gzkit/deprecations.py:41` (line right, path wrong);
`version_sync.py:289` (claim belongs at `:46`); `src/gzkit/.../release.py:201-203`
(path elided in the register); `pool-curation.md:47` (quote accurate, sits at
`:106`); a dangling *"Phase 3 Q4"*; stale `Q8` and `Q2`; and
`design-candidates.md`, ruled into existence by `Q-12` and absent.

## Load-bearing terms used without definition

**The two that blocked the reading:** **IRON LAW** — *"`Q-05` is a ruling about
it; you cannot evaluate the ruling without it"* — and **Architectural
Boundaries 1 and 2**.

**Assumed throughout, never defined:** OBPI, brief, ADR, REQ, TASK, PRD; lane and
kind; the five gates and Gate 5; the ledger and the L1/L2/L3 layering; corpus and
rendition; `@covers`; ARB receipt; airlock and seam; handoff; pool ADR and
promote/demote/park; GHI; FAIL-CLOSED; grandfather file and ratchet; drift and
reconcile.

**Standards vocabulary assumed:** the normative force of *shall*/*should*, used
as an argument throughout and never explained; integrity level; baseline and the
functional/developmental split; *declared undeveloped argument*; correspondence
method, viewpoint, view; information item; test oracle; V&V independence; and
**`embedded`**, an IEEE 1012 Annex C category used in README as if defined, with
its only explanation inside a prohibited file.

**Coined and not defined:** the `Class: —` value on F-025, F-032, F-034, F-035 —
the class vocabulary admits four values and `—` is not one of them.

## What the reader did not open, and what it believed was there

> I wanted **Astra's review**, twice and hard — once for the eight `REJECT` rows,
> once to test whether `DISAGREEMENTS.md`'s characterisation of them […] is the
> whole of what was rejected or a summary of it. That wanting is the finding: the
> register's most important current fact about itself is held only in a file it
> labels "historical… challenge input, not a second register," and the summary it
> offers in its place is not enough to act on.

It did not want the numbers: *"the ILLUSTRATIVE doctrine is stated clearly enough
that I never felt the need to check one, which is the register working as
designed."*

> What I did not miss, and this is the strongest thing I can say for the register:
> I never once needed a piece to understand *what kind of thing* this
> investigation is, what it forbids, or why it forbids it. […] The failures are at
> the seams — a deferred pass, a ruling that landed in one file and not the other
> four, and an evidence tier that four dispositions route into. Those are
> repairable in the register without touching the pieces.

---

## Disposition, as of 2026-09-23

Recorded here so a later reader can tell the reading from its consequences. The
body above is **not** edited to match.

| Item | Disposition |
|---|---|
| Gap 1 — which findings Astra rejected | **Closed.** The reconciliation pass mapped all 25 challenge rows onto `F-###` ids. Also **corrected a miscount the reading inherited**: the table has 25 rows and **9** REJECT, not 26 and 8 |
| Gap 2 — `M-A`…`M-H` undefined; `M-F` uncited | **Open.** Still held only in piece 01 § 12 |
| Gap 3 — two senses of *settled* | **Open.** No ruling yet separates evidence-settled from operator-settled |
| Gap 4 — why the deferral, what resumes it | **Closed by event.** The operator lifted it and the pass ran |
| Gap 5 — provenance of seven `D2` rows | **Open**, and recorded in `consequence-bands.md` § Amendments |
| Gaps 6–7 — IRON LAW, Architectural Boundaries | **Closed.** README § Terms this series cites as binding now points at the authority for both |
| Gap 8 — re-derivation unavailable in-boundary | **Open**, and judged structural by the reader |
| Contradiction — has the report been read | **Closed.** Reconciliation resolved it; the `CONFIRMED` bar was narrowed to *a row the review never reached* |
| Contradiction — `F-###` ratified | **Closed.** `Q-11` confirmed 2026-09-23; the three denying files corrected |
| Contradiction — `Q-12` self-contradictory | **Closed.** `Q-12` confirmed; *"Unratified."* struck; the file is created when Phase 4 opens, so its absence is now the ruling working |
| Contradiction — Astra's deposit path | **Open**, minor. README § Roles still says `raw/` against `Q-13` |
| Contradiction — nine vs. ten `D2`; the 24/26 tally | **Closed.** Both corrected, in `consequence-bands.md`, F-019 and `DISAGREEMENTS.md` |
| Contradiction — orphaned *"Until then"* | **Closed.** Reworded to name the reconciliation pass; no prohibition changed |
| Contradiction — change logs denying their bodies | **Partly closed.** Superseded entries are retained as dated records rather than rewritten; new entries are dated 2026-09-23 so the log can order itself |
| Anchors that did not resolve | **Closed** in the five canonical files. **Still present in frozen pieces 01 and 02**, which may be corrected only by a later piece |
| Undefined vocabulary beyond the two named | **Open.** No glossary exists for the series |

**The reading's own status.** It is not a finding and carries no `F-###`. Its
strongest claim — that the register leaks at the seams rather than failing — was
tested by the reconciliation pass that followed, which found one further gap the
cold read could not see from inside its boundary: a challenge row with **no
`F-###` to land on**, recorded at `DISAGREEMENTS.md` `D-08`. **The seeding of
`FINDINGS.md` from the pieces was not exhaustive either.**
