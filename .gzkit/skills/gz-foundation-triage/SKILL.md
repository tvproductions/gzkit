---
name: gz-foundation-triage
persona: main-session
description: Rank the in-flight foundation backlog by priority — cross-references
  agent-insights.jsonl signal count, GHI occurrence count, and declared invariants;
  flags port/adapter reclassification candidates; diagnosis only, ephemeral ranked report.
category: adr-lifecycle
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-05-23
metadata:
  skill-version: "1.0.0"
model: sonnet
---

# gz-foundation-triage

Rank the in-flight foundation backlog by priority. The bundled script does the
deterministic work (gather Draft/Proposed foundation ADRs, count governance
signals, render the deliverable). The agent does the cognitive work (read each
candidate's § Intent and § Decision, classify severity, flag port/adapter
reclassification candidates). Determinism lives at the rendering edge;
cognitive freedom lives only on the input edge.

This skill is **diagnosis only**. It MUST NOT mutate any foundation ADR,
ledger entry, registry, or promote/complete/change-status on any artifact.
Running the skill is read-only across the governance surface.

The rubric module at `src/gzkit/foundation/rubric.py` is the foundation-triage-rubric
OBPI's surface and is not implemented in this OBPI; this skill references it
by path/name and ranks on raw signal counts in the interim.

## Invocation

```text
/gz-foundation-triage
```

## Triage Procedure (binding — three steps)

When this skill is invoked, the agent MUST execute the three steps below in
order. The deliverable is the rank-ordered list from Step 3.

### Step 1 — Mechanical pre-pass (single script call)

Run the bundled helper once with `--format json` to gather every in-flight
(Draft or Proposed) foundation ADR with its governance-signal counts inline:

```bash
uv run python .gzkit/skills/gz-foundation-triage/scripts/triage.py --format json
```

Each record contains: `id` (canonical ADR id, e.g. `ADR-0.0.57`), `status`
(one of `Draft`/`Proposed`), `title`, `path` (foundation ADR file relative
to repo root), `insight_count` (`agent-insights.jsonl` mentions of the ADR
id), `ghi_count` (GHI references mined from the same insights stream),
`invariant_mentions` (occurrences in `AGENTS.md` and `.gzkit/rules/*.md`).
The script is read-only over the governance corpus — it parses files; it
never writes them.

### Step 2 — Cognitive pass (read each candidate, classify severity)

For each record in the Step 1 JSON, read the foundation ADR's `§ Intent`
section and `§ Decision` section. This is the contract; everything else
hangs off it. Do not classify without reading both.

Then apply the **port/adapter reclassification check** (mirrored from the
pool-triage cognitive-pass pattern, which adopted GHI #424 round-3
hardening): flag any candidate whose scope authors an invariant or
prerequisite without which downstream features cannot exist. A flagged
candidate is emitted as `{id, reclassify: "foundation"}` in a separate
annotation list, NOT as a rank-input entry. Ranked candidates and
reclassification annotations are mutually exclusive: a single candidate
appears in one list or the other, never both.

Compose a single rank-input JSON document with one entry per candidate the
agent recommends working on:

```json
{
  "rankings": [
    {"id": "ADR-0.0.57", "severity": "urgent"},
    {"id": "ADR-0.0.48", "severity": "next-quarter"}
  ],
  "reclassify_foundation": [
    {"id": "ADR-pool.some-slug", "reclassify": "foundation"}
  ]
}
```

**Rendering-edge contract (binding — structural-only schema):**

| Field | Constraint |
|-------|------------|
| `rankings[*].id` | str; must appear in the Step 1 fetched set |
| `rankings[*].severity` | one of `urgent` (pull this quarter), `next-quarter`, `latent` |
| `reclassify_foundation[*].id` | pool ADR id (slug-form) |
| `reclassify_foundation[*].reclassify` | literal `"foundation"` |
| any other field | rejected by the renderer |

The schema is structural-only by design. The agent's cognitive contribution
is **selection + ordering + severity + reclassification flag**; the renderer
owns all prose, derived from the fetched candidate set.

### Step 3 — Deterministic rendering

Write the rank-input JSON to a cache file under `.gzkit/cache/foundation-triage/`,
then pass that path to the script with `--format rank`:

```bash
# Write tool: .gzkit/cache/foundation-triage/rank.json
uv run python .gzkit/skills/gz-foundation-triage/scripts/triage.py \
    --format rank --rank-input .gzkit/cache/foundation-triage/rank.json
```

The script renders a deterministic markdown deliverable: one numbered row
per ranked foundation, each row containing the severity and title in a
fixed shape; the reclassification annotations render in a separate section
beneath. **The script's stdout IS the deliverable** — do not echo, restate,
copy, or paraphrase that output in agent-generated text.

There is no Step 4. The rank list and the reclassification annotation list
together ARE the recommended work order.

## Output Contract

Declared form: **deterministic markdown**, the script's `--format rank`
output, presented verbatim. Chat-renderable; no Rich box-drawing glyphs;
no ANSI color sequences.

## Ephemeral-output invariant (binding)

After a foundation-triage run, the following MUST hold:

```bash
git status --porcelain docs/design/adr/foundation/ .gzkit/ledger.jsonl
# Expected: empty output
```

If any foundation ADR file or `.gzkit/ledger.jsonl` shows as modified, the
ephemeral / diagnosis-only invariant has been violated and the skill is
defective. The skill is a read-only diagnostic; promotion remains an
operator decision under the relevant lifecycle ADR.

## Anti-patterns

- Running foundation-triage as a commit gate (it is on-demand only)
- Auto-promoting foundations from the triage output
- Mutating any foundation ADR or ledger entry as a side-effect
- Restating the rendered deliverable in agent-generated prose
- Adding agent-supplied prose fields to the rank-input JSON schema

## Related

- ADR-0.0.57 — foundation-ADR nominal-ID semantics and priority triage
- `.gzkit/skills/ghi-triage/SKILL.md` — sibling pattern in the
  `governance-triage` bounded context
- pool-triage cognitive-pass — the port/adapter reclassification check
  inherits its language from the pool-triage cognitive-pass pattern
