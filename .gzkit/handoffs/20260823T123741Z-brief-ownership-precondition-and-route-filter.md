---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-23T12:37:41Z'
agent: claude-code
continues_from: 20260823T022851Z-session-close-861-865-corpus-and-preflight.md
---

## Current State Summary

Opened as a handoff review of `20260823T022851Z-session-close-861-865-corpus-and-preflight.md` and became four landed commits. The operator ruled proceed on advised steps 2 and 3, set aside step 4 (resume ADR-0.35.0), and step 1 was already discharged before this session opened. Tree clean at `57d28f2b`, HEAD == origin/main, no locks held.

Landed oldest first: `1827c48e` (seven mechanical CHECKPOINT exit bookmarks, isolated from the canon change); `ee709fc8` (the brief-ownership PRECONDITION seated as invariant-tier canon in AGENTS.md § Defect-fix routing, corpus 76 -> 77 entries, corpus attestation 'attest completed' by g0); `e51427fd` (OBPI-0.35.0-08 amended for the post-collapse route set, plus a new REQ-0.35.0-08-08); `809f1370` (the route-filtered enumeration in the drift advisory and a class fix in the vendor-manifest reader). `6465a985` and `57d28f2b` are git-sync ledger sweeps.

NOTHING IS IN FLIGHT. ADR-0.35.0 remains the ADR in flight by ascending-semver doctrine — heavy, Pending, 1/10 OBPIs landed, closeout BLOCKED — and the operator set aside resuming it.

## Important Context

THE PRECONDITION LANDED AND THEN CAUGHT A REAL COLLISION WITHIN THE HOUR, on its first live use. `ee709fc8` seated a rule requiring the defect-fix routing thresholds to be preceded by a grep of the OBPI briefs asking WHO OWNS THE WORK. Applied to this session's own next task it surfaced OBPI-0.35.0-09 Requirement 4a — 'NEVER delete a corpus-attested rendition' — which forbade a codex-rendition deletion the agent had recommended and the operator had already approved. The DISPOSITION-over-match clause is what did the work: the first loose grep matched 40 briefs and established nothing, reproducing the entry-id-in-brief 7/7 failure the clause exists to name.

AGENTS.md IS PLAYBACK-ONLY and the candidate IS the surface. Playback writes the committed rendition's bytes verbatim, so placement is AUTHORED, not derived. Every other invariant-tier entry renders under § Operator Doctrine regardless of its section field; seating this one under § Defect-fix routing required writing it there in the candidate.

ONLY root IS ROUTED. The AgentContract route set is exactly one consumer and the manifest declares no codex setpoint. The codex rendition is a RETAINED RECORD frozen at 59 corpus entries since 2026-08-17 — never rot, never to be deleted.

THE TWO-STAGE REVIEW EARNED ITS COST. spec-reviewer and quality-reviewer both returned CONCERNS and both finding sets were applied. The quality reviewer found a production defect the change INTRODUCED: the shared grading predicate reaches the vendor-manifest reader, which called .get() on an unguarded json.loads result, so a manifest whose top level is valid JSON but not an object raises AttributeError past the seam's OSError/ValueError handler — costing the exit code after the corpus row is durable, which that handler's own comment forbids in those words. The spec reviewer found the 'parity' test was not parity: it pinned the expectation to a literal before comparing, so a hardcoded stem-not-equal-codex would pass — the exact private copy the REQ forbids.

THE ARB RECEIPT IS STILL THE ONLY HONEST EXIT CODE. The harness notification reported 'exit code 0' on a run whose arb ruff exit_status was 1, and the log printed 'All checks passed!' immediately below that failing line — it belonged to the next stage.

THE PRE-PUSH GATE RUNS ~3.5 MINUTES. Background every push.

## Decisions Made

- [operator-ruled] Proceed on advised steps 2 (git-sync) and 3 (seat the GHI #864 routing guidance in AGENTS.md); step 4 (resume ADR-0.35.0) SET ASIDE. Booked via handoff decide with --set-aside.
- [operator-ruled] Corpus attestation for the AGENTS.md canon add, verbatim 'attest completed', relayed through --attestation-text enriched with receipt ids. Corpus attestation, NEVER Gate 5.
- [operator-ruled] Take the drift-warning finding as a direct fix and retire the codex rendition alongside it — SUPERSEDED the same turn when the precondition surfaced OBPI-0.35.0-09 Requirement 4a. The deletion half was withdrawn and the recommendation retracted.
- [operator-ruled] Amend OBPI-0.35.0-08, then fix — chosen over stopping or filing a fresh GHI.
- [operator-ruled] Run the full pipeline with subagent dispatch, after the agent surfaced the conflict between the session harness instruction forbidding unrequested agent calls and the canon forbidding OBPI work outside the pipeline skill. Surfaced rather than resolved silently, which is what that canon requires.
- [operator-ruled] Follow the brief's OWN precedent once OBPI-0.35.0-08 proved uncompletable: direct-fix the unblocked REQs ahead of the brief, exactly as REQs 01/02/05/06 were landed under `48a5f799` and `dcf29b95`, and record them in the PARTIALLY PRE-LANDED table. No Gate 5 claimed.
- [agent-chose] Seat the canon bullet under § Defect-fix routing rather than appending to § Operator Doctrine, because it is a precondition ON the threshold table it precedes.
- [agent-chose] Classify the corpus entry Judgment, not Promotable — the scorecard defines Promotable as a clause with neither a witness nor an admission, and this one carries the admission in its own text.
- [agent-chose] Recompose ONLY the root consumer; the drift warning's instruction to also recompose codex was refused as over-broad.
- [agent-chose] Fix the AttributeError at the CLASS in the manifest reader rather than widening the seam's except clause, which also makes that reader's own docstring true.
- [agent-chose] Separate commits throughout — bookmarks, canon, brief amendment, code fix — so each diff is exactly its own subject.
- [agent-chose] Did NOT hand-write a pipeline marker when the dispatch verb refused; logged the channel gap as an insight instead (Behavior Rules — Never #6).

## Immediate Next Steps

1. Decide whether OBPI-0.35.0-07-content-land-orchestrator should be built next. It is the sole blocker on OBPI-0.35.0-08's completion: REQ-0.35.0-08-04 requires the advisory to name `gz content land`, which is not a registered verb, and OBPI-0.35.0-07 is Draft. Read live state from `uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing`, never from a figure transcribed here.
2. Bind @covers to REQ-0.35.0-08-01, -02, -05 and -06 before any attempt at completing that OBPI. All four are [behavior], whose only proof channel is a covering test, and the REQ-coverage gate is unwaivable on every lane. The brief's PARTIALLY PRE-LANDED table calls them landed on prose evidence; completion reads the decorator channel and will not see them. REQ-06 needs more than a decorator — see Pending.
3. Resume ADR-0.35.0 proper — the lowest-semver feature ADR holding unlanded OBPIs and therefore the ADR in flight. It was SET ASIDE this session, not discharged. Any OBPI worked there runs through the gz-obpi-pipeline skill.
4. Rule on the two follow-ons in Pending: the dispatch-channel gap and the untested candidate-exclusion arm.

## Pending Work / Open Loops

- OBPI-0.35.0-08 is PARTIALLY LANDED and CANNOT COMPLETE. REQ-03 (re-opened by the amendment) and REQ-08 landed in `809f1370` with RED witnesses; REQ-04 is blocked on the unlanded `gz content land` verb; REQ-07 is a closeout-layer structural fence. No Gate 5 was claimed and none should be until REQ-04 clears.
- REQ-0.35.0-08-06 is UNPROVABLE THROUGH THIS HARNESS, not merely untested. `CliRunner.invoke` merges stdout and stderr into one buffer (`tests/commands/common.py`, redirect_stdout and redirect_stderr onto the same object), so its stream-separation claim cannot be expressed as an assertion at all. Recorded in the brief table. Closing it needs a different runner or a re-worded REQ — an operator call.
- The candidate-exclusion arm of is_graded_rendition SURVIVES DELETION against every fixture in the repo. Every candidate fixture uses a stem the route arm rejects first (root.candidate, codex.candidate), so the arm is decisive only in the empty-route branch, which nothing reaches. Exposure rose in `809f1370` because the drift advisory became its third caller. The predicate belongs to the TERMINAL OBPI-0.35.0-09, so it was flagged rather than touched.
- `gz obpi dispatch` binds to a running pipeline marker, so a direct-fix path that genuinely dispatches spec-reviewer and quality-reviewer cannot record it. Both reviews ran this session and the channel reports nothing; they are recorded in `809f1370`'s commit body instead. Logged as a discovery insight. Do NOT resolve by hand-writing a marker.
- The rendition-drift warning is FIXED for the route arm, but the gap it exposed is wider: the reconciler reports a brief CLEAN on all five dimensions while REQs are pre-landed or invalidated, because the allowlist dimension checks that declared paths exist and that files citing the REQs are listed — an unstarted brief has no @covers citations, so both arms are structurally 0. Exit 0 there means "nothing contradicts it yet", never "the brief matches reality".
- Copilot mirror removal, deferred by operator in a prior session. 65 files including `src/gzkit/schemas/manifest.json` and the negative-controls module asserting the four-mirror set.
- AGENTS.md now renders 43310 B against the 32768 B Codex delivery cap — 10542 B over, widened by 1075 B this session, disclosed and knowingly accepted in the corpus attestation. Advisory until 1.0 per the operator stay; tracked at GHI #815 [settled]; the instructions-files-diet chore is the vehicle and has still not run.

## Verification Checklist

```bash
uv run gz obpi lock list                                  # expect: No active locks
git rev-list --left-right --count origin/main...HEAD      # expect: 0	0
uv run gz validate --rendition-freshness                  # expect: exit 0
uv run gz validate --rendition-floor-coherence            # expect: exit 0
uv run gz validate --invariant-coherence                  # expect: exit 0
uv run gz validate --req-kind-discipline                  # expect: exit 0
uv run gz obpi brief-drift OBPI-0.35.0-08-remember-post-append-advisory
uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing
uv run gz content land --help                             # expect FAILURE: proves REQ-08-04 still blocked
grep -n 'Precondition' AGENTS.md
```
Read exit_status from the ARB receipt for any backgrounded verifier, never the harness notification — this session it reported 'exit code 0' against a real ruff failure, with a stray 'All checks passed!' from the NEXT stage printed directly beneath the failing line.

## Evidence / Artifacts

- `AGENTS.md` lines 283-285 — the seated precondition
- `.gzkit/corpus/AGENTS.md.jsonl` — entry id corpus-defect-fix-routing-2026-08-23T07:15:30.869803+00:00
- `.gzkit/renditions/AGENTS.md/root.corpus.json` — corpus_fingerprint 8fce908b8229, 77 entries, attestor g0
- `src/gzkit/commands/content/_drift.py` — the route-filtered enumeration
- `src/gzkit/content/vendors.py` — the manifest top-level type guard
- `src/gzkit/content/rendition_store.py` — is_graded_rendition, the shared predicate
- `tests/commands/test_content_remember.py`, `tests/commands/test_content_retire.py`
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-08-remember-post-append-advisory.md`
- `docs/governance/defect-fix-routing.md` § Precondition
- RED witness receipt ids (both failure_class=assertion): arb-red-REQ-0.35.0-08-03-a84e371f264d4050bf8be165bed7b55d and arb-red-REQ-0.35.0-08-08-6abd3bcd045b496d9a999cc6d196c718
- Final receipt ids, all exit_status=0: arb-ruff-8c2b145b103f4fb09c47de340a96c12c, arb-step-typecheck-16be634f7d864a049c8abe1ebb3b3cd9, arb-step-unittest-f19066cd097a4b92a93972d0407faa3e (8751 tests)
- Advisor-QC receipt id arb-step-judge-331e2aa77ac94356880fd325d95b2ad4 (score 1.0)
- `.gzkit/insights/agent-insights.jsonl` — three records this session: a defect against the content drift module, a discovery on the precondition's first catch, and a discovery against the obpi dispatch channel

## Settled Rulings

483 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
