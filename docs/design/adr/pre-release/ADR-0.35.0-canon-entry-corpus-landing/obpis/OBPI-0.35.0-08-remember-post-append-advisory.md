---
id: OBPI-0.35.0-08-remember-post-append-advisory
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 8
lane: Heavy
status: Completed
allowlist:
- src/gzkit/commands/content/remember.py
- src/gzkit/commands/content/_drift.py
- src/gzkit/commands/content/retire.py
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
  - TASK-0.35.0-08-04-02
  - TASK-0.35.0-08-02-02
  - TASK-0.35.0-08-04-03
  - TASK-0.35.0-08-01-02
  - TASK-0.35.0-08-04-04
  - TASK-0.35.0-08-06-02
req_atomic:
# Declared 2026-10-03 at Stage 2, where the labor happened (GHI #590). REQ-01, REQ-02,
# REQ-04 and REQ-06 are ABSENT on purpose: each carried more than one unit of labor and was
# subdivided via `gz task start --seq next`.
#   REQ-01 -> seq 01/02: the covering test (2026-08-23), then the Step-4b repair that
#             made advisory emission best-effort.
#   REQ-02 -> seq 01/02: the ValueError binding (2026-08-23), then the OSError arm
#             through a real unreadable sidecar.
#   REQ-06 -> seq 01/02: the paired byte-identity test, then the paired output-fault
#             test that gives the exit-code clause a conclusive RED (added at Stage 5,
#             after the red-parity gate refused the first test's `none` witness).
#   REQ-04 -> seq 01/02/03/04: the advisory prose and its unit test; the manpage
#             contract and the Gate 4 scenarios; the review repair that put the
#             attestation flags on the printed command; then the Step-4b repair
#             that shell-quotes the surface.
# REQ-03: one change to the enumeration, shared with REQ-08.
- REQ-0.35.0-08-03
# REQ-05: one covering test for the silent case; no production change.
- REQ-0.35.0-08-05
# REQ-07: structural fence; its proof is the parent ADR's Boundary Invariants entry.
- REQ-0.35.0-08-07
# REQ-08: one covering test binding the advisory to the shared predicate.
- REQ-0.35.0-08-08
---

# OBPI-0.35.0-08-remember-post-append-advisory: Remember Post Append Advisory

## ADR Item

> **ANNOTATED 2026-09-02 (operator-ruled) — THIS BRIEF'S `status: Active` IS RESIDUE, NOT A DRAW.**
> It was started by an agent on 2026-08-23 WITHOUT operator consent — the IRON LAW
> violation recorded verbatim in `AGENTS.md` § Operator Doctrine (*"NEVER, EVER, EVER,
> EVER DO OBPI WORK ON YOUR OWN. NEVER!"*). Operator, 2026-09-01, verbatim: *"08 was a
> misbehaved agent"* / *"it was a rogue agent who decided to run the OBPI without my
> consent."* The ledger carries the residue — `brief_reconciled`, four
> `red_receipt_emitted`, `brief_reconcile_drift_detected` and `obpi_lock_claimed`, all
> dated 2026-08-23.
>
> **DO NOT RESUME THIS BRIEF ON THE STRENGTH OF ITS STATUS.** `gz adr status` reports it
> `in_progress` beside `OBPI-0.35.0-03`, which is the brief actually in flight (operator,
> 2026-09-01: *"03 (08 was a misbehaved agent)"*). An agent has already once read exactly
> this state as license to work it. The work itself remains legitimate and UNDRAWN; only
> the operator may draw it.
>
> It stays `Active` deliberately. There is no governed reversal from `Active` back to
> unstarted — `get_allowed_transitions('OBPI','Active')` returns `['Completed',
> 'Abandoned']` and no CLI verb supplies the missing edge — which is the whole of
> **GHI #930**, now folded into **GHI #611**'s corrective-action primitive by operator
> ruling. This brief is that gap's only live reproduction, so clearing it would erase the
> evidence; `Abandoned` is refused because it would mark legitimate, undrawn work
> permanently abandoned under closed abandon categories (ADR-0.0.41).
>
> Annotation authored by the direct path under an explicit operator ruling — no lock, no
> pipeline marker, no TASK, no dispatch — on the precedent set for `OBPI-0.35.0-01`.
>
> **DRAWN 2026-10-03 (operator-initiated).** The operator invoked
> `/gz-obpi-pipeline OBPI-0.35.0-08`. The annotation above is the record of the 2026-08-23
> history and no longer bars the work.


- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #8 - "`gz content remember` post-append advisory -- three-part recovery prose, exit stays 0, never refuses the append"

**Status:** Completed

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

**Dependency order (ADR-0.35.0 § Scope Minimization):** 08's capture/advisory core has partially landed, but this brief completes only after 07 supplies the runnable land recovery verb. Existing Active status remains unauthorized residue under the dated annotation; this authoring repair is not an implementation draw.

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
> | REQ-0.35.0-08-02 | **BOUND 2026-08-23, one channel of three** | `test_malformed_sidecar_never_costs_the_append_or_the_exit_code`; RED observed before `dcf29b95`. It genuinely raises — `RenditionProvenance.model_validate_json` throws a `ValidationError` (a `ValueError` subclass) into the drift seam's `except (OSError, ValueError)` — so it proves the REQ's raise-survival semantics. `test_malformed_manifest_never_costs_the_exit_code` was bound to this REQ and the binding was REMOVED the same day: `vendors.py::_read_manifest_key` now guards `isinstance(data, dict)` (landed in `809f1370`), so a `[]` manifest returns `{}` and NOTHING raises — that test proves the guard, not the REQ, and the decorator claimed a proof its body no longer carries. Two of the REQ's three named channels remain unbound: *absent renditions directory* returns `[]` gracefully rather than raising, so it structurally cannot prove raise-survival, and *unreadable sidecar* is exercised only on the `ValueError` branch, never the `OSError` one. **OSError branch BOUND 2026-10-03** — `test_drift_detection_raising_oserror_never_costs_the_append_or_the_exit_code` makes the sidecar path a directory, so the production read itself raises. |
> | REQ-0.35.0-08-03 | **RE-OPENED 2026-08-23** | was landed by the same test as 08-01, which asserts BOTH `claude` and `codex` are named. The operator-ruled amendment above changed the REQ's subject to the ROUTED consumer only, so that test now pins the behaviour the amended REQ forbids. Re-derive its assertions; do not read the old GREEN as coverage. **Landed 2026-08-23** — `test_warns_naming_the_routed_consumer_not_the_retained_record` on both the remember and retire halves; RED witness `arb-red-REQ-0.35.0-08-03-a84e371f264d4050bf8be165bed7b55d`. |
> | REQ-0.35.0-08-08 | **landed 2026-08-23** | `test_advisory_names_exactly_what_the_gates_grade`; count and names parsed from one rendered line, expectation derived from the predicate rather than pinned to a literal. RED witness `arb-red-REQ-0.35.0-08-08-6abd3bcd045b496d9a999cc6d196c718`. |
> | REQ-0.35.0-08-04 | **LANDED 2026-10-03** | `test_advisory_names_drift_cites_the_seam_and_gives_a_runnable_land`. The advisory names the corpus->rendition seam, cites ADR-0.0.37 § Decision Re-Alignment with that section's own item title quoted, and gives `uv run gz content land <surface>` with `--attestor` and `--attestation-text` as the next step (the flags were added in the same day's fix cycle; see the Change Log); the compose + commit recovery lines are removed. RED observed on the assertion before the change. Was OPEN: the advisory cited the failing gates and pointed at `compose` + `commit`. |
> | REQ-0.35.0-08-05 | **BOUND 2026-08-23, one disjunct of two; second disjunct STRUCTURALLY UNREACHABLE** | `test_silent_when_no_rendition_has_been_committed` proves the reachable disjunct (no committed renditions -> no advisory), with its assertions strengthened the same day from a single `gz content compose` substring check to the advisory's structural markers, so unrelated advisory output can no longer pass silently. The FIRST disjunct — *renditions already on the current corpus fingerprint* — can never co-occur with a `remember` that reaches the advisory: `remember.py` calls `append_entry` BEFORE `warn_on_rendition_drift`, `drifted_consumers` computes `current` AFTER the append, and `corpus_fingerprint` digests every entry (`rendition_store.py:56-64`), so a successful append always moves the fingerprint; duplicate-text appends are refused earlier and never reach the advisory at all. Confirmed independently by the spec review. The clause *and stderr is empty* is INEXPRESSIBLE through this harness for the same reason REQ-06 is — `CliRunner.invoke` merges both streams into one buffer (`tests/commands/common.py:69`). **RESOLVED 2026-08-24 — the operator ruled reword over changing the runner. Both residuals are removed from the REQ text rather than left unproven; the covering test is unchanged and still binds the reachable disjunct.** |
> | REQ-0.35.0-08-06 | **REWORDED 2026-08-24 — was marked landed on an unobservable claim; still OPEN** | `CliRunner.invoke` merges both streams into one buffer (`tests/commands/common.py`, `redirect_stdout(output)` and `redirect_stderr(output)`), so the stream-separation half of this REQ cannot be expressed as an assertion here at all. The byte-identical-corpus-rows half is also unasserted. Found by the independent spec review, 2026-08-23; pre-existing, not introduced by that change. **Operator ruled reword over changing the runner (2026-08-24):** the stream-separation clause is struck from the REQ and stderr-only routing is now proven nowhere in this brief; the retained byte-identity and exit-code halves still need a covering test. **BOUND 2026-10-03** — `test_corpus_row_is_byte_identical_with_and_without_drift`, paired fixtures on one frozen clock. `gz arb red` returned `none` because the property already held on the base tree; the witness is the killed mutation in the executed acceptance proof. |
> | REQ-0.35.0-08-07 | **open (structural-fence)** | audited at ADR closeout, not here |
>
> **COVERAGE CHANNEL WARNING (spec review, 2026-08-23) — DISCHARGED for REQs 01, 02 and 05 on 2026-08-23; REQ-06 stands.** The warning read: REQs 01, 02, 05 and 06 carry NO `@covers` decorator anywhere in the repo, all four are `[behavior]` whose only proof channel is `@covers`, and the rows above called them landed on PROSE evidence while `gz obpi complete` reads the decorator channel. Measured before the repair: `gz covers` reported `covered_reqs 2`, `behavior_uncovered_reqs 5`. After: `covered_reqs 5`, `behavior_uncovered_reqs 2` — REQ-04 (blocked on the unlanded `gz content land`) and REQ-06 (unprovable through this harness). **The count is not the evidence.** One binding added in that repair was removed again the same day because the decorator asserted a proof its test body did not carry, and a second was strengthened because a substring check stood in for the REQ's actual claim — both found by the independent spec review, not by the coverage number, which rose either way. REQ-06 remains unbound and unprovable here; it is an operator call, now joined by the two REQ-05 residuals recorded in its row above.
>
> **2026-10-03: REQ-04 is unblocked and landed.** `gz content land` is a registered verb since
> OBPI-0.35.0-07 completed, so the blocker recorded in the next paragraph no longer holds. The
> paragraphs below are kept as the record of what was true when they were written.
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
- `src/gzkit/commands/content/retire.py` — READ-ONLY; imported by the retire-side covering tests for `_is_named`, the name-plausibility floor. Pulled into scope by declaring `test_content_retire.py`, not by any change here — the same transitive route as `tier_policy.py` below. Declared 2026-08-25 (operator-ruled) after OBPI-0.35.0-02's invisible-attestor repair added the module-level import and `gz validate --brief-reconcile` surfaced the drift against THIS brief; that OBPI cannot amend this allowlist from inside its own transaction contract. **Amended 2026-09-29 (operator-ruled, GHI #894).** Verbatim: *"Authorize the move (Recommended)"* and *"Amend the brief (Recommended)"*. `_is_named` and its UCD constants (`_DEFAULT_IGNORABLE_LETTERS`, `_DEFAULT_IGNORABLE_LETTERS_UCD_VERSION`, `ucd_currency_warning`) moved out of this file to `src/gzkit/core/attestor_names.py` (public names `is_named`, `DEFAULT_IGNORABLE_LETTERS`, `DEFAULT_IGNORABLE_LETTERS_UCD_VERSION`, `ucd_currency_warning`) so the ledger validator can apply the same predicate; `retire.py` now imports them and `test_content_retire.py`'s import lines were repointed. This amendment permits ONLY that extraction; the rest of the READ-ONLY declaration stands, and this OBPI still changes nothing here.
- `src/gzkit/core/attestor_names.py` — READ-ONLY; the name-plausibility floor's new home (GHI #894), imported by the retire-side covering tests. Pulled into scope by declaring `test_content_retire.py`, not by any change here.
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

## Verification Clarifications

REQ-02 exercises both exception branches through the production advisory call; an absent
renditions directory that returns an empty set is a separate no-drift fixture, not evidence
that an exception was survived. REQ-04 checks the three-part advisory in combined output,
consistent with the recorded operator choice to retain the existing runner. REQ-06 controls
clock and entry identity inputs in paired fixtures so byte equality tests advisory neutrality,
not differences between independently timestamped captures. Preserve all historical
pre-landed evidence below without treating it as completion.

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
uv run gz content land AGENTS.md --attestor g0 --attestation-text "demo corpus delta attested" --dry-run
```

> **Corrected 2026-10-03, twice.** (1) The landing line read
> `uv run gz content land AGENTS.md --dry-run`. Run after the append it exits 1: the append
> moves the corpus, and landing then requires `--attestor` and `--attestation-text` even for
> a dry run (observed in a disposable checkout). (2) A middle line,
> `uv run gz validate --rendition-freshness`, is removed. After the append it exits 3 by
> design, which is the drift the advisory announces, and the Stage-4 evidence generator
> requires every Demo command to exit 0, so it blocked the packet on the state it was meant
> to show. The landing plan's old and new corpus fingerprints show the same drift.
> The first line appends to the real corpus, so run this Demo in a disposable checkout
> (`uv run gz obpi adversary-workspace <OBPI-ID>`), never in the working repository.

## Acceptance Criteria

<!--
Each checkbox carries a deterministic REQ ID and exactly one kind tag
(ADR-0.0.59; `gz validate --req-kind-discipline`):
  [behavior]         -> proven ONLY by an @covers test in tests/**
  [support]          -> proven ONLY by a path-citing ledger event + structural validator
  [structural-fence] -> proven ONLY by a parent-ADR ## Boundary Invariants entry
-->

- [ ] REQ-0.35.0-08-01 [behavior]: Given an append that leaves every committed rendition of the surface stale, when `gz content remember` runs, then the entry IS appended and the exit code is 0 — the advisory never becomes a refusal.
- [ ] REQ-0.35.0-08-02 [behavior]: Given drift-detection itself raising OSError for unreadable evidence or ValueError for malformed provenance, when `remember` runs, then the entry is STILL appended and the exit code is STILL 0 — the append is durably written before the advisory is computed.
- [ ] REQ-0.35.0-08-03 [behavior]: Given two committed renditions rendered stale by the append — one ROUTED for the surface's content type and one a retained off-route record — when `remember` runs, then the advisory names the count and the ROUTED consumer by name, and does NOT name the off-route record. **Amended 2026-08-23 (operator-ruled).** This REQ read *"two committed renditions (`claude`, `codex`) … names the count and BOTH consumers by name"*. Both named vendors were retired as `AgentContract` consumers by OBPI-0.35.0-09: `claude` was renamed `root` (its Requirement 3a) and `codex` was collapsed off-route while deliberately retained as a record (its Requirement 4a — *"NEVER delete a corpus-attested rendition"*). The property being proven is UNCHANGED and is why the REQ exists — the advisory must be SPECIFIC, naming consumers rather than emitting a generic "renditions are stale" string. What changed is which consumers are nameable: naming an off-route record prescribes a recompose that is impossible (the manifest declares no setpoint for it) and forbidden (per-vendor `AgentContract` renditions are prohibited), so the specificity this REQ demands now REQUIRES the route filter rather than a bare directory glob. Brief is `Draft`, so this is ordinary pre-attestation repair, not the attested-REQ-subject-retirement transition (`.claude/rules/governance-core.md`).
- [ ] REQ-0.35.0-08-04 [behavior]: Given the advisory fires, when the CLI's combined output is read, then it carries all three parts — the named drifted renditions, the cited ADR-0.0.37 corpus->rendition seam, and a runnable gz content land invocation naming the surface.
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

### Change Log

- **2026-10-03 — REQ-0.35.0-08-04.** Advisory prose retargeted in
  `src/gzkit/commands/content/_drift.py`: seam named and cited, next step is
  `uv run gz content land <surface>`. First draft paraphrased the seam and its test asserted
  only the ADR id; corrected before review so the test asserts the seam name with the ADR id.
- **2026-10-03 — REQ-0.35.0-08-02.** OSError branch bound through a real unreadable sidecar.
  A first draft mocked the drift call; replaced before review.
- **2026-10-03 — REQ-0.35.0-08-06.** Paired-fixture byte-identity test added.
- **2026-10-03 — Gate 3 and Gate 4.** `docs/user/manpages/content.md` gains the advisory
  contract with captured output; `features/content_remember.feature` gains two scenarios.
- **2026-10-03 — REQ-0.35.0-08-08 proof baseline.** `tests/commands/test_content_retire.py`
  could not be imported when run alone: `gzkit.ledger_events` fails if imported before
  `gzkit.ledger` (a production import cycle outside this brief's Allowed Paths, recorded with
  `gz insights remember`). The test module now imports `gzkit.ledger` first, so the REQ-08
  covering test runs on its own. The production cycle is not repaired here.
- **2026-10-03 — finding `QR-0.35.0-08-04-printed-land-invocation-refused-in-firing-state`
  (quality review, receipt `arb-step-qualityreview-76c995ef5bdf4968934b19c8c19aa1ab`;
  the spec review, `arb-step-specreview-f62289ff7c9040fea40fe1f83cfad942`, noted the same
  root unmapped), REQ-0.35.0-08-04.** The advisory printed bare
  `uv run gz content land <surface>`, which landing refuses in exactly the state the advisory
  fires, because a moved corpus requires `--attestor` and `--attestation-text`. Repair: the
  advisory prints the invocation with both flags, in the placeholder wording landing's own
  refusal uses. The unit test now extracts the printed command by shape and runs it through
  the real parser, so a misspelled verb or flag fails there. The unit fixture cannot carry a
  landing, so recovery is demonstrated at Gate 4: a scenario runs `remember` on the
  three-consumer landing project, shows bare `land` refused for want of attestation, then
  runs the printed command with its placeholders filled and observes the landing complete.
- **2026-10-03 — review notes, same cycle.** Prose assembly extracted to `_advisory_lines`
  to keep `warn_on_rendition_drift` inside the function-size band. The REQ-01 and REQ-02
  tests now guard their fixture premises; the REQ-05 test's vestigial `compose` assertion
  is replaced. The manpage states the no-sidecar exclusion and the attested next step.
- **2026-10-03 — round-2 reviews (spec `arb-step-specreview-a46f35dac082412eb20aed1f300f669c`,
  quality `arb-step-qualityreview-b783acaec8ed4db8945db0259cf0392c`).** Both accepted all
  eight proofs and closed the REQ-0.35.0-08-04 finding against the repaired state. Their
  unmapped notes were then repaired in a second cycle: the stale module docstring in
  `features/steps/content_remember_steps.py`, and a `unittest.main()` block in
  `tests/commands/test_content_remember.py` that sat above the last test class (18 tests
  ran through it before the move, 21 after). The REQ-04 proof gained a fourth substitution,
  the attestation flags dropped from the printed command. The `## Demo` third line was
  corrected the same day.
- **2026-10-03 — Step 4b round 1 (Codex, tier 1, receipt
  `arb-step-codexadversary-c811f6d7391a45ca9b339d772f89b0db`): refuted, two mapped findings.**
  The reviewer replayed all eleven recorded substitutions and ran the Demo, both test
  modules and both features in a disposable checkout, then produced two counterexamples.
  - `AR-0.35.0-08-01-advisory-write-error-changes-exit`, REQ-0.35.0-08-01. A stderr sink
    raising `OSError` while the advisory was written made `remember` exit 1 after the row
    was durable; the flush and print sat outside the best-effort handler. Repair: emission
    is guarded for `OSError` and `ValueError`, as detection is. Covering test
    `test_advisory_output_fault_never_costs_the_exit_code` (paired with a no-drift control).
  - `AR-0.35.0-08-04-unquoted-surface-breaks-printed-command`, REQ-0.35.0-08-04. A surface
    named `Land Surface.md` printed a command that split into two arguments and exited 2.
    Repair: the printed command uses `shlex.quote(surface)`; names without special
    characters print unchanged. Covering test
    `test_printed_command_quotes_a_surface_name_containing_a_space`.
  - Two unmapped notes repaired in the same batch. The REQ-0.35.0-08-08 test's fixture now
    routes a consumer named `alpha` through a vendor manifest, so a hard-coded
    `stem != "root"` copy of the predicate, which survived before, now fails it.
    `warn_on_rendition_drift`'s docstring no longer says a retirement can only shrink the
    floor. The manpage states both new behaviours.
  Closure of both findings is for the Step 4b follow-up to give or withhold.
- **2026-10-03 — round-5 Stage-2 reviews of the Step 4b repairs (spec
  `arb-step-specreview-dacab557598a422d9233afd45ad0a2df`, quality
  `arb-step-qualityreview-18e3f5de23da4a8a9a8201508d4c601a`).** Both accepted all eight
  proofs and closed both Step 4b findings and the earlier REQ-04 finding by reading. Their
  notes are not mapped to any REQ and are carried to the ceremony unrepaired, except the
  manpage sentence, which was corrected (the quoting is POSIX-shell quoting):
  - the emission handler's `ValueError` arm has no covering assertion, and
    `test_advisory_output_fault_never_costs_the_exit_code` does not assert the failing sink
    was reached (its reach is shown by the killed `emission-fault-not-guarded` substitution);
  - `sys.stdout.flush()` shares the emission `try`, so a stdout fault also drops an advisory
    stderr could have delivered;
  - `tests/commands/test_content_retire.py` keeps a docstring saying retirement only ever
    shrinks the floor; `TestContentRememberDriftWarning` is past the class-size guidance;
  - an output fault on the SUCCESS line or the ledger append in
    `src/gzkit/commands/content/remember.py`, after the row is durable, also exits 1. It
    behaves the same with and without drift, so it is not the advisory's doing; whether
    Requirement 1's "on EVERY path" reaches it is the operator's ruling.
- **2026-10-03 — Step 4b round 2, focused follow-up (Codex, tier 1): accepted, all three
  mapped findings closed by execution.** The reviewer re-ran its own round-1 counterexamples
  on the repaired tree (both now pass), replayed all 14 recorded substitutions, ran both
  test modules, both features and the Demo, and approved all eight current proofs. Its
  verdict lines: `CORROBORATED-WITH-CAVEATS` / `not-refuted`. Its stated weakest point: the
  REQ-01 output-fault test neither asserts the failing sink was reached nor covers the
  emission handler's `ValueError` arm; its own instrumented probe observed both arms reached
  with exit 0. It ran the success-line and ledger output faults (exit 1, row durable, with
  and without drift) and judged them outside REQ-01; that is its opinion, and the question
  stays with the operator.
  Two receipts carry this round. `arb-step-codexadversary-532836277d0e409db476f5300dd499ab`
  is the executed review; the importer refused it because three unmapped observations reused
  finding ids from earlier rounds with different text. The reviewer's own thread was resumed
  and re-issued the same object with new ids for those three and the statement "No judgment
  changed": `arb-step-codexadversary-786f351877904100a29553682a505316`, which is the imported
  record. Every other field was compared and is identical.
- **2026-10-03 — correction made AFTER attestation and completion (Stage 5).** The operator
  attested ("attest completed") and `gz obpi complete` recorded the completion. The per-change
  gate then failed on `gz validate --red-parity`: REQ-0.35.0-08-06's RED witness was
  `failure_class: none`, which that validator never lets an executed acceptance proof erase.
  The orchestrating agent had carried that `none` past Stage 3, whose table marks it blocking,
  and had reported red-parity as passing when it passed only because the brief was not yet
  `Completed`. That error is recorded with `gz insights remember`.
  Repair, in `tests/commands/test_content_remember.py` only: a second REQ-0.35.0-08-06
  covering test, `test_exit_code_and_row_are_identical_with_and_without_drift_under_an_output_fault`.
  REQ-06's exit-code clause is false on the base tree under an advisory output fault (drift
  exits 1, no drift exits 0), so the test fails there by assertion: RED receipt
  `arb-red-REQ-0.35.0-08-06-e102516d2600415e879c371edc281c80` (`failure_class` assertion, working-tree base). No production file changed.
  The operator, asked how much re-review to run on the post-attestation change, ruled
  verbatim: "Finish the two reviews, then sync (Recommended)". Round-6 Stage-2 reviews: spec
  `arb-step-specreview-1b1d4259f37b41bf93749016a6ce246a` and quality
  `arb-step-qualityreview-c24004323feb4ed3a0df08a5cc1e626e`, both accepted, both judging the test
  to be REQ-06 as written and not REQ-01 re-labelled. **No Step 4b round ran on this
  correction: the cross-vendor reviewer has not seen the added test.** Post-correction records:
  lint `arb-ruff-2f643767eaed463f800c740ce9c4e7b9`, typecheck
  `arb-step-typecheck-3c45e0e3be444b809cc04e940bba529c`, full unit suite
  `arb-step-unittest-36689e12c5c948b5ba56d8c81d43c322` (11408 tests, exit 0).
  The Implementer dispatch for this correction has no ledger record, because the pipeline
  marker had been removed at completion. The Stage-4 packet under `.gzkit/evidence/` is the
  packet the operator attested against and is left as it was. Reviewer notes carried: the
  REQ-06 and REQ-01 proofs share one discriminating substitution on the exit-code clause;
  the byte-identity half of REQ-06 still has no RED of its own; the dated 2026-08-24 sentence
  in the REQ-0.35.0-08-06 acceptance criterion ("still UNASSERTED ... remains OPEN"), and the
  "Brief is `Draft`" sentences in three criteria, describe a state that no longer holds and
  are left as dated contract text.
- **2026-10-03 — outside this brief (four items recorded with
  `gz insights remember` for an operator routing ruling, and one noted here).** The `gz-content-remember` skill
  still shows the compose, advise, commit chain as the way to land a captured entry.
  `docs/user/runbook.md` still says a retirement implies no recomposition. The
  `gzkit.ledger_events` import cycle named above is a production defect.
  The rendition-freshness gate's recovery message and `retire`'s floor-direction prose still
  say recompose and re-attest. Noted here only: this brief's frontmatter `allowlist` omits
  `src/gzkit/core/attestor_names.py`, which its Allowed Paths body lists as READ-ONLY.

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
uv run gz arb step --name unittest -- uv run unittest-parallel -t . -s tests --buffer
Ran 11407 tests
OK (skipped=7)
receipt: arb-step-unittest-c4592cebdbf84d95902c8fb71f253af5 (exit_status 0)

uv run -m unittest tests.commands.test_content_remember tests.commands.test_content_retire
Ran 79 tests
OK
```

### Code Quality

```text
uv run gz arb ruff        -> exit_status 0, receipt arb-ruff-beeb7f3446134fdd8d54c639fa57a6bc
uv run gz arb typecheck   -> exit_status 0, receipt arb-step-typecheck-99ecd388c77c46e2a1aa13afb68eec9b
```

### Gate 3 (Docs)

```text
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
exit_status 0, receipt arb-step-mkdocs-d2c1b207d90044a59557adfbb618846d
```

### Gate 4 (BDD)

```text
uv run gz arb step --name behave -- uv run -m behave features/content_remember.feature features/content_land.feature
2 features passed, 0 failed, 0 skipped
20 scenarios passed, 0 failed, 0 skipped
140 steps passed, 0 failed, 0 skipped
receipt: arb-step-behave-b9ae23437ab347ccb163176bb3bde746 (exit_status 0)

uv run gz arb step --name behave -- uv run -m behave --tags=@REQ-0.35.0-08-04,@REQ-0.35.0-08-05 features/
3 scenarios passed, 0 failed, 453 skipped
receipt: arb-step-behave-178ac5a438fb4d8db9f00195520f34cf (exit_status 0)
```

### Gate 5 (Human)

```text
Operator (g0), 2026-10-03, verbatim: attest completed
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

Before, `gz content remember` warned about drifted renditions but pointed at a per-consumer
compose and commit recovery and never cited the seam, and GHI #654 had named the original
defect as the silence. Now the advisory names which routed consumers drifted, cites the
corpus->rendition seam (ADR-0.0.37 § Decision Re-Alignment), and prints the one
`gz content land` command that recovers, with the attestation flags that command requires in
that state. The append is never refused and the exit code stays 0, including when drift
detection or the advisory's own output fails.

### Key Proof


The brief's Demo, run by the Stage-4 evidence generator in a disposable copy on 2026-10-03 (both commands exit 0). The entry id is elided because it carries a timestamp.

```text
$ uv run gz content remember AGENTS.md --section behavior-rules --text "Advisory demonstration entry." --tier compressible
Appended corpus entry corpus-behavior-rules-... to AGENTS.md [behavior-rules].

Warning: this append drifted 1 committed rendition(s) of 'AGENTS.md'
  (root). They no longer derive from the current corpus,
  so `gz check` will now fail on:
    - Rendition freshness

  Why: the corpus->rendition seam (ADR-0.0.37 § Decision Re-Alignment). The
  corpus is the "Append-only corpus (source of truth)" and a committed
  rendition is derived from it, so this append leaves each one stale
  until it is landed.

  Land the corpus into every consumer in one governed step. The corpus moved,
  so the landing takes your attestation of the corpus change:
    uv run gz content land AGENTS.md \
        --attestor <handle> --attestation-text "<the operator's verbatim words>"
```

Executed proof for the three parts: `proof-9547d290ab01499f969af47e274b81e3` (REQ-0.35.0-08-04), five substitutions each killed on an assertion. Full unit suite `arb-step-unittest-c4592cebdbf84d95902c8fb71f253af5` (11407 tests, exit 0); lint `arb-ruff-beeb7f3446134fdd8d54c639fa57a6bc`; typecheck `arb-step-typecheck-99ecd388c77c46e2a1aa13afb68eec9b`; docs `arb-step-mkdocs-d2c1b207d90044a59557adfbb618846d`; Gate 4 `arb-step-behave-b9ae23437ab347ccb163176bb3bde746` (20 scenarios). Independent cross-vendor confirmation: `arb-step-codexadversary-786f351877904100a29553682a505316`.

### Step 4b — Independent Adversarial Validation

**Adversary identity and tier.** Tier 1, cross-vendor: OpenAI Codex dispatched through the
`openai-codex` Claude Code plugin (`codex-companion.mjs task --write --cwd <disposable checkout>`),
ARB-wrapped on every round. Each round ran in a throwaway writable copy of the reviewed tree, so
the adversary replayed the recorded proofs and ran its own probes. Codex reported `ready: true`
before round 1, so tiers 2 and 3 were forbidden.

**The adversary refuted this OBPI once before corroborating it.** The claims it broke were
REQ-01 (an advisory output fault cost the exit code) and REQ-04 (the printed command was not
runnable for a surface name containing a space).

| Round | Receipt | Verdict | Claims broken / outcome |
|---|---|---|---|
| 1 | `arb-step-codexadversary-c811f6d7391a45ca9b339d772f89b0db` | **NOT-CORROBORATED / refuted** | All eleven recorded substitutions replayed; 7 of 8 proofs approved. `AR-0.35.0-08-01-advisory-write-error-changes-exit` (REQ-01): a stderr sink raising `OSError` while the advisory was written made `remember` exit 1 after the row was durable. `AR-0.35.0-08-04-unquoted-surface-breaks-printed-command` (REQ-04): for `Land Surface.md` the printed command split into two arguments and exited 2 |
| 2 | `arb-step-codexadversary-532836277d0e409db476f5300dd499ab` | **CORROBORATED-WITH-CAVEATS / not-refuted** | Focused follow-up. Its own two counterexamples re-run and passing; all 14 recorded substitutions replayed; 8 of 8 proofs approved; three closures. Import REFUSED: three unmapped observations reused earlier finding ids with different text |
| 2, re-issue | `arb-step-codexadversary-786f351877904100a29553682a505316` | **accepted** (the imported record) | The same reviewer's resumed thread re-issued the round-2 object with new ids for those three observations and the statement "No judgment changed". Every other field compared identical |

**How each was resolved.** REQ-01: advisory emission in `warn_on_rendition_drift` is guarded for
`OSError` and `ValueError`, as detection already was, with a red-first paired test
(`test_advisory_output_fault_never_costs_the_exit_code`) and an `emission-fault-not-guarded`
substitution. REQ-04: the printed command uses `shlex.quote(surface)`, with a red-first test
(`test_printed_command_quotes_a_surface_name_containing_a_space`) and a
`surface-not-shell-quoted` substitution. The earlier Stage-2 finding
`QR-0.35.0-08-04-printed-land-invocation-refused-in-firing-state` (the printed command lacked the
attestation flags landing requires) was closed again by the adversary's own three-consumer probe:
bare `land` exit 1, the printed attested command exit 0, no remaining drift. No operator ruling
was needed to close a finding; no requirement, allowlist or threat-model boundary was amended.

**What the adversary left open, unmapped to any requirement.** Its weakest point: the REQ-01
output-fault test neither asserts the failing sink was reached nor covers the handler's
`ValueError` arm (its own probe observed both arms reached with exit 0). It executed an output
fault on the success line and on the ledger append in `remember.py` (exit 1, row durable, with and
without drift) and judged both outside REQ-01; whether Requirement 1's "on EVERY path" reaches
them was put to the operator and is unruled at completion. It confirmed the five items outside
this brief's Allowed Paths that the Change Log records. It ran on macOS only.

### Implementation Summary


- Parent ADR Decision item implemented: § Decision item 7, "`gz content remember` gains a POST-APPEND ADVISORY -- three-part recovery prose per `.claude/rules/guardrail-feedback-prose.md`, never a refusal, exit stays 0. Capture must never be blocked: losing the operator's words is strictly worse than a red tree. The tree going red is correct; GHI #654's defect is the SILENCE, not the redness." (Feature Checklist item #8)
- Files created: none
- Files modified: `src/gzkit/commands/content/_drift.py`, `tests/commands/test_content_remember.py`, `tests/commands/test_content_retire.py`, `features/content_remember.feature`, `features/steps/content_remember_steps.py`, `docs/user/manpages/content.md`
- Advisory: shared by `remember` and `retire`; names the count and each routed consumer graded by `is_graded_rendition`, cites the corpus->rendition seam (ADR-0.0.37 § Decision Re-Alignment), and prints `uv run gz content land <surface>` with `--attestor` and `--attestation-text`, the surface quoted for a POSIX shell. Detection and emission are both best-effort: neither can cost the append or the exit code.
- Tests added: six unit tests in `TestContentRememberDriftWarning` (three-part advisory run through the real parser, spaced surface name, unreadable sidecar, advisory output fault, byte-identical rows, and, added after attestation, the paired output-fault test for REQ-06's exit-code clause) and three BDD scenarios, one of which runs the command extracted from the advisory and observes the landing. The REQ-08 test's fixture now routes a consumer named `alpha`.
- Date completed: 2026-10-03
- Attestation status: operator attested ("attest completed")
- Defects noted: stderr-only routing is proven by no test (struck from REQ-05 and REQ-06 by operator ruling 2026-08-24); the REQ-01 output-fault test does not assert the failing sink was reached and does not cover the emission handler's `ValueError` arm; an output fault on the success line or the ledger append in `remember.py` also exits 1 after the row is durable, with or without drift, and whether Requirement 1 reaches it is unruled; five items outside this brief's Allowed Paths are recorded with `gz insights remember` (see the Change Log)

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.35.0-08: the post-append advisory in src/gzkit/commands/content/_drift.py names the drifted routed consumers, cites the corpus->rendition seam (ADR-0.0.37 § Decision Re-Alignment) and prints the attested gz content land command; the append is never refused and the exit code stays 0. Receipts: arb-ruff-beeb7f3446134fdd8d54c639fa57a6bc; arb-step-typecheck-99ecd388c77c46e2a1aa13afb68eec9b; arb-step-unittest-c4592cebdbf84d95902c8fb71f253af5 (11407 tests, exit 0); arb-step-mkdocs-d2c1b207d90044a59557adfbb618846d; arb-step-behave-178ac5a438fb4d8db9f00195520f34cf (3 scenarios); arb-step-behave-b9ae23437ab347ccb163176bb3bde746 (20 scenarios). Step 4b, tier 1 Codex: round 1 arb-step-codexadversary-c811f6d7391a45ca9b339d772f89b0db refuted with two findings, both repaired; round 2 arb-step-codexadversary-786f351877904100a29553682a505316 accepted, 8 of 8 proofs approved, three findings closed by execution. 7 BEHAVIOR REQs covered by tests; REQ-0.35.0-08-07 is a structural fence audited at ADR closeout. Packet replay VERIFIED: .gzkit/evidence/OBPI-0.35.0-08-remember-post-append-advisory.stage4a.md.
- Date: 2026-10-03

---

**Date Completed:** 2026-10-03

**Evidence Hash:** -
