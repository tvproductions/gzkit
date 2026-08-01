# CHORE: Module SLOC Cap (Radon)

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `module-sloc-cap-radon`

---

## Overview

Enforce module size against the **one canonical threshold table**
(`.gzkit/rules/complexity-thresholds.json`), metric `radon_raw_nloc`:

| Band | Percentile | SLOC | Trigger |
|---|---|---|---|
| advise | p75 | 311.75 | advisory |
| warn | p90 | 733.2 | advisory |
| **block** | **p95** | **1031.9** | **fails the chore** |

`radon_raw_nloc` is radon's `sloc` field — see
`gzkit.complexity.measurement._run_radon_raw`, which records `entry.get("sloc")`
under that metric key. Measuring any other field would compare a different
quantity than the corpus was measured with.

> **This chore previously declared its own `<=1000` hard cap and `<=600` soft
> cap.** Both were a threshold authority outside the canonical table, which
> `.gzkit/rules/complexity-thresholds.md` § Invariant names directly: *"Downstream
> surfaces … consume the table; none of them owns its own thresholds. A new
> threshold authority appearing anywhere else is doctrine drift by another name."*
> Neither number matched the corpus. The invented 1000 sat between the p90 and p95
> bands, so it failed `cli/parser_governance.py` (1010 SLOC) — a module the corpus
> does not block — while presenting itself as the authority. Repointed 2026-08-01.

### Shrink-only ratchet

Modules already over the block band at the 2026-08-01 cutover are listed in
[`data/module_size_grandfather.json`](../../../data/module_size_grandfather.json)
with the SLOC they carried, and registered in
[`data/waiver_ratchet_registry.json`](../../../data/waiver_ratchet_registry.json)
under ADR-0.0.73 Boundary Invariant #8. The list turns one way only:

| Condition | Result |
|---|---|
| A module over the band, not listed | **fail** — no new over-band modules |
| A listed module that grew | **fail** — an entry is a ceiling, not a licence |
| A listed module now under the band | **fail** — surrender the entry; that is what makes it a ratchet |

Adding an entry to silence a fresh violation is the laundering Boundary
Invariant #8 forbids.

## Policy and Guardrails

- **Lane:** Lite — internal structural refactoring, no external contract changes
- No behavioral changes; public imports via `__init__.py` re-exports
- Split by cohesion, not by arbitrary line count

## Workflow

### 1. Baseline

```bash
uvx radon raw src/ -s -j > .gzkit/chores/module-sloc-cap-radon/proofs/radon-baseline.json
```

### 2. Plan

- Identify modules exceeding 600 SLOC soft cap
- Plan cohesive splits preserving public API

### 3. Implement

Split modules by responsibility. Maintain backwards-compatible imports.

### 4. Validate

```bash
uv run -m unittest -q
uvx radon raw src/ -s -j
```

## Checklist

- [ ] No modules exceed 1000 SLOC hard cap
- [ ] Modules approaching 600 SLOC documented
- [ ] Tests pass unchanged

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run -m unittest -q` | 0 |

## Evidence Commands

```bash
uvx radon raw src/ -s -j > .gzkit/chores/module-sloc-cap-radon/proofs/radon-report.json
```

---

**End of CHORE: Module SLOC Cap (Radon)**
