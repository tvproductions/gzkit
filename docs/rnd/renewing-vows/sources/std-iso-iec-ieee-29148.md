# ISO/IEC/IEEE 29148 — Systems and software engineering — Life cycle processes — Requirements engineering

Research date: 2026-10-06. Persona: main-session — craftsperson, governance-aware, whole-file-reasoning, direct. Provenance: R&D run `renewing-vows`. This is a citation record, not a copy: the source is copyrighted and is cited and paraphrased only. Read live on this date at the URL(s) below.

## Bibliographic facts

- **Publishers:** ISO and IEC (ISO/IEC JTC 1/SC 7) jointly with IEEE (Computer Society, Software & Systems Engineering Standards Committee, C/S2ESC), under the ISO–IEEE Partner Standards Development Organization agreement.
- **Designation:** ISO/IEC/IEEE 29148:2018. IEEE lists the same document as IEEE/ISO/IEC 29148-2018.
- **Title:** Systems and software engineering — Life cycle processes — Requirements engineering.
- **Current edition:** second edition, 2018-11 (IEEE: board approval 2018-10-23, published 2018-11-30). It cancels and replaces the first edition, ISO/IEC/IEEE 29148:2011, which had itself superseded IEEE 830-1998, IEEE 1233-1998 and IEEE 1362-1998.
- **Status:** current. IEEE SA lists 29148-2018 as an Active Standard. A third edition is in preparation: IEEE lists project P29148 (Active PAR, approved 2025-09-10) as superseding 29148-2018, and the search-engine index of iso.org lists ISO/IEC/IEEE DIS 29148 at the enquiry (DIS) stage. The same index reports that ISO confirmed the 2018 edition at systematic review in 2024.
- **Publisher URLs:**
  - IEEE SA, 2018 edition: <https://standards.ieee.org/standard/29148-2018.html>
  - IEEE SA, revision project P29148: <https://standards.ieee.org/ieee/29148/12262/>
  - IEEE SA, 2011 edition (superseded by 29148-2018): <https://standards.ieee.org/ieee/29148/5289/>
  - ISO catalog, 2018 edition: <https://www.iso.org/standard/72089.html>; revision in progress: <https://www.iso.org/standard/94091.html>
  - Official sample pages (cover, contents, foreword, introduction, clauses 1 to 3.1.34), served by iTeh Standards: <https://cdn.standards.iteh.ai/samples/72089/62bb2ea1ef8b4f33a80d984f826267c1/ISO-IEC-IEEE-29148-2018.pdf>
- **Access note:** iso.org refused automated fetch (HTTP 403) and showed a human-verification challenge in a browser. The challenge was not completed. ISO-side status is therefore taken from the search-engine index of iso.org, not from a direct read. Edition, contents and definitions were read directly from the IEEE SA pages and the official sample pages.

## Scope (paraphrased)

The standard specifies the processes that produce requirements for systems and software products, including services, across the life cycle. It gives guidance for applying the requirements-related processes of ISO/IEC/IEEE 15288 and ISO/IEC/IEEE 12207. It specifies which information items those processes produce, what each must contain, and how they may be formatted. Its normative references are the dated editions ISO/IEC/IEEE 15288:2015 and ISO/IEC/IEEE 12207:2017.

## Claims checked

| Claim (from the record) | Verdict | Basis |
|---|---|---|
| The current edition is 2018. | VERIFIED | IEEE SA 2018 page: Active Standard, published 2018-11-30. Sample cover: second edition, 2018-11. A third edition is in work (IEEE P29148; ISO DIS 29148), so the record should cite the year explicitly. |
| It defines a concept of operations (ConOps) and an operational concept (OpsCon). | VERIFIED | Sample pages: both are defined terms, at 3.1.5 (concept of operations) and 3.1.16 (operational concept). The public contents list Annex A (normative), System operational concept, and Annex B (informative), Concept of operations. |
| It defines the ConOps and/or the OpsCon as an *information item*. | NOT VERIFIED | The clause that lists the information items (clause 7) is not in the public preview. The public contents place the BRS, StRS, SyRS and SRS under clause 8 (guidelines for information items) and clause 9 (information item content). The OpsCon and the ConOps sit outside those clauses, in Annexes A and B. Operational-concept material also appears as a section *inside* the BRS content (9.3.16, high-level operational concept) and the StRS content (9.4.16, operational concept). Whether the standard classes either annex as an information item cannot be read from public material. |
| The stakeholder requirements specification (StRS) and system requirements specification (SyRS) are information items it defines. | VERIFIED | Public contents: 8.3 (StRS) and 8.4 (SyRS) under clause 8, guidelines for information items. Their content is set out in 9.4 and 9.5 under clause 9, information item content. Definitions: 3.1.29 (StRS) and 3.1.33 (SyRS). |
| It treats "constraints" as a requirement category. | VERIFIED | 3.1.7 defines a constraint as a limitation imposed from outside on the system, its design or implementation, or on the process used to develop or modify it. 3.1.19 defines a requirement as a statement of a need together with its associated constraints and conditions. The SyRS and SRS definitions (3.1.33, 3.1.27) list design constraints among the kinds of requirement each collects. The StRS definition (3.1.29) lists constraints. Constraint headings recur in the content clauses: 9.3.12 and 9.3.19 (BRS), 9.4.12 and 9.4.19 (StRS), 9.6.16 (SRS). |
| Load-bearing: the ConOps is the information item from which stakeholder requirements derive, so it sits *above* a product requirements document. In 29148's terms, the ConOps/OpsCon comes before the StRS. | NOT VERIFIED | No public text states this ordering, so the claim is an inference. The nearest public statement is Note 2 to 3.1.5: the ConOps "provides the basis for bounding the operating space, system capabilities, interfaces and operating environment". That gives the ConOps a bounding role; it does not say the StRS derives from it. The public structure also complicates a strict "ConOps above" tier. The ConOps annex is informative. Operational-concept content is a section *inside* the BRS (9.3.16) and the StRS (9.4.16). The business-level requirements collection is the BRS (3.1.4), not the ConOps. The contents list the business or mission analysis process (6.2) before the stakeholder needs and requirements definition process (6.3), but that is an order of processes, not a derivation rule. Settling the claim needs the full text of 6.2–6.3 and Annexes A–B. |

## Notes for the record

- In 29148:2018 the nearest analogue of a product requirements document is the BRS or the StRS, not something above them. Name which one is meant before claiming that the ConOps sits above it.
- Both the ConOps definition (3.1.5) and the OpsCon definition (3.1.16) cite ANSI/AIAA G-043A-2012e as their source. If the record leans on the ConOps concept itself, that guide is the upstream text.
- 29148:2018 binds dated references (15288:2015, 12207:2017). Both have since been superseded: the IEEE page for 12207-2026 names ISO/IEC/IEEE 15288:2023, and 12207:2017 is replaced by 12207:2026 (see `std-iso-iec-ieee-12207.md`).
