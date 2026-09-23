<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# IEEE / ISO/IEC/IEEE standards analysis series

A standing series that reads gzkit against a corpus of modern systems- and
software-engineering standards. The purpose is **not** standards conformance.
The standards are used as a mature body of engineering vocabulary, to answer
four questions about this project:

1. What has gzkit already rediscovered correctly?
2. What engineering objects has it conflated?
3. What important concepts are missing or weak?
4. What existing process or artifact can be simplified or removed?

The governing principle is **use the standards to improve engineering clarity,
not to import bureaucracy**. Every piece in the series carries a section naming
the machinery gzkit should *not* adopt, because most of what these standards
contain is acquisition, contractual or large-organization apparatus that a
project with one operator and several agents would only be harmed by.

## Start here

**Read [`FINDINGS.md`](FINDINGS.md) first.** It is the canonical register — what
the investigation currently accepts as supported — and it is the only file needed
to know where things stand. The numbered pieces are evidence behind its rows.

| File | Tier | What it is |
|---|---|---|
| [`FINDINGS.md`](FINDINGS.md) | **canonical** | The findings, with status and evidence pointers. Living; amended in place |
| [`DISAGREEMENTS.md`](DISAGREEMENTS.md) | **canonical** | Where Agent 0 and Agent 1 disagree, preserved unresolved |
| [`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md) | **canonical** | Operator questions and rulings, including successive-change evaluation (`Q-15`) and the FDAU origin and retained hypothesis (`Q-16`) |
| [`consequence-bands.md`](consequence-bands.md) | **canonical, PROVISIONAL** | Operator-ruled consequence scale (`Q-04`). Scores rest on `OPEN` findings; must be re-scored after Phase 2 |
| [`01-…`](01-engineering-method-2026-09-22.md), [`02-…`](02-requirements-vs-release-2026-09-22.md) | historical | Raw investigation record — what an agent said, frozen at its date |
| [Astra's adversarial review](gzkit-engineering-assessment-adversarial-review.md) | historical | Agent 1's Phase 2 report, as deposited. Raw record — challenge input, not a second register |
| [Act 1 cold read](act1-cold-read-2026-09-23.md) | historical | Agent 2's Act 1 verdict on **this register**, frozen at its date. Raw record — evidence about the register, not a finding about gzkit |
| [Dex Horthy transcript excerpts](raw/dex-horthy-successive-change-2026-09-23.md) | historical, external testimony | Timestamped source excerpts behind the successive-change evaluation criterion; not verified findings about gzkit |
| [`raw/`](raw/README.md) | historical | Index and tier statement for raw reports |
| [`02-…-evidence/`](02-requirements-vs-release-evidence/) | tooling | `measure.py` — the re-derivation script piece 02's figures come from. **Not investigation narrative**: it holds no conclusions, carries no literals from its authoring date, and reports whatever tree it is given |

**Canonical is not normative.** A finding here records what the investigation
supports. It binds nothing, changes no rule, and authorises no work.

**This is not a standards-compliance initiative, and no phase of it may become
one.** gzkit is not pursuing conformance with any standard in this corpus, will
not claim conformance, and is not obliged to adopt anything a standard contains.
The corpus is used as vocabulary. [`FINDINGS.md`](FINDINGS.md) F-032 and F-033
are the standing guard on this, and F-032 binds Phase 4 as a filter.

## Investigation origin and retained hypothesis — FDAU

**Recorded 2026-09-23 at the operator's request; `Q-16`.** The operator identifies
xplane-fdau's emergent organization as the origin of this IEEE investigation:
*"fdau's accidental design is what brought this ieee analysis to bear and to
light."* The standards were gathered to help determine what gzkit ought to do
after that comparison exposed a more intelligible separation of engineering
objects. FDAU is an originating example to examine, not a reference implementation
to copy or a demonstrated standards-conformant system.

**Hypothesis to retain.** Requirements and specifications describe obligations;
ADRs record architectural decisions; bounded briefs assemble the requirements,
relevant decisions, specifications, plans, tasks, and evidence needed for a
change; releases identify selected delivered increments. The useful work-package
function of OBPIs can survive without making an ADR the mandatory container or
coupling its identity to a release. Semantic capability areas and hierarchical
`Nx.y` identifiers may make the work easier to navigate without encoding release
membership. This is a synthesis of the operator's framing, preserved verbatim at
[`Q-16`](OPEN-QUESTIONS.md#q-16-how-do-we-keep-the-fdau-origin-and-separation-hypothesis-under-consideration).
It is not an approved replacement ontology, identifier scheme, or migration.

**Inspectable comparison source.** The reviewed FDAU snapshot is
`49eec3557145d9825c7026aa4dfee718443d433f`:
[backlog method](https://github.com/tvproductions/xplane-fdau/blob/49eec3557145d9825c7026aa4dfee718443d433f/docs/project/backlog-method.md),
[roadmap](https://github.com/tvproductions/xplane-fdau/blob/49eec3557145d9825c7026aa4dfee718443d433f/ROADMAP.md),
and [backlog](https://github.com/tvproductions/xplane-fdau/blob/49eec3557145d9825c7026aa4dfee718443d433f/BACKLOG.md).
Its [retrospective](https://github.com/tvproductions/xplane-fdau/blob/49eec3557145d9825c7026aa4dfee718443d433f/docs/project/backlog-governance-model.md)
also contains proposals for other projects; distinguish those from implemented
FDAU behavior. Its child-and-gate tracking does not itself establish durable
individual requirement identity or complete bidirectional traceability. The
operator attributes the organization to the agent's emergent design, rather than
to a capability supplied by Superpowers; that provenance account is not an audit
of Superpowers.

**How it remains in consideration.** Carry this question through the existing
phases, when each is authorised, and record its disposition rather than allowing
it to disappear into a generic recommendation to improve governance:

| Existing stage | Treatment of the retained hypothesis |
|---|---|
| Measurement program | Read `M-A` and `M-B` against the durable-obligation / bounded-work distinction; retain evidence that weakens it as well as evidence that supports it. This does not commission either measurement |
| Phase 4 — design | Explicitly compare a model with separately identified requirements, decisions, work packages, and releases against the current model and narrower repairs. Examine brief relationships and semantic `Nx.y` navigation without assuming that literal composite keys or renumbering are needed. Record what to retain, revise, or reject and why |
| Phase 5 — pilot | Use `Q-15`'s existing successive-change sequence to test whether a changed requirement, deferred brief, and later release preserve identity, approval history, and evidence. Include a case where completed work is not yet released |
| Phase 6 — independent evaluation | Reconstruct what was required, decided, worked, verified, and shipped from retained artifacts. Check both semantic separation and the cost of maintaining the links; inspect FDAU's limitations as possible failure modes |
| Phase 7 — operator decision | Give this hypothesis an explicit adopt / revise / reject disposition supported by the pilot evidence; record an inconclusive result as inconclusive |

**Relationship to the existing record.** This bears on F-001, F-002, F-005,
F-008, F-012, and F-015; it neither supplies new evidence for their status nor
settles their qualifications. `Q-08` already rules against deriving a package
version from an ADR identifier, and `Q-10` selects a ledger release record.
Preserve those rulings while investigating the wider separation. `Q-12` still
places design candidates in `design-candidates.md` only after Phase 4 is
authorised. The hypothesis is retained here as investigation framing; Phase 4
and the runtime governance rules remain unchanged.

## Investigation phases

| Phase | Purpose | Lead | Status |
|---|---|---|---|
| 0 | Frame the investigation | operator | complete |
| 1 | Primary forensic assessment | Agent 0 | complete — pieces 01, 02 |
| 2 | Adversarial review of Phase 1 | Agent 1 (Astra) | complete — report received 2026-09-22 |
| 3 | Reconciliation and canonicalization | Agent 0 | **complete 2026-09-23** — reconciled, disagreements recorded, stop condition met (`Q-14`) |
| 4 | Design target engineering model against the [successive-change criterion](#success-across-successive-changes) (`Q-15`), explicitly addressing the [FDAU separation hypothesis](#investigation-origin-and-retained-hypothesis-fdau) (`Q-16`) | — | not authorised |
| 5 | Bounded pilot across [successive changes](#success-across-successive-changes) (`Q-15`) | — | not authorised |
| 6 | Independently evaluate the pilot against the [adopted criterion](#success-across-successive-changes) (`Q-15`) | — | not authorised |
| 7 | Adopt / revise / reject | — | not authorised |
| 8 | Incremental migration | — | not authorised |
| 9 | Measure and periodically reassess | — | not authorised |

### Success across successive changes

**Adopted for this investigation, 2026-09-23.** The operator asked, *"how can
we inculcate the more compelling aspects of Dex's experiences and conclusions
here?"* and accepted the proposed criterion and pilot approach with *"okay,
let's do that then"*. Operator: **g0**. The ruling is registered at
[`Q-15`](OPEN-QUESTIONS.md#q-15-how-can-we-inculcate-the-more-compelling-aspects-of-dexs-experiences-and-conclusions-here).
The accepted criterion is:

> A remedy must preserve required behavior, authority, and evidence across
> successive changes. Its evaluation must examine whether later work remains
> understandable and verifiable, including by an agent that did not author the
> remedy. Additional rules, artifacts, and checks are not themselves evidence of
> improvement.

This is an evaluation commitment within the investigation. It adds no runtime
gate and does not initiate Phase 4 design, a pilot, or implementation. The phase
authorisation table and the Phase 6 independence rule remain in force.

**Source and evidence boundary.** The operator supplied an AI Native Dev
conversation attributed to Dex Horthy. [Selected transcript excerpts](raw/dex-horthy-successive-change-2026-09-23.md)
retain timestamps and original wording. His experiences motivate the questions
below; they do not establish their answers for gzkit. No finding gains a status
from this testimony. Benchmark figures, model rankings, and universal claims
about context length are not adopted as evidence.

| Lesson to test | Application in the existing phases |
|---|---|
| Generating a system and maintaining it are different capabilities | Phase 5 exercises successive changes against the same evolving pilot; Phase 6 evaluates later changes as well as the first success |
| Passing checks can miss architectural deterioration | Phase 6 examines actual dependencies, state ownership, and failure paths alongside results; the explanation must point to implementation evidence |
| Planning has greatest value where mistakes are expensive to reverse | Phase 4 gives explicit attention to requirement identity, release authority, and historical evidence, distinguishing them from cheaply reversible details |
| Existing code supplies examples for later agents | Phase 4 identifies the implementation patterns a later agent is likely to copy; Phase 6 checks whether those patterns agree with the intended design |
| Corrections should improve subsequent work | Phase 6 checks whether operator corrections recur, and whether existing instructions, skills, or verifiers address the cause before proposing another mechanism |

**Where the testimony lands in the register.** Reconciled 2026-09-23, after the
criterion was adopted. Each excerpt is mapped to the row it **bears on**; none
is evidence **for** that row. Verified mechanically at reconciliation: the
register held 35 rows at 15 `QUALIFIED` / 14 `OPEN` / 2 `CONFIRMED` /
2 `DISPUTED` / 2 `REJECTED` before and after the deposit, so the boundary above
— *no finding gains a status from this testimony* — holds as stated.

| Excerpt | Bears on | What it is, and is not |
|---|---|---|
| `11:11` accumulated difficulty | F-025, F-007 | A different codebase decaying over months. **F-025 attributes duration to no cause** and lists eleven live candidates; this adds testimony to that list, not a measurement removing anything from it |
| `19:10` *"expected pain"* — chance × pain | `consequence-bands.md`, `Q-05` | **Contrast, not corroboration.** Horthy's framing is probability-weighted; the bands are `D + R` and deliberately are not, and `Q-05` ruled the 16085 consequence threshold *weaker*, not merely different. A reader must not take this as support for re-proposing it — that re-proposal is prohibited |
| `28:51` *"no fast oracle for software maintainability"* | F-028, `M-D` | A claim about **feedback speed**, distinct from F-028's claim about vocabulary — which Astra corrected: 29119 **Part 1** does define oracle. Bears on `M-D`'s unresolved method problem, the highest-risk item in the program |
| `34:45` instructions unfollowed because context is too large | F-023, F-024 | The closest match to an existing finding. **F-023 is `QUALIFIED`** — Astra withdrew the 92,000-token figure and its dominance claim; testimony does not restore a withdrawn measurement |
| `38:29`, `38:38` bad code degrades future work | F-020, F-021 | Motivates the *existing code supplies examples* row above. F-020 **chose no authoritative side on any of its 22 rows**, and that restraint is unaffected |
| `39:44`, `39:50` analyse session traces for recurring corrections | F-006, F-021, `M-C` | The practice gzkit's insights ledger would serve. **`M-C` already asks the sharper question** — whether the insights ledger has ever changed an outcome. Testimony describes the practice; `M-C` is the measurement |

**Two reconciliation notes.**

**It agrees with the register's principal safeguard.** The criterion's closing
sentence — *"Additional rules, artifacts, and checks are not themselves evidence
of improvement"* — is **F-032** restated from outside the investigation. F-032
is the challenge table's only unqualified `CONFIRM` and binds Phase 4 as a
filter; it now carries independent agreement from a practitioner who reached it
by different means. That is corroboration of a *method* commitment, and it is
still not evidence for any finding.

**The excerpts inherit F-022's defect.** They cite a SHA-256 of a supplied
attachment that **is not in this repository**, so neither the excerpts nor the
selection behind them can be re-derived or audited from the repo — the shape
F-022 names, *"an evidence record nobody else can retrieve is not evidence"*,
applied to this investigation's own record. It is recorded rather than repaired:
vendoring a third-party transcript is a licensing decision for the operator, and
§ Standards corpus already declines to vendor licensed texts for the same
reason. **A future reader should treat the excerpts as attributed, not as
verifiable.**

**Phase 5 pilot shape, for when authorised.** Demonstrate an initial release
within the bounded pilot, then exercise a changed requirement, a deferred item,
and a later release. Carry forward the resulting artifacts rather than resetting
to a clean example between changes. The pilot must expose whether requirement
identity and approval history remain understandable, release membership can be
reconstructed, and later changes trigger unexpected repairs or repeated requests
for settled operator decisions.

**Phase 6 evaluation.** An agent that did not author the remedy locates its
governing decisions and reconstructs the relevant requirement and release
history from the retained artifacts, without private explanations from the
designer. This exercise is separate from the completed Act 1 cold read. Record
correctness, regressions, reconstruction effort, and operator corrections
separately, with evidence pointers and the scope of each observation. Use the
information-need-first approach already proposed in `M-G`; establish a comparable
baseline before claiming improvement and record relevant differences in task,
model, and context. Reduced effort alone does not establish improved governance,
and one successful sequence does not prove general maintainability.

The evaluation feeds the existing Phase 7 **adopt / revise / reject** decision.
An inconclusive result remains inconclusive. This adds neither a review stage
nor a presumption that new registries, rules, or checks are the remedy.

### Roles

| Agent | Role |
|---|---|
| **Agent 0** | Primary investigator (Phase 1) and reconciliation lead (Phase 3) |
| **Agent 1 — Astra** | Adversarial reviewer (Phase 2). Run separately by the operator; deposits reports where its tooling puts them — the Phase 2 report is at this directory's root by operator ruling (`Q-13`), and [`raw/`](raw/README.md) states the tier |
| **Agent 2** | Later independent reader, **then** design participant — in that order (see below) |

Agent 0's lead is **procedural**: it does not make Agent 0's findings
authoritative over Agent 1's challenges. Agent 1's critique enters as **evidence
and challenge input**, not as a second canonical register merged automatically
into the first.

### How the three roles compose across phases (binding)

**The three agents are not three workers taking turns.** They are three
**positions relative to the evidence**, defined by how anchored each is:

| Agent | Position | Anchoring |
|---|---|---|
| Agent 0 | constructs | Most anchored — holds all the context, so least able to see its own assumptions |
| Agent 1 | attacks | Anchored *by Agent 0's output*; it argues on that terrain |
| Agent 2 | reads cold | Least anchored — the only one that can say whether the record stands without its authors |

Phases 1→2→3 worked because **construct → attack → reconcile** is a sequence in
which each step consumes the previous step's output — not because three agents
each took a turn. **The triad recurs only in analysis phases**, and rotating all
three through every phase would make the investigation pay its own F-023 entry
cost three times over for passes that mostly add nothing.

| Phase | Composition |
|---|---|
| 4 — design | **Full triad.** A design needs attacking *more* than findings do: it has no evidence yet, only reasoning |
| 5, 8 — pilot, migration | Execution. Agent roles barely apply; the operator runs these |
| 6 — evaluate pilot | Independence-critical — see the rule below |
| 7, 9 — adopt, measure | Operator decision, and recurring measurement |

### Phase 6 independence rule (binding)

**Agent 0 must not lead the evaluation of a pilot it designed.** Phase 6 is led
by Agent 2, or by Agent 1 — never by the agent that produced the Phase 4 design.

Whoever designs a thing cannot judge whether it worked. This is IEEE 1012
Annex C's independence point, and it is the same failure mode observed twice in
this investigation on 2026-09-22: Agent 0 used its own unsettled output as a
settled input, in `consequence-bands.md` and — as Astra independently found —
in piece 01 §§ 4, 6 and 8. **A constraint on the lead is exactly the kind that
goes unwritten unless it is written early**, which is why it is recorded here
before Phase 4 exists.

### Agent 2 sequencing constraint (binding)

**Independent reader and design participant are two jobs, and doing them in the
wrong order destroys the first.** The moment an agent has a stake in a design it
can no longer give an unanchored reading. Agent 2 therefore works in two declared
acts, in this order:

**Act 1 was taken on 2026-09-23**, by operator ruling, immediately ahead of the
Phase 3 reconciliation pass and for exactly the reason below. Its verdict —
*the register stands, with load-bearing qualifications* — and its ranked gap
list are recorded at [`act1-cold-read-2026-09-23.md`](act1-cold-read-2026-09-23.md),
with a dated disposition table separating the reading from its consequences.
**Act 1 cannot be retaken**: the register it read no longer exists in that form.

The reasoning that put it first is retained, because it will apply again to any
successor register: Act 1 is not phase-bound, the register exists, and the cold
read is *most* valuable **before** reconciliation rewrites it — what is on disk
on the day of the reading is what a newcomer would actually inherit.

**Act 1 — the cold read.** Agent 2 reads **only** this README, `FINDINGS.md`,
`DISAGREEMENTS.md`, `OPEN-QUESTIONS.md` and `consequence-bands.md`. It reads
**neither** the numbered pieces **nor** anything in `raw/`. It then answers one
question and records the answer before doing anything else:

> Can the investigation's current position be stated from the canonical register
> alone — and if not, exactly what could not be determined?

**Act 2 — design participation.** Only after Act 1's verdict is recorded may
Agent 2 read the raw record and join design work, as a **declared second role**.
**Act 2 does not exist until Phase 4 is authorised**, and Phase 4 is not
authorised. Act 1, by contrast, is available now and does not depend on Phase 2 —
reading the register cold is a test of the register, not of the findings.

**Why the order is binding.** Act 1 is the only falsifiability test the register
has. It checks whether this investigation exists durably in the repository or
still only in Agent 0's and Agent 1's context. A failed cold read is a finding
**about the register**, and the register is then what gets repaired — not the
reader. It is also the closest thing available here to genuine V&V independence:
Agent 1 read Agent 0's report and is anchored by it, whereas Agent 2 in Act 1 is
not. IEEE 1012 Annex C names this problem, and piece 01 found gzkit's honest
self-description is already the `embedded` form.

**Current gate. Phase 3 is complete as of 2026-09-23.** The Phase 2 report
arrived 2026-09-22; the reconciliation pass mapped all 25 rows of its § 2
challenge table onto `FINDINGS.md`, moved 19 statuses, and recorded eight
disagreements at `D-01` … `D-08`. Fourteen rows remain `OPEN` and **stay** there:
`Q-14` rules that `OPEN` is a **settled** disposition for a row the review never
reached. Two rows are `DISPUTED` (F-006, F-021) and **must not be read as settled
in either direction** — a disagreement recorded is not a disagreement resolved.

**Phase 4 is not authorised, and Phase 3 closing does not authorise it.** It
requires explicit operator authorisation, not an absence of objection. Nothing in
this register, and no `CONFIRMED` row, constitutes that authorisation. Operator
decisions are recorded in [`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md), including
`Q-09`'s deferral and `Q-15`'s evaluation criterion. The completed reconciliation
does not permit promotion of findings the review never reached. **Phase 4 must
not begin implicitly** — a design candidate that goes unchallenged is still not
a decision.

**Phase numbering, one caution.** Piece 01 § 12 originally titled its measurement
plan *"PROPOSED PHASE 2 INVESTIGATION PLAN"*, which meant measurement rather than
adversarial review. Those items were renumbered **`M-A` … `M-H`** on 2026-09-22
by operator ruling. A pre-2026-09-22 reference to "Phase 2" in this series may
mean the measurement program.

## Terms this series cites as binding

Two terms are cited in this register as binding constraints without being stated
in it. Both are **gzkit doctrine, not investigation vocabulary**. The authority
is the pointer; the gloss is a reading aid and is **ILLUSTRATIVE, never
authoritative** (`AGENTS.md` § Governance doctrine surfaces). Cite the authority,
not the gloss.

### IRON LAW

Cited at § Currently prohibited, at `Q-05` and on F-018.

- **The rule in force:** root `AGENTS.md` § OBPI Acceptance Protocol — *"Only the operator initiates and executes OBPI work through
  gz-obpi-pipeline."* **The rule in force does not use the name**, which is why
  searching this repository for *"IRON LAW"* finds commentary rather than canon.
- **The name, and the operator's verbatim wording:** the corpus,
  `.gzkit/corpus/AGENTS.md.jsonl`, entry
  `corpus-operator-doctrine-verbatim-canon-2026-08-23T14:33:19...`. Read it with
  the content skills; the corpus is not hand-edited.
- **Dated record of the compression:**
  [`context-audit-2026-09-12/root-doctrine.md`](../context-audit-2026-09-12/root-doctrine.md),
  which carries the original beside what landed in `AGENTS.md`.
- **Gloss, sufficient to read `Q-05`:** only the operator may *initiate* OBPI
  work, across every arm of it — claiming or releasing locks, pipeline markers,
  starting or completing TASKs, dispatching implementers or reviewers, editing a
  brief. A narrow operator-named task that happens to fall inside an OBPI's scope
  is not initiation. **It is a blanket prohibition on initiation and delegates
  nothing**, which is exactly why `Q-05` rules the 16085 consequence threshold
  *strictly weaker* rather than merely different: a threshold defines a line
  below which authority is delegated, and this rule delegates none. **Advisory —
  no mechanical witness distinguishes operator-initiated from agent-initiated
  OBPI work today**, which is itself the condition F-018 is about.

### Architectural Boundaries 1 and 2

Cited at `Q-03`, at `Q-09` and on F-006.

- **In force at:** root `AGENTS.md` § Architectural Boundaries, as six numbered items.
- **As written:** **1.** *"Do not promote post-1.0 pool ADRs into active work."*
  **2.** *"Do not add more pool ADRs to the runtime track."*
- Only 1 and 2 are cited by this series. **Boundary 6** — *"Do not let derived
  views silently become source-of-truth"* — is the one F-021 and
  [`consequence-bands.md`](consequence-bands.md) reason inside without naming,
  and a Phase 4 design touching either should read it.

---

## The measurement program — `M-A` … `M-H`

Eight findings route their disposition to a measurement item, so the items are
summarised here. **Authoritative text: [`01 § 12`](01-engineering-method-2026-09-22.md).**
The program is **proposed and not executed**, except as noted. It proposes no
implementation, and `01 § 12` closes by naming what it must not do: no
replacement taxonomy, no new lifecycle, no new tooling — *"adding machinery is
the failure mode most consistent with this repository's history."*

| Item | What it measures | Follows | State |
|---|---|---|---|
| `M-A` | What a persistent requirement object would have to carry, by classifying ~200 REQs and ~200 FAIL-CLOSED constraints against 29148 § 5.2.5/§ 5.2.6 | F-001, F-002 | proposed. **Declared open risk:** the answer may be that most REQs are correctly transient and the persistent layer must be authored fresh — a larger finding, not a smaller one |
| `M-B` | The deleted specification corpus — reconstruct the deleted briefs, classify what was lost as durable vs transient, check whether any deleted REQ is still cited by live code, a test or a `@covers` | F-003 | proposed. Settles `D-03` |
| `M-C` | Whether the six intake surfaces can be reduced, by tracing where sampled items actually end up; duplication and mortality across surfaces | F-006 | proposed. Bears on `D-01` |
| `M-D` | The claim behind each gate and each enforcement claim, in 15026-2 § 5.3.3 form, and whether a non-agent witness exists | F-019, F-021 | proposed, **gated on its own method problem** — the prior audit disqualified itself as *"a stochastic surface auditing a stochastic surface."* Highest-risk item. Bears on `D-05` |
| `M-E` | Whether an architecture description is warranted, or whether extending `gz drift`/`gz covers` reaches the same property more cheaply | F-013 | proposed. **Declared bias:** the correspondence route is likely cheaper and should be tested first |
| `M-F` | The real duplication between Gate 4 and Gate 2 — run behave with coverage instrumentation against the unit suite, and count the behave-only REQs | *(no finding — see below)* | **EXECUTED 2026-09-23** — [`03`](03-gate4-gate2-duplication-2026-09-23.md). **This is the home of `D-08`**, whose disposition it does NOT move |
| `M-G` | Baselines for the metrics Phase 1 could measure only once, each stated as an information need before a measure (15939 § 6.2 b) | F-025 | proposed. Settles `D-04` |
| `M-H` | Consequence bands, defined **with the operator** — *"cannot be done by an agent alone"* | `Q-04` | **DISCHARGED 2026-09-22** — [`consequence-bands.md`](consequence-bands.md), authored live with the operator. Still `PROVISIONAL` |

**Sequencing, from `01 § 12`:** `M-A`, `M-B` and `M-C` are independent and may run
concurrently. `M-D` must not start until its method problem is settled. `M-E`
depends on `M-A`. `M-G` depends on `M-H`, which is discharged. `M-F` is
independent, and is executed.

**Two things this table makes visible that the register previously could not.**
`M-F` **exists** and is the measurement home for the BDD-duplication claim that
never became a finding — recorded at `DISAGREEMENTS.md` `D-08` as a challenge
with nothing to land on. And `M-H` is **already discharged**, so the program is
7/8 outstanding rather than 8/8; nothing in the register said so.
*(Amended 2026-09-23: `M-F` has since been executed — piece
[`03`](03-gate4-gate2-duplication-2026-09-23.md) — so the program now stands at
**6/8 outstanding**.)*

---

## Reading posture

These are **dated records**, in the sense `docs/governance/` already uses (see
[`config-derivation-census-2026-09-20.md`](../config-derivation-census-2026-09-20.md)).
A value written in the prose is ILLUSTRATIVE, never authoritative
(`AGENTS.md` § Governance doctrine surfaces). Each piece pins the commit it was
measured against and ships a re-runnable script beside it; the script carries no
literals from its authoring date, so re-running it reports whatever tree it is
given rather than confirming a transcribed figure.

Findings are classified **KEEP** / **REFINE** / **ADD** / **REMOVE**, and nothing
is classified merely because a standard contains it.

**The numbered pieces are frozen at their date; the canonical register is
not.** [`FINDINGS.md`](FINDINGS.md), [`DISAGREEMENTS.md`](DISAGREEMENTS.md) and
[`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md) are living documents amended in place
with dated notes — the shape [`advisory-rules-audit.md`](../advisory-rules-audit.md)
already uses. A piece is corrected only by a later piece saying so.

These records are analysis, not canon. Nothing here binds until it is carried
into a rule, an ADR, or the corpus by the ordinary route. Where a piece
disagrees with an earlier piece, the later one says so explicitly rather than
silently superseding it.

## Pieces — raw investigation record

Historical. Subordinate to [`FINDINGS.md`](FINDINGS.md); read it first.

| # | Piece | Subject | Measured at |
|---|-------|---------|-------------|
| 01 | [Engineering-method assessment](01-engineering-method-2026-09-22.md) | Whole-system pass: the engineering ontology, persistent versus transient knowledge, traceability, the OBPI as a work package, agent entry and exit cost | `6a0e5241e` |
| 02 | [Requirements engineering versus release management](02-requirements-vs-release-2026-09-22.md) | The identifier seam: decision identity, requirement identity and release identity sharing one semver namespace; baselines as the missing bridge object | `be663409a` |
| 03 | [What Gate 4 actually adds over Gate 2](03-gate4-gate2-duplication-2026-09-23.md) | Measurement item `M-F`: behave and unittest run under identical coverage instrumentation, the behave-only line and REQ residue, and what retiring Gate 4 would actually cost | `43d63da8d` |

## Standards corpus

Twenty-four standards, read at clause level. Not summarized — used selectively
to answer concrete questions raised by the repository.

| Area | Standards |
|------|-----------|
| Lifecycle and systems context | ISO/IEC/IEEE 12207:2026, 15288:2023, 24748-1:2024, 24748-2:2024, 24748-3:2020, 24748-6:2023, 24748-10:2026, 24765:2017 |
| Requirements and engineering information | ISO/IEC/IEEE 29148:2018, 15289:2019 |
| Architecture | ISO/IEC/IEEE 42010:2022, 42020:2019, 42030:2019 |
| Verification and assurance | IEEE 1012-2024, IEEE 730-2026, ISO/IEC/IEEE 15026-2:2022 |
| Testing | ISO/IEC/IEEE 29119-1:2022, 29119-2:2021, 29119-3:2021, 29119-4:2021 |
| Engineering management | ISO/IEC/IEEE 15939:2017, 16085:2021, 16326:2019 |
| Delivery and operations | ISO/IEC/IEEE 32675:2022 |

The standards texts themselves are **not** vendored into this repository; they
are licensed documents. Pieces cite standard, clause and a paraphrase, and quote
only where exact wording carries the argument.

## The three permissions that shape the whole series

Read these before proposing that gzkit adopt anything, because they bound what
adoption can even mean:

- **Information, not documents.** ISO/IEC/IEEE 15289:2019 § 5.1 (*shall*) holds
  that information items conform when unpublished but available in a repository,
  divided across documents, or combined into one; § 3.1.11 defines "include" as
  having the information **or a reference to it**. ISO/IEC/IEEE 29148:2018
  Clause 7 and 29119-3:2021 § 4.1.1 say the same for requirements and test
  information. A ledger with a derived view conforms exactly as a document set
  does.
- **A mandated process is not a mandated artifact.** 15289 § 8.2: a definition
  "does not in itself indicate that a specific information item is produced",
  and clauses requiring planning "do not necessarily mean that a documented plan
  is produced."
- **Fewer processes, honestly discharged, beats more processes diluted.**
  12207:2026 § 4.3 prefers full conformance to a smaller declared process set
  over tailored conformance to a larger one. ISO/IEC/IEEE 32675:2022
  § 6.3.1.3 b) 4) goes further and requires enabling change through "compact
  low-dependency scopes, **low gates**, low overhead."

## Handoff — for an agent joining now

Read this section plus [`FINDINGS.md`](FINDINGS.md), and
[`DISAGREEMENTS.md`](DISAGREEMENTS.md), [`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md)
and [`consequence-bands.md`](consequence-bands.md) as needed. That is enough;
**you do not need to replay Phase 1 or Phase 2.** This set is exactly Agent 2's
Act 1 reading list — if you are Agent 2, stop at its boundary and do not open the
numbered pieces or `raw/`.

**What is confirmed.** Two rows: F-032 (most of the standards' machinery should
not be adopted here) and F-033 (conformance is dischargeable by reference). Both
carry the challenge table's only affirmative verdicts. Fifteen rows are
`QUALIFIED` — survived in narrowed form, with the narrowing on the row — and
fourteen are `OPEN`, which under `Q-14` means **stated with evidence and never
reached by the review**: settled, and not promotable.

**What is disputed.** Two findings, both load-bearing: **F-006** (does a
persistent system model exist, or only fragments) and **F-021** (can the system
retire what it detects). Eight entries are recorded at `D-01` … `D-08` in
[`DISAGREEMENTS.md`](DISAGREEMENTS.md), three of them `A0 CONCEDES` and three
`MISSING EVIDENCE`. `D-08` records a challenge with **no finding to land on** —
evidence that the seeding of `FINDINGS.md` from the pieces was not exhaustive.

**What is decided.** Operator questions and their rulings are recorded in
[`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md); `Q-09` is deferred. `Q-15` adopts the
[successive-change evaluation criterion](#success-across-successive-changes)
for later design, pilot, and independent evaluation. Carry that criterion into
Phases 4–6 when authorised; its adoption does not open those phases.
`Q-16` records FDAU as the investigation's origin and retains the
[separation hypothesis](#investigation-origin-and-retained-hypothesis-fdau).
Carry its explicit comparison and disposition forward alongside `Q-15`; retaining
it does not select a remedy or authorise Phase 4.

**What remains unmeasured.** The proposed `M-A` … `M-E` and `M-G` measurements
and the successive-change pilot. `M-H` is discharged, with its scores still
provisional; `M-F` is executed at piece
[`03`](03-gate4-gate2-duplication-2026-09-23.md) and settles less than its
headline suggests — it bounds Gate 4's *line* redundancy and leaves the
assertion-level question `D-08` raises untouched. Operator rulings do not
establish empirical findings.

**What must not be assumed:**

- **Do not assume the central hypothesis is settled.** That persistent knowledge
  should leave the work package (F-001) is the investigation's leading finding
  and is `QUALIFIED`, not established.
- **Do not assume long OBPI duration has a known cause.** F-025 lists eleven live
  candidate explanations and attributes duration to none of them. Converging early
  is the most likely way this investigation goes wrong.
- **Do not assume a finding implies its remedy.** Findings stop at what is;
  remedies are Phase 4.
- **Do not assume a standard's presence is an argument.** F-032 and F-033: most of
  this corpus should not be adopted, and conformance is dischargeable by reference.
- **Do not assume the numbers are current.** Every figure is a dated observation.
  Re-run the command or the script.
- **`F-###` ids are ratified** (`Q-11`, ruled 2026-09-22, confirmed
  2026-09-23). Allocated in order, never reused, stable across phases. Cite them
  freely.

**Currently prohibited:**

- Beginning Phase 4 design. It is not authorised.
- Promoting any finding to `CONFIRMED` that the Phase 2 review did not reach.
  The review is read and reconciled; a row it never challenged is still
  unchallenged.
- Creating an ADR, OBPI, REQ or TASK from anything in this directory.
- Treating a design candidate as a decision, or this register as doctrine.
- Editing the numbered pieces other than by a dated amendment.
- **Agent 2 reading the numbered pieces or `raw/` before its Act 1 cold read is
  recorded.** The reading is worthless once anchored, and it cannot be retaken.
- **Retiring or replacing the five-gate vocabulary.** Standing operator
  constraint, 2026-09-22: *"do not abandon the five gates without a discussion
  with me."* This binds Phase 4 designs too, including as a side effect.
- **Re-proposing the 16085 consequence threshold** as a replacement for the
  IRON LAW. Ruled against at `Q-05`, as weaker rather than merely different.
- Promoting `ADR-pool.feature-adr-semver-discipline` before the `kind` guard
  lands (`Q-09`).

**Next permitted step: none without operator authorisation.** Phase 3's stop
condition — every row carrying a settled status, and the disagreements recorded —
was met on 2026-09-23. **Phase 4 requires explicit operator authorisation**, not
merely an absence of objection, and the full triad when it opens. Work that
remains available *without* entering Phase 4: the measurement program `M-A` …
`M-H` (`M-H` discharged, `M-F` executed, six outstanding), and the two open register questions
— whether findings should be authored for `D-08` and for the three independently
observed `D2` rows.

## Relationship to gzkit's own engineering artifacts

One-directional. **Findings are inputs; nothing in this directory is an output of
the governance pipeline, and nothing here creates one.**

- No ADR, OBPI brief, REQ or TASK is created by this investigation. A Phase 4
  decision leaves by the ordinary route — `gz-design` → ADR → OBPI — and only the
  operator initiates that work (`AGENTS.md` § OBPI Acceptance Protocol).
- A defect noticed here routes by `AGENTS.md` § Defect-fix routing like any
  other. Being named in a finding neither authorises nor blocks its repair.
- Nothing here is Layer 1 canon or Layer 2 ledger. These are analysis documents;
  `.gzkit/ledger.jsonl` remains the system of record
  ([`state-doctrine.md`](../state-doctrine.md)).
- Findings are **not** requirements. They carry no proof channel, no `@covers`
  binding and no gate.

## Related

- [`docs/governance/state-doctrine.md`](../state-doctrine.md) — the L1/L2/L3 layers these pieces reason about
- [`docs/governance/trust-doctrine.md`](../trust-doctrine.md) — trust-chain poisoning, gzkit's own rediscovery of V&V independence
- [`docs/governance/advisory-rules-audit.md`](../advisory-rules-audit.md) — the Mechanical/Judgment scorecard the pieces read as an honesty instrument
- [`docs/governance/req-scope-discipline.md`](../req-scope-discipline.md) — the three-kind REQ taxonomy and the measurement that produced it

---

## Amendments

- **2026-09-23 — `M-F` executed; piece [`03`](03-gate4-gate2-duplication-2026-09-23.md) added.**
  The first measurement item run by an agent alone (`M-H` was run with the
  operator). Both suites instrumented identically, subprocess capture enabled on
  both sides so the ten subprocess-driving step files were not scored as reaching
  nothing. **Headline: the unit suite already covers 98.9% of every line behave
  reaches, and 47 of 74 feature files add no reach at all.** Five of `01
  § 8.3`'s six transcribed figures verify; the behave-only REQ count is 55 rather
  than ~54, and *"restates the unit file name-for-name"* is literally false and
  should not be re-cited. **The result is deliberately one-sided and says so:**
  line coverage cannot see a different assertion over the same line, which is
  exactly Phase 2's challenge at `D-08`, so `D-08` keeps `MISSING EVIDENCE` and
  no finding was authored. Two sub-results stand on their own terms — the 35
  `@wip` scenarios prove nothing not already `@covers`-ed, and
  `subagent_pipeline.feature` adds neither a line nor a REQ tag. `M-F`'s state
  moved to EXECUTED in § The measurement program; the program is 6/8 outstanding.
- **2026-09-23 — FDAU origin and separation hypothesis retained (`Q-16`).**
  Recorded the operator's account of why the IEEE investigation began, pinned
  the comparison sources, and linked explicit consideration through the phase
  and handoff paths. Preserved the useful work-package idea and the proposed
  separation without adopting a schema, changing findings, or opening Phase 4.
- **2026-09-23 — Dex Horthy deposit reconciled against the register.**
  § Success across successive changes gains **Where the testimony lands in the
  register**: each excerpt mapped to the F-### or `M-` item it bears on, with the
  bears-on / evidence-for distinction stated per row. The deposit's own boundary
  claim was **verified mechanically** — the status distribution is unchanged
  across 35 rows — rather than accepted on its word. Two notes recorded: the
  criterion independently agrees with **F-032**, the register's only unqualified
  `CONFIRM`; and the excerpts cite a source not present in the repository, so
  they inherit **F-022**'s retrievability defect and are attributed rather than
  verifiable. **No finding status changed and no row gained evidence.**
- **2026-09-23 — evaluation ruling propagated after operator check.** The
  operator asked *"did you update where needed?"*. The first update had recorded
  the decision here but omitted `OPEN-QUESTIONS.md`. Added `Q-15` there and
  linked it from the phase table, criterion, and handoff reading path. Removed
  stale current-state prose that described ruled questions as unknown and the
  completed reconciliation as awaiting execution. Historical amendments remain
  dated records. No finding or phase authorisation changed.
- **2026-09-23 — successive-change evaluation adopted by g0.** Operator:
  *"okay, let's do that then"*, accepting the proposed success criterion and
  pilot approach following the Dex Horthy transcript discussion. Added
  § Success across successive changes and retained timestamped source excerpts
  in `raw/`. The lessons are evaluation questions, not new findings. Phase 4–9
  authorisation, Phase 6 independence, the five gates, and finding statuses are
  unchanged.
- **2026-09-23 — Phase 3 recorded complete (`Q-14`).** The phase table, § Current
  gate, § Next permitted step and § Handoff updated. **No finding changed status
  and nothing was promoted**: the fourteen `OPEN` rows stay `OPEN`, and the
  ruling is about what `OPEN` *means*, not about what those rows assert. The
  `CONFIRMED` bar is unchanged and still requires that the review reached a row.
  **The Phase 4 bar is restated rather than relaxed**, in § Current gate and
  § Next permitted step, because a phase closing is the most likely moment for
  the next one to be read as open. It is not.
- **2026-09-23 — three cold-read gaps closed.** § Roles corrected: it said Astra
  deposits into `raw/`, against `Q-13`'s ruling that the Phase 2 report stays at
  this directory's root. **§ The measurement program added** — `M-A` … `M-H`
  summarised from `01 § 12`, which the five canonical files previously never
  reached, leaving eight findings routing to items a reader could not evaluate
  (cold-read gap 2). Two facts surfaced by writing it: **`M-F` exists** and is
  the home of `D-08`, and **`M-H` is already discharged** by
  `consequence-bands.md`. The evidence directory is added to the file table as
  **tooling** rather than narrative (cold-read gap 8): a re-derivation script
  holds no conclusions, so reading it cannot anchor a future Act 1 the way a
  report would. **That last point narrows a binding reading list and the operator
  may overturn it** — § Agent 2 sequencing constraint still bars the numbered
  pieces and `raw/`, and only the script is at issue.
- **2026-09-23 — Agent 2's Act 1 cold read recorded** at
  [`act1-cold-read-2026-09-23.md`](act1-cold-read-2026-09-23.md), historical
  tier, and added to the file table; § Agent 2 sequencing constraint updated to
  say Act 1 was taken and cannot be retaken. **Act 2 is unchanged and still does
  not exist until Phase 4 is authorised.** The reading was taken by an isolated
  agent holding no prior context, dispatched because the main session was already
  anchored by the handoff chain — the caveat is recorded in the record itself.
  Written up because its verdict had existed only in session memory while its
  consequences were already landed in the register: **F-007 happening to this
  investigation**, caught before the session ended.
- **2026-09-23 — § Terms this series cites as binding added.** Agent 2's Act 1
  cold read could not evaluate `Q-05` because **IRON LAW** is cited four times
  across this register and stated nowhere in the five canonical files; the same
  held for **Architectural Boundaries 1 and 2**, cited as binding at `Q-03`,
  `Q-09` and F-006. Both are now pointed at their authority. **The cause is worth
  keeping:** the rule in force in `AGENTS.md` does not carry the name *IRON LAW*,
  so a reader searching for the name finds commentary and a reader reading
  `AGENTS.md` finds the rule without the name — the operator's own standing
  caution that *"a search is not a read"* and that doctrine is routinely stated as
  a flag value or a path rather than as the prose being searched for. No rule was
  restated as authority here; the glosses are marked ILLUSTRATIVE.
- **2026-09-23 — `Q-11` and `Q-12` recorded.** § What must not be assumed had
  told readers not to assume `F-###` was ratified; it had been ratified on
  2026-09-22, and the line is replaced with the ruling. `Q-12` is confirmed:
  Phase 4 design candidates will live in `design-candidates.md` in this
  directory, tiered below `FINDINGS.md`, **created when Phase 4 is authorised**
  — so § Currently prohibited's bar on beginning Phase 4 design is unaffected,
  and no empty container is created ahead of it.
- **2026-09-22 — Phase 3 reconciliation pass recorded.** § Current gate,
  § Next permitted step, § Handoff (*what is confirmed*, *what is disputed*) and
  the `CONFIRMED` prohibition updated to the post-reconciliation state. **The
  prohibition was narrowed, not lifted:** it now forbids promoting a row the
  review never reached, which is the condition that actually bears after the
  report has been read. **This also settles, in one direction, the contradiction
  flagged below** — this file and `DISAGREEMENTS.md` previously stated two
  different gate conditions on promotion to `CONFIRMED`. The operator may
  overturn the reading.
- **2026-09-22 — Act 1 cold-read repair pass (mechanical only).** § Current gate's
  orphaned *"Until then"* — editing residue with no antecedent, inside a binding
  paragraph — reworded to name the reconciliation pass it was describing. **No
  prohibition was added, removed or relaxed.** This section is new; changes to
  this file were previously unrecorded. **Unresolved, left for the operator:**
  § Handoff states the Phase 2 report *"has not been read"*, against this file's
  own phase table and `DISAGREEMENTS.md` § Status; § Currently prohibited gates
  promotion to `CONFIRMED` on the report being read while `DISAGREEMENTS.md`
  gates it on that file being populated; § What must not be assumed records
  `F-###` as unratified against `Q-11`'s ruling; § Roles says Astra deposits into
  `raw/` against `Q-13`'s ruling that the report stays at the directory root; and
  **IRON LAW** and **Architectural Boundaries 1 and 2** are cited as binding
  here without being stated, quoted or pointed at anywhere in the five canonical
  files.
