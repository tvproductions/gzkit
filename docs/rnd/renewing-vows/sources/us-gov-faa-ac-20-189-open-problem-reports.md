# FAA Advisory Circular 20-189, Management of Open Problem Reports (OPRs)

Research date: 2026-10-08. Persona: main-session — craftsperson, governance-aware, whole-file-reasoning, direct. Provenance: R&D run `renewing-vows`; the operator supplied the PDF on 2026-10-08, after the run recorded that this circular, the companion of AC 00-71, was unread. This is source research, not a skill implementation or operator ruling. Public domain (US federal government work). Read in full on this date from the supplied PDF; the bearing sections are quoted verbatim below.

## Bibliographic facts

- **Issuing body:** Federal Aviation Administration, US Department of Transportation. Initiated by AIR-622; signed by the Acting Director, Policy and Innovation Division, Aircraft Certification Service.
- **Document:** AC No. 20-189, "Management of Open Problem Reports (OPRs)". Date: Sep 16, 2022. The "Change" field is blank.
- **The copy read:** `AC_20-189_(final).pdf`, 11 pages, 454,399 bytes, SHA-256 `30042e1dfff49db2953e6683874baafdb912a9096900f3f62f3bb98ab3ba0b73`. PDF metadata: title "AC 20-189", created 2022-09-19. The operator supplied it from outside the repository; the session did not fetch it from faa.gov.
- **Not vendored.** The PDF is not copied into the repository; the checksum identifies the copy.
- **Status:** current as of the copy. Whether a later revision exists was not checked.
- **Its companion.** § 3.3: "See AC 00-71, Best Practices for Management of Open Problem Reports." That circular's record is `us-gov-faa-ac-00-71-open-problem-reports.md`. The two share their definitions word for word: the problem report, the open problem report, the four states (recorded, classified, resolved, closed) and the four classifications (significant, functional, process, life cycle data). Those are quoted in that file and not repeated here.
- **Legal weight** (§ 1): it "describes an acceptable means for showing compliance"; conformity "is voluntary only"; "if you use the means described in this AC, you should follow it in all applicable respects".
- **Harmonisation** (§ 3.2): "harmonized as appropriate with European Union Aviation Safety Agency (EASA) AMC 20-189."

## The text

### Why it was written (§ 3.1)

> Each of the system, software, and AEH domains relies on problem report (PR) management to ensure the proper management of OPRs and to help ensure safe products at the time of approval. However, existing guidance on PR and OPR management is inconsistent and incomplete across domains.

### Managing problem reports (§ 5)

> The PR management process is a key enabler for OPR management. ... Consequently, this process reduces the risk of a loss of visibility of critical issues remaining at the time of approval.

> 5.2 A problem recorded after approval should also be managed through the PR management process, and any related systemic process issues should be identified and corrected.

> 5.3 PRs that cannot be resolved by the current stakeholder should be reported in a manner that is understandable to the affected stakeholders.

> 5.4 For PRs that may have an impact on other products or articles that are developed within an organization, a means should be established for sharing PR information so that any necessary corrective actions can be taken.

### Classifying open reports (§ 6.1)

> 6.1.1 The applicant should establish an OPR classification scheme including, at a minimum, the following classifications: ‘Significant’, ‘Functional’, ‘Process’, and ‘Life Cycle Data’. Other classifications or sub-classifications may be created as needed. The classification scheme should be described in the appropriate planning document(s).

> 6.1.2 Each OPR should be assigned a single classification per the classification scheme. When multiple classifications apply, the OPR should be assigned the classification with the highest priority.

> 6.1.3 The classification of an OPR should account for and document all mitigations known at the time of classification that are under the control of the classifying stakeholder. A mitigation that is controlled by another stakeholder may be considered in the classification only if validated with that stakeholder

> 6.1.4 A stakeholder, other than the aircraft TC or STC applicant, should classify as ‘Significant’ any OPR for which the classification may vary between ‘Functional’ and ‘Significant’, depending on the installation.

### Assessing them (§ 6.2)

> Each OPR should be assessed to determine:
>
> - Any resulting functional limitations or operational restrictions at the equipment level (for TSO articles) or at the product level (for other types of approvals);
> - Relationships that may exist with other OPRs; and
> - For a ‘Significant’ or ‘Functional’ OPR, the underlying technical cause of the problem.

### What may stay open (§ 6.3)

> Disposition: OPRs classified as ‘Significant’ per the classification in paragraph 6.1, for which no sufficient mitigation or justification exists to substantiate the acceptability of the safety effect, should be resolved prior to approval.

### Reporting them (§ 6.4)

> An OPR summary report should be prepared and provided to the affected stakeholder(s), and to the certification authority upon request.

For each open report the summary gives: its identification; the affected configuration items or processes; a title and a description "formulated in a manner understandable by the affected stakeholder(s)"; the conditions under which the problem occurs; its classification; "Relationships that are known to exist with other OPRs"; and by class, the mitigations or justifications, any "Functional limitations and operational restrictions", and:

> 6.4.6.5. For each OPR not classified as ‘Significant’ or ‘Functional’, justification that the error cannot have a safety or functional effect.

### Who does it (§ 7)

> 7.1 PR Management (per paragraph 5): Should be performed by the stakeholder at each level. The applicant has responsibility for the overall PR process for all the involved stakeholders.

## Claims checked

| Claim (from the record) | Verdict | Where in the text |
| --- | --- | --- |
| "Problem report" is the term for a recorded defect, from DO-178C. | VERIFIED | § 4.1: "adapted from DO-178C/ED-12C". |
| An open defect at release is a recognised, managed state. | VERIFIED | § 4.1 and § 6: the open problem report, with classification, assessment, disposition and a summary report. |
| Problem reports are life cycle data at § 11.17. | NOT VERIFIED | No clause number is given. |

## Notes for the record

- **An open report may ship; an unmitigated significant one may not.** That is the whole of the disposition rule.
- **The lower classes carry a burden of proof.** A report not classed significant or functional needs a "justification that the error cannot have a safety or functional effect".
- **Classify up when it depends on where the part is installed.**
- **A mitigation someone else controls counts only if they have confirmed it.**
- **Each report is assessed for its relationships to other open reports** and, for the two higher classes, its "underlying technical cause".
- **Problems found after approval go through the same process**, and "any related systemic process issues should be identified and corrected".
- **A report must be readable by whoever inherits it.**
- **Problems are shared across products** that might have the same fault.
- **The scheme is written into the plan**, not invented at closeout.
