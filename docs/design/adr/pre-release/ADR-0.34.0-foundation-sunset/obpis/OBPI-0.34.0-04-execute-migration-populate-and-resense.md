---
id: OBPI-0.34.0-04-execute-migration-populate-and-resense
parent: ADR-0.34.0-foundation-sunset
item: 4
lane: Heavy
sensitivity: security
status: Draft
---

# OBPI-0.34.0-04-execute-migration-populate-and-resense: Execute Migration, Populate, and Re-sense

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.34.0-foundation-sunset/ADR-0.34.0-foundation-sunset.md`
- **Checklist Item:** #4 — "execute-migration-populate-and-resense: Execute the sunset migration and verify the graph: gz adr demote the 23 genuinely-unstarted foundations to pool (body-preserving); populate the manifest with the ~51 grandfathered foundations; emit an attested foundation_grandfathered ledger event per entry (backfill-at-populate, Gate-5 witnessed, making the ledger complete-by-construction); run gz ontology resense + diff to confirm the corpus subgraph survives the 23-node ADR-0.0.X->ADR-pool.slug rename with no orphaned lineage or @covers/@surface edges. Scoped to the migration data mutation + its immediate ontology integrity check; status-index reconcile and gate-activation are OBPI-05. (heavy lane: migration action, new ledger event, ontology re-sense; sequences AFTER Sunset steps 1-4)."

**Status:** Draft

## Objective

Execute the migration DATA + graph-integrity half of the sunset as one atomic
action: demote the 23 genuinely-unstarted foundations (0/N OBPIs, including
`ADR-0.0.42` storybook and `ADR-0.0.1`) to pool (body-preserving), populate
`data/foundation_grandfather.json` with the ~51 grandfathered foundations, emit
one **attested** `foundation_grandfathered` ledger event per manifest entry
(backfill-at-populate, so the ledger is complete-by-construction), and confirm
the ontology corpus subgraph survives the 23-node `ADR-0.0.X` → `ADR-pool.slug`
rename with no orphaned lineage. "Done" is: the migration ran, the manifest is
populated, every grandfathered foundation carries a terminal Layer-2 event, and
the re-sense diff is clean.

> **Seam with OBPI-05:** the ACTIVATION half — reconciling the Layer-3 status
> index (`register-adrs` / `gz validate --adr-status-fresh`) and wiring the
> `--taxonomy` gate into `gz check` as the final act of the whole Sunset — lives
> in OBPI-0.34.0-05 (`activate-standing-taxonomy-gate`), which depends on this
> OBPI's populate + backfill. This brief stops at clean migration data + a clean
> graph.

> **Sequencing (binding — see § Sequencing):** this OBPI implements after
> OBPI-01/02/03 and after Sunset steps 1–4 make the tree terminal; OBPI-05
> follows it.

## Lane

**Heavy** — this OBPI performs a migration action (23 demotions), introduces a
new ledger event type (`foundation_grandfathered`), and re-senses the ontology
corpus subgraph. Those are runtime-contract / schema / observable-surface
changes, so heavy-lane Gates 3 (docs), 4 (BDD), and 5 (human attestation) all
apply.

**`sensitivity: security`** — the Allowed Paths overlap a registered surface in
`data/security_surfaces.json`: `src/gzkit/ledger_events.py` (`ledger_integrity`
— the append-only event factory). The auto-detect floor is fail-closed on
overlap (GHI #625), so this brief declares `security` and its Gate 5 fires the
extended security walkthrough.

## Allowed Paths

<!-- First backtick token on each bullet is the path; **CREATE** marks net-new files (existence-gate exempt, GHI #419). -->

- `src/gzkit/foundation/sunset_migrate.py` — **CREATE**: one-shot migration
  entrypoint in the existing `gzkit.foundation` package (run via
  `uv run python -m gzkit.foundation.sunset_migrate`; `--dry-run` / `--apply`,
  emits a JSON receipt — mirrors the `scripts/backfill_*.py` convention). Drives
  the demotions, manifest populate, and attested event emission. NOT a new `gz`
  CLI verb — a one-shot migration, per the ADR's "reuse existing surfaces, no
  new report verb" decision.
- `data/foundation_grandfather.json` — **CREATE** (created by OBPI-0.34.0-01;
  populated here): write the ~51 grandfathered IDENTITY-ONLY entries (id, title,
  semver, frozen_at; no lifecycle field).
- `src/gzkit/commands/adr_demote.py` — additive/read: the reused `gz adr demote`
  verb (foundation → pool). Read for round-trip semantics; correct only if
  REQ-01 exposes a body-preservation gap.
- `src/gzkit/events.py` — additive ONLY: add the `foundation_grandfathered`
  typed event model and its membership in the `TypedLedgerEvent` discriminated
  union; no existing variant touched.
- `src/gzkit/ledger_events.py` — additive ONLY: add the
  `foundation_grandfathered_event(...)` factory (sibling of
  `artifact_renamed_event`). **(security: `ledger_integrity`)**
- `tests/` — REQ-derived unit tests and the ledger/structural-validator proof
  for REQ-02.

## Denied Paths

- `src/gzkit/governance/trust_audits/taxonomy.py` — the closed-kind,
  manifest-integrity, and terminal-partition assertions are authored by
  OBPI-01 and OBPI-03; OBPI-04 only CONSUMES them.
- The `FoundationGrandfatherManifest` Pydantic model and golden-file guard test
  (OBPI-01 scope) — OBPI-04 populates the JSON the model validates, not the model.
- `gz plan create` / `gz adr promote` authoring-rejection code (OBPI-02 scope).
- The coupled-surface doc/skill sweep and ADR-0.0.18 retirement (OBPI-03 scope).
- `src/gzkit/quality.py` and `src/gzkit/commands/quality.py` — the `gz check`
  taxonomy-gate wiring and its `run_taxonomy_audit` runner are OBPI-05 scope.
- `gz register-adrs` / the Layer-3 status-index reconcile — OBPI-05 scope.
- `src/gzkit/cli/**` parser wiring for any new verb — the migration is a
  one-shot script, not a CLI surface addition.
- `.gzkit/ledger.jsonl` by hand — events are emitted only through the ledger
  API / factory. New dependencies, CI files, lockfiles.
- Any path not listed in Allowed Paths.

## Requirements (FAIL-CLOSED)

1. NEVER run the migration `--apply` before Sunset steps 1–4 are terminal
   (0.0.65 and 0.0.72 finished; 0.0.54, 0.0.64, 0.0.37 closed out). If any
   prerequisite foundation is still in Pending-with-attested-work limbo, print a
   BLOCKERS list and halt — a mid-limbo populate would make the terminal-partition
   gate false-red the instant it wires.
2. ALWAYS partition by Layer-2 ledger truth, never frontmatter: only the 23
   genuinely-unstarted (0/N net-OBPI) foundations demote; foundations holding
   attested work are grandfathered, never pooled.
3. ALWAYS emit exactly one attested `foundation_grandfathered` event per manifest
   entry at populate time (backfill-at-populate). For pre-ledger foundations the
   Gate-5 human attestation of this migration is the legitimate witness. NEVER
   hand-edit the ledger to synthesize these events.
4. NEVER store a lifecycle field in `data/foundation_grandfather.json` — entries
   are IDENTITY-ONLY (id, title, semver, frozen_at). Lifecycle is read live from
   the ledger; baking it into a Layer-1 file is the exact state-doctrine drift
   the 0.0.37 frontmatter-lie demonstrated.
5. ALWAYS run `gz ontology resense` after the demotions and confirm the diff
   introduces NO orphaned lineage or dangling `@covers`/`@surface` edges from the
   23-node rename.
6. NEVER reconcile the Layer-3 status index or wire the `--taxonomy` gate into
   `gz check` here — that ACTIVATION work is OBPI-05's scope and depends on this
   OBPI's populate + backfill having completed.
7. Work MUST stay inside the Allowed Paths; denied paths remain untouched.

> STOP-on-BLOCKERS: if any prerequisite closeout is missing, print a BLOCKERS
> list and halt before any write.

## Sequencing

This OBPI is gated by two ordering constraints; both must hold before `--apply`:

1. **Campaign order (Sunset steps 1–4).** The migration runs AFTER the tree is
   made terminal: finish `ADR-0.0.65` and `ADR-0.0.72`; close out `ADR-0.0.54`,
   `ADR-0.0.64`, and `ADR-0.0.37`. Until those land, foundations sit in
   Pending-with-attested-work limbo.
2. **Intra-ADR order.** OBPI-04 depends on OBPI-01 (manifest model + closed-kind
   / manifest-integrity assertions), OBPI-02 (authoring rejection), and OBPI-03
   (terminal-partition assertion + doctrine retirement + doc sweep). OBPI-04
   consumes all three.

**OBPI-05 follows this OBPI.** The status-index reconcile and the `--taxonomy`
gate-wire (the final act of the whole Sunset — wiring ≡ terminal tree, so it
lands green; anti-staging-flag doctrine forbids wiring earlier over limbo
foundations) are OBPI-05's scope, gated on this OBPI's populate + backfill.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision — quote the OBPI-04 line verbatim** into the
  Implementation Summary (REVIEW REFINEMENTS (b) backfill-at-populate, (c)
  ontology re-sense; SEQUENCING paragraph).
- [ ] Parent ADR § Intent — the partition-by-ledger-truth why-frame.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.34.0-foundation-sunset/ADR-0.34.0-foundation-sunset.md`

> **STOP:** If you cannot quote the parent ADR § Decision item this OBPI
> implements, STOP and re-read before touching Allowed Paths.

**Governance (read once, cache):**

- [ ] `AGENTS.md` / `CLAUDE.md` — Defect-fix routing, attestation, state-doctrine.
- [ ] `docs/governance/state-doctrine.md` — Layer-1/2/3 (manifest is L1,
  ledger is L2, status index is L3).
- [ ] `.claude/rules/security-sensitivity.md` — the security Gate-5 walkthrough.

**Context (sibling OBPIs — this OBPI consumes their output):**

- [ ] OBPI-01 — `FoundationGrandfatherManifest` model, closed-kind /
  manifest-integrity assertions, golden-file guard.
- [ ] OBPI-02 — authoring rejection.
- [ ] OBPI-03 — terminal-partition assertion (reads `foundation_grandfathered`),
  doctrine retirement, doc sweep.

**Existing Code (understand current state):**

- [ ] `src/gzkit/commands/adr_demote.py` — `_strip_frontmatter_keys` /
  `_set_frontmatter_value` body-preservation path (`_build_demote_plan` keeps the
  ADR body, strips `kind`/`semver`/`date`, rewrites `id`/`status`), and
  `_apply_demote` emitting `artifact_renamed` (reason `pool_demotion`). REQ-01's
  round-trip test asserts against this.
- [ ] `src/gzkit/events.py` — the `TypedLedgerEvent` discriminated-union
  definition (~line 744), `ArtifactRenamedEvent` as the model template, and
  `parse_typed_event`; the new `foundation_grandfathered` model joins the union.
- [ ] `src/gzkit/ledger_events.py` — the `artifact_renamed_event(...)` factory
  shape (returns `LedgerEvent`, appended via `Ledger.append`); the new
  `foundation_grandfathered_event(...)` factory mirrors it.
- [ ] `src/gzkit/commands/ontology.py` — `ontology_resense_cmd` and the
  `diff_snapshots` shape (`added_nodes`/`removed_nodes`/`added_edges`/`removed_edges`)
  that REQ-03's clean-diff assertion reads.
- [ ] `scripts/backfill_adr_taxonomy.py` — the one-shot `--dry-run` / `--apply`
  + `artifacts/receipts/` JSON-receipt convention the migration entrypoint
  follows.

**Prerequisites (check existence, STOP if missing):**

- [ ] The ~51-entry grandfather roster and the 23-entry demote roster are
  computed from the ledger (net-OBPI last-event-wins), not frontmatter.
- [ ] Sunset steps 1–4 confirmed terminal (see § Sequencing).

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from the three REQs below, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Runbook / status-index references reflect the migration outcome

### Gate 4: BDD (Heavy)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy + security)

- [ ] Human attestation recorded (this attestation IS the pre-ledger backfill
  witness for Requirement 3)
- [ ] Security walkthrough: `ledger_integrity` surface enumerated;
  `arb-step-security-scan-*` receipt confirmed

## Verification

<!-- Construction housekeeping — single-program, shell-less lines only.
     No &&, ||, |, ;, $(...), or redirects. -->

```bash
uv run gz validate --brief-headings
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --sensitivity
uv run mkdocs build --strict
```

## Demo

<!-- The yielded product — concrete, runnable demonstrations. -->

```bash
# 1. Round-trip a single demotion in dry-run — shows the ADR-0.0.42 storybook
#    foundation becomes ADR-pool.<slug> with its Intent/Decision body preserved.
uv run gz adr demote ADR-0.0.42 --ghi 520 --dry-run

# 2. Preview the full migration (no writes): the 23 demotions + the ~51
#    manifest entries + the 51 foundation_grandfathered events it would emit.
uv run python -m gzkit.foundation.sunset_migrate --dry-run

# 3. Apply the migration with the Gate-5 attestation as the backfill witness.
uv run python -m gzkit.foundation.sunset_migrate --apply --attestor "g0" --attestation "Foundation sunset migration — 23 demoted, 51 grandfathered."

# 4. Confirm the corpus subgraph survived the 23-node rename — clean diff,
#    no orphaned lineage or dangling @covers/@surface edges.
uv run gz ontology resense --json
```

> The activation demo — `register-adrs`, `gz validate --taxonomy` /
> `--adr-status-fresh`, and `gz check --json` showing the `"ADR taxonomy"`
> step — lives in OBPI-0.34.0-05.

## Acceptance Criteria

<!-- REQ-<semver>-<obpi_item>-<criterion_index> [kind] per ADR-0.0.59. -->

- [ ] REQ-0.34.0-04-01 **[BEHAVIOR]**: `gz adr demote` moves a genuinely-unstarted
  foundation to pool while PRESERVING its Intent/Decision content — round-trip:
  the resulting `ADR-pool.<slug>` file retains the original ADR body verbatim
  (only `kind`/`semver`/`date` stripped and `id`/`status` rewritten). Proof: a
  `@covers(REQ-0.34.0-04-01)` unit test demoting a fixture foundation and
  asserting body equality.
- [ ] REQ-0.34.0-04-02 **[SUPPORT]**: each grandfathered foundation receives one
  attested `foundation_grandfathered` ledger event at populate time. Proof
  channel: **ledger event + structural validator** (a `foundation_grandfathered`
  event exists in `.gzkit/ledger.jsonl` for every `data/foundation_grandfather.json`
  entry, one-to-one, and the terminal-partition/manifest-coherence validator
  confirms the bijection) — NOT a `@covers` test.
- [ ] REQ-0.34.0-04-03 **[BEHAVIOR]**: after the migration, `gz ontology resense`
  diff shows no orphaned lineage introduced by the 23-node rename — no dangling
  `@covers`/`@surface` edges and no removed corpus node left without a successor.
  Proof: a `@covers(REQ-0.34.0-04-03)` test asserting the re-sense diff over the
  renamed set is clean.

> The status-index freshness + `--taxonomy`-in-`gz check` criteria moved to
> OBPI-0.34.0-05 (`activate-standing-taxonomy-gate`) — REQ-0.34.0-05-01/02/03.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from the three REQs
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now documented
- [ ] **Key Proof:** One concrete usage example included
- [ ] **Gate 3/4 (Heavy):** Docs build, BDD scenarios pass
- [ ] **Gate 5 (Human + security):** Attestation recorded; security walkthrough done
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md`
> section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here (this attestation is the pre-ledger backfill witness)
```

### Value Narrative

<!-- Before: 23 foundations rotting in limbo; the ledger incomplete for
     pre-ledger foundations (no terminal Layer-2 event). After: 23 pooled
     (bodies preserved), ~51 grandfathered with attested terminal Layer-2
     events, and the ontology corpus subgraph intact across the rename. The
     activation half (status-index reconcile + permanent gz check gate) lands
     in OBPI-05. -->

### Key Proof

<!-- One concrete before/after: a demoted foundation's ADR-pool.<slug> retains
     its Intent/Decision body verbatim, and `gz ontology resense --json` shows a
     clean diff after the 23-node rename. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- One bullet per issue for traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
