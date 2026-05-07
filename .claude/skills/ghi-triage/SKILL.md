---
name: ghi-triage
persona: main-session
description: Triage every open GHI — read each body, classify severity, and produce a deterministic rank-ordered deliverable. The bundled script handles fetch + routing + final rendering; the agent does the body-reading judgment pass between them. Use when reviewing the open-issue queue, before a planning session, or when deciding what to actually pull next.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-25
metadata:
  skill-version: "4.1.0"
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
    {
      "number": 324,
      "severity": "blocking",
      "action": "fix triage skill rendering",
      "why": "operator-facing surface degrades chat output every invocation"
    },
    {
      "number": 323,
      "severity": "degrading",
      "action": "scope behave-req-tags to post-impl briefs",
      "why": "validator currently fires on Draft briefs that have no scenarios yet"
    }
  ]
}
```

**Rendering-edge contract (binding):**

| Field | Constraint |
|-------|------------|
| `number` | int; must appear in the Step 1 fetched set |
| `severity` | one of `blocking` (current work fails), `degrading` (succeeds but produces drift), `latent` (deferrable) |
| `action` | ≤80 chars; single clause; no newlines; no markdown control characters (`* _ \` # \| < >`) |
| `why` | ≤120 chars; single clause; same character restrictions |

These are enforced by the script and rejected with exit 1 on violation.
The intent is to constrain WHY-shape at the render boundary so determinism
does not leak through cognitive freedom on the input side — the agent is
free to choose what to say; the rendering contract pins how it can say it
(see GHI #324, comment by voidborne-d).

### Step 3 — Render the deliverable

Pipe the rank-input JSON to the script with `--format rank`:

```bash
echo '<rank-input JSON>' | uv run python .claude/skills/ghi-triage/scripts/triage.py --format rank --rank-input -
```

Or write the JSON to a file and pass `--rank-input <path>`. The script
renders a deterministic markdown deliverable: one numbered row per ranked
GHI, each row containing the severity, route, action, and WHY in a fixed
shape. **Present the script's output verbatim. This is the deliverable.**

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
- Composing rank input with multi-clause sentences, embedded markdown,
  or newline-separated reasoning — the validator rejects these by
  design; do not work around it by stripping characters until validation
  passes, re-think the WHY language instead
- Calling the script twice for the same data (one for `--format markdown`,
  one for `--format json`) — Step 1 is a single call
- Running `gz state --json` unconditionally — the cross-check is
  conditional on `files_mentioned` overlap with in-flight ADR allowed
  paths
- Rendering per-GHI panels, recommended-order tables, or any other
  intermediate view between Step 2 and Step 3 — the rank list IS the
  deliverable
- Modifying GHIs from this skill — triage is read-only

## Related

- `AGENTS.md` § Defect-fix routing — the routing thresholds the script encodes
- `AGENTS.md` § Behavior Rules — Always (offload + judgment invariants)
- `AGENTS.md` § OPERATOR ECONOMY OF EFFORT — chat-renderable summary doctrine
- `.gzkit/skills/ghi-author/SKILL.md` — authors the GHIs this skill triages
- `.gzkit/skills/ghi-close/SKILL.md` — closes GHIs after the routed work lands
- `.claude/rules/gh-cli.md` — allowed `gh` commands
- GHI #324 — the v3 → v4 rewrite that produced this contract
