---
name: gz-obpi-specify
persona: main-session
description: Create and semantically author OBPI briefs linked to parent ADR items. Use when decomposing implementation into OBPI increments.
category: obpi-pipeline
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-12
metadata:
  skill-version: "1.3.0"
---

# gz-obpi-specify

Decompose an ADR's Feature Checklist into implementable OBPI briefs. Each brief
inherits lane, objective, and scope from the parent ADR's WBS table — not from
hardcoded defaults.

---

## Rationale: Increment Size as a Safety Property

OBPI increment size is **not a process preference** — it is an architectural
safety property. The brief boundary is the only reliable firing point for
governance gates.

Interpretability research (Lindsey et al. 2025) shows that once a model is
committed mid-output, grammatical-coherence circuits hold it on-rails until
the current structural unit is finished, even when safety circuits would
otherwise want it to stop. The repo-level analog: once an agent is three
files deep in a multi-file edit, completion pressure holds it on-rails until
the edit is structurally complete — a gate that would otherwise block the
direction cannot fire cleanly mid-edit.

OBPI briefs function as the agent's "sentence boundaries": the gate can fire
between briefs, not inside one. Bundling two briefs' worth of work into one
implementation pass collapses that firing point, even when the two briefs
are related. Keep briefs narrow enough that the pipeline has somewhere to
stop you.

---

## When to Use

- After an ADR is authored and its Decomposition Scorecard is valid
- When the Feature Checklist and WBS table are aligned (same count, same ordering)
- To create one OBPI brief per checklist item

## When NOT to Use

- For pool ADRs (they cannot receive OBPIs until promoted)
- If the ADR has no Feature Checklist or Decomposition Scorecard
- If the WBS table and Feature Checklist are misaligned (fix the ADR first)

---

## Invocation

```bash
# Create one OBPI brief (lane and objective from WBS table)
uv run gz specify my-feature-slug --parent ADR-0.0.11 --item 3

# Create and author one OBPI brief in one pass
uv run gz specify my-feature-slug --parent ADR-0.0.11 --item 3 --author

# Override lane explicitly
uv run gz specify my-feature-slug --parent ADR-0.0.11 --item 3 --lane heavy

# Dry run (show what would be created)
uv run gz specify my-feature-slug --parent ADR-0.0.11 --item 3 --dry-run

# Create all OBPIs for an ADR (run once per checklist item)
for i in $(seq 1 6); do
  uv run gz specify slug-$i --parent ADR-0.0.11 --item $i
done
```

---

## What the Command Does

1. **Reads the parent ADR** — resolves file, parses Feature Checklist and Decomposition Scorecard
2. **Validates alignment** — checklist item count must match scorecard target
3. **Parses the WBS table** — extracts lane, specification summary, and status per row
4. **Resolves lane** — priority: explicit `--lane` CLI arg > WBS table row > fallback `lite`
5. **Resolves objective** — from WBS specification summary column (not "TBD")
6. **Creates the brief** — renders the OBPI template with populated frontmatter
7. **Records the ledger event** — appends `obpi_created` to the project ledger

---

## Lane Resolution

| Source | When Used |
|--------|-----------|
| `--lane heavy` (CLI) | Always wins when explicitly passed |
| WBS table row | Used when `--lane` is not passed and WBS table has a row for this item |
| Fallback `lite` | Used when neither CLI nor WBS provides a lane |

The command prints the lane source so the operator can verify:
```
Lane: heavy (source: WBS table)
```

---

## Authored-Readiness Contract

`gz specify` is the ADR-to-OBPI decomposition command, not a pseudo-authoring
shortcut. It fills the brief with deterministic ADR-derived content, but the
brief is only ready for pipeline execution when it passes authored validation:

```bash
uv run gz obpi validate --adr ADR-0.0.11 --authored
```

That gate requires each brief to have substantive:

- Objective
- Allowed Paths
- Denied Paths
- Requirements (FAIL-CLOSED)
- Discovery Checklist prerequisites and existing-code entries
- OBPI-specific verification commands
- REQ-backed acceptance criteria

## Skill Responsibility

The skill does not stop at `uv run gz specify`.

The intended workflow is:

1. Run `gz specify --author` to materialize the OBPI from the ADR/WBS contract and execute the authored pass.
2. Read the parent ADR sections that govern the item: Feature Checklist, WBS row,
   Intent, Decision, Interfaces, Evidence, and adjacent OBPIs when needed.
3. Author the brief semantically:
   - narrow Allowed Paths and Denied Paths to the real execution boundary
   - rewrite Requirements into OBPI-specific fail-closed rules
   - populate Discovery Checklist with real prerequisite and existing-code reads
   - replace generic verification with commands that prove this item specifically
   - ensure Acceptance Criteria are concrete and mapped to REQ IDs
4. Run `uv run gz obpi validate --authored <path>` and keep authoring until it passes.

The CLI owns deterministic decomposition. The skill owns the semantic authoring
pass that turns the generated brief into an execution contract.

---

## Pre-Save Ground-Truth Check (GHI #190)

Before saving a brief, every path in the `Allowed Paths` and `Denied Paths`
sections MUST be verified against on-disk reality. LLM authoring routinely
imports model priors from adjacent projects (airlineops, half-remembered
TOML-based chore patterns) and writes them as if they were gzkit conventions.
The OBPI-0.0.16-03 brief shipped with fabricated framework paths
(`config/chores/<slug>.toml`, `src/gzkit/chores/<module>.py`,
`tests/chores/test_<module>.py`) — none of those conventions exist; the real
chore framework uses `config/gzkit.chores.json` + `ops/chores/<slug>/`
packages. The implementer had to rewrite Allowed Paths as a scope amendment
before proceeding.

### Per-path verification — apply to every Allowed Paths and Denied Paths entry

For each path:

1. **Glob the path** — `Glob(pattern=<path>)`. If the path matches existing
   files, the path is grounded. Continue.
2. **Glob the parent directory** — `Glob(pattern=<parent>/*)`. If the parent
   exists, inspect its contents:
   - Confirm at least one file in the parent uses the same extension
     (`.py`, `.toml`, `.json`, `.md`) as the proposed path. The matching
     extension is your evidence that the file you propose to create is
     consistent with the convention of the directory.
   - If the parent exists but no file shares the extension, STOP — either
     the convention is different (verify by reading a sibling file) or the
     proposed path is fabricated. Do not save.
3. **If neither the path nor the parent exists** — the path is green-field.
   Verify the convention by:
   - Reading the parent ADR's Interfaces / Evidence sections for the
     intended layout, OR
   - Searching for adjacent precedents (`Grep`, `Glob`) that establish the
     intended convention, OR
   - Asking the human ("the brief proposes `<path>` but no precedent exists;
     is this a new convention?") before saving.

### Mandatory STOP conditions

Do NOT save a brief if any of the following is true:

- An Allowed Path references a directory tree that does not exist and has
  no precedent (e.g. `src/gzkit/chores/` when chores live in `ops/chores/`).
- An Allowed Path uses an extension that no sibling file uses
  (e.g. `.toml` when sibling files are `.json`).
- The author has not personally read at least one existing file in each
  parent directory of an Allowed Path before saving.

### Anti-pattern

| Thought | Reality |
|---------|---------|
| "The framework probably uses TOML for chores like airlineops does" | Verify it. `Glob("config/**/*.toml")` and `Glob("config/**/*.json")` will tell you in one call which convention this repo uses. |
| "I'll let the implementer correct the paths if they're wrong" | The OBPI-0.0.16-03 implementer paid the cost of a scope amendment + context-burning rewrite because the brief author skipped this check. The cost of one Glob call before saving is far lower than the cost of an in-flight scope amendment. |
| "The Allowed Paths look architecturally correct — that's enough" | Architectural plausibility is not ground truth. Run the Glob. Read a sibling file. Then save. |

### Future mechanical enforcement

A future iteration adds `gz validate --briefs --ground-truth` — a fail-closed
CLI pass that checks every Allowed Path in every Draft brief against on-disk
reality. Until then, this section governs authoring discipline by hand.
Tracked as a follow-up to GHI #190.

---

## Pre-Conditions

- Parent ADR must have a valid Decomposition Scorecard
- Feature Checklist item count must match scorecard `Final Target OBPI Count`
- Parent ADR must not be a pool ADR

## Post-Conditions

- OBPI brief file created at `{adr-dir}/obpis/OBPI-{version}-{NN}-{slug}.md`
- Lane matches WBS table (or CLI override)
- Objective derived from WBS specification summary
- `obpi_created` ledger event recorded

---

## Validation

After creating all briefs:

```bash
# Fail closed if any brief is still thin or pseudo-authored
uv run gz obpi validate --adr ADR-0.0.11 --authored

# Verify count matches
ls docs/design/adr/foundation/ADR-0.0.11-*/obpis/ | wc -l

# Verify lanes match WBS
grep "^lane:" docs/design/adr/foundation/ADR-0.0.11-*/obpis/*.md

# Register any unregistered OBPIs
uv run gz register-adrs ADR-0.0.11 --all
```

---

## Heavy Lane Requirements

When a brief's lane is Heavy (from WBS or CLI override):

1. **Read `assets/HEAVY_LANE_PLAN_TEMPLATE.md`** before authoring — this is mandatory
2. Gate 5 attestation is required before OBPI closure
3. Human must execute CLI commands and provide explicit attestation
4. BDD scenarios + docs/manpage updates are additional acceptance criteria

**Heavy lane failure modes:**
- Marking OBPI closed before human attestation
- Skipping Gate 5 attestation step
- Not presenting CLI commands for human verification

---

## Common Rationalizations

These thoughts mean STOP — you are about to ship a thin or pseudo-authored brief:

| Thought | Reality |
|---------|---------|
| "The generated brief looks complete enough — ship it" | `gz specify` only fills ADR-derived defaults. The semantic authoring pass is mandatory. The authored validation gate exists because generated briefs are the start, not the end. |
| "The Allowed Paths from the template will work" | Template defaults are intentionally broad. Narrow them to the real execution boundary or the OBPI will sprawl during implementation. |
| "I can leave Discovery Checklist generic — the implementer will figure it out" | Generic checklists produce generic implementations. The checklist is where you record the prerequisite reads that prevent re-discovery on every pipeline run. |
| "REQ IDs are bookkeeping — I'll add them after the brief is approved" | Tests derive from REQ IDs. No REQ IDs means tests cannot be traced to acceptance criteria, which collapses the TDD discipline at Gate 2. |
| "Verification commands can be the same across all OBPIs in this ADR" | The point of OBPI-specific verification is that each brief proves *this* increment. Shared verification means you can't tell which brief broke. |
| "The WBS lane says lite but this is heavier than I thought — I'll just proceed lite" | The WBS lane is the canonical contract. If the work is heavier, fix the WBS first, then re-run specify. Silently proceeding lite skips Gate 5 attestation. |
| "`gz obpi validate --authored` is failing on minor things — I'll dismiss them" | The authored gate is fail-closed for a reason. Each warning is a brief that won't survive pipeline execution. Fix every one. |

## Red Flags

- A brief whose Allowed Paths matches the parent ADR's full scope (no narrowing)
- Requirements section that copies the ADR's intent verbatim instead of OBPI-specific fail-closed rules
- Discovery Checklist with no concrete file paths or prerequisite reads
- Acceptance Criteria written in prose without REQ-XX identifiers
- Verification commands that don't actually exercise this OBPI's surface
- Heavy lane brief without `assets/HEAVY_LANE_PLAN_TEMPLATE.md` consulted
- Stopping at `gz specify` without running `gz obpi validate --authored`

## Related Skills

| Skill | Relationship |
|-------|--------------|
| `gz-adr-create` | Creates the parent ADR that specify decomposes |
| `gz-obpi-pipeline` | Executes briefs created by specify |
| `gz-adr-evaluate` | Evaluates ADR+OBPI quality (run after specify) |
