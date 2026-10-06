# ISO/IEC/IEEE 42010 — Software, systems and enterprise — Architecture description

Research date: 2026-10-06. Persona: main-session — craftsperson, governance-aware, whole-file-reasoning, direct. Provenance: R&D run `renewing-vows`. This is a citation record, not a copy: the source is copyrighted and is cited and paraphrased only. Read live on this date at the URL(s) below.

## Bibliographic facts

- **Publishers:** ISO and IEC (ISO/IEC JTC 1/SC 7) jointly with IEEE (Computer Society, C/S2ESC), under the ISO–IEEE Partner Standards Development Organization agreement.
- **Designation:** ISO/IEC/IEEE 42010:2022. IEEE lists the same document as IEEE/ISO/IEC 42010-2022.
- **Title:** Software, systems and enterprise — Architecture description. The 2011 edition was titled Systems and software engineering — Architecture description.
- **Current edition:** second edition, 2022-11 (IEEE: board approval 2022-09-21, published 2022-11-07). It cancels and replaces the first edition, ISO/IEC/IEEE 42010:2011.
- **Status:** current. IEEE SA lists it as an Active Standard. The search-engine index of iso.org shows it published (stage 60.60) on 2022-11-07, with the 2011 edition withdrawn on the same date.
- **Publisher URLs:**
  - IEEE SA: <https://standards.ieee.org/ieee/42010/6846/>
  - ISO catalog: <https://www.iso.org/standard/74393.html>
  - Official sample pages (cover, contents, foreword, introduction, clauses 1 to 5.2.3), served by iTeh Standards: <https://cdn.standards.iteh.ai/samples/74393/fc7b7f103d8446a4b87a3261e31370d3/ISO-IEC-IEEE-42010-2022.pdf>
- **Access note:** iso.org refused automated fetch (HTTP 403) and showed a human-verification challenge in a browser. The challenge was not completed. ISO-side status is from the search-engine index of iso.org. Edition, contents and definitions were read directly from the IEEE SA page and the official sample pages.

## Scope (paraphrased)

The standard specifies requirements for the structure and expression of an architecture description (AD) for many kinds of entity, from software and systems to enterprises, systems of systems, product lines, service lines, technologies and business domains. It separates an entity's architecture from the AD that expresses it; architectures themselves are not its subject. It specifies requirements for architecture description frameworks, architecture description languages, architecture viewpoints and model kinds, and the conformance criteria for each. It prescribes no process, method, notation, tool, format or medium for creating or recording an AD.

## Claims checked

| Claim (from the record) | Verdict | Basis |
|---|---|---|
| The current edition is 2022. | VERIFIED | IEEE SA: Active Standard, published 2022-11-07. Sample cover: second edition, 2022-11. Its foreword says this edition cancels and replaces the 2011 edition. |
| It names architecture decisions, and their rationale, as something an architecture description records. | VERIFIED | Public contents: 5.2.12 (architecture decisions and rationale, within the conceptual foundations) and 6.10 (recording of architecture decisions and rationale), with subclauses 6.10.1 (decision recording) and 6.10.2 (rationale recording). Clause 6 is the specification of an AD, and clause 4 makes clause 6 the basis of any conformance claim for an AD. Whether 6.10 is worded as a requirement or a recommendation is not visible publicly. |
| Architecture decisions are an *element* of an AD in the standard's defined sense (AD element, 3.4). | NOT VERIFIED | 3.4 defines an AD element as an "identified or named part of an architecture description". Note 1 to 3.4 gives a non-exhaustive list of AD elements: stakeholders, concerns, stakeholder perspectives, aspects, ADLs, ADFs, correspondences and correspondence methods, views, view components, viewpoints and model kinds. Decisions and rationale are not on it. The normative text of 6.10, which could settle the question, is not public. |

## Notes for the record

- Cite ISO/IEC/IEEE 42010:2022, 6.10, for decision and rationale recording, rather than describing decisions as an "AD element".
- The public terms and definitions (3.1–3.19) include no "architecture decision record" or "ADR". Reserving ADR for architecture decisions is therefore the record's own usage choice. It is consistent with 6.10's decision recording, but the standard does not coin the term.
