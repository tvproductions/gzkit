# SAE ARP4754A — Guidelines for Development of Civil Aircraft and Systems

Research date: 2026-10-06. Persona: main-session — craftsperson, governance-aware, whole-file-reasoning, direct. Provenance: R&D run `renewing-vows`. This is a citation record, not a copy: the source is copyrighted and is cited and paraphrased only. Read live on this date at the URL(s) below.

## Bibliographic facts

- **Publisher:** SAE International. The issuing committee is S-18, Aircraft and Systems Development and Safety Assessment.
- **Designation:** ARP4754A (Aerospace Recommended Practice), revision A of ARP4754. DOI 10.4271/ARP4754A.
- **Title:** Guidelines for Development of Civil Aircraft and Systems.
- **Edition:** ARP4754A, revised 2010-12-21. ARP4754 was first issued 1996-11-01.
- **Status:** superseded. SAE MOBILUS marks ARP4754A as Historical. The current revision is ARP4754B, revised 2023-12-20 (DOI 10.4271/ARP4754B), under the same title.
- **Publisher URLs:**
  - SAE MOBILUS, ARP4754A: <https://saemobilus.sae.org/standards/arp4754a-guidelines-development-civil-aircraft-systems>
  - SAE MOBILUS, ARP4754B: <https://saemobilus.sae.org/standards/arp4754b-guidelines-development-civil-aircraft-systems>
  - SAE training course C2301 (ARP4754B): <https://saemobilus.sae.org/courses/arp4754b-guidelines-development-civil-aircraft-systems-c2301>
  - sae.org product page: <https://www.sae.org/standards/content/arp4754a/>. It redirected to a page that rendered no content on this date, so the MOBILUS pages were used.

## Scope (paraphrased)

**ARP4754A.** The document covers the development of aircraft systems, taking account of the aircraft's operating environment and functions. That includes validating requirements and verifying the design implementation for certification and product assurance. It gives practices for showing compliance with regulations, written in the context of 14 CFR Part 25 and EASA CS-25, and possibly applicable to the other Parts and CS codes. Post-certification modifications are covered in its section 6. It leaves out several subjects and points each to its own guidance:

| Subject left out | Pointed to |
|---|---|
| Detailed software development | DO-178B/ED-12B |
| Electronic hardware development | DO-254/ED-80 |
| Integrated modular avionics | DO-297/ED-124 |
| Safety assessment methodology | ARP4761 |
| In-service safety assessment | ARP5150 and ARP5151 |
| Structures, and MMEL/CDL development | — |

**ARP4754B (2023).** It keeps that frame and updates the pointers: DO-178C/ED-12C for software, DO-326A/ED-202A for airworthiness security, and ARP4761A/ED-135 for safety assessment processes. It also names safety, alongside certification and product assurance, as a purpose of requirements validation and implementation verification.

## Claims checked

| Claim (from the record) | Verdict | Basis |
|---|---|---|
| ARP4754A is the 2010 *Guidelines for Development of Civil Aircraft and Systems*. | VERIFIED | SAE MOBILUS: ARP4754A, revised 2010-12-21, under that title. |
| ARP4754A is the revision to cite as current. | CONTRADICTED | ARP4754B (revised 2023-12-20) is the current revision, and ARP4754A is marked Historical. |
| ARP4754A assigns development assurance levels (FDAL/IDAL) from the severity of failure conditions. | NOT VERIFIED | Neither the ARP4754A nor the ARP4754B public scope on SAE mentions development assurance levels, FDAL/IDAL or severity classification. The nearest publisher material is the outline of SAE's own ARP4754B course (C2301), which has a module titled "Safety Assessment and Development Assurance Level Assignment". That shows DAL assignment is part of ARP4754B's subject matter and is tied to safety assessment. It does not show the severity-to-level mapping, the FDAL/IDAL terms, or anything specific to revision A. |

## Notes for the record

- The record's doctrine claim is that lane, as an assurance level, should follow the severity of the failure condition. That claim rests on the third row. Until that row is checked against a licensed copy, the analogy has no publicly verifiable anchor in SAE's text.
- Public regulator documents could supply that anchor instead. Two candidates:
  - the FAA advisory circular that recognises ARP4754A, which is US-government material and is handled by the companion `us-gov-*` records;
  - EASA Certification Memorandum CM-DASA-002 Issue 01 (17 December 2024), *Development Assurance Considerations in Product Certification*, <https://www.easa.europa.eu/en/downloads/140779/en>. Only its cover and contents were read here; it was not checked against this claim.
- Cite ARP4754B for current practice. If the argument depends on ARP4754A's wording, say why the historical revision is cited.
