# Config-derivation census — 2026-09-20

> **This is a dated record.** Every figure below was observed on the 2026-09-20
> tree at `f3c1e446c`. The values are ILLUSTRATIVE, never authoritative
> (`AGENTS.md` § Governance doctrine surfaces). The authority is the script:
> re-run [`config-derivation-2026-09-20-evidence/census.py`](config-derivation-2026-09-20-evidence/census.py)
> rather than trusting a number transcribed here. It carries no literals from
> this date, so it reports whatever tree it is run against.

## The question

Operator, 2026-09-20: *"how many other arbitrary and random rules do we have
lingering? i've said it many times... we lack strong central config management in
gzkit... its bad."*

Occasioned by `SKILL_BODY_MAX_LINES = 300` (GHI #1065), whose only provenance is a
prose table that arrived in a bulk sync commit on 2026-04-25 and was mechanized
five months later without being derived.

## What was already built, and what it answers

GHI #929 (*"44 registries, 93 readers, no owner, loader, or coherence gate"*,
closed 2026-09-02) produced `data/config_registry.json`. It works, and it is not
the gap: it fail-closes on any top-level data registry that is neither declared
there nor matched by the waiver ratchet's globs, and it **verifies** each declared
owner actually references the file rather than trusting an asserted list.

It answers *who reads this value*. Nothing asks *where this value came from*. The
**owner** half of #929's title shipped; the **loader** and **coherence** halves did
not, and derivation was never in its scope.

## Measured 2026-09-20

**`data/*.json` — 45 registries**

| Provenance | Count |
|---|---|
| Cites an authority (`docs/**.md`, `ADR-`, `GHI #N`, operator ruling) | 26 |
| No provenance field at all | 12 |
| Prose only, citing nothing | 2 |
| Bare array — structurally cannot carry provenance | 5 |
| **No traceable derivation** | **19 of 45 (42%)** |

The sharpest instances are the registries named for the thing they fail to source:

```
audit_thresholds.json         {"max_covers_backfill_commits": 3, "max_covers_backfill_days": 7}
eval_feedback_thresholds.json {"low_score_threshold": 3.0, "red_team_count_threshold": 3,
                               "cluster_min_recurrence": 3}
```

Five enforced magic numbers, zero provenance between them.

**`src/gzkit/**` — 56 module-level numeric policy constants.**

`config_registry.json`'s `_doc` declares the registry pair *"EXHAUSTIVE over
data/*.json"*. A threshold living in a Python module body is therefore not merely
unsourced; it is **unreachable** by the gate built to catch unsourced config.
`SKILL_BODY_MAX_LINES` is one of 56.

**Five policy names with two or more homes, two of them disagreeing:**

| Name | Homes | Values |
|---|---|---|
| `DEFAULT_MAX_OUTPUT_CHARS` | `arb/red_reporter.py`, `arb/step_reporter.py` | **4000 / 8000** |
| `DEFAULT_TIMEOUT_SECONDS` | `complexity/advisor/config.py`, `justify/evidence.py` | **30.0 / 3.0** |
| `DEFAULT_MAX_REVIEW_AGE_DAYS` | `skills_audit.py`, `sync_skills.py` | 90 / 90 |
| `DEFAULT_TIMEOUT_S` | `complexity/advisor/timeout.py`, `hooks/install_complexity_advisor.py` | 30.0 / 30.0 |
| `GIT_TIMEOUT_S` | `check_fingerprint.py`, `red_witness.py` | 120 / 120 |

A disagreement here means **nothing reconciles these two values**, never that one
is wrong — the two contexts may genuinely warrant different numbers. The three
that agree are the more direct finding: a single concept with two independent
homes, held equal today by nothing but coincidence.

Separately, `eval_feedback_thresholds.json` holds `cluster_min_recurrence: 3` and
`low_score_threshold: 3.0` while `chores/eval_feedback_cluster_lib.py` holds
`_DEFAULT_CLUSTER_MIN_RECURRENCE = 3` and `_DEFAULT_SCORE_THRESHOLD = 3.0`. The
name-grouping above does not catch this shape — a JSON key duplicated as a Python
default — so the true duplication count is a **lower bound**.

## What the census does not claim

- It does not claim the 19 unsourced registries hold wrong values. It claims no
  reader can tell a deliberate choice from an inherited accident.
- It does not claim the 56 constants all belong in config. The name pattern is
  broad and the population includes implementation details; a reader judges rows.
- It does not propose an architecture. `config_registry.json` proves the
  declaration-plus-verified-consumer shape works for ownership; whether derivation
  wants the same shape, a required field, or something else is a design question
  this record deliberately leaves open.

## Class

This is the mirror of the `doctrine-declared-without-mechanism` family the campaign
tracks at Movement C: there, doctrine exists with no mechanism; here, mechanisms
enforce with no doctrine behind their numbers. That mirror is currently tracked by
no campaign box and no advisory-scorecard row.
