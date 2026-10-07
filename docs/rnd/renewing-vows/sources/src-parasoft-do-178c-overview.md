# Parasoft — "What Is RTCA DO-178C? Overview & Compliance in Aerospace"

Research date: 2026-10-07. Persona: main-session — craftsperson, governance-aware, whole-file-reasoning, direct. Provenance: R&D run `renewing-vows`; the operator supplied the URL on 2026-10-07 in answer to the question of which texts were still unread. This is a citation record, not a copy: the source is copyrighted and is cited and paraphrased, with short quotations only. Read live on this date at the URL below.

## Bibliographic facts

- **Publisher:** Parasoft, a vendor of software testing tools. The page is in its Learning Center and promotes its products in places.
- **Title:** What Is RTCA DO-178C? Overview & Compliance in Aerospace.
- **Author and date:** none shown on the page.
- **URL:** <https://www.parasoft.com/learning-center/do-178c/what-is/>
- **Retrieval:** HTTP 200, 185,360 bytes of HTML, about 29,500 characters of text after markup was removed. The passages below were read from the downloaded page text by the session, not from a summary of it.
- **Kind of source:** secondary. It is a vendor's overview of DO-178C, section by section. It is not RTCA's text and it is not RTCA's statement about its own document.

## What a secondary source can and cannot do here

The run's companion record `std-rtca-do-178c.md` holds each DO-178C claim against the publisher's public material. This page cannot move a claim there to VERIFIED, because a vendor's account of a standard is an assertion about it. What it can do is show that a claim the run carried from memory is also what a practitioner source says, and show which claims it does not address at all. The last column says which.

## Claims checked

| Claim (from the record) | On this page | Effect |
|---|---|---|
| DO-178C has software levels A to E. | Yes. The page gives the history as five levels lettered A through E, with "Level A was the most stringent and Level E meant no safety requirement." | Secondary support for level E, which the DO-178C record left not verified. |
| A level is assigned from the severity of the failure condition. | Yes. It places the determination in Section 2 and ties levels to outcomes: a catastrophic result "would be classified as software level A"; hazardous "would be software level B"; down to level E, where there is no safety concern. | Secondary support. This is the model the run's integrity-level decision says gzkit's scale does not use. |
| Section 11 is the software life cycle data. | Yes. "Section 11 discusses artifacts like the data and documentation produced during the software life cycle." The page titles it "Software Life Cycle Data, Section 11". | Secondary support for the section number. |
| Problem reports are life cycle data, at § 11.17. | Partly. "Problem reports" is in the page's list of life cycle data items. The number 11.17 is not on the page. | The item is supported; the clause number stays not verified. |
| The software configuration index and the software accomplishment summary are life cycle data. | Yes. Both are named in the same list. | Secondary support for both terms. |
| Objectives are tabulated in Annex A, by level. | Partly. The page cites "Table A-1" and "Table A-2" and says of planning that there are "seven objectives that must be satisfied based on the software level (A-D)". It gives no total and no count per level. | The tables are supported; counts stay not verified. |
| Bidirectional traceability is required, to a depth that varies by level. | Yes. "The depth of traceability varies based on the software level", described from level D (requirements to tests) through levels C and B (to low-level requirements and source code) to level A (to object code). | Secondary support. |
| Testing is requirements-based. | Yes, as history: DO-178B "advised not to look at the code to create test cases, but to look at your requirements", backed by structural coverage. | Secondary support. |
| Structural coverage criteria differ by level (statement, decision, MC/DC). | Partly. The page names "statement, branch, and MC/DC coverage" and object-code coverage, and does not say which level requires which. | The criteria are named; the mapping to levels stays not verified. |
| Independence varies by level. | Named only. The page lists "Variations in the objectives, independence, software life cycle data, and control categories by software level" among what DO-178C provides, and says nothing more. | Stays not verified. |
| Tool qualification is in DO-330. | Yes. Requirements for each tool qualification level "are described in DO-330". | Agrees with `std-rtca-do-330.md`, already verified. |
| DO-178C was published 2011-12-13. | Differs. The page says "Released in January 2012". | The RTCA product page governs; the difference is a vendor's date against the publisher's. |
| DO-178C points to ARP4754B for system development. | Differs. The page names "SAE ARP4754A" and plain "ARP4754". It does not mention ARP4754B or ARP4761. | No support for the current revisions; the page appears to predate or ignore them. |

## What the page adds that the run had not recorded

- **Configuration status accounting is a DO-178C activity.** The page lists the software configuration management process activities of Section 7, among them "Configuration status accounting" and "Problem reporting, tracking, and corrective action". The run sourced that term to EIA-649 and MIL-HDBK-61B only.
- **Control categories.** Items are treated as Control Category 1 or 2 by level; CC1 items "must undergo full problem reporting processes, formal change review, and release processes". The run has no row for this.
- **The twelve sections by number and title**, from Section 2 (system aspects) to Section 12 (additional considerations), with Section 6 as verification, Section 7 as configuration management, Section 8 as quality assurance and Section 9 as certification liaison.

## Notes for the record

- The page is an overview written to sell tooling. Where it and the RTCA product page differ, as on the publication date, the publisher governs.
- Nothing here gives a clause number below section level. Rows that cite § 11.17, an Annex A count, or coverage by level still need the standard.
