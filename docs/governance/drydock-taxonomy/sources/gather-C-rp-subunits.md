# Gather C: the RP-n specification pages' sub-units and self-names

Domain: `docs/governance/drydock-taxonomy.md` § 9 item 6. Gathered 2026-11-22, read-only. Every page
below was read whole, long pages paged with offset and limit. Store and ledger checks were run with
`grep`/`git log`, and their outputs are quoted where they matter.

Store and ledger facts these rows rely on, measured 2026-11-22:

- `data/catalog/work_packages.json` holds one record, `WP-01-astral-toolchain` (`kind: repair`,
  `aliases: ["RO-9"]`). Its `procedure` reads *"Task cards: RO-9 tranches 1 to 7"*.
- `data/catalog/orders.json` has `"orders": []`.
- `.gzkit/ledger.jsonl` has 0 rows naming `ORD-`, 0 `order_transitioned` rows and 0 rows naming
  `RP-12`. `WP-01-astral-toolchain` has 5 `work_package_transitioned` rows (initiated, frozen,
  commenced, accepted, closed) and 2 `work_package_issue_closed` rows. Its `closed` row is at
  2026-10-29T07:34:12Z, with decision `proceed` and attestor `g0`.
- Task trailers in `git log`, counted by prefix: `TASK-ro0-` 99, `ro1-` 9, `ro2-` 15, `ro3-` 18,
  `ro4-` 3, `ro5-` 17, `ro6-` 194, `ro7-` 3, `ro8-` 2, `ro9-` 89, `ro10-` 1, `ro11-` 4, `ro14-` 27,
  `ro15-` 2 and `rp12-` 43. No trailer starts `TASK-ro12-` or `TASK-ro13-`.
- The 190 commits whose subjects name `RP-12 O1` to `O3` all carry the trailer
  `TASK-rnd-repair-work-organization`. RP-12's O4 commits carry `TASK-rp12-o4-task3`, `-task4` and
  `-task5`.

## Per page

| Page | Self-name, title and body (quoted) | Sub-units: name, count, example id | Sub-unit id in a store or ledger? | Gate 5 / attestation recorded | Naming status |
|---|---|---|---|---|---|
| `harbor-ro1-cut-measurement.md` | Title *"RP-1 specification — stopping the bleeding, and measuring every cut"*. Banner *"Named `RO-1` until 2026-11-03; `RP-1` replaces it in live text and `RO-1` stays its alias"*. Body *"Repair order RO-1 of the harbor pilotage drydock"*. | **acts** (a) to (g): 7, lettered, e.g. *"act (c)"*. **steps** of "The protocol, per cut stage": 5 (Size, Meaning retention, Instruction eval, Ruling, Record). **contractor acts**: 2, numbered 1 and 2. **stage**: RP-7's cut stages, each with a report `control-plane-cut-<stage>-<date>.md`. **restoration line**: 1. **rulings**: 3 bullets, unnumbered. The witness cites **"WP-16"**. | None. `TASK-ro1-` ×9 in commits only. | None. RP-1 is open, and its closure is stated in prose. | Title: RULED (contract § Rulings of 2026-11-03, operator *"A"*). Body "Repair order RO-1": CONTRADICTED by the same ruling. "acts (a) to (g)": SOURCED (contract § Repair orders, RP-1 row). Steps and contractor acts: UNSOURCED (agent page structure). |
| `harbor-ro2-identity-seam.md` | Title *"RP-2 specification — one identity seam for every reader"*. RO banner as on RP-1. Body *"Repair order RO-2 of the harbor pilotage drydock"*. Also *"This is phase 1 of `ADR-pool.identifier-ladder-migration`"*. | **tranches** 1 to 5, table `#`, e.g. *"tranche 3"*. The page says *"Each tranche is one act under § Records of the contract: one commit with a `Task:` trailer (`TASK-ro2-<slug>`)"*. **commands** 1 to 4 (the measurement). **phase** 1 and 2 (the pool ADR's). Baseline **rows** by kind (`parent`, `compose`). | None. `TASK-ro2-` ×15. | Closed 2026-10-19, recorded in the status prose and passage-log row 51 (*"operator brief from the coordinating session"*). No Gate 5 words and no ledger row. | Tranches: RULED, operator 2026-10-18 *"One RO, tranches (Rec.)"*. Body name: CONTRADICTED (2026-11-03 ruling). |
| `harbor-ro3-requirements-store.md` | Title *"RP-3 specification — the requirements store, empty"*. RO banner. Body *"Repair order RO-3 … one tranche per act"*. | **tranches** 1 to 4 (*"Each tranche is one act … one commit"*). The status line lists 2 to 3 commits per tranche, e.g. tranche 2: `2fa677a76`, `d39752974`, `a43f0220e`. **rulings** 1 to 12, numbered. | None. `TASK-ro3-` ×18. | Closed 2026-10-22 *"on the operator's word"*. Passage-log row 68 records the selection *"RO-3 closed (Rec.)"*. No ledger Gate 5. | Tranches: SOURCED (contract RP-3 row, *"four tranches"*). "One commit per tranche": CONTRADICTED by the page's own status line. Body name: CONTRADICTED. |
| `harbor-ro4-release.md` | Title *"RP-4 specification — release detached from the ADR"*. RO banner. Body *"Repair order RO-4"*. | **tranches** 1 to 4, named (Store and events, Version, Closeout, Skills and canon). **rulings** 1 to 7, plus ruling 8 under *"Change order of 2026-10-30"*. Restoration and Witness sections. | None. `TASK-ro4-` ×3. | None. Nothing of RP-4 has landed. | Tranches: SOURCED (page). Change order: RULED, operator 2026-10-30 *"yes, it blocks; RO-4 owns it"*. Body name: CONTRADICTED. |
| `harbor-ro5-work-packages.md` | Title *"RP-5 specification — work packages, task cards and repair orders"*. RO banner. Body *"Repair order RO-5"*. Ruling 1: *"A repair order is a work package"*. | **tranches** 1 to 6 (6 added by the change order of 2026-10-30, accepted 2026-10-31). **rulings** 1 to 10. **amendments** 1 to 4 (§ Amended 2026-10-28). **"Ruled 2026-10-28"** bullets: 6. **items** 1 to 8 (§ Amended 2026-10-31). **act**: *"The only RO-5 act landed is the never-evict lock act"*. **task cards**: the formal work package's procedure. | RP-5 has no store record. Its tranche 5 witness is `WP-01-astral-toolchain`. `TASK-ro5-` ×17. | None for RP-5. The witness package's Gate 5 is on the ledger, but that close is RP-9's. | Title "task cards": CONTRADICTED. Contract § Rulings of 2026-11-03: *"Task card is dropped"*. RP-12 ruling 21 lists *task card* as a rejected synonym. Ruling 1 "repair order is a work package": RULED 2026-10-25 *"A"*, CONTRADICTED by the level table (requirements model § 12). The page's own 2026-11-03 banner states the new reading without retiring ruling 1. Tranche 6: RULED (*"accept"*). |
| `harbor-ro6-canon-retirement.md` | Title *"RP-6 specification — superseded canon corrected"*. RO banner. Body *"Repair order RO-6"*. | **tranches** 1 to 3 (PRD; IEEE and ladder records; Skills, glossary and GovZero). **rulings** 1 to 9. **items** in "Items RO-6 retires or corrects". The contract's RP-6 row adds change orders **CO-1** and **CO-2** and **held rulings H2 to H5** from `harbor-classic-adr-change-order.md` (that record not read in full here). | None. `TASK-ro6-` ×194, all dated 2026-10-25 or later, most from 2026-11-08 on. | None. | Tranches: SOURCED. The status line *"Nothing of RO-6 has landed"* is stale against 190 later commits: a defect. Body name: CONTRADICTED. |
| `harbor-ro7-context-cut.md` | Title *"RP-7 specification — the rest of the context cut"*. RO banner. Body *"Repair order RO-7"*. | **stages** 1 to 7 (Rules, Nested AGENTS.md, Demotion list, Skill bodies, Agents and personas, Catalogue merge, AGENTS.md), e.g. *"stage 2"*. **rulings** 1 to 3. **change order** of 2026-11-08 (placement), pointing to `harbor-ro7-placement.md`. **leads**: 2. | None. `TASK-ro7-` ×3. | None. | Stages: SOURCED (#1246 *"Stage 1 is the rules narrative lift"*; contract row *"staged"*). Change order: RULED, operator 2026-11-08 *"place the entire endeavor into the existing and ongoing drydock"*. Body name: CONTRADICTED. |
| `harbor-ro7-placement.md` | Title *"RP-7 change order of 2026-11-08 — placement: gate, chore or rule"*. Body *"A dated record of the change order the operator issued on RP-7"*. No RO banner. | **change-order items** 1 to 5 (*"change order item 1"*). A second **change order** (2026-11-12, the hexagon test gates). **held rulings** H1 to H15. **findings** F1 to F24, graded blocks, due or deferred. **batches** A to D. **bands** A to C. **rules** *"Rule 1 of 5"* to *"Rule 5 of 5"*. Landed-table rows. Tests-policy **rows** #91 to #91d. | None. | None. | Self-name "change order on RP-7": RULED (contract § Rulings of 2026-11-08). H and F ids: UNSOURCED as a scheme, and their bare forms collide with other schemes (see Contradictions). |
| `harbor-ro8-in-flight-work.md` | Title *"RP-8 specification — the in-flight work disposed"*. RO banner. Body *"Repair order RO-8"*. | **acts** 1 to 4 (Carry, Withdraw, Release Package, Handback), *"Acts (for the contractor)"*. **rulings** 1 to 5. The contract's RP-8 row adds **CO-5**. | None. `TASK-ro8-` ×2. | None. | Acts: SOURCED. Their timing is ruled 2026-10-30 (*"A"*, twice): acts 1 to 3 run at the transfer of custody. Body name: CONTRADICTED. |
| `harbor-ro9-astral-toolchain.md` | Title *"RP-9 specification — the toolchain realigned to Astral's project discipline"*. RO banner. Body *"Repair order RO-9"*. Status *"RO-9 closed 2026-10-29 through `WP-01-astral-toolchain`'s Gate 5"*. | **tranches** 1 to 7 (*"Each tranche is one act … one commit … (`TASK-ro9-<slug>`)"*). Sections *"Ruled for tranche 4/5/6/7"* and *"Amended for tranche 4"* (×6). GHI #1184's **candidates**: 9 rows. Population **rows** 1 to 11. | Yes, the package only: `WP-01-astral-toolchain`, alias `RO-9` (not `RP-9`). Its `procedure` names the tranches as *"Task cards"*. No tranche has an id. `TASK-ro9-` ×89. | **Ledger**: `work_package_transitioned` to `closed`, 2026-10-29T07:34:12Z, `proceed`, attestor `g0`. This is the only RP with a ledger Gate 5. | Tranches: SOURCED (contract row *"seven tranches"*). "One commit per tranche": CONTRADICTED. Tranche 4 has at least 5 commits in WP-01's OQE, and passage-log row 70 reads *"RO-9 tranche 4, first two acts"*. Alias set: stale against the live name (#1302). Body name: CONTRADICTED. |
| `harbor-ro9-uv-project-norms.md` | Title *"uv's project model — the normative checklist RO-9 holds gzkit to"*. Body *"A record, read 2026-10-18"*, yet also *"Re-read it when uv moves a minor"*. No RP banner. Uses RO-9 throughout. | **sections** § 1 to § 8 of rule tables, plus *"Where uv is silent, and RO-9 decides"*. Cites **tranche 5** and **tranche 7**. No sub-units of its own. It is a reference record, not a package specification. | None. | Not applicable. | RO-9 name: UNSOURCED whether this is live text (must read RP-9) or a dated record (may keep RO-9). It calls itself both. |
| `harbor-ro10-safe-mode-classification.md` | Title *"RP-10 specification — safe-mode guard classification and A/B/C/D scheduling"*. RO banner. Body *"Repair order RO-10"* and *"Status: PARKED"*. | **versions**: lean (frozen) and heavy (to design). Heavy-version **sections** 1 to 5. Protection **kinds** 1 to 3. Rubric **steps** 1 to 5. **open questions** 1 to 4. **contractors**: 2. **rulings**: 7 bullets. **check levels** A, B, C and D. | None. `TASK-ro10-` ×1. | None (parked). | Parked: RULED (*"yes, draft RO-10 and park it"*). Sub-units: UNSOURCED. Body name: CONTRADICTED. |
| `harbor-ro11-intake.md` | Title *"RP-11 specification — intake"*. RO banner. Body *"Repair order RO-11"* and *"this order settles"*. | **tranches** 1 to 3 (The code, The records, The verbs). **rulings** 1 to 8. **doors**: 5 (the `source` values). **levels**: 3 (family, capability, outcome). | None. `TASK-ro11-` ×4. | None. | Tranches: RULED, accepted 2026-10-30 (*"the page and its tranches accepted by the operator the same day (yes)"*). Body name: CONTRADICTED. |
| `harbor-ro12-contractor-kit.md` | Title *"RP-12 specification — the contractor kit"*. RO banner. Body *"Repair package RP-12 of the harbor pilotage drydock, a repair order when this page was opened (the repair strata ruling, 2026-11-03)"*. | **orders** O1 to O9 (ruling 25 table *"Order"*), e.g. *"O2"*. Ruling 165: *"O1 to O9 are this page's build orders, not ledger orders"*. **tasks** within an order: O2 tasks 1 to 5, O3 tasks 1 to 7, O4 tasks 1 to 5, e.g. *"O4 task 5"*. **acts** within a task, e.g. *"O2 task 3 act 1"* to *"act 6"* and *"O4 task 1, act 2"*. **rulings** 1 to 205. **refusals** 1 to 15 (the witness floor). **open points** 1 to 12 (all closed). Per-order **dock trial** (sweep, red proofs, flight, inspection). **inspections** first to eighth (O2). **findings** 1 to 11 (O3's inspection). Probe **runs** 1 to 9. **record decisions** A1 to A8, B1 to B12 and C1 to C12 (from the R&D record). | **None.** `orders.json` is empty, the ledger has no `ORD-` row, and RP-12 has no `WP-` record. Ruling 43 makes a short name such as `O2` an alias, and ruling 49 makes it unique within its package, but no record exists to carry one. The only `ORD-` id ever booked is `ORD-01-fix`, in the dock-trial throwaway project. Commit subjects name *"(RP-12 O4 task 5)"*. Trailers: O1 to O3 `TASK-rnd-repair-work-organization`, O4 `TASK-rp12-o4-taskN`. | O1 to O4 Gate 5s are **dated prose sections** of this page under ruling 165 (*"Proceed: O1 attested"* 2026-11-20, O2 and O3 the same day, *"Proceed: O4 attested"* 2026-11-22). Ruling 165: *"no ledger row is written for it by hand"*, to ride O9's carry (rulings 10 and 165). Package: none. | Package name: RULED (2026-11-03 rename; ruling 25 quotes the repair strata ruling *"Package at RO level (Recommended)"*). "O1 to O9 are repair orders": RULED by ruling 25 (2026-11-04, *"A"*), CONTRADICTED by ruling 165 (2026-11-20, *"A: Kit now, O4 later (Rec.)"*). "act became task": RULED by ruling 25, CONTRADICTED by the page's acts nested under tasks. |
| `harbor-ro13-mode-contract.md` | Title *"RP-13 specification — the two-way mode contract"*. RO banner. Body *"Repair order RO-13"*. | **tranches** with letter ids. Foundation **F1 to F5**, before the retrofit **T0**, Retrofit **R1 to R3**, e.g. *"F2, the place of call"*. Ruling 11: *"a tranche at a time"*. **rulings** 1 to 11. | None. No `TASK-ro13-` trailers. | None. | Tranches: RULED, accepted 2026-10-31 (*"i accept"*). The contract's RP-13 row says *"Foundation tranche"* (singular) where the page has five: CONTRADICTED. Body name: CONTRADICTED. |
| `harbor-ro14-obpi-forward-migration.md` | Title *"RP-14 specification — the forward migration from OBPI to work package"*. RO banner. Body *"Repair order of the harbor pilotage contract"*, with no number. Ruling 3: *"The migration is its own order"*. | **tranches** 1 to 3. Tranche 1 is *"cut into acts"* 1 to 7, each with an *"Act N's reading"* section. **rulings** 1 to 24. An **exit item** (§ Exit item 12). **exits**: reopen, departure, hold and terminate. | None. `TASK-ro14-` ×27. | None. | Tranches: RULED by ruling 3 (2026-10-31, *"a"*: *"in three tranches, with an exit item"*). Acts in a tranche: SOURCED (page). Body "repair order": CONTRADICTED by 2026-11-03. |
| `harbor-ro15-project-structure.md` | Title *"RP-15 specification — maximal Astral project structure"*. RO banner. Body *"Repair order of the harbor pilotage contract, added by amendment"*. Ruling 1: *"Project structure is a repair order"*. | **tranches** 1 to 6 (6 by the change order of 2026-11-12). That change order's **items** 1 to 3. **Landed** items 1 to 3. **rulings** 1 to 4. **open points** 1 to 3. The starter's acceptance **rows** A01 to A18. | None. `TASK-ro15-` ×2. | None. | Ruling 1: RULED, operator *"I consider that RO worthy"* (pre-2026-11-03, now read as a package). Tranches: SOURCED. Body name: CONTRADICTED. |
| Contract `harbor-pilotage-candidate-2026-10-15.md` § Repair orders | Section *"Repair orders"*. Table column **"Order"**, rows `RP-0` to `RP-15`, *"In dependency order"*. The text says *"the orders are RP-0 to RP-13 as the table stood, with RP-14 and RP-15 added"*. | The rows cite: RP-1 *"acts (a) to (g)"*; RP-2 *"one order in five tranches"*; RP-3 *"four tranches"*; RP-5 *"tranche 6"*; RP-14 *"Tranche 1/2/3"*; RP-12 refusals (1) to (9); RP-13 *"Foundation tranche"* and *"Retrofit tranches"*; RP-6 CO-1, CO-2 and held rulings H2, H4, H5; RP-8 CO-5; RP-9 *"seven tranches"*; RP-7 *"one WP-16 report per stage"*. The rows sit in this order: 0, 1, 2, 3, 5, 14, 12, 13, 11, 15, 4, 6, 7, 9, 8, 10. | None. The packages are not in the store (#1302). | Exit 9 requires each order closed through the operator's Gate 5. § List of discrepancies: *"an order closes through the operator's Gate 5 only when all its lines are cleared"*. | Column "Order" for packages: CONTRADICTED by the level table (draft T10). Rename: RULED 2026-11-03. |
| **RP-0** (no page) | Specified only in the contract's § Repair orders RP-0 row (*"the drydock itself"*, *"this contract rewritten to the ratified plan …"*, owner *"the session"*) and its § List of discrepancies subsection *"RP-0 — the drydock itself"* (5 lines). | **acts**: passage-log rows *"RO-0 act: …"*. No tranches. | None. `TASK-ro0-` ×99. | None. | Name: RULED (2026-11-03 rename). Specification home: the contract row alone, UNSOURCED as a choice (no ruling says RP-0 needs no page). |

File names. Every page is named `harbor-roN-*` while its live name is `RP-N`. The 2026-11-03
ruling's scope (*"live text only. Rename in the general arrangement, § Repair orders, § Exit and
other current prose"*) does not mention file paths, so keeping the old names is UNSOURCED (neither
ruled nor contradicted). Two prefixes are each shared by two files:

- `ro7` covers the RP-7 specification and RP-7's change-order record.
- `ro9` covers the RP-9 specification and a uv reference record.

No convention says which file kinds take a `roN` prefix. RP-6's and RP-8's change-order record is
named `harbor-classic-adr-change-order.md`, with no `roN` prefix, while RP-7's is `harbor-ro7-placement.md`.

## Sub-unit vocabulary across pages

| Unit name | Pages using it | Meaning | Consistent? |
|---|---|---|---|
| tranche | RP-2, 3, 4, 5, 6, 9, 11, 13, 14, 15; contract rows; WP-01 `procedure` | An ordered slice of a package's work. Its weight differs by page: one act and one commit (RP-2, 3, 9), a container of acts (RP-14), a letter-coded unit (RP-13 F/T/R), a store "task card" (WP-01), or *"what a tranche was is a repair order"* (RP-12 ruling 25). | **No.** It holds five different weights. |
| act | RP-0 (passage log), RP-1, RP-2, 3, 9 (= tranche), RP-5, RP-8, RP-14, RP-12; contract § Records | One commit with a `Task:` trailer (§ Records, RP-2/3/9). Lettered landed items (RP-1 (a) to (g)). Numbered contractor steps (RP-1 1 and 2). Top-level work items (RP-8 Carry to Handback). Parts of a tranche (RP-14 1 to 7). Parts of a task (RP-12 *"O2 task 3 act 5"*). Retired into "task" (RP-12 ruling 25). Maintenance acts (RP-12 record C1 to C12). Tag acts issue, hang, authorize and clear (RP-12 ruling 6). | **No.** It is the most overloaded word. |
| order / repair order | every page's body; RP-5 ruling 1; RP-12 O1 to O9; RP-14 ruling 3; RP-15 ruling 1; contract column | The package itself (the old RO-n sense and every page body). A ledger order `ORD-<NN>-<slug>` (ruling 43). A build order O1 to O9 (ruling 165). | **No.** |
| O*n* (order alias) | RP-12 only | Its nine build orders, each with a Gate 5 in prose. In the grammar it would be an alias (ruling 43), but none is booked. | Within RP-12: no (rulings 25 and 165). |
| task | RP-12 (O*n* tasks); RP-5 ("task cards" become "task", 2026-11-03) | One of an order's tasks, reviewed and closed on the operator's word. Ruling 25 reads it as the old "act", but acts still sit inside it. Also a `TASK-` id, minted at run time. | **No.** |
| task card | RP-5 title and amendment 1, WP-01 `procedure`, RP-5 pen and ink | The procedure's units, read as RO-9's tranches in WP-01. | **No.** Dropped 2026-11-03 and a rejected synonym (RP-12 ruling 21). |
| stage | RP-1, RP-7 (1 to 7); RP-14 (pipeline "stage table", "Stage 4") | A cut stage measured by RP-1's protocol, or a pipeline stage. | No. Two meanings. |
| step | RP-1 (protocol 1 to 5), RP-10 (rubric 1 to 5) | A procedure step. | Yes within each page. Not an id. |
| item | RP-5 (§ Amended 2026-10-31, 1 to 8), RP-7 placement (change-order items 1 to 5), RP-15 (change-order items 1 to 3; Landed items 1 to 3), RP-14 and the contract (Exit items 1 to 13) | A numbered clause of a change order or of § Exit. | Loosely. |
| change order | RP-4, 5, 7, 7-placement, 15; contract RP-6 and RP-8 rows (CO-1 to CO-6) | A dated scope change the operator issues on a package. In RP-5 and RP-15 it adds a tranche; in RP-4 it adds a ruling; in RP-7 it adds a separate record. The ladder rung's definition is RP-5 amendment 3. Only the classic-ADR record numbers them (CO-*n*). | Partly. The form varies, and the numbering exists only in one record. |
| phase | RP-2 (the pool ADR's phases 1 and 2), RP-10 (ADR-0.0.74's "Phase 2"), contract (superseded regime phases) | A borrowed or older unit, not the page's own. | Not applicable. |
| ruling *n* | RP-3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 15 numbered; RP-1, 2, 9, 10 bulleted | Local numbering per page, cited as "RP-12 ruling 43". It is not an id in any store; insight scopes hold the words. | No. Bulleted and numbered pages are mixed. |
| refusal *n* | RP-12 (1 to 15); contract RP-12 row (1 to 9) | A witness-floor row. | Yes. Ruling 29 lets the page grow the list. |
| open point / open question | RP-12 (1 to 12), RP-15 (1 to 3), RP-10 (1 to 4) | An unruled question. | Two names for one thing. |
| F*n* / R*n* / T0 | RP-13 (F1 to F5, T0, R1 to R3) | Tranche ids. | They collide (see Contradictions). |
| H*n* / F*n* | RP-7 placement (H1 to H15, F1 to F24) | Held rulings and graded findings. | They collide. |
| dock trial / sweep / flight / probe / inspection | RP-12 (per O*n*) | Verification units of an order. | Within RP-12 only. Ruling 201 narrows them from O5 on. |
| Restoration (list-of-discrepancies lines) | RP-1, 4, 5, 6, 7, 11, 13 | A section that points to the contract's lines. | Yes. |
| version (lean / heavy) | RP-10 | Two design depths. | Not applicable. |
| WP-*n* (legacy) | RP-1 l.16 (*"WP-16's effectiveness read per cut"*); contract RP-1 and RP-7 rows | The pre-catalog work packages WP-1 to WP-16 (superseded record). | It collides with the live `WP-<NN>-<slug>` series. |

## Contradictions

1. **RP-12's O1 to O9.** Ruling 25 (2026-11-04, *"A"*): *"RP-12 is a repair package, what a
   tranche was is a repair order with its own Gate 5, and what an act was is a task"*. Ruling 165
   (2026-11-20, *"A: Kit now, O4 later (Rec.)"*): *"O1 to O9 are this page's build orders, not
   ledger orders"*. Ruling 43 adds *"A short name used in a specification, such as this page's
   `O2`, is kept as an alias"*, yet `orders.json` is empty.
2. **RP-12's acts inside tasks.** Ruling 25 says *"what an act was is a task"*. The page then
   writes *"O2 task 3 act 1"* to *"act 6"* and *"O4 task 1, act 2"*.
3. **One tranche, one commit.** *"Each tranche is one act under § Records of the contract: one
   commit"* (RP-2 l.162, RP-3 l.134, RP-9 l.143). Against it:
   - RP-3's status line lists 2 to 3 commits per tranche.
   - Passage-log row 70 reads *"RO-9 tranche 4, first two acts"*.
   - WP-01's OQE lists 5 tranche-4 commits.
   - RP-14 l.80 reads *"Tranche 1, cut into acts"* 1 to 7.
4. **What a tranche is.** WP-01 `procedure` reads *"Task cards: RO-9 tranches 1 to 7"*. RP-12
   ruling 25 reads *"what a tranche was is a repair order"*. The contract's 2026-11-03 ruling reads
   *"Task card is dropped"*. RP-5's title still reads *"…task cards and repair orders"*.
5. **"A repair order is a work package."** RP-5 ruling 1 (2026-10-25, *"A"*) says so, and so does
   RP-15 ruling 1 (*"Project structure is a repair order"*, *"I consider that RO worthy"*). The level
   table puts a repair order at the Order level and a repair package at the Story level. Neither
   ruling is marked superseded.
6. **Live self-names.** Every body except RP-12's reads *"Repair order RO-n"* or *"Repair order
   of the harbor pilotage contract"*. The 2026-11-03 ruling reads *"`RP-n` replaces `RO-n` in live
   text … Each order is a repair package"*. The banner exempts only *"the dated rulings below"*.
7. **Task-trailer prefixes.** Contract § Records says *"`TASK-ro<n>-<slug>` until the repair
   tagging scheme lands"*. RP-12 O4 uses `TASK-rp12-o4-taskN`. RP-12 O1 to O3's 190 commits carry
   `TASK-rnd-repair-work-organization`. RP-14 ruling 22 reads *"a commit is the package's when its
   `Task:` trailer starts with the lowercased package id"*, and no commit carries such a trailer.
8. **The alias set and an example id.** WP-01's `aliases` are `["RO-9"]` only, without the live
   `RP-9`. RP-5 ruling 7's example *"`WP-07-astral-toolchain (RO-9)`"* differs from the actual
   `WP-01-astral-toolchain`.
9. **Legacy `WP-16`.** RP-1 l.16 and the contract's RP-1 and RP-7 rows use *"WP-16"* as live text,
   which collides with the live `WP-<NN>-<slug>` series. Requirements model § 2 reads *"a retired
   code is never reused"*.
10. **Bare-id collisions.**
    - `F2` is an RP-13 tranche (*"F2 builds on what it leaves"*) and also an RP-7 finding (contract:
      *"finding F2"*).
    - `R1` to `R3` are RP-13 retrofit tranches and also the contract's rulings of 2026-10-17
      (*"R1 (2026-10-17): the repair order mirrors…"*, quoted in RP-5; *"R2"* and *"R3"* in RP-4).
      `R3` is also a family capability in RP-8.
    - `H1` is an RP-7 placement held ruling, a classic-ADR held ruling (contract Exit 9 *"held
      ruling H1"*) and a superseded harbor leg.
    - `T0` (RP-13) sits beside the draft's T1 to T11.
11. **RP-13's foundation.** The contract reads *"**Foundation tranche:**"* in the singular. The page
    has five foundation tranches, F1 to F5 (*"the foundation tranches land after RO-11"*).
12. **Three homes for Gate 5.** RP-9's is a ledger row, RP-12's O1 to O4 are prose sections of
    their page, and RP-2's and RP-3's are a "closed" status with no Gate 5 at all. Exit 9 requires
    *"each repair order closed through the operator's Gate 5"*.
13. **RP-6's stale status.** *"Nothing of RO-6 has landed"* (2026-10-25) is stale against 190
    `TASK-ro6-` commits from 2026-11-08 on. This is a defect, not taxonomy.
14. **The uv-norms page.** It calls itself *"A record, read 2026-10-18"* yet asks to be re-read at
    each uv minor, and it keeps `RO-9` with no rename banner. Its status as live or dated is
    unruled.
15. **"Order" means three things in RP-12:**
    - the package (body: *"a repair order when this page was opened"*);
    - the build order O*n* (ruling 165);
    - the ledger order `ORD-` (rulings 43 and 44).

## Files read in full

| File | Lines (wc -l) | Read |
|---|---|---|
| `docs/governance/drydock-taxonomy.md` | 149 | whole |
| `docs/governance/harbor-ro1-cut-measurement.md` | 47 | whole |
| `docs/governance/harbor-ro2-identity-seam.md` | 204 | whole |
| `docs/governance/harbor-ro3-requirements-store.md` | 173 | whole |
| `docs/governance/harbor-ro4-release.md` | 60 | whole |
| `docs/governance/harbor-ro5-work-packages.md` | 106 | whole |
| `docs/governance/harbor-ro6-canon-retirement.md` | 53 | whole |
| `docs/governance/harbor-ro7-context-cut.md` | 73 | whole |
| `docs/governance/harbor-ro7-placement.md` | 193 | whole |
| `docs/governance/harbor-ro8-in-flight-work.md` | 55 | whole |
| `docs/governance/harbor-ro9-astral-toolchain.md` | 366 | whole |
| `docs/governance/harbor-ro9-uv-project-norms.md` | 133 | whole |
| `docs/governance/harbor-ro10-safe-mode-classification.md` | 84 | whole |
| `docs/governance/harbor-ro11-intake.md` | 46 | whole |
| `docs/governance/harbor-ro12-contractor-kit.md` | 828 | whole, in seven chunks |
| `docs/governance/harbor-ro13-mode-contract.md` | 68 | whole |
| `docs/governance/harbor-ro14-obpi-forward-migration.md` | 173 | whole |
| `docs/governance/harbor-ro15-project-structure.md` | 141 | whole |
| `data/catalog/work_packages.json` | 65 | whole |
| `data/catalog/orders.json` | 4 | whole |
| `docs/governance/harbor-pilotage-candidate-2026-10-15.md` | 1953 | **not whole.** Read: the heading list; ll. 340–479 (§ Mandate tail, § Records, § Repair orders whole, § Exit whole); ll. 1010–1030 (§ Rulings of 2026-11-02 and 2026-11-03 whole); ll. 1337–1380 (superseded § Work packages, lines cut at 400 chars); ll. 1475–1554 and 1584–1784 (superseded chart, § Work packages added, § List of discrepancies whole). The passage log (ll. 1782–1953) was only grep-sampled. |

Not read, though cited by these sources: `docs/governance/harbor-classic-adr-change-order.md` (the
CO-*n* and H-*n* units), `docs/rnd/repair-work-organization.md` (the repair strata ruling's verbatim
words) and `docs/governance/ieee/requirements-model.md` § 12.

## Gap-fill

Added 2026-11-22 at the coordinator's request. Still read-only. Three sources, each read whole:

- `docs/governance/harbor-classic-adr-change-order.md` (148 lines);
- `docs/rnd/repair-work-organization.md` (612 lines);
- the contract's § Passage log, ll. 1782–1953 of `harbor-pilotage-candidate-2026-10-15.md`, every row
  read, no sampling.

Two checks were also run: `grep -c work_package_changed .gzkit/ledger.jsonl` returned **0**, and a grep
of `safe-mode-doctrine.md` for *return to service package*, *tranche* and *act* gave the doctrine
lines quoted below. Requirements model § 12 was not read; another track covers it.

### The repair strata ruling, verbatim

`docs/rnd/repair-work-organization.md` § *decision · the repair strata: the repair package at RO
level, the repair order at tranche level, the task at act level*, ruled 2026-11-02. Option A as put:

> **A** repair package is what RO-14 is today, the reason and scope; repair order is what a tranche
> is today, an ordered set of tasks toward that reason; task is what an act is today; the existing
> `kind: repair` record stays the repair package and the release rule stays true; cost, `RO-n`
> becomes a misnomer and *tranche* and *act* retire.

The operator selected **"Package at RO level (Recommended)"**. The record then adds: *"This
corrects the sentence in RO-5 ruling 1, 'A repair order is a work package': the record that ruling
built is the repair package."*

The same record also traces where the two words came from: *"Act enters the contract at `8984ba022`
(2026-10-16), the pilotage chart, agent-drafted. No ruling defines it."* *"Tranche enters the
contract at `e89b30089` (2026-10-18), specifying RO-2. Its one ruling is a selection on one order's
shape: 'One RO, tranches (Rec.)'."* It also says *"The one-commit rule does not describe the
practice"*: `TASK-ro14-wp-airlock-#1185` and three other trailers each carry three commits, and 40
commits carry no `Task:` trailer.

Related rulings in that record:

- **Four levels on both sides.** Operator: *"yes, that's the structure"*. The top row was later
  named feature package and return to service package (*"it should be called a return to service
  package"*).
- **An order is a real record.** Option A as put: *"a real record with an id, an ordered task list,
  its REQ bindings, and its own freeze and inspection, Gate 5 staying at the package"*. Operator:
  *"a"*. The Gate 5 part was later superseded by *"Gate 5 sits at the order"*, operator *"answer was
  A"*.
- **The rename.** Option A as put: *"`RP-n` replaces `RO-n` in the contract and specifications by
  contract amendment, keeping the numbers, `RO-n` staying an alias through the identity seam,
  ledger rows, commits and handoffs staying as written, the record id staying `WP-<NN>-<slug>`"*.
  Operator: *"A"*.
- **The incident's package.** *"every opening of the marker has one, written from diagnosis for an
  incident, where the contract is that package"*. Operator: *"a"*. The doctrine carries it at
  `safe-mode-doctrine.md:41`: *"where the drydock contract is that package"*.
- **The task.** *"the unit of action is the **task**. *Task card* is dropped."*
- **The canon form.** The level table is canon (operator: *"yes, it stands; use 'none (new)' the
  table needs to kept and associated as canon"*).

### New sub-unit names and ids found

| Unit / id | Where | Meaning | In a store or ledger? |
|---|---|---|---|
| **CO-1 to CO-7** | classic-ADR record § The change orders | Change orders numbered **across** owning orders, not per package: CO-1 and CO-2 on RP-6; CO-3 on RP-4; CO-4 on RP-5, RP-12 and RP-14; CO-5 on RP-8; CO-6 on the *design acceptance* discrepancy line (RP-0, holder D); CO-7 on *"the contract itself, by amendment only"*. CO-3 and CO-4 are *"Confirmation only"*. | No. `work_package_changed` has **0** ledger rows, so no change order of any rung is booked anywhere. |
| **H1 to H6** (classic ADR) | the same record § Held rulings; passage log rows 1919–1924 | Six held rulings, all ruled 2026-11-08. My earlier RP-6 row said *"H2 to H5"*: **corrected to H1 to H6.** | No. |
| **ADR-`[0-9]{4,}`** and edition file **ADR-`[0-9]{4,}`-`[0-9]{3,}`-slug.md** | classic-ADR record H5; passage log row 1923 | The sequential decision id and its edition reference. The sequence starts at 0001 at the crossover commit (H4). | Not yet minted. The crossover is unlanded. |
| **the passage log's "Act" column** | passage log header `\| Date \| Act \| Before \| After \| Commit \| Witness \|` | Every row is filed as an act. | Document only. |
| lettered acts **A, B, C** | passage log rows 1855–1857 (RO-9 tranche 4, 2026-10-23) | Acts inside a tranche. | No. |
| incident-numbered acts **act 1 to 3** | rows 1852–1854 (*"CI red on `872fb99c8`, act 1/2/3"*) | Acts numbered per CI incident, not per tranche. | No. |
| **hidden finding 1 to 4** | rows 1860–1863 | Findings a seam fix surfaced. | No. |
| **witness repair** | rows 1812 (RO-0), 1834 (RO-2 tranche 5) | An unnumbered follow-up act. | No. |
| **first act / second act** | rows 1810–1811 (RO-0) | RP-0's acts, ordinal. | No. |
| **TEST FLIGHT** | row 1903 | RP-5's witness flight closing WP-01. | Its Gate 5 is on the ledger (WP-01 `closed`). |
| **session cycle** | rows 1819, 1837 | A drydock exit and re-entry. | Ledger (`mx_session_*`). |
| **WP-1 to WP-16** (legacy) | rows 1793, 1795, 1801, 1802, 1805 | Pre-catalog work packages, renamed from WO on 2026-10-16. Operator, verbatim: *"retire it, work package everywhere - change now: 'WO-1 to WO-11' to WP"*. Row 1801 also reads *"WP-1 to WP-11 keep their numbers and GHIs"*. | No store record. Each is keyed to a GHI (WP-1 #1242 … WP-16 #1252). |
| **harbor legs H1 to H10, drydock repairs D1 to D6** | row 1796 (H1 to H10); row 1798 folds H10; the superseded chart lists H1 to H9 | Units of the superseded chart. | No. |
| **executive decision n**, **Q1/Q3/Q5/Q6**, **S2-080**, **R1 to R6**, **Mandate n**, **row n** (R&D disposition) | passage log, scattered | Ruling, question, control and disposition ids. | Only S2-080 sits in a data file (`data/obpi_pipeline_control_inventory.json`). |
| **visit**, **squawk**, **check A/B/C/D**, **return to service package** | repair-work-organization record | Level and occasion terms. | Check levels are on chores (`check: {level, provisional: true}`, disposition row 3). |

### New contradictions

16. **Tranche and act were retired, but are still in use.** The strata ruling (2026-11-02,
    *"Package at RO level (Recommended)"*) took option A, whose stated cost is that *"tranche and act
    retire"*. After the ruling they remain live units:
    - RP-12 *"O2 task 3 act 1"* (2026-11-07);
    - RP-15 *"tranche 6"* (change order of 2026-11-12);
    - RP-13 tranches F1 to F5 and R1 to R3;
    - RP-5 tranche 6.

    The contract's adopting § Rulings of 2026-11-03 does not repeat the retirement.
17. **The strata ruling was applied to one package only.** It puts the repair order at the tranche
    level (*"repair order is what a tranche is today, an ordered set of tasks toward that reason"*).
    Only RP-12 recut its tranches as orders (ruling 25). The tranches of RP-4, 5, 6, 11, 13, 14 and
    15 still have no order record, no freeze and no Gate 5 each. RP-14 ruling 3 (*"in three
    tranches"*) stands unamended.
18. **The order record lost its fields.** The R&D ruling said *"an order is a real record with an
    id, an ordered task list, its REQ bindings, and its own freeze and inspection"* (operator *"a"*).
    RP-12 ruling 46 (2026-11-05, *"b"*) made it *"thin … no REQ list"*, with *"the tasks' order is
    the ledger's"*. Ruling 165 then made O1 to O9 *"build orders, not ledger orders"*. Neither later
    ruling cites the R&D ruling it narrows.
19. **"Change order" has two meanings.** RP-5 amendment 3 defines a change order as a ladder rung
    *on a package* (*"a change to scope, boundary or test … issued only by the operator"*). The
    classic-ADR record's CO-7 is a change order owned by *"the contract itself, by amendment only"*,
    which contract § Records B1 calls a contract amendment, *"never through a repair order"*. CO-6
    is owned by a discrepancy line. CO-3 and CO-4 are *"Confirmation only"* and change nothing. No
    `work_package_changed` row exists for any CO-n.
20. **Every passage-log row is filed as an act.** The column heading is "Act", yet the rows include
    rulings (*"classic ADR held ruling H1"*), specifications (*"RO-2 specified"*), contract
    amendments (row 1893), session cycles and change orders. Contract § Records reads *"§ Passage
    log is appended per act"*. The doctrine's item 5 (`safe-mode-doctrine.md:63`) reads *"One commit
    per act"*. Many rows cite *"this commit"* or several commits.
21. **RP-12's work is missing from the passage log.** The log's rows run to 2026-11-19, yet no row
    covers RP-12's rulings 1 to 205 or O1 to O4's tasks, acts, dock trials and Gate 5s (2026-11-04
    to 2026-11-22). RP-12 ruling 10 freezes the passage log only at O9's carry, and § Records still
    requires a row per act. RP-7 and RP-15 kept adding rows over the same period (rows 1917–1950).
22. **RP-9 tranche 4 numbers its acts three ways, with collisions.**
    - *"first two acts"* (row 1851, 2026-10-22);
    - *"act A"*, *"act B"*, *"act C"* (rows 1855–1857, 2026-10-23);
    - *"act 2"* (row 1866, 2026-10-24);
    - *"act B"* again (*"git sync, then act B"*, row 1875, 2026-10-24).

    "Act 2" and "act B" each name two different acts inside one tranche, and CI-incident rows add
    their own act 1 to 3.
23. **The return to service package is filled by the contract, which never says so.** The draft
    taxonomy's § 2 lists *"Return to service package | none: no record, no event, no verb"*. The R&D
    ruling and `safe-mode-doctrine.md:41` make *"the drydock contract"* that package for an
    incident. The contract never names itself one: its title is *"the harbor pilotage contract"*,
    and only its diagram node (l.114) and its 2026-11-03 ruling bullet name the level. The package
    exists as a document but not as a record, and T6 should say which it is asking about.

### Changes to the 15 earlier contradictions

- **#1 (RP-12's O1 to O9): strengthened.** The strata ruling and the "real record" ruling (both
  R&D, 2026-11-02 and 2026-11-03) back ruling 25's reading. Ruling 165 contradicts both, not only
  ruling 25.
- **#3 (one tranche, one commit): strengthened.** The R&D record measured the same failure
  independently (*"The one-commit rule does not describe the practice"*), and passage-log rows list
  several commits per act (row 1866: `501b5a228`, `c1d8555e8`; row 1917: 13 commits).
- **#5 (repair order is a work package): status changed.** The ruling now has a ruled correction:
  *"This corrects the sentence in RO-5 ruling 1"* (2026-11-02). The contradiction stands only as the
  RP-5 page's unamended text, beside RP-15 ruling 1.
- **#6 (live self-names): strengthened.** Option A as put names *"the contract and specifications"*
  in scope. The RP-n rename does not cover the doctrine's *"naming the repair order"*
  (`safe-mode-doctrine.md:61,63`), which is not my source and is flagged only.
- **#7 (task-trailer prefixes): refined.** The RP-n ruling leaves *"commits … staying as written"*.
  No ruling says what a *new* commit's trailer is after 2026-11-03. Since then, 190 commits carry
  `TASK-ro6-`, O4 commits carry `TASK-rp12-`, and O1 to O3 commits carry
  `TASK-rnd-repair-work-organization`.
- **#9 (legacy WP-16): refined and widened.** The legacy names are **ruled**: WO-1 to WO-11 became
  WP, 2026-10-16, and *"WP-1 to WP-11 keep their numbers"*. Through WP-16 they are keyed to GHIs.
  The store's `WP-<NN>-<slug>` series (RP-5 ruling 6, 2026-10-25) shares that number space:
  `WP-01-astral-toolchain` and the legacy `WP-1` (GHI #1242, the orientation campaign block) are
  different packages with near-identical ids.
- **#10 (bare-id collisions): corrected.** The classic-ADR held rulings are **H1 to H6**, not H2 to
  H5. The passage log disambiguates by prefix (*"RP-7 held ruling H1"*, *"classic ADR held ruling
  H1"*), while the contract's RP-6 row and Exit 9 use the bare form (*"held ruling H4"*, *"held
  ruling H1"*). Harbor legs ran H1 to H10 (row 1796) before H10 was folded.
- **#12 (three homes for Gate 5): refined.** RP-0's only change order, CO-6, is owned by a
  discrepancy line and not by a package. RP-2's close is passage-log row 1832, written on an
  *"operator brief from the coordinating session"*, with no Gate 5 words. RP-3's is row 1849, by
  selection *"RO-3 closed (Rec.)"*.
- **#2, #4, #8, #11, #13, #14, #15: unchanged.**

Per-page table corrections:

- The RP-6 row's *"held rulings H2 to H5"* should read **H1 to H6**, with CO-1 to CO-7 spanning
  several orders.
- The vocabulary table's **act** and **tranche** should read **UNSOURCED** as definitions. Tranche
  was ruled only for RP-2's shape. Both were then **retired by ruling** (2026-11-02), which
  contradiction 16 records.

### Files read in full, gap-fill

| File | Lines (wc -l) | Read |
|---|---|---|
| `docs/governance/harbor-classic-adr-change-order.md` | 148 | whole |
| `docs/rnd/repair-work-organization.md` | 612 | whole, in four chunks |
| `docs/governance/harbor-pilotage-candidate-2026-10-15.md` § Passage log | ll. 1782–1953 (172 lines, 168 rows) | whole, in seven chunks |
