---
name: gz-adr-promote
persona: main-session
description: Promote a pool ADR into canonical ADR package structure. Use when moving a backlog item (ADR-pool.*) into an active, versioned ADR.
category: adr-lifecycle
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-09-29
metadata:
  skill-version: "1.8.1"
model: sonnet
---

# gz adr promote

## Overview

Turn one pool ADR into a versioned ADR package with one OBPI brief per checklist
item, and record the move in the ledger. `uv run gz adr promote <POOL-ADR>
--semver X.Y.Z --kind feature` (`adr_promote_cmd`,
`src/gzkit/commands/adr_promote.py`; parsing helpers in `adr_promote_utils.py`):

- **refuses before any I/O, exit 1** (`_validate_promotion_kind_semver`): a
  missing `--kind`; `--kind pool` (pool is the source kind); `--kind
  foundation` where the kind is closed (`data/foundation_grandfather.json`
  exists, as in gzkit per ADR-0.34.0), or, where it is open, with a
  non-`0.0.x` semver; `--kind feature` with a `0.0.x` semver;
- **refuses, exit 1, while planning:** a source that is not a pool id, is
  already renamed in the ledger, or already carries `promoted_to:`; an invalid
  `--semver` or `--slug`; a target id already in the ledger or on disk; a pool
  ADR with an empty or missing `## Target Scope`, or with no items to derive;
- derives the target id `ADR-<semver>-<slug>` (slug from `--slug`, else from
  the pool id), the checklist from the pool (see Slug Source Contract), and
  renders the ADR template with status `Proposed` (`--status draft` for
  Draft), `kind:` and `promoted_from:`. It carries `## Intent` (or
  `## Problem Statement`) and `## Decision` into the new ADR and preserves
  `## Target Scope`, `## Non-Goals`, `## Dependencies`, `## Promotion
  Criteria`, `## Inspired By` and `## Notes`. Lane is `--lane`, else the pool's
  `lane:`, else the project `mode`; parent is `--parent`, else the pool's;
- `--dry-run` prints the target, the brief paths and the events it would
  append, and writes nothing. With `--json` it prints only the result payload;
- **otherwise writes** `<paths.adrs>/pre-release/<id>/<id>.md` (`foundation/`
  for an open foundation kind) and `obpis/<OBPI-ID>.md` per checklist item, and
  rewrites the pool file to `status: Superseded` with `promoted_to:` and a
  promoted-on note. It appends `artifact_renamed` (reason `pool_promotion`,
  extras `kind` and `semver`), one `obpi_created` per brief, and an
  `obpi_unparked` for every OBPI a prior demotion parked at this pool id
  (GHI #584);
- **then checks what it wrote**, unless `--force`: brief structure and path
  validity (GHI #419) and template scaffold, exit 1; then the `gz adr evaluate`
  scoring (`evaluate_adr`, no ledger event), exit 3 on any verdict but GO. On
  either failure the files, the Superseded pool file and the ledger events
  stay. Recover by authoring the package and
  re-checking with `uv run gz obpi validate --adr <ID> --authored` and `uv run
  gz adr evaluate <ID>`. Do not re-promote: the recorded rename refuses it, with
  `--force` as well.

It appends no `adr_created`. The promoted ADR inherits the pool id's
`adr_created` through the rename. A pool ADR that was never booked (`gz plan
create --kind pool` books nothing) leaves the promoted ADR without one, and
`gz adr report` (`_warn_orphaned_adrs`) warns that it exists on disk but is not
registered in the ledger.

## Slug Source Contract (GHI #241)

`_promoted_checklist_from_pool` resolves OBPI slugs from the pool ADR in this
order. Author the pool to hit the first path that fits:

1.  **`## Proposed OBPI Decomposition` table (preferred).** A markdown table
    with `Slug` and `Description` columns (a leading `#` column is fine; extra
    columns like `Lane` are ignored; a row whose slug is not kebab-case is
    dropped). The `Slug` column drives the OBPI name;
    the `Description` column becomes the Feature Checklist text.

    ```markdown
    ## Proposed OBPI Decomposition

    | # | Slug | Description | Lane |
    |---|------|-------------|------|
    | 01 | check-pipeline | Implement ordered check pipeline | Lite |
    | 02 | auto-repair-tier | Deterministic auto-repair executor | Lite |
    ```

2.  **`- **slug** — narrative` bullets in `## Target Scope`.** When every
    top-level bullet uses the bold-prefix convention (em dash, en dash or
    hyphen), the bold text becomes the OBPI slug and the narrative becomes the
    checklist text.

    ```markdown
    ## Target Scope

    - **check-pipeline** — Implement ordered check pipeline with Pydantic models
    - **auto-repair-tier** — Deterministic auto-repair executor
    ```

3.  **Legacy narrative-only bullets (deprecated).** Still accepted for
    backward compatibility but emits a deprecation warning on promote. The
    full bullet text becomes both slug source and checklist text, which
    produces long, narrative-leaking OBPI slugs. Migrate to path 1 or 2.

`## Target Scope` is required on every path, table or not: it must be non-empty
and is preserved verbatim as the promoted ADR's narrative scope. Bullets nested
under `### H3` subsections within it are **ignored** by paths 2 and 3; only
direct top-level bullets count as scope. A pool ADR can therefore decompose
under a clean table (path 1) while keeping rich prose in a
`### Detailed specification` subsection below.

## Workflow

1.  **Identify the pool ADR** (e.g. `ADR-pool.ai-runtime-foundations`) and read
    it through. Check it against `AGENTS.md` § Architectural Boundaries and the
    active campaign plan, which sets release prioritization.
2.  **Choose the target version and kind.** `--kind feature` in gzkit, with the
    semver the ascending feature-ADR order allows (the work-order ruling carried
    in `gz-obpi-pipeline`). In an adopter project where `foundation` is open, it
    takes a `0.0.x` semver; resolve the boundary with the invariance test,
    *"Foundation = without it, we wouldn't be doing the project"*
    (the hexagonal-ports lens: ports point to invariance; adapters are features),
    per
    `docs/user/concepts/foundation-feature-invariance-test.md`.
3.  **Decompose in the pool ADR, before promoting.** Promotion creates one
    checklist item and one brief per derived scope item, 1:1, and fits the
    scorecard to that count (`_promotion_scorecard`). The decomposition decision
    is therefore the pool's table or bullets. Size it with
    `docs/governance/GovZero/obpi-decomposition-matrix.md`: the Rule of Three
    baseline (which the doc sets for heavy-lane ADRs), then the Matrix of Four
    overlay (Single-Narrative, Testability Ceiling, State Anchor, Surface
    Boundary). A unit that violates a principle is split further.
4.  **Preview:** `uv run gz adr promote <POOL-ADR> --semver <X.Y.Z> --kind
    feature --dry-run`. Check the target id, the brief slugs and any legacy-bullet
    warning.
5.  **Promote:** the same command without `--dry-run`. If the post-write checks
    exit 1 or 3, the promotion stands: author the retained package and run the
    two re-check commands the output names.
6.  **Book the ADR if the pool never was:** `uv run gz register-adrs
    <NEW-ADR-ID>` appends `adr_created` when the promoted id has none, and
    reports nothing to register when the rename carried one over.
7.  **Verify:** the ADR under `pre-release/` (or `foundation/`), one brief per
    checklist item under its `obpis/`, the pool file `status: Superseded` with
    `promoted_to:`, and in the ledger the `artifact_renamed`, the
    `obpi_created` events and an `adr_created` that resolves to the new id
    (`uv run gz adr status <NEW-ADR-ID>`).

## Options

- `--semver` (required): the target version, `X.Y.Z`.
- `--kind` (required, no default): `feature`; `pool` is always refused;
  `foundation` only where the kind is open.
- `--slug`: target slug override (defaults to the slug derived from the pool id).
- `--title`: target title (defaults to the pool H1 title).
- `--parent`: parent override (defaults to the pool's `parent:`).
- `--lane`: `lite` or `heavy` (defaults to the pool's `lane:`, then the project `mode`).
- `--status`: `proposed` (default) or `draft`.
- `--dry-run`, `--json`: preview; structured result payload.
- `--force`: skip the post-write structure, scaffold and evaluation checks. It
  does not bypass the kind/semver binding and works only on the first
  application.

## Common Rationalizations

These thoughts mean STOP — you are about to violate the architectural boundary:

| Thought | Reality |
|---------|---------|
| "The pool ADR doesn't have actionable Target Scope bullets, but I know what it means" | Promotion is fail-closed without actionable scope. Your interpretation is not a substitute. Refine the pool ADR first. |
| "The Rule of Three feels like overengineering for this small ADR" | The decomposition protocol exists because ADRs that skip it produce briefs that drift during implementation. Small now, sprawling later. |
| "I'll add OBPIs after the promote runs" | Promotion fixes the checklist and briefs 1:1 from the pool's decomposition. Change the pool's table or bullets before promoting, not the promoted package after it. |
| "The post-promote check failed — I'll promote again with `--force`" | The promotion is already applied and recorded; the rename refuses a second run. Author the retained briefs and re-check them. |
| "I can skip `--dry-run`, I know the layout" | `--dry-run` costs nothing. A wrong-version promotion is undone only by `gz adr demote`, which deletes the package. |
| "The original pool ADR was written years ago — it doesn't need re-evaluation" | Pool ADRs are intent. If the intent is years old, the foundation it assumed may not exist. Re-read `AGENTS.md` § Architectural Boundaries before promoting. |

## Red Flags

- Promoting a pool ADR that `AGENTS.md` § Architectural Boundaries rules out
- A target semver ahead of the lowest feature ADR with unlanded OBPIs
- Resulting Feature Checklist count differs from generated OBPI brief count
- Pool file or ledger edited by hand to "finish" a promotion
- Re-running promotion after its post-write checks failed
- No `adr_created` resolving to the promoted id after step 6
- Decomposition Protocol skipped or applied superficially

## Demote (inverse lifecycle)

`uv run gz adr demote <ADR-ID> --ghi <N>` (`adr_demote_cmd`,
`src/gzkit/commands/adr_demote.py`) reverses a promotion. It turns a feature or
foundation ADR into `ADR-pool.<slug>`, strips `kind`, `semver`, `date` and
`promoted_from`, **deletes the source package directory** (briefs and closeout
form), appends `artifact_renamed` (reason `pool_demotion`) and parks each child
OBPI (`obpi_parked`), which a later re-promotion unparks. It exits 3 when
another ADR names this one as parent or when `@covers` decorators under
`tests/` name REQs from the deleted briefs (GHI #773); `--force` overrides both.

A promote/demote round trip always collides on the retained pool file, which
fails by default. Choose `--on-collision take-demoted` when the ADR was worked
after promotion, or `keep-pool` when it never diverged from its intake
(GHI #775).

```bash
uv run gz adr demote ADR-0.27.0-arb-receipt-system-absorption --ghi 520 --on-collision take-demoted --dry-run
uv run gz adr demote ADR-0.27.0-arb-receipt-system-absorption --ghi 520 --on-collision take-demoted
```

## Example

```bash
uv run gz adr promote ADR-pool.harness-fitness-report --semver 0.60.0 --kind feature --dry-run
uv run gz adr promote ADR-pool.harness-fitness-report --semver 0.60.0 --kind feature
uv run gz register-adrs ADR-0.60.0-harness-fitness-report
uv run gz adr status ADR-0.60.0-harness-fitness-report
```
