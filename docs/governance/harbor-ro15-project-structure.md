<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# RO-15 specification — maximal Astral project structure

**2026-11-01. Status: scope and the brownfield reach ruled; placement and tranche owner open; no tranche started.** Operator: **g0**. Repair order of the [harbor pilotage contract](harbor-pilotage-candidate-2026-10-15.md), added by amendment. It follows [RO-9](harbor-ro9-astral-toolchain.md), which aligned the toolchain and left the structure of a project unwitnessed.

## Scope

gzkit and every project it governs follow [uv's project model](https://docs.astral.sh/uv/concepts/projects/) to the maximum, as [`tvproductions/gz-skills-first-starter`](https://github.com/tvproductions/gz-skills-first-starter) does. The authority is Astral's documentation. The starter is the worked reference: its alignment contract, its acceptance rows A01 to A18 and its worked migrations show what proof of conformance looks like.

## Rulings

1. **Project structure is a repair order** (operator, verbatim: *"the reason I wanted you to look at that starter is because it adopts/assumes maximal python project structuring via astral's recommended best practices. I consider that RO worthy."*).
2. **The standard** (operator, verbatim: *"maxx: <https://docs.astral.sh/uv/concepts/projects/>"* and *"gz-starter maximizes this, we should too/"*).
3. **Brownfield reach.** Put to the operator: report then prove; migrate automatically; refuse until conformant. Operator, by selection: *"Report, then prove (Recommended)"*. `gz init` never breaks a working build and never refactors a project's code. It inventories every gap, and adoption stays incomplete until a governed migration passes the structure rules. An old layout needs an evidenced exception.

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

## Kept from gzkit's rulings

- uv stays a floor, never an exact pin (GHI #1283).
- A fact is declared once where Astral's tools read it (RO-9), where the starter requires several statements to agree.
- Ruff stays at `ALL` with preview (RO-9). The starter's rule-selection text is outside this order.

## Open points

1. Placement. Recommended: immediately before RO-4, so the kit work continues and the sea trial's released wheel proves the structure.
2. Who lands the tranches.
3. Whether a scaffold's `.python-version` takes an exact patch, as gzkit's own does.
4. Whether `build-constraint-dependencies` carries hashes, which uv's build page describes.

## Witness

`gz validate --astral-discipline` reads zero on the structure rules for gzkit and a freshly scaffolded project, and a brownfield fixture reaches conformance with its build intact (§ Exit item 13).
