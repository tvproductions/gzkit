# NASA/TM-2001-210876, Hayhurst, Veerhusen, Chilenski and Rierson, A Practical Tutorial on Modified Condition/Decision Coverage (2001)

Research date: 2026-10-08. Persona: main-session — craftsperson, governance-aware, whole-file-reasoning, direct. Provenance: R&D run `renewing-vows`. This is source research, not a skill implementation or operator ruling. Public domain (NASA technical memorandum; one author is FAA staff). Read on this date from the NASA Technical Reports Server copy at the URL below, as page images; the cover, contents, abstract and pages 1–10 read, the rest not read. The tutorial is written against DO-178B, the predecessor of DO-178C, and says of itself that it "does not constitute regulatory software policy or guidance."

## Bibliographic facts

- Authors: Kelly J. Hayhurst (NASA Langley), Dan S. Veerhusen (Rockwell Collins), John J. Chilenski (Boeing), Leanna K. Rierson (Federal Aviation Administration).
- Document: NASA/TM-2001-210876, May 2001, Langley Research Center. Supported by the FAA William J. Hughes Technical Center.
- URL read: <https://ntrs.nasa.gov/api/citations/20010057789/downloads/20010057789.pdf> (NTRS citation 20010057789).

## Excerpts, verbatim

> This tutorial concerns one particular objective in DO-178B: objective 5 in Table A-7 of Annex A. This objective, which is applicable to level A software only, requires that tests achieve modified condition/decision coverage (MC/DC) of the software structure. (§ 1, p. 1)

> Three of the measures in Table 1 are found in objectives for test coverage given in DO-178B Table A-7 of Annex A:
> - objective 7 requires statement coverage for software levels A-C
> - objective 6 requires decision coverage for software levels A-B
> - objective 5 requires MC/DC for software level A
> (§ 2.3, p. 8)

> There are actually four objectives in Table A-7 for test coverage of software structure. Objective 8, requiring data coupling and control coupling for software levels A-C, is not addressed in this tutorial; but, is mentioned here for completeness. (§ 2.3, footnote 9, p. 8)

> The Annex A objectives for requirements-based test coverage are stated with respect to both high- and low-level requirements. Objective 3 in Table A-7 requires test coverage of high-level requirements for software levels A-D; and objective 4 in Table A-7 requires test coverage of low-level requirements for software levels A-C. (§ 2.2.1, p. 5)

> Structural coverage analysis provides a means to confirm that "the requirements-based test procedures exercised the code structure" (DO-178B, section 6.4.4). (§ 2.2.2, p. 6)

## Claims checked

| Claim (from the record) | Verdict | Where in the text |
| --- | --- | --- |
| Structural coverage criteria are set by software level: statement coverage at levels A–C, decision coverage at levels A–B, MC/DC at level A, and none at level D. | VERIFIED for DO-178B | § 2.3, p. 8, quoted above; level D is absent from the three structural objectives and present only in the requirements-coverage objective 3 (§ 2.2.1). DO-178C retained Table A-7's structure according to the public RTCA material in `std-rtca-do-178c.md`, but this text is about DO-178B and says so throughout. |
| The coverage objectives sit in Annex A Table A-7. | VERIFIED for DO-178B | § 1 and § 2.3. |
| The count of objectives per level in DO-178C (71, 69, 62, 26). | NOT VERIFIED | The tutorial gives no count. |
| Problem reports are life cycle data at DO-178C § 11.17. | NOT VERIFIED | Not addressed. |
