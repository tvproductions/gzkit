---
id: OBPI-0.35.0-08-remember-post-append-advisory
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 8
lane: Heavy
status: Active
allowlist:
- src/gzkit/commands/content/remember.py
- src/gzkit/commands/content/_drift.py
- src/gzkit/content/vendors.py
- src/gzkit/content/rendition_store.py
- src/gzkit/content/tier_policy.py
- tests/commands/test_content_remember.py
- tests/commands/test_content_retire.py
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
- REQ-0.35.0-08-08
verification:
- uv run gz lint
- uv run gz typecheck
- uv run gz test
- uv run gz validate --documents
- uv run gz validate --req-kind-discipline
- uv run gz cli audit
- uv run mkdocs build --strict
tasks:
  - TASK-0.35.0-08-01-01
  - TASK-0.35.0-08-02-01
  - TASK-0.35.0-08-03-01
  - TASK-0.35.0-08-04-01
  - TASK-0.35.0-08-05-01
  - TASK-0.35.0-08-06-01
  - TASK-0.35.0-08-07-01
  - TASK-0.35.0-08-08-01
---

# OBPI-0.35.0-08-remember-post-append-advisory: Remember Post Append Advisory

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #8 - "`gz content remember` post-append advisory -- three-part recovery prose, exit stays 0, never refuses the append"

**Status:** Draft

## Objective

Give `gz content remember` a POST-APPEND advisory that names the renditions its append just drifted, cites the ADR-0.0.37 corpus->rendition seam, and points at the governed next step — while the append always succeeds and the exit code stays 0. GHI #654's defect is the SILENCE, not the redness.

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
> | REQ-0.35.0-08-01 | **BOUND 2026-08-23** | `test_append_survives_and_exit_stays_0_when_the_advisory_fires` — authored for this REQ because the previously cited test (`test_warns_naming_the_routed_consumer_not_the_retained_record`) asserts exit 0 and never reads the corpus, so it cannot carry the append-intact half. The new test asserts BOTH halves: exit 0 AND the corpus on disk holding the entry with its `surface`/`section`/`text`. Negative control (substituting for `gz arb red`, which returns `not-applicable` once production has landed): `append_entry` was disabled and the test failed. That failure was ERROR-class (`FileNotFoundError` on the corpus read), not assertion-class, for that one mutation shape; subtler breaks (wrong text or section) fail on the field assertions. |
> | REQ-0.35.0-08-02 | **BOUND 2026-08-23, one channel of three** | `test_malformed_sidecar_never_costs_the_append_or_the_exit_code`; RED observed before `dcf29b95`. It genuinely raises — `RenditionProvenance.model_validate_json` throws a `ValidationError` (a `ValueError` subclass) into the drift seam's `except (OSError, ValueError)` — so it proves the REQ's raise-survival semantics. `test_malformed_manifest_never_costs_the_exit_code` was bound to this REQ and the binding was REMOVED the same day: `vendors.py::_read_manifest_key` now guards `isinstance(data, dict)` (landed in `809f1370`), so a `[]` manifest returns `{}` and NOTHING raises — that test proves the guard, not the REQ, and the decorator claimed a proof its body no longer carries. Two of the REQ's three named channels remain unbound: *absent renditions directory* returns `[]` gracefully rather than raising, so it structurally cannot prove raise-survival, and *unreadable sidecar* is exercised only on the `ValueError` branch, never the `OSError` one. |
> | REQ-0.35.0-08-03 | **RE-OPENED 2026-08-23** | was landed by the same test as 08-01, which asserts BOTH `claude` and `codex` are named. The operator-ruled amendment above changed the REQ's subject to the ROUTED consumer only, so that test now pins the behaviour the amended REQ forbids. Re-derive its assertions; do not read the old GREEN as coverage. **Landed 2026-08-23** — `test_warns_naming_the_routed_consumer_not_the_retained_record` on both the remember and retire halves; RED witness `arb-red-REQ-0.35.0-08-03-a84e371f264d4050bf8be165bed7b55d`. |
> | REQ-0.35.0-08-08 | **landed 2026-08-23** | `test_advisory_names_exactly_what_the_gates_grade`; count and names parsed from one rendered line, expectation derived from the predicate rather than pinned to a literal. RED witness `arb-red-REQ-0.35.0-08-08-6abd3bcd045b496d9a999cc6d196c718`. |
> | REQ-0.35.0-08-04 | **OPEN** | advisory currently cites the failing gates and points at `compose` + `commit`; it does NOT cite the ADR-0.0.37 seam, and its next step is not yet `gz content land` |
> | REQ-0.35.0-08-05 | **BOUND 2026-08-23, one disjunct of two; second disjunct STRUCTURALLY UNREACHABLE** | `test_silent_when_no_rendition_has_been_committed` proves the reachable disjunct (no committed renditions -> no advisory), with its assertions strengthened the same day from a single `gz content compose` substring check to the advisory's structural markers, so unrelated advisory output can no longer pass silently. The FIRST disjunct — *renditions already on the current corpus fingerprint* — can never co-occur with a `remember` that reaches the advisory: `remember.py` calls `append_entry` BEFORE `warn_on_rendition_drift`, `drifted_consumers` computes `current` AFTER the append, and `corpus_fingerprint` digests every entry (`rendition_store.py:56-64`), so a successful append always moves the fingerprint; duplicate-text appends are refused earlier and never reach the advisory at all. Confirmed independently by the spec review. The clause *and stderr is empty* is INEXPRESSIBLE through this harness for the same reason REQ-06 is — `CliRunner.invoke` merges both streams into one buffer (`tests/commands/common.py:69`). **RESOLVED 2026-08-24 — the operator ruled reword over changing the runner. Both residuals are removed from the REQ text rather than left unproven; the covering test is unchanged and still binds the reachable disjunct.** |
> | REQ-0.35.0-08-06 | **REWORDED 2026-08-24 — was marked landed on an unobservable claim; still OPEN** | `CliRunner.invoke` merges both streams into one buffer (`tests/commands/common.py`, `redirect_stdout(output)` and `redirect_stderr(output)`), so the stream-separation half of this REQ cannot be expressed as an assertion here at all. The byte-identical-corpus-rows half is also unasserted. Found by the independent spec review, 2026-08-23; pre-existing, not introduced by that change. **Operator ruled reword over changing the runner (2026-08-24):** the stream-separation clause is struck from the REQ and stderr-only routing is now proven nowhere in this brief; the retained byte-identity and exit-code halves still need a covering test. |
> | REQ-0.35.0-08-07 | **open (structural-fence)** | audited at ADR closeout, not here |
>
> **COVERAGE CHANNEL WARNING (spec review, 2026-08-23) — DISCHARGED for REQs 01, 02 and 05 on 2026-08-23; REQ-06 stands.** The warning read: REQs 01, 02, 05 and 06 carry NO `@covers` decorator anywhere in the repo, all four are `[behavior]` whose only proof channel is `@covers`, and the rows above called them landed on PROSE evidence while `gz obpi complete` reads the decorator channel. Measured before the repair: `gz covers` reported `covered_reqs 2`, `behavior_uncovered_reqs 5`. After: `covered_reqs 5`, `behavior_uncovered_reqs 2` — REQ-04 (blocked on the unlanded `gz content land`) and REQ-06 (unprovable through this harness). **The count is not the evidence.** One binding added in that repair was removed again the same day because the decorator asserted a proof its test body did not carry, and a second was strengthened because a substring check stood in for the REQ's actual claim — both found by the independent spec review, not by the coverage number, which rose either way. REQ-06 remains unbound and unprovable here; it is an operator call, now joined by the two REQ-05 residuals recorded in its row above.
>
> **Remaining scope after the 2026-08-23 amendment: REQ-04, REQ-03 (re-opened) and REQ-08.** REQ-04 remains BLOCKED — `gz content land` is not a registered verb (measured 2026-08-23) and OBPI-0.35.0-07 is `Draft`, so this OBPI cannot complete until 07 lands. REQ-03 and REQ-08 are unblocked and land together: they are one change to the enumeration. Original note follows.
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

- `src/gzkit/commands/content/remember.py` — the append path that calls the advisory
- `src/gzkit/commands/content/_drift.py` — the advisory itself, shared with `retire`; GHI #863 lifted it out of `remember.py`, which is why this brief's original allowlist did not cover its own subject
- `src/gzkit/content/vendors.py` — the manifest reader the enumeration now reaches; added 2026-08-23 under coupled-surface coherence (AGENTS.md DO IT RIGHT 1a) after the independent quality review found the route filter opened an uncaught `AttributeError` channel into the capture-unblockable seam
- `src/gzkit/content/rendition_store.py` — READ-ONLY here; home of `is_graded_rendition`, the shared predicate REQ-0.35.0-08-08 binds the advisory to. Declared because the covering test imports it to derive its expectation rather than pinning a literal; this brief does not modify it, and its candidate-exclusion arm belongs to the terminal OBPI-0.35.0-09.
- `src/gzkit/content/tier_policy.py` — READ-ONLY; imported by the retire-side covering tests for `invariant_entries`. Pulled into scope by declaring `test_content_retire.py`, not by any change here.
- `tests/commands/test_content_retire.py` — the retire half of the shared advisory
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
3. NEVER auto-compose or auto-commit. Auto-commit of a rendition bypasses the corpus attestation, and `gz content commit` is fail-closed on empty attestation by explicit design whenever the corpus moved (`commit.py:88-117`; conditional since GHI #821 — an auto-commit after a `remember` ALWAYS lands in the fail-closed arm, because the append is exactly what moves the fingerprint, so this requirement is unweakened); routing around it is the bypass AGENTS.md § Never #1 forbids (ADR § Alternatives I).
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
- [ ] `src/gzkit/commands/content/commit.py:88-117` — the corpus-attestation fail-close this OBPI must not route around (re-seated by GHI #821; was 47-54)

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
- [ ] REQ-0.35.0-08-03 [behavior]: Given two committed renditions rendered stale by the append — one ROUTED for the surface's content type and one a retained off-route record — when `remember` runs, then the advisory names the count and the ROUTED consumer by name, and does NOT name the off-route record. **Amended 2026-08-23 (operator-ruled).** This REQ read *"two committed renditions (`claude`, `codex`) … names the count and BOTH consumers by name"*. Both named vendors were retired as `AgentContract` consumers by OBPI-0.35.0-09: `claude` was renamed `root` (its Requirement 3a) and `codex` was collapsed off-route while deliberately retained as a record (its Requirement 4a — *"NEVER delete a corpus-attested rendition"*). The property being proven is UNCHANGED and is why the REQ exists — the advisory must be SPECIFIC, naming consumers rather than emitting a generic "renditions are stale" string. What changed is which consumers are nameable: naming an off-route record prescribes a recompose that is impossible (the manifest declares no setpoint for it) and forbidden (per-vendor `AgentContract` renditions are prohibited), so the specificity this REQ demands now REQUIRES the route filter rather than a bare directory glob. Brief is `Draft`, so this is ordinary pre-attestation repair, not the attested-REQ-subject-retirement transition (`.claude/rules/governance-core.md`).
- [ ] REQ-0.35.0-08-04 [behavior]: Given the advisory fires, when stderr is read, then it carries all three parts — the named drifted renditions, the cited ADR-0.0.37 corpus->rendition seam, and a runnable gz content land invocation naming the surface.
- [ ] REQ-0.35.0-08-05 [behavior]: Given a surface with no committed renditions at all, when `remember` runs, then NO advisory is emitted — the combined CLI output carries none of the advisory's structural markers. **Amended 2026-08-24 (operator-ruled: reword rather than change the runner).** This REQ read *"Given a surface whose renditions are already on the current corpus fingerprint, or a surface with no committed renditions at all, … then NO advisory is emitted and stderr is empty"*. Two clauses were unprovable and are REMOVED rather than left asserting what no test can reach. (1) The first disjunct is STRUCTURALLY UNREACHABLE: `remember.py` calls `append_entry` BEFORE `warn_on_rendition_drift`, `drifted_consumers` computes `current` AFTER the append, and `corpus_fingerprint` digests every entry (`rendition_store.py:56-64`), so a successful append always moves the fingerprint; duplicate-text appends are refused earlier and never reach the advisory at all. (2) *and stderr is empty* is INEXPRESSIBLE through this harness — `CliRunner.invoke` merges both streams into one buffer (`tests/commands/common.py:69`) — and is replaced by the observable property the covering test already asserts. The property being proven is UNCHANGED and is why the REQ exists: a `remember` that renders nothing stale must stay silent. Brief is `Draft`, so this is ordinary pre-attestation repair, not the attested-REQ-subject-retirement transition (`.claude/rules/governance-core.md`).
- [ ] REQ-0.35.0-08-06 [behavior]: Given the same append performed once with drift present and once without, when the corpus rows are compared, then they are BYTE-IDENTICAL and the exit code is identical — the advisory changes nothing it observes. **Amended 2026-08-24 (operator-ruled: reword rather than change the runner).** This REQ read *"… then they are BYTE-IDENTICAL and stdout's success output is identical — the advisory is stderr-only and changes nothing it observes"*. The stream-separation claim is REMOVED: `CliRunner.invoke` merges stdout and stderr into one buffer (`tests/commands/common.py:69`), so *the advisory is stderr-only* cannot be expressed as an assertion here at all, and the prior GREEN was recorded on an unobservable claim (found by the independent spec review, 2026-08-23). **What the reword COSTS is stated rather than hidden: stderr-only routing is now proven NOWHERE in this brief.** Re-binding it requires a runner that splits the streams; the operator ruled reword over that change on 2026-08-24, so the property is not claimed here. The retained halves — byte-identical corpus rows and an unchanged exit code — are the observable core of *changes nothing it observes* and are still UNASSERTED, so this REQ remains OPEN and needs a covering test. Brief is `Draft`, so this is ordinary pre-attestation repair, not the attested-REQ-subject-retirement transition (`.claude/rules/governance-core.md`).
- [ ] REQ-0.35.0-08-08 [behavior]: Given a committed on-route rendition, a `*.candidate.md` staging artifact, and a retained off-route rendition all present under `.gzkit/renditions/<surface>/`, when the advisory enumerates drifted consumers, then it names exactly the set the shared `content.rendition_store.is_graded_rendition` predicate grades — the same predicate `--rendition-freshness` and `--rendition-floor-coherence` enumerate by — rather than a private copy. Scoped to the PREDICATE, not to the gates' finding sets: an on-route rendition with no sidecar at all is skipped here (`provenance is not None`) while `--rendition-freshness` reports it, a deliberate difference documented in `_drift.drifted_consumers` so that pre-existing drift is not misattributed to this mutation. An earlier wording of this REQ said "the set the gates grade", which overclaimed that difference away (independent spec review, 2026-08-23). The advisory's entire content is a claim about which gates will now fail; enumerating by a rule those gates do not use lets it name a consumer neither gate would ever flag, and send the operator to recompose it. `is_graded_rendition` was authored under OBPI-0.35.0-09's rendition-grading requirement for exactly this reason and its docstring names the failure mode — *"a private copy in each gate is the two-copies-one-binds shape that let the root-contract doctrine drift in the first place"* — while `_drift.drifted_consumers` carries precisely such a copy, reproducing the candidate exclusion and omitting the route test.
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
