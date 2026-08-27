---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-27T00:41:26Z'
agent: g0
session_id: 017W13ZMeaX62R6TUiS4pP85
continues_from: .gzkit/handoffs/20260826T114419Z-behave-selection-open-and-four-unreasoned-claims.md
---

## Current State Summary

Session ran clean and is concluding with a green, synced tree. Two commits landed
on `main`, both pushed: `8a388833` (behave-gate rationale) and `c1b97652` (the
corpus_store write-discipline fix). `uv run gz check` exits 0 on a fully staged
tree; `git log origin/main..HEAD` is empty.

Three arcs, in order.

**1. The behave-selection thread is CLOSED.** The prior session left it as the
live open question. Measured: 443 scenarios across 68 feature files, zero
`Scenario Outline`; 326 carry an effective `@REQ-` tag and 117 do NOT; zero
feature files carry a feature-level tag, so tag inheritance covers nothing. The
untagged 117 cluster by file (29 in `subagent_pipeline.feature`, 12 in
`task_governance.feature`, 9 each in `obpi_lock.feature` and `persona.feature`).
Past `@wip` (35, already excluded by `behave.ini`) and `@dispatch` (31), every
remaining tag is a near-singleton. The measurement ANSWERS the question in the
negative: no honest selection predicate exists today, because a `@REQ` filter at
the gate would drop a quarter of the suite silently.

**2. Eight GHIs triaged.** Ran the `ghi-triage` skill scoped to the eight unruled
issues. Seven ranked; #884 excluded because its repair is already in the tree.

**3. The corpus_store write discipline landed.** Operator ruled to take #881,
#880 and #875 together. All three are cuts of one twelve-line function and all
three are now CLOSED with individual disposition comments.

## Important Context

**THE SESSION'S GOVERNING CORRECTION: reading the surface OVERTURNED a claimed
gap rather than confirming it.** The resumed handoff staged `quality.py:559` as
"the capability exists and the gate does not use it" — the fourth instance of its
own recorded error pattern. Reading the surface said otherwise: the `run_behave`
docstring already documented the split, and `commands/quality.py:321`
(`_run_obpi_scoped_behave`, fed by `resolve_obpi_behave_tags`) IS the tags
consumer. A handoff written to enforce *"a search is not a read"* was one step
from committing that error itself. That is recorded in `8a388833`'s body, not
quietly fixed.

**PRECONDITIONS EXPIRE, AND ALL THREE OF THIS SESSION'S DID.** Every one of
#875/#880/#881 recorded `corpus_store.py` as fenced — a Denied Path for
OBPI-0.35.0-02, a read-only coupled surface for OBPI-0.35.0-01. Re-derived at
close: both briefs are `attested_completed`, `gz obpi lock list` reports no
active locks, and a sweep of every brief under `docs/design/adr/*/*/obpis/` for
`corpus_store|concurren|atomic|os.replace|fsync` returned only terminal briefs.
Honoring those blockers without re-deriving them would have parked three
canon-destroying defects behind a fence that no longer existed.

**THE ORDERING INSIDE `append_entry` IS THE CONTRACT, not an implementation
detail.** Validating INSIDE the lock closes a FOURTH defect neither #875 nor
#880 could close alone: `content_retire_cmd` takes one snapshot at
`retire.py:157` and both guards read it, while `append_entry` re-reads the file,
so two processes retiring the same live entry both pass guards computed against
pre-retirement state. Exclusion alone serializes them but each still writes a
row that looked valid against its own stale snapshot; validation alone lets both
validate against the same stale snapshot. Mutation-tested from both directions —
removing either half kills
`TestConcurrentDoubleRetireIsRefused`. Do not "simplify" that ordering.

**A DEFECT THE RED TEST FOUND THAT NO GHI HAD NAMED.** The first atomic-commit
implementation named its staging file by pid, which every THREAD of one process
shares. The concurrency test failed with `FileNotFoundError` — one writer
replaced the staging file another was still holding open. Staging is now unique
by construction via a same-directory named temporary file, matching the
precedent at `commands/content/edit.py:72`.

**THE LOCK IS AN OS LOCK, DELIBERATELY NOT A MARKER FILE.** A marker outlives
the process that created it, so one crash would wedge an append-only canon store
permanently. `fcntl.flock` and `msvcrt.locking` are both released by the kernel
on abnormal exit. The sidecar is deliberately NOT the corpus file, whose inode
the commit replaces — a lock on the old inode would guard a file no later writer
opens.

**SCOPE LIMITS THAT WERE STATED RATHER THAN CLAIMED.** #881's class sentence
reaches every Layer-1 write path lacking temp+fsync+replace; what closed is the
corpus store's append path ONLY. The ledger appends are untouched, and that
wider class is what GHI #878 still carries. On network filesystems where `flock`
is advisory, cross-process exclusion is not guaranteed and no test claims it is.
`append_entry` can now raise `ValueError` and both callers catch only `OSError`;
neither can reach it today, so no speculative handling was added.

**The retire command's "nothing written" prose was NOT softened — it is now
TRUE.** GHI #881 proposed correcting the misleading message; making the
guarantee real instead is the more thorough fix, so `retire.py:377-385` stands
unchanged and now means what it says.

**Tooling note for the next session:** `gh issue list --state open` defaults to
`--limit 30`, so a bare count silently truncates. Pass `--limit 200`. The true
open count at session end is 35.

## Decisions Made

- [operator-ruled] Close the behave-selection thread; the full suite stays at the gate (verbatim selection: "Close it — full suite stays"). Recorded as a dated measurement at the surface rather than changing behavior. Rejected alternatives, all presented with tradeoffs: filter the gate by `@REQ` now (drops 117 of 443 scenarios), tag the 117 first and revisit, or park the thread.
- [operator-ruled] The agent takes no self-directed work; the operator names it (verbatim selection: "You direct it — I'll wait").
- [operator-ruled] Triage the eight unruled GHIs.
- [operator-ruled] Take #881, #880 and #875 together as one repair (verbatim: "take #881, #880, and #875 together").
- [agent-chose] Excluded GHI #884 from the triage ranking rather than ranking it low — its repair is already in the tree (the runtime-wrapper walk at `obpi_complete_adversarial.py:93` and `:135-138`, five pinning tests, 56 tests OK). It is a close-candidate needing no code, and ranking it as work would have misrepresented it.
- [agent-chose] Sliced the fix vertically — one test, one observed RED, minimum code to GREEN, three times — per `.gzkit/rules/tests.md` § Red-Green-Refactor's horizontal-slicing prohibition, rather than authoring all tests then all implementation.
- [agent-chose] Mutation-tested every guard rather than trusting green: dropping the validation, reverting to a truncating write, and swapping the lock for a null context each kill their own test. Also re-ran the atomic-commit mutation AFTER switching production to the pathlib spelling for `PTH105`, to confirm the test's patch still reaches the implementation instead of passing vacuously.
- [agent-chose] Added a fourth test for the double-retire race because the module docstring made a specific claim about it. Building the cause-to-test table surfaced the claim as uncovered; the skill's own canonical regression (GHI #708 to #771) is exactly this shape — naming tests is not covering a family.
- [agent-chose] Wrote three separate close comments rather than one shared disposition, per the never-batch-close constraint, each with its own cause-to-test table scoped to the class that GHI named.
- [agent-chose] Made the retire command's "nothing written" claim true rather than softening the prose, and left that file untouched.
- [agent-chose] Fixed all four ruff and ty findings properly (PTH105, SIM117, B023, an unused type-ignore) rather than suppressing them; B023 became a module-level closure factory instead of a loop-local closure.
- [agent-chose] Did NOT emit ARB receipts for the GHI closes. Operator doctrine is verbatim that a GHI is its own work order and receipt, and the canonical serial unittest step costs about 142s against a gate that already passed.

## Immediate Next Steps

1. **Nothing is in flight — the tree is clean, synced, and green.** The next unit of work is an operator choice, not a resumption.
2. **The triage ranking stands as the recommended order for the remaining GHIs**: #879 (obpi precomplete reports READY on a REFUTED verdict — a presence-check gate that actively licenses attestation on refuted work), then #887, #886, #883, #882. All route `direct-fix`; precedent is 453 `fix()` commits in 60 days against a threshold of 3.
3. **GHI #884 needs closing, not coding.** Its repair is verified present in the tree with five pinning tests. Run `/ghi-close 884` citing the commit that landed the runtime-wrapper walk.
4. **GHI #887 is the one that pays back session cost directly.** Its measured window is the operator's own complaint in ledger form: 21 `red_receipt_emitted`, 10 `task_started`, ZERO `task_completed`, four agents, three adversary rounds run after the brief was structurally uncompletable. The pipeline has no state meaning "waiting on a human," so nothing stops the spend.
5. **Do NOT promote `ADR-pool.validator-scope-registration-seam`.** ADR-0.35.0 is still in flight and ascending-semver order binds — read its landed count from `uv run gz adr status ADR-0.35.0`, never from a figure transcribed here.
6. **OBPI-0.35.0-03 stays HELD and OBPI-0.35.0-08 stays `in_progress`.** Resuming either is operator-initiated work under the IRON LAW.
7. **Working discipline that held this session and should continue:** `git add -A` then `uv run gz check` so the pre-push gate reuses the pass; `gz check --fast` for the inner loop; read the surface before reporting any absence; and pass `--limit 200` to `gh issue list`.

## Pending Work / Open Loops

- **GHI #879** — OPEN. `adversarial_validation` reports READY on a REFUTED verdict; the predicate is a heading match, which AGENTS.md § PRIME DIRECTIVE names as the presence-check prohibition.
- **GHI #887** — OPEN. No blocked-on-operator pipeline state; unbounded adversary spend against a structurally uncompletable brief.
- **GHI #886** — OPEN. Stage-2 dispatch credit lives only in the Layer-3 pipeline marker, so the sanctioned `--clear-stale` recovery path destroys it.
- **GHI #883** — OPEN. The two canonical ledger readers disagree on explicit null and on array item types; the array-item hole affects all 54 event types.
- **GHI #882** — OPEN, and labeled `enhancement` rather than defect: the ledger validator has no conditional rule form. Its own body calls it new capability, so the direct-fix route there is a judgment rather than a threshold result.
- **GHI #884** — OPEN but CLOSEABLE with no code; repair verified in the tree this session.
- **GHI #878** — OPEN, and now carries the residual scope #881 [settled] deliberately did not claim: every Layer-1 write path lacking temp+fsync+atomic-replace, the ledger appends foremost.
- **GHI #888** — OPEN, two arms, neither fixed.
- **GHI #873, #874** — OPEN. Sibling findings from the same adversarial review pass that produced #875 [settled]; untouched by this session's repair.
- **`ADR-pool.validator-scope-registration-seam`** — pooled, two instances recorded, awaiting its turn behind ADR-0.35.0.
- **`ADR-pool.doctrine-amendment-protocol`** — designed, not built.
- **The advisory `gz check` warning** — the AGENTS.md `operator-doctrine-verbatim-canon` section spans 29994-43915 B and straddles the codex 32768 B cap; `architectural-boundaries` starts at 46255 B, entirely past it. Undelivered canon is not in force. Not filed and not acted on.
- **Residual on the corpus store, disclosed in the close comments:** network filesystems where `flock` is advisory get no cross-process guarantee; a future load-time invariant added to the corpus load boundary outside `validate_tombstone_algebra` would reintroduce the read/write asymmetry with no mechanical witness.

## Verification Checklist

```bash
git log --oneline -3
git log --oneline origin/main..HEAD | wc -l   # expect 0
git status --porcelain                        # expect clean
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

Re-derive the behave measurement rather than trusting the numbers above:

```bash
find features -name '*.feature' | wc -l                              # expect 68
grep -rhE '^\s*Scenario:' features --include='*.feature' | wc -l     # expect 443
```

Full gate:

```bash
uv run gz check                                                      # expect exit 0
```

The sidecars must stay invisible to git:

```bash
touch .gzkit/corpus/AGENTS.md.jsonl.lock
git status --porcelain .gzkit/corpus/                                # expect empty
rm -f .gzkit/corpus/AGENTS.md.jsonl.lock
```

## Evidence / Artifacts

Commits, both pushed to `main`:

- `8a388833` — `docs(quality): record why the check gate runs behave unfiltered`
- `c1b97652` — `fix(corpus-store): close all three write-discipline defects in append_entry (GHI #875, GHI #880, GHI #881)`

Files changed:

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

Prior handoff in the chain:
`.gzkit/handoffs/20260826T114419Z-behave-selection-open-and-four-unreasoned-claims.md`

## Settled Rulings

546 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
