# Work and Repair Taxonomy (DRAFT)

> **Status: DRAFT for the operator's rulings, 2026-11-22. High consequence.** Not canon. It
> gathers, in one place, every level, record, identifier, short name and closed set that gzkit's
> work and repair structure uses today, with where each is defined and where the places disagree.
> Each open point is numbered **T1 to T11** for a ruling. Where this page and a ruled source
> disagree, the source governs until a ruling here says otherwise.
>
> Why it exists: opening RP-12's repair order 5 showed that the drydock's own packages and
> orders have no record in the system the drydock built (operator, 2026-11-22: *"if this isn't
> documented in one place, we are in trouble already"*; *"this is a HIGH CONSEQUENCE document and
> decision set, this is meant to bring sanity out of the dry dock - high priority"*). Measured the
> same day by reading the code, the stores and the canon pages cited below. Insight scope
> `drydock-formalism`.

## 1. The four levels

Canon: `docs/governance/ieee/requirements-model.md` § 12, the level table (operator: *"the table
needs to kept and associated as canon - it captures the design very well"*).

| Level | Construction | Repair | Decides | Who |
|---|---|---|---|---|
| Epic | Feature package | Return to service package | why; value delivered, or seaworthiness | Operator |
| Story | Work package | Repair package | the cohesive grouping of orders; scope and footprint; initiation | Operator |
| Order | Work order | Repair order | the REQ-to-task binding; the freeze; inspection and buy-back; **Gate 5** | Coordinator, inspector, operator |
| Action | Task | Task | one recorded action, its measure, its (V) mark | Craftsman |

## 2. Record identifiers

| Record | Identifier today | Grammar defined in | In the store, 2026-11-22 |
|---|---|---|---|
| PRD | `PRD-…` | identity seam (prefix) | live |
| Family | three-letter mnemonic, `SES` (ruled 2026-10-30) | requirements model § The records, § Family schemes | **single letters** `X H C M P D R G A L Q` in `data/catalog/families.json` (T8) |
| Capability | family + number, `SES1` | requirements model | none |
| Outcome | capability + dotted number, `SES1.4` | requirements model; `OUTCOME_CODE_PATTERN` in `src/gzkit/models/catalog.py` accepts **one letter** (`H1.4`) | 0 (T8) |
| Catalog REQ | `REQ-<n>`, area-free | identity seam `CATALOG_REQ_ID_BODY` | 0 |
| Legacy REQ | `REQ-<semver>-<NN>-<NN>` | identity seam | in OBPI briefs |
| Work package / repair package | `WP-<NN>-<slug>`, kind in the `kind` field | `WORK_PACKAGE_ID_PATTERN`, `models/catalog.py` (RO-5 ruling 6, 2026-10-25) | 1: `WP-01-astral-toolchain` (repair, alias `RO-9`, closed) (T2) |
| Work order / repair order | `ORD-<NN>-<slug>`, kind read from its package | `ORDER_ID_PATTERN`, `models/catalog.py` (RP-12 ruling 43, 2026-11-05) | **0** (T3, T5) |
| Return to service package | **none** | none: no record, no event, no verb | none (T6) |
| Feature package | *"to be named when its store lands"* | requirements model | none (T7) |
| Task | `TASK-<semver>-<NN>-<NN>-<NN>`, or `TASK-<slug>[-#<ghi>]` | identity seam | commit trailers |
| ADR | `ADR-x.y.z-<slug>`, `ADR-pool.<slug>` | identity seam | live |
| OBPI (legacy order) | `OBPI-x.y.z-NN-<slug>` | identity seam | live |
| Release Package | the version | requirements model | live |

The identity seam (`src/gzkit/core/models.py`, `IdKind`) knows four kinds: **ADR, OBPI, REQ,
TASK**. No work, repair or drydock identifier resolves through it (T9).

## 3. Drydock records

| Record | Identifier | Defined in |
|---|---|---|
| Tag (tag-out log) | `TAG-<NN>-<slug>` | `src/gzkit/events.py` `TAG_ID_PATTERN`; RP-12 ruling 111 |
| Maintenance-record entry | `ENT-<NN>-<slug>` | `ENTRY_ID_PATTERN`; ruling 169 |
| Discrepancy | `DSC-<NN>-<slug>` | `DISCREPANCY_ID_PATTERN`; ruling 169 |
| Dispatch | `D-<16 hex>` | `DISPATCH_ID_PATTERN`; RP-12 O1 |

## 4. Short names and aliases

| Name | Means | Held where | Problem |
|---|---|---|---|
| `RP-0` to `RP-15` | the drydock's repair packages | the contract's § Repair orders table; specification pages | not in the store; `gz wp show RP-14` fails (#1302) (T4) |
| `RO-n` | the old name of those packages, an alias since 2026-11-03 | prose; `aliases` on WP-01 only | never resolved (#1302); collides with any `RO-` for repair orders (T3) |
| `O1` to `O9` | RP-12's repair orders | the kit page | *"build orders, not ledger orders"* (ruling 165); their Gate 5s are dated prose (T5) |
| `WO-1` to `WO-11` | work packages, before 2026-10-16 | dated rows | retired 2026-10-16 (operator: *"retire it, work package everywhere"*); requirements model § 2: *"a retired code is never reused"* (T3) |
| an order alias | any word, such as `O2` | `ORDER_ALIAS_PATTERN` (ruling 43) | in the grammar; no order exists |

## 5. Closed sets the drydock built (`src/gzkit/events.py` unless named)

- Package states: `initiated → frozen → commenced → accepted → closed`; a repair package uses
  `initiated → closed` (ruling 44).
- Order states: `opened → frozen → commenced → accepted → closed`.
- Gate 5 decisions: `proceed, redirect, pause, terminate`. Exits: `reopen, departure, hold,
  terminate`.
- Change ladder: `pen_and_ink, change_order, attachment, supplement, alteration, departure`.
- Dispatch roles: `Implementer, SingleDriver, Repair, Restoration` (`work_package_run.py`).
- Tag: class `Danger | Caution`; position hung `off | advisory | recording`, found adds `on`;
  source `order-work | standard-disconnect | mel-bypass | surveillant-stop`; surface kind
  `validator | check | hook | path`; check level `C | D`.
- Discrepancy: grade `blocks-return-to-service | due-by-event`; source `left-broken |
  inspector-rejection | found-in-work`.
- The out-of-service condition: one state, level `hangar | drydock` (the marker's older `mode`
  `mx | safe` reads as its alias).

## 6. Where the text contradicts the level table

- `docs/governance/harbor-pilotage-candidate-2026-10-15.md` § Repair orders: the section and its
  table's column are named **"Order"**, and its rows are repair packages RP-0 to RP-15 (T10).
- `docs/governance/safe-mode-doctrine.md:67`: *"Each order is a repair package named `RP-n`"*
  (T10).
- `docs/governance/safe-mode-doctrine.md:52`: *"A repair order is the maintenance mirror of the
  work package"*, superseded in place on 2026-11-03 but still the paragraph's lead (T10).

## 7. Decisions for the operator

| # | Decision | Today |
|---|---|---|
| T1 | Keep § 1's four levels and their names as canon | canon since 2026-11-03 |
| T2 | Package identifiers: one `WP-` series for both kinds, or kind spelled in the id (`RP-` repair, `WP-` work) | one `WP-` series (RO-5 ruling 6) |
| T3 | Order identifiers: one `ORD-` series, or kind spelled (`RO-` repair, `WO-` work), and what becomes of the old `RO-n` and `WO-n` names | one `ORD-` series (ruling 43) |
| T4 | The contract's `RP-0` to `RP-15`: records in the store, or short names resolving to records | prose; #1302 open |
| T5 | RP-12's O1 to O9: ledger repair orders, and when O1 to O4's Gate 5s move from prose to the ledger | prose until O9's carry (rulings 10, 165) |
| T6 | The return to service package: its identifier, record and the operator's act | none |
| T7 | The feature package's identifier | unnamed |
| T8 | Family and outcome codes: apply the three-letter recode ruled 2026-10-30 to the store and the pattern | single letters in code and store |
| T9 | One identity seam: every identifier in § 2 to § 4 resolves through `IdKind` | four kinds |
| T10 | Correct the contract and the doctrine to the level table | contradicts it |
| T11 | Where the ruled taxonomy lives as the one home, and what witnesses it | nowhere |

## 8. Rulings

None yet. Each ruling is recorded here with its question, the options put and the operator's
verbatim words, as it is made.
