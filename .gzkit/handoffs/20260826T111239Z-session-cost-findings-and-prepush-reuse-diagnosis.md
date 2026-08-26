---
mode: CREATE
adr_id: ADR-pool.validator-scope-registration-seam
branch: main
timestamp: '2026-08-26T11:12:39Z'
agent: g0
session_id: c9cd37ec
continues_from: 20260826T105039Z-validator-scope-seam-pooled-and-sloc-band-amended.md
---

## Current State Summary

Session closed out GHI #885 and spent its remainder on why closing it took ninety
minutes. Five commits landed on `main`, all pushed.

`1fb42c25` — GHI #885, CLOSED. Corpus retirements are witnessed by SUBJECT rather
than presence: `gz validate --corpus-retirement-witness` requires a ledger event
whose `retired_entry_id` EQUALS each `retires`/`supersedes` pointer's target.
Before the fix, 12 corpus rows carried a retirement pointer, 5 events existed, 7
retirements had NO witness, and every validator read green. Repair shipped as
`gz content reconcile-retirements`, emitting a distinct
`corpus_retirement_reconciled` rather than backfilling a governed receipt. All 7
reconciled; 12/12 witnessed.

`9b1cbc32` — `radon_raw_nloc` block band p95 to p99 on operator override.
`data/module_size_grandfather.json` EMPTIED (all five entries fell under the new
band). The chore's percentile label now derives from the table.

`18fb5f8a` — `ADR-pool.validator-scope-registration-seam` plus the prior handoff.

`639a5c8c` and this session's final commit — AGENTS.md § Execution Rules now
names `gz check --fast` and the staging discipline the pre-push reuse gate needs.
Both routed through compose/commit/sync, never hand-edited.

## Important Context

**The pre-push reuse gate was already built. It was defeated by workflow, and the
agent's own diagnosis was wrong the first time.**

`.pre-commit-config.yaml:159` already reads `entry: uv run gz check
--reuse-verified`. The agent recommended adding it without reading the config —
a wrong recommendation the operator acted on. Corrected in the same session.

Why it never fired: `_record_full_pass` (`commands/quality.py:720`) records a
verified fingerprint ONLY when `tree_is_fully_staged`, because the fingerprint
names the INDEX tree while the gate ran against the WORKING tree, and those are
the same object only on a fully-staged tree. The post-commit ledger hook leaves
`.gzkit/ledger.jsonl` modified after every commit, so a `gz check` run
immediately afterwards is always against a dirty tree and is never recorded. The
tool prints the remedy verbatim — "`git add -A` before `gz check` to let the
pre-push gate reuse it" — and it went unread nine times in one session.

The mechanism itself is sound and should not be changed: content-addressed, so an
intervening commit does not defeat it and any edit does; fail-open, so an
unreadable repo runs the gate rather than skipping. The fix was a documentation
line, not code.

**Cohesion measurements taken this session, captured nowhere else.**

- Adding ONE `gz validate` scope costs SEVENTEEN registrations across sixteen
  files. `VALIDATOR_REGISTRY` holds 93 `_ScopeEntry` rows, `validate()` declares
  94 explicit `check_*` kwargs, argparse carries 95 flags and 94 forwarding
  lines. Four parallel ~94-item lists whose counts DO NOT AGREE, a fifth copy in
  `data/check_scope_membership.json`, and three test modules whose only job is
  checking the copies match. Eleven of the seventeen are mechanical; six are
  genuine authorship. Captured in
  `ADR-pool.validator-scope-registration-seam` (Option C).
- `.gzkit.json` is 19 lines of paths and authorship and configures NO policy.
  Policy lives in 40 unindexed `data/*.json` registries of which 23 (57%) are
  grandfather or waiver lists. `waiver_ratchet_registry.json` is a registry whose
  subject is the other waiver lists.
- The `radon_raw_nloc` corpus reports inter-project variance of 1,093,055 and
  says in its own words "high variance, the corpus disagrees" — against 0.0833
  for `radon_cc`, where it says the corpus "speaks with one voice". Thirteen
  projects (django, pip, mypy, flask, textual, a cpython subset and others) have
  no shared norm for module length. That is why p95 was the wrong block band.

**Two doctrine-without-mechanism findings, disclosed and unfiled.** The
operator-amendable mapping protocol routes amendment records through
`ADR-pool.doctrine-amendment-protocol`, which is designed and not built; and it
claims "Silent edits are forbidden by the validator (exit 3)" while
`validate_complexity_thresholds` has no concept of an amendment record.

**Operator state.** Verbatim across the session: "every task now takes hours";
"working on gzkit is slow death and I am not young anymore"; "this is so
extremely painful — we can't get through any operation without you tripping all
over things"; "you worked on this for 90 minutes - totally untenable". Treat
session cost as a first-class constraint, not an afterthought.

## Decisions Made

- [operator-ruled] Rule GHI #885 arm 1, #878 and #888 jointly; then "ratify all three, fold the fourth into #888 as arm 2".
- [operator-ruled] Repair the seven via a DISTINCT event type, never a backfilled `corpus_entry_retired`.
- [operator-ruled] Move the block band p95 to p99 ("do #1"); derive the label ("fix the label and commit it").
- [operator-ruled] Pool the registration-seam work ("this sounds like absolute insanity, yes to pool").
- [operator-ruled] Do NOT file further GHIs for findings surfaced this session ("everytime you touch the codebase you create several GHIs"). Three findings are therefore captured in the pool ADR and these handoffs rather than as issues.
- [operator-ruled] Add `gz check --fast` to AGENTS.md § Execution Rules; then "do #1 - make pre-push reuse the verified tree".
- [agent-chose] p99 over removing the band: § Invariant requires every metric to carry a `block` band.
- [agent-chose] Mutation-tested both new suites rather than trusting green — a presence-check degradation fails one test, a backfilled event type fails three.
- [agent-erred] RECOMMENDED WIRING `--reuse-verified` INTO THE PRE-PUSH HOOK WITHOUT READING `.pre-commit-config.yaml`. It was already there at line 159. The operator acted on a wrong recommendation. Root cause: asserted a gap from the absence of an observed effect rather than from reading the config. AGENTS.md § Operator Doctrine already binds this — "a search is not a read".
- [agent-erred] Surfaced the blocking-gate pattern only after the fifteenth gate, having been told to stop three times. AGENTS.md § Behavior Rules — Always #18 requires surfacing blocking failures upfront.
- [agent-erred] Ran the full 8870-test suite NINE times (~21 minutes) while `gz check --fast` existed and was never invoked; four of six full-check runs were verifying non-test gates `--fast` covers.

## Immediate Next Steps

1. **Stage before checking.** `git add -A` then `uv run gz check`, so the pre-push gate reuses the verified fingerprint instead of paying the suite twice. Now documented in AGENTS.md § Execution Rules.
2. Prefer `uv run gz check --fast` for inner-loop iteration; reserve the full gate for the pre-commit verification pass.
3. Do NOT promote `ADR-pool.validator-scope-registration-seam`. ADR-0.35.0 is still in flight — read its live position with `uv run gz adr status ADR-0.35.0` — and ascending-semver order binds.
4. GHI #888 remains OPEN with both arms unfixed. A correctly-written SUPPORT REQ still resolves its ledger arm off any event of the cited type.
5. GHI #878 remains OPEN. Its detection arm is satisfied by the reconciler; the write-path posture and the wider unguarded-ledger-append class are untouched.
6. OBPI-0.35.0-03 stays HELD. Its blocking dependency landed, so the hold's condition is met, but resuming it is operator-initiated work under the IRON LAW.
7. Consider test selection as the next lever on session cost: 8870 tests, 572 suites, 10 workers, ~143s, with no scoping to the changed surface. This is the remaining structural cost after staging discipline and `--fast`.

## Pending Work / Open Loops

- **GHI #888** — OPEN, two arms, neither fixed.
- **GHI #878** — OPEN. Wider class explicitly not closed: `register.py:317`, `adr_demote.py:486-496`, every unguarded ledger append after a durable mutation.
- **`ADR-pool.validator-scope-registration-seam`** — pooled, awaiting its turn behind ADR-0.35.0.
- **`ADR-pool.doctrine-amendment-protocol`** — designed, not built; threshold amendment records have no designated home until it is.
- **`validate_complexity_thresholds` cannot detect silent edits** despite doctrine claiming exit 3. Unfiled by operator instruction.
- **The 57% exception surface** — 23 of 40 `data/*.json` files are grandfather or waiver lists. Unfiled by operator instruction.
- **Test-suite cost** — no test selection; every full gate is 8870 tests.
- OBPI-0.35.0-08 still `in_progress` with a draft brief and no lock.
- GHI #884, #882, #879, #886, #887, #883, #881, #880 remain unruled.

## Verification Checklist

```bash
git log --oneline -6
git log --oneline origin/main..HEAD | wc -l     # expect 0 after sync
gh issue view 885 --json state                  # expect CLOSED
uv run gz check                                 # expect exit 0
```

Confirm the pre-push reuse gate is wired and that a staged tree records a
verified fingerprint — the whole subject of this session's final change:

```bash
grep -n "reuse-verified" .pre-commit-config.yaml    # expect line 159
git add -A && uv run gz check                       # must NOT print "not recorded as verified"
uv run gz check --reuse-verified                    # expect a skip, not a second suite run
```

Re-derive the corpus facts from the store, reading the JSON `event` FIELD and
never a substring grep — event names appear inside other events' prose blobs:

```bash
uv run python -c "
import json; from pathlib import Path
from gzkit.content.corpus_store import load_corpus
from gzkit.content.models.corpus import tombstone_target
c = load_corpus(Path('.'), 'AGENTS.md')
ptrs = {tombstone_target(e) for e in c.entries if tombstone_target(e)}
rows = [json.loads(l) for l in Path('.gzkit/ledger.jsonl').read_text().splitlines() if l.strip()]
w = {r.get('retired_entry_id') for r in rows if r.get('event') in ('corpus_entry_retired','corpus_retirement_reconciled')}
print('pointers', len(ptrs), '| witnessed', len(ptrs & w), '| unwitnessed', len(ptrs - w))"
```

Expect `pointers 12 | witnessed 12 | unwitnessed 0`.

## Evidence / Artifacts

Commits: `1fb42c25` (GHI #885), `9b1cbc32` (threshold amendment), `18fb5f8a`
(pool ADR + handoff), `639a5c8c` (`--fast` in Execution Rules), plus this
session's final AGENTS.md commit.

Authored: `docs/design/adr/pool/ADR-pool.validator-scope-registration-seam.md`,
`src/gzkit/governance/trust_audits/corpus_retirement_witness.py`,
`src/gzkit/commands/content/reconcile_retirements.py`,
`src/gzkit/governance/trust_audits/_qc_nc_corpus.py`,
`tests/governance/test_corpus_retirement_witness.py`,
`tests/commands/test_content_reconcile_retirements.py`.

Amendment record: `docs/governance/complexity/complexity-thresholds-rationale.md`
section "Amendment record — radon_raw_nloc, 2026-08-26".

AGENTS.md changes routed through the governed seam — `gz content compose`, then
`gz content commit --attestor g0`, then `gz agent sync control-surfaces`. Corpus
fingerprint unchanged at 8459d30b0fba across both; invariant floor 21214B unmoved.

GHI comments: #885 ruling (5423111469) and close; #878 (5423116058); #888 (5423123822).

ARB receipts, all `exit_status: 0`: `arb-ruff-56454fd750ec44e0a051fa730e07333b`,
`arb-step-typecheck-bcb2a976ba854d40b57e344439c188b6`,
`arb-step-unittest-4a4ba0938eca4b68b721a8fff7456581` (Ran 8870 tests, OK),
`arb-step-mkdocs-fc8885a8f79c4aa88cdbcf2834476377`.

## Settled Rulings

535 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
