---
name: ghi-triage
persona: main-session
description: Triage every open GHI — read each body, classify severity, and produce a deterministic rank-ordered deliverable. The bundled script handles fetch + routing + final rendering; the agent does the body-reading judgment pass between them. Use when reviewing the open-issue queue, before a planning session, or when deciding what to actually pull next.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-05-08
metadata:
  skill-version: "5.1.0"
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
uv run python .claude/skills/ghi-triage/scripts/triage.py [args] --format json
```

Each record contains: `number`, `title`, `labels`, `klass` (one of
`defect`/`enhancement`/`investigation`/`chore`/`unlabeled`), `body`
(full), `files_mentioned`, `dup_of`, `route`, `urgency`, `rationale`,
`created_at`, `updated_at`. The `route` field is the script's mechanical
classification per `AGENTS.md` § Defect-fix routing — treat it as evidence
the agent reasons over, not as the final answer.

### Step 2 — Read each body, compose rank input

For each GHI in the JSON, read the body (it is inline — no `gh issue view`
needed). Compose a single rank-input JSON document with one entry per GHI
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

The schema is structural-only by design. Earlier versions (≤4.3.x) accepted
agent-supplied `action` and `why` prose, which then duplicated the
renderer's output in the operator's chat surface — the rank-input JSON
visible in the Bash command (or Write/heredoc) showed the same severity +
action + why content the rendered deliverable then printed back. GHI #424
was reopened twice while chat-silence rules tried to suppress that
duplication; only removing the prose fields from the schema makes
recurrence mechanically impossible. The agent's cognitive contribution is
**selection + ordering + severity**; the renderer owns all prose, derived
from the fetched issue set.

### Step 3 — Render the deliverable

Write the rank-input JSON to a cache file under `.gzkit/cache/triage/`,
then pass that path to the script with `--format rank`:

```bash
# Write tool: .gzkit/cache/triage/rank.json  ← {"rankings":[…]}
uv run python .claude/skills/ghi-triage/scripts/triage.py \
    --format rank --rank-input .gzkit/cache/triage/rank.json
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
ordering dependency) or to add an explicit precondition to the WHY field
(e.g. "must precede #N because they share `src/foo.py`"). Do **not** run
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

1. `gh issue list --state open --limit N --json number,title,labels,createdAt,updatedAt,body`
2. `git log --since='60 days ago' --grep='^fix('` to compute precedent count (cached in `~/.cache/gzkit/triage-precedent.json` keyed by HEAD SHA — recomputed only when HEAD moves)
3. Detects duplicates by identical title (canonical = lowest number)
4. Routes each issue:
   - **direct-fix** when precedent ≥3 (default — almost any defect can be corrected inside the GHI itself; the GHI is the repair vessel and its receipts are the audit trail)
   - **close-dup** when an earlier issue has the same title
   - **ambiguous** when precedent is missing (operator decides direction)
   - **Escalation rule (one-way only):** if a GHI's shape warrants architectural work, the operator authors a *new ADR* via `gz plan` / `gz-design`, and OBPI decomposition follows from that ADR. The path is GHI → ADR → OBPI; it is never GHI → OBPI. An OBPI without an ADR home is a definitional defect, not a destination. Triage cannot manufacture either escalation step — schema/contract/scope-expansion signals in a GHI body are surfaced through the rationale field as escalation hints for operator judgment, not as a routing flip, and the script will never emit an OBPI route.
5. Scores urgency: `now` (blocking signal), `soon` (defect default), `later` (chore)
6. Validates rank input (severity enum, action ≤80 chars, why ≤120 chars, no newlines, no markdown control chars) and renders the deterministic deliverable

The mechanical pre-pass is necessary but not sufficient. It cannot read
the body for intent, weigh against in-flight ADR work, or sequence work
by dependency — that is what the agent does in Step 2.

## Why script + agent, not script alone

The v2 redesign collapsed triage to "run a script, present output." That
produced **routing classification, not triage** — the script can compute
`precedent ≥3 AND ≤3 files` but cannot answer "is this issue blocking the
current ADR?" or "should #319 land before #318?"

The v3 rewrite over-corrected: it bound the agent to render Rich panels +
recommended-order tables + rank lists *inline*, producing three views of
the same eight rows and routing the deliverable rendering through agent
prose where determinism leaked turn-to-turn. Three concrete defects
landed that v3 addressed with new ceremony rather than fixing the
fundamental: **the script should render the deliverable; the agent
should provide judgment as structured input** (GHI #324).

v4 keeps the script as both the mechanical pre-pass AND the deterministic
renderer, with the agent contributing exactly one structured artifact
(the rank input). Cognitive freedom on the input; determinism on the
render. This matches `AGENTS.md` § Behavior Rules — Always #5 (offload
deterministic work to scripts) and § OPERATOR ECONOMY OF EFFORT
(operator never reads raw output without a human-readable summary —
markdown is human-readable; Rich-in-chat is not).

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

- `AGENTS.md` § Defect-fix routing — the routing thresholds the script encodes
- `AGENTS.md` § Behavior Rules — Always (offload + judgment invariants)
- `AGENTS.md` § OPERATOR ECONOMY OF EFFORT — chat-renderable summary doctrine
- `.gzkit/skills/ghi-author/SKILL.md` — authors the GHIs this skill triages
- `.gzkit/skills/ghi-close/SKILL.md` — closes GHIs after the routed work lands
- `.claude/rules/gh-cli.md` — allowed `gh` commands
- GHI #324 — the v3 → v4 rewrite that produced this contract
- GHI #424 — the chat-silence enforcement series; round 4 added the
  cache-path `--rank-input` requirement and the PreToolUse Bash hook
  that pin both surfaces of the duplicate-render shape
