---
id: OBPI-0.35.0-07-content-land-orchestrator
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 7
lane: Heavy
status: Active
allowlist:
- src/gzkit/commands/content/land.py
- src/gzkit/commands/content/__init__.py
- src/gzkit/content/landing.py
- src/gzkit/content/rendition_store.py
- src/gzkit/events.py
- src/gzkit/schemas/ledger.json
- config/doc-coverage.json
- tests/content/test_tui_affordances.py
- tests/cli/test_attestor_default.py
- src/gzkit/content/corpus_store.py
- src/gzkit/content/retention.py
- .gitignore
- src/gzkit/governance/events.py
- src/gzkit/ontology/corpus.py
- tests/test_schemas.py
- tests/content/test_landing.py
- tests/commands/test_content_land.py
- features/content_land.feature
- features/steps/content_land_steps.py
- docs/user/manpages/content.md
- docs/user/runbook.md
- docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-07-content-land-orchestrator.md
reqs:
- REQ-0.35.0-07-01
- REQ-0.35.0-07-02
- REQ-0.35.0-07-03
- REQ-0.35.0-07-04
- REQ-0.35.0-07-05
- REQ-0.35.0-07-06
- REQ-0.35.0-07-07
- REQ-0.35.0-07-08
- REQ-0.35.0-07-09
- REQ-0.35.0-07-10
verification:
- uv run -m unittest tests.content.test_landing tests.commands.test_content_land
- uv run -m behave features/content_land.feature
- uv run gz lint
- uv run gz typecheck
- uv run gz test
- uv run gz validate --documents
- uv run gz validate --req-kind-discipline
- uv run gz validate --rendition-freshness
- uv run gz cli audit
- uv run mkdocs build --strict
tasks:
  - TASK-0.35.0-07-01-01
  - TASK-0.35.0-07-02-01
  - TASK-0.35.0-07-03-01
  - TASK-0.35.0-07-04-01
  - TASK-0.35.0-07-05-01
  - TASK-0.35.0-07-06-01
  - TASK-0.35.0-07-07-01
  - TASK-0.35.0-07-08-01
  - TASK-0.35.0-07-09-01
  - TASK-0.35.0-07-10-01
---

# OBPI-0.35.0-07-content-land-orchestrator: Content Land Orchestrator

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
<!-- gz-validate-skip: command-shape -->
- **Checklist Item:** #7 - "gz content land &lt;surface&gt; orchestrator -- journaled multi-consumer publication with per-file atomic replacement, single corpus attestation on the corpus delta, shared `landing_id`, landing state file written first and cleared last, `--status` and non-destructive resume that does NOT re-prompt for attestation"

**Status:** Draft

## Objective

Ship gz content land &lt;surface&gt; — one corpus-attested, journaled, resumable landing of the corpus across every consumer of a surface: a landing state file written before the first byte and cleared last, one corpus attestation on the corpus delta covering N consumers under a shared `landing_id`, a `--status` that classifies consumers by corpus fingerprint rather than mtime, and a non-destructive resume that never re-prompts for attestation.

> **AMENDED 2026-08-18 (operator-ruled, GHI #822): this brief's content-surface
> attestation is renamed from "Gate 5" to CORPUS ATTESTATION.** Gate 5 names
> OBPI/ADR completion attestation (`ADR-0.0.36`) and nothing else; a build step
> wearing that name is the collision the transit/exchange/handoff fence forbids
> (operator ruling 2026-08-17, `AGENTS.md` § Operator Doctrine). The noun is
> `corpus`, not `rendition`, because the same ruling puts the attestable subject on
> the corpus and holds a rendition to be a Layer-3 derived view, "never the thing
> attested." Parent ADR § Decision carries the governing amendment. This brief's own
> `### Gate 5 (Human)` gate-covenant sections are UNCHANGED — those are the genuine
> Gate 5, on this OBPI's completion. Naming only; no REQ semantics change.

**Dependency order:** 07 depends on 05 (pure candidate/lineage generator), 06 (owned-lineage verification), 09 (active route resolution) and 14 (the retention gate, operator-sequenced before 07 on 2026-09-24; ADR BI-10), plus the ledger atomicity/durability corrections tracked by GHI #952/#953 before implementation begins. Per § Scope Minimization, 07 is NOT cuttable — without the generator and `land`, OBPIs 01-03 are schema with no consumer. See the testability-ceiling note in Requirements: the parent ADR's Decomposition Scorecard flagged this item up front.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/commands/content/land.py` — the orchestrator command **CREATE**
- `src/gzkit/commands/content/__init__.py` — content-group parser registration for land only
- `src/gzkit/content/landing.py` — landing state file model, staged publication, journal, resume and status logic **CREATE**
- `src/gzkit/content/rendition_store.py` — `landing_id` on the provenance sidecar, additively only
- `src/gzkit/events.py` — typed landing event model (`ledger_events.py` is a registered `ledger_integrity` security surface and is NOT touched; the event is appended with `ledger_row(model)` — ruling 2026-09-27)
- `src/gzkit/schemas/ledger.json` — the landing event's schema entry
- `src/gzkit/governance/events.py` — the landing event emitter
- `src/gzkit/ontology/corpus.py` — coupled consumer: every new ledger event type is dispositioned here (ruling 2026-09-27)
- `tests/test_schemas.py` — coupled consumer: the per-event model map (ruling 2026-09-27)
- `config/doc-coverage.json` — new-verb coupled consumer
- `tests/content/test_tui_affordances.py` — new-verb coupled consumer
- `tests/cli/test_attestor_default.py` — new-verb coupled consumer: `gz content land` defaults `--attestor` from config (ruling 2026-09-27)
- `src/gzkit/content/corpus_store.py` — READ-ONLY fixture import for the covering tests; never modified (ruling 2026-09-27)
- `src/gzkit/content/retention.py` — READ-ONLY import (retention map model and sidecar path); never modified (ruling 2026-09-27)
- `.gitignore` — ignore the landing lock, journal and staging sidecars by name (ruling 2026-09-27)
- `tests/content/test_landing.py` — covering tests **CREATE**
- `tests/commands/test_content_land.py` — covering tests **CREATE**
- `features/content_land.feature` — Gate 4 scenarios **CREATE**
- `features/steps/content_land_steps.py` — Gate 4 step definitions **CREATE**
- `docs/user/manpages/content.md` — the `land` contract and the named rollback
- `docs/user/runbook.md` — the operator flow and the named rollback
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-07-content-land-orchestrator.md` — this brief's evidence sections

## Denied Paths

- `src/gzkit/content/composer.py`, `src/gzkit/content/lineage.py` — the generator is OBPI-0.35.0-05 and is invoked, never modified
- `src/gzkit/content/ownership.py` — OBPI-0.35.0-04, read-only
- `src/gzkit/governance/trust_audits/**` — OBPI-0.35.0-06
- `src/gzkit/sync_surfaces.py`, `src/gzkit/governance/compose.py` — playback wiring is OBPI-0.35.0-09
- `src/gzkit/commands/content/remember.py` — OBPI-0.35.0-08
- New dependencies, CI files, lockfiles
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. Implement one landing transaction state machine with three verification groups: preflight/staging, durable publication/completion, and status/resume/recovery. Argument shape and attestation are preflight invariants; they are not separate products. No automatic rollback command, storage generation redesign, parallel publishers or per-consumer repudiation is added. Preserve all ten REQs.
2. ALWAYS require the positional `<surface>`. It is required, matching `compose` and `commit`; there is no default surface.
3. ALWAYS write the landing state file BEFORE the first byte of the first consumer and clear it LAST, after the final consumer's sidecar. It MUST carry the `landing_id`, the intended consumer set, and the corpus fingerprint. Sidecars are written alongside their renditions, so a crash after `claude.md` and before `codex.md` otherwise leaves the two consumers with NO common record that a landing was in flight (`DESIGN_FORCING_FUNCTIONS.md` § 5).
4. RATIFIED PUBLICATION CONTRACT — operator approval recorded below. Stage and verify every target before publication; any staging failure leaves committed artifacts unchanged. Publication uses atomic replacement per file, not an atomic snapshot of the entire set. A crash or replace failure may leave mixed artifacts; retain the journal, refuse successful completion and expose the actual verified state for resume. Never claim sequential renames provide whole-set atomic visibility.
5. ALWAYS take exactly ONE corpus attestation, on the CORPUS DELTA, covering all N consumers. Empty attestor/text is refused only for a new corpus delta without reusable attestation evidence. Unchanged-corpus re-render and verified resume reuse the existing evidence; missing or corrupt evidence is not proof of unchanged canon. Each consumer's sidecar records the same `attestation_text` and the same `landing_id`. The justification is determinism: generation over owned sections is reproducible and renditions are Layer-3 derived views, so N attestations would demand N human judgments where only one exists.
6. NAMED HONESTLY, NOT ELIDED: a single attestation over N consumers is STRUCTURALLY A BUNDLE — the shape AGENTS.md § MAKE LLM STOCHASTIC VIBES INERT names as a vibing signature — and it has no per-consumer repudiation story, because ADR-0.0.71 gives `repudiate` at OBPI granularity (ADR § Consequences Negative #3). The shared `landing_id` in every sidecar is what makes the bundle at least legible; do not implement anything that obscures it.
7. NEVER classify consumer state by mtime comparison. `--status <landing_id>` MUST classify each consumer as on the new corpus fingerprint, on the old one, or indeterminate, by comparing FINGERPRINTS. Mtime comparison is precisely the fake witness `rendition_floor_coherence.py:1-9` was filed against; do not hand the operator the discredited instrument.
8. ALWAYS make resume non-destructive. Re-running `land` against a set in which some consumers already landed MUST leave those consumers byte-unchanged. An interrupted publication remains incomplete; files already verified against their target hashes are not rewritten.
9. NEVER re-prompt for attestation on resume. The corpus attestation is on the corpus delta, not on the write; resume reuses the recorded `attestation_text` and `landing_id`. If resume re-prompts, the operator will `--force` past it at 2am and the attestation becomes theater — the exact failure AGENTS.md names.
10. ALWAYS name the rollback in the operator docs. Committed renditions are single files at `.gzkit/renditions/<surface>/<consumer>.md` with NO prior-version retention, so "put it back" means restoring the surface's whole artifact set from git: `git restore --source=<known-good-revision> --staged --worktree -- .gzkit/renditions/<surface>/`, which, unlike `git checkout <revision> -- <dir>`, also removes artifacts the landing added. That is acceptable, but it MUST be stated rather than left for the operator to discover at 2am. AMENDED 2026-09-27 (operator ruling, option chosen verbatim: "Name restore, amend REQ (Recommended)"): this read "means `git checkout`"; both Stage-2 reviewers showed, and the orchestrator reproduced in a scratch repository, that a pathspec checkout leaves newer lineage and retention sidecars beside restored renditions.
11. ALWAYS emit three-part recovery prose on every fail-closed exit and on every indeterminate `--status` verdict per `.claude/rules/guardrail-feedback-prose.md`.
12. ALWAYS pass every consumer's candidate through the OBPI-0.35.0-14 retention gate (`enforce_retention`, the complete gate — never `validate_retention` alone) before anything is written (ADR BI-10). `land` accepts a repeatable `--retention-map PATH`; each map binds to its consumer through the existing map-target check. A consumer whose candidate removes a block of its prior committed rendition without a valid map refuses the WHOLE landing at preflight, writing nothing. DROPPED condition ids are checked against the `--attestation-text` supplied on THIS invocation. A validated map is published as `<consumer>.retention.json`, staged, journaled and hashed with the consumer's other artifacts; a consumer with no removed block has any stale retention sidecar removed within the same journaled publication. Resume reuses the staged retention sidecar and never re-runs the gate against new attestation text (Requirement 9). Operator ruling 2026-09-27, option chosen: "Repeatable map (Recommended)".
13. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Publication Amendment (Ratified)

**Ratified 2026-09-05 (local), operator g0.** Approval, verbatim: **"approve the 07 work"**.
The approval accepts the reviewed journaled per-file publication contract and resolves the
remaining design-review condition. It does not assert implementation completion or waive
the predecessor and ledger prerequisites. The original Requirement 4 said:
> ALWAYS write atomically across the whole consumer set — temp-then-rename for every consumer, with no rename performed until every consumer's bytes are staged. A failure at consumer 2 of 3 MUST leave all three committed renditions unmodified.

REQ-05 simultaneously required:
> Given a landing interrupted after the first consumer, when the filesystem is inspected, then the landing state file EXISTS

Sequential renames cannot satisfy whole-set atomic visibility. The approved contract uses
journaled per-file publication because it preserves the existing file layout and the
explicitly requested status/resume behavior. The alternative is atomic activation of an
immutable generation, requiring a new storage/read protocol beyond these declared paths.
This amendment is now binding for parent Decision 6 and checklist item 7; it is not Gate 5 completion.

## Ledger Prerequisite

The current Ledger.append flushes without a durable fsync transaction and does not serialize
all writers. GHI #952/#953 own that shared defect. This item MUST NOT claim that primitive
already exists: verify their delivered concurrency/crash/durability tests and receipts before
implementation. Do not implement a landing-private ledger writer or assume a surface lock
protects unrelated event writers. The prerequisite must supply a durable atomic append and a
stable event identity that can be checked idempotently after uncertain completion. If it
remains absent, 07 is blocked on that named repair; no journal cleanup or durable-completion
claim may rely on today's Ledger.append. This does not reopen completed OBPI-04's explicitly
bounded attestation.

## Landing State and Integrity Contract

Before any committed artifact changes, acquire a surface-scoped writer lock and validate
the full target set, including candidates, lineage and owned-section findings from 06.
Dry-run writes nothing. Reject changed route/ownership/corpus inputs after preparation.
Store a durable journal under the existing rendition directory with landing id, old/new
corpus fingerprints, route and ownership digests, exact target paths, old/new artifact hashes,
attestation evidence and publication progress. Stage each consumer's complete artifact
set — rendition, provenance and lineage, plus the retention sidecar when Requirement 12
publishes or removes one — and fsync durable state before each publication boundary. Another active landing
for the surface cannot interleave writes. Treat malformed state and unsafe paths as errors.

The phases are prepared -> publishing -> verified -> complete. File presence is never
completion proof. Hash all published bytes, validate owned lineage, and verify every target's
shared landing id and attestation before emitting one idempotent typed completion event.
Clear the active journal only after that event is durable. Preserve the target/hash manifest
in that event so status works after journal cleanup. A crash after the last file but before
the event resumes final verification; a crash after the event but before cleanup does not
duplicate the event or attestation. Test interruption at each boundary, including between a
rendition and its sidecars, and a disappeared/corrupt artifact with apparently valid metadata.

Status takes a landing id and is read-only. It compares all actual artifact hashes to the
recorded old/new manifests, reporting new, old or indeterminate per consumer; it never trusts
mtime or just the sidecar's claimed corpus fingerprint. Resume without new attestation
requires the same corpus, route, ownership and complete journal/evidence. Input drift or
indeterminate external edits refuse automatic overwrite and name the precise recovery path.
The entire set has one success boundary, but readers of individual files may observe mixed
bytes while publication is incomplete; this is the approved guarantee.

Rollback documentation must enumerate rendition, provenance and lineage together from one
known-good git revision. It must also verify whether that revision matches the current corpus;
restoring old files cannot pretend to roll back append-only canon. Preserve the interrupted
journal and report any remaining drift until governed recovery completes.

REQ-02/05/06/07/08 cover the state transitions and failure boundaries above. REQ-04 also
covers old sidecars loading without optional landing_id, new landings requiring it, and
RenditionProvenance still rejecting unexpected fields or embedded lineage.

## Threat Model

Ratified 2026-09-27 by operator g0, option chosen: "Ratify draft (Recommended)".

- **In scope.** An interrupted process at any publication boundary; concurrent `gz` invocations; edits by hand or by another tool to files under `.gzkit/renditions/<surface>/` (renditions, provenance and lineage sidecars, retention sidecars, the landing journal), including a good sidecar copied next to altered bytes.
- **Accepted residual.** Someone with write access who appends forged rows to `.gzkit/ledger.jsonl`, or who forges a journal and a ledger that agree with each other. This is the same residual OBPI-0.35.0-04 accepted for `.gzkit/ownership/` (same directory class, same access). Findings that require it are out of scope for Step 4b.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- [ ] `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/DESIGN_FORCING_FUNCTIONS.md` — pre-mortem, WWHTBT, constraint archaeology, 2am-operator, reversibility, scope minimization.

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `AGENTS.md` - agent operating contract
- [ ] `.gzkit/rules/tests.md` § REQ Scope Discipline — the three-kind proof-channel matrix this brief's Acceptance Criteria are tagged against

**Context:**

- [ ] ADR § Decision item 6 — the orchestrator, the single attestation, and the shared `landing_id`.
- [ ] `DESIGN_FORCING_FUNCTIONS.md` § 5 The 2am Operator Question — the five gaps that are REQs here, not nice-to-haves.
- [ ] ADR § Consequences (Negative) #3 and § Decomposition Scorecard testability-ceiling note.
- [ ] ADR § Alternatives C — delta-patch retained as the PRESENTATION layer inside `land`, rejected as the destination.

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.35.0-05 landed: the deterministic generator emits candidates and lineage maps for every consumer
- [ ] `src/gzkit/content/rendition_store.py` exists with `save_rendition`, `save_fingerprint`, `corpus_fingerprint`, and `RenditionProvenance`
- [ ] `src/gzkit/commands/content/commit.py` exists — the single-consumer corpus-attested commit path this orchestrator generalizes
- [ ] data/vendor-manifest.json supplies active routes; AgentContract has root only. Use an isolated synthetic surface with three declared consumers for failure/recovery scenarios. Off-route retained files are never targets.
- [ ] `docs/user/manpages/content.md` and `docs/user/runbook.md` exist

**Existing Code (understand current state):**

- [ ] `src/gzkit/content/rendition_store.py:31-53` — `RenditionProvenance` is frozen with `extra="forbid"`; adding `landing_id` is an additive optional field, exactly as `rendition_fingerprint` was under GHI #694
- [ ] `src/gzkit/content/rendition_store.py:95-134` — `rendition_exists`, `save_rendition`, `save_fingerprint`: the single-consumer write path being made atomic across a set
- [ ] `src/gzkit/commands/content/commit.py:44-140` — the existing corpus-attestation commit and its sidecar write. Its gate is CONDITIONAL since GHI #821 (fail-closed only on a corpus delta); Requirements 5 and 9 are unaffected because both already scope the attestation to the DELTA
- [ ] `src/gzkit/governance/trust_audits/rendition_floor_coherence.py:1-9` — the module docstring naming mtime comparison as the discredited witness `--status` must not reuse

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. -->

<!-- gz-validate-skip: command-shape -->
```bash
uv run -m unittest tests.content.test_landing tests.commands.test_content_land
uv run -m behave features/content_land.feature
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz validate --rendition-freshness
uv run gz cli audit
uv run mkdocs build --strict
```

## Demo

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz content land --help
uv run gz content land AGENTS.md --dry-run
uv run -m behave features/content_land.feature
```

## Acceptance Criteria

<!--
Each checkbox carries a deterministic REQ ID and exactly one kind tag
(ADR-0.0.59; `gz validate --req-kind-discipline`):
  [behavior]         -> proven ONLY by an @covers test in tests/**
  [support]          -> proven ONLY by a path-citing ledger event + structural validator
  [structural-fence] -> proven ONLY by a parent-ADR ## Boundary Invariants entry
-->

- [ ] REQ-0.35.0-07-01 [behavior]: Given gz content land invoked with no positional argument, when it runs, then it exits non-zero with a usage error — `<surface>` is required, matching `compose` and `commit`.
- [ ] REQ-0.35.0-07-02 [behavior]: Given a surface with three consumers and an induced failure while staging the second, when `land` runs, then NONE of the three committed renditions, provenance sidecars or lineage artifacts is modified. Also induce a replace failure after the first published file: journal/status expose incomplete publication, no completion event is emitted, and retry resumes from verified hashes without rewriting completed files.
- [ ] REQ-0.35.0-07-03 [behavior]: Given a new corpus delta without reusable attestation evidence and land invoked with empty or whitespace-only attestor or attestation text, when it runs, then it exits non-zero and writes nothing — no state file, no rendition, no sidecar, no ledger event. Unchanged-corpus re-render and verified resume instead succeed using existing evidence; forged or mismatched evidence is refused.
- [ ] REQ-0.35.0-07-04 [behavior]: Given a successful landing across N consumers, when the sidecars are read, then all N carry the SAME `attestation_text` and the SAME `landing_id`, and exactly one corpus-attestation ledger event was emitted for the corpus delta.
- [ ] REQ-0.35.0-07-05 [behavior]: Given a landing interrupted after the first consumer, when the filesystem is inspected, then the landing state file EXISTS and carries the `landing_id`, the full intended consumer set, and the corpus fingerprint; and given a landing that completed, then the state file is ABSENT — written before the first byte, cleared after the last sidecar.
- [ ] REQ-0.35.0-07-06 [behavior]: Given a `landing_id` and a consumer set in mixed state, when `--status <landing_id>` runs, then each consumer is classified as new-fingerprint, old-fingerprint, or indeterminate by verifying actual rendition/lineage hashes and their provenance against recorded old/new corpus fingerprints; altered bytes with a copied good sidecar are indeterminate. Given two renditions with identical fingerprints but different mtimes, then the classification is IDENTICAL for both — mtime is never consulted.
- [ ] REQ-0.35.0-07-07 [behavior]: Given an interrupted landing where consumer 1 of 3 already landed, when `land` is re-run to resume, then consumer 1's rendition and sidecar are BYTE-UNCHANGED and consumers 2 and 3 land — resume is non-destructive.
- [ ] REQ-0.35.0-07-08 [behavior]: Given a resume of an interrupted landing whose state file records an attestation, when `land` is re-run, then it completes WITHOUT prompting for or requiring `--attestor`/`--attestation-text`, reusing the recorded values and `landing_id` — and no `--force`-style override is needed or offered.
- [ ] REQ-0.35.0-07-10 [behavior]: Given a consumer whose generated candidate removes a block of its prior committed rendition, when `land` runs without a `--retention-map` for that consumer, or with one that fails the retention gate (for example a DROPPED id absent from this invocation's `--attestation-text`), then it exits 3 and writes nothing for ANY consumer — no state file, rendition, sidecar or ledger event; and given a valid map, the landing completes and publishes `<consumer>.retention.json` with the consumer's other artifacts.
- [ ] REQ-0.35.0-07-09 [support]: `docs/user/manpages/content.md` and `docs/user/runbook.md` document the `land` contract and NAME the rollback — committed renditions have no prior-version retention, so recovery is `git restore --source=<known-good-revision> --staged --worktree -- .gzkit/renditions/<surface>/`, restoring the whole artifact set and removing artifacts added since (amended 2026-09-27, operator ruling "Name restore, amend REQ (Recommended)"; it read "recovery is `git checkout`") — witnessed by an `artifact_edited` ledger event citing `docs/user/manpages/content.md`, and `gz validate --cli-alignment` resolves every gz content land reference they prescribe.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

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
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Change Log

- 2026-09-27, Stage 1 plan audit (FAIL receipt: no plan; ADR/brief drift). Four operator rulings, options chosen verbatim: (1) "Repeatable map (Recommended)" — Requirement 12 and REQ-0.35.0-07-10 added so `land` passes the OBPI-14 retention gate (ADR BI-10), which the brief predated; (2) "Avoid the surface (Recommended)" — `src/gzkit/ledger_events.py` (a registered `ledger_integrity` surface) removed from the allowlist, and the typed event is built with `ledger_row(model)`; (3) "Add both (Recommended)" — `src/gzkit/ontology/corpus.py` and `tests/test_schemas.py` added as coupled consumers of a new ledger event type; (4) "Ratify draft (Recommended)" — § Threat Model added. Allowed Paths bullets were split to one path each, because `extract_allowed_paths` reads only the first backticked path of a bullet (its documented contract), which hid paths from `gz plan audit` and `--sensitivity`. Defects recorded with `gz insights remember`: the `--sensitivity` floor reads only the first path of a multi-path Allowed Paths bullet (fail-open; hid `ledger_events.py` here), and OBPI-0.39.0-01/-02 fail that floor unseen because the scope is out of `gz check`.

- 2026-09-27, Task 1 (implementer, opus; dispatch recorded). Delivered the pure preparation layer and the CLI shell (25 tests OK). Operator ruling, option chosen verbatim: "Add all three (Recommended)" — allowlist gains `tests/cli/test_attestor_default.py` (new-verb coupled consumer) and read-only `src/gzkit/content/corpus_store.py` and `src/gzkit/content/retention.py` (brief-reconcile counts covering-test imports), the same amendment ratified for OBPI-0.35.0-14. Defect fixed in scope: `save_fingerprint` wrote sidecars with `write_text`, producing CRLF bytes on Windows that differ from the bytes a landing hashes and publishes; it now writes LF bytes, pinned by a byte-form test.

- 2026-09-27, Task 1 Stage-2 round. Proofs: REQ-01 proof-d2622f19a60f4356afadd6dc43a047bb (1 control), REQ-03 proof-79edf99d02884362912e1a9347816f91 (3 controls), REQ-10 proof-195a0a140a514199b10d06ec50f249f3 (2 controls); every control killed on an assertion and restored green. Quality review arb-step-qualityreview-d67330382a3b4c8b9be43817b07b7659 accepted all three, with three unmapped observations (oversized `prepare_landing`; CLI refusal exit/no-write assertions vacuous while `publish_landing` was a stub; an unneeded `arbitrary_types_allowed`). Spec review arb-step-specreview-22e569903f5d4e21b7b74b1291d7c282 refuted REQ-10 with spec-rev1-req10-stray-map-exits-1-not-3: a map targeting an unrouted consumer exited 1, where REQ-10 and the retention gate's own map-target check make it exit 3. It also recorded the success halves of REQ-03 and REQ-10 as missing proof (owned by Tasks 2 and 3). All repairs are batched into Task 2's dispatch as one fix cycle.

- 2026-09-27, Task 2 (implementer, opus; dispatch recorded; one resume after its turn limit). Delivered journaled publication, verification, the idempotent `rendition_landed` event and journal-last cleanup, and repaired the Task 1 findings in one batch: a map bound to another surface or an unrouted consumer now exits 3 (spec-rev1-req10-stray-map-exits-1-not-3); the REQ-03 and REQ-10 success halves are proven end to end through the CLI; `prepare_landing` split to 31 lines; `arbitrary_types_allowed` dropped and plan payloads made immutable. Operator ruling, option chosen verbatim: "Ignore all three (Recommended)" — `.gitignore` added to the allowlist and the landing's `.landing.lock`, `.landing.json` and `.landing-staging-*/` sidecars ignored by name, matching OBPI-0.35.0-04's ownership sidecars. Measured: `landing.py` is 1,212 lines, under the `gz check` module-size block band (radon_raw_nloc 3,143.82) and xenon-clean at `--max-absolute C --max-modules B --max-average A`; several Task 1 helpers exceed the advisory lizard function bands, and the module exceeds `pythonic.md`'s 600-line guidance. Both are advisory and disclosed for review rather than split, because the allowlist names one landing module.

- 2026-09-27, Task 3 (implementer, opus; dispatch recorded) delivered `--status` and resume through one shared publication path. Two orchestrator corrections under REQ-0.35.0-07-08 followed: a landing killed while staging (phase `prepared`, nothing published) now regenerates its bytes from the journal's recorded values and resumes without attestation, and each consumer's reviewed retention sidecar text is recorded in the journal so resume never re-runs the gate. Task 4 (implementer, opus) delivered the manpage `### land` section with the named rollback, the runbook flow, the doc-coverage entry, the TUI fence and 13 BDD scenarios. INCIDENT during Task 4: a failed `cd` chain left the implementer at the repository root, and two real `gz content land AGENTS.md` landings ran; one ledger row recorded fabricated attestation text for g0. Operator ruling, option chosen verbatim: "Restore + void both (Recommended)". Renditions restored with `git checkout HEAD`, `root.lineage.json` removed, rows `rendition-landed-landing-20260927T235819Z-6b95f418` and `rendition-landed-landing-20260927T235820Z-83fe801f` voided with `gz ledger correct` (cause agent-error, attestor g0). Recorded as an insight.
- 2026-09-27, process deviation, disclosed: Tasks 2 and 3 were reviewed together with Task 4 in one combined Stage-2 round, because every task edits the one landing module and each edit stales every proof. Orchestrator corrections before that round: CRLF line endings written by the Task 2 implementer normalized to LF (the proof runner matches raw bytes); `_provenance_claim` removed from status as unreachable (the provenance sidecar's content hash already binds its landing_id and corpus fingerprint; its mutation survived); success-path unit tests routed through `_must_succeed` so a refusal fails as an assertion; one internally inconsistent mutation replaced. Proofs: all nine BEHAVIOR REQs valid, 24 of 24 mutations killed on assertion. Quality review arb-step-qualityreview-ba916fb2b2ab4348a65aa6cba8d91512 accepted all nine and closed the three Task 1 findings. Spec review arb-step-specreview-546a46b9f9d64c54a8c1a6bf0f0d8b7d approved eight, closed the same three findings, and recorded spec-rev2-req02-retry-from-verified-hashes-unproven: the REQ-02 proof never retries after the replace failure, so a flag-based resume would pass it. Repair batch dispatched with that proof plus four auxiliary corrections.
- 2026-09-27, gate defects found and fixed in the same working tree under their own routes (not OBPI scope): GHI #1143 (`run_command` had no timeout; `gz test` hung 24 minutes), repaired with a packaged hang bound that kills the whole process tree; and `gz arb step` never set its child's stdio encoding, so `tests/arb/test_step_output_cli.py` passed only in shells with `PYTHONUTF8` set. Both land in the same commit as this OBPI's work: the `ty` pre-commit hook type-checks the whole working tree, so a partial commit of either fix failed on the uncommitted landing module; the commit message names each part.

- 2026-09-27, Stage-2 fix cycle 1 (implementer, sonnet; dispatch recorded; one resume). Repaired spec-rev2-req02-retry-from-verified-hashes-unproven with `test_retry_resumes_from_verified_hashes_not_from_the_published_flag`, now in the REQ-02 proof with the mutation `resume-skips-by-published-flag` (killed on assertion); the resume note now names only flags this invocation supplied (a configured `--attestor` is not reported as ignored) and names dropped `--retention-map` values; a failing staging cleanup no longer masks the exit-2 refusal; the landing manifest's round trip through the ledger event is pinned by a test. All nine proofs re-run: 25 of 25 mutations killed on assertion. Focused follow-up: spec arb-step-specreview-2617905ffe284f1fbbe640dca4a3b3ac and quality arb-step-qualityreview-e295c75f3d8845eebd81b95d72fe6d4f accepted all nine current proofs and closed every mapped finding. One cosmetic observation deferred: the resume note says "were ignored" for a single flag. Stage-3 receipts: arb-ruff-4f4e80dbc54b43d1b09d556ad8b58179, arb-step-typecheck-4ab83c7ed25a431289ede565e3d62682, arb-step-unittest-92545fa88b7244189c1b3d02080b97a0, arb-step-mkdocs-87b2feb3938545c19f4ef3792429a58a, arb-step-behave-6cd45fd061784845ab93f0fab462ab0e (13 scenarios, 96 steps).

- 2026-09-27/28, REQ-09 scoped review and repair. Spec arb-step-specreview-e2f9726aa5c9430380f625c25a1b85aa and quality arb-step-qualityreview-a4e21a70ef954e92995e8f81fbff3579 both refuted REQ-09: `git checkout <rev> -- <dir>` leaves artifacts added since `<rev>` (reproduced by the orchestrator in a scratch repository). Operator ruling, option chosen verbatim: "Name restore, amend REQ (Recommended)" — Requirement 10 and REQ-09 amended to `git restore --source=<rev> --staged --worktree`; code recovery prose and docs repaired (implementer, sonnet; dispatch recorded), resume note grammar fixed. All ten proofs re-run valid (25 of 25 mutations killed; REQ-09 SUPPORT pass). Follow-up spec arb-step-specreview-7c33d579e6404c22981224557428c375 and quality arb-step-qualityreview-f4d2438d928f460491f31b9a1bb4453a accepted all ten current proofs and closed every mapped finding; Stage-2 status ready. Step 4a packet `.gzkit/evidence/OBPI-0.35.0-07-content-land-orchestrator.stage4a.md` VERIFIED by `gz obpi verify-packet`.
- 2026-09-27/28, Step 4b (tier 1, Codex plugin `task --write` in a disposable checkout, digest f8276d8c…). The Codex plugin was not installed; operator installed it (option "Install plugin, tier 1 (Recommended)"). Round 1 (arb-step-codexadversary-37f1a032013e45d4b7c86f90d3b4f90b, imported): environment failure — Codex's Windows sandbox could not re-ACL `~\.codex\.sandbox-bin` (owner BUILTIN\Administrators; `helper_sandbox_lock_failed`, error 5; upstream openai/codex #36475, #45734, #46380); no findings, no approvals. Operator closed other Codex processes, then, on "fix it", the orchestrator renamed the directory to `.sandbox-bin.old` so Codex recreated it, and set aside a stale companion `broker.json` whose runtime had died. Round 2 (arb-step-codexadversary-70151f5432974f658c362e2bfd5fe005): NOT-CORROBORATED; replayed one mutation per BEHAVIOR REQ and confirmed the git-restore rollback, approved 7 of 10 proofs, and found three counterexamples: `adv-07-publication-overwrites-concurrent-edit` (REQ-02: `_publish` does not recheck a target's old hash at its replacement boundary, so an in-scope edit during staging is overwritten), `adv-07-resume-overwrites-concurrent-edit` (REQ-07: same gap on resume), `adv-07-manpage-edit-witness-absent` (REQ-09: no `artifact_edited` event cites the manpage; the SUPPORT resolver passed on file existence). IMPORT REFUSED (exit 3): the review's replay records carried abridged test output without the unittest summary line, which the importer classifies as `error`, contradicting its prose. The findings are therefore not yet in the acceptance ledger; this entry is their record until the next round.

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
