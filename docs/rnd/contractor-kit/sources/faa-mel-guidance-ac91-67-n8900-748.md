# FAA MEL guidance — AC 91-67 (6/28/91) and Notice N 8900.748 (8/9/25) (verbatim); FAA Order 8900.1 Vol. 4 Ch. 4 NOT retrieved

Retrieval date: 2026-10-26. Persona: primary-source researcher. This file holds FAA-issued text only. Every passage is quoted; nothing below the provenance block is summary.

## Provenance and what was / was not captured

### Not retrieved: FAA Order 8900.1, Volume 4, Chapter 4 (MELs and CDLs), and MMEL Policy Letters PL-25, PL-34, PL-36

- `https://fsims.faa.gov/PICDetail.aspx?docId=8900.1,Vol.4,Ch4,Sec1` — host does not resolve (`host fsims.faa.gov` → NXDOMAIN, 2026-10-26). The FSIMS site has been retired; FAA's own comment logs on faa.gov say its content moved to the Dynamic Regulatory System (DRS).
- `https://drs.faa.gov` — returns HTTP 200 but only a JavaScript single-page-application shell (`<title>Dynamic Regulatory System</title>`, Angular bundles `main-*.js`); no document text is served to a plain HTTP client. No attempt was made to reverse-engineer the application's internal API or to use a scripted browser; no third-party mirror was used as a substitute. **Gap: the 8900.1 V4C4 text defining (M)/(O) procedures, deferral, placarding, repair categories/intervals and MEL preamble, and the PL-25 (MMEL and MEL Definitions), PL-34 (MMEL and MEL Preamble) and PL-36 (Part 91 MEL Approval and Preamble) texts, remain unread.** Reading them needs either an interactive browser session on DRS or an operator-supplied PDF.
- faa.gov hosts no copy of these: web searches (2026-10-26) for V4C4 and for PL-25/PL-34 on faa.gov returned only notices, MMEL drafts and MMEL comment logs that refer to them. FAA draft MMELs on faa.gov (e.g. `https://www.faa.gov/aircraft/draft_docs/mmel/MMEL_DA-2000EX_EASy_Rev_10_Draft.pdf`, created 2026-05-27) carry only a pointer: "Refer to the current FAA MMEL Policy Letter (PL)- 25, MMEL/MEL Definitions, found on the FAA" DRS website, and the same for PL-34. Third-party copies seen in search results (a boeing.com-hosted B737 MMEL .docx, a tc.gc.ca-hosted MMEL, vendor webinar PDFs, a pilot forum post quoting PL-25 Rev. 16) were not used.
- Secondary bibliographic facts, from FAA notices on faa.gov, not from the policy letters themselves: N 8900.694 (eff. 4/22/24, cancelled 4/22/25) says "PL-34 serves as the preamble for Master Minimum Equipment Lists (MMEL) and MELs; it does not grant relief." N 8900.748 (below) names Order 8900.1 Volume 4, Chapter 4, Section 2 as "MEL Requirements for 14 CFR Part 91 Operators and 14 CFR Parts 133, 137, and 141 Certificate Holders". The repair categories A–D are therefore available in this file only as the AC 91-67 statements that they exist and to whom they apply, not as their definitions.

### Captured, Part 1: FAA Notice N 8900.748

- URL: https://www.faa.gov/documentLibrary/media/Notice/N_8900.748.pdf (HTTP 200, application/pdf, 303,622 bytes, 26 pages).
- Edition: N 8900.748, "Revised Minimum Equipment List (MEL) LOA D095 and LOA D195 Templates Per 14 CFR Parts 91, 133, 137, and 141", Effective Date 8/9/25, Cancellation Date 8/9/26 (so expired as of retrieval; its paragraph 7 states the content "has been incorporated into Order 8900.1, Volume 4, Chapter 4, Section 2"). Initiated by AFS-800.
- Captured: paragraphs 1–7 and the signature line; Appendix A (sample LOA D095, Part 91) and Appendix E (sample LOA D195, Part 91) in full. Not captured: Appendices B–D and F–H (the same templates for Parts 133, 137, 141).
- Handling: born-digital PDF; text extracted with `pdftotext -layout`, then page headers/footers ("8/9/25 N 8900.748", "Appendix X", page numbers) dropped and each paragraph's wrapped lines joined with single spaces. The paragraph 5a appendix table and each LOA's empty "Table 1 – Authorized Aircraft" are re-rendered as Markdown tables; a URL split by a line break ("orders_no tices") is rejoined. No words changed.

### Captured, Part 2: Advisory Circular AC 91-67

- URL: https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_91-67.pdf (HTTP 200, application/pdf, 5,558,986 bytes, 34 pages; SHA-256 `790ac4d48a22db095bf1bbea7330503936ae095ba9fdb64f08f0c4209143d5f8`).
- Edition: AC 91-67, "Minimum Equipment Requirements for General Aviation Operations Under FAR Part 91", Date 6/28/91, Initiated by AFS-820. Current-status note: N 8900.680 (eff. 10/16/23, on faa.gov) still cites "AC 91-67, Minimum Equipment Requirements for General Aviation Operations Under 14 CFR Part 91, § 91.213" as the AC containing "detailed information concerning MEL development and content"; a draft "AC 91-67A Coord Copy" exists on faa.gov draft_docs and was not read. Whether 91-67 is still the current edition was not otherwise verified.
- The PDF is a 1991 scan with a poor embedded OCR layer (e.g. "FAR 5 43.9", "accordancewith"). The text below was therefore **transcribed by reading rendered page images** (pdftoppm, 110 dpi), not copied from the OCR layer. Transcription choices: italic run-in headings shown in italics; underlining noted in square brackets; editorial notes in square brackets; flow-chart box text given in reading order.
- Captured: cover page paragraphs 1–4; paragraph 5 (Background); paragraph 6 (Definitions a–aa) in full; Chapter 1 paragraphs 1–8 and Figure 1; Chapter 2 paragraphs 13–14 and Figure 2; Chapter 3 paragraphs 19–23 (through 23f(2)(iv)) and Figure 3. Not captured: paragraph 7 (Comments Invited) and signature block; table of contents; Figure 4 (discrepancy record) and anything after PDF page 21; Appendices 1–4 (sample MMEL documents, sample LOA, sample title page, commonly asked questions).

---

## Part 1 — FAA Notice N 8900.748 (Effective 8/9/25; Cancellation 8/9/26)

NOTICE — U.S. DEPARTMENT OF TRANSPORTATION, FEDERAL AVIATION ADMINISTRATION — N 8900.748 — National Policy — Effective Date: 8/9/25 — Cancellation Date: 8/9/26

SUBJ: Revised Minimum Equipment List (MEL) LOA D095 and LOA D195 Templates Per 14 CFR Parts 91, 133, 137, and 141

1. Purpose of This Notice. This notice announces a nonmandatory revision to Letter of Authorization (LOA) D095, MMEL and a Procedures Document Used as an MEL, and LOA D195, Minimum Equipment List (MEL). The template revisions apply to Title 14 of the Code of Federal Regulations (14 CFR) part 91 operators and 14 CFR parts 133, 137, and 141 certificate holders.

2. Audience. The primary audience for this notice is the Flight Standards (FS) Safety Assurance offices’ aviation safety inspectors (ASI) assigned to provide oversight of 14 CFR part 91 operators and 14 CFR parts 133, 137, and 141 certificate holders. The secondary audience includes the Safety Standards and Foundational Business offices.

3. Where You Can Find This Notice. You can find this notice on the MyFAA employee website at https://employees.faa.gov/tools_resources/orders_notices and the Dynamic Regulatory System (DRS) at https://drs.faa.gov. Operators and the public can find this notice on the Federal Aviation Administration’s (FAA) website at https://www.faa.gov/regulations_policies/orders_notices and DRS.

4. Background.

a. To reduce unnecessary administrative work, Table 2, Responsible Person, has been removed from 14 CFR part 91 LOAs D095 and D195, as this information is addressed in the operator’s part 91 LOA A001, Issuance and Applicability, revision 02c or later.

b. To reduce unnecessary administrative work, the “Remarks” column has been removed from LOA D195, Table 1, Authorized Aircraft.

c. To emphasize the requirement for a procedures document, the LOA D095 title has been changed from “MMEL Used as an MEL” to “MMEL and a Procedures Document Used as an MEL.”

5. Guidance.

a. Appendices. Appendices to this notice show the revised templates. This notice contains the following:

| Appendix | Authorizing Document | Paragraph | Applicable to Part |
|---|---|---|---|
| A | LOA | D095 | 91 |
| B | LOA | D095 | 133 |
| C | LOA | D095 | 137 |
| D | LOA | D095 | 141 |
| E | LOA | D195 | 91 |
| F | LOA | D195 | 133 |
| G | LOA | D195 | 137 |
| H | LOA | D195 | 141 |

b. FAA Order 8900.1, Flight Standards Information Management System. Volume 4, Chapter 4, Section 2, MEL Requirements for 14 CFR Part 91 Operators and 14 CFR Parts 133, 137, and 141 Certificate Holders.

6. Action.

a. Nonmandatory Revision. This is a nonmandatory revision to 14 CFR parts 91, 133, 137, and 141 LOA D095 and D195 templates.

b. Verification of 14 CFR Part 91 LOA A001 Revision and Responsible Person. When either 14 CFR part 91 LOA D095 or part 91 LOA D195 is issued or reissued, ASIs must:

(1) Ensure the operator has been issued 14 CFR part 91 LOA A001 revision 02c or later,

(2) Verify that the Responsible Person named in Table 1 of LOA A001 is the same as the Responsible Person named in the operator’s MEL request letter, and

(3) Update and reissue LOA A001 as required.

7. Disposition. The information in this notice has been incorporated into Order 8900.1, Volume 4, Chapter 4, Section 2. Direct questions or comments concerning the information in this notice to the General Aviation and Commercial Division (AFS-800) at 202-267-1100.

Robert Reckert for Lawrence Fields Executive Director, Flight Standards Service

### N 8900.748 Appendix A

Appendix A. Sample LOA D095, MMEL and a Procedures Document Used as an MEL: 14 CFR Part 91

1. This Letter of Authorization (LOA) is issued under the provisions of 14 CFR Part 91, § 91.213(a)(2) and authorizes the operator, [Operator Name], to operate the aircraft listed below in Table 1, Authorized Aircraft, using the aircraft make, model, and series (M/M/S)-specific Master Minimum Equipment List (MMEL) and the operator’s procedures document that meets the detailed criteria stated in this LOA, as a minimum equipment list (MEL).

2. Operations to which § 91.213(a) applies must be conducted in accordance with the M/M/S-specific MMEL, the operator’s procedures document, and this LOA; otherwise, relief under the provisions of § 91.213(a) is not available to the operator.

3. The M/M/S-specific MMEL, the operator’s procedures document, and this LOA together are an approved MEL and constitute a Supplemental Type Certificate (STC) for the aircraft and must be available to the pilot in command (PIC) when operating under the provisions of § 91.213(a).

4. Authorized Aircraft. The operator is authorized to use an approved MEL, as defined in subparagraph 3 above, for the aircraft listed in Table 1 below, provided the conditions and limitations of this LOA are met.

Table 1 – Authorized Aircraft

| Aircraft Serial Number | Aircraft Registration Number | Aircraft M/M/S |
|---|---|---|
| | | |

5. The operator’s procedures document must, per § 91.213(a)(5), contain the following:

a. The operator’s name, aircraft serial and registration numbers (or “Fleet”), aircraft M/M/S, and the MMEL revision number on which the MEL is based.

b. Maintenance (M) and Operations (O) procedures that correspond with the (M) and (O) provisos listed in the M/M/S-specific MMEL, based on the items installed on the operator’s aircraft for which the operator desires MEL relief.

(1) The operator may use (M) and (O) procedures as published by the manufacturer, or use operator-developed (M) and (O) procedures that have been developed using the guidance provided in the approved Aircraft Flight Manual (AFM), Aircraft Maintenance Manual (AMM), manufacturer’s recommendations, engineering specifications, or other appropriate sources.

(2) The (M) and (O) procedures must meet the intent of the (M) and (O) provisos in the MMEL and must never be less restrictive than the MMEL.

(3) Such (M) or (O) procedures must be accomplished in accordance with the provisions and requirements of 14 CFR Part 43, 91, or 145, as appropriate.

c. A list of all M/M/S-specific MMEL items that contain the statement “as required by 14 CFR,” based on the items installed on the operator’s aircraft for which the operator desires MEL relief. The operator’s procedures document must:

(1) List the specific 14 CFR part and section (e.g., 14 CFR Part 91, § 91.209) and carry the applicable 14 CFR section on board the aircraft; or

(2) Specify the operational requirements or limitations to conduct the flight in accordance with the applicable 14 CFR part and section.

d. Applicable definitions, per current MMEL Policy Letter (PL)-25, MMEL/MEL Definitions.

e. A preamble, per current MMEL PL-36, 14 CFR Part 91 MEL Approval and Preamble.

6. To use the relief available in an MMEL PL with a current Global Change (GC) designation, in an STC Relief Approval Letter (e.g., Design Change Approval Letter), or in a design change evaluated and approved by the responsible Flight Standards office:

a. The applicable document in subparagraph 6 above must be included as an attachment to the MMEL, and

b. The operator’s procedures document must address applicable (M) and (O) provisos and “as required by 14 CFR” procedures that are contained in the document, as described in subparagraphs 5b and 5c above.

7. A means of recording discrepancies and corrective actions must be within the aircraft and available to the PIC when operating under the provisions of § 91.213(a).

8. When a mandatory revision to the M/M/S-specific MMEL is published by the Flight Operations Evaluation Board (FOEB), within 90 calendar days of the date of the MMEL revision, the operator must obtain a copy of the revision, carry the latest MMEL revision on board the aircraft, and incorporate applicable changes in its procedures document. The operator’s procedures document must address applicable (M) and (O) procedures and applicable “as required by 14 CFR” procedures.

9. Equipment installed on the aircraft authorized in Table 1 above (other than nonessential equipment and furnishings (NEF), such as galley equipment and passenger entertainment devices) that are not listed in the MMEL, or a document used for relief as specified in subparagraph 6 above, must be operational for flight.

10. This LOA is issued to, and valid only for, the operator named in subparagraph 1 above and the aircraft listed in Table 1 above. It is without an expiration date and will remain valid unless:

a. The operator fails to comply with the requirements of this LOA when operating under the provisions of § 91.213(a);

b. It is voluntarily surrendered by the operator for cancellation;

c. The operator ceases to be the operator of the aircraft listed in the applicable authorization;

d. It is canceled, rescinded, or revoked by the FAA;

e. The aircraft listed on the authorization change(s) registration number(s); or

f. The aircraft listed on the authorization is issued an experimental Special Airworthiness Certificate for research and development (R&D) or changes projects associated with an experimental Special Airworthiness Certificate for the purpose of R&D.

11. Responsible Person. The Responsible Person for this authorization is listed in Table 1 of LOA A001, Issuance and Applicability (revision 02c or later).

### N 8900.748 Appendix E

Appendix E. Sample LOA D195, Minimum Equipment List: 14 CFR Part 91

1. This Letter of Authorization (LOA) is issued under the provisions of 14 CFR Part 91, § 91.213(a)(2) and authorizes the operator, [Operator Name], to operate the aircraft listed below in Table 1, Authorized Aircraft, using an operator-developed minimum equipment list (MEL). The operator-developed MEL must be based on the aircraft make, model, and series (M/M/S)-specific Master Minimum Equipment List (MMEL).

2. Operations to which § 91.213(a) applies must be conducted in accordance with the operator-developed MEL and this LOA; otherwise, relief under the provisions of § 91.213(a) is not available to the operator.

3. The approved operator-developed MEL and this LOA together constitute a Supplemental Type Certificate (STC) for the aircraft and must be available to the pilot in command (PIC) when operating under the provisions of § 91.213(a).

4. Authorized Aircraft. The operator named in subparagraph 1 above is authorized to use an operator-developed MEL for the aircraft listed in Table 1 below, provided the conditions and limitations of this LOA are met:

Table 1 – Authorized Aircraft

| Aircraft Serial Number | Aircraft Registration Number | Aircraft M/M/S |
|---|---|---|
| | | |

5. The operator-developed MEL must never be less restrictive than the M/M/S-specific MMEL and must contain the following:

a. The operator’s name, aircraft serial and registration numbers (or “Fleet”), aircraft M/M/S, and the MMEL revision number on which the MEL is based.

b. A table of contents.

c. A log of revisions.

d. Applicable definitions, per current MMEL Policy Letter (PL)-25, MMEL/MEL Definitions.

e. A preamble, per current MMEL PL-36, 14 CFR Part 91 MEL Approval and Preamble.

f. Control page(s) or List of Effective Page(s) (LEP).

g. Air Transport Association of America (ATA) or Joint Aircraft System/Component (JASC) coded system sections.

h. Maintenance (M) and Operations (O) procedures that correspond with the (M) and (O) provisos listed in the M/M/S-specific MMEL, based on the items installed on the operator’s aircraft for which the operator desires MEL relief.

(1) The operator may use (M) and (O) procedures as published by the manufacturer, or use operator-developed (M) and (O) procedures that have been developed using the guidance provided in the approved Aircraft Flight Manual (AFM), Aircraft Maintenance Manual (AMM), manufacturer’s recommendations, engineering specifications, or other appropriate sources.

(2) The (M) and (O) procedures must meet the intent of the (M) and (O) provisos in the MMEL and must never be less restrictive than the MMEL.

(3) Such (M) or (O) procedures must be accomplished in accordance with the provisions and requirements of 14 CFR Part 43, 91, or 145, as appropriate.

i. The operator-developed MEL must address all items listed in the M/M/S-specific MMEL that contain the statement “as required by 14 CFR,” based on the items installed on the operator’s aircraft for which the operator desires MEL relief. The MEL will:

(1) List the specific 14 CFR part and section (e.g., 14 CFR Part 91, § 91.209) and carry the applicable 14 CFR section on board the aircraft; or

(2) Specify the operational requirements or limitations to conduct the flight in accordance with the applicable 14 CFR part and section.

j. The operator-developed MEL must adequately and safely address all applicable provisos and notes contained in the MMEL “Remarks or Exceptions” column.

6. The operator-developed MEL may include the relief available in an MMEL PL with a current Global Change (GC) designation, in an STC Relief Approval Letter (e.g., Design Change Approval Letter), or in a design change evaluated and approved by the responsible Flight Standards office. These relief documents are considered an approved addendum to the MMEL, and therefore, the requirements of subparagraph 5 above also apply to these documents.

7. A means of recording discrepancies and corrective actions must be within the aircraft and available to the PIC when operating under the provisions of § 91.213(a).

8. When a mandatory revision to the M/M/S-specific MMEL is published by the Flight Operations Evaluation Board (FOEB), within 90 calendar days of the date of the MMEL revision, the operator must revise the operator-developed MEL and submit the revision to the responsible Flight Standards office. The revised operator-developed MEL is not valid until approved by the responsible Flight Standards office. If the revised content of the MMEL is not applicable, the operator must document the inapplicability of the mandatory MMEL revision by revising the MEL control page(s) or LEP to indicate the MEL is in compliance with the mandatory MMEL revision. The operator will retain the previous, FAA-signed MEL control page(s) or LEP within the MEL.

9. Except for MEL revisions solely for the purpose of documenting the inapplicability of a mandatory MMEL revision, or to incorporate MMEL PL-25 or MMEL PL-36 revisions, the operator must submit a copy of an MEL revision to the responsible Flight Standards office for approval. Reissuance of this LOA is not required when a mandatory MMEL revision is not applicable to the operator-developed MEL.

10. Equipment installed on the aircraft authorized in Table 1 above (other than nonessential equipment and furnishings (NEF), such as galley equipment and passenger entertainment devices) that are not listed in the operator-developed MEL, or a relief document as specified in subparagraph 6 above, must be operational for flight.

11. This LOA is issued to, and valid only for, the operator named in subparagraph 1 above and the aircraft listed in Table 1 above. It is without an expiration date and will remain valid unless:

a. The operator fails to comply with the requirements of this LOA when operating under the provisions of § 91.213(a);

b. It is voluntarily surrendered by the operator for cancellation;

c. The operator ceases to be the operator of the aircraft listed in the applicable authorization;

d. It is canceled, rescinded, or revoked by the FAA;

e. The aircraft listed on the authorization change(s) registration number(s); or

f. The aircraft listed on the authorization is issued an experimental Special Airworthiness Certificate for research and development (R&D) or changes projects associated with an experimental Special Airworthiness Certificate for the purpose of R&D.

12. Responsible Person. The Responsible Person for this authorization is listed in Table 1 of LOA A001, Issuance and Applicability (revision 02c or later).

---

## Part 2 — AC 91-67, Minimum Equipment Requirements for General Aviation Operations Under FAR Part 91 (6/28/91)

Transcribed from page images of the FAA-hosted scan. Bold/italic run-in headings of the original are rendered in italics. Original page numbers (i–v, 1–17) are given in brackets.

### [p. i] Cover page

Subject: MINIMUM EQUIPMENT REQUIREMENTS FOR GENERAL AVIATION OPERATIONS UNDER FAR PART 91 — Date: 6/28/91 — AC No: 91-67 — Initiated by: AFS-820

1. PURPOSE. This advisory circular (AC) describes acceptable methods for the operation of aircraft under Federal Aviation Regulations (FAR) Part 91 with certain inoperative instruments and equipment which are not essential for safe flight.

*a. These acceptable methods of operation are:*

(1) Operation of aircraft with a Minimum Equipment List (MEL), as authorized by FAR § 91.213(a).

(2) Operation of aircraft without an MEL under FAR § 91.213(d).

*b. This AC also explains the process* for obtaining Federal Aviation Administration (FAA) approval of an MEL.

2. RELATED FAR SECTIONS. The following FAR provide additional information on operations with or without a FAR Part 91 MEL:

*a. FAR § 43.9:* Content, form, and disposition of maintenance, preventive maintenance, rebuilding, and alteration records (except inspections performed in accordance with FAR Parts 91, 123, and 125 and FAR §§ 135.411(a)(1) and 135.419).

*b. FAR § 43.11:* Content, form, and disposition of the records for inspections conducted under FAR Parts 91 and 125 and FAR §§ 135.411(a)(1) and 135.419.

*c. FAR § 91.205:* Powered civil aircraft with standard category U.S. airworthiness certificates: Instrument and equipment requirements.

*d. FAR § 91.405:* Maintenance required.

3. FORMS AND REPORTS. The FAA Flight Standards District Office (FSDO) contacted by an MEL applicant provides the applicant a Master Minimum Equipment List (MMEL) for the applicant's particular aircraft.

4. RELATED READING MATERIAL. Users of this AC will find detailed background and indepth information in the Federal Register, Vol. 53, No. 239, December 13, 1988. The public may obtain copies of this issue of the Federal Register from the FAA, Office of Public Affairs, Public Inquiry Center, APA-230, 800 Independence Ave., SW., Washington, DC 20591.

### [p. ii] 5. Background

5. BACKGROUND. Except as provided in FAR § 91.213, all instruments and equipment installed on an aircraft must be operative in order for the operator to operate it. However, the FAA recognized that safe flight can be conducted under the MEL concept and under specific conditions with inoperative instruments and equipment.

*a. Regulatory History.* Until the most recent change to FAR § 91.213, the MEL concept applied only to air carrier and commercial operations and general aviation operators of multiengine aircraft for which FAA had developed an MMEL. Operators of aircraft for which FAA had not developed an MMEL had to comply with FAR § 91.405. This section required that all aircraft discrepancies occurring between required inspections had to be repaired in accordance with FAR Part 43 before the aircraft could be operated. This meant that all the aircraft's instruments and equipment, regardless of whether they were essential or not to the flight operation conducted, had to be operative. This requirement often placed a burden on operators.

*b. Amendments to FAR Part 91.* Over the past decade, the FAA initiated several rulemaking projects to alleviate the regulatory burden of FAR § 91.405. Before the issuance of a final rule change, FAA encouraged public and industry participation, accepted and reviewed public comments, and conducted public hearings which were attended by other Government agencies and the industry.

(1) The FAA briefly suspended FAR § 91.213 and allowed issuance of MEL's by exemption. During this period, the FAA gained valuable information on the usefulness and safety aspects of using MEL's in general aviation.

(2) Further, general aviation operators have a history of safe operations using FAR § 91.205 as the sole reference for determining the instrument and equipment requirements for a particular flight.

(3) However, operators indicated the need for relief from FAR § 91.405, and the FAA agreed that the FAR should reflect current operational practices. Consequently, the FAA amended FAR Parts 43 and 91 in December 1988.

*c. New Regulatory Requirements.* The amendment to FAR Parts 43 and 91 provides a regulatory basis for the operation of aircraft with inoperative instruments and equipment. Operators conduct these operations within a framework of a controlled program of maintenance inspections, repairs, and parts replacement. However, operators must exercise good judgement and have, at each required inspection, any inoperative instrument or equipment repaired or inspected or the maintenance deferred, as appropriate.

### [pp. ii–v] 6. Definitions

6. DEFINITIONS.

*a. Aircraft Evaluation Group (AEG).* The AEG is the FAA office responsible for the development and publication of an approved MMEL for those aircraft within its area of responsibility.

*b. Aircraft Flight Manual (AFM).* The AFM is the source document for operational limitations and performance for an aircraft. The term AFM can apply to either an airplane flight manual or a rotorcraft flight manual. FAA requires an AFM for type certification. The responsible FAA Aircraft Certification Office (ACO) approves an AFM.

*c. Aircraft Maintenance Manual (AMM).* The AMM is the source document for maintenance procedures for an aircraft. The term AMM can apply to either an airplane maintenance manual or a rotorcraft maintenance manual. FAA requires the AMM for type certification.

*d. Airworthiness Directive (AD).* An AD is a mandatory airworthiness requirement for a particular make and model aircraft or installed equipment. An AD is supplementary to the aircraft original airworthiness approval.

*e. Air Transportation Association (ATA) Numbering System.* The standard ATA numbering system refers to systems on different aircraft in a standardized manner. MMEL's use the ATA numbering system.

*f. Calendar Days* include all days, with no exclusion for weekends and holidays.

*g. Deactivation* means to make a piece of equipment or an instrument unusable to the pilot/crew by preventing its operation.

*h. Deferred Maintenance* is the postponement of the repair or replacement of an item of equipment or an instrument.

*i. Equipment List* is an inventory of equipment installed by the manufacturer or operator on a particular aircraft.

*j. Flight Operations Evaluation Board (FOEB).* The FOEB is composed of FAA personnel who are operations, avionics, airworthiness, and aircraft certification specialists. The FOEB develops an MMEL for a particular aircraft type under the direction of the AEG.

*k. Inoperative* means that a system and/or component has malfunctioned to the extent that it does not accomplish its intended purpose and/or is not consistently functioning normally within its approved operating limits or tolerances.

*l. Kinds of Operations List (KOL).* The KOL specifies the kinds of operations (e.g., visual flight rules (VFR), instrument flight rules (IFR), day, or night) in which the aircraft can be operated. The KOL also indicates the installed equipment that may affect any operating limitation. Although the certification rules require this information, there is no standard format; consequently, the manufacturer may furnish it in various ways.

*m. Letter of Authorization (LOA).* The FSDO issues an LOA to the operator when the FSDO authorizes the operator to operate under the provisions of an MEL. Together, the LOA, the procedures document (paragraph v. following), and the MMEL constitute a Supplemental Type Certificate (STC). The operator must carry the STC in the aircraft during its operation.

*n. Maintenance is the inspection, overhaul, repair, preservation, or replacement of parts.* This definition excludes preventive maintenance (see paragraph u. following). After a mechanic performs maintenance, other than preventive maintenance, a properly certificated maintenance person must approve the aircraft for return to service.

*o. MMEL.* An MMEL contains a list of items of equipment and instruments that may be inoperative on a specific type of aircraft (e.g., BE-200, Beechcraft model 200). It is also the basis for the development of an individual operator's MEL.

*p. MEL.* The MEL is the specific inoperative equipment document for a particular make and model aircraft by serial and registration numbers; e.g., BE-200, N12345. A FAR Part 91 MEL consists of the MMEL for a particular type aircraft, the MMEL's preamble, the procedures document, and a LOA. The FAA considers the MEL as an STC. As such, the MEL permits operation of the aircraft under specified conditions with certain equipment inoperative.

*q. Next Required Inspection* is the one required under either an FAA-approved inspection program, a 100-hour inspection, or an annual inspection, as appropriate.

*r. Operations (O) and Maintenance (M) procedures* in the MMEL refer to the specific maintenance procedures the operator uses to disable or render items of equipment inoperative and to specific operating conditions and limitations, as appropriate.

(1) An O symbol in column 4 of the MMEL indicates that a specific operations procedure must be accomplished before or during operation with the listed item of equipment inoperative. Normally, the flightcrew accomplishes these procedures; however, other personnel, such as maintenance personnel, may be qualified and authorized to perform the procedure.

(2) An M symbol in column 4 of the MMEL indicates that a specific maintenance procedure must be accomplished before beginning operation with the listed item of equipment inoperative. Normally, maintenance personnel accomplish these procedures; however, other personnel, such as the flightcrew, may be qualified and authorized to perform functions. Qualified maintenance personnel must perform procedures requiring specialized knowledge, skills, or the use of tools or test equipment.

*s. Operator refers to an individual or company (corporation, entity, etc.).* As used in this AC, operator applies to those who are applicants for, or holders of, authority to conduct operations under the provisions of a FAR Part 91 MEL.

*t. Placard is a decal or label with letters at least 1/8-inch high.* The operator or mechanic must place the placard on or near inoperative equipment or instruments so that it is visible to the pilot or flightcrew and alerts them to the inoperative equipment.

*u. Preventive Maintenance.* The term preventive maintenance refers to simple or minor preservation operations and/or the replacement of small standard parts not involving complex assembly. FAR Part 43, Appendix A(c), contains a list of preventive maintenance items. Qualified mechanics or certificated pilots may accomplish preventive maintenance and approve the aircraft for return to service.

*v. Procedures Document as referred to in this AC* pertains to a separate document containing the O and M procedures developed by the operator and any other operating information applicable to operation with an MEL, such as the "as required by the FAR" items that list the FAR by part and section or stipulate the operating conditions.

*w. Proposed Master Minimum Equipment List (PMMEL).* The PMMEL is the working document used as the basis for development of the MMEL. Normally, the manufacturer proposes it during the certification process. However, an operator of a unique type aircraft, for which an MMEL does not exist, may submit a PMMEL for FAA approval.

*x. Return to Service.* Return to service has two applications. An appropriately certificated person approves an aircraft for return to service after an inspection or after maintenance. A certificated pilot, in fact, returns the aircraft to service after the pilot conducts an appropriate preflight and accepts the aircraft for an intended flight.

*y. Small Aircraft* means aircraft with a maximum certificated takeoff weight of 12,500 pounds or less.

*z. STC.* An STC is a major change in type design not great enough to require a new application for a type certificate under FAR § 21.19. An example would be installation of a powerplant different from what was included in the original type certificate.

aa. *Type Certificate Data Sheets (TCDS)* and Specifications are documents issued by the FAA which describes the aircraft's airworthiness requirements relating to a specific type, make, and model of aircraft. These documents are available at a FSDO.

[Paragraph 7, COMMENTS INVITED, and the signature block (David R. Harrington, Acting Director, Flight Standards Service) on p. v are not transcribed.]

### [pp. 1–4] Chapter 1. General (paragraphs 1–8)

CHAPTER 1. GENERAL

1. APPLICABILITY. This AC provides guidance for the operation of the following aircraft under FAR Part 91:

*a. Aircraft for which no MMEL has been developed by the FOEB:*

(1) Rotorcraft.

(2) Nonturbine-powered airplanes.

(3) Gliders.

(4) Lighter-than-air aircraft.

*b. Aircraft for which an MMEL has been developed* but for which the FSDO has not [underlined in original] authorized operation with an MEL.

(1) Small rotorcraft.

(2) Nonturbine-powered small single and multiengine airplanes.

*c. All other aircraft* which have an MEL or for which an operator seeks MEL authorization under FAR § 91.213.

*d. An operator may operate* an aircraft for which FAA has issued an original Experimental airworthiness certificate in accordance with FAR § 91.213 only when authorized in that certificate's operating limitations.

*e. This AC does not apply to* operators holding certificates issued under FAR Parts 121, 125, 129, and 135.

*f. Holders of letters of full deviation authority* from FAR Part 125 and operating under FAR Part 91, Subpart F, may apply for authorization to operate with a FAR Part 91 MEL.

2. MEL VS. FAR § 91.213(d). Although FAA amended FAR Part 91 to provide relief to operators under the MEL concept, some operators may find it less burdensome or less complicated to operate under the provisions of FAR § 91.213(d). The applicant should discuss the requirements of each method with FSDO inspectors to decide which method of compliance better suits the particular operation. Appendix 3 contains a list of commonly asked questions which may assist in the decision.

*a. An MEL is a precise listing of instruments, equipment, and procedures* that allows an aircraft to be operated under specific conditions with inoperative equipment. The MMEL, as part of the MEL, by nature does not cover equipment installed or modified under other STC's. Any STC or other major modification may make the MMEL invalid for a particular modified aircraft.

*b. The FAR require* that all equipment installed on an aircraft in compliance with the airworthiness standards and operating rules be operative. The FAA-approved MMEL includes those items of equipment and other items which the FAA finds may be inoperative and yet maintain an acceptable level of safety. Obviously, the MMEL does not contain required items such as wings, flaps, rudders, etc. When a FAR Part 91 operator uses an MMEL as an MEL, all instruments and equipment not covered in the MMEL must be operative at all times regardless of the operation conducted, unless:

(1) They are newly installed and are not instruments or equipment specifically required by the airworthiness rule under which the aircraft is type certificated, required by AD, or required for specific operations under FAR § 91.213(b)(1)-(3), such as Traffic Alert and Collision Avoidance System (TCAS), an extra piece of navigational equipment, a windshear detection device, a ground proximity warning system, a radar altimeter, passenger convenience items, etc.;

(2) The operator has developed procedures for disabling or rendering them inoperative; and

(3) The operator has contacted the FSDO having oversight within 10 calendar days following an installation and requested that the equipment be added to the MMEL.

(i) The operator must furnish the following information:

(A) A copy of the STC or FAA Form 337, Major Repair and Alteration, that approved each equipment installation and the associated limitations listed in the AFM supplement or on the 337. The FOEB needs this information to account for installation differences as well as for maintaining MMEL relief that is consistent with the limitations.

(B) A system description that details sufficiently the interface of the equipment with the crew; i.e., location, controls, operations, how it is used, etc.

(C) A statement that describes the transfer of function when the equipment is inoperative; i.e., not required for the flight, as per crew procedures, because of alternate systems, etc.

(ii) If the FAA determines that the equipment has been previously considered by the FOEB for inclusion in the MMEL and denied, or if the FOEB convenes and denies inclusion, the FAA will not grant relief. The equipment must be operational before aircraft can take off.

(iii) If the FOEB determines that the equipment should be added to the MMEL, the operator will receive the updated MMEL and must prepare O and M procedures for that piece of equipment.

*c. If FAA has not authorized operating with an MEL* for an operator's specific aircraft, the operator may apply for an MEL (Chapter 3, paragraph 20). However, the operator can always elect to operate without an MEL under the provisions of FAR § 91.213(d).

(1) FAR § 91.213(d) requires only those instruments listed in FAR § 91.213(d)(2) to be operative.

(2) The operator can operate the aircraft with those instruments and equipment not listed in FAR § 91.213(d)(2) inoperative.

3. RELATIONSHIP BETWEEN THE PMMEL, THE MMEL, AND THE MEL. When an aircraft is first manufactured, the FOEB determines the minimum operative instruments and equipment required for safe flight in that aircraft type in each authorized operating environment. During the type certification process, the manufacturer submits a PMMEL to the FOEB. Based on its determinations, the FOEB reviews the PMMEL and develops an MMEL from it. Once the FOEB approves the MMEL, a copy is available to each FSDO via an automated system that allows the FSDO to download the MMEL onto a diskette or hard copy. The FSDO provides MMEL's to applicants to use, along with the procedures document, preamble, and LOA, as an MEL.

*a. As technology changes and new equipment* becomes available, the FOEB will reconvene to develop new MMEL's or to revise and update existing ones.

*b. When an FOEB makes a change to an MMEL,* all operators using that MMEL as their MEL will receive a postcard advising them of the revised MMEL. The FSDO provides operators copies of the revised MMEL. The operator then makes the necessary changes to the procedures document through the normal revision process (Chapter 3, paragraph 22).

4. SINGLE- AND MULTIENGINE MEL'S. The FAA has developed MMEL's for most of the FAA type certificated aircraft in general service today. All multiengine airplanes have an MMEL that is specific to the type design; e.g., Beech Baron, BE-58. The FAA has developed a generic, single-engine MMEL to provide to operators of single-engine aircraft.

5. AIRCRAFT FOR WHICH NO MMEL HAS BEEN DEVELOPED.

*a. If an FOEB has not developed* an MMEL for a certain type of rotorcraft, nonturbine-powered airplane, glider, or lighter-than-air aircraft, that aircraft may be operated with inoperative equipment under the provisions of FAR § 91.213(d).

*b. In those cases where an operator* has an older or rare design aircraft that has no MMEL, the operator may submit a PMMEL to the appropriate FOEB for evaluation. Once the AEG approves the MMEL, the operator could use it as the MEL along with the other required documents.

6. MEL RESTRICTIONS. Operators of small rotorcraft, nonturbine-powered small single- and multiengine airplanes, and other aircraft for which a MMEL has been developed, may elect to operate with a MEL or under the provisions of FAR § 91.213(d). However, the latter option does not apply if the aircraft has an MEL approved under FAR Parts 121, 125, 129, or 135. For example, an owner has leased an aircraft to an air carrier operator, and the air carrier operator has applied for and received an approved MEL for FAR Part 135 operations. Compliance with such an MEL is mandatory, even during FAR Part 91 operations. If the operator wants to operate under FAR § 91.213(d), the operator would have to surrender the MEL authorization.

7. REMOVAL OR DEACTIVATION. When an operator elects to operate without an MEL, any inoperative instrument or equipment must either be removed (FAR § 91.213(d)(3)(i)) or deactivated (FAR § 91.213(d)(3)(ii)), then placarded.

*a. Removal of any item of equipment* that affects the airworthiness of an aircraft requires following an approved procedure. A properly certificated maintenance person must record the removal in accordance with FAR § 43.9. A person authorized by FAR § 43.7 must make the appropriate adjustments to the aircraft's weight and balance information and the equipment list, fill out and submit FAA Form 337, and approve the aircraft for return to service.

*b. The operator must evaluate any proposed deactivation* to assure there is no adverse effect that could render another system less than fully capable of its intended function.

(1) A certificated pilot can accomplish deactivation involving routine pilot tasks, such as turning off a system. However, for a pilot to deactivate an item or system, that task must come under the definition of preventive maintenance in FAR Part 43, Subpart A.

(2) If the deactivation procedures do not fall under preventive maintenance, a properly certificated maintenance person must accomplish the deactivation. The maintenance person must record the deactivation in accordance with FAR § 43.9 [the scan prints the "4" faintly; read as 43.9] (figure 1, Sample Maintenance Record Entries.).

*c. Placarding can be as simple as writing the word "inoperative"* on a piece of masking tape and attaching it to the inoperative equipment or to its cockpit control. Placarding is essential since it reminds the pilot that the equipment is inoperative. It also ensures that future flightcrews and maintenance personnel are aware of the discrepancy.

8. INOPERATIVE EQUIPMENT AND REQUIRED INSPECTIONS. An operator may defer maintenance on inoperative equipment that has been deactivated or removed and placarded inoperative.

*a. When the aircraft is due for inspection in accordance with the FAR,* the operator should have all inoperative items repaired or replaced.

*b. If an owner does not want specific inoperative equipment repaired,* then the maintenance person must check each item to see if it conforms to the requirements of FAR § 91.213(d). The operator and maintenance personnel should also assess how permanent removal of the item could affect safe operation of the aircraft.

(1) The repair interval categories (A, B, C, D, etc.) in the MMEL do not apply to FAR Part 91 MEL's.

(2) The maintenance person must furnish the owner/operator with a signed and dated list of all discrepancies not repaired.

(3) The maintenance person must ensure that each item of inoperative equipment that is to remain inoperative is placarded appropriately.

[p. 5, Figure 1. Sample Maintenance Record Entries]

Placard (Minimum 1/8-inch high letters)

Landing Light Inoperative:

PREVENTIVE MAINTENANCE ENTRY:

(DATE) Total time_______hours. Landing light bulb removed in accordance with (manufacturer) maintenance manual, Chapter_____, page____. Landing light switch placarded inoperative.

Pilot's Signature — Certificate Number

Placard (Minimum 1/8-inch high letters)

Aircraft Heater Inoperative:

MAINTENANCE ENTRY (FAR §43.9):

(DATE) Total time_______hours. Aircraft heater and control switch deactivated by capping heater fuel lines in accordance with (manufacturer) maintenance manual, Chapter_______, page____. Heater control switch placarded inoperative.

Mechanic's Signature — Certificate Number

9.-12. RESERVED.

### [pp. 7–9] Chapter 2. Conducting Operations Without an MEL (paragraphs 13–14, Figure 2)

CHAPTER 2. CONDUCTING OPERATIONS WITHOUT AN MEL

13. APPLYING FAR § 91.213(d). This chapter provides guidance for operators who elect to conduct flight operations under the provisions of FAR § 91.213(d). Operating under FAR § 91.213(d) requires no application to or approval from FAA. An operator, after operating under FAR § 91.213(d), may elect at any time to apply for authorization to operate under an MEL (Chapter 3).

14. THE DECISION SEQUENCE. Figure 2 is a flow chart depicting the typical sequence of events a pilot or operator, operating under FAR § 91.213(d), should follow when the pilot or operator discovers inoperative equipment. For example, during a preflight inspection for a VFR-day, cross-country flight, the pilot discovers that the number 2 automatic direction finder (ADF) head is inoperative.

*a. The pilot checks the aircraft's equipment list or KOL* to see if the number 2 ADF is a required item (FAR § 91.213(d)(2)(ii)). If the number 2 ADF is required in the equipment list or KOL, the aircraft is not airworthy. The operator must have the number 2 ADF replaced or repaired before operating the aircraft. In this example, the number 2 ADF is not a required item on the equipment list.

*b. Next, the pilot checks the airworthiness regulation* under which the aircraft was certificated to determine if the number 2 ADF is part of the VFR-day type certificate (FAR § 91.213(d)(2)(i)). (These requirements are summarized in a TCDS, copies of which are available at FSDO's or from qualified maintenance personnel.) If the number 2 ADF is required as part of the VFR-day type certification, the aircraft is not airworthy. The operator must have the number 2 ADF replaced or repaired before operating the aircraft. In this example, the number 2 ADF is not required by type certification.

*c. Next, the pilot checks to see if an AD requires the number 2 ADF.* The pilot can accomplish this by checking the aircraft's maintenance logs to see if the number 2 ADF was installed as a result of an AD. However, it may be necessary for the pilot to consult a qualified maintenance person to determine AD compliance. If an AD requires the number 2 ADF to be operative, the aircraft is not airworthy. The operator must have the number 2 ADF replaced or repaired before operating the aircraft. In this example, there is no AD requiring the number 2 ADF to be operative.

*d. Next, the pilot checks to see if the number 2 ADF is required by FAR §§ 91.215, 91.205, or 91.207.* The pilot can accomplish this by checking those sections of the FAR or by consulting with a maintenance technician or FSDO personnel. If any of those sections of the FAR require a number 2 ADF, then the aircraft would not be airworthy with the number 2 ADF inoperative. The operator must have the number 2 ADF replaced or repaired before operating the aircraft. In this example, those sections of the FAR do not require the number 2 ADF to be operative.

*e. At this point the inoperative number 2 ADF* must either be removed from the aircraft (FAR § 91.213(d)(3)(i)) or deactivated (FAR § 91.213(d)(3)(ii)). The person removing or deactivating the number 2 ADF must placard it inoperative in the appropriate location. (A pilot should consult maintenance personnel before deactivating or having maintenance personnel remove any item of equipment.)

*f. Finally, the pilot should decide whether* the inoperative number 2 ADF creates a hazard for the anticipated conditions of the flight, e.g., VFR-day.

15.-18. RESERVED.

[p. 8, Figure 2. Pilot Decision Sequence When Operating Without An MEL — box text, top to bottom]

During the preflight inspection, the pilot recognizes inoperative instruments or equipment.

Is the equipment required by the aircraft's equipment list or the kinds of equipment list? (FAR § 91.213(d)(2)(ii).) → If YES, the aircraft is unairworthy and maintenance is required.

If NO, is the equipment required by the VFR-day type certificate requirements prescribed in the airworthiness certification regulations? (FAR § 91.213(d)(2)(ii).) See appendix 1 of this AC. → If YES, the aircraft is unairworthy and maintenance is required.

If NO, is the equipment required by AD? (FAR § 91.213(d)(2)(iv).) → If YES, the aircraft is unairworthy and maintenance is required.

If NO, is the equipment required by FAR §§ 91.205, 91.207, etc.? (FAR § 91.213(d)(2)(iii).) → If YES, the aircraft is unairworthy and maintenance is required.

If NO, the inoperative equipment must be removed from the aircraft (FAR § 91.213(d)(3)(i)) or deactivated (FAR § 91.213(d)(3)(ii)) and placarded as inoperative.

At this point the pilot shall make a final determination to confirm that the inoperative instrument/equipment does not constitute a hazard under the anticipated operational conditions before release for departure.

### [pp. 11–17] Chapter 3. Operating Aircraft With an MEL (paragraphs 19–23, Figure 3)

CHAPTER 3. OPERATING AIRCRAFT WITH AN MEL

19. APPLICABILITY. This chapter provides guidance for operators who want to conduct flight operations under the provisions of an MEL.

20. APPLYING FOR MEL APPROVAL. FAA has only one procedure for the issuance of FAR Part 91 MEL's, and it is the procedure the FSDO will follow for FAR Part 91 MEL authorizations. The operator who wishes to conduct operations with an MEL must contact the FSDO which has jurisdiction over the geographic area where the aircraft is based and make an appointment.

*a. FAR Part 91 operators who received MEL authorization* under the approval system in place before July 5, 1990, have letters of authorization that will expire. Those operators may continue to operate as usual; however, at least 30 days before the letter is due to expire, the operator should contact the issuing FSDO so that the FSDO can issue a new LOA.

*b. For FAR Part 91 operators seeking MEL authorization* under the current approval system, the FSDO will assign a Flight Standards inspector to advise the applicant about FAR requirements pertinent to using an MEL. During the initial appointment, the applicant will likely be dealing with a team of inspectors from the operations, airworthiness, and avionics units.

*c. The inspector will provide the applicant* with a copy of the appropriate MMEL, a copy of this AC, and a copy of the preamble to the MMEL. If the operator has installed items of equipment that are not on the MMEL, the operator must request that the MMEL be amended to include those items of equipment. This request is made to the FSDO.

*d. The operator and the team of inspectors* discuss the requirements for the procedures document. When FSDO personnel believes that the operator understands the requirements for operating with an MEL, the FSDO issues the operator the LOA (appendix 4).

(1) The LOA contains the legal name of the operator and the address of the operator's principal base of operations.

(2) Both the FAA inspector and the operator (or the operator's bona fide representative) sign the LOA.

*e. If, after meeting with FSDO personnel and discussing MEL operational considerations,* an inspector believes that the applicant does not have a good understanding of the requirements, the FSDO will not issue the LOA. If the LOA is still desired, the applicant should obtain the necessary understanding of the requirements from appropriate sources. After obtaining and understanding the requirements, the applicant can again request the LOA from the FSDO. The applicant could also elect to operate under FAR § 91.213(d).

*f. Once the FSDO issues the LOA,* the applicant is then responsible for developing a document that contains O and M procedures for disabling or rendering inoperative items of equipment in accordance with FAR Parts 43, 91, or 145 (if a repair station accomplishes the activity), as appropriate. No further FAA approval is necessary, and the operator can begin flight operations. The MMEL, preamble, LOA, and the procedures document are now considered an MEL.

(1) The operator should develop the O and M procedures using guidance contained in the manufacturer's aircraft flight and/or maintenance manuals, the manufacturer's recommendations, engineering specifications, and other appropriate sources. The operator may consult FSDO airworthiness inspectors for advice or clarification, but the operator is responsible for preparing the document.

(2) The operator must consider the following when preparing the procedures document:

(i) The operator's procedures document may be more restrictive than the MMEL either by the applicant's choice or because of AD's or operating rules. The operator's procedures document may not be less restrictive than the MMEL. [last sentence underlined in original]

(ii) The title page of the procedures document must contain the following statement:

This MEL is applicable to FAR Part 91 operations only and may not be used for operations conducted under FAR Parts 121, 125, 129, or 135.

(iii) The operator must use the ATA numbering system for equipment and instruments, as is used in all MMEL's (appendix 1). The operator must use the ATA numbering system in sequence when describing O and M procedures, including the numbers for equipment installed in the aircraft. When equipment is not installed in a specific aircraft, the applicant need not develop O and M procedures for those items of equipment.

(iv) Operators must ensure that the procedures document lists the items of equipment that are actually installed on the specific aircraft. This provides guidance to a pilot as to which items of equipment may be inoperative for a particular operation.

(v) Equipment specifically required by the airworthiness rule under which the aircraft is type certificated, equipment required by AD, and equipment required for specific operations under FAR § 91.213(b)(1), (2) and (3) must be operative. It is important to note that all items related to the airworthiness of the aircraft that are not included on the MMEL must be operative. [last sentence underlined in original]

(vi) The A, B, C, and D codes, listed in column 1 of the MMEL, apply only to operations conducted under FAR Parts 121, 125, 129, and 135.

(vii) Where the MMEL states "as required by FAR," the procedures document should list the particular FAR by part and section, or describe the actual FAR requirement applicable to the operator's particular operation. For example, where the FAR requires a clock for IFR flight, the operator's procedures document should say, "May be inoperative for VFR."

(viii) The procedures document must specify suitable limitations in the form of placards, maintenance procedures, crew operating procedures, and other restrictions to ensure an acceptable level of safety.

(ix) The procedures document must specify those conditions under which an item may be inoperative. The remarks must also identify required maintenance or operational tasks. The symbol "O" or "M", placed in column 4 of the MMEL (appendix 1), indicates that an O or M procedure is applicable to that item. Indicating the O and M procedures in the procedures document provides flightcrews and ground support personnel with a single procedural reference document. [the words "single procedural reference document" underlined in original]

(x) If the O and M procedures are already stated in the AFM, the maintenance manual, or other available FAA-approved source, the operator needs to show only the reference; e.g., O: AFM, pp. 3-8 through 3-10, para. 3-47. If the operator uses this reference format in the procedures document, the referenced source must be readily available to the ground support personnel, and a copy of the references source must be carried in the aircraft and be readily available to the flightcrew.

(xi) If the O and M procedures are not in the AFM, the maintenance manual, or other available FAA-approved source, or if the operator wishes to use a different procedure, then the operator must list the procedure in the procedures document.

(xii) The procedures document may not conflict with the AFM limitations, emergency procedures, AD's, or the AMM.

(3) An operator may begin operations before completion of the procedures document. If the operator has not yet developed a procedure for an item, that item must be operative. When an instrument or item of equipment becomes inoperative, the operator must follow the procedure indicated in the procedures document or the operator could be in noncompliance with the FAR.

21. MEL AUTHORIZATION. The MEL applies only to a particular aircraft make, model, serial number, and registration number. Also, it applies only to the operator who received the authorization.

*a. When more than one operator has operational control of a specific aircraft,* all operators must meet with inspectors from the issuing FSDO to discuss MEL operational considerations, as described in paragraph 20. The FSDO may find it appropriate to list all operators on the LOA. Each operator must sign the "Statement of Operator" on the LOA.

*b. The FSDO may issue operators who use several aircraft* of the same type a single LOA that lists each aircraft by serial and registration numbers. The FSDO will issue separate letters for different types of aircraft.

(1) When operators add or delete aircraft of the same type from their fleet, they must notify the FSDO having oversight within 10 calendar days following the change. The FSDO will reissue the LOA containing the new information. Again, both the operator and the inspector must sign the new LOA.

(2) The operator must surrender the previous letter upon reissuance of a new one. The FSDO should place the old letter in the operator's file.

*c. At any time after operating with a FAR Part 91 MEL,* an operator may elect to operate under FAR § 91.213(d). The operator must surrender the LOA to the issuing FSDO and must conform to all provisions of FAR § 91.213(d) during operations.

22. REVISIONS. The operator may have to revise the procedures document under several conditions. The AEG may authorize an FOEB to revise the MMEL, the operator may add equipment, or the FOEB may develop a type-specific MMEL for a single-engine aircraft.

*a. When the FOEB revises an MMEL,* the FAA automated, national MMEL data base notifies operators who have MEL authorizations by mail. The operator is then responsible for obtaining a copy of the revised MMEL from the FSDO that issued the authorization. Within 30 calendar days of notification, the operator must replace the superseded revision of the MMEL with the current revision and add or delete procedures to the procedures document, as applicable.

*b. Within 10 calendar days of installing new equipment* not on the MMEL, the operator may request that the MMEL be amended.

(1) If the items of newly installed equipment are not instruments or equipment specifically required by the airworthiness rule under which the aircraft is type certificated, an AD, or for specific operations under FAR § 91.213(b)(1), (2) or (3); and exceed what is listed on the MMEL; and the FSDO has determined that the equipment has not previously been denied for inclusion in an MMEL, the operator may petition the FOEB for inclusion of the newly installed equipment in the MMEL. All petitions, with appropriate supporting information, will be forwarded by the FSDO to the appropriate FOEB. Then the operator may add the equipment temporarily to the MMEL and develop appropriate O and M procedures for the equipment. The operator may then operate with the equipment inoperative pending a decision by the FOEB on the operator's request for an MMEL revision to include the equipment.

(2) If the FOEB has previously denied the inclusion of the equipment, or if the equipment is safety related, or if the equipment was previously installed or is "factory original," the operator may still petition the FOEB through the FSDO for inclusion of the equipment in the MMEL. However, the operator may not gain relief for the equipment by adding the equipment to the MMEL temporarily and adding procedures to the procedures document pending the FOEB's decision. The equipment must be operative before operating the aircraft.

*c. Although FAA has developed a generic MMEL* for operators of single-engine aircraft, an FOEB may decide that a complex, turbine-powered single-engine aircraft requires a type-specific MMEL. For example, an FOEB has developed a type-specific MMEL for the Cessna 208, Caravan.

(1) When an FOEB develops a specific MMEL for a single-engine aircraft, the FAA will notify all holders of MEL's for that aircraft under the generic MMEL that the specific MMEL is available.

(2) Within 30 calendar days of notification, the operator must obtain the MMEL from the FSDO and begin the process for a new LOA. Only by issuing a new LOA will the FSDO be assured that the operator has and is using the type-specific MMEL.

(3) Once the FSDO issues the new LOA, the operator must develop, within an additional 30 calendar days, a new procedures document that conforms to the requirements of the type-specific MMEL. The operator will find that most of the procedures that were acceptable under the generic MMEL will transfer to the new procedures document. If equipment becomes inoperative while the operator is developing the new procedures document, the operator may still use the previous procedures, as appropriate.

23. CONDUCTING OPERATIONS WITH AN MEL. In addition to carrying the documents that comprise the MEL onboard the aircraft, the operator must have onboard any technical manuals needed to accomplish O and M procedures. Figure 3 illustrates the sequence of events involved in applying the MEL to inoperative equipment.

*a. Inoperative Items Before Flight.* During a preflight inspection for a VFR-day flight, the pilot discovers a navigation light is inoperative.

(1) The pilot checks the aircraft's MEL to determine under what, if any, flight conditions the aircraft could be operated without operator navigation lights. The MEL indicates that the aircraft may be operated during daylight hours without operable navigation lights.

(2) The pilot checks the procedures document and deactivates the navigation lights by pulling the correct circuit breaker and having it collared by an appropriately certificated person.

(3) The pilot places a placard which indicates that the lights are inoperative near the navigation light control.

(4) The pilot examines the conditions of the proposed flight and determines that the flight can be conducted safely without navigation lights.

*b. In-Flight Failures.* An MEL applies only to the takeoff of an aircraft with inoperative instruments or equipment. The pilot's operating handbook or the AFM indicate procedures to follow for instrument or equipment failure in flight. The pilot in command (PIC) should handle the in-flight failure in accordance with those procedures. As soon as possible after landing safely, the PIC must enter a notation of the inoperative equipment in the aircraft's maintenance records, logbooks, or discrepancy record. Before the next takeoff, the pilot must apply the MEL to inoperative equipment as per the procedures in paragraph a. above. An MEL allows the PIC to defer maintenance on many items under the following conditions:

(1) The aircraft is in a condition for safe flight, and

(2) For the inoperative item, the pilot has followed the specific conditions, limitations, and procedures in the procedures document.

*c. Deactivation or Removal and Placarding.* See Chapter 1, paragraph 7.

*d. Correcting MEL Inoperative Items.* The MEL permits operations with inoperative items of equipment for the minimum period of time necessary until the equipment is repaired. It is important that operators have repairs done at the earliest opportunity in order to return the aircraft to its design level of safety and reliability. In all cases, inoperative equipment must be repaired or the maintenance deferred at the aircraft's next required inspection (FAR § 91.405(c)).

(1) Operators shall establish procedures to correct those inoperative items authorized within specified time requirements.

(2) Owners of aircraft operated under FAR Part 91 may opt to use one of several types of airworthiness inspection systems, depending upon the operator's use of the aircraft. Therefore, the time between required inspections or inspection segments will vary.

(3) Items of inoperative equipment, authorized by the MEL to be inoperative, must be inspected or repaired by qualified maintenance personnel, or maintenance deferred, at the next 100-hour, annual, progressive, or unscheduled inspection. However, if FAR § 91.213 requires that an item be repaired, the item cannot be deferred.

*e. Recordkeeping Requirements.* A record of inoperative equipment must remain in the aircraft so pilots will be aware of all discrepancies.

(1) Since some operators do not carry aircraft logbooks in the aircraft, a discrepancy record or log (figure 4) is a good alternative. When an operator uses this type of discrepancy log in lieu of the aircraft's maintenance records, the operator must retain the log as a part of the aircraft's records as per FAR § 91.417(b).

(2) If the operator elects to use the aircraft maintenance record to log inoperative items, that portion of the record must be carried onboard the aircraft during all operations.

(3) Corrective actions and maintenance procedures shall be accomplished and recorded in accordance with FAR §§ 43.9, 91.405, and 91.417.

(4) Failure to record an inoperative item may result in an operation of the aircraft contrary to the FAR because subsequent pilots would not be able to determine the airworthiness of the aircraft.

*f. Aircraft Used in Multiple Operations.* FAR § 91.213(c) allows a person who has an approved MEL under FAR Parts 125, 129, or 135 to use that MEL for FAR Part 91 operations. The FAR Parts 121, 125, 129, or 135 MEL must specify requirements for authorized FAR Part 91 operators to comply with the more restrictive provisions established in the approved MEL. It is important that operators be capable of conducting operations in accordance with the MEL. This includes, but is not limited to, accomplishing required maintenance in accordance with the certificate holder's requirements.

(1) The use of a leased aircraft creates a situation where several persons may be operating the same aircraft under different regulations. For example, a Cessna 340 could be operated by an approved school under FAR Part 91, by an air carrier under FAR Parts 135, and by a rental pilot under FAR Part 91. FAA will not approve multiple MEL's, which would create pilot confusion, with discrepancy lists and sets of procedures for the same aircraft. In the example, the aircraft would operate under the FAR Part 135 MEL, including the A, B, C, and D codes, with approval from the FSDO for other users to conduct operations under other regulations.

(2) FAA will grant operators approval for multiple users of an MEL under FAR Parts 121, 125, 129, or 135 MEL, subject to the following conditions:

(i) The operator is responsible for training all persons in the MEL's use, including the logging and clearing of discrepancies and the use of the A, B, C, and D codes.

(ii) Operators shall maintain a complete, current list of all persons trained and authorized to use the MEL.

(iii) The operator is responsible for determining the aircraft's maintenance status on its return from a FAR Part 91 operation. The operator must accomplish this before the aircraft is put back into FAR Parts 121, 125, 129, or 135 service.

(iv) FAA Principal Operations Inspectors shall verify that operators have established procedures that ensure an acceptable level of safety before authorizing persons to use the MEL under FAR Part 91.

[p. 16, Figure 3. Pilot Decision Sequence When Operating With An MEL — box text]

During the preflight inspection, the pilot discovers inoperative instrument or equipment.

The pilot checks aircraft's MEL. If the inoperative equipment is not included in MEL but is required by type certificate, AD, or special conditions: — If yes, → The aircraft is not airworthy; repair before flight.

— If no, → Pilot performs or has a qualified person perform the appropriate O or M deactivation or removal procedure. → The pilot or maintenance personnel placard the inoperative equipment. → The pilot can take off after confirming that the inoperative equipment does not present hazards to the conditions of flight.

[Remainder of p. 17 onward (figure 4 discrepancy log, appendices 1–4: sample MMEL documents, sample letter of authorization, sample title page, commonly asked questions) not transcribed.]
