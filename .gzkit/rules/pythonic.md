---
id: pythonic
paths:
  - "**/*.py"
description: Pythonic standards and idiomatic code contract
---

# Pythonic Standards (Idiomatic Code Contract)

<!-- rule-version: 0.7.0 -->

> **Rule version:** `0.7.0` — principle 9 and § Size Limits cite the canonical threshold table for function and module size and keep <=300 lines for classes (RP-7 held ruling H2, operator, 2026-11-13: *"A: Cite the table"*); prior banners in [Rule Version History](../../docs/governance/rule-version-history.md#pythonicmd).

## Core Principles

1. **Clarity over cleverness** — explicit, readable, consistent code
2. **Separation of concerns** — isolate IO, transforms, QC, persistence
3. **Typed interfaces** — enforce with `uv run ty check .`
4. **EAFP for IO, LBYL for contracts** — clear error boundaries
5. **Context managers** — for files, DBs, sessions, progress phases
6. **No mutable defaults** — use `None` + factory
7. **Pydantic BaseModel for data** — TypedDict for shapes; see models policy
8. **Explicit exceptions** — typed errors; **no bare `except:` / `except Exception:`** (enforced by ruff `BLE001` on `src/gzkit`; see § Error Handling)
9. **Small units** — function and module size by the canonical threshold table (§ Size Limits); <=300 lines/class
10. **No implicit globals** — explicit configuration and state

## Size Limits & Refactoring

**Function and module size are the canonical threshold table's**, never this rule's: the `lizard_nloc` and
`lizard_file_nloc` bands of `.gzkit/rules/complexity-thresholds.json`, read through `complexity-thresholds.md`.
**Classes <=300 lines** stays the one size limit this rule owns, because the table carries no class metric
(operator, 2026-11-13, RP-7 held ruling H2: *"A: Cite the table"*). Cite the table, never a number copied from it.

| Limit | Enforced by | Status |
|---|---|---|
| Classes <=300 | `gz validate --class-size` (`code_quality.py`, `limit = 300` hardcoded, waivers in `_CLASS_SIZE_WAIVERS`) | **live gate** |
| Function size (`lizard_nloc`) | nothing: `complexity_advise.py` reads `lizard_ccn` alone (`gzkit.complexity.functions.METRIC_KEY`) | the band has no consumer; authoring-time guidance |
| Module size (`lizard_file_nloc`) | `gz check`'s "Module size" step runs `.gzkit/chores/module-sloc-cap-radon/check_module_size.py` over `src/` against the shrink-only `data/module_size_grandfather.json` | **live gate** on the table's `block` band |
| *(cyclomatic)* | `gz validate --complexity-ceiling` and Ruff `C901`, both at `[tool.ruff.lint.mccabe] max-complexity` (each function, module mean and overall mean CC <=20); cognitive complexity by the same gate, scored by gzkit over CPython's `ast` at `.gzkit.json`'s `complexity.cognitive_ceiling` (15, held by the shrink-only `data/cognitive_complexity_baseline.json`) | **live gate** — a *third* ceiling, matching neither authority: the table's `lizard_ccn` blocks at 11.0, so a CC-15 function passes the ceiling while `block` per the table |

## Imports (PEP 8)

- **Top-level imports only.** Standard library, third-party, then local.
- **No lazy imports** unless required for optional dependencies or cycle avoidance. **(PLC0415 runs under Ruff `ALL` since 2026-10-23; scorecard row 23 is Promotable until a control plants a lazy import.)** The ordering half above is enforced by ruff `I`, and this half by PLC0415, which RO-9 tranche 4 selected with every other Ruff rule (operator rulings 2026-10-23: a keyed shrink-ratchet baseline, *"b"*, counted and run by gzkit). The sites that predate it are held per file in `data/ruff_baseline.json`, so a new lazy import fails `uv run gz lint` while the held ones await the per-site reading the 2026-08-08 acceptance described: the carve-outs named in this bullet are what most of them claim, and a legitimate deferred import carries a `# noqa: PLC0415` naming its carve-out rather than a blanket suppression. The acceptance of 2026-08-08 (138 sites, then unselected) is recorded in [Rule Version History](../../docs/governance/rule-version-history.md#pythonicmd).
- **Annotations are deferred (Python 3.14, PEP 649 and 749).** New code writes annotations unquoted and without `from __future__ import annotations`, PEP 563's stringizing form, which 3.14's deferred evaluation supersedes and PEP 749 plans to deprecate. An import that only an annotation needs sits at the top level under `if TYPE_CHECKING:`, never in a function body, so the cycle-avoidance carve-out above covers runtime cycles only. A Pydantic model's field types are evaluated when the class is built, so they stay runtime imports. Annotations are read with `annotationlib.get_annotations`, never from a class `__dict__` (RUF063). `lazy import` (PEP 810) is Python 3.15, not 3.14, so a carve-out above is still a function-local import. **(Ruff `TID251` refuses the PEP 563 import through a `banned-api` entry in `pyproject.toml`, which landed once no module carried one; the dated evidence scripts keep theirs under a per-file exception. `gz validate --astral-discipline` refuses a 3.14 floor whose Ruff config drops the entry, so scorecard row 23b is Mechanical.)**

## Error Handling

- **Inside the walls, expected failures are values.** In the domain and the handlers, an expected failure is a member of a closed result union (a handler's variants), handled exhaustively under ty; no `GzkitError` is raised there (`docs/governance/hexagonal-architecture.md` § Values, entities and storage). Advisory until the hexagon's packages exist; today's code predates them.
- **Outside the walls, translate to the `GzkitError` hierarchy.** Adapters and the configurator catch specific exceptions and translate them: a driving adapter turns a returned error into a `GzkitError`, an exit code and a message through an exhaustive `match`; a driven adapter turns an infrastructure failure into a returned error, or raises for a fault. `GzkitError` lives in `gzkit.core.exceptions` today, inside `core/`, and moves outside the walls under the run's row 5 programme.
- **A fault is not caught inside.** A defect or an exhausted resource may surface inside as an exception; it propagates to the boundary uncaught.
- **No bare `except:` / `except Exception:`** outside CLI boundaries.

**Mechanized 2026-08-08 by ruff `BLE001`, after running nowhere for as long as this clause has existed.** `BLE` was absent from `[tool.ruff.lint] select` while the advisory scorecard recorded row 18 as **Mechanical**, "ruff BLE001 enforces" — a rule declared, scored as witnessed, and enforced by nothing. Six live violations sat in `src/gzkit`, one of them behind a `# noqa: BLE0001` typo that suppressed nothing and was undetectable precisely *because* the rule was off: a wrong suppression code is invisible when the rule it names never runs.

Scope is the shipped package. The `per-file-ignores` exclusions are boundary surfaces this clause already exempts by its own "outside CLI boundaries" wording — never-raise SessionStart hooks, orientation scripts, red-phase test scaffolding — plus the generated hook mirrors, which cannot carry an inline `# noqa` because they are emitted from string templates in `src/gzkit/hooks/scripts/`. Inside the package, a genuine boundary catch carries `# noqa: BLE001` with a cited reason; the breadth is justified in place, never assumed.

## Toolchain (Astral)

| Tool         | Role                  | Command                 |
| ------------ | --------------------- | ----------------------- |
| **uv**       | Environment/execution | `uv run` / `uvx`        |
| **ruff**     | Linting (every rule, against `data/ruff_baseline.json`)/formatting | `uv run gz lint` |
| **ty**       | Static typing         | `uv run ty check .`     |
| **unittest** | Testing               | `uv run gz test` |

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
