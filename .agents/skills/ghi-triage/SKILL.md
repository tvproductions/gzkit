---
name: ghi-triage
persona: main-session
description: Triage every open GHI — read each body, cross-check against current ADR/OBPI state and recent commits, and produce an ordered work plan with per-issue rationale. The bundled script is the mechanical pre-pass (routing classification + duplicate detection); the agent does the judgment pass on top of it. Use when reviewing the open-issue queue, before a planning session, or when deciding what to actually pull next.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-25
metadata:
  skill-version: "3.1.0"
---

# ghi-triage

Real triage — read each issue, weigh it against current state, recommend an
order. The bundled script handles the mechanical pre-pass so the agent
spends its tokens on judgment, not on re-shelling `gh` and `git`.

## Invocation

```text
/ghi-triage              ← triage all open GHIs
/ghi-triage --label defect    ← filter to one label
/ghi-triage --limit 25        ← cap the scan
```

## Triage Procedure (binding)

When this skill is invoked, the agent MUST execute all five steps in order.
Step 1 is mechanical (run the script). Steps 2–5 are the actual triage —
do not skip them. Stopping after step 1 produces routing classification, not
triage, and that mislabel was the GHI #316-class failure this skill exists
to close.

### Step 1 — Mechanical pre-pass (single command)

Render the human-readable Rich table once, for the operator:

```bash
uv run python .claude/skills/ghi-triage/scripts/triage.py [args]
```

Present the output verbatim. This is the **evidence**, not the deliverable.

### Step 2 — Pull structured records for judgment

In the same turn, run the script again with `--format json` to get the
candidate set with bodies, file mentions, and pre-computed routing in a
form the agent can reason over without re-shelling `gh`:

```bash
uv run python .claude/skills/ghi-triage/scripts/triage.py [args] --format json
```

Each record contains: `number`, `title`, `labels`, `klass` (one of
`defect`/`enhancement`/`investigation`/`chore`/`unlabeled`), `body`
(full), `files_mentioned`, `dup_of`, `route`, `urgency`, `rationale`,
`created_at`, `updated_at`.

### Step 3 — Cross-check current state (parallel)

Gather the context needed to judge each GHI's relevance against in-flight
work. Run these in parallel in one tool call:

```bash
uv run gz status --table        # active ADRs, gate state, blockers
uv run gz state --json          # artifact lineage, OBPI claims
git log --oneline -25           # what just landed (avoid recommending in-flight work)
uv run gz obpi-lock list        # what other agents have claimed
```

If any command surfaces an active OBPI or recent commit that overlaps a
GHI body or its `files_mentioned`, that overlap is a triage signal — note
it in step 4.

### Step 4 — Per-GHI judgment pass

For each GHI in the JSON, render a per-issue judgment block as a Rich
panel or section. The operator reads, doesn't paste — Rich rendering all
the way. Each block answers three questions:

1. **What is this issue actually asking for?** Read the body, not just
   the title. One sentence describing the real ask.
2. **What is its relationship to current state?** Cite the ADR/OBPI/commit
   from step 3 if there is overlap, dependency, or supersession; say
   "independent" if not.
3. **Severity and confidence.** `blocking` (current work fails until
   fixed), `degrading` (current work succeeds but produces drift),
   `latent` (deferrable without immediate harm); plus a one-line
   confidence note grounded in observed evidence (file count, body
   specificity, recency).

Use Rich `Panel` with the GHI number + title as the panel title, and a
short body (3–5 lines max). Color the panel border by severity:
`bold red` blocking, `yellow` degrading, `dim` latent.

### Step 5 — Ordered work plan (Rich table)

After all per-GHI panels, render a final Rich table titled **Recommended
order** with columns `Order`, `GHI`, `Action`, `Why now / why later`. The
ordering is the agent's call — derived from severity + dependency chain +
operator-value-per-token, not from the mechanical urgency bucket. Tie
each row's "Why" back to a step-3 finding or a step-4 severity claim so
the operator can audit the reasoning.

If two GHIs have a hard ordering dependency, state it explicitly in the
"Why now / why later" column ("must precede #N because …").

### Step 6 — Final rank-ordered list (last block, always)

After the step-5 table, emit a compact rank-ordered list as the last
block of the reply. This is the at-a-glance answer to "what should I
work on?" — operator can read the full table for reasoning, then drop to
this list to pick the next ticket.

Format: a Rich-rendered enumerated list, one row per GHI, in the same
order as step 5's table. Each row reads:

```
N. #GHI — <route> — <one-line action>
```

Use the Rich `Console.print` color palette from the per-GHI panels:
blocking rows in `bold red`, degrading in `yellow`, latent in `dim`.
This block is the deliverable's terminal punctuation — there is nothing
after it.

## Output Contract

Declared form: **all Rich, all the way through.** No markdown tables,
no plain-text bullet lists, no copy-paste short list. The operator reads
the rendered output; they do not paste it elsewhere.

Required output blocks, in order:

1. The script's Rich table from step 1 (verbatim — do not re-render).
2. One Rich `Panel` per GHI from step 4, severity-colored.
3. A Rich `Table` titled **Recommended order** from step 5.
4. A compact rank-ordered Rich list from step 6 — last block, always.

Steps 2 and 3 are produced by the agent emitting `console.print()`-equivalent
text via the `Bash` tool with a small inline `uv run python` block, OR by
the agent printing Rich-formatted strings directly using ANSI escapes.
Prefer the inline-Python approach — it composes with the existing skill
script's color palette and the operator gets consistent rendering.

## What the script does (pre-pass details)

1. `gh issue list --state open --limit N --json number,title,labels,createdAt,updatedAt,body`
2. `git log --since='60 days ago' --grep='^fix('` to compute precedent count
3. Detects duplicates by identical title (canonical = lowest number)
4. Routes each issue per `AGENTS.md` § Defect-fix routing thresholds:
   - **direct-fix** when precedent ≥3 AND no OBPI signal AND ≤3 files mentioned
   - **OBPI-ceremony** on schema/contract/scope-expansion/brief-boundary signals
   - **close-dup** when an earlier issue has the same title
   - **ambiguous** when precedent is missing
5. Scores urgency: `now` (blocking signal), `soon` (defect default), `later` (chore)
6. Emits Rich (default), markdown (`--format markdown`), or JSON
   (`--format json`) — JSON is the agent's input to steps 4 and 5.

The mechanical pre-pass is necessary but not sufficient. It cannot read
the body for intent, weigh against in-flight ADR work, or sequence work
by dependency — that is what the agent does in steps 2–5.

## Why script + agent, not script alone

The v2 redesign collapsed triage to "run a script, present output." That
was faster than ad-hoc Bash, but it produced **routing classification,
not triage** — the script can compute `precedent ≥3 AND ≤3 files` but
cannot answer "is this issue blocking the current ADR?" or "should #319
land before #318?" Operators kept asking those questions after the
classifier ran, which meant the classifier was the pre-pass, never the
deliverable.

v3 keeps the script as the mechanical pre-pass (it's still the right
shape for fetch + classify + render) and binds the agent to do the
judgment work the operator was always going to ask for anyway. This
matches `AGENTS.md` § Behavior Rules — Always #5 (offload deterministic
work to scripts/subagents) and #7 (don't run a confident-wrong-direction
classification when the operator wants real triage).

## Anti-patterns

- Stopping after step 1 and presenting the script's table as the
  deliverable — that is routing classification, not triage
- Skipping step 3 — per-GHI judgment without cross-checking current state
  is opinion, not triage
- Rendering steps 4 or 5 in plain text or markdown — the Output Contract
  is Rich all the way; markdown is for the `--format markdown` consumer,
  not for the agent's reply
- Treating the script's `urgency` field as the final ordering — it is a
  bucket (now/soon/later), not a sequence
- Modifying GHIs from this skill — triage is read-only

## Related

- `AGENTS.md` § Defect-fix routing — the routing thresholds the script encodes
- `AGENTS.md` § Behavior Rules — Always (offload + judgment invariants)
- `.gzkit/skills/ghi-author/SKILL.md` — authors the GHIs this skill triages
- `.gzkit/skills/ghi-close/SKILL.md` — closes GHIs after the routed work lands
- `.claude/rules/gh-cli.md` — allowed `gh` commands
