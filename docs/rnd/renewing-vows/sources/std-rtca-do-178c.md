# RTCA DO-178C — Software Considerations in Airborne Systems and Equipment Certification

Research date: 2026-10-06. Persona: main-session — craftsperson, governance-aware, whole-file-reasoning, direct. Provenance: R&D run `renewing-vows`. This is a citation record, not a copy: the source is copyrighted and is cited and paraphrased only. Read live on this date at the URL(s) below.

## Bibliographic facts

- **Publisher:** RTCA, Inc. The document was prepared by RTCA SC-205 jointly with EUROCAE WG-71; EUROCAE publishes the twin as ED-12C.
- **Designation:** RTCA DO-178C.
- **Title:** Software Considerations in Airborne Systems and Equipment Certification.
- **Edition:** DO-178C, issued 2011-12-13, according to the RTCA store. EUROCAE ED-12C is dated January 2012 and has a Corrigendum 1 (February 2021) that fixes minor editorial errors. RTCA notes that errata against DO-178C exist.
- **Status:** current. RTCA's DO-178() page calls DO-178C the current version and says FAA Advisory Circular AC 20-115D references it.
- **Related RTCA documents:**
  - DO-248C/ED-94C: supporting information and FAQs.
  - DO-330: tool qualification.
  - DO-331, DO-332, DO-333: technology supplements.
  - DO-278A/ED-109A: the counterpart for CNS/ATM systems.
- **Publisher URLs:**
  - RTCA store: <https://my.rtca.org/productdetails?id=a1B36000001IcmqEAC>
  - RTCA DO-178() page: <https://www.rtca.org/do-178/>
  - EUROCAE ED-12C: <https://www.eurocae.net/product/ed-12c-software-considerations-in-airborne-systems-and-equipment-certification/>
  - EUROCAE ED-12C Corrigendum 1: <https://www.eurocae.net/product/ed-12c-corr-1-software-considerations-in-airborne-systems-and-equipment-certification-corrigendum-1/>
- **RTCA-hosted explanatory papers used:** FAS Topic Papers (FTPs) from the joint RTCA/EUROCAE Forum for Aeronautical Software, listed at <https://www.rtca.org/sc-240/forum-for-aeronautical-software/>. Every FTP says it is informational and educational only, and that it is not official RTCA/EUROCAE policy or position. This record relies on an FTP only where it quotes DO-178C text or gives its location. Papers used:
  - FTP1034 rev 3: <https://www.rtca.org/wp-content/uploads/2024/06/FTP1034_3-PUBLICATION.pdf>
  - FTP1050 rev 3: <https://www.rtca.org/wp-content/uploads/2024/06/FTP1050_3-PUBLICATION.pdf>
  - FTP1000 rev 9: <https://www.rtca.org/wp-content/uploads/2020/12/FTP1000_9.pdf>
  - FTP1042 rev 3: <https://www.rtca.org/wp-content/uploads/2024/06/FTP1042_3-PUBLICATION.pdf>
  - FTP1052 rev 2: <https://www.rtca.org/wp-content/uploads/2020/12/FTP1052_2.pdf>
  - FTP1055 rev 3: <https://www.rtca.org/wp-content/uploads/2020/12/FTP1055_3.pdf>

## Scope (paraphrased)

The RTCA store describes DO-178C as recommendations for producing airborne software that performs its intended function with a level of confidence in safety that meets airworthiness requirements. It also says that showing compliance with DO-178C's objectives is the primary means of gaining approval for software in civil aviation products. EUROCAE describes ED-12C as guidance for determining, consistently and with acceptable confidence, that the software aspects of airborne systems and equipment comply with airworthiness requirements.

## Claims checked

| Claim (from the record) | Verdict | Basis |
|---|---|---|
| DO-178C (2011) is the current version. | VERIFIED | RTCA store: issued 2011-12-13 by SC-205. The RTCA DO-178() page calls it the current version. |
| It defines software levels A through E. | NOT VERIFIED | Levels A, B, C and D appear in RTCA-hosted FAS papers (FTP1034, FTP1042, FTP1052). Level E does not appear in any public RTCA or EUROCAE material read, and the definitions of the levels are in the purchased text. |
| Its objectives are tabulated in Annex A. | VERIFIED | FTP1034 quotes objectives 8 and 9 of Annex A Table A-5 and states: "DO-178C/ED-12C Annex A contains a summary of the objectives". It notes that the full objective text is in the body of the document (6.6a–b) and also cites Table A-7. |
| Some objectives must be met with independence. | VERIFIED | FTP1034 says the structural-coverage objectives in Table A-7 (objectives 5–7), and objective 9 of Table A-5, apply at Levels A–C, with independence required at Levels A and B. FTP1050 quotes DO-178C's glossary definition of independence. For verification, the work must be done by someone other than the developer of the item being verified. For software quality assurance, independence also includes the authority to ensure corrective action. |
| It requires bidirectional traceability. | NOT VERIFIED | FTP1050 says bi-directional traceability through the software development artifacts must be established and maintained. That is the FAS group's own guidance: it neither quotes nor locates DO-178C text. DO-178C's wording on trace data is not publicly inspectable. |
| Its structural coverage criteria (statement, decision, MC/DC) are set by software level. | NOT VERIFIED | Public FAS papers place the structural-coverage objectives at Annex A Table A-7, objectives 5–7 (FTP1034). They say Level D requires no structural coverage (FTP1042). They note an extra object-code objective, at 6.4.4 item c, that applies only at Level A (FTP1052). None of the public material read names the statement, decision and MC/DC criteria or maps them to levels. |
| Section 11 enumerates the software life cycle data. | VERIFIED | FTP1050 quotes Section 11's statement of what life cycle data is for: planning, directing, explaining, recording or evidencing activities. |
| Problem reports, the Software Accomplishment Summary (SAS) and the Software Configuration Index (SCI) are DO-178C life cycle data. | VERIFIED | FTP1050 treats DO-178C problem reports and the SAS as required artifacts: open problem reports must be listed, with justification, in the SAS. FTP1000 names both the SAS and the SCI. Where each sits within Section 11 is not shown. |
| Problem reports are § 11.17, and the SAS and SCI have their own Section 11 subsections. | NOT VERIFIED | Clause number unverified. No public RTCA or EUROCAE material read gives Section 11 subsection numbers for these items. |

## Notes for the record

The public FTPs do confirm these DO-178C section numbers, which the record may use:

- subsection 12.2: the criteria for deciding whether a tool needs qualification (FTP1055); FTP1000 cites tool criteria 1 and 3 under 12.2.2;
- paragraph 7.2.2: the definition of a baseline (FTP1050);
- 6.6a–b: the full text of the parameter data item objectives (FTP1034).
