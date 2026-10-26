# Quote verification: inventory-navy-tum.md against tum.txt

- Inventory: `docs/rnd/contractor-kit/sources/inventory-navy-tum.md` (not edited)
- Source: `scratchpad/src/tum.txt` (pdftotext -layout, 4,521 lines)
- Scripts: `scratchpad/verify_tum.py` (matcher), `scratchpad/sections.py` (section labeller), `scratchpad/ctx.py` (text that comes before a quote that starts mid-sentence). Raw results are in `results.json`, `results_last.json` and `sections.txt` in the same folder.

## Method

1. I extracted every `"…"` string from the inventory: 419 strings. The inventory has no curly double quotes.
2. Normalization was applied to both sides. Page header and footer lines were dropped (`S0400-AD-URM-010/TUM Rev level: 08`, bare page numbers, `X-n` page numbers). Whitespace was collapsed and lines joined. `- ` was folded to `-`, which fixes line-break hyphenation such as `tag- out`. Curly and straight single and double quotes were folded together, because the source prints `“RA Not Available”` where the inventory writes `'RA Not Available'`. En and em dashes were folded to `-`.
3. `...` is treated as a gap. Each fragment has to appear in order, at most 1,500 characters after the previous one. Every elided gap was printed and read.
4. Pass 1 matched against the full-width text. Pass 2 matched against a right-column-only stream, which handles the two- and three-column glossary and block-overview tables. Anything still unmatched was checked by hand against the layout.
5. Sections: each matched source line was labelled with its enclosing paragraph (numbered heading, then a./(1)/(a)). I compared that label with the inventory's cited section. I checked by hand every appendix cite, every multi-cite (for example "1.3.3.a(3); 1.6.3.b(2); D block 14; K TORS block 10") and every NOTE or block-number cite.
6. Elision: for every quote with `...`, and for every quote that starts mid-sentence (lower-case start or a leading `(`), I read the source text around it for a dropped condition, exception or scope.

## Summary counts

| Measure | Count |
|---|---|
| Quoted strings in the inventory | 419 |
| Exact match, pass 1 (full-width text) | 392 |
| Exact match, pass 2 (right column of the glossary and overview tables) | 20 |
| Matched by hand: layout or extraction artifact, wording supported by the source | 7 |
| **Text verified (words found in the source)** | **419 / 419** |
| MISQUOTE | 0 |
| PARAPHRASE presented as a quote | 0 |
| WRONG-SECTION | 0 |
| MEANING-CHANGING-ELISION (ellipsis or leading truncation drops a condition or scope) | 10 (6 material, 4 minor) |
| EXTRACTION-ARTIFACT (did not match mechanically, wording confirmed by hand) | 7 |
| **Quotes clean on text, section and meaning** | **409 / 419** |

Every cited section was confirmed, including App B glossary entries, D LIRS blocks 6/7/10/11/14/15/16/18/19/21, the K TORS overview blocks 4/10/11/23, the K Fig. K-1 note for block 5, the 1.8.6.c NOTE, the 1.9.1(.b) NOTE, the I 2.d NOTE, C 1/3.b/3.c/4/4.a–c, F 4.g/5.a/5.b, H 2–6, I 2/4, J 1–4, and K 3.b/3.g/3.h/5.b/5.d. The multi-cites also hold: 1.6.5.a(1) and 1.6.5.b(3) (L1090, L1146); 1.6.4.b(1) and 1.6.5.a(2) (L1015, L1095); 1.6.4.b(2) and 1.6.5.a(2)(a) (L1024, L1105); 1.8.5.d and K 5.e(2) (L1523, L3904); 1.3.3.a(3), 1.6.3.b(2), D block 14 and K TORS block 10 (L535, L897, L2062, L4069). The App B "Watch/Duty Officer" row's citation of "K TORS overview, block 23" is correct: the block's printed number is lost in the extraction, but the next row reads "when block 23 is signed" (L4174), and its title is "SIGNATURE OF WATCH OFFICER/DUTY OFFICER".

## Failure table

Row labels: "1.3" means section 1, row 3 of the inventory. "inv L" is the inventory line number. "tum L" is the tum.txt line number.

| # | Row / section label (inv L) | Quote as written (abridged) | What the source actually says (tum L) | Verdict |
|---|---|---|---|---|
| 1 | §1 row 3 AO, "May" column (inv 22), cited 1.7.4.b(6)(c) | "may authorize two persons to independently check the position of the specific valve" | "(c) When the actual position of a danger-tagged valve is in doubt, the Authorizing Officer, with specific permission from the responsible Ship's Force Department Head and from the RA Representative, when applicable, may authorize two persons…" (L1367–1370). Placed in the AO's powers with both the doubt trigger and the permission requirement removed. Rows 1.19 and 4a give the full sentence. | MEANING-CHANGING-ELISION |
| 2 | §1 row 3 AO, "May not" column (inv 22), cited 1.8.3 | "repositioning of components shall be accomplished after the Authorizing Officer has verified all tag clearance was accomplished correctly." | "If immediate re-positioning of components is required, then specific consideration must be given to the sequence… **Otherwise,** repositioning of components shall be accomplished after…" (L1477–1480). The rule covers only the case where immediate repositioning is not required. The quote makes it unconditional. 1.8.5.b allows immediate repositioning by the person clearing the tag. | MEANING-CHANGING-ELISION |
| 3 | §2 row 22 Tag-out Log (inv 91), cited 1.5.1.c | "a separate tag-out log for each propulsion plant shall be maintained in addition to other ship's tag-out logs." | "c. **On nuclear-powered ships,** a separate tag-out log for each propulsion plant shall be maintained…" (L631–632). The nuclear-only scope is dropped. The same scope applies to row 1.5's "Is administered by the Watch/Duty Officer." (1.5.1.c(1), L633), which the inventory presents without the qualifier. | MEANING-CHANGING-ELISION |
| 4 | §1 row 20 Two operators (inv 39), cited 1.6.4.a(5)(b) | "a formal valve lineup (or equivalent) must be performed to ensure that two operators verify and document the valve's position and torque…" | "**If the locking device will not allow stem movement,** a formal valve lineup (or equivalent) must be performed…" (L991–994). The sentence before says that when the device allows stem movement, "the poster may proceed" without the two-operator lineup. The condition is dropped. | MEANING-CHANGING-ELISION |
| 5 | §4a Independence (inv 207), cited 1.8.5.d | "the tag may be destroyed ... following an independent verification that the correct tag has been cleared. This independent verification shall be performed by another person assigned by the Authorizing Officer." | "All tags should be returned immediately to the Authorizing Officer. **If a tag is in a location that prevents returning the tag… such as a radiological or hazardous material containment,** the tag may be destroyed **and disposed of in the appropriate manner within the containment** following an independent verification…" (L1521–1526). The leading condition and the elided phrase together carry the only containment limit. As written, the quote reads as a general destroy-after-verification rule. Row 1.17 is fine: it keeps "within the containment" and its label names the condition. | MEANING-CHANGING-ELISION |
| 6 | §4c Removal by someone other than the applier (inv 239), cited 1.8.4.a | "the Authorizing Officer may authorize clearing the tag by marking the Clearance Authorized Repair Activity block on the TRS as 'RA Not Available'." | "**In situations where the RA Representative is no longer available (i.e., RA has completed work and left the geographical area or the ship has departed)** the Authorizing Officer may authorize…" (L1497–1500). In a table about removal authority, the quote reads as a general AO override of the RA co-signature. (Row 1.3 carries the same quote under the gloss "Without the RA:", which is broader than the source's "no longer available (i.e., …)". Row 3.50 quotes it in full.) | MEANING-CHANGING-ELISION |
| 7 | §3 row 27 Filed active (inv 152), cited 1.6.6.c | "The THS and LIRS ... are then filed in the active section of the appropriate tag-out log." | "The THS and LIRS **(if not using electronic signatures**, the electronic system does not support the use of the THS for RA Witness or to document multiple RA's witnessing shared tags) are then filed…" (L1177–1179). The ellipsis removes the condition on filing the LIRS. | MEANING-CHANGING-ELISION (minor) |
| 8 | §3 row 57 Completion and filing cleared (inv 182), cited 1.8.7.a | "…(2) File the completed LIRS ... in the cleared section of the tag-out log binder…" | "(2) File the completed LIRS **(if not using electronic signatures)** in the cleared section…" (L1554–1555). Same dropped condition as #7. | MEANING-CHANGING-ELISION (minor) |
| 9 | §3 row 30 Certified line item: revalidation (inv 155), cited 1.6.8 | "certified tag-outs may be invalidated due to system design changes and temporary systems used." | "**During CNO-scheduled availabilities or for specific systems affected by complex evolutions (e.g., system flushes),** certified tag-outs may be invalidated…" (L1196–1198). The scope is dropped. | MEANING-CHANGING-ELISION (minor) |
| 10 | §1 row 36 CTE, "May" column (inv 55), cited H 5.b(2) | "the CTE should have responsible representatives of the shipyard conduct checks of tags and labels and audits of the tag-out log in addition to…" | "(2) **When considered appropriate,** the CTE should have responsible representatives…" (L3322–3324). A discretionary provision reads as a standing one. | MEANING-CHANGING-ELISION (minor) |
| 11 | §2 row 14 LIRS block header (inv 83) | "Work Necessary to Clear Tag(s) (Including Tests)" | Fig. 1 prints "WORK NECESSARY TO CLEAR TAG(S) (INCLUDING TEST)" (L1978). The block-7 overview prints "WORK NECESSARY TO / CLEAR TAG(S) / (INCLUDING TESTS)" stacked in a narrow column (L2039–2041). The wording is supported by the overview. The case was changed to title case. | EXTRACTION-ARTIFACT |
| 12 | §2 row 14, cited D LIRS block 7 (inv 83) | "Enter the work that must be completed… ready condition. ... Tags may be removed… before authorizing clearing the line item." | Verbatim in a three-column row (L2039–2045). The elided text is "For PMS, a general statement such as 'complete maintenance IAW MRC' is adequate.", which does not change the meaning. | EXTRACTION-ARTIFACT |
| 13 | §2 row 18 THS columns (inv 87), cited D Fig. 2 | "REPLACED TAG AUTHORIZING OFFICER (INITIAL/DATE)" | Stacked header "REPLACED TAG / AUTHORIZING OFFICER / (INITIAL/DATE)" (L2116–2119; also the overview, L2169–2173). | EXTRACTION-ARTIFACT |
| 14 | §2 row 18 THS columns (inv 87) | "POSTED BY (INITIAL)", "POSTING CHECKED BY (INITIAL)", "REPAIR ACTIVITY WITNESS (INITIAL)" | Stacked headers in Fig. 2 (L2115–2121). Only a case-insensitive match is possible across the stack. The wording is confirmed. | EXTRACTION-ARTIFACT (×3) |
| 15 | §2 row 30 Audit Report columns (inv 99), cited D Figs. 10–11 | "Tag Serial Number" | Stacked "Tag Serial / Number" (L2626–2627). The neighbouring quote "Tagged Position" is stacked the same way but matched by chance elsewhere. Confirmed at L2626–2627. | EXTRACTION-ARTIFACT |

The 20 quotes matched only by the right-column pass are not failures. They are App B entries for AAO, Certified Line Item, LMA, NSA, RA Rep, LIRS, THS, TRS, TORS and Index Sheet, D LIRS blocks 6 (×2), 10, 11, 16, 18 and 19, and K TORS blocks 4, 11 and 23. Each is verbatim inside its table column.

## Advisory (not counted as failures)

- inv 42, row 1.23, 1.6.3.b(2): the `...` elides the proposer-signature allowance ("When local instructions allow, the documented verification signature made by a qualified repair activity individual proposing the tag-out may be used…") and the RA Rep's residual responsibility. Both qualify "shall independently review". The same row quotes both in its other columns, so the row as a whole does not lose them. A matrix builder lifting only that cell would.
- Small leading conditions trimmed but implied by the row label: inv 41 "the repair activity will perform an independent 100% validation…" (drops "If used for repair activity work,"; row 4a keeps it). inv 42 "the RA Representative signs the Clearance Authorized Repair Activity block." (drops "If the tag supported Repair Activity work (…) then"). inv 43 "the RA Witness should normally accompany…" (drops "When required,"). inv 174 "authorization to remove a tag…" (drops "When all line items requiring a tag are cleared as indicated by the tag being listed on the TRS,").
- inv 241, 4c: "Ship's Force ... shall also verify…": the ellipsis stands in for "is responsible for … RA. They". The meaning is faithful.
- Header inv 10: "independen", "remov", "stop" and "authoriz" are the author's grep terms, not quotations of a passage. They are counted in the 419 and do occur in the source.
- Gloss in row 1.11 (not a quote error): "In the electronic system the WCS/POIC (Work Complete) block is signed by the AO". 1.3.2.f(5), quoted in row 1.4, also lets the AAO sign that block in limited cases.

## [reading] notes

There is one `[reading]` (inv line 244, after §4c). Its quoted anchors are correct: "a person" (1.6.3.d(4), L947, "Assign a person to post the tag(s).") and "The person assigned" (1.8.5.b, L1508). Its claim that removal authority sits with the AO and, where applicable, the RA Representative is consistent with 1.8.1 (L1448–1450) and 1.8.4.a/b (L1493–1503). A grep for poster-equals-remover wording ("person who posted", "same person", "person attaching", "who hung") found no such rule. The note correctly limits its scope to "the appendices I read", since E, G and L were skipped. **No `[reading]` misstates its quote.**
