# Plan — OBPI-0.35.0-09-codex-playback-wiring (REQ coverage completion)

**OBPI:** OBPI-0.35.0-09-codex-playback-wiring
**Parent ADR:** ADR-0.35.0-canon-entry-corpus-landing (checklist item #9)
**Lane:** Heavy
**Entry:** Stage 2 — the routing/fence implementation landed 2026-08-17; the
BEHAVIOR REQs it was authored under were never bound to covering tests.

## Context

`uv run gz covers OBPI-0.35.0-09-codex-playback-wiring --json` reports
`covered_reqs: 2, uncovered_reqs: 9, behavior_uncovered_reqs: 8` (18.2%).

The implementation is present — the collapse of `AgentContract` to a single
`root` consumer, the vendor-manifest fence, the shared `is_graded_rendition`
predicate, and the min-cap delivery witness all landed. What did not land is the
REQ→test binding: this OBPI's tests were tagged against the **superseded** REQs
their validators were originally built under (`REQ-0.0.74-09-*`,
`REQ-0.0.37-22-*`), so they pass without proving this brief's claims.

Only `REQ-09-08` and `REQ-09-09` carry `@covers` for this OBPI.

`REQ-09-07` is `[structural-fence]` — proven by a parent-ADR
`## Boundary Invariants` entry, never by a test (ADR-0.0.59). It is out of
scope for the coverage pass and must not be forced into a unit test.

## Files

All within the brief's declared allowlist:

- `tests/governance/test_rendition_floor_coherence.py` — REQ-05, REQ-11
- `tests/governance/test_rendition_freshness.py` — REQ-11
- `tests/governance/test_surface_delivery_witness.py` — REQ-10
- `tests/governance/test_compose.py` — REQ-01, REQ-02, REQ-03
- `tests/test_sync_surfaces.py` — REQ-02, REQ-04, REQ-06

## Steps

1. **REQ-09-05 — tag only.** `test_missing_invariant_entry_is_fail_closed`
   (`test_rendition_floor_coherence.py:57`) already asserts exactly the REQ's
   semantic: an invariant-tier entry removed from a rendition fails the gate
   closed naming that consumer. Add `@covers("REQ-0.35.0-09-05")` alongside the
   existing tag. Verify the assertion before tagging — a tag on a test that does
   not assert the REQ is the GHI #272 cosmetic-backfill pattern.

2. **REQ-09-11 — tag + author.** `test_staged_candidate_file_is_not_treated_as_a_rendition`
   (`test_rendition_freshness.py:148`) covers the *candidate* half. The REQ also
   asserts a **superseded off-route rendition** is not graded, and exactly one
   artifact is graded. Author the missing half against `is_graded_rendition`,
   then tag both.

3. **REQ-09-10 — author.** `test_surface_delivery_witness.py` has 17 tests, zero
   `@covers`, and zero occurrences of `min_cap`/`minimum`. The REQ's semantic —
   the single delivered surface is measured against the **minimum** declared cap
   and the witness **names** which vendor set it — is untested. Author it.

4. **REQ-09-01 — author.** The consumer must be a *parameter* of
   `sync_surfaces.sync_agents_md` and `governance.compose.render_agent_contract`,
   not a literal. No test drives a named consumer through either. Author one that
   passes a consumer and asserts that consumer's rendition is the one loaded.

5. **REQ-09-02 — tag + author.** `test_rendered_bytes_are_the_committed_rendition_verbatim`
   (`test_compose.py:88`) covers the verbatim half. The "written to root
   `AGENTS.md` **and to no other contract path**" half is untested — that is the
   half that would have caught the second-AGENTS.md failure the objective names.
   Author the destination assertion, tag both.

6. **REQ-09-03 — verify then tag.** `test_missing_rendition_returns_empty_bytes`
   (`test_compose.py:94`) asserts empty bytes; the REQ asserts **no file written
   and no error raised**. If the existing test does not assert the no-write
   property, author it rather than tagging over the gap.

7. **REQ-09-04 and REQ-09-06 — author.** Byte-identity of AGENTS.md across the
   routing change (04) and determinism across two sync runs (06). Both are
   whole-pipeline properties; neither has a test.

8. **RED witness per REQ.** For each BEHAVIOR REQ, run
   `uv run gz arb red --req <REQ-ID> --obpi OBPI-0.35.0-09-codex-playback-wiring`
   and record `failure_class`. A `none` verdict is blocking — the test cannot
   fail when the logic changes, so it witnesses nothing. Tag-only REQs (05) still
   require the witness: an existing passing test proves nothing about
   falsifiability under this REQ.

9. **Task envelope.** All eleven TASKs are `seq=01`, which Signature (b) blocks
   without a `req_atomic:` exemption. This pass subdivides genuinely multi-step
   REQs via `uv run gz task start --seq next` rather than declaring atomicity —
   REQs 02, 03 and 11 each have a tag half and an author half, so they are
   demonstrably not atomic.

10. **Step 4b adversary.** Heavy lane requires an independent adversary before
    attestation. Tier 1 is Codex via `/codex:adversarial-review`; check
    `codex:setup` `ready` first and only drop tiers on a genuine `ready: false`.

## Verification

From the brief's declared verification block:

```
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --invariant-coherence
uv run gz validate --rendition-floor-coherence
uv run gz validate --surfaces
uv run gz validate --req-kind-discipline
uv run mkdocs build --strict
```

Plus the gate this plan exists to clear:

```
uv run gz covers OBPI-0.35.0-09-codex-playback-wiring --json   # uncovered_reqs == 0
uv run gz obpi precomplete OBPI-0.35.0-09-codex-playback-wiring
```

## Step 6a — Plan-Before-Exploration Disclosure

**Destination-in-mind.** Before writing this plan I had already formed the
conclusion that the remedy was *"add `@covers` tags to the tests that already
exist."* That destination was partly wrong, and the survey is what corrected it:
`test_surface_delivery_witness.py` has no test of the min-cap semantic at all,
and the superseded-rendition half of REQ-11 is likewise absent. Had I acted on
the destination I formed first, I would have tagged five tests, watched
`gz covers` go green, and shipped an OBPI whose REQs were *labelled* proven
rather than proven. That is the failure this brief's own objective describes at
one layer up — a doctrine with no mechanical witness.

**Rejected alternatives.**

1. *Declare `req_atomic:` for all eleven REQs to clear Signature (b).* Rejected:
   REQs 02, 03 and 11 each decompose into a tag half and an author half, so
   asserting indivisible labor would be false. The exemption exists for REQs with
   no labor below them, not as a route around subdivision.
2. *Waive the coverage gate via `data/behave_coverage_waivers.json`.* Rejected on
   canon: `--accept-uncovered` is refused on every lane because BEHAVIOR's only
   proof channel is a `@covers` test (AGENTS.md § OBPI Acceptance Protocol).
   A waiver here would be the gate-satisfying move rather than the gate-meeting
   one.
3. *Re-scope the brief to drop the uncovered REQs.* Rejected: the REQs describe
   behavior that shipped. Removing them to make the gate pass would falsify the
   brief rather than reconcile it, and the operator's correction doctrine is
   explicit that discovering more is needed to fulfil intent is a **correction**,
   not a scope reduction.
4. *Enter at `--from=verify` and push through.* Rejected — that is what produced
   this plan. The entry assumed implementation-complete; the coverage gate proves
   otherwise, so the correct entry is Stage 2.
