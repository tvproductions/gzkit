# FAA Advisory Circular 20-115D, Airborne Software Development Assurance Using EUROCAE ED-12( ) and RTCA DO-178( )

Research date: 2026-10-08. Persona: main-session — craftsperson, governance-aware, whole-file-reasoning, direct. Provenance: R&D run `renewing-vows`; the operator supplied the PDF on 2026-10-08, the same day the operator ruled that DO-178C itself is not bought. This is source research, not a skill implementation or operator ruling. Public domain (US federal government work). Read in full on this date from the supplied PDF; the bearing sections are quoted verbatim below.

## Bibliographic facts

- **Issuing body:** Federal Aviation Administration, US Department of Transportation. Initiated by AIR-134; signed by the Manager, Design, Manufacturing, & Airworthiness Division, Aircraft Certification Service.
- **Document:** AC No. 20-115D, "Airborne Software Development Assurance Using EUROCAE ED-12( ) and RTCA DO-178( )". Date: 07/21/2017. The "Change" field is blank.
- **What it cancels** (§ 3): "AC 20-115C, Airborne Software Assurance, dated July 19, 2013."
- **The copy read:** `AC_20-115D.pdf`, 16 pages, 511,369 bytes, SHA-256 `5597a1af49c872a1a843c05601742ddcc8e8a190642f31e3cb9ce8e0dc63d91e`. PDF metadata: title "AC 20-115D", created 2017-10-23. The operator supplied it from outside the repository; the session did not fetch it from faa.gov.
- **Not vendored.** The PDF is not copied into the repository; the checksum identifies the copy.
- **Status:** current as of the copy. Whether a later revision exists was not checked.
- **Kind of source:** primary for what the regulator says about DO-178C, and for nothing inside DO-178C that it does not itself state. It is the FAA's recognition of the standard, in the FAA's words.
- **Legal weight** (§ 1a): "This AC is not mandatory and does not constitute a regulation. However, if you use the means described in the AC, you must follow it in all applicable respects."

## The text

### What the FAA recognizes (§ 1)

> b. This AC recognizes the following current EUROCAE and RTCA, Inc. documents:
>
> (1) EUROCAE ED-12C, Software Considerations in Airborne Systems and Equipment Certification, dated January 2012, and RTCA DO-178C, Software Considerations in Airborne Systems and Equipment Certification, dated December 13, 2011.
>
> (2) EUROCAE ED-215, Software Tool Qualification Considerations, dated January 2012, and RTCA DO-330, Software Tool Qualification Considerations, dated December 13, 2011.

It also recognizes the three supplements (DO-331, DO-332, DO-333), and names DO-248C as supporting information, "a collection of frequently asked questions (FAQs) and discussion papers (DPs) compiled and approved by the authors".

### The form of the guidance (§ 4a)

> The guidance provided in these documents is in the form of:
>
> (1) Objectives for software life cycle processes;
>
> (2) Activities that provide a means for satisfying the objectives; and
>
> (3) Descriptions of the evidence that indicate that the objectives have been satisfied.

### Using DO-178C (§ 6)

> a. You should satisfy all of the objectives associated with the software level assigned to the software and develop all of the associated life cycle data demonstrating satisfaction of the applicable objectives, as listed in the ED-12C/DO-178C Annex A tables ... You should plan and execute activities that will satisfy each objective.

> c. Section 9.4 of ED-12C/DO-178C specifies the software life cycle data related to the type design of the certified product. However, not all of the specified data applies to all software levels; specifically Design Description and Source Code are not part of the type design data for Level D.

> d. You should make available to us, upon request, any of the data described in section 11 of ED-12C/DO-178C, applicable tool qualification data, data outputs from any applicable supplements, and any other data needed to substantiate satisfaction of all applicable objectives.

> e. The FAA may publish an acceptable means of compliance for specific regulations, stating the required relationship between the criticality of the software-based systems and the software levels as defined in ED-12C/DO-178C. Such acceptable means of compliance will take precedence over the application of section 2.3 of ED-12C/DO-178C.

### How a level is assigned (§ 9b(2))

> (2) The system safety process assigns the minimum development assurance level based on the severity classifications of failure conditions for a given function. The ED-12B/DO-178B software levels are consistent with the ED-12C/DO-178C software levels.

### Re-using and changing approved software (§ 9b)

> (1) Assess the legacy software to be modified or re-used for its usage history from previous installations. If the software has safety-related service difficulties, airworthiness directives, or open problem reports with a potential safety impact on the proposed installation, establish plans to resolve all related software deficiencies.

> (4) If modifications to the software are required, conduct a software change impact analysis (CIA) to determine the extent of the modifications, the impact of those modifications, and what verification is required to ensure that the modified software performs its intended function and continues to satisfy the identified means of compliance.
>
> (a) Identify the software changes to be incorporated and perform a CIA consisting of one or more analyses associated with the software change as identified in section 12.1 of ED-12C/DO-178C;
>
> (b) Conduct the verification as indicated by the CIA; and
>
> (c) Summarize the results of the CIA in the Plan for Software Aspects of Certification (PSAC) or in the Software Accomplishment Summary (SAS).

On configuration data (§ 5a(4)): "If using configuration data, as defined under “Parameter Data Item” in ED-12C/DO-178C, existing processes for such data have been evaluated and found to be acceptable".

On field-loadable software (§ 8b(2)): "The FLS should be protected against corruption or partial loading to an integrity level appropriate for the software level of the FLS."

### Tool qualification (§ 10)

> Section 12.2 of ED-12C/DO-178C, and ED-215/DO-330 provide an acceptable method for tool qualification. ED-215/DO-330 contains its own complete set of objectives, activities, and life cycle data for tool qualification.

> (1) ED-12C/DO-178C establishes five levels of tool qualification based on the tool use and its potential impact in the software life cycle processes (see section 12.2.2 and Table 12-1 of ED-12C/DO-178C).

Table 2 correlates the older tool types with the levels:

| DO-178B tool qualification type | Software level | DO-178C tool criteria | Tool qualification level |
| --- | --- | --- | --- |
| Development | A | 1 | TQL-1 |
| Development | B | 1 | TQL-2 |
| Development | C | 1 | TQL-3 |
| Development | D | 1 | TQL-4 |
| Verification | A, B | 2 | TQL-4 |
| Verification | C, D | 2 | TQL-5 |
| Verification | All | 3 | TQL-5 |

## Claims checked

Each verdict is against this circular: what the regulator says of the standard.

| Claim (from the record) | Verdict | Where in the text |
| --- | --- | --- |
| DO-178C was published 2011-12-13. | VERIFIED | § 1b(1): "dated December 13, 2011". |
| A level is assigned from the severity of the failure condition. | VERIFIED | § 9b(2): "based on the severity classifications of failure conditions for a given function". The assignment is made by "the system safety process", outside DO-178C. |
| The standard's own word is "software level". | VERIFIED | Throughout; "development assurance level" is used once, of what the system safety process assigns. |
| Objectives are tabulated in Annex A, by level. | VERIFIED | § 6a: "the objectives associated with the software level assigned ... as listed in the ED-12C/DO-178C Annex A tables". No count is given. |
| Section 11 is the software life cycle data. | VERIFIED | § 6d: "the data described in section 11". |
| Problem reports are life cycle data at § 11.17. | NOT VERIFIED | "Open problem reports" are used as evidence in § 5a(1) and § 9b(1); no clause number is given. |
| Tools are qualified, at five levels, under DO-330. | VERIFIED | § 10 and Table 2. |
| A verifying tool is held to less than a generating tool. | VERIFIED | Table 2: development tools at TQL-1 to TQL-4, verification tools at TQL-4 and TQL-5. |
| Structural coverage criteria differ by level. | NOT VERIFIED | Not addressed. |
| Level E exists. | NOT VERIFIED | Table 1 and Table 2 run A to D; level E is not mentioned. |

## Notes for the record

- **The severity model now stands on a primary text.** The regulator states it in one sentence, and places the assignment in the system safety process.
- **A change to approved software starts with a change impact analysis**: the extent of the change, its impact, and "what verification is required". Its result is written into the plan or the accomplishment summary.
- **Prior use counts, and so do its problems.** Re-use is assessed from "usage history", service difficulties and open problem reports.
- **Guidance has three parts**: objectives, activities that satisfy them, and descriptions of the evidence that shows it.
- **Data at the lowest levels is less.** Design description and source code are not type design data at level D.
- **"Integrity level" appears once**, of protection against corrupted loading "appropriate for the software level". It is not the standard's name for its levels.
- **Still only in the standard:** the number § 11.17, any count of objectives, and level E.
