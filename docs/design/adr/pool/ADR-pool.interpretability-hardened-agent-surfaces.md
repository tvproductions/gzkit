---
id: ADR-pool.interpretability-hardened-agent-surfaces
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by:
  - Lindsey et al. 2025 (Anthropic interpretability — "On the Biology of a Large Language Model")
  - GHI #141 (canonical tool/skill/runbook drift violation)
---

# ADR-pool.interpretability-hardened-agent-surfaces: Interpretability-Hardened Agent Surfaces

## Status

Pool

## Date

2026-04-14

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Three of gzkit's governance surfaces rely on narrative discipline (authoring
conventions, advisory rules) in places where interpretability research now
suggests structural binding is required. Each surface is load-bearing and
has an observed violation trigger:

1. **Attestation enrichment** binds agents' claims about lint/test/coverage
   to session recall, which is structurally unreliable: the reporting
   pathway and the execution pathway are separate circuits (Lindsey et al.
   2025 — the math-explanation pathway is distinct from the math-execution
   pathway). The only faithful record of a QA step is the wrapped-command
   receipt.

2. **Mirror surfaces** (`.claude/`, `.github/`) are editable by default. The
   canonical rule in `skill-surface-sync.md` says "edit `.gzkit/` first",
   but agents instinctively edit the mirror because it is the path of least
   resistance. The doctrine of "refusal by default, override by feature"
   from Lindsey et al. 2025 applies: mirror writes should be denied by
   default and allowed only when the invoker is the sync command.

3. **Tool↔skill↔runbook alignment** is advisory per
   `tool-skill-runbook-alignment.md`. GHI #141 is the canonical violation:
   `gz adr status` is live, runbook-prescribed, and wielded by four skills,
   but no skill routes operators to it via discovery; `gz-adr-status`
   instead routes to `adr report`. The failure mode mirrors "known-answer
   misfire → hallucination" from Lindsey et al. 2025 — the skill layer
   suppresses the refusal default while the capability layer shows no
   matching verb.

The three surfaces share a single architectural intent: **agent-facing
surfaces must bind to structural evidence, not narrative recall**.
Interpretability hardening means replacing "agent will remember to do X" with
"the system will not let agent X drift."

## Design Tensions

| Tension | Option A | Option B |
|---------|----------|----------|
| **Enforcement breadth** | All three surfaces hardened in one patch release | Incremental — one surface per patch release, observe adoption between |
| **Lite vs. Heavy per surface** | All Heavy (CLI contract changes, hook surface, validation semantics) | Mirror hook Lite (settings-only), other two Heavy |
| **Receipt-ID validation granularity** | Parse receipt IDs out of `--attestation-text` and verify each | Require a new `--receipt` repeated flag, reject attestation without it |
| **Mirror hook scope** | Deny all Edit/Write under mirror paths, allow only via sync env marker | Warn-only v1, deny in v2 |
| **Surface invariants** | Hard fail `gz validate --surfaces` on any missing skill-to-verb link | Warn on first run, fail after a grace window |

## Potential OBPI Decomposition (Sketch)

1. **ARB receipt-ID binding for attestation** (GHI #145)
   - Parse receipt IDs out of `--attestation-text` / `--attestor`
   - Verify each cited receipt exists under `artifacts/receipts/` and status matches claim
   - Lane behavior: Lite warn, Heavy fail-closed
   - Update `gz obpi complete` and `gz adr emit-receipt`

2. **Mirror-edit deny hook** (GHI #146)
   - Pre-write hook script added under `.claude/hooks/`
   - Registered in `.claude/settings.json` for Edit/Write on
     `.claude/skills/**`, `.claude/rules/**`, `.github/skills/**`,
     `.github/instructions/**`
   - Bypass via sync-command environment marker
   - Deny message routes agent to canonical `.gzkit/` path

3. **Surface invariant checks in `gz validate --surfaces`** (GHI #144)
   - Invariant 1: every CLI verb in `src/gzkit/cli/**` referenced by at
     least one skill via `gz_command:` frontmatter or body invocation
   - Invariant 2: every skill's `gz_command:` matches a runbook-prescribed
     verb for the operator moment implied by the skill name
   - New validation failure modes, exit code propagation
   - Heavy lane: manpage + behave smoke + ADR

## Dependencies

- ARB receipt system is already present (`arb_lint_receipt.schema.json`,
  `artifacts/receipts/`). Consolidation with ADR-0.27.0 (ARB absorption)
  only if both move together.
- Claude hook infrastructure is already present (see
  `.claude/hooks/plan-audit-gate.py`). No new runtime needed — only a new
  hook script and registration.
- `gz validate --surfaces` is an existing verb; the change is adding new
  invariant checks, not a new subcommand.

## Consequences (if promoted)

**Positive:**

- Attestation becomes structurally faithful — no more narrative-only claims
- Mirror drift becomes impossible by construction, not by rule-reading
- Tool↔skill↔runbook alignment becomes mechanically verifiable
- Interpretability-driven safety framing carries forward to future surfaces

**Negative:**

- Heavy-lane ADR ceremony cost (three OBPIs, gates 1–5 each)
- Risk of hook-bypass surface area (agents will look for escape hatches)
- Initial `gz validate --surfaces` failure if existing skills are drifted
  (GHI #141 is the known violation; likely not the only one) — requires a
  reconciliation pass before the new checks can be enabled

**Neutral:**

- Pairs well with the doctrine-only patch that landed alongside this pool
  entry (GHI #147, #148, and #145 rule-half): doctrine establishes the
  intent, this ADR mechanizes it.

## Sibling doctrine (already landed)

Three sibling GHIs landed doctrine-only updates in the same patch release:

- **GHI #147** — `gz-plan-audit` Step 6a plan-before-exploration ordering
  check; `gz-design` Step 3 rejected-alternatives requirement. Advisory v1.
- **GHI #148** — OBPI increment-size reframed as a safety property (gate
  firing point) in `gz-obpi-specify`; new constraint row in
  `constraints.md` Pipeline Lifecycle.
- **GHI #145 (rule half)** — `attestation-enrichment.md` now carries a
  Receipt-ID Requirement section with Lite/Heavy lane semantics. The CLI
  enforcement half (OBPI 1 above) is what this pool entry promotes.

Those updates establish the doctrinal baseline. This pool entry, when
promoted, mechanizes the three surfaces that cannot rely on doctrine alone.

## Origin

Identified 2026-04-14 during GHI triage after authoring #144–#148. The
three code-changing GHIs (#144, #145, #146) do not fit cleanly under any
existing absorption ADR (0.27, 0.34, 0.36) — those absorption ADRs are
structured around the opsdev-to-gzkit parity matrix and absorbing
interpretability-hardening work into them would scope-creep the Absorb/
Compare/Evaluate decision. Per architectural boundary memo rule #5,
interpretability hardening is a gzkit-native innovation and should not
travel through the absorption-ADR surface.

## Promotion Notes

When promoting:

- Confirm this has not been subsumed by a later ARB or hook ADR
- Verify GHI #144, #145, #146 are still open and aligned with the OBPI
  sketch above
- Lane: Heavy (per GHI acceptance criteria)
- Minor odometer bump (gzkit post-0.40.x runtime track)
- Run `gz-adr-evaluate` on promotion to confirm rationale quality before
  scoping OBPIs
