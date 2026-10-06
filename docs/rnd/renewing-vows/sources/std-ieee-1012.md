# IEEE 1012 — IEEE Standard for System, Software, and Hardware Verification and Validation

Research date: 2026-10-06. Persona: main-session — craftsperson, governance-aware, whole-file-reasoning, direct. Provenance: R&D run `renewing-vows`. This is a citation record, not a copy: the source is copyrighted and is cited and paraphrased only. Read live on this date at the URL(s) below.

## Bibliographic facts

- **Publisher:** IEEE (IEEE Standards Association; Computer Society, C/S2ESC).
- **Designation:** IEEE 1012-2024 is current. The record cites IEEE 1012-2016.
- **Title:** IEEE Standard for System, Software, and Hardware Verification and Validation.
- **Current edition:** 2024 (board approval 2024-11-12, published 2025-08-22). It supersedes IEEE 1012-2016.
- **Status:**
  - 1012-2024 is Active.
  - 1012-2016 (board approval 2016-05-15, published 2017-09-29, with corrigendum 1012-2016/Cor 1-2017) is Superseded by 1012-2024.
  - A further revision, P1012, holds an Active PAR approved 2026-03-26 to supersede 1012-2024.
- **Publisher URLs:**
  - IEEE SA, 1012-2024: <https://standards.ieee.org/ieee/1012/7324/>
  - IEEE SA, 1012-2016 (superseded): <https://standards.ieee.org/ieee/1012/5609/>
  - IEEE SA, revision project P1012: <https://standards.ieee.org/ieee/1012/12536/>
  - SEVOCAB entry: <https://pascal.computer.org/sev_display/search.action?term=independent+verification+and+validation>
- **Access note:** SEVOCAB is the systems and software engineering vocabulary database run jointly by the IEEE Computer Society and ISO/IEC JTC 1/SC 7. It is published periodically as ISO/IEC/IEEE 24765. It records each definition with its source standard and clause. It is used here as the standards bodies' own public statement of the 1012 definition.

## Scope (paraphrased)

Verification and validation (V&V) processes determine whether the products of an activity conform to that activity's requirements, and whether the product satisfies its intended use and user needs. V&V life cycle requirements are set by integrity level. The scope covers systems, software and hardware and their interfaces, including items that are developed, maintained or reused (legacy, commercial off-the-shelf, non-developmental). V&V comprises analysis, evaluation, review, inspection, assessment and testing.

## Claims checked

| Claim (from the record) | Verdict | Basis |
|---|---|---|
| The current edition is 2016. | CONTRADICTED | The IEEE SA pages for 1012-2016 and 1012-2024 show 2016 superseded by 2024. |
| The 2016 edition carries a 2017 corrigendum. | VERIFIED | The IEEE SA page for 1012-2016 lists 1012-2016/Cor 1-2017. That corrigendum belongs to the superseded edition. |
| It defines independent V&V (IV&V) in terms of technical, managerial and financial independence. | VERIFIED | SEVOCAB gives the IV&V definition with its source as IEEE 1012-2024, clause 3.1: V&V performed by an organization that is "technically, managerially, and financially independent of the development organization". This was checked against the 2024 edition's definition; the 2016 wording was not inspected. If the record cites an annex elaborating the three kinds of independence, its clause number is unverified. |

## Notes for the record

- The definition requires a performing *organization* that is independent of the development organization on all three axes. Mapping gzkit's Step 4b adversary review to IV&V therefore needs an argument for managerial and financial independence, not only technical independence. A review step that is not independent on all three falls outside the definition.
- The IEEE abstracts for 1012-2016 and 1012-2024 do not mention independence; they emphasise integrity levels.
