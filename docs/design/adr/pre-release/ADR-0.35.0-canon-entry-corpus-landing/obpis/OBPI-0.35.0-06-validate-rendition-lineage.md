---
id: OBPI-0.35.0-06-validate-rendition-lineage
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 6
lane: Heavy
status: Draft
allowlist:
- src/gzkit/governance/trust_audits/rendition_lineage.py
- src/gzkit/governance/trust_audits/__init__.py
- src/gzkit/cli/parser_maintenance.py
- src/gzkit/governance/trust_audits/_qc_negative_controls.py
- src/gzkit/governance/trust_audits/_qc_nc_entrypoints.py
- src/gzkit/commands/validate_cmd.py
- src/gzkit/quality.py
- src/gzkit/commands/quality.py
- src/gzkit/qc_binding.py
- src/gzkit/governance/trust_audits/_qc_claim_exemptions.py
- data/check_scope_membership.json
- data/check_step_concurrency.json
- tests/governance/test_rendition_lineage.py
- tests/cli/test_validate_registry_parity.py
- features/rendition_lineage.feature
- features/steps/rendition_lineage_steps.py
- docs/user/manpages/validate.md
- docs/governance/governance_runbook.md
- docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-06-validate-rendition-lineage.md
reqs:
- REQ-0.35.0-06-01
- REQ-0.35.0-06-02
- REQ-0.35.0-06-03
- REQ-0.35.0-06-04
- REQ-0.35.0-06-05
- REQ-0.35.0-06-06
- REQ-0.35.0-06-07
- REQ-0.35.0-06-08
verification:
- uv run -m unittest tests.governance.test_rendition_lineage
- uv run -m behave features/rendition_lineage.feature
- uv run gz lint
- uv run gz typecheck
- uv run gz test
- uv run gz validate --rendition-lineage
- uv run gz validate --documents
- uv run gz validate --req-kind-discipline
- uv run gz cli audit
- uv run mkdocs build --strict
tasks:
  - TASK-0.35.0-06-01-01
  - TASK-0.35.0-06-02-01
  - TASK-0.35.0-06-03-01
  - TASK-0.35.0-06-04-01
  - TASK-0.35.0-06-05-01
  - TASK-0.35.0-06-06-01
  - TASK-0.35.0-06-07-01
  - TASK-0.35.0-06-08-01
---

# OBPI-0.35.0-06-validate-rendition-lineage: Validate Rendition Lineage

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #6 - "gz validate --rendition-lineage -- fail-closed over owned sections, coverage % surfaced to Fidelity Assertions"

**Status:** Draft

## Objective

Ship gz validate --rendition-lineage: exit 0 when every owned section in a committed rendition is derivable from the effective corpus, exit 3 on hand-authored prose inside an owned section, unowned bytes reported as measured debt and never failed, and the coverage percentage surfaced so the gate's partial scope is declared rather than implied.

**Dependency order (ADR-0.35.0 § Scope Minimization):** 06 depends on 04 (the ownership declaration that defines the gate's scope) and 05 (the lineage map and the generator whose output the gate compares against). 04 is delivered; the instruction that 04 and 06 are cut together is a scope-retention rule, not simultaneous execution. This item completes enforcement over the delivered ownership declaration.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/governance/trust_audits/rendition_lineage.py` — the new validator scope **CREATE**
- `src/gzkit/governance/trust_audits/__init__.py` — scope registration
- `src/gzkit/cli/parser_maintenance.py` — argparse option and handler forwarding
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py` — live scope negative control (fixture builder + roster entry)
- `src/gzkit/governance/trust_audits/_qc_nc_entrypoints.py` — `_ep_rendition_lineage` runner the roster entry pairs with (allowlist amended pre-implementation; see Change Log)
- `src/gzkit/commands/validate_cmd.py` — handler/default-scope wiring
- `src/gzkit/quality.py`, `src/gzkit/commands/quality.py` — the `gz check` step runner and its `_STEP_GUARD_META` MX-severity entry, i.e. the AUTOMATIC CALLER GHI #785 requires for a newly authored gate (allowlist amended 2026-09-11 as a direct consequence of the operator's wire-the-caller ruling; see Change Log)
- `data/check_scope_membership.json` — declare `rendition_lineage` `in_check` (GHI #744's `gz validate --gate-callers`, in the default `gz check` bundle, fails closed on any registered `_ScopeEntry` absent from this file's `in_check`/`out_of_check` split; allowlist amended pre-implementation, see Change Log)
- `src/gzkit/qc_binding.py`, `data/check_step_concurrency.json`, `tests/cli/test_validate_registry_parity.py`, `src/gzkit/governance/trust_audits/_qc_claim_exemptions.py` — the remaining documented obligations of registering a `gz check` step (`src/gzkit/commands/quality.py:444` carries the list): a `_STEP_CLASSIFICATION` entry, a concurrency declaration, and the explicit-tier parity frozenset. Allowlist amended 2026-09-11, consequent on the same wire-the-caller ruling; see Change Log
- `tests/governance/test_rendition_lineage.py` — covering tests **CREATE**
- `features/rendition_lineage.feature`, `features/steps/rendition_lineage_steps.py` — **CREATE**, Gate 4 scenarios
- `docs/user/manpages/validate.md`, `docs/governance/governance_runbook.md` — the new scope
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-06-validate-rendition-lineage.md` — this brief's evidence sections

## Denied Paths

- `src/gzkit/governance/trust_audits/rendition_floor_coherence.py` — the existing invariant-floor gate is a sibling scope and stays as-is; its substring-test defect is discharged by OBPI-0.35.0-03, not rewritten here
- `src/gzkit/content/composer.py`, `src/gzkit/content/lineage.py` — the generator and lineage writer are OBPI-0.35.0-05 and are consumed read-only
- `src/gzkit/content/ownership.py` — OBPI-0.35.0-04, consumed read-only
- `AGENTS.md` — the gate measures the surface; it never edits it
- New dependencies, CI files, lockfiles
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. ALWAYS fail closed over OWNED SECTIONS ONLY. Unowned bytes are reported as measured debt and MUST NEVER contribute to a non-zero exit. A gate whose scope is partial and undeclared is the theater ADR-0.35.0 exists to remove.
2. ALWAYS surface the coverage figure in the scope's output — sections owned of total, bytes owned of total, and the percentage — using OBPI-04's owned-section UTF-8 spans over total section spans. Report effective-entry text bytes and per-section entry counts separately as population statistics; neither is the ratchet nor unique rendered-byte coverage. The authoring-era 31.2% is historical, not a target. The figure is asserted in the parent ADR's Fidelity Assertions and must be reproducible from this scope's output.
3. NEVER hardcode 31.2%, 8, 22, 9,966, or 22,378. Every figure is computed from the ownership declaration, the effective corpus, and the committed rendition at run time. A stored constant is a witness that cannot fail — the same defect class as the `ByteEvidence` inflation.
4. ALWAYS read the EFFECTIVE corpus (OBPI-0.35.0-01), never `load_corpus`'s raw return. A consumer left on the raw log is a one-line omission whose symptom is a GREEN gate over a rendition that omits canon — pre-mortem #3, the worst detection latency in this ADR.
5. ALWAYS emit three-part recovery prose on the exit-3 path per `.claude/rules/guardrail-feedback-prose.md`: which owned section drifted, that owned sections are corpus-derived by ADR-0.35.0 § Decision item 4, and the runnable next step.
6. NEVER present marking a section `unowned` as the recovery for a lineage failure. Pre-mortem #2 is that owned-section fail-closed becomes the thing agents route around, and the cheapest route is un-owning; the recovery prose must name the corpus round-trip, with the attested raise-path (OBPI-0.35.0-04) as a deliberate, attested move and never as the suggested escape.
7. ALWAYS resolve severity through the shared MX checkpoint the way `rendition_floor_coherence.py:47-51` does, so hangar behavior is consistent across the two content gates.
8. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Audit Contract

Read the declared active route set, not a glob of retained renditions. The public scope validates required committed renditions plus their committed lineage and
ownership; it does not require a retained candidate. Expose a pure verification function for
an explicitly supplied candidate/lineage pair, which 07 uses before publication. That
candidate check must not reject a valid repair because the old committed rendition is stale. CORRUPT
required lineage, duplicate/unknown section identities, missing/extra entry ids,
retired ids, overlapping or out-of-bounds byte spans, and wrong corpus/rendition bindings
fail closed. Derive the expected output independently from current effective corpus and
ownership; do not trust an artifact's self-reported owned flags or spans as evidence.

**AMENDED 2026-09-11 (operator-ruled): a lineage that has NEVER been published is not yet
"required", and its absence is DISCLOSED rather than fail-closed.** As originally written this
paragraph read "Missing or corrupt required lineage ... fail closed", which composed with
GHI #785 into a contradiction: a newly-authored gate MUST have an automatic caller
(`data/uncalled_gate_grandfather.json` forbids grandfathering a new gate verbatim — "NEVER add
an entry to silence a newly-authored gate ... that is the laundering ADR-0.0.73 Boundary
Invariant #8 forbids"), but wiring a caller for a gate that fail-closes on the live repo's
never-yet-published lineage would hold `gz check` red on every commit until OBPI-0.35.0-07
lands. The operator ruled the absence DISCLOSED: a surface declaring ownership with no
committed lineage has no graded scope at all, the scope exits 0, and the coverage figure
reports those sections as ungraded so the debt stays visible. This keeps the paragraph's own
first sentence — "read the declared active route set, not a glob of retained renditions" —
governing: an unpublished lineage is not a required committed artifact yet. Fail-closed
behaviour over owned-section drift (REQ-01 through REQ-06) is UNCHANGED wherever a committed
lineage exists; only the never-published case moved from refusal to disclosure. See Change Log
2026-09-11.

REQ-01/02 include these artifact-integrity controls and a registered negative control through
the public scope. REQ-03 permits arbitrary valid unowned content only when metadata is sound;
it is not an exemption for missing proof artifacts. REQ-04 verifies multibyte text, H1/preamble
accounting, section histograms, and recomputation after ownership changes. Population entry
bytes must never be labeled rendered coverage. REQ-06 proves the CLI parser reaches the scope.

Normal execution fails closed. MX checkpoint policy may downgrade findings according to its
explicit mode; downgraded findings remain reported and do not count as normal-mode proof for
landing or completion. The audit core returns findings independently of presentation severity
so 07 can reject any owned drift even in MX mode.

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

- [ ] ADR § Decision item 4 — owned-sections-only fail-closed, and why the coverage percentage is in Fidelity Assertions.
- [ ] ADR § Consequences (Negative) #1, #2 and #4 — thin coverage, the ratchet's missing forcing function, and the route-around risk this gate's recovery prose must not feed.
- [ ] ADR § Fidelity Assertions — two rows resolve to this scope; both expect exit 0.
- [ ] `.claude/rules/guardrail-feedback-prose.md` — the three-part bar every fail-closed surface must clear.

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.35.0-04 landed: `.gzkit/ownership/AGENTS.md.json` declares every AGENTS.md section
- [ ] OBPI-0.35.0-05 landed: `<consumer>.lineage.json` is emitted and the generator is deterministic
- [ ] OBPI-0.35.0-01 landed: `effective_corpus()` is the corpus read path
- [ ] `src/gzkit/governance/trust_audits/rendition_floor_coherence.py` exists — the sibling scope whose registration, MX-checkpoint, and `ValidationError` shape this scope mirrors
- [ ] `src/gzkit/commands/validate_cmd.py` exists and carries the scope-registration pattern

**Existing Code (understand current state):**

- [ ] `src/gzkit/governance/trust_audits/rendition_floor_coherence.py:32-105` — the whole sibling scope: MX checkpoint resolution, per-surface iteration, `ValidationError` construction, and the drift ledger event
- [ ] `src/gzkit/governance/trust_audits/rendition_floor_coherence.py:1-9` — the module docstring naming mtime comparison as the discredited fake witness this family of gates exists to replace
- [ ] `src/gzkit/commands/validate_cmd.py` — how a scope is registered and how `gz check` picks up its default scope set

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
uv run -m unittest tests.governance.test_rendition_lineage
uv run -m behave features/rendition_lineage.feature
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --rendition-lineage
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz cli audit
uv run mkdocs build --strict
```

## Demo

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz validate --rendition-lineage
uv run gz validate --rendition-lineage --json
uv run -m behave features/rendition_lineage.feature
```

## Acceptance Criteria

<!--
Each checkbox carries a deterministic REQ ID and exactly one kind tag
(ADR-0.0.59; `gz validate --req-kind-discipline`):
  [behavior]         -> proven ONLY by an @covers test in tests/**
  [support]          -> proven ONLY by a path-citing ledger event + structural validator
  [structural-fence] -> proven ONLY by a parent-ADR ## Boundary Invariants entry
-->

- [ ] REQ-0.35.0-06-01 [behavior]: Given a committed rendition whose every owned section matches the deterministic materialization of the effective corpus, when gz validate --rendition-lineage runs, then it exits 0.
- [ ] REQ-0.35.0-06-02 [behavior]: Given a committed rendition in which an OWNED section carries prose that is not derivable from the effective corpus, when the scope runs fail-closed, then it exits 3 and names the offending section id.
- [ ] REQ-0.35.0-06-03 [behavior]: Given a committed rendition in which an UNOWNED section carries arbitrary hand-authored prose, when the scope runs, then it exits 0 and reports those bytes as measured debt — unowned text never fails the gate.
- [ ] REQ-0.35.0-06-04 [behavior]: Given the day-one ownership declaration and corpus, when the scope runs, then its output carries the coverage figure computed at run time — owned sections of total, owned bytes of total, and the percentage — and changing the ownership declaration changes the reported figure.
- [ ] REQ-0.35.0-06-05 [behavior]: Given a corpus in which an invariant entry has been retired by a tombstone and a rendition that still carries its text inside an owned section, when the scope runs, then it exits 3 — the scope reads the effective corpus, so a retired entry left in an owned section is drift, not a pass.
- [ ] REQ-0.35.0-06-06 [behavior]: Given the exit-3 path, when stderr is read, then it carries all three recovery parts — the drifted owned section, the cited ADR-0.35.0 § Decision item 4, and a runnable corpus round-trip next step — and it does NOT name un-owning the section as the recovery.
- [ ] REQ-0.35.0-06-07 [support]: gz validate --rendition-lineage is registered in the validator scope registry and documented in `docs/user/manpages/validate.md` and `docs/governance/governance_runbook.md` — witnessed by an `artifact_edited` ledger event citing `docs/user/manpages/validate.md` — and `gz validate --cli-alignment` resolves every reference those docs prescribe.
- [ ] REQ-0.35.0-06-08 [structural-fence]: The fail-closed reach of `--rendition-lineage` is owned sections only, and no ADR-0.35.0 OBPI extends it over unowned bytes. The gate's partial scope is a declared property of the whole decomposition — OBPI-0.35.0-04 sets the scope, 05 supplies the comparison artifact, 07 consumes the result — so it is audited at ADR closeout, not per-OBPI.

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

### Change Log

Substantive corrections and decisions taken inside this operator-initiated OBPI.

#### 2026-09-11 — operator ruling: never-published lineage is DISCLOSED, not fail-closed; caller wired

**Contract amendment, not a defect repair.** The normative text is the inline AMENDED paragraph
in § Audit Contract; this entry is its provenance.

**The conflict, as measured.** Implementation completed with 9/9 tests green, then registering
`_ScopeEntry("rendition_lineage", ...)` turned `gz validate --gate-callers` red with exactly one
finding: *"Gate validate:rendition_lineage has no automatic caller: nothing in `gz check`,
`.pre-commit-config.yaml`, or `.github/workflows/**` invokes it, so it can be red indefinitely
while every gate reports green (GHI #785)."* Both documented escapes were closed:

- Grandfathering is FORBIDDEN for this case. `data/uncalled_gate_grandfather.json`'s own `_doc`
  reads verbatim: *"NEVER add an entry to silence a newly-authored gate -- wire its caller
  instead; that is the laundering ADR-0.0.73 Boundary Invariant #8 forbids."* This gate is
  newly authored.
- Wiring the caller under the ORIGINAL design (missing committed lineage ⇒ exit 3) would hold
  `gz check` red on every commit until OBPI-0.35.0-07 publishes `root.lineage.json`, because
  the live repo declares ownership for `AGENTS.md`/`root` and has no committed lineage yet.

**Operator ruling (2026-09-11): bootstrap-tolerant, and wire the caller.** A surface declaring
ownership with no committed lineage has no graded scope at all: the scope exits 0 and the
reported figure marks those sections ungraded, so the absence is DISCLOSED rather than silent.
The Audit Contract's own first sentence governs the reading — *"read the declared active route
set, not a glob of retained renditions"* — so a lineage never yet published is not a required
committed artifact. Fail-closed behaviour over owned-section drift (REQ-01 through REQ-06) is
UNCHANGED wherever a committed lineage exists; only the never-published case moved from refusal
to disclosure. No REQ text changed: none of REQ-01..08 ever spoke to the missing-lineage case.

**Allowlist amended again as a direct consequence.** "Wire the caller" requires the `gz check`
step surfaces — `src/gzkit/quality.py` (the step runner) and `src/gzkit/commands/quality.py`
(its `_STEP_GUARD_META` MX-severity entry) — and `data/check_scope_membership.json` moves from
`out_of_check` to `in_check`. Added without re-asking, because the operator's ruling already
determined it (AGENTS.md § Operator Economy of Effort #7: where a ruling governs, act and name
the rule rather than re-eliciting it).

**The caller wiring then cascaded further than the ruling's presentation anticipated, and that
is disclosed rather than absorbed silently.** Registering a `gz check` step carries a documented
obligation list (`src/gzkit/commands/quality.py:444`), and binding the step without discharging
it took the full suite to 28 failures (11 failures, 17 errors) while all three named gates read
exit 0 — the precise shape of a green-gate-over-red-suite. Measured and confirmed independently
by the orchestrator: `build_qc_registry()` raises
`KeyError: "QC step 'Rendition lineage' has no classification entry"` (root cause of all 17
errors), and `tests/cli/test_validate_registry_parity.py` fails on
`'rendition_lineage' : explicit-tier stem set must match the pre-collapse _explicit_scope_runners exactly`.
Three further surfaces were therefore added to the allowlist — `src/gzkit/qc_binding.py`,
`data/check_step_concurrency.json`, `tests/cli/test_validate_registry_parity.py` — on the same
consequent-on-the-ruling basis. A sixth surface, `src/gzkit/governance/trust_audits/_qc_claim_exemptions.py`, followed for the same reason once the step was bound: `gz validate --exemption-controls` requires a newly authored enforcement claim to DECLARE whether its gate has an exemption surface, and refuses the grandfather escape in the same words as the uncalled-gate list — *"NEVER add an entry to exemption_control_grandfather.json to silence a newly-authored claim -- declare it instead; that is the laundering ADR-0.0.73 Boundary Invariant #8 forbids."* Confirmed independently by the orchestrator against the live failure. The concurrency declaration's value was MEASURED, not guessed:
`read_only` (ledger bytes unchanged across a run, and the module emits zero ledger events).

#### 2026-09-11 — allowlist amended pre-implementation: two mechanically-coupled surfaces

**No implementation yet; this is a Stage-1 discovery finding, operator-approved before plan mode.**

Discovery reading (parent ADR, sibling `rendition_floor_coherence.py`, `validate_cmd.py`'s
scope registry) surfaced two files a new `_ScopeEntry("rendition_lineage", ...)` registration
would touch that the brief's original Allowed Paths omitted:

- **`data/check_scope_membership.json`** — mechanically forced. `gz validate --gate-callers`
  (GHI #744, default `gz check` scope) fails closed on any registered `validate_cmd.py`
  `_ScopeEntry` absent from this file's `in_check`/`out_of_check` split
  (`tests/governance/test_check_scope_parity.py`). Registering `rendition_lineage` without
  declaring it here would break `gz check` on the very next commit repo-wide. Since no
  committed lineage sidecar exists yet on the live repo (OBPI-07 has not landed to publish
  one), this scope belongs in `out_of_check` — enrolling it in `gz check`'s hardcoded step
  list today would make the default gate fail closed on every commit until 07 lands.
- **`src/gzkit/governance/trust_audits/_qc_nc_entrypoints.py`** — required by this brief's own
  Audit Contract text: "REQ-01/02 include these artifact-integrity controls and a registered
  negative control through the public scope." Every roster entry in `_qc_negative_controls.py`
  (already allowed) pairs a fixture builder with an `_ep_<scope>` runner defined in this sibling
  file (module-size discipline split, `.claude/rules/pythonic.md`); the roster entry cannot
  resolve without a matching `_ep_rendition_lineage` here.

Presented to the operator with citations (file:line evidence for both couplings) before any
source edit. Operator approved amending the allowlist to add both files. Applied surgically —
no other Allowed Paths entries changed, no scope widened beyond these two coupled surfaces.

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
