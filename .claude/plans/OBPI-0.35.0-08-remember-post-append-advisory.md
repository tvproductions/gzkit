# Plan — OBPI-0.35.0-08-remember-post-append-advisory (coverage-channel repair)

## Context

`gz covers OBPI-0.35.0-08-remember-post-append-advisory --json` measured
2026-08-23: `total_reqs 8`, `covered_reqs 2`, `behavior_uncovered_reqs 5`.
Only REQ-03 and REQ-08 carry a `@covers` binding. REQ-01, -02, -04, -05 and -06
are `[behavior]`, whose sole proof channel under ADR-0.0.59 is a `@covers` test,
and the OBPI-completion REQ-coverage gate is unwaivable on every lane.

The brief's PARTIALLY PRE-LANDED table records REQ-01/-02/-05/-06 as landed on
prose evidence, citing tests by name. Those tests exist; they carry no decorator.
The table is Layer-1 authorship, the decorator scan is what the gate queries —
the two disagree, and the gate is the one that binds.

Scope of this plan is the coverage channel only. Production behaviour landed
under `48a5f799` (advisory) and `dcf29b95` (regression repair) and is NOT
re-implemented here.

## Out of scope (named blockers, not deferrals)

- **REQ-04** — requires the advisory to name `gz content land <surface>`.
  `uv run gz content land --help` exits 2 (measured 2026-08-23); the verb ships
  in OBPI-0.35.0-07, which is `Draft`. Blocked by construction.
- **REQ-06** — `CliRunner.invoke` merges stdout and stderr onto one buffer
  (`tests/commands/common.py`), so the REQ's stream-separation claim cannot be
  expressed as an assertion through this harness. Operator call.
- **REQ-07** — `[structural-fence]`; proof channel is the parent-ADR
  `## Boundary Invariants` entry, audited at ADR closeout. Never a unit test.

This OBPI therefore CANNOT reach Gate 5 in this pass, and no Gate 5 is claimed.
The pipeline is expected to halt at Stage 3 Phase 1b with REQ-04 and REQ-06
named. That halt is pre-existing, not created by this work.

## Files

- `tests/commands/test_content_remember.py` — the only file edited (brief
  allowlist line 114).
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-08-remember-post-append-advisory.md`
  — evidence-section update recording the coverage repair and the REQ-05 arm-1
  finding (brief allowlist, this brief's own evidence sections).

No `src/**` file is touched.

## Steps

1. **REQ-0.35.0-08-01 — author a covering test, do not merely decorate.**
   The brief cites `test_warns_naming_the_routed_consumer_not_the_retained_record`
   for this REQ, but that test asserts `exit_code == 0` and never reads the
   corpus, so the REQ's "the entry IS appended" half is unasserted. Bolting a
   decorator onto it would claim proof the assertions do not carry.
   Author a dedicated test in `TestContentRememberDriftWarning`: seed the surface
   and a stale on-route committed rendition, run `remember`, then assert BOTH
   halves — `exit_code == 0` AND the corpus on disk holds exactly the appended
   entry. Bind `@covers("REQ-0.35.0-08-01")`.

2. **REQ-0.35.0-08-02 — bind the two existing raising-path tests.**
   `test_malformed_sidecar_never_costs_the_append_or_the_exit_code` and
   `test_malformed_manifest_never_costs_the_exit_code` both already assert the
   REQ's exact semantics (drift detection raises -> entry still appended, exit
   still 0, corpus read back). Add `@covers("REQ-0.35.0-08-02")` to each. No
   assertion change is needed; these tests were authored against the REQ.

3. **REQ-0.35.0-08-05 — bind the reachable arm; report the unreachable one.**
   Add `@covers("REQ-0.35.0-08-05")` to
   `test_silent_when_no_rendition_has_been_committed`, which proves arm 2 ("a
   surface with no committed renditions at all -> no advisory").
   Arm 1 ("renditions already on the current corpus fingerprint") is
   STRUCTURALLY UNREACHABLE for this verb: `warn_on_rendition_drift` computes
   `current = corpus_fingerprint(load_corpus(...))` AFTER the append
   (`src/gzkit/commands/content/_drift.py`), and `corpus_fingerprint` digests
   every entry (`src/gzkit/content/rendition_store.py:56`), so a successful
   `remember` always moves the fingerprint and no sidecar can match it at the
   moment the advisory runs. Do NOT author a test that fakes the arm. Record the
   finding in the brief and route it to the operator alongside REQ-06.

4. **Record the findings in the brief's PARTIALLY PRE-LANDED table** — REQ-01
   citation corrected to the new test, REQ-02 and REQ-05 marked bound, REQ-05
   arm 1 recorded as structurally unreachable pending an operator call.

## Verification

- `uv run gz covers OBPI-0.35.0-08-remember-post-append-advisory --json` —
  expect `covered_reqs` 2 -> 5, `behavior_uncovered_reqs` 5 -> 2 (REQ-04, -06).
- `uv run gz arb step --name unittest -- uv run -m unittest -q`
- `uv run gz arb ruff`
- `uv run gz arb typecheck`
- `uv run gz validate --req-kind-discipline`
- Negative control for the REQ-01 test: the RED witness (`gz arb red`) cannot
  fire here because production already landed, so it returns `not-applicable`.
  Substitute a manual negative control — break the production behaviour, observe
  the new test fail on its assertion, restore.

## Notes — Step 6a disclosures (plan-before-exploration ordering)

**Destination-in-mind.** Before writing this plan I had already formed the
conclusion that step 2 and step 3 are pure decorator additions and step 1 is not
— that the REQ-01 citation was hollow. That conclusion came from reading the
brief's own COVERAGE CHANNEL WARNING and then the cited test body, in that
order, so the plan is partly a reconstruction of a destination reached during
exploration. The REQ-05 arm-1 unreachability was NOT in mind beforehand; it
surfaced while reading `_drift.py` to check whether arm 1 was testable, and it
changed the plan from "add three decorators" to what is written above.

**Rejected alternatives.**
(a) *Decorate all four cited tests and move on.* Rejected: it would bind
REQ-01 to a test that cannot fail when the append breaks, producing a green
coverage gate over an unproven behaviour — the hollow-test family the two-stage
review exists to catch.
(b) *Author a test for REQ-05 arm 1 by calling `drifted_consumers` directly with
a hand-set fingerprint.* Rejected: it would prove a helper, not the REQ, whose
subject is `remember`'s observable behaviour. Testing the unreachable arm through
a side door would make the gate green while the stated behaviour stays
unexercised.
(c) *Re-word REQ-05 to drop arm 1, and REQ-06 to drop stream separation.*
Rejected as an agent-side action: amending an acceptance criterion to match what
is testable is an operator call, not a convenience the implementer takes.
(d) *Build OBPI-0.35.0-07 first so REQ-04 clears and this OBPI can complete.*
Rejected because the operator explicitly ruled the coverage work first and set
that step aside this session.
