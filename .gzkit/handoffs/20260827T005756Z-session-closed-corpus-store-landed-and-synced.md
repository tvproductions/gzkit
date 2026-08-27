---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-27T00:57:56Z'
agent: g0
session_id: 017W13ZMeaX62R6TUiS4pP85
continues_from: .gzkit/handoffs/20260827T004126Z-corpus-store-write-discipline-and-behave-thread-closed.md
---

## Current State Summary

Session is CLOSED and fully synced. `origin/main` and `HEAD` are 0/0, the working
tree is clean, and `uv run gz check` exits 0 on a fully staged tree.

Three commits landed and pushed:

- `8a388833` — `docs(quality): record why the check gate runs behave unfiltered`
- `c1b97652` — `fix(corpus-store): close all three write-discipline defects in append_entry (GHI #875, GHI #880, GHI #881)`
- `cf7938d8` — the predecessor handoff and its promoted rulings

Three arcs completed.

**1. The behave-selection thread is CLOSED**, on measurement rather than
preference. 443 scenarios across 68 feature files, zero `Scenario Outline`; 326
carry an effective `@REQ-` tag and 117 do NOT; zero feature files carry a
feature-level tag, so tag inheritance covers nothing. The untagged 117 cluster by
file (29 in `subagent_pipeline.feature`, 12 in `task_governance.feature`, 9 each
in `obpi_lock.feature` and `persona.feature`). Past `@wip` and `@dispatch` every
remaining tag is a near-singleton. No honest selection predicate exists today: a
`@REQ` filter at the gate would drop a quarter of the suite silently.

**2. Eight GHIs triaged** via the `ghi-triage` skill. Seven ranked; #884 excluded
because its repair is already in the tree.

**3. GHI #875, #880 and #881 are CLOSED**, taken together on operator ruling as
one repair of one twelve-line function, each with its own disposition comment and
cause-to-test table.

This handoff exists in addition to its immediate predecessor because the settled
rulings corpus promotes one generation behind: authoring it seats this session's
four operator rulings into `.gzkit/handoffs/rulings.jsonl`, which the predecessor
structurally could not do.

## Important Context

**THE PRE-PUSH GATE CAUGHT A DEFECT IN THIS SESSION'S OWN HANDOFF, and that is
the most useful thing that happened at the end.** The first `gz git-sync --apply`
committed and then FAILED to push: `gz validate --transcribed-adr-counts`
refused a live ADR count transcribed into the predecessor handoff's prose. The
validator's own reasoning is the lesson — a count computed from Layer-2 has no
reconciliation path once copied into prose, and *"this is the handoff a resuming
session reads, so a stale figure here is acted on."* The line now points at
`uv run gz adr status` instead of carrying a number. **Never transcribe an ADR
or OBPI count into a handoff.**

**`gz git-sync --apply` COMMITS BEFORE THE PUSH GATE RUNS.** A gate failure
therefore leaves a real commit on the branch with nothing pushed, and
`git status` reads clean while work is unpushed. Diagnose a failed sync with
`git rev-list --count origin/main..HEAD`, never with `git status`. Because that
commit was unpushed, the correct repair was `git commit --amend` after
re-staging and re-running the gate, not a stacked fixup.

**THE SETTLED-RULINGS CORPUS PROMOTES ONE GENERATION BEHIND, BY DESIGN.** The
predecessor handoff raised the corpus by exactly the count of ITS predecessor's
operator rulings, and promoted none of its own. Verified rather than assumed:
grepping `rulings.jsonl` for this session's ruling text returned zero, and every
row citing the predecessor as source carried the generation-earlier text. The
skill's canonical regression (GHI #722) is ten operator rulings silently dropped
over a missing list marker, so a rising count is NOT evidence that your own
rulings landed. Grep the store for their text.

**`gz handoff create` REJECTS BACKTICK-QUOTED DOTTED SYMBOLS IN THE EVIDENCE
SECTION** — it reads them as file paths and refuses the document. Name symbols
without the dotted form there.

**THE SESSION'S GOVERNING CORRECTION: reading the surface OVERTURNED a claimed
gap rather than confirming it.** The resumed handoff staged `quality.py:559` as
"the capability exists and the gate does not use it" — the fourth instance of
its own recorded error pattern. Reading the surface said otherwise: the
`run_behave` docstring already documented the split, and
`commands/quality.py:321` IS the tags consumer. A handoff written to enforce
*"a search is not a read"* was one step from committing that error itself.

**PRECONDITIONS EXPIRE, AND ALL THREE OF THIS SESSION'S DID.** Every one of
#875/#880/#881 recorded `corpus_store.py` as fenced — a Denied Path for one
OBPI, a read-only coupled surface for another. Re-derived at close: both briefs
are `attested_completed`, `gz obpi lock list` reports no active locks, and a
sweep of every brief under `docs/design/adr/*/*/obpis/` for
`corpus_store|concurren|atomic|os.replace|fsync` returned only terminal briefs.

**THE ORDERING INSIDE `append_entry` IS THE CONTRACT, not an implementation
detail.** Validating INSIDE the lock closes a FOURTH defect neither #875 nor
#880 could close alone: `content_retire_cmd` takes one snapshot at
`retire.py:157` and both guards read it, while `append_entry` re-reads the file,
so two processes retiring the same live entry both pass guards computed against
pre-retirement state. Exclusion alone serializes them but each still writes a
row that looked valid against its own stale snapshot; validation alone lets both
validate against the same stale snapshot. Mutation-tested from both directions.
Do not "simplify" that ordering.

**A DEFECT THE RED TEST FOUND THAT NO GHI HAD NAMED.** The first atomic-commit
implementation named its staging file by pid, which every THREAD of one process
shares. The concurrency test failed with `FileNotFoundError` — one writer
replaced the staging file another was still holding open. Staging is now unique
by construction via a same-directory named temporary file.

**THE LOCK IS AN OS LOCK, DELIBERATELY NOT A MARKER FILE.** A marker outlives
the process that created it, so one crash would wedge an append-only canon store
permanently. `fcntl.flock` and `msvcrt.locking` are both released by the kernel
on abnormal exit. The sidecar is deliberately NOT the corpus file, whose inode
the commit replaces.

**SCOPE LIMITS STATED RATHER THAN CLAIMED.** GHI #881's class sentence reaches
every Layer-1 write path lacking temp+fsync+replace; what closed is the corpus
store's append path ONLY. The ledger appends are untouched, and that wider class
is what GHI #878 still carries. On network filesystems where `flock` is
advisory, cross-process exclusion is not guaranteed and no test claims it is.

**Tooling note:** `gh issue list --state open` defaults to `--limit 30`, so a
bare count silently truncates. Pass `--limit 200`. True open count at session
end is 35.

## Decisions Made

- [operator-ruled] Close the behave-selection thread; the full suite stays at the gate (verbatim selection: "Close it — full suite stays"). Recorded as a dated measurement at the surface rather than changing behavior.
- [operator-ruled] The agent takes no self-directed work; the operator names it (verbatim selection: "You direct it — I'll wait").
- [operator-ruled] Triage the eight unruled GHIs.
- [operator-ruled] Take #881, #880 and #875 together as one repair (verbatim: "take #881, #880, and #875 together").
- [operator-ruled] Write the handoff and sync (verbatim: "write hand off, git sync").
- [agent-chose] Amended the unpushed handoff commit rather than stacking a fixup, after confirming it held only the handoff and its rulings and that nothing had been pushed.
- [agent-chose] Authored a SECOND handoff on the follow-up request rather than pointing at the existing one — it seats this session's four operator rulings into the corpus, which the predecessor structurally could not do.
- [agent-chose] Excluded GHI #884 from the triage ranking rather than ranking it low; its repair is already in the tree with five pinning tests, so it is a close-candidate needing no code.
- [agent-chose] Sliced the fix vertically per the horizontal-slicing prohibition in `.gzkit/rules/tests.md`, rather than authoring all tests then all implementation.
- [agent-chose] Mutation-tested every guard rather than trusting green, and re-ran the atomic-commit mutation after a lint-driven spelling change to confirm the test's patch still reaches the implementation.
- [agent-chose] Added a fourth test for the double-retire race because the module docstring made a specific claim about it that the cause-to-test table exposed as uncovered.
- [agent-chose] Wrote three separate GHI close comments rather than one shared disposition, per the never-batch-close constraint.
- [agent-chose] Made the retire command's "nothing written" claim true rather than softening the prose, leaving that file untouched.
- [agent-chose] Did NOT emit ARB receipts for the GHI closes; operator doctrine is verbatim that a GHI is its own work order and receipt.

## Immediate Next Steps

1. **Nothing is in flight.** Tree clean, branch synced 0/0, gate green. The next unit of work is an operator choice, not a resumption.
2. **The triage ranking is the recommended order for what remains**: #879 (obpi precomplete reports READY on a REFUTED verdict — a presence-check gate that actively licenses attestation on refuted work), then #887, #886, #883, #882. All route `direct-fix`; precedent is 453 `fix()` commits in 60 days against a threshold of 3.
3. **GHI #884 needs closing, not coding.** Its repair is verified present in the tree with five pinning tests. Run `/ghi-close 884` citing the commit that landed the runtime-wrapper walk.
4. **GHI #887 is the one that pays back session cost directly.** Its measured window is 21 `red_receipt_emitted`, 10 `task_started`, ZERO `task_completed`, four agents, and three adversary rounds run after the brief was structurally uncompletable. The pipeline has no state meaning "waiting on a human," so nothing stops the spend.
5. **Do NOT promote `ADR-pool.validator-scope-registration-seam`.** ADR-0.35.0 is still in flight and ascending-semver order binds — read its landed count from `uv run gz adr status ADR-0.35.0`, never from a figure transcribed here.
6. **OBPI-0.35.0-03 stays HELD and OBPI-0.35.0-08 stays `in_progress`.** Resuming either is operator-initiated work under the IRON LAW.
7. **Working discipline that held this session:** `git add -A` then `uv run gz check` so the pre-push gate reuses the pass; `gz check --fast` for the inner loop; read the surface before reporting any absence; pass `--limit 200` to `gh issue list`; and never transcribe an ADR or OBPI count into a handoff.

## Pending Work / Open Loops

- **GHI #879** — OPEN. `adversarial_validation` reports READY on a REFUTED verdict; the predicate is a heading match, which AGENTS.md § PRIME DIRECTIVE names as the presence-check prohibition.
- **GHI #887** — OPEN. No blocked-on-operator pipeline state; unbounded adversary spend against a structurally uncompletable brief.
- **GHI #886** — OPEN. Stage-2 dispatch credit lives only in the Layer-3 pipeline marker, so the sanctioned `--clear-stale` recovery path destroys it.
- **GHI #883** — OPEN. The two canonical ledger readers disagree on explicit null and on array item types; the array-item hole affects all 54 event types.
- **GHI #882** — OPEN, labeled `enhancement`: the ledger validator has no conditional rule form. Its own body calls it new capability, so the direct-fix route there is a judgment rather than a threshold result.
- **GHI #884** — OPEN but CLOSEABLE with no code; repair verified in the tree this session.
- **GHI #878** — OPEN, and now carries the residual scope #881 [settled] deliberately did not claim: every Layer-1 write path lacking temp+fsync+atomic-replace, the ledger appends foremost.
- **GHI #888** — OPEN, two arms, neither fixed.
- **GHI #873, #874** — OPEN. Sibling findings from the adversarial review pass that produced #875 [settled]; untouched by this session's repair.
- **`ADR-pool.validator-scope-registration-seam`** — pooled, two instances recorded, awaiting its turn behind ADR-0.35.0.
- **`ADR-pool.doctrine-amendment-protocol`** — designed, not built.
- **The advisory `gz check` warning** — the AGENTS.md `operator-doctrine-verbatim-canon` section straddles the codex delivery cap and `architectural-boundaries` starts entirely past it. Undelivered canon is not in force. Not filed and not acted on.
- **Corpus-store residuals disclosed in the close comments:** network filesystems where `flock` is advisory get no cross-process guarantee; a future load-time invariant added to the corpus load boundary outside `validate_tombstone_algebra` would reintroduce the read/write asymmetry with no mechanical witness.

## Verification Checklist

```bash
git log --oneline -4
git rev-list --left-right --count origin/main...HEAD   # expect 0 0
git status --porcelain                                 # expect clean
```

Confirm the three closures and the true open count (the bare form truncates at 30):

```bash
for n in 875 880 881; do gh issue view $n --json number,state,stateReason; done
gh issue list --state open --limit 200 --json number --jq 'length'   # expect 35
```

Re-run the corpus store suite and its neighbours:

```bash
uv run -m unittest tests.content.test_corpus_store -q                # expect 10 tests OK
uv run -m unittest tests.content.test_corpus_store tests.content.test_corpus_model \
  tests.commands.test_content_retire tests.commands.test_content_remember \
  tests.commands.test_content_reconcile_retirements \
  tests.governance.test_corpus_retirement_witness -q                 # expect 161 tests OK
```

Re-derive the behave measurement rather than trusting the figures above:

```bash
find features -name '*.feature' | wc -l                              # expect 68
grep -rhE '^\s*Scenario:' features --include='*.feature' | wc -l     # expect 443
```

Confirm this session's operator rulings actually reached the corpus (a rising
count is not evidence — grep the text):

```bash
grep -c 'full suite stays' .gzkit/handoffs/rulings.jsonl             # expect 1
uv run gz handoff rulings --search "take #881"
```

Full gate, and the sidecar invisibility the fix depends on:

```bash
uv run gz check                                                      # expect exit 0
touch .gzkit/corpus/AGENTS.md.jsonl.lock
git status --porcelain .gzkit/corpus/                                # expect empty
rm -f .gzkit/corpus/AGENTS.md.jsonl.lock
```

## Evidence / Artifacts

Commits, all pushed to `main`:

- `8a388833` — `docs(quality): record why the check gate runs behave unfiltered`
- `c1b97652` — `fix(corpus-store): close all three write-discipline defects in append_entry (GHI #875, GHI #880, GHI #881)`
- `cf7938d8` — the predecessor handoff plus its promoted rulings, amended to remove a transcribed ADR count the pre-push gate refused

Files changed across the session:

- `src/gzkit/quality.py` — the behave runner's docstring now states the three verification contracts per call site; the gate call carries a pointer, not a second copy of the numbers
- `src/gzkit/content/corpus_store.py` — exclusion, validation-before-persistence, and atomic commit; module docstring records all three and why validating inside the lock is load-bearing
- `tests/content/test_corpus_store.py` — four new test classes plus two module-level thread-body factories
- `.gitignore` — the two corpus sidecar patterns

Covering tests, all in `tests/content/test_corpus_store.py`:

- `TestAppendValidatesBeforePersisting` — an unresolvable tombstone leaves the store readable
- `TestAppendCommitsAtomically` — a failed commit leaves the store byte-identical
- `TestConcurrentAppendsAllLand` — no concurrent append is lost across 20 barrier-synchronized trials
- `TestConcurrentDoubleRetireIsRefused` — exactly one of two racing retirements lands

Surfaces read during precondition re-derivation:

- `src/gzkit/commands/content/retire.py` — the snapshot at `:157`, the guards at `:172` and `:245`, the OSError handler at `:377`
- `src/gzkit/commands/content/remember.py` — the second production writer at `:128`
- `src/gzkit/commands/obpi_complete_adversarial.py` — GHI #884's landed repair
- `src/gzkit/content/models/corpus.py` — `validate_tombstone_algebra` and the load/append boundaries

Handoff ruling booked this session: `gz handoff decide --decision proceed` on
`.gzkit/handoffs/20260826T114419Z-behave-selection-open-and-four-unreasoned-claims.md`,
session `017W13ZMeaX62R6TUiS4pP85`.

Immediate predecessor:
`.gzkit/handoffs/20260827T004126Z-corpus-store-write-discipline-and-behave-thread-closed.md`

## Settled Rulings

550 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
