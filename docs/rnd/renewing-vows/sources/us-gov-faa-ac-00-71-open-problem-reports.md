# FAA Advisory Circular 00-71, Best Practices for Management of Open Problem Reports (OPRs)

Research date: 2026-10-08. Persona: main-session — craftsperson, governance-aware, whole-file-reasoning, direct. Provenance: R&D run `renewing-vows`; the operator supplied the PDF on 2026-10-08. This is source research, not a skill implementation or operator ruling. Public domain (US federal government work). Read in full on this date from the supplied PDF; the bearing sections are quoted verbatim below.

## Bibliographic facts

- **Issuing body:** Federal Aviation Administration, US Department of Transportation. Initiated by AIR-622; signed by the Acting Director, Policy and Innovation Division, Aircraft Certification Service.
- **Document:** AC No. 00-71, "Best Practices for Management of Open Problem Reports (OPRs)". Date: Sep 16, 2022. The "Change" field is blank.
- **The copy read:** `AC_00-71_(final).pdf`, 10 pages, 396,108 bytes, SHA-256 `55fbc33c7269b75692f6d125903c84ee895c2cf63d346656a7971cc83bdd626f`. PDF metadata: title "AC 00-71", created 2022-09-19. The operator supplied it from outside the repository; the session did not fetch it from faa.gov.
- **Not vendored.** The PDF is not copied into the repository; the checksum identifies the copy.
- **Status:** current as of the copy. Whether a later revision exists was not checked.
- **Its companion.** § 1: it "is intended to complement AC 20-189, Management of Open Problem Reports (OPRs)". AC 20-189 holds the classification scheme this circular explains, and the run has not read it.
- **Legal weight** (§ 1): "conformity with this guidance document (as distinct from existing statutes and regulations) is voluntary only".

## The text

### Definitions (§ 3.1)

> Development assurance – All of those planned and systematic actions used to substantiate, with an adequate level of confidence, that errors in requirements, design, and implementation have been identified and corrected such that the system satisfies the applicable certification basis (source: ARP4754A/ED-79A).

> Error – A mistake in requirements, design, or implementation with the potential of producing a failure.

> Failure – The inability of a system or system component to perform a function within specified limits (source: DO-178C/ED-12C and DO-254/ED-80).

> Open problem report (OPR) – A problem report that has not reached the state ‘closed’ at the time of approval.

> Problem report (PR) – A means to identify and record the resolution of anomalous behavior, process non-compliance with development assurance plans and standards, and deficiencies in life cycle data (adapted from DO-178C/ED-12C).

### The four states of a problem report (§ 3.2)

> Recorded – A problem that has been documented using the problem reporting process.
>
> Classified – A problem report that has been categorized in accordance with an established classification scheme.
>
> Resolved – A problem report that has been corrected or fully mitigated, for which resolution of the problem has been verified but not formally reviewed and confirmed.
>
> Closed – A resolved problem report that underwent a formal review and confirmation of an effective resolution of the problem.

### The four classifications (§ 3.3)

> Significant – assessed at the product, system, or equipment level, a PR that has an actual or potential effect on the product, system, or equipment function that may lead to a Catastrophic, Hazardous, or Major failure condition, or may affect compliance with the operating rules.
>
> Functional – a PR that has an actual or a potential effect on a function at the product, system, or equipment level.
>
> Process – a PR that records a process non-compliance or deficiency that cannot result in a potential safety nor a potential functional effect.
>
> Life Cycle Data – a PR that is linked to a deficiency in a life cycle data item but not linked to a process non-compliance or process deficiency.

### Managing them (§ 4.1)

> 4.1.2 PR Classification – a means to classify PRs prior to the time of approval of the product or of the TSO article, as early in the life cycle as practical. While early classification may be preliminary, it will help to focus attention on PRs with a potential safety or functional effect, as well as process PRs that may impact the development or development assurance processes.

> 4.1.3 PR Assessment – a means to assess the effect of having a PR remain open at the time of approval. Assessment of PRs classified as ‘Significant’, ‘Functional’ or ‘Process’ would typically be performed by a review board which includes representatives from the appropriate disciplines ... Assessment of PRs classified as ‘Life Cycle Data’ may be performed within the peer review process instead of a review board.

> 4.1.4 PR Resolution – a means to correct or mitigate PRs prior to the time of approval, as early in the life cycle as practical. The PR resolution process may depend on the classification of the PR; for example, shorter closure loops could be set for PRs classified as ‘Life Cycle Data’.

> 4.1.5 PR Closure – a means to close PRs, which includes the review and confirmation of the resolution of the problem, and is indicated through a documented authorization process (e.g., Change Control Board signoff).

### One classification each, by priority (§ 4.2)

> 4.2.1 The most important clarification when compared with the former classification scheme is to give each OPR a single classification using a given order of priority ... This promotes visibility of the most relevant issues and helps to prevent inconsistencies in classification. For example, a missing or incorrect requirement issue can be classified as ‘Life Cycle Data’ only if it is confirmed that it cannot be classified as ‘Significant’, ‘Functional’, or ‘Process’, in that order of priority.

> 4.2.4 ... An example of an OPR that should not be classified as a ‘Process’ PR is one related to a requirement that was not completely verified due to a process deficiency, because the potential safety or functional impact remains undetermined. Considering the highest priority classification would, in such a case, lead to a ‘Significant’ or ‘Functional’ classification, thus putting even more emphasis on the need to resolve the shortcoming in the verification activities.

### Severity is judged where the thing is installed (§ 4.3.2)

> For example, in the case of an engine TC, a partial or complete loss of thrust or power is regarded as a Minor Engine Effect, whereas it may have a more severe effect at the aircraft level. Unless the engine manufacturer can confirm that the effect at the installation level is no more than Minor, the OPR would be classified as ‘Significant’.

## Claims checked

| Claim (from the record) | Verdict | Where in the text |
| --- | --- | --- |
| "Problem report" is DO-178C's term for a recorded defect. | VERIFIED | § 3.1: defined, "adapted from DO-178C/ED-12C". |
| Problem reports are life cycle data at § 11.17. | NOT VERIFIED | No clause number is given. |
| A defect knowingly left open has a name in the airworthiness register. | VERIFIED, with a better term than the record's | § 3.1: an "open problem report" is one "that has not reached the state ‘closed’ at the time of approval". The record's "deferred defect (MEL item)" names a different thing, equipment inoperative in service, and is unsourced. |

## Notes for the record

- **Resolved is not closed.** A fix that is made and verified is "Resolved". It is "Closed" only after "a formal review and confirmation of an effective resolution", shown by "a documented authorization".
- **Four states in order**: recorded, classified, resolved, closed.
- **Four classes, one per report, by priority**: significant, functional, process, life cycle data. A report takes the highest class it could belong to.
- **An unverified requirement is not a paperwork problem.** Where the impact "remains undetermined", the report is classed up, not down.
- **Leaving a report open at approval is a decision that is assessed**, by a review board for the three higher classes.
- **Severity is judged at the level where the item is installed**, and the burden is on the maker of the part to show it is no worse there.
- **"Development assurance" is defined**, from the systems standard: actions that substantiate "with an adequate level of confidence" that errors "have been identified and corrected".
- **Classify early, even provisionally.**
- The scheme itself is in AC 20-189, unread.
