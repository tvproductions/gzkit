---
id: OBPI-0.35.0-06-validate-rendition-lineage
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 6
lane: Heavy
status: Completed
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
  - TASK-0.35.0-06-01-02
  - TASK-0.35.0-06-02-02
  - TASK-0.35.0-06-03-02
  - TASK-0.35.0-06-04-02
  - TASK-0.35.0-06-05-02
  - TASK-0.35.0-06-06-02
  - TASK-0.35.0-06-07-02
---

# OBPI-0.35.0-06-validate-rendition-lineage: Validate Rendition Lineage

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #6 - "gz validate --rendition-lineage -- fail-closed over owned sections, coverage % surfaced to Fidelity Assertions"

**Status:** Completed

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
- `src/gzkit/qc_binding.py`, `data/check_step_concurrency.json`, `tests/cli/test_validate_registry_parity.py`, `src/gzkit/governance/trust_audits/_qc_claim_exemptions.py` — the remaining documented obligations of registering a `gz check` step (`src/gzkit/commands/quality.py:418` carries the list): a `_STEP_CLASSIFICATION` entry, a concurrency declaration, and the explicit-tier parity frozenset. Allowlist amended 2026-09-11, consequent on the same wire-the-caller ruling; see Change Log
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
7. ALWAYS resolve severity through the shared MX checkpoint the way `rendition_floor_coherence.py:78` does, so hangar behavior is consistent across the two content gates.
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
- [ ] REQ-0.35.0-06-07 [support]: gz validate --rendition-lineage is registered in the validator scope registry and documented in `docs/user/manpages/validate.md` and `docs/governance/governance_runbook.md` — witnessed by the `artifact_edited` SUPPORT citation naming `docs/user/manpages/validate.md`, whose declared proof is arm 2 of `_support_path_arm_ok` (GHI #647): the cited artifact EXISTS on disk, paired with the structural-validator arm — and `gz validate --cli-alignment` resolves every reference those docs prescribe. **AMENDED 2026-09-11 (operator-ruled): the original text asserted a ledger row the governed emitter cannot produce for this path; see § Evidence → Change Log.**
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

#### 2026-09-11 — Step-4b follow-up: design escalation, one repair, one finding routed out

The tier-1 follow-up (`arb-step-codexadversary-4329ae96fc6f45799e069e8d255f2567`) confirmed all
four prior dispositions — the three repairs work and, in its words, "the REQ-07 amendment
honestly describes its proof channel" — and refuted on two NEW counterexamples.

**The design-escalation rule fired (operator ruling 2026-09-03) and dispatching STOPPED.** Both
rounds named the same root at different surfaces:

- Round 1 weakest point: *"equating successful mutation controls with fulfillment of the whole
  requirement ... the mutation evidence is real, but its assertions cover narrower claims than
  the acceptance contract."*
- Round 2 weakest point: *"The proof suite primarily witnesses returned findings ... does not
  establish the complete CLI contract across output modes and integrity failures. Consequently,
  all recorded mutations can be killed while JSON failures exit successfully."*

One of the two new findings was INTRODUCED by this OBPI's own round-1 repair, which the rule
names as the signature of patching a surfacing rather than the design. The design question — the
proof model witnesses the audit function's RETURN VALUES while the REQs are written as CLI-level
claims ("exits 3") — went to the operator rather than into another fix cycle.

- **`req-06-missing-citation-recovery-incomplete`** (REQ-0.35.0-06-06) — REPAIRED here, because
  it is this OBPI's own regression. The `_uncited_materialized_entries` finding added for REQ-01
  was an exit-3 path emitting a bare diagnostic; REQ-06 scopes its obligation to "the exit-3
  path", not to one message producer. Added `_missing_citation_message` with the same three-part
  shape (`What failed` / `Why forbidden` + ADR-0.35.0 § Decision item 4 / runnable `Next step`,
  never the un-owning escape). Observed RED before the fix: `AssertionError: 'Why forbidden:' not
  found in "lineage section 'owned-section' is corpus-owned and materializes corpus entry
  'e-canon', but cites no lineage entry for it..."`. Witnessed by
  `strip-recovery-from-the-missing-citation-finding`, killed assertion-class.
- **`req-02-json-cli-owned-drift-exits-zero`** (REQ-02/REQ-05) — ROUTED OUT as **GHI #995**
  (operator ruling 2026-09-11). `gz validate --<scope> --json` exits 0 on a failing scope while
  its payload reports `"valid": false`: the `as_json` branch at
  `src/gzkit/commands/validate_cmd.py:1661-1678` returns before the
  `SystemExit(1)`/`SystemExit(3)` classification. Independently reproduced before filing rather
  than taken on the reviewer's report — identical fixture, `exit=3` plain vs `exit=0` with
  `--json`. It is PRE-EXISTING and REPO-WIDE: the branch dates to `b27f42c92` (2026-05-02), four
  months before this OBPI, and affects every scope routed through the main handler; three
  sibling `as_json` branches in the same file correctly `raise SystemExit(3 if errors else 0)`.
  Repairing it changes exit-code behavior for every validator scope, so it is not this gate's
  obligation.

**Transport note.** That follow-up review could not be imported (`exit 3`, "original
finding/proof scope mismatch"): it closed prior findings on obligations whose current proofs it
had not accepted, and `_closure_retains_subject` requires a closed finding's proof to appear in
`accepted_proof_ids`. Its ARB receipt is durable and its findings were acted on; the acceptance
ledger carries no review record for that round.

#### 2026-09-11 — stale source-line citations corrected in normative text

Round-3 spec review (`arb-step-specreview-2b5c43b76b0e4011875b6ac582661fe3`, info severity)
observed that § Requirements #7 cited `rendition_floor_coherence.py:47-51` for MX checkpoint
parity, but lines 47-51 of that module are `from __future__`/`pathlib`/`gzkit.advisory` import
statements; the `_disposition.grounds(_checkpoint.resolve(...))` call it means is at line 78.
The parity itself was independently confirmed correct — only the anchor was wrong.

Corrected to `rendition_floor_coherence.py:78`. Auditing every source-line citation in this
brief while the correction was in hand (fix the class, not the instance) surfaced a second
imprecise anchor: `src/gzkit/commands/quality.py:444` was cited twice as "carries the list" of
`gz check` step-registration obligations, but 444 lands inside family A item 6; the obligation
statement begins at line 418 (`_build_check_steps`' docstring, "ADDING A STEP HERE IS NOT ONE
EDIT"). Corrected to `:418` in both places. The two Discovery Checklist ranges
(`rendition_floor_coherence.py:32-105` and `:1-9`) were verified accurate as read-guidance spans
and left unchanged.

These edits are in normative sections, so they moved the acceptance input digest and required a
full re-proof and both Stage-2 reviews to be re-run. Operator directed the correction rather
than deferring it (2026-09-11), with that cost stated in advance.

#### 2026-09-11 — operator ruling: REQ-07 names the witness the channel actually produces

**Contract amendment, not a defect repair.** The normative text is the amended REQ-0.35.0-06-07
line in § Acceptance Criteria; this entry is its provenance.

**As authored, REQ-07 asserted a witness nothing can emit.** Its text required "an
`artifact_edited` ledger event citing `docs/user/manpages/validate.md`". Measured 2026-09-11:
zero such rows exist across `path`/`id`/`artifact`/`artifact_path`, and
`is_governance_artifact('docs/user/manpages/validate.md')` returns **False**
(`src/gzkit/hooks/core.py`), so the only governed emitter — the post-commit recorder in
`src/gzkit/hooks/commit_ledger.py`, which appends `artifact_edited` for
`governance_paths_in_commit` — can never produce that row for this path. The two remaining
routes were a hand-appended ledger row (forbidden, AGENTS.md § Behavior Rules — Never #2) and
widening `GOVERNANCE_PATTERNS` (outside this brief's Allowed Paths, and it would make every
manpage edit emit the event repo-wide).

**What actually proves it, and why that is not a weakening.** `_support_path_arm_ok`
(`src/gzkit/req_kind_support.py`, GHI #647) declares three genuine SUPPORT proofs, and arm 2 is
the one that governs an `artifact_edited` citation: the cited artifact EXISTS on disk, paired
with the structural-validator arm checking its shape. Its own rationale is explicit that this is
the designed path precisely because *"`artifact_edited` is not emitted for most artifacts"*, and
that the pairing is *"at least as strong as a historical edit-event"*. The REQ now names that
arm instead of a row the machinery does not write, so the text and the proof channel assert the
same thing.

**How it was adjudicated.** The finding `req-07-declared-artifact-edit-witness-missing` was
raised by the tier-1 cross-vendor adversary
(`arb-step-codexadversary-8eaeb01d5ff44b29bcd08416ec80f67b`) and independently re-raised as
`major` by the round-2 spec reviewer (`arb-step-specreview-34084af1fe814da4adf8cd55e4a19ff6`,
refused at import for reusing the finding identity). The implementing agent first contested it on
the arm-2 reading under an operator ruling; two of three independent reviewers rejected that
reading, so the contest was abandoned rather than pressed. The operator then ruled the REQ TEXT
the defect and directed this amendment. The agent did not self-close the finding at any point.

#### 2026-09-11 — Step-4b tier-1 refutation: three repairs, one contested finding

Receipt `arb-step-codexadversary-8eaeb01d5ff44b29bcd08416ec80f67b` (tier 1, cross-vendor,
replayed in a disposable writable checkout) returned **NOT-CORROBORATED / refuted** with four
mapped findings. Recorded in the acceptance ledger as history; three were repaired, one is
contested with source evidence rather than repaired. Repairs were re-proved and re-reviewed.

- **`req-02-pure-verifier-accepts-owned-drift`** (REQ-0.35.0-06-02) — REPAIRED. The Audit
  Contract requires the audit core to return findings independently of presentation severity
  "so 07 can reject any owned drift even in MX mode", and `verify_candidate_against_declaration`'s
  own docstring claimed it and `validate_rendition_lineage` "can never disagree about what a
  sound lineage is". They disagreed: the pure verifier checked headings, spans, ownership
  agreement and id liveness but never compared owned section TEXT to its materialization, so an
  equal-length substitution returned `[]`. The derivation comparison now lives in the pure core
  (the single owned-drift reporter, carrying the full three-part prose); `_owned_drift` is
  removed and `_grade_rendition` computes one regeneration and feeds it in. Witnessed by
  `never-detect-owned-section-drift`, killed assertion-class against both the committed-path and
  pure-core tests.
- **`req-01-missing-owned-entry-ids-pass`** (REQ-0.35.0-06-01) — REPAIRED. Liveness is vacuous
  over the ids a lineage OMITS, so an owned section citing `entry_ids=[]` passed while recording
  no provenance at all. `_uncited_materialized_entries` now requires an owned section to cite
  every live entry whose text actually appears in its regenerated materialization — grounded in
  the derivation, so a `compressible` entry the setpoint dial legitimately dropped is not
  reported as a missing citation. Witnessed by `never-report-an-uncited-materialized-entry`,
  killed assertion-class.
- **`req-06-recovery-emitted-to-stdout`** (REQ-0.35.0-06-06) — REPAIRED. The REQ names the
  channel ("when stderr is read"); the fail-closed path returned a `ValidationError` that the
  shared CLI renders to stdout, and the covering test asserted on `.message`, proving the prose
  was composed but never that it reached the channel. The gate now emits the three-part prose to
  stderr on the fail-closed path, as it already did in warn mode. Witnessed by
  `withhold-the-recovery-prose-from-stderr`, killed assertion-class.
- **`req-07-declared-artifact-edit-witness-missing`** (REQ-0.35.0-06-07) — CONTESTED, not
  repaired (operator ruling 2026-09-11, presented with the mechanism). The finding reads the REQ
  text literally and calls the file-existence path a "fallback". It is not: `_support_path_arm_ok`
  arm 2 (`src/gzkit/req_kind_support.py:255-258`, GHI #647) is gzkit's declared SUPPORT proof
  semantics for an `artifact_edited` citation, written because *"`artifact_edited` is not emitted
  for most artifacts"*, and the arm is documented as "at least as strong as a historical
  edit-event". Measured: `is_governance_artifact('docs/user/manpages/validate.md')` returns
  **False**, so the post-commit emitter (`hooks/commit_ledger.py`) can never produce the row the
  finding asks for. Satisfying it literally would require a hand-appended ledger row (forbidden,
  AGENTS.md § Behavior Rules — Never #2) or widening `GOVERNANCE_PATTERNS` in `hooks/core.py`
  (outside this brief's Allowed Paths, and it would make every manpage edit emit the event
  repo-wide). Carried to the Step-4b follow-up with this evidence for independent adjudication;
  the implementing agent does not self-close it.

**Also this session, before the adversary ran:** all 8 proofs were re-executed because an
unrelated commit (`5139681f5`, the GHI #992 pipeline fix, touching `src/gzkit/commands/obpi_cmd.py`
and `validate_frontmatter.py`) moved the global acceptance input digest and staled the prior
round — the documented non-dependency-minimal invalidation in
`docs/user/manpages/obpi-acceptance.md` § Freshness and Limits, not a defect in this OBPI. Both
Stage-2 reviews were re-run and re-imported against the fresh proof identities.

**Tracked separately:** GHI #993 — `gz obpi acceptance human-review` has no obligation scope and
hardcodes `stage="adversarial"`, so using it to close a single Stage-2 finding would also stamp
tier-3 adversarial approval across every obligation. Found while re-binding the REQ-03 residual
closure; the operator routed that closure away from `human-review` for exactly this reason.

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
obligation list (`src/gzkit/commands/quality.py:418`), and binding the step without discharging
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

### Step 4b — Independent Adversarial Validation

**Adversary identity and tier.** Tier 1, cross-vendor: OpenAI Codex dispatched through the
`openai-codex` Claude Code plugin (`codex-companion.mjs task --write --cwd <disposable checkout>`),
ARB-wrapped on every round. Codex reported `ready: true` throughout, so tiers 2 and 3 were
forbidden. Each round ran in a throwaway writable copy of the reviewed tree so the adversary could
REPLAY recorded proofs rather than judge them by reading.

**The adversary REFUTED this OBPI three times before corroborating.** Two Claude Stage-2 reviewers
had passed the pre-repair state 8/8 twice; the cross-vendor tier is what caught the defects.

| Round | Receipt | Verdict | Claims broken |
|---|---|---|---|
| 1 | `arb-step-codexadversary-8eaeb01d5ff44b29bcd08416ec80f67b` | **NOT-CORROBORATED / refuted** | 4 findings (REQ-01, REQ-02, REQ-06, REQ-07) |
| 2 | `arb-step-codexadversary-4329ae96fc6f45799e069e8d255f2567` | **NOT-CORROBORATED / refuted** | confirmed all 4 prior dispositions; raised 2 new (JSON exit bypass, missing-citation recovery) |
| 3 | `arb-step-codexadversary-61d07ad4157a45ff9cd20a672ac42a8e` | CORROBORATED-WITH-CAVEATS / not-refuted | — |
| 4 | `arb-step-codexadversary-81439f474a3d4f39b375ed6e22eeef32` | **refuted by design** | record-correction round: replayed the 8 outstanding controls, raised the historical finding into Layer-2 |
| 5 | `arb-step-codexadversary-07dfb35f0aaf4af482c86feb724c750b` | CORROBORATED / not-refuted | closed the raised finding after verifying the repair by execution |

Round 2's review record was **REFUSED at import** (it closed findings on obligations whose current
proofs it had not accepted, which `_closure_retains_subject` forbids), so it carries no
acceptance-ledger entry. Its ARB receipt is durable and both of its findings were subsequently
recorded by other means. Disclosed here rather than smoothed over.

**What the adversary broke, and how each was resolved.**

- **REQ-02 — `verify_candidate_against_declaration` accepted owned drift.** It checked headings,
  spans, ownership agreement and entry-id liveness but never compared owned section TEXT to its
  materialization; an equal-length `X` substitution returned `[]`. RESOLVED by moving the
  derivation comparison into the pure core as the single owned-drift reporter and removing
  `_owned_drift`.
- **REQ-01 — missing owned entry ids passed.** Liveness is vacuous over OMITTED ids, so an owned
  section citing `entry_ids=[]` passed with no recorded provenance. RESOLVED by
  `_uncited_materialized_entries`, grounded in the derivation so a legitimately dropped
  `compressible` entry is never falsely flagged.
- **REQ-06 — recovery prose reached stdout, not stderr.** The REQ names the channel; the covering
  test asserted on `ValidationError.message`, proving composition and never delivery. RESOLVED by
  emitting the three parts to stderr on the fail-closed path.
- **REQ-07 — the declared `artifact_edited` witness does not exist.** Independently re-raised by a
  spec reviewer. `is_governance_artifact()` returns `False` for `docs/user/manpages/validate.md`, so
  the post-commit emitter can never produce that row. The implementing agent contested this reading
  first and was OVERRULED by independent review; the operator then ruled the REQ TEXT the defect and
  directed the amendment now recorded in § Acceptance Criteria. Round 5 judged the amendment
  "honestly describes its proof channel."
- **JSON exit bypass (`req-02-json-cli-owned-drift-exits-zero`).** `gz validate --json` exits 0 on a
  failing scope while its payload reports `valid: false`. Independently reproduced before filing;
  PRE-EXISTING (`b27f42c92`, 2026-05-02) and REPO-WIDE. Operator-ruled OUT of this OBPI and routed
  to **GHI #995**; retained as an auxiliary observation with a null obligation.
- **`req-06-missing-citation-recovery-incomplete`.** A regression introduced by this OBPI's OWN
  REQ-01 repair — its new exit-3 path emitted a bare diagnostic while REQ-06 scopes to "the exit-3
  path" as a whole. RESOLVED by `_missing_citation_message`.

**Design escalation.** Rounds 1 and 2 named the same ROOT at different surfaces, and one new finding
had been introduced by a prior repair — the signature of patching a surfacing rather than a design.
Under the design-escalation rule dispatching STOPPED and the scope question went to the operator,
who ruled the boundary (repair the regression here, route the shared-CLI defect to GHI #995).

**Replay coverage.** All 11 recorded mutation controls were independently replayed by the tier-1
adversary at the completion digest `90807b7e…` — 8 in round 4, 2 in round 3, and
`strip-recovery-from-the-missing-citation-finding` in rounds 3 and 5.

**Accepted residual.** `req-03-unowned-content-mutation-gap` is DISCLOSED, not proven: its
cross-module half is structurally unwitnessable from inside this OBPI because `composer.py` is a
Denied Path of the landed OBPI-0.35.0-05. Operator-ruled an accepted residual after two independent
rounds named the same root.

### Gate 5 (Human)

```text
attest completed
```

Operator `g0`, 2026-09-12, against the replay-VERIFIED Stage-4a packet at
`.gzkit/evidence/OBPI-0.35.0-06-validate-rendition-lineage.stage4a.md`, explicitly accepting the
bounded result including the disclosed REQ-03 residual and the separately routed defects.
Completion carried an operator-approved `--accept-security-floor` override (independent evaluator
determination NOT-SECURITY-RELEVANT) because the canonical security-scan slot cannot run until the
toolchain ADR promoting `pool.agentic-security-review` lands.

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof


The gate run live against the repository, exit 0, disclosing rather than failing on the never-yet-published `AGENTS.md` lineage that OBPI-0.35.0-07 will publish:

```
$ uv run gz validate --rendition-lineage
Validated: rendition_lineage

✓ All validations passed (1 scopes).
[advisory] rendition-lineage: 1 committed rendition(s) graded; 0/22 sections owned, 0/47851 bytes owned (0.0%); 12 section(s) / 41846 byte(s) UNGRADED (declared corpus-owned with no committed lineage). Unowned and ungraded bytes are measured debt and never change this scope's exit code (ADR-0.35.0 § Decision item 4).
```

That single run demonstrates REQ-04 (coverage computed at run time, not stored) and the operator-ruled bootstrap disclosure together. Fail-closed behaviour is witnessed by 11 assertion-class mutation kills, every one independently replayed at this digest by the tier-1 cross-vendor adversary — 8 in receipt `arb-step-codexadversary-81439f474a3d4f39b375ed6e22eeef32`, 2 in `arb-step-codexadversary-61d07ad4157a45ff9cd20a672ac42a8e`, and `strip-recovery-from-the-missing-citation-finding` in both that receipt and `arb-step-codexadversary-07dfb35f0aaf4af482c86feb724c750b`.

Stage-3 gates re-run fresh at the completion digest, all `exit_status 0`: `arb-ruff-ab86ee6b0199483b8eb85f82e0394ec0`, `arb-step-typecheck-1c706bdc42bf4db4bc86c02edaa1cbaf`, `arb-step-unittest-b1a805a8b6b04d44abecba040eec88e0` (10159 tests, 4 skipped), `arb-step-mkdocs-acab19b488a343b48c4b934fa2451663`, `arb-step-behave-eaae5376ad8548c989eff61c9aed166e` (3 scenarios, 20 steps). `gz covers`: `behavior_uncovered_reqs 0`.

### Implementation Summary


- Files created: `src/gzkit/governance/trust_audits/rendition_lineage.py` (535 lines — the `gz validate --rendition-lineage` owned-section derivation gate: `measure_coverage`, `verify_candidate_against_declaration`, `_uncited_materialized_entries`, `_drift_message`/`_missing_citation_message`, `validate_rendition_lineage`); `tests/governance/test_rendition_lineage.py` (636 lines, 16 covering tests); `features/rendition_lineage.feature` + `features/steps/rendition_lineage_steps.py` (3 Gate-4 scenarios, 20 steps)
- Files modified: scope registration and CLI wiring (`trust_audits/__init__.py`, `cli/parser_maintenance.py`, `commands/validate_cmd.py`); the GHI #785 automatic-caller chain (`quality.py`, `commands/quality.py`, `qc_binding.py`, `data/check_scope_membership.json`, `data/check_step_concurrency.json`, `tests/cli/test_validate_registry_parity.py`); negative-control surfaces (`_qc_negative_controls.py`, `_qc_nc_entrypoints.py`, `_qc_claim_exemptions.py`); docs (`docs/user/manpages/validate.md`, `docs/governance/governance_runbook.md`); this brief
- Tests added: 16 unit tests across the 6 BEHAVIOR REQs plus 3 BDD scenarios; 11 recorded mutation controls, all 11 killed assertion-class and all 11 independently replayed by the tier-1 cross-vendor adversary at the completion digest
- Date completed: 2026-09-12
- Attestation status: operator `g0` attested "attest completed" at acceptance digest `90807b7ef6ec9ae9f6df25e05c08bcc723d984ed0f40d4d5feb7f21de3507931`, against the replay-VERIFIED Stage-4a packet at `.gzkit/evidence/OBPI-0.35.0-06-validate-rendition-lineage.stage4a.md`, explicitly accepting the bounded result including the disclosed REQ-03 residual and the separately routed defects
- Defects noted: 8 findings raised across the OBPI, all dispositioned — 5 repaired and independently closed, 1 (`req-07-declared-artifact-edit-witness-missing`) resolved by an operator-ruled REQ-07 amendment naming arm 2 of `_support_path_arm_ok` (GHI #647), 1 (`req-03-unowned-content-mutation-gap`) accepted as a DISCLOSED residual rather than proven, 1 (`req-02-json-cli-owned-drift-exits-zero`) routed out as pre-existing and repo-wide to GHI #995. Also filed: GHI #993 (acceptance `human-review` has no obligation scope), GHI #994 (a non-executing reviewer recorded a confirmation it could not have made). The tier-1 adversary refuted three times before corroborating; one finding was a regression introduced by this OBPI's own earlier repair

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.35.0-06-validate-rendition-lineage at acceptance digest 90807b7ef6ec9ae9f6df25e05c08bcc723d984ed0f40d4d5feb7f21de3507931, attested by operator g0 against the replay-VERIFIED Stage-4a packet (.gzkit/evidence/OBPI-0.35.0-06-validate-rendition-lineage.stage4a.md, gz obpi verify-packet exit 0). Operator explicitly accepted the bounded result including the disclosed REQ-03 residual and the separately routed defects. Evidence: 8/8 acceptance proofs valid at that digest with 11 assertion-class mutation kills, all 11 independently replayed there by the tier-1 cross-vendor adversary; Stage-3 gates re-run fresh, all exit_status 0 — arb-ruff-ab86ee6b0199483b8eb85f82e0394ec0, arb-step-typecheck-1c706bdc42bf4db4bc86c02edaa1cbaf, arb-step-unittest-b1a805a8b6b04d44abecba040eec88e0 (10159 tests, 4 skipped), arb-step-mkdocs-acab19b488a343b48c4b934fa2451663, arb-step-behave-eaae5376ad8548c989eff61c9aed166e (3 scenarios, 20 steps); gz covers behavior_uncovered_reqs 0. Stage-4 review set on that digest: spec arb-step-specreview-42ad26da08b74a2bb78758680e976caf, quality arb-step-qualityreview-b9fd1be9156b4e61b21c171c548cf499, tier-1 adversarial arb-step-codexadversary-61d07ad4157a45ff9cd20a672ac42a8e (CORROBORATED-WITH-CAVEATS / not-refuted), plus record-correction arb-step-codexadversary-81439f474a3d4f39b375ed6e22eeef32 and closing arb-step-codexadversary-07dfb35f0aaf4af482c86feb724c750b. All 8 findings dispositioned, zero open, zero blockers.
- Date: 2026-09-12

---

**Date Completed:** 2026-09-12

**Evidence Hash:** -
