# Gather D: requirement kinds, REQ specializations, records; gates, lanes, kinds, states, undo verbs

Gathered 2026-11-22 for `docs/governance/drydock-taxonomy.md` § 9, items 7 and 8. This is read-only research: no repo file was edited and no `gz` write was run. Status key:

- **RULED**: an operator ruling or ADR decision exists, quoted.
- **SOURCED**: defined in canon or code, and no ruling was found after full reading.
- **CONTRADICTED**: two sources disagree. Both are quoted.
- **UNSOURCED**: the term is used but defined nowhere. What was read is said.

Each line cite is `path:line`, and paths are repo-relative to `the repository root`.

---

## Domain 7a: Requirement kinds and proof channels

| # | Term | Meaning as stated | Defined | Implemented | Status |
|---|---|---|---|---|---|
| 7.1 | REQ kind (the closed set) | "every REQ in an OBPI brief's Acceptance Criteria carries exactly one of three kinds — BEHAVIOR, SUPPORT, or STRUCTURAL-FENCE … Each kind has exactly one proof channel" | `docs/design/adr/foundation/ADR-0.0.59-…/ADR-0.0.59-….md:33`; `docs/governance/req-scope-discipline.md:44-51`; `.gzkit/rules/tests.md:101-109` | `src/gzkit/req_kind.py:32-37` `ReqKind(StrEnum)`; `src/gzkit/models/catalog.py:109` `kind: Literal["BEHAVIOR","SUPPORT","STRUCTURAL-FENCE"]` | **RULED**: ADR-0.0.59 Decision (attested by g0 on 2026-05-27). Boundary Invariant 1 reads: "The REQ taxonomy is closed-set: exactly three kinds" (ADR-0.0.59:208-211). |
| 7.2 | BEHAVIOR | "Code behavior — functions, commands, CLI outputs, state transitions, error paths, configuration parsing", proven by "A `@covers`-decorated test in `tests/**`" | `req-scope-discipline.md:99-106`; `tests.md:107`; ADR-0.0.59 BI 3 (:217-219), "witnessed exclusively through `@covers`-decorated tests" | `req_kind.py:49` → `TEST_COVERS`; brief-time check `src/gzkit/commands/validate_req_kind.py:73-82`, which only requires that the Allowed Paths contain `tests/` | **RULED** (ADR-0.0.59) |
| 7.3 | BEHAVIOR proof for a user-facing REQ | Canon: "Every BEHAVIOR REQ under a user-facing outcome needs a passing scenario tagged with its REQ id … **in addition to** its `@covers` unit test" | `docs/governance/ieee/requirements-model.md:178-180` | Legacy gate: "a BEHAVIOR REQ is satisfied by a tagged scenario **or** an `@covers` unit test" (`tests.md:89`, GHI #636) | **CONTRADICTED**: requirements-model:179 says AND; tests.md:89 says OR. The model's rule targets catalog outcomes and the tests.md rule targets legacy briefs, but neither source names that scope split. |
| 7.4 | SUPPORT | "Governance artifacts, doctrine docs, rule files, data files … that *support* behavior", proven by "The conjunction of two signals": a ledger event citing the artifact AND a structural validator scope | `req-scope-discipline.md:123-136`; `tests.md:108` | `req_kind.py:50` → `LEDGER_PLUS_VALIDATOR`; `src/gzkit/req_kind_support.py:353-413` | **RULED** (ADR-0.0.59 Decision) |
| 7.5 | Witness clause | "Witnessed by `<event_type>` [citing `<path>`] + `gz validate --<scope>`." "Exactly one clause per REQ" | `req-scope-discipline.md:142-156` | `req_kind_support.py:90-131` (`_witness_clause`, `_sole_event_type`) | **SOURCED**. It is called "binding, GHI #888", but the source is a GHI fix, not an operator ruling. |
| 7.6 | SUPPORT brief-time check | Doc: it fails when the REQ "text lacks **both** a `gz validate --` scope reference and a ledger event keyword" | `req-scope-discipline.md:305-306` | Code fails unless it finds `has_validator and has_ledger`, so it fails when **either** is missing (`validate_req_kind.py:97-100`) | **CONTRADICTED**: the doc's "lacks both" against the code's either-missing failure. |
| 7.7 | SUPPORT status at the parity gate | Doc: "SUPPORT REQs always receive `proof_status="advisory-support"`. Full ledger-event querying is deferred to a future OBPI." | `req-scope-discipline.md:400-405` | Code runs a real ledger query plus validator dispatch whenever it has a project root (`req_kind.py:238-240`, `req_kind_support.py:353-413`, ADR-0.0.69) | **CONTRADICTED**: the doc is stale against the code. |
| 7.8 | STRUCTURAL-FENCE | "Integration-state properties scoped to the parent ADR's boundary … cross-OBPI invariants", proven by "A parent-ADR `## Boundary Invariants` entry … naming this OBPI (`(OBPI-NN[, …])`)" | `req-scope-discipline.md:179-202`; `tests.md:109`; suite-level post-condition boundary case `req-scope-discipline.md:222-243` (GHI #547) | `req_kind.py:51` → `PARENT_ADR_INVARIANT`; `src/gzkit/req_kind_fence.py:200-238` | **RULED** (ADR-0.0.59 Decision, Path D adopted, ADR-0.0.59:185). The anchor-token form comes from GHI #538. |
| 7.9 | STRUCTURAL-FENCE at the OBPI layer | ADR-0.0.59 Decision item (3): "STRUCTURAL-FENCE REQs report 'grandfathered' (advisory only) at the OBPI layer"; req-scope-discipline:186-188 says the same | ADR-0.0.59:33; `req-scope-discipline.md:186-188, 356` | `req_kind.py:243`: "STRUCTURAL-FENCE + no `project_root` → `"unproven-fence"` (fail-close; never advisory)". `unproven-fence` is not counted in `grandfathered_reqs` (`req_kind.py:314-325`). | **CONTRADICTED**: the ADR's Decision text against the code. ADR-0.0.59 BI 2 (:212-216) calls the grandfathered path "a transitional placeholder" that ADR-0.0.69 replaced, so the ADR disagrees with itself. |
| 7.10 | STRUCTURAL-FENCE brief-time check | Doc: it fails "when the parent ADR file has no `## Boundary Invariants` heading" | `req-scope-discipline.md:307` | The code also requires the OBPI anchor (`validate_req_kind.py:138-151`), as the same doc says at :190-202 | **CONTRADICTED** within one doc (:307 against :190-202). |
| 7.11 | Kind for catalog and repair REQs | `ReqBase.kind`: "Which proof channel binds it (ADR-0.0.59)". Model § 10: "SUPPORT and STRUCTURAL-FENCE REQs keep their declared proof channels" | `models/catalog.py:109-111`; `requirements-model.md:180` | The fence resolver parses only the legacy grammar: a `REQ-<n>` hits `m is None` and returns `"unproven-fence"` (`req_kind_fence.py:224-226`). `--req-kind-discipline` scans OBPI briefs for `REQ_ID_BODY_PLAIN` only (`validate_req_kind.py:29-34, 258`). A catalog or repair REQ has no "parent ADR": `member_of` names an outcome, and `held_on` names a package. | **CONTRADICTED**: canon says catalog REQs keep the channels, but the PARENT_ADR_INVARIANT channel cannot resolve for a REQ that has no parent ADR, and no validator checks kind discipline for catalog REQs. |
| 7.12 | ProofChannel member names | `TEST_COVERS`, `LEDGER_PLUS_VALIDATOR`, `PARENT_ADR_INVARIANT` | `req-scope-discipline.md:344` | `req_kind.py:40-45` | **SOURCED**. ADR-0.0.59 names a `ProofChannel` model, not its members. |
| 7.13 | `proof_status` vocabulary | Doc: "`pass` / `fail` / `advisory-support` / `grandfathered` / `inferred-*`". Model field: "pass / fail / missing-citation" | `req-scope-discipline.md:345`; `req_kind.py:85` | The code emits `pass`, `fail`, `advisory-support`, `grandfathered-support`, `undeclared-support`, `unproven-support`, `unproven-recursion-fence`, `unproven-fence`, `inferred-behavior`, `inferred-support` and `inferred-structural-fence` (`req_kind.py:235-244`; `req_kind_support.py:365-377`; `req_kind_fence.py:211-216`) | **CONTRADICTED**: three different lists. |
| 7.14 | Kind tag syntax and case | "`REQ-X.Y.Z-NN-NN [kind]: claim` — author UPPERCASE, do not rewrite existing lowercase tags" | `tests.md:103`; `req-scope-discipline.md:53-82` | Case-insensitive regex `validate_req_kind.py:29-33` | **RULED**: operator ruling of 2026-08-11 ("Tag case carries no meaning; author UPPERCASE; existing lowercase tags are correct and are NOT to be rewritten"). |
| 7.15 | Untagged legacy REQ / inferred kind / grandfathering cache | One-shot inference; "Inferred REQs carry `proof_status` of `inferred-behavior` … always advisory"; the override cache is `data/req_kind_grandfathering.json` | `req-scope-discipline.md:363-369`; ADR-0.0.59 Decision item (3) | `req_kind.py:98-120` (`infer_req_kind`), `:149-183` | **RULED** (ADR-0.0.59 Decision item 3) |
| 7.16 | Mixed-state brief | "a brief whose `## Acceptance Criteria` section contains at least one REQ with a `[kind]` tag and at least one without". An all-untagged brief passes. | `req-scope-discipline.md:300-302` | `validate_req_kind.py:211-227, 248-251` | **SOURCED** |
| 7.17 | `--bypass-req-kind-discipline-once` | It "Skips the three-channel parity fail-close for the run and emits a `bypass_used` ledger event". It is on `gz covers` only. | `req-scope-discipline.md:371-398` | `src/gzkit/cli/parser_maintenance.py:372-393`; `src/gzkit/commands/covers.py:146-228` | **RULED**: ADR-0.0.59 Decision, "Emergency-bypass surface (operator-blessed addition)". The asymmetry comes from GHI #546. |
| 7.18 | A fourth kind | It "requires a follow-up **foundation** ADR amendment" | ADR-0.0.59:33, BI 1 (:208-211); `req-scope-discipline.md:288-291` | none | **CONTRADICTED**: the `foundation` kind has been CLOSED to new authoring since ADR-0.34.0 (`AGENTS.md:133`; ADR-0.34.0 Decision). The amendment path ADR-0.0.59 names cannot be authored. |

## Domain 7b: REQ specializations and their fields

| # | Term | Meaning as stated | Defined | Implemented | Status |
|---|---|---|---|---|---|
| 7.19 | Base requirement (`ReqBase`) | "A base requirement carries statement, criteria, kind, revision and proof … the base carries `supersedes`" | `requirements-model.md:279-283` | `models/catalog.py:97-117` | **RULED**: operator, *"sounds an opportunity for classic inheritance - they likely have some specialization"* (§ 12, 2026-11-03), declared by RP-12 rulings 45 and 48 (2026-11-05) |
| 7.20 | Catalog REQ (`CatalogReq`) | It "keeps `member_of` an outcome, `derives_from` and `applies_to`" | `requirements-model.md:281, 32` | `models/catalog.py:120-126` | **RULED** (§ 12; RP-12 ruling 45) |
| 7.21 | Repair REQ (`RepairReq`) | It "is held on its repair package, names its problem report, and may name a design REQ it aligns to" | `requirements-model.md:282-283, 32` | `models/catalog.py:129-139`. `held_on` uses the general `WORK_PACKAGE_ID_PATTERN` and does not check that the package's kind is `repair`. | **RULED** (§ 12; RP-12 rulings 45, 48) |
| 7.22 | `specialization` mark | "each marked `"specialization": "catalog"` or `"repair"`" | `requirements-model.md:283` | `models/catalog.py:123, 132, 143` (discriminated union `Req`) | **RULED** (RP-12 ruling 48) |
| 7.23 | The construction side's name | Level table: **Construction** / Repair (`requirements-model.md:253-258`). REQ mark: **catalog** / repair. Work package kind: **delivery** / repair (`models/catalog.py:204`). | as cited | as cited | **CONTRADICTED**: one side of the construction-and-repair split has three names (construction, catalog, delivery). |
| 7.24 | Legacy REQ | `REQ-<semver>-<NN>-<NN>`. "Legacy `ADR-`, `OBPI-`, `REQ-<semver>-NN-MM` and `TASK-` identifiers are frozen and resolve through the ledger's `artifact_renamed` alias layer" | `requirements-model.md:57-59` | `src/gzkit/core/models.py:62-66` (`REQ_ID_BODY`, `REQ_ID_BODY_PLAIN`); `ReqId` `:517-534`; the parent is derived from the spelling at `:260-263, 280-293` | **RULED** (§ 2) |
| 7.25 | Short REQ reference | "The item-criterion form (``REQ-NN-MM``) a commit message cites, relative to its ADR" | `core/models.py:67-68` | `REQ_SHORT_ID_BODY` | **SOURCED** (code only; no canon page names it) |
| 7.26 | Catalog REQ id | "`REQ-<n>`, sequential, area-free, never reused". "`REQ-<n>` carries no dots, so it cannot be mistaken for the legacy" form | `harbor-ro3-requirements-store.md:87, 100-102`; `requirements-model.md:32, 52-56` | `core/models.py:69-71, 187-211`; `models/catalog.py:43` | **RULED**: § 2 ("the 2026-10-17 ruling stands"). `IDENTITY_MODELS["REQ"]` is the legacy `ReqId` only (`core/models.py:581-587`), so `IdKind.REQ` covers both grammars while the REQ identity model admits one. |
| 7.27 | `statement` | "effect and rationale" | `harbor-ro3:88`; `requirements-model.md:225` | `catalog.py:107` | **RULED** (§ 11, maxim 8, 2026-10-18) |
| 7.28 | `criteria` / `Criterion` | "one or more pass/fail criteria (state or input → required outcome → evidence), on the `ghi-close` closure-contract precedent" | `requirements-model.md:225`; `harbor-ro3:88-90` | `catalog.py:87-94` (`state_or_input`, `required_outcome`, `evidence`), `:108` (`min_length=1`) | **RULED** (§ 11, maxim 8) |
| 7.29 | `revision` | "counts editorial amendments only … and a revision never resets proof; a change a test asserting the prior statement would fail against is a new REQ carrying `supersedes`" | `requirements-model.md:96, 297` | `catalog.py:112-114` (`ge=1`) | **RULED**: RP-12 ruling 31, operator *"A"*, 2026-11-04. Residue: `harbor-ro3:90` still says "an integer that only rises", and § 11's *Done drift* row (`requirements-model.md:226`) says a reopening "resets that REQ's proof". That row is about reopening, not revision, so it is listed here as a residue to confirm, not as a contradiction. |
| 7.30 | `supersedes` | "A remodel revises forward: the new REQ carries a `supersedes` link and the prior is never edited" | `requirements-model.md:294-297` | `catalog.py:115-117` | **RULED**: operator, *"we don't change a req with a model as much as we supersede it"*, 2026-11-03 |
| 7.31 | `member_of` | "membership is a field (`member_of`), so moving a REQ between outcomes keeps its id" | `requirements-model.md:53-56` | `catalog.py:124`, with the one-letter `OUTCOME_CODE_PATTERN` (that pattern is draft T8) | **RULED** (§ 2) |
| 7.32 | `derives_from` | "A REQ names the PRD FR or § 7 attributes it refines" | `requirements-model.md:230` | `catalog.py:125` | **RULED** (§ 11, concept 3) |
| 7.33 | `applies_to` | NFR targets: "Proof is recorded per target, and the NFR is SATISFIED only when every target is" | `requirements-model.md:148-151` | `catalog.py:126`; `events.py` `ReqProofRecordedEvent.target` | **RULED** (§ 8.1) |
| 7.34 | `held_on`, `problem_report`, `aligns_to` | "`held_on`, `problem_report` (the issue number) and `aligns_to`" | `requirements-model.md:283` | `catalog.py:133-139` (`problem_report: int ge=1`, "(ruling 9)") | **RULED** (RP-12 rulings 45, 48) |
| 7.35 | REQ proof verdict | "Each REQ carries proof only …: `SATISFIED`, `UNSATISFIED` or `UNKNOWN`. Missing evidence is `UNKNOWN`" | `requirements-model.md:90-92` | `src/gzkit/events.py:1748` `ReqVerdict`; `req_proof_recorded` `:1767-1783` | **RULED** (§ 4, amended "after the operator's direction to learn from Backplane") |
| 7.36 | Parallel proof vocabularies | catalog `SATISFIED/UNSATISFIED/UNKNOWN`; legacy `proof_status` (7.13); OBPI `proof_state` `missing/partial/recorded/validated`; `req_proof_inputs.status` `present/missing` | `obpi-runtime-contract.md:168-178, 225-228` | `ledger.py:169`; `ledger_semantics.py:625` | **SOURCED** individually. Four "proof" vocabularies exist with no crosswalk anywhere (see the collisions section). |
| 7.37 | Scope disposition (deferral, exclusion) | "a scope disposition with an approver and a revisit condition, never a satisfaction result" | `requirements-model.md:96-97` | partly: `Departure.req`, "The REQ it departs on, as its scope disposition" (`catalog.py:186-188`) | **RULED** (§ 4) |

## Domain 7c: Requirements-model records

| # | Term | Meaning as stated | Defined | Implemented | Status |
|---|---|---|---|---|---|
| 7.38 | PRD | "Functional (`FR-nnn`) and non-functional (§7) requirements: the parent obligation set" | `requirements-model.md:28` | `core/models.py:397-405` (`^PRD-[A-Z0-9]+-<semver>$`; status `Draft/Review/Approved/Superseded`); `core/lifecycle.py:70-75` | **SOURCED** |
| 7.39 | FR id, `NFR-<slug>` | `FR-nnn`. "an attribute is `NFR-<slug>` derived from its `###` heading under PRD § 7" | `requirements-model.md:28`; `harbor-ro3:43-44` | `gz validate --catalog` edges (not read here) | **RULED**: RO-3 ruling 7, *"Derive from heading (Rec.)"* |
| 7.40 | Family | "One responsibility area, with a one-sentence scope in the legend". Fields: `code`, `band`, `name`, `scope` | `requirements-model.md:29`; `harbor-ro3:76-78` | `catalog.py:55-65` (`code` `^[A-Z]$`); `data/catalog/families.json` (11 single letters) | **CONTRADICTED**: the three-letter recode ruled 2026-10-30 (`requirements-model.md:190-193`) against the code and the store (draft T8, already listed) |
| 7.41 | Band | "Product elements … Common elements, serving every product family" | `requirements-model.md:202-205` | `catalog.py:61` `Literal["product","common"]` | **RULED** (decision 8.3, 2026-10-18, *"so, perhaps MIL-STD-881 had the best compromise?"*) |
| 7.42 | Capability | "A named grouping of outcomes with a scope; never carries work (ruled 2026-10-29)" | `requirements-model.md:30` | **no model and no store**. It exists only as the digits inside `OUTCOME_CODE_PATTERN` (`catalog.py:40`). | **RULED** as a record, but not implemented: no field holds its scope. |
| 7.43 | Outcome | "One reviewable deliverable: statement, owner, `user_facing`, `governed_by`, `depends_on`, `modules` (the code paths it owns; ruled 2026-10-30)" | `requirements-model.md:31, 126-129` | `catalog.py:68-84`: **no `modules` field**, and `extra="forbid"` refuses one. `WorkPackage.modules` says "a delivery package reads its outcome's" (`catalog.py:213-216`), but no outcome field exists to read. | **CONTRADICTED**: the ruled field (`requirements-model.md:31, 128`, "*The contract is the outcome* (operator ruling 2026-10-30, *"A"*)") against the model. `harbor-ro3:81-85` also omits `modules`. |
| 7.44 | Outcome lifecycle | "`queued → designing → specified → planned → in_progress → implemented → reviewed → verified → validated → released`, with the side states `blocked` and `deferred`". "a withdrawal is the terminal state `withdrawn`" | `requirements-model.md:77-89` | `events.py:1732-1746` (no `withdrawn`); `catalog_ledger.py:1-75`: "Reopening and withdrawal are RO-5's and are refused here" | **CONTRADICTED**: `withdrawn` was ruled on 2026-10-31 (operator *"A"*), but the `OutcomeState` Literal lacks it. Return-to-origin is **RULED** (`harbor-ro3:33-37`). |
| 7.45 | Outcome `validated` | § 12: "**An outcome's `validated` is derived, not attested**" | `requirements-model.md:83-86, 267-271` | `events.py:1764`: `attestor`, "The Gate 5 attestor; required into validated". `harbor-ro3:108`: "`attestor` (required into `validated`, the Gate 5 act)" | **CONTRADICTED**: the ruled § 12 (operator *"c - …this is the decoupling we were working towards"*) against the event model and the RO-3 spec. |
| 7.46 | `user_facing` | "a CLI, API, schema or runtime contract used by humans or external systems" | `requirements-model.md:175-178` | `catalog.py:76` | **RULED** (decision 10) |
| 7.47 | `governed_by` | "An outcome links to zero or more governing ADRs" | `requirements-model.md:164-166` | `catalog.py:77` | **RULED**: operator, 2026-10-17, *"I don't think that every requirements or feature necessitates an architectural design or decision record"* |
| 7.48 | `depends_on` prefixes | "an outcome code, `gate:<n>` for a gate `.gzkit/manifest.json` declares, or `external:<slug>`" | `harbor-ro3:45-47` | `catalog.py:78-80`; `trust_audits/catalog.py:467` reads the manifest's `gates` | **RULED**: RO-3 ruling 8, *"Declared prefixes (Rec.)"*. `gate:5` resolves against a manifest that lists Gate 5 for heavy only (see 8.5). |
| 7.49 | External | `slug`, `name`, `scope` | `harbor-ro3:94-95` | `catalog.py:146-157`; `data/catalog/externals.json` | **RULED** (ruling 8) |
| 7.50 | Feature file and `@SES1.4` tag | "The executable behaviour of one user-facing outcome" | `requirements-model.md:33, 158-159` | `Outcome.feature` (`catalog.py:81-83`) | **RULED** (§ 8.4, § 10) |
| 7.51 | Feature package | "A list of outcomes already in the catalog … the **epic**" | `requirements-model.md:35, 255` | none (draft T7) | **RULED** as a record (2026-10-30, § 12). Its identifier is an **UNSOURCED** sub-item. |
| 7.52 | Release Package | "Which outcomes a version is planned to carry … The Release Package says which **outcomes** advance in a version, replacing the earlier 'which REQ states advance'" | `requirements-model.md:39, 133-144` | No model in `catalog.py`. The template `src/gzkit/templates/release_package.md:1-15, 26-30` has `id: RELEASE-{{version}}`, `entries: - req: REQ-C0000 from: approved to: implemented`, and packages `WP-0000`. | **CONTRADICTED**: the template advances **REQ states** (`approved`→`implemented`, states found in no ruled set) under a REQ grammar `REQ-C0000` and a package grammar `WP-0000` that match neither `REQ-<n>` nor `WP-<NN>-<slug>`. The template cites `safe-mode-doctrine.md` § The Release Package, which this gather did not read. |
| 7.53 | Release targeting | "the lowest-version open Release Package is worked first" | `requirements-model.md:106-110` | none | **RULED** (2026-10-29, operator *"a"*) |
| 7.54 | ADR as a record | "One architecture decision … decision status (proposed, accepted, superseded …): no checklist, no work packages, no release". "Architecture decisions are peers of the catalog, never its parents" | `requirements-model.md:34, 43, 167-171` | No model implements it. Legacy `AdrFrontmatter` carries lane, kind and nine statuses (8.12). | **CONTRADICTED**: see 8.12. Two ADR concepts share one name and one id grammar. |
| 7.55 | Backlog board | "A view composed from the catalog and the ledger; never edited" | `requirements-model.md:41` | none | **SOURCED** |
| 7.56 | Delivery event types and cutover | "the measured candidate set"; "only events with a later `ts` are read" | `harbor-ro3:54-59` | `catalog.py:405-429`; `data/catalog/delivery_events.json` | **RULED**: rulings 10 to 12, *"All nine (Rec.)"*, *"Grammar over fields (Rec.)"*, *"Timestamp in registry (Rec.)"* |
| 7.57 | Alteration, Departure (form, duration, configuration change) | Alteration: "A planned remodel, approved at freeze". Departure: "A departure from the package's own approved specification" | RO-5 amendment 4 (cited in code; the RO-5 page was not read here) | `catalog.py:160-188` (`reconnected/replaced/retired`; `deviation/waiver`; `temporary/permanent`) | **SOURCED** (here; the ruling is in RO-5, outside this gather) |
| 7.58 | "Layer" (records-table column) | Layer 1 canon, 2 ledger, 3 view (`requirements-model.md:26-41`, state doctrine) | as cited | — | **SOURCED**, but the word collides: `layered-trust.md:22-27` uses Layer 1/2/3 for **tools** (evidence gathering, ledger consumption, file sync), and `gate5-architecture.md:22-56` uses Layer 1/2/3 for **docs** (runbook, manpages, docstrings). |

---

## Domain 8a: Gates

| # | Term | Meaning as stated | Defined | Implemented | Status |
|---|---|---|---|---|---|
| 8.1 | Gate 1 | "ADR recorded \| the ADR exists and its frontmatter agrees with the ledger" (AGENTS). "ADR (Intent) … Record intent and tradeoffs before implementation … Applies to: All work" (charter) | `AGENTS.md:121-127`; `docs/governance/GovZero/charter.md:32-38` | `src/gzkit/commands/gates.py:27` `Gate1Result = Literal["pass","fail","policy_breach"]`; `.gzkit/manifest.json` `gates` | **CONTRADICTED** at the new levels. The charter says Gate 1 "Applies to: All work", but requirements-model:164-166 rules that an outcome needs "zero or more" ADRs. A work order or outcome with no ADR has no defined Gate 1. |
| 8.2 | Gate 2 | "Tests pass \| `uv run gz test`". Charter: "TDD … Passing unit tests with coverage floor (≥40%)" | `AGENTS.md:126`; `charter.md:42-48` | `gates.py:437-442`; manifest `verification.test` | **SOURCED** |
| 8.3 | Gate 3 | "Docs updated \| `uv run mkdocs build --strict`, plus the skill audit". "Heavy lane only" | `AGENTS.md:127`; `charter.md:52-58` | `gates.py:443-448` | **SOURCED**. Collision: `gate5-architecture.md:10, 13` calls docs "the Gate 5 artifact" (8.6). |
| 8.4 | Gate 4 | "BDD verified \| `uv run -m behave features/`". "Gate 4 precedes Gate 5 on the heavy lane and nowhere else" | `AGENTS.md:128, 139`; `charter.md:62-68` | `gates.py:449-454` | **CONTRADICTED**, pending adoption. Requirements-model § 10 moves the BDD anchor "from the ADR's lane to the outcome" (`:175-177`, `:477`), but AGENTS still binds it to the lane. |
| 8.5 | Gate 5 | "Human attests \| the operator's attestation". "Gate 5 is universal: it applies to every OBPI completion in every lane, kind and sensitivity" | `AGENTS.md:129, 131`; `charter.md:72-80` (lite gates "1, 2, 5", `:89`) | `src/gzkit/commands/adr_audit.py:496-513` returns `True`; `ledger_semantics.py:16-29`; `gates.py:285-287` prints "Gate 5 (Human): PENDING (manual)". **`.gzkit/manifest.json` `gates`: `"lite": [1, 2]`, `"heavy": [1, 2, 3, 4, 5]`**, read by `gates.py:430` and `trust_audits/catalog.py:467`. | **RULED**: ADR-0.0.36 Decision, "Brief-level human attestation is required for every OBPI completion, regardless of parent ADR kind or lane. There is no self-close path" (operator: *"drop all ideas of self-closing… GovZero is Zero-maxxing"*). **CONTRADICTED** by four sources: (a) the manifest's `lite: [1,2]` omits Gate 5; (b) `obpi-runtime-contract.md:156, 187-191, 324-325` still says "Heavy-lane (any kind) or foundation-kind … require attestation"; (c) `obpi-transaction-contract.md:52-53, 168-169, 183` says "Heavy and Foundation work MUST preserve Gate 5"; (d) `gate5-architecture.md:10`: "Gate 5 enforces **code-documentation-intent alignment** for Heavy lane work". |
| 8.6 | Gate 5's level | The § 12 table puts **Gate 5** in the Order row: "**Gate 5 sits at the order**, as on every OBPI (operator: *"answer was A"*). The package closes when its orders close" | `requirements-model.md:257, 264-266` | Order: `events.py:2034-2080`, with `decision`, `attestor` and operator words "at closed". Package: `events.py:1819, 1826`, `attestor` "The Gate 5 attestor; required into closed" and `decision` "The Gate 5 decision, at closed". Outcome: `events.py:1764`. | **CONTRADICTED**: § 12 against the package-level and outcome-level Gate 5 fields. The legacy story level also carries Gate 5: the charter says "Human attestation is the sole authority for ADR closeout" (`charter.md:80`) and `adr-lifecycle.md:142-148` "When a human provides Gate 5 attestation, the ADR status updates". |
| 8.7 | Gate 5 decisions | `proceed`, `redirect`, `pause`, `terminate` (per order: "redirect as a superseding order …, terminate returning the REQ to the package unbound") | `requirements-model.md:229` | `events.py:1792` `WorkPackageDecision` | **RULED** (RP-12 ruling 30, 2026-11-04, operator *"A"*). The draft already lists it in § 5. |
| 8.8 | Closeout attestation terms | "**Completed** / **Completed — Partial: [reason]** / **Dropped — [reason]** … These terms are canonical" | `charter.md:98-108`; `adr-lifecycle.md:144-148`; `audit-protocol.md:31-33` | `ledger.py:148-152`: `"partial": "Completed - Partial"` (a hyphen, not the em dash) | **SOURCED**. A **RULED** mapping exists to the order vocabulary: "PRD FR-009's Completed, Partial and Dropped map to proceed, redirect and terminate" (`requirements-model.md:229`). Two vocabularies are in use. |
| 8.9 | Operator-verbatim attestation | "operator-verbatim conversational attestation IS the Gate-5 attestation … `attestation_type: operator-verbatim-conversational`" | ADR-0.0.36:39 | `--attestation-text` | **RULED**: operator, 2026-05-14, *"WHEN I SAY ATTEST COMPLETED IT IS MOTHERFUCKING COMPLETE — ALWAYS, ALWAYS, ALWAYS"* |
| 8.10 | REQ-coverage gate | "every BEHAVIOR REQ needs a passing `@covers` test before `gz obpi complete`. A gap stops completion on heavy lane or foundation kind and warns on lite … `--accept-uncovered` never waives a BEHAVIOR REQ (GHI #537)" | `AGENTS.md:156` | `obpi_completion_uncovered_accept` event (`events.py:592`) | **RULED** (ADR-0.0.25). **CONTRADICTED** in detail: ADR-0.0.25 Decision 1 checks "any REQ" and Decision 2 lets `--accept-uncovered=REQ-…` waive any REQ, "Heavy/foundation briefs require an interactive TTY + `ACCEPT` confirmation" (ADR-0.0.25:46-59). AGENTS limits the gate to BEHAVIOR REQs and forbids waiving them, and the TTY gate was removed (ADR-0.0.36 addendum, :39). The ADR text was not amended. |
| 8.11 | Pool isolation from gates | Pool ADRs "must not receive Gate 1+ events" | `trust_audits/taxonomy.py:59-67` | `taxonomy.py:35-45`, a forbidden-event set holding `attestation`, `obpi_completed`, `adr_attested`, `adr_audit` and `adr_closeout` | **SOURCED**. Four of those seven names (`attestation`, `obpi_completed`, `adr_attested`, `adr_closeout`) are not event types in `events.py`. `req_kind_support.py:43` calls `obpi_completed` a "ghost". Those four entries are **UNSOURCED**. |

## Domain 8b: Lanes, ADR kinds, sensitivity

| # | Term | Meaning as stated | Defined | Implemented | Status |
|---|---|---|---|---|---|
| 8.12 | Lane `lite` / `heavy` | "`heavy` lane … is for changes to a CLI, API, schema or runtime contract used by humans or external systems; documentation, process and template changes stay `lite`" | `AGENTS.md:129`; `charter.md:85-94` | `core/models.py:365` `Literal["lite","heavy"]` (ADR); `:380` OBPI `Literal["lite","heavy","Lite","Heavy"]`; `obpi.json` lane enum is the same; `catalog.py:209-211` (repair package only); `events.py:1832` (package lane derived at close) | **RULED**: ADR-0.0.17 decision 1 (locked with the operator 2026-04-18): "`kind` and `lane` are orthogonal … Lane describes *external-contract exposure*". **CONTRADICTED** by two sources: (a) the OBPI enum's widening to `Lite`/`Heavy` is named as the defect instance (#1319) in `.gzkit/rules/models.md` § Closed sets, and `ledger-schema.md:255-261` gives `Lite \| Heavy`; (b) ADR-0.0.17:42 says "Pool ADRs have no lane until promoted", but pool frontmatter carries `lane: lite` (`docs/design/adr/pool/ADR-pool.adr-amendment-tracking.md:5`), and ADR-0.0.17:73 allows "hint fields". |
| 8.13 | Where lane lives | Legacy: on the ADR and the OBPI. New model: "lane wording moves from the ADR to the outcome" via `user_facing` (`requirements-model.md:477`). A repair package "holds its lane" and a delivery package "holds no lane, which the outcome derives" (`catalog.py:194-198`). | as cited | as cited | **CONTRADICTED**, pending adoption. Lane sits at four places (ADR, OBPI, repair package, package-close event), plus `user_facing` on the outcome. |
| 8.14 | Lane → gates | lite: Gates 1–2 (plus universal Gate 5); heavy: 1–5 | `AGENTS.md:129-131`; `charter.md:87-90` (lite 1, 2, 5) | `.gzkit/manifest.json` `gates` (lite `[1,2]`) | **CONTRADICTED**: see 8.5(a) |
| 8.15 | ADR kind `feature` | "active/committed (or queued) capability. Carries release-impacting semver (`0.y.z` and up)" | ADR-0.0.17:37-41; `AGENTS.md:133` | `core/models.py:366` `Literal["foundation","feature"]`; `taxonomy.py:271-303` | **RULED** (ADR-0.0.17, locked 2026-04-18) |
| 8.16 | ADR kind `pool` | "storage/waiting area for backlog items. No semver, no lane". "Pool kind derives from id prefix, not frontmatter" | ADR-0.0.17:38, 46; `AGENTS.md:133` ("New gzkit ADRs are `feature` … or `pool`") | `taxonomy.py:261-268` (a `kind:` on a pool ADR is an error); pool interview `semver: "pool"` `taxonomy.py:145-150` | **RULED** (ADR-0.0.17 decision 3). **CONTRADICTED** by two sources: (a) `src/gzkit/schemas/adr.json` frontmatter `required: ["id","status","semver","lane","kind","parent","date"]`, and `AdrFrontmatter` (`core/models.py:352-369`) requires `kind` and a numeric `semver`. The schema's own `kind` description says "Pool ADRs have no kind in frontmatter", yet a pool file (id, status, parent, lane only) fails that required list. (b) `adr-lifecycle.md:49-56, 90-97` gives the pool identifier as `0.2.0-pool.forecaster-core` and `ADR-0.2.0-pool.exog-pipeline.md`, against the live grammar `ADR-pool.<slug>` (`core/models.py:34`). "Pool" is also an ADR **status** (8.20), so the word is both a kind and a status. |
| 8.17 | ADR kind `foundation` | "app/system invariants and identity-shaping facts … Always `0.0.x`". "`foundation` (`0.0.x`) is CLOSED to new authoring here (roster `data/foundation_grandfather.json`; adopters scaffold open)" | ADR-0.0.17:39; `AGENTS.md:133`; ADR-0.0.18:19-32 | `taxonomy.py:289-303, 527-593` (`foundation_kind_closed`, `grandfather_dangling`, `foundation_limbo`); `core/models.py:113-132` | **RULED**: ADR-0.34.0 Decision (attested 2026-07-31). The ADR-0.0.37 amendment to ADR-0.0.18 (:163-170) requires a structural witness. Nominal integers come from ADR-0.0.57 (ADR-0.0.17:159-167). |
| 8.18 | Foundation grandfather manifest | "IDENTITY-ONLY entries (id, title, semver, frozen_at) and NO lifecycle field" | ADR-0.34.0:27 | `data/foundation_grandfather.json` (51 entries, a JSON list); `gzkit.models.foundation_grandfather` (not read) | **RULED** (ADR-0.34.0) |
| 8.19 | Sensitivity | "Permitted values: `security` or absent". "`security` sensitivity adds security-scan requirements to Gate 5" | ADR-0.0.22:38; `AGENTS.md:146`; `.gzkit/rules/security-sensitivity.md:15-29` | `core/models.py:369, 394` `Literal["security"] \| None`; `adr_audit.py` sensitivity predicate (:490-493) | **RULED** (ADR-0.0.22 Decision). The hangar demotion to advisory is SOURCED as "deliberate, not a defect" (`security-sensitivity.md:29`). |

## Domain 8c: ADR and OBPI states and statuses

| # | Term | Meaning as stated | Defined | Implemented | Status |
|---|---|---|---|---|---|
| 8.20 | ADR lifecycle states | Canon: Pool, Draft, Proposed, Accepted, Completed, Validated, Superseded, **Abandoned** ("Canon … if conflict exists, this document governs") | `adr-lifecycle.md:5, 12-25, 222-223` | **Six differing sets:** `AdrFrontmatter`/`adr.json` adds Pending and Deprecated and drops Abandoned (`core/models.py:353-363`); `ADR_TRANSITIONS` has Pool…Validated plus Superseded and Deprecated, with no Abandoned or Pending (`core/lifecycle.py:46-61`); the registry has `["Draft","Proposed","Accepted","Superseded","Deprecated"]` (`registry.py:166-170`); `derive_adr_semantics` emits Validated, Abandoned, Completed, Accepted and Pending (`ledger.py:1518-1553`); `ledger-schema.md:243-245` matches the canon; the new model's decision status is "proposed, accepted, superseded" (`requirements-model.md:167`) | **CONTRADICTED** |
| 8.21 | Dropped closeout end state | Canon: "**Dropped — [reason]** \| Abandoned" | `adr-lifecycle.md:148, 167` | `lifecycle.py:208, 220`: "A dropped closeout ends `Deprecated`". `ledger.py:1529-1530`: `"dropped"` → `"Abandoned"` | **CONTRADICTED**: the transition writer and the status deriver disagree, and canon names "Deprecated" a non-canonical term ("Use 'Superseded' … or 'Abandoned'", `adr-lifecycle.md:211`). |
| 8.22 | `Pending` | Canon: "Pending \| Use "Proposed" or "Accepted"" (deprecated) | `adr-lifecycle.md:212` | `ledger.py:1536-1544` derives `Pending` for every pre-attestation ADR not yet Accepted; the schema keeps it "for legacy on-disk values" | **CONTRADICTED** |
| 8.23 | Work-start transitions | "if we start work on an ADR, it is accepted"; Draft walks through Proposed | `lifecycle.py:184-200` | same | **RULED**: operator 2026-09-16 and 2026-09-28 (quoted in code) |
| 8.24 | Pool promotion's source status | The pool file is marked "`status: Superseded`, `promoted_to: …`" | `adr-lifecycle.md:134` | — | **CONTRADICTED** within the doc: "ADRs in the `docs/design/adr/pool/` directory may **ONLY** have status `Pool`" (`adr-lifecycle.md:101`) |
| 8.25 | Closeout phase | `pre_closeout`, `closeout_initiated`, `attested`, `validated` | — | `ledger.py:1525-1544` | **SOURCED** (code only) |
| 8.26 | Release tag rule | "The release tag SHALL be the highest validated non-foundation ADR" | `adr-lifecycle.md:251-275` | — | **CONTRADICTED**: requirements-model § 7 rules that "No version appears in any outcome, work package or REQ id" and that releases are Release Package membership plus a ledger release record (`requirements-model.md:133-144`) |
| 8.27 | OBPI frontmatter status | Union "accepts operator-facing terms and canonical OBPI_RUNTIME_STATES (ADR-0.0.16 STATUS_VOCAB_MAPPING)": Draft, Active, Completed, Abandoned, pending, in_progress, completed, attested_completed, validated, drift, withdrawn | `src/gzkit/schemas/obpi.json` (status description) | `core/models.py:381-393`; `registry.py:175-190` | **SOURCED**. It lacks `repudiated` (8.29). |
| 8.28 | OBPI operator-facing transitions | Draft→Active→Completed; Draft or Active→Abandoned | — | `core/lifecycle.py:63-68` | **SOURCED**. `Abandoned` has no ledger event (8.36). |
| 8.29 | OBPI runtime states | Contract: pending, in_progress, completed, attested_completed, validated, drift (6) | `obpi-runtime-contract.md:149-158` | `ledger.py:154-162` lists 7 (adds `withdrawn`). `ledger_semantics.py:416-522` emits 8 (adds `repudiated`). | **CONTRADICTED**: three different lists. |
| 8.30 | `completed` vs `attested_completed` | `completed`: "Lite-compatible completion proof is present". `attested_completed`: "Heavy-lane (any kind) or foundation-kind (any lane)" | `obpi-runtime-contract.md:155-156` | `ledger_semantics.py:443-446` keys on the receipt's `obpi_completion` value | **CONTRADICTED**: ADR-0.0.36 Decision 3 refuses new receipts with "`obpi_completion: completed` without the `attested_` prefix". The contract still frames the pair as lite versus heavy. |
| 8.31 | `attestation_requirement` / `attestation_state` | `optional`/`required`; `not_required`/`missing`/`recorded` | `obpi-runtime-contract.md:180-199` | `ledger.py:170-171`; `ledger_semantics.py:32-57, 406-413`. A withdrawn OBPI emits `optional`/`not_required` (`:465-466`). | **CONTRADICTED**: ADR-0.0.36 removes "the receipt schema's `optional` enum value" for new entries (:33, :75). The code keeps it for legacy receipts and for withdrawn OBPIs. |
| 8.32 | `proof_state`; `anchor_state`; `req_proof_inputs` kinds and status | as listed | `obpi-runtime-contract.md:168-178, 203-236, 303-312` | `ledger.py:169-175`; `ledger_semantics.py` | **SOURCED** (the doc and the code agree) |
| 8.33 | Pipeline stage, entry, position | stages `implement/verify/ceremony/sync`; entries `full/verify/ceremony/sync`; position kinds `task/phase/round/step` | `obpi-runtime-contract.md:81-117` | `events.py:654-657`; `pipeline_stage_fence.py` `CANONICAL_STAGES` (not read) | **SOURCED** |
| 8.34 | Parked / unparked | "reversible retirement of an OBPI whose parent left active status" | — | `events.py:380-397`; `obpi_lifecycle.py:81-101` | **SOURCED** (GHI #584) |
| 8.35 | Blocked on operator / unblocked | "the OBPI's next legitimate action is a human's" | `parser_obpi.py:453-490` | `events.py:400-443`; `obpi_lifecycle.py:104-151` | **SOURCED** (GHI #887) |
| 8.36 | `obpi_abandoned` | Listed among "Events that permanently retire an OBPI", and used in ADR-0.34.0's partition as a negation | `obpi_lifecycle.py:20-29`; ADR-0.34.0:23 | **No event model** in `events.py`, no producer, no CLI verb. A text search of `src`, `docs/governance`, `.gzkit/rules` and `AGENTS.md` finds it only at `obpi_lifecycle.py:27`. | **UNSOURCED** |

## Domain 8d: Undo verbs

| # | Term | Meaning as stated | Defined | Implemented | Status |
|---|---|---|---|---|---|
| 8.37 | `gz obpi withdraw` | "retires an OBPI permanently (superseded, phantom, duplicate; not re-completable)". Help text: "Withdraw a phantom or erroneous OBPI" | `AGENTS.md:137`; ADR-0.0.71:39 (sticky `withdrawn=True`) | `parser_obpi.py:424-451` (requires `--attestor`); `events.py:353-358` `attestor: str = ""` (optional in the model); `ledger.py:1306-1318` | **RULED** as existing doctrine, recorded by ADR-0.0.71 (*"Two verbs, two meanings is clearer and safer"*, ADR-0.0.71:208). The CLI requires an attestor while the event model defaults it to empty. |
| 8.38 | `gz obpi repudiate` | "reverses a completion whose attestation or evidence was invalid while the work intent stands (re-completable by genuine re-attestation)". Causes: `model-induced-fabrication`, `operator-error`, `verification-invalid` | `AGENTS.md:137`; ADR-0.0.71:47-55, BI 87-108 | `parser_obpi.py:551-596`; `events.py:513-519`; `ledger.py:1274-1280, 1384-1395`; `ledger_semantics.py:483-522` | **RULED**: ADR-0.0.71, operator 2026-06-12, *"new verb means adr... i accept."* **CONTRADICTED** in code: `obpi_lifecycle.py:20-29` puts `obpi_completion_repudiated` in `TERMINAL_EVENTS`, "Events that **permanently retire** an OBPI", against ADR-0.0.71 BI 2 ("Repudiation reverses, it does not retire") and BI 5. Through that set, `orphaned_obpi_ids` and `parkable_children` treat a repudiated OBPI as permanently disposed. |
| 8.39 | `gz obpi supersede` | "Record an obpi_superseded event … replaced by the superseding OBPI named via --by" | `parser_obpi.py:513-549` | `events.py` `ObpiSupersededEvent` (`superseded_by`, `rationale`, `attestor`); in `TERMINAL_EVENTS` | **SOURCED**. It overlaps AGENTS.md's "withdraw … (superseded, …)": two verbs claim supersession. |
| 8.40 | `gz wp withdraw-legacy` / `legacy_unit_withdrawn` | "`gz obpi withdraw`'s successor (RO-14 ruling 13)" | `events.py:361-377`; `docs/user/manpages/wp-withdraw-legacy.md` (not read) | `obpi_lifecycle.py:16-18`; `ledger.py:1311` | **SOURCED** here (RO-14 ruling 13 is cited but its page was not read) |
| 8.41 | `ledger_event_corrected` (`gz ledger correct`) | "append-only corrective action over any event"; dispositions `void/discharged/reinstated`; causes `agent-error/operator-error/runtime-error/condition-resolved` | `events.py:522-548` docstring, quoting the operator: *"we need the power to UNDO agent (or human) error"* | `events.py:546-548` | **SOURCED** (GHI #611; the operator's intent is quoted in code, but no ruling record was read) |
| 8.42 | "Two verbs undo a completion" | AGENTS: exactly two (withdraw, repudiate) | `AGENTS.md:137` | The code has withdraw, withdraw-legacy, repudiate and supersede (`TERMINAL_EVENTS`), plus park, block and ledger-correct as reversible dispositions | **CONTRADICTED**: AGENTS' count of two against the roster in code |

---

## Collisions with the draft's § 1 level table

1. **Gate 5's level.** § 12 puts Gate 5 at the Order ("as on every OBPI"), so legacy OBPI Gate 5 matches. Gate 5 also appears at the **Story** level in two places: legacy ADR closeout (`charter.md:80`; `adr-lifecycle.md:142-148`) and the new `work_package_transitioned` close, which has `attestor`, "The Gate 5 attestor; required into closed", and `decision`, "The Gate 5 decision, at closed" (`events.py:1819, 1826`). It is attested at the **outcome** too (`events.py:1764`; `harbor-ro3:108`), although § 12 rules the outcome's `validated` "derived, not attested". § 12 says the package closes when its orders close, and that the **epic** carries the value or seaworthiness attestation.
2. **"ADR" has two meanings.** It is (a) the decision record, a catalog peer with status proposed, accepted or superseded and no checklist (§ 9), and (b) the mADR, which § 12 says the Story succeeds ("Work package … Succeeds the mADR"). Gate 1 ("ADR recorded"), lane, kind and closeout all bind to sense (b), while § 9 keeps only sense (a). One id grammar serves both.
3. **OBPI is the "legacy order".** This is consistent with § 12's Succeeds column. OBPI states (8.27–8.31) and undo verbs (8.37–8.42) are therefore order-level vocabulary. The new order states (`opened → frozen → commenced → accepted → closed`, `events.py:2035`) do not crosswalk to them anywhere.
4. **Lane is spread across levels.** It sits on the ADR (story), the OBPI (order), the repair package (story, stored), the package close (story, derived), and as `user_facing` on the outcome (catalog). No source rules which level owns it.
5. **Gates 1–4 have no level.** Gates attach to the ADR's lane in legacy canon. The release template has "Each shipped package's lane gates" (`release_package.md:37-39`), which is story level, and `depends_on: gate:<n>` lets an outcome depend on a gate. Nothing maps Gates 1–4 onto Epic, Story, Order or Action.
6. **STRUCTURAL-FENCE is tied to the parent ADR.** It is "a cross-OBPI invariant scoped to the parent ADR", which at the new levels means a cross-order invariant scoped to the story. Its proof anchor (`## Boundary Invariants` on the parent ADR) has no counterpart on a work package or repair package. Catalog and repair REQs have no parent ADR (7.11).
7. **"Validated" at four levels.** ADR `Validated` (post-audit), OBPI runtime `validated`, outcome `validated` (derived), and `proof_state` `validated`.
8. **"Kind" is overloaded.** REQ kind (BEHAVIOR…), ADR kind (feature, pool, foundation), work package `kind` (delivery, repair), `req_proof_inputs.kind` (command, artifact, …), `IdKind` (ADR, OBPI, REQ, TASK), and `kind` on `artifact_renamed`.
9. **The construction side has three names** (7.23): construction, catalog, delivery.
10. **Release.** The Release Package (§ 7), the release-tag rule (8.26) and the release template (7.52) are three different release models.

## Contradictions (one line each)

- C1 Gate 5 universality: ADR-0.0.36 and AGENTS.md:131 say every lane. Against them: `.gzkit/manifest.json` gates `lite: [1,2]`; `obpi-runtime-contract.md:156,187-191,324`; `obpi-transaction-contract.md:52-53,168-169,183`.
- C2 Gate 5's meaning: `charter.md:72-80` says human attestation; `gate5-architecture.md:10` says "code-documentation-intent alignment for Heavy lane work".
- C3 Gate 5's level: requirements-model § 12 (:264) puts it at the order. `events.py:1819,1826` (package close), `events.py:1764` and `harbor-ro3:108` (outcome `validated`), and `charter.md:80` (ADR closeout) each place it elsewhere.
- C4 Outcome `validated`: requirements-model.md:267 says derived, not attested; `events.py:1764` and `harbor-ro3:108` say the attestor is required into validated.
- C5 Outcome `withdrawn`: requirements-model.md:87-89 rules a terminal `withdrawn`; the `LifecycleState`/`OutcomeState` Literal at `events.py:1732-1746` lacks it.
- C6 Outcome `modules`: ruled at requirements-model.md:31,128; absent from the `Outcome` model (`catalog.py:68-84`, extra=forbid), although `WorkPackage.modules` says it reads it (`catalog.py:213-216`).
- C7 Release Package: requirements-model.md:137-140 says it advances outcomes; `templates/release_package.md:6-8,30` advances REQ states `approved→implemented` with `REQ-C0000` and `WP-0000` grammars.
- C8 BEHAVIOR for user-facing: requirements-model.md:179 requires scenario AND `@covers`; tests.md:89 accepts scenario OR `@covers`.
- C9 Catalog and repair REQ kinds: requirements-model.md:180 says the declared proof channels are kept; `req_kind_fence.py:224-226` and `validate_req_kind.py:29-34` cannot resolve or check a `REQ-<n>`.
- C10 STRUCTURAL-FENCE at the OBPI layer: ADR-0.0.59:33 and req-scope-discipline.md:186-188 say grandfathered/advisory; `req_kind.py:243` says unproven-fence, fail-close.
- C11 SUPPORT parity status: req-scope-discipline.md:400-405 says always advisory-support; `req_kind_support.py:353-413` resolves for real.
- C12 SUPPORT brief check: req-scope-discipline.md:305-306 fails on "lacks both"; `validate_req_kind.py:97-100` fails when either is missing.
- C13 STRUCTURAL-FENCE brief check: req-scope-discipline.md:307 needs the heading only; :190-202 and `validate_req_kind.py:138-151` also require the OBPI anchor.
- C14 `proof_status` vocabulary: req-scope-discipline.md:345, `req_kind.py:85` and the code's eleven emitted values are three different lists.
- C15 Fourth REQ kind: ADR-0.0.59:33 and BI 1 require a foundation ADR amendment; the foundation kind has been closed since ADR-0.34.0 (AGENTS.md:133).
- C16 Construction-side naming: construction (`requirements-model.md:253`), `catalog` (`catalog.py:123`), `delivery` (`catalog.py:204`).
- C17 Family code width: three letters ruled 2026-10-30 (`requirements-model.md:190-193`); one letter in `catalog.py:60` and `families.json` (draft T8).
- C18 ADR states: `adr-lifecycle.md:12-25` and five code or schema sets (`core/models.py:353-363`, `core/lifecycle.py:46-61`, `registry.py:166-170`, `ledger.py:1518-1553`, plus `requirements-model.md:167`) disagree.
- C19 Dropped closeout: `lifecycle.py:220` ends Deprecated; `ledger.py:1530` and `adr-lifecycle.md:148` say Abandoned.
- C20 `Pending`: a deprecated term in `adr-lifecycle.md:212`, yet derived by `ledger.py:1537,1543`.
- C21 Pool status: `adr-lifecycle.md:101` allows only `Pool` in pool/; `adr-lifecycle.md:134` marks the promoted pool file `status: Superseded`.
- C22 Pool identifier: `adr-lifecycle.md:53,94` gives `ADR-0.2.0-pool.<slug>`; `core/models.py:34` and ADR-0.0.17 give `ADR-pool.<slug>`.
- C23 Pool frontmatter: ADR-0.0.17:46,60 (no kind, no semver, no lane) against `adr.json`'s required kind, semver and date and `AdrFrontmatter` (`core/models.py:364-366`), and against live pool files carrying `lane`.
- C24 OBPI lane enum: `models.md` § Closed sets names the `Lite`/`Heavy` widening a defect (#1319), yet it remains at `core/models.py:380`, in `obpi.json`, and in `ledger-schema.md:259`.
- C25 Lane location: AGENTS.md:129 keys lanes on the ADR; requirements-model.md:175-177,477 moves them to the outcome's `user_facing`; `catalog.py:194-211` stores them on repair packages only.
- C26 Gate 1 scope: `charter.md:38` says "All work"; `requirements-model.md:164-166` says an outcome has zero or more ADRs.
- C27 Gate 4 binding: AGENTS.md:139 binds it to the heavy lane; requirements-model.md:175-177 binds it to `user_facing` outcomes.
- C28 OBPI runtime states: the contract lists 6 (`obpi-runtime-contract.md:149-158`), `ledger.py:154-162` lists 7, and `ledger_semantics.py` emits 8 (with `repudiated`).
- C29 `completed`/`attested_completed` and `optional`: ADR-0.0.36 Decisions 3 and 33 retire both for new receipts; `obpi-runtime-contract.md:155-156,180-199` and `ledger.py:170-171` keep them.
- C30 Repudiation's terminality: ADR-0.0.71 BI 2 and 5 say it reverses and does not retire; `obpi_lifecycle.py:20-29` lists it in `TERMINAL_EVENTS`, "permanently retire".
- C31 Undo-verb count: AGENTS.md:137 says "Two verbs"; the code has withdraw, withdraw-legacy, repudiate, supersede and ledger-correct.
- C32 REQ-coverage gate: ADR-0.0.25 Decisions 1 and 2 cover any REQ, are waivable, and need TTY; AGENTS.md:156 covers BEHAVIOR only, never waived, with no TTY.
- C33 Release tag: `adr-lifecycle.md:253` uses the highest validated feature ADR; `requirements-model.md:133-144` uses Release Package membership with no version in any id.
- C34 Attestation-term spelling: "Completed — Partial" (em dash, `charter.md:105`) against `"Completed - Partial"` (hyphen, `ledger.py:150`).

## Counts

Each row is counted once, by its primary status.

- **Domain 7 (58 rows):** RULED 34, SOURCED 9, CONTRADICTED 15, UNSOURCED 0. One UNSOURCED sub-item: the feature package's identifier (7.51). 7.58 is a word collision and is counted SOURCED. 7.29 is RULED, with a residue flagged.
- **Domain 8 (42 rows):** RULED 8, SOURCED 14, CONTRADICTED 19, UNSOURCED 1 (8.36 `obpi_abandoned`). One UNSOURCED sub-item: four ghost event names in the pool-isolation list (8.11). Five CONTRADICTED rows are ruled terms whose implementation or other canon disagrees: 8.5 Gate 5, 8.10 REQ-coverage gate, 8.12 lane, 8.16 pool kind, 8.38 repudiate.
- **Total (100 rows):** RULED 42, SOURCED 23, CONTRADICTED 34, UNSOURCED 1, plus 2 UNSOURCED sub-items. The contradiction list has 34 entries, C1 to C34.

## Files read in full (line counts)

| File | Lines |
|---|---|
| `docs/governance/drydock-taxonomy.md` | 149 |
| `docs/governance/ieee/requirements-model.md` | 491 |
| `docs/governance/harbor-ro3-requirements-store.md` | 173 |
| `src/gzkit/models/catalog.py` | 429 |
| `src/gzkit/core/models.py` | 754 |
| `data/catalog/reqs.json` | 4 |
| `data/catalog/outcomes.json` | 4 |
| `data/catalog/families.json` | 71 |
| `src/gzkit/req_kind.py` | 363 |
| `src/gzkit/req_kind_support.py` | 413 |
| `src/gzkit/req_kind_fence.py` | 238 |
| `src/gzkit/commands/validate_req_kind.py` (the `--req-kind-discipline` implementation) | 260 |
| `docs/governance/req-scope-discipline.md` | 419 |
| `docs/design/adr/foundation/ADR-0.0.59-…/ADR-0.0.59-….md` | 244 |
| `docs/design/adr/foundation/ADR-0.0.36-universal-obpi-attestation/…md` | 181 |
| `docs/design/adr/foundation/ADR-0.0.71-completion-repudiation/…md` | 242 |
| `docs/design/adr/foundation/ADR-0.0.25-obpi-completion-req-coverage-gate/…md` | 170 |
| `docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/…md` | 179 |
| `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/…md` | 203 |
| `docs/design/adr/pre-release/ADR-0.34.0-foundation-sunset/…md` | 152 |
| `AGENTS.md` (§ Gate Covenant and § OBPI Acceptance Protocol at :119-160; the whole file was in context) | 248 |
| `.gzkit/rules/tests.md` | 113 |
| `.gzkit/rules/security-sensitivity.md` | 52 |
| `.gzkit/rules/models.md`, `adr-audit.md`, `gate5-runbook-code-covenant.md`, `mode-contract.md` (read as their `.claude/rules` mirrors, loaded in context) | 37 / 70 / 46 / 21 (mirror text) |
| `docs/governance/GovZero/adr-lifecycle.md` | 285 |
| `docs/governance/GovZero/charter.md` | 119 |
| `docs/governance/GovZero/obpi-runtime-contract.md` | 327 |
| `docs/governance/GovZero/obpi-transaction-contract.md` | 193 |
| `docs/governance/GovZero/gate5-architecture.md` | 184 |
| `docs/governance/GovZero/ledger-schema.md` | 383 |
| `docs/governance/GovZero/layered-trust.md` | 301 |
| `src/gzkit/ledger_semantics.py` | 650 |
| `src/gzkit/obpi_lifecycle.py` | 419 |
| `src/gzkit/lifecycle.py` | 230 |
| `src/gzkit/core/lifecycle.py` | 129 |
| `src/gzkit/governance/trust_audits/taxonomy.py` | 836 |
| `src/gzkit/templates/release_package.md` | 48 |

**Read in part, which is not a full read:**

- `src/gzkit/events.py` (2488 lines): lines 100-260, 350-445 and 500-560, the `Literal` grep of the whole file, 1725-1860, and the order block at 2034-2080.
- `src/gzkit/ledger.py` (1646 lines): 140-175, 1100-1120, 1185-1300 and 1500-1555.
- `src/gzkit/cli/parser_obpi.py`: 415-600.
- `src/gzkit/commands/gates.py`: 25-60, 285-300 and 415-470.
- `src/gzkit/commands/adr_audit.py`: 490-515.
- `src/gzkit/registry.py`: 160-200.
- `src/gzkit/catalog_ledger.py` (170 lines): 1-75.
- ADR-0.0.22 (336 lines): lines 1-80 in full; lines 80-336 were viewed condensed and are OBPI decomposition and Q&A.
- `src/gzkit/schemas/adr.json` and `obpi.json`: the frontmatter `required` lists and properties only.
- `.gzkit/manifest.json`: `gates` and `verification` only.
- `data/foundation_grandfather.json` (308 lines): parsed as a list of 51 entries; head and tail viewed.
- `docs/governance/GovZero/audit-protocol.md` (174 lines): text search only.

**Listed but not read** (`.gzkit/rules/` holds 29 files; `docs/governance/GovZero/` holds 24):

- The generated concatenation `.gzkit/rules/AGENTS.md`.
- `obpi-decomposition-matrix.md`, `staleness-classification.md`, `adr-obpi-ghi-audit-linkage.md`, `obpi-pipeline-runbook.md`, `command-doctrine.md`.
- `pipeline_stage_fence.py`, `gzkit.models.foundation_grandfather`, the RO-5, RP-12 and RO-14 specification pages, and `safe-mode-doctrine.md` § The Release Package.

Any claim above that rests on these is marked in its row.

---

## Gap-fill (2026-11-22, the coordinator's second pass)

This pass was read-only. Four sources were read whole: `src/gzkit/ledger.py` (1646 lines), ADR-0.0.22 (336 lines, every line), `docs/governance/GovZero/audit-protocol.md` (174 lines) and `docs/governance/GovZero/obpi-decomposition-matrix.md` (127 lines).

The ruling search ran `uv run gz handoff rulings --json --search "<term>"` once for each of 123 search strings covering the 100 terms. The help text calls the verb "Read-only". The corpus holds 2,463 rulings as plain strings, with no dates. The searches matched 577 distinct rulings, and all 577 were read. The raw results are in `(gathering scratch) rulings-D/`: `terms.txt`, `counts.txt`, `r<n>.json` and `union.txt`. In that directory, `[n]` refers to a line of `union.txt`.

### Status changes to the 100 terms

| Row | Was | Now | Why |
|---|---|---|---|
| 7.29 `revision` | RULED | **CONTRADICTED** (C35) | Ruling [92]: "A REQ's revision rises on any change to its statement, criteria or kind, and on nothing else (verbatim: "A")". RP-12 ruling 31 (`requirements-model.md:96`) says revision counts editorial amendments only. No retirement of [92] was found. |
| 7.42 Capability | RULED | **CONTRADICTED** (C36) | Rulings [183]–[186] give the capability a store, `data/catalog/capabilities.json`, written by the ruled, unbuilt `catalog capability` verb, landing empty; `gz validate --catalog` refuses an outcome whose capability has no record. Neither the store nor the verb exists: `CATALOG_FILES` (`catalog.py:27-34`) and `ls data/catalog` both lack it. |
| 7.57 Alteration / Departure | SOURCED | **RULED** | [259] (operator, "okay, A is it"); RP-12 ruling 63 [260]; [263]; RP-12 ruling 60 [264]; RO-5 [117] |
| 8.23 Work-start transitions | RULED | **CONTRADICTED** (C40) | [218] says "ADR-0.35.0 holds status Draft through implementation and the lifecycle question is CLOSED". Against it: [480] "If we start work on an ADR, it is accepted"; [482] "Walk Draft→Proposed→Accepted at launch"; and `lifecycle.py:184-200`. |
| 8.40 `withdraw-legacy` | SOURCED | **RULED** | [236]: "Tranche 1's names: gz wp dispatch, block, unblock and withdraw-legacy, with their work_package_ and legacy_unit_withdrawn events (verbatim: "a")" |
| 8.41 `ledger_event_corrected` | SOURCED | **RULED** | [576]: "we need the power to UNDO agent (or human) error"; "this isn't new design, this is defect correction." [274]: "Keep original events immutable. Corrections must be attributable…" |

**Rows that stay CONTRADICTED but now have a ruled side:**

- **8.5 / 8.14 (C1 narrowed).** Ruling [267] gives the manifest's lite list: "I accept the gate 4 and gate 5 correction" and "Yes to your correction on lite: [1,2]". The surviving contradictions are three:
  - `charter.md:89` gives "Lite | 1, 2, 5";
  - the manifest lists Gate 5 inside heavy's lane gates (`[1,2,3,4,5]`), although Gate 5 is not lane-gated;
  - the two OBPI contracts still scope Gate 5 to heavy and foundation work.
- **8.21 (C19).** Ruling [317] reads "GHI #1014 dropped closeout (verbatim: 'Map to Deprecated (Recommended)')". That ruling backs `lifecycle.py:220`. It is contradicted by `ledger.py:1530` (Abandoned) and by `adr-lifecycle.md:148, 211`, which calls Deprecated non-canonical.
- **7.45 (C4).** The code follows an earlier ruling. [196], RO-3 ruling 5, says "an attestor into validated". The later rulings, [210] and § 12, say "validated is derived". C4 is a ruling against a later ruling, with the code on the older one.
- **7.52 (C7).** The template follows an earlier ruling. [234] says "a separate release artifact governs which REQ states advance in a version". It was later replaced by [201], "A Release Package plans in outcomes and repair packages", which § 7 also records. [121] adds a related ruling: "prd drives major, release package drives minor, ghi pressure drives patch". That strengthens C33 against the release-tag rule in `adr-lifecycle.md`.
- **8.6 (C3, sharpened as C41).** Package-level Gate 5 is itself ruled. RP-12 ruling 77 [300] reads "Gate 5 refuses a subagent-stamped call at the order and the package (… both closes)", and Gate 5 was attested on WP-01 [295]. Ruling [200] also reads "Gate 5 is attested once at the work package's close", which [296] "Gate 5 sits at the order" replaced.
- **8.13.** The package side is ruled: `obpi-decomposition-matrix.md:7` (RO-5 rulings 4 and 9) reads "A work package's lane is read from its outcome … or stored on its repair package". [253] puts the lane criterion at the OBPI: "whether the external contract is changed by the OBPI". `AGENTS.md:129` still keys lane on the ADR.
- **7.43.** A second ruled field is missing from the model: `source` (C37). The ruled `modules` field (C6) is reinforced three times: [205] "the outcome, which gains a modules field", [93] the freeze lock covers "the outcome's statement, modules and user_facing", and [80].
- **7.44.** C5 is reinforced by [235]: "A withdrawal is the terminal state withdrawn, setting retired, allowed only before released".
- **8.38.** C30 is reinforced. The operator repudiated OBPIs and then re-completed them, [559]–[563]: "4. yes, we do the work right and thoroughly." That is the re-completable semantics `TERMINAL_EVENTS` denies.

**Further rulings for rows whose status is unchanged:**

- **7.2:** [4] re-kinding BEHAVIOR to SUPPORT inside attested briefs; [18], [212], [213] hexagon BEHAVIOR REQ variants (Montenegro Table 8.3).
- **7.3 / 8.4:** [20] "BDD stays the standing user-facing rationale, only re-anchored to the outcome"; [279]; [278] Behave stays out of the hexagon; [276].
- **7.14:** [62]. **7.19:** [67]; [88] decision 1, see G.17. **7.21:** RP-12 rulings 45 [68], 48 [69], 50 [70] ("a repair requirement supersedes only a repair requirement"; `ReqBase.supersedes` at `catalog.py:115-117` does not enforce it, and `gz validate --catalog` was not read), 53 [71] and 78 [72].
- **7.23:** [79] "Construction and repair are two pipelines on one runtime"; [80] and [81] use "delivery package". C16 stands, now with rulings on both sides.
- **7.30:** [103], [113]; RP-12 rulings 83 [114], 85 [458] and 87 [459].
- **7.37:** [117] "a DFS on a REQ is the scope disposition". **7.39 / 7.48:** [122]. **7.40:** [144], [147], [148] (C17). **7.47:** [203].
- **7.51:** [146], [207], [254], [255]. The feature package's identifier is still unsourced.
- **7.53:** [248]. **7.54:** [204], [488].
- **8.7:** RP-12 ruling 75 [313]. **8.10:** [333] "Keep lite-lane REQ gaps warn-only".
- **8.12:** [13] "external contract/api behavior must be heavy"; [253]; [334] "Lane is not route"; [168]; [339] (C39).
- **8.15 / 8.17:** [367], [368], [377], [420]. **8.16:** [367], [377], [414], [416] (C38).
- **8.37:** [204] "briefs withdraw as superseded". **8.39:** [537] "A supersede ends a run, with park and withdraw", which concerns a pipeline run, not the verb.
- **8.36 `obpi_abandoned`:** no ruling found. It stays UNSOURCED.

### New terms found in the gap-fill reading

| # | Term | Meaning as stated | Defined | Implemented | Status |
|---|---|---|---|---|---|
| G.1 | The five gates form a closed set | "New gate (Gate 6 — Security Review) … REJECTED: breaks the 5-gate covenant's stability … The 5-gate model is itself foundational (ADR-0.0.1 lineage)" | ADR-0.0.22:296, :320 | `gates.py` handlers 1–5 | **RULED** (ADR-0.0.22, Alternative 2) |
| G.2 | Step 4b before Gate 5 | "Step 4b is **mandatory and unconditional** before Gate 5 on OBPI completion" | [280] | not read here | **RULED** |
| G.3 | Corpus attestation is not Gate 5 | "Corpus attestation, NEVER Gate 5" | [283]; AGENTS § Attestation | — | **RULED** |
| G.4 | Pool entry status `Pulled`; the pool as intentions | "The pool stays as intentions, not ADRs, parsed into requirements on demand"; "the first gz catalog admit through the pool door sets the entry status to Pulled" | [414], [416], [197], [207] | **absent**: no `Pulled` string anywhere in `src/gzkit`, and `AdrFrontmatter.status` (`core/models.py:353-363`) lacks it | **CONTRADICTED** (C38) |
| G.5 | Outcome `source` | "Every catalog outcome requires its source, the 29148 source attribute and upward trace leg"; "An ADR leads to work through an outcome … its source and governed_by the ADR" | [199], [203]; `requirements-model.md:169` ("whose source and `governed_by` are the ADR") | **absent** from `Outcome` (`catalog.py:68-84`, extra=forbid) | **CONTRADICTED** (C37) |
| G.6 | Integrity level | The consequence bands become "a second axis beside lane, proposed only; lane keeps its external-contract criterion … named integrity level" | [168] | none (proposed only) | **RULED** (proposal only) |
| G.7 | Lane is not route | "only a finding of unmet ADR intent can go to a brief, and only by the operator's ruling" | [334] | ghi-close and ghi-author skills (not read) | **RULED** |
| G.8 | In-flight ADR and repair assignment | "The next-semver route for a correction to a Validated ADR is retired; such scope enters the in-flight ADR as a repair assignment" | [246], [245], [241], [244] | — | **RULED** |
| G.9 | Variant (hexagon REQ) | "one member of a hexagon handler's result union … avoid scenario, outcome, outcome row, path, case" | [213]; `tests.md:98` | `gz validate --hexagon-tests` (not read) | **RULED** |
| G.10 | Security walkthrough checklist | ADR: "credential handling reviewed, subprocess input validated, crypto choices justified, boundary validation confirmed", with a "receipt-stale (>24h) fails attestation" test. Rule: surface enumeration, receipt confirmation, classification confirmation. | ADR-0.0.22:215, :84, :245; `security-sensitivity.md:39-43` (RP-7 H4) | `gz obpi complete` reads the rule's section | **CONTRADICTED** (C47) |
| G.11 | Effective gate status | Within a Completed/Validated lifecycle epoch, "`gate_checked: fail` events are treated as observational noise", shown as pass, with a laundering sidecar | `ledger.py:1001-1097` (GHI #392, #411) | same | **SOURCED** |
| G.12 | Gate status values | "Mapping of gate number to latest status ("pass"/"fail")"; Gate 1 adds `policy_breach` | `ledger.py:962-999`; `gates.py:27` | `GateCheckedEvent.status: str` (unconstrained) | **SOURCED** |
| G.13 | ADR audit receipt events read as Gate 5 | `_AUDIT_HUMAN_ATTESTATION_EVENTS = {"validated","attested","accepted"}` | `ledger.py:164-168` | mirrors `adr_audit._HUMAN_ATTESTATION_RECEIPT_EVENTS` | **SOURCED** |
| G.14 | Closeout ceremony phases | Pre-Closeout / During Closeout / Post-Closeout; "Agent cannot self-transition out of 'During' phase" | `audit-protocol.md:83-99` | `closeout_phase` (`ledger.py:1525-1545`) | **SOURCED** |
| G.15 | Decomposition dimensions and overlays | five dimensions scored 0–2; Single-Narrative, Testability Ceiling, State Anchor and Surface Boundary overlays; Rule of Three (legacy) | `obpi-decomposition-matrix.md:11-57` | `gz validate --brief-size` (`src/gzkit/brief_size_bounds.json`) | **RULED** as rekeyed: "Rekeyed 2026-10-28 by drydock RO-5 ruling 9" |
| G.16 | The four records named | "requirements catalog (family.capability.outcome), feature package, work package, release package" | [146] | — | **RULED** |
| G.17 | Requirements-model decision 1 (grain) | "a REQ is one acceptance statement under a feature outcome and a work package plans one outcome (verbatim: "you got it")" | [88] | — | **RULED**, but **absent from its canon home**: `requirements-model.md` numbers its decisions from 2 ("### 2. Identity"), with no decision 1. Its "work package plans one outcome" clause was later amended by § 12. |

### New contradictions (C35 onward)

- **C35, `revision`.** Ruling [92] says revision "rises on any change to its statement, criteria or kind". RP-12 ruling 31 (`requirements-model.md:96`) says it counts "editorial amendments only … a change a test asserting the prior statement would fail against is a new REQ". No retirement of [92] was found.
- **C36, capability store.** Ruled by [183]–[186]: `data/catalog/capabilities.json`, the ruled, unbuilt `catalog capability` verb, and `gz validate --catalog` refusing an outcome whose capability has no record. In code: no such file in `CATALOG_FILES` (`catalog.py:27-34`) or in `data/catalog/`. This may be owed to RO-11, which [182] says lands "the capability records … by change order". Whether RO-11 has landed is for the track that read the RP pages.
- **C37, outcome `source`.** Ruled by [199] and [203], and written in `requirements-model.md:169`. The `Outcome` model has no `source` field, and `extra="forbid"` refuses one (`catalog.py:68-84`).
- **C38, what the pool is.** Rulings [414], [416], [197] and [207] make the pool intentions, "not ADRs", with an entry status `Pulled`. Against them: `AGENTS.md:133` "New gzkit ADRs are `feature` … or `pool` (`ADR-pool.<slug>`)"; `adr-lifecycle.md:99-108`, where pool status is `Pool` only; the `AdrFrontmatter.status` Literal; and the fact that no `Pulled` exists in `src/gzkit`.
- **C39, issue lane (candidate).** RP-12 ruling 64 [339] says "the issue lane retires in Act 5". Against it: `WorkPackage.lane`, "Stored on a repair package only" (`catalog.py:209-211`), and `obpi-decomposition-matrix.md:7` "stored on its repair package". The meaning of "issue lane" is unconfirmed; the track that read RP-12 should check it.
- **C40, ADR state at work start.** [218] says "ADR-0.35.0 holds status Draft through implementation and the lifecycle question is CLOSED". Against it: [480] "If we start work on an ADR, it is accepted", [482] "Walk Draft→Proposed→Accepted at launch", and `lifecycle.py:184-200`.
- **C41, Gate 5 at the package.** § 12 (`requirements-model.md:264-266`) says "The package closes when its orders close and its why is answered; the epic carries the value or seaworthiness attestation". Against it: RP-12 ruling 77 [300], "Gate 5 refuses a subagent-stamped call at the order and the package (… both closes)"; [295] "Gate 5 on WP-01, closing RO-9"; and `events.py:1819,1826`.
- **C42, a superseded OBPI's state.** `obpi_lifecycle.py:20-29` counts `obpi_superseded` as terminal, "permanently retire". `ledger.py:1371-1381` sets a `superseded` flag that `derive_obpi_semantics` never reads (`ledger_semantics.py:541-544` short-circuits only `withdrawn` and `repudiated`). A superseded OBPI therefore keeps deriving pending, completed and so on. The same holds for `parked` and `blocked_on_operator`.
- **C43, ADR attestation status overwritten.** `ledger.py:1244-1250` sets `attestation_status` to the receipt's `attestation_text`, the operator's free text, for any audit receipt `validated`, `attested` or `accepted`. `derive_adr_semantics` (`ledger.py:1529-1533`) matches only the tokens `dropped`, `completed` and `partial`. An ADR whose latest such event is an `attested` or `accepted` audit receipt, but not `validated`, therefore derives `Pending` or `Accepted`, not `Completed`, against the mapping in `adr-lifecycle.md:144-148`. This is inferred from reading the code; nothing was run.
- **C44, is the ledger proof of attestation?** `audit-protocol.md:55, 73, 165`: "Agent MUST treat logs and ledgers as reconciliation artifacts …, not as proof of human attestation"; "Ledger entries are for agent reconciliation only. They do not constitute proof of human attestation." Against it: `AGENTS.md:92`, "Completion evidence is the ledger", and the backstop for *Hallucinated authorization* in `agent-failure-modes.md`: "Gate 5 `--attestor` + non-empty `evidence.attestation_text`, ledger-written".
- **C45, what the decomposition matrix sizes.** `AGENTS.md:135`: "ADR Feature Checklist items and OBPI briefs correspond 1:1; size them with the OBPI Decomposition Matrix". `adr-lifecycle.md:179-201` calls the "checklist-to-brief count check … a blocking governance failure". Against both: `obpi-decomposition-matrix.md:7, 105-109`, "Rekeyed … size an **outcome** and a **task card** instead of an ADR checklist … the checklist-count step [is] retired" (RO-5 ruling 9).
- **C46, "task card".** `obpi-decomposition-matrix.md:7, 37, 41` still sizes "task cards". Against it: ruling [321], "The unit of action is the task; card is dropped", and `requirements-model.md:38`, "Called *task card* until 2026-11-03".
- **C47, security walkthrough checklist.** ADR-0.0.22:215 and :84/:245 give four items plus a test that a receipt older than 24 hours fails attestation. `security-sensitivity.md:39-43` (RP-7 H4) gives three different items and no staleness test. ADR-0.0.22 was not amended.

### Collisions added

- The word **"mode"**:
  - `resolve_adr_lane` falls back to `config.mode` when an ADR records no lane (`ledger.py:362-365`);
  - the MX marker's `mode` field is `mx` or `safe`;
  - `closeout_initiated.mode` is a separate field again.
- The word **"superseded"**:
  - `anchor_state = superseded`, where later commits changed recorded scope and the anchor is "superseded, not stale" (`ledger_semantics.py:239-241`);
  - an OBPI superseded by `gz obpi supersede`;
  - a REQ superseded by `supersedes`;
  - an ADR status `Superseded`.
- **Where lane is recorded.** The ledger books lane on `adr_created` (`ledger.py:1123-1124, 1174`), and the status surface resolves it from there (`resolve_adr_lane`). The frontmatter field `lane` is a second copy. No source names which of the two governs.

### Revised counts (117 terms, the 17 G-rows included)

| | Ruled | Sourced | Contradicted | Unsourced |
|---|---|---|---|---|
| Domain 7 (58) | 33 | 8 | 17 | 0 |
| Domain 8 (42) | 9 | 12 | 20 | 1 |
| G.1–G.17 (17) | 10 | 4 | 3 | 0 |
| **Total (117)** | **52** | **24** | **40** | **1** |

Two unsourced sub-items stand, as before: the feature package's identifier and the four ghost event names in 8.11. The contradiction list now runs to C47.

### Files read in full in this pass

| File | Lines |
|---|---|
| `src/gzkit/ledger.py` | 1646 |
| `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/ADR-0.0.22-security-sensitivity-doctrine.md` | 336 |
| `docs/governance/GovZero/audit-protocol.md` | 174 |
| `docs/governance/GovZero/obpi-decomposition-matrix.md` | 127 |
| The 577 matched rulings (`rulings-D/union.txt`) | 577 entries |
