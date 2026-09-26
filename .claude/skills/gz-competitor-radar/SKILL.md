---
name: gz-competitor-radar
description: Run a monthly B+ competitor-discovery radar for spec-driven and agent-workflow tools, render JSON-governed reports, grill suggested gzkit moves, and route approved opportunities without unattended governance mutation.
compatibility: Project-local skill contract.
# Withheld from delivery: this radar judges candidates by whether they name a
# gzkit-relevant strength and recommends gzkit governance moves, and the wheel
# ships only `src/gzkit/skills/**/*.md`, so its scripts never arrive (GHI #915).
project_local: true
category: agent-operations
metadata:
  skill-version: "1.1.0"
  govzero-framework-version: "v6"
  govzero-author: "gzkit-governance"
  govzero_layer: "Layer 1 - Evidence Gathering"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-09-26
model: opus
---

# gz-competitor-radar

Monthly competitor radar for spec-driven development, agent skills, executable
spec ecosystems, and adjacent workflow tools.

## Posture

- **Discovery: B+.** Scan the seeded registry and actively discover new
  candidates. Admit new candidates only when the scan cites evidence and names a
  gzkit-relevant strength, rejection, or route.
- **Execution: B-.** The report may recommend ADR/GHI/pool moves, but it does
  not mutate governance artifacts. It opens a grill/design discussion first.
- **Report structure: C.** Render both product snapshots and strength-pattern
  maps. Products show trajectory; patterns prevent copying brands.
- **Source of truth.** `artifacts/reports/competitor-radar/registry.json` and
  monthly scan JSON files govern the Markdown. Markdown reports under
  `artifacts/reports/competitor-radar/` are generated projections and must not
  be hand-edited.
- **Portability.** Deterministic scripts live with this skill under
  `scripts/`, per Agent Skills packaging guidance.
- **Cadence.** Monthly is the intended cadence, but nothing schedules it: the
  radar runs when the operator invokes it. The newest file under
  `artifacts/reports/competitor-radar/scans/` shows when it last ran.

## When To Use

- Monthly competitor/status scan.
- Ad-hoc scan when a new comparator appears.
- Before deciding whether competitor strengths warrant a new pool ADR, existing
  pool update, active ADR amendment, GHI, or explicit rejection.
- When the operator asks to grill competitor-derived recommendations.

## Workflow

1. **Refresh sources.** Browse current official sources first: project homepage,
   repository, docs, release notes, marketplace entry, and credible radar-style
   commentary. Do not rely on memory.
2. **Update scan JSON.** For a new month, create the skeleton with
   `radar.py new-scan --month YYYY-MM`: it seeds one snapshot per registry
   competitor and refuses an existing month unless `--overwrite` is passed.
   Write findings to `artifacts/reports/competitor-radar/scans/YYYY-MM.json`.
   The agent authors this JSON from evidence and from grill answers. The
   operator does not edit JSON or Markdown.
3. **Render reports.**

   ```bash
   uv run python .gzkit/skills/gz-competitor-radar/scripts/radar.py render
   ```

4. **Validate JSON and generated Markdown.**

   ```bash
   uv run python .gzkit/skills/gz-competitor-radar/scripts/radar.py validate
   ```

5. **Open the grill discussion.** For each suggested move, ask one question at a
   time, recommend an answer, and walk the decision tree. Record answers back
   into the scan JSON, rerender, and revalidate.
6. **Route only after decisions.** Approved outcomes may update pool ADRs, file
   GHIs through `ghi-author`, or start design/promotion work. Rejections are
   recorded explicitly. A move's `route` must be one of `existing-pool-adr`,
   `new-pool-adr`, `open-feature-adr`, `ghi`, `explicit-rejection` or
   `discussion-only`; foundation ADRs are closed to new authoring
   (`AGENTS.md` § Gate Covenant), so there is no foundation route.

## Grill Discipline

Ask the per-move questions in `references/grill-questions.md` for every
suggested move, and its admission questions for every new candidate. Ask one
question at a time. Prefer a recommended answer with tradeoffs. If the
answer is discoverable from repo state or source evidence, gather it instead of
asking the operator to type it.

## Scripts

All scripts are stdlib Python and portable with the skill:

```bash
uv run python .gzkit/skills/gz-competitor-radar/scripts/new_scan.py --month YYYY-MM
uv run python .gzkit/skills/gz-competitor-radar/scripts/render_report.py
uv run python .gzkit/skills/gz-competitor-radar/scripts/validate_registry.py
uv run python .gzkit/skills/gz-competitor-radar/scripts/validate_report.py
```

The wrapper scripts delegate to `scripts/radar.py`. `validate_registry.py`
and `validate_report.py` both run the same full `validate`.

## Data Contract

Registry source:

```text
artifacts/reports/competitor-radar/registry.json
```

Monthly scan source:

```text
artifacts/reports/competitor-radar/scans/YYYY-MM.json
```

Generated reports:

```text
artifacts/reports/competitor-radar/index.md
artifacts/reports/competitor-radar/YYYY-MM.md
```

Validation compares rendered Markdown byte-for-byte against the JSON source. If
the Markdown differs, edit the JSON or the renderer, rerender, and revalidate.

## References

- `references/registry.schema.json` — registry shape.
- `references/scan.schema.json` — monthly scan shape.

The schemas name only the top-level keys. `radar.py validate` is the authority:
it also checks each competitor, pattern, snapshot and move, their ids and
cross-references, and the route and watch-level vocabularies.
- `references/report-template.md` — report section contract.
- `references/grill-questions.md` — grill question bank.

## Related Skills

- `gz-design`
- `gz-adr-evaluate`
- `gz-justify`
- `ghi-author`
- `gz-agent-sync`
