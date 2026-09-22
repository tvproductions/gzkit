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

These records are analysis, not canon. Nothing here binds until it is carried
into a rule, an ADR, or the corpus by the ordinary route. Where a piece
disagrees with an earlier piece, the later one says so explicitly rather than
silently superseding it.

## Pieces

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

## Related

- [`docs/governance/state-doctrine.md`](../state-doctrine.md) — the L1/L2/L3 layers these pieces reason about
- [`docs/governance/trust-doctrine.md`](../trust-doctrine.md) — trust-chain poisoning, gzkit's own rediscovery of V&V independence
- [`docs/governance/advisory-rules-audit.md`](../advisory-rules-audit.md) — the Mechanical/Judgment scorecard the pieces read as an honesty instrument
- [`docs/governance/req-scope-discipline.md`](../req-scope-discipline.md) — the three-kind REQ taxonomy and the measurement that produced it
