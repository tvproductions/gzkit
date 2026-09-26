<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Open questions — engineering-method assessment

> Questions that repository inspection **cannot** answer. Everything answerable
> from the repository was answered in the pieces and is not repeated here.
>
> **Status 2026-09-23: `Q-01` … `Q-16` carry operator rulings**, with `Q-09`
> deferred and its sequencing named. `Q-15` records the adopted evaluation
> criterion; `Q-16` retains the FDAU origin and separation hypothesis. Neither
> authorises Phase 4 or a pilot.
> **Update 2026-09-25:** `Q-17` records the accepted grounding pivot and the
> request to develop its bounded Phase 4 design. The investigations continue;
> pilot execution, adoption of candidate mechanics, and migration are not opened.
> **Update 2026-09-25:** `Q-16` records the operator's accepted requirement-reference
> relationship, request for deeper comparison, and subsequent narrowing to
> separation of ADRs, requirements, and release/backlog planning. It also retains
> the subsequently requested mADR alternative for comparison.
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
3. **Meta** — `Q-11` … `Q-17`, about the conduct of the investigation itself.

---

## Operator judgment

### Q-01 — Does a demoted ADR forfeit its requirements?

**RULED 2026-09-22 — unexamined consequence.** The delete is collateral, not design. F-003 is therefore a **defect**: `gz adr demote` should archive rather than delete, and `M-B` characterises what was lost. The dangling behave tags remain a separate defect.

`gz adr demote` executes `shutil.rmtree`, and has destroyed a large share of all
REQ acceptance criteria and FAIL-CLOSED constraints ever authored.
`pool-curation.md:106` rules that *"Deleting a retired pool file is an
anti-pattern"* — but that ruling is about the **pool file**, not the brief tree,
and no ruling covering the latter was found. Either demoted work deliberately
forfeits its specification, or this is an unexamined consequence.

**Why it cannot be answered from the repository:** both readings are consistent
with every artifact found. **What turns on it:** whether `M-B` treats this as a
defect or as a premise. Piece 02 raises the stakes — it measures live behave
scenario tags pointing at briefs that no longer exist. *(Raised in both pieces;
merged here.)* · Findings: F-003, F-002.

### Q-02 — What is gzkit's product, and is the PRD retired or dormant?

**RULED 2026-09-23 (operator, narrowing the 2026-09-22 ruling) — repair stale metadata and restore linkage.** Operator's words, verbatim: *"repair stale metadata and restore linkage."* The PRD is **not rewritten**. What is stale is its metadata — `status: Draft` since January, and frontmatter frozen at 2026-01-22 against six commits through 2026-08-17 — and what is missing is the citation path from `FR-*`/`AC-*` down to the ADRs below it. Both are repairs to an existing live document, not a replacement of it. Not retired, not left dormant. The repair is Phase 4 or later and is **not** authorised by this ruling.

**What this narrows, and why.** The 2026-09-22 ruling read *"rewrite the PRD around the system as it actually ships."* Two things arrived after it. The operator observed that the PRD's frontmatter is frozen while the file is not — six commits through 2026-08-17, and a problem statement that still reads as live. Astra's Phase 2 review reached the same place independently from the adversarial side: the finding *"Overreads missing explicit links"*, with counterevidence that the PRD *"contains later glossary/context additions"* and *"still states a product and north star"* [E10], and the alternative explanation *"Weak explicit linkage and stale metadata, rather than absent product intent."* **A rewrite and a metadata repair imply different work and different risk:** a rewrite discards a live document's history to fix fields it already has, which is the *"adding machinery"* failure mode F-032 names as this repository's most likely one. The superseded ruling is retained above the fold because a future reader could otherwise re-derive it.

**Superseded ruling, 2026-09-22 (retained):** *rewrite the PRD around the system as it actually ships. The product claim stands; the January framing does not.* The product-claim half is carried forward unchanged; only the remedy shape is narrowed.

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
the source of truth for what shipped." `src/gzkit/commands/version_sync.py:46`
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

**Confirmed 2026-09-23 (operator).** Ratification stands as ruled; **no
identifier changes.** Alternatives considered and rejected: namespaced
(`IEEE-F-001`) — nothing in the repository competes for `F-###`, so the
namespace buys nothing today; per-piece (`01-F-03`) — works against the
convention's own *stable across phases* property, and F-035 already spans two
pieces, stated in `01` and rejected by `02`.

**The cost warning in the original entry has partly come due**, which is an
argument for confirming rather than re-IDing: the ids are now cited across 19
reconciled finding rows and all eight `D-` entries in
[`DISAGREEMENTS.md`](DISAGREEMENTS.md), in addition to `FINDINGS.md` itself.

**This ruling was already recorded on 2026-09-22 and three files continued to
deny it** — `FINDINGS.md` § Identifier convention, its § Amendments, and
`README.md` § What must not be assumed all still read the convention as an
unratified agent assumption. Those three are corrected as part of this
confirmation. The lesson is recorded rather than the contradiction merely fixed:
**a ruling written in one file does not propagate itself.**

### Q-12 — Where do Phase 4 design candidates live?

**RULED 2026-09-22 — a `design-candidates.md` in this directory**, tiered below `FINDINGS.md`. Candidates never enter the findings register, so a candidate cannot be misread as a decision.

Decisions leave by the ordinary route — `gz-design` → ADR → OBPI — and
[`README.md`](README.md) already rules that nothing here binds until carried
there. But **candidates**, which are explicitly not decisions, have no home.

**Confirmed 2026-09-23 (operator).** The location is decided; **the file is
created when Phase 4 is authorised, not before.** A later numbered piece was
considered and rejected: pieces are frozen at their date and corrected only by a
later piece, whereas a candidate is revised in place until it becomes a decision
or is dropped. An empty container created ahead of need is the *"adding
machinery"* failure mode F-032 names, and F-032 is now `CONFIRMED` and binds
Phase 4 as a filter — so `design-candidates.md` does not exist yet, and its
absence is the ruling working rather than a dangling pointer. The 2026-09-22
entry read **RULED** in its heading and *"Unratified."* in its last line; that
contradiction is resolved here in favour of the heading.

**Update 2026-09-25:** `Q-17` now authorizes bounded design drafting and review;
[`design-candidates.md`](design-candidates.md) is created under this ruling.

### Q-13 — How is the Phase 2 adversarial review delivered? *(blocking)*

**RULED 2026-09-22 — Astra runs separately and deposits its reports into this folder.** **Report received 2026-09-22**, deposited at the directory root as `gzkit-engineering-assessment-adversarial-review.md` (not inside `raw/`). **Operator ruling 2026-09-22: leave it where Astra put it, for now** — provisional, and reopened only by the operator. Phase 3 is unblocked; the reconciliation pass is deferred by operator decision.

Agent 1's review is not in this repository and was not in the reconciling agent's
context when this workspace was seeded. **Phase 3 cannot complete without it**:
every `OPEN` row in `FINDINGS.md` stays `OPEN`, and
[`DISAGREEMENTS.md`](DISAGREEMENTS.md) stays empty, until the challenge is read.

Needed: the report itself, or a path to it, or the session to query.

### Q-14 — Is `OPEN` a settled status for a row the adversarial review never reached?

**RULED 2026-09-23 — yes. `OPEN` is a settled disposition when the reason is that the Phase 2 review did not reach the row.** The fourteen such rows **stay `OPEN`**; they are **not** promoted. What changes is that `OPEN` is now recognised as a resting state and not only a waiting one, so **Phase 3's stop condition is met.**

The reconciliation pass mapped all 25 of Astra's challenge rows onto the
register and left fourteen findings untouched, because Astra reviewed **pieces 01
and 02** rather than this register and declared its own review non-exhaustive. A
row it never reached was never exposed to challenge, so it cannot be `CONFIRMED`
— but it was also not left unresolved by anything. **Its disposition is known:
stated with evidence, unchallenged.**

**What this does not do.** It does not promote any row, does not weaken the
`CONFIRMED` bar — which still requires that the review actually reached a row —
and **does not authorise Phase 4**, which needs explicit operator authorisation
and does not follow from Phase 3 closing.

**The alternative, and why it was not taken.** Commissioning a second adversarial
pass aimed at this register would invent a fourth role: README § Roles is binding,
and Agent 1 is run separately by the operator. The agent's recommendation on the
record was that fourteen rows resting `OPEN` with a stated reason is a truer
record than fourteen rows promoted by a pass commissioned to close a gate. · Findings: all fourteen `OPEN` rows.

---

### Q-15 — How can we inculcate the more compelling aspects of Dex's experiences and conclusions here?

**RULED 2026-09-23 — adopt the successive-change evaluation criterion and pilot
approach within the existing investigation phases.** Operator: **g0**.

Operator question, verbatim: *"how can we inculcate the more compelling aspects of Dex's experiences and conclusions here?"*

Operator approval, verbatim: *"okay, let's do that then"*.

**What was approved.** The criterion and five evaluation questions in
[`README.md` § Success across successive changes](README.md#success-across-successive-changes):
preserve behavior, authority, and evidence across successive changes; evaluate
later work as well as initial implementation; inspect architecture alongside
checks; attend to costly-to-reverse decisions and patterns later agents will
copy; observe whether corrections prevent recurrence. The bounded pilot carries
the same artifacts through an initial release, a changed requirement, a deferred
item, and a later release. Independent evaluation includes an agent that did not
author the remedy reconstructing decisions and history from retained artifacts.
The README holds the criterion and evaluation detail; this entry records the
ruling and links to that text rather than maintaining a second specification.

**Evidence boundary.** [Transcript excerpts](raw/dex-horthy-successive-change-2026-09-23.md)
are external testimony motivating questions, not confirmed findings about gzkit.
Correctness, regressions, reconstruction effort, and operator corrections are
observed separately. Reduced effort or more checks alone is not success.

**Scope.** This records evaluation expectations for Phases 4–6 and informs
Phase 7's adopt / revise / reject decision. It adds no runtime gate, changes no
finding status, and does not authorise design, pilot execution, or implementation.
The Phase 6 independence rule and five-gate vocabulary remain unchanged.

---

### Q-16 — How do we keep the FDAU origin and separation hypothesis under consideration?

**RULED 2026-09-23 — retain the operator's framing and the originating FDAU
comparison through the IEEE analysis.** Operator: **g0**. This records the
request to keep the direction under consideration, not approval of a replacement
engineering model.

Operator framing, verbatim:

> I think there are strengths in fdau's repressentation and organization as it separates requirements, tasks, and releases. although slightly accidental (superpowers does not provide these things), what the agnet came up with in fdau does a better job at separartinb these things than gzkit does. also, relative to the ieee guidance, gzkit is over-conflating too many things and misusing things like adrs. Also, obpis are an in-passing informality that has been too informalized in gzkit. However, opbis do bring together requirements and tasks, in an work package, that is useful. But then we tie these things to adrs in a way that the adr is being used outside of its actual purpose. And, hard-linking adrs to a release cycle is a complete mistake. OBPIs should perhaps just become work packages, or briefs, that work as a composite key to tie adrs, requirements, and tasks. As is the case with these SDD skills packages, these briefs can then even bring specs and plans into scope. As we complete these briefs, we can consider how a set of these briefs may constitute a release increment. that is, in hind sight, a better design than the sequence that gzkit now enforces. I think fdau shows the kernel of this - not perfected in any sense.  This is why I gathered these ISO/IEEE standards - to try to get a handle on what gzkit ought to do. seeing the structure in fdau - particularly the semantic naming of feature/requirement areas, and the sequence.subsequence structure: Nx.y.

Operator retention request and origin account, verbatim:

> okay, if you see the soundness of this, how do we keep it under consideration as this IEEE analysis plays out? fdau's accidental design is what brought this ieee analysis to bear and to light.

**Where it is carried.**
[`README.md` § Investigation origin and retained hypothesis — FDAU](README.md#investigation-origin-and-retained-hypothesis-fdau)
holds the synthesis, commit-pinned sources, limitations, and explicit revisit
points in the existing measurement, design, pilot, evaluation, and decision
stages. The phase table and joining-agent guidance link to that same text.
Later consideration must give the hypothesis a reasoned disposition; it may
revise or reject it rather than treating the operator's diagnosis as an empirical
finding or the FDAU model as perfected.

**Questions retained for design, not answered by this recording.** Whether a
brief has independent identity and typed links rather than a literal composite
key; how many decisions or requirements may relate to a brief; which obligations
outlive it; how semantic families and `Nx.y` identifiers behave under change;
and how completed work maps to an approved delivered configuration. The agent's
earlier suggestion of an independent brief identifier is an option to examine,
not an operator-ratified schema.

**Accepted relationship — 2026-09-25.** Operator: **g0**. In a discussion of
moving OBPIs from ADRs into capabilities, renaming them briefs, and bringing
requirements, tasks, and V&V together as a work package, the operator accepted
the following relationship. Operator words, verbatim:

> yes to this: "a brief can present requirements together with their work and evidence while referencing their authoritative definitions. That would let the bundle be useful without making the requirements disappear into it again."
>
> But, I ask for a deeper analysis of my options lest I make a mistake like I did with the ADR.

The accepted point is that the brief assembles requirements with work and
evidence by reference to authoritative definitions. The choice of storage,
identifiers, revision binding, capability boundaries, migration route, and
timing remains open. The broader capability/brief model remains a direction
under discussion; this acceptance does not select a migration or change the
investigation's phase authorizations.

**Purpose of the concurrent efforts — 2026-09-25.** The operator clarified
why the four efforts exist. Operator words, verbatim:

> I reached for ieee to ground on authority/first principles; I reached for the test evaluation because I believe the models have been writing poor tests; I reach for the magna carta because I need some prioritized path forward; I reach for for the effort about requirements/release separation because I know the current approach is flawed.

The option comparison must therefore account for engineering grounding,
trustworthy verification, prioritized execution, and correction of the
requirements/release model. Reorganizing artifacts alone does not establish
that the other three purposes have been fulfilled.

**Organizing model remains open — 2026-09-25.** The operator clarified the
role of the proposed capability organization and the external sources. Operator
words, verbatim:

> I do not know if reaching for capabilities organization "buckets" is right either. I mention SEI as one potential anchor. I am trying to fall back on IEEE as a fallback onto authority/standards/principles.

Whether capabilities should organize the work at all remains a question, not
only where their boundaries belong. SEI is one possible source to examine;
the operator seeks grounding in standards and engineering principles before
selecting the organizing model. Distinguish what a cited standard states, the
investigation's interpretation, and a proposed gzkit implementation. Neither
the accepted requirement-reference relationship nor this clarification selects
a parent hierarchy for briefs.

**Simplified separation and effort classification — 2026-09-25.** Operator:
**g0**. The operator narrowed the discussion after the agent proposed a broader
recovery program. Operator words, verbatim:

> we need to separate adrs, requirements, and release tracking, that is the simplest. we also might want to just make the smallest adjustment that allows for that. adr == release increment is a mistake. tying the requirements corpus to adrs is a mistake. not treating release/backlog planning as a separate matter is a mistake.
>
> shoddy tests is tech debt.
>
> double-checking against ieee is good reflective maintenance
>
> Magna cart is release planning.

This establishes the separation sought and distinguishes the roles of the
existing efforts. The smallest sufficient adjustment is the option to examine;
the wording does not select an implementation. Capability containers and a
broader reorganization are not prerequisites implied by this direction. The
earlier grounding constraint also carries forward, in the operator's words:

> also, I still strongly believe in keeping TDD, BDD, DDD as strong grounding influences on this project.

**Alternative requested for exploration — 2026-09-25.** Operator: **g0**.
The operator then asked to examine retaining deliberate ADR/release coupling
as a modified ADR (mADR), with an independent reusable requirements catalog.
Operator words, verbatim:

> there is also the case that my appropriation of the adr is ok/defensible and tying it to release is a new kind of discipline. the models need that coupling and strictness and that all downstream misalignments are accidents to correct as we accept tight coupling between intent, design, and architecture. We just GHI corrections, as I do. And NEVER allow more than one active ADR. all else is pooled. It is a recovery.
>
> So, what if I have a new conceptualization of adr and we just deal with it? do not move to a new adr until all current problems resolved with GHIs and patch bumps.
>
> Explore that as a simpler alternative and allow our mADR (modified) to be some agentic workaroud/provision. This still allows all current research projects to remain valid.
>
> I can still pull REQS away into a catalog and sew them in. this allows for a REQs reuse. An FDAU-like REQ system.
>
> this is a bastardization and an extension of REQ coding.
>
> OBPI-x.y.x-nn-NNx.y
>
> obpi (adr number) - obpi sequence nn - REQ code (NNx.y)
>
> I still need a defensible source for the fdau system though.

This is an alternative to compare, not a selection of a replacement model or
identifier schema. Separate the evidence for requirement identification and
traceability from the provenance of FDAU's specific notation. The candidate's
claims about agent behavior and causes of misalignment remain hypotheses.
Adopting a version-derivation rule contrary to `Q-08` would require explicitly
revisiting that ruling; exploring the alternative does not change it.

**Accepted identity distinction and further exploration — 2026-09-25.**
Operator: **g0**. The operator responded **"I love this:"** to the following
three-identity distinction (table formatting normalized):

| Identity | Illustrative form | Meaning |
|---|---|---|
| Catalog requirement | `REQ-C2.3` | The independently maintained obligation |
| Work package | `OBPI-0.35.0-14` | The assignment being executed |
| Requirement assignment | `OBPI-0.35.0-14-C2.3` | That OBPI's responsibility for that requirement |

The operator seeks IEEE, SEI, and other authoritative grounding for an
increment-to-brief discipline around human/agent work, with catalog requirements
revisited as understanding changes and each brief declaring its contribution.
An OBPI as a sortie, enclosing or referencing a plan/specification, remains
under discussion. Retaining the ADR name is not a condition of the proposed
campaign-step function. The operator explicitly challenges the proposal:

> This might be an epicyclic cope btw.
>
> can I pull this off without it becoming Ptolemy vs. Copernicus?

The acceptance concerns the distinction among the three identities. It does
not ratify identifier grammar, a storage schema, the sortie terminology, or
claims that agents require this exact hierarchy. Evaluate whether the proposed
control removes ambiguity and special cases; do not treat retention of the
existing artifact structure as the criterion for success.

**Product needs and bounded advances — 2026-09-25.** Operator: **g0**.
The operator further explained the model and its original purpose. Excerpts,
verbatim:

> I think the modification - pull REQs out, even during adr planning, is a way to allow reqs to evolve separately. an army learns from the wars, campaigns, and battles it fights. requirements are categorical and attend to the product as a system of needs.  the adrs, obpis and tasks are a way to achieve a single advance of the system to attempt to realize the constellation of requirements in a moment in time, under the capabilities of the time, and the constraints of the time. each adr is a battle into the realization of the system, the briefs are the ops orders, and the plan, spec, tasks are ways to move towards the material realization of the reqs.
>
> In fact, the whole point of one-brief-per-item is that the agent could only handle one serious foray into the system. I conceived of the airlock to help with that.

The comparison must preserve that intended bounded-work function rather than
treat the ADR/OBPI structure as defective solely because its terminology departs
from conventional ADR usage. The catalog is proposed as independent product
knowledge, including requirements learned during planning; each work assignment
states its contribution to an identifiable requirement state. The original
[airlock design](../work-phases-and-airlock.md#1-the-core-idea-model-in-model-out)
describes the same bounded-context purpose. This records intent, not a finding
that the shipped airlock fully realizes it or that the proposed extraction is
already implemented.

**Scope.** `Q-08` and `Q-10` remain ruled; `Q-12`'s candidate-file timing and
`Q-15`'s evaluation criterion remain in force. No finding changes status. This
entry starts neither Phase 4 nor a new R&D run, creates no ADR or OBPI, and
changes no runtime rule, identifier, five-gate vocabulary, or release authority.

**Subsequent direction, 2026-09-25:** `Q-17` records the conversation's accepted
grounding pivot. It develops this hypothesis into a bounded design exercise;
the earlier framing above remains its history rather than the latest direction.

### Q-17 — Move this conversation to a plausible design pivot

**RULED 2026-09-25 — preserve the accepted direction as a grounding/anchoring
pivot and develop its design.** Operator: **g0**. Source: the operator's requests
below. This authorizes bounded Phase 4 drafting and design review, not a pilot,
implementation, ADR booking, campaign reordering, or migration.

The operator accepted the following role statement, supplied in their message:

> The resulting roles are understandable:
>
> - **Requirements catalog:** what the product must satisfy, why, and how that understanding has changed.
> - **mADR:** the decision and rationale for the next bounded advance, including its scope and constraints.
> - **Brief:** the assignment—its contribution to selected requirements, implementation boundaries, and required evidence.
> - **Plan, specification, and tasks:** the detail needed to execute that assignment.
> - **Release record:** what actually shipped, with its supporting evidence.

Their acceptance and scope clarification, verbatim:

> I deeply agree, help me with this (also ADRs capture, currently, a lot of design intent and REQ material):

The referenced distinction was between independently maintained product
obligations and local acceptance criteria: extraction must read the existing
ADRs as well as their briefs, and must not convert every implementation step
or evidence obligation into an enduring catalog requirement. The operator also
deeply agreed with binding an assignment to the requirement state it addresses,
preserving historical evidence rather than silently updating its claim when
requirements change. They requested help with the control hypothesis: enforced
boundaries and transitions cannot establish semantic correctness, and TDD,
BDD, DDD, and test evaluation remain necessary.

Operator request, verbatim:

> The anthropic articles you found are also compelling.
>
> Copernicus is the truth that my current model is flawed. Clinging to Ptolemy is the pain of correction and relying on epicycles.
>
> I need help moving this whole conversation to a plausible design pivot.

Subsequent operator directions, verbatim:

> I will continue all investigations - ieee can substantiate the design even in some of its nomenclature appropriations were wrong. the tests do have a problem, the magna carta is a release planning logic.
>
> make the results from this conversation a GROUNDING/ANCHORING pivot.

**Anchor and candidate home:**
[`design-candidates.md` § Grounding pivot](design-candidates.md#grounding-pivot).
The grounding section carries the accepted distinctions; the remainder proposes
mechanics and an evaluation path. Future design starts from this anchor rather
than silently reopening the roles or treating an agent's preferred terminology
as a requirement. An explicit operator decision may revise the anchor.

**What continues:** IEEE/SEI grounding and challenge; the test investigation and
verification-debt work; Magna Carta's release planning; the existing campaign
and its governed execution. The pivot neither discredits these efforts nor
consolidates them into a new compulsory recovery program. Correct or unconventional
nomenclature alone does not decide the engineering value of a mechanism.

**What remains proposed:** catalog layout and executable identity grammar,
assignment amendment mechanics, applicability/supersession, whole-requirement
satisfaction claims, release interruption policy, and migration timing. The
accepted catalog/work-package/assignment distinction does not ratify a parser.
The existing five gates, operator initiation, TDD/BDD/DDD grounding, campaign
sequence, Q-08, Q-10, and Q-15 remain. Consequence bands stay PROVISIONAL and
are not consumed by this candidate. No finding changes status.

**Review boundary:** the Phase 4 full-triad requirement is met by the main
author, a separate adversarial design reader, and a fresh design reader. This
is not a repeat of the historical Act 1 or an independent evaluation of an
executed pilot. The design-review record lives with the candidate. Adoption of
the proposed mechanics requires later evidence and an operator decision; the anchor is not a claim
that the implementation already meets it.

**Retention correction, 2026-09-25.** The operator subsequently asked:

> we have a LOT of design pivot candidates here, have you richly captured it? this is a very important design conversation/session

The first candidate preserved the latest synthesis but compressed the wider
option space too far. The [dated session record](design-pivot-session-2026-09-25.md)
now retains the stakes, reasoning sequence, supplied dialogue's contribution,
and source limitations. The [expanded option inventory](design-candidates.md#alternatives-and-their-disposition)
separates recovery timing/extent, conventional ADRs, capability ownership,
retained and stronger mADR coupling, naming, requirement mechanics, and earlier
implementation-order proposals. This fulfills the request for rich capture;
it does not reopen the accepted five roles or turn prior proposals into rulings.
Affordability and execution timing remain unmeasured/unselected, respectively.

**Explicit ownership ruling, 2026-09-25.** The operator then directed amendment
of Magna Carta §3 and its governing surfaces, rather than a proposal link alone.
The [campaign amendment](../build-to-1.0-campaign-2026-09-20.md#amendments-2026-09-25)
preserves the full instruction verbatim and superseded hierarchy explicitly.
Durable requirements now have independent authority; bounded mADR/ADR →
brief/OBPI → plan/specification/tasks assignments reference identifiable
requirement states. Briefs retain local acceptance criteria. Acceptance binds
requirement state and product configuration; release content is a separate claim.
This is adopted doctrine with an explicit implementation boundary: current
identifiers, parsers, proof bindings and historical ledger subjects remain until
governed migration. The candidate pilot, executable catalog and identity grammar
remain unimplemented proposals. No campaign order, 1.0 gate or finding status changes.

---

## Amendments

- **2026-09-25 — `Q-17` records explicit adoption of the ownership relationship.**
  Linked the operator-ratified Magna Carta §3 amendment and distinguished adopted
  doctrine from unimplemented catalog mechanics and the retained execution rules.

- **2026-09-25 — `Q-17` enriched after the operator's retention challenge.**
  Recorded the request verbatim and linked deliberation history and the expanded
  option inventory, distinguishing accepted grounding, operator-origin options,
  agent recommendations, source support, and unresolved choices.

- **2026-09-25 — `Q-17` records the grounding pivot and bounded design request.**
  Preserved accepted roles and operator wording, including continuation of all
  investigations. Opened the designated candidate file for drafting and review;
  retained the separate boundaries for pilot, adoption, and implementation.

- **2026-09-25 — `Q-16` retains the bounded-foray origin.** Recorded the
  operator's product-needs/advance distinction and the original brief/airlock
  purpose; linked the existing design account without claiming runtime proof.
- **2026-09-25 — `Q-16` records acceptance of the three-identity distinction.**
  Retained the request for authoritative grounding and the explicit challenge
  to preserving a flawed structure through added exceptions. Schema and
  terminology choices remain open.
- **2026-09-25 — `Q-16` retains the mADR alternative.** Preserved the request
  to explore one active delivery increment, GHI/patch correction, independently
  reusable requirements, composite references, and defensible source grounding.
  Exploration does not select the alternative or supersede `Q-08`.
- **2026-09-25 — `Q-16` narrows the separation discussion.** Recorded the
  operator's distinction between the structural correction, test debt, IEEE
  reflective maintenance, and Magna Carta release planning; retained the
  possibility of the smallest sufficient adjustment and the TDD/BDD/DDD
  grounding constraint. Linked the clarification from the README.
- **2026-09-25 — `Q-16` records the accepted requirement-reference relationship.**
  Preserved the operator's acceptance and request for deeper option analysis
  verbatim. Linked the clarification from the retained hypothesis; no migration
  choice, runtime rule, or phase authorization is inferred.
- **2026-09-23 — `Q-16` records the operator's FDAU framing and retention
  request verbatim.** Linked its treatment in the README, phase table, and
  joining-agent guidance. The ruling concerns continued consideration; the
  proposed engineering model remains subject to design and independent testing.
- **2026-09-23 — `Q-15` registered after the operator asked** *"did you update
  where needed?"*. The approved criterion was already in the README, but its
  ruling was missing from this register. Recorded the existing approval and
  linked the README phase and handoff paths to it. Updated the current status
  and Meta range; earlier dated counts remain historical records.
- **2026-09-23 — `Q-14` allocated and ruled.** New Meta question: whether `OPEN`
  is a settled status for a row the Phase 2 review never reached. **Ruled yes.**
  Given an id rather than recorded only in an amendment log, because it binds how
  every `OPEN` row is read — the failure mode `Q-11` demonstrated, where a ruling
  lived in one file while three others denied it. **Phase 3's stop condition is
  met as of this ruling; Phase 4 remains unauthorised.**
- **2026-09-23 — `Q-11` and `Q-12` confirmed by operator ruling; both
  self-contradictions closed.** `Q-11`: ratification stands, no identifier
  changes, and the three files that still denied it are corrected.
  `Q-12`: `design-candidates.md` in this directory, tiered below
  `FINDINGS.md`, **created when Phase 4 is authorised and not before**; the
  entry's trailing *"Unratified."* is struck in favour of its **RULED** heading.
  With `Q-02`'s narrowing, **all thirteen questions are now ruled and
  internally consistent.**
- **2026-09-23 — `Q-02` narrowed by operator ruling.** *"Repair stale metadata and
  restore linkage"*, replacing *"rewrite the PRD"* as the remedy shape; the
  product-claim half of the 2026-09-22 ruling carries forward unchanged and the
  superseded wording is retained in the entry. Recorded on F-014, whose
  `QUALIFIED` narrowing from Astra's Phase 2 challenge said the same thing from
  the adversarial side. **This closes the last of the four next steps the
  2026-09-22 handoffs carried.** Dated 2026-09-23 UTC; prior entries in this
  register are dated 2026-09-22 and the separation is deliberate, since a
  same-day change log cannot order its own entries.
- **2026-09-22 — Act 1 cold-read repair pass (mechanical only).** **No ruling
  changed.** `Q-03`'s `pool-curation.md:47` → `:106`, where the quoted
  anti-pattern ruling actually sits; the quote itself is accurate. `Q-08`'s
  `src/gzkit/commands/version_sync.py:289` → `:46`, the function that does what
  the entry describes. **Unresolved, left for the operator:** `Q-12` is headed
  **RULED** and ends *"Unratified."* four lines later in the same entry, and the
  `design-candidates.md` it rules into existence does not exist; `Q-11` is ruled
  **ratified** while `FINDINGS.md` and `README.md` both still record `F-###` as
  an unratified agent assumption.
- **2026-09-22 — Seeded (Phase 3).** `Q-01` … `Q-10` merged from
  [`01 § 10`](01-engineering-method-2026-09-22.md) (seven) and
  [`02 § Questions for the operator`](02-requirements-vs-release-2026-09-22.md)
  (four), deduplicated — piece 01's Q1 and piece 02's Q3 are one question and are
  merged as `Q-01`. `Q-11` … `Q-13` are new and are about the investigation
  rather than about gzkit.
