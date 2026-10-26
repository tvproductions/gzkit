# Verification of inventory-maritime.md quotes

Checked 2026-10-25. Subject: `docs/rnd/contractor-kit/sources/inventory-maritime.md` (182 lines, not edited).

Scripts and data (scratchpad, prefixed `maritime_` because other verifiers share this directory):

- `scratchpad/maritime_verify_quotes.py`: extracts every `"…"` string with its row and citation. It normalizes whitespace and curly/straight quotes on both sides and splits on `…`. Each fragment must appear in order, with no more than 1500 characters between fragments. It searches all eight source files and records the file, the line, the nearest heading, the 160 characters before the match and the omitted text for every elision.
- `scratchpad/maritime_results.json`, `maritime_review.txt`: per-quote output.
- `scratchpad/maritime_compare.py`: compares the saved files with the re-fetched text.
- `scratchpad/maritime_fetch/`: the re-fetched eCFR XML.

## Summary counts

| Measure | Count |
|---|---|
| Quoted strings in the inventory (excluding the bare `"…"` on line 3) | **185** |
| Matched character-for-character in a source file, after whitespace and quote-style normalization only | **179** |
| ...of these, at the cited section and paragraph (checked by hand from the match context) | **179** |
| ...of these, with no elision problem | **176** |
| Quotes with a meaning-changing elision | **3** |
| Strings that are not quotes of a source (mentions or absence claims), checked separately | **6** |
| MISQUOTE / WRONG-SOURCE / WRONG-SECTION / PARAPHRASE | **0 / 0 / 0 / 0** |

How the 6 non-source strings came out:

- Line 26, `"DFARS 252.217-7001 (Surety bonds?)"`, quotes the R&D brief, not a source. The inventory's correction holds. The source reads "252.217-7001 Surge option." and "As prescribed in 217.208-70(b)" (dfars-252-217-master-agreement-clauses.md L392–394). 7001 is not in the 217.7104(a) list (dfars-217-71-master-agreement.md L111–125). "252.217-7008 Bonds." is at L101.
- Line 36, `"third party"`: the only occurrence in the sources, case-insensitive, is "Third party examiner" (ship-repair.md L29). The claim holds.
- Line 42, `"Vessel's commander"`: a case variant of "vessel's commander" (ship-repair.md L105, 252.217-7010(d)(1)). No definition exists. The claim holds.
- Line 182, `"restore"`, `"restorer"`, `"return to service"`: none occurs in any source file, case-insensitive. The absence claim holds. The nearest forms are "restoring" (1915.89(i)(1)) and "return to normal operating condition" (App. A).

## Re-fetch comparison

Every document came back from the eCFR versioner API at the dates in the inventory header, with HTTP 200 (the endpoint needs `--compressed`; without it, it returns 406). I re-fetched all six files the inventory author fetched, and also the eight sections behind ship-repair.md and dfars-252-217-7003-changes.md. The method: strip the XML tags, normalize whitespace, then check (a) that every body line of the saved file appears in the fetched text and (b), for full-section files, that every fetched paragraph appears in the saved file.

| Saved file | Body lines found exactly in fetched text | Fetched paragraphs missing from saved |
|---|---|---|
| dfars-217-71-master-agreement.md | 68 / 68 | 0 |
| far-2-101-46-101-definitions.md | 27 / 28 (the one miss is the author's label "Selected entries (verbatim, in source order):") | 0 for 46.101 (2.101 is a declared excerpt) |
| osha-1915-80-definitions.md | 46 / 46 | 0 |
| osha-1915-11-definitions.md | 37 / 37 | 0 |
| uscg-46-cfr-70-10-1-definitions.md | 5 / 5 | n/a (declared excerpt) |
| dfars-252-217-master-agreement-clauses.md (13 sections) | 183 / 185 (both misses are the author's provenance sentences) | 0 |
| dfars-252-217-7003-changes.md | 18 / 18 | 0 |
| ship-repair.md (71.50-1, 71.55-1, 71.55-5, 71.60-1, 252.217-7005, -7010, -7015, 1915.89) | 267 / 269 (both misses are the author's provenance paragraphs) | 0 (the only flagged items were the 8 section headings, which are rendered as `###` lines that the comparison skipped) |

**Result: the saved files are faithful.** No source word differs, and there are no whitespace-only differences. Every regulatory paragraph in the full-section files is present. The FAR 2.101 excerpt does not hide a definition of "Contractor" or "Government" either: the full re-fetched 2.101 has neither.

## Failure table

| Row label (inventory line) | Quote as written | What the source says (file, line) | Verdict |
|---|---|---|---|
| Lockout/tags-plus coordinator (L49) | "Lockout/tags-plus coordinator. An employee whom the employer designates to coordinate and oversee all lockout and tags-plus applications … The lockout/tags-plus coordinator also maintains the lockout/tags-plus log." | "…coordinate and oversee all lockout and tags-plus applications **on vessels or vessel sections and at landside work areas when employees are performing multiple servicing operations on the same machinery, equipment, or systems at the same time, and when employees are servicing multiple machinery, equipment, or systems on the same vessel or vessel section at the same time.** The lockout/tags-plus coordinator also maintains the lockout/tags-plus log." (osha-1915-80-definitions.md L49, 1915.80(b)(15)) | MEANING-CHANGING-ELISION: the elision removes the trigger condition. As quoted, the coordinator oversees *all* applications without condition. The source limits the role to multiple, simultaneous servicing (matching 1915.89(c)(7)(i), ship-repair.md L189–193). |
| Senior officer present, "Duty" column (L51) | "It shall be the responsibility of the senior officer present to secure copies of certificates … to maintain a safe condition on the vessel by full observance of all qualifications and requirements listed by the marine chemist in the certificate." (71.60-1(d)) | "It shall be the responsibility of the senior officer present to secure copies of certificates issued by the certified marine chemist or such person authorized by the Officer in Charge, Marine Inspection. **It shall be the responsibility of the senior officer present, insofar as the persons under his control are concerned,** to maintain a safe condition…" (ship-repair.md L81) | MEANING-CHANGING-ELISION: the ellipsis joins two separate duties across a sentence break into one, which reads as if securing copies served to maintain a safe condition. It also drops the limit "insofar as the persons under his control are concerned". |
| Termination for default (L139) | "…terminate the whole or any part of a job order if the Contractor fails to— (1) Make delivery … (2) Make progress, so as to endanger performance of the job order; or (3) Perform any of the other provisions of this agreement or a job order." | "(1) Make delivery **of the supplies or to perform the services within the time specified in a job order or any extension;**" (dfars-252-217-master-agreement-clauses.md L130, 252.217-7009(a)(1)) | MEANING-CHANGING-ELISION: the omission drops the timeliness condition ("within the time specified … or any extension") and the alternative ground "perform the services". As quoted, the ground reads as failure to deliver at all, not failure to deliver on time. |

## Readings that misstate their quotes

1. **L179 (first bullet):** "the repairer runs its own inspection system and the owner (Government) checks it 'at any time' (252.217-7005(c), (c)(3))." The source gives the Government's "at any time" right over a different object: "The Government may inspect and test **all material and workmanship** at any time during the Contractor's performance of the work." (ship-repair.md L95, 7005(c)). It says nothing about checking the contractor's inspection system. That system is also conditional: "As specified in the job order…" ((c)(3)). The reading merges the two paragraphs.
2. **L180 (second bullet):** "The repairer's authorized employee removes the lock and starts up (1915.89(i), (j))." This is stated without qualification. The Notes to 1915.89(i) and (j) (ship-repair.md L333, L349) cover the case where the Navy ship's force removes the systems or controls startup and "the employer is prohibited from starting up the machinery, equipment, or system". The inventory's own row at L174 quotes that Note. The reading is true only outside that case.

All other `[reading]` items (L35, L36, L91, L181, L182) agree with their quotes and sources.

## Minor observations (not failures)

- Some leading or trailing truncations carry no ellipsis. The header promises ellipses only for omissions *inside* a passage, so these are within the stated convention, but some drop context:
  - L34 "Selection" and L148 "Certifier selected by the regulator, on the parties' recommendation" begin after "however, if the services of such certified marine chemist are not reasonably available," (71.60-1(c)(1)). OCMI selection is a fallback, which the L148 row label does not convey. The L179 reading states the fallback correctly.
  - L65 begins after the triggers "Whenever the Contracting Officer determines that a vessel, its cargo or stores, would be endangered by delay, or … military necessity…" (252.217-7004(b)). The row label "(emergency)" covers this.
  - L86 ends the audit-report list at (iv) and omits (v) and (vi) (1915.89(q)(4)).
- L36 (Third party examiner) elides items (1)–(4) of a conjunctive list. The ellipsis is shown and the meaning is not changed, but an entity must meet all five items.
- L158 elides "in protecting employees as removal of the system by the authorized employee who applied it. After meeting these requirements, the employer shall do the following in sequence:" (1915.89(i)(3)). This leaves "at least as effective …" without its comparison, and hides that the employer is the actor in (i)–(iii). It is not meaning-changing.
