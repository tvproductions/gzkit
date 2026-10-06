# US Government Sources Index

Research date: 2026-10-06. Persona: main-session — craftsperson, governance-aware, whole-file-reasoning, direct. Provenance: R&D run `renewing-vows`. This is an index of the US-government source files in this directory, not a skill implementation or operator ruling.

## Retrieval conditions on 2026-10-06

- The eCFR's human-readable pages redirected automated requests to a request-access page, which was not used. The four CFR files were read through the eCFR public API, each passage through two endpoints.
- faa.gov, jcs.mil and doctrine.af.mil returned HTTP 403 to every automated request. Four files therefore record NOT VERIFIED throughout, with the official URLs and labelled secondhand edition evidence: AC 121-22, JO 7110.65, JP 3-30 and JP 3-60. Their header's last sentence says the official text was not reachable, not "Read live".
- AC 120-82 was read from an unofficial facsimile copy, because the official faa.gov copy returned HTTP 403. Its title and date are anchored by Pub. L. 111-216 § 201(a)(5) (govinfo.gov) and 14 CFR 13.401 (eCFR). Its excerpts should be re-checked against the official PDF before doctrine cites them.
- MIL-HDBK-61 was read from the official ASSIST QuickSearch copy.

## Files

| File | Title | Edition/date confirmed | URL | VERIFIED | NOT VERIFIED | CONTRADICTED |
| --- | --- | --- | --- | --- | --- | --- |
| `us-gov-14cfr-part5-sms.md` | 14 CFR Part 5, Safety Management Systems | Yes: eCFR up to date as of 2026-10-02 (as amended by Amdt. 5-2, 89 FR 33104, Apr. 26, 2024) | <https://www.ecfr.gov/current/title-14/part-5> | 6 | 1 | 0 |
| `us-gov-14cfr-43-9.md` | 14 CFR §§ 43.5, 43.7 and 43.9 (with § 121.709) | Yes: eCFR up to date as of 2026-10-02 | <https://www.ecfr.gov/current/title-14/section-43.9> | 5 | 2 | 0 |
| `us-gov-14cfr-part119.md` | 14 CFR Part 119, §§ 119.5, 119.7, 119.49 | Yes: eCFR up to date as of 2026-10-02 | <https://www.ecfr.gov/current/title-14/part-119> | 2 | 0 | 0 |
| `us-gov-14cfr-121-subpart-L.md` | 14 CFR Part 121 Subpart L (with § 1.2) | Yes: eCFR up to date as of 2026-10-02 | <https://www.ecfr.gov/current/title-14/part-121/subpart-L> | 3 | 1 | 0 |
| `us-gov-faa-ac-120-82-foqa.md` | FAA AC 120-82, Flight Operational Quality Assurance | Date 4/12/04, read from an unofficial facsimile and corroborated by Pub. L. 111-216 § 201(a)(5). Current status not confirmed. | <https://www.faa.gov/regulations_policies/advisory_circulars/index.cfm/go/document.information/documentID/23227> (HTTP 403) | 5 | 1 | 0 |
| `us-gov-faa-ac-121-22-mrb.md` | FAA AC 121-22, Maintenance Review Board | No. Secondhand: AC 121-22D (2024-05-31) current, 121-22C cancelled. | <https://www.faa.gov/regulations_policies/advisory_circulars/index.cfm/go/document.information/documentID/1042771> (HTTP 403) | 0 | 4 | 0 |
| `us-gov-faa-jo-7110-65-position-relief.md` | FAA Order JO 7110.65, Air Traffic Control (position relief) | No. Secondhand: JO 7110.65BB, changes dated through 7-9-26. | <https://www.faa.gov/air_traffic/publications/atpubs/atc_html/> (HTTP 403) | 0 | 5 | 0 |
| `us-gov-jp-3-30.md` | JP 3-30, Joint Air Operations | No. Secondhand: 25 July 2019. | <https://www.jcs.mil/Doctrine/Joint-Doctrine-Pubs/3-0-Operations-Series/> (HTTP 403) | 0 | 5 | 0 |
| `us-gov-jp-3-60.md` | JP 3-60, Joint Targeting | No. Secondhand: 28 September 2018; a 2026 edition is possible. | <https://www.jcs.mil/Doctrine/Joint-Doctrine-Pubs/3-0-Operations-Series/> (HTTP 403) | 0 | 7 | 0 |
| `us-gov-mil-hdbk-61.md` | MIL-HDBK-61B w/Change 1, Configuration Management Guidance | Yes: 15 August 2025, Active (ASSIST) | <https://quicksearch.dla.mil/qsDocDetails.aspx?ident_number=202239> | 7 | 0 | 0 |

Totals: 28 VERIFIED, 26 NOT VERIFIED, 0 CONTRADICTED.
