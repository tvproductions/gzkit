# RTCA DO-330 — Software Tool Qualification Considerations

Research date: 2026-10-06. Persona: main-session — craftsperson, governance-aware, whole-file-reasoning, direct. Provenance: R&D run `renewing-vows`. This is a citation record, not a copy: the source is copyrighted and is cited and paraphrased only. Read live on this date at the URL(s) below.

## Bibliographic facts

- **Publisher:** RTCA, Inc. (prepared by SC-205, jointly with EUROCAE WG-71). The EUROCAE twin is ED-215.
- **Designation:** RTCA DO-330.
- **Title:** Software Tool Qualification Considerations.
- **Edition:** issued 2011-12-13, according to the RTCA store. RTCA notes that errata against DO-330 exist.
- **Status:** current. It is on sale in the RTCA store, and RTCA's DO-178() page lists it as the tool-qualification document of the DO-178C suite.
- **Publisher URLs:**
  - RTCA store: <https://my.rtca.org/productdetails?id=a1B36000001IcfkEAC>
  - RTCA DO-178() page: <https://www.rtca.org/do-178/>
- **RTCA-hosted FAS Topic Papers used:** these carry the same caveat as in the DO-178C record. They are informational only, not RTCA/EUROCAE policy, and are used here only where they locate DO-330 content.
  - FTP1015 rev 1: <https://www.rtca.org/wp-content/uploads/2020/12/FTP1015_1.pdf>
  - FTP1009 rev 6: <https://www.rtca.org/wp-content/uploads/2020/12/FTP1009_6.pdf>
  - FTP1055 rev 3: <https://www.rtca.org/wp-content/uploads/2020/12/FTP1055_3.pdf>
  - FTP1041 rev 4: <https://www.rtca.org/wp-content/uploads/2024/06/FTP1041_4-PUBLICATION.pdf>
  - FTP1008 rev 4: <https://www.rtca.org/wp-content/uploads/2020/12/FTP1008_4.pdf>

## Scope (paraphrased)

In DO-330, a tool is a computer program, or a functional part of one, used to help develop, transform, test, analyze, produce or modify another program, its data or its documentation. Examples are code generators, compilers, test tools and modification-management tools. DO-330 sets out the process and objectives for qualifying such tools. It is written so that tool developers without a background in DO-178C or DO-278A guidance can apply it.

## Claims checked

| Claim (from the record) | Verdict | Basis |
|---|---|---|
| DO-330 dates from 2011. | VERIFIED | RTCA store: issued 2011-12-13 by SC-205. |
| It governs tool qualification. | VERIFIED | The RTCA store description says: "This document explains the process and objectives for qualifying tools." FTP1055 locates the criteria for whether a tool needs qualification in DO-178C subsection 12.2, and the qualification guidance in DO-330. |
| It defines tool qualification levels TQL-1 to TQL-5. | VERIFIED | FTP1015 contrasts TQL-1, 2, 3 and 4 with TQL-5 for the objectives in DO-330 Annex A Table T-10. FTP1009 distinguishes TQL-1 through TQL-4 from TQL-5. FTP1055 calls TQL-1 the highest level, the one to which the full set of DO-330 objectives applies. |

## Notes for the record

These notes bear on mapping gzkit gating validators to qualified tools.

- FTP1055 (non-authoritative) summarises when qualification is needed. A tool needs qualification only when it eliminates, reduces or automates a DO-178C process and its output is not verified.
- FTP1055 also sorts tools into criteria. A tool whose output could put an error into the software is tool criteria 1. A tool that could only fail to detect an error is criteria 2 or 3.
- A gating validator is a verification-type tool, so in this analogy it is a criteria 2 or 3 tool. FTP1055 says most such tools are TQL-5. A TQL-5 tool must meet 14 DO-330 objectives, against 76 for TQL-1. It is qualified as a black box, with no artifacts about how it was developed.
- The table that assigns a TQL from the tool criteria and the software level is in the purchased text (DO-178C 12.2 and DO-330). It was not publicly inspectable, so its clause number is unverified.
- FTP1041 gives the FAS reading of DO-330 Annex A Table T-0 objective 5. At TQL-1 and TQL-2, whoever wrote the tool's operational verification and validation cases should not be the person who developed the tool.
