# ISO/IEC/IEEE 14764 — Software engineering — Software life cycle processes — Maintenance

Research date: 2026-10-06. Persona: main-session — craftsperson, governance-aware, whole-file-reasoning, direct. Provenance: R&D run `renewing-vows`. This is a citation record, not a copy: the source is copyrighted and is cited and paraphrased only. Read live on this date at the URL(s) below.

## Bibliographic facts

- **Publishers:** ISO and IEC (ISO/IEC JTC 1/SC 7) jointly with IEEE (Computer Society, C/S2ESC), under the ISO–IEEE Partner Standards Development Organization agreement.
- **Designation:** ISO/IEC/IEEE 14764:2022. IEEE lists the same document as IEEE/ISO/IEC 14764-2021 (board approval 2021-12-08, published 2022-01-21). The year differs between the two designations; the document is the same.
- **Title:** Software engineering — Software life cycle processes — Maintenance.
- **Current edition:** third edition, 2022-01. It cancels and replaces the second edition, ISO/IEC 14764:2006. Its introduction says it harmonizes ISO/IEC 14764 with IEEE Std 1219 and updates the result for ISO/IEC/IEEE 12207:2017.
- **Status:** current. IEEE SA lists it as an Active Standard. The search-engine index of iso.org shows it published, with the 2006 edition withdrawn.
- **Publisher URLs:**
  - IEEE SA: <https://standards.ieee.org/ieee/14764/7701/>
  - ISO catalog: <https://www.iso.org/standard/80710.html>
  - Official sample pages (cover, contents, foreword, introduction, clauses 1 to 6.1.1), served by iTeh Standards: <https://cdn.standards.iteh.ai/samples/80710/9a26fc3a1a464fa286fb85d6c1eeed31/ISO-IEC-IEEE-14764-2022.pdf>
- **Access note:** iso.org refused automated fetch (HTTP 403) and showed a human-verification challenge in a browser. The challenge was not completed. ISO-side status is from the search-engine index of iso.org. IEEE pages and the sample pages were read directly.

## Scope (paraphrased)

The standard gives guidance on the software maintenance process and its activities and tasks as defined in ISO/IEC/IEEE 12207 (the 2017 edition's 6.4.13). It describes that process in more detail and defines the types of maintenance. It covers planning for maintenance while software is under development as well as maintaining existing products. It applies whatever the life cycle model, size, complexity or criticality. It excludes the operation of software, and throw-away or short-term software. It is a guidance document: its conformance clause (4) says conformance cannot be claimed to 14764 itself, only to the 12207 maintenance process, whose requirements it reproduces in boxed text.

## Claims checked

| Claim (from the record) | Verdict | Basis |
|---|---|---|
| The current edition is 2022. | VERIFIED | Sample cover: third edition, 2022-01. IEEE SA: Active, published 2022-01-21, under the IEEE designation year 2021. |
| It names the maintenance types corrective, adaptive, perfective and preventive. | VERIFIED | Defined terms: 3.1.4 corrective, 3.1.1 adaptive, 3.1.9 perfective, 3.1.10 preventive. Figure 1, in the 3.1.8 modification-request entry, shows them as types of maintenance. The text of the types-of-maintenance clause (8.2) is not public. |
| It possibly also names emergency maintenance. | VERIFIED | 3.1.5 defines emergency maintenance as an unscheduled modification that temporarily keeps a system operational until corrective maintenance is done. Note 2 to 3.1.5 says it "can be regarded as a corrective maintenance type". Note 7 to 3.1.8 says some organizations split each type into scheduled, unscheduled and emergency. |
| Implied by the record's four-way mapping: corrective, adaptive, perfective and preventive are the standard's complete set of maintenance types. | CONTRADICTED | The 2022 edition defines additive maintenance (3.1.2): a modification after delivery that adds functionality or features. It is explicitly distinguished from perfective maintenance. Figure 1 shows five types: corrective, preventive, adaptive, additive and perfective. |

## Notes for the record

The 2022 definitions, paraphrased, set against the record's mapping:

- **Corrective (3.1.4):** a modification after delivery that corrects discovered problems. Matches gzkit "fix".
- **Adaptive (3.1.1):** a modification after delivery that keeps the product usable in a changed or changing environment. Matches "vendor-alignment".
- **Perfective (3.1.9):** a modification that provides enhancements for users, improves information for users, or improves performance, maintainability or other attributes. Covers "refactor" through maintainability.
- **Preventive (3.1.10):** a modification after delivery that corrects latent faults before they occur in the live system. "Chores" map here only where a chore corrects a latent fault.
- **Additive (3.1.2):** adds functionality or features after delivery. The record's mapping has no slot for it.

Two further points bear on the mapping:

- Every maintenance *type* above is defined as a modification. Upkeep that modifies nothing falls under the broader definition of software maintenance (3.1.12, the totality of activities needed to support a software system), but under none of the types.
- Figure 1 and 3.1.8 classify a modification request as either a correction (corrective, preventive, adaptive) or an enhancement (adaptive, additive, perfective). Adaptive appears in both. 3.1.11 defines a problem report (PR) as a document that identifies and describes problems detected in a software product.
