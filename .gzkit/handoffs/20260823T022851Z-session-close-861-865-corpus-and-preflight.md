---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-23T02:28:51Z'
agent: claude-code
session_id: 9499fa38-e667-4082-9865-46e09f75b3ac
continues_from: .gzkit/handoffs/20260822T190153Z-flagged-item-routing-plan.md
---

## Current State Summary

Session opened as an evaluation of 19 externally-published Claude Code practices against gzkit's measured state, and turned into five GHIs. Four are closed against commits; one is open pending a design call. Nothing is in flight and no lock is held (`gz obpi lock list` -> No active locks). Tree clean at `ccce5a75`, HEAD == origin/main.

Landed this session, oldest first: `ca354b84` (GHI #861 - Stage-2 dispatch prompts now carry the persona frame, a required `why` kwarg, the RGR discipline with the `gz arb red` witness, and complexity bands read from `.gzkit/rules/complexity-thresholds.json` instead of three literals the authority never held); `8ed48271` + `f6407e9b` (GHI #862 - `gz content remember` refuses a text already live, seven duplicate invariant entries retired, root rendition re-linked under operator attestation); `a68cb860` (GHI #863 - `gz content retire` now warns about the rendition drift it causes, via a helper shared with `remember`); `cefb567e` (OBPI-0.35.0-03 amended); `e09b9d20` (GHI #864 - `ghi-author` Step 0 now reads OBPI briefs); `ccce5a75` (time-bomb lock fixtures defused).

GHI #865 is OPEN and is the only carried work.

## Important Context

THE CENTRAL FINDING OF THE SESSION is a shape, not a bug: a presence check answers 'is something armed', never 'what does it say'. It bit three times. (1) The GHI #862 collision was first reported as `entry_id in brief` -> 7/7, which established nothing because the brief enumerated BOTH sides of every pair; read against its `retire X; RETAIN Y` structure, the operator ruling had INVERTED the brief on all seven groups. (2) A help-text assertion passed on garbled spliced prose because it only checked absence-plus-keyword. (3) The GHI #864 remedy had to be written to demand a brief's DISPOSITION rather than the fact of a match, or it would have reproduced the first error.

AGENTS.md IS PLAYBACK-ONLY. `sync_agents_md` replays the committed rendition verbatim; a hand edit is overwritten. Any change to the root contract is a corpus `remember` plus an attested `gz content commit`. This is why GHI #864's routing half landed in `docs/governance/defect-fix-routing.md` rather than in AGENTS.md § Defect-fix routing.

RETIREMENT MOVES THE CORPUS FINGERPRINT even though it only shrinks the invariant floor, so `--rendition-freshness` demands a recompose the retire help text said was not implied. That contradiction is what GHI #863 fixed.

THE ARB RECEIPT IS THE ONLY HONEST EXIT CODE for backgrounded work. Three times this session the harness notification reported 'exit code 0' while the real exit was 1 - the trailing `echo` was the last process. Read `exit_status` off the receipt, never the notification.

THE PRE-PUSH GATE RUNS ~3.5 MINUTES, past the 2-minute foreground cap. Background every push.

## Decisions Made

- [operator-ruled] Topical section wins for the seven duplicate corpus groups (verbatim: "topical section wins, retire the canon-section copies"). This INVERTED OBPI-0.35.0-03's REQUIREMENT 12, which neither operator nor agent knew at ruling time. The ruling stands on evidence the brief's author lacked: all seven canon-section rows are one `cli:content-remember` bulk import that flattened seven differentiated classifications to `Ambiguous`.
- [operator-ruled] Amend the brief rather than reverse the corpus, ruled twice - once for the out-of-band discharge and again after the inversion was measured (verbatim both times: "option 1").
- [operator-ruled] Gate-5 attestation for the rendition re-link (verbatim: "attest completed"), relayed through `--attestation-text` enriched with receipt ids.
- [operator-ruled] Emotional phrasing captured in canon may be cleaned and toned down; the invariant floor governs corpus-text-to-render fidelity, not capture wording.
- [operator-ruled] Never propose an isolated OBPI - every OBPI attaches to a parent ADR. Corrected an agent proposal to route the Copilot-mirror removal that way.
- [operator-ruled] Defer the Copilot mirror removal (65 files, schema + validator scopes).
- [agent-chose] Withdrew the directive-polarity recommendation after measuring that 34 of 92 negative directives are operator verbatim canon and unrewritable; the raw count was not a signal.
- [agent-chose] Landed GHI #864's routing half in the expansion doc, because AGENTS.md is playback-only and a hand edit would be overwritten.
- [agent-chose] Separate commits for the #864 fix and the time-bomb fix - unrelated defects, and bundling would corrupt both scope boundaries.
- [agent-chose] Rebuilt two unpushed commits via `git reset --soft HEAD~2` rather than adding a third fixup commit, after verifying the tree was clean, both were local, and both messages were saved to disk.

## Immediate Next Steps

1. Rule on GHI #865 - arm 1 (a `gz validate` detector over `tests/`), arm 2 (an injectable `now` on `is_expired`/`elapsed_minutes`, the seam `_classify_staleness` already has), or both. No further investigation is needed; the scan in the body is complete over `tests/`.
2. Run `/git-sync` to land the session's `.gzkit/ledger.jsonl` and `.gzkit/insights/agent-insights.jsonl` appends.
3. Decide whether GHI #864 [settled]'s routing guidance should also be seated in AGENTS.md § Defect-fix routing proper. That is a corpus `remember` plus an attested `gz content commit`, not an edit.
4. Resume ADR-0.35.0 - it is the lowest-semver feature ADR with unlanded OBPIs and therefore the ADR in flight. Read its live lifecycle and landed count from `uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing`, never from a figure transcribed here - the count is computed from Layer-2 and a second copy in prose has no reconciliation path. OBPI-0.35.0-03 is amended and its residue runs through `gz-obpi-pipeline`.

## Pending Work / Open Loops

- GHI #865 (OPEN) - wall-clock time-bomb test fixtures. The instance is fixed and the scan proves no second bomb exists today; what is missing is the guard preventing the next one. Blocked only on the arm-1/arm-2 design call.
- The `TTY or PTY` canon tone-down remains UNDONE and is now operator-level by construction: its surviving copy is the `RETAIN` id in REQUIREMENT 3 of the live OBPI-0.35.0-03 brief, so the rule shipped in `e09b9d20` classifies it as a brief-owned routing question. Executing it means retiring the surviving copy and re-remembering the cleaned wording; the GHI #862 [settled] guard explicitly permits that sequence and there is a test pinning it.
- Copilot mirror removal, deferred by operator. 65 files including `src/gzkit/schemas/manifest.json` and `_qc_negative_controls.py`, which asserts the four-mirror set.
- OBPI-0.35.0-03 residue: REQ-0.35.0-03-04's fence property is TRUE (zero live byte-identical invariant texts) but was proven outside the two-stage review meant to witness it.
- AGENTS.md renders 42235 B against the 32768 B Codex delivery cap, 9467 B over, with two must-survive sections at or past the boundary. Advisory until 1.0 per the operator stay; the `instructions-files-diet` chore is the vehicle and has not run recently - the surface grew 34354 -> 42235 B between 2026-08-17 and this session.

## Verification Checklist

```bash
uv run gz obpi lock list                      # expect: No active locks
git rev-list --left-right --count origin/main...HEAD   # expect: 0	0
uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing
gh issue view 865 --json state,title          # expect: OPEN
uv run gz validate --rendition-floor-coherence
uv run gz validate --invariant-coherence
uv run gz validate --rendition-freshness
uv run gz obpi brief-drift OBPI-0.35.0-03-retire-duplicate-invariant-entries
```
Read `exit_status` from the ARB receipt for any backgrounded verifier, never the harness notification - it reported 'exit code 0' against a real exit of 1 three times this session.

## Evidence / Artifacts

- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-03-retire-duplicate-invariant-entries.md`
- `.gzkit/skills/ghi-author/SKILL.md`
- `docs/governance/defect-fix-routing.md`
- `tests/skills/test_ghi_author_brief_ownership.py`
- `tests/mx/test_mx_lock_lifecycle.py`
- `src/gzkit/commands/content/_drift.py`
- `src/gzkit/commands/content/retire.py`
- `src/gzkit/content/models/corpus.py`
- `src/gzkit/pipeline_dispatch.py`
- `.gzkit/corpus/AGENTS.md.jsonl`
- `.gzkit/renditions/AGENTS.md/root.corpus.json`
- `.gzkit/insights/agent-insights.jsonl`

## Settled Rulings

477 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
