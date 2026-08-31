---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-31T01:30:37Z'
agent: claude-code
session_id: 4ff2acbb-f6a7-4597-b04b-82098030be4f
continues_from: .gzkit/handoffs/20260830T221558Z-handoff-review-and-compose-blocker-correction.md
---

## Current State Summary

CLEAN RESUME POINT. Everything this session produced is committed and pushed; nothing is in flight. At authoring time HEAD and origin/main are both e5f60db5, `git status --short` is empty, `git rev-list --left-right --count origin/main...HEAD` is 0 0, and `uv run gz obpi lock list` reports no active locks. No ADR parent, no OBPI scope, no pipeline marker, no TASK open.

This document exists because its immediate predecessor `.gzkit/handoffs/20260830T221558Z-handoff-review-and-compose-blocker-correction.md` was authored BEFORE the commit it advised, so its own step 1 ("commit the two uncommitted files") was discharged minutes after it was written. That is the same pre-staleness this session spent its effort correcting in an earlier handoff, so it is closed here rather than left for a resuming session to trip over. Read the predecessor for the full session narrative and the measured correction; read THIS document for where things actually stand.

Two commits landed and pushed: d98eb3c2 (session-exit bookmarks plus the booked resume ruling) and e5f60db5 (the predecessor handoff, one insight line, and the rulings store at 619 entries).

ONE LIVE QUESTION REMAINS, and it is the operator's: who owns seeding `.gzkit/rules/**` into the corpus. Nothing else is pending agent work.

## Important Context

THE ONE THING A RESUMING SESSION MUST NOT REDO. An earlier handoff in this chain parked an open loop asserting that `surface_content_types` in `data/vendor-manifest.json` makes `gz content compose` fail closed on every rule surface. It was measured and is false on both halves: compose exits 1 with "No corpus store", so the cause is an ABSENT CORPUS, and the single-entry map is the deliberate, attested design of terminal `OBPI-0.35.0-09-codex-playback-wiring`, which documents that an unmapped surface falls back to the union. `src/gzkit/content/vendors.py:140` returns None for an unmapped surface and its docstring calls that "a real answer, not an error". The strike and its witnessing command are recorded in the predecessor; an insight is filed at scope content.compose.

THE OWNERSHIP QUESTION, stated precisely so it can be ruled without re-derivation. GHI #921 is open and its corrected title names the subject: `.gzkit/rules/**` is uncorpused. Two readings of operator canon conflict.

Reading A — GHI-direct. Operator canon reads "GHIs are AUTHORIZED for direct repair, always" and "Never spin up an ADR or OBPI merely to discharge a GHI". Under A the seeding is direct repair via `gz content remember`, agent-workable on a ruling.

Reading B — ADR-0.35.0 work. An earlier handoff asserted the corpus half "remains operator-initiated under ADR-0.35.0-canon-entry-corpus-landing per the IRON LAW". Under B no agent may begin any arm of it.

The evidence found against B: all eight non-terminal ADR-0.35.0 briefs were read and none owns rule-surface corpus seeding. Every hit is an incidental citation of `.gzkit/rules/tests.md` as a proof-channel reference, and `OBPI-0.35.0-05-corpus-candidate-generator` is the compose and lineage machinery rather than rule capture. The evidence for B: the IRON LAW is absolute about who initiates, and if the work IS ADR-0.35.0's then an absent brief means a brief must be authored, which is itself operator-initiated. An agent cannot resolve this without re-ruling canon, so Behavior Rules — Always #9 applies.

INHERITED CAUTIONS THAT STILL BIND. `gz validate --transcribed-adr-counts` refuses a live ADR count transcribed into a handoff; cite `uv run gz adr status <ADR-ID>` instead, as this document does. Any commit touching `src/**` or `tests/**` needs a `Task:` trailer, using the slug form for direct-fix work outside OBPI scope rather than minting a formal TASK id. Handoff authoring must route through `gz handoff create`; its Evidence-section validator reads a backticked dotted token as a file path, so commit ranges and dotted scope names belong outside backticks.

## Decisions Made

- [operator-ruled] Commit then push the handoff, insight and rulings store (verbatim: "commit, then push"). Landed as e5f60db5 and pushed d98eb3c2 to e5f60db5.
- [operator-ruled] Write a fresh handoff (verbatim: "write fresh handoff").
- [agent-chose] Chained this document from the predecessor rather than starting an unlinked one. An unchained handoff drops the lineage that carries the struck loops and the settled-ruling corpus, which the skill names as a red flag.
- [agent-chose] Kept this document SHORT and pointed the reader at the predecessor for narrative. Its job is to be an accurate resume point, not to re-tell a session already recorded one commit earlier.
- [agent-chose] Did not re-open or re-argue the ownership question while authoring; it is carried as the single live next step exactly as the predecessor framed it.

## Immediate Next Steps

1. RULE ON OWNERSHIP OF THE RULES-CORPUS SEEDING. Reading A (GHI #921 is the work order; seeding via `gz content remember` is direct repair, agent-workable on a ruling) versus Reading B (it belongs to ADR-0.35.0-canon-entry-corpus-landing and every arm is operator-initiated under the IRON LAW). Both readings and the evidence for each are set out in Important Context. This is the only live question in the tree.
2. Hold the two operator-held discussions. Neither is agent work: the design spike, whose premise is uncorrected by anything an agent may assert; and whether a delivery-cap breach on must-survive canon stays advisory, tracked at GHI #815.
3. Do not re-investigate anything in Pending Work marked STRUCK. Each was measured against code or ledger and answered; re-deriving them has already cost three separate readings across this chain.
4. If a further instructions-files-diet run is drawn on the rules arm, it must rank NEW material. The version-chain family is discharged across all 25 canonical rules and the remaining large blocks are binding sub-invariants, tables and proof-channel definitions rather than narrative.

## Pending Work / Open Loops

OPEN, and the only live question: ownership of the rules-corpus seeding, Reading A versus Reading B as set out in Important Context. GHI #921 is open.

OPEN, operator-held: the design spike (fully open by ruling), and whether a delivery-cap breach on must-survive canon stays advisory. Root AGENTS.md renders well past the codex cap with operator-doctrine-verbatim-canon straddling the boundary; tracked at GHI #815, and no attestation discloses the current figure.

OPEN, unrouted spike residual: nested projection is unmeasured. `agents-md-map-doctrine.md` declares paths of AGENTS.md, CLAUDE.md and `.claude/rules/*.md` while `agents_md_map_conformance.py` line 100 pins the rendered path to AGENTS.md alone, so the nested AGENTS.md corpus is governed by no shape doctrine.

STRUCK — DO NOT RE-INVESTIGATE. The `surface_content_types` blocker, corrected by measurement this session (see Important Context). The retained off-route codex rendition, which is a deliberately sealed record that nothing reads. `gz validate --brief-reconcile` exiting 0 on a Draft brief, which is correct by design at `brief_reconcile.py:301`.

PRE-EXISTING and untouched: the `gz check` advisory reports unlinked specs.

## Verification Checklist

Run these before trusting any claim above.

git rev-list --left-right --count origin/main...HEAD
  Expect 0 0. If not, work landed after this document was written.

git status --short
  Expect empty. This handoff is authored on a clean tree by design.

git log --oneline -3
  Expect e5f60db5, d98eb3c2, ed00f950 at authoring time.

uv run gz obpi lock list
  Expect no active locks.

uv run gz status
  Expect no gate pending for this session; nothing here is ADR-scoped.

gh issue view 921 --json state,title
  Expect OPEN, titled "instruction surfaces: .gzkit/rules/** is uncorpused, and fans out to all 26 generated AGENTS.md".

uv run gz content compose .gzkit/rules/chores.md --consumer claude --candidate <any-file>
  Expect exit 1 with "No corpus store". This is the command that witnesses the struck blocker; re-run it before doubting the strike.

uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing
  Read its lifecycle and landed count here rather than trusting any figure transcribed in prose.

uv run gz handoff rulings --search "corpus"
  Check the settled corpus before re-arguing the ownership question.

## Evidence / Artifacts

Commits landed and pushed this session:
- d98eb3c2 chore(handoffs): book two session-exit bookmarks and the resume ruling, 3 files, +80
- e5f60db5 chore(handoffs): record the review session and correct a mis-stated blocker, 3 files, +130

Handoff chain, newest first:
- `.gzkit/handoffs/20260830T221558Z-handoff-review-and-compose-blocker-correction.md` — the session narrative, the measured correction, and the struck loop
- `.gzkit/handoffs/20260830T101523Z-rules-diet-version-chain-discharge.md` — the resumed predecessor whose step 1 was already discharged
- `.gzkit/handoffs/20260830T102509Z-session-exit-bookmark.md` and `.gzkit/handoffs/20260830T103623Z-session-exit-bookmark.md` — the mechanical bookmarks that bracket it

Layer-2 records:
- `.gzkit/ledger.jsonl` — the handoff_resume_decided row booking the operator ruling on the resumed predecessor
- `.gzkit/insights/agent-insights.jsonl` — one defect record at scope content.compose with four evidence lines
- `.gzkit/handoffs/rulings.jsonl` — the append-only settled-ruling store, written by gz handoff create and never hand-edited

Surfaces read for the correction, unchanged since:
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-09-codex-playback-wiring.md`
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-05-corpus-candidate-generator.md`
- `src/gzkit/content/vendors.py`
- `data/vendor-manifest.json`

## Settled Rulings

622 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
