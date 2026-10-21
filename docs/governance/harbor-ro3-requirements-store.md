<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# RO-3 specification — the requirements store, empty

**2026-10-21. Status: specified; tranche 1 landed (`96e7ed62f`, `cd1afd70f`); tranches 2 to 4 open.** Operator: **g0**. Repair order RO-3 of the
[harbor pilotage drydock](harbor-pilotage-candidate-2026-10-15.md#repair-orders): the store that
[the requirements model](ieee/requirements-model.md) rules, landed as empty structure under
`data/catalog/`. It populates nothing beyond the ruled family legend, changes no identifier, and
migrates no legacy ADR, OBPI or REQ. The verbs that edit the catalog, freeze a baseline and move an
outcome are RO-5's. The session that specified it does not land it; a cheaper session does, one
tranche per act.

## Rulings

The model's decisions 2 to 11 stand as ruled on 2026-10-18 and are not restated here. The four
questions they left open were ruled on 2026-10-21, verbatim selections, booked as an insight (scope
`harbor-ro3`):

1. **Layout** — *"One file per kind (Rec.)"*: `data/catalog/families.json`, `outcomes.json` and
   `reqs.json`, each a list under a `_doc` header, one schema each.
2. **The legend** — *"Seed the legend (Rec.)"*: `families.json` carries the eleven families of
   decision 8.3; `outcomes.json` and `reqs.json` land empty. This narrows the row's "No entry authored"
   to outcomes and REQs: the legend was already ruled canon.
3. **Events** — *"Library producer + probe (Rec.)"*: the outcome-lifecycle and REQ-proof events land
   with their writer functions and no CLI verb, each proven by an isolated producer probe in
   `gzkit.ledger_producer_probe`, so the ledger-vocabulary inertness ratchet is never raised.
4. **The forward rule** — *"Advisory until RO-5 (Rec.)"*: a delivery event appended after RO-3 lands
   that names no REQ or outcome is an advisory, and becomes a failure when RO-5's verbs can supply an
   outcome id. Legacy events are never backfilled.

## The population, measured 2026-10-21

| Surface | Today |
|---|---|
| `data/catalog/` | absent |
| The registry read seam, `gzkit.registries` | resolves bare filenames under `data/` only, and refuses a path (GHI #1067), so `catalog/families.json` cannot be read through it today |
| Identifier kinds, `gzkit.core.models.IdKind` | ADR, OBPI, REQ, TASK; `REQ` is recognized by its leading token, and the RO-2 resolver derives a REQ's owner from its brief or, as a marked fallback, from the `REQ-<semver>-NN-MM` spelling |
| A new event type's registration | five surfaces, measured landing `mx_session_lease_renewed` (GHI #1261): the typed model and the union in `gzkit.events`, `src/gzkit/schemas/ledger.json`, the type map in `tests/test_schemas.py`, the corpus disposition list in `gzkit.ontology.corpus`, and a producer the inertness check can verify |
| The ledger | 19,381 events of 75 types; no event names an outcome; 1,340 of 19,241 named a REQ on 2026-10-18 |
| Delivery event types | the ones that record work done or proven: `task_started`, `task_completed`, `obpi_receipt_emitted`, `gate_checked`, `attested`, `acceptance_recorded`, `red_receipt_emitted`, `stage2_dispatch_recorded`, `closeout_initiated` (4,432 events, of which only `acceptance_recorded`, `red_receipt_emitted` and twelve `obpi_receipt_emitted` name a REQ) |
| The PRD | 31 FRs (FR-001 to FR-031, FR-004 retired, FR-005a and FR-005b split) and four § 7 attributes, the `derives_from` targets |
| BDD | 83 feature files; `gz validate --behave-req-tags` already binds a BEHAVIOR REQ to a tagged scenario or an `@covers` test (GHI #636) |

## The store

**`families.json`** — the legend, seeded with decision 8.3's table: `code` (one letter), `band`
(`product` or `common`), `name`, and `scope` (one sentence). Product: X, H, C, M, P, D. Common: R, G,
A, L, Q.

**`outcomes.json`** — empty. Each entry: `code` (family letter and dotted number, `H1.4`), `statement`,
`owner`, `user_facing` (decision 10's test), `governed_by` (ADR ids, resolved through the RO-2 seam),
`depends_on` (outcome codes, gates or named external boundaries), `feature` (the feature file carrying
the outcome's code as a tag, required when `user_facing`), and `retired` (a retired code stays, so it
is never reused). No lifecycle state: delivery status lives only in the ledger (decision 3).

**`reqs.json`** — empty. Each entry: `id` (`REQ-<n>`, sequential, area-free, never reused), `member_of`
(one outcome code), `statement` (effect and rationale), `criteria` (one or more of state or input →
required outcome → evidence, on the `ghi-close` closure-contract precedent), `kind` (BEHAVIOR,
SUPPORT, STRUCTURAL-FENCE), `revision` (an integer that only rises), `derives_from` (PRD FR ids or § 7
attributes), and `applies_to` (targets, for a Q-family NFR only). No proof: proof lives only in the
ledger (decision 4).

Each file has a JSON schema under `src/gzkit/schemas/` and a frozen Pydantic model, and each is
declared in `data/config_registry.json` with its reader as owner.

**The new REQ grammar.** `REQ-<n>` carries no dots, so it cannot be mistaken for the legacy
`REQ-<semver>-NN-MM`; the RO-2 resolver gains the catalog as the store of a new-grammar REQ's
`member_of`, and never derives its owner from the spelling.

## The events

| Event | Fields | Writer |
|---|---|---|
| `outcome_transitioned` | `outcome`, `from_state`, `to_state` (decision 4's lifecycle and its side states `blocked` and `deferred`), `evidence` (the ledger event id that justifies the move), `attestor` (required into `validated`, the Gate 5 act) | a library function refusing a transition the lifecycle does not allow |
| `req_proof_recorded` | `req`, `revision`, `commit`, `verdict` (`SATISFIED`, `UNSATISFIED`, `UNKNOWN`), `evidence` (receipt or test id), `target` (an `applies_to` member, for an NFR) | a library function refusing a verdict outside the three and a revision the catalog does not hold |

Each lands on all five registration surfaces with its isolated producer probe (ruling 3).

## The witness

One scope, `gz validate --catalog`, in the default `gz check`:

- **Structure:** each file against its schema; codes and ids unique; a family letter in the legend;
  an outcome's family existing; a code's band matching its family.
- **Edges:** `depends_on` resolving and acyclic; `governed_by` resolving through the RO-2 seam;
  `member_of` resolving; `derives_from` naming a live PRD FR or § 7 attribute.
- **Coverage report:** a PRD FR or § 7 attribute no REQ derives from is listed. With the catalog
  empty that is every one of them, so the report is advisory until the catalog is populated.
- **BDD alignment:** a user-facing outcome names a feature file carrying its code as a tag, and each
  BEHAVIOR REQ under it has a scenario tagged with its id there, alongside its `@covers` test.
- **Freeze lock:** a REQ in a frozen baseline is not edited except by a recorded reopening. The
  baseline event is RO-5's; see § Known uncertainties.
- **Forward rule:** a delivery event (the declared list, held in a registry, not in code) appended
  after the RO-3 landing commit that names no REQ or outcome is an advisory (ruling 4).

Every check carries a negative control, as every `gz validate` scope does.

## Tranches

Each tranche is one act under § Records of the contract: one commit with a `Task:` trailer
(`TASK-ro3-<slug>`), a failing test observed first, `gz arb red --commit` with its verdict and every
survivor driven, the full unit tier run before push (the per-change gate misses tests that scan a
registry or the tree, insight scope `gz-check-changed-tests`), and a passage-log row.

| # | Scope | Done when |
|---|---|---|
| 1 | The read seam admits the one declared subdirectory `catalog/`; the three files, schemas and models; the legend seeded; the config-registry entries; `gz validate --catalog` with the structure checks | the files validate, the scope runs in `gz check`, the legend's eleven families pass and a malformed entry fails |
| 2 | `outcome_transitioned` and `req_proof_recorded` on all five surfaces, their writer functions and producer probes | the inertness check reads both verified; a disallowed transition and a fourth verdict are refused |
| 3 | The edge checks, the coverage report, BDD alignment, and the new REQ grammar in the RO-2 resolver | each check's negative control catches its case; the resolver names a `REQ-<n>`'s outcome from `member_of` |
| 4 | The forward rule, its delivery-event registry and cutover | an undeclared delivery event after the cutover is announced; legacy events are not read |

RO-3 closes when the four tranches have landed: its row's witness reads "schemas validate; `gz test`
green; the validators registered".

**Boundaries.** RO-3 authors no outcome or REQ, edits no PRD text, adds no CLI verb, retires no
legacy identifier and regroups no feature file. A change that would alter an attested REQ's subject
is repaired at the surface and recorded.

**Known uncertainties.** Each is read by the tranche that owns it:

- The freeze lock needs a frozen-baseline event, which RO-5's work package declares. Tranche 3 either
  lands the check against that event's declared shape, vacuous until RO-5 fires it, or leaves the check
  to RO-5; that choice is the operator's when tranche 3 begins.
- Whether `depends_on` names gates and external boundaries by a code of their own or by a free string
  with a declared prefix.
- Whether the § 7 attributes need ids (`NFR-performance`) for `derives_from` to resolve them.
- Which delivery event types the forward rule lists; the table above is the measured candidate set.

## Before-figures

Read when RO-3 closes, as the 2026-10-18 baseline row asks: catalog files 0, families 0, outcomes 0,
REQs in the catalog 0; event types 75; delivery events naming a REQ or outcome after the cutover: none
yet measured.
