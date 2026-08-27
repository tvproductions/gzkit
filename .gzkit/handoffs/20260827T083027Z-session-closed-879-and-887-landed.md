---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-27T08:30:27Z'
agent: g0
session_id: 017W13ZMeaX62R6TUiS4pP85
continues_from:
- .gzkit/handoffs/20260827T014405Z-session-exit-bookmark.md
- .gzkit/handoffs/20260827T005756Z-session-closed-corpus-store-landed-and-synced.md
---

## Current State Summary

Session is CLOSED and synced. `origin/main` and `HEAD` are 0/0, the working tree is
clean, and `uv run gz check` exits 0 on a fully staged tree.

Two GHIs closed, one filed, three commits landed:

- `c544205b` — `fix(obpi-precomplete): read the Step-4b verdict, not the heading (GHI #879)`
- `a2313fe1` — the predecessor handoff bookmark and its ledger rows
- `847f21f6` — `feat(obpi): give the pipeline a blocked-on-operator state (GHI #887)`

**GHI #879 [settled]** — `_check_adversarial_validation` returned ok on any brief
carrying a `### Step 4b` heading, so a brief recording REFUTED and one recording
NOT-REFUTED were the same input. It printed READY on OBPI-0.35.0-02, whose section
records REFUTED twice. The check now parses the verdict and fails closed on a
refutation, on a caveated refutation, and on a section recording no verdict at all.

**GHI #887 [settled]** — the pipeline had no state meaning "waiting on a human", so
nothing stopped spending against a structurally uncompletable brief. Added
`gz obpi block` / `gz obpi unblock` emitting `obpi_blocked_on_operator` and
`obpi_unblocked`; pipeline launch fails closed while a block stands, and precomplete
reports it as an 11th precondition.

**GHI #889** — filed at the #879 close. The sibling arm of the same class:
`_check_arb_receipts_present` counts receipt files and never opens `exit_status`.

Open GHI count at session end is 34 (the bare `gh issue list` form truncates at 30;
pass `--limit 200`).

## Important Context

**A BLOCKER COMMENT IS A CLAIM ABOUT THE TREE ON THE DAY IT WAS WRITTEN, AND BOTH OF
#887'S PREMISES CAME APART WHEN RE-DERIVED.** Its comment asked the operator to rule
between a real event pair and a marker-only state, and said the work was not routable
in-session because a schema change meets the OBPI-ceremony criteria. Neither survived.
ADR-0.0.9 Rule 5 is verbatim that *"Layer 3 artifacts cannot block gates. Only L1
(canon) and L2 (events) can be gate evidence"*, and that ADR's own table names pipeline
markers as Layer 3 — so marker-only was foreclosed, not open. Operator doctrine is
equally verbatim that a GHI-tracked defect routes to direct fix *regardless of* those
ceremony criteria. Read the surface before honoring a blocker, even one the operator
wrote.

**WHERE CANON RULES, ACT AND NAME THE RULE — DO NOT HAND IT BACK AS A MENU.** AGENTS.md
Operator Economy of Effort #7 governs exactly the shape #887 presented: a settled matter
rendered as an open choice is a drift vector, because a re-ruling can land somewhere
other than canon.

**THE #879 FIXTURE WAS ITSELF AN INSTANCE OF THE DEFECT.** The pre-existing test
asserting the check PASSES was backed by a fixture reading verbatim "Codex refuted it."
Repaired at the surface per the attested-REQ-subject-retirement rule in
`.claude/rules/governance-core.md`: the fixture now records a clean verdict so the
test's literal assertion stays true, the test is renamed to say what it proves, and the
refuted case it carried is asserted by a new sibling test rather than lost.

**POSITIONAL-LAST IS THE WRONG VERDICT PARSER, AND MEASUREMENT SAID SO.** The obvious
rule — the last verdict token in the section is the standing one — reads
OBPI-0.34.0-04 backwards: it opens with NOT-REFUTED (SHIP) and then narrates six earlier
refutations. Measured across all 20 Step-4b sections on disk before committing to a
design. The check therefore fails closed when a refutation appears at all and says in
its remediation that it cannot tell from prose whether it stands.

**REFUTED IS A SUBSTRING OF NOT-REFUTED.** That is GHI #888's live failure shape applied
to verdicts, a denial read as an assertion. Longest-first alternation and a word-boundary
lookaround pair each close it independently; both are kept and each is pinned by its own
test. The vocabulary is read from the completion command's own ADVERSARY_VERDICTS tuple,
never a second literal.

**THE NEVER-FIRED LEDGER BASELINE IS FLAT AT 10 ONLY BECAUSE IT IS PLUS TWO AND MINUS
TWO.** `data/ledger_vocabulary_grandfather.json` absorbed the two new event types and
shed mx_session_closed and mx_session_opened, which a producer now emits and nobody had
drained. The ratchet baseline count is unchanged, and that flatness must never be read
as "no growth" — the two-line diff is the honest record.

**GATES FOUND FIVE COUPLED SURFACES I WOULD NOT HAVE GUESSED.** Adding a ledger event
type obliges: the JSON schema, the typed-model registry in `tests/test_schemas.py`, a
graph handler in `src/gzkit/ledger.py`, the ontology corpus, and the never-fired
disclosure. Adding a CLI verb obliges: `config/doc-coverage.json`, a manpage, the manpage
index, both runbooks, and a wielding skill under `.gzkit/skills/`. Every one of those was
surfaced by a gate rather than by inspection.

**XENON REFUSED THE FIRST SHAPE OF THE #887 GUARD.** Adding the branch inline pushed
`obpi_pipeline_cmd` to rank D. Extracted to a helper mirroring the file's existing
airlock-diagnostic shape, and the mutation sweep was re-run after the move to confirm
every test's patch still reaches the implementation.

**A MUTATION HARNESS CAN REPORT A FALSE NEGATIVE.** One mutant read as "hollow test"
until I chased it: `str.replace(old, new, 1)` had hit an identical line in a sibling
check 200 lines earlier, so the mutation never reached the target. Anchor uniquely and
assert the count.

**THE PIPE GATE FIRES ON THE AGENT, NOT THE ARTIFACT.** `.claude/hooks/verifier-pipe-gate.py`
refuses any unittest or gz verifier piped into a filter, because the shell reports the
filter's exit status. Use `set -o pipefail` on every verifier run. It also refuses a
compound command that both writes a heredoc and pipes a verifier, so split those into two
calls.

## Decisions Made

- [operator-ruled] Take GHI #879 first, in the triage ranking order (verbatim selection: "#879 first, per ranking"). Booked to Layer 2 against the resumed handoff.
- [operator-ruled] Take GHI #887 next (verbatim: "take #887 next").
- [operator-ruled] Author a fresh handoff and sync (verbatim: "create fresh handoff, git sync").
- [agent-chose] Read #887's design question as ALREADY ANSWERED by ADR-0.0.9 Rule 5 rather than re-eliciting it, naming the rule that governed per Operator Economy of Effort #7.
- [agent-chose] Routed #887 as a direct fix despite its schema, CLI and runtime breadth, on operator doctrine that a GHI-tracked defect routes to direct fix regardless of the ceremony criteria. No OBPI machinery was touched.
- [agent-chose] Placed the #887 gate at pipeline LAUNCH rather than at completion, because completion is the operator's own act and a human attesting IS the ruling a block awaits.
- [agent-chose] Required --next-action on `gz obpi block`, so a block names the awaited decision rather than recording a complaint a second reader cannot discharge.
- [agent-chose] Made recording a block need no attestor, because requiring a human to authorize the statement that a human is needed would reproduce the deadlock.
- [agent-chose] Failed the #879 check closed on any refutation appearing rather than guessing which verdict stands, and documented that limit in the remediation text.
- [agent-chose] Filed GHI #889 rather than folding the ARB-receipt arm into #879, because that check never establishes WHICH receipts are this OBPI's evidence, so "are they green" has no well-formed answer yet.
- [agent-chose] Repaired the #879 fixture at the surface and added a sibling test, rather than deleting the test or leaving it asserting the retired predicate.
- [agent-chose] Updated the never-fired baseline to measured truth (plus two, minus two) rather than letting the ratchet count rise, and disclosed the composition explicitly.
- [agent-chose] Did NOT emit ARB receipts for either close; operator doctrine is verbatim that a GHI is its own work order and receipt.

## Immediate Next Steps

1. **Nothing is in flight.** Tree clean, branch synced 0/0, gate green. The next unit of work is an operator choice.
2. **GHI #886 is the strongest next pull, and most of its reasoning is already built.** It is the same ADR-0.0.9 Rule 5 applied to a second fact: Stage-2 dispatch credit lives only in the Layer-3 pipeline marker, so the sanctioned clear-stale recovery path destroys it. #887 [settled] just established the Layer-2 pattern to mirror, including the graph handler and the disclosure discipline.
3. **Then GHI #883, then #882.** #883 is the two canonical ledger readers disagreeing on explicit null and on array item types, affecting all 54 event types. #882 is labeled enhancement and its own body calls it new capability, so routing there is a judgment rather than a threshold result.
4. **GHI #889 is open and needs a scoping ruling before code.** Its check globs the project's whole receipt history, so "are the receipts green" is undefined until "which receipts are this OBPI's evidence" is settled. Candidate scopings are recorded in the issue body; none was chosen.
5. **Do NOT promote `ADR-pool.validator-scope-registration-seam`.** Ascending-semver order binds and ADR-0.35.0 is still in flight; read its landed count from `uv run gz adr status ADR-0.35.0`, never from a figure transcribed here.
6. **OBPI-0.35.0-03 stays HELD and OBPI-0.35.0-08 stays in_progress.** Resuming either is operator-initiated work under the IRON LAW.
7. **Working discipline that held:** `git add -A` then `uv run gz check` so the pre-push gate reuses the pass; `set -o pipefail` on every verifier; mutation-test each guard and re-run the sweep after any refactor; read the surface before honoring a blocker comment; pass `--limit 200` to `gh issue list`.

## Pending Work / Open Loops

- **GHI #886** — OPEN. Stage-2 dispatch credit lives only in the Layer-3 marker, so clear-stale destroys it. Same Rule 5 as #887 [settled] on a different fact.
- **GHI #883** — OPEN. The two canonical ledger readers disagree on explicit null and on array item types; the array-item hole affects all 54 event types.
- **GHI #882** — OPEN, labeled enhancement: the ledger validator has no conditional rule form.
- **GHI #889** — OPEN, filed this session. `_check_arb_receipts_present` counts receipt files and never reads exit status; measured 577 of 3718 receipts carry a non-zero exit while the check reports green. Needs a scoping ruling first.
- **GHI #888** — OPEN, two arms, neither fixed.
- **GHI #878** — OPEN. Carries the residual scope the corpus-store repair deliberately did not claim: every Layer-1 write path lacking temp, fsync and atomic replace.
- **GHI #877** — OPEN. Typed union rejects roughly 300 committed ledger rows the JSON schema accepts.
- **GHI #873, #874** — OPEN. Sibling findings from the adversarial pass that produced the corpus-store repair.
- **Not closed by the #887 [settled] fix:** a pipeline already mid-flight when a block lands. The guard refuses the NEXT launch; on the measured incident that stops three of four, but it does not interrupt a running stage sequence.
- **Not closed by the #879 [settled] fix:** which Step-4b verdict STANDS. The check fails closed on a refutation appearing at all and says so; deciding the standing verdict remains a human read.
- **`ADR-pool.validator-scope-registration-seam`** — pooled, awaiting its turn behind ADR-0.35.0.
- **`ADR-pool.doctrine-amendment-protocol`** — designed, not built.
- **The advisory `gz check` warning** — the AGENTS.md operator-doctrine section straddles the codex delivery cap. Undelivered canon is not in force. Not filed and not acted on.

## Verification Checklist

```bash
git log --oneline -3
git rev-list --left-right --count origin/main...HEAD   # expect 0 0
git status --porcelain                                 # expect clean
```

Confirm the two closures, the new issue, and the true open count (the bare form
truncates at 30):

```bash
for n in 879 887; do gh issue view $n --json number,state,stateReason; done
gh issue view 889 --json number,state                  # expect OPEN
gh issue list --state open --limit 200 --json number --jq "length"   # expect 34
```

Re-run this session's suites. Note `set -o pipefail`; a piped verifier reports the
filter's exit status and the pre-tool hook refuses the unguarded form:

```bash
set -o pipefail
uv run -m unittest tests.commands.test_obpi_precomplete \
  tests.test_adversarial_validation_audit \
  tests.governance.test_operator_block_state \
  tests.governance.test_operator_block_gate \
  tests.commands.test_obpi_block_cmd -q          # expect 87 tests OK
```

Confirm the new verbs resolve and the docs surfaces are covered:

```bash
uv run gz obpi block --help
uv run gz obpi unblock --help
uv run gz cli audit                                    # expect 140/140 covered
```

Confirm the ledger-vocabulary disclosure still holds, and that the flat count is
plus-two-minus-two rather than no growth:

```bash
uv run python src/gzkit/chores/ledger-vocabulary-inertness/check_ledger_inertness.py
git show 847f21f6 -- data/ledger_vocabulary_grandfather.json
```

Confirm this session's operator rulings reached the corpus (a rising count is not
evidence — grep the text):

```bash
uv run gz handoff rulings --search "per ranking"
uv run gz handoff rulings --search "take #887"
```

Full gate:

```bash
git add -A && uv run gz check                          # expect exit 0
```

## Evidence / Artifacts

Commits, all pushed to `main`:

- `c544205b` — the Step-4b verdict read
- `a2313fe1` — the predecessor bookmark and its ledger rows
- `847f21f6` — the blocked-on-operator state

Runtime surfaces changed:

- `src/gzkit/commands/obpi_precomplete.py` — the verdict parser, the bounded
  section scan, and the new operator-block precondition
- `src/gzkit/obpi_lifecycle.py` — the block projection, mirroring the park pair
- `src/gzkit/pipeline_runtime.py` — the launch-refusal blocker function
- `src/gzkit/commands/obpi_cmd.py` — the two commands and the extracted launch guard
- `src/gzkit/events.py` — the two event models
- `src/gzkit/ledger_events.py` — the two factories
- `src/gzkit/ledger.py` — the two-way graph handler and the re-exports
- `src/gzkit/schemas/ledger.json` — the two payload schemas
- `src/gzkit/cli/parser_obpi.py` and `src/gzkit/cli/parser_handler_manifest.py` — the verbs
- `src/gzkit/ontology/corpus.py` — the corpus entries

Governance and docs surfaces:

- `data/ledger_vocabulary_grandfather.json` — the plus-two-minus-two disclosure
- `config/doc-coverage.json` — the two command declarations
- `docs/user/manpages/obpi-block.md` and `docs/user/manpages/obpi-unblock.md`
- `docs/user/manpages/index.md`, `docs/user/runbook.md`, `docs/governance/governance_runbook.md`
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` and its wheel twin
  `src/gzkit/skills/gz-obpi-pipeline/SKILL.md` — the blocked-on-operator section,
  skill-version 6.41.0 to 6.42.0, vendor mirrors regenerated rather than hand-edited

Covering tests:

- `tests/governance/test_operator_block_state.py` — the projection, nine tests
- `tests/governance/test_operator_block_gate.py` — the launch refusal, seven tests
- `tests/commands/test_obpi_block_cmd.py` — the two verbs end to end, seven tests
- `tests/commands/test_obpi_precomplete.py` — the verdict read and the block
  precondition, fourteen new tests
- `tests/test_adversarial_validation_audit.py` — the repaired fixture and its new
  sibling test
- `tests/test_schemas.py` — the typed-model registry entries

Surfaces read during re-derivation:

- `docs/governance/state-doctrine.md` — Rule 5, which settled the #887 design question
- `src/gzkit/commands/obpi_complete_adversarial.py` — the completion chokepoint whose
  verdict vocabulary the pre-flight now reads

Handoff ruling booked this session: `gz handoff decide --decision proceed` on
`.gzkit/handoffs/20260827T005756Z-session-closed-corpus-store-landed-and-synced.md`,
session 017W13ZMeaX62R6TUiS4pP85.

## Settled Rulings

555 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
