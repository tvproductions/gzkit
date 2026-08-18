---
id: OBPI-0.35.0-08-remember-post-append-advisory
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 8
lane: Heavy
status: Draft
allowlist:
- src/gzkit/commands/content/remember.py
- tests/commands/test_content_remember.py
- features/**
- docs/user/manpages/content.md
- docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-08-remember-post-append-advisory.md
reqs:
- REQ-0.35.0-08-01
- REQ-0.35.0-08-02
- REQ-0.35.0-08-03
- REQ-0.35.0-08-04
- REQ-0.35.0-08-05
- REQ-0.35.0-08-06
- REQ-0.35.0-08-07
verification:
- uv run gz lint
- uv run gz typecheck
- uv run gz test
- uv run gz validate --documents
- uv run gz validate --req-kind-discipline
- uv run gz cli audit
- uv run mkdocs build --strict
---

# OBPI-0.35.0-08-remember-post-append-advisory: Remember Post Append Advisory

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #8 - "`gz content remember` post-append advisory -- three-part recovery prose, exit stays 0, never refuses the append"

**Status:** Draft

## Objective

Give `gz content remember` a POST-APPEND advisory that names the renditions its append just drifted, cites the ADR-0.0.37 corpus->rendition seam, and points at the governed next step — while the append always succeeds and the exit code stays 0. GHI #654's defect is the SILENCE, not the redness.

**Dependency order (ADR-0.35.0 § Scope Minimization):** 08 is independent of the 01 -> 02 -> 03 chain and of 04 -> 05 -> 06 -> 07; it may land at any point. Its advisory text names the OBPI-0.35.0-07 verb as the governed next step, so the prose is authored against that verb's final shape.

<!-- gz-validate-skip: command-shape -->
> **PARTIALLY PRE-LANDED — read before implementing (reconciled 2026-07-22, operator-ruled).**
> GHI #654's capture-silence gap was direct-fixed ahead of this brief because it was
> a live footgun (it red-treed the repo once already; see `dc2bc605`) and this brief
> cannot fully land until OBPI-0.35.0-07 makes `gz content land` runnable — its own
> Prerequisites say so. The landed commits are `48a5f799` (advisory) and `dcf29b95`
> (regression repair: `load_fingerprint` raises on a malformed sidecar, which was
> costing `remember` its exit code).
>
> | REQ | State | Where |
> |-----|-------|-------|
> | REQ-0.35.0-08-01 | **landed** | `test_warns_naming_every_drifted_consumer` asserts exit 0 with the append intact |
> | REQ-0.35.0-08-02 | **landed** | `test_malformed_sidecar_never_costs_the_append_or_the_exit_code`; RED observed before `dcf29b95` |
> | REQ-0.35.0-08-03 | **landed** | same test as 08-01 — names the count and both consumers |
> | REQ-0.35.0-08-04 | **OPEN** | advisory currently cites the failing gates and points at `compose` + `commit`; it does NOT cite the ADR-0.0.37 seam, and its next step is not yet `gz content land` |
> | REQ-0.35.0-08-05 | **landed** | `test_silent_when_no_rendition_has_been_committed` |
> | REQ-0.35.0-08-06 | **landed** | advisory writes to stderr; stdout success line unchanged |
> | REQ-0.35.0-08-07 | **open (structural-fence)** | audited at ADR closeout, not here |
>
> **Remaining scope is REQ-04 only:** retarget the three-part prose in
> `_warn_on_rendition_drift()` to cite the ADR-0.0.37 corpus->rendition seam
> explicitly and to name `gz content land <surface>` once OBPI-0.35.0-07 lands.
> Do not re-implement the landed REQs; re-derive their assertions if you change
> the advisory's shape.
>
> Note: `gz obpi brief-drift` reported this brief **clean** on all five dimensions
> (allowlist / discovery / verification / req_count / citation) while four of its
> REQs were already satisfied — the reconciler cannot see pre-landed REQ
> satisfaction, so this note is authored rather than computed.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/commands/content/remember.py` — the post-append advisory
- `tests/commands/test_content_remember.py` — covering tests
- `features/**` — Gate 4 scenarios
- `docs/user/manpages/content.md` — the `remember` advisory contract
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-08-remember-post-append-advisory.md` — this brief's evidence sections

## Denied Paths

- `src/gzkit/content/corpus_store.py` — the append path itself is untouched; this OBPI adds an advisory AFTER it, never a precondition before it
- `src/gzkit/content/models/corpus.py` — OBPI-0.35.0-01
- `src/gzkit/commands/content/land.py` — OBPI-0.35.0-07; this OBPI names the verb, never implements or invokes it
- `src/gzkit/governance/trust_audits/**` — no new gate; the advisory is not a validator
- New dependencies, CI files, lockfiles
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. NEVER refuse the append. On EVERY path — drift detected, drift-detection itself failing, corpus unreadable, renditions absent — the entry is appended and the exit code stays 0. Capture is the operator's words entering canon; a capture tool that refuses is a tool that loses doctrine (ADR § Alternatives J).
2. ALWAYS append FIRST, advise SECOND. The advisory is computed after the corpus row is durably written, so a fault in drift detection can never cost the operator their words.
3. NEVER auto-compose or auto-commit. Auto-commit of a rendition bypasses Gate 5, and `gz content commit` is fail-closed on empty attestation by explicit design (`commit.py:47-54`); routing around it is the bypass AGENTS.md § Never #1 forbids (ADR § Alternatives I).
4. ALWAYS emit three parts per `.claude/rules/guardrail-feedback-prose.md`: (1) WHAT DRIFTED — the count of now-stale renditions and each one NAMED by consumer; (2) WHY — the ADR-0.0.37 corpus->rendition seam, cited, not paraphrased; (3) GOVERNED NEXT STEP — the runnable gz content land invocation for the surface.
5. NEVER emit the advisory when nothing drifted. A surface with no committed renditions, or renditions already on the current corpus fingerprint, produces a silent success — an advisory that always fires is noise, and noise is how the real signal gets ignored.
6. ALWAYS write the advisory to stderr, leaving stdout's existing success output unchanged, so machine consumers of `remember` are unaffected.
7. NEVER let the advisory alter the appended row. The corpus row written with the advisory firing MUST be byte-identical to the row written without it.
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

- [ ] ADR § Decision item 7 and § Consequences (Positive) #6 — the advisory, and `remember` ceasing to be a footgun.
- [ ] ADR § Alternatives I and J — auto-compose-and-commit and refuse-the-append, both rejected; do not re-litigate.
- [ ] GHI #654 — the orchestration gap; its defect is the SILENCE, not the tree going red.
- [ ] `.claude/rules/guardrail-feedback-prose.md` — the three-part bar, including the prohibition on a next step that is not runnable.

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/commands/content/remember.py` exists and appends via `corpus_store.append_entry`
- [ ] `src/gzkit/content/rendition_store.py::corpus_fingerprint` and `load_fingerprint` exist — the drift signal is a fingerprint comparison, never an mtime comparison
- [ ] `.gzkit/renditions/AGENTS.md/root.corpus.json` and `codex.corpus.json` exist — the provenance sidecars whose frozen fingerprints the advisory compares against
- [ ] OBPI-0.35.0-07's gz content land &lt;surface&gt; shape is settled, so the advisory's next-step string is runnable rather than aspirational
- [ ] `docs/user/manpages/content.md` exists

**Existing Code (understand current state):**

- [ ] `src/gzkit/commands/content/remember.py` — the current append path and its stdout success output, which stays unchanged
- [ ] `src/gzkit/content/rendition_store.py:56-64` and `:135-144` — `corpus_fingerprint` and `load_fingerprint`; `load_fingerprint` returns `None` for an absent sidecar, which the freshness gate reads as drift
- [ ] `src/gzkit/commands/content/commit.py:47-54` — the Gate-5 fail-close this OBPI must not route around

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
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz cli audit
uv run mkdocs build --strict
```

## Demo

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz content remember AGENTS.md --section behavior-rules --text "Advisory demonstration entry." --tier compressible
uv run gz validate --rendition-freshness
uv run gz content land AGENTS.md --status
```

## Acceptance Criteria

<!--
Each checkbox carries a deterministic REQ ID and exactly one kind tag
(ADR-0.0.59; `gz validate --req-kind-discipline`):
  [behavior]         -> proven ONLY by an @covers test in tests/**
  [support]          -> proven ONLY by a path-citing ledger event + structural validator
  [structural-fence] -> proven ONLY by a parent-ADR ## Boundary Invariants entry
-->

- [ ] REQ-0.35.0-08-01 [behavior]: Given an append that leaves every committed rendition of the surface stale, when `gz content remember` runs, then the entry IS appended and the exit code is 0 — the advisory never becomes a refusal.
- [ ] REQ-0.35.0-08-02 [behavior]: Given drift-detection itself raising (unreadable sidecar, absent renditions directory, malformed provenance), when `remember` runs, then the entry is STILL appended and the exit code is STILL 0 — the append is durably written before the advisory is computed.
- [ ] REQ-0.35.0-08-03 [behavior]: Given two committed renditions (`claude`, `codex`) rendered stale by the append, when `remember` runs, then the advisory names the count and BOTH consumers by name — not a generic "renditions are stale" string.
- [ ] REQ-0.35.0-08-04 [behavior]: Given the advisory fires, when stderr is read, then it carries all three parts — the named drifted renditions, the cited ADR-0.0.37 corpus->rendition seam, and a runnable gz content land invocation naming the surface.
- [ ] REQ-0.35.0-08-05 [behavior]: Given a surface whose renditions are already on the current corpus fingerprint, or a surface with no committed renditions at all, when `remember` runs, then NO advisory is emitted and stderr is empty.
- [ ] REQ-0.35.0-08-06 [behavior]: Given the same append performed once with drift present and once without, when the corpus rows are compared, then they are BYTE-IDENTICAL and stdout's success output is identical — the advisory is stderr-only and changes nothing it observes.
- [ ] REQ-0.35.0-08-07 [structural-fence]: `gz content remember` refuses an append on NO path introduced anywhere in ADR-0.35.0. Capture is unblockable across the whole decomposition — OBPI-0.35.0-06's gate and OBPI-0.35.0-07's orchestrator both make the tree redder, and either could be tempted to add a precondition to `remember` to keep it green. The property is audited at ADR closeout because it is violated by ADDING something elsewhere, not by anything visible in this brief's own diff.

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
