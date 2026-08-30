---
id: pythonic
paths:
  - "**/*.py"
description: Pythonic standards and idiomatic code contract
---

# Pythonic Standards (Idiomatic Code Contract)

<!-- rule-version: 0.5.1 -->

> **Rule version:** `0.5.1` — diet pass under GHI #921 (operator ruling 2026-08-30, *"do 1 and 2"*): the superseded `0.5.0`–`0.2.1` version chain is lifted to [Rule Version History](../../docs/governance/rule-version-history.md#pythonicmd), restoring the one-sentence shape `skill-surface-sync.md` § Non-negotiable rules #2 requires. Binding rules unchanged; scoped `**/*.py`, this rule loads on every Python edit, so narrative is the most expensive thing it can carry.

## Core Principles

1. **Clarity over cleverness** — explicit, readable, consistent code
2. **Separation of concerns** — isolate IO, transforms, QC, persistence
3. **Typed interfaces** — enforce with `uvx ty check .`
4. **EAFP for IO, LBYL for contracts** — clear error boundaries
5. **Context managers** — for files, DBs, sessions, progress phases
6. **No mutable defaults** — use `None` + factory
7. **Pydantic BaseModel for data** — TypedDict for shapes; see models policy
8. **Explicit exceptions** — typed errors; **no bare `except:` / `except Exception:`** (enforced by ruff `BLE001` on `src/gzkit`; see § Error Handling)
9. **Small units** — <=50 lines/function, <=600 lines/module, <=300 lines/class
10. **No implicit globals** — explicit configuration and state

## Size Limits & Refactoring

**Limits:** Functions <=50 lines | Modules <=600 lines | Classes <=300 lines

> **Unreconciled with the canonical threshold table — read before citing these numbers.**
> `complexity-thresholds.md` § Invariant declares one canonical threshold table and that
> *"a new threshold authority appearing anywhere else is doctrine drift by another name."*
> These three numbers are such an authority, and they **disagree with the table in both
> directions**: `lizard_nloc` blocks at **37.0** (p95) where this rule permits 50;
> `radon_raw_nloc` blocks at **1031.9** (p95) where this rule flags 600 (the table's *warn*
> band is 733.2, so a 700-line module is merely `advise` there and a violation here).
>
> What is actually enforced today:
>
> | Limit | Enforced by | Status |
> |---|---|---|
> | Classes <=300 | `gz validate --class-size` (`code_quality.py`, `limit = 300` hardcoded, waivers in `_CLASS_SIZE_WAIVERS`) | **live gate** — the table carries no class-size metric, so this rule is the only authority |
> | Functions <=50 | nothing | authoring-time guidance only |
> | Modules <=600 | nothing | authoring-time guidance only |
> | *(cyclomatic)* | `.pre-commit-config.yaml` `uvx xenon --max-absolute C` (CC 11–20) | **live gate** — a *third* ceiling, matching neither authority: the table's `radon_cc` blocks at 11.0, so a CC-15 function passes xenon while `block` per the table |
>
> The table's function/module bands have **no consumer**: `complexity_advise.py` is
> `METRIC_KEY = "radon_cc"` with `metrics_checked = 1  # currently only radon_cc`.
> `docs/governance/advisory-rules-audit.md` miscodes this as *"Mechanical | xenon complexity"* —
> xenon measures cyclomatic rank, never line count; that Mechanical claim is unbacked.
>
> Resolving this requires a class-size band the corpus does not yet carry (a distillation pass,
> per `gz-complexity-distill`), so it is **not** a prose fix. Surfaced as Pass A conflict-matrix
> row 11; routed for operator decision. Until then: treat <=300 as binding (it gates), <=50 and
> <=600 as guidance, and cite the table — not this rule — for any threshold claim.

## Imports (PEP 8)

- **Top-level imports only.** Standard library, third-party, then local.
- **No lazy imports** unless required for optional dependencies or cycle avoidance. **(Advisory — PLC0415 is not enabled.)** The ordering half above is enforced by ruff `I`; this half is not. The advisory scorecard claimed it was "partially enforced by ruff PLC0415" — `PL` has never been in `[tool.ruff.lint] select`, so the rule ran nowhere and **138 live violations** stand in `src/gzkit` (measured 2026-08-08). **This posture is ACCEPTED, not deferred (operator ruling 2026-08-08).** The carve-outs named in this very bullet are what most of those sites claim, so separating a legitimate deferred import from a lazy one is a per-site reading, not a switch — and enabling PLC0415 without that pass would either fail the build or bury 138 blanket `noqa`s, a blanket suppression reproducing exactly the blindness the disabled rule already produced. Calling it "deferred" implied a queue that nothing was advancing; the honest state is a measured, disclosed advisory. Re-measured 2026-08-08 at the acceptance: **still 138** (`uv run ruff check src/gzkit --select PLC0415 --statistics`). Reclassify on either a completed per-site pass or an observed instance of a lazy import causing a defect — not on the count moving.

## Error Handling

- Catch specific exceptions, translate to `core.errors`.
- **No bare `except:` / `except Exception:`** outside CLI boundaries.

**Mechanized 2026-08-08 by ruff `BLE001`, after running nowhere for as long as this clause has existed.** `BLE` was absent from `[tool.ruff.lint] select` while the advisory scorecard recorded row 18 as **Mechanical**, "ruff BLE001 enforces" — a rule declared, scored as witnessed, and enforced by nothing. Six live violations sat in `src/gzkit`, one of them behind a `# noqa: BLE0001` typo that suppressed nothing and was undetectable precisely *because* the rule was off: a wrong suppression code is invisible when the rule it names never runs.

Scope is the shipped package. The `per-file-ignores` exclusions are boundary surfaces this clause already exempts by its own "outside CLI boundaries" wording — never-raise SessionStart hooks, orientation scripts, red-phase test scaffolding — plus the generated hook mirrors, which cannot carry an inline `# noqa` because they are emitted from string templates in `src/gzkit/hooks/scripts/`. Inside the package, a genuine boundary catch carries `# noqa: BLE001` with a cited reason; the breadth is justified in place, never assumed.

## Toolchain (Astral)

| Tool         | Role                  | Command                 |
| ------------ | --------------------- | ----------------------- |
| **uv**       | Environment/execution | `uv run` / `uvx`        |
| **ruff**     | Linting/formatting    | `uv run ruff check .`   |
| **ty**       | Static typing         | `uvx ty check .`        |
| **unittest** | Testing               | `uv run -m unittest -q` |

## Type-check suppression syntax (ty — binding)

- **Type-check suppression syntax** — a bracketed `# type: ignore[...]` must name a `ty:`-prefixed code

`ty` skips every code lacking a `ty:` prefix, so an all-foreign directive suppresses nothing while
reading exactly like a suppression (GHI #197). That same skipping lets one comment serve two
checkers: when another tool reads the line, add ty's code rather than deleting the foreign one.

| Form | When |
|------|------|
| `# type: ignore` (bare) | Unconditional; precise narrowing unnecessary |
| `# ty: ignore[<ty-code>]` | Specificity — cite ty's own code (`invalid-assignment`, `unresolved-attribute`, `no-matching-overload`, …) |
| `# type: ignore[ty:<ty-code>]` | Equivalent; only when a `type:`-shaped comment must be kept for another tool |
| `# type: ignore[<foreign-code>, ty:<ty-code>]` | Interop — one comment serving ty and another checker |

Map foreign codes with ty's [mypy/pyright table](https://docs.astral.sh/ty/coming-from-mypy-or-pyright/#mapping-pyrightmypy-rules-to-tyruff-rules); `no-untyped-def`,
`import-untyped`, and `no-any-return` have no ty equivalent, so those markers are deleted rather than
translated. Fail-closed by `gz validate --type-ignores` over `_TYPE_IGNORE_AUDIT_ROOTS`. Background: [Rule Version History](../../docs/governance/rule-version-history.md#pythonicmd).
