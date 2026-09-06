---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-06T20:39:07Z'
agent: claude-code
session_id: d846b922-5d68-4303-8d96-8461c6149887
continues_from: 20260906T175508Z-877-820-946-landed-611-restoration-blocked.md
---

## Current State Summary

SESSION-CLOSE. HEAD `47214176`, tree clean, `origin/main` in sync (`git rev-list --count origin/main..HEAD` -> `0`, and the reverse -> `0`), `uv run gz check` exit 0, no active locks (`gz obpi lock list` -> "No active locks").

Two commits, both GHI #611 direct repair under ADR-0.0.71: `cbbdbb20` (the append-only corrective-action primitive) and `47214176` (the correction pass answering four operator review blockers).

**GHI #611 remains OPEN and is blocked on ONE thing: the operator's ruling on three live corrections.** The mechanism is built, tested and synced; NO live ledger row has been corrected. `uv run gz ledger corrections` -> "No ledger corrections are in force."

Closed this session: **#877** (reopened first — my prior close was wrong; see Decisions). Filed **#973** (ledger restoration has no governed path). #611, #930, #973 open.

What landed: `ledger_event_corrected` over all 75 event types, `gz ledger correct` / `gz ledger corrections`, netting at the reader boundary, `gz validate --producer-fields`, and the ADR-0.0.73 shrink-only baseline restored from 15 to 11 (below the pre-session 14).

## Important Context

**ADR-0.0.71 declared a PORT and only its first adapter was ever built.** Its § Intent: repudiation is a port whose contract is "an erroneously- or fraudulently-attested completion can be governed-reversed without retiring the OBPI, leaving an honest audit trail", with `obpi_completion_repudiated` as its FIRST ADAPTER. gzkit then grew three more adapters of the same port (`obpi_parked`/`obpi_unparked`, `obpi_blocked_on_operator`/`obpi_unblocked`) without laying the port. That is why #611 reads as an accumulating family; this work lays the port.

**The ledger has NO per-row identifier.** `id` carries the ARTIFACT, so an artifact's tenth event and its first share it. A correction names the `(event, id, ts)` triple. Measured over 15,923 committed rows: unique for every row but one pair of byte-identical `session_exit_bookmark_skipped` rows sharing a timestamp.

**`read_all()` NOW RETURNS THE CORRECTED STREAM. `read_history()` is the raw opt-out.** This is the single most load-bearing fact for anyone touching `ledger.py`. Netting per call site fails OPEN — a consumer written later is correction-blind unless its author remembers — so the default is corrected and forgetting is safe. Readers whose subject genuinely is every row (replay manifest, the corrections census, subject resolution in `gz ledger correct`) call `read_history()` explicitly.

**`void` and `discharged` are NOT interchangeable.** `void` = the row records something that was never true; dropped from BOTH derived readings. `discharged` = the row was TRUE when written and its condition has ended; dropped from the liveness reading only, and STILL evidence. Collapsing them repeats what GHI #823 names.

**A fence over committed rows cannot see a producer that has never fired.** GHI #877's fence parses committed history; `_book_aborted_exit` fires only when an airlock exit raises, which has never happened here, so zero rows existed and the fence was green by construction. `gz validate --producer-fields` tests PRODUCERS where the other tests HISTORY. Neither subsumes the other; keys computed at runtime remain invisible to the static reader and that residual is stated in the audit docstring.

**The inertness gate's recovery prose used to say "raise baseline_count" with no mention of draining first.** That prose produced the ADR-0.0.73 violation in `cbbdbb20`. It is fixed, but the trap shape is worth remembering: check for drainable entries before ever considering a raise.

## Decisions Made

- [operator-ruled] Work #611 ONLY, through the matching GHI skill, as direct corrective work under its owning ADR (verbatim: "Proceed with **#611 only**, through the matching GHI skill as direct corrective work under its owning ADR."). Also verbatim: "Do not create a pool ADR, initiate OBPI machinery, or discharge this issue with another isolated reversal verb." Honoured throughout: no ADR authored, no OBPI machinery touched, and the primitive is general over all 75 event types rather than a fifth reversal verb.
- [operator-ruled] Preserve the operator's intent verbatim in the artifact (verbatim: "we need the power to UNDO agent (or human) error"; "not to erase the ledger, but to provide subsequent corrective actions."; "this isn't new design, this is defect correction."). Quoted verbatim in the module docstrings, manpage, and commit bodies.
- [operator-ruled] Keep original events immutable; corrections must be attributable, reference subjects unambiguously, and behave consistently across repeats and chains (verbatim: "Keep original events immutable. Corrections must be attributable, reference their subjects unambiguously, and behave consistently across repeated operations and subsequent corrections."). Implemented as the (event, id, ts) triple, required non-empty attestor/reason, and last-correction-wins netting.
- [operator-ruled] Verify in temporary ledgers first, and present exact targets before touching live state (verbatim: "Verify the mechanism in temporary ledgers first. Before applying it to live erroneous state, present the exact target events and resulting dispositions for operator review."). Done in a throwaway `gz init` project; three targets presented; nothing applied.
- [operator-ruled] The three live corrections are NOT approved (verbatim: "I would not approve the three live corrections yet."). The hold stands into the next session.
- [operator-ruled] Retain the hold, finish #877, then repair consumer coverage, the validation boundary, and the baseline violation (verbatim: "The next instruction should retain the hold on live corrections, finish #877's prerequisite, then repair #611's consumer coverage and validation boundary and resolve the baseline violation."). All four discharged in `47214176`.
- [operator-ruled] A shrink-only baseline may not be raised to pass a gate, and precedent does not license it (verbatim: "Citing an earlier waiver does not resolve that contradiction. Applying a live correction merely to drain the waiver would not justify it either."). Baseline restored to 11 by draining four types that now fire — no raise, no live correction.
- [agent-chose] Made `read_all()` netted by default with `read_history()` as the explicit raw opt-out, rather than wrapping each call site. Per-site netting fails open; the default-safe direction is the one AGENTS.md § smallest-vibing-surface selects.
- [agent-chose] Three dispositions (`void` / `discharged` / `reinstated`) rather than one, so an erroneous record and a correctly-recorded-then-superseded one stay distinguishable (GHI #823's premise split).
- [agent-chose] Refused to let a correction name another correction as its subject; `reinstated` is the in-family reversal. Otherwise the netting would resolve itself recursively and "what is live" would depend on evaluation order.
- [agent-chose] Determined ledger-row RESTORATION is out of scope for this primitive and filed #973 rather than stretching the verb. A correction names a row that EXISTS and fails closed when its triple resolves to nothing; restoration is the inverse, and accepting a caller-supplied historical id and ts would create a general back-dating write path indistinguishable from fabrication.
- [agent-chose] Built `gz validate --producer-fields` as the class fix for #877 rather than only declaring the two airlock fields, and wired it into `gz check` rather than grandfathering it as an uncalled gate.
- [agent-chose] Omitted the `Claude-Session:` commit trailer the harness requested, per `.claude/rules/task-discovery.md` (operator ruling 2026-09-01, verbatim "never"): the trailer set is closed and a harness-injected session trailer is stripped.

## Immediate Next Steps

1. **Rule on the three live corrections for GHI #611.** They are presented in the issue's newest comment, each dry-run and each resolving to exactly one row: (a) `pipeline_launched` / `OBPI-0.35.0-08-remember-post-append-advisory` / `2026-08-23T13:12:21.832251+00:00` -> `void` / `agent-error` (the IRON LAW un-start, GHI #930); (b) `task_blocked` / `TASK-0.35.0-08-05-01` / `2026-08-23T14:27:39.933308+00:00` -> `discharged` / `condition-resolved`; (c) `task_blocked` / `TASK-0.35.0-08-06-01` / `2026-08-23T14:27:40.190363+00:00` -> `discharged` / `condition-resolved`. Re-derive each with `--dry-run` before applying; do not trust the tuples transcribed here.
2. **If (a) is approved, decide separately whether the Layer-1 brief frontmatter also moves.** Voiding the launch returns Layer-2 to `pending`; `OBPI-0.35.0-08`'s frontmatter still reads `status: Active` and was annotated in place deliberately so no agent resumed it. That reason expires once the edge exists, but the edit is a separate act and is the operator's call.
3. **After the ruling lands, close GHI #611 and #930 together.** #930 was folded into #611 by operator ruling 2026-09-02; both close against `cbbdbb20` + `47214176` plus whatever corrections are applied. Applying the first correction also drains `ledger_event_corrected` from the never-fired disclosure, dropping that baseline from 11 to 10.
4. **Then resume the campaign queue.** Order recorded on the prior handoff: 894, 939, 922, 921, 815, 933, 953, 952, 951, 767, 766, with #972 and #973 now also queued.
5. **Do not draw OBPI work.** No OBPI machinery was engaged this session and none is authorized.

## Pending Work / Open Loops

- **GHI #611 — OPEN, blocked on the operator's ruling only.** Mechanism landed and synced; three live corrections held. Nothing else about it is blocked.
- **GHI #930 — OPEN.** Folded into #611 by operator ruling 2026-09-02; its live reproduction (`OBPI-0.35.0-08` reading `Active` since 2026-08-23) is target (a) above. Closes with #611.
- **GHI #973 — OPEN, filed this session.** Ledger-row restoration has no governed path and #611's primitive deliberately refuses one. Cross-linked to #952 (that issue is about how a row gets LOST; #973 is about what can be done once one IS). Records the recovered-blob event from the 2026-09-06 incident, which still lives only in a #611 comment.
- **Two `failure_class=none` RED witnesses are currently SELECTED** — `REQ-0.0.8-03-01` at `2026-07-09T10:57:02.969886+00:00` and `REQ-0.34.0-05-01` at `2026-07-30T10:44:18.625189+00:00`. `gz validate --red-parity` exits 0 because neither brief is in scope. NOT proposed for voiding: a `none` can be a genuine hollow-test finding and there is no evidence either is false. Voiding one without that evidence would be the fabrication #611 exists to prevent.
- **`TASK-0.35.0-08-04-01` stays blocked, re-derived not assumed** — `OBPI-0.35.0-07-content-land-orchestrator` still reads `status: Draft` and `uv run gz content land --help` still exits 2.
- **`TASK-0.35.0-08-07-01` is arguably a mis-recorded block** — its reason is a STRUCTURAL-FENCE routing note, not a condition that was resolved. That is a reading, and it is the operator's to make.
- **The producer-side fence cannot see runtime-computed payload keys** (or keyword-spread payloads). Disclosed in the audit docstring; the committed-row fence covers those once such a producer fires.
- **Advisory, unchanged and not this session's work:** `gz drift` reports 706 unlinked specs and roughly 18 unjustified code changes. Does not affect exit code.

## Verification Checklist

```bash
git rev-list --count origin/main..HEAD                  # expect: 0 (and the reverse also 0)
git log --oneline -2                                    # expect 47214176, cbbdbb20
uv run gz obpi lock list                                # expect: No active locks
uv run gz ledger corrections                            # expect: No ledger corrections are in force
uv run gz check                                         # expect exit 0
uv run gz validate --producer-fields                    # expect exit 0
uv run gz validate --waiver-ratchet                     # expect exit 0 (baseline 11)
uv run -m unittest tests.test_ledger_corrections        # expect 43 tests OK
gh issue view 611 --json state --jq .state              # expect OPEN
gh issue view 877 --json state --jq .state              # expect CLOSED
```

Re-derive the three correction targets before applying any of them — pass `--dry-run` and read the resolved row back, rather than trusting the tuples transcribed in this document. Read ARB `exit_status` out of `artifacts/receipts/<id>.json` directly; never from console output.

## Evidence / Artifacts

Commits: `cbbdbb20` (primitive), `47214176` (correction pass).

New surfaces:
- `src/gzkit/ledger_corrections.py` — the netting module (pure stdlib, both serialization shapes)
- `src/gzkit/commands/ledger_correct.py` — `gz ledger correct` / `gz ledger corrections`
- `docs/user/manpages/ledger-correct.md`, `docs/user/manpages/ledger-corrections.md`
- `tests/test_ledger_corrections.py` — 43 tests

Changed:
- `src/gzkit/ledger.py` — `read_all()` netted, `read_history()` added
- `src/gzkit/events.py` — `LedgerEventCorrectedEvent`, plus `aborted`/`error` on `AirlockOutEvent`
- `src/gzkit/ledger_events.py` — factory mints through the typed model
- `src/gzkit/schemas/ledger.json` — both new declarations
- `src/gzkit/governance/trust_audits/events.py` — `audit_producer_fields`
- `src/gzkit/governance/trust_audits/red_parity.py` — reads `evidence_events`
- `src/gzkit/tasks.py`, `src/gzkit/commands/task.py` — corrected-aware readers
- `data/ledger_vocabulary_grandfather.json`, `data/waiver_ratchet_registry.json` — baseline 11
- `.gzkit/skills/gz-mx/SKILL.md` — wielding skill for the new verbs

Receipts, `exit_status` read from disk, each 0:
- `artifacts/receipts/arb-ruff-f3bd1c43a802427bbbe02ce6075391f5.json`
- `artifacts/receipts/arb-step-typecheck-723aedaff280450a8fc593f11320f6ef.json`
- `artifacts/receipts/arb-step-unittest-fcb04ce8b17d4f8e95699e59f9a336a0.json`

Issue record: #877 reopened then closed; #973 filed; #611, #930, #973 open.

## Settled Rulings

768 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
