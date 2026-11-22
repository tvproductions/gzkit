# Gather G — the naming lineage of gzkit's work and repair levels

Gathered 2026-11-22 for the operator's ruling on `docs/governance/drydock-taxonomy.md` (T1 to T11).
Read-only: no repo file was edited, no `gz` verb that writes was run. A dated record. "Store" means
`.gzkit/handoffs/rulings.jsonl` (2,464 lines), read through `gz handoff rulings --search` and a
read-only script over the same file for its `ts` and line numbers. A store row's `ts` is its
**booking** date; rows L1 to about L830 were migrated in bulk on 2026-08-22 (GHI #838), so their
`ts` is not the ruling date. Where a ruling's own date is known from the record it is used.

"Supersedes" says which earlier row the ruling replaces and whether it **cites** it (explicit) or
not (silent). "Live?" is what code and the stores hold today (measured this session, or by the
draft's § 2 where noted).

## 1. Chronological lineage

| # | Date | Source path:line | Operator's verbatim words | What it names | Supersedes | Live in code/store? |
|---|---|---|---|---|---|---|
| 1 | before 2026-08-22 (booked 08-22) | store L349, L447, L455, L569, L572, L605, L743 | "yes, give directly via ghi" (L349), read against canon "a GHI is itself the work order and the receipt"; "GHIs are AUTHORIZED for direct repair, always" makes GHI #921 "the work order" (L605) | **work order = a GHI** | — (first) | Live in prose: `ghi-author` skill description, "when a finding needs its own work order"; never a record |
| 2 | before 2026-08-22 (booked 08-22) | store L432 | "never, ever recommend/allow an out-of-sequence work order for adrs" | "work order" in the sense *order of working* (sequence), not a record | — | the ascending-order rule was retired 2026-10-30 (store L1840) |
| 3 | 2026-09-27 | `docs/rnd/design-amendment.md:396-406` | "A, amendment" | **amendment** (noun); skill `gz-adr-amend`, the ruled, unbuilt `adr amend` verb; rejects *engineering change notice* because it "sits too close to *work order*, which canon reserves for a GHI" (line 403) | — | not built; `AMD-` in 0 files under `src/gzkit` |
| 4 | 2026-09-27 | `docs/rnd/design-amendment.md:541-562`; store L1128 | "A as offered, if that makes more sense to you. A in the way you previously presented it." | **`AMD-<semver>-NN`**, **`REQ-<semver>-ANN-NN`**, **`TASK-<semver>-ANN-NN-NN`** | — | not built; vehicle `ADR-0.40.0`, GHI #1148 open |
| 5 | 2026-10-04 | store L1346 | "our new plan is to keep the (m)ADR as a release increment bucket. However, I wanted it to be themematically cohesive" | **(m)ADR** as the release-increment bucket | — | no |
| 6 | 2026-10-04 | store L1347 | "whatever we develop beyond the stopgap (m)ADR, will be closer to a feature bucket/bundle and in between the BDD/SDD materials here" | **feature bucket/bundle** as the (m)ADR's successor | — | — |
| 7 | 2026-10-05 | `docs/rnd/renewing-vows.md:120-122` (insight 21:01:04) | 'chore is level A-D airframe checks (still mx), squawks are line-discovered issues (ghis)' | **chore = letter check**; **squawk = GHI** | — | — |
| 8 | 2026-10-05 | `docs/rnd/renewing-vows.md:2064-2071` (insight 22:03:25) | 'A' | **The artifact ladder**: pool → change proposal `ECP-<slug>`; feature ADR/(m)ADR → engineering order `EO-0.35.0-<slug>`; OBPI → work package `WP-0.35.0-10-<slug>`; TASK → task card (`TASK-` kept); ADR reserved `ADR-<n>`; release → block | rows 5, 6 silently (the (m)ADR gets a name, not a bucket) | ECP-, EO- in 0 files; `ADR-pool.identifier-ladder-migration` (lines 20-28) still states it |
| 9 | 2026-10-07 | `docs/rnd/renewing-vows.md:2073-2078` | (carry-forward, no new words) | ladder migration timed to 1.0 (FOC), not "IOC" | row 8's "at IOC", explicit | program and pool ADR say so |
| 10 | 2026-10-07 | `docs/rnd/renewing-vows.md:2351-2364` | 'Two slower tiers, signal-triggered (Recommended)' | **maintenance visit**: due chores and triage flown together as one named visit | — | advisory, no signal |
| 11 | 2026-10-08 | `docs/rnd/renewing-vows.md:1544-1549`; `:2797-2801`; `doctrine-merge.md:409` | 'work package: does it really have two meanings?'; 'these are too expensive unless we think they are availablre in a library' | **work package** one sense (AC 120-16G's "scheduled work package" = a packaged visit); **letter check** = the operator's own practice | — | — |
| 12 | 2026-10-10 | `docs/rnd/renewing-vows.md:4413-4427`; `doctrine-merge.md:465-474` | 'it stands, then git sync' (item 13) | kept as gzkit's own terms: letter check, squawk, **change proposal**, **block**; renamed: the chore registry = **the maintenance schedule**; sequenced items = **the campaign order** | glossary rows of row 8 re-standinged, explicit | glossary held in `doctrine-merge.md` Part 0 only |
| 13 | 2026-10-10 | `docs/rnd/renewing-vows.md:4444-4462`; `doctrine-merge.md:86-88, 121-124` | 'ratify Part 0, then git sync' (line 2 ruled 'it stands, add the seventh') | statement of command line 2: "standing orders for every position, a **tasking order for one work package**"; Terms: **Order**, **Release** = "Gate 5 attestation, which is return to service" | — | in `command-doctrine.md` per the ratification |
| 14 | 2026-10-10 | `docs/rnd/renewing-vows.md:4570-4576` | 'pool; beside it, provisional, new, now — create, then git sync' | "the ladder names a **change proposal as a pool ADR**" | applies row 8 | four pool ADRs booked |
| 15 | 2026-10-10 | `docs/rnd/renewing-vows.md:4621-4630`; `identifier-migration-program.md:13-20` | 'B, create, then git sync' | `ADR-pool.identifier-ladder-migration` carries ECP/EO/WP/task card/block | — | live pool file, unamended since |
| 16 | 2026-10-10 | `maintenance-visit-advice.md:65-71`; `renewing-vows.md:4656-4927` | 'admit visit B', 'admit visit A', … 'admit visit E' | **visits A to E** (A the light check, B the debt check, C mining, D conformance sweep, E control-surface coherence) | — | names in proofs and the record |
| 17 | 2026-10-10 | `docs/rnd/renewing-vows.md:4497` (agent's wording under 'go on row 2') | 'go on row 2, then git sync' | "**Work orders** filed through `ghi-author`" (GHI = work order, row 1's sense) | — | — |
| 18 | 2026-10-11 | store L1456; `renewing-vows.md:4932-4934` | "do the skill sweep, then git sync" | the ten skill repairs "as **one work order**" | — | — |
| 19 | 2026-10-15 | store L1542 | "if WP- fits better, then that is fine" | the drydock's unit of work may be **`WP-`** | silent, against the drydock's `WO-n` | — |
| 20 | 2026-10-15/16 | `doctrine-merge.md:130-145` | 'keep these metaphor entrenched in canon, this won't be the last time we need to reach for this approach' | safe mode terms: harbor pilot, harbor, **drydock**, sea trial, seaworthy, handback, voyage, **pilotage chart**, **passage log**; "the labor unit under safe mode is the **work package** … keyed to a GHI" | — | Part 0 text; *act* enters the contract the same day, agent-drafted, unruled (`repair-work-organization.md:115`) |
| 21 | 2026-10-16 | store L1552; `doctrine-merge.md:141-142` | "retire it, work package everywhere - change now: 'WO-1 to WO-11' to WP" | **work order retired**; `WO-1..WO-11` → `WP-` | row 1's term silently (GHI-as-work-order is not mentioned); the drydock `WO-n`, explicit | `WO-` in 2 files under `src/gzkit` |
| 22 | 2026-10-16 | store L1544 | "adrs are not releases, i am surprised you recommend this" | an ADR is a decision record, not a release | row 5, silent | — |
| 23 | 2026-10-16 | store L1553; `doctrine-merge.md:146-153` | "Release Package it is, rename and write WP-12" | **Release Package** (release management document type) | row 8's **block**, silent | live as a type and template |
| 24 | 2026-10-17 | store L1573 | "A, no separate document — retire the engineering order rung" | **engineering order rung retired** | row 8's EO, explicit in words, but cites no row; row 15's pool ADR not amended | EO in no code |
| 25 | 2026-10-17 | store L1574; `harbor-pilotage-candidate-2026-10-15.md:495, 1810` (spot-read) | "A on all five" (R1 to R6) | **R1: the repair order mirrors the work package and the work order stays retired**; the contract rewritten to § Repair orders **RO-0 to RO-8** | row 19/21's drydock `WP-n`, silent (they become `RO-n`) | `RO-9` alias on WP-01 |
| 26 | 2026-10-17 | store L1572 | "It's possible that ADR could lead to work package, or the requirements catalog could lead to it" | a **work package** is cut from an ADR or the catalog | — | — |
| 27 | 2026-10-17 | store L1577, L1578 | "i may not have called it squawk, but that would have been the best"; "'squawk' is the right term for this: 'hangar visit on a reason'" | **squawk = a hangar visit on a reason** (MX on-demand mode) | row 7's squawk = GHI, silent | — |
| 28 | 2026-10-18 | `requirements-model.md:50-59`, `:133-134`; store L1598 | "you got it" (decision 1); decision 2 ruled one decision at a time (insights, scope harbor-pilotage-wp4) | **`WP-<NN>-<slug>`**, no version in any id; "a work package plans one outcome"; **a retired code is never reused**; legacy ADR/OBPI/REQ/TASK ids frozen behind aliases | row 8's `WP-<semver>-<NN>-<slug>`, explicit (`requirements-model.md:133`, `identifier-migration-program.md:17`) | `WORK_PACKAGE_ID_PATTERN` live (`models/catalog.py:46`) |
| 29 | 2026-10-18 | `requirements-model.md:195-206`; store L1599 | "torn here, there are reasons for A and B"; "so, perhaps MIL-STD-881 had the best compromise?" | family legend, **single letters** X H C M P D R G A L Q | — | 11 single-letter families in `data/catalog/families.json` |
| 30 | 2026-10-18 | store L1614 | 'One RO, tranches (Rec.)' | **tranche** as the sub-unit of a repair order (RO-2) | — | "tranche" in 69 files under `src/gzkit` |
| 31 | 2026-10-25 | `harbor-ro5-work-packages.md:21` (spot-read) | "A" | RO-5 ruling 1: **"A repair order is a work package"**, `kind: delivery \| repair` | row 25 explicit in spirit ("mirrors" → "is") | `kind` field live; 1 record |
| 32 | 2026-10-25 | `harbor-ro5-work-packages.md:29` (spot-read) | "A" | RO-5 ruling 6: **one id series** `WP-<NN>-<slug>` for both kinds; `RO-n` stay aliases through the identity seam | — | WP-01 `aliases: ['RO-9']`; seam knows 4 kinds only (draft § 2) |
| 33 | 2026-10-25 | store L1693, L1700, L1698 | "The RO (or a sequence of ROs) are obligated to return the system to a prior, or new, stable system state."; "prd drives major, release package drives minor, ghi pressure drives patch"; "process for pool drain and work for pool drain are not the same thing" | RO = repair order (package level) owns restoration; **release package** drives minor; **pool stays as intentions, not ADRs** | row 14's "change proposal is a pool ADR", silent | — |
| 34 | 2026-10-26 | store L1723, L1725 | "okay, A. Looking at the matrix, that appears to be the strongest?"; "B avoids collision and fits" | a **work package** = its formal work package (procedure as **task cards**) + OQE, both kinds; the **change ladder** pen and ink, change order, attachment, supplement | — | ladder closed set live (draft § 5) |
| 35 | 2026-10-27 | `repair-work-organization.md:219` (quoting `contractor-kit.md`) | "A" | one condition with a standby level: **hangar** (one squawk) or **drydock** (under a contract) | — | — |
| 36 | 2026-10-29 | store L1821, L1825, L1826 | "We know that the 13 repair orders are all part of this dry dock session"; "any unspecified repair orders need to be fixed immediately" | RO-0..RO-13 are **repair orders** | — | — |
| 37 | 2026-10-30 | `requirements-model.md:29, 190-193` | (drydock contract § Rulings of 2026-10-30) | families **recoded to three letters** (`SES`, `SES1`, `SES1.4`) | row 29, explicit | **not applied**: store single letters, `OUTCOME_CODE_PATTERN` one letter (`models/catalog.py:40`) |
| 38 | 2026-10-30 | `four-records.md:200-212`; store L1852 | "REQ catalog with fdau familiy.cap.? structure, feature pack, work pack, release pack - work packs ARE OBPIs and match TASKs to REQs" | the four records; **work package = the OBPI** | rows 6, 8 (work package as OBPI confirmed) | — |
| 39 | 2026-10-30 | `four-records.md:235-246` | "yes, at most one for now - this the successor to the madr and the work pack is the successor to the obpi" | **feature package = mADR's successor**; **work package = OBPI's successor** | row 6, silent; row 8's engineering order, silent | — |
| 40 | 2026-10-30 | `four-records.md:295-307`; store L1853 | "no, those were shortenings (surprised I need to be this pedantic): requirements catalog (family.capability.outcome), feature package, work package, release package." | full names: **requirements catalog**, **feature package** (the only new name), **work package**, **release package** | row 38's "pack" readings, explicit | feature package has no store or id |
| 41 | 2026-10-30 | store L1834 | "A" | Gate 5 attested once **at the work package's close** | — | superseded by row 52 |
| 42 | 2026-10-31 | store L1890 | "a" | the **level** is a new marker field, `hangar` or `drydock`, `mode` its alias | — | draft § 5 still lists it; #1304 open |
| 43 | 2026-10-31 | store L1897, L1898 | "A"; "a" | `gz obpi` removed, history read-only via aliases; **RO-14** a new order by contract amendment | — | — |
| 44 | 2026-11-01 | store L1915 | "I consider that RO worthy." | project structure is a **repair order** (RO-15) | — | — |
| 45 | 2026-11-01 | store L1926, L1929 | "Repair declares (Recommended)"; "Hold at freeze (Recommended)" | **repair package** / **delivery package** (first booked uses) | — | — |
| 46 | 2026-11-02 | `repair-work-organization.md:130-132`; store L1937 | "Package at RO level (Recommended)" | **repair strata**: repair package at RO level, **repair order at tranche level**, **task at act level**; *tranche* and *act* retire (option A's stated cost) | row 31 ("A repair order is a work package"), explicit (line 132); row 30's tranche, explicit by cost | RP-12 still names "task N Act M"; RP-14/15 still "tranche" (U8) |
| 47 | 2026-11-02 | `repair-work-organization.md:176-187`; store L1938 | "yes, that's the structure" | **four levels on both sides**: why / grouping / marriage of REQ to task / action; **work order returns** | row 21, explicit ("reversing its retirement of 2026-10-16") | — |
| 48 | 2026-11-02 | `repair-work-organization.md:195-205`; store L1939 | "we could call it an out-of-service package"; "yes, out of service means the marker is open is also very strong" | **out-of-service package** (provisional); **out of service** = MX marker open; **on the line** = GHI work | — | — |
| 49 | 2026-11-02 | `repair-work-organization.md:223-233` | "These are synonyms for sure, so option A, but I'm not really convinced about two depths" | **hangar** and **drydock** synonyms; one depth; `gz mx` keeps its name | row 35, explicit; row 42 (L1890) not cited | not applied (#1304) |
| 50 | 2026-11-02 | `repair-work-organization.md:251-266`; store L1942 | "honestly, it should be called a return to service package … So I might call it feature package on the build side and return to service package on the repair side." | **return to service package**; out of service is a flag | row 48's out-of-service package, explicit | no record, event or verb |
| 51 | 2026-11-02/03 | `repair-work-organization.md:343-355, 517-526`; store L1943 | "yes, adopt the four levels - use the rich detail we found"; "A + B are GHI driven … C + D are mx driven" | **check levels A, B, C, D** (plus transit/daily/weekly) | row 7's "chore is level A-D", refines; row 16's visits A–E not cited | chores declare `check: {level, provisional}` |
| 52 | 2026-11-02 → 11-03 | `repair-work-organization.md:383-394` then `:483-488` | "a" (order a real record, Gate 5 at package) then "answer was A" | **order is a real record**; Gate 5 first at the package, then **at the order** | row 41, and its own 11-02 entry, explicit (line 486) | order store live, 0 records |
| 53 | 2026-11-03 | `repair-work-organization.md:398-401`; store L1948, L1970 | "A" | **`RP-n` replaces `RO-n`** in live text, numbers kept, `RO-n` an alias, record id stays `WP-<NN>-<slug>`; narrowed to "the contract's live text only" | row 25/32's `RO-n` as live name, explicit | `RP-` alias not in store (#1302); 0 files under `src/gzkit` match `RP-\d` |
| 54 | 2026-11-03 | `repair-work-organization.md:404-406`; store L1949 | "a" | every opening of the marker has a **return to service package** | — | not built (#1303) |
| 55 | 2026-11-03 | `repair-work-organization.md:410-414`; store L1950 | "1. no 2. let's discuss 3. ask it" | the unit of action is the **task**; ***card* dropped** | rows 8, 34 ("task card"), explicit | `identifier-migration-program.md:18` and the pool ADR still say task card |
| 56 | 2026-11-03 | `repair-work-organization.md:445-465`; store L1953 | "I'm saying that the WO IS the OBPI, which is a correction"; "work package is the mADR successor, the WO is the OBPI successor." | **work order = OBPI's successor**; work package groups orders for cohesion | rows 28, 38, 39 (work package = OBPI successor), explicit, amended at `four-records.md:246`, `requirements-model.md:36` | — |
| 57 | 2026-11-03 | `repair-work-organization.md:500-513`; store L1956 | "A wins because you elevate the feature pack to "epic" and keep the WP (mADR) as a story." | **epic** = feature package; **story** = work package (mADR's successor) | row 39 (feature package = mADR successor), explicit | — |
| 58 | 2026-11-03 | `repair-work-organization.md:528-533`; `requirements-model.md:250-258`; store L1959 | "yes, it stands; use "none (new)" the table needs to kept and associated as canon - it captures the design very well." | **the level table** (Epic/Story/Order/Action × Construction/Repair, Succeeds, Decides, Who) is canon | rows 46, 47, 50 tables, explicit | canon in `requirements-model.md` § 12 |
| 59 | 2026-11-03 | `repair-work-organization.md:552-557`; `doctrine-merge.md:125-129`; store L1962 | "Option A" | **return to service** is the operator's separate act at the return to service package's close | row 13's Release term ("Gate 5 … which is return to service"), explicit in `doctrine-merge.md` | not built |
| 60 | 2026-11-04 | store L1981; `harbor-ro12-contractor-kit.md:8` (spot-read) | "A" (ruling 25) | RP-12's **nine repair orders** O1 to O9 | — | O1–O4 closed; Gate 5s in page prose |
| 61 | 2026-11-05 | store L1998; `requirements-model.md:37` | "a" (ruling 43) | **`ORD-<NN>-<slug>`**, one grammar for work and repair orders, kind read from the package | — | `ORDER_ID_PATTERN` live (`models/catalog.py:49`); `data/catalog/orders.json` 0 records |
| 62 | 2026-11-05 | store L2004 | "b" (ruling 49) | an **order alias** unique within its package | — | `ORDER_ALIAS_PATTERN` live (`:52`) |
| 63 | 2026-11-08 | store L2110 | "each by selection" (H5) | classic ADR ids **`ADR-[0-9]{4,}`** with the seam's slug | row 8's `ADR-<n>`, silent (program's 11-08 amendment cites H4) | not landed (RP-6) |
| 64 | 2026-11-14 | store L2198 | "Work order after RTS" (twice) | GHIs #1322, #1323 become **work orders after return to service** | — | no work order exists |
| 65 | 2026-11-17 | store L2271 | "B: TAG-<NN>-<slug>" (ruling 111) | **`TAG-<NN>-<slug>`** | — | `TAG_ID_PATTERN` (draft § 3) |
| 66 | 2026-11-20 | store L2353; `harbor-ro12-contractor-kit.md:749` (spot-read) | "A: Kit now, O4 later (Rec.)" (ruling 165) | O1–O9 are the page's **build orders, not ledger orders**; Gate 5 in the kit | — | Gate 5s of O1–O4 in prose |
| 67 | 2026-11-20 | store L2361 | "A: ENT and DSC (Rec.)" (ruling 169) | **`ENT-<NN>-<slug>`**, **`DSC-<NN>-<slug>`** | the 2026-10-07 "maintenance record entry" term (row 10's neighbour, `renewing-vows.md:2295`), silent | patterns live (draft § 3) |
| 68 | 2026-11-22 | store L2445 | "per wp/wo" | operator uses **wp/wo** as live short names | — | — |
| 69 | 2026-11-22 | store L2456, L2460 | "Proceed: O4 attested"; "complete the rnd and move to RP-12/RO-5" | RP-12's **repair order O4**; repair order 5 called **RO-5** | row 53's `RO-n` = alias of `RP-n`, silent collision (RO-5 is also RP-5) | — |

69 rulings in the lineage (rows 2, 17 and 18 are usages under an operator go rather than naming
rulings in their own right; rows 11 and 20 are terms ruled with their source).

## 2. Each name's standing

| Name | Latest ruling | Later text that contradicts it |
|---|---|---|
| **Epic / Story / Order / Action** | row 58 (2026-11-03, the level table) | none found. The draft's T1 restates it. |
| **Feature package** | rows 57, 58: the epic, succeeds none; identifier "to be named when its store lands" (`requirements-model.md:35`) | none in text; never built |
| **Work package** | rows 56–58: the story, the mADR's successor, `WP-<NN>-<slug>` | `identifier-migration-program.md:17` and `ADR-pool.identifier-ladder-migration.md:25` (OBPI → work package); `doctrine-merge.md:140-142` (safe mode's labor unit is the work package, keyed to a GHI); statement of command line 2, "a tasking order for one work package" (`doctrine-merge.md:86-88`, ratified 2026-10-10); Part III "the six phases are the life of one work package" (`doctrine-merge.md:619`); AC 120-16G's "scheduled work package" used for a maintenance visit (`doctrine-merge.md:408, 678`) |
| **Repair package** | rows 46, 53: RO level, `RP-n` in live text, record id `WP-<NN>-<slug>` | `safe-mode-doctrine.md:67` "Each order is a repair package"; `harbor-pilotage-candidate` § Repair orders "Order" column (draft § 6) |
| **Work order** | rows 47, 56, 58: the OBPI's successor, the order level, `ORD-<NN>-<slug>` (row 61) | `safe-mode-doctrine.md:52` and `doctrine-merge.md:141-142` still say "retired (2026-10-16)"; `ghi-author` skill description and rows 1, 17, 18, 64 use it for a GHI |
| **Repair order** | rows 46, 58: the order level; RP-12's O1–O9 (row 60) are build orders, not ledger orders (row 66) | `safe-mode-doctrine.md:52` "A repair order is the maintenance mirror of the work package … held as a repair work package"; row 69 (operator's RO-5 for an order) |
| **Return to service package** | rows 50, 54, 59 | none; no identifier, record, event or verb (draft T6) |
| **Out-of-service package** | withdrawn by row 50 | none |
| **Task** | row 55: the unit of action; *card* dropped; `TASK-…` kept | `identifier-migration-program.md:18`, the pool ADR (task card); RP-12 practice "O2 task 3 … Act 1" puts acts beneath tasks (store L2040-L2068) |
| **Task card** | dropped by row 55 | as above |
| **Act** | retired by row 46 (task at the act level) | RP-12 rulings 54, 55, 67, 68 and "Build Act 1…6" (2026-11-07/08), O4 "act 2, act 3" (2026-11-20) |
| **Tranche** | retired by row 46 (repair order at the tranche level) | RP-15 tranche 6 (store L2175-L2185, 2026-11-12/13); RP-14 tranche 3 (L2196, 2026-11-14); 69 source files |
| **Engineering order** | retired by row 24 (2026-10-17) | `identifier-migration-program.md:16` "ruled"; `ADR-pool.identifier-ladder-migration.md:9, 24`; `doctrine-merge.md:435` glossary row; `doctrine-merge.md:632` ("the engineering order and the brief's requirements") |
| **Change proposal / `ECP-`** | rows 12, 14 (kept as a term; a pool ADR is one) | rows 33 and `four-records.md:281-293` (the pool stays as intentions, the predecessor of a feature package); `ECP-` never applied |
| **Block** | row 12 (kept as a term) | rows 23, 33, 40, 58 name the release record **Release Package**; `identifier-migration-program.md:20, 88` and the pool ADR still use block |
| **Release Package / release package** | rows 23, 33, 40; level table "the version" | none, beyond row 12's block |
| **ADR identifier** | row 63: `ADR-[0-9]{4,}` with slug | `requirements-model.md:34` and `identifier-migration-program.md:19` say `ADR-<n>` |
| **(m)ADR / feature ADR** | rows 22, 56–58 (decision record; its grouping job is the work package's) | none live; row 5 is silent-superseded |
| **OBPI** | rows 43, 56, 58 (frozen legacy, succeeded by the work order) | the ladder program (OBPI → work package) |
| **`WO-n`** | retired by row 21; row 28 "a retired code is never reused" | draft T3 offers `WO-` again for work orders |
| **`RO-n`** | alias of `RP-n` (rows 32, 53) | row 69 (operator's "RO-5" for RP-12's order 5); `RO-9` on WP-01 is the only alias stored |
| **`RP-n`** | row 53 | not resolvable (#1302); not in store |
| **`ORD-` / order alias** | rows 61, 62 | 0 orders; RP-12's O1–O9 are not ORD records (row 66) |
| **`O1`–`O9`** | rows 60, 66 | draft T5 |
| **Squawk** | row 49's reading: a squawk is answered on the line (`repair-work-organization.md:229`); row 12 keeps it as the GHI's term | row 27 (2026-10-17: a hangar visit on a reason) is not cited by row 49 |
| **Hangar / drydock** | row 49: synonyms, one depth | row 42 (2026-10-31 level field) uncited; draft § 5 lists `level hangar \| drydock` |
| **Check levels A–D** | row 51 | row 16's visits A–E use the same letters for packaged visits |
| **Maintenance visit / maintenance schedule** | rows 10, 12, 16 | none |
| **Amendment / `AMD-`** | rows 3, 4 | rows 34 (change ladder) and 58 (a remodel is a new REQ that supersedes, `requirements-model.md:290-297`) never cite them |
| **Family / outcome codes** | row 37: three letters | not applied in `families.json` or `OUTCOME_CODE_PATTERN` (draft T8) |
| **`TAG-`, `ENT-`, `DSC-`** | rows 65, 67 | none |

## 3. Unresolved supersessions

Two rulings that conflict where neither cites the other, or where a later ruling was explicit in
its R&D record but the surfaces that state the earlier one were never amended (marked *unapplied*).

1. **Engineering order.** Row 24 retired the EO rung (2026-10-17). The identifier migration program (amended 2026-11-08 for ADRs only) and `ADR-pool.identifier-ladder-migration` still list EO as ruled, and neither cites row 24. Silent.
2. **What the work package succeeds.** Row 56 (2026-11-03) made the work order the OBPI's successor. Four-records and the requirements model were amended. The identifier program, the pool ADR, doctrine-merge Part 0's safe-mode term, statement-of-command line 2 ("a tasking order for one work package") and Part III still treat the work package as the OBPI's successor. *Unapplied.*
3. **Work order retired vs restored.** Row 47 cites and reverses row 21, but `safe-mode-doctrine.md:52` and `doctrine-merge.md:141-142` still say "retired". *Unapplied* (draft T10 covers the doctrine line only).
4. **Work order = GHI vs work order = order level.** The Aug–Oct canon (row 1, the `ghi-author` description, `design-amendment.md:403`, rows 17, 18) and row 47/56 never cite each other. Row 64 (2026-11-14) uses the term both ways at once. Silent.
5. **`RO-n` names.** Rows 32 and 53 make `RO-n` an alias of `RP-n`. Row 69 (2026-11-22) uses "RO-5" for RP-12's repair order 5, which collides with RP-5's alias. Silent.
6. **"A repair order is a work package".** Row 46 corrects it explicitly. `safe-mode-doctrine.md:52, 67` and the contract's § Repair orders "Order" column keep the old level. *Unapplied* (draft T10).
7. **Act and tranche.** Both were retired with the 2026-11-03 strata (row 46), and the task replaced the act. RP-12 then ran "task N, Act M" (2026-11-07 onward), and RP-14 and RP-15 kept "tranche" (2026-11-12, 11-14). That puts a fifth level beneath the task. No ruling cites the retirement. Silent.
8. **Task card.** Row 55 dropped "card". The identifier program (line 18) and the pool ADR still say task card. *Unapplied.*
9. **Block vs Release Package.** Row 12 kept "block" for the release (2026-10-10). Rows 23 and 40 named the Release Package, and the level table gives the version to it. Neither cites block, and block survives in the program and the pool ADR. Silent.
10. **Change proposal vs pool intentions.** Rows 8, 12 and 14 make a pool ADR a change proposal (`ECP-`). Rows 33 and 40 (four-records) keep the pool as intentions, the predecessor of a feature package, and never mention ECP. Silent.
11. **(m)ADR as the release bucket.** Row 5 (2026-10-04) and row 22 (2026-10-16, "adrs are not releases") conflict. Row 22 does not cite row 5. Silent; harmless now.
12. **Squawk, three meanings.** Row 7 says squawk = GHI. Row 27 says squawk = a hangar visit on a reason. Row 49 says a squawk is answered on the line. Row 49 does not cite row 27. Silent.
13. **Hangar/drydock as a level.** Row 49 reversed row 35 explicitly, but not row 42 (2026-10-31, the marker's level field). The draft's § 5 still states that field. Silent, and #1304 is open.
14. **Letters A–E vs A–D.** Row 16's maintenance visits A–E and row 51's check levels A–D use the same letters for different things, and neither cites the other. Silent.
15. **Amendment vs change ladder and supersession.** Rows 3 and 4 (the `AMD-` and `REQ-…-ANN-…` grammar, 2026-09-27) never meet rows 34 and 58 (the change ladder; a remodel is a new superseding `REQ-<n>`). ADR-0.40.0 and GHI #1148 still carry the AMD design. Silent.
16. **ADR id.** Row 8's `ADR-<n>` and row 63's `ADR-[0-9]{4,}`+slug conflict. `requirements-model.md:34` keeps `ADR-<n>`, and the program's 2026-11-08 amendment cites H4, not H5. A silent refinement.
17. **Two kinds of "repair order".** RP-12's O1–O9 (rows 60, 66: build orders, not ledger orders) and the ledger repair order `ORD-` (row 61) share one name at one level. Ruling 165 distinguishes them, but no taxonomy ruling does (draft T5).
18. **"A retired code is never reused" vs the draft's options.** Row 28's rule, ruled for catalog codes, is quoted by the draft against `WO-`. Yet T3 offers `WO-`/`RO-` for orders. Whether the rule binds work identifiers is unruled.
19. **The Release term in the canonical doctrine (unverified).** Row 59's amendment is in `doctrine-merge.md` Part 0 (commit `9a7f2486c`, per `repair-work-organization.md:595`). Whether `docs/governance/GovZero/command-doctrine.md`, which carries Part 0 since 2026-10-10, was amended too was not read in this gather.

Ruled and resolved explicitly (for completeness, no action owed): row 28 over row 8's `WP-<semver>`; row 37 over row 29 (unapplied in the store and pattern, T8); row 52 over row 41 (Gate 5 at the order); row 57 over row 39 (the feature package is the epic, not the mADR's successor); row 50 over row 48.

## 4. Files read in full

| File | Lines |
|---|---|
| `docs/governance/drydock-taxonomy.md` | 149 |
| `docs/rnd/renewing-vows.md` | 5,235 |
| `docs/rnd/renewing-vows/doctrine-merge.md` | 797 |
| `docs/rnd/renewing-vows/identifier-migration-program.md` | 116 |
| `docs/rnd/renewing-vows/maintenance-visit-advice.md` | 98 |
| `docs/rnd/renewing-vows/review.md` | 184 |
| `docs/rnd/renewing-vows/where-things-stand-2026-10-11.md` | 169 |
| `docs/rnd/four-records.md` | 353 |
| `docs/rnd/four-records/review.md` | 85 |
| `docs/rnd/design-amendment.md` | 751 |
| `docs/rnd/repair-work-organization.md` | 612 |
| `docs/governance/ieee/requirements-model.md` | 491 |
| `docs/rnd/house-style.md` | 1,239 |
| `docs/rnd/subagent-folding.md` | 572 |
| `docs/rnd/big-picture-skill.md` | 229 |
| `docs/rnd/ghi-batch-closure.md` | 396 |
| `docs/rnd/ghi-landscape-reorganization.md` | 304 |

**What the five other runs hold, having read them whole.**
- `house-style.md`: no naming ruling on a level, record or unit. It names "the house style" (ruled, "All, under one name"), and the operator asks in passing whether design belongs "inside a work package or a work order" (line 448). It uses "classic ADR" and "change order" as standing terms.
- `subagent-folding.md`: none. It quotes the contract's "deterministic repair orders" and the contractor-kit's "per-act" dispatch (line 136), the RO-level usage of 2026-10-27.
- `big-picture-skill.md`: none.
- `ghi-batch-closure.md`: no level names. Held terms readiness (R1–R4), landing queue and ruling docket (lines 312-317); the agent calls #921 "an epic in GHI clothing" (line 157).
- `ghi-landscape-reorganization.md`: none ("work units", line 261, is the agent's prose).

**Read in part, not in full** (spot-reads to place a store ruling, cited as such above):
- `docs/governance/harbor-ro5-work-packages.md` lines 21, 29, 32, 77, 89
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md` lines 377, 394, 495, 923, 1810
- `docs/governance/safe-mode-doctrine.md` lines 50-52, 66-67
- `docs/governance/harbor-ro12-contractor-kit.md` lines 8, 57, 279, 292, 350-388, 749
- `docs/design/adr/pool/ADR-pool.identifier-ladder-migration.md` lines 9, 20-28, 66, 83 (90 lines; its only "Superseded" note is line 83, and it carries no amendment after 2026-10-10)

**Store reads.** `gz handoff rulings --search` for each name in the brief. Counts: work order 16, work package 15, repair package 9, repair order 9, return to service 8, feature package 4, engineering order 1, change proposal 0, task card 1, epic 4, story 24, block 100. Three read-only regex passes over `.gzkit/handoffs/rulings.jsonl` then covered every row naming an order, package, card, act, tranche, alias, grammar, identifier, ladder, mADR, squawk or bundle (about 450 rows printed; every naming row is entered above).

**Code and store measured this session.** `data/catalog/work_packages.json` holds 1 record (`WP-01-astral-toolchain`, repair, `aliases: ['RO-9']`). `orders.json`, `reqs.json` and `outcomes.json` hold 0 each. `families.json` holds 11 single-letter families. `src/gzkit/models/catalog.py:40,46,49,52` define the outcome, work-package, order and alias patterns. Under `src/gzkit`, `ECP-`, `EO-`, `AMD-`, `RP-\d`, `feature_package`, `return_to_service_package` and `task_card` occur in 0 files, `WO-` in 2, `tranche` in 69. The `IdKind` census is the draft's (§ 2), not re-run here.

## Gap-fill (2026-11-22, on the coordinator's two read gaps)

**Read in full for it.** `docs/governance/harbor-pilotage-candidate-2026-10-15.md` (1,953 lines):
§ Repair orders (377-411) and every § Rulings section, read whole: 2026-10-17 (477-505), 2026-10-29
(507-662), 2026-10-30 (664-860), 2026-10-31 (862-987), 2026-11-01 (989-1008), 2026-11-02 (1010-1014),
2026-11-03 (1016-1023), 2026-11-08 (1025-1054), 2026-11-12 (1056-1074), 2026-11-13 (1076-1128),
2026-11-14 (1130-1141), 2026-11-19 (1143-1155). Also read, because they hold the 2026-10-15/16
rulings: § Superseded on 2026-10-30 (1157-1206), § Superseded on 2026-10-17 (1208-1607), including
§ Work packages, the WP-4 draft, the pilotage chart and the executive decisions of 2026-10-16. Not
read: § Authority to § Records (1-376), § Exit (413-475, except items 8-13 at 428-470, read), the
list of discrepancies and the passage log (1608-1953).
`docs/design/adr/pool/ADR-pool.identifier-ladder-migration.md`: read whole (90 lines).
Item 19: answered by track B. `command-doctrine.md` lines 68-69 still make Gate 5 the return to
service and were not amended on 2026-11-03. That is confirmed, and *unapplied*.

### Lineage rows confirmed or corrected

| Row | Verdict | What the contract shows |
|---|---|---|
| 19, 20, 21 | confirmed | The contract's § Work packages of 2026-10-15/16 (1337-1363) has the drydock units already as WP-1 to WP-8, and WP-10 to WP-16 were added 2026-10-16 (1584-1606). "Each is a GHI through `ghi-author`" (1339), so the safe-mode work package is GHI-keyed. Of the rulings of 2026-10-15/16, "the work order retired" stands (504). |
| 22, 23 | confirmed | "adrs are not releases" is booked for civil rule on 2026-10-16 (1367-1373). The Release Package is "confirmed by the operator" as executive decision 2 (1569) and entrenched as a type (1539-1548). |
| 24 | **corrected: explicit, owned, unapplied** | The verbatim words are in § Rulings of 2026-10-17 (494). The contract's *Amended 2026-10-18* note (1196-1198) cites the 2026-10-05 ladder: "The engineering-order rung of the 2026-10-05 ladder is retired … the ladder's other rungs stand, and identifiers still migrate at 1.0 with aliases before it". RP-6's row (407) owns retiring "the engineering-order rung in the ladder records". The supersession is explicit; the program and the pool ADR are the unapplied surfaces. |
| 25 | **corrected: widened** | "A on all five" (495-500) also rules **R2**, "Gate 5 stays per work package with a release attestation on top"; **R3**, "the Release Package is the plan and the ledger release record the shipped claim"; and **R5**, "the alias resolver pulled into the drydock as **RO-2**", the first `RO-n` naming in a ruling. |
| 26 | confirmed | 492-493 |
| 28 | confirmed | Amended 2026-10-18 (1193-1195): "a work package delivers exactly one outcome". |
| 33 | confirmed | The restoration ruling of 2026-10-25 is verbatim at 388 ("the RO's obligation … The RO (or a sequence of ROs)"). The pool-as-intentions words are quoted at 1206 ("they just aren't ADRs any longer … they live just fine as intentions"). |
| 36 | **corrected: widened** | § Rulings of 2026-10-29 (517-527): "Induction freeze … RO-0 to RO-13". It also supersedes the contractor-kit record's clause that out-of-scope work is "**a new job order, a new RO**" (513-514, 525-527): a finding is graded instead. See new row 70. |
| 37 | confirmed | 2026-10-30 (803-818): *"three"*; *"yes, those eleven"*; the codes are `AIR`, `SES`, `CTL`, `MNT`, `PKG`, `DEC`, `RQW`, `GAT`, `ATT`, `LED`, `QUA`. `REQ`, `ADR`, `PRD` and `GHI` are avoided as family codes. |
| 38 to 40 | **corrected: widened** | § Rulings of 2026-10-30 (754-794): the locked stand-in names were **catalog item**, **feature/value bundle**, **work package** ("the OBPI's essence carried forward … through task cards") and **release package**. In the mapping (776-785), the OBPI's TASKs are "task cards", and "**a GHI with a patch release is a repair work package in a cart**". |
| 41 | **corrected: date and supersession** | It is ruled in § Rulings of **2026-10-29** (594-602), not 10-30, which is only the store's booking. It cites and supersedes R2 (2026-10-17, per work package) and the requirements model of 2026-10-18 (per outcome), explicitly. |
| 42 | **corrected: source** | The hangar/drydock level field (store L1890) is not in the contract's § Rulings of 2026-10-31. That section instead rules "**Lockout is dropped as a mode signal**" (917-920) and speaks of "one condition with a standby level". The store row stays its only source here. |
| 43, 44 | confirmed | 965-976 (nothing retained in OBPI; RO-14); 999-1008 (RO-15) |
| 46 to 59 | confirmed | The contract adopts them by amendment B1 in § Rulings of 2026-11-03 (1018-1022): four levels; feature package the epic; work package the story and the mADR's successor; work order the OBPI's successor; *task card* dropped; Gate 5 at the order; hangar and drydock synonyms; a return to service package per opening. It adopts no identifier (no `WP-`/`ORD-` grammar is stated). |
| 53 | **corrected: widened** | The adoption text itself (1023) reads "`RP-n` replaces `RO-n` in live text … **Each order is a repair package**; `RO-n` stays its alias through the identity seam (GHI #1302)". It keeps `RO-n` in rulings sections, superseded records, the passage log, dated banners, the record of 2026-10-30 and the lines of the list of discrepancies. |
| 63 | **corrected: widened** | RP-6's row (407): the grammar is `ADR-[0-9]{4,}` for the id and `ADR-[0-9]{4,}-[0-9]{3,}-<slug>.md` for the **edition file**, with the slug the seam's `SLUG_BODY` (H5). CO-2 owns reconciling "the October identifier program's 1.0 timing and bulk-rename clauses … explicitly" (H2). The supersession of `ADR-<n>` is therefore owned and explicit in intent, but unapplied (RP-6 has not landed). |

### New lineage rows

| # | Date | Source path:line | Operator's verbatim words | What it names | Supersedes | Live? |
|---|---|---|---|---|---|---|
| 70 | before 2026-10-29 (contractor-kit record) | `harbor-pilotage-candidate-2026-10-15.md:513-514, 525-527` | (the record's clause, quoted by the contract) | **job order**: out-of-scope work becomes "a new job order, a new RO" | superseded for findings on 2026-10-29, explicit ("record it now as a ruling") | no |
| 71 | 2026-10-16 | `harbor-pilotage-candidate-2026-10-15.md:1516, 1563-1568, 1214` | "confirm all three, amend the chart"; executive decisions "the operator may overrule any by a word" | D1: "the **engineering order, the feature bundle**, lands contracts on REQs for one bounded advance … the work package replaces the OBPI as the labor unit"; catalog id **`REQ-C<n>`** (executive decision 1) | row 8 (EO given the bundle's job) | `REQ-C` not in the seam; the canon is `REQ-<n>` |
| 72 | 2026-10-30 / 31 | `harbor-pilotage-candidate-2026-10-15.md:830-858, 959-961` | *"A"* (`catalog admit`); *"A"* (`capabilities.json`); *"A"* (`capability`); *"A"* (`transition`) | record and verb names: the ruled, unbuilt `catalog admit` verb; **capability record** in `data/catalog/capabilities.json` via the ruled, unbuilt `catalog capability` verb; `edit`, `reopen`, `withdraw`, `transition`; event `catalog_edited` | — | `capabilities.json` absent from `data/catalog/` (draft § 2: Capability "none") |
| 73 | 2026-10-31 | `harbor-pilotage-candidate-2026-10-15.md:921-925` | *"A"* | RP-13's retrofit tranches labelled **R1 to R3** (foundation F1 to F5) | — | spec labels |

**Pool ADR, read whole.** It confirms the program's ladder as of 2026-10-10. A pool ADR "is a change
proposal" (line 20). The grammar is `EO-<semver>-<slug>` and `WP-<semver>-<NN>-<slug>` (24-25). "a TASK is
a task card" (25-26); "a release is a block" (27-28). It closes with "the stopgap's successor is a
feature bundle, named here" (83-84), meaning the engineering order. Its phases are "each a work package
the operator initiates" (48-49). It carries no amendment for the EO retirement (2026-10-17/18), the
`WP-<NN>` re-rule (2026-10-18), the four records (2026-10-30), the dropped card or the level table
(2026-11-03), or the `ADR-[0-9]{4,}` grammar (2026-11-08). This strengthens U1, U2, U8, U9 and U10.

### Updates to section 3

- **U1** is now *explicit, owned by RP-6, unapplied*. The contract's 2026-10-18 note cites the
  ladder, and the program and pool ADR were never amended to it.
- **U2** gains the pool ADR's line 83: the "feature bundle" is named EO as the (m)ADR's successor,
  against 2026-10-30 (feature package) and 2026-11-03 (work package).
- **U7** gains the contract's own § Rulings of 2026-11-12, "RP-15 as tranche 6" (1065-1068), written
  after tranche retired on 2026-11-03.
- **U16** is now *owned by CO-2 on RP-6* (H2, H5), unapplied.
- **U19** is closed by track B as a confirmed unapplied surface: `command-doctrine.md:68-69`.

### New unresolved supersessions

20. **The contract contradicts itself in one ruling section.** § Rulings of 2026-11-03 places the repair order at the order level (1020), then says "Each order is a repair package" (1023). Its own § Repair orders table heads the packages "Order" (394).
21. **Two `WP-` series.** The drydock's WP-1 to WP-16 (2026-10-15/16, GHI-keyed) are still cited live in § Repair orders ("WP-16's effectiveness read per cut", RP-1 row 397; "one WP-16 report per stage", RP-7 row 408). The catalog series `WP-<NN>-<slug>` already holds `WP-01-astral-toolchain`, and neither cites the other.
22. **Two R-series.** The appraisal's R1 to R6 (2026-10-17) and RP-13's retrofit tranches R1 to R3 (2026-10-31) share labels in one contract, and neither cites the other.
23. **`REQ-C<n>` against `REQ-<n>`.** Executive decision 1 (2026-10-16) set `REQ-C<n>`, and the 2026-10-17 rewrite keeps "the WP-4 shapes as civil-rule design input" standing (1214). The requirements model and the identity seam use `REQ-<n>`. Silent.
24. **"No separate document" against the feature package.** 2026-10-17 retired the EO rung with "no separate document" (494), and the 2026-10-30 general arrangement repeats "There is no bounded-advance document" (1189). The four-records run created the feature package on 2026-10-30 as a new record and cites neither. The two may be compatible, since the feature package carries no version, release or order, but no ruling says so.
