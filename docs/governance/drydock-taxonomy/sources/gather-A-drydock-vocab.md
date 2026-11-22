# Gather A — the drydock vocabulary and the change ladder

Gathered 2026-11-22 for `docs/governance/drydock-taxonomy.md` § 9 items 1 and 2. Read-only; no repo file
edited, no writing `gz` verb run. Status key: **RULED** (an operator ruling found, quoted), **SOURCED**
(defined in canon or code, no operator ruling found after full reading of the listed sources),
**CONTRADICTED** (two sources disagree, both quoted), **UNSOURCED** (used, nowhere defined).
Abbreviations for paths:

- `DOC` = `docs/governance/safe-mode-doctrine.md`
- `CON` = `docs/governance/harbor-pilotage-candidate-2026-10-15.md` (the contract)
- `KIT` = `docs/governance/harbor-ro12-contractor-kit.md`
- `R13` = `docs/governance/harbor-ro13-mode-contract.md`
- `R5` = `docs/governance/harbor-ro5-work-packages.md`
- `MCR` = `.gzkit/rules/mode-contract.md`; `MXR` = `.gzkit/rules/mx-mode.md`
- `SK` = `.gzkit/skills/gz-mx/SKILL.md`; `TPL` = `.gzkit/templates/safe_mode_contract.md`
- `REC` = `docs/rnd/contractor-kit.md` (R&D record; read by section, see Files read)
- `RWO` = `docs/rnd/repair-work-organization.md` (R&D record; decisions read by section)
- `P0` = `docs/rnd/renewing-vows/doctrine-merge.md` Part 0 § Terms (ratified 2026-10-10, *"ratify Part 0"*)
- `RM` = `docs/governance/ieee/requirements-model.md`
- Code: `ev` = `src/gzkit/events.py`; `mk` = `src/gzkit/mx/marker.py`; `al` = `src/gzkit/mx/alarms.py`;
  `cp` = `src/gzkit/mx/checkpoint.py`; `inv` = `src/gzkit/mx/invariants.py`; `aw` = `src/gzkit/mx/awareness.py`;
  `to` = `src/gzkit/mx/tag_out.py`; `wpl` = `src/gzkit/work_package_ledger.py`; `pg` = `src/gzkit/cli/parser_governance.py`

## Domain 1 — the drydock vocabulary

| # | Term | Meaning as stated (quote) | Defined | Code | Status | Synonyms / rejected; § 1 collision |
|---|---|---|---|---|---|---|
| 1 | **drydock** | *"The ship is out of the water so the structure can be repaired and realigned ... designs and lands the new structures; it does not populate them"* | DOC:51; P0:135 *"The structural rebuild out of the water"* | `mk` `Level` value `"drydock"` (mk:39) | RULED — operator 2026-10-17, DOC:15: *"drydock is an extreme measure. the A,B,C,D system is aeronautical, but scheduled checks. the drydock metaphor, although nautical, is more - for me - an on-demand and drastic"*; 2026-11-03 synonym of hangar, RWO:227 *"These are synonyms for sure, so option A"* | synonym: hangar (ruled); *availability* not taken (REC:3053) |
| 2 | **hangar** (Maintenance Hangar, MX) | DOC:21 (superseded in place) *"The hangar level is standing maintenance, a hangar visit that answers one squawk"*; DOC:27 *"Hangar and drydock are synonyms"* | DOC:21, 27; SK:17-23 | `mk:39` `Level = Literal["hangar","drydock"]`; `al:35` alarms off only at `"drydock"`; `pg:884-886` `--level` choices `hangar`/`drydock`, help *"hangar (default): one squawk"* | CONTRADICTED — ruled synonym (RWO:231 *"Hangar and drydock are synonyms for the out-of-service place"*) vs code keeps two levels with different behaviour (`al:27-35`; `aw:145` banner) and MCR:22 *"the hangar level and the drydock level"*; DOC:21 says the text "describes the mechanism until" GHI #1304 | `MX`, *maintenance hangar*; § 1 collision: "level" |
| 3 | **maintenance mode** (standing) | *"Maintenance mode is standing: the Maintenance Hangar, the chores, the patch releases, and the GitHub issues that carry repair, refactor and address work"* | DOC:15; CON:61 | none distinct (the `mx` marker) | RULED — 2026-10-17, DOC:15 *"I'd like maintenance mode and GitHub issues to be very tightly coupled"*; CON:490 *"maintenance mode is really rich... I just am able to go to safe mode occasionally"* | — |
| 4 | **safe mode** | *"the condition at the drydock level"* (DOC:21); P0:130 *"The regime for a crisis the ordinary ceremony cannot govern"* | DOC:13-21; P0:130 | `ev:1068` `mode: Literal["mx","safe"]`; `mk:40` `LEVEL_OF_MODE {"mx":"hangar","safe":"drydock"}`; `aw:33-40` banner | RULED — 2026-10-16 *"A, extend gz mx with a safe mode - which is 'martial law' toggle"* (CON:1794); *"safe mode is the sole term, update the canon"* (CON:1803) | rejected: *martial law* (CON:1803) |
| 5 | **out of service** | *"The vessel is out of service exactly while the MX flag, `.gzkit/mx.json`, is open"* | DOC:27; MXR § Out of service | `mk.condition` (mk:270-288) reads it; no field named out-of-service | RULED — RWO:203 *"yes, out of service means the marker is open is also very strong"*; DOC:27 *"These are synonyms for sure, so option A"* | *out-of-service package* withdrawn (RWO:259) |
| 6 | **on the line** (line work) | *"Work done with every alarm on is on the line, a GHI fixed directly included"* | DOC:28; RWO:205 | none | RULED — RWO:205 *"on the line is the operator's word for that state"*, from RWO:203 *"remain underway or out on the line"* | operator's speech: *gate apron*, *dock level work* (RWO:227), not adopted |
| 7 | **alarm test** | *"Work that must lower an alarm, or that changes a control or the standard one judges by, is out of service"* | DOC:28; RWO:237-239 | none | RULED — RWO:239 *"the alarm test decides, and I like it"* | — |
| 8 | **standby level** | DOC:21 *"one condition with a standby level commanded at entry: hangar or drydock"* (superseded in place 2026-11-03); MCR:23 MEL entry *"level per standby level"* | DOC:21; MCR:22-23; R13:10 | `mk:81-89` field `level`; `pg:884` | CONTRADICTED — REC:2744 ruled two levels (*"A"*, 2026-10-27) then RWO:233 reversed: *"RO-13's level per standby level and every mode-contract paragraph naming both standby levels read one level"*; still MCR:23 and R13:10 (*"that re-reading is open for this specification"*) | § 1 collision: "level" |
| 9 | **standby** (the command) | *"safe mode's command to modules to reduce their level of operational compliance"* | REC:2251 | none (RP-13 F2 unbuilt) | RULED — operator 2026-10-26, REC:2236-2237 *"safe mode, on the other hand, could tell modules to reduce their level of operational compliance. You know, this is what I meant by a standby mode."* (ruled in principle, REC:2243) | REC:2087 earlier *"Standby is still unsourced"*, then settled |
| 10 | **the condition** (on / absent / unreadable / unbound / exiting) | *"The condition is on only when the marker is present, parses, is bound to a still-open `mx_session_opened` event and is not exiting"* | DOC:21; MXR § Honor the marker; MCR:22 | `mk:43` `ConditionCause`; `mk:270-288` `condition()` | RULED — 2026-10-27, REC:2719-2725 operator *"A"* | *non-operational condition*, *operational condition* (MCR:22) |
| 11 | **marker** (`.gzkit/mx.json`) | *"the single filesystem truth-source for MX mode"* | ADR-0.0.74; `mk:1-17` | `mk:29` `MARKER_RELPATH`; `mk:61-99` `Marker` | RULED — committed to the repo, REC:2707 operator *"A"* (2026-10-27) | *MX flag* (DOC:27) |
| 12 | **check levels** Transit, A, B, C, D | DOC:29-37 table: A *"inspect and report"*, B *"repair that touches no control"*, C *"repair that may reach a control"*, D *"re-author a control or its standard"* | DOC:29-39; RWO:343-357 | `ev:2109` `TagCheckLevel = Literal["C","D"]`; `to:68-69` | RULED — RWO:345 *"yes, adopt the four levels - use the rich detail we found"*; DOC:39 *"B for now until we have more maturity"* | *letter check* (operator), *line* / *heavy maintenance* (FAA); § 1 collision: "level", and four check levels vs four work levels |
| 13 | **standard disconnect list** | *"Each level means more disassembly and disconnection, by a standard disconnect list, the manual"* | DOC:40; RWO:359-367 | `ev:2105` `TagSource` value `"standard-disconnect"`; no list exists | RULED — RWO:361 *"each level means more disassembly and disconnection"* (not built: *"the lists wait on the design-for-service R&D run"*, DOC:40) | *the manual*; blanket = RP-13 group entry |
| 14 | **squawk** | *"the on-demand repair of one reported discrepancy: the GitHub issue is the write-up"* | DOC:15 | none | RULED — 2026-10-17, DOC:15 *"the exiting mx system does have on-demand 'squawk' modes as well"* | — |
| 15 | **problem report** and its states (recorded, classified, resolved, closed) | *"In its role the GitHub issue is a problem report (AC 00-71 § 3.1) ... the fix commit's SHA witnesses resolved, and only a review ... closes it"* | DOC:15; REC:3059 | `ev:1869-1881` `work_package_issue_closed` | RULED — B12, DOC:15 operator *"A"* (2026-10-27) | — |
| 16 | **return to service** (the act) | *"the operator's act at that package's close, apart from each order's Gate 5, and the flag closes on it"* | DOC:41; RM:275-277; P0:125-129 (amended) | none: no event, no verb; KIT ruling 32 gates it (unbuilt, KIT:61 row 14 "Partial") | RULED — RWO:554 *"Option A"* (2026-11-03) | P0 before 2026-11-03: *"Gate 5 attestation, which is return to service"* (amended); collision with § 1 Epic row ("Return to service package") |
| 17 | **return to service package** | *"Every opening of the flag has a return to service package ... written from diagnosis for an incident, where the drydock contract is that package; generated from the level for a scheduled check"* | DOC:41; TPL:7-10; RWO:404-408; RM:255 | none (GHI #1303; `SK:65-66` *"until GHI #1303 makes the verb require it, the skill asks and --reason names it"*) | RULED — RWO:406 *"a"*; name RWO:255 *"it should be called a return to service package"* | withdrawn: *out-of-service package* (RWO:259); held, not ruled: *return to service plan* (RWO:249); = § 1 Epic, repair column |
| 18 | **dock trial** | REC:641 *"each job order states its dock trial (its own witness, its alarms reconnected, run by the restorer, inspected, before return to service)"*; KIT ruling 27 (KIT:469) *"Each order's dock trial runs its own refusal tests at full strength, each refusal shown red then green, with gz check"* | REC:633-654; KIT:94-106, 469, 820 | none (scripts under `docs/governance/harbor-ro12-dock-trial-evidence/`) | RULED — REC:645 *"Yes, I like A's compromise"*; KIT:469 *"A"*; narrowed by ruling 201, KIT:820 *"Item 5 governs"* (from O5 no full-strength dock trial) | REC's *"run by the restorer"* superseded by KIT ruling 27 (working session runs, independent reviewer inspects) |
| 19 | **sea trial** | DOC:53 *"done by the normal crew rather than the contractors, in one of two approved forms. Best: a fresh project on the released wheel ... Better: an increment of real work in gzkit itself"* | DOC:53; CON:447-459 (exit item 10) | none | CONTRADICTED — ruled REC:675 *"A"* (and *"Make the two an OR ..."*), but P0:136 still reads *"Sea trial. One work package run on a fresh install of the released wheel"* and TPL:117 *"The sea trial belongs to civil rule's first voyage, not to the exit"* | REC:603 *"Sea trial stays contested"* (term) |
| 20 | **seaworthy / seaworthiness** | *"The structure is repaired and its witnesses read true; the ship can sail under normal ceremony without choking"* | DOC:53; P0:137; CON:413 (§ Exit — seaworthiness) | none | RULED — P0 ratified (*"ratify Part 0"*): *"Seaworthy. The one condition on which safe mode ends."* | — |
| 21 | **handback** | *"The amendment the operator ratifies at seaworthiness, in the form of a transfer of custody"* | DOC:54; P0:137-138; SK:138-153 | none (KIT ruling 33's drafting verb unbuilt; witness floor row 15 "Nothing", KIT:62) | CONTRADICTED — CON:415-416, 434 makes the ratified handback an exit condition (*"Safe mode ends when ... 9. The handback amendment is ratified"*) vs DOC:99 *"The handback amendment follows the exit and precedes civil rule"* and SK step 6 after step 5 | — |
| 22 | **transfer of custody** | *"It enumerates three categories: every open discrepancy ..., every departure from specification the hangar accepted, and each deferred action with its new holder. An empty category is stated as none"* | DOC:54; SK:143-153; REC:3018-3040 | none | RULED — C12, REC:3030 operator *"A"* | — |
| 23 | **civil rule / civil control; voyage** | DOC:55 *"Normal voyages. Ordinary operations under the new structures"*; P0:138-139 *"Voyage. Ordinary operations under the Magna Carta"* | DOC:55; P0:138; CON:32-45 | none | RULED — operator 2026-10-15, CON:32-34 *"From this martial law back to 'civil control.'"*; P0 ratified | *magna carta (civilian rule)* (CON:45) |
| 24 | **martial law** | the operator's early word for safe mode | CON:32-45 | none | RULED (retired) — CON:1803 *"safe mode is the sole term, update the canon"*; survives only in quoted words | rejected synonym of safe mode |
| 25 | **Magna Carta** | the campaign; P0:118 *"the Magna Carta is gzkit's"* | P0:117-118; CON:33 | none | SOURCED (P0 ratified as the campaign's name; the operator's word) | — |
| 26 | **harbor** (phase) / harbor legs | P0:135 *"Harbor. The passage in: the load cuts and the instruments"*; CON:1490 regime row | P0:131-135; CON:1475-1510 (superseded record) | none | CONTRADICTED — AGENTS.md:237 and P0:131-132 *"one exceptional period through harbor, drydock and sea trial"* vs DOC:103 (operator 2026-10-17 corrected it, *"your whole dry dock plan was ill conceived"*) and CON:1208-1212 (*"Superseded on 2026-10-17 (record, not binding)"*) | — |
| 27 | **harbor pilot** | *"The strongest model available, booked by the operator, takes the conn ... plans, measures, diagnoses and takes rulings with the operator"* | DOC:50; P0:132-134 | none | RULED — CON:27-28 *"I basically want a VERY POWERFUL model to take over, like a harbor pilot"*; P0 ratified | *the pilot*; *the session* in CON § Division of labor (CON:304) |
| 28 | **pilotage chart** | P0:139 *"the leg-by-leg instrument"* | P0:139; CON:1475-1496 (superseded) | none | SOURCED (P0 ratified; the chart itself superseded 2026-10-17) | — |
| 29 | **passage log** | DOC:62 *"One row per act: what changed, the measurement before and after, the commit, the witness"* | DOC:62; CON:1782ff | becomes a view (KIT ruling 8) over `ev:2267` `entry_booked` | RULED — KIT ruling 8 (KIT:433) *"A"*: *"The passage log becomes a view over these events"*; ruling 10 (KIT:435) frozen as written | — |
| 30 | **contract** (safe-mode contract) and its pin | DOC:59 *"Written before entry, from the template ... changes only by its own amendment, never through a repair order"* | DOC:59; TPL; SK:83-103 | `src/gzkit/mx/contract.py:24` `AMENDED_EVENT = "mx_contract_amended"`; `ev:1071-1076, 1142-1157` | RULED — CON:3 *"ratify the contract"*; B1 DOC:59 *"A"*; pin CON:1821 *"Hash at entry + amend event (Rec.)"* | = the return to service package for an incident (DOC:41); *master agreement* (DFARS) |
| 31 | **general arrangement; band** | DOC:60 *"The drawing of the target structure ... Every repair order names the band it serves"* | DOC:60; CON:86-268 | none | RULED — CON:553-557 *"Yeah. It's very clear to me that we have no business leaving dry dock without that being clear"*; CON:705 *"A"* | — |
| 32 | **MEL** (Minimum Equipment List) | REC:2062-2073 *"one list of controls, its Minimum Equipment List"*; MCR:23 entry fields | MCR:23; R13:34; REC:2057-2092 | none: F1 (the MEL model) unbuilt (R13:42); `ev:2105` `"mel-bypass"` source only | RULED — REC:2079 *"A: MEL with Meyer levels (Recommended)"* | — |
| 33 | **(M) bypass procedure** | AC 91-67 ¶ 6r(2): *"accomplished before beginning operation with the listed item of equipment inoperative"*; REC:2066 *"performed by the repairing craftsman and recorded on the tag-out log"* | MCR:23; REC:2027-2030, 2066 | `ev:2105` `TagSource` `"mel-bypass"`; KIT § Mode Contract column "(M) bypass" (KIT:403) | RULED — same ruling (REC:2079) | — |
| 34 | **(O) limitation** | *"the condition the system runs under without it"* (REC:2068); MCR:24 *"otherwise inoperative under its (O) limitation"* | MCR:23-24; REC:2068 | prose only (KIT Mode Contract rows, KIT:412-421) | RULED — same ruling (REC:2079) | — |
| 35 | **placard** | *"the notice the port gives every affected party at the place of call (AC 91-67 ¶ 7c)"* | MCR:23; REC:2069 | none (GHI #1299, CON:1903) | RULED — same ruling (REC:2079) | — |
| 36 | **restore condition and deadline** | *"at the latest the exit re-run"* | MCR:23; REC:2071 | none | RULED — same ruling (REC:2079) | — |
| 37 | **built-in self-test; suitability for function** | MCR:24 *"suitable when its latest result passed within the declared interval"* | MCR:24; R13:14, 46; REC:2246-2250 | none (F5 unbuilt) | RULED — REC:2230-2234 operator's words; R13 ruling 9 *"a"* | BITE unsourced (REC:2261) |
| 38 | **accepted state / not yet accepted** | REC:2466-2468 *"accepted and lowered ... or not yet accepted"* | MCR:23; R13:27, 68; KIT ruling 18 | KIT Mode Contract "Accepted" column (prose) | RULED — REC:2472 *"A: one condition (Recommended)"*; KIT:443 ruling 18 *"A"* | *factory floor*, *assembly mode* folded in (REC:2474) |
| 39 | **inoperative** | AC 91-67 ¶ 6k *"does not accomplish its intended purpose"* | MCR:24; REC:2263 | none | SOURCED (AC 91-67's term adopted under the MEL ruling) | — |
| 40 | **mode contract** (two-way) | MCR:18 *"Every new control ... carries the two-way mode contract from its first commit"* | MCR; R13:14; KIT § Mode Contract | none mechanical (MCR:28 *"Advisory: no mechanical witness yet"*) | RULED — operator 2026-10-26, MCR:18 *"an overarching design requirement permanently and always with everything we build"* | — |
| 41 | **group entry** (temporary) | R13:25 *"The checkpoint is one temporary group entry"* | R13:25; DOC:40 (*"the blanket"*) | none | RULED — R13 ruling 4 *"a"* | *the blanket* |
| 42 | **the floor / `GATE5_INVARIANTS`** | DOC:94 *"Gate 5 attestation; the ledger through verbs; operator PII; the PRIME DIRECTIVE; and no control is removed. These are the hangar's gate5_invariants"* | DOC:94; MXR | `inv:26-34` `{"gate5-attestation","secrets","operator-pii","ledger","grader-gaming"}`; `cp:33` | CONTRADICTED — DOC:94's list vs `inv:26-34` (code adds `secrets`, `grader-gaming`; has no PRIME DIRECTIVE or no-control-removed member) | — |
| 43 | **advisory / demotion** | MXR: *"advisory means non-grounding, never discarded"* | MXR; `cp:110-125` | `cp:18-37` `resolve`; `src/gzkit/mx/disposition.py:45` `Route.ADVISORY` | RULED — R6 2026-10-17 *"A"* (CON:499-500) | — |
| 44 | **alarm / slow alarms** | `al:1-12` *"An alarm hook runs through python -m gzkit.mx.alarms"* | DOC:63; CON:283 | `al:27-52` | RULED — 2026-10-25 CON:283 *"... then we adjust tests and turn the "security alarms" back on"* | *security alarms* |
| 45 | **tripwire** | DOC:63 *"checks that measure the old structure go off, or become tripwires that record collateral disturbance without ringing"* | DOC:63; R13:55 | none | SOURCED (RP-10 rubric parked, CON:411) | Caution tag = *"a tripwire that records"* (TPL:97) |
| 46 | **pinned CRITICAL; fast static checks** | DOC:63 *"Lint and the fast static checks stay on and pinned CRITICAL"* | DOC:63; MXR § Opting a guard | `cp:35` (`emitted_level != CRITICAL`) | RULED — 2026-10-27, DOC:63 *"somebody sweeps up the shop floor every night"* | — |
| 47 | **tag-out log** | REC:1084-1086; KIT ruling 4 *"The tag-out log is ledger events, the log a derived view"* | DOC:54; KIT:429; TPL:94-98 | `ev:2125-2264`; `to:172-210` `tag_log`, `open_tags` | RULED — REC:1088 *"A"* (*the isolation is the Navy's tag-out*); KIT:429 *"A"* | rejected: *lockout log*, *compliance register* |
| 48 | **tag class: Danger / Caution** | TPL:96-97 *"a Danger tag (an alarm off and locked) or a Caution tag (a tripwire that records)"* (also REC:1084) | TPL:96; REC:1084; KIT ruling 5 | `ev:2098-2099` comment *"Danger forbids operating the surface, Caution limits it"* | CONTRADICTED — TPL:96-97/REC:1084 vs `ev:2098` (two different definitions) | ruled REC:1088 *"A"* |
| 49 | **line item** | KIT ruling 5 (KIT:430) the typed fields; JFMM I-13.2.c *legible to a worker not involved* | KIT:430, 659 | `to:88-100` `LINE_ITEM` | RULED — KIT:430 *"A"*; ruling 120 *"A: issue carries item (Rec.)"* | — |
| 50 | **issue / hang / clearance authorized / clear** | KIT ruling 6: *"Issue by the coordinator as Authorizing Officer, then hang by the repair dispatch ...; clearance authorized by the coordinator, then clear by the restoration dispatch"* | KIT:431 | `to:278-372, 402-495, 527-591, 708-771`; `ev:2125-2264` | RULED — KIT:431 *"A"* | — |
| 51 | **position hung / position found / out of position** | `ev:2101` `off, advisory, recording`; found adds `on` (KIT ruling 140) | KIT:430, 693, 699 | `ev:2101, 2115`; `to:669-705` `_block_out_of_position` | RULED — KIT:430 *"A"*; ruling 137 *"A: book an order block (Rec.)"*; ruling 140 *"A: hung positions + on (Rec.)"* | collision: tag position `advisory` vs demotion `advisory` |
| 52 | **not available** (repair activity) | KIT ruling 7: *"the event records the repair activity not available (TUM 1.8.4.a)"* | KIT:432 | `ev:2220` `repair_activity: Literal["not-available"]` | RULED — KIT:432 *"A"* | — |
| 53 | **Authorizing Officer** | the coordinator's duty to issue and clear (REC:1086) | REC:1086; KIT:431 | `to:4-6` docstring; `ev:2128` | RULED — REC:1088 *"A"* | — |
| 54 | **tag source** | KIT ruling 124 *"the order's own work, a standard disconnect list entry, an MEL (M) bypass and a surveillant's stop"* | KIT:667 | `ev:2105` | RULED — KIT:667 *"A: four kinds, no ref (Rec.)"* | — |
| 55 | **lockout** | dropped as a mode signal; earlier the isolation's name | R13:31; CON:917-920 | none | RULED (retired) — R13 ruling 10 *"A"*: *"Lockout is dropped as a mode signal"*; REC:1091 lockout → tag-out | rejected: *lockout*, *lockout log*, *lockout/tags-plus* |
| 56 | **maintenance record; entry** | DOC:54 *"the permanent work under 14 CFR § 43.9(a)"*; KIT ruling 8 *"one entry event carrying what was done ..."* | DOC:54; KIT:433, 751, 753 | `ev:2267-2296` `entry_booked`; `ev:1891` `ENTRY_ID_PATTERN`; `src/gzkit/mx/entries.py` | RULED — REC:823 three-records decision; KIT:433 *"A"*; ruling 166 *"A: Subsume (Rec.)"* | the MX log is its view (ruling 166) |
| 57 | **list of discrepancies; discrepancy; grade; source** | DOC:63 *"one line per discrepancy, graded blocks return to service or due by a named event"*; KIT ruling 9 sources *"left broken, an inspector's rejection, or found in the work"* | DOC:63; CON:1608-1618; KIT:434 | `ev:2118, 2122, 2299-2369`; `src/gzkit/mx/record_rows.py:22` `DUE_BY` | RULED — REC:1558 *"B′"*; KIT:434 *"A"* | — |
| 58 | **punch list / compliance register** | retired: REC:3207 *"punch list retired, unsourced"*; DOC:61 *"register is retired inside the hangar"* | REC:1536-1563, 3204-3211; KIT ruling 21 rejected-synonym list | `aw:39` banner *"what it breaks goes on the punch list"* | CONTRADICTED — retired (REC:1558 *"B′"*; KIT:447 lists *punch list* as a rejected synonym) vs live in `aw:39` and MXR:144 *"binds through the contract's punch list"* | ruling 21's term witness is scoped to the kit personas and skill only (KIT:447) |
| 59 | **deferred finding** | CON:385-386 *"a deferred finding, carried into civil rule with a named holder and a revisit condition, and never a new order"* | CON:382-386, 519-527, 574-577 | none | RULED — CON:512-515 *"this is perfect. are we using it?"*, *"record it now as a ruling"*; CON:576 *"yes, hand it to the owning outcome"* | — |
| 60 | **induction freeze (work scope frozen at induction)** | CON:382-384 *"the orders are RP-0 to RP-13 as the table stood ... A finding raised from then on is graded, not added"* | CON:382-386, 517-518 | none | RULED — CON:512-515 (as row 59) | — |
| 61 | **work package log; register** | DOC:61 *"a Layer 3 view assembled from the repair work packages, their issues and the ledger, never edited ...; register is retired inside the hangar"* | DOC:61; CON:354-358; TPL:77-80 | none (no producer) | CONTRADICTED — B11 ruled (DOC:61 *"A"*) yet SK:90 *"§ Repair orders (the register, ...)"* and SK:231 *"the register are read"* | rejected: *register* inside the hangar |
| 62 | **restoration; restored / reconnected / retired / replaced** | CON:1630-1633 the four dispositions; DOC:52 *"Restoration is part of the order"* | CON:388-392, 1628-1635; DOC:52 | none (dispositions are prose lines) | RULED — CON:388 *"the renovation contractor must reattach all safeguards ..."*; CON:1628 *"yes, that is fine, it works well"* | — |
| 63 | **commencement of work** | REC:2938-2940 *"the coordinator records commencement of work once every surface the package works has its tag-out entry hung"* | REC:2933-2949; KIT:24 | `ev:1786, 2035` state `"commenced"` | RULED — C1, REC:2941 *"A"* | — |
| 64 | **final inspection and acceptance; closeout** | DOC:90 *"a work package closes by final inspection and acceptance ... then closed"*; *closeout* the release's act alone | DOC:90; REC:2970-2991; KIT:439 | `ev:1786, 2035` `"accepted"`, `"closed"` | RULED — C10, REC:2981 *"b"*; KIT ruling 14 *"A"* (at the order) | rejected: *closeout review* |
| 65 | **shift turnover** | REC:3003-3006 *"at every session relief in the hangar the relieving session reviews the tag-out log ..."* | REC:2993-3016; KIT:444 | none (refusal 7 "Nothing", KIT:54) | RULED — C11, REC:3007 *"a"*; KIT ruling 19 *"A"* | rejected: *position relief briefing* |
| 66 | **MX session (holder); lease; renew; lease expired; advisory debt** | KIT ruling 3 *"A hung tag and the mx-session lease are held by the MX session id that gz mx enter mints"* | KIT:428, 717; MXR § The lease | `mk:48` `SESSION_LOCK_KEY`; `ev:1092-1124`; `src/gzkit/mx/lease.py:24` | RULED — KIT:428 *"mx session makes sense"*; KIT:717 *"A: mint a fresh id (Rec.)"*; MXR *"at worst, we book a status at least expiry and notify"*, *"Make renewal lease-only ..."*, *"Per contract (Rec.)"* | — |
| 67 | **drydock session** | DOC:15 *"one mx_session_opened to mx_session_closed span with mode: safe and its contract"* | DOC:15; REC:3042-3057 | `ev:1054-1090` | SOURCED — REC:3044 *"Not put to the operator: canon answers it"* | — |
| 68 | **exit; hard gate; exiting** | DOC:99 *"the hard gate that re-runs every guard at full strength"*; `mk:93-99` *"True while gz mx exit re-runs the guards"* | DOC:96-99; SK:126-136 | `mk:93-99` `exiting`; `src/gzkit/commands/mx_cmd.py:422` | SOURCED (ADR-0.0.74; GHI #1257) | — |
| 69 | **marker repair** | `ev:1127-1133` *"rewritten restores the marker ...; removed clears a marker no session backs"* | SK:180-191; DOC:21 | `ev:1127-1139`; `mx_cmd.py:545` | RULED — `ev:1130` and DOC:21 *"b"* (2026-10-31) | — |
| 70 | **full-strength report** | MXR: CI's job *"reports without failing the run"* | MXR § Honor the marker | `cp:40-50` `GZKIT_MX_FULL_STRENGTH` | RULED — MXR (2026-10-26) *"report only, decide within #1273"* | — |
| 71 | **factory floor / assembly mode** | REC:2360-2363 *"A provision ... is built in as part of assembly, but held disabled"* | REC:2352-2374, 2461-2477 | none | RULED (amended away as a signal) — REC:2472 *"A: one condition (Recommended)"*: *"It survives as the not yet accepted state"* | operator's *assembly mode* (REC:2446) |
| 72 | **care rule (governors off)** | DOC:42 *"Running past a disabled limit is a deliberate act of diagnosis or test, noted as such"* | DOC:42; KIT:10 | none | RULED — DOC:42 *"while the governors are disabled don't overrev the engine"* | — |
| 73 | **pivot / airworthiness directive** | DOC:44 *"Each change is noted in the manual as an airworthiness directive would be"* | DOC:44 | none | RULED — DOC:44 *"this is the best time to pivot, this is exactly why we are in dry dock"* | — |
| 74 | **bootstrap** | CON:318-327 the operator and a working session build RP-12 before any repairer exists | CON:318-327; KIT ruling 26-27 | none | RULED — CON:323-325 *"... we'll improvise and innovate until we have a pattern to build from. A."* | — |
| 75 | **airlock** (transit gate) | CON:125 *"Airlock: transit gate, slice from modules"*; CON:222-224 | CON:125, 222-224 | `ev:1341-1388` `airlock_in`/`airlock_out` | SOURCED (gathered for its MX-adjacent use only; `disposition.py:10` also says *"defect airlock"*) | collision: "defect airlock" in `disposition.py:10` names the hangar/GHI route, not transit |
| 76 | **AOG** (`aog-mx-hangar` route) | `disposition.py:38` *"CRITICAL — ground the session into the hangar"* | ADR-0.0.74 item 12 | `src/gzkit/mx/disposition.py:38` `Route.AOG_MX_HANGAR` | SOURCED (code; the acronym is nowhere expanded in the sources read) | — |
| 77 | **GZ_<LEVEL> severity levels** | `levels.py:1-12` CRITICAL ... DEBUG, NOTICE 25 | ADR-0.0.74 item 11 | `src/gzkit/mx/levels.py:19-28` | SOURCED | § 1 collision: "level" (a fifth sense) |
| 78 | **quay** | CON:1797 *"the chart's H8 and the quay name the skill"*; CON:1798 *"the exit at the harbor's quay"* | nowhere | none | UNSOURCED — read every listed source whole; used only in two superseded passage-log rows | — |
| 79 | **incident (response)** | DOC:41 *"written from diagnosis for an incident"* | DOC:41; RWO:245, 249 | none | SOURCED — RWO:249 *"Held for the operator's word ... not yet ruled: ... everything else out of service is incident response"* | — |
| 80 | **heavy check / hangar visit** | DOC:15 *"the hangar visits taken on cadence"*; DOC:21 *"a hangar visit that answers one squawk"* (superseded) | DOC:15, 21; CON:509-513 | none | SOURCED | the shallow depth withdrawn (RWO:229) |

## Domain 2 — the change ladder and the change order

| # | Term | Meaning as stated (quote) | Defined | Code | Status | Synonyms / rejected; collisions |
|---|---|---|---|---|---|---|
| 1 | **change ladder** | R5:44 *"each rung a recorded event on the package"*; four rungs (R5:45-48); *"alteration and departure from specification"* a separate item 4 (R5:51-53) | R5:44-57; KIT:26; REC:1291-1329 | `ev:1787-1790` `WorkPackageRung` six values incl. `alteration`, `departure`; `wpl:46` `RUNGS` | CONTRADICTED — canon: four rungs (R5:57 *"each naming its rung (pen_and_ink \| change_order \| attachment \| supplement)"*; KIT:26 *"the change ladder (pen and ink, change order, attachment, supplement) ...; alteration and departure from specification against the package's own specification"*) vs code `ev:1787` comment *"The change ladder's rungs, with alteration and departure from specification"*, six values; the draft § 5 repeats the six | collision: the 2026-10-05 *ladder* (ADR / engineering order / Release Package / work package / TASK, CON:1516, 1196-1198) is a different ladder |
| 2 | **pen and ink** (`pen_and_ink`) | R5:45 *"administrative changes and resequencing, including the repairer's in-scope reordering ...; approved by the coordinator"* | R5:45; REC:1305 | `wpl:571` approver must be `coordinator`; `wpl:575` keeps superseded content | RULED — REC:1316 *"B avoids collision and fits"* | — |
| 3 | **change order** (the rung) | R5:46 *"a change to scope, boundary or test; work stops when the need is found; issued only by the operator, who approved the original"* | R5:46, 50, 62; REC:1307 | `wpl:571, 575, 577-578` (`work_stopped` true only on a change order); `ev:1858, 1861` (`modules` a change order adds) | RULED — REC:1316 *"B avoids collision and fits"*; R5:62 *"It's a reopening (Recommended)"* (a test change by change order opens a supplement) | DFARS's name for the rung (REC:1320, a marked liberty) |
| 4 | **the change order as the operator's act** | KIT ruling 32 (KIT:479): *"A3 keeps for the operator alone the change order, the attachment, lifting a hold without a resolution and return to service. Each requires --attestor g0 and the operator's exact words ..."* | KIT:479; KIT:61 (witness floor row 14) | not built: `wpl:571` checks a typed `approver` value (`ev:1855` `Literal["operator","coordinator"]`); KIT:61 *"Partial: gz wp change checks the rung against a typed --approver ..., which any caller can type"*; lands with O5 | RULED — KIT:479 *"A"* (2026-11-04) | KIT ruling 76 (KIT:568, *"A: orders closed, no own decision (Rec.)"*) does not concern the change order: it rules a repair package's close (no Gate 5 decision of its own) and says *"Return to service stays the operator's separate act, landing with O5 (rulings 32, 44)"* |
| 5 | **change order on a repair order row** (the contract's usage) | CON:521-522 *"Blocking: worked under its owning order, or by a change order the operator issues within that order's scope"*; e.g. CON:400, 404, 406, 408 *"change order 2026-10-30 ..."* | CON:382-386, 521-522, 1027-1053 | none: RP-n are not store records (draft T4), so these change orders are booked only as contract amendments (`mx_contract_amended`) | CONTRADICTED — TPL:77 *"The table states what each order lands; it is changed only by amendment of this contract"* (so a change order to an RP row amends the contract) vs R5:50 *"A change order never changes the contract (DFARS 217.7103-6(b))"* and DOC:59 *"The contract changes only by its own amendment, never through a repair order"* | — |
| 6 | **attachment** | R5:47 *"added work inside the boundary with no new tag-outs; approved by the operator"* | R5:47; REC:1309 | `wpl:571` (operator); the "no new tag-outs" condition is not checked | RULED — REC:1316 *"B ..."* | — |
| 7 | **supplement** | R5:48 *"a new formal work package within the package"* | R5:48; REC:1310 | `wpl:535-540` requires `supplement` naming *another* work package the store holds | CONTRADICTED — R5:48 (*"within the package"*, a formal work package being the package's instructions, R5:42) vs `wpl:537-540` *"Supplement ... is not another work package the store holds"* (a separate `WP-` record); R5:62 also calls it *"a new work package, a supplement"* | — |
| 8 | **alteration** | R5:52 *"the planned remodel. It is approved in the formal work package before work starts and accounted for at close as a configuration change"* | R5:52, 63; REC:1372-1374 | `wpl:543-544`; `ev:1824, 1828-1830, 2069-2071` (`approved_alterations`, `configuration_changes`) | RULED — REC:1381 *"okay, A is it - make sure the agents/personas/skills are well-versed in these details"*; R5:63 *"Operator, at freeze (Recommended)"* | — |
| 9 | **configuration change** | R5:52 *"in the maintenance record's reconnected, replaced and retired lines, with canon and docs updated"* | R5:52, 66 | `ev:1828` `configuration_changes` | RULED — same as row 8 | — |
| 10 | **departure from specification (DFS)** | R5:53 *"recorded only where the work cannot meet its own approved specification ... A DFS never changes the work"*; CON:1616-1618 *"A shortfall the operator accepts as a departure from specification is a DFS, not a discrepancy"* | R5:53, 64; REC:1375-1377; KIT:438 (ruling 13) | `ev:1789` rung `"departure"`; `wpl:545-550` | RULED — REC:1381 *"okay, A is it ..."* | collision: `ev:1794` `WorkPackageExit` value `"departure"` (an exit from the fix-cycle bound naming a REQ, RO-14 ruling 12) is a different act with the same word |
| 11 | **deviation / waiver** | R5:53 *"a deviation (requested before the work) or a waiver (after the nonconformance is found)"* | R5:53, 64 | `ev:1862` `form: Literal["deviation","waiver"]` | RULED — as row 10 | — |
| 12 | **temporary / permanent; clear-by** | R5:53 *"temporary with a clear-by condition or permanent"* | R5:53 | `ev:1863-1866` | RULED — as row 10 | — |
| 13 | **job order** | DFARS: the repair order's specification (REC:425-433) | REC:425-436, 1324-1326 | none | RULED (retired as gzkit's name) — REC:1316 *"B avoids collision and fits"*, consequence REC:1325 *"job order ... is superseded as gzkit's name and stays only as DFARS's term in the crosswalk"*; R5:50 | rejected: *job order* (and *revision* kept as the REQ's word) |
| 14 | **engineering order (rung)** | CON:1224-1226 *"the engineering order, the feature bundle that succeeds the (m)ADR ..."* (superseded) | CON:1196-1198, 1721 | none | RULED (retired) — CON:494 *"A, no separate document — retire the engineering order rung"* (2026-10-17) | a rung of the other, 2026-10-05 ladder |
| 15 | **revision** | RM:297 *"revision counts editorial amendments only and never resets proof"* | RM:297; KIT:477 | `ev:1778, 1803` | RULED — KIT ruling 31 *"A"* | kept as the REQ's word, not a ladder rung (R5:50) |
| 16 | **contract amendment (B1)** | DOC:59 *"a repair order that needs a contract change stops for a contract amendment first"* | DOC:59; CON:370-375 | `src/gzkit/mx/contract.py:70-98` | RULED — B1 *"A"* | see row 5 |
| 17 | **superseded content, kept** | R5:44 *"the superseded content, which is kept (JFMM I-2.3.7.3.c(2))"* | R5:44 | `ev:1857`; `wpl:575-576` (required for pen and ink and change order only) | RULED — part of REC:1316 option B | — |
| 18 | **approver** | R5:44 *"its approver"* | R5:44-48 | `ev:1855`; `wpl:101, 571` | SOURCED (code); to be replaced by ruling 32's verbatim-words gate (KIT:479), unbuilt | — |
| 19 | **resolution answers** (pen-and-ink change, escalate, rework done, tag corrected, change order, accepted DFS, operator's ruling, buy-back) | KIT ruling 13 (KIT:438) *"a typed answer fitted to its trigger, with evidence the ledger resolves"* | KIT:436-438 | none (O5 unbuilt; witness floor row 10 "Partial", KIT:57) | RULED — KIT:438 *"A"* | the ladder's rungs reused as stop answers |
| 20 | **reopening (by change order)** | R5:62 *"A change order that changes the frozen test opens a new work package, a supplement"* | R5:62; R5:78 | none | RULED — R5:62 *"It's a reopening (Recommended)"* | collision: `ev:1794` exit `"reopen"` and the ruled, unbuilt `catalog reopen` verb (R5:81) |

## Collisions with the draft's § 1 level table

- **"level"** carries five senses: § 1's four work levels (Epic, Story, Order, Action, RM:253-258); the check
  levels Transit/A/B/C/D (DOC:29-37, `ev:2109`); the standby level hangar/drydock (`mk:39`, `pg:884`); the
  `GZ_<LEVEL>` severity ladder (`src/gzkit/mx/levels.py:19-28`); and Meyer's checking level in an MEL entry
  (MCR:23, REC:2083 *"Level is Meyer's word for the setting"*). Two "four levels" sit side by side in DOC
  (§ Out of service and the four levels heads both the check levels, DOC:29, and the work levels, DOC:43).
- **"Order"**: § 1's order row vs P0:121-122 *"Order. How command reaches the work: a standing order ...; a
  tasking order binds one work package"* (ratified); vs DOC:67, TPL:10, CON:78-84, CON § Repair orders, where
  each "order" is an `RP-n` repair package; vs KIT's `O1`-`O9` *"this page's build orders, not ledger orders"*
  (KIT:749); vs *change order*, a ladder rung on a package, not an order-level record; vs *job order*
  (retired).
- **Gate 5 at the order vs the contract's exit item 9**: CON:435 *"each repair order closed through the
  operator's Gate 5"*, where a repair order there is an `RP-n` package, vs KIT ruling 76 (KIT:568) *"A repair
  package ... books no Gate 5 decision of its own"*.
- **Epic / return to service**: § 1's Epic repair cell "Return to service package" has no record, event or
  verb (row 17 above); P0:123-124 before its 2026-11-03 amendment equated Gate 5 with return to service.
- **Action vs act**: § 1's Action/task vs the doctrine's per-*act* records (DOC:62-63, *"one commit per act"*)
  and KIT's *Acts* (KIT:24: initiation, commencement, stop work ...), which are order- and package-level acts.
- **Story "initiation"**: the order is also opened *"only on the operator's words"* (KIT ruling 52, KIT:520),
  so initiation-like operator acts occur at both Story and Order.
- **Two meanings of "advisory"**: a demoted guard (`cp:45`) and a tag's hung position `advisory` (`ev:2101`).
- **Two meanings of "departure"**: the DFS rung (`ev:1789`) and the fix-cycle exit (`ev:1794`); also two of
  "terminate" (Gate 5 decision `ev:1792` and exit `ev:1794`) and "hold" (exit `ev:1794` vs surveillance hold,
  KIT ruling 11).

## Contradictions

1. Hangar and drydock are ruled synonyms with one depth (RWO:223-235; DOC:27) but the code keeps two levels: `src/gzkit/mx/alarms.py:35` turns the slow alarms off only at `"drydock"`, `src/gzkit/cli/parser_governance.py:884-886` offers `--level hangar|drydock` (*"hangar (default): one squawk"*), and `.gzkit/rules/mode-contract.md:22` still names *"the hangar level and the drydock level"* (acknowledged at KIT:401; GHI #1304).
2. Standby level: RWO:233 *"every mode-contract paragraph naming both standby levels read one level"* vs `.gzkit/rules/mode-contract.md:23` *"level per standby level"* and R13:10 *"That re-reading is open for this specification"*.
3. Sea trial: DOC:53 and CON:447-459 (two approved forms, gates exit) vs `docs/rnd/renewing-vows/doctrine-merge.md:136` *"Sea trial. One work package run on a fresh install of the released wheel"* and `.gzkit/templates/safe_mode_contract.md:117` *"The sea trial belongs to civil rule's first voyage, not to the exit"*.
4. Handback order: CON:415-416, 434 (the ratified handback is exit condition 9, before safe mode ends) vs DOC:99 *"The handback amendment follows the exit and precedes civil rule"* and SK:138-141 (step 6 after the exit).
5. Harbor as a phase: AGENTS.md:237 and doctrine-merge.md:131-132 *"one exceptional period through harbor, drydock and sea trial"* vs DOC:103 (corrected 2026-10-17) and CON:1208-1212 (that shape superseded).
6. Work order: doctrine-merge.md:141-142 *"the term "work order" was retired on 2026-10-16"* (ratified Part 0, unamended) vs RM:257 and DOC:52 (*"work order returns as the OBPI's successor"*, 2026-11-03).
7. Repair order means `RP-n` package: CON:78-84 § Purpose *"A repair order is the maintenance mirror of the work package ... a repair work package"* and TPL:10 *"Each order is a repair package named RP-n"*, beyond the draft § 6's three instances, vs RM:257 (order level).
8. Exit item 9 vs ruling 76: CON:435 *"each repair order closed through the operator's Gate 5"* (an RP-n package) vs KIT:568 *"books no Gate 5 decision of its own"*.
9. The floor: DOC:94 *"Gate 5 attestation; the ledger through verbs; operator PII; the PRIME DIRECTIVE; and no control is removed. These are the hangar's gate5_invariants"* vs `src/gzkit/mx/invariants.py:26-34` `{gate5-attestation, secrets, operator-pii, ledger, grader-gaming}`.
10. Change ladder rung count: R5:57 and KIT:26 (four rungs; alteration and DFS separate records) vs `src/gzkit/events.py:1787-1790` `WorkPackageRung` with six values (and the draft § 5's "Change ladder" line).
11. Supplement: R5:48 *"a new formal work package within the package"* vs `src/gzkit/work_package_ledger.py:537-540` requiring another `WP-` record.
12. Change order on a contract row: TPL:77 (the § Repair orders table *"is changed only by amendment of this contract"*) vs R5:50 *"A change order never changes the contract"* and DOC:59.
13. Tag classes: TPL:96-97 and REC:1084 (*"an alarm off and locked; a tripwire that records"*) vs `src/gzkit/events.py:2098` (*"Danger forbids operating the surface, Caution limits it"*).
14. Punch list: retired (REC:1558 *"B′"*; KIT:447 rejected synonym) vs live in `src/gzkit/mx/awareness.py:39` (*"what it breaks goes on the punch list"*) and `.gzkit/rules/mx-mode.md:144`.
15. Register: retired inside the hangar (DOC:61, B11 *"A"*) vs `.gzkit/skills/gz-mx/SKILL.md:90, 231` (*"the register"*).
16. Template drift (not a term ruling, recorded for T10): TPL:87 *"feature-area registry"* (CON:692-695: *"the feature-area registry is the family legend"*) and TPL:89 *"task-card"* (dropped 2026-11-03, CON:1020).

Superseded, not live contradictions (noted so they are not re-raised): REC:641 *"run by the restorer"* for the dock trial (KIT ruling 27 governs; KIT:8 says the record governs until an amendment here); RWO:383-392 *"Gate 5 stays at the package"* (RWO:483 and RM:264 put it at the order); REC:2063 MEL signals *"safe mode, standby, lockout"* (standby re-read as a command, REC:2251; lockout dropped, R13:31).

## Files read in full, with line counts

| File | Lines | Read |
|---|---|---|
| `docs/governance/drydock-taxonomy.md` | 149 | whole |
| `docs/governance/safe-mode-doctrine.md` | 103 | whole |
| `.gzkit/rules/mode-contract.md` | 28 | whole |
| `docs/governance/harbor-pilotage-candidate-2026-10-15.md` | 1953 | whole (lines 1-1953, paged) |
| `docs/governance/harbor-ro12-contractor-kit.md` | 828 | whole (lines 1-828, paged) |
| `docs/governance/harbor-ro13-mode-contract.md` | 68 | whole |
| `.gzkit/skills/gz-mx/SKILL.md` | 234 | whole |
| `docs/governance/harbor-ro5-work-packages.md` | 106 | whole |
| `.gzkit/templates/safe_mode_contract.md` | 126 | whole |
| `.gzkit/rules/mx-mode.md` (via its `.claude/rules/` mirror, delivered in context) | ~150 | whole |
| `src/gzkit/mx/marker.py` | 288 | whole |
| `src/gzkit/mx/checkpoint.py` | 125 | whole |
| `src/gzkit/mx/contract.py` | 126 | whole |
| `src/gzkit/mx/disposition.py` | 83 | whole |
| `src/gzkit/mx/invariants.py` | 253 | whole |
| `src/gzkit/mx/levels.py` | 41 | whole |
| `src/gzkit/mx/alarms.py` | 56 | whole |
| `src/gzkit/mx/series.py` | 33 | whole |
| `src/gzkit/mx/__init__.py` | 17 | whole |
| `src/gzkit/mx/tag_rows.py` | 132 | whole |
| `src/gzkit/mx/record_rows.py` | 108 | whole |
| `src/gzkit/mx/lease.py` | 71 | whole |
| `src/gzkit/mx/tag_out.py` | 771 | whole |
| `src/gzkit/mx/awareness.py` | 208 | whole |
| `src/gzkit/events.py` | 2488 | lines 1054-1160 and 1732-2488 whole (the MX, catalog, work-package, dispatch, order, tag and record events); the class index of the rest |
| `src/gzkit/work_package_ledger.py` | 647 | lines 1-110 and 520-592 (header, models, the change-ladder writer) |

Read by section only (not relied on for any absence claim): `docs/rnd/contractor-kit.md` (3404 lines; sections at 396-447, 589-604, 633-680, 1045-1054, 1082-1095, 1291-1395, 1536-1564, 1993-2097, 2226-2270, 2339-2375, 2442-2481, 2701-2768, 2933-2950, 2970-3058, 3204-3215); `docs/rnd/repair-work-organization.md` (612 lines; 199-307, 343-374, 383-409, 552-566); `docs/governance/ieee/requirements-model.md` (491 lines; § 12, 242-299); `docs/rnd/renewing-vows/doctrine-merge.md` (797 lines; Part 0 § Terms, 104-154). Not read: `src/gzkit/mx/{hardening,log,entries,discrepancies,proxy_reality,git_commits}.py` beyond a term search, `src/gzkit/commands/mx_cmd.py` beyond its definition index, and `docs/rnd/contractor-kit/vocabulary-matrix.md` (the crosswalk's source; `data/maintenance_crosswalk.json` does not exist).

## Gap-fill (2026-11-22, at the coordinator's request)

Two passes, still read-only. (1) I read in full the six `mx/` modules I had only searched, and all of
`src/gzkit/work_package_ledger.py` (lines 1-647). (2) I ran `uv run gz handoff rulings` once as `--json`
(2,463 rulings, saved to `(gathering scratch) gapA/rulings.json`) and applied the
verb's own case-insensitive substring test to all 123 search strings for the 100 terms. The result for
`--search "dock trial"` matched the verb's own output (8 rulings). The match counts per string are in
`(gathering scratch) gapA/counts.txt`. A ruling is cited below as `HR[n]`, its index
in the `--json` list.

### Code read in full: the terms each module implements or names

| Module (lines) | Terms implemented or named |
|---|---|
| `src/gzkit/mx/hardening.py` (352) | **lease** (`lease_hours`, the `mx-session` lock TTL, :37-39, 148-150); **lease start / renewal** (`lease_starts`, :127-145); **single-occupancy hangar** (`_MAX_OPEN = 1`, :40-41; *"more than one open session is a hard breach"*); **no normal release while the hangar is open** (`normal_release_blocked`, :219-239, *"an MX maintenance hangar is open; exit it (gz mx exit) before releasing"*); **advisory debt** (*"the open hangar IS the advisory-debt state"*, :12-14, 288-318), aged **per contract** (`_debt_since`, :266-285); **dangling state** (*"ledger open but marker missing"*, :15-17, 326-352); every guard resolves through the checkpoint with a `GZ_<LEVEL>` |
| `src/gzkit/mx/log.py` (441) | **MX log**, self-described at :1 as *"the complete-by-construction maintenance record"* and at :15 as *"the maintenance record's view at exit (RP-12 ruling 166)"*; render header *"=== MX Maintenance Log (complete by construction) ==="* (:394); the **window** (enter anchor to exit anchor, :10-13, 213-287); **fixes**; **artifacts touched**; **unrecorded work** (`UnrecordedWork`, :105-113; rulings 166, 189); **maintenance record (N entries)** by order (:350-379); refusals on an unreadable record, ledger or git (rulings 190, 193, 204; :145-146, 423-441) |
| `src/gzkit/mx/entries.py` (385) | **maintenance record** (`maintenance_record`, :93-109); **entry** `ENT-<NN>-<slug>` (:250-260); **performer** (`PERFORMERS = (IMPLEMENTER, SINGLE_DRIVER, RESTORATION)`, :55-56; ruling 175); the 14 CFR § 43.9(a) elements as fields (:76-81); **Gate 5 as the signature** (`RecordedEntry.gate5`, :112-148; `_gate5_line` writes *"not signed"*, :191-201); **landing commit / landed / not landed** (`LandingCommit`, `landings`, :151-188, 204-214; rulings 167, 170, 192); **entry block** (:217-247; ruling 191) |
| `src/gzkit/mx/git_commits.py` (95) | the one git reader of the record's views; **commits unreadable** (`CommitsUnreadableError`, :31-32; ruling 193); *"A git that cannot be read is never an empty history"* (:10) |
| `src/gzkit/mx/discrepancies.py` (593) | **list of discrepancies** writer and reducer; grade **`BLOCKS = "blocks-return-to-service"`** (:52-53) and `DUE_BY`; source **`FOUND_IN_WORK`** (:54-55); **inspector's rejection** refused until O6 (:169-174); **performer** (reuses `entries.PERFORMERS`); **carry** of a hung tag (`_check_carry_clear`, :527-543; rulings 171, 185); **problem report** (*"a line filed as an issue leaves the list as an open problem report"*, :519-523); **root cause / corrective action** and **recurrence** (:428-501; ruling 181); the `ClearWitnesses` port (:64-89); *"report it in the handback"* / *"report the evidence in the handback"* to a stamped performer (:217, 228, 567) |
| `src/gzkit/mx/proxy_reality.py` (188) | **grader-gaming** floor member's live negative control (:8-10, 159-188); **clearing gate** (`_CLEARING_GATE = "gate5"`, :33-35: *"The gate that "cleared" every repudiated completion is Gate 5"*); no drydock term otherwise |
| `src/gzkit/work_package_ledger.py` (647) | **lifecycles** by kind (`LIFECYCLES`, :45: a repair package `("initiated","closed")`); **change ladder** writer (`record_work_package_change`, :553-589; pen and ink the coordinator's, every other rung the operator's, :571; superseded content kept for pen and ink and change order, :575-576; work stops only on a change order, :577-578); rung subjects (`_rung_fields`, :524-550: supplement names another WP, alteration and departure name their item, a departure's form, duration and clear-by copied from the store); **sealed footprint** (`_seals`, `sealed_footprint`, `declared_modules`, :204-271: the latest freeze, the package's or an order's, *"plus each change order booked after it"*, :249-255; ruling 56); **alteration approved at freeze** (:304-309); **residual risk**, **configuration changes**, **open departures** at close (:395-414); **repair close** with no Gate 5 decision of its own, refused with no order, an open order or a hung tag (`_check_repair_close`, :351-392; rulings 30, 76, 79, 187); **held REQs** (`package_held_reqs`, :328-348; ruling 78); **issue closed against its repair package** (:611-647; ruling 10); **blocked package** (:184-201, 481-493) |

### Rulings `gz handoff rulings` holds that the table lacked

| Term (row) | Ruling not in the table | Effect |
|---|---|---|
| tripwire (D1 #45) | HR[1693] *"Three kinds of protection: irreversible damage and identity rules stay alarms; old-structure checks go off, cheap ones as tripwires (verbatim: "1. yes; 2. yes; 3. yes, off" and "tripwires for the cheap ones, long ones fully off")"* | SOURCED → **RULED** |
| hangar visit (D1 #80) | HR[1576] *"A hangar visit opened on a reason is a squawk (verbatim: "'squawk' is the right term for this: 'hangar visit on a reason'")"*; HR[1575] *"i may not have called it squawk, but that would have been the best"* | SOURCED → **RULED** (the squawk row gains both quotes) |
| Magna Carta (D1 #25) | HR[1443] *"the magna carta is a campaign to focus the progression of gzkit to a stable release state"* | SOURCED → **RULED** |
| approver (D2 #18) | HR[1930] *"--approver and --operator stay typed names, the limit staying on the discrepancy list and any fix taken up for every human-act verb together (verbatim: "A")"* (2026-11-02, also CON:1012) | SOURCED → **CONTRADICTED** (contradiction 18) |
| MX hangar entry and exit (D1 #2, #68) | HR[447] *"The agent opens and closes the MX hangar, not the operator (verbatim: "the mx system isn't going to work if you expect me to open and close it"). Standing from this session forward."*; HR[448] *"`gz mx exit --attestor g0` was run by the agent"* | status unchanged; contradiction 17 |
| standby level (D1 #8) | HR[1888] *"The level is a new marker field, hangar or drydock, with mode read as its alias and the ledger's mode untouched (verbatim: "a")"* | still CONTRADICTED; this is the ruling behind `mk:81-89` and `ev:1068` |
| safe mode (D1 #4) | HR[1573] *"safe mode isn't here to drive req/feature work, it is for deep repairs/realignments"*; HR[1665] *"the safe mode hangar shouldn't stop routine big fixes, it just suspends blocking"*; HR[1756] *"we are supposed to be freeing things up in mx, not hashing canaries"*, then *"both"*; HR[2455] *"why would we introduce safe mode exceptions? that is going to get out of control and lost very quickly."* | stays RULED |
| drydock (D1 #1) | HR[1574] *"this does not countermand the A,B,C,D checks of the mx system"*; HR[1819] *"We know that the 13 repair orders are all part of this dry dock session"*, *"that's what some of flight testing and sea trials are for. So I accept that."* | stays RULED |
| seaworthy, voyage (D1 #20, #23) | HR[1548] *"my expectation is the we leave martial law \| safe mode \| dry dock with a return to seaworthiness so that I can return to a normal voyage"* | stays RULED; the operator's words treat martial law, safe mode and dry dock as one condition |
| handback (D1 #21) | HR[1779] *"Blocking lines clear (Recommended)"*; HR[1829] *"yes, hand it to the owning outcome"*; HR[1840] *"A"* (catalog empty at the handback); HR[1929] *"A"* (docs organization waits for the handback); HR[2215] *"A: Reword to doctrine"* | stays CONTRADICTED; contradiction 19 is added |
| placard (D1 #35) | HR[1815] *"revert, comment on 1299, close WP-01 placarded, then handoff"*; HR[1816] *"that is a broad indictation during mx safemode, not a normal part of gz wp"* | stays RULED; the placard is a safe-mode indication, not a `gz wp` field |
| lease / renew (D1 #66) | HR[1600] *"you told me the lock was closed, asked that we close the old and open new."*; HR[1632] *"reopen lease"*; HR[1633] *"yes, we need the concept of a renewal"*; HR[1644, 1667, 1811, 2223] renewals | stays RULED |
| tag-out log (D1 #47) | HR[1715] *"One tag-out per surface; parallel repairers only on disjoint surfaces (verbatim: "don't do multiples for the sake of it")"* | stays RULED |
| change order, rung and act (D2 #3, #4) | HR[1710] *"The tasking spec is a job order changed only by the operator's change order (verbatim: "A")"*; HR[1723] *"... change order (the operator alone) ..."*; HR[1780] *"a test change by change order is a reopening"* | stay RULED |
| change order on a contract row (D2 #5) | HR[1825], [1854], [1857], [1878], [1886], [2105], [2107] (*"Change orders on anchors (Recommended)"*), [2149], [2172] (*"Yes, change orders"*) | stays CONTRADICTED; the operator has ruled this usage nine times, so the contradiction is in where it is recorded, not whether it was ruled |
| departure, the exit (D2 #10) | HR[1905] *"The exits fit the freeze rules: reopen, departure, hold, terminate, the once-only limit crossing packages (verbatim: "a")"*; HR[2261] *"Accept as O2's DFS (Recommended)"* | stays RULED; the homonym is now ruled on both sides |
| return to service (D1 #16) | HR[2196] *"Work order after RTS"* | stays RULED; adds the synonym **RTS** |
| airworthiness directive (D1 #73) | HR[326] *"ghi direct fix is repair and correction... akin to an 'airworthiness directive'"* | stays RULED; see the collision below |

Strings with no hit in the 2,463 rulings: *standby level*, *pilotage chart*, *passage log*, *(O)*,
*restore condition*, *accepted state*, *inoperative*, *gate5_invariants*, *out of position*,
*Authorizing Officer*, *tag source*, *work package log*, *reconnected*, *final inspection*,
*shift turnover*, *drydock session*, *hard gate*, *marker repair*, *factory floor*, *assembly mode*,
*AOG*, *quay*, *pen-and-ink*, *clear-by*. Each of these keeps the status the canon sources gave it.

### New terms found in the gap-fill

| Term | Meaning as stated | Defined | Code | Status |
|---|---|---|---|---|
| **maintenance discipline** | KIT:16 *"Safe mode suspends canon and does not suspend that discipline"* | KIT:16; HR[1768] | none | RULED — HR[1768] *"these are right, btw, but i don't think you tell up from down right now"*, ruling that *"safe mode suspends canon; the maintenance discipline is the drydock's own regime and the kit is that discipline"* |
| **drydock act** | a unit of work done inside the drydock, not an ADR | HR[2424]; DOC:62-63 (*act*) | none | RULED — HR[2424] *"not together and not an ADR - we will NOT perpetuate the old ADR system here. I just need some GSD approaches here."* |
| **lean safe mode** | the frozen minimal safe mode, with RP-10 parked | HR[1694]; CON:411 (*"the lean version is in force and frozen"*) | none | RULED — HR[1694] *"yes, freeze lean, park the spec, two contractors"* |
| **flight test / test flight** | CON:1903 *"TEST FLIGHT under safe mode — RO-5 witness"* | the `gz-flighttest` skill's description (*"flies one sortie with a human Go/No-Go"*); HR[1819] | none in `mx/` | SOURCED (the skill body is not read; HR[1819] accepts its use and gives no definition) |
| **RTS** | abbreviation of return to service | HR[2196] | none | RULED (synonym, the operator's own spelling) |
| **unrecorded work** | a window commit that names no entry the session's record holds | KIT ruling 166, 189 | `log.py:105-113, 197-210` | RULED — KIT ruling 166 *"A: Subsume (Rec.)"*; ruling 189 *"A: Unrecorded, named (Rec.)"* |
| **window** (enter-to-exit) | `log.py:10-13`, bounded by the `mx_session_opened` and `mx_session_closed` timestamps | DOC:15 (*"enter-to-exit log"*) | `log.py:213-305` | SOURCED (ADR-0.0.74 item 6) |
| **MX log / MX Maintenance Log** | the record's view at exit (`log.py:15`) | SK:131-133; KIT ruling 166 | `log.py:116-143, 382-441` | CONTRADICTED (contradiction 20) |
| **landing commit; landed / not landed** | the commit whose subject names an entry; *"an entry no landed commit names reads as not landed"* | KIT rulings 167, 170, 192 | `entries.py:151-214` | RULED — rulings 167 *"A: Performer books (Rec.)"*, 170 *"A: Name it in the subject (Rec.)"*, 192 *"A: Both views (Rec.)"* |
| **performer** | the dispatch that did the work: Implementer, SingleDriver or Restoration | KIT ruling 175 | `entries.py:55-56` | RULED — *"A: Who did the work (Rec.)"* |
| **carry / carried tag** | a hung tag an order's acceptance carries on one open due-by line, to a pause alone | KIT rulings 171, 184 to 188 | `ev:2038-2048`; `discrepancies.py:527-543`; `wpl:378-392` | RULED — ruling 171 *"A: Carry, pause only (Rec.)"* |
| **single-occupancy hangar (max open)** | *"The hangar is single-occupancy, so more than one open session is a hard breach"* | ADR-0.0.74 item 14 | `hardening.py:40-41, 169-211` | SOURCED |
| **dangling state** | *"ledger open but marker missing"* | ADR-0.0.74; MXR § The lease | `hardening.py:326-352` | SOURCED |
| **release lock while open** | *"refuses a normal release while the hangar is open"* | ADR-0.0.74 item 14 | `hardening.py:219-239` | SOURCED |
| **residual risk** | recorded at a delivery close or a proceed | R5 ruling 5; RM § 11 | `wpl:407-408`; `ev:1827, 2082` | RULED — R5 ruling 5 *"A"* |
| **held REQ** | *"a repair REQ holds at the revision an order closed as proceed froze it"* | KIT ruling 78 | `wpl:328-348`; `ev:1839-1841` | RULED — *"A: a holds reader, outcomes later (Rec.)"* |
| **sealed footprint (seal)** | the latest freeze's modules plus each change order after it | KIT ruling 56 | `wpl:204-271` | RULED — ruling 56 *"A"* |
| **clearing gate** | `proxy_reality.py:33-35` Gate 5, *"the human attestation step that the fabrication fooled"* | ADR-0.0.74 OBPI-13 | `proxy_reality.py:35` | SOURCED |
| **grader-gaming** (floor member) | `invariants.py:7-11` the observability system is itself a grader | ADR-0.0.74 | `inv:32`; `proxy_reality.py` | SOURCED |

### New collisions

- **airworthiness directive**: HR[326] uses it for a GHI direct fix, which is line work (*"ghi direct fix is repair and correction... akin to an 'airworthiness directive'"*). DOC:44 uses it for a drydock change noted in the manual, which is out of service. One term covers both sides of the alarm test.
- **(M)**: the MEL's (M) bypass procedure vs the *(m)ADR* (HR[1344], [1345]).
- **clearance / cleared**: a tag's clearance authorized (KIT ruling 6) vs *"the re-claim is the clearance"* for a reaped lock (HR[1349]) vs the *clearing gate* of `proxy_reality.py:35`.
- **discrepancy**: HR[1288] (*"move forward, note a disprepancy and we can ghi those"*, before the drydock) routes every discrepancy to a GHI. KIT ruling 9 keeps a discrepancy on the list and files it as a GHI only when it leaves the package's scope.

### Contradictions added by the gap-fill

17. Who opens and closes the hangar: HR[447] and [448] *"The agent opens and closes the MX hangar, not the operator (verbatim: "the mx system isn't going to work if you expect me to open and close it"). Standing from this session forward."* vs SK:38 *"The operator operates this skill; the skill invokes gz mx"*, DOC:98 *"Entry: the operator invokes the gz-mx skill"*, CON:317 *"The operator ... enters and exits through the gz-mx skill"*, and MXR *"agents do not shell out to gz mx enter or gz mx exit directly"*.
18. Typed approver: HR[1930] (2026-11-02) keeps `--approver` and `--operator` typed, with *"any fix taken up for every human-act verb together"*, vs KIT ruling 32 (2026-11-04, KIT:479), which gates four operator acts alone on verbatim words and replaces the typed `--approver operator` of `gz wp change` only.
19. Two handbacks: `src/gzkit/mx/discrepancies.py:217, 228, 567` tell a stamped performer to *"report it in the handback"* and *"Report the evidence in the handback"*. That is the subagent's report to the coordinator (KIT:104, `handbackReport`). DOC:54 defines the handback as *"The amendment the operator ratifies at seaworthiness"*.
20. The MX log names itself the record: `src/gzkit/mx/log.py:1` *"MX log assembler — the complete-by-construction maintenance record"* vs `log.py:15` and KIT ruling 166 (*"the entry events are the maintenance record, and the MX log becomes the view that renders them at exit"*).

### Statuses after the gap-fill

| Domain | Terms | RULED | SOURCED | CONTRADICTED | UNSOURCED |
|---|---|---|---|---|---|
| 1 (80 original) | 80 | 62 (+3: tripwire, hangar visit, Magna Carta) | 8 | 9 | 1 (`quay`) |
| 2 (20 original) | 20 | 16 | 0 | 4 (+1: approver) | 0 |
| New terms | 19 | 11 | 7 | 1 (MX log) | 0 |
| Total | 119 | 89 | 15 | 14 | 1 |

### Files read in full in the gap-fill

| File | Lines |
|---|---|
| `src/gzkit/mx/hardening.py` | 352 |
| `src/gzkit/mx/log.py` | 441 |
| `src/gzkit/mx/entries.py` | 385 |
| `src/gzkit/mx/git_commits.py` | 95 |
| `src/gzkit/mx/discrepancies.py` | 593 |
| `src/gzkit/mx/proxy_reality.py` | 188 |
| `src/gzkit/work_package_ledger.py` | 647 (whole now; 1-110 and 520-592 read before) |
| `uv run gz handoff rulings --json` output | 2,463 rulings, every match for all 123 search strings read |
