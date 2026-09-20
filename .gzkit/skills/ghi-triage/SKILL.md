---
name: ghi-triage
persona: main-session
description: Triage every open GHI — read each body, classify severity, and produce a deterministic rank-ordered deliverable. The bundled script handles fetch + routing + final rendering; the agent does the body-reading judgment pass between them. Use when reviewing the open-issue queue, before a planning session, or when deciding what to actually pull next.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-09-20
metadata:
  skill-version: "5.3.0"
model: sonnet
---

# ghi-triage

Real triage — read each issue, classify severity, recommend an order. The
bundled script does the deterministic work (fetch, route, render the
deliverable). The agent does the cognitive work (read each body, compose a
short WHY per issue). Determinism is enforced at the rendering boundary;
cognitive freedom lives only on the input edge.

## Invocation

```text
/ghi-triage              ← triage all open GHIs
/ghi-triage --label defect    ← filter to one label
/ghi-triage --limit 25        ← cap the scan
```

## Triage Procedure (binding — three steps)

When this skill is invoked, the agent MUST execute the three steps below
in order. There is no Rich table view, no per-GHI panel ceremony, and no
recommended-order intermediate table — those views were three redundant
restatements of the same data (GHI #324). The deliverable is the
rank-ordered list from Step 3, full stop.

### Step 1 — Pull structured records (single script call)

Run the script once with `--format json` to fetch the open queue, score
routing, detect duplicates, and emit one record per issue with the full
body inline:

```bash
uv run python .gzkit/skills/ghi-triage/scripts/triage.py [args] --format json
```

Each record contains: `number`, `title`, `labels`, `klass` (one of
`defect`/`enhancement`/`investigation`/`chore`/`unlabeled`), `body`
(full), `files_mentioned`, `dup_of`, `route`, `urgency`, `rationale`,
`blockers`, `family_signal`, `stale_annotations`, `created_at`,
`updated_at`. The `route` field is the script's
mechanical classification per `AGENTS.md` § Defect-fix routing — treat it as
evidence the agent reasons over, not as the final answer.

**`blockers` is the freshness instrument for `ghi-close` § Phase 1 step 1a.**
Each entry carries the blocker comment's `created_at`, its `references`
(`kind` / `identifier` / `state`), and `cites_settled`. A reference resolves
`live`, `settled`, or `unknown`; ADR and OBPI references are always `unknown`,
because their only repo-local index is a Layer-3 derived view. `rationale`
leads with `stale blocker: cites settled #N` when any citation has closed.

**The flag is a citation, not a verdict.** A blocker may name a closed GHI as a
*precondition* (it no longer gates — re-derive and proceed) or as *provenance*
("the pattern #585 established"). Nothing mechanical separates them, so the
script reports and the agent adjudicates. `unknown` is never reported as
settled: missing evidence is not evidence that a precondition cleared.

**`family_signal` and `stale_annotations` are the family-and-staleness pass
(row 4 of `docs/rnd/ghi-landscape-reorganization.md`). They are not peers.**

`stale_annotations` is **exact**. A body that writes `#889 (open)` transcribes a
Layer-2 fact GitHub already renders live, so whether that transcription still
holds is a lookup. Each entry names a reference whose subject has since closed.
The annotation is **decoration, not a precondition** — unlike `blockers`, a
decayed annotation gates nothing, and the body is never rewritten to fix it
(`#889 (open)` is a dated record of what its author observed). Read it as a
reason to discount the annotation and re-derive the relationship yourself. The
remedy is upstream: `ghi-author` § Step 4 no longer writes them.

`family_signal` is **candidate evidence with a measured error rate, never a
count**. It lists the doctrine-declared-without-mechanism phrases a body uses.
Measured 2026-09-20 against the 38 members
`docs/governance/f1-family-share-2026-09-20-evidence/measure.py` names among 57
open issues, it disagrees with that reader on 15 — 9 it matched that the reader
excluded, and 6 members no phrase catches (#950, #968, #997, #1011, #1012,
#1013). **An empty list is not evidence of non-membership.** Root-cause class is
not a surface-word property, which is precisely why the family slips past
`ghi-author` Step 0's title skim; a signal built from surface words inherits the
same limit and may not be reported as a family size.

Neither field enters the rank input, which stays structural-only (GHI #424).
The pass informs the judgment in Step 2; the ranking stays the agent's.

### Step 2 — Read each body, compose rank input

For each GHI in the JSON, read the body (it is inline — no `gh issue view`
needed). While reading, rule on the pass described above: decide family
membership from the body's root cause rather than from whether
`family_signal` fired, and discount any cross-reference listed in
`stale_annotations` instead of inheriting it. Ranking several members of one
family adjacently is a legitimate ordering judgment; reporting a family
*count* from the signal is not.

Compose a single rank-input JSON document with one entry per GHI
the agent recommends working on, in the agent's recommended order:

```json
{
  "rankings": [
    {"number": 324, "severity": "blocking"},
    {"number": 323, "severity": "degrading"}
  ]
}
```

**Rendering-edge contract (binding — structural-only schema, GHI #424
round 3):**

| Field | Constraint |
|-------|------------|
| `number` | int; must appear in the Step 1 fetched set |
| `severity` | one of `blocking` (current work fails), `degrading` (succeeds but produces drift), `latent` (deferrable) |
| any other field | **rejected** — the script returns exit 1 if a `rankings[*]` entry contains keys other than `number` and `severity` |

The schema is structural-only by design: prose fields in the rank input
duplicated the renderer's output in the operator's chat surface, and only
removing them from the schema made that impossible (GHI #424). The agent's
cognitive contribution is **selection + ordering + severity**; the renderer owns
all prose, derived from the fetched issue set.

### Step 3 — Render the deliverable

Write the rank-input JSON to a cache file under `.gzkit/cache/triage/`,
then pass that path to the script with `--format rank`:

```bash
# Write tool: .gzkit/cache/triage/rank.json  ← {"rankings":[…]}
uv run python .gzkit/skills/ghi-triage/scripts/triage.py --format rank --rank-input .gzkit/cache/triage/rank.json
```

`--rank-input` rejects stdin (`-`) and any path outside
`.gzkit/cache/triage/` (GHI #424 round 4). Inline-pipe shapes —
`echo '<json>' | triage.py … --rank-input -` — surface the entire rank
payload on the bash command line and reproduce the duplicate-render shape
in chat; the cache-path requirement makes that structurally impossible.

The script renders a deterministic markdown deliverable: one numbered row
per ranked GHI, each row containing the severity, route, and title in a
fixed shape. **The script's stdout IS the deliverable. The Bash tool
result shown to the operator is the presentation — do not echo, restate,
copy, or paraphrase that output in agent-generated text.**

A PreToolUse `Bash` hook (`.claude/hooks/ghi-triage-chat-silence.py`,
GHI #424 round 4) inspects the assistant's most recent turn whenever
`triage.py --format rank` is invoked. If the turn contains two or more
distinct `#NNN` GHI tokens each within 200 characters of a severity word
(`blocking|degrading|latent`), the hook exits 2 and blocks the tool call.
Compose the rank input silently — the hook is the structural backstop on
the chat-text surface, paired with the `--rank-input` cache-path
requirement on the bash-command-line surface.

There is no Step 4. There is no "Recommended order" follow-up table. The
rank list IS the recommended order.

## Optional cross-check (conditional, NOT mandatory)

If — and only if — a GHI body's `files_mentioned` plausibly overlaps an
in-flight ADR's allowed paths, run targeted state inspection for that
overlap:

```bash
uv run gz state --json
uv run gz obpi lock list
```

Use the result to set severity to `blocking` (overlap creates a hard
ordering dependency) and to order the dependent GHI after the one it waits on —
the rank input carries no prose field to say why. Do **not** run
this cross-check unconditionally — `gz state --json` is a 1.5 MB output
that takes 10–30 s to compute; running it on every triage burns operator
time for no signal. The default state of this step is *skipped*.

## Output Contract

Declared form: **deterministic markdown**, the script's `--format rank`
output, presented verbatim. Chat-renderable; no Rich box-drawing glyphs
that wrap mid-character in chat surfaces; no ANSI color sequences that
get stripped; no per-GHI panel restating the body excerpt the JSON
already contained.

The rank list is the only deliverable. The script also supports
`--format markdown` (chat-renderable candidate-set table for operator
skim) and `--format rich` (terminal-only, opt-in for TTY operators) but
neither is part of the agent's binding output.

## What the script does (mechanical detail)

1. `gh issue list --state open --limit N --json number,title,labels,createdAt,updatedAt,body,comments`
2. `git log --since='60 days ago' --grep='^fix('` to compute precedent count (cached in `~/.cache/gzkit/triage-precedent.json` keyed by HEAD SHA — recomputed only when HEAD moves)
3. Detects duplicates by identical title (canonical = lowest number)
3a. Mines blocker comments for cited GHI/ADR/OBPI references and resolves each
   GHI against live state, so a precondition that has already closed surfaces
   in the report instead of being inherited as standing fact. A bare `#N`
   preceded by an ordinal word (`rule #6`, `` `some-rule.md` #6 ``) is not
   treated as a citation — it numbers another document, and resolving it
   against the tracker produces a confident false gate
4. Routes each issue:
   - **direct-fix** when precedent ≥3 (default — almost any defect can be corrected inside the GHI itself; the GHI is the repair vessel and its receipts are the audit trail)
   - **close-dup** when an earlier issue has the same title
   - **ambiguous** when precedent is missing (operator decides direction)
   - **Escalation rule (one-way only):** if a GHI's shape warrants architectural work, the operator authors a *new ADR* via `gz plan` / `gz-design`, and OBPI decomposition follows from that ADR. The path is GHI → ADR → OBPI; it is never GHI → OBPI. An OBPI without an ADR home is a definitional defect, not a destination. Triage cannot manufacture either escalation step — schema/contract/scope-expansion signals in a GHI body are surfaced through the rationale field as escalation hints for operator judgment, not as a routing flip, and the script will never emit an OBPI route.
5. Scores urgency: `now` (blocking signal), `soon` (defect default), `later` (chore)
6. Validates rank input (each entry is exactly `number` + `severity`; the severity enum; the number is in the fetched set; any other key exits 1) and renders the deterministic deliverable

The mechanical pre-pass is necessary but not sufficient. It cannot read
the body for intent, weigh against in-flight ADR work, or sequence work
by dependency — that is what the agent does in Step 2.

## Why script + agent, not script alone

A script alone produces **routing classification, not triage** — it can compute a
precedent count but cannot answer "is this issue blocking the current ADR?" or
"should #319 land before #318?". An agent alone rendering the deliverable leaks
determinism turn to turn. So the script is both the mechanical pre-pass and the
deterministic renderer, and the agent contributes exactly one structured
artifact, the rank input (GHI #324). Cognitive freedom on the input; determinism
on the render.

## Anti-patterns

- Running the script with `--format markdown` or `--format rich` and
  presenting that as the deliverable — those are operator-skim views,
  not the rank deliverable
- Adding `action`, `why`, `rationale`, or any prose field to a `rankings[*]`
  entry — the schema is structural-only and rejects extras with exit 1.
  The rationale for ranking lives in the agent's reasoning, not the
  payload (GHI #424 round 3 — prose in input duplicates renderer output).
- Calling the script twice for the same data (one for `--format markdown`,
  one for `--format json`) — Step 1 is a single call
- Piping the rank-input JSON via `echo '<json>' | … --rank-input -` —
  rejected by the script (GHI #424 round 4); surfaces the entire payload
  on the bash command line and reproduces the duplicate-render shape in
  chat. Write the JSON to `.gzkit/cache/triage/<name>.json` and pass the
  path.
- Running `gz state --json` unconditionally — the cross-check is
  conditional on `files_mentioned` overlap with in-flight ADR allowed
  paths
- Rendering per-GHI panels, recommended-order tables, or any other
  intermediate view between Step 2 and Step 3 — the rank list IS the
  deliverable
- Narrating rank choices in chat before piping to `--format rank`
  (e.g. *"Ranked order: 1. #N — blocking; …"*) — the JSON is the
  agent's input artifact; chat-side restatement duplicates the
  deliverable
- Echoing the renderer's output in agent text after `--format rank`
  has produced it — even verbatim. The Bash tool result already
  presents the deliverable in Claude Code surfaces; restating it
  through the agent's generation channel is a duplicate render, not
  a confirmation. "Present verbatim" means *let the tool result stand*,
  not *copy-paste it into a text response*.
- Modifying GHIs from this skill — triage is read-only

## Related

- `AGENTS.md` § Defect-fix routing — the routing the script encodes
- `.gzkit/skills/ghi-author/SKILL.md` — authors the GHIs this skill triages
- `.gzkit/skills/ghi-close/SKILL.md` — closes GHIs after the routed work lands
- `.gzkit/rules/gh-cli.md` — allowed `gh` commands
- GHI #324 (script renders, agent supplies structured judgment) and GHI #424 (chat-silence: cache-path `--rank-input` plus the PreToolUse Bash hook)
