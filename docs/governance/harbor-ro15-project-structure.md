<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# RP-15 specification — maximal Astral project structure

> Named `RO-15` until 2026-11-03; `RP-15` replaces it in live text and `RO-15` stays its alias (contract § Rulings of 2026-11-03). The dated rulings below keep the name they were written with.


**2026-11-01. Status: scope, the brownfield reach and placement ruled; tranche 6 owner ruled 2026-11-12, tranches 1 to 5 owner open; tranche 6 started 2026-11-12.** Operator: **g0**. Repair order of the [harbor pilotage contract](harbor-pilotage-candidate-2026-10-15.md), added by amendment. It follows [RO-9](harbor-ro9-astral-toolchain.md), which aligned the toolchain and left the structure of a project unwitnessed.

## Scope

gzkit and every project it governs follow [uv's project model](https://docs.astral.sh/uv/concepts/projects/) to the maximum, as [`tvproductions/gz-skills-first-starter`](https://github.com/tvproductions/gz-skills-first-starter) does. The authority is Astral's documentation. The starter is the worked reference: its alignment contract, its acceptance rows A01 to A18 and its worked migrations show what proof of conformance looks like.

## Rulings

1. **Project structure is a repair order** (operator, verbatim: *"the reason I wanted you to look at that starter is because it adopts/assumes maximal python project structuring via astral's recommended best practices. I consider that RO worthy."*).
2. **The standard** (operator, verbatim: *"maxx: <https://docs.astral.sh/uv/concepts/projects/>"* and *"gz-starter maximizes this, we should too/"*).
3. **Brownfield reach.** Put to the operator: report then prove; migrate automatically; refuse until conformant. Operator, by selection: *"Report, then prove (Recommended)"*. `gz init` never breaks a working build and never refactors a project's code. It inventories every gap, and adoption stays incomplete until a governed migration passes the structure rules. An old layout needs an evidenced exception.

4. **Placement.** Put to the operator: immediately before RO-4, or straight after RO-14's tranche 1. Operator, verbatim: *"agree"* to the first, so the kit work is uninterrupted and the sea trial's released wheel proves the structure.

## The gap, measured 2026-11-01

Read from gzkit's tree, a fresh `gz init` project and a small flat setuptools project, each in a scratch directory.

| uv's guidance | gzkit | A fresh scaffold | An existing project after `gz init` |
| --- | --- | --- | --- |
| `pyproject.toml`, `uv.lock` committed, `.venv` ignored | conforms | conforms | lock written; no rule reads the rest |
| A packaged `src/<name>/` for commands, distribution or a library, with `py.typed` on a library | conforms | conforms | flat layout unchanged and no finding |
| `uv_build` by default | conforms | conforms | setuptools held in the baseline |
| Commands in `[project.scripts]`, run through the project environment | conforms, but 10 loose scripts carry no inline metadata and 9 files insert into `sys.path` | `gz` is not in the lock: `uv run gz` resolved to `~/.local/bin/gz` | not read |
| `uv.lock` and `requirements.txt` not kept together | conforms | conforms | `requirements.txt` held in the baseline |
| Development tools in `[dependency-groups]`, the legacy field retired | conforms | conforms | held in the baseline; the legacy field is not read |
| A deployment does not depend on the source tree (`--no-editable`) | clean-install proof not yet confirmed | not read | not read |

The defect that makes this blocking: `gz init` adds `data/` and `design/` beside a flat package, setuptools discovery then refuses *"Multiple top-level packages"*, and `uv build` moved from exit 0 to exit 2. `gz validate --astral-discipline` has no rule about a project's structure, so the seven violations that project carried went into its baseline and the scope passed.

## Tranches

| # | What lands |
| --- | --- |
| 1 | The witness: structure rules in `gz validate --astral-discipline`, on the shrink-only baseline. A `src/` package, a declared backend, commands in `[project.scripts]`, `py.typed` on a library, a separate `tests/`, no `sys.path` injection, no competing `uv.toml`, `ruff.toml` or `ty.toml`, no `managed = false`, no `tool.uv.dev-dependencies`. |
| 2 | gzkit's own tree: the `sys.path` insertions removed, each loose script an entry point or a PEP 723 script. |
| 3 | The scaffold: `gz` locked in the project, so `uv run gz` never falls through to `PATH`. |
| 4 | Clean-install proof: the wheel installed in a fresh environment outside the checkout, with import origins, the CLI and packaged data read (A12), and `--no-editable` behaviour. |
| 5 | Brownfield: `gz init` leaves a working build working, reports every gap, and a fixture migrates to conformance under the rulings above. |
| 6 | The hexagon's structures (change order of 2026-11-12, below): the kernel package, the hexagonal architecture system package map, and the dependency-rules test widened to every mapped region. |

## Kept from gzkit's rulings

- uv stays a floor, never an exact pin (GHI #1283).
- A fact is declared once where Astral's tools read it (RO-9), where the starter requires several statements to agree.
- Ruff stays at `ALL` with preview (RO-9). The starter's rule-selection text is outside this order.

## Open points

1. Who lands tranches 1 to 5. Tranche 6 is landed by the main session, which the operator chose on 2026-11-12 in answer to *which work moves next* (verbatim: *"RP-15 tranche 6"*).
2. Whether a scaffold's `.python-version` takes an exact patch, as gzkit's own does.
3. Whether `build-constraint-dependencies` carries hashes, which uv's build page describes.

## Change order of 2026-11-12 — the hexagon's structures (tranche 6)

**Authority.** The R&D run [`hexagonal-specification`](../rnd/hexagonal-specification.md), signed off funded on
2026-11-11, ruled that the hexagon's structures land in this drydock and gzkit's use cases migrate into them after
return to service (operator, verbatim: *"Yes"*, then *"Ruling stands"*). The order that first carried the hexagonal
direction, RP-9, closed on 2026-10-29. Placed here by the operator, verbatim: *"A: RP-15 plus RP-7"*: the structures
on this order, the test gates on RP-7's placement (contract § Rulings of 2026-11-12). Specification:
[`docs/governance/hexagonal-architecture.md`](hexagonal-architecture.md).

**What tranche 6 lands.**

1. **The kernel package**, a sibling of `core/`, importing stdlib and Pydantic only and holding no gzkit governance
   concept: the bases `ValueObject`, `Entity`, `DomainEvent`, `Command`, `Query` and `Dto` (frozen Pydantic models;
   `create(...) -> Self | ValidationErrors` where the specification gives one), the error-value types, and the
   command and query buses (a startup registry that fails fast on a missing handler).
2. **The hexagonal architecture system package map** in `pyproject.toml` `[tool.py-gzkit]`, naming each top-level
   package's part of the hexagon. Its approval as a classic decision record (the house-style run's ruling) waits on
   RP-6's identity crossover; until then the map lands as this tranche's draft and is flagged as such.
3. **The dependency rules, widened.** `tests/policy/test_import_boundaries.py` reads every region's row from the map
   and enforces the specification's per-region table, with the base-to-region cross-check (each kernel base
   subclassed only in its region) and the Protocol-and-name check (each handler inherits exactly one use-case
   `Protocol` and takes its name). It runs on a per-change gate, which clears the mechanism of RP-7's finding F22
   (that line stays RP-7's), and ships in the kernel for adopters to run.

**Rulings while landing it (2026-11-12).**

- **The checker lives in the kernel.** The checker is a stdlib `ast` module inside the kernel.
  `tests/policy/test_import_boundaries.py` imports it, and the policy-test isolation check is narrowed to admit the
  kernel alone, since the kernel holds no application code. Put to the operator: (A) checker in the kernel, isolation
  narrowed; (B) a copy in each place; (C) checker in the test only until `gz init` scaffolds the hexagon. Operator,
  verbatim: *"A: kernel, narrow isolation"*.
- **The kernel's name is a draft.** The run held the name open to diamond 2. The package lands as `gzkit.kernel`,
  flagged as a draft name, like the package map.
- **Unmapped code is a finding.** Put to the operator: (A) every package or module the map does not name is a
  finding, held with today's out-of-region imports in one shrink-only baseline; (B) a `legacy` region the checker
  skips. Operator, verbatim: *"A: unmapped is a finding"*.

**Ruling after the review (2026-11-13).**

- **#1267 is held to migration.** The independent review found the checker cannot see #1267's edge while `core/` is
  unmapped. Put to the operator, measured first (mapping the eight `core/*.py` modules into the domain gives seven
  import findings): (A) hold the placement to migration, amend #1267's closure contract to the current canon's
  `core/domain`, and grade it due by the first use case migrated; (B) map today's `core/` modules into the domain now;
  (C) hold the placement and build #1267's transitive check on today's `core/`. Operator, verbatim: *"A: hold to
  migration"*. The contract's § List of discrepancies carries #1267 on its own line.

**Landed 2026-11-12.**

| Item | Where | Commit |
| --- | --- | --- |
| 1. The kernel | `src/gzkit/kernel/`: the bases and error values (`bases.py`, `errors.py`), the buses (`buses.py`) | `05e4a6eb4`, `c0e9e9005` |
| 2. The package map | `pyproject.toml` `[tool.py-gzkit.hexagon]`, a draft | `dfa669511` |
| 3. The dependency rules, widened | `gzkit.kernel.dependency_checker`; `tests/policy/test_import_boundaries.py`; `gz validate --hexagon-dependencies` in the default tier; the baseline `data/hexagon_dependency_baseline.json` (177 findings: 161 unmapped, 16 imports from `gzkit.cli`) | `dfa669511`, `5a6ec7ac0` |

The witness reads *in place and only shrinking*: the controls `NC:hexagon-dependencies` (a planted out-of-region
import) and `NC:hexagon-dependencies-baselined` (the baseline admits a held finding) pass, and the checker's unit
tests plant an `Entity` outside `core/domain` and a handler with no use-case `Protocol`.

**Mode contract** (`.gzkit/rules/mode-contract.md`), stated here until RP-13 builds the declaration shapes.

| Control | Operational | Hangar | Drydock | MEL entry | Self-test |
| --- | --- | --- | --- | --- | --- |
| `gz validate --hexagon-dependencies` | on (exit 3) | advisory, demoted by the MX checkpoint | advisory, demoted by the MX checkpoint | (M) none needed: an advisory run still prints every finding; (O) a new finding can land while the hangar is open; placard: the `[MX advisory]` line; restore: the exit re-run at full strength; accepted state: findings no more than the baseline holds | `NC:hexagon-dependencies` and `NC:hexagon-dependencies-baselined`, run on every `gz check` by its *Enforcement floor* step, the enforcement-claim meta-validator, pinned critical so it never demotes in the hangar |
| `tests/policy/test_import_boundaries.py` ratchet | on | on: a unit test has no MX level | on | none: it never stands down | the planted-baseline check, re-run 2026-11-12: one entry removed and one stale entry added each failed |

**Not in tranche 6.** Moving gzkit's modules into the regions (each use case migrates after return to service, the
run's row 1); `gz init` scaffolding the hexagon (a row 1 work package after return to service); the test-discipline
gates (RP-7's change order of 2026-11-12).

**Witness.** The kernel's unit tests; controls showing the widened checker refuses a planted out-of-region import, an
`Entity` outside `core/domain`, and a handler with no use-case `Protocol`; the checker on a per-change gate. Today's
violations enter a **shrink-only baseline**, because gzkit's code migrates only after return to service: at exit the
witness reads *in place and only shrinking*, not zero. These checks are their own validator, outside
`--astral-discipline`'s structure rules, so § Exit item 13 still reads zero on those alone. Each new check declares its
two-way mode contract in its design (`.gzkit/rules/mode-contract.md`).

**Grade.** Blocks return to service, by the timing ruling.

## Witness

`gz validate --astral-discipline` reads zero on the structure rules for gzkit and a freshly scaffolded project, and a brownfield fixture reaches conformance with its build intact (§ Exit item 13).
