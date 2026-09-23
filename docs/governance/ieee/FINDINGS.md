<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Canonical findings — engineering-method assessment

> **Tier: canonical within the investigation; not doctrine.** This register is
> what the investigation currently accepts as supported. It binds nothing. Per
> [`README.md`](README.md), nothing here takes effect until it is carried into a
> rule, an ADR, or the corpus by the ordinary route.
>
> **This is a living register**, amended in place with dated notes — the shape
> [`advisory-rules-audit.md`](../advisory-rules-audit.md) already uses. The
> numbered pieces are frozen dated records; this file is not.
>
> **Figures are ILLUSTRATIVE, never authoritative** (`AGENTS.md` § Governance
> doctrine surfaces). Every row cites the piece § that holds the measurement and,
> where one exists, the command or script that re-derives it. Prefer re-running
> it to trusting a number transcribed here.

**Seeded 2026-09-22 (Phase 3) from pieces 01 and 02.**

---

## How to read a status

| Status | Meaning |
|---|---|
| `CONFIRMED` | Stated with evidence, exposed to adversarial challenge, and surviving with its evidence intact |
| `QUALIFIED` | Survives in narrowed or corrected form; the narrowing is recorded on the row |
| `DISPUTED` | A challenge stands unresolved. The disagreement is carried in [`DISAGREEMENTS.md`](DISAGREEMENTS.md) |
| `OPEN` | Stated with evidence, and **not reached by the adversarial review**. A **settled** disposition, not a waiting one (`Q-14`, ruled 2026-09-23): the row cannot be `CONFIRMED`, because nothing challenged it, and nothing is outstanding against it either |
| `REJECTED` | Withdrawn. Retained only where a future investigator could otherwise re-derive it |

**`CONFIRMED` requires that the adversarial review actually reached the row.**
Fourteen rows are `OPEN` because Astra reviewed pieces 01 and 02 rather than this
register and declared its review non-exhaustive; `Q-14` rules that this is a
settled disposition, not an outstanding one. Promoting such a row would make the
status word mean nothing. Promoting a Phase 1 finding to `CONFIRMED` before its
challenge has been read would make the status word mean nothing.

**`settled` and `ruled` are different words here, and the difference is
binding.** A finding's **status** is about *evidence*: `settled` describes how
far its disposition has been carried by observation and challenge. An operator
**ruling** answers a `Q-##` — a question about what to do — and says nothing
about whether the finding's evidence survived. **The two are orthogonal**, so a
row may be `OPEN` or even `DISPUTED` and carry a ruling at the same time: F-006
is `DISPUTED` on the evidence and ruled at `Q-03`. Never write that a `Q-##` is
*settled*; write that it is **ruled**. Never write that a finding is *ruled*;
write that its evidence is `OPEN`, `QUALIFIED`, `CONFIRMED`, `DISPUTED` or
`REJECTED`. The `Ruling` column in the index carries the `Q-##`, where one
exists.

`Class` is the series' own disposition vocabulary — **KEEP / REFINE / ADD /
REMOVE** — and is orthogonal to status. Status says how well supported a finding
is; class says what it argues for. A finding can be `OPEN` and `KEEP`.

**Identifier convention.** Flat, series-global `F-###`, allocated in order,
never reused, stable across phases. No prior `F-###` convention existed in this
repository; this one was **ratified by the operator** at `Q-11`
([`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md) § Meta), ruled 2026-09-22 and
confirmed 2026-09-23 against the namespaced and per-piece alternatives.

---

## Index

| ID | Finding | Status | Class | Ruling |
|---|---|---|---|---|
| | **A — The persistent / transient boundary** | | | |
| F-001 | Persistent engineering knowledge is carried by transient work packages | QUALIFIED | REFINE |  |
| F-002 | Requirement and constraint identity is a coordinate inside the work package | QUALIFIED | REFINE |  |
| F-003 | ADR demotion destroys specification | QUALIFIED | REFINE | Q-01 |
| F-004 | Roughly 10% of a brief is durable engineering knowledge; the rest is work log | OPEN | REFINE |  |
| F-005 | The work package has accumulated responsibilities, in the template | QUALIFIED | REFINE |  |
| F-006 | Six intake surfaces each carry part of a system model that exists nowhere | DISPUTED | ADD | Q-03 |
| F-007 | Transient matter is accumulating inside durable stores | OPEN | REFINE | Q-06 |
| | **B — Identity, traceability and the release seam** | | | |
| F-008 | Decision, requirement and release identity share one semver namespace | OPEN | REFINE | Q-08 |
| F-009 | No requirement revision counter exists | OPEN | ADD |  |
| F-010 | No requirements baseline; the freeze mechanism exists and is aimed elsewhere | OPEN | ADD |  |
| F-011 | Requirements are governed by continuous reconciliation | OPEN | REFINE |  |
| F-012 | Traceability is one leg of the five 29148 names | QUALIFIED | ADD |  |
| F-013 | No architecture description in the 42010 § 6 sense | OPEN | ADD |  |
| F-014 | The PRD is inert; product-intent traceability was practised once | QUALIFIED | REFINE | Q-02 |
| F-015 | No release record; the ledger cannot reconstruct a release | OPEN | ADD | Q-10 |
| F-016 | Identifier renameability funds a large standing machinery cost | OPEN | REMOVE |  |
| F-017 | Two coverage numbers disagree with no reconciling statement | QUALIFIED | REFINE |  |
| | **C — Enforcement and evidence** | | | |
| F-018 | Jurisdiction is declared in prose and refused by nothing | QUALIFIED | REFINE | Q-05 |
| F-019 | Gates record exit codes where the covenant promises claims | QUALIFIED | REFINE | Q-07 |
| F-020 | Documentation and implementation disagree at 22 measured points | QUALIFIED | REFINE |  |
| F-021 | The system finds its own facades honestly and cannot retire them | DISPUTED | ADD |  |
| F-022 | Evidence records are incomplete as evidence | OPEN | REFINE |  |
| | **D — Cost and accumulation** | | | |
| F-023 | Agent entry cost is dominated by procedure, not by the problem | QUALIFIED | REFINE |  |
| F-024 | Governance prose outweighs source code several-fold | OPEN | REFINE |  |
| F-025 | Work-package duration and the collapse of pipeline throughput | QUALIFIED | — |  |
| F-026 | A long release stall that no gate can see | OPEN | ADD |  |
| | **E — Strengths** | | | |
| F-027 | The REQ→test correspondence machinery, with violation recording | QUALIFIED | KEEP |  |
| F-028 | The anti-tautological-test stack is ahead of the testing standard | QUALIFIED | KEEP |  |
| F-029 | The REQ-kind taxonomy independently rediscovers the verification-method split | QUALIFIED | KEEP |  |
| F-030 | Path-scoped agent rules with real runtime enforcement | OPEN | KEEP |  |
| F-031 | `RELEASE_NOTES.md` is load-bearing, not duplication | OPEN | KEEP |  |
| | **F — Method boundary** | | | |
| F-032 | Most of the standards' machinery should not be adopted here | CONFIRMED | — |  |
| F-033 | Conformance is dischargeable by reference, not by document | CONFIRMED | KEEP |  |
| | **G — Retired readings** | | | |
| F-034 | *Parked OBPIs indicate stalling work* | REJECTED | — |  |
| F-035 | *The four-baseline scheme is acquisition bureaucracy* | REJECTED | — |  |

---

## A — The persistent / transient boundary

### F-001 — Persistent engineering knowledge is carried by transient work packages

- **Status:** QUALIFIED · **Class:** REFINE
- **Observation.** The OBPI brief is not merely a carrier of durable engineering
  knowledge; for requirements and constraints it is the only place that knowledge
  exists. There is no REQ registry and no constraint registry. The one designated
  durable home for system invariants, `## Boundary Invariants`, is present on 23
  of 372 ADRs.
- **Evidence.** `01 § 4.4` (the wrong-side-of-the-boundary table), `01 § 6`,
  `01 § 2` (object inventory). Re-derive brief section shares from the briefs
  under `docs/design/adr/**/obpis/`.
- **Interpretation.** This is the investigation's central hypothesis and the
  finding every other finding in group A depends on.
- **Qualification (piece 02, 2026-09-22).** Piece 01 said requirements "have no
  durable owner." That was imprecise in a way that mattered: **they have an
  owner, and it is the wrong one.** The release plan owns them, and a
  release-scope decision destroys them. An absent owner and a wrong owner imply
  different remedies, so the sharpened form is the one that stands.
- **Standards lens.** 16326:2019 § 7.3.1.1 (*shall*) — a project plan shall
  provide "a reference to the official statement of product requirements."
  12207:2026 Annex B Table B.1 types requirements and traceability mappings as
  `artefact`, initiated in one process and revised in others.
- **Consequence.** Knowledge is destroyed on a schedule set by work-package
  lifecycle rather than by system lifecycle. See F-003 for the measured loss.
- **Phase 2 challenge (Astra, 2026-09-22) — DOWNGRADE TO HYPOTHESIS, on the causal claim.** Challenge-table row *"§6: Persistent knowledge in OBPI explains long duration"*: *"No causal test; created-to-completed mixes queue and execution."* Counterevidence: one OBPI open more than 33 days completed **3.25 hours after its first lock** [E2] — elapsed time is not work time. Alternatives offered: authorization/sequence waiting, scope coupling, churn. **The placement observation is not challenged; the explanatory claim built on it is.** Astra's §1 records that piece 01 postponed this classification to its own measurement item while treating the answer as settled in §§ 4, 6 and 8 — the same discipline failure the operator caught independently. Carried as `D-04`.
- **Disposition.** Not a design decision. The remedy shape is named normatively
  by the standard, but which object carries persistent identity is `M-A`.

### F-002 — Requirement and constraint identity is a coordinate inside the work package

- **Status:** QUALIFIED · **Class:** REFINE
- **Observation.** `REQ-<adr-semver>-<obpi-NN>-<req-NN>` encodes the requirement's
  parentage in its identity, so it cannot outlive the work package that
  introduced it. Constraints are worse off: the FAIL-CLOSED population is the
  largest requirement-shaped population in the repository and the least
  identified.
- **Evidence.** `01 § 2`, `01 § 4.4`, `01 § 5.2`; one consolidated REQ grammar at
  `src/gzkit/triangle.py:24-31`. Re-derive with `uv run gz covers` and
  `uv run gz drift`.
- **Interpretation.** The identifier grammar is sound and globally unique. What
  is wrong is ownership, not syntax — which makes this cheaper to correct than it
  looks.
- **Standards lens.** 29148:2018 § 5.2.8.2 pairs an immutable identity with a
  separate mutable version number; 12207 § 6.4.3.3 (*shall*) requires traceability
  maintained "Through the life cycle."
- **Consequence.** Traceability questions (a), (d) and (h) in `01 § 5.1` are
  unanswerable, and the loss in F-003 is structural rather than incidental.
- **Phase 2 challenge (Astra, 2026-09-22) — REJECT, on the stated form.** Challenge-table row *"§2/§8: Hierarchical IDs cannot outlive work packages"*: *"Logical assertion, not observed property of the grammar"*, and *"Contradicted by 29148's permitted relational identity"* [S2]. Counterevidence: *"The parser accepts an ID independently; storage lookup and deletion govern discoverability"* [E6]. **This register concedes the stated form**, because its own Interpretation above already says the grammar is sound and the defect is ownership rather than syntax — the Observation's *"cannot outlive"* overstated what the Interpretation claimed. **Surviving claim:** lifecycle and storage policy, not the identifier grammar, is what destroys a requirement's discoverability. Carried as `D-02`.
- **Disposition.** `M-A` decides whether the persistent object is a subset of
  today's REQs or a different object. **Piece 01 declares an open risk here:**
  most REQs may be correctly transient, which would be a larger finding, not a
  smaller one.

### F-003 — ADR demotion destroys specification

- **Status:** QUALIFIED · **Class:** REFINE
- **Observation.** `gz adr demote` executes `shutil.rmtree(source_dir)`, deleting
  the ADR package including `obpis/`. Measured across git history, a large
  fraction of all REQ acceptance criteria and FAIL-CLOSED constraints ever
  authored in this repository has been deleted this way. The surviving pool file
  retains the ADR's prose and zero REQ identifiers.
- **Evidence.** `src/gzkit/commands/adr_demote.py:475`; `01 § 1.2(c)`, `01 § 4.4`,
  `01 § 6`. Re-derive with `git log --diff-filter=D` over brief paths.
  `src/gzkit/obpi_lifecycle.py:256-260` names a worse case in its own comment:
  demoting an already-parked parent deletes every brief while emitting no park
  events — *"A hollow exit 0."*
- **Interpretation.** The knowledge did not migrate to a model. It went to git
  history, which no tool in this repository reads as a specification source.
- **Standards lens.** 12207 § 6.4.3.3 (*shall*), traceability through the life
  cycle.
- **Consequence.** Piece 02 measures live behave scenario tags pointing at briefs
  that no longer exist, so the loss has already produced dangling references.
- **Ruled 2026-09-22 (operator).** `Q-01` answered: **unexamined consequence.** The delete is collateral, not design, so this is a **defect**, not a premise. Demote should archive rather than delete; `M-B` characterises the loss.
- **Phase 2 challenge (Astra, 2026-09-22) — DOWNGRADE TO HYPOTHESIS.** Challenge-table row *"§1/§4/§6: Deleted briefs demonstrate loss of 39% of enduring requirements"*: *"Deletion count is real; durability and causal attribution are unclassified"*, and the 16326 inference is called invalid. Counterevidence: *"364 of 384 deletion events cluster in two deliberate demotion campaigns, largely unstarted work"* [E1]. **The deletion is confirmed; what was deleted is not classified.** The share of the deleted population that was durable engineering knowledge rather than retired backlog is unmeasured on both sides — `M-B`'s question exactly. The operator's `Q-01` ruling that the delete is collateral rather than designed is unaffected by this challenge. Carried as `D-03`.
- **Disposition.** Whether this was intended is `Q-01` — and the answer decides
  whether it is a defect or a premise. `M-B` would characterise what was lost.

### F-004 — Roughly 10% of a brief is durable engineering knowledge; the rest is work log

- **Status:** OPEN · **Class:** REFINE
- **Observation.** Across all live briefs, `## Acceptance Criteria` and
  `## Requirements (FAIL-CLOSED)` together are about a tenth of brief content.
  `## Evidence` alone is roughly a quarter. In the largest brief, Acceptance
  Criteria is 19 lines against 1,048 lines of Evidence.
- **Evidence.** `01 § 6` (section inventory across 556 briefs).
- **Interpretation.** The ratio is the finding, not the absolute size. A work
  package whose durable content is a tenth of its bulk imposes the other
  nine-tenths on every reader of the durable part.
- **Standards lens.** 16326 § 7.7.3.2 (`should`) — a work package specifies
  resources, duration, work products, acceptance criteria and dependencies. It
  does **not** specify requirements.
- **Consequence.** Feeds F-023: the brief is a small share of agent entry cost,
  and a small share of the brief is the actual specification.
- **Phase 2 note (Astra, 2026-09-22) — not directly challenged.** The challenge-table row covering brief overload confirms *"Template growth and mixed content are direct observations"* while disputing the inference (see F-005). The section-share ratio measured here is not contested, and no counterevidence is offered against it. Status unchanged: Astra's review was scoped to pieces 01 and 02 and is explicitly non-exhaustive, so silence on a row is not survival of it.
- **Disposition.** Follows F-001. No separate decision.

### F-005 — The work package has accumulated responsibilities, in the template

- **Status:** QUALIFIED · **Class:** REFINE
- **Observation.** `src/gzkit/templates/obpi.md` grew roughly fivefold in lines
  and doubled in sections over eight months. Briefs at birth grew on the same
  curve, while post-birth growth stayed modest.
- **Evidence.** `01 § 6`; `git log` over `src/gzkit/templates/obpi.md` and
  `git log --diff-filter=A` over brief paths.
- **Interpretation.** Because growth is at birth and not after, **the accumulation
  is in the template, not in evidence accrual.** The work package was given more
  responsibilities; it did not acquire them by doing more work. This distinction
  matters for F-025, where "briefs got bigger" is a candidate explanation for
  duration.
- **Standards lens.** 16326 § 7.7.3.2, as above — five of the brief's concerns
  (planning, specification, implementation, repair, assurance) sit in one
  document.
- **Consequence.** Every increment pays for sections it does not use.
- **Phase 2 challenge (Astra, 2026-09-22) — CONFIRM WITH QUALIFICATION.** Challenge-table row *"§6: OBPI is overloaded and template responsibilities grew"*: *"Template growth and mixed content are direct observations"*, but *"Standards do not prohibit mixed artifacts."* Counterevidence: *"Briefs deliberately retain closure rationale; acceptance criteria and plans are not categorically incompatible"* [E2]. Alternative: *"Required ceremony grew; selection could reduce reading without splitting storage."* **The growth measurement stands; the inference that the mixing is itself the defect does not.** This bears directly on Phase 4: reducing what a reader must read is separable from splitting where content is stored.
- **Disposition.** Open. Reducing the template is a design candidate, not a
  finding.

### F-006 — Six intake surfaces each carry part of a system model that exists nowhere

- **Status:** DISPUTED · **Class:** ADD
- **Observation.** Pool ADRs, GitHub issues, the insights ledger, chores, the
  campaign plan and handoffs each hold part of the project's durable knowledge.
  **No surface is a backlog *against* a model, because no surface holds the
  model.** Risk and research-question have no home at all.
- **Evidence.** `01 § 2` (object inventory), `01 § 4.4`, `01 § 8.2`.
- **Interpretation.** The surfaces are not redundant with each other; they are
  each partial. That is why consolidation reads as lossy from any single surface's
  point of view.
- **Standards lens.** 16085 § 6.4.3.3 (risk profile) — absent entirely. 42010
  § 6.9.1 (*shall*) — known inconsistencies recorded.
- **Consequence.** A documented three-session rediscovery loop: the repository
  records three independent sessions re-deriving the same suspected defect.
- **Ruled 2026-09-22 (operator).** `Q-03` answered: **drain the defect-shaped pool entries to GHIs**, applying `pool-curation.md`'s three-gate filter retroactively. The pool returns to intake-only. Architectural Boundaries 1 and 2 stand unchanged.
- **Phase 2 challenge (Astra, 2026-09-22) — REJECT, twice.** Two challenge-table rows land here. *"§2/§8: No persistent system model or knowledge home exists"*: *"Absence claim not sustained"*, and it *"Conflates full 42010 AD conformity with possession of useful system knowledge."* Counterevidence: *"State/trust doctrine, CLI specification, architectural identity, source ontology, and OKF knowledge bundle exist"* [E7,E9,E10]. And *"§2/§4: Risks/research questions have no home; interface spec absent beyond manpages"*: *"Nonexistence claims exceed the inventory"*, *"A concept need not have its own object"*, with ADR consequences, research records and a canonical CLI specification named as counterevidence [E9,E10]. Astra's alternative in both cases is a **narrowing, not a dismissal**: *"Fragmented, partly stale, insufficiently queryable knowledge."* **Unresolved.** The two positions partly talk past each other — this finding claims no surface holds a model *as a model*, Astra names artifacts that hold system knowledge — and the register does not resolve that by fiat. Carried as `D-01`.
- **Disposition.** `M-C` traces where items in each surface actually end up.

### F-007 — Transient matter is accumulating inside durable stores

- **Status:** OPEN · **Class:** REFINE
- **Observation.** The mirror of F-001. Roughly a fifth of `rulings.jsonl` rows
  are transient session orders sharing an untyped, retirement-free store with
  durable doctrine. Handoffs are never compacted. `## Evidence` is pure work log
  preserved in L1 canon. `obpi_lock_ttl_warning` events are written and read by
  nothing.
- **Evidence.** `01 § 4.4`; `.gzkit/handoffs/rulings.jsonl` (no kind, status,
  scope or retirement field).
- **Interpretation.** Both directions of the boundary are broken, and they are
  the same defect: no object declares its own lifetime.
- **Standards lens.** 15289:2019 Table 3 — a decision record with none of the
  record's required fields.
- **Consequence.** Durable stores lose signal as they grow, which raises the cost
  of the entry in F-023.
- **Ruled 2026-09-22 (operator).** `Q-06` answered: **sequenced.** No handoff compaction until the durable facts have somewhere else to live. Compaction is a consequence of resolving F-001, not an independent decision.
- **Disposition.** Open. Compaction is gated on the durable facts having a home
  first (`Q-06`), which is a sequencing decision.

---

## B — Identity, traceability and the release seam

### F-008 — Decision, requirement and release identity share one semver namespace

- **Status:** OPEN · **Class:** REFINE
- **Observation.** An ADR identifier is a decision record wearing a release
  number; a REQ identifier contains that release number; a tag is an actual
  shipped release. The coupling is eight lines: `_extract_adr_version` regexes a
  semver out of a filename and `sync_project_version` writes it to
  `pyproject.toml`, `__init__.py` and the README badge, **with no `kind` guard.**
  The two lines have already diverged — releases exist with no ADR, and ADRs with
  no release.
- **Evidence.** `02 § The finding`, `02 § The mechanism`, `02 § Findings #1`;
  `src/gzkit/commands/version_sync.py:17-20` and `:46`. Re-derive with
  [`02-requirements-vs-release-evidence/measure.py`](02-requirements-vs-release-evidence/measure.py).
- **Interpretation.** That the two lines diverged while sharing a notation is the
  proof they were never the same thing.
- **Standards lens.** 24748-3 § 6.3.5.4 — version, revision and release status as
  separate fields per item, rather than one encoded string. *No clause prohibits
  an encoded identifier;* the principle is constructed from the separation of
  attributes.
- **Consequence.** The missing `kind` guard is a latent defect under either
  answer to `Q-08`.
- **Ruled 2026-09-22 (operator).** `Q-08` answered: **the `RELEASE_NOTES.md:1226` ruling stands; the code owes the change.** `version_sync` stops deriving the package version from an ADR identifier. The missing `kind` guard is repairable immediately and independently.
- **Disposition.** `Q-08` is ruled; the form of the decoupling is Phase 4.

### F-009 — No requirement revision counter exists

- **Status:** OPEN · **Class:** ADD
- **Observation.** 29148 § 5.2.8.2 pairs an immutable identity with a mutable
  version number whose stated purpose is signalling volatility. gzkit has neither
  half: identity is mutable and revision is absent.
- **Evidence.** `02 § Findings #3`.
- **Interpretation.** Volatility is currently invisible. A requirement that has
  been rewritten ten times is indistinguishable from one written once.
- **Standards lens.** 29148 § 5.2.8.2.
- **Consequence.** No basis exists for judging requirement stability, which is an
  input any baseline decision would need.
- **Disposition.** Depends on F-002 being settled first.

### F-010 — No requirements baseline; the freeze mechanism exists and is aimed elsewhere

- **Status:** OPEN · **Class:** ADD
- **Observation.** No requirements baseline exists. The approve-and-freeze
  mechanism gzkit would need was **already built, works, and is fail-closed** —
  and is pointed at the agent contract rather than at requirements.
- **Evidence.** `02 § gzkit already built a baseline — and pointed it somewhere
  else`, `02 § Findings #4`.
- **Interpretation.** This is the cheapest of the group-B findings to act on,
  because the mechanism is not missing — only its target.
- **Standards lens.** 12207 § 6.3.5.3 b) 3) NOTE 12 — baseline content "is
  developed through the technical processes, but is formalised at a point in time
  through the configuration management process." **CM must not be where
  engineering meaning is decided.** Supersedes the reading now recorded as F-035.
- **Consequence.** Nothing can say what the agreed set of requirements was at any
  past moment.
- **Disposition.** A design candidate, not a decision. Phase 4.

### F-011 — Requirements are governed by continuous reconciliation

- **Status:** OPEN · **Class:** REFINE
- **Observation.** Hundreds of `brief_reconciled` events, a substantial minority
  carrying drift, and a smaller set that widened the allowlist to match what had
  already been touched.
- **Evidence.** `02 § Findings #5`; `01 § 6`. Re-derive from `.gzkit/ledger.jsonl`
  via `measure.py`.
- **Interpretation.** Continuous reconciliation is **the structural opposite of a
  baseline.** It is not a weaker baseline; it is a different and incompatible
  posture. This matters because F-010's remedy cannot simply be layered on top.
- **Standards lens.** 12207 § 3.1.12 — a baseline is a "formally approved
  version… fixed at a specific time."
- **Consequence.** Any baseline proposal must first rule on what reconciliation
  is for.
- **Disposition.** Open, and coupled to F-010 and F-018.

### F-012 — Traceability is one leg of the five 29148 names

- **Status:** QUALIFIED · **Class:** ADD
- **Observation.** REQ→verification exists and works. REQ→need, REQ→architecture,
  REQ→implementing element and REQ→parent do not. Of eleven traceability questions
  posed in piece 01, four are answerable, three partially, four not at all.
- **Evidence.** `01 § 5.1` (the eleven-question table), `01 § 4.2`.
- **Interpretation.** The missing legs are not evenly weighted: the two that close
  the most questions are NEED→REQUIREMENT and REQUIREMENT→COMPONENT.
- **Standards lens.** 29148 § 6.4.3.5 (five legs); 12207 § 6.4.3.3 (*shall*).
  Citation corrected by piece 02: "requirements shall be configuration
  controlled" is § 6.4.3.5, not § 6.6.
- **Consequence.** Impact analysis and blast radius are unavailable; the
  `## Discovery Checklist` substitutes for them and is presence-checked only.
- **Phase 2 challenge (Astra, 2026-09-22) — CONFIRM WITH QUALIFICATION, and the qualification changes the remedy.** Challenge-table row *"§4/§5: Only REQ→test trace exists; parent/allocation are absent"*: *"Production source allocation is unpopulated; total absence is false."* Counterevidence: *"`ReqEntity.parent_obpi` exists; source-anchor/coupling implementation exists, with zero current source anchors"* [E6,E7]. Alternative: *"Incomplete population/projection rather than missing modeling capability."* **This is a material correction.** REQ→parent and REQ→implementing element are **built and unpopulated**, not missing. A finding of absent capability argues for construction; a finding of unpopulated capability argues for population. Phase 4 must not read this row as the former.
- **Disposition.** `01 § 5.2` proposes a six-node, seven-edge graph of which four
  edges already exist. That is a **design candidate**, not a decision.

### F-013 — No architecture description in the 42010 § 6 sense

- **Status:** OPEN · **Class:** ADD
- **Observation.** 372 ADRs satisfy 42010 § 6.10.1–6.10.2 (decisions and
  rationale) and no other subclause of § 6. No viewpoints, views, view components,
  correspondences or inconsistency list exist as artifacts.
- **Evidence.** `01 § 3`, `01 § 4.2`.
- **Interpretation.** **Decisions are indexed by when they were made, not by what
  they cover**, so no coverage property over concerns can exist.
- **Standards lens.** 42010:2022 § 4 and § 6 (*shall*).
- **Consequence.** No answer to "which decisions bear on this surface."
- **Phase 2 note (Astra, 2026-09-22) — not directly challenged.** The challenge-table row rejecting *"No persistent system model or knowledge home exists"* charges a conflation of *"full 42010 AD conformity with possession of useful system knowledge."* **That charge lands on F-006's inference, not on this row's observation**, which is a bounded subclause-coverage count and is not contradicted by any counterevidence Astra offers. Status therefore unchanged. The `M-E` disposition — test whether extending correspondence methods reaches the property more cheaply than an architecture description — is strengthened rather than weakened by Astra's *"A concept need not have its own object."*
- **Disposition.** `M-E` tests whether an architecture description is warranted or
  whether extending the existing correspondence methods reaches the same property
  more cheaply. **Piece 01 declares its own bias:** the correspondence route is
  likely cheaper and should be tested first.

### F-014 — The PRD is inert; product-intent traceability was practised once

- **Status:** QUALIFIED · **Class:** REFINE
- **Observation.** The PRD has been `status: Draft` since January. Its `FR-*`
  identifiers appear nowhere outside it; its `AC-*` identifiers appear outside it
  only in the first pre-release ADR and that ADR's OBPIs.
- **Evidence.** `01 § 1.2(b)`, `01 § 2`.
- **Interpretation.** Traceability to stated product intent was practised once and
  then abandoned across every subsequent ADR. The requirements model below it is
  live and working; its foundation is not.
- **Standards lens.** 29148 § 6.3/§ 6.4; 12207 Table B.1 (`artefact`).
- **Consequence.** The top of the traceability chain is absent, so NEED→REQUIREMENT
  (F-012) has nothing to attach to until `Q-02` is answered.
- **Ruled 2026-09-22 (operator).** `Q-02` answered: **rewrite the PRD around the system as it actually ships.** The product claim stands — distribution is mechanically enforced — but the January framing does not. This restores the top of the traceability chain that F-012's NEED→REQUIREMENT edge needs.
- **Narrowed 2026-09-23 (operator).** `Q-02`'s remedy shape is narrowed to **repair stale metadata and restore linkage** — operator verbatim: *"repair stale metadata and restore linkage."* The PRD is not rewritten. **The product-claim half of the prior ruling stands unchanged; only the remedy narrows.** This lands where this row's Phase 2 challenge already pointed: *"Weak explicit linkage and stale metadata, rather than absent product intent."* For F-012's NEED→REQUIREMENT edge the consequence is the same edge by a cheaper route — the identifiers exist and are uncited, rather than being absent and needing authorship.
- **Phase 2 challenge (Astra, 2026-09-22) — CONFIRM WITH QUALIFICATION.** Challenge-table row *"§1/§2: PRD is frozen/inert; product-intent traceability was abandoned"*: *"Identifier-use evidence is narrower than claimed semantics"*, and it *"Overreads missing explicit links."* Counterevidence: *"PRD contains later glossary/context additions; git shows changes through August 17. It still states a product and north star"* [E10]. Alternative: *"Weak explicit linkage and stale metadata, rather than absent product intent."* **The identifier measurements stand; "inert" does not.** Astra reached this independently of, and agrees with, the narrowing the operator's `Q-02` ruling is awaiting — *repair stale metadata and restore linkage* rather than *rewrite*. **This bears on an unanswered operator question and is flagged for it.**
- **Disposition.** `Q-02` is ruled, and narrowed 2026-09-23 to metadata repair plus linkage restoration; the repair itself is Phase 4 or later, and is not authorised by this register.
  Leaving it Draft and uncited is the one option that costs without paying.

### F-015 — No release record; the ledger cannot reconstruct a release

- **Status:** OPEN · **Class:** ADD
- **Observation.** Release ceremony records no approval: `operator_approval` is a
  Pydantic default that nothing assigns, nearly all tags are lightweight, and the
  ledger event carries the previous tag and is appended before the release is
  created. One event type of 67 carries version information. No event says "this
  set of artifacts is the approved content of version X."
- **Evidence.** `02 § Ceremony without approval`, `02 § Findings #7, #8, #13`;
  `measure.py`.
- **Interpretation.** Release is the one place where gzkit's usual instinct —
  record it in the ledger, derive the view — was not applied.
- **Standards lens.** 15289:2019 Table 3 makes the release record and the
  requirement record separate rows with **disjoint owning processes**, and the
  requirement record carries no version and no release field.
- **Consequence.** What shipped in a given version is not reconstructible from
  L2.
- **Ruled 2026-09-22 (operator).** `Q-10` answered: **a ledger release record** — an L2 event asserting the approved content of a version. Chosen over a tag or a manifest because it matches the instinct F-033 identifies as already standards-conformant, and adds no L1 surface.
- **Disposition.** `Q-10` is ruled as to form. Whether the unit of approval is a manifest, a ledger
  event or an annotated tag is a design question; *whether it should exist* is
  not.

### F-016 — Identifier renameability funds a large standing machinery cost

- **Status:** OPEN · **Class:** REMOVE
- **Observation.** Roughly 880 source lines and 1,680 test lines of rename
  machinery, dozens of regexes across dozens of modules, and a measurable share of
  every `gz check` run exist because identifiers are renameable. Feature semver
  slots have been reused, and a large number of work items have carried multiple
  identifiers.
- **Evidence.** `02 § Findings #6, #10`; `measure.py`. Re-derive the check cost by
  timing `uv run gz check`.
- **Interpretation.** This cost is downstream of F-002 and F-008, not independent
  of them. It is listed separately because it is the one place the identity
  problem shows up as a recurring, measurable tax rather than as a risk.
- **Standards lens.** 29148 § 5.2.8.2 — immutable identity.
- **Consequence.** Every contributor pays it on every check.
- **Disposition.** REMOVE is **contingent** on F-008 and F-009 being settled
  first. Removing the machinery before fixing identity would be the wrong order.

### F-017 — Two coverage numbers disagree with no reconciling statement

- **Status:** QUALIFIED · **Class:** REFINE
- **Observation.** `gz covers` and `gz drift` report different counts over what
  doctrine treats as one coverage surface, and no statement anywhere reconciles
  the populations.
- **Evidence.** `01 § 5.1`; `01 § 11` row 22. Re-derive with `uv run gz covers`
  and `uv run gz drift` in the same tree.
- **Interpretation.** Small in itself, and a good probe: two derived views of one
  property that nobody has had cause to reconcile.
- **Standards lens.** 42010 § 6.9.3 — a correspondence method records whether it
  holds or records all known violations.
- **Consequence.** Either number can be cited as *the* coverage figure.
- **Phase 2 challenge (Astra, 2026-09-22) — CONFIRM WITH QUALIFICATION, and it supplies the missing statement.** Challenge-table row *"§5: Coverage numbers disagree without a coherent basis"*: *"Totals verified; semantic explanation omitted"*, and *"Different proof populations are legitimate."* Counterevidence: *"Covers includes feature tags and broader kinds; drift filters non-test obligations and retired work"* [E6]. **The disagreement is not a defect in either number; the absence of a reconciling statement is.** Astra's §1 separately reproduces the `1,794/2,749` coverage and `713` drift figures exactly. This sharpens the row into a documentation repair with a known answer, which strengthens the existing direct-repair disposition.
- **Disposition.** Candidate for direct repair under the defect-fix route; it is
  one surface and small. Not an assessment decision.

---

## C — Enforcement and evidence

### F-018 — Jurisdiction is declared in prose and refused by nothing

- **Status:** QUALIFIED · **Class:** REFINE
- **Observation.** `## Allowed Paths` appears in almost every brief and is parsed
  by five independent parsers. `## Denied Paths` is never tested against a write.
  The airlock computes a HOLD decision that all six call sites print and continue
  past, over an input that is empty in practice. The operator-only-initiation rule
  appears in a dozen-plus prose locations and no code; the corpus records its own
  violation.
- **Evidence.** `01 § 1.2(d)`, `01 § 6`, `01 § 8.2`;
  `.claude/hooks/pipeline-gate.py:156-158`; `src/gzkit/airlock/enter.py:158-170`;
  `src/gzkit/commands/airlock.py:14-18`, which states the limitation honestly in
  code.
- **Qualification (within Phase 1, on re-verification).** An earlier reading in
  the investigation held that `pipeline-gate.py` had its jurisdiction fence
  inverted. **The precise reading is that it is a pipeline-*stage* fence which
  happens to be allowlist-scoped, not a jurisdiction fence that was reversed.**
  The effect is the same — no hook refuses an out-of-scope write — but the
  mechanism is a gap, not a reversal, and the two imply different repairs.
- **Interpretation.** Jurisdiction here is discovered after the work, not enforced
  before it; the reconciles that widened an allowlist to fit what was already
  touched are the clearest instance.
- **Standards lens.** 16085 § 6.4.3.2 — a threshold defines what is acceptable
  "without explicit review by the stakeholders", i.e. escalation as a boundary of
  delegated authority.
- **Consequence.** An unenforced prohibition that is known to have been violated
  is weaker than an enforced threshold that delegates below a line.
- **Ruled 2026-09-22 (operator).** `Q-05` answered: **keep the IRON LAW and pursue a mechanical witness.** The 16085 consequence threshold is **not adopted** — it is enforceable but strictly weaker, because it delegates below a line. Do not re-propose it as a remedy for F-018.
- **Consequence input.** Hooks score `C2` in [`consequence-bands.md`](consequence-bands.md).
- **Phase 2 challenge (Astra, 2026-09-22) — CONFIRM WITH QUALIFICATION, plus an evidence correction.** Challenge-table row *"§1/§8: Jurisdiction/airlock do not prevent inspected out-of-scope writes"*: *"Direct caller/hook evidence"*, verdict confirmed. Counterevidence narrows the scope: *"Airlock's limitation is explicit; its NC calls `airlock_enter`, not merely `_decide`; existing successor owns calibration"* [E8]. **Evidence correction:** the anchor cited above is `enter.py:158-170` (`_decide`); Astra's reading is that the non-conformance path calls `airlock_enter`, and the row should be re-anchored accordingly before Phase 4 relies on it. Alternative: *"Unfinished calibration/compulsion and harness coverage"* rather than absent enforcement by design. **Separately, Astra independently REJECTS the 16085 threshold remedy** — *"Risk tolerance is not a grant of authority"*, *"Initiation is an explicit human-sovereignty policy; a violation does not invalidate its purpose"* — converging with the operator's `Q-05` ruling from the opposite direction.
- **Disposition.** `Q-05` is ruled against the threshold. The
  threshold is enforceable but is genuinely a *weaker* rule than the blanket
  prohibition.

### F-019 — Gates record exit codes where the covenant promises claims

- **Status:** QUALIFIED · **Class:** REFINE
- **Observation.** The large majority of `gate_checked` events carry no
  observation of what was verified — empty, or a literal constant string, or a
  skip recorded as a pass. Gate 2 ("Tests pass") has been satisfied many times by
  lint and typecheck runs. `_run_gate_5()` in `gz gates` is `console.print(...);
  return True`, and zero gate-5 events exist. `gz gates` itself prints a
  deprecation notice on every invocation while AGENTS.md documents the covenant
  against it.
- **Evidence.** `01 § 1.2(e)`, `01 § 8.2`; `src/gzkit/commands/gates.py:153-160`, `:261-263`;
  `src/gzkit/governance/deprecations.py:41` (GHI #705).
- **Interpretation.** In 24748-1 § 4.3.2 terms these are **checks, not decision
  gates** — no outcome can hold, restart or terminate anything.
- **Standards lens.** 15026-2 § 5.3.3 — a claim needs a property, a limit, an
  uncertainty bound and a scope.
- **Consequence.** The largest single source of false confidence in the system.
- **Ruled 2026-09-22 (operator).** `Q-07` answered: **re-point the covenant** at `gz closeout` and `gz obpi complete`, keeping the five-gate vocabulary. Edits to `AGENTS.md` go through the corpus ceremony, not a hand-edit.
- **Standing constraint (operator, 2026-09-22).** *"do not abandon the five gates without a discussion with me."* **Retiring or replacing the five-gate vocabulary is prohibited absent an explicit operator discussion** — including as an incidental consequence of any Phase 4 design. This finding describes what the gates record; it does not license removing them.
- **Consequence input.** Surfaces in this finding are scored in [`consequence-bands.md`](consequence-bands.md): gate logic `C2`, validators `C2`, receipt durability `C3`. Ten of sixteen scored surfaces are `D2` — they fail by reporting success.
- **Phase 2 challenge (Astra, 2026-09-22) — CONFIRM WITH QUALIFICATION; the universal form falls.** Challenge-table row *"§1/§8: Gates record exit codes and decide nothing"*: *"Good historical payload concern; false generalization"*, and it *"Confuses a check, a gate condition, and the authorization consuming it."* Counterevidence: *"Closeout blocks failures; completion emits human-attestation receipts"* [E4]. Alternative: *"Deprecated interface plus dispersed evidence, not universally absent gating."* **Surviving claim:** the historical `gate_checked` payloads are weak, and the deprecated `gz gates` Gate-5 stub is a poor guide to current completion behaviour. **Withdrawn:** that nothing in the system gates. Astra's §1 states the same in its own words. The operator's `Q-07` ruling — re-point the covenant at `gz closeout` and `gz obpi complete` — was reached independently and moves in the same direction. Carried as `D-06`.
- **Disposition.** `Q-07` is ruled. The superseded option was to retire
  the gate vocabulary. Both are coherent; they are not the same project. `M-D`
  would name the claim behind each gate.

### F-020 — Documentation and implementation disagree at 22 measured points

- **Status:** QUALIFIED · **Class:** REFINE
- **Observation.** Twenty-two specific places where a documented rule and the
  code that implements it say different things, each with both sides cited.
- **Evidence.** `01 § 11` — the disagreement register, held there in full and not
  duplicated here.
- **Interpretation.** Piece 01 **chose no authoritative side on any row**, and
  that restraint should survive into Phase 4. Several rows are not drift but
  declared degradation, disclosed in the code or skill itself; conflating the two
  kinds would be the obvious error.
- **Standards lens.** 42010 § 6.9.1 (*shall*) — record known inconsistencies.
- **Consequence.** Any agent reading doctrine can act on a rule the code does not
  implement.
- **Phase 2 challenge (Astra, 2026-09-22) — three of the twenty-two rows rejected.** The register of disagreements is not itself challenged; three of its rows are. *"§11: Computed `not-refuted` bypasses real adversarial outcome"* — **REJECT**: *"`completion_review` checks proofs, required reviews, and unresolved findings first; refuted rounds can be retained"* [E4]; alternative, *"Legacy dead code/comment beside newer acceptance model."* *"§2/§11: Fifteen agent attestations indict current Gate 5"* — **REJECT**: *"All fifteen date to March; universal rule cutoff is April 26"* [E4]; the count is *"not version-stratified"*, so it is pre-doctrine practice, and the present relay-authentication limitation is a separate question. *"§2/§11: `staleness.periodDays` is unread"* — **REJECT**: *"Contradicted by code and tests"*; *"Status calculates due dates; session orientation consumes status; freshness script also reads the field"* [E3]; what is absent is an autonomous scheduler or operator selection of due work, not a reader. **Consequence for this finding:** piece 01's restraint in choosing no authoritative side is vindicated, but at least three rows are not live disagreements at all — they are resolved against piece 01 on counterevidence, and must be marked as such before the register is used.
- **Disposition.** Each row routes independently. Some are direct-repair sized;
  some need an operator ruling. None is an assessment decision.

### F-021 — The system finds its own facades honestly and cannot retire them

- **Status:** DISPUTED · **Class:** ADD
- **Observation.** The repository records, in durable artifacts and without
  softening, that a majority of its enforcement claims do not prove what they
  assert while `gz check` reports them all verified; that a contract
  "auto-enforces nothing" and its effectiveness is "an UNTESTED HYPOTHESIS"; and
  it maintains a ledger accessor whose purpose is to re-surface failures that the
  effective view launders to pass. Grandfather files freeze rows scored
  "Mechanical" that nothing witnesses.
- **Evidence.** `01 § 1.2(f)`, `01 § 8.1`;
  [`enforcement-claim-nc-audit-2026-07-18.md`](../enforcement-claim-nc-audit-2026-07-18.md),
  [`evidence-record-contract.md`](../evidence-record-contract.md),
  `data/mechanical_witness_grandfather.json`.
- **Interpretation.** **This is the defining characteristic of the system.** The
  error-detecting loop works. What is missing is a mechanism to *retire* what it
  finds, so findings accumulate alongside the defects they describe. In 15026-2
  § 3.1.7 terms the grandfather ratchets are *declared undeveloped arguments* —
  a recognised and legitimate form, not a dodge.
- **Standards lens.** 42010 § 6.9.1 (*shall*); 15026-2 § 3.1.7.
- **Consequence.** The honest inventory is itself distributed across six stores
  with no index and no retirement path (F-006).
- **Phase 2 challenge (Astra, 2026-09-22) — REJECT on the second half.** Challenge-table row *"§1/§8: Self-detection works but retirement is missing"*: *"Historical audit and backlog sizes do not establish current failure"*, and *"A baseline is not automatically an undeveloped assurance argument"* — which challenges this row's 15026-2 § 3.1.7 reading of the grandfather ratchets directly. Counterevidence: *"July NC defects have subsequent repair commits; withdrawal, repudiation and demotion were exercised"* [E1,E5]. A second row, *"§2/§11: Insights have no reader or close path"*, is **CONFIRM WITH QUALIFICATION**: *"Too absolute"*; *"Rubric reads references from content; 36 `defect-resolution` records exist"* [E3]; the surviving alternative is *"No adequate linked current-state reduction, despite useful archival signals."* **Unresolved.** The self-detection half is not challenged and is separately affirmed in Astra's §1. The *"cannot retire"* half is rejected as stated — retirement verbs exist and were exercised — while the narrower claim that no linked current-state view of what remains unretired exists is left standing by Astra's own alternative. **This row is described above as the defining characteristic of the system, so the dispute is load-bearing and is not resolved here.** Carried as `D-05`.
- **Disposition.** `M-D`, which carries its own method problem: the prior audit
  disqualified itself as *"a stochastic surface auditing a stochastic surface."*
  **`M-D` must first establish what a non-agent witness looks like, or declare the
  question unanswerable by agent labour.** Highest-risk item in the program.

### F-022 — Evidence records are incomplete as evidence

- **Status:** OPEN · **Class:** REFINE
- **Observation.** A substantial share of receipts exist only on the authoring
  machine, because `artifacts/` is gitignored and the tracked ones were
  force-added. Command binding covers only four canonical step names; the
  receipts cited as Gate-4 and Stage-4 evidence are among those with none. No exit
  record captures what the work assumed, or what it disturbed beyond the allowlist
  reconcile.
- **Evidence.** `01 § 2` (receipt row), `01 § 7.3`, `01 § 11` rows 10 and 11;
  `src/gzkit/arb/validator.py:279`.
- **Interpretation.** An evidence record nobody else can retrieve is not evidence.
- **Standards lens.** 15026-2 § 5.3.2 — an evidence item carries scope of
  applicability, uncertainty and assumptions; a receipt carries provenance only.
  29148 § 5.2.7 (*shall*) — "All assumptions made regarding a requirement shall be
  documented."
- **Consequence.** The § 5.2.7 `shall` has nowhere in this system to be satisfied,
  and assumptions are precisely what a handoff cannot recover.
- **Disposition.** Open.

---

## D — Cost and accumulation

### F-023 — Agent entry cost is dominated by procedure, not by the problem

- **Status:** QUALIFIED · **Class:** REFINE
- **Observation.** Mandatory reading before an agent writes a line against a
  median OBPI totals roughly 92,000 tokens, of which the brief — the artifact
  describing the work — is under 4%. The single largest item is the pipeline
  skill; the second is a status command whose opening is campaign narrative. The
  handoff corpus adds a second entry cost and is capped by a depth bound, so the
  ancestor count the session hook reports is a floor, not the true chain length.
- **Evidence.** `01 § 1.2(g)`, `01 § 7.1`, `01 § 8.2`;
  `src/gzkit/session_start.py:185`, `src/gzkit/handoff_api.py:1181`.
- **Interpretation.** The composition matters more than the total: this is not a
  verbose-documentation problem, it is a procedure-dominates-problem problem.
- **Standards lens.** 32675 § 6.3.1.3 b) 4) (normative task list) — enable change
  through "compact low-dependency scopes, **low gates**, low overhead."
- **Consequence.** Beyond volume, `01 § 7.1` lists seven things an entering agent
  must **reconstruct** because nothing states them.
- **Phase 2 challenge (Astra, 2026-09-22) — CONFIRM WITH QUALIFICATION.** Challenge-table row *"§7/§8: Mandatory entry costs 92k tokens and dominates cost"*: *"Composite byte estimate, not measured delivered tokens or time."* Counterevidence: *"Uses ADR-0.35.0 size with a median brief; generic status is not required by the inspected pipeline; harness inputs vary"* [E2] — the figure pairs the largest ADR with a median brief, and one of its components is not mandatory on the inspected path. Alternative: *"Overdelivery, lineage policy, or irrelevant retrieval rather than missing objects."* **Surviving claim:** context delivery is large and repetitive, and the brief is a small share of it — Astra's §1 calls the reconstruction burden *"credible"*. **Withdrawn:** the 92,000-token figure as a measured universal entry cost, and its claimed dominance over other costs.
- **Disposition.** Open. Note the standing `gz-context-diet` route already exists
  for part of this.

### F-024 — Governance prose outweighs source code several-fold

- **Status:** OPEN · **Class:** REFINE
- **Observation.** Documentation lines exceed source lines by roughly two to one,
  and total governance prose by roughly three and a half to one. Handoffs alone
  are more than half the source tree's line count.
- **Evidence.** `01 § 1.2(h)`. Re-derive with a line count over `src/`, `tests/`,
  `docs/` and `.gzkit/`.
- **Interpretation.** A ratio alone is not a defect — a governance framework is
  expected to be prose-heavy. It is reported because of what dominates the ratio:
  handoffs, an object with **no standard analogue**, transient by design and
  permanent in practice.
- **Standards lens.** None directly; 15289 § 5.1 permits information to live
  unpublished in a repository.
- **Consequence.** Feeds F-023 and F-007.
- **Disposition.** Open, and gated on `Q-06`.

### F-025 — Work-package duration and the collapse of pipeline throughput

- **Status:** QUALIFIED · **Class:** —
- **Observation.** Two separate measurements. **Duration:** median about three
  days, p90 about twenty, a third exceeding a week. **Throughput:** OBPI creation
  fell by more than an order of magnitude over seven months, while the
  GHI→direct-fix channel carries roughly four times the traffic of the
  ADR→OBPI pipeline.
- **Evidence.** `01 § 6` (health block), `01 § 1.2(a)`. Re-derive from
  `.gzkit/ledger.jsonl` and `git log`.
- **Interpretation.** **No single cause is supported by the Phase 1 evidence, and
  the investigation must not converge on one prematurely.** The persistent-knowledge
  hypothesis (F-001) is *a* candidate explanation for duration, not the
  established one. Candidates that remain live, none excluded by current evidence:
  task scope; architecture coupling; validation burden; excessive context (F-023);
  requirement churn (F-011); agent capability limits; perfectionistic completion
  criteria; poor subsystem boundaries; repeated review cycles; weak
  authority/jurisdiction boundaries (F-018); and template-driven growth in
  responsibilities (F-005).
- **Standards lens.** 15939 § 6.2 b) — state the information need and the decision
  it supports **before** the measure, never the reverse.
- **Consequence.** A remedy chosen against the wrong cause would be expensive and
  would look justified.
- **Phase 2 challenge (Astra, 2026-09-22) — CONFIRM WITH QUALIFICATION on throughput; the refusal to attribute duration is affirmed.** Challenge-table row *"§1: GHI repair is the primary change channel, roughly 4:1"*: *"Commit-label counts support a descriptive trend, not effort or delivered value."* Counterevidence: *"Commits mentioning GHIs and OBPIs are not mutually exclusive work units; one feature may need many repair commits"* [E1]. Alternative: *"Deliberate stabilization, batching, and operator-controlled feature sequencing"* — i.e. the ratio may be a governance choice rather than a symptom. **Surviving claim:** the ratio is a real descriptive trend in commit labels. **Withdrawn:** reading it as a measure of effort or delivered value. **This row's explicit refusal to attribute duration to any cause is the one methodological position Astra affirms rather than challenges**, and its candidate list already contains Astra's alternatives. Carried with `D-04`.
- **Disposition.** `M-G` baselines these as repeated measures. **Explicitly:
  duration is not attributed to any cause by this register.**

### F-026 — A long release stall that no gate can see

- **Status:** OPEN · **Class:** ADD
- **Observation.** Several hundred commits and a very large line delta sit
  unreleased since the last tag, with no ADR attestations in that window.
  `audit_version_release` checks only version↔tag agreement, so no gate can
  observe the stall.
- **Evidence.** `02 § Findings #15`; `measure.py`.
- **Interpretation.** The check is correct about what it checks; the gap is that
  nothing checks staleness.
- **Standards lens.** 32675 § 6.3.5.2 a) (*shall*) — a verifiable chain of
  evidence from source baselines through persisted derived objects.
- **Consequence.** The divergence in F-008 grows unobserved.
- **Disposition.** A staleness signal is a design candidate. Phase 4.

---

## E — Strengths

> Presented **without numeric ranking.** The evidence supports each as strong; it
> does not support an ordering among them.

### F-027 — The REQ→test correspondence machinery, with violation recording

- **Status:** QUALIFIED · **Class:** KEEP
- **Observation.** `gz covers`, `gz drift`, one consolidated REQ grammar replacing
  roughly twenty disagreeing regexes, and thousands of `@covers` annotations.
- **Evidence.** `01 § 8.1`; `src/gzkit/triangle.py:24-31` (GHI #615).
- **Interpretation.** This is 42010 § 6.9.3 correspondence methods with violation
  recording, **independently built, with absence correctly counted as a
  violation** — the hard half of the clause.
- **Standards lens.** 42010 § 6.9.3 NOTE 1.
- **Consequence.** The single most valuable asset in the repository and the
  natural foundation for anything Phase 4 proposes.
- **Phase 2 challenge (Astra, 2026-09-22) — CONFIRM WITH QUALIFICATION.** Challenge-table row *"§3/§8: REQ correspondence and proof-channel distinction are strong assets"*: *"Direct implementations and reproducible link counts"*, and a *"Useful analogy to correspondence methods, not full conformance proof."* Counterevidence: *"Static tags do not prove execution or semantic coverage."* Alternative: *"Strength is bounded discoverability and routing of proofs."* **The asset is affirmed and its scope narrowed:** Astra's §1 reproduces the coverage and drift figures exactly and calls the mechanism *"useful, functioning"*, while recording that it *"measure[s] linkage, not passing execution or adequacy."* The KEEP class is unaffected; the claim that it proves coverage is not made here and must not be inferred.
- **Disposition.** KEEP. Any design that weakens it should be rejected on that
  ground alone.

### F-028 — The anti-tautological-test stack is ahead of the testing standard

- **Status:** QUALIFIED · **Class:** KEEP
- **Observation.** RED witnesses classify into `assertion` / `error` / `none` /
  `not-applicable` and refuse to equate them. Mutation witnesses separate
  `killed`/`survived` (a claim about the guard) from `invalid`/`inconclusive` (a
  claim about the run), and document a real cache-contamination bug.
- **Evidence.** `01 § 8.1`; `red_witness.py`, `mutation_witness.py` (GHI #963).
- **Interpretation.** **29119 has no vocabulary for any of this** — "test oracle"
  appears zero times in Parts 2–4. The measured honesty is the point: a
  meaningful share of RED receipts are classified `none`, meaning tests that
  demonstrably cannot fail were found and recorded rather than suppressed.
- **Standards lens.** 29119-4 § 5.1 — expected results derive from the basis, not
  the implementation.
- **Consequence.** A genuine capability the standards corpus cannot improve.
- **Phase 2 challenge (Astra, 2026-09-22) — CONFIRM WITH QUALIFICATION, and a factual correction to the standards claim.** Challenge-table row *"§3/§8: Anti-tautology stack is ahead of 29119; `none` proves inability to fail"*: *"Mechanisms useful; superiority and universal inference unsupported."* **Correction:** *"Part 1 explicitly defines oracle and oracle problem"* [S8]. The Observation above scopes its zero-occurrence count to Parts 2–4, which remains literally true, but **the inference that 29119 has no vocabulary for this does not survive** — Part 1 supplies it. Second counterevidence: *"A passing selected baseline does not establish incapacity to fail on all relevant faults"*, so a `none` classification is a *"Local adequacy witness with limited experiment scope"*, not a proof of incapacity. **Surviving claim:** the mechanisms and their measured honesty. **Withdrawn:** *"ahead of the testing standard"* as stated, and `none` as proof of inability to fail. Carried as `D-07`.
- **Disposition.** KEEP.

### F-029 — The REQ-kind taxonomy independently rediscovers the verification-method split

- **Status:** QUALIFIED · **Class:** KEEP
- **Observation.** gzkit measured that a third of test assertions were
  filesystem-shaped — grepping prose from production docs to satisfy coverage
  parity, detecting no code regressions — and responded with three REQ kinds
  carrying **distinct proof channels**.
- **Evidence.** `01 § 8.1`;
  [`req-scope-discipline.md`](../req-scope-discipline.md) lines 9-40.
- **Interpretation.** An independent rediscovery of 29148 § 6.5.2.2's verification
  methods and 29119-4 § 5.1's basis rule, arrived at by measurement rather than by
  reading the standard.
- **Standards lens.** 29148 § 6.5.2.2; 29119-4 § 5.1.
- **Consequence.** The proof-channel binding is the mechanism any persistent
  requirement object must preserve.
- **Phase 2 challenge (Astra, 2026-09-22) — CONFIRM WITH QUALIFICATION.** Covered by the same challenge-table row as F-027, *"§3/§8: REQ correspondence and proof-channel distinction are strong assets"*, whose qualification is that the strength is *"bounded discoverability and routing of proofs"* rather than proof of semantic coverage. The taxonomy's independent-rediscovery claim is not challenged. The existing note that adoption is partial — most REQs untagged, inference supplying a default — is the same bound from the other direction.
- **Disposition.** KEEP. Note `01 § 11` row 1 records that most REQs are untagged
  and inference supplies a default — the taxonomy is sound; its adoption is
  partial.

### F-030 — Path-scoped agent rules with real runtime enforcement

- **Status:** OPEN · **Class:** KEEP
- **Observation.** Every `.claude/rules/*.md` carries `paths:` scoping, enforced
  by `gz validate --unscoped-rules` — genuine progressive disclosure against a
  large rule corpus.
- **Evidence.** `01 § 8.1`; ADR-0.0.20.
- **Interpretation.** Directly witnessed during Phase 1: a hook blocked two of the
  investigating agent's own commands for masking a verifier's exit status behind a
  pipe, cited the rule, and supplied the corrected form. **A claim made explicit
  and then mechanically enforced, in an external agent's hands, on first
  contact.**
- **Standards lens.** None; this is agent-era practice with no standards analogue.
- **Consequence.** The working model for what F-019's gates could become.
- **Disposition.** KEEP.

### F-031 — `RELEASE_NOTES.md` is load-bearing, not duplication

- **Status:** OPEN · **Class:** KEEP
- **Observation.** It is a validator input — the release roster is derived from it
  — and the only surviving record for a dozen tags orphaned by the 2026-04-19
  filter-repo rewrite. The mechanically-derivable version is generated and
  discarded on every release.
- **Evidence.** `02 § Findings #12`; `src/gzkit/governance/trust_audits/release.py:201-203`.
- **Interpretation.** Recorded explicitly because it looks like duplication and is
  a plausible target for removal. It is not.
- **Standards lens.** 15289 Table 3 — the release record.
- **Consequence.** Removing it would destroy the only record of twelve releases.
- **Disposition.** KEEP. Flagged as a **do-not-simplify** surface for Phase 4.

---

## F — Method boundary

### F-032 — Most of the standards' machinery should not be adopted here

- **Status:** CONFIRMED · **Class:** —
- **Observation.** Piece 01 § 9 enumerates the machinery to leave behind: the
  agreement processes, organizational project-enabling processes, the four
  mandated requirements documents, formal V&V plans and IV&V organizational forms,
  SQA-unit independence, organizational test policy, architecture boards and
  design authorities, architecture description frameworks, the full evaluation and
  measurement apparatus, PMBOK scheduling, stakeholder negotiation ceremony, risk
  committees, and conformance-claim tailoring ceremony. Piece 02 adds the
  configuration-management half.
- **Evidence.** `01 § 9`, `02 § Bureaucracy filter for this seam`.
- **Interpretation.** Nearly all of it presupposes two parties with divergent
  authority, or an organization outside the project. Where one person holds every
  role, the mediation apparatus is empty. Two standards argue affirmatively for
  less: 12207 § 4.3 prefers full conformance to a smaller declared process set,
  and 32675 § 6.3.1.3 b) 4) requires "low gates, low overhead."
- **Qualification (piece 02, 2026-09-22).** One row is withdrawn — see F-035.
- **Consequence.** This finding is the investigation's principal safeguard: the
  failure mode most consistent with this repository's history is **adding
  machinery.**
- **Phase 2 challenge (Astra, 2026-09-22) — CONFIRM.** Challenge-table row *"§9: Avoid wholesale compliance bureaucracy; reuse local mechanisms"*: *"Good project-fit judgment"*, *"Broadly supported by flexible information-item packaging"* [S4]. **This is the only unqualified CONFIRM in the challenge table**, and it lands on the register's principal safeguard. Astra attaches one condition, recorded here because it is aimed at this investigation rather than at gzkit: *"Must apply this same restraint to the report's proposed ontology."* **The filter binds the investigation's own remedies, not only the standards corpus.** Astra separately REJECTS two remedy proposals on exactly this ground — independent requirement identity, and one consolidated inconsistency list — neither of which this register asserts as a finding.
- **Disposition.** Binding on Phase 4 as a filter, not as a decision.

### F-033 — Conformance is dischargeable by reference, not by document

- **Status:** CONFIRMED · **Class:** KEEP
- **Observation.** 15289 § 5.1 (*shall*) holds that information items conform when
  unpublished but available in a repository, divided across documents, or combined
  into one; § 3.1.11 defines "include" as having the information **or a reference
  to it**; § 8.2 holds that a process definition "does not in itself indicate that
  a specific information item is produced." 29148 Clause 7 and 29119-3 § 4.1.1 say
  the same for requirements and test information.
- **Evidence.** `01 § 9` preamble; `README.md` § The three permissions.
- **Interpretation.** **A ledger with a derived view conforms exactly as a
  document set does.** gzkit's existing instinct — put it in the ledger, derive
  the view — is already the conformant form.
- **Standards lens.** 15289 § 5.1, § 3.1.11, § 8.2.
- **Consequence.** No finding in this register implies writing a document.
- **Phase 2 challenge (Astra, 2026-09-22) — affirmed, no counterevidence offered.** The challenge table's §9 row records the standards interpretation as *"Broadly supported by flexible information-item packaging"* [S4], which is this finding's whole claim, and offers counterevidence only against the report's own proposed ontology. Astra's alternative — *"Existing sources plus targeted retrieval"* — is this finding restated as a remedy posture. **Promoted on an affirmative standards-interpretation verdict rather than on absence of challenge.**
- **Disposition.** KEEP as the standing reading that bounds what adoption can
  mean.

---

## G — Retired readings

> Retained because a future investigator could re-derive them from the same
> evidence and reach the wrong conclusion.

### F-034 — *Parked OBPIs indicate stalling work*

- **Status:** REJECTED · **Class:** —
- **Observation as stated.** A large number of `obpi_parked` events was read as
  evidence that work packages stall.
- **Why rejected.** All of them carry `reason: pool_demotion`, land on five
  timestamps across three days, and represent a single backlog-demotion campaign
  (GHI #520, repaired under GHI #584). **The park count says nothing about
  work-package health.**
- **Rejected by.** Piece 01, on re-verification, before publication. It never
  reached a published finding.
<!-- gz-validate-skip: command-shape -->
- **Residue that survives.** Parking has **no operator verb** — `gz obpi park`
  does not exist, and those events were emitted only by `gz adr demote` and a
  backfill module. A lifecycle state with doctrine, a schema and a lifecycle
  module, and no way for an operator to enter it deliberately. That absence is a
  real observation; the stalling reading is not.

### F-035 — *The four-baseline scheme is acquisition bureaucracy*

- **Status:** REJECTED · **Class:** —
- **Observation as stated.** Piece 01 § 9 filed 29148 § 6.6.2.2.2's four-baseline
  scheme under *do not adopt*, on the grounds that it partitions change authority
  between acquirer and supplier and one operator has one authority level.
- **Why rejected.** The clause has two halves and only one is contractual. **The
  contractual half — assignment of change-approval authority between parties —
  stands as correctly excluded. The four-fixed-points half is the answer to the
  question piece 02 was asking** and should not have been discarded with it.
- **Rejected by.** Piece 02, 2026-09-22.
- **Superseded by.** F-010. What transfers is stated there and in
  `02 § Bureaucracy filter for this seam`: at least two baseline kinds, one for
  agreed intent and one for evolving in-flight state under local change authority
  — the functional/developmental split, minus the acquirer.

---

## Amendments

- **2026-09-23 — `OPEN` redefined by operator ruling (`Q-14`).** `OPEN` was
  defined as *"disposition not yet settled"*; it now reads as **stated with
  evidence and not reached by the adversarial review — a settled disposition, not
  a waiting one.** **No row changed status**, and the fourteen `OPEN` rows are
  not promoted. The seeding note is rewritten to state the `CONFIRMED` bar as it
  now stands. **Phase 3's stop condition is met; Phase 4 is not authorised.**
- **2026-09-23 — *settled* and *ruled* separated by operator ruling.** § How to
  read a status now states that **evidence status and operator rulings are
  orthogonal**, with F-006 — `DISPUTED` and ruled at `Q-03` — as the worked case.
  Five dispositions that read *"`Q-0N` is settled"* now read *"is ruled"*; the two
  genuine evidence-sense uses (F-009 *"Depends on F-002 being settled"*, F-016
  *"contingent on F-008 and F-009 being settled"*) are correct under the new rule
  and are unchanged. **The index gains a `Ruling` column**, populated for the
  eight rows carrying an operator ruling — F-003, F-006, F-007, F-008, F-014,
  F-015, F-018, F-019 — and left **blank**, not `—`, for the other 27: `—` is
  already an undefined value in the `Class` column and repeating it would repeat
  the defect. **Found by Agent 2's Act 1 cold read (gap 3)**, which could not
  determine what an `OPEN` row carrying a ruling licenses. **No status and no
  ruling changed** — this is vocabulary and visibility only.
- **2026-09-23 — `Q-11` ratification propagated.** § Identifier convention and
  the seeding entry below both read `F-###` as an agent assumption pending
  ratification, **eleven amendments after the operator ratified it**. Corrected
  to record the ruling. No identifier changed. Found by Agent 2's Act 1 cold
  read, which could not tell from the canonical files whether the convention was
  ratified or not.
- **2026-09-23 — F-014's `Q-02` ruling narrowed by the operator** to *"repair
  stale metadata and restore linkage"*, from *"rewrite the PRD."* Status
  unchanged at `QUALIFIED`; the narrowing agrees with the Phase 2 challenge
  already recorded on the row, and the product-claim half of the original ruling
  is carried forward unchanged. See [`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md)
  `Q-02` for the reasoning and the retained superseded wording.
- **2026-09-22 — Phase 3 reconciliation pass applied.** All 25 rows of Astra's
  § 2 challenge table mapped onto this register; each affected row carries a
  **Phase 2 challenge** block quoting the verdict, the counterevidence and the
  alternative explanation, and stating what survives and what is withdrawn.
  **Nineteen rows carry a challenge block; seventeen statuses moved:** F-032 and
  F-033 → `CONFIRMED`; F-002, F-003, F-005, F-012, F-014, F-017, F-019, F-020,
  F-023, F-025, F-027, F-028, F-029 → `QUALIFIED`; F-006 and F-021 → `DISPUTED`.
  F-001 and F-018 were already `QUALIFIED` and keep that status, narrowed
  further by their challenge blocks. **Fourteen rows remain
  `OPEN` deliberately** — Astra reviewed pieces 01 and 02, not this register, and
  declares its own scope non-exhaustive, so a row it never reached was not
  exposed to challenge and did not survive one. F-004 and F-013 carry a
  **Phase 2 note** recording that the challenge lands adjacent to them rather
  than on them. Disagreements at `D-01` … `D-08` in
  [`DISAGREEMENTS.md`](DISAGREEMENTS.md). **Three material corrections a Phase 4
  reader must not miss:** F-012's missing traceability legs are **built and
  unpopulated**, not absent; F-028's *"ahead of the testing standard"* falls
  because 29119 **Part 1** defines the oracle vocabulary the finding searched
  Parts 2–4 for; and F-023's 92,000-token entry cost pairs the largest ADR with a
  median brief and includes a component the inspected pipeline does not require.
<!-- gz-validate-skip: code-citation -->
- **2026-09-22 — Act 1 cold-read repair pass (mechanical only).** Anchor and
  identifier repairs following Agent 2's Act 1 cold read. **No status moved and no
  finding changed in substance.** F-019's `src/gzkit/gates.py:163`, `:256-258` →
  `src/gzkit/commands/gates.py:153-160`, `:261-263`: the cited path does not
  exist, and at the real path the old line numbers land on Gate 4's PASS/FAIL
  rather than on anything the finding asserts. `:153-160` is the
  `_record_gate_result` call that passes `result.returncode` and the constant
  string `"stdout/stderr captured"` — the exit-code-for-a-claim substitution the
  finding is about; `:261-263` is `_run_gate_5`. F-019's
  `src/gzkit/deprecations.py:41` → `src/gzkit/governance/deprecations.py:41`
  (line correct, path wrong). F-008's `version_sync.py:289` → `:46`, where
  `sync_project_version` writes `pyproject.toml`, `__init__.py` and the README
  badge; `:289` is the penultimate line of an unrelated bump-detection helper.
  F-031's elided `src/gzkit/.../release.py:201-203` →
  `src/gzkit/governance/trust_audits/release.py:201-203`. Stale
  pre-renumbering ids: `Q8` → `Q-08` (F-008 § Consequence), `Q2` → `Q-02`
  (F-014 § Consequence). Dangling "Phase 3 Q4" → `Q-11` (§ Identifier
  convention). F-019's `D2` count corrected from nine to ten, matching
  `consequence-bands.md`'s own table. **Unresolved, left for the operator:**
  § Identifier convention and § Amendments below both read `F-###` as "pending
  operator ratification", while `Q-11` records it as **ratified**.
- **2026-09-22 — Seeded (Phase 3).** 35 findings drawn from pieces 01 and 02. All
  rows `OPEN` except three `QUALIFIED` (F-001, F-018, F-032) and two `REJECTED`
  (F-034, F-035), none of which was qualified or rejected by the Phase 2
  adversarial review — that pass has not yet been applied. *(Identifier
  convention `F-###` was recorded here as an agent assumption pending
  ratification; it was ratified at `Q-11` on 2026-09-22 and confirmed
  2026-09-23.)*
