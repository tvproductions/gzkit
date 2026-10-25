# COMNAVAIRFORINST 4790.2E, Naval Aviation Maintenance Program (NAMP): retrieval record

- Document sought: COMNAVAIRFORINST 4790.2E, *The Naval Aviation Maintenance Program (NAMP)*, 28 October 2024 (current edition; it replaces COMNAVAIRFORINST 4790.2D Change 1, per the highlights enclosure quoted below).
- Retrieval date: 2026-10-25.
- **Result: the full text of 4790.2E was NOT retrieved. No NAMP definition requested by the R&D run (Maintenance Control, Maintenance Officer, QA, QAR, CDI, CDQAR, MAF/work order, work center, inspector independence, safe-for-flight, FCF, ADB, tool control, Maintenance Control Supervisor) was read from primary text in this run.** Do not decide names from this file for those terms.
- What WAS read from official NAVAIR-hosted primary text: (1) the COMNAVAIRFOR release message for 4790.2E and (2) the 4790.2E highlights enclosure. Verbatim passages follow, quoted to fix the edition, its date and where the full text is hosted.

## Refusals and unavailability (recorded, not worked around)

| URL | What it is | Result on 2026-10-25 |
|---|---|---|
| https://www.navair.navy.mil/Naval-Aviation-Maintenance-Program | NAVAIR NAMP landing page (download links) | HTTP 403, Cloudflare "Attention Required!" challenge page (curl and WebFetch) |
| https://www.navair.navy.mil/documents?name=&field_document_description_value=NAMP | NAVAIR document library; search indexes list an entry titled "NAMP 4790.2E 28 October 2024 (AMA 2024-07 attached)" there | HTTP 403, Cloudflare challenge (curl and WebFetch). The file URL of the full 4790.2E could therefore not be learned; filename guesses under `/sites/g/files/jejdrs536/files/document/[filename]/` returned HTTP 404. |
| https://myteam.navair.navy.mil/KM/60/business-processes/resource-management-and-adminstration-processes/NAMP | Location named in the release message for the full 4790.2E | Not attempted: a NAVAIR "myteam" (CAC) site, not public. |
| https://navalsafetycommand.navy.mil/Portals/100/Documents/1-NAMP%20CH%201-Intro.pdf and .../3-NAMP%20CH%203-Maintenance%20Concepts_Programs%20and%20Processes.pdf | Naval Safety Command copies of NAMP chapters (search snippets identify them as 4790.2C, 2017, a superseded edition) | HTTP 403 "Access Denied" (Akamai edgesuite), curl and WebFetch |
| https://www.secnav.navy.mil/doni/Directives/04000%20Logistical%20Support%20and%20Services/04-700%20General%20Maintenance%20and%20Construction%20Support/4790.2K.pdf | OPNAVINST 4790.2K (25 Apr 2025), the OPNAV NAMP policy instruction (a related document, not the COMNAVAIRFORINST) | TLS connection reset (curl: `SSL_ERROR_SYSCALL`; WebFetch: "Socket is closed"), two attempts |

Third-party copies were found only as study aids (Quizlet, Docsity, Scribd, DocHub, studyguides.com, dokumen.tips, yumpu) or as superseded editions on non-government hosts (navytribe.com 4790.2B, 2012 contents page only; fodnews.com 4790.2A Chapter 10, 2008). None was used: they are not the current edition, and the study-aid pages are not the document.

## Verbatim passage 1: the 4790.2E release message (official, primary)

- URL: https://www.navair.navy.mil/sites/g/files/jejdrs536/files/document/%5Bfilename%5D/namp%20release%20msg.pdf (HTTP 200, application/pdf, 59,252 bytes)
- Message DTG: R 061615Z NOV 24, FM COMNAVAIRPAC SAN DIEGO CA, SUBJ/ANNOUNCEMENT TO THE RELEASE OF COMNAVAIRFORINST 4790.2E NAMP//
- Text extracted with `pdftotext -layout`; line breaks of the message format kept.

> REF/A/DOC/OPNAVINST 4790.2J/-/01FEB2005//
> REF/B/DOC/COMNAVAIRFORINST 4790.2D CH-1/15FEB2022//
> REF/C/MSG/DTG 150026Z NOV 24//
> NARR/REF A CONTAINS OPNAV NAMP POLICY AND MANAGEMENT DIRECTION.
> REF B IS THE NAVAL AVIATION MAINTENANCE PROGRAM (NAMP).
> REF C IS COMNAVAIRFORINST 4790.2D NAMP RELEASE MESSAGE IS CANCELED.//

> GENTEXT/REMARKS/1. Per REF A, COMNAVAIRFOR is responsible for
> implementation, administration, and management of the Naval Aviation
> Maintenance Program (NAMP). This message is to announce the release
> of COMNAVAIRFORINST 4790.2E, a revision to REF B. Revision E
> incorporates 84 changes, 36 AMAs, and numerous corrections. Other
> directives and instructions related to the NAMP should be reviewed
> and revised as necessary to ensure conformity.
> 2. The full NAMP 4790.2E and CSEC will be available NLT than COB
> 22 November 2024 and can be accessed at:
> https://myteam.navair.navy.mil/KM/60/business-processes/resource-
> management-and-adminstration-processes/NAMP and a non-CAC required
> version will be made available. Users who encounter download or
> website connectivity problems should contact their ISIC for
> assistance, or send email to NAVAIR at the following address:
> namp.4790@us.navy.mil.
> 3. NAVAIR will retain both COMNAVAIRFORINST 4790.2D CH-1 and
> COMNAVAIRFORINST 4790.2E with CSEC databases until
> 28 February 2025. By this date, activities will purge all previously
> downloaded copies of COMNAVAIRFORINST 4790.2D CH-1 and replace with
> the 4790.2E.
> 4. On 3 March 2025, activities must be prepared for Aviation
> Maintenance Inspections (AMI) under revision E and begin use of the
> updated CSEC to conduct audits and evaluations.

Note: the reference OPNAVINST 4790.2J (2005) in this message has since been superseded by OPNAVINST 4790.2K (25 Apr 2025, per its DON Issuances listing title), which could not be retrieved (table above).

## Verbatim passage 2: 4790.2E highlights, Enclosure (1) (official, primary)

- URL: https://www.navair.navy.mil/sites/g/files/jejdrs536/files/document/%5Bfilename%5D/NAMP%204790.2E%2028%20October%202024%20Highlights.pdf (HTTP 200, application/pdf, 190,476 bytes; PDF CreationDate 22 Nov 2024)
- Text extracted with `pdftotext -layout`. Only the passages bearing on the requested roles are quoted; the enclosure is a change summary, not the instruction, and contains no definition of any requested term.

> This revision replaces COMNAVAIRFORINST 4790.2D Change 1. COMNAVAIRFORINST
> 4790.2E contains the following highlights.

> Chapter 5 – O-level Maintenance Control; I-level Production Control; Aircraft , Engine,
> and Equipment Inspection; Aircraft Acceptance, Transfer, and Ferry

> Chapter 7 - Quality Assurance (QA)
> •   Provides COs direction on and the authority to reinstate/grant QA & non-QA qualifications.
> •   Introduces the concept of Impromptu CDI evaluations and grading criteria.

> 10.7 NAMP Compliance Auditing NAMPSOP
> •   Defines auditing requirements to include corrective action plans for all long-term
>     discrepancies tracked on the QA Discrepancy Tracker.

> 12.1 COMNAVAIRSYSCOM Aviation Depot Level Industrial Programs
> •   Establishes distinct policy guidance from Chapter 10 to Chapter 12 for the following
>     programs: 12.1.4.8 Tool Control Program (TCP), [...]

> Chapter 15 – Organizational Level (O-Level) Maintenance Data System (MDS)
> Functions, Responsibilities, and Source Document Procedures

> Appendix A - Acronyms, Abbreviations, and Definitions
> •   Adds AMEA – A naval message issued by a FST to advise activities of systemic
>     discrepancies with aviation maintenance compliance being discovered through trend analysis
>     or during engineering inspections.
> •   Adds BCMI – BCMI is a Commander, Fleet Readiness Centers (COMFRC) managed
>     program where selected IMAs are supplemented with on-site D-Level artisans to perform D-
>     Level repair tasks on selected components that are within the capability of the artisan and the
>     IMA.

What these passages establish: 4790.2E's definitions volume is "Appendix A - Acronyms, Abbreviations, and Definitions"; QA is "Chapter 7 - Quality Assurance (QA)"; Maintenance Control is in Chapter 5 ("O-level Maintenance Control"); the Tool Control Program is named as such (depot policy at 12.1.4.8); the CDI title is current in 4790.2E. The definitions themselves remain unread.

## To complete this source

A human with a browser (or CAC access to the myteam site) can download the full 4790.2E from the NAVAIR NAMP page or document library and place the PDF in the scratchpad; Appendix A and Chapter 7 can then be extracted verbatim into this file.
