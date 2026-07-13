---
id: OBPI-0.0.72-03-insight-record-reconcile
parent: ADR-0.0.72-meta-governance-coherence
item: 3
lane: Heavy
status: Completed
# req_atomic — each REQ is one indivisible unit of labor with no sub-REQ
# subdivision: REQ-01 (append helper), REQ-02 (localized round-trip + fail-closed
# construction), and REQ-05 (the `gz insights remember` verb) were each one
# coherent code+test increment; REQ-03 (AGENTS.md rendition + scaffold reconcile)
# and REQ-04 (rationale-doc prose) were each one authoring edit. None was
# subdivided into seq=02+; the pipeline-minted seq=01-per-REQ buckets are the
# true labor shape.
req_atomic:
  - REQ-0.0.72-03-01
  - REQ-0.0.72-03-02
  - REQ-0.0.72-03-03
  - REQ-0.0.72-03-04
  - REQ-0.0.72-03-05
---

# OBPI-0.0.72-03-insight-record-reconcile: Insight Record Reconcile

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md`
- **Checklist Item:** #3 - "ADAPTER (C4): reconcile `InsightRecord` ↔ authoring contract — provide an InsightRecord-backed append helper (mechanical writer); and expose it as the governed `gz insights remember` CLI verb (mirrors `gz content remember`, closes GHI #575); align AGENTS.md Behavior Rule 11 (now pointing at `gz insights remember`) + agent-contract-rationale 'required fields' prose with the model envelope (add ts/type; evidence as list[str]); verify a helper-produced append round-trips clean via a localized round-trip test (real emitted output re-validated against InsightRecord). [OBPI-01 global validator WITHDRAWN 2026-07-13 — coherence realized locally.]"

**Status:** Completed

## Objective

An `InsightRecord`-backed append helper under `src/gzkit/insights/` becomes the single mechanical writer for `.gzkit/insights/agent-insights.jsonl`, so a hand-authored append can no longer drift from the schema that gates the file. A **`gz insights remember`** CLI verb (mirroring the existing `gz content remember`) is the governed author surface that wraps the helper — the `gz <verb>` surface agents actually invoke — closing **GHI #575** (no governed insight-author verb, only a hand-append path). The AGENTS.md Behavior Rule 11 authoring contract — edited at its composition source, never the rendered surface — now directs agents to `gz insights remember` instead of a raw jsonl append, and the agent-contract-rationale 'required fields' prose name exactly the model's required fields (`ts`, `type`, `scope`, `summary`) and specify `evidence` as a list, closing contradiction C4 (the model required `ts`/`type`/`evidence: list[str]` that the prose omitted, which failed a hand-authored append this session). Architecture (hexagonal): the append helper is the core/domain writer; `gz insights remember` is the CLI adapter over it.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md` — parent ADR for intent and scope
- `src/gzkit/insights/model.py` — read/extend: the `InsightRecord` envelope (`ts`, `type`, `scope`, `summary` required; `evidence: list[str]`) is the contract the helper and prose reconcile to
- `src/gzkit/insights/append.py` — **CREATE** the `InsightRecord`-backed append helper (the mechanical writer); it constructs an `InsightRecord` and serializes one JSONL line so the append path cannot drift from the model
- `tests/governance/test_insight_append.py` — **CREATE** TDD tests: the helper's emitted line validates against `InsightRecord` and round-trips clean
- `.gzkit/renditions/AGENTS.md/claude.md` — **the real AGENTS.md source** (brief-reality correction 2026-07-13, operator-ratified): `gz governance render --target agents-md` plays this committed rendition back verbatim (ADR-0.0.37 OBPI-22). Behavior Rule 11 lives HERE — the rendition is hand-authored and the corpus (`.gzkit/corpus/AGENTS.md.jsonl`) has NO Rule-11 entry, so this is the edit point. EDIT THIS, never the rendered `AGENTS.md` directly; then re-render.
- `.gzkit/renditions/AGENTS.md/claude.candidate.md` — compose-candidate staging (`gz content compose AGENTS.md --consumer claude --candidate ...`)
- `.gzkit/templates/agents.md` — the **adopter scaffold** (`gz init` bootstrap for new projects), NOT this repo's AGENTS.md source; updated in the same commit for adopter coherence (Maxim 1a).
- `src/gzkit/templates/agents.md` — wheel-distributed copy of the scaffold; byte-equivalent to `.gzkit/templates/agents.md` (ADR-0.0.31 distribution invariant, `gz validate --distribution`)
- `docs/governance/agent-contract-rationale.md` — the Behavior Rule 11 'Required fields' prose (lines 209-214) aligned to the model envelope
- `src/gzkit/commands/insights.py` — **CREATE** the CLI adapter: `register_insights_parsers` + the `gz insights remember` handler wrapping the append helper (mirrors `src/gzkit/commands/content/` `remember`; parses `--type/--scope/--summary/--evidence/--next-action`)
- `src/gzkit/cli/main.py` — wire `register_insights_parsers(commands)` into the top-level parser (mirrors the `register_content_parsers(commands)` call)
- `tests/commands/test_insights_cmd.py` — **CREATE** TDD tests for the `gz insights remember` verb (appends one valid line; empty required arg fails closed)
- `config/doc-coverage.json` — register `insights remember` (manpage=false, mirroring the sibling `content remember`; the verb is documented via `--help` + its wielding skill). Keeps `gz cli audit` at 125/125 parity without a standalone manpage.
- `features/insights_remember.feature` — **CREATE** behave scenario (Gate 4) exercising `gz insights remember` end-to-end
- `.gzkit/skills/gz-insights-remember/SKILL.md` — **CREATE** the wielding skill (tool-skill Invariant 1: every CLI verb needs a skill; `gz_command: gz insights remember`); mirrored to vendor skill dirs by `gz agent sync control-surfaces`

> **Composition nuance (ADR-0.0.37) — CORRECTED 2026-07-13:** `AGENTS.md` is a played-back surface — `gz governance render --target agents-md` reads the committed rendition `.gzkit/renditions/AGENTS.md/claude.md` verbatim (OBPI-22 playback) and `gz validate --invariant-coherence` byte-compares render-vs-committed. The original brief said the source was `.gzkit/templates/agents.md`; that is the ADR-0.0.37 template model, which was SUPERSEDED by the corpus→rendition model and is now the **adopter scaffold**, not this repo's source. Trace confirmed: `render_agents_md` plays back the rendition; the corpus has no Rule-11 entry (the rendition is hand-authored — the OBPI-21/22 repudiation). So: EDIT `.gzkit/renditions/AGENTS.md/claude.md`, then `gz governance render --target agents-md`; update the scaffold in the same commit for adopter coherence. NEVER hand-edit the rendered `AGENTS.md`.

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `AGENTS.md` — the RENDERED composition target; NEVER hand-edit it (breaks `gz validate --invariant-coherence`). Edit `.gzkit/templates/agents.md` and re-render instead.
- `.gzkit/insights/agent-insights.jsonl` — the live trust surface; not rewritten by this OBPI (the helper appends to it at runtime, but no historical line is touched — trust-doctrine T2)
- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: The append helper MUST produce records that validate cleanly against `InsightRecord` (`src/gzkit/insights/model.py`) — every helper-written line passes `audit_insights_shape` / `gz validate --insights-shape`. The helper constructs the model first, then serializes; it never hand-builds a dict that could omit `ts`/`type`.
1. REQUIREMENT: The `gz insights remember` verb MUST construct the record via the append helper (never a separate dict path), append exactly one line per invocation, and FAIL CLOSED (non-zero exit) when a required field (`--type`/`--scope`/`--summary`) is empty or `--type` is not one of the `InsightRecord` enum values. The verb MUST be registered so `gz cli audit` and `gz validate --cli-alignment` resolve it.
1. REQUIREMENT: The AGENTS.md Behavior Rule 11 prose MUST name EXACTLY the model's required fields — `ts`, `type`, `scope`, `summary` — and specify `evidence` as a list (not scalar-or-list), AND direct agents to `gz insights remember` as the governed author path. The agent-contract-rationale 'Required fields' list MUST match the same envelope.
1. NEVER: Edit the rendered `AGENTS.md` directly. Edit the composition source `.gzkit/templates/agents.md`, keep `src/gzkit/templates/agents.md` byte-equivalent, re-render via `gz governance render --target agents-md`; `gz validate --invariant-coherence` MUST stay clean.
1. ALWAYS: stdlib + Pydantic only — no new runtime dependency (STDLIB-FIRST doctrine; `InsightRecord` is the already-attested Pydantic surface).
1. ALWAYS: TDD — a failing test derived from the REQ (helper output validating against `InsightRecord`) is authored before the helper exists.
1. REQUIREMENT: Work MUST stay inside the Allowed Paths; denied paths (especially the rendered `AGENTS.md`) remain untouched.
1. NEVER: Mark the OBPI accepted while scaffold defaults remain in the brief.
1. ALWAYS: Reconcile the brief with the parent ADR before implementation begins.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md`
- [ ] Required path exists or is intentionally created in this OBPI: `AGENTS.md`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

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

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. These are CONSTRUCTION HOUSEKEEPING (lint, type,
     test, mkdocs) — they prove the codebase is healthy, not what the OBPI
     yielded. The yielded product belongs in the `## Demo` section below.

     AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. The
     OBPI-pipeline verify stage executes commands via shlex.split + shell=False
     (GHI #415); compound commands are blocked at authoring time by
     gz validate --brief-command-shape and rejected at the verify stage.
     Write multi-step verification as separate uv run ... lines. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run gz validate --invariant-coherence
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Append a defect insight through the governed verb — no hand-authoring.
# gz insights remember wraps the mechanical helper: it builds an InsightRecord
# (ts/type/scope/summary + evidence list), then serializes one JSONL line, so
# the append cannot omit ts/type. This is the governed surface Rule 11 points at.
uv run gz insights remember --type defect --scope insights/model.py --summary "InsightRecord required ts/type that AGENTS.md Rule 11 omitted (C4)" --evidence src/gzkit/insights/model.py:32

# The helper-written line validates against InsightRecord — the exact append
# that failed closed this session now passes the gating audit.
uv run gz validate --insights-shape

# The reconciled Behavior Rule 11 prose re-renders byte-identically — the
# composition source was edited, not the rendered AGENTS.md.
uv run gz validate --invariant-coherence
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.72-03-01 [behavior]: Given the `InsightRecord`-backed append helper invoked with a `defect` (or `improvement`) payload, when it writes a line to `.gzkit/insights/agent-insights.jsonl`, then the emitted line parses as JSON and validates against `InsightRecord` — `ts` (ISO8601+tz), `type`, `scope`, `summary` present and `evidence` a `list[str]`. (@covers test)
- [ ] REQ-0.0.72-03-02 [behavior]: Given a record produced by the append helper, when the helper's ACTUAL emitted line is round-tripped through `InsightRecord` directly (a localized per-writer round-trip test capturing a real emission, never a hand-built happy-path stub), then it re-validates with no divergence — and an emitted line missing a required field (`ts`/`type`/`scope`/`summary`) fails closed with a `ValidationError`. (@covers test)
- [ ] REQ-0.0.72-03-03 [support]: AGENTS.md Behavior Rule 11 — edited at the real source `.gzkit/renditions/AGENTS.md/claude.md` (the played-back rendition) and re-rendered; adopter scaffold `.gzkit/templates/agents.md` (mirrored to `src/gzkit/templates/agents.md`) updated for coherence — names the model's required fields (`ts`, `type`, `scope`, `summary`), specifies `evidence` as a list, and directs agents to `gz insights remember`. Proof (SUPPORT, GHI #647 channel 2): the citation names `artifact_edited` for `.gzkit/renditions/AGENTS.md/claude.md` and that artifact exists on disk (content-authorship `artifact_edited` is not emitted for these edits — disk presence is the channel), plus the structural validator `gz validate --invariant-coherence` exit 0; `gz validate --req-kind-discipline` admits the proof.
- [ ] REQ-0.0.72-03-04 [support]: The `docs/governance/agent-contract-rationale.md` 'Required fields' prose (Behavior Rule 11 rationale) is aligned with the `InsightRecord` envelope — adds `ts`/`type` and specifies `evidence` as a list. Proof (SUPPORT, GHI #647 channel 2): the citation names `artifact_edited` for `docs/governance/agent-contract-rationale.md` and that artifact exists on disk, plus the structural validator `gz validate --documents` exit 0; `gz validate --req-kind-discipline` admits the proof.
- [ ] REQ-0.0.72-03-05 [behavior]: Given `gz insights remember --type improvement --scope <s> --summary <m> [--evidence <e> ...]`, when it runs, then it appends exactly one line to `.gzkit/insights/agent-insights.jsonl` that validates against `InsightRecord` (constructed via the append helper), and invoking it with an empty `--summary` or an out-of-enum `--type` exits non-zero and writes no line. (@covers test)

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

### Step 4b — Independent Adversarial Validation

- **Adversary:** Codex (tier 1, cross-vendor; `codex-cli 0.144.1`, authenticated) via `codex:codex-rescue`, separate refute-framed context.
- **Initial verdict:** REFUTED-WITH-CAVEATS. The CLI verb survived every attack (fail-closed confirmed real — empty `--summary` → exit 1 no write, bad `--type` → exit 2 no write; tests bite; no-write verified). Two caveats: (1) the RED witnesses were hollow — `arb red` errored on `Unknown REQ identifier` because the brief is uncommitted, so the base-tree worktree lacked the REQ; (2) it read the SUPPORT proof as "fake" (no ledger event citing the edited path).
- **Resolution:** (1) Produced a genuine **assertion-level RED** for all 3 BEHAVIOR REQs by stubbing the helper write and watching the tests fail (`False is not true: the helper must write…` ×2, `0 != 1` for the verb); strengthened the two helper tests with an explicit `path.exists()` assertion so their RED is clean, not `FileNotFoundError`. (2) False positive — the SUPPORT proof is **GHI #647 channel 2** (`artifact_edited` citation resolved by the artifact existing on disk + the structural validator), which `gz validate --req-kind-discipline` admits; corrected the brief's proof text to describe the real channel rather than a non-existent ledger event.
- **Final verdict:** caveats resolved; the verb behavior was NOT-REFUTED throughout, and the evidence spine is now backed.

```text
fail-closed: empty --summary -> exit 1 "no line written"; bad --type -> exit 2; line count unchanged
assertion RED (write stubbed): 03-01/03-02 "False is not true: the helper must write"; 03-05 "0 != 1"
green restored: Ran 5 tests OK
req-kind-discipline + documents + invariant-coherence + distribution + insights-shape + skill-alignment + cli-alignment: 7/7 pass
```

### Value Narrative

Before: agents hand-appended `.gzkit/insights/agent-insights.jsonl` and drifted from the `InsightRecord` schema (C4 — Behavior Rule 11 prose omitted `ts`/`type`, which failed a real append this session), and there was no governed author verb (GHI #575). Now: `gz insights remember` constructs-then-serializes an `InsightRecord` (stamps `ts`, validates the envelope), so a schema-drifting line is structurally impossible; AGENTS.md Rule 11/6 + the rationale doc now direct agents to the verb.

### Key Proof


```text
$ uv run gz insights remember --type improvement --scope <s> --summary <m> --evidence <e>
→ appended {"ts":"2026-07-13T11:28:25…","type":"improvement",…}   # validates as InsightRecord
$ uv run gz insights remember --type improvement --scope test --summary ""
→ Error: invalid insight record; no line written.   exit 1        # fail-closed, no write
$ grep -c "gz insights remember" AGENTS.md → 2                     # Rule 6 + Rule 11 point at the verb
```
Receipt: `arb-step-unittest-04c97bdf` (5/5), `arb-ruff-710bab87`, `arb-step-typecheck-dd651619`.

### Implementation Summary


- Files created: `src/gzkit/insights/append.py` (mechanical writer), `src/gzkit/commands/insights.py` (`gz insights remember` adapter), `tests/governance/test_insight_append.py`, `tests/commands/test_insights_cmd.py`, `.gzkit/skills/gz-insights-remember/SKILL.md`, `features/insights_remember.feature`.
- Files modified: `src/gzkit/cli/main.py` (wire verb), `.gzkit/renditions/AGENTS.md/claude.md` + re-rendered `AGENTS.md` (Rule 11/6 → verb), `.gzkit/templates/agents.md` + `src/gzkit/templates/agents.md` (adopter scaffold), `docs/governance/agent-contract-rationale.md` (envelope prose), `config/doc-coverage.json` (register `insights remember`).
- Tests added: 5 (`@covers` REQ-03-01/02/05, BEHAVIOR); clean assertion RED demonstrated for all three.
- Date completed: 2026-07-13.
- Attestation status: operator-attested ("attest completed", g0).
- Defects noted: fixed GHI #581 (pipeline `req_count` gate) in flight as a separate direct-fix (`c465934b`); closes GHI #575.

## Tracked Defects

- REQ-count drift: 9 declared vs 5 acceptance criteria (brief reconcile, attestor g0)

- REQ-count drift: 9 declared vs 5 acceptance criteria (brief reconcile, attestor g0)

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.72-03 governed insight verb `gz insights remember` + `append_insight_record` helper (closes C4 / GHI #575); AGENTS.md Behavior Rule 11/6 + agent-contract-rationale + adopter scaffold reconciled to the verb (gz validate --invariant-coherence green); 5 unit tests pass (receipt arb-step-unittest-04c97bdf6a704be882ad852cd50aa446), lint clean (arb-ruff-710bab871f0d450c9c8423881709ddcd), typecheck clean (arb-step-typecheck-dd651619567c4a7f89ff115e37c1b36c), behave @REQ-0.0.72-03-05 pass, 7 validators green, gz cli audit 125/125. Codex tier-1 Step-4b returned REFUTED-WITH-CAVEATS; both caveats resolved (clean assertion-level RED for all 3 BEHAVIOR REQs; SUPPORT proof corrected to GHI #647 channel 2). Attestor g0.
- Date: 2026-07-13

---

**Date Completed:** 2026-07-13

**Evidence Hash:** -
