---
id: OBPI-0.35.0-09-codex-playback-wiring
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 9
lane: Heavy
status: Active
allowlist:
- src/gzkit/sync_surfaces.py
- src/gzkit/governance/compose.py
- src/gzkit/content/vendors.py
- src/gzkit/schemas/vendor_manifest.json
- src/gzkit/governance/trust_audits/vendor_manifest.py
- src/gzkit/governance/trust_audits/surface_delivery_witness.py
- src/gzkit/governance/trust_audits/rendition_floor_coherence.py
- src/gzkit/governance/trust_audits/rendition_freshness.py
- src/gzkit/content/rendition_store.py
- src/gzkit/content/corpus_store.py
- src/gzkit/governance/trust_audits/_qc_negative_controls.py
- data/vendor-manifest.json
- data/distribution_baseline_manifest.json
- src/gzkit/content/templates/agentcontract/**
- .gzkit/renditions/AGENTS.md/**
- tests/test_sync_surfaces.py
- tests/governance/test_compose.py
- tests/content/test_vendor_manifest.py
- tests/content/test_composer.py
- tests/content/test_tier_policy.py
- tests/content/test_byte_stability.py
- tests/commands/test_content_compose.py
- tests/governance/test_setpoint_coherence.py
- tests/governance/test_surface_delivery_witness.py
- tests/governance/test_rendition_floor_coherence.py
- tests/governance/test_rendition_freshness.py
- tests/content/test_rendition_store.py
- features/**
- docs/user/runbook.md
- docs/governance/agent-control-surface-rendering-substrate.md
- docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-09-codex-playback-wiring.md
reqs:
- REQ-0.35.0-09-01
- REQ-0.35.0-09-02
- REQ-0.35.0-09-03
- REQ-0.35.0-09-04
- REQ-0.35.0-09-05
- REQ-0.35.0-09-06
- REQ-0.35.0-09-07
- REQ-0.35.0-09-08
- REQ-0.35.0-09-09
- REQ-0.35.0-09-10
- REQ-0.35.0-09-11
verification:
- uv run gz lint
- uv run gz typecheck
- uv run gz test
- uv run gz validate --invariant-coherence
- uv run gz validate --rendition-floor-coherence
- uv run gz validate --surfaces
- uv run gz validate --req-kind-discipline
- uv run mkdocs build --strict
tasks:
  - TASK-0.35.0-09-11-01
  - TASK-0.35.0-09-01-01
  - TASK-0.35.0-09-02-01
  - TASK-0.35.0-09-03-01
  - TASK-0.35.0-09-04-01
  - TASK-0.35.0-09-05-01
  - TASK-0.35.0-09-06-01
  - TASK-0.35.0-09-07-01
  - TASK-0.35.0-09-08-01
  - TASK-0.35.0-09-09-01
  - TASK-0.35.0-09-10-01
  - TASK-0.35.0-09-01-02
---

# OBPI-0.35.0-09-codex-playback-wiring: Codex Playback Wiring

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #9 - "Codex playback wiring -- make the `lite` setpoint falsifiable; coordinates with ADR-pool.vendor-alignment-codex"

**Status:** Active

## Objective

**RE-SCOPED 2026-08-17 (operator-ruled).** This OBPI was authored to play `codex.md` back to a *second*, Codex-specific contract surface. That premise was wrong, and the correction is doctrine recovery rather than new design.

**AGENTS.md is the root contract and the agent-harness default; the single rendition serves EVERY harness.** Operator verbatim 2026-08-17: *"claude reads AGENTS.md too — the lite rendition serves both"*; *"agents.md is more universal than stubborn anthropic. So, agents.md is the agent harness default."* This is **OLD GROUND**: `docs/governance/agent-control-surface-rendering-substrate.md:211` has named the root vendor since authoring — `gz content render agent_contract --vendor=root`.

The doctrine drifted to a per-consumer shape in **three** places, none of which was ever ruled:

| Surface | Carries |
|---|---|
| `docs/governance/agent-control-surface-rendering-substrate.md:276` (§ Agent Orientation Index) | `.gzkit/renditions/AGENTS.md/<consumer>.md` — a Layer-3 row describing the implementation, 65 lines below the Layer-1 worked example it contradicts |
| `data/vendor-manifest.json` | `"AgentContract": ["claude", "codex"]` + two temperatures |
| `src/gzkit/content/vendors.py:21` `_FALLBACK_ROUTES` | the same pair, hardcoded in Python |

The same module already knows the truth: `delivery_cap_for`'s docstring states *"Codex silently truncates root `AGENTS.md` past `project_doc_max_bytes`."* The correct fact and the drift sit ~100 lines apart in one file, because the doctrine carried **no mechanical witness** — the third arm of the doctrine-declared-without-mechanism family (campaign Movement C).

Objective, restated: **collapse `AgentContract` to one rendition played back to root `AGENTS.md`, and fence the manifest so a per-vendor AgentContract can never be declared again.** The `lite` setpoint becomes falsifiable not because a second file is consumed, but because the *one* consumed file is measured against the smallest declared vendor cap.

**Measured blast radius (2026-08-17, before implementation).** The literal `"AgentContract": ["claude", "codex"]` occurs at **20 sites across 10 files** — `data/vendor-manifest.json`, `vendors.py:21`, five test modules, and three `features/steps/` modules. The fence invalidates every one of them, so the allowlist names them rather than discovering them at verify time. Fixture manifests are updated to the corrected shape rather than exempted: a fixture asserting a forbidden shape is a fixture teaching the next reader the wrong doctrine.

**Scope boundary (binding).** This OBPI wires the pipe and installs the fence. It does **not** decide what flows through it: which prose survives into a single ≤32,768 B rendition is a `gz content compose` + Gate-5 `commit`, driven by the `instructions-files-diet` chore under the 2026-08-17 cadence ruling. GHI #815 therefore stays OPEN after this OBPI and is correctly re-diagnosed as a **size** problem again, not a routing one.

**Dependency order (ADR-0.35.0 § Scope Minimization):** 09 is independent of the 01 -> 02 -> 03 chain and may land at any point. Per § Scope Minimization it is NOT cuttable: codex playback is the only thing that makes the `lite` setpoint falsifiable, and its cross-ADR coordination with `ADR-pool.vendor-alignment-codex` gets HARDER, not easier, if deferred into a window where that ADR has moved.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/sync_surfaces.py` — consumer resolution in the playback path only (currently `sync_agents_md`, lines 372-380)
- `src/gzkit/governance/compose.py` — `render_agents_md` consumer resolution
- `tests/test_sync_surfaces.py`, `tests/governance/test_compose.py` — covering tests
- `features/**` — Gate 4 scenarios
- `docs/user/runbook.md` — the codex playback surface
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-09-codex-playback-wiring.md` — this brief's evidence sections

## Denied Paths

The owning design returned to pool on 2026-08-08 (GHI #773), so these name its
checklist items rather than OBPI ids — pool ADRs carry no OBPIs by doctrine. The
boundary is unchanged: `ADR-pool.vendor-alignment-codex` owns all five surfaces
and this OBPI must not touch them.

- `.codex/config.toml` and `src/gzkit/sync_surfaces.py::render_codex_config` / `sync_codex_config` (lines 475-510) — Codex config generation, checklist item 01
- Codex hook registration and vendor-native adapters — checklist item 02
- `.agents/personas/**`, `.agents/skills/**`, Codex subagent role definitions — checklist item 03
- `gz validate --surfaces` and its Codex drift scope — checklist item 05
- Codex instruction-budget proofs and the Codex runbook — checklist item 06
- `src/gzkit/content/composer.py` — the generator is OBPI-0.35.0-05; this OBPI wires PLAYBACK, never composition
- New dependencies, CI files, lockfiles
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. READ ADR-pool.vendor-alignment-codex BEFORE SCOPING ANY EDIT. It owns the Codex surface. This OBPI coordinates; it does not collide. Its six checklist items — config generation, hooks policy, skills/personas/subagents, harness-aware pipeline runtime, surface validation, instruction budget and docs — are ALL out of scope here.
2. ALWAYS resolve the playback consumer rather than hardcoding it. `sync_surfaces.py:374-376` and `governance/compose.py:28-29` both load `("AGENTS.md", "claude")` as a literal; the playback path must take the consumer as a parameter (Cockburn's rule, `.claude/rules/hexagonal-architecture.md` operative rule 4).
3. **NEVER introduce a second `AgentContract` destination.** The only destination is root `AGENTS.md` (`config.paths.agents_md`). The authored form of this requirement resolved the destination from `config.vendors.codex.surface_root` (`.agents`, `enabled=False`) — **withdrawn 2026-08-17 on the operator's ruling that Codex reads root `AGENTS.md`.** Playing a contract back to a path no harness loads would have satisfied every gate in this brief while delivering nothing, and would have manufactured the second AGENTS.md the root doctrine forbids. `ADR-pool.vendor-alignment-codex` is unaffected: it owns `.codex/config.toml`, hooks, personas and skills — never the root contract.
4. NEVER regress the delivered contract. AGENTS.md after this OBPI MUST be byte-identical to AGENTS.md before it — the collapse is a **routing** change, not a content change. `gz validate --invariant-coherence` byte-compares a re-render against committed AGENTS.md and is in the default `gz check` scope. Which prose survives into a single ≤32,768 B rendition is a separate Gate-5 `compose`/`commit`; doing it here would bundle a human judgment into a mechanical change.
3a. **The single consumer is named `root`** (operator ruling 2026-08-17: *"ok, go with root"*), matching the doctrine's own vendor token at `agent-control-surface-rendering-substrate.md:211`. The rename of `claude.md`/`claude.corpus.json` → `root.md`/`root.corpus.json` is a `git mv` and preserves every attested fact: `RenditionProvenance` freezes `corpus_fingerprint`, `rendition_fingerprint`, `attestor` and `attestation_text`, and the consumer is a **filename key** that none of them depend on. Keeping `claude` was rejected because it re-encodes a vendor name on a universal contract — the exact confusion this OBPI exists to remove.
4a. **NEVER delete a Gate-5-attested rendition.** Collapsing the route set retires `codex.md` as a *consumer*, not as a *record*: superseded rendition files and their `.corpus.json` provenance sidecars stay on disk. Deleting an attested artifact to tidy a route table destroys the attestation trail (`ADR-0.0.71` semantics — supersede, never erase).
5. ALWAYS keep playback verbatim and deterministic — load the committed rendition bytes and write them; no LLM, no template substitution, no network (ADR § Alternatives L; the existing `render_agents_md` docstring contract).
6. ALWAYS stay bootstrap-safe. An absent `codex.md` rendition MUST produce no write and no error, exactly as `rendition_exists` already guards the claude path.
7. ALWAYS make the setpoint falsifiable — the point of this OBPI. Once `codex.md` is played back to a consumed surface, a `lite` rendition that drops an invariant-tier entry becomes a real failure rather than an unfalsifiable claim. The existing `--rendition-floor-coherence` scope already iterates every consumer under `.gzkit/renditions/<surface>/`; verify it now binds over a surface that is actually read.
8. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

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

- [ ] ADR § Decision item 8 and § Consequences (Positive) #5 — codex playback and `codex.md` becoming falsifiable.
- [ ] `DESIGN_FORCING_FUNCTIONS.md` § 3 Constraint Archaeology, heavy/lite setpoint — "A setpoint with no playback cannot be wrong", and why item 9 belongs in this ADR rather than deferred.
- [ ] `docs/design/adr/pool/ADR-pool.vendor-alignment-codex.md` § Decision and § Checklist — the six items that are out of scope here; read in full before editing.
- [ ] `.claude/rules/hexagonal-architecture.md` operative rule 4 — never name the technology in the core; take it as a parameter.

**Prerequisites (check existence, STOP if missing):**

- [ ] **Re-measure every rendition byte figure before quoting it.** The authored form of this checklist pinned `codex.md` at 13,606 B; it measured **15,764 B** on 2026-08-17, and `claude.md` / root `AGENTS.md` measured **34,354 B**. Run `wc -c` — never transcribe a figure from this brief.
- [ ] `.gzkit/renditions/AGENTS.md/*.md` and their `*.corpus.json` provenance sidecars exist and are readable
- [ ] `src/gzkit/sync_surfaces.py::sync_agents_md` exists and currently hardcodes the `claude` consumer
- [ ] `src/gzkit/governance/compose.py::render_agents_md` exists and currently hardcodes the `claude` consumer
- [ ] `docs/governance/agent-control-surface-rendering-substrate.md` § Worked example line 211 still reads `--vendor=root`; § Agent Orientation Index still reads `<consumer>.md`. **If they now agree, the fence in REQ-09-09 already landed — STOP and re-read the ledger before re-doing it.**
- [ ] `docs/design/adr/pool/ADR-pool.vendor-alignment-codex.md` present and read — it owns `.codex/**`, never the root contract

**Existing Code (understand current state):**

- [ ] `src/gzkit/sync_surfaces.py:372-380` — the hardcoded `rendition_exists(project_root, "AGENTS.md", "claude")` playback branch and its template bootstrap fallback
- [ ] `src/gzkit/governance/compose.py:28-29` — the second hardcoded `("AGENTS.md", "claude")` load
- [ ] `src/gzkit/sync_surfaces.py:475-510` — `render_codex_config` / `sync_codex_config`, the `ADR-pool.vendor-alignment-codex`-owned surface this OBPI must not touch
- [ ] `src/gzkit/config.py:26-60, 106-107` — `VendorConfig`, `vendors.codex`, and the existing `codex_skills` / `codex_config` path fields
- [ ] `src/gzkit/governance/trust_audits/rendition_floor_coherence.py:59-72` — already iterates every consumer, so the `lite` floor binds the moment codex is consumed

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
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --invariant-coherence
uv run gz validate --rendition-floor-coherence
uv run gz validate --surfaces
uv run gz validate --req-kind-discipline
uv run mkdocs build --strict
```

## Demo

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz agent sync control-surfaces
uv run python -c "from pathlib import Path; from gzkit.governance.compose import render_agents_md; print('claude bytes', len(render_agents_md(Path('.'), consumer='claude')), '| codex bytes', len(render_agents_md(Path('.'), consumer='codex')))"
uv run gz validate --rendition-floor-coherence
```

## Acceptance Criteria

<!--
Each checkbox carries a deterministic REQ ID and exactly one kind tag
(ADR-0.0.59; `gz validate --req-kind-discipline`):
  [behavior]         -> proven ONLY by an @covers test in tests/**
  [support]          -> proven ONLY by a path-citing ledger event + structural validator
  [structural-fence] -> proven ONLY by a parent-ADR ## Boundary Invariants entry
-->

- [ ] REQ-0.35.0-09-01 [behavior]: Given the playback path, when it is invoked for a named consumer, then it loads that consumer's committed rendition — the consumer is a parameter in both `sync_surfaces.sync_agents_md` and `governance.compose.render_agents_md`, and the literal `"claude"` appears in neither as a hardcoded load target.
- [ ] REQ-0.35.0-09-02 [behavior]: Given the committed `AgentContract` rendition, when the surface sync runs, then its bytes are written VERBATIM to root `AGENTS.md` (`config.paths.agents_md`) and to no other contract path — byte-for-byte, no reflow, no template substitution. There is exactly one `AgentContract` destination because there is exactly one root contract.
- [ ] REQ-0.35.0-09-03 [behavior]: Given NO committed `codex.md` rendition, when the surface sync runs, then no Codex contract file is written and no error is raised — playback is bootstrap-safe for the new consumer exactly as it already is for `claude`.
- [ ] REQ-0.35.0-09-04 [behavior]: Given the surface sync before and after this OBPI, when AGENTS.md is compared, then it is BYTE-IDENTICAL — the `claude` playback path is unchanged in behavior by the consumer parameterization.
- [ ] REQ-0.35.0-09-05 [behavior]: Given the single `AgentContract` rendition with an invariant-tier corpus entry removed, when `gz validate --rendition-floor-coherence` runs fail-closed, then it exits 3 naming that consumer — the setpoint is falsifiable because the rendition it grades is the one actually delivered.
- [ ] REQ-0.35.0-09-08 [behavior]: Given a `data/vendor-manifest.json` declaring more than one route OR more than one temperature for `AgentContract`, when the manifest is validated, then it fails closed naming the root-contract doctrine — a second per-vendor `AgentContract` rendition cannot be declared, in JSON or in code. Delivery **caps** are explicitly exempt and stay per-vendor: a cap is an observed fact about someone else's product (`delivery_cap_for` docstring), whereas a route and a temperature are controls gzkit chooses.
- [ ] REQ-0.35.0-09-09 [behavior]: Given `src/gzkit/content/vendors.py::_FALLBACK_ROUTES` and `data/vendor-manifest.json`, when they disagree on any content type, then the disagreement fails closed. The fallback table is a second copy of the routing authority maintained by a comment (*"Update both surfaces together"*) — the same two-copies-one-binds shape that let this drift ship, one layer down.
- [ ] REQ-0.35.0-09-10 [behavior]: Given root `AGENTS.md` and the per-vendor delivery caps declared for `AgentContract`, when the surface-delivery witness runs, then it measures the single delivered surface against the **minimum** declared cap and names the vendor that sets it. One file serving every harness must satisfy the smallest cap; measuring it per-route was only coherent while each route had its own file.
- [ ] REQ-0.35.0-09-11 [behavior]: Given `.gzkit/renditions/<surface>/` containing a committed rendition, a `*.candidate.md` staging artifact, and a superseded off-route rendition, when `gz validate --rendition-floor-coherence` runs, then it grades the committed on-route rendition ONLY. Enumerating by directory glob is what makes Requirement 4a above ("never delete an attested rendition") unlivable — a retained record would be graded against a corpus it was never committed against, forever. Candidates are graded today (measured 2026-08-17: `AGENTS.md/codex.candidate` appears in the gate's own error output), which is a separate defect of the same enumeration: a candidate is by definition not committed.
- [ ] REQ-0.35.0-09-06 [behavior]: Given identical committed renditions, when the surface sync is run twice, then both the claude and codex destination files are byte-identical across runs — playback stays deterministic.
- [ ] REQ-0.35.0-09-07 [structural-fence]: ADR-0.35.0 makes NO change to the surfaces ADR-pool.vendor-alignment-codex owns — `.codex/config.toml` generation, Codex hook registration and adapters, Codex subagent role definitions, the `gz validate --surfaces` Codex drift scope, and the Codex instruction-budget artifacts. This ADR wires playback of an existing committed rendition and nothing else. The boundary is cross-ADR and can only be audited once the whole ADR-0.35.0 diff is in hand, so it is a closeout-layer fence rather than a per-OBPI check.

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
