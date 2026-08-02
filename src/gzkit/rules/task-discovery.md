---
id: task-discovery
paths:
  - "src/gzkit/**"
  - "docs/design/adr/**"
  - ".gzkit/**"
description: Four-channel TASK attribution discovery taxonomy for governance traceability
---

<!-- rule-version: 0.5.1 -->

# TASK Discovery (gzkit)

> **Rule version:** `0.5.1` — commit-trailer channel is producer-stamped (`0.5.0`, GHI #731); prior version history lifted to [Rule Version History](../../docs/governance/rule-version-history.md#task-discoverymd). Binding rules unchanged.

## Invariant

**Every unit of labor traceable to a TASK MUST surface that attribution through at least one of four discovery channels — with a floor: any commit touching `src/**` or `tests/**` MUST additionally carry a `Task:` trailer.**

The channels are **cumulative-with-a-floor, not a free choice.** An `@advances` decorator on a `src/gzkit/**` function does *not* discharge the trailer obligation for the commit that lands it: `gz validate --commit-trailers` fails closed on src/ and tests/ scope regardless of decoration (`has_task_trailer()` in `src/gzkit/tasks.py`; GHI #552). `@advances` registration has no commit-time consequence. See `.gzkit/rules/tests.md` § TASK-Driven Workflow. Layer-drift across the channels (different TASK IDs for the same logical unit) is itself a fail-close signature, not a tolerable inconsistency. The four-channel design ensures no single channel can become the silent bypass surface that GHI #553 named.

## The Four Channels

| Channel | Surface | Authoring contract | Discovery mechanism |
|---------|---------|--------------------|--------------------|
| Python `@advances` | Source functions in `src/gzkit/**` | `@advances("TASK-X.Y.Z-NN-MM-PP")` decorator on functions that materially advance the named TASK | Import-time decoration registers `TaskAttributionRecord`; module-level registry queried via `get_task_registry()` (ADR-0.0.64 / OBPI-02) |
| Frontmatter `tasks:` | Structured artifacts (OBPI briefs, ADR packages where applicable) | `tasks: list[str]` YAML frontmatter field listing TASK IDs this artifact advances | YAML parser walks frontmatter; schema enforcement deferred to OBPI-0.0.64-04 (`gz validate --task-envelope-coherence`) |
| Commit trailer | Git commit messages | `Task: TASK-X.Y.Z-NN-MM-PP` trailer in the final paragraph | `parse_task_trailers()` in `gzkit.tasks`; validated by `gz validate --commit-trailers` |
| Ledger `task_id` | Worklog event types in `.gzkit/ledger.jsonl` | Optional `task_id: str | None` field on the eight validator-enforced worklog event types (OBPI-0.0.64-01; additively present on further event types) | JSON deserialization via `gzkit.events`; validator scope per OBPI-04 |

## Convention: Python `@advances`

```python
from gzkit.tasks import advances

@advances("TASK-0.0.64-02-01-01")
def my_function() -> None:
    """Function body unchanged — the decorator is metadata-only."""
    ...
```

**Decoration-time fail-close:**

- Invalid TASK ID format → `ValueError` at import (typos cannot ship)
- Unknown parent REQ → `ValueError` at import (TASK IDs whose `REQ-X.Y.Z-NN-MM` parent isn't in any extracted brief cannot ship)

The validation surface mirrors `@covers`'s precedent: typos that would silently pass at runtime instead block at import.

## Convention: Frontmatter `tasks:`

```yaml
---
id: OBPI-0.0.64-02-advances-decorator-and-discovery-convention
parent: ADR-0.0.64-task-envelope-and-planning-decomposition
tasks:
  - TASK-0.0.64-02-01-01
  - TASK-0.0.64-02-02-01
---
```

The `tasks:` channel is the structured-artifact equivalent of the `@advances` decorator — it declares which TASKs an artifact advances when the artifact itself is the deliverable (vs. when source functions are). Use this channel on briefs and ADR-package frontmatter when the work is documentation-shaped rather than code-shaped.

Schema enforcement for `tasks:` (rejecting malformed TASK IDs and unknown parents) is on the OBPI-0.0.64-04 work surface; this rule documents the channel.

## Convention: Commit trailer

> **Auto-stamped (GHI #731).** `.gzkit/hooks/prepare-commit-msg-task-trailers`
> appends a `Task:` line per in-progress TASK on `src/**`/`tests/**` commits; an
> authored trailer of ANY form suppresses it. Witness status unruled — GHI #731.


```
fix(tasks): wire @advances decorator (GHI #553)

Task: TASK-0.0.64-02-01-01
```

The commit trailer is the freeform fallback for labor that does not produce a Python function or a structured artifact — chore work, sync ceremonies, documentation drift fixes. It is **also mandatory** on any `src/**` or `tests/**` commit (see § Invariant). `gz validate --commit-trailers` enforces this surface.

`parse_task_trailers()` accepts three forms — `.gzkit/rules/tests.md` § TASK-Driven Workflow is the canonical form table; this list is a pointer, not a second authority:

| Form | Use |
|------|-----|
| `TASK-X.Y.Z-NN-MM-PP` | Formal four-tier ID — labor under an OBPI |
| `TASK-<kebab-slug>` **(optional `-#<ghi>`)** | Direct-fix work outside OBPI scope |
| `TASK-<ceremony-slug>` | Ceremony work (e.g. `TASK-gz-git-sync`) |

**The `-#<ghi>` anchor is OPTIONAL.** Append it only when a GHI already exists. **Filing a GHI *to satisfy the trailer* is a moratorium violation** (operator directive 2026-06-01) — it also drags a full `/ghi-author` Step-0 prior-art run into existence for an issue that exists only to feed a string. The regex is explicit about this: `_ANY_TASK_TRAILER_RE` (`src/gzkit/tasks.py:219`) is `[a-z][a-z0-9-]*(?:-#\d+)?`, and its comment names the requirement *"the friction that turned the direct-fix path into a tarpit"*.

## Convention: Ledger `task_id`

The eight validator-enforced worklog event types in `src/gzkit/events.py` (`artifact_edited`, `gate_checked`, `evidence_emitted`, `policy_breach`, `validator_run`, `tool_invoked`, `agent_message`, `lint_run` — the set `gz validate --task-envelope-coherence` signature (a) checks) carry an optional `task_id: str | None = None` field (OBPI-0.0.64-01). The field is additively present on further telemetry/ceremony event types as well, but only these eight are coherence-enforced. Worklog events emitted under an active TASK SHOULD populate this field.

## Subdivision sub-invariant

A single REQ may have multiple TASKs (labor-subdivision via `seq=01`, `seq=02`, …). When work subdivides, each labor unit MUST get its own TASK ID — not a shared coarse-default-bucket TASK. The `seq` component is the subdivision axis; the OBPI pipeline mints `seq=01` per REQ as the coarse-default bucket, and operators/agents must `gz task start --seq next` to subdivide further.

Default-bucket-only OBPIs (every REQ has only `seq=01`) without a `req_atomic: list[str]` exemption in brief frontmatter are themselves a fail-close signature (OBPI-04 validator scope).

## Layer-drift fail-close

When a single logical unit of labor surfaces across multiple channels with different TASK IDs — `@advances` decorator names TASK-A, frontmatter `tasks:` names TASK-B, commit trailer names TASK-C — the divergence IS the signal. The OBPI-04 validator will fail Heavy lane closeouts on layer-drift; Lite lane warns.

## Do Not

- Do not use `@advances` as a comment marker (`# @advances: TASK-...`) — the decorator is the contract; comments have no AST node, no decoration-time validation, no typo defense
- Do not pre-register full TASK IDs in a closed set — TASKs are minted by the pipeline at runtime; validation is via the parent REQ
- Do not coarse-bucket subdivisible labor under a single `seq=01` TASK — subdivision via `seq=02`, `seq=03`, … is the mechanism, not an option
- Do not silently rewrite TASK IDs across channels to "make the validator happy" — layer-drift is the signal, not the defect to suppress

## Related

- ADR-0.0.64-task-envelope-and-planning-decomposition (parent)
- OBPI-0.0.64-01-task-id-worklog-schema-additive (Ledger `task_id` channel)
- OBPI-0.0.64-04-gz-validate-task-envelope-coherence (validator)
- `.gzkit/rules/skill-surface-sync.md` (rule version-discipline convention)
- `src/gzkit/tasks.py` (`@advances`, `TaskAttributionRecord`, registry)
