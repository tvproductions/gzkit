---
id: OBPI-0.35.0-14-meaning-preserving-landing
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 14
lane: Heavy
status: Completed
allowlist:
  - src/gzkit/content/retention.py
  - src/gzkit/commands/content/commit.py
  - src/gzkit/commands/content/__init__.py
  - src/gzkit/content/corpus_store.py
  - src/gzkit/content/rendition.py
  - tests/content/test_retention.py
  - tests/commands/test_content_commit.py
  - features/content_commit_retention.feature
  - features/steps/content_commit_retention_steps.py
  - docs/user/manpages/content.md
  - .gzkit/skills/gz-content-compose/SKILL.md
  - src/gzkit/skills/gz-content-compose/SKILL.md
  - .claude/skills/gz-content-compose/SKILL.md
  - .agents/skills/gz-content-compose/SKILL.md
  - docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-14-meaning-preserving-landing.md
reqs:
  - REQ-0.35.0-14-01
  - REQ-0.35.0-14-02
  - REQ-0.35.0-14-03
  - REQ-0.35.0-14-04
  - REQ-0.35.0-14-05
  - REQ-0.35.0-14-06
  - REQ-0.35.0-14-07
  - REQ-0.35.0-14-08
verification:
  - uv run -m unittest tests.content.test_retention tests.commands.test_content_commit
  - uv run -m behave features/content_commit_retention.feature
  - uv run gz validate --documents --req-kind-discipline --cli-alignment
  - uv run gz cli audit
  - uv run mkdocs build --strict
tasks:
  - TASK-0.35.0-14-01-01
  - TASK-0.35.0-14-02-01
  - TASK-0.35.0-14-03-01
  - TASK-0.35.0-14-04-01
  - TASK-0.35.0-14-05-01
  - TASK-0.35.0-14-06-01
  - TASK-0.35.0-14-07-01
  - TASK-0.35.0-14-08-01
  - TASK-0.35.0-14-01-02
  - TASK-0.35.0-14-02-02
  - TASK-0.35.0-14-02-03
  - TASK-0.35.0-14-03-02
  - TASK-0.35.0-14-04-02
  - TASK-0.35.0-14-05-02
  - TASK-0.35.0-14-06-02
  - TASK-0.35.0-14-06-03
  - TASK-0.35.0-14-07-02
# REQ-atomic rationale (GHI #590 signature b): REQ-01..07 are subdivided above
# because their labor spanned plan tasks. REQ-01, -04 and -05 each had a CLI gate
# task and a BDD task; REQ-02 had a validator task, a CLI task and the Step-4b
# round-1 repair; REQ-03 had a validator task and a CLI task; REQ-06 had
# validator, CLI and BDD replay tasks; REQ-07 had the docs/skill task and the
# round-1 manpage amendment. REQ-08 is a STRUCTURAL-FENCE whose proof channel is
# the parent ADR's BI-10 entry, audited at ADR closeout. It carries no production
# labor of its own, so seq=01-only is honest for it.
req_atomic:
  - REQ-0.35.0-14-08
---

# OBPI-0.35.0-14-meaning-preserving-landing: Meaning Preserving Landing

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #14 - "Meaning-preserving landing -- a candidate that removes any block of the prior committed rendition is promoted only with a retention map. Each condition of each removed block is either KEPT at a quoted candidate span or DROPPED with a reason the operator approves; the conditions are extracted by an independent reviewer; the map is persisted as `<consumer>.retention.json`. Sequenced before item 7 by operator ruling 2026-09-24 (GHI #1090)"

**Status:** Completed

## Objective

`gz content commit` refuses to promote a candidate that removes any block of the consumer's prior committed rendition unless a retention map accounts for every condition of every removed block. Each condition is either KEPT at a quoted candidate span or DROPPED with a reason the operator names. When the promotion succeeds, the map is persisted as `<consumer>.retention.json`.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

The contract changes are a new `--retention-map` flag on `gz content commit`, a new refusal (exit 3) and a new sidecar artifact.

## Allowed Paths

- `src/gzkit/content/retention.py` — **CREATE**, a pure core module (stdlib + Pydantic) beside `content/lineage.py`. It holds the block splitter, the removed-block delta, the `RetentionMap` model and the validator.
- `src/gzkit/commands/content/commit.py` — the promotion seam: load the map, run the gate, write the sidecar
- `src/gzkit/commands/content/__init__.py` — the `content commit` parser: `--retention-map` flag, help text and exit-3 documentation
- `src/gzkit/content/corpus_store.py`, `src/gzkit/content/rendition.py` — READ-ONLY fixture imports of the covering commit tests (`append_entry`, `candidate_path`); listed so the brief reconciles against the test tree, never modified by this OBPI (amendment 2026-09-25, ratified by the operator: "ratify the allowlist")
- `tests/content/test_retention.py` — **CREATE**, following `tests/content/test_lineage.py`
- `tests/commands/test_content_commit.py`
- `features/content_commit_retention.feature` — **CREATE**, following `features/content_retire.feature`
- `features/steps/content_commit_retention_steps.py` — **CREATE**, following `features/steps/content_retire_steps.py`
- `docs/user/manpages/content.md` — the `commit` section: flag, sidecar, refusal and recovery
- `.gzkit/skills/gz-content-compose/SKILL.md` — the wielding skill: reviewer dispatch, map authoring, presenting drops to the operator
- `src/gzkit/skills/gz-content-compose/SKILL.md`, `.claude/skills/gz-content-compose/SKILL.md`, `.agents/skills/gz-content-compose/SKILL.md` — generated mirrors, written only by `uv run gz agent sync control-surfaces`, never hand-edited
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-14-meaning-preserving-landing.md`

## Denied Paths

- `src/gzkit/ledger_events.py`, `src/gzkit/schemas/ledger.json` — `ledger_events.py` is a registered security surface (`data/security_surfaces.json`). Adding a retention digest to `rendition_committed` would bring this OBPI under `sensitivity: security`, so it is out of scope. See the named residual under Requirements.
- `src/gzkit/content/rendition_store.py` — `RenditionProvenance` stays `frozen=True` / `extra="forbid"` with no retention fields (BI-03, § Alternatives O). The sidecar path helper lives in `retention.py`, next to `lineage_path`, following its pattern.
- `src/gzkit/content/models/corpus.py`, `src/gzkit/commands/content/remember.py`, `src/gzkit/commands/content/retire.py` — the gate reads the rendition delta, not the corpus log. Capture stays unblockable (BI-06).
- `src/gzkit/content/composer.py`, `src/gzkit/content/lineage.py` — generation and lineage are read, never changed. A lossy candidate is caught at promotion, not at generation.
- `.gzkit/corpus/**`, `.gzkit/renditions/**`, `AGENTS.md` — no canon or rendition is published by this OBPI. Fixtures live in temporary directories.
- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The prior rendition is the consumer's COMMITTED rendition (`rendition_path(root, surface, consumer)`). With no prior rendition (first commit), nothing was removed and the gate is vacuous. A missing prior is never evidence that nothing was lost, so the vacuous branch MUST test for the committed file's absence, never for an empty delta after a read failure. An unreadable prior rendition is exit 2.
2. REQUIREMENT: A BLOCK is a markdown heading, paragraph, list item or table row, as separated in the rendered surface. Fenced code blocks count as one block. A prior block is REMOVED when its text (LF-normalized, trailing whitespace per line stripped) is not a substring of the candidate. Moving or reordering a block never removes it.
3. REQUIREMENT: The map validator is pure and total. Given (removed blocks, candidate text, map, attestation text) it returns every violation, never the first only, so one refusal names every gap. Violations:
   - a removed block with no map entry
   - a meaningful character of a removed block (any non-whitespace character except markdown markup `*`, `_`, `` ` ``, `#`, `|`, `>` and the block's leading list marker) that lies inside no condition quote and no non-binding quote (reported per sentence, naming the uncovered text). This is ADR-0.35.0 Decision 10's "every sentence ... lies inside at least one condition", allowing a sentence to be split across several conditions whose quotes together cover it
   - a condition quote that is not a substring of its removed block
   - a KEPT span that is not a substring of the candidate
   - a DROPPED condition with an empty reason
   - `extracted_by` or `mapped_by` empty, or equal to each other after case-folding and whitespace trimming
   - a DROPPED condition whose id does not appear in the attestation text at a token boundary
   - a map entry naming no removed block of this delta, or two entries for the same removed block (every map entry is validated; none is silently ignored)
   - two conditions sharing an id anywhere in the map
   - a non-binding declaration with an empty or whitespace-only reason (amended 2026-09-25 by operator ruling; see Change Log)
   - a map whose `surface` or `consumer` differs from the invocation's (amended 2026-09-25 by operator ruling; see Change Log)
4. REQUIREMENT: Any violation makes `gz content commit` exit 3 and write NOTHING: no rendition, no provenance sidecar, no retention sidecar, no ledger event. The refusal prints each violation with the removed block's first line and a three-part recovery (`.claude/rules/guardrail-feedback-prose.md`).
5. REQUIREMENT: On success, the validated map is written to `.gzkit/renditions/<surface>/<consumer>.retention.json`, in the same transaction order as the rendition and provenance writes. The next promotion overwrites it; history lives in git beside the rendition. A promotion with no removed blocks removes any stale retention sidecar, so a sidecar never describes a delta it did not govern.
6. REQUIREMENT: The `RetentionMap` model is Pydantic, `frozen=True`, `extra="forbid"` (`.gzkit/rules/models.md`). Condition ids are short, human-typable tokens (`C1`, `C2`, …), unique within a map, so the operator can name a drop in plain words.
7. NEVER call an LLM, the network or a subprocess from `retention.py` or the gate. Extraction is agent work recorded in the map. The tool checks only what a byte comparison can prove (ADR-0.35.0 § Alternatives L).
8. NEVER weaken an existing `commit` refusal: an empty attestation on a moved corpus, an absent candidate or an absent corpus still fail exactly as today. The retention gate runs after those checks and before any write.
9. ALWAYS treat the named residual as disclosed, not solved. The tool cannot prove that the reviewer extracted every sub-clause condition, that a KEPT span carries the same meaning as its quote (a KEPT span is checked only for presence in the candidate), that a drop id in the attestation text came from the operator, or that the reviewer was a different model rather than a different name. The sentence-coverage floor bounds the first at clause level. The independent reviewer's check of each KEPT pair, and the success output that prints every pair for the operator, hold the second. The rule against fabricating operator words holds the third. The fourth is left to the skill's dispatch record. The Layer-2 retention digest is deferred with the security-surface exclusion above and must be surfaced to the operator at completion.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Retention Map Contract

```json
{
  "surface": "AGENTS.md",
  "consumer": "root",
  "extracted_by": "<reviewer agent identity>",
  "mapped_by": "<author agent identity>",
  "blocks": [
    {
      "removed": "<the removed block, verbatim>",
      "conditions": [
        {"id": "C1", "quote": "<substring of removed>", "disposition": "kept", "span": "<substring of candidate>"},
        {"id": "C2", "quote": "<substring of removed>", "disposition": "dropped", "reason": "<why>"}
      ],
      "non_binding": [{"quote": "<substring of removed>", "reason": "<why this sentence binds nothing>"}]
    }
  ]
}
```

Coverage: mark every character of the removed block that lies inside any occurrence of a non-empty condition quote or non-binding quote. Every meaningful character must be marked: any non-whitespace character except markdown markup (`*`, `_`, `` ` ``, `#`, `|`, `>`) and the block's leading list marker. Symbols such as `<=`, `≥`, `%` and `--` count, because they change meaning. Report each sentence that holds an unmarked alphanumeric character, quoting the unmarked text. Mere overlap is NOT coverage: a condition quoting three words of a sentence leaves the rest of the sentence unaccounted for, and that residue is exactly where a dropped qualifier hides (Change Log 2026-09-24).

**The #1090 replay, as a fixture:**
- Prior block: `c3582975f:AGENTS.md:234`, verbatim.
- Candidate: the compressed bullet the 2026-09-17 diet landed.

"`--accept-uncovered` is refused on every lane" has no KEPT span in that candidate. A map that marks it KEPT fails the span check. A map that omits it, or that quotes only "cannot be waived" from the same sentence, fails coverage. Only a DROPPED disposition named in the attestation text passes, and that makes the loss visible and operator-owned.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary: § Decision item 10, "NO LANDING LOSES MEANING WITHOUT AN APPROVED DROP".
- [ ] Parent ADR § Intent — the 2026-09-24 amendment. It explains why the gate reads the rendition delta rather than the corpus retirement log.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] GHI #1090 and its two comments: the motivating loss and its restore at `5d6b9d173`
- [ ] BI-03, BI-06 and BI-10 in the parent ADR. BI-10 is this OBPI's fence against OBPI-07's `content land`.
- [ ] OBPI-0.35.0-07 brief: `land` must call this gate (BI-10), so the gate's entry point must be callable without the CLI

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/commands/content/commit.py`
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/content/lineage.py` (pattern for the sidecar path helper)
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] `src/gzkit/commands/content/commit.py` — the check order (candidate, corpus, attestation) and the write order (`save_rendition`, `save_fingerprint`, `emit_rendition_committed`)
- [ ] `src/gzkit/content/lineage.py` — `lineage_path` / candidate-lineage sidecar layout to mirror
- [ ] `src/gzkit/content/rendition_store.py` — `rendition_path`, `load_fingerprint`; confirm no field is added to `RenditionProvenance`
- [ ] `src/gzkit/commands/content/__init__.py` — the `commit` parser registration near the `--attestation-text` help
- [ ] `tests/commands/test_content_commit.py` and `features/content_retire.feature` — fixture and step conventions
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

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

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run -m unittest tests.content.test_retention tests.commands.test_content_commit
uv run -m behave features/content_commit_retention.feature
uv run gz validate --documents --req-kind-discipline --cli-alignment
uv run gz cli audit
uv run mkdocs build --strict
```

## Demo

Self-contained: the command below creates a throwaway project with `mktemp -d` and runs every commit there, so no canon in this repository moves. `gz obpi present-evidence` executes Demo commands in the live checkout (GHI #1093). It seeds a prior committed rendition, a lossy candidate and a retention map (the fixture of the manpage worked example), then runs three commits. The first has no map and is refused with exit 3, naming both removed blocks. The second has the map, but C2 is not attested, and is refused with exit 3 (`dropped-id-not-attested`). The third has C2 attested and lands with exit 0, writing `root.retention.json`. Each refusal's full text is printed. The command exits non-zero unless all three outcomes hold.

```bash
R="$(pwd)"; D="$(mktemp -d)"; cd "$D" && uv run --project "$R" python - <<'PY'
import json, subprocess, sys
from pathlib import Path
from gzkit.content.corpus_store import append_entry, load_corpus
from gzkit.content.models import CorpusEntry
from gzkit.content.rendition import candidate_path
from gzkit.content.rendition_store import RenditionProvenance, corpus_fingerprint, rendition_fingerprint, save_fingerprint, save_rendition
root = Path(".")
Path(".gzkit/corpus").mkdir(parents=True, exist_ok=True)
append_entry(root, "AGENTS.md", CorpusEntry(id="e1", surface="AGENTS.md", section="behavior-rules", tier="compressible", classification="Mechanical", text="seed", origin="demo", ts="2026-09-25T00:00:00+00:00"))
corpus = load_corpus(root, "AGENTS.md")
prior = "# AGENTS.md\n\n- Run `uv run gz check` before every push.\n\n- Never push with `--no-verify`; the pre-push hook is the gate.\n"
save_rendition(root, "AGENTS.md", "root", prior.encode("utf-8"))
save_fingerprint(root, "AGENTS.md", "root", RenditionProvenance(corpus_fingerprint=corpus_fingerprint(corpus), corpus_entry_count=len(corpus.entries), rendition_fingerprint=rendition_fingerprint(prior.encode("utf-8")), committed_ts="2026-09-24T00:00:00+00:00", attestor="g0", attestation_text="baseline"))
cand = candidate_path(root, "AGENTS.md", "root")
cand.parent.mkdir(parents=True, exist_ok=True)
cand.write_text("# AGENTS.md\n\n- Run `uv run gz check` before every push; never bypass the pre-push hook.\n", encoding="utf-8")
Path("retention.json").write_text(json.dumps({"surface": "AGENTS.md", "consumer": "root", "extracted_by": "reviewer-agent", "mapped_by": "author-agent", "blocks": [
    {"removed": "- Run `uv run gz check` before every push.", "conditions": [{"id": "C1", "quote": "Run `uv run gz check` before every push.", "disposition": "kept", "span": "Run `uv run gz check` before every push"}], "non_binding": []},
    {"removed": "- Never push with `--no-verify`; the pre-push hook is the gate.", "conditions": [
        {"id": "C2", "quote": "Never push with `--no-verify`;", "disposition": "dropped", "reason": "the candidate no longer names the --no-verify flag; C3 keeps the intent, the flag itself is dropped"},
        {"id": "C3", "quote": "the pre-push hook is the gate.", "disposition": "kept", "span": "never bypass the pre-push hook"}], "non_binding": []}]}), encoding="utf-8")
def commit(*extra):
    args = ["content", "commit", "AGENTS.md", "--consumer", "root", "--attestor", "g0", *extra]
    proc = subprocess.run([sys.executable, "-m", "gzkit", *args], capture_output=True, text=True, check=False)
    print("$ gz " + " ".join(args))
    print((proc.stdout + proc.stderr).rstrip())
    print(f"exit {proc.returncode}\n")
    return proc.returncode
codes = [commit("--attestation-text", "compress behavior rules"),
         commit("--attestation-text", "compress behavior rules", "--retention-map", "retention.json"),
         commit("--attestation-text", "compress behavior rules; C2 drop approved", "--retention-map", "retention.json")]
sidecar = Path(".gzkit/renditions/AGENTS.md/root.retention.json")
print("exit codes:", codes, "| sidecar written:", sidecar.exists())
sys.exit(0 if codes == [3, 3, 0] and sidecar.exists() else 1)
PY
```

## Acceptance Criteria

<!-- REQ kinds per ADR-0.0.59; enforced by gz validate --req-kind-discipline. -->

- [ ] REQ-0.35.0-14-01 [BEHAVIOR]: Given a prior committed rendition and a candidate from which one or more prior blocks are absent, when `gz content commit` runs without `--retention-map`, then it exits 3, names every removed block, and writes no rendition, provenance sidecar, retention sidecar or ledger event
- [ ] REQ-0.35.0-14-02 [BEHAVIOR]: Given a retention map, when any condition quote is not a substring of its removed block, any KEPT span is not a substring of the candidate, any DROPPED condition has an empty reason, any non-binding declaration has an empty reason, the map's `surface` or `consumer` differs from the invocation's, or any sentence of a removed block is covered by no condition and no non-binding declaration, then the commit exits 3 and the output names every violation, not only the first
- [ ] REQ-0.35.0-14-03 [BEHAVIOR]: Given a retention map whose `extracted_by` or `mapped_by` is empty, or whose two identities are equal after case-folding and trimming, when `gz content commit` runs, then it exits 3 and names the independence violation
- [ ] REQ-0.35.0-14-04 [BEHAVIOR]: Given a map with a DROPPED condition, when the condition's id is absent from `--attestation-text` the commit exits 3; when it is present and every other check passes, the commit succeeds and `<consumer>.retention.json` holds the validated map
- [ ] REQ-0.35.0-14-05 [BEHAVIOR]: Given no prior committed rendition, a byte-identical re-render, a candidate that only adds or reorders blocks, or a whitespace-only difference, when `gz content commit` runs without a map, then it succeeds exactly as before this OBPI. A promotion with no removed blocks leaves no stale retention sidecar behind.
- [ ] REQ-0.35.0-14-06 [BEHAVIOR]: Given the #1090 replay fixture (prior block from `c3582975f:AGENTS.md:234` verbatim; candidate carrying the 2026-09-17 compressed bullet), when a map marks every condition KEPT, then the commit exits 3 on the `--accept-uncovered` condition, whose span is absent from the candidate. The same map with that condition DROPPED and its id in the attestation text succeeds.
- [ ] REQ-0.35.0-14-07 [SUPPORT]: `docs/user/manpages/content.md` documents `--retention-map`, the map schema, the sidecar, exit 3 and the recovery. `.gzkit/skills/gz-content-compose/SKILL.md` instructs dispatching an independent reviewer to extract conditions before the author maps them, and presenting every DROPPED condition to the operator by id before commit. Witnessed by `artifact_edited` citing `.gzkit/skills/gz-content-compose/SKILL.md` + `gz validate --cli-alignment`.
- [ ] REQ-0.35.0-14-08 [STRUCTURAL-FENCE]: Every path that promotes a candidate to a committed rendition enforces the retention gate over the same prior-rendition delta. None reaches `save_rendition` around it — audited at ADR closeout against § Boundary Invariants BI-10.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Change Log

- 2026-09-24, Requirement 3 and § Retention Map Contract (REQ-0.35.0-14-02, -06): coverage changed from "a sentence is covered when it overlaps a condition quote" to "every alphanumeric character lies inside some condition or non-binding quote". The overlap rule was an authoring error that weakened ADR-0.35.0 Decision 10, which says every sentence "lies inside at least one condition". Observed counterexample on the Task 1 code: a map quoting only "REQ-coverage gate", "BEHAVIOR REQ" and "cannot be waived" as KEPT returned zero violations while the #1090 clause "`--accept-uncovered` is refused on every lane" went unaccounted. The brief now matches the operator-ruled ADR; no operator ruling was changed.
- 2026-09-24, Task 1 orchestrator findings before review (REQ-02/-03/-06): empty-quote coverage bypass, unnormalized candidate, substring drop-id match, list/table/numbered/bold block boundaries, missing duplicate-id check, and missing splitter/delta tests. All fixed red-first by a sonnet fix dispatch (37 tests).
- 2026-09-24, Stage-2 review of Task 1 (findings q1-req06-dropped-attested-weak, F-REQ06-success-half-unproven, F-REQ06-covers-misbinding; spec receipt arb-step-specreview-ca344ab5c4424eaeb9c8065c4aa34812, quality receipt arb-step-qualityreview-28adece31aa64afb8171cef106776dd4): REQ-06's success half was unasserted and its fixture was not verbatim; unit tests were bound to the CLI-level REQ-01/-04; the duplicate-id tests were bound to REQ-06. The quality review also noted that alphanumeric-only coverage misses meaning-bearing symbols (`<=`, `%`), that the span check read the unnormalized candidate, that there were two divergent sentence splitters, and that duplicate or unknown map entries went unvalidated. Requirement 3 and the contract were widened to meaningful-character coverage and whole-map validation accordingly. Follow-up round findings (spec receipt arb-step-specreview-7bf7c9a414754f22864ba43cd8159e43, quality receipt arb-step-qualityreview-7b6728d1f769451d94f8ada4cb45d025; both refused at import because the envelope was malformed): REQ-02/-03 proofs lacked mutations for quote-in-block, empty reason and empty identities, so the specs were extended and re-proved; REQ-05 was bound on two unit tests, and the orchestrator removed those bindings; `lower()` was used where the contract says case-folding, and the orchestrator changed it to `casefold()`. A KEPT span is not related to its quote: this is disclosed as a judgment residual in ADR Decision 10 and Requirement 9, and mitigated by the reviewer check and by operator display (Task 2 prints every KEPT pair; Task 4's skill requires the reviewer to verify each pair). 2026-09-25, non_binding print confirmation round: spec (arb-step-specreview-3fe7f3dada124b6686459448bb67eacd) and quality (arb-step-qualityreview-12c96393123e4b8493120ad2073a3fb6) both accepted the six re-run proofs (proof-2e4ac1f3…, -531f6514…, -65e0efaf…, -13308aa2…, -b38565d2…, -152c14cf…); Stage-2 status for REQ-01..06 is ready. The success report now prints every non_binding exemption (test_success_prints_non_binding_exemptions_with_their_reason). 2026-09-25, Task 2 closing round: spec (arb-step-specreview-b39267f0113544f098721db741111e33) and quality (formatting repair arb-step-qualityreview-8d50b40cc12c4055a9d59f24b818f483 of arb-step-qualityreview-bd4431412398445897566344a64bc4e4) both accepted all six proofs and closed all five mapped findings; Stage-2 status for REQ-01..06 was ready. Two notes acted on: (1) non_binding declarations can exempt an entire removed block, yet the success report printed only KEPT/DROPPED conditions, so an exemption stayed invisible to the operator. This defect is in scope and was sent to an implementer to print every non_binding quote with its reason (brief Requirement 9 mitigation). (2) BI-10 input for OBPI-07 and the closeout audit: the sidecar write and the stale-sidecar unlink live in content_commit_cmd, not in enforce_retention, so OBPI-07's land must reuse them rather than re-implement them. 2026-09-25, Task 2 review fix cycle 3 (tests only): added CLI tests test_multiple_violations_all_named_in_one_refusal (REQ-02; three violation kinds, each named, nothing written) and test_independence_violations_named_at_cli (REQ-03; equal-after-fold and empty identities, exit 3, nothing written). Each was witnessed failing on its own assertion with its guard disabled, and retention.py was verified byte-identical to HEAD afterwards. Both were wired into the REQ-02/-03 proofs as nominated tests of the existing mutations, and all six proofs were re-run; 82 tests OK. 2026-09-25, operator ruling, verbatim: "authorize the third fix cycle, ratify the allowlist." This unblocks Stage 2 for a third Task-2 fix cycle (REQ-02/-03 CLI-level proof, then a closing review that re-closes the five open findings) and ratifies the read-only fixture allowlist amendment below. 2026-09-25, full `gz check` before the session sync (orchestrator corrections; they stale all proofs, which are re-run after the block ruling): removed an unused `# type: ignore` in test_retention.py; removed the hardcoded manpage path from the commit refusal prose (GHI #425 single-source rule); shortened the `--retention-map` help to 80 characters or fewer; and ALLOWLIST AMENDMENT pending operator ratification: `src/gzkit/content/corpus_store.py` and `src/gzkit/content/rendition.py` added as read-only fixture imports, because brief_reconcile counts the covering tests' imports as subjects. Task 2 follow-up review (spec receipt arb-step-specreview-497d837133ce4457a4be5cda74bcb4c3, imported, refuted, REQ-06 approval withheld; quality receipt arb-step-qualityreview-(t2r2), imported, accepted all six): the REQ-04 refusal-content repair was confirmed. New counterexample (REQ-04/-06, Requirement 6): an empty condition id satisfies the token-boundary attestation check against any text. Sent to review fix cycle 2 with id-pattern validation, map-level violation labels, one first_line helper, a stronger recovery assertion, and CLI selectors added to the REQ-06 proof. Task 2 Stage-2 review (spec receipt arb-step-specreview-a29c996114b44c0b8a445499b3802bb3, refused at import for an extra field; quality receipt arb-step-qualityreview-f9f8452a243d418a820d15904ec419ad, imported and accepted all six proofs): the spec review's mapped finding spec-t2-req04-refusal-content-unproven (the REQ-04 tests did not assert first-line naming, the recovery prose, or provenance/ledger non-writes on a validator refusal) is acted on even though the import failed. The quality review found that a non-UTF-8 map escaped as a traceback and that the CLI replay asserted only 'C1'; both were sent back as review fix cycle 1. Known limitation, deferred to its owner rather than rebuilt here: a partial IO failure after save_rendition and save_fingerprint leaves the rendition promoted without its retention sidecar. The two existing writes already share that exposure, and atomic multi-file publication is OBPI-0.35.0-07's journaled landing (ADR-0.35.0 Decision 6). Task 2, orchestrator finding before review (REQ-0.35.0-14-04, Requirement 3): the gate checked drop ids against the EFFECTIVE attestation, which can be a standing attestation carried forward from an earlier commit when an explicit candidate removes text without moving the corpus, so an old attestation containing 'C1' would satisfy a new drop. The defect was the orchestrator's Task 2 prompt ('effective'), not the contract, which says 'the attestation text'. It was sent back to the Task 2 implementer to fix red-first: drop ids must appear in the --attestation-text supplied with this commit. Closing round (spec receipt arb-step-specreview-d693eccc4f954fa3a7b904ceb445f79d, quality receipt arb-step-qualityreview-75b2e197a72f438a8d22c2862414d056): both accepted proofs proof-49bc68858ce44563942747ae9f7d116c (REQ-02), proof-78fb1ea595d74fdf9da641bf68a2824f (REQ-03) and proof-af0671c7d7cc4fc285a04866a0d058f9 (REQ-06), and closed all three mapped findings; Task 1 Stage-2 status is ready. Advisory, unmapped: split_blocks exceeds the lizard nloc/ccn bands (xenon C passes). Repaired in review fix cycle 1 (sonnet): verbatim #1090 fixture with a complete map and three REQ-06 assertions (passes / only the unattested drop fires / absent KEPT span fires); meaningful-character coverage; normalized span check; one sentence splitter; duplicate and unknown map entries; validate_retention split into per-check helpers (xenon C ceiling clean). The orchestrator rebound the last two REQ-04 unit tests to REQ-02. Re-proved REQ-02 (coverage, symbol, span and drop-attestation mutations), REQ-03 and REQ-06 (coverage, drop-attestation and span mutations); 46 tests OK.
- 2026-09-25, Task 3 (BDD, REQ-01/-04/-05/-06) Stage-2 review: the implementer's handoff was lost when session 37f9383a ended, so the orchestrator reviewed its output directly. It replaced a dangling `scratchpad/prior-234.txt` citation in the steps file with the reproducible `git show c3582975f:AGENTS.md | sed -n '234p'`, and confirmed both #1090 fixture constants are verbatim. Adding the feature files staled all six proofs; they were re-run (proof-d6c76e21…, -72cfb8b0…, -76c15a98…, -0ba7822d…, -2160e15a…, -402dd1e5…). Spec review arb-step-specreview-61b9a3a691174d51bde64a1190f2c29d and quality review arb-step-qualityreview-9feff9c3a8a34b73943dfc323bc2c7d9 (a formatting repair and completion of arb-step-qualityreview-5ae1e25da79140b584a50825790ad318, whose output carried no acceptance envelope) accepted all six current proofs and closed the five mapped findings q1-req06-dropped-attested-weak, F-REQ06-success-half-unproven, F-REQ06-covers-misbinding, spec-t2-req02-cli-every-violation-unproven and spec-t2-req03-cli-independence-unproven. Scoped Stage-2 readiness for REQ-01..06 was ready. Both reviews noted, as unmapped minor findings, that the REQ-01 scenario did not check the ledger and the REQ-04 scenario checked only that the sidecar existed. Both assertions were added (`no "rendition_committed" ledger event was written`; `the retention sidecar ... holds the map`, which compares the parsed map). Each was witnessed failing on its own assertion under a negative control: a tampered sidecar `mapped_by` failed 2 scenarios; the ledger step placed on a successful commit failed 1. The source was restored byte-identical (shasum OK). Behave: 4 scenarios, 32 steps.
- 2026-09-25, REQ-0.35.0-14-07 witness clause amended by operator ruling, verbatim (option chosen): "Cite skill + cli-alignment (Recommended)". The clause "`artifact_edited` citing both paths + `gz validate --documents --cli-alignment`" could never resolve: `parse_support_citation` accepts one cited path and one scope, and read `both` as the path, so the path arm always failed. It now reads "`artifact_edited` citing `.gzkit/skills/gz-content-compose/SKILL.md` + `gz validate --cli-alignment`". The REQ body still names both surfaces; the manpage half is judged by the spec and quality reviewers. The parser accepting a non-path token after `citing` is recorded as an insight for follow-up.
- 2026-09-25, Task 4 (docs and skill, REQ-07). A haiku implementer hit its 25-turn limit after changing only the options-table cell, and it left untracked `.gzkit/corpus/TEST.md.jsonl` and `.gzkit/renditions/TEST.md/` in the repository. The orchestrator removed them; they wrote no ledger rows. A sonnet redispatch added the skill's `## Before commit: the retention map` procedure (skill 1.1.0) and the manpage worked example. The example is built only from output the orchestrator captured in a throwaway directory outside the repository. The orchestrator then replaced C2's self-contradictory reason ("folded into ...") with an honest one from a re-run, and removed an untrue "git-initialised" claim. The closing Stage-2 round was: quality arb-step-qualityreview-ba35f3427eda44838ea459f2c313374f (accepted all eight and closed the five prior findings) and spec arb-step-specreview-50316e475f1a4a769c464a9b35eaf80e (a formatting repair of arb-step-specreview-f89f5529288a403abe57be2f2c393af3, whose finding carried the legacy shape; refuted). The spec review mapped counterexample spec-t4-req07-manpage-minimal-example-refused: the manpage's Minimal example quoted the removed block without its trailing period, so the tool refuses that map with `uncovered-sentence`. This was confirmed by running the example map through `validate_retention`: the old map gave ['uncovered-sentence']; the fixed map, with C1 attested, gave []. Repairs, batched into one round: (1) the example quote now includes the period; (2) the manpage's Named-residual paragraph now states all four Requirement 9 residuals, each with its correct mitigation. It had listed three and attached "no fabricated operator words" to the KEPT-meaning residual. Requirement 9's own text lists four residuals but maps mitigations as first/second/third, and that ordinal mismatch is left for operator ruling. (3) `test_validator_detects_kept_span_not_in_candidate` now filters on the exact kind `kept-span-not-in-candidate`, not the substring `span`. (4) The skill's `## Do Not` no longer forbids the promotion its own procedure ends in, and it says where the reviewer's KEPT-pair verdict goes. (5) An import-order fix (ruff I001) in the BDD steps, forced by the turn-end lint hook during the review window. Mirrors were re-synced; unit (retention + commit), behave and `gz validate --documents --cli-alignment` all exit 0.
- 2026-09-25, Task 4 focused follow-up (review fix cycle 1): spec arb-step-specreview-fb71973712734f248546bf722de2e669 and quality arb-step-qualityreview-b2e6154471df453e9a17f3efbe81e437 (a formatting repair of arb-step-qualityreview-1de7d0081c88412082203fe0089eaef1, whose verdict read 'approved') accepted all eight current proofs. They closed spec-t4-req07-manpage-minimal-example-refused and re-closed the five earlier findings. Unscoped Stage-2 status: ready, no blockers, no open findings. Disclosed, unmapped and non-blocking: `test_validator_rejects_identical_extracted_and_mapped` still uses an OR/substring filter; an empty `mapped_by` is proven at the validator tier, not the CLI tier; the manpage usage line's `C2 drop accepted` is not paired with the one-condition Minimal example. Stage 3 on the final tree: arb-ruff-400ac6506afc4a65bdd9bf1fe6d6df85, arb-step-typecheck-7fdd90a835b149d1ae181d1e6e77f880, arb-step-unittest-6206b528481b4358beacef4cceedabd4 (10817 tests OK, 4 skipped), arb-step-mkdocs-1385ee2a1ed5450c91940d4f799db09e, arb-step-behave-ba98d2df385b41969a162289db8ca278 (REQ-01/-04/-05/-06: 4 scenarios, 32 steps), all exit 0; `gz validate --documents --req-kind-discipline --cli-alignment` and `gz cli audit` exit 0; `gz covers` 0 BEHAVIOR uncovered. RED witness (arb-red-REQ-0.35.0-14-01..06): `error` against the reconstructed base 6c6f98dc6 for every BEHAVIOR REQ. That is inconclusive, non-blocking, and not a finding against the tests; the executed acceptance proofs carry the behavioral evidence.
- 2026-09-25, Stage 4a incident and Demo amendment. `gz obpi present-evidence` executed this brief's former `## Demo` in the LIVE checkout (`stage4_evidence._run_demo`, `cwd=project_root`). Its second command, `gz content commit AGENTS.md --consumer root --attestor g0 --attestation-text "demo"`, succeeded. It overwrote `.gzkit/renditions/AGENTS.md/root.corpus.json`'s recorded operator attestation with "demo" (restored by the orchestrator from HEAD before any commit; `root.md` was byte-identical) and appended a `rendition_committed` ledger row at 2026-09-25T01:28:45Z with attestor g0. The operator made no such commit. That row is tool-generated and is disclosed here and in GHI #1093; the append-only ledger cannot drop it. `gz obpi block` was recorded. Operator ruling, verbatim (options chosen): "Demo fix: Self-contained tmp Demo (Recommended); Ledger row: Disclose + GHI (Recommended); File GHI: Yes, file it (Recommended)" (`gz obpi unblock`). The `## Demo` now seeds a `mktemp -d` project and asserts the three outcomes (exit codes [3, 3, 0] and the sidecar written). A test run from the repository root exited 0, and the repository's `git status` and ledger line count (17415) were unchanged. GHI #1093 tracks the class defect in `_run_demo`.
- 2026-09-25, Step 4b round 1 (tier-1 Codex, receipt arb-step-codexadversary-19743ce8aff64c9a998251308ba6ec9b; imported through the formatting repair arb-step-codexadversary-91370c4450284f6da7afbb02cbb7e22d, identical except for the removed `verification_gaps` key, which the orchestrator's prompt had wrongly requested). Verdict CORROBORATED-WITH-CAVEATS, accepted: REQ-01..07 approved. All 18 mutations replayed in a disposable checkout (source digest 309d6955…) were killed on assertions and restored byte-identically; the Demo returned [3, 3, 0]. REQ-08 was left unadjudicated because the prompt told the adversary not to adjudicate it, which is an orchestrator prompt defect recorded as an insight. Three auxiliary counterexamples, each confirmed by the orchestrator against the source: (1) `aux-invalid-utf8-prior-exit`: a non-UTF-8 prior rendition exits 1 ("Unexpected error"), not the exit 2 Requirement 1 requires, because `enforce_retention` catches only `OSError`. This is a correction under the existing Requirement 1 and needs no ruling. (2) `aux-empty-nonbinding-reason`: a `non_binding` entry with an empty reason can exempt a whole removed block without a DROPPED id, contrary to ADR Decision 10's "declared non-binding with a reason". (3) `aux-retention-map-target-unbound`: a map naming another surface/consumer is accepted and persisted. Operator ruling, verbatim (options chosen): "Amend + fix now (Recommended)" for (2) and "Amend + fix now (Recommended)" for (3). Requirement 3 gains both violations. REQ-0.35.0-14-02's statement, the acceptance criterion that proves Requirement 3's enumerated violations, names them too, so its proof can carry their controls. All three are repaired in one batch; every proof is then re-run, spec and quality re-reviewed, and a focused Step 4b round 2 follows.
- 2026-09-25, Task 5 (the round-1 repair batch). A sonnet implementer (dispatch recorded; one resume after its turn limit) made three changes. (1) `enforce_retention` now catches `UnicodeDecodeError` alongside `OSError` and exits 2. (2) `_check_empty_non_binding_reason` adds kind `non-binding-without-reason`; it is a validator check rather than a Pydantic constraint, so it never hides other violations. (3) A map-target check adds kind `map-target-mismatch`, merged into the same refusal. Assertion-level RED was reported for each of five new tests. The orchestrator then made two changes: it moved the map-target check into `retention.py` as the pure helper `check_map_target` (called by `enforce_retention`), so that every REQ-02 control shares one proof source and `validate_retention`'s signature stays unchanged for OBPI-07 (BI-10); and it added one assertion that the non-UTF-8 prior rendition's bytes are unchanged. The Requirement-1 test carries no `@covers`, because no acceptance criterion states the exit-2 clause. All eight proofs were re-run at input digest 220bb858…, all valid: REQ-01 proof-df929d5d…, REQ-02 proof-c1dd2ecc… (10 controls, adding non-binding-reason-unchecked, map-surface-unchecked and map-consumer-unchecked), REQ-03 proof-9d0e75ef…, REQ-04 proof-8415eb94…, REQ-05 proof-c77149c0…, REQ-06 proof-a627857e…, REQ-07 proof-3de8e21e…, REQ-08 proof-a3971f6f…. The Stage-2 spec review (arb-step-specreview-ca58765b74cc411985d944fb03ff7530) and quality review (arb-step-qualityreview-d9b4e4dea21d43a7bff72d0b34614446) were both refused at import, because each merged the legacy and acceptance envelopes. Both found the same gap: the manpage did not document the two amended Requirement-3 rules (REQ-07, AGENTS.md § DO IT RIGHT 1a). The orchestrator's repair batch had missed this coupled surface. The manpage now states both rules and that a non-UTF-8 prior rendition is exit 2. `docs/` lies outside the acceptance input population, so the digest and all eight proofs stayed current. Both reviews are recorded through formatting repair, and a focused spec and quality follow-up closes the REQ-07 finding.
- 2026-09-25, Requirement 9 ordinal repair, after completion. Requirement 9 named four residuals but mapped mitigations as first/second/third: the KEPT-meaning residual had none, and the operator-words and dispatch-record mitigations sat one place early. The Gate-5 attestation disclosed this wording as unresolved. Operator ruling, verbatim: "Correct Req 9 in place and log it (Recommended)". The mitigation sentences now map all four in order, matching `docs/user/manpages/content.md` § Named residual. No REQ, proof or attested behavior changed.

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

### Step 4b — Independent Adversarial Validation

**Adversary identity and tier.** Tier 1, cross-vendor: OpenAI Codex, dispatched through the `openai-codex` Claude Code plugin (`codex-companion.mjs task --write --cwd <disposable checkout>`) and ARB-wrapped on every round. `codex:setup` reported `ready: true`, so tiers 2 and 3 were forbidden. Each round ran in a throwaway writable copy of the reviewed tree (`gz obpi adversary-workspace`), so the adversary replayed the recorded proofs rather than judging them by reading.

| Round | Receipt | Verdict | Claims broken |
|---|---|---|---|
| 1 | `arb-step-codexadversary-19743ce8aff64c9a998251308ba6ec9b` | CORROBORATED-WITH-CAVEATS / accepted | REQ-01..07 approved after 18 replayed controls; 3 auxiliary counterexamples; REQ-08 not adjudicated |
| 1 (formatting repair) | `arb-step-codexadversary-91370c4450284f6da7afbb02cbb7e22d` | identical judgment | imported; the original was refused only for a `verification_gaps` key the orchestrator's prompt had wrongly requested |
| 2 | `arb-step-codexadversary-0db64ea60fbb4e8dbef0e952323057aa` | CORROBORATED-WITH-CAVEATS / accepted | none; all 8 proofs approved, 21 controls replayed, no findings |

**What the adversary broke, and how each was resolved.** Round 1's three counterexamples carried no obligation id, so none blocked the gate. They were repaired anyway, as Task 5:

- **`aux-invalid-utf8-prior-exit`.** A non-UTF-8 prior committed rendition exited 1 ("Unexpected error"), while Requirement 1 requires exit 2. RESOLVED: `enforce_retention` catches `UnicodeDecodeError` alongside `OSError`. Round 2 confirmed exit 2, prior bytes unchanged, and no sidecar or ledger row.
- **`aux-empty-nonbinding-reason`.** A `non_binding` entry with an empty reason could exempt a whole removed block without a DROPPED id. RESOLVED by operator ruling ("Amend + fix now (Recommended)"): a new Requirement-3 violation, `non-binding-without-reason`, reported alongside the others. Round 2 confirmed it fires for empty and whitespace-only reasons and not for a real one.
- **`aux-retention-map-target-unbound`.** A map naming another surface or consumer was accepted and persisted. RESOLVED by operator ruling ("Amend + fix now (Recommended)"): `check_map_target`, called from `enforce_retention` and merged into the same refusal, with `validate_retention`'s signature unchanged for OBPI-0.35.0-07. Round 2 confirmed both mismatches fire and a matching map lands.

**Weakest point (round 2, the adversary's words, summarized).** The target binding sits outside the unchanged `validate_retention` API, so a future promotion caller must use the complete gate. That is BI-10's fence for OBPI-0.35.0-07's `land`, audited at ADR closeout; it is not a finding against this OBPI.

**What the adversary could not confirm.** The disposable copy carries no Git metadata, so it could not verify the reviewed revision SHA. It did not perform the ADR-wide BI-10 closeout audit; it approved REQ-08 on its declared channel and on the local promotion path it inspected.

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

### Key Proof


```text
$ uv run -m behave features/content_commit_retention.feature
1 feature passed, 0 failed, 0 skipped
4 scenarios passed, 0 failed, 0 skipped
32 steps passed, 0 failed, 0 skipped
```

The brief's self-contained `## Demo` builds a mktemp project and runs three commits. A commit with no map is refused (exit 3). A commit with an unattested DROPPED condition is refused (exit 3). With C2 attested the commit lands (exit 0) and writes `root.retention.json`. The Demo prints `exit codes: [3, 3, 0] | sidecar written: True`. `gz obpi present-evidence` observed this on 2026-09-25 with the ledger line count and `git status` unchanged, and the tier-1 adversary reproduced it independently.

Receipts (Stage 3 on the final tree, acceptance input digest 220bb858…): arb-step-unittest-2324c61641434b0aa43a1d6eeca95683 (10822 tests OK, 4 skipped), arb-ruff-4e5dc659d853417aada46f818691b33c, arb-step-typecheck-a6c57f0798d64074931db71901b13eb7, arb-step-mkdocs-7135a077f08c4511adbbc85bbc4cded5, arb-step-behave-fa64e2019e4b46cfb2a65695eea0bc28. Stage-2 reviews: arb-step-specreview-cabd2da0ec7b4f899d2d19e245bcb589 and arb-step-qualityreview-6da8f48d0fdd457aab3ff086f8aa440f. Step 4b: arb-step-codexadversary-0db64ea60fbb4e8dbef0e952323057aa (tier 1, CORROBORATED-WITH-CAVEATS / accepted, 8 of 8 proofs, 21 replayed controls, no findings).

### Implementation Summary


- Parent ADR § Decision item implemented: item 10, "NO LANDING LOSES MEANING WITHOUT AN APPROVED DROP".
- Files created: `src/gzkit/content/retention.py` (pure core: block splitter, removed-block delta, meaningful-character coverage, the total validator `validate_retention`, `check_map_target`, the `RetentionMap` model, the sidecar path helper); `tests/content/test_retention.py`; `features/content_commit_retention.feature`; `features/steps/content_commit_retention_steps.py`.
- Files modified: `src/gzkit/commands/content/commit.py` (the retention gate `enforce_retention`, which runs after the existing checks and before any write; exit 2 for any unreadable prior, including non-UTF-8; the sidecar write and stale-sidecar removal; the KEPT/DROPPED/NON-BINDING report); `src/gzkit/commands/content/__init__.py` (the `--retention-map` flag and exit 3); `tests/commands/test_content_commit.py`; `docs/user/manpages/content.md`; `.gzkit/skills/gz-content-compose/SKILL.md` v1.1.0, with generated mirrors.
- Tests added: 88 tests across the two unit modules, plus 4 BDD scenarios (32 steps). Each BEHAVIOR REQ is proven by executed mutation controls: 21 in all, each killed on an assertion and restored byte-identically.
- Date completed: 2026-09-25.
- Attestation status: operator g0, verbatim "attest completed", holding the replay-VERIFIED Step-4a packet and the tier-1 Step-4b round-2 verdict.
- Defects noted: GHI #1090 is the motivating loss (canon restored at 5d6b9d173; this OBPI is the prevention). GHI #1092 and #1093 were filed in flight. Step-4b round 1 found three auxiliary counterexamples, repaired in Task 5; two of them were ruled into Requirement 3 and REQ-02 by the operator. Requirement 9's ordinal wording is left for an operator ruling. Named residuals: the Layer-2 retention digest (deferred; the ledger event module is a security surface) and the partial-IO sidecar exposure (owned by OBPI-0.35.0-07). BI-10 input for OBPI-0.35.0-07: `land` must call `enforce_retention` (the complete gate), not only `validate_retention`.

## Tracked Defects

- GHI #1090 — the motivating loss (lane scope dropped by the 2026-09-17 compression); restored at `5d6b9d173`, independently of this OBPI.

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — operator g0, verbatim at Stage 4, holding the Step-4a packet (.gzkit/evidence/OBPI-0.35.0-14-meaning-preserving-landing.stage4a.md, gz obpi verify-packet VERIFIED, exit 0) and the independent Step-4b round-2 tier-1 cross-vendor verdict CORROBORATED-WITH-CAVEATS / accepted, with no findings (receipt arb-step-codexadversary-0db64ea60fbb4e8dbef0e952323057aa). In round 2 the adversary replayed all 21 mutation controls in a disposable writable checkout (workspace digest 1656e806c455bbd2961c7ac864512b041658ea2a76f9c2c7577b27520e2414a3); each killed on an assertion and was restored byte-identically. It approved all eight proofs, REQ-08 on its declared BI-10 channel. Round 1 (arb-step-codexadversary-19743ce8aff64c9a998251308ba6ec9b, imported via formatting repair arb-step-codexadversary-91370c4450284f6da7afbb02cbb7e22d) found three auxiliary counterexamples. All three were repaired in Task 5; two were ruled into Requirement 3 and REQ-02 by the operator ("Amend + fix now (Recommended)"). All eight obligations hold current executed proof at input digest 220bb8582ab6d31b975edaaec2e43ad149c0c669ca4025bc19108a44701ce8b5, accepted by spec review arb-step-specreview-cabd2da0ec7b4f899d2d19e245bcb589 and quality review arb-step-qualityreview-6da8f48d0fdd457aab3ff086f8aa440f, which re-closed the six prior findings. gz obpi acceptance status --stage stage4 reports ready, with zero blockers and zero open findings. gz obpi precomplete reports READY, 11 of 11. Baseline gates: arb-step-unittest-2324c61641434b0aa43a1d6eeca95683 (10822 tests, 4 skipped), arb-ruff-4e5dc659d853417aada46f818691b33c, arb-step-typecheck-a6c57f0798d64074931db71901b13eb7, arb-step-mkdocs-7135a077f08c4511adbbc85bbc4cded5, arb-step-behave-fa64e2019e4b46cfb2a65695eea0bc28 (4 scoped scenarios, 32 steps). Disclosed and not resolved by this attestation: the tool-generated rendition_committed ledger row of 2026-09-25T01:28:45Z (GHI #1093); Requirement 9's ordinal wording; the deferred Layer-2 retention digest; and the partial-IO sidecar exposure owned by OBPI-0.35.0-07.
- Date: 2026-09-25

---

**Date Completed:** 2026-09-25

**Evidence Hash:** -
