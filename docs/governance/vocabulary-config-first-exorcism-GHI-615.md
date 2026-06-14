# The Vocabulary Config-First Exorcism — Remediation Rites (GHI #615)

> **Status:** PREPARED — NOT YET EXECUTED. This document is the campaign spec
> ("the rites"). No vocabulary mutation lands until the § Open Decisions are
> ratified by the operator. Authored under emergency direction 2026-06-13.
>
> **Tracking:** GHI #615. Top of the build-to-1.0 campaign.
> **Canon mirrored:** airlineops Config-First doctrine (their GHI-75).
> **Severity:** Foundational. The disease touches every structured-document
> surface in gzkit.

> **Amendment (operator-ratified, 2026-06-14) — Barcode Projection supersedes Config-First-only.**
> The remediation target is enlarged from "central vocabulary config so authored
> frontmatter validates" to **frontmatter-as-projection**: structured-document
> frontmatter is a Layer-3 *render* of the Layer-2 ledger state machine, never
> hand-authored. This amendment supersedes the framing of § 4, inverts § 5
> Phase 8, and resolves § 6.
>
> Operator ruling (verbatim, 2026-06-13): *"frontmatter must ONLY be a projection
> from the ledger and ONLY mechanically rendered. think of frontmatter as being
> the result of reading a barcode/qrcode. our statemachine should be the only
> thing that matters. perhaps we need a data (json) sidecar to ensure that these
> are ONLY projection rendered. it is a FOUL to have model touch the frontmatter
> ad hoc."*
>
> **Ratified architecture (Decision A — barcode-everything + sidecar):**
> - Each rendered frontmatter field is either **ledger-projected** (`status` —
>   rendered live from the ledger at render time, never cached) or an
>   **authorship fact** (`id`, `parent`, `kind`, `lane`, `tasks`) held in a
>   committed, co-located JSON **sidecar** (`<artifact>.gz.json`).
> - Render = merge(sidecar authorship + live ledger-projected status). The
>   markdown **body** stays authored; only the frontmatter fence is rendered.
> - **One writer.** Frontmatter is emitted only through a skill-gated verb; a
>   model writing it ad hoc is a foul, blocked fail-closed by `gz validate
>   --frontmatter-projection` (re-render + byte-compare, the
>   `--invariant-coherence` technique).
> - Migration reads existing frontmatter exactly once (ledger wins on conflict),
>   dry-run + per-file report, idempotent.
>
> **Product tree, stateful at every node (F1 = ii).** Operator ruling (verbatim,
> 2026-06-13): *"each major release would have a PRD, which then suggests a
> contitution would be the true root of the product 'tree.' … if we need
> PRD-per-major release (which I favor), then (ii) is closer to true."*
> Constitution (root) → PRD (per major release) → ADR → OBPI; lifecycle state
> machines are added for **PRD and Constitution** so all four statuses are ledger
> projections.
>
> **§ 6 Open Decisions — resolution.** Q1 ratified: **TitleCase frontmatter /
> snake_case ledger**, `status_vocab` mapping between layers, machine-consistency
> enforced by the § 4.3 lattice plus a new frontmatter↔ledger totality guard.
> Q2–Q4 demote to *render-target settings* (frontmatter is no longer a writable
> surface that can drift) and are fixed in the barcode ADR. **§ 4 and § 5 Phase 8
> invert:** the goal is no longer "parse frontmatter strictly as source" but
> "stop reading frontmatter as source — render it."
>
> **Dependencies (sequencing ruling "a").** This remediation now sits at the tail
> of a chain — **CMS / progressive disclosure (ADR-0.0.37) → Firewall foundation
> ADR → barcode + lifecycle doctrine.** Nothing here mutates until the CMS is
> terminal and the firewall is booked. Tracked across GHI #615 (vocabulary
> substrate) and GHI #607 (firewall).

> **Amendment (operator-ratified, 2026-06-14) — Constitution/PRD definitions, stability-gradient ordering, charter-projection (iii).**
>
> Operator analogy (verbatim): a Constitution *"stands in place longer than the
> advance of major versions of any given product"* (cf. Anthropic's constitution,
> <https://www.anthropic.com/constitution>, which governs across model
> generations). **Endurance is the defining property.**
>
> **Definitions.**
> - **Constitution** — the enduring normative charter (principles + invariants),
>   amended only deliberately, persisting across major versions; the **root
>   because it is the slowest-changing layer**. Cadence: *amendment*. The
>   `gz constitute` schema already encodes its shape
>   (`Principles / Rules / Exceptions / Amendments`) — built for endurance, never
>   instantiated.
> - **PRD** — the per-major-release product requirements; a **child of the
>   Constitution**, superseded each major release. Cadence: *per major version*
>   (confirmed by `PRD-GZKIT-1.0.0`'s semver root).
>
> **Ordering principle (resolves the backwards spine).** The tree is ordered by
> **rate of change**: Constitution (amendment) → PRD (release) → ADR (feature) →
> OBPI (increment) — most-enduring roots, most-volatile leaves. The legacy
> `PRD → Constitution` (~12 surfaces incl. the `agents.md` template, `tests.md`,
> `validate_commit_trailers.py`, the campaign) **inverts the gradient and is
> backwards**; correction is owned by the product-tree/lifecycle ADR (re-render,
> never hand-edit). This grounds F1=ii: lifecycles differ because *cadences*
> differ (Constitution: Draft→Review→Ratified→**Amended**→Superseded; PRD:
> Draft→Review→Approved→Superseded-per-release).
>
> **Constitution ↔ invariant-registry = (iii) couple-as-projection.** The
> Constitution charter is **authored** (human-ratified, amendment-gated); the
> constitutional-invariant registry (ADR-0.0.37 CMS) + the rendered AGENTS.md are
> its **mechanical projection** — the barcode doctrine generalized to the root.
> *Like Anthropic's:* charter authored, behavior projected.
>
> **As-built comprehension (2026-06-14, observed).** The tree is operationally
> **PRD-rooted**: one PRD (`PRD-GZKIT-1.0.0`, Draft), **73 ADRs
> `parent: PRD-GZKIT-1.0.0`**, **no Constitution artifact instantiated**, no
> PRD↔Constitution linkage. Making Constitution the root is therefore **net-new
> construction** — instantiate the charter, wire `PRD.parent → Constitution`,
> bridge the 73 ADRs, add the lifecycles — owned by the product-tree/lifecycle
> ADR, not a string edit.

---

## 0. The one-sentence diagnosis

gzkit has **no central configuration for its enumerated governance
vocabularies** (OBPI/ADR/PRD/Constitution `status`, `lane`); the values were
copied verbatim into ~9 Pydantic models, 2 contradictory JSON schemas, 600
brief frontmatters, the ADR corpus, authoring tools, skills, validators, and
docs — each copy free to drift — so **no two surfaces agree on the same
vocabulary in the same casing**. This is a Config-First violation: the
single-source-of-truth that airlineops has, gzkit's extraction dropped.

## 1. Why this is terminal-if-unfixed

Every governance guarantee gzkit makes rests on parsing structured documents.
If the vocabulary those documents use is not pinned to one source, then:

- Validators pass documents that are actually drifted (false negatives) and
  block valid ones (false positives — the `req_count=-8` and lane-casing
  cascades observed 2026-06-13).
- "Schema validation" is theater: the schemas disagree with each other and
  with the corpus, so conformance to one means nonconformance to another.
- Authoring tools mint fresh drift on every new document.
- The anti-vibing mantra is structurally defeated at the canon layer: the
  governance surface itself is the slop it exists to prevent.

## 2. The evidence (full blast radius, file:line)

### 2.1 The vocabulary is copied, never sourced

| Surface | Location | `lane` values | `status` values |
|---|---|---|---|
| Pydantic — OBPI | `src/gzkit/core/models.py:56-69` | `lite, heavy, Lite, Heavy` | `Draft, Active, Completed, Abandoned, pending, in_progress, completed, attested_completed, validated, drift, withdrawn` (11) |
| Pydantic — ADR | `src/gzkit/core/models.py:29-42` | `lite, heavy` | `Pool, Pending, Draft, Proposed, Accepted, Completed, Validated, Superseded, Deprecated` (9) |
| Pydantic — PRD | `src/gzkit/core/models.py:79` | — | `Draft, Review, Approved, Superseded` |
| Pydantic — Constitution | `src/gzkit/core/models.py:90` | — | `Draft, Review, Ratified, Superseded` |
| Pydantic — BriefStructure | `src/gzkit/governance/brief_structure.py:40-42` | `Lite, Heavy` | `Draft, Validated, Completed` (3) |
| JSON schema — obpi.json | `src/gzkit/schemas/obpi.json:27-48` | `lite, heavy, Lite, Heavy` | 11 values (different ordering) |
| JSON schema — obpi_brief_structure.json | `src/gzkit/schemas/obpi_brief_structure.json:20-29` | `Lite, Heavy` | `Draft, Validated, Completed` (3) |
| Input-tolerance map | `src/gzkit/governance/status_vocab.py:32-56` | — | **21 keys**, 5 casing conventions, rampant synonyms |
| Ledger states | `src/gzkit/ledger.py:60-69` | — | `pending, in_progress, completed, attested_completed, validated, drift, withdrawn` |

**Contradictions proven:**
- The two OBPI schemas (`obpi.json` 11 values vs `obpi_brief_structure.json` 3
  values) **disagree with each other** about the same document type.
- `BriefStructure.status` accepts `Validated` — used by **zero** briefs — and
  rejects `attested_completed` (198 briefs), `Abandoned` (9), `in_progress` (1).
- PRD says `Approved`; Constitution says `Ratified` — divergent terms for the
  same lifecycle position.

### 2.2 The synonym soup (`STATUS_VOCAB_MAPPING`, 21 keys → 8 ledger terms)

`In Progress` = `In-Progress` = `in_progress`; `Abandoned` = `Withdrawn` =
`Superseded` = `Deprecated` = `archived`; casings mixed across TitleCase,
snake_case, lowercase, hyphenated, and space-separated. This map is legitimate
as an **input-tolerance** layer for legacy migration — but it is **not** a
canonical vocabulary, and binding schemas to its keys (attempted and reverted
2026-06-13) launders the slop rather than removing it.

### 2.3 The corpus drift (measured 2026-06-13, 600 briefs)

```
status:  Completed 239 | attested_completed 198 | Draft 145 | Abandoned 9 | in_progress 1
lane:    Heavy 410 | Lite 98 | heavy 65 | lite 19        (84 briefs lowercase)
```

Brief structured-frontmatter adoption: **3 of 600** parse as `BriefStructure`;
**597 fall back to `LegacyBriefShape`** regex-scraping (`parse_brief`,
`src/gzkit/governance/brief_structure.py:100-128`, defaults `strict=False`,
never called strict).

### 2.4 ADR-frontmatter parser sprawl (same disease, second document type)

~14 modules re-parse ADR frontmatter by hand instead of through the one
`AdrFrontmatter` model / `adr.json`: `src/gzkit/sync.py`,
`governance/adr_status_index.py`, `governance/trust_audits/taxonomy.py`,
`governance/trust_audits/sensitivity.py`,
`governance/trust_audits/lock_handoff_coupling.py`, `commands/init_cmd.py`,
`commands/validate_cmd.py`, `foundation/rubric.py`, `justify/parser.py`,
`skills/__init__.py`, `skills_audit.py`, `skills_mirror.py`, `triangle.py`,
`chores/eval_feedback_cluster_lib.py`.

### 2.5 What is already sound (do not "fix" these)

- The model↔schema drift-guard in `tests/test_schemas.py` **works** — it caught
  the speculative divergence on 2026-06-13. The enforcement bones exist; they
  just guard hardcoded copies instead of a single source.
- `tests/test_schemas.py` has a Literal-vs-enum binding check per model.
- `personas` and `rules` already parse schema-first correctly
  (`models/persona.py`, `rules/__init__.py`).
- The 60+ `gz validate` scopes are real (no theater stubs found).
- `status_vocab.canonicalize_status()` is the right input-normalization seam.

## 3. The canon to mirror — airlineops Config-First (their GHI-75)

airlineops solved exactly this. The proven shape (`../airlineops/src/opsdev/lib/adr.py:59-92`,
`../airlineops/tests/policy/test_adr_status_config_first.py`):

1. **Config is the source.** Vocabulary lives in settings under
   `governance.adr_statuses`, loaded via `load_settings()`.
2. **Loader with frozen fallback.**
   ```python
   _FALLBACK_STATUSES = frozenset({"Pool","Draft","Proposed","Accepted",
                                   "Completed","Validated","Superseded","Abandoned"})
   @lru_cache(maxsize=1)
   def _get_allowed_statuses() -> frozenset[str]:
       try:
           return frozenset(load_settings().governance.adr_statuses)
       except (...): return _FALLBACK_STATUSES
   ```
3. **AST policy test** (`test_adr_status_config_first.py`) fails closed if
   `ALLOWED_STATUSES` is a hardcoded set literal, if `_get_allowed_statuses`
   is absent, or if validators reference the constant instead of the loader.
4. Note airlineops' canonical ADR vocabulary is **8 clean TitleCase terms, no
   synonyms, one casing** — the antithesis of gzkit's 21-key soup.

## 4. Target architecture for gzkit

> One song, one key, one room. Every surface DERIVES; none copies.

### 4.1 The single source of truth (new)

`src/gzkit/governance/vocabulary.py` — the ONLY place vocabulary literals live:

```python
# Canonical, clean, no-synonym, single-casing vocabularies.
# Per-artifact because lifecycles genuinely differ (ADR != OBPI != PRD).
OBPI_LANES: frozenset[str]            # e.g. {"Lite", "Heavy"}
OBPI_STATUSES: frozenset[str]         # see § Open Decisions
ADR_LANES: frozenset[str]
ADR_STATUSES: frozenset[str]
PRD_STATUSES: frozenset[str]
CONSTITUTION_STATUSES: frozenset[str]
```

Backed by config (`config/governance-vocabulary.json` or the existing settings
surface) loaded via cached accessors with frozen fallbacks — airlineops shape.
`status_vocab.STATUS_VOCAB_MAPPING` is retained ONLY as the legacy→canonical
**input** map and MUST map exclusively onto these canonical sets (a test
asserts every mapping value lands in the canonical set).

### 4.2 Everyone derives

| Consumer class | Binding requirement |
|---|---|
| Pydantic models (`core/models.py`, `brief_structure.py`) | Field validators call the loader; no `Literal[...]` vocabulary copies |
| JSON schemas (`obpi.json`, `obpi_brief_structure.json`, `adr.json`, `prd.json`, `constitution.json`) | `enum` generated from the source at build/test time; drift-guard test fails on divergence |
| Authoring tools (`gz plan`, `gz obpi specify`, `gz prd`, `gz constitute`, scaffolders) | Write only canonical terms; never a literal |
| Validators / auditors (`validate_cmd`, `trust_audits/*`, `adr_audit`, `gates`, `frontmatter_coherence`) | Read the loader; the ~14 hand parsers route through the model |
| Skills (`.gzkit/skills/**`) | Reference the canonical vocabulary doc; no inline value lists |
| Docs (`docs/user/**`, `docs/governance/**`, runbooks) | Cite the canonical doc; examples use canonical terms only |
| Corpus (600 briefs + ADRs + PRDs) | Normalized to canonical terms via one migration pass |

### 4.3 The enforcement lattice (so it stays fixed)

1. **Config-first AST policy test** (mirror airlineops): fails if any module
   hardcodes a vocabulary set/Literal instead of deriving from the source.
2. **Schema↔source drift-guard**: every JSON `enum` == the canonical source.
3. **Model↔schema drift-guard**: extend the existing `tests/test_schemas.py`
   check (already sound) to assert against the source, not copies.
4. **Corpus conformance validator** `gz validate --vocabulary`: every brief/
   ADR/PRD frontmatter term ∈ canonical set; wired into `gz check`, fail-closed.
5. **Authoring-output test**: scaffolders' emitted frontmatter ∈ canonical set.
6. **Docs/skills lint**: no inline vocabulary lists outside the canonical doc.

## 5. The rites — phased execution sequence (each phase green before the next)

- **Phase 0 — Ratify vocabularies** (§ Open Decisions). Blocks all else.
- **Phase 1 — Source of truth.** Add `governance/vocabulary.py` + config +
  loaders + frozen fallbacks + the Config-First AST policy test. Additive;
  green; nothing bound yet.
- **Phase 2 — Bind the models.** Replace every `Literal[...]` vocabulary copy
  in `core/models.py` + `brief_structure.py` with loader-backed validators.
  Extend `tests/test_schemas.py` to assert against the source.
- **Phase 3 — Bind the schemas.** Generate the `enum`s from the source;
  add the schema↔source drift-guard. Kills the obpi.json/obpi_brief_structure
  contradiction.
- **Phase 4 — Normalize the corpus.** One migration pass: 600 briefs + ADRs +
  PRDs → canonical terms (status + lane). Idempotent; reported per-file;
  dry-run first.
- **Phase 5 — `gz validate --vocabulary`** corpus-conformance scope, wired into
  `gz check`, fail-closed.
- **Phase 6 — Authoring tools.** Every scaffolder/authoring verb writes only
  canonical terms; add authoring-output tests.
- **Phase 7 — Parser-sprawl consolidation.** Route the ~14 ADR-frontmatter
  hand-parsers and the OBPI trust-audit regexes through the models.
- **Phase 8 — Flip `parse_brief` to enforce** + migrate the 597 legacy briefs
  to structured frontmatter (or adopt a robust single body-parser → validated
  model; decide in Phase 0).
- **Phase 9 — Skills + docs.** Canonical-vocabulary doc authored; skills/docs
  reference it; inline-list lint enabled.
- **Phase 10 — Close GHI #615** citing the landed commits + the enforcement
  lattice as the durable destination.

## 6. Open Decisions (operator ratification required — Phase 0 gate)

These are the ONLY judgment calls; everything downstream is mechanical once set.

1. **Casing convention.** TitleCase human terms (airlineops precedent:
   `Draft, Completed, …`) vs. lowercase snake_case mirroring the ledger
   (`pending, completed, …`). *Recommendation: TitleCase for frontmatter
   (human-facing, airlineops-aligned); the ledger keeps its snake_case
   states; `status_vocab` maps between them.*
2. **OBPI status set.** Proposed canonical (5):
   `{Draft, Active, Completed, Abandoned, Drift}` — collapses
   `attested_completed`/`validated`→`Completed` in **frontmatter** (the ledger
   retains the attestation distinction as Layer-2 truth per state-doctrine).
   *Alternative:* keep `Attested` distinct in frontmatter (6 terms).
3. **ADR status set.** Adopt airlineops' 8 verbatim:
   `{Pool, Draft, Proposed, Accepted, Completed, Validated, Superseded, Abandoned}`.
4. **Lane casing.** Proposed: TitleCase `{Lite, Heavy}` for both ADR and OBPI
   (unifies the current ADR-lowercase / OBPI-mixed split). *Confirm or keep
   ADR lowercase.*
5. **PRD vs Constitution status** unification (`Approved` vs `Ratified`):
   keep distinct (different artifacts) or unify.
6. **Brief enforcement model** (Phase 8): migrate 597 briefs to structured
   frontmatter, OR make `parse_brief` build+validate the model from a single
   robust body parser (no 597-file frontmatter migration). *Recommendation:
   the robust-parser path — lower blast radius, same schema guarantee.*

## 7. Safety / rollback

- No phase mutates the corpus before Phases 1–3 land the source + guards.
- Every phase is independently revertable; the migration (Phase 4) is dry-run
  first with a per-file report.
- The Config-First AST test (Phase 1) prevents regression to hardcoded copies
  for all future work, including during the campaign itself.

## 8. Acceptance — "the exorcism is complete" when

1. `grep` finds **zero** vocabulary set/Literal copies outside
   `governance/vocabulary.py` (enforced by the AST policy test).
2. All JSON `enum`s equal the source (drift-guard green).
3. `gz validate --vocabulary` passes over the full corpus and is in `gz check`.
4. Authoring tools emit only canonical terms (authoring-output tests green).
5. `parse_brief` enforces; no `LegacyBriefShape` fallback in the gate path.
6. The ~14 ADR-frontmatter hand-parsers are gone (routed through the model).
7. The canonical-vocabulary doc is the single cited reference in skills + docs.
8. `uv run gz check` is green end-to-end.

---

*Prepared 2026-06-13 under GHI #615. Awaiting operator ratification of § 6
before Phase 1 begins. Nothing in this campaign executes until the rites are
read and the vocabularies are set.*
