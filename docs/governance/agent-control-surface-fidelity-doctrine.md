# Agent Control Surface Fidelity Doctrine

> **North star.** Agent = Model + Harness + Intent. Harness = vendor harness (Claude Code, Codex, Copilot) + local extension (gzkit is the local extension layer). The **Agent Control Surface** is the per-turn corpus the harness loads on the model's behalf — `AGENTS.md`, `CLAUDE.md`, `.claude/rules/**`, skill bodies, the chore registry, persona files, handoffs. **gzkit is control surfaces and tools designed so that operator intent makes the model's intrinsic weaknesses and negative tendencies inert.**
>
> This doctrine governs that surface's fidelity to its declared rules.

## Binding claim

> **The Agent Control Surface preserves every binding rule from its canonical sources to its rendered output. Surface weight does not regress past tested floors. Pointers resolve. Bullets are reachable from the loading scenarios they should fire in. Drift in the rendered surface is detectable at compile time, not at audit time.**

This is gzkit's structural backstop for every other governance pillar. PRIME DIRECTIVE assumes the rule is loaded; DO IT RIGHT assumes the doctrine is reachable; the anti-vibing mantra assumes the contract is intact. Without surface fidelity, those upstream pillars cannot be enforced — a silently-missing rule is invisible to the discipline that depends on it.

## Why this doctrine is foundation-tier

By the invariance test (foundation = "without it, we wouldn't be doing the project"):

- gzkit's purpose is to make stochastic LLM vibing structurally inert at the agent control surface.
- Every other gzkit pillar — PRIME DIRECTIVE, DO IT RIGHT, anti-vibing mantra, Stdlib-First, Operator Economy — operates on the assumption that the contract surface the agent reads per turn is faithful to its declared rules.
- That assumption is structurally untested today. The diet pass GHI #327 surfaced one consequence: operators (and agents) can edit the per-turn surface in ways that silently drop bullets, regress weight, or break pointers, and existing validators do not catch it.
- ADR-0.14.0 and ADR-0.16.0 closeouts both record the failure pattern: heavy-lane parents with self-closed lite-lane child OBPIs, missing brief-level attestation, dirty-worktree receipts, ADRs whose titles promised more than their deliverables. Surface fidelity validators are designed to surface this class structurally.

This is a structural backstop for the upstream pillars, **not a corollary**. If Surface Fidelity fails, the upstream pillars cannot be enforced — a missing rule is invisible to PRIME DIRECTIVE because PRIME DIRECTIVE assumes the rule is loaded.

## Derivation from upstream pillars

This doctrine derives from existing canon, not adjacent to it:

- **PRIME DIRECTIVE #5 (FLAG DEFECTS, NEVER EXCUSE THEM):** drift in the agent control surface is itself a defect class; the doctrine names that class and the validators surface its instances.
- **DO IT RIGHT #1 (fix the class of failure, not the instance):** "blind reduction" of the per-turn surface during a diet pass, or silent rule loss during sync, is a class of failure; the doctrine closes the class with bullet-retention, weight-regression, and pointer-integrity validators.
- **DO IT RIGHT #4 (verify observed behavior, not assumed behavior):** today, we assume the per-turn surface preserves its rules; this doctrine makes that observable, not assumed.
- **MAKE LLM STOCHASTIC VIBES INERT operative claim 3 ("doctrine drift is invariant drift"):** silent loss of a binding rule from the per-turn surface is doctrine drift; mechanical detection is the structural defense.
- **OPERATOR ECONOMY pillar:** the rendered Agent Control Surface is the operator's primary review surface for governance authoring; fidelity is what makes that review trustworthy.

The doctrine does not introduce a new philosophical claim. It names what the upstream pillars already imply and gives that implication mechanical teeth.

## Substrate-invariance

This doctrine is invariant across implementation eras (per ADR-0.0.34 — Agent Control Surface Rendering Substrate):

- **Era 1 — today:** hand-authored + partial-templated static files. Validators grep against rendered output and the limited canonical sources that exist (`src/gzkit/templates/agents.md`, `.gzkit/rules/**`).
- **Era 2 — substrate landed:** Pydantic content models + Jinja2 templates render the full surface. Validators diff canonical models against rendered output; tests are sharper.
- **Era 3 — progressive disclosure:** scenario-aware retrieval composes per-turn surface on demand. Validators check the per-scenario render; canonical bullet-retention claims become bullet-reachability-from-scenario claims.

In every era, the agent reads a static document. What changes is composition method. **The doctrine's invariants survive transitions; validators evolve to test the active composition method.** Errors in the rendered output become feedback to whatever composition method is active.

## The four invariants

### Invariant 1 — Bullet retention

Every bullet on the canonical advisory scorecard (`docs/governance/advisory-rules-audit.md`) classified Mechanical or Promotable MUST be present, verbatim, in the per-turn agent control surface (or — once Era 2 lands — in the canonical Pydantic content model that renders the surface).

**Mechanical check (Era 1):**

```bash
uv run gz validate --bullet-retention
```

Reads the advisory scorecard for Mechanical/Promotable rows; asserts each bullet's substring presence in the union of `AGENTS.md` + `CLAUDE.md` + `.claude/rules/**`. Exit 3 on any missing bullet.

**Mechanical check (Era 2):**

Diff canonical Pydantic content models against the advisory scorecard; assert every Mechanical/Promotable bullet is registered as a `Bullet` instance in some `AgentContract.pillars[*].bullets` (or equivalent per surface).

### Invariant 2 — Surface weight regression

The total per-turn agent control surface line count (Era 1) or canonical-model bullet count (Era 2) MUST NOT regress past the recorded floor without an explicit waiver entry citing rationale.

Direction-binding (no growth past current snapshot) is fail-closed. Absolute warning bands grounded in literature (HumanLayer / Builder.io / TestQuality 2026) fire as warnings with mandatory waiver entries:

| Band | Per-turn lines | Action |
|---|---|---|
| Green | ≤ 1800 | No action |
| Yellow | 1801 – 2200 | Warn; require waiver entry in `data/surface_weight_waivers.json` with rationale and ARB receipt |
| Red | > 2200 | Fail closed |

Bands are **provisional.** Recalibration cadence is 6 months minimum, against operational evidence. Recalibration is itself a doctrine artifact; band edits require attestation.

**Mechanical check:**

```bash
uv run gz validate --surface-weight
```

Reads `data/surface_weight_floor.json` (snapshot + waivers); asserts current per-turn line count is within green or yellow-with-waiver. Exit 3 on red without waiver; exit 0 with warning on yellow with valid waiver.

### Invariant 3 — Pointer integrity

Every `> See [...](path#anchor)` lift pointer in the per-turn agent control surface MUST resolve to an existing destination heading anchor. Lifted-pedagogy pages MUST carry a `<!-- lifted-from: <path>#<anchor> -->` HTML comment naming each origin, and the origin MUST carry the back-pointer.

**Mechanical check:**

```bash
uv run gz validate --pointer-anchors
```

Parses every `> See [...]` blockquote pointer in `AGENTS.md` + `CLAUDE.md` + `.claude/rules/**`; resolves each to its destination file and anchor; asserts the anchor exists. Reverse-checks: every `<!-- lifted-from: -->` comment in `docs/governance/**` has a matching back-pointer at the origin. Exit 3 on any unresolved pointer.

### Invariant 4 — Loading-scenario reachability

Every Mechanical/Promotable bullet MUST be reachable from at least one declared loading scenario. No bullet may be present in a canonical source but unreachable by any scenario's loading rules.

A loading scenario is the (vendor harness × operator moment) tuple that the harness honors when deciding what to load. Today these are implicit in `paths:` frontmatter (Claude Code) and equivalent vendor-specific scoping. The substrate doctrine (ADR-0.0.34) commits to making them explicit as a registry; this doctrine commits to validating reachability against that registry.

**Mechanical check (Era 2 onward):**

```bash
uv run gz validate --scenario-reachability
```

Reads `data/agent-control-surface-scenarios.json` (the loading-scenarios registry); asserts every Mechanical/Promotable bullet is reachable from at least one scenario's loading rules; warns on bullets reachable from zero scenarios (orphans). Exit 3 on any orphan with no waiver.

**Era-1 fallback:** since the registry does not yet exist as a canonical artifact, this validator runs in advisory mode (warning only) until ADR-0.0.34 substrate work lands the registry.

## Levers and constraints

| Layer | Lever (gzkit owns) | Constraint (gzkit accepts) |
|---|---|---|
| Canonical authorship | Pydantic content models (Era 2); rule frontmatter (Era 1); validator suite | — |
| Rendering | Jinja2 templates (Era 2); naive substitution (Era 1); deterministic byte-stable output | — |
| Vendor mirror sync | Mirror-fidelity validation; canonical-source authority | Vendor harness honors its own loading semantics; gzkit's templates adapt to vendor format changes |
| Loading per turn | — | Vendor harness decides what loads (path-scoped frontmatter for Claude Code, equivalent for Codex/Copilot) |
| Within-turn dynamics | — | Context window is append-only at runtime; "forgetting" exists only between turns |

The doctrine works the levers gzkit owns to shape outcomes within constraints gzkit does not control. **Resilience comes from precision-scoping: the doctrine governs what gzkit composes and validates, not what the vendor harness loads at runtime.** Composition is between turns; validation is on every render and every save; runtime loading is the vendor's call.

## Composite + narrow scopes

Validators wire up under both composite and narrow `gz validate` scopes, matching gzkit's existing pattern:

```bash
# Composite — runs all four invariants
uv run gz validate --surface-fidelity

# Narrow — granular CI signal
uv run gz validate --bullet-retention
uv run gz validate --surface-weight
uv run gz validate --pointer-anchors
uv run gz validate --scenario-reachability
```

`gz check` includes `--surface-fidelity` in its default pipeline. Pre-commit hooks include the cheap structural checks (bullet retention + weight + pointer anchors); scenario reachability is CI-only until the registry lands.

## Test surface

Tests live under `tests/governance/` per the per-rule-file naming pattern:

- `tests/governance/test_bullet_retention.py` — REQ-derived assertions per `.gzkit/rules/tests.md` § Tests assert semantics, not strings. Asserts each Mechanical/Promotable bullet is present in the per-turn surface; named per the eval-awareness corollary (no `assert_audit_passes`-shaped names).
- `tests/governance/test_surface_weight.py` — asserts current per-turn line count is within band; exercises waiver-entry validation; pins the snapshot file's schema.
- `tests/governance/test_pointer_integrity.py` — parses pointers; resolves anchors; pins the `<!-- lifted-from: -->` comment shape.
- `tests/governance/test_scenario_reachability.py` — Era-2-onward; asserts bullet-to-scenario reachability against the registry.

Tests run as part of `gz test`; `gz check` includes the validator pipeline; pre-commit fires the cheap subset.

## The pattern (D2 framing — name the pattern, not the ADRs)

The validators are designed to surface the following failure pattern wherever it occurs:

- A canonical source declares a binding rule
- An editorial pass (diet, refactor, sync, ADR closeout) modifies the rendered output without preserving the rule
- The closeout completes despite reflection-issues recording attestation gaps
- The drift is invisible until an operator catches it months later

The doctrine does not name specific ADRs in this page. The validators surface the historical instances when they sweep; the audit is where the named drift surfaces. This is the appropriate separation: the doctrine names the failure class structurally; the audit names the instances empirically.

## Anti-patterns

- **Treating frontmatter `status: Validated` as proof.** Per State Doctrine, frontmatter is Layer-1 authorship; the ledger is Layer-2 truth. Fidelity audits read the ledger.
- **Self-closing brief-level attestation on a heavy-lane or foundation-kind parent.** Per the OBPI Acceptance Protocol Lane & Kind Attestation Matrix, both axes alone force human attestation at the brief level. The validators assert this constraint.
- **Capturing OBPI completion receipts from a dirty worktree.** Receipts captured against superseded anchors are a fidelity signal. The validators flag `recorder_warnings: ["Working tree was dirty when the completion receipt was captured."]` entries in the ledger.
- **Letting a Mechanical or Promotable bullet drift to "redundant, can be cut."** Bullet retention is binary. Cutting requires advisory-scorecard reclassification first; reclassification is itself an attested doctrine artifact.
- **Speculative line-count floors.** The warning bands are provisional; recalibration is the load-bearing artifact, not the band edges. Treat the bands as guidance until operational evidence supports tightening.

## Calibration commitment

Warning bands and absolute floors are provisional. Recalibration runs no more frequently than every 6 months, against operational evidence accumulated under the validators' running history. Each recalibration is itself a doctrine artifact: PR + attestation + ADR-CLOSEOUT-FORM-style evidence row. Recalibration without evidence is a doctrine violation.

## Related canon

- **ADR-0.0.34 (paired foundation, this cluster):** Agent Control Surface Rendering Substrate. The substrate this doctrine's validators evolve to test against in Era 2.
- **ADR-0.0.19 (Validated, foundation):** `gz justify` — the Pydantic+Jinja2 deterministic rendering precedent; reference implementation for round-trip fidelity.
- **ADR-0.0.18 (foundation):** ADR Taxonomy Doctrine. Foundation-kind brief-level attestation rigor; the Lane & Kind Attestation Matrix the validators enforce.
- **ADR-0.16.0 (closed, drifted):** "CMS Architecture Formalization" — partial prior. The substrate doctrine generalizes its scope; the fidelity doctrine's validators retroactively flag its closeout drift in audit.
- **ADR-0.0.33 (airlineops, Pool):** Agent Context Engineering. 12-Factor Agents Factor 3 (Own Your Context Window), Factor 9 (Compact Errors). Cross-project validation of the territory.
- **`docs/governance/advisory-rules-audit.md`:** the scorecard the bullet-retention validator reads; canonical classification of every binding rule.
- **`docs/governance/state-doctrine.md`:** Layer 1 / Layer 2 / Layer 3 framing; fidelity audits read Layer 2.
- **`docs/governance/trust-doctrine.md`:** trust-chain T1/T2/T3 invariants; this doctrine fires at T2 (the rendered output the agent reads).

## Origin

GHI #327 — instructions-files-diet pass surfaced the empirical question: "how do we know we didn't reduce blindly?" The honest answer is that today's gzkit cannot answer that question structurally. This doctrine is the structural answer.

## Behavioral test layer (deferred follow-up)

The four invariants are *structural* — they answer "did the rule survive the edit?" The complementary *behavioral* test layer answers "does the agent comply with the rule when the surface is loaded?" That layer requires a golden-dataset of (input, expected behavior) pairs and LLM-as-judge or assertion-based grading; it is materially more expensive and less deterministic. The behavioral layer is acknowledged here as the second tier of fidelity testing; its design lives under a separate follow-up GHI to be authored when the structural layer is operating.

Structural-without-behavioral is not full fidelity. Behavioral-without-structural is testing against a corpus that may have already silently lost rules. The mature stack runs both. This doctrine commits to the structural layer; the behavioral layer is named, deferred, and tracked.
