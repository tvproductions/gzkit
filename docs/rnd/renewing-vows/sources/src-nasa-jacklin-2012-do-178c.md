# Jacklin (NASA Ames), "Certification of Safety-Critical Software Under DO-178C and DO-278A"

Research date: 2026-10-07. Persona: main-session — craftsperson, governance-aware, whole-file-reasoning, direct. Provenance: R&D run `renewing-vows`; the operator supplied the PDF on 2026-10-07. This is a citation record: the paper is cited and paraphrased, with short quotations. Read in full on this date from the supplied PDF.

## Bibliographic facts

- **Author:** Stephen A. Jacklin, Aerospace Engineer, Intelligent Systems Division, NASA Ames Research Center. The paper's acknowledgments say the author was a member of RTCA Special Committee 205, which wrote DO-178C, and is listed in Appendix A of that document.
- **Title:** Certification of Safety-Critical Software Under DO-178C and DO-278A.
- **Venue:** each page carries "American Institute of Aeronautics and Astronautics"; the PDF metadata title is "Jacklin - 2607- Final for 2012 AIAA Infotech-corrected", created 2012-06-28. The paper's own text gives no conference name or date.
- **The copy read:** `20120016835.pdf`, 14 pages, 121,175 bytes, SHA-256 `466035d3e47ebdd9dd87eae4541ad1cb04113769f8160d3b8541a7fc55f0e8e5`. The file name has the form of a NASA technical-reports identifier; the session did not look it up.
- **Rights:** the copy carries no copyright statement. The author is a US government employee, which usually makes such a paper a government work, and the copy does not say so. It is treated here as a cited source with short quotations, and it is not vendored.
- **Kind of source:** secondary, and a strong one. It is an overview of DO-178C by a member of the committee that wrote it. It is still not RTCA's text, and it cannot move a claim to VERIFIED against that text.

## What it was supplied for, and what it is

The operator sent it after the run asked for the definitions of initial and full operational capability. It does not contain them: "operational capability", "IOC" and "FOC" occur nowhere in it. It is a source for the DO-178C rows.

## What the paper says

### Software levels, and how they are assigned

Section II.A: DO-178C "uses the same software levels categories (SL-A to SL-E) as are used in DO-178B", and "Level A is the highest level of software criticality." The levels are placed in DO-178C section 2. Table 1 ties each level to a "Software Failure Effect Category":

| Software failure effect category | DO-178C software level | DO-278A assurance level |
| --- | --- | --- |
| Catastrophic | SL-A | AL-1 |
| Hazardous | SL-B | AL-2 |
| Major | SL-C | AL-3 |
| Less than major, more than minor | Not used | AL-4 |
| Minor | SL-D | AL-5 |
| No Effect | SL-E | AL-6 |

### The two documents use two words for the level

Section IV lists the terminology differences. The first:

> “Software level” in DO-178C was replaced with “assurance level” in DO-278A

DO-278A's title, from the paper's reference list, is "Software Integrity Assurance Considerations for Communication, Navigation, Surveillance and Air Traffic Management (CNS/ATM) Systems".

### The philosophy

Section II:

> Since testing can never prove the absence of software errors, the primary DO-178C philosophy is to demonstrate the quality of the software development process from beginning to end in an effort to minimize the creation of error.

Section II.C, on what DO-178C leaves out: validation is "the process of determining that the software requirements are correct and complete", and "DO-178C does not provide guidance for software validation testing".

### Coverage

Section II.A: DO-178C "divides coverage into two types, requirements-based coverage and structural coverage." Requirements-based coverage "analyzes the software test cases to confirm that they provide proof that all requirements have been satisfied." It "requires extensive verification coverage testing for level A and B software". The paper does not say which structural criterion binds at which level.

### Traceability in both directions

Section III.C:

> DO-178C emphasizes that two-way or bi-directional traceability is required between 1) system requirements (allocated to software) and high-level requirements, 2) high-level requirements and low-level requirements, 3) low-level requirements and source code, 4) software requirements and test cases, 5) test cases and procedures, and 6) test procedures and test results.

> This assures that orphan source code and dead source code are not inadvertently produced.

### Objectives and Annex A

Section III.A: the tables in Annex A "have also been modified to include a new “activity” column that lists the relevant activities associated with all verification activities supporting the objective." The paper gives no count of objectives.

### Data that steers behaviour is verified like code

Section III.B: parameter data items are "data that influences the behavior of the software without modifying the executable object code", and "DO-178C calls for the same verification process to be followed for parameter data file items as that done for executable object code."

### Tools

Section III.E:

> DO-178C states that the tools used to generate software or to verify software must themselves be verified to be correct. This tool verification process is called qualification. Moreover, a tool such as a compiler qualified for one project is not necessarily qualified for a different project.

Section VI.A: DO-330 "defines five tool qualification levels", and it "places more stringent verification requirements on tools used to generate code than tools used to verify code." The top three levels are for tools that generate software; the lower two are for tools that verify it. Section VI.C: a tool has two life cycles, its own and that of the software it is used on, and a "tool operational requirements" document states how it will be used.

### Assurance cases

Section III.F: DO-178C "defines an assurance case as a technique in which arguments are explicitly given to link the evidence to the claims of compliance with the system safety objectives."

### Credit for service history

Section III.D: software "that has been in service a length of time and whose executable object code has not been modified in an uncontrolled manner may be given certification credit."

### Levels in contact

Section IV.E, of ground systems: "The main concern when coupling systems is that software approved to a lower assurance level might potentially corrupt software approved to a higher level."

### Sections of DO-178C the paper names

Section 2, software levels; 3, the software life cycle; 4, planning; 4.5, development standards; 5, development; 6, verification; 7, configuration management; 8, quality assurance; 9, certification liaison; 10, certification; 12.2, tool qualification; 12.3, alternative methods. It attaches "the software design standards" to section 11.

### Dates

DO-178C "was released in December 2011", with DO-278A, DO-248C, DO-330, DO-331, DO-332 and DO-333.

## Claims checked

| Claim (from the record) | In this paper | Effect |
| --- | --- | --- |
| DO-178C has levels A to E. | Yes, with their failure-effect categories. | Secondary support from a committee member. |
| A level is assigned from the severity of the failure condition. | Yes: Table 1 keys each level to a failure effect category. | Secondary support. This is the model gzkit's scale does not use. |
| DO-178C calls the level a "development assurance level". | No. DO-178C's term is "software level"; "assurance level" is DO-278A's. | The record's attribution of "assurance level" to DO-178C is corrected. |
| Bidirectional traceability is required. | Yes, across six named pairs. | Secondary support, with the reason given. |
| Testing is requirements-based, with structural coverage. | Yes. | Secondary support. |
| Structural coverage criteria differ by level (statement, decision, MC/DC). | Not addressed beyond "extensive" for levels A and B. | Stays not verified. |
| Objectives are tabulated in Annex A. | Yes; no count. | The tables are supported; counts stay not verified. |
| Problem reports are life cycle data at § 11.17. | Not addressed. | Stays not verified. |
| Gating tools must be qualified, under DO-330. | Yes, with five levels and the split between generating and verifying tools. | Agrees with `std-rtca-do-330.md`. |
| DO-178C was published in December 2011. | Yes. | Agrees with the publisher's 2011-12-13; the Parasoft page's "January 2012" is the outlier. |

## Notes for the record

- **In RTCA's own usage an "assurance level" is assigned from the failure effect category.** That is the reason the run gave for not using the term for gzkit's consequence bands, now stated by a member of the committee.
- **A tool that verifies is held to less than a tool that generates.** In gzkit's terms a validator is the first kind and an agent that writes code is the second.
- **A tool's qualification does not travel between projects.**
- **Data that changes behaviour without changing code gets the code's verification.** gzkit's rule that execution reads thresholds and rosters from JSON puts a great deal of behaviour in such data.
- **The document set separates verification from validation** and gives no guidance on the second.
- **What still needs the standard itself:** the number § 11.17, any count of objectives, and the coverage criterion per level.
