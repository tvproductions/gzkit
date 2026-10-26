# Quote verification: inventory-navy-jfmm-v5.md

- Subject: `docs/rnd/contractor-kit/sources/inventory-navy-jfmm-v5.md` (not edited)
- Sources: `scratchpad/src/jfmm5.txt` (pdftotext -layout, 28,385 lines); `navy-jfmm-vol5-glossary.md`; the PDF itself, for the Ch. 3 App. A matrix (`pdftotext -raw`, p. 129) and the Ch. 2 App. B flowchart (rendered p. 113)
- Scripts (all in the scratchpad):
  - `verify_jfmm5.py` extracts quotes, handling nested quotes. It normalises curly quotes, whitespace, line-end hyphens and page furniture: every `CHG n` header, date headers including `07 Nov 2023` and `16 Oct 2019`, and `V-x-y-n` footers. It treats `…`, `...` and `[...]` as ordered gaps, with a 2,500-char window. It runs a strict pass, then a loose alphanumeric pass, and then a pass over the glossary pages with the left (term) column stripped.
  - `section_check.py` maps each hit to its Part, chapter and appendix (from the page footer), its nearest numbered paragraph heading, its subparagraph letter and its `(n)` item, and compares that location with the cited paragraph.
  - `elisions.py` prints the text each ellipsis removed. `edges.py` prints the rest of the sentence on both sides of each quote.
  - Raw results are in `verify_raw.json` and `verify_raw_sec.json`, `elisions.txt` and `edges.txt`.

## Counts

| | n |
|---|---|
| Quoted strings extracted (records) | 632 |
| Not source quotes, excluded: L12 header `"…"`; L506 `"restorer who reconnects"` (R&D term in a [reading], not JFMM text) | 2 |
| L203: one quote split into 5 records by a malformed `""Replace` (doubled opening quote) | -4 |
| **Source quotes checked** | **626** |
| Matched strictly by script (incl. glossary column pass) | 616 |
| Hand-checked after script miss / loose-only (L49, 120, 124, 149, 161, 195, 203, 227, 236, 260) | 10 |
| **Wording verified verbatim** (script + hand) | **623** |
| Wording failures (MISQUOTE) | 3 |
| Wording verified, but an omission/truncation changes meaning (MEANING-CHANGING-ELISION) | 36 (14 high, 12 medium, 10 low) |
| **Verified clean (verbatim, correct section, no meaning-changing cut)** | **587** |
| WRONG-SECTION | 0 confirmed |
| PARAPHRASE | 0 |

Section check: 619 matched quotes were located. All automated flags (10 numeric, 6 letter-level) were false positives from my side and were cleared by hand. They came from in-text cross-references parsed as headings, "a, .b"-style comma cites, glossary vs chapter multi-cites, and the `10.6.1.3–.4` range. I checked 41 `(n)`-level cites and QA-form `Blk` cites at item level: no mismatch. Appendix `¶n` cites were checked to appendix level only.

Hand-verified script misses, all OK (layout artifacts, not inventory errors):
- L124: QAS prerequisite cell (matrix columns).
- L149 and L236: App. B flowchart labels. The path order in L149 matches the arrows on the rendered page.
- L195: DFS message fields.
- L227: QA form 1 face.
- L203: the Replace/re-install/repair text, source 7498–7503.
- The Part III App. A glossary entries (L527, 536, 549, 551×2): the two-column layout split them, and they matched after the column strip.
- L92, 160, 276, 327, 572: line-end hyphenation only.

## Failure table

### MISQUOTE (wording not in source)

| Inv. line / row | Quote as written | Source actually says (line) | Verdict |
|---|---|---|---|
| L120, Qualification ladder (I-3 App. A) | "302 Controlled Material Petty Officer or Controlled Material Handler … 303 Quality Assurance Inspector (QAI) [prerequisite 301 Craftsman] …" | Watchstation cell reads "302 Controlled Material Petty / Handler (CMPO or CMH)" (5934–5935; same in `-raw` extraction). "Officer or Controlled Material" is not in the 302 title; it was imported from the 105 fundamentals cell. The 303 prerequisites are "301 Craftsman" **and** "302 Controlled Material Petty Officer or Controlled Material Handler (CMPO or CMH)**" (5937–5940); the bracket shows only 301. | MISQUOTE + MEANING-CHANGING-ELISION |
| L260, row 6e (I-2.3.3.1.e) | "LWC Supervisor or Division Officer may add materials after the FWP is open…" | "Lead Work Center (LWC) Supervisor or Division Officer may add materials…" (4529–4532). The string "LWC Supervisor or" does not occur; the quote silently contracts "(LWC) Supervisor". | MISQUOTE (minor) |
| L49, ISIC (I-1.5.a) | "ISICs are responsible to the TYCOM for the following: a. Organize and implement a QA program…" | A 5-line NOTE ("(SUBMARINES ONLY) WHEN ISIC FUNCTIONS ARE DELEGATED…") sits between "for the following:" and "a." (2534–2541). It is omitted with no ellipsis, which breaks the inventory's own rule. | MISQUOTE (unmarked omission; meaning intact) |

### MEANING-CHANGING-ELISION: high (cuts a not / except / unless / excluding, or a limiting condition, so the quoted rule reads broader than the source)

| Inv. line / row | Quote as written | What was cut (source line) | Verdict |
|---|---|---|---|
| L29, Scope (outside organizations) (I-FWD 1.2.a) | "…and to outside organizations (shipyards, contractors, Regional Maintenance Centers) performing work on ships." | The next sentence of the same subpara: "This volume does not currently apply to outside organizations (shipyards, contractors) when an availability is conducted in a depot facility and the contract specifies the use of other specifications." (732–733). The row is about contractors and drops the contractor exclusion. | MEANING-CHANGING-ELISION (truncation) |
| L48, TYCOM trials restriction (I-1.4.m(1)) | "…TYCOM approval to operate the FBW-SCS to previously authorized conditions is granted" | Sentence continues ", unless specifically addressed in the Sea Trial agenda or as stated in Departure From Specifications, Deviations or Waivers." (2517–2519). It is cut mid-sentence with no ellipsis. | MEANING-CHANGING-ELISION |
| L210, Tool and Material Accountability Log (I-5.4.5.1.d) | "A formal written record must be maintained for all material … taken inside the physical boundary …" | The second ellipsis removes the limiting clause "that are small enough to fit inside the material openings in the hardware and do not have lanyards attached." (7143). "All material" is broader than the source. | MEANING-CHANGING-ELISION |
| L347, Adjudicate before operating (I-8.2.3) | "…must be adjudicated prior to ship's underway operations … All submarine DFS … except: a. … turned over to the Shipyard …" | The first ellipsis cuts "except when executing berth shifts that do not involve open ocean movements (i.e. movements within a harbor or river)." (12805). The second cuts the condition of exception a: "A ship is in a Chief of Naval Operations availability and the affected system or component has been" (12808). | MEANING-CHANGING-ELISION |
| L359, Major (periodicity) (I-8.2.5.j) | "Nonconformance requests that result in a change of the URO MRC inspection periodicity …, a change…require NAVSEA approval." | The ellipsis cuts "(not authorized by the MRC)" (12946). Only changes not authorized by the MRC need NAVSEA approval. | MEANING-CHANGING-ELISION |
| L362, Minor (test alternatives) (I-8.2.6.c) | "Any condition that requires at sea operations to certify planned maintenance or repairs" | Sentence continues "excluding structural watertight integrity testing except as previously discussed." (13093–13094). | MEANING-CHANGING-ELISION |
| L408, Expiry expected (I-8.3.9.a) | "(1) Nonconformances must not be permitted to expire for equipment or systems that are in operation or will be operated during the availability" | Continues "except:" followed by a list of exceptions (13438). The framing sentence "It is acceptable for nonconformances to expire while the ship … is in a scheduled availability except as listed here:" is also elided. | MEANING-CHANGING-ELISION |
| L408 (I-8.3.9.b) | "(Submarines, DSS and SOC assets only) Must not get underway with expired nonconformances" | Continues "unless the submarine, DSS or SOC asset is repositioned by tug or similar craft." (13448–13449). | MEANING-CHANGING-ELISION |
| L532, User Activity (III-1.2.3.l) | "The User Activity must issue the DSS certification continuity report before manned operations" | Continues "(Not applicable when in pursuit of certification or reinstatement of certification per reference (a) paragraph 3.7.4.)" (24903–24904). | MEANING-CHANGING-ELISION |
| L317, Post-closeout audit (I-9.3.1.b(2)(a)) | "Perform a closeout vertical audit of all Controlled Work Packages (CWP) on a quarterly basis, except RECs" | Continues ", when not in a Chief of Naval Operations availability." (14002–14003). | MEANING-CHANGING-ELISION |
| L272, Change: attachment (I-2.3.7.4) | "it can be accomplished by using an attachment to the FWP…" | The preceding precondition is dropped: "If additional work must be added to the FWP and it is relatively extensive but does not require a change in plant conditions or work boundary," (4979–4980). Row L176 quotes it correctly. | MEANING-CHANGING-ELISION |
| L295, REC revision triggers (I-5.6.4.b(14)) | "(a) Change in work boundaries … (b) Change in NDT or test requirements … This does not include a DFS for unaccomplished testing. … (c) Scope of work changes" | It keeps one exception but elides two others: "An MCR/REC revision is not required to delete undisturbed joints." (7538–7539) and "An MCR/REC revision is not required for NDT incidental to minor repairs…" (7545–7547). | MEANING-CHANGING-ELISION |
| L436, Acceptance testing is a critical inspection (I-5.4.3.a(1)) | "Inspections performed for all acceptance testing (…) for certification of work completed under a Controlled Work Package (CWP)." | Item (1) continues "(Nuclear and non-nuclear manually operated valves which have adjustable packing do not require certification by an independent inspector.)" (6997–6999). | MEANING-CHANGING-ELISION |
| L357, Major examples (I-8.2.5.c) | "c. Failure to meet all applicable standards for major repairs …" | The ellipsis cuts "unless other alternatives are authorized by this volume." (12897–12898). | MEANING-CHANGING-ELISION |

### MEANING-CHANGING-ELISION: medium (cuts an applicability, platform or scope condition)

| Inv. line / row | Quote as written | What was cut (source line) | Verdict |
|---|---|---|---|
| L303, row 23i (I-5.6.8.b) | "Prior to the ship's underway after an FMA availability … the FMA Commanding Officer will issue a letter report…" | The ellipsis cuts ", refit or inport period when SUBSAFE, SFCC work was performed," (7728–7729). The letter is required only when SUBSAFE/SFCC work was done. | MEANING-CHANGING-ELISION |
| L303 (I-5.6.8.c) | "Prior to ship's underway, activities other than FMAs … will issue a letter report to the submarine" | The ellipsis cuts "which perform SUBSAFE or SFCC maintenance on submarines" (7734–7735). It applies to all non-FMA activities. | MEANING-CHANGING-ELISION |
| L207, FMA Certification Report (I-5.6.8.b) | "the FMA Commanding Officer will issue a letter report…" | The same leading condition is dropped (7728–7729). | MEANING-CHANGING-ELISION |
| L53, ISIC (DFS) (I-1.5.g) | "(3) Approve or disapprove DFS requests. … (9) Maintain files…" | The ellipsis cuts "(4) Obtain TYCOM or NAVSEA approval of DFS when required by the appropriate TYCOM, NAVSEA directive, technical specification or manual." (2576–2577). The ISIC then reads as the final approver. The parallel TYCOM row L46 keeps its (4). | MEANING-CHANGING-ELISION |
| L47, TYCOM return to service (I-1.4.m(2)) | "Following verification … is satisfactory, … issue a message…" | The second ellipsis cuts a precondition: "and upon confirmation that FBW-SCS certification was not affected for those portions of ship FBW-SCS not affected by the ISEA or activity performing the work," (2523–2525). | MEANING-CHANGING-ELISION |
| L171, CWP/REC serial numbers (I-2.3.5.a) | "the ship's QAO will issue the CWP or REC numbers sequentially for entry in Block 4 of the ship's QA form 9." | The scope prefix is dropped: "For controlled (i.e., Level I, Nuclear, Scope of Certification, SFCC) or SUBSAFE work to be performed by Ship's Force only," (4812–4813). The ellipsis also removes the repair-activity cases. | MEANING-CHANGING-ELISION |
| L246, row 3 (I-2.3.5.a) | Same quote | Same prefix dropped (4812–4813). | MEANING-CHANGING-ELISION |
| L54, ISIC pre-underway (I-1.5.q) | "the ISIC QAO must complete a QA Pre-Underway Checklist." | Dropped: "(Submarines only) Prior to submerged underway operations when submarines are in a port with an ISIC, or when a submarine is in an availability such as…" (2722–2725). | MEANING-CHANGING-ELISION |
| L51, ISIC work screening (I-1.5.c) | "Organize and implement a work request screening process…" | Dropped: "(Submarines, Aircraft Carriers, Readiness Support Groups and RMCs only)" (2546). | MEANING-CHANGING-ELISION |
| L235, row 0 (I-1.5.c) | Same | Same (2546). | MEANING-CHANGING-ELISION |
| L221, QA-12 Block 7B | "The Approval Activity will fill in the "TEMPORARILY APPROVED UNTIL DATE"" | Continues "for non-Electronic Departure from Specification departures. Electronic Departures … will automatically populate…" (17136–17138). | MEANING-CHANGING-ELISION |
| L362, Minor (test alternatives) (I-8.2.6.b) | "Any condition which is associated with exemptions or alternatives to non-nuclear retest requirements in section 7.4 of part I, chapter 7" | Continues ", of this volume on testing, except where noted." (13067–13068). | MEANING-CHANGING-ELISION |

### MEANING-CHANGING-ELISION: low (qualifier, example exception or extra trigger cut; quoted rule still essentially true)

| Inv. line / row | Quote as written (start) | What was cut (source line) | Verdict |
|---|---|---|---|
| L306, row 25b (I-7.1.2.b) | "…will be work center or bench tested and inspected prior to installation" | ", when required." (11199–11200) | MEANING-CHANGING-ELISION |
| L182, QA form 34 (I-1.6.12.ac) | "Retain any QA form 34 generated…" | Prefix "(Submarines only)" (3120) | MEANING-CHANGING-ELISION |
| L211, TMDE on the record (I-5.2.1) | "the type of equipment, range, serial numbers…" | Prefix "When inspections or measurements using TMDE are performed with the results documented on a Quality Assurance (QA) form," (6844–6845) | MEANING-CHANGING-ELISION |
| L71 and L282, QAO close-out (I-1.6.12.g) | "Review and close out all TWDs … prior to startup or getting underway." | "(e.g., if the work is on a spare component it may not be necessary to close the TWD)" (3048) | MEANING-CHANGING-ELISION (2 quotes) |
| L190, Qualification file (I-10.5.4) | "b. Qualification test results. …" | "For Oxygen Clean qualifications, this entry is not required." (15127) | MEANING-CHANGING-ELISION |
| L576, Survey card categories (III-9.3.2.1.d) | "Category II. Findings which, while not mandatory for resolution …, identify systemic weaknesses" | "to obtain or maintain certification" (27169). Without it, "not mandatory" reads as absolute, and the source adds "These deficiencies should be resolved in a timely manner." | MEANING-CHANGING-ELISION |
| L483, Sampling (I-9 App. D ¶2 NOTE) | "ISICS SHOULD GENERALLY REVIEW 20%…" | Prefix "WHERE NOT PREVIOUSLY DEFINED BY REFERENCE (A)," (14569) | MEANING-CHANGING-ELISION |
| L72, QAS (I-1.6.12.ae) | "Verify an active Job Control Number exists … at the completion of all scheduled Fleet Maintenance Activity Availabilities" | Cut mid-sentence with no ellipsis: ", major or minor, CNO availabilities or at least quarterly and maintain an auditable record…" (3127–3128) | MEANING-CHANGING-ELISION |
| L118, CMPO/CMH (I-3.4.8.c) | "commands must have a method to ensure CMPOs or CMHs do not handle material excluded from their qualification." | Prefix "Activities may modify the qualification card … If this is done," (5798–5799) | MEANING-CHANGING-ELISION |

## [reading] passages that misstate their quote

| Inv. line | Problem |
|---|---|
| L124 | It says the inspector "is a qualified craftsman plus inspection fundamentals". The source matrix also lists **302 CMPO/CMH** as a 303 QAI prerequisite, marked ** "Command Specific" (5937–5940, 5952–5954). The reading rests on the L120 omission. Its second claim, that the QAS prerequisite cell reads "305 Quality Assurance Inspector (QAI)", is accurate. The 308 QAS row repeats it. |
| L488 | (a) It presents "verification" (V, craftsman) and "inspection" (I, inspector) as distinct acts. But the sentence it then quotes as the meaning of "independent" (I-5.4.3, 6973–6975) says a critical inspection "requires **verification** by a separate individual, other than the craftsman, qualified as an inspector". The source uses "verification" for the inspector's act too. (b) That sentence defines "Critical Inspections", not "independent". The tie to "independent" comes from the NOTE that follows ("MINIMUM REQUIREMENTS FOR USAGE OF AN INDEPENDENT INSPECTOR", 6980–6981). It is a fair inference but is stated as a definition. |
| L506 | `"restorer who reconnects"` is in quotation marks but is not JFMM text; it is the R&D's own term. Its other two quotes are verbatim and in place (13.2.c, 24039; 12.4.9, 23998–23999). The "a worker who was not involved in the disconnection" phrase sits inside an "e.g." test of marking clarity. The source does not require such a worker to do the reconnection; the reading's wording ("identifiable by") is consistent with that. The claim that 12.4.9 is the only Part I organisational-independence assignment holds against every "independent" occurrence in Part I (lines < 24200). |

## Notes (not counted as failures)

- L161, margin symbols (I-2.3.3.1.j(3)): the words are verbatim, but the list enumerators (b)–(h) are dropped without marking (4640–4654).
- L203: the cell opens with a doubled `""Replace"`. The text is verbatim (7499–7503).
- L120: the bracketed column labels are disclosed ("bracketed column labels added").
- L291: the quote spans QA-9 Blk 19 correctly. My matcher's first hit landed on Blk 18's identical opening, and I hand-confirmed Blk 19.
- Many verbatim quotes end at a sentence boundary where the next sentence carries a related rule. The edge scan (`edges.txt`) flagged 93. Only those above change the meaning of what is quoted. The rest, e.g. L101, L204 and L535, add rules without negating the quote.
