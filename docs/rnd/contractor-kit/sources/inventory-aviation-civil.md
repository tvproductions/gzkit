# Inventory — U.S. civil aviation maintenance vocabulary (verbatim)

Compiled 2026-10-25 for the R&D run recorded at `docs/rnd/contractor-kit.md`. Persona: primary-source researcher. Track: U.S. civil aviation maintenance texts already in the repository. Nothing was fetched from outside the repository for this inventory.

Rules of this file:

- Every row gives an exact quote and its section. Quotes are copied from the repository source files named below; no words were changed. An ellipsis (…) marks words omitted by this inventory; "..." inside a quote is the source file's own elision. Where a source file renders a PDF in `pdftotext -layout` line blocks, the line breaks inside one sentence are joined with a single space here; nothing else is altered.
- `[reading]` marks this inventory's interpretation. Anything not so marked is quotation or bibliographic fact.
- Source keys (S1–S11) are used in every row.

## 1. Header — files read

| Key | File | Edition / provenance stated in the file | Read |
|---|---|---|---|
| S1 | `docs/rnd/contractor-kit/sources/14cfr43.md` | eCFR Title 14 Part 43, issue date 2026-10-15, retrieved 2026-10-25 via eCFR API; §§ 43.1–43.17 in full; "Appendices A–F to Part 43 are NOT included." | In full |
| S2 | `docs/rnd/contractor-kit/sources/14cfr121-371.md` | eCFR, issue date 2026-10-15, retrieved 2026-10-25; §§ 121.365, 121.369, 121.371, 121.378, 121.380, 121.709, each in full | In full |
| S3 | `docs/rnd/contractor-kit/sources/faa-rii-return-to-service.md` | § 1.1 selected definitions and § 91.407 (eCFR 2026-10-15); AC 120-16G (1/4/16) line ranges 1–35, 812–871, 1131–1276, 1556–1615; AC 43-9D (9/22/25) lines 1–12, 98–185 | In full |
| S4 | `docs/rnd/renewing-vows/sources/us-gov-faa-ac-120-16g-maintenance-programs.md` | AC 120-16G dated 1/4/16; excerpt record made 2026-10-08 from an operator-supplied PDF (SHA-256 `c3f8566005af…`), PDF not vendored | In full |
| S5 | `docs/rnd/renewing-vows/sources/us-gov-14cfr-121-subpart-L.md` | eCFR Title 14 "up to date as of" 2026-10-02; excerpts of §§ 121.367, 121.369(b)–(c), 121.373(a), 121.374 (part), 121.379, § 1.2 | In full |
| S6 | `docs/rnd/renewing-vows/sources/us-gov-14cfr-43-9.md` | eCFR "up to date as of" 2026-10-02; §§ 43.5, 43.7, 43.9, 121.709(a)–(b) | In full |
| S7 | `docs/rnd/renewing-vows/sources/us-gov-faa-ac-00-71-open-problem-reports.md` | AC 00-71 dated Sep 16, 2022; excerpt record from operator-supplied PDF, not vendored | In full |
| S8 | `docs/rnd/renewing-vows/sources/us-gov-faa-ac-20-189-open-problem-reports.md` | AC 20-189 dated Sep 16, 2022; excerpt record from operator-supplied PDF, not vendored | In full |
| S9 | `docs/rnd/renewing-vows/sources/us-gov-faa-ac-120-71b-sop-pm.md` | AC 120-71B dated 1/10/17; excerpt record from operator-supplied PDF, not vendored | In full; mined only for maintenance, deferral, problem reports and monitoring, as briefed |
| S10 | `docs/rnd/renewing-vows/sources/std-ata-msg-3.md` | ATA MSG-3 rev. 2022.1 | In full — **metadata and paraphrase only; no quoted MSG-3 text.** One quoted phrase is from the publisher's product description, not the standard. Nothing from S10 is used as a vocabulary row. |
| S11 | `docs/rnd/renewing-vows/sources/std-easa-part-145.md` | Reg. (EU) No 1321/2014 consolidated 07.08.2026 | In full — **quotes only 145.A.50(a), 145.A.50(b) and M.A.801(e)**; the rest is cited by point and subject. EU, not U.S.; used below only where it fills a U.S. gap, and labelled. |

Edition agreement: S1/S6 (§§ 43.5, 43.7, 43.9) and S2/S6 (§ 121.709(a)–(b)) are two retrievals (eCFR 2026-10-15 and 2026-10-02). The quoted text was compared and is word-for-word identical in this inventory's reading.

Not read, and why:

- The primary PDFs behind S4, S7, S8, S9 are not in the repository (each file says "Not vendored"). S4, S7, S8, S9 are a prior session's excerpt records; quotes from them are second-hand transcriptions, and only the passages that record chose to quote are available. S3's AC 120-16G line blocks are a separate, later extraction and are preferred where the two overlap.
- 14 CFR Part 43 Appendices A (list of major repairs/alterations and preventive maintenance), B (major repair/alteration form disposition) and D (inspection checklist scope) are referenced by §§ 43.3(a), 43.9(d), 43.15(c) but excluded from S1.
- Regulations named by the read texts but not present in any repository file: Part 65 (mechanic, repairman, inspection authorization privileges), Part 145 (repair stations), § 119.65 (Director of Maintenance, chief inspector positions), § 121.628 and § 91.213 (inoperative equipment / MEL), § 121.363, § 121.368, § 121.375, § 121.377, § 121.380a (headings only in S5), § 91.405, § 91.409, § 91.417 (quoted only through AC 43-9D), and the Part 135 counterparts. Rows below that depend on these are marked as gaps.

## 2. Roles and authorities

**The Administrator (FAA)**
- "Except as provided in this section and § 43.17, no person, other than the Administrator, may approve an aircraft, airframe, aircraft engine, propeller, appliance, or component part for return to service after it has undergone maintenance, preventive maintenance, rebuilding, or alteration." — § 43.7(a) [S1, S6]
- "We do not approve your CAMP. There is no regulation that requires an approval. However, we do issue air carrier operations specifications (OpSpecs) to you that authorize you to use a maintenance program and the air carrier maintenance manual required by FAA regulations." — AC 120-16G § 1-5 [S4]
- [reading] The regulator authorizes a program and holds the operator to results; it does not approve the program. Closest analogue to the human who sets scope is not the FAA but the certificate holder (below); the FAA is the authority that grants the right to approve.

**Mechanic (holder of a mechanic certificate)**
- May: "The holder of a mechanic certificate may perform maintenance, preventive maintenance, and alterations as provided in Part 65 of this chapter." — § 43.3(b) [S1]
- May: "The holder of a mechanic certificate or an inspection authorization may approve an aircraft, airframe, aircraft engine, propeller, appliance, or component part for return to service as provided in Part 65 of this chapter." — § 43.7(b) [S1, S6]
- Part 121 signature: "Be signed by an authorized certificated mechanic or repairman except that a certificated repairman may sign the release or entry only for the work for which he is employed and certificated." — § 121.709(b)(3) [S2]
- Gap: the limits of the privileges are in Part 65, not read.

**Repairman (holder of a repairman certificate)**
- May: "The holder of a repairman certificate may perform maintenance, preventive maintenance, and alterations as provided in part 65 of this chapter." — § 43.3(c) [S1]
- May not (Part 121): "a certificated repairman may sign the release or entry only for the work for which he is employed and certificated." — § 121.709(b)(3) [S2]
- Light-sport: "The holder of a repairman certificate (light-sport aircraft) with a maintenance rating may approve an aircraft issued a special airworthiness certificate in light-sport category for return to service, as provided in part 65 of this chapter." — § 43.7(g) [S1]

**Inspection Authorization (IA) holder**
- "The holder of a mechanic certificate or an inspection authorization may approve … for return to service as provided in Part 65 of this chapter." — § 43.7(b) [S1] (ellipsis marks words omitted here; full sentence above)
- "Maintenance personnel may indicate the type of certificate exercised by using airframe (A), powerplant (P), Airframe and Powerplant (A&P), Inspection Authorization (IA), or CRS." — AC 43-9D § 8.6 [S3]

**Person working under supervision**
- May: "A person working under the supervision of a holder of a mechanic or repairman certificate may perform the maintenance, preventive maintenance, and alterations that his supervisor is authorized to perform, if the supervisor personally observes the work being done to the extent necessary to ensure that it is being done properly and if the supervisor is readily available, in person, for consultation." — § 43.3(d) [S1]
- May not: "However, this paragraph does not authorize the performance of any inspection required by Part 91 or Part 125 of this chapter or any inspection performed after a major repair or alteration." — § 43.3(d) [S1]
- [reading] The regulation's nearest word to "repairer under direction" — authority is borrowed from the supervisor and stops short of inspection.

**Repair station (holder of a repair station certificate); certificated repair station (CRS)**
- "The holder of a repair station certificate may perform maintenance, preventive maintenance, and alterations as provided in Part 145 of this chapter." — § 43.3(e) [S1]
- "The holder of a repair station certificate may approve … for return to service as provided in Part 145 of this chapter." — § 43.7(c) [S1]
- Foreign CRS: "after maintenance, preventive maintenance, or alterations performed by a repair station that is located outside the United States, the airworthiness release or log entry required by paragraph (a) of this section may be signed by a person authorized by that repair station." — § 121.709(c) [S2]
- "Certificated repair stations (CRS) frequently work on components shipped to them without the maintenance records. To provide for this situation, repair stations should supply owners and operators with copies of work orders written for the work in lieu of maintenance record entries." — AC 43-9D § 8.4 Note [S3]
- Gap: Part 145 not read.

**Certificate holder / air carrier (Part 121 or 135 operating certificate)**
- Perform: "The holder of an air carrier operating certificate or an operating certificate issued under Part 121 or 135, may perform maintenance, preventive maintenance, and alterations as provided in Part 121 or 135." — § 43.3(f) [S1]
- Approve: "The holder of an air carrier operating certificate or an operating certificate issued under Part 121 or 135, may approve … for return to service as provided in Part 121 or 135 of this chapter, as applicable." — § 43.7(e) [S1]
- "A certificate holder may perform, or it may make arrangements with other persons to perform, maintenance, preventive maintenance, and alterations as provided in its continuous airworthiness maintenance program and its maintenance manual." — § 121.379(a) [S5]
- "A certificate holder may approve any aircraft, airframe, aircraft engine, propeller, or appliance for return to service after maintenance, preventive maintenance, or alterations that are performed under paragraph (a) of this section. However, in the case of a major repair or major alteration, the work must have been done in accordance with technical data approved by the Administrator." — § 121.379(b) [S5]
- Authority sits with the carrier, not the individual: "You accomplish all maintenance and approval for return to service on your aircraft under your air carrier certificate by your maintenance organization or persons authorized by you, not by any individual or organization under their own individual certificate." — AC 120-16G § 5-1b(2) [S3]
- "NOTE: The certificate requirements contained in the regulations stated above are directed at the air carrier. The certificated airman acting in this position does not exercise the authority or privileges of his or her certificate." — AC 120-16G § 5-1b(1) NOTE [S3]
- Retains responsibility when work is contracted: "Consistent with the regulations, you remain primarily responsible for the performance of each RII accomplished by the other person." — AC 120-16G § 7-1a [S3]
- [reading] This is the strongest civil analogue for the human who sets scope and owns return to service: the organization holds the authority; individuals sign on its behalf.

**Person directly in charge**
- "each person who is directly in charge of maintenance, preventive maintenance, or alterations, and each person performing required inspections must hold an appropriate airman certificate." — § 121.378(a) [S2]
- Definition: "For the purposes of this section, a person directly in charge is each person assigned to a position in which he is responsible for the work of a shop or station that performs maintenance, preventive maintenance, alterations, or other functions affecting aircraft airworthiness." — § 121.378(b) [S2]
- What it does and need not do: "A person who is directly in charge need not physically observe and direct each worker constantly but must be available for consultation and decision on matters requiring instruction or decision from higher authority than that of the persons performing the work." — § 121.378(b) [S2]
- [reading] The closest regulatory text to the drydock "coordinator who runs the work": responsible for a shop's work, available for decision, not a constant observer, and not (by this section) an inspector.

**Required inspection personnel / RII inspector**
- Qualification: "No person may use any person to perform required inspections unless the person performing the inspection is appropriately certificated, properly trained, qualified, and authorized to do so." — § 121.371(a) [S2]
- Under an inspection unit: "No person may allow any person to perform a required inspection unless, at that time, the person performing that inspection is under the supervision and control of an inspection unit." — § 121.371(b) [S2]
- May not: "No person may perform a required inspection if he performed the item of work required to be inspected." — § 121.371(c) [S2]
- Roster and written limits: "Each certificate holder shall maintain, or shall determine that each person with whom it arranges to perform its required inspections maintains, a current listing of persons who have been trained, qualified, and authorized to conduct required inspections. The persons must be identified by name, occupational title, and the inspections that they are authorized to perform. The certificate holder (or person with whom it arranges to perform its required inspections) shall give written information to each person so authorized describing the extent of his responsibilities, authorities, and inspectional limitations." — § 121.371(d) [S2]
- Designation by title: "The method of performing required inspections and a designation by occupational title of personnel authorized to perform each required inspection." — § 121.369(b)(3) [S2]
- Certificate not exercised: "This is an air carrier qualification requirement; the individual does not exercise that certificate when accomplishing the RII. You must formally notify each of these individuals of their RII authorization as well as its scope (§§ 121.371(d) and 135.429(e))." — AC 120-16G § 7-2b [S3]

**Inspection unit; supervisory personnel of the inspection unit**
- "under the supervision and control of an inspection unit." — § 121.371(b) [S2]
- Who may overrule an inspector: "Instructions and procedures to prevent any decision of an inspector, regarding any required inspection from being countermanded by persons other than supervisory personnel of the inspection unit, or a person at that level of administrative control that has overall responsibility for the management of both the required inspection functions and the other maintenance, preventive maintenance, and alterations functions." — § 121.369(b)(8) [S2]

**Director of Maintenance (DOM); chief inspector**
- "Your Director of Maintenance (DOM) and chief inspector must hold an airman's certificate with Airframe and Powerplant (A&P) ratings." — AC 120-16G § 5-1b(1) [S3]
- Gap: this sentence is the only occurrence of either title in the texts read. The positions themselves are established in § 119.65, not in the repository. [reading] The regulations read describe the function ("a person at that level of administrative control that has overall responsibility for … both", § 121.369(b)(8)) without naming the title.

**Person approving the work / person approving for return to service**
- "If the work performed … has been performed satisfactorily, the signature, certificate number, and kind of certificate held by the person approving the work. The signature constitutes the approval for return to service only for the work performed." — § 43.9(a)(4) [S1, S6]
- "The person approving or disapproving for return to service an aircraft, airframe, aircraft engine, propeller, appliance, or component part after any inspection performed in accordance with part 91, 125, § 135.411(a)(1), or § 135.419 shall make an entry in the maintenance record of that equipment" — § 43.11(a) [S1]
- Part 121 record: "The name or other positive identification of the individual approving the work." — § 121.369(c)(3) [S2]
- "Section 121.709 requires that anyone who you authorize to issue an approval for return to service hold an appropriate airman's certificate." — AC 120-16G § 5-1b(1) [S3]
- "The Airworthiness Release Form or log entry must be signed by an appropriately certificated individual who is authorized by you to make the Airworthiness Release Form or log entry on your behalf." — AC 120-16G § 8-10b(4) [S3]
- Performer and approver can differ: "However, when work is accomplished by one person and approved for return to service by another, the dates may differ. Two signatures may also appear under this circumstance; however, a single entry in accordance with 14 CFR § 43.9(a)(3) is acceptable." — AC 43-9D § 8.5 [S3]

**Person performing the work**
- "each person who maintains, performs preventive maintenance, rebuilds, or alters … shall make an entry in the maintenance record of that equipment" — § 43.9(a) [S1, S6]
- "The name of the person performing the work if other than the person specified in paragraph (a)(4) of this section." — § 43.9(a)(3) [S1]
- Standard of work: "Each person maintaining or altering, or performing preventive maintenance, shall do that work in such a manner and use materials of such a quality, that the condition of the aircraft … worked on will be at least equal to its original or properly altered condition" — § 43.13(b) [S1]

**Pilot; pilot in command (PIC); check pilot**
- Pilot may do preventive maintenance: "Except for holders of a sport pilot certificate, the holder of a pilot certificate issued under part 61 may perform preventive maintenance on any aircraft owned or operated by that pilot which is not used under part 121, 129, or 135 of this chapter." — § 43.3(g) [S1]
- Pilot may approve after own preventive maintenance: "A person holding at least a private pilot certificate may approve an aircraft for return to service after performing preventive maintenance under the provisions of § 43.3(g)." — § 43.7(f) [S1]
- PIC receives the release: "When an airworthiness release form is prepared the certificate holder must give a copy to the pilot in command and must keep a record thereof for at least 2 months." — § 121.709(d) [S2]
- Operational check flight: "until an appropriately rated pilot with at least a private pilot certificate flies the aircraft, makes an operational check of the maintenance performed or alteration made, and logs the flight in the aircraft records." — § 91.407(b) [S3]
- Not maintenance: "Updates of databases in installed avionics meeting the conditions of this paragraph are not considered maintenance and may be performed by pilots" — § 43.3(k) [S1]
- [reading] The PIC is a recipient of the return-to-service instrument, not its signer; the check pilot under § 91.407(b) is a post-return operational verifier — the closest civil text to "restorers who return the system to service".

**Pilot flying (PF) / pilot monitoring (PM)** (flight deck, not maintenance)
- "Pilot Monitoring (PM). The PM monitors the aircraft state and system status, calls out any perceived or potential deviations from the intended flightpath, and intervenes if necessary." — AC 120-71B § 1.4 item 8 [S9]
- "The PF is responsible for managing, and the PM is responsible for monitoring the current and projected flightpath and energy of the aircraft at all times." — AC 120-71B § 6.4 item 2 [S9]

**Manufacturer**
- "A manufacturer may approve for return to service any aircraft, airframe, aircraft engine, propeller, appliance, or component part which that manufacturer has worked on under § 43.3(j). However, except for minor alterations, the work must have been done in accordance with technical data approved by the Administrator." — § 43.7(d) [S1]

**Owner / operator / lessee**
- "Title 14 CFR § 91.417 states that an aircraft owner/operator shall keep and maintain aircraft maintenance records." — AC 43-9D § 8.1 [S3]
- "Title 14 CFR § 91.405 requires each owner or operator to ensure that maintenance personnel make appropriate entries in the maintenance records to indicate that the aircraft has been approved for return to service." — AC 43-9D § 8.2 [S3]
- Receives discrepancies: "that persons must give the owner or lessee a signed and dated list of those discrepancies." — § 43.11(b) [S1]

**Person with whom the certificate holder arranges (contract maintenance provider)**
- "each person with whom it arranges for the performance of that work must have an organization adequate to perform the work." — § 121.365(a) [S2]
- "Policies, procedures, methods, and instructions for the accomplishment of all maintenance, preventive maintenance, and alterations carried out by a maintenance provider." — § 121.369(b)(10) [S2]

**Review board / Change Control Board** (certification, not maintenance)
- "Assessment of PRs classified as 'Significant', 'Functional' or 'Process' would typically be performed by a review board which includes representatives from the appropriate disciplines" — AC 00-71 § 4.1.3 [S7]
- "PR Closure – a means to close PRs, which includes the review and confirmation of the resolution of the problem, and is indicated through a documented authorization process (e.g., Change Control Board signoff)." — AC 00-71 § 4.1.5 [S7]

**EU comparison only — certifying staff** [S11]
- "A certificate of release to service shall be issued by appropriately authorised certifying staff on behalf of the organisation when that certifying staff has verified that all the maintenance that was ordered has been properly carried out by the organisation …" — 145.A.50(a) [S11] (ellipsis: remainder in § 5 below)

## 3. Kinds of work

**Maintenance**
- "Maintenance means inspection, overhaul, repair, preservation, and the replacement of parts, but excludes preventive maintenance." — § 1.1 [S3]

**Preventive maintenance**
- "Preventive maintenance means simple or minor preservation operations and the replacement of small standard parts not involving complex assembly operations." — § 1.1 [S3]
- "Those items, the performance of which is a major alteration, a major repair, or preventive maintenance, are listed in appendix A." — § 43.3(a) [S1] (Appendix A not read)

**Overhaul (as a record claim)**
- "No person may describe in any required maintenance entry or form an aircraft, airframe, aircraft engine, propeller, appliance, or component part as being overhauled unless— (1) Using methods, techniques, and practices acceptable to the Administrator, it has been disassembled, cleaned, inspected, repaired as necessary, and reassembled; and (2) It has been tested in accordance with approved standards and technical data, or in accordance with current standards and technical data acceptable to the Administrator, which have been developed and documented by the holder of the type certificate, supplemental type certificate, or a material, part, process, or appliance approval under part 21 of this chapter." — § 43.2(a) [S1]

**Rebuilding**
- "No person may describe in any required maintenance entry or form an aircraft, airframe, aircraft engine, propeller, appliance, or component part as being rebuilt unless it has been disassembled, cleaned, inspected, repaired as necessary, reassembled, and tested to the same tolerances and limits as a new item, using either new parts or used parts that either conform to new part tolerances and limits or to approved oversized or undersized dimensions." — § 43.2(b) [S1]
- [reading] "Rebuilt" and "overhauled" are defined as conditions on what a record may *say*, not as kinds of work in § 1.1. The rebuilt standard is "as a new item"; overhaul is not.

**Alteration — major / minor**
- "Major alteration means an alteration not listed in the aircraft, aircraft engine, or propeller specifications— (1) That might appreciably affect weight, balance, structural strength, performance, powerplant operation, flight characteristics, or other qualities affecting airworthiness; or (2) That is not done according to accepted practices or cannot be done by elementary operations." — § 1.1 [S3]
- "Minor alteration means an alteration other than a major alteration." — § 1.1 [S3]
- No § 1.1 definition of "alteration" itself was among the selections in S3.

**Repair — major / minor**
- "Major repair means a repair: (1) That, if improperly done, might appreciably affect weight, balance, structural strength, performance, powerplant operation, flight characteristics, or other qualities affecting airworthiness; or (2) That is not done according to accepted practices or cannot be done by elementary operations." — § 1.1 [S3]
- "Minor repair means a repair other than a major repair." — § 1.1 [S3]
- Classification duty: "You should have detailed major/minor classification procedures in your manual to evaluate each repair or alteration on a case-by-case basis" — AC 120-16G § 5-2 [S3]
- Why the list is not enough: "exclusive reliance on the part 43, appendix A, list of major repairs and alterations to make the major/minor classification might result in the misclassification of some repairs and alterations because the part 43, appendix A, list does not include evolving airplane design and construction techniques" — AC 120-16G § 5-2 [S3]

**Inspection (Part 91/125/135 inspections)**
- "Each person performing an inspection required by part 91, 125, or 135 of this chapter, shall— (1) Perform the inspection so as to determine whether the aircraft, or portion(s) thereof under inspection, meets all applicable airworthiness requirements" — § 43.15(a)(1) [S1]
- Checklist: "Each person performing an annual or 100-hour inspection shall use a checklist while performing the inspection." — § 43.15(c)(1) [S1]
- Routine vs detailed: "Routine inspections consist of visual examination or check of the appliances, the aircraft, and its components and systems, insofar as practicable without disassembly. Detailed inspections consist of a thorough examination of the appliances, the aircraft, and its components and systems, with such disassembly as is necessary." — § 43.15(d)(1) [S1]

**Required inspection (Part 121) / Required Inspection Item (RII)**
- Not defined in § 1.1: "14 CFR § 1.1 (General definitions) contains no definition of "return to service" or "required inspection item"" — S3 finding note (compiler's statement, not regulation).
- Operative definition: "A designation of the items of maintenance and alteration that must be inspected (required inspections), including at least those that could result in a failure, malfunction, or defect endangering the safe operation of the aircraft, if not performed properly or if improper parts or materials are used." — § 121.369(b)(2) [S2]
- Term "required inspections" fixed by: "Each certificate holder that performs any inspections required by its manual in accordance with § 121.369(b)(2) or (3) (in this subpart referred to as required inspections)" — § 121.365(b) [S2]
- Granularity: "Your RII lists should identify specific items of maintenance for each aircraft type you operate. It is inappropriate to designate entire systems as RIIs." — AC 120-16G § 7-1b [S3]
- Exclusions in the decision flow: "RII does not apply as it is limited to installations and repairs on aircraft"; "RII does not apply as those lists contain items of equipment which the Administrator has determined may be inoperative or removed while still maintaining aircraft airworthiness"; "RII does not apply as system operational integrity can be assessed." — AC 120-16G Figure 7-1 [S3]
- Weight: "RIIs relate directly to flight safety. Consider all your RIIs with the same safety of flight consideration and emphasis even if accomplishing an individual RII adversely impacts your flight schedule, it is related to a scheduled or an unscheduled task, or it arises at an awkward time or at an inconvenient location." — AC 120-16G § 7-1c [S3]
- Essential maintenance: "When another person performs RII to include the entire aircraft, this is considered Essential Maintenance." — AC 120-16G § 7-1a [S3]
- [reading] The RII test in Figure 7-1 excludes a task when a required functional test "will simulate operational functions and defect failures" — i.e. a mechanized test can substitute for the independent human inspection. Directly relevant to which drydock work needs the independent inspector.

**Scheduled / unscheduled maintenance**
- "Scheduled maintenance consists of all the individual maintenance tasks performed according to the maintenance time limitations, also called a maintenance schedule." — AC 120-16G § 5-4a [S4]
- "Unscheduled maintenance includes procedures, instructions, and standards for maintenance that occurs on an unscheduled or unforeseen basis. A need for unscheduled maintenance may result from scheduled maintenance tasks, pilot reports, or unforeseen events" — AC 120-16G § 5-4b [S4]
- Routine/nonroutine: "The method of performing routine and nonroutine maintenance (other than required inspections), preventive maintenance, and alterations." — § 121.369(b)(1) [S2]
- Scheduled task: "A scheduled maintenance task is a maintenance action that you perform at regular, scheduled intervals." — AC 120-16G § 6-3a(2) [S4]
- Work package: "The regulations are broad enough to permit you to organize all of these individual tasks into a series of integrated scheduled work packages of your own design" — AC 120-16G § 6-1 [S4]

**Operational check**
- "makes an operational check of the maintenance performed or alteration made, and logs the flight in the aircraft records." — § 91.407(b) [S3]
- Substitute: "The aircraft does not have to be flown as required by paragraph (b) of this section if, prior to flight, ground tests, inspection, or both show conclusively that the maintenance, preventive maintenance, rebuilding, or alteration has not appreciably changed the flight characteristics or substantially affected the flight operation of the aircraft." — § 91.407(c) [S3]

**Performance standard for all work**
- "shall use the methods, techniques, and practices prescribed in the current manufacturer's maintenance manual or Instructions for Continued Airworthiness prepared by its manufacturer, or other methods, techniques, and practices acceptable to the Administrator" — § 43.13(a) [S1]
- Airworthiness limitations: "Each person performing an inspection or other maintenance specified in an Airworthiness Limitations section of a manufacturer's maintenance manual or Instructions for Continued Airworthiness shall perform the inspection or other maintenance in accordance with that section" — § 43.16 [S1]

## 4. Documents and records

**Maintenance record entry**
- Content: "(1) A description (or reference to data acceptable to the Administrator) of work performed. (2) The date of completion of the work performed. (3) The name of the person performing the work if other than the person specified in paragraph (a)(4) of this section. (4) If the work performed … has been performed satisfactorily, the signature, certificate number, and kind of certificate held by the person approving the work. The signature constitutes the approval for return to service only for the work performed." — § 43.9(a)(1)–(4) [S1, S6]
- Detail standard: "The description should be in sufficient detail to permit a person unfamiliar with the work to understand what was done and the methods and procedures used in doing it." — AC 43-9D § 8.4 [S3]
- Format: "Maintenance records may be kept in any format that provides record continuity, includes required contents, lends itself to the addition of new entries, provides for signature entry, and is intelligible." — AC 43-9D § 8.2 [S3]
- Referenced documents: "Manufacturer's manuals, Service Letters (SL), Service Bulletins (SB), work orders, FAA ACs, and others, which accurately describe what was done or how it was done, may be referenced. Except for the documents mentioned that are in common usage, referenced documents are to be made a part of the maintenance records" — AC 43-9D § 8.4 [S3]
- Retention (Part 91, via AC): "Title 14 CFR § 91.417(b) requires records of maintenance, alterations, and required or approved inspections to be retained until the work is repeated, superseded by other work, or for 1 year." — AC 43-9D § 8.2 [S3]

**Inspection record entry; list of discrepancies; placard "Inoperative"**
- Airworthy statement: "“I certify that this aircraft has been inspected in accordance with (insert type) inspection and was determined to be in airworthy condition.”" — § 43.11(a)(4) [S1]
- Not approved statement: "“I certify that this aircraft has been inspected in accordance with (insert type) inspection and a list of discrepancies and unairworthy items dated (date) has been provided for the aircraft owner or operator.”" — § 43.11(a)(5) [S1]
- Discrepancy list and placards: "If the person performing any inspection required by part 91 or 125 or § 135.411(a)(1) of this chapter finds that the aircraft is unairworthy or does not meet the applicable type certificate data, airworthiness directives, or other approved data upon which its airworthiness depends, that persons must give the owner or lessee a signed and dated list of those discrepancies. For those items permitted to be inoperative under § 91.213(d)(2) of this chapter, that person shall place a placard, that meets the aircraft's airworthiness certification regulations, on each inoperative instrument and the cockpit control of each item of inoperative equipment, marking it “Inoperative,” and shall add the items to the signed and dated list of discrepancies given to the owner or lessee." — § 43.11(b) [S1]

**Major repair / alteration form**
- "In addition to the entry required by paragraph (a) of this section, major repairs and major alterations shall be entered on a form, and the form disposed of, in the manner prescribed in appendix B, by the person performing the work." — § 43.9(d) [S1]

**Part 121 recordkeeping system (manual)**
- "a suitable system (which may include a coded system) that provides for preservation and retrieval of information in a manner acceptable to the Administrator and that provides— (1) A description (or reference to data acceptable to the Administrator) of the work performed; (2) The name of the person performing the work if the work is performed by a person outside the organization of the certificate holder; and (3) The name or other positive identification of the individual approving the work." — § 121.369(c) [S2]
- "All the records necessary to show that all requirements for the issuance of an airworthiness release under § 121.709 have been met." — § 121.380(a)(1) [S2]
- Status records: "The identification of the current inspection status of the aircraft" — § 121.380(a)(2)(v); "The current status of applicable airworthiness directives, including the date and methods of compliance, and, if the airworthiness directive involves recurring action, the time and date when the next action is required." — § 121.380(a)(2)(vi); "A list of current major alterations to each airframe, engine, propeller, and appliance." — § 121.380(a)(2)(vii) [S2]
- Retention: "the records specified in paragraph (a)(1) of this section shall be retained until the work is repeated or superseded by other work or for one year after the work is performed." — § 121.380(c)(1); "The records specified in paragraph (a)(2) of this section shall be retained and transferred with the aircraft at the time the aircraft is sold." — § 121.380(c)(3) [S2]

**Airworthiness release / aircraft log entry**
- "No certificate holder may operate an aircraft after maintenance, preventive maintenance or alterations are performed on the aircraft unless the certificate holder, or the person with whom the certificate holder arranges for the performance of the maintenance, preventive maintenance, or alterations, prepares or causes to be prepared— (1) An airworthiness release; or (2) An appropriate entry in the aircraft log." — § 121.709(a) [S2]
- The four certifications: "(i) The work was performed in accordance with the requirements of the certificate holder's manual; (ii) All items required to be inspected were inspected by an authorized person who determined that the work was satisfactorily completed; (iii) No known condition exists that would make the airplane unairworthy; and (iv) So far as the work performed is concerned, the aircraft is in condition for safe operation" — § 121.709(b)(2) [S2]
- Signature as certification: "Instead of restating each of the conditions of the certification required by paragraph (b) of this section, the air carrier may state in its manual that the signature of an authorized certificated mechanic or repairman constitutes that certification." — § 121.709(e) [S2]
- Separate from log: "If you use an Airworthiness Release Form, you must keep it separate and distinct from the aircraft log. It is not included in the maintenance record requirements." — AC 120-16G § 8-10b(2)(a) [S3]
- Same thing, two forms: "Other than form or format, there is no legal or technical difference between an Airworthiness Release Form and a log entry." — AC 120-16G § 8-10b(2)(a) [S3]
- Naming: "To avoid confusion and to be consistent with the regulations, you should not identify this entry in the aircraft log as an airworthiness release." — AC 120-16G § 8-10b(2)(b) [S3]

**Work cards / job cards / task cards; work forms; engineering orders; work orders**
- "Work cards, sometimes referred to as job cards or task cards, while not a specific regulatory requirement, have evolved as a best practice. We consider work cards to be part of your air carrier manual and the air carrier maintenance program. They are the “what to do” and the “how to do it” parts of your maintenance program. ... Your work cards provide a control element to the performance of maintenance. ... The second primary function is to document maintenance activities" — AC 120-16G § 3-3d [S4] (ellipses are in S4's transcription)
- RII marking: "You should clearly identify your RII requirements on work forms, job cards, engineering orders, etc., or by any other method consistent with your maintenance program." — AC 120-16G § 7-2c [S3]
- Schedule link: "you should identify on the maintenance schedule the task or work card associated with each scheduled maintenance task." — AC 120-16G § 6-3c [S4]
- Work order (CRS): "repair stations should supply owners and operators with copies of work orders written for the work in lieu of maintenance record entries. The work order copy must include the information required by 14 CFR § 91.417(a)(1)(i)–(iii)" — AC 43-9D § 8.4 Note [S3]
- [reading] "Engineering order" appears only as a list item; no text read defines it.

**Maintenance manual; maintenance program; CAMP; maintenance schedule**
- Program duty: "Each certificate holder shall have an inspection program and a program covering other maintenance, preventive maintenance, and alterations that ensures that— (a) Maintenance, preventive maintenance, and alterations performed by it, or by other persons, are performed in accordance with the certificate holder's manual; (b) Competent personnel and adequate facilities and equipment are provided for the proper performance of maintenance, preventive maintenance, and alterations; and (c) Each aircraft released to service is airworthy and has been properly maintained for operation under this part." — § 121.367 [S5]
- Manual contents: "The certificate holder's manual must contain the programs required by § 121.367 that must be followed in performing maintenance, preventive maintenance, and alterations of that certificate holder's airplanes" — § 121.369(b) [S2]
- Organization chart and contractor list: "The certificate holder shall put in its manual a chart or description of the certificate holder's organization required by § 121.365 and a list of persons with whom it has arranged for the performance of any of its required inspections, other maintenance, preventive maintenance, or alterations, including a general description of that work." — § 121.369(a) [S2]
- CAMP: "CAMP means continuous airworthiness maintenance program." — § 1.2 [S5]; "Since then, the CAP has become known, in a colloquial sense, as a Continuous Airworthiness Maintenance Program (CAMP)." — AC 120-16G § 1-4f [S4]
- Schedule: "The maintenance time limitations set out the what, how, and when of your scheduled maintenance effort." — AC 120-16G § 6-1 [S4]
- Changes need justification: "Keep in mind that more maintenance is not always a good idea, so if you decide to decrease intervals or add tasks, you should go through the same justification process as any other change to the maintenance schedule." — AC 120-16G § 6-3b [S4]

**CASS (Continuing Analysis and Surveillance System)**
- "Each certificate holder shall establish and maintain a system for the continuing analysis and surveillance of the performance and effectiveness of its inspection program and the program covering other maintenance, preventive maintenance, and alterations and for the correction of any deficiency in those programs, regardless of whether those programs are carried out by the certificate holder or by another person." — § 121.373(a) [S5]
- "Your maintenance program should also have a system of continuing surveillance, investigation, data collection, analysis, corrective action, and corrective action followup that ensures all parts of your maintenance program are effective and are being performed in accordance with your manual. “Effective” means that you are achieving the desired results according to the maintenance program objectives and the standards that you, the air carrier, set. Program performance means that all personnel are following your program as you have documented it in your manual." — AC 120-16G § 1-6b [S4]
- Acronym in regulation: "This program must be the certificate holder's existing reliability program or its Continuing Analysis and Surveillance System (CASS) supplemented for ETOPS." — § 121.374(h) [S5]

**RII roster / authorization notice**
- See § 121.371(d) under Roles. "Your manual must include a list of persons with whom you have arranged for the performance of any required inspections (§§ 121.369(a) and 135.427(a)), both within your organization and within other organizations that perform maintenance on your behalf." — AC 120-16G § 7-2a [S3]

**Problem report (PR); open problem report (OPR); OPR summary report** (aircraft certification / development assurance — not in-service maintenance)
- "Problem report (PR) – A means to identify and record the resolution of anomalous behavior, process non-compliance with development assurance plans and standards, and deficiencies in life cycle data (adapted from DO-178C/ED-12C)." — AC 00-71 § 3.1 [S7]
- "Open problem report (OPR) – A problem report that has not reached the state 'closed' at the time of approval." — AC 00-71 § 3.1 [S7]
- Classes: "Significant – assessed at the product, system, or equipment level, a PR that has an actual or potential effect on the product, system, or equipment function that may lead to a Catastrophic, Hazardous, or Major failure condition, or may affect compliance with the operating rules." / "Functional – a PR that has an actual or a potential effect on a function at the product, system, or equipment level." / "Process – a PR that records a process non-compliance or deficiency that cannot result in a potential safety nor a potential functional effect." / "Life Cycle Data – a PR that is linked to a deficiency in a life cycle data item but not linked to a process non-compliance or process deficiency." — AC 00-71 § 3.3 [S7]
- One class each: "Each OPR should be assigned a single classification per the classification scheme. When multiple classifications apply, the OPR should be assigned the classification with the highest priority." — AC 20-189 § 6.1.2 [S8]
- Summary report: "An OPR summary report should be prepared and provided to the affected stakeholder(s), and to the certification authority upon request." — AC 20-189 § 6.4 [S8]
- Burden on lower classes: "For each OPR not classified as 'Significant' or 'Functional', justification that the error cannot have a safety or functional effect." — AC 20-189 § 6.4.6.5 [S8]
- Post-approval: "A problem recorded after approval should also be managed through the PR management process, and any related systemic process issues should be identified and corrected." — AC 20-189 § 5.2 [S8]

**Deferral records — gap**
- No text read defines a deferral record, deferred defect, MEL item record or carry-forward item. The only deferral-related wording in the U.S. texts read: "Is the item potentially deferrable per the minimum equipment list (MEL) or Configuration Deviation List (CDL)?" — AC 120-16G Figure 7-1 [S3]; and the § 43.11(b) placard/discrepancy-list text above, which cites § 91.213(d)(2) (not read). § 121.628 and § 91.213 are not in the repository.
- EU comparison, cited only by subject in S11 (no quote available): "release within approved limitations when the ordered maintenance cannot be completed" — S11 table entry for 145.A.50(e) (compiler's paraphrase, not regulation text); quoted CRS content: "4. the limitations to airworthiness or operations, if any." — M.A.801(e)4 [S11]

**Life-limited part record (tag)**
- "Life-limited part means any part for which a mandatory replacement limit is specified in the type design, the Instructions for Continued Airworthiness, or the maintenance manual." — § 43.10(a) [S1]
- "The method must deter the installation of the part after it has reached its life limit." — § 43.10(c) [S1]

## 5. Acts and states

**Approval for return to service**
- Preconditions: "No person may approve for return to service any aircraft, airframe, aircraft engine, propeller, or appliance, that has undergone maintenance, preventive maintenance, rebuilding, or alteration unless— (a) The maintenance record entry required by § 43.9 or § 43.11, as appropriate, has been made; (b) The repair or alteration form authorized by or furnished by the Administrator has been executed in a manner prescribed by the Administrator; and (c) If a repair or an alteration results in any change in the aircraft operating limitations or flight data contained in the approved aircraft flight manual, those operating limitations or flight data are appropriately revised and set forth as prescribed in § 91.9 of this chapter." — § 43.5 [S1, S6]
- Condition of operation: "No person may operate any aircraft that has undergone maintenance, preventive maintenance, rebuilding, or alteration unless— (1) It has been approved for return to service by a person authorized under § 43.7 of this chapter; and (2) The maintenance record entry required by § 43.9 or § 43.11, as applicable, of this chapter has been made." — § 91.407(a) [S3]
- Scope of the signature: "The signature constitutes the approval for return to service only for the work performed." — § 43.9(a)(4) [S1]
- Air carrier: "After performing any maintenance, preventive maintenance, or alterations on your airplane, you must approve it for return to service before you may operate it. As an air carrier, you must issue an approval for return to service under § 121.709 or § 135.443, as appropriate." — AC 120-16G § 5-3 [S3, S4]
- Singular requirement: "Your approval for return to service certification and documentation required by § 121.709 or § 135.443 is a singular requirement, but you may execute it in one of two ways" — AC 120-16G § 8-10b(2) [S3]
- [reading] Return to service is a precondition gate (record first, then approval, then operation), and the approval is bounded both by scope ("only for the work performed") and by knowledge ("No known condition exists", § 121.709(b)(2)(iii)).

**Disapproval for return to service**
- "the person approving or disapproving for return to service" — § 43.11(a) [S1]; "the (aircraft or components) are (approved or disapproved) for return to service." — § 43.11(a)(6) [S1]

**Release to service (released to service)**
- "Procedures to ensure that required inspections, other maintenance, preventive maintenance, and alterations that are not completed as a result of shift changes or similar work interruptions are properly completed before the aircraft is released to service." — § 121.369(b)(9) [S2]
- "Each aircraft released to service is airworthy and has been properly maintained for operation under this part." — § 121.367(c) [S5]

**Required inspection — perform; accept / reject**
- "Procedures, standards, and limits necessary for required inspections and acceptance or rejection of the items required to be inspected and for periodic inspection and calibration of precision tools, measuring devices, and test equipment." — § 121.369(b)(5) [S2]
- "You must also have those procedures, standards, and limits necessary for the acceptance or rejection of each of your RIIs. As you will not find RIIs or procedures, standards, and limits for RIIs in an Original Equipment Manufacturer (OEM) manual, you will have to develop these and put them in your manual." — AC 120-16G § 7-2d [S3]
- All performed before release: "Your manual must include procedures to ensure that you perform and complete all required inspections (§§ 121.369(b)(6) and 135.427(b)(6)) before you release the aircraft to service (§§ 121.369(b)(9) and 135.427(b)(9))." — AC 120-16G § 7-2e [S3]

**Buy-back**
- "Procedures for the reinspection of work performed pursuant to previous required inspection findings (buy-back procedures)." — § 121.369(b)(4) [S2]
- "You should also clearly state RII buy-back procedures (§§ 121.369(b)(4) and 135.427(b)(4))." — AC 120-16G § 7-2c [S3]
- [reading] In the regulation, buy-back is the reinspection of corrective work done after an inspector's finding — the inspector's rejection loop closing — not the first acceptance.

**Countermand (of an inspector's decision)**
- "to prevent any decision of an inspector, regarding any required inspection from being countermanded by persons other than supervisory personnel of the inspection unit, or a person at that level of administrative control that has overall responsibility for the management of both the required inspection functions and the other maintenance, preventive maintenance, and alterations functions." — § 121.369(b)(8) [S2]

**Work interruption / shift handover**
- § 121.369(b)(9), quoted above under Release to service. [S2]

**Problem report states: recorded, classified, resolved, closed**
- "Recorded – A problem that has been documented using the problem reporting process." / "Classified – A problem report that has been categorized in accordance with an established classification scheme." / "Resolved – A problem report that has been corrected or fully mitigated, for which resolution of the problem has been verified but not formally reviewed and confirmed." / "Closed – A resolved problem report that underwent a formal review and confirmation of an effective resolution of the problem." — AC 00-71 § 3.2 [S7]
- Closure act: "PR Closure – a means to close PRs, which includes the review and confirmation of the resolution of the problem, and is indicated through a documented authorization process (e.g., Change Control Board signoff)." — AC 00-71 § 4.1.5 [S7]
- Assessment of leaving open: "PR Assessment – a means to assess the effect of having a PR remain open at the time of approval." — AC 00-71 § 4.1.3 [S7]
- Disposition: "OPRs classified as 'Significant' per the classification in paragraph 6.1, for which no sufficient mitigation or justification exists to substantiate the acceptability of the safety effect, should be resolved prior to approval." — AC 20-189 § 6.3 [S8]
- Mitigation by others: "A mitigation that is controlled by another stakeholder may be considered in the classification only if validated with that stakeholder" — AC 20-189 § 6.1.3 [S8]

**Deferral — gap**
- See § 4 "Deferral records — gap". The only quoted U.S. act-word is "potentially deferrable" (AC 120-16G Figure 7-1) [S3]. [reading] In the civil texts read, an inoperative item is a placarded discrepancy listed to the owner (§ 43.11(b)); there is no read text for the act of deferring, its approval or its time limit.

**Corrective action / followup (CASS)**
- "continuing surveillance, investigation, data collection, analysis, corrective action, and corrective action followup" — AC 120-16G § 1-6b [S4]
- "and for the correction of any deficiency in those programs" — § 121.373(a) [S5]

**Monitoring; intervention; transfer of roles** (flight deck)
- "Transfer of PF and PM roles should be done positively with verbal assignment and verbal acceptance to include a short brief of aircraft state." — AC 120-71B § 6.4 item 4 [S9]
- "Considerations for the decision to take over control should include subtle incapacitation or no response or flightpath correction after two challenges." — AC 120-71B § 6.6.2.1 [S9]
- "If the sequence cannot be re-established or the crew is unclear on where to resume the checklist, the appropriate section of the checklist should be reaccomplished from the beginning." — AC 120-71B § 5.2.3 [S9]

**EU comparison — certificate of release to service** [S11]
- "A certificate of release to service shall be issued by appropriately authorised certifying staff on behalf of the organisation when that certifying staff has verified that all the maintenance that was ordered has been properly carried out by the organisation in accordance with the procedures specified in point 145.A.70, taking into account the availability and use of the maintenance data specified in point 145.A.45, and that there are no known non-compliances which endanger flight safety." — 145.A.50(a) [S11]
- "A certificate of release to service shall be issued before flight at the completion of any maintenance." — 145.A.50(b) [S11]

## 6. Independence rules

1. Doer may not inspect own work (prohibition on the person): "No person may perform a required inspection if he performed the item of work required to be inspected." — § 121.371(c) [S2]
2. Doer may not inspect own work (manual duty on the carrier): "Instructions to prevent any person who performs any item of work from performing any required inspection of that work." — § 121.369(b)(7) [S2]
3. Stated as the primary concept: "A primary concept of the RII function is to prevent any person who performs any item of work from performing any required inspection of that work (§§ 121.369(b)(7) and 135.427(b)(7)). Therefore, it is important that you identify RIIs whenever possible so that everyone knows that an RII is required." — AC 120-16G § 7-2c [S3]
4. Organizational separation: "Each person performing required inspections in addition to other maintenance, preventive maintenance, or alterations, shall organize the performance of those functions so as to separate the required inspection functions from the other maintenance, preventive maintenance, and alteration functions. The separation shall be below the level of administrative control at which overall responsibility for the required inspection functions and other maintenance, preventive maintenance, and alteration functions are exercised." — § 121.365(c) [S2]
5. Inspector under an inspection unit at the time of inspection: "No person may allow any person to perform a required inspection unless, at that time, the person performing that inspection is under the supervision and control of an inspection unit." — § 121.371(b) [S2]
6. Inspector's decision protected from countermand: § 121.369(b)(8), quoted in § 5 above. [S2]
7. Inspector authority written and bounded: "shall give written information to each person so authorized describing the extent of his responsibilities, authorities, and inspectional limitations." — § 121.371(d) [S2]
8. Supervised worker may not perform inspections: "However, this paragraph does not authorize the performance of any inspection required by Part 91 or Part 125 of this chapter or any inspection performed after a major repair or alteration." — § 43.3(d) [S1]
9. Performer and approver may be different persons (permitted, not required): "when work is accomplished by one person and approved for return to service by another, the dates may differ. Two signatures may also appear under this circumstance" — AC 43-9D § 8.5 [S3]
10. Release certifies the independent inspection occurred: "All items required to be inspected were inspected by an authorized person who determined that the work was satisfactorily completed" — § 121.709(b)(2)(ii) [S2]
11. Flight-deck independent confirmation (not maintenance): "Critical items should be verified by both the PF and PM. ... Inertial platform alignment and computer programming should be accomplished by one crewmember and independently confirmed by another." — AC 120-71B § 5.2.2.5 [S9]
12. Concurrent roles held by two people: "At any point in time during the flight, one pilot is the PF and one pilot is the PM." — AC 120-71B § 6.4 item 1 [S9]
13. Problem report closure by formal review separate from resolution: "Resolved – … verified but not formally reviewed and confirmed." / "Closed – A resolved problem report that underwent a formal review and confirmation of an effective resolution of the problem." — AC 00-71 § 3.2 [S7]

[reading] on independence:
- Independence in the U.S. maintenance regulations read is required only for **required inspections**. No text read requires that the person approving for return to service be different from the person who did the work; § 43.9(a)(3) presumes they are often the same ("if other than the person specified in paragraph (a)(4)").
- Independence has three layers: person (§ 121.371(c)), organization (§ 121.365(c), "below the level of administrative control"), and decision protection (§ 121.369(b)(8)). Only one person or level may overrule the inspector.
- The inspector may be in the same company as the doer; § 121.365(c) separates functions, not employers.

## Counts

- Source files read: 11 (9 with quoted text; S10 metadata/paraphrase only; S11 three quoted points, EU).
- Role entries: 20 (incl. 1 EU comparison). Kinds-of-work entries: 11. Document/record entries: 12 (incl. 1 gap). Acts/states entries: 13 (incl. 1 gap, 1 EU comparison). Independence rules: 13.
- Gaps named: Part 65, Part 145, § 119.65 (DOM/chief inspector), § 91.213 / § 121.628 (MEL/deferral), Part 43 Appendices A, B, D, primary PDFs of four ACs.
