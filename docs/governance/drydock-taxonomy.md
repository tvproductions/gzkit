# Work and Repair Taxonomy (DRAFT)

> **Status: DRAFT for the operator's rulings, 2026-11-22. High consequence.** Not canon. It
> gathers in one place every level, record, identifier, short name, closed set and term of art
> that gzkit's work and repair structure uses today. For each it gives where it is defined, where
> code holds it, and where the places disagree. The open points are numbered **T1 to T35** for
> rulings. Where this page and a ruled source disagree, the source governs until a ruling here
> says otherwise.
>
> **Why it exists.** Opening RP-12's repair order 5 showed that the drydock's own packages and
> orders have no record in the system the drydock built. The operator, 2026-11-22: *"if this
> isn't documented in one place, we are in trouble already"*; *"this is a HIGH CONSEQUENCE
> document and decision set, this is meant to bring sanity out of the dry dock - high priority"*;
> *"we'll review ALL of the taxonomy (make sure it is thorough and exhaustive), and then settle
> this, finally and once-and-for-all."* Insight scope `drydock-formalism`.
>
> **How it was gathered.** The first draft (sections 1 to 6, `dd6cc87cc`) was measured by reading
> the code, the stores and the canon pages. The exhaustive pass of 2026-11-22 ran seven read-only
> tracks, A to G. Each track read its sources whole, checked every term against the 2,463 booked
> rulings (`gz handoff rulings`), and marked each term **ruled**, **sourced**, **contradicted** or
> **unsourced**. Its tables, verbatim quotations and line citations are kept as dated records
> under [`drydock-taxonomy/sources/`](drydock-taxonomy/sources/gather-G-naming-lineage.md). This
> page is their synthesis, and a source row governs where this page summarizes it.

## 0. What the gathering found, in brief

- **The level table holds.** Nothing later than its ruling contradicts the four levels of
  2026-11-03 (§ 1). The trouble lies around it, in five places:
  1. Older names that were never withdrawn from the surfaces that carry them.
  2. One word ruled in several senses.
  3. Code that was never brought up to the ruling.
  4. Sub-units below the task that the 2026-11-02 strata ruling retired and practice kept.
  5. Gate 5, found at four levels.
- **Naming was ruled again and again.** The lineage (§ 6) holds 73 naming rulings dated 2026-08
  to 2026-11-22. A second, complete ladder was ruled on 2026-10-05: engineering order, change
  proposal, task card and block. Its parts were retired one at a time, and the program page and
  the pool ADR that state it were never amended.
- **The terms and their status**, by track:

| Track | Domain | Term rows | Ruled | Sourced | Contradicted | Unsourced |
|---|---|---|---|---|---|---|
| A | drydock vocabulary, change ladder | 119 | 89 | 15 | 14 | 1 |
| B | control roles, personas, positions, crosswalk, the constitution | 119 (+28 rejected synonyms) | 66 | 37 | 13 | 3 |
| C | the RP-n pages' self-names and sub-units | 17 pages, 30 unit names | — | — | 23 contradictions | — |
| D | REQ kinds and specializations, records, gates, lanes, kinds, states, undo verbs | 117 | 52 | 24 | 40 | 1 |
| E | ledger events, alias mechanisms, identifier census | 107 events, 10 alias mechanisms, 28 identifiers | — | — | 10 contradictions | — |
| F | R&D, insights, GHI labels and states, chores, receipts and runs, handoff and ceremony files, the hexagon map | 165 | 71 | 67 | 17 | 10 |
| G | the naming lineage | 73 rulings | — | — | 24 unresolved supersessions | — |

Read for this page directly: `docs/governance/GovZero/charter.md`, whole (119 lines), the sole
authority for gate definitions (§ 5.4).

## 1. The four levels

Canon: `docs/governance/ieee/requirements-model.md` § 12, the level table (operator, 2026-11-03:
*"the table needs to kept and associated as canon - it captures the design very well"*; lineage
row 58).

| Level | Construction | Repair | Decides | Who |
|---|---|---|---|---|
| Epic | Feature package | Return to service package | why; value delivered, or seaworthiness | Operator |
| Story | Work package | Repair package | the cohesive grouping of orders; scope and footprint; initiation | Operator |
| Order | Work order | Repair order | the REQ-to-task binding; the freeze; inspection and buy-back; **Gate 5** | Coordinator, inspector, operator |
| Action | Task | Task | one recorded action, its measure, its (V) mark | Craftsman |

**What sits beside the levels** (requirements model § The records, § 7, § 12). The levels are the
work; three records frame it, and two more record and show it:

- **The catalog** says what must be true: PRD → family (`SES`) → capability (`SES1`) → outcome
  (`SES1.4`) → REQ (`REQ-1207`), with a feature file for each user-facing outcome. **The ADR**
  records one architecture decision, a peer of the catalog, never its parent.
- **The Release Package** says what is planned to ship. Its identifier is the version. It holds
  which outcomes a version is planned to carry and the repair packages it carries, and it may
  carry completed work orders from a work package that is not complete (operator, 2026-11-03:
  *"c - it is possible that a release package includes some completed work orders from a work
  package without completing the whole package, this is the decoupling we were working
  towards."*). It is mutable while a target. The ledger's release record is the shipped claim.
- **The input sets the release.** New construction and a remodel go to a Release Package, as a
  minor. A repair and a refactor go to a patch.
- **The ledger** records what happened, and **the backlog board** is a view of it, never edited.

Text that disagrees on the release:

- `templates/release_package.md` advances REQ states with `REQ-C0000` and `WP-0000` grammars
  (D C7).
- `adr-lifecycle.md:253` tags a release by the highest validated feature ADR (D C33).
- The 2026-10-05 ladder's *block* for the release was never withdrawn from the program page or
  the pool ADR (lineage row 12) (T14).

Canon already rules all three, and each has an owner in the drydock (read 2026-11-22):

- The template retires under RP-4 ruling 7: *"the package is a catalog record, not a document"*
  (`harbor-ro4-release.md:30`).
- The release-tag rule goes with RP-4 tranche 4, which retires the ADR-as-carrier text in
  `adr-lifecycle.md:227-277` (`harbor-ro4-release.md:44`).
- *Block* goes with RP-6 item 2, which corrects *"release → block"* in the ladder records
  (`harbor-ro6-canon-retirement.md:12, 44`). RP-6 leaves the pool ADR as is, because a pool entry
  is an intention (`:17`); that pool ADR is T14's.

All three are open because the owning work has not landed: *"Nothing of RO-4 has landed"*
(`harbor-ro4-release.md:56`).

The successions it rests on (lineage rows 56 and 57; operator, 2026-11-03: *"work package is the
mADR successor, the WO is the OBPI successor"*; *"A wins because you elevate the feature pack to
"epic" and keep the WP (mADR) as a story"*).

**Text that defines these levels otherwise, still live:**

- **The constitution's Order.** `command-doctrine.md:66-67` defines it as *"How command reaches
  the work: a standing order binds every position; a tasking order binds one work package"*, one
  order for the whole package (B 15) (T1).
- **The constitution's maintenance visit.** `command-doctrine.md:167-168` makes it *"a scheduled
  work package of the operator's own design"*, a third kind the store cannot hold (B 17) (T23).
- **The construction side's three names.** It is called *construction* (level table), `catalog`
  (the REQ specialization) and `delivery` (the package `kind`) (D C16) (T23).
- **Gate 5 sits at four levels.** By the source:
  - the order (§ 12);
  - the package close (`events.py:1819,1826`, RP-12 ruling 77, WP-01's close);
  - the outcome into `validated` (`events.py:1764`);
  - ADR and OBPI closeout (`charter.md:74-80`).

  The constitution also makes Gate 5 *the* return to service (`command-doctrine.md:68-69`) (T12).

## 2. Record identifiers

| Record | Identifier today | Grammar defined in | In the store, 2026-11-22 |
|---|---|---|---|
| PRD | `PRD-…` | identity seam (prefix) | live |
| Constitution | `CONSTITUTION-…` | seam (E census) | live |
| Family | three-letter mnemonic, `SES` (ruled 2026-10-30, lineage row 37) | requirements model § The records, § Family schemes | **single letters** `X H C M P D R G A L Q` in `data/catalog/families.json` and in the seed shipped to adopters, `src/gzkit/catalog_seed.json` (T8) |
| Capability | family + number, `SES1` | requirements model; its store `capabilities.json` and its `catalog capability` verb are ruled, not built (D C36) | **no store file exists** |
| Outcome | capability + dotted number, `SES1.4`, exactly three levels | requirements model; `OUTCOME_CODE_PATTERN` (`models/catalog.py:40`) accepts **one letter at any depth** (`H1`, `H1.4.2`) | 0 (T8) |
| Catalog REQ / repair REQ | `REQ-<n>`, area-free; `specialization: catalog \| repair` | seam `CATALOG_REQ_ID_BODY` | 0; a repair REQ **does** resolve through the seam, its `WP-` package as parent (E C8) |
| Legacy REQ | `REQ-<semver>-<NN>-<NN>` | seam | in OBPI briefs |
| Work package / repair package | `WP-<NN>-<slug>`, kind in the `kind` field (`delivery \| repair`) | `WORK_PACKAGE_ID_PATTERN`, `models/catalog.py:46` (RO-5 ruling 6, 2026-10-25) | 1: `WP-01-astral-toolchain` (repair, alias `RO-9`, closed) (T2) |
| Work order / repair order | `ORD-<NN>-<slug>`, kind read from its package | `ORDER_ID_PATTERN`, `models/catalog.py:49` (RP-12 ruling 43, 2026-11-05) | **0** (T3, T5) |
| Return to service package | **none** | none: no record, event or verb (#1303) | none (T6) |
| Feature package | *"to be named when its store lands"* | requirements model | none (T7) |
| Task | `TASK-<semver>-<NN>-<NN>-<NN>`, or `TASK-<slug>[-#<ghi>]` | seam (the slug form is classified, never resolved) | commit trailers in four spellings (T29) |
| ADR | `ADR-x.y.z-<slug>`, `ADR-pool.<slug>`; the classic ADR's `ADR-[0-9]{4,}-<slug>` is ruled, not landed (RP-6 H5) | seam | live (T33) |
| OBPI (legacy order) | `OBPI-x.y.z-NN-<slug>` | seam | live |
| Event | `EV-…` | `IDENTITY_MODELS`, not `IdKind` (E C9) | live |
| Release Package | the version | requirements model | live |
| Amendment | `AMD-<semver>-NN`, `REQ-<semver>-ANN-NN` (ruled 2026-09-27) | design-amendment R&D; ADR-0.40.0 | not built (T19) |
| Engineering order, change proposal | `EO-<semver>-<slug>`, `ECP-<slug>` (ruled 2026-10-05) | identifier migration program; `ADR-pool.identifier-ladder-migration` | never built; EO retired 2026-10-17 (T14) |

The identity seam (`src/gzkit/core/models.py`, `IdKind`) knows four kinds: **ADR, OBPI, REQ,
TASK**. `IDENTITY_MODELS` holds five, adding `EV`. The `gz validate --id-seam` witness scans only
those kinds, so at least nine drydock parse sites have none. The grammars live in three homes:
`core/models.py`, `models/catalog.py` and `events.py`. Folding them into one seam is sized at
about nine new kinds, nine grammar constants and six mint functions (E § 3a) (T9).

### 2.1 How a REQ relates to its place in the catalog (review called for in W2)

Read 2026-11-22 against the requirements model and `src/gzkit/models/catalog.py`, whole.

Canon: a catalog REQ is a member of exactly one outcome. The outcome sits in one capability, and
the capability in one family. The REQ's id is area-free (`REQ-1207`), so its place is the
`member_of` field and never the id. A work package draws REQs from any outcomes (amended
2026-11-03), and the order binds REQs to tasks.

Code, against that:

1. **The chain above the outcome is a string, not a record.** `member_of` names an outcome code.
   The capability exists only as that code's prefix, because no capability store is built. The
   family is a one-letter field (`Family.code`, pattern `^[A-Z]$`, *"The family's one letter"*).
   Nothing checks that `SES1` exists or that `SES` is a family.
2. **The outcome pattern takes any depth**, so `member_of` accepts `H1` (a capability's shape) or
   `H1.4.2` (four levels).
3. **A delivery package names one outcome.** `WorkPackage.outcome` is a single code, the
   2026-10-30 reading (*"one dated attempt to deliver one outcome"*). The 2026-11-03 amendment
   says a work package draws REQs from any outcomes.
4. **The order holds no REQs.** The REQ-to-task binding the level table gives the order lives
   only in its `frozen` event (ruling 46, thin record). The R&D ruled the order *"a real record
   with an id, an ordered task list, its REQ bindings"* (C 18). No task event can name an order
   (E C4).
5. **A repair REQ sits on the package, not the order.** `RepairReq.held_on` is a `WP-` id, and
   its only catalog link is an optional `aligns_to` a catalog REQ.
6. **Two other REQ forms place themselves by id.** The legacy `REQ-<semver>-NN-NN` encodes its
   ADR and OBPI. `REQ-C<n>` (executive decision 1, 2026-10-16) is still kept as design input
   (T35).
7. **The construction side has no orders yet, by ruling.** A delivery package holds no orders and
   keeps the five package states until RP-14 moves construction onto the order (RP-12 rulings 2,
   44 and 103). Until then a construction REQ has no order to bind it, so the level table's Order
   row is built for repair only.
8. **Stale docstrings in the same file**: *"task cards"* (`procedure`), *"Drydock names such as
   `RO-9`"* (`aliases`), *"its family letter"* (`OUTCOME_CODE_PATTERN`).

**Owners, read 2026-11-22.**

- RP-11 (`harbor-ro11-intake.md`, rulings 3 to 7, tranches 1 to 3) owns items 1 and 2: the
  three-letter re-code, the exact three-level pattern
  `^[A-Z]{3}[1-9][0-9]*\.[1-9][0-9]*$`, the capability records and the outcome's `source` and
  `modules`. Its tranche 1 does not list the seed shipped to adopters,
  `src/gzkit/catalog_seed.json`, which holds the single letters too: a gap in RP-11's scope.
- RP-5 ruling 7 owns the outcome's `withdrawn`.
- RP-14 owns the derived `validated` (RP-12 ruling 78).
- `member_of` is held to an existing outcome by `catalog_edges.py:186`.

## 3. Drydock records

| Record | Identifier | Defined in |
|---|---|---|
| Tag (tag-out log) | `TAG-<NN>-<slug>` | `src/gzkit/events.py` `TAG_ID_PATTERN`; RP-12 ruling 111 |
| Maintenance-record entry | `ENT-<NN>-<slug>` | `ENTRY_ID_PATTERN`; ruling 169 |
| Discrepancy | `DSC-<NN>-<slug>` | `DISCREPANCY_ID_PATTERN`; ruling 169 |
| Dispatch | `D-<16 hex>` | `DISPATCH_ID_PATTERN`; RP-12 ruling 1, built in O1 |
| MX session | a UUID | the marker |
| Change order (as numbered on pages) | `CO-1` to `CO-7` | page prose only; 0 `work_package_changed` rows (C gap-fill) |

The ids differ in digit width. The seam's ids take exactly two digits and the drydock ids two or
more, and two slug grammars stand side by side (E).

## 4. Short names and aliases

| Name | Means | Held where | Problem |
|---|---|---|---|
| `RP-0` to `RP-15` | the drydock's repair packages | the contract's § Repair orders table; the `harbor-roN-*.md` pages | not in the store; `gz wp show RP-14` fails (#1302); RP-0 has no page (T4, T30) |
| `RO-n` | the old name of those packages, an alias since 2026-11-03 | live text of every RP page but RP-12; `gz wp new --alias` help; `aliases` on WP-01 only | never resolved (#1302); the operator's *"RP-12/RO-5"* (2026-11-22) uses `RO-5` for an order, colliding with RP-5's alias (T3) |
| `O1` to `O9` | RP-12's repair orders | the kit page | *"build orders, not ledger orders"* (ruling 165); their Gate 5s are dated prose (T5) |
| tranches of RP-2 to RP-15 | what the 2026-11-02 strata made repair orders | each page | only RP-12 recut its tranches as orders; the others have no order record, freeze or Gate 5 (C 17) (T5) |
| `WO-1` to `WO-11` | work packages before 2026-10-16 | dated rows | retired 2026-10-16 (*"retire it, work package everywhere"*); requirements model § 2: *"a retired code is never reused"* (T3) |
| legacy `WP-1` to `WP-16` | the same packages renamed 2026-10-16, each keyed to a GHI | the contract (RP-1 and RP-7 rows, *"WP-16's effectiveness read"*) | a second `WP-` series beside `WP-01-astral-toolchain` (G 21) (T2) |
| an order alias | any word, such as `O2` | `ORDER_ALIAS_PATTERN` (ruling 43); ruling 49: *"resolves with the package beside it"* | no order exists; `gz wp order` matches the exact id only (E C2) |
| bare sub-ids | `F2`, `R1` to `R3`, `H1`, `T0` | RP-7, RP-13, the classic-ADR record, the contract's 2026-10-17 rulings | each names two or three different things (C 10, G 22) (T30) |

Ten alias mechanisms exist (E § 2). Three bear on T9:

- the free-text `WorkPackage.aliases`, with one instance, `RO-9`;
- `Order.aliases`, with none;
- the `artifact_renamed` fold, with 187 rows over ADR and OBPI ids.

Nothing resolves the first two.

## 5. Closed sets and vocabularies

### 5.1 What the drydock built (`src/gzkit/events.py` unless named)

- **Package states:** `initiated → frozen → commenced → accepted → closed`; a repair package
  uses `initiated → closed` (ruling 44). **Order states:** `opened → frozen → commenced → accepted
  → closed`.
- **Gate 5 decisions:** `proceed, redirect, pause, terminate`. **Exits:** `reopen, departure,
  hold, terminate`. `proceed`, `pause` and `hold` mean different things in these sets and in the
  handoff decision `proceed | pause | hold | revert` (F C8) (T31).
- **Change ladder:** canon has **four rungs**: pen and ink, change order, attachment and
  supplement. Alteration and departure from specification are separate records (RP-5 spec:57;
  kit:26). `WorkPackageRung` codes **six values** (`events.py:1787`), which the first draft
  copied (A 10) (T20).
- **Dispatch roles: six**, not four. They are `Implementer, SingleDriver, Repair, Restoration,
  SpecReviewer, QualityReviewer` (`work_package_run.py:87-94`). The reviewer is also named
  `"Reviewer"` (`pipeline_dispatch.py:31`) and split into spec and quality sub-roles in
  `roles.py:130` (B 3, 5) (T22).
- **Tag:** class `Danger | Caution`; position hung `off | advisory | recording`, found adds `on`;
  source `order-work | standard-disconnect | mel-bypass | surveillant-stop`; surface kind
  `validator | check | hook | path`; check level `C | D`.
- **Discrepancy:** grade `blocks-return-to-service | due-by-event`; source `left-broken |
  inspector-rejection | found-in-work`.
- **The out-of-service condition:** one state, level `hangar | drydock`; the marker's older
  `mode` `mx | safe` reads as its alias, and `mx_session_opened` still writes `mode` (E C7). Ruled
  2026-11-02 as synonyms with *one* depth, yet the code keeps two levels (A 1) (T17).

### 5.2 Drydock vocabulary (track A: 119 terms, 89 ruled)

Its terms of art are ruled and live:

- drydock, hangar, out of service, standby level, dock trial, sea trial, handback, transfer of
  custody, return to service, MEL with its (M) and (O) entries;
- seaworthiness, harbor pilot, pilotage chart, passage log, carry, sealed footprint and held REQ.

Contradicted:

- **Sea trial:** two approved forms against Part 0's fresh install only (A 3).
- **Handback:** whether the ratified handback comes before the exit (contract exit 9) or after it
  (doctrine, skill) (A 4). The same word is also used for a subagent's report back
  (`mx/discrepancies.py`, A 19) (T26).
- **Who opens and closes the hangar:** rulings 447 and 448 say the agent, *"Standing from this
  session forward"*; the skill, doctrine, contract and rule say the operator (A 17) (T25).
- **The floor:** the doctrine lists Gate 5, ledger, PII, the PRIME DIRECTIVE and no-control-removed;
  `mx/invariants.py` lists gate5-attestation, secrets, operator-pii, ledger and grader-gaming
  (A 9) (T25).

Unsourced: `quay`, found only in two superseded passage-log rows.

`src/gzkit/commands/mx_cmd.py` was read whole for this page (657 lines). It sides with the skill
on T25: *"The agent never opens the hangar on its own"* (line 5); *"Only the operator renews the
lease"* (line 606). It mixes two vocabularies in one function: `--mode must be mx or safe`
(line 324) beside *"--level drydock requires --contract"* (line 277). It prints the one condition
under two names, *"Safe mode opened"* and *"MX session opened"* (lines 390, 512) (T17).

### 5.3 Control roles, positions and personas (track B: 119 terms, 66 ruled)

- **Control roles.** The census defines gate, safeguard, tripwire, alarm, monitor and dispatcher
  (`census-code-controls.md:66-71`). That is the auditor's reading, and no operator ever ruled on
  it.
  - **Tripwire:** the census's *"any other blocking check"* against RP-10's *"does not stop the
    work … it records"*.
  - **Alarm:** the census's *"only announces or warns"* against RP-10's *"An alarm stops the work"*,
    which the doctrine's alarm test and `gzkit.mx.alarms` follow.

  RP-13 rulings 5 and 8 make the role label a ruled field of every MEL entry, so these contested
  definitions carry weight (B 1, 2, 13) (T21).
- **Positions.** The positions are craftsman, QAI/inspector, coordinator, surveillant, operator,
  captain, crew and orchestrating session, all ruled. No ruling maps the seven persona files to
  them.
  - `main-session` *"executes pipelines"*; the coordinator *"performs no work itself"*.
  - The craftsman performs the repair (A4), and the runtime gives that work to `Implementer`;
    ruling 175 *"leaves [it] standing"*.
  - Ruling 175 admits SingleDriver on an order, and `work_package_run.py:514` refuses SingleDriver
    on every repair package (B 4, 10) (T22).
- **Not built, though ruled:** the crosswalk JSON (`data/maintenance_crosswalk.json`), the term
  witness, the four kit personas, `gz-repair-pipeline`, and the QAI and surveillance dispatches.
  All are owed to RP-12 O6 and O8.
- **Rejected synonyms (28), each with its ruling** (B § 5a). Some are still live:
  - *punch list*, in the safe-mode banner itself (`mx/awareness.py:39`) and in `mx-mode.md`;
  - *fix cycle*, in kit rulings 57, 72 and 132, `count_fix_cycles` and `events.py:1793`;
  - *register*, in the gz-mx skill;
  - *restoration contractor*, in the WP-01 store.

  *Task card* is a rejected synonym under ruling 21 and was dropped on 2026-11-03, yet it is still
  in `models/catalog.py:218` and the decomposition matrix.

### 5.4 Gates, lanes, kinds and states (track D: 117 terms, 40 contradicted)

- **The charter.** `charter.md` is the *"sole authority for gate definitions"*. It defines Gate 5
  as ADR closeout and OBPI completion, with the closeout terms Completed, Completed — Partial and
  Dropped. It knows no order and no package, and none of the order-level decisions `proceed,
  redirect, pause, terminate`.
  - It says Gate 1 *"applies to all work"*, against an outcome with zero or more ADRs (D C26).
  - Its reference `config/governance_manifest.json` does not exist.
  - Its header reads *Last reviewed 2026-01-08*, but it was edited on 2026-10-10.
- **Gate 5 universality** (ADR-0.0.36) is contradicted by three sources:
  - `obpi-runtime-contract.md` and `obpi-transaction-contract.md` (heavy and foundation only);
  - `gate5-architecture.md:10` (*"code-documentation-intent alignment for Heavy lane work"*);
  - the manifest's `lite: [1,2]`. That one is ruled, so the conflict left is with the charter's
    lite *"1, 2, 5"* (D C1).
- **Lane's home.** Lane is keyed on the ADR (`AGENTS.md`), on the outcome's `user_facing`
  (§ 10), and on repair packages only (`catalog.py`). Gate 4 is bound to the heavy lane in one
  source and to `user_facing` outcomes in another (D C25, C27) (T24).
- **The pool.** It is *"intentions, not ADRs"* with an entry status `Pulled` (2026-10-25). Against
  that, `AGENTS.md` makes it an ADR kind and `adr-lifecycle.md` allows status `Pool` only. Its id
  is `ADR-pool.<slug>` in code and `ADR-0.2.0-pool.<slug>` in the lifecycle page (D C21, C22,
  C38) (T14, T33).
- **ADR states, OBPI states and the undo verbs.** Five state sets disagree. A dropped closeout
  ends `Deprecated` in one module and `Abandoned` in another. OBPI runtime states number 6, 7 or
  8 by source. `AGENTS.md` says *"Two verbs undo a completion"*, and the code has five. Repudiation
  *"reverses, it does not retire"* by ruling, yet it is listed among the terminal events
  (D C18 to C31) (T34).
- **REQ kinds and their checks** (BEHAVIOR, SUPPORT, STRUCTURAL-FENCE). Catalog and repair
  `REQ-<n>` cannot be resolved or checked by the fence resolver or `--req-kind-discipline`; it
  always reads `unproven-fence`. `proof_status` has three vocabularies. The doc and the code
  disagree on what the SUPPORT and STRUCTURAL-FENCE brief checks require (D C8 to C15) (T34).
- **The catalog's outcome.** Its ruled fields `withdrawn`, `modules` and `source` are missing from
  the model, which has `extra="forbid"`. `validated` is *"derived, not attested"* by § 12, yet
  requires an attestor in code (D C4 to C6, C37).

### 5.5 Ledger events (track E: 107 types)

- **78** of the 107 types record work or repair at some level. **29** have no ledger row: every
  order, tag, entry, discrepancy and dispatch event, `work_package_changed`,
  `outcome_transitioned` and `req_proof_recorded`.
- Only `WP-01-astral-toolchain` has package events: 5 transitions and 2 issue closes.
- **No event exists at the Epic level.**
- **TASK events cannot name an order.** They require `obpi_id` and `adr_id`, against RP-12
  ruling 46, *"A task binds to its order by its own ledger events naming the order"* (E C4).
  `tasks.py` chains task → REQ → OBPI → ADR (F C24) (T29).

### 5.6 R&D, GHI, chores, receipts, files, hexagon (track F: 165 rows)

- **"Work order" means a GHI** in `rnd-discipline.md:301`, `agents-md-map-doctrine.md`, the
  `ghi-author` description, `ghi-close` and `chore-class-system.md`. It is the order level in
  `rnd-discipline.md:432` and § 1 (F C1, C25; G 4) (T15).
- **"Freeze"** is fenced out of R&D (*"do not import it"*), yet it is a package and order state
  (F C2) (T31).
- **Run** has six senses, and the acceptance "run id" is a `WP-` or `ORD-` id. **Block** has
  three: the release, the token block and `gz wp block`. **Package** is also the hexagon's Python
  package (F C7, C9, C21) (T31).
- **The hexagonal specification holds both mappings** of what the work package succeeds, and
  neither is retracted: OBPI → work package (lines 906-914), and *"the work package is the old
  mADR, the work order is the old OBPI"* (line 2066) (F C5, C23).
- The **receipt-id grammar** has three forms, and the strict regex rejects ids the code itself
  mints (F C15).
- `enhancement`'s GitHub description, *"New feature or request"*, contradicts the correction
  doctrine (F C10).
- Labels defined nowhere in canon: `chore`, `session-handoff`, `emergency` and
  `recovery-prerequisite`.

### 5.7 The RP-n pages' sub-units (track C)

Thirty unit names are in use: tranche, act, stage, step, item, change order (CO-n), order, O-n,
task, task card, phase, ruling n, refusal n, open point, F-n, T0, R-n, H-n, dock trial, sweep,
flight, probe, inspection, and lean or heavy version, among others.

- **The 2026-11-02 strata.** That ruling made the repair order what a tranche was and the task
  what an act was, and *tranche* and *act* retired. Practice since:
  - RP-12 writes *"O2 task 3 act 1"*;
  - RP-14 and RP-15 still cut tranches;
  - the contract itself ruled *"RP-15 as tranche 6"* on 2026-11-12.

  That makes a fifth level beneath the task (C 16, G 7) (T13).
- **The passage log** files every row under "Act". It has no rows for RP-12's rulings 1 to 205
  or its O1 to O4 work, although § Records still requires one per act (C 20, 21) (T28).
- **The pages' file names** are `harbor-roN-*.md`. Two pages share `ro7` and two share `ro9`, and
  RP-0 has no page (C) (T30).

## 6. The naming lineage

Full table: [`sources/gather-G-naming-lineage.md`](drydock-taxonomy/sources/gather-G-naming-lineage.md),
73 rulings with the operator's verbatim words, what each supersedes and whether it says so.

The main line, in order:

| Date | Ruling | Lineage row |
|---|---|---|
| Aug–Oct | a GHI *is* the work order | 1 |
| 2026-10-05 | the artifact ladder: change proposal `ECP-`, engineering order `EO-`, **OBPI → work package**, task card, block | 8 |
| 2026-10-16 | work order retired, *"work package everywhere"*; the Release Package named | 21, 23 |
| 2026-10-17 | the engineering order rung retired; R1, *"the repair order mirrors the work package"* | 24, 25 |
| 2026-10-18 | `WP-<NN>-<slug>`; *"a retired code is never reused"* | 28 |
| 2026-10-25 | RO-5 ruling 1, *"A repair order is a work package"*; one `WP-` series for both kinds | 31, 32 |
| 2026-10-30 | the four records; work package = the OBPI's successor; three-letter families | 37 to 40 |
| 2026-11-02 | repair strata (tranche → repair order, act → task, both words retire); four levels on both sides, **work order returns**; return to service package | 46, 47, 50 |
| 2026-11-03 | `RP-n` replaces `RO-n`; card dropped; **work order = the OBPI's successor, work package = the mADR's**; epic and story; **the level table is canon**; return to service a separate act; Gate 5 at the order | 52, 53, 55 to 59 |
| 2026-11-05 | `ORD-<NN>-<slug>` for both kinds; the order alias | 61, 62 |
| 2026-11-20 | O1 to O9 are build orders, not ledger orders | 66 |

**Unresolved supersessions (G § 3 and gap-fill, 24 items).** Each is either *silent*, where two
rulings conflict and neither cites the other, or *unapplied*, where the later ruling was explicit
but the surfaces stating the earlier one were never amended. The *unapplied* ones are listed in
§ 7.1; the *silent* ones are decisions in § 8.

## 7. What the gathering found that needs no new ruling

### 7.1 Unapplied: a later ruling governs and the surface still states the earlier one

Canon already rules these. The surfaces are corrected to the ruling named, routed under **T10**,
and no choice is put.

| # | Stale statement | Where | Ruling that governs |
|---|---|---|---|
| U1 | "work order" retired | `safe-mode-doctrine.md:52`; `doctrine-merge.md:141-142` | 2026-11-02/03, work order returns (rows 47, 56) |
| U2 | "a repair order is a work package" / "each order is a repair package" | `safe-mode-doctrine.md:52, 67`; contract § Purpose 78-84, § Repair orders "Order" column, its own § Rulings of 2026-11-03 line 1023; `safe_mode_contract.md:10`; `harbor-ro5:21`; `harbor-ro15:8` | 2026-11-02 strata (row 46); level table (row 58) |
| U3 | `RO-n` in live text | every RP page body but RP-12's; `parser_wp.py:272` help | 2026-11-03, `RP-n` replaces `RO-n` (row 53) |
| U4 | work package = the OBPI's successor | `identifier-migration-program.md`; `ADR-pool.identifier-ladder-migration.md`; `doctrine-merge.md` Part 0 safe-mode term, Part III, statement line 2; `hexagonal-specification.md:906-914` | 2026-11-03 (row 56) |
| U5 | engineering order "ruled" | program; pool ADR (lines 9, 24, 83); `doctrine-merge.md:435, 632` | 2026-10-17, rung retired (row 24); RP-6 owns it |
| U6 | task card | program:18; pool ADR; RP-5 title; `safe_mode_contract.md:89`; `obpi-decomposition-matrix.md`; `models/catalog.py:218`; WP-01's `procedure` | 2026-11-03, *card* dropped (row 55) |
| U7 | Gate 5 *is* the return to service | `command-doctrine.md:68-69`; matrix A2 | 2026-11-03 Option A, a separate act (row 59) |
| U8 | "one exceptional period through harbor, drydock and sea trial" | `AGENTS.md` (through its corpus); `doctrine-merge.md:131-132` | corrected 2026-10-17 (`safe-mode-doctrine.md:103`) |
| U9 | sea trial = fresh install only | `doctrine-merge.md:136`; `safe_mode_contract.md:117` | the contract's two approved forms (*"Make the two an OR"*) |
| U10 | retired terms in live use: punch list, register, fix cycle, restoration contractor, `restorer` | `mx/awareness.py:39`; `mx-mode.md:144`; gz-mx skill:90, 231; kit rulings 57, 72, 132; `events.py:1793`; WP-01 store; `ledger_producer_probe.py` | B′, B11, C5, ruling 21 |
| U11 | the MX log *is* the maintenance record | `mx/log.py:1` | kit ruling 166 (the log is the view) |
| U12 | Gate 5 heavy and foundation only | `obpi-runtime-contract.md`; `obpi-transaction-contract.md`; `gate5-architecture.md:10` | ADR-0.0.36 |
| U13 | Part I "copied byte for byte" | `doctrine-merge.md:11-12, 478` | the constitution's 2026-10-10 amendments |
| U14 | the classic ADR id `ADR-<n>` | `requirements-model.md:34`; program:19 | RP-6 H5, owned by CO-2 |
| U15 | Gate 5 at the package's close (2026-10-29) | the settled-ruling corpus, unmarked under *"do NOT re-open"* | 2026-11-03, Gate 5 at the order (row 52) |

### 7.2 Ruled and not yet built (owed work, already planned)

- The three-letter recode, in the store, the pattern and the shipped seed (T8).
- `RP-n` resolution (#1302).
- The return to service package (#1303).
- One depth for hangar and drydock (#1304).
- The capability store.
- The outcome's `withdrawn`, `modules` and `source`.
- Order alias resolution (ruling 49).
- The task's binding to its order (ruling 46).
- The crosswalk and the term witness (rulings 20 and 21, O8).
- The operator's verbatim words in place of a typed approver (ruling 32, witness row 14, O5).

### 7.3 Defects found in flight, not taxonomy

Each needs a GHI through `ghi-author`. None is filed yet.

| # | Defect | Evidence |
|---|---|---|
| X1 | `next_id` mints a work-package number from the store alone, so a number the ledger holds can be reissued | `work_package_store.py:31` against `order_store.py:43-44` (E C3) |
| X2 | `gz chores propose-ghi` calls `gh issue create` directly, skipping `ghi-author`'s prior-art lookup | `chores_propose_ghi_cmd.py:91-109` (F C14) |
| X3 | the audit report looks for `closeout/CLOSEOUT.md` (0 files), not `ADR-CLOSEOUT-FORM.md` (79 files) | `audit_cmd.py:124` (F C17) |
| X4 | an ADR attested by audit receipt may derive Pending or Accepted, not Completed: free text overwrites `attestation_status` and the derivation matches three tokens (read, not run) | `ledger.py:1244-1250` (D C43) |
| X5 | the closeout-ceremony skill names a state file, a folder layout and a runbook path that do not exist | the skill:105, 415; `references/folder-structure.md` (F C18 to C20) |
| X6 | `gz wp attach` runs `gh issue edit`, which is not on the allowed list | `work_package_github.py:82` (F C11) |
| X7 | the SingleDriver arm of ruling 175 is unreachable | `work_package_run.py:514-515` (B 4) |
| X8 | `derive_obpi_semantics` never reads `superseded`, `parked` or `blocked_on_operator` | `obpi_lifecycle.py` (D C42) |
| X9 | the charter links `config/governance_manifest.json`, which does not exist | `charter.md:119` |
| X10 | RP-6's status, *"Nothing of RO-6 has landed"*, is stale against 190 `TASK-ro6-` commits | `harbor-ro6-canon-retirement.md` (C 13) |
| X11 | requirements-model decision 1 (REQ grain) is missing; the numbering starts at 2 | `requirements-model.md` (D) |
| X12 | the strict receipt regex rejects `arb-meta-receipt-bind-…` and `arb-red-…` ids the code mints | `step_reporter.py:21-25` (F C15) |

## 8. Decisions for the operator

T1 to T11 are the first draft's, sharpened by the gathering; T12 to T35 are what the exhaustive
pass adds. Each is put one at a time, with its options and a recommendation, and recorded in § 9.

| # | Decision | Today |
|---|---|---|
| T1 | Keep § 1's four levels and names as canon, and amend the constitution's *Order* (*"a tasking order binds one work package"*) to them | canon since 2026-11-03; the constitution defines Order otherwise |
| T2 | Package identifiers: one `WP-` series for both kinds, or the kind spelled in the id (`RP-` repair, `WP-` work); and what becomes of the legacy `WP-1` to `WP-16` | one `WP-` series (RO-5 ruling 6); the operator, 2026-11-22: *"I am happy for RP/RO and WP/WO"* |
| T3 | Order identifiers: one `ORD-` series, or the kind spelled (`RO-` repair, `WO-` work); whether *"a retired code is never reused"* binds work identifiers; and what becomes of the old `RO-n` and `WO-n` | one `ORD-` series (ruling 43); `RO-n` is RP-n's alias; `WO-n` retired |
| T4 | The contract's `RP-0` to `RP-15`: records in the store, or short names resolving to records | prose; #1302 open |
| T5 | Which repair orders are ledger records: RP-12's O1 to O9, the tranches of the other packages, and when O1 to O4's prose Gate 5s reach the ledger | prose until O9's carry (rulings 10, 165); the R&D ruled the order *"a real record"* |
| T6 | The return to service package: its identifier, its record, the operator's act, and whether the drydock contract is that package | none; the doctrine calls the contract it, the contract does not |
| T7 | The feature package's identifier | unnamed |
| T8 | Family and outcome codes: apply the three-letter recode of 2026-10-30, with the depth rule, to the store, the pattern and the shipped seed | single letters in code, store and seed |
| T9 | One identity seam: every identifier in §§ 2 to 4 resolves through it, with its witness | four kinds; three grammar homes |
| T10 | The route for § 7.1's fifteen corrections: one contract amendment, change orders per package, or GHIs | unrouted |
| T11 | **Ruled W14: the requirements model.** Where the ruled taxonomy lives as the one home, and what witnesses it | nowhere |
| T12 | Gate 5's home: the order alone, or also the package close and the outcome; and the charter's closeout terms against the order's decisions | four homes in text and code |
| T13 | Below the task: apply the retirement of *act* and *tranche*, or rule a named sub-unit | retired 2026-11-02 and still in use |
| T14 | The 2026-10-05 ladder: retire the whole of it (EO, ECP, task card, block) and amend the program and the pool ADR; and whether the pool is ADRs or intentions | parts retired one by one; the pool ADR unamended |
| T15 | "Work order" meaning a GHI: retire that sense, and name what a GHI is in the taxonomy | both senses live |
| T16 | Squawk: one meaning (a GHI; a hangar visit on a reason; answered on the line) | three rulings |
| T17 | Hangar and drydock: one depth as ruled 2026-11-02, or the two levels the marker field and the code keep; and the standby level | ruled one; built two |
| T18 | Letters A to E (maintenance visits) against A to D (check levels) | both live |
| T19 | The amendment (`AMD-`, ruled 2026-09-27) against the change ladder and the superseding REQ | never reconciled; ADR-0.40.0 carries `AMD-` |
| T20 | The change ladder: four rungs or six; the supplement's record; whether a change order may change a contract row; the numbering of `CO-n` | canon four, code six |
| T21 | Control roles: the senses of tripwire and alarm (and dispatcher), which MEL entries are keyed on | the census's reading, unruled |
| T22 | Positions, personas and dispatch roles: the mapping of each persona file to a position, the reviewer's name, the craftsman against `Implementer` | unmapped |
| T23 | The construction side's one name (construction, catalog, delivery), and whether the maintenance visit is a third kind of package | three names; the store holds two kinds |
| T24 | Lane's home: the ADR, the outcome's `user_facing`, or the package | three homes |
| T25 | Who opens and closes the hangar (rulings 447 and 448 against the skill and the doctrine), and the floor's one list | contradicted |
| T26 | The handback: before or after the exit, and the subagent's "handback" renamed | contradicted |
| T27 | *"The briefing gates nothing"* (the constitution) against kit ruling 19's turnover gate | contradicted |
| T28 | The passage log: rows per act after *act* retired, and RP-12's missing rows | stale since 2026-11-04 |
| T29 | The task trailer for order work, and the task's ledger binding to its order | four trailer spellings; TASK events lack `order` |
| T30 | The specification pages' file names (`harbor-roN`), RP-0's page, and how sub-ids are namespaced | unruled |
| T31 | The overloaded words: order, level, run, block, package, repair, freeze, proceed, pause, hold, departure, terminate, advisory, clearance, gate, sortie, checkpoint, dispatch | each with two to six senses (A, B, F collisions) |
| T32 | The settled-ruling corpus: mark a superseded ruling under its *"do NOT re-open"* banner | three unmarked instances found (B 14) |
| T33 | The ADR and pool identifiers: `ADR-[0-9]{4,}-<slug>`, `ADR-pool.<slug>` against `ADR-0.2.0-pool.<slug>` | ruled in RP-6, not applied |
| T34 | The legacy vocabularies (ADR and OBPI states, undo verbs, REQ kinds and their checks): reconcile them now, or freeze them as legacy with their contradictions owned by RP-6 and RP-14 | 40 contradictions in D |
| T35 | `REQ-C<n>` (executive decision 1, 2026-10-16) against `REQ-<n>`, and the *"no separate document"* rulings against the feature package (G 23, 24) | silent |
| T36 | The Release Package's identifier, and the `RP` collision: *repair package* and *Release Package* both abbreviate to RP. The contract's own diagram already labels the Release Package node `RP` (`harbor-pilotage-candidate-2026-10-15.md:116`). The operator, 2026-11-22: releases are *"where we DO use semver so it would likely NOT be RP but rather use something like gzkit (or GZ-) maj.min.patch-slug"* | the version is the identity (requirements model); the template mints `RELEASE-{{version}}` |
| T38 | **Ruled W10.** One repair discipline in every condition: drydock, safe mode and line GHI work all run as repair package → repair order → FIX + task (operator, 2026-11-22: *"this discipline works for dry dock, safe mode and "normal" GHI work I would imagine"*). What differs by condition: the epic (a return to service package only when the marker is open), whether one GHI is a package of one order, and Gate 5 on a line order | line GHI work leaves one `fix(…): (GHI #N)` commit and no record |
| T39 | Gate 5 on a line repair order, against `AGENTS.md` § Attestation's *"a GHI needs no completion attestation"* | line GHIs close on a reviewer subagent |
| T40 | **Done W13**, in the requirements model § The store. The catalog store documented in one place: every file under `data/catalog/`, its kind, its writer verb and its schema (W12) | spread over `harbor-ro3`, `harbor-ro5`, the kit and the model docstrings |
| T37 | Numbered rulings on each package's specification page (RP-12 holds 205, RP-11 holds 11), cited as *"RP-11 ruling 4"*: a fourth id family, scoped by page, never in the store or the identity seam | prose only |

## 9. Rulings

Each ruling is recorded here with its question, the options put and the operator's verbatim
words, as it is made. Rulings made during the walk-through are numbered W1 onward. T1 to T35 are
put after it.

- **W1 (2026-11-22, step 1).** The question: what happens to the three surfaces that disagree on
  the release (the template, `adr-lifecycle.md`'s release-tag rule, *block*)? Two options were
  put: leave them with their owners, RP-4 ruling 7, RP-4 tranche 4 and RP-6 item 2 (recommended),
  or fix them ahead of RP-4's sequence. Operator: *"agreed, leave them with their owners"*.
- **W2 (2026-11-22, step 2b).** The operator confirmed the catalog and ADR identifiers, and called
  for two reviews. Verbatim: *"family, those single letters are superseded. capability, yes.
  outcome, yes. REQ - yes. but how does a REQ relate to its place in the catalog? there seems to
  be drift here. We need review. ADR - yes."* On the identity seam: *"this is insane and all over
  the place (looks like terrible drift to me)"*. The REQ review is § 2.1. The seam is T9, carried
  with the operator's reading of it as drift.
- **W3 (2026-11-22, disentangling link 2).** The question: where does a catalog record's parent
  link live, given decision 2's *"Codes are never derived into parentage: the catalog holds the
  relationships, and a code's spelling proves nothing"* and the family lookup's `o.code[0]`
  (`trust_audits/catalog.py:121`)? Three options were put:
  - A: a field on each record. The capability carries `family`, the outcome carries
    `capability`, and a validator holds each parent to a record and the code to its parent.
    Recommended.
  - B: the code is the link, which reverses decision 2.
  - C: membership lists on the parent.

  Operator: *"A, a field on each record"*. RP-11's tranches 1 and 2 (the re-code and the
  capability records) are where it lands. Neither names the field today, so this is a change to
  RP-11's scope, routed with T10.
- **W4 (2026-11-22, direction).** On being shown that a package's specification page divides its
  work by numbered rulings, tranches and acts, the operator said, verbatim: *"those rulings are
  not good. We should have Repair Package, that contains Repair Orders. Repair Orders can then
  have tasks (and perhaps repair REQs?). Let's get that clear first"*.
- **W5 (2026-11-22, direction).** Shown how the drydock's work came to live in page prose, the
  operator said, verbatim: *"we are in safe mode, we need to (other than spent ledgers), "nuke
  the planet from orbit, it's the only way to be sure"-level repair here. This vibe coding is very,
  very poisonous and destructive. Agents kept vibe coding this because we allowed it and an
  agent's "copy cat" tendencies are very, very strong and certain."* and *"Let's get this
  repair-side hierarchy down first before we worry about an 8-step rectification plan."* The repair
  is total: everything except the spent ledger. The repair-side hierarchy is settled first.
- **W6 (2026-11-22, the repair hierarchy).** The hierarchy as the operator stated it: a repair
  package contains repair orders, and a repair order contains its tasks. The question put was
  where the repair requirement lives:
  - A: in its repair order. Recommended.
  - B: on the package, as built under RP-12 ruling 45.
  - C: both.

  Shown that A mirrors the construction side's work while a catalog REQ lives in the catalog,
  the operator named a new concept. Verbatim: *"okay, then we need a new concept, how about
  FIX?"*, and, confirming the agent's reading (*FIX as the repair requirement, its own `FIX-<n>`
  series, living in the repair order, sharing the base requirement's shape and proof path*):
  *"yes, that's the concept ==> fix is the repair requirement, otherwise, we have a bad name and
  semantic collision."* This reverses RP-12 ruling 45's one shared `REQ-<n>` sequence.
  `REQ` names a catalog requirement only.
- **W7 (2026-11-22, FIX question 1).** The question: does a FIX belong to exactly one repair order,
  and what becomes of it under each Gate 5 outcome? Three options were put:
  - A: one order at a time. On proceed it holds. On redirect it moves to the superseding order by
    a ledger event and is re-frozen there. On pause it stays. On terminate it is withdrawn with
    the order, the GHI stays open, and a new attempt writes a new FIX that may `supersedes` it.
    Recommended.
  - B: terminate returns it to the package unbound, as ruling 30 reads today.
  - C: bound by several orders over its life.

  Operator: *"A, one order at a time"*. This amends RP-12 ruling 30's terminate clause (*"its REQ
  returns to the package unbound"*). *Amended by W8*: on a redirect no FIX moves.
- **W8 (2026-11-22, FIX identity).** The operator, verbatim: *"a fix is unique to the RP/RO it
  lives within (we may find ourselves fixing something again in the future)."* So a FIX lives in
  one package and one order for its whole life and is never reused, and a later repair of the
  same thing is a new FIX carrying a `repeats` link to the earlier one, distinct from
  `supersedes`. The question put, on the tension with W7's redirect clause:
  - A: a redirect writes new FIXes in the superseding order, each `supersedes` its counterpart,
    and the redirected order's FIXes close with it as superseded. Recommended.
  - B: keep W7's move, unique to the package only.

  Operator: *"A, a redirect writes new FIXes (the referene chains will help with traceability and
  analyses)"*.
- **W9 (2026-11-22, FIX question 2).** The question: how do GHIs and FIXes relate? Three options
  were put:
  - A: one GHI yields many FIXes; each FIX answers exactly one GHI, which its package carries;
    a recurrence is a new GHI and a new FIX with `repeats`. Recommended.
  - B: a FIX may answer several GHIs.
  - C: one GHI, one FIX.

  Operator: *"A"*.
- **W10 (2026-11-22, T38 and the check levels).** The question: does canon stand as one repair
  discipline at every level (repair package → repair order → FIX + task), with A and B on the line,
  C and D out of service, and the alarm test deciding (`safe-mode-doctrine.md`, the four check
  levels, ruled 2026-11-03)? Or do C and D also run on the line? Operator, verbatim: *"yes, and I
  wanted that to be solidly confirmed as we now have an organizational discipline for repair work
  that gzkit has never had. All GHI work for repair was woefully ad hoc and sometimes that is not
  useful. This is an emerging discipline that is much better."* T38 is ruled. Line GHI work joins
  the discipline. T39, Gate 5 on a line order, stays open.
- **W11 (2026-11-22, FIX question 2b).** The question: when does a GHI close? Three options were
  put:
  - A: when every FIX answering it holds. The close comment cites each FIX and how its order
    closed, the order's close standing as the review. Recommended.
  - B: the FIXes mark it resolved and a separate `ghi-close` reviewer pass closes it.
  - C: at its package's close.

  Operator: *"A"*. This amends `ghi-close`'s review-closes step (decision B12) for a GHI worked
  through the repair discipline: the order's close is the review on record.
- **W12 (2026-11-22, the store).** The operator asked: *"are we really using all of these .json
  files to hold the entire structure? not critiquing, but this seems new to me."* Shown:
  - the three layers: records under `data/catalog/`, state only in the ledger, views composed;
  - RP-3 ruling 1, *"One file per kind (Rec.)"*, 2026-10-21;
  - that JSON as the format was never put as its own question.

  Operator: *"it stands for now, finish FIX question 3 - (that design is fine, I hope it is
  well-documented)"*. Measured 2026-11-22, it is not documented in one place. `harbor-ro3` §
  The store describes four files, `harbor-ro5` the work packages, the kit the orders, and the
  model docstrings the rest. No page describes the whole store (T40).
- **W13 (2026-11-22, FIX question 3).** The question: where are FIXes stored? Three options were
  put:
  - A: their own file, `data/catalog/fixes.json`, each FIX naming its `order`, with no `package`
    field. Recommended.
  - B: nested in each order's record.
  - C: their own file naming both `order` and `package`.

  Operator: *"A, and for God's sake, please tighten up that documentation, NOW. Where is the
  canonical and collated location for the documentation for these things? I am increasingly
  finding that they are strewn all about."* The store is collated the same day in
  `docs/governance/ieee/requirements-model.md` § The store, and `harbor-ro3` points there. T40 is
  done.
- **W14 (2026-11-22, T11).** The question: where does the ruled work, repair and catalog taxonomy
  live as its one home? Three options were put:
  - A: the requirements model, each ruled part folding into it, the RP-n pages becoming dated
    records that point there, and a validator refusing a units-of-work term or id grammar
    defined elsewhere. Recommended.
  - B: a new canon page for work and repair.
  - C: this page as canon.

  Operator: *"A, the requirements model is the one home. however, also, we need a GIANT step back
  here... how disorganized is our big picture documentation of gzkit? I suspect it is a shambles
  right now."* T11 is ruled. Its witness is owed.
- **W15 (2026-11-22, direction).** Shown the documentation tree measured: 2,030 pages, 124 flat
  governance pages, no governance index, a `docs/README.md` map naming two of fifteen directories,
  38 of 238 governance pages in the site's navigation, and 183 pages claiming sole or canonical
  authority. Operator, verbatim: *"finish the taxonomy walk first, then open the R&D (this is most
  CERTAINLY dry dock fodder too, the vibe code kudzu is excessive and accelerating)."* So a
  documentation R&D run (`gz-rnd`) opens when this walk ends, and its outcome is drydock work.
- **W16 (2026-11-22, FIX question 4).** The question: the FIX identifier. Three options were put:
  - A: `FIX-<n>`, one sequence, never reused, minted from the store and the ledger. Recommended.
  - B: numbered within its order.
  - C: `FIX-<n>-<slug>`.

  Operator: *"A, FIX-<n> (however, what is the harm in anything having a slug? slugs are much
  friendlier to quick human examination, plus, for context and conversation, I can always refer
  to a briefer expression - REQ-99, FIX-1003. discuss)"*.
- **W17 (2026-11-22, one rule for every record id).** The harms were weighed: a stale slug,
  renames, long references, parse ambiguity. The question put: one rule for every record id, REQ
  and FIX included?
  - `PREFIX-<n>-<slug>`.
  - The slug is frozen at minting and starts with a letter.
  - The number is the key.
  - The short form `PREFIX-<n>` always resolves.

  Operator: *"yes, one rule for every record id"*. This amends `REQ-<n>` (area-free, no slug) and
  W16 to carry a frozen slug. The prefixes themselves stay T2, T3 and T36. Short-form resolution
  is the identity seam's (T9).
- **W18 (2026-11-22, FIX question 5).** The question: how is a FIX proved? Three options were
  put:
  - A: one path for REQ and FIX. `@covers` and the resolver accept both, the proof event (0 rows
    today) is renamed to name either, such as `proof_recorded` with an `obligation` field, and a
    FIX carries the same three kinds and rules. Recommended.
  - B: keep `req_proof_recorded` for both.
  - C: a separate FIX path.

  Operator: *"A, one proof path for both"*.
- **W19 (2026-11-22, FIX question 6).** C5 (2026-10-27) retired *fix cycle* for *rework* and
  *buy-back*, and about 25 live uses remain in `src/gzkit`. The renaming put, applying C5:
  - fix cycle → rework;
  - the fix-cycle bound → the rework bound;
  - the fix-cycle exit → the rework exit;
  - the `fix_cycles` field → `reworks`.

  Old ledger rows are read under their old field name, because the spent ledger is never
  touched (W5). Operator: *"yes, confirm the renaming as listed"*. *Fix* now names the FIX
  record and the ordinary-English `fix(…):` commit type only.
- **W20 (2026-11-22, disentangling link 5).** The question: a work package and its outcomes,
  given § 12's *"drawing REQs from any outcomes"* against the code's single `outcome` field. Three
  options were put:
  - A: no field, the outcomes derived from the REQs its orders bind.
  - B: a declared `outcomes` list set at initiation. An order binding a REQ outside it is refused,
    and widening it is a change order. Recommended.
  - C: keep one outcome.

  Operator: *"B, a declared outcomes list at initiation"*. The operator then asked: *"so does the
  catalog hold outcomes or requirements? I am confused"*.
  Shown: the catalog holds both, as two levels of one tree. Outcomes are what is delivered and
  what feature packages, work packages and Release Packages plan with. REQs are what must be
  true, what work orders bind and `@covers` proves. They meet at the derived `validated`.
  Operator: *"yes, that clears it up; go to link 6"*.
- **W21 (2026-11-22, disentangling link 6).** The question: does a work order's record list the
  REQs it binds? The R&D ruled the order *"a real record with … its REQ bindings"* (2026-11-02,
  *"a"*), and RP-12 ruling 46 ruled it thin, with *"no REQ list"* (2026-11-05, *"b"*). Three
  options were put:
  - A: the record lists the REQ ids it binds, editable while `opened` and fixed at freeze. The
    `frozen` event books each REQ at its revision, and a catalog REQ is bound by at most one open
    order at a time. Recommended.
  - B: keep ruling 46.
  - C: the record's list alone, with no baseline in the event.

  Operator: *"A"*. This reverses ruling 46's *"no REQ list"* and mirrors W13's FIXes.

## 10. The gathering, closed

Every domain the first draft listed as owed was gathered from its sources, each read whole, and
every term was checked against the booked rulings. The per-track **Files read in full** lists
give the line counts. What a track read only in part is named there, and no absence claim rests
on it; every part-read was closed by another track's whole read.

| Domain | Track | Source record |
|---|---|---|
| Drydock vocabulary; the change ladder and the change order (rulings 32, 76) | A | [`gather-A-drydock-vocab.md`](drydock-taxonomy/sources/gather-A-drydock-vocab.md) |
| Control roles; personas and positions; the crosswalk and rejected synonyms; the constitution | B | [`gather-B-roles-personas.md`](drydock-taxonomy/sources/gather-B-roles-personas.md) |
| Each RP-n page's sub-units; the passage log; the classic-ADR change order; the repair strata | C | [`gather-C-rp-subunits.md`](drydock-taxonomy/sources/gather-C-rp-subunits.md) |
| Requirement kinds and REQ specializations; gates, lanes, ADR kinds, OBPI states; undo verbs | D | [`gather-D-reqs-gates-states.md`](drydock-taxonomy/sources/gather-D-reqs-gates-states.md) |
| Ledger events; alias stores and grammars; the identifier census | E | [`gather-E-events-aliases-census.md`](drydock-taxonomy/sources/gather-E-events-aliases-census.md) |
| R&D kinds and dispositions; insight types; GHI labels and states; chores; receipt and run ids; handoff and ceremony files; the hexagon map | F | [`gather-F-rnd-ghi-chores-hex.md`](drydock-taxonomy/sources/gather-F-rnd-ghi-chores-hex.md) |
| The naming lineage across every R&D record, the contract's rulings and the settled-ruling store | G | [`gather-G-naming-lineage.md`](drydock-taxonomy/sources/gather-G-naming-lineage.md) |
| The gate definitions; the hangar's door | this page | `docs/governance/GovZero/charter.md` and `src/gzkit/commands/mx_cmd.py`, each read whole |
