---
id: OBPI-0.35.0-09-codex-playback-wiring
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 9
lane: Heavy
status: Completed
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
- docs/user/manpages/content.md
- docs/user/skills/gz-content-compose.md
- docs/user/skills/gz-advisor-qc.md
- .gzkit/skills/gz-advisor-qc/SKILL.md
- .claude/skills/gz-advisor-qc/**
- .agents/skills/gz-advisor-qc/**
- .github/skills/gz-advisor-qc/**
- src/gzkit/skills/gz-advisor-qc/**
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

**Status:** Completed

## Objective

**RE-SCOPED 2026-08-17 (operator-ruled).** This OBPI was authored to play `codex.md` back to a *second*, Codex-specific contract surface. That premise was wrong, and the correction is doctrine recovery rather than new design.

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

**Scope boundary (binding).** This OBPI wires the pipe and installs the fence. It does **not** decide what flows through it: which prose survives into a single ≤32,768 B rendition is a `gz content compose` + corpus-attested `commit`, driven by the `instructions-files-diet` chore under the 2026-08-17 cadence ruling. GHI #815 therefore stays OPEN after this OBPI and is correctly re-diagnosed as a **size** problem again, not a routing one.

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
- `docs/user/manpages/content.md`, `docs/user/skills/gz-content-compose.md`,
  `docs/user/skills/gz-advisor-qc.md`, `.gzkit/skills/gz-advisor-qc/SKILL.md` — **added
  2026-08-21 under operator ruling.** The authored blast radius measured the JSON literal
  `"AgentContract": ["claude", "codex"]` (20 sites, 10 files) and therefore never saw the
  DOCUMENTATION surface, where the retired route survives as `--consumer codex` prose. The
  tier-1 Codex adversary (receipt `arb-step-codexadversary-3da844475ab041a69f62249c42eb0113`)
  refuted the first documentation repair on exactly this: three surfaces were fixed because
  three had been named, which is the instance rather than the class. Gate 3 is required on
  this lane, and twelve operator-facing commands pointing at a route the manifest fence now
  refuses is a documentation defect, not a cosmetic one. The vendor mirrors are listed
  because `gz agent sync control-surfaces` regenerates them from the canonical skill.
- Historical briefs (`OBPI-0.35.0-05`, `OBPI-0.0.37-22`) and superseded campaign editions
  retain the old shape deliberately and are **NOT** in scope: they are sealed records of what
  was true on their date.
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
4. NEVER regress the delivered contract. AGENTS.md after this OBPI MUST be byte-identical to AGENTS.md before it — the collapse is a **routing** change, not a content change. `gz validate --invariant-coherence` byte-compares a re-render against committed AGENTS.md and is in the default `gz check` scope. Which prose survives into a single ≤32,768 B rendition is a separate corpus-attested `compose`/`commit`; doing it here would bundle a human judgment into a mechanical change.
3a. **The single consumer is named `root`** (operator ruling 2026-08-17: *"ok, go with root"*), matching the doctrine's own vendor token at `agent-control-surface-rendering-substrate.md:211`. The rename of `claude.md`/`claude.corpus.json` → `root.md`/`root.corpus.json` is a `git mv` and preserves every attested fact: `RenditionProvenance` freezes `corpus_fingerprint`, `rendition_fingerprint`, `attestor` and `attestation_text`, and the consumer is a **filename key** that none of them depend on. Keeping `claude` was rejected because it re-encodes a vendor name on a universal contract — the exact confusion this OBPI exists to remove.
4a. **NEVER delete a corpus-attested rendition.** Collapsing the route set retires `codex.md` as a *consumer*, not as a *record*: superseded rendition files and their `.corpus.json` provenance sidecars stay on disk. Deleting an attested artifact to tidy a route table destroys the attestation trail (`ADR-0.0.71` semantics — supersede, never erase).
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

Amended 2026-08-21: the Demo exercised `claude` and `codex` and printed
`claude bytes 0 | codex bytes 15755` — a retired route and a consumer with nothing
committed, demonstrating the drift this OBPI removes rather than the collapse it
delivers. Surfaced by the tier-1 Codex adversary (receipt
`arb-step-codexadversary-0bd5c04ee75c45a992052d9bfa9ad9f2`).

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz agent sync control-surfaces
uv run python -c "from pathlib import Path; from gzkit.content.vendors import routes_for; from gzkit.governance.compose import render_agents_md; c, = routes_for('AgentContract', project_root=Path('.')); print('routed consumer:', c, '| rendition bytes:', len(render_agents_md(Path('.'), consumer=c)), '| delivered AGENTS.md bytes:', Path('AGENTS.md').stat().st_size)"
uv run gz validate --vendor-manifest
uv run gz validate --rendition-floor-coherence
```

The single-element unpack (`c, = routes_for(...)`) is the demonstration, not a
convenience: it raises if `AgentContract` ever resolves to more or fewer than one
consumer, so the Demo cannot print a tidy answer for a re-vendored contract.

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
- [ ] REQ-0.35.0-09-06 [behavior]: Given an identical committed rendition for any named consumer, when the surface sync is run twice, then the delivered destination file is byte-identical across runs — playback stays deterministic. Amended 2026-08-21: this REQ read *"both the claude and codex destination files"*, which REQ-0.35.0-09-02 forbids in the same brief ("exactly one `AgentContract` destination because there is exactly one root contract"). The two-destination phrasing predates the route collapse this OBPI performs; the property being proven — playback is verbatim and re-running it cannot perturb the delivered contract — is unchanged, and the covering test already exercises a generic consumer (`alt-harness`) rather than either named vendor. Brief is `Active`, so this is ordinary pre-attestation repair, not the attested-REQ-subject-retirement transition.
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

### Step 4b — Independent Adversarial Validation

**Adversary:** Codex (`codex-cli 0.149.0`), **tier 1** — a different-vendor model, dispatched
ARB-wrapped, prompted to REFUTE and required to paste observed output. Tier-1 availability was
checked (binary present, `~/.codex/auth.json` present), so tiers 2/3 were forbidden.

**Three passes. All three returned `REFUTED`; every finding was fixed and re-verified.**

| Pass | Receipt (`exit_status: 0`) | Verdict | What it broke |
|---|---|---|---|
| 1 | `arb-step-codexadversary-0bd5c04ee75c45a992052d9bfa9ad9f2` | REFUTED | fence was cardinality not identity; 5 hollow tests; docs on retired route |
| 2 | `arb-step-codexadversary-3da844475ab041a69f62249c42eb0113` | REFUTED | omission slipped both guards; REQ-11 categorically false; 12 doc sites survived |
| 3 | `arb-step-codexadversary-76971da7d2c04b09a65f1b2eaacfc038` | REFUTED | `surface_content_types` was itself an unwitnessed second copy; `{}` routes silent; 12 mirror sites |

**Pass 1 — the load-bearing one.** By mutation testing it proved **five** covering tests
survived deliberately broken production behavior, and that `_root_contract_errors` checked
`len(declared) > 1` — *singleton*, not *root identity*. Changing the manifest and
`_FALLBACK_ROUTES` coherently to `["codex"]` passed validation and all five fence tests,
refuting this OBPI's stated objective. **Resolved:** the check is now
`list(declared) != [_ROOT_CONSUMER]` on both arms; the five substituted/half-covering tests
were rewritten against their REQs' actual subjects.

**Pass 2.** Confirmed pass 1's repairs bite (both new tests go red under a restored
cardinality mutant; restoration byte-exact by SHA-256) and found that both identity checks
guard OPTIONAL structures, so *deleting* a key skipped the guard — the invariant degraded to
*"exactly root, if declared"*. **Resolved:** `_missing_setpoint_error` couples the setpoint
obligation to the route. It also ruled that GHI #840's "latent, not live" was *"honest as a
description of today's artifacts … not a correctness defense"*, which the operator ruled
should be fixed rather than deferred.

**Pass 3.** Confirmed REQ-0.35.0-09-11 is now literally true (`root=True claude=False
candidate=False`) and its covering test non-hollow (`negative-control observed_red=True`), and
named as **weakest point** that `surface_content_types` *"recreates the exact two-copies,
comment-says-synchronize, nothing-binds failure class this OBPI is meant to eliminate."*
That was correct and is the finding this OBPI most needed to hear: the #840 remedy had arrived
in the very shape `REQ-0.35.0-09-09` exists to forbid. **Resolved:** the agreement arm now
witnesses `surface_content_types` against `_FALLBACK_SURFACE_CONTENT_TYPES` on the same terms
as the route table, and the `routes and …` truthiness guard was dropped so a blanked route map
is divergence rather than absence.

**Post-repair verification** (the tree being attested): lint `arb-ruff-e523208311b749c2b043a2259369dd87`;
typecheck `arb-step-typecheck-cdb4a25d2c1440938621d9704bf889a5`; tests
`arb-step-unittest-9fa48c68f2b14ff9a634c52b42455212` (8542 pass); docs
`arb-step-mkdocs-62eb323aa526468382fdf97417759362`; ten `gz validate` scopes exit 0;
`gz covers` reports 0 uncovered BEHAVIOR REQs.

**Residual, disclosed rather than closed.** Pass 3's findings were fixed but a *fourth* pass
was not run — the operator ruled to complete on the standing evidence rather than continue the
loop. Every pass-3 finding was re-verified by the same probes the adversary used (pasted in
this session), not by assertion. The RED falsifiability witness (`gz arb red`) remains
degraded by GHI #839 for this OBPI — it reported `failure_class: none` for all ten BEHAVIOR
REQs because it resolves its base as `HEAD`, which already contains the production code.
Independent mutation testing across three adversary passes stood in for it, and found real
defects the witness could not have.

### Value Narrative

`AgentContract` was routed to two per-vendor consumers (`claude`, `codex`) across three
surfaces that had each drifted from the root-contract doctrine, none of which was ever ruled
and none of which carried a mechanical witness. The correct fact and the drift sat ~100 lines
apart in one module. Now there is ONE rendition, played back verbatim to root `AGENTS.md`, and
a fence that fails closed on any attempt to re-vendor it — in JSON or in code. The `lite`
setpoint becomes falsifiable because the file being graded is the file every harness reads.

### Key Proof


```text
$ uv run python -c "... routes_for('AgentContract') ... render_agents_md ..."
routed consumer: root | rendition bytes: 39996 | delivered AGENTS.md bytes: 39996
```

One consumer; rendition bytes identical to the delivered contract — verbatim playback, no
reflow, no substitution. And the fence refuses the re-vendoring that previously passed:

```text
content_type_routes.AgentContract declares [codex], but there is exactly one root
contract and it is served by the single consumer 'root'.
```

### Implementation Summary


- **Routing collapse:** `sync_agents_md` / `render_agents_md` take the consumer as a
  parameter; `data/vendor-manifest.json` and `vendors._FALLBACK_ROUTES` declare
  `AgentContract: ["root"]`; playback is bootstrap-safe for an unrouted consumer
  (no write, no raise).
- **Root-identity fence:** `vendor_manifest.py` asserts `list(declared) != [_ROOT_CONSUMER]`
  on the route AND temperature arms (was `len(...) > 1`, which passed a coherent
  re-vendoring), plus `_missing_setpoint_error` coupling the setpoint obligation to the route.
- **Second-copy witnesses:** the agreement arm now binds `surface_content_types` as well as
  `content_type_routes`, and treats an empty route map as divergence rather than absence.
- **GHI #840 closed:** new `surface_content_types` authority (manifest + schema + fallback
  mirror) read by `vendors.content_type_for_surface`; `is_graded_rendition` scopes the route
  test to the OWNING content type instead of unioning all of them.
- **Files modified:** `src/gzkit/governance/trust_audits/vendor_manifest.py`,
  `src/gzkit/content/vendors.py`, `src/gzkit/content/rendition_store.py`,
  `src/gzkit/sync_surfaces.py`, `src/gzkit/schemas/vendor_manifest.json`,
  `data/vendor-manifest.json`, `docs/user/runbook.md`, `docs/user/manpages/content.md`,
  `docs/user/skills/gz-content-compose.md`, `docs/user/skills/gz-advisor-qc.md`,
  `docs/governance/agent-control-surface-rendering-substrate.md`,
  `.gzkit/skills/gz-advisor-qc/SKILL.md` (0.1.0 -> 0.2.0) + regenerated mirrors, this brief.
- **Tests added/repaired:** 6 added across `tests/content/test_vendor_manifest.py`,
  `tests/governance/test_rendition_floor_coherence.py`,
  `tests/governance/test_surface_delivery_witness.py`, `tests/test_sync_surfaces.py`;
  5 rewritten against their REQs' actual subjects after pass 1 proved them hollow;
  1 attested test (`REQ-0.0.37-22-03`) repaired at the surface per
  `governance-core.md` § attested-REQ-subject-retirement. Suite 8536 -> 8542.
- **Date completed:** 2026-08-21
- **Attestation status:** operator-verbatim, recorded at completion
- **Defects noted:** GHI #840 fixed here; GHI #839 (RED witness base resolution) and
  GHI #815 (delivered surface 7,228 B over the Codex cap) remain OPEN and out of scope;
  runbook Gate-5 naming routed to GHI #822. See § Tracked Defects.

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

- **GHI #840 — FIXED 2026-08-21 under operator ruling; ready to close on this commit.**
  `is_graded_rendition` routed by the union across all content types, so a consumer routed
  for a *different* content type was graded under this surface — a retained `claude.md`
  under `AGENTS.md/` would be graded because `claude` routes Rule, Skill, Persona and four
  others. It was latent (no such file on disk) but `REQ-0.35.0-09-11` was **categorically
  false**, which the tier-1 adversary refused to accept as shippable and the operator ruled
  should be fixed rather than deferred or narrowed.
  **The remedy is the first of the two the earlier note called design calls:** a
  `surface_content_types` map in `data/vendor-manifest.json` (schema-admitted; mirrored by
  `vendors._FALLBACK_SURFACE_CONTENT_TYPES`) declaring `AGENTS.md -> AgentContract`, read by
  the new `vendors.content_type_for_surface`. It is seated in the file that ALREADY owns
  routing rather than as a second authority elsewhere — which is what made it a small change
  instead of the drift this OBPI is undoing. The `RenditionProvenance` alternative was not
  taken: it would have required writing a new field into frozen, corpus-attested sidecars.
  An **unmapped** surface still falls back to the union, deliberately and in the docstring:
  the map answers "which content type owns this surface", and for an undeclared surface the
  honest answer is "unknown", under which "routed for something" beats grading nothing.
  Covered by `test_a_consumer_routed_for_another_content_type_is_not_graded_here`, which
  reproduces the adversary's exact repro and was watched failing
  (`['AGENTS.md/claude', 'AGENTS.md/root'] != ['AGENTS.md/root']`) before the fix.

- **`tests/governance/test_rendition_freshness.py::test_consumers_checked_independently`
  was resting on the #840 defect and was repaired, not deleted.** It hosted its property on
  `AGENTS.md` with `claude` as the second consumer, chosen — per its own prior comment —
  because `claude` "still routes for Rule/Chore/Persona/etc.", i.e. on the very union #840
  names. It carries `@covers("REQ-0.0.37-22-03")` from **terminal** `ADR-0.0.37`, so the
  `.claude/rules/governance-core.md` § attested-REQ-subject-retirement path applies: the
  REQ's subject (consumers scored INDEPENDENTLY) is untouched by the ruling, so the
  assertion is kept true and the proof-channel binding kept attached. Only the venue moved,
  to an unmapped surface — `AgentContract` now has exactly one route by doctrine, so two
  GRADED consumers under `AGENTS.md` is unreachable by construction, and the new venue also
  covers the unmapped-surface fallback branch.
- The Step 4b adversary's other named production defect, `REQ-0.35.0-09-03`, was FIXED in
  this OBPI rather than tracked: `sync_agents_md` raised `TemplateNotFound` for a consumer
  with no committed rendition, which the REQ forbids in its own words.

- **Runbook § content-surface still names the corpus attestation "Gate 5"** —
  `docs/user/runbook.md:1214`, `:1224`, `:1227`. GHI #822's 2026-08-18 rename swept
  `content/commit.py`, `content/__init__.py`, `docs/user/manpages/content.md`, `ADR-0.35.0`
  and seven of its briefs; the runbook was not in that set. Observed 2026-08-21 while
  repointing the same section's `--consumer` examples off the retired `codex` route. NOT
  fixed here: this is GHI #822's subject, not this OBPI's route collapse, and line 1214
  ("evidence for the operator at Gate 5") needs a doctrine reading on whether it is one of
  the genuine `cite at Gate 5` references that rename deliberately left alone. Routed to
  the operator rather than resolved in flight (`AGENTS.md` § Behavior Rules — Always #9).
  Still OPEN after the 2026-08-21 allowlist amendment: that ruling widened scope to the
  `--consumer codex` ROUTE prose, which is this OBPI's subject, while the Gate-5 /
  corpus-attestation NAMING is GHI #822's subject and is left where it belongs.

- **The delivered surface is 39,996 B against the Codex 32,768 B cap — 7,228 B OVER**, as
  the surface-delivery witness reports on every `gz check`. This is GHI #815 and is
  explicitly OUT of scope per this brief's § Scope Boundary: the OBPI wires the pipe and
  installs the fence, and which prose survives into a single ≤32,768 B rendition is a
  `gz content compose` + corpus-attested `commit` driven by the `instructions-files-diet`
  chore. Recorded here because the route collapse is what made the overage *measurable
  against the delivered file* rather than against a rendition nothing read.

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.35.0-09 collapses AgentContract to a single `root` rendition played back verbatim to root AGENTS.md (rendition bytes 39996 == delivered AGENTS.md bytes 39996), and replaces the cardinality check that had passed a coherent re-vendoring to ["codex"] with a root-IDENTITY fence on both the route and temperature arms. Three tier-1 Codex adversary passes all returned REFUTED and every finding was fixed and re-verified, not argued away: five covering tests that survived deliberately broken production behavior were rewritten against their REQs' actual subjects; the setpoint obligation was coupled to the route so omission cannot skip the guard; GHI #840 was closed with a new surface_content_types authority making REQ-0.35.0-09-11 literally true rather than narrowed to fit; and that authority was then bound to its in-code mirror after the adversary correctly named it as the same two-copies-one-binds shape this OBPI exists to remove. Twelve operator-facing documentation sites were swept off the retired codex route under an operator-ruled allowlist amendment. Verified on the attested tree: arb-ruff-e523208311b749c2b043a2259369dd87, arb-step-typecheck-cdb4a25d2c1440938621d9704bf889a5, arb-step-unittest-9fa48c68f2b14ff9a634c52b42455212 (8542 pass), arb-step-mkdocs-62eb323aa526468382fdf97417759362, ten gz validate scopes exit 0, gz covers 0 uncovered BEHAVIOR REQs. Adversary receipts arb-step-codexadversary-0bd5c04ee75c45a992052d9bfa9ad9f2, arb-step-codexadversary-3da844475ab041a69f62249c42eb0113, arb-step-codexadversary-76971da7d2c04b09a65f1b2eaacfc038. Disclosed and NOT claimed clean: no fourth adversary pass ran (operator ruled to complete on standing evidence), GHI #839 leaves the RED witness degraded for this OBPI, and GHI #815 and #822 remain open and out of scope.
- Date: 2026-08-21

---

**Date Completed:** 2026-08-21

**Evidence Hash:** -
