# Quote verification: inventory-aviation-civil.md

Audited file: `docs/rnd/contractor-kit/sources/inventory-aviation-civil.md` (354 lines, not edited).
Script: `scratchpad/verify_aviation.py`. Raw results are in `out.json`, `out.txt` and `review.txt` (section context per hit) in the same directory.

## Method

- The script extracted every straight-double-quoted string from line 11 onward (header table included). Lines 1–10 are the file's own rules preamble and quote only the ellipsis markers.
- Normalization on both sides: whitespace collapsed (this joins the `pdftotext -layout` line breaks), the `>` blockquote marker stripped, and curly quotes mapped to straight quotes. A second "loose" pass also folded case and dashes. No quote needed it except the case-only term mention "Rebuilt".
- `…` (U+2026) was treated as an inventory omission: the fragments had to occur in order within 1,500 characters. A trailing `…` was treated as truncation. A literal `...` was required to appear in the source.
- The cited source was searched first, then all of S1–S11. For each hit the script reported the nearest preceding `###` heading and the paragraph markers. I checked every cited section against those markers by eye.
- Every quote the script could not match was checked by hand. Every partial quote (one starting in lowercase, or with `…`) was compared against the full source sentence for a dropped "except", "not" or condition.

## Summary counts

| Measure | Count |
|---|---|
| Quoted strings in the inventory | **209** (the script split line 178's nested quote into two; counted here as one) |
| Verified verbatim in a source (script 187 + hand 18) | **205** |
| of which second-hand (cited only to the S4/S7/S8/S9 excerpt records of PDFs that are not vendored) | **41** |
| Not source quotes (target vocabulary, or the inventory's own heading) | 4: L60 "repairer under direction", L83 "coordinator who runs the work", L120 "restorers who return the system to service", L314 "Deferral records — gap" (the inventory's own heading at line 265) |
| MISQUOTE | 0 |
| WRONG-SOURCE | 0 |
| WRONG-SECTION | 0 |
| PARAPHRASE presented as a quote | 0. The two compiler paraphrases (L178 S3 finding note, L267 S11 table entry) are labelled as such and match their source text verbatim. |
| MEANING-CHANGING-ELISION | 5 rows (6 quotes): see the table |
| `[reading]` misstatements | 4: see below |

Hand-verified (the script missed these):

- L182 ×3, L185 and L266 sit in S3's Figure 7-1 (lines 200–260), where the column layout interleaves the text. All match once the columns are read apart, and the cited section is right.
- L178: the nested quote is S3 line 5, verbatim.
- The other twelve are short term mentions inside rows or `[reading]` lines that carry no key: L31 (S4/S7/S8/S9 "Not vendored"), L99, L159 ×3, L164, L211, L238, L281 ×2, L346, L347. All were found in the sources and sections the rows imply. L159's "Rebuilt" differs from the source only in capitalization; L238's "Engineering order" is the singular of S3's "engineering orders".

Second-hand rows: inventory lines 39, 123, 124, 139, 140, 188, 189, 191, 192, 234, 236, 244 (second quote, § 1-4f), 245, 246, 250, 257, 258, 259 ×4, 260–263, 307 ×4, 308–311, 317, 321–323, 341, 342 and 343 ×2.

- All 41 match their excerpt record verbatim.
- L266 is attributed to S3, where it is primary, and also appears in S4.
- L279 is cited [S3, S4] and matches both, so it is not second-hand.
- The `...` elisions in L234 (S4) and L341 (S9) are present in those records as written.

## Failure table

| Row (inventory line) | Quote as written | What the source says (file:line) | Verdict |
|---|---|---|---|
| L80, Person directly in charge, § 121.378(a) [S2] | "each person who is directly in charge of maintenance, preventive maintenance, or alterations, and each person performing required inspections must hold an appropriate airman certificate." | `contractor-kit/sources/14cfr121-371.md:71`: "(a) **Except for maintenance, preventive maintenance, alterations, and required inspections performed by a certificated repair station that is located outside the United States,** each person who is directly in charge …" | MEANING-CHANGING-ELISION (low–moderate). The leading exception is cut with no `…`, so the certificate rule reads as universal. Row 65 covers foreign repair stations only for § 121.709(c) signatures. |
| L110, Person performing the work, § 43.9(a) [S1, S6] | "each person who maintains, performs preventive maintenance, rebuilds, or alters … shall make an entry in the maintenance record of that equipment" | `contractor-kit/sources/14cfr43.md:157`: "(a) … **Except as provided in paragraphs (b) and (c) of this section,** each person who maintains …". § 43.9(b) (line 167) moves Part 121/135 CAMP holders to Part 121/135 recording. § 43.9(c) (line 169) excludes Part 91/125/135 inspection performers. | MEANING-CHANGING-ELISION (moderate). The cut exception removes exactly the Part 121 carriers the rest of the inventory relies on. |
| L118, Operational check flight, § 91.407(b) [S3] | "until an appropriately rated pilot with at least a private pilot certificate flies the aircraft, makes an operational check …" | `contractor-kit/sources/faa-rii-return-to-service.md:51`: "(b) **No person may carry any person (other than crewmembers) in an aircraft that has been maintained, rebuilt, or altered in a manner that may have appreciably changed its flight characteristics or substantially affected its operation in flight** until …" | MEANING-CHANGING-ELISION (moderate). The trigger condition and the scope (it bars only carrying non-crew persons) are dropped, so the flight reads as a general post-maintenance requirement. |
| L195, Operational check, § 91.407(b) [S3] | "makes an operational check of the maintenance performed or alteration made, and logs the flight in the aircraft records." | Same source line 51 as L118. | MEANING-CHANGING-ELISION (low). Same dropped condition. Partly mitigated: L196 quotes § 91.407(c), which states the "not appreciably changed" exception. |
| L135, contract maintenance provider, § 121.365(a) [S2] | "each person with whom it arranges for the performance of that work must have an organization adequate to perform the work." | `contractor-kit/sources/14cfr121-371.md:15`: "Each certificate holder that performs any of its maintenance **(other than required inspections)**, preventive maintenance, or alterations, and each person with whom it arranges …". "That work" excludes required inspections, which § 121.365(b) covers. | MEANING-CHANGING-ELISION (low). The referent of "that work" is lost. |
| L185 `[reading]`, Figure 7-1 [S3] | "will simulate operational functions and defect failures" | `faa-rii-return-to-service.md:243–250`: "Is a required test performed on the item that will simulate operational functions and defect failures, **malfunctions or defects that would impact the safe flight or landing of the aircraft?**" Yes → "RII does not apply as system operational integrity can be assessed." | MEANING-CHANGING-ELISION (low). The quote stops mid-phrase with no `…` and drops the safety qualifier that narrows which tests count. |

Noted but not failures:

- L143, 145.A.50(a) [S11]: a trailing `…` drops "…and that there are no known non-compliances which endanger flight safety". The omission is marked and the row points to the full text at L326, which is verbatim.
- L343, AC 00-71 § 3.2: "Resolved – … verified but not formally reviewed and confirmed." drops "corrected or fully mitigated". The full definition is at L307, so the meaning holds.

## `[reading]` lines that misstate their quote or source

1. **L347** says "Only one person or level may overrule the inspector." § 121.369(b)(8) (`14cfr121-371.md:43`) names **two** classes who may countermand an inspector: "supervisory personnel of the inspection unit, **or** a person at that level of administrative control that has overall responsibility for the management of both …". This misstates the source.
2. **L185** calls the Figure 7-1 test "a required functional test" and concludes "a mechanized test can substitute for the independent human inspection". The source says only "a required test" that "will simulate operational functions…"; nothing in it says the test is mechanized. This is overreach on top of the elision in the table.
3. **L120 and the L113 heading** use "check pilot" for the § 91.407(b) pilot. The source term is "an appropriately rated pilot with at least a private pilot certificate". "Check pilot" appears in no S1–S11 text in this sense (only incidentally in S9 line 34, about SOP adherence). This is a coined label presented beside regulatory role names. Low severity.
4. **L346** says § 43.9(a)(3) "presumes they are often the same". The text ("if other than the person specified in paragraph (a)(4)") only allows the performer and approver to be the same person; it states no presumption about how often. Low severity. The other half of that line ("No text read requires … be different") checks out against the texts read.

All other `[reading]` lines are consistent with their quotes: L40, L60, L77, L83, L99, L159, L238, L281, L298, L314, and the L345–348 block apart from items 1 and 4. The L99 claim that the DOM/chief-inspector sentence is the only occurrence of either title holds: the only hit is `faa-rii-return-to-service.md:126`.

## Section placement

Every quote sits in the section its row cites. This includes:

- the nested eCFR paragraphs, e.g. § 121.380(a)(2)(v)–(vii), § 121.709(b)(2)(i)–(iv), § 43.11(a)(4)–(6);
- the AC 120-16G paragraphs 5-1b(1)/(2) and the NOTE, 7-1a–c, 7-2a–e, 8-10b(2)(a)/(b) and (4), and Figure 7-1;
- AC 43-9D 8.1, 8.2, 8.4 and its Note, 8.5 and 8.6;
- the item numbers in S9 § 1.4 item 8 and § 6.4 items 1, 2 and 4;
- AC 00-71 §§ 3.1, 3.2, 3.3, 4.1.3 and 4.1.5, and AC 20-189 §§ 5.2, 6.1.2, 6.1.3, 6.3, 6.4 and 6.4.6.5.
