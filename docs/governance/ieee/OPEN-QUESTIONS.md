<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Open questions — engineering-method assessment

> Questions that repository inspection **cannot** answer. Everything answerable
> from the repository was answered in the pieces and is not repeated here.
>
> **Status 2026-09-22: all thirteen are ruled**, one of them (`Q-09`) as a
> deferral with its sequencing named.
> Each ruling is recorded under its question; the questions are kept as asked,
> because the record of what was asked is part of the record of what was decided.
>
> **This file holds questions, not findings.** A question here is not a weak
> finding and must not be promoted into [`FINDINGS.md`](FINDINGS.md) by being
> answered plausibly. Findings carry evidence; questions carry the absence of a
> decision.

Three kinds, kept separate because they resolve by different means:

1. **Operator judgment** — `Q-01` … `Q-10`. No amount of further investigation
   settles these; they are choices about what this project is.
2. **Further measurement** — held as the measurement program `M-A` … `M-H` in
   [`01 § 12`](01-engineering-method-2026-09-22.md), not duplicated here.
3. **Meta** — `Q-11` … `Q-13`, about the conduct of the investigation itself.

---

## Operator judgment

### Q-01 — Does a demoted ADR forfeit its requirements?

**RULED 2026-09-22 — unexamined consequence.** The delete is collateral, not design. F-003 is therefore a **defect**: `gz adr demote` should archive rather than delete, and `M-B` characterises what was lost. The dangling behave tags remain a separate defect.

`gz adr demote` executes `shutil.rmtree`, and has destroyed a large share of all
REQ acceptance criteria and FAIL-CLOSED constraints ever authored.
`pool-curation.md:47` rules that *"Deleting a retired pool file is an
anti-pattern"* — but that ruling is about the **pool file**, not the brief tree,
and no ruling covering the latter was found. Either demoted work deliberately
forfeits its specification, or this is an unexamined consequence.

**Why it cannot be answered from the repository:** both readings are consistent
with every artifact found. **What turns on it:** whether `M-B` treats this as a
defect or as a premise. Piece 02 raises the stakes — it measures live behave
scenario tags pointing at briefs that no longer exist. *(Raised in both pieces;
merged here.)* · Findings: F-003, F-002.

### Q-02 — What is gzkit's product, and is the PRD retired or dormant?

**RULED 2026-09-22 — rewrite the PRD around the system as it actually ships.** The product claim stands; the January framing does not. Not retired, not left dormant. The rewrite is Phase 4 or later and is **not** authorised by this ruling.

The PRD describes a governance CLI shipped to other projects, with users,
adoption friction and a validation path. The repository's observable behaviour is
a system whose primary user is its own operator. These imply different
requirement sets.

**What turns on it:** the top of the traceability chain. Reviving, replacing or
formally retiring the PRD are all defensible; **leaving it `Draft` and uncited is
the one option that costs without paying.** · Finding: F-014.

### Q-03 — Is the pool an intake, a graveyard, or a defect queue — and which should it stop being?

**RULED 2026-09-22 — drain the defect-shaped entries to GHIs**, applying `pool-curation.md`'s three-gate filter retroactively. The pool returns to intake-only. **Architectural Boundaries 1 and 2 are not relaxed.**

Classification puts roughly a third of pool entries as defects against shipped
code and a fifth as missing verification obligations, against about a tenth that
are actual architecture decisions. Creation has effectively stopped and so has
promotion. Architectural Boundaries 1 and 2 forbid promoting post-1.0 pool ADRs
and forbid adding pool ADRs to the runtime track.

**What turns on it:** the defect entries are real and currently unreachable by
any repair route. Only the operator can rule whether they are abandoned,
re-routed, or the boundaries relaxed. · Finding: F-006.

### Q-04 — What consequence scale should govern verification rigour?

**RULED 2026-09-22 — settled live with the operator. See [`consequence-bands.md`](consequence-bands.md).** Two axes scored together (detectability and recoverability), band derived as `D + R`, sixteen surfaces scored. `M-G`'s consequence-scaled measures are unblocked in form. **The scores are PROVISIONAL** — they derive from findings that are still `OPEN`, and must be re-scored once Phase 2 is reconciled. **The bands do not re-key the lanes and do not touch the five gates** — that is Phase 4.

IEEE 1012 Clause 5 makes it normative that rigour scale to integrity level,
assigned recursively so high-consequence parts are segregated. gzkit's lite/heavy
lanes are a two-level scheme keyed to **surface kind** (CLI, API, schema =
heavy), not to consequence.

**Why it cannot be answered from the repository:** it requires a judgment about
what actually goes wrong, and how badly, when a given surface is wrong.
**What turns on it:** every proportionality question downstream. `M-H` is the
structured session that would produce it, and `M-G`'s consequence-scaled measures
depend on it. · Findings: F-019, F-018.

### Q-05 — Will an enforceable escalation threshold be accepted in place of the un-enforced IRON LAW?

**RULED 2026-09-22 — keep the IRON LAW; pursue a mechanical witness for the rule as written.** The 16085 consequence threshold is **rejected**, not deferred: it is enforceable but strictly weaker, because it delegates below a line. **Do not re-propose it.**

The operator-only-initiation rule appears in a dozen-plus prose locations and no
code, and the corpus records its own violation. 16085 § 6.4.3.2 offers the
alternative shape: a threshold defining what is acceptable "without explicit
review by the stakeholders", in three bands.

**The honest statement of the trade:** the threshold is enforceable but is a
**weaker** rule than a blanket prohibition, because it delegates below the line.
This is a governance preference, not a technical finding. · Finding: F-018.

### Q-06 — Are handoffs working memory or an archive, and may they be compacted?

**RULED 2026-09-22 — sequenced: no compaction until the durable facts have a home.** Handoff compaction is a consequence of resolving F-001, not an independent decision. An ad-hoc extraction pass is rejected.

They are demonstrably the sole custodian of live engineering facts — piece 01
found cross-module contract facts with zero hits anywhere else in the repository.
Compacting them risks losing exactly the material that is nowhere else; not
compacting guarantees the entry cost keeps rising.

**Sequencing, not preference:** the answer depends on whether the durable facts
get a home first. · Findings: F-007, F-023, F-024.

### Q-07 — Should `gz gates` and the five-gate covenant be reconciled, and in which direction?

**RULED 2026-09-22 — re-point the covenant** at `gz closeout` and `gz obpi complete`; the five-gate vocabulary is kept. Edits to `AGENTS.md` go through the corpus ceremony.

> **Standing operator constraint, 2026-09-22:** *"do not abandon the five gates without a discussion with me."* Retiring or replacing the five-gate vocabulary is **prohibited** absent explicit operator discussion, including as an incidental consequence of a Phase 4 design.

`gz gates` prints a deprecation notice on every run and is superseded by
`gz closeout` (GHI #705), while AGENTS.md's Gate Covenant documents the
deprecated verb, and Gate 5 within it is `return True`.

**Two coherent answers:** re-point the covenant at the real mechanisms
(`gz closeout`, `gz obpi complete`), or retire the gate vocabulary in favour of
what 24748-1 would call checks. **They are not the same project.** · Finding:
F-019.

### Q-08 — Which of the two release rulings stands?

**RULED 2026-09-22 — the `RELEASE_NOTES.md:1226` ruling stands; the code owes the change.** `version_sync` stops deriving the package version from an ADR identifier. The missing `kind` guard is repairable immediately and independently of the larger decoupling.

`RELEASE_NOTES.md:1226` rules that "the release line — not ADR frontmatter — is
the source of truth for what shipped." `src/gzkit/commands/version_sync.py:289`
does the opposite: it makes an ADR identifier the package version. The prose
decoupled them; the code never did.

**Either the code owes a change, or the ruling owes a retraction.** The missing
`kind` guard is a latent defect under either answer. · Finding: F-008.

### Q-09 — Promote, withdraw, or supersede `ADR-pool.feature-adr-semver-discipline`?

**DEFERRED 2026-09-22 — keep it in the pool, and sequence the `kind` guard ahead of any promotion decision.**

Operator reasoning, and it is decisive: *the req-vs-release problem is at play here.* Promotion would mint a semver-bearing ADR identifier through `adr_promote.py:156` — the operator-supplied `--semver` path with **no next-free-feature-minor guard** — which is precisely the authoring surface this pool ADR indicts. `version_sync.py:17-20` would then be free to read that identifier as a package version. **The remedy would instantiate the defect it repairs.** Verified in code, not inferred. Revisit once the guard lands.

Authored 2026-05-28, `status: Pool`, and it already names all three drift
surfaces and quotes *"Doctrine drift is invariant drift."* It has carried the
diagnosis for four months while the defect class kept producing commits.

**Constrained by Q-03 and by Architectural Boundaries 1 and 2.** · Findings:
F-008, F-006.

### Q-10 — What is the unit of approval for a release?

**RULED 2026-09-22 — a ledger release record**: an L2 event asserting the approved content of a version. Chosen over an annotated tag or a manifest because it matches the instinct F-033 identifies as already standards-conformant and adds no L1 surface.

Nothing today says "this set of artifacts is version X."

**Separate the two halves:** whether it should be a manifest, a ledger event or
an annotated tag is a design question for Phase 4; **whether it should exist is
not.** · Finding: F-015.

---

## Meta — about this investigation

### Q-11 — Ratify the `F-###` identifier convention?

**RULED 2026-09-22 — flat series-global `F-###`, ratified.** Allocated in order, never reused, stable across phases.

No `F-###` convention existed in this repository before this register. The
identifiers now in [`FINDINGS.md`](FINDINGS.md) are an **agent assumption**, not
an operator ruling. Identifier shape is doctrine-adjacent here — validators and
scanners enforce ADR, OBPI and REQ id shapes, and two recent commits repaired
exactly that class.

**Cheap to change now, expensive after Phase 4 begins citing these ids.**
Alternatives: namespaced (`IEEE-F-001`), or per-piece (`01-F-03`).

### Q-12 — Where do Phase 4 design candidates live?

**RULED 2026-09-22 — a `design-candidates.md` in this directory**, tiered below `FINDINGS.md`. Candidates never enter the findings register, so a candidate cannot be misread as a decision.

Decisions leave by the ordinary route — `gz-design` → ADR → OBPI — and
[`README.md`](README.md) already rules that nothing here binds until carried
there. But **candidates**, which are explicitly not decisions, have no home.

Proposed: a later numbered piece or a `design-candidates.md` in this directory,
never in `FINDINGS.md`, so that a candidate cannot be misread as a decision.
**Unratified.**

### Q-13 — How is the Phase 2 adversarial review delivered? *(blocking)*

**RULED 2026-09-22 — Astra runs separately and deposits its reports into this folder.** **Report received 2026-09-22**, deposited at the directory root as `gzkit-engineering-assessment-adversarial-review.md` (not inside `raw/`). **Operator ruling 2026-09-22: leave it where Astra put it, for now** — provisional, and reopened only by the operator. Phase 3 is unblocked; the reconciliation pass is deferred by operator decision.

Agent 1's review is not in this repository and was not in the reconciling agent's
context when this workspace was seeded. **Phase 3 cannot complete without it**:
every `OPEN` row in `FINDINGS.md` stays `OPEN`, and
[`DISAGREEMENTS.md`](DISAGREEMENTS.md) stays empty, until the challenge is read.

Needed: the report itself, or a path to it, or the session to query.

---

## Amendments

- **2026-09-22 — Seeded (Phase 3).** `Q-01` … `Q-10` merged from
  [`01 § 10`](01-engineering-method-2026-09-22.md) (seven) and
  [`02 § Questions for the operator`](02-requirements-vs-release-2026-09-22.md)
  (four), deduplicated — piece 01's Q1 and piece 02's Q3 are one question and are
  merged as `Q-01`. `Q-11` … `Q-13` are new and are about the investigation
  rather than about gzkit.
