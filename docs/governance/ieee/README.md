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
| [`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md) | **canonical** | The thirteen questions and the operator's ruling on each |
| [`consequence-bands.md`](consequence-bands.md) | **canonical** | Operator-ruled consequence scale (`Q-04`). Input to Phase 4; re-keys nothing |
| [`01-…`](01-engineering-method-2026-09-22.md), [`02-…`](02-requirements-vs-release-2026-09-22.md) | historical | Raw investigation record — what an agent said, frozen at its date |
| [`raw/`](raw/README.md) | historical | Raw reports not part of the numbered series |

**Canonical is not normative.** A finding here records what the investigation
supports. It binds nothing, changes no rule, and authorises no work.

**This is not a standards-compliance initiative, and no phase of it may become
one.** gzkit is not pursuing conformance with any standard in this corpus, will
not claim conformance, and is not obliged to adopt anything a standard contains.
The corpus is used as vocabulary. [`FINDINGS.md`](FINDINGS.md) F-032 and F-033
are the standing guard on this, and F-032 binds Phase 4 as a filter.

## Investigation phases

| Phase | Purpose | Lead | Status |
|---|---|---|---|
| 0 | Frame the investigation | operator | complete |
| 1 | Primary forensic assessment | Agent 0 | complete — pieces 01, 02 |
| 2 | Adversarial review of Phase 1 | Agent 1 (Astra) | **report not received in-repo** |
| 3 | Reconciliation and canonicalization | Agent 0 | **in progress** — workspace seeded 2026-09-22 |
| 4 | Design target engineering model | — | not authorised |
| 5 | Bounded pilot | — | not authorised |
| 6 | Evaluate pilot | — | not authorised |
| 7 | Adopt / revise / reject | — | not authorised |
| 8 | Incremental migration | — | not authorised |
| 9 | Measure and periodically reassess | — | not authorised |

**Roles.** Agent 0 performed Phase 1 and leads Phase 3. That lead is procedural:
it does not make Agent 0's findings authoritative over Agent 1's challenges.
Agent 1's critique enters as **evidence and challenge input**, not as a second
canonical register merged automatically into the first.

**Current gate.** Phase 3 is blocked on receiving the Phase 2 report. Astra runs
separately and deposits into this folder; nothing had landed as of 2026-09-22
([`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md) `Q-13`). **All thirteen open questions were
ruled by the operator on 2026-09-22**, one (`Q-09`) as a deferral. Until then no finding may be
promoted to `CONFIRMED`. **Phase 4 is not authorised and must not begin
implicitly** — a design candidate that goes unchallenged is still not a decision.

**Phase numbering, one caution.** Piece 01 § 12 originally titled its measurement
plan *"PROPOSED PHASE 2 INVESTIGATION PLAN"*, which meant measurement rather than
adversarial review. Those items were renumbered **`M-A` … `M-H`** on 2026-09-22
by operator ruling. A pre-2026-09-22 reference to "Phase 2" in this series may
mean the measurement program.

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

Read this section plus [`FINDINGS.md`](FINDINGS.md). That is enough; **you do not
need to replay Phase 1 or Phase 2.**

**What is confirmed.** Nothing, in the register's sense of the word. 35 findings
are recorded with evidence, but none has been through the adversarial pass, so
none is `CONFIRMED`. Three are `QUALIFIED` and two `REJECTED` — all by Agent 0's
own later work, not by the Phase 2 review.

**What is disputed.** Nothing is recorded as disputed, **because the Phase 2
report has not been read** — not because the two agents agree. Do not read
[`DISAGREEMENTS.md`](DISAGREEMENTS.md)'s emptiness as consensus.

**What is unknown.** `Q-01` … `Q-13` in [`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md),
and everything the measurement program `M-A` … `M-H` would measure.

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
- **Do not assume `F-###` ids are ratified.** They are an agent assumption
  (`Q-11`).

**Currently prohibited:**

- Beginning Phase 4 design. It is not authorised.
- Promoting any finding to `CONFIRMED` before the Phase 2 report is read.
- Creating an ADR, OBPI, REQ or TASK from anything in this directory.
- Treating a design candidate as a decision, or this register as doctrine.
- Editing the numbered pieces other than by a dated amendment.
- **Retiring or replacing the five-gate vocabulary.** Standing operator
  constraint, 2026-09-22: *"do not abandon the five gates without a discussion
  with me."* This binds Phase 4 designs too, including as a side effect.
- **Re-proposing the 16085 consequence threshold** as a replacement for the
  IRON LAW. Ruled against at `Q-05`, as weaker rather than merely different.
- Promoting `ADR-pool.feature-adr-semver-discipline` before the `kind` guard
  lands (`Q-09`).

**Next permitted step.** Receive the Phase 2 adversarial review (`Q-13`), then
reconcile it row by row into `FINDINGS.md` and `DISAGREEMENTS.md`. Phase 3 is
complete when every row carries a settled status and the disagreements are
recorded — at which point Phase 4 requires **explicit operator authorisation**,
not merely an absence of objection.

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
