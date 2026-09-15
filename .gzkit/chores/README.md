# Chores Package — Agent Contract

**STOP. Read this entire file before authoring or modifying any chore.**

This directory is the **canonical, packaged source** of gzkit chores
(`src/gzkit/chores/`). It ships in the wheel and is discoverable at runtime via
`importlib.resources.files("gzkit.chores")`. Project repositories receive
project-local overlays at `.gzkit/chores/<slug>/`; canonical templates here are
read-only at runtime.

---

## Two-Surface Layout (ADR-0.0.21)

| Surface | Path | Role | Shipped in wheel? |
|---------|------|------|-------------------|
| Canonical (package) | `src/gzkit/chores/<slug>/` | Authoritative templates and registry | **Yes** |
| Project overlay | `.gzkit/chores/<slug>/` | Project-local copies + execution evidence (`proofs/`) | No |

`gz chores` resolves each slug **project-first → package-fallback**: it looks
under `<project_root>/.gzkit/chores/<slug>/` first; if that path is absent or
incomplete, it falls back to the canonical package resource. The same order
applies to the `registry.json` file (REQ-0.0.21-04-05).

`gz chores list --explain` prints one row per chore labeling the resolution
source as `project`, `package`, or `missing`.

**`proofs/` is always project-local, never canonical.** Canonical templates
under `src/gzkit/chores/<slug>/` MUST NOT ship `proofs/` content. Execution
evidence is generated at run time under `.gzkit/chores/<slug>/proofs/`.

---

## Slug Directory Contract

Each subdirectory (canonical OR project overlay) is a self-contained chore
package containing:

| File | Purpose | Required |
|------|---------|----------|
| `CHORE.md` | Definition, workflow, acceptance criteria | Yes |
| `acceptance.json` | Machine-readable criteria for automation | Yes |
| `README.md` | Human-readable summary | Yes |
| `proofs/` | Execution evidence directory (project-local only) | Yes (project-local) |

The package surface ships `CHORE.md`, `acceptance.json`, and `README.md` for
every canonical slug. `proofs/` is never canonical.

---

## MANDATORY: Consult Before Acting

Before executing or modifying any chore, read:

1. **The chore's `CHORE.md`** — Contains the authoritative procedure
2. **The registry** at `src/gzkit/chores/registry.json` (canonical) — for
   discovery; `gz chores list` is the operator-facing surface

---

## Chore Execution Protocol

### Step 1: Discover and read the CHORE.md

```bash
uv run gz chores list --explain
uv run gz chores show <chore_slug>
```

The `--explain` flag tells you whether each slug resolves from `project`,
`package`, or is `missing`.

### Step 2: Dry-run criteria

```bash
uv run gz chores advise <chore_slug>
```

### Step 3: Execute and log

```bash
uv run gz chores run <chore_slug>
```

This validates acceptance criteria and writes a dated log entry to
`.gzkit/chores/<slug>/proofs/CHORE-LOG.md`. Per-slug evidence is project-local.

### Step 4: Audit log presence

```bash
uv run gz chores audit --all
```

---

## Health Check and Layout Discipline

### `gz chores doctor` — Restore canonical scaffold (REQ-0.0.21-09)

```bash
uv run gz chores doctor                 # Repair missing canonical files
uv run gz chores doctor --dry-run       # Report-only; no file changes
uv run gz chores doctor --json          # One JSON record per slug
```

`doctor` re-creates any missing canonical file (`CHORE.md`, `acceptance.json`,
`README.md`) inside `.gzkit/chores/<slug>/` from the package source, byte-for-byte
matching the canonical scaffold output. It never touches `proofs/` content
(REQ-0.0.21-09-05) and never modifies project-local-only slugs that are absent
from the canonical set (REQ-0.0.21-09-06).

### `gz validate --chores-layout` — Layout enforcement (REQ-0.0.21-08)

```bash
uv run gz validate --chores-layout
```

Fails closed (exit 3) on any unwaived `CHORE.md` or `acceptance.json` outside
`src/gzkit/chores/`, `.gzkit/chores/`, or the configured `paths.chores`.
Waivers are explicit entries in `data/chores_layout_waivers.json`; silent skips
are not permitted.

---

## What You MUST NOT Do

1. **DO NOT skip the CHORE.md** — It contains the authoritative procedure.
2. **DO NOT put proofs in `artifacts/` or any path outside the slug overlay.**
   Proofs go in `.gzkit/chores/<slug>/proofs/`.
3. **DO NOT write a second copy of a chore's criteria or version in `CHORE.md`.**
   `gz chores run` executes `acceptance.json` and reads `registry.json`; those are
   the authorities. In `CHORE.md`:
   - the criteria section cites `acceptance.json`, carries no table, and may quote
     only commands the JSON runs — it explains the criteria, never restates them;
   - there is no `**Version:**` field, and the newest change note (`**X.Y.Z (…)**`)
     names the version the registry carries — bump both together;
   - `**Lane:**`, `**Slug:**`, `**Vendor:**` and `**Timeout:**` may stay beside
     their rationale, but must equal the registry;
   - obligations the runner cannot check go under `## Manual completion checks`,
     labelled as not run by `gz chores run`.

   Authored twice with nothing holding them equal, 17 of 40 chores' criteria and 7
   versions drifted (GHI #1002). `tests/governance/test_chore_metadata_authority.py`
   holds these on the project surface; its limits (commands under runners other than
   `uv`/`uvx`/`python`/`gz`/`test`, required files named only in prose) are stated in
   `audit_chore_metadata_authority`'s docstring.
4. **DO NOT create a chore without all required files** (`CHORE.md`,
   `acceptance.json`, `README.md`, plus a `proofs/` directory in the project
   overlay).
5. **DO NOT add `proofs/` content to the canonical package surface.** Proofs are
   execution evidence, not canon.
6. **DO NOT introduce a `CHORE.md` or `acceptance.json` outside the two canonical
   roots.** `gz validate --chores-layout` will fail closed; layout drift is the
   re-emergence pattern ADR-0.0.21 exists to prevent.
7. **DO NOT discharge a finding by suppression.** No criterion runs through a shell
   or passes an exit-forcing flag, and no step writes suppression markers.
   `.gzkit/rules/chores.md` § Suppression is not a repair is the rule;
   `audit_chore_suppression` holds criteria and CHORE.md commands, and a marker
   hand-written during a run is the arm it cannot see.

---

## What You SHOULD Do

1. **Follow the established pattern** — Study existing chores under
   `src/gzkit/chores/` before creating new ones.
2. **Keep proofs atomic** — One file per evidence artifact.
3. **Use descriptive filenames** — `ruff-report-2026-04-25.txt`, not
   `output.txt`.
4. **Commit project-local proofs** — They are tracked, not gitignored, and
   live under `.gzkit/chores/<slug>/proofs/`.

---

## Adding a New Chore (Canonical)

A new chore meets § Admission criterion first, and the operator directs its
creation. Use an existing canonical chore as a template. Required structure for
a canonical addition:

```text
src/gzkit/chores/<slug>/
├── CHORE.md          # Definition, workflow, acceptance criteria
├── acceptance.json   # Machine-readable criteria
└── README.md         # Brief human summary
```

After creating, register the slug in `src/gzkit/chores/registry.json` with its
class declaration (§ Class Declaration). Project
overlays (`.gzkit/chores/<slug>/`) are scaffolded by `gz init` or `gz chores
doctor` from the canonical surface.

---

## What a Chore Is

A chore is authorized, recurring maintenance labor. It finds a problem,
analyzes it, recommends an approach and fixes what it is licensed to fix,
consulting the operator where the judgment is the operator's. Operator
statement (2026-09-12, verbatim): *"A chore is authorized to find, analyze,
solve and fix."* A chore is upkeep run at intervals, not a work order: it files
a GHI sparingly, and in consultation with the operator.

### Admission criterion

Not every refactoring is a chore — operator, verbatim: *"not all refactorings
are chores, but most chores can lead to refactorings."* Work is admitted to the
registry only when it is **toil** in the Google SRE sense (*Site Reliability
Engineering* ch. 5), and two characteristics decide:

- **Repetitive, on evidence.** It has already recurred. *"If you're performing
  a task for the first time ever, or even the second time, this work is not
  toil."*
- **No enduring value.** The surface drifts back and the work comes due again.
  A one-time system-wide refactoring leaves a permanent improvement; that is
  engineering work, it can never be *due* again, and registering it corrupts
  every staleness reading.

**The operator directs creation.** A chore run or an R&D pass may advise that a
new chore is warranted, citing the recurrence evidence. The registry never
self-populates, and an agent never registers a chore on its own reading.

---

## The Five Classes

`class` answers why the chore exists, what makes it stale, and what staleness
costs. Chores in one class are handled uniformly. The model's `ChoreClass` is
the authority for the values; this table is checked against it.

| Class | The finding is | Staleness signal | What staleness costs | The operator is there to |
|-------|----------------|------------------|----------------------|--------------------------|
| `conformance` | code deviates from a standard gzkit declares | content delta | gradual decay; high where no commit-path gate exists | nothing at write time; canon repair is `operator-only-repair` |
| `coherence` | two authored surfaces disagree and neither is the declared authority | content delta | an agent meets the contradiction mid-work and rules on it silently | supply the ruling, which only the operator holds |
| `curation` | a corpus has accumulated past usefulness | accumulated work | bloat, per-turn context weight, signal decay | judge what is still useful; the likeliest rubber-stamp site |
| `mining` | history holds a recurring pattern worth acting on | elapsed time | the feedback loop is lost and the same failure keeps recurring | decide whether a pattern is worth a work order |
| `currency` | the outside world moved | elapsed time | **assertions become false**, not merely stale | nothing at write time; canon repair is `operator-only-repair` |

The class predicts a chore's staleness signal and rung; it does not set them.
Each chore declares both.

**Staleness announces; it does not gate.** Operator ruling (2026-09-12,
verbatim): *"indicators, chores shouldn't have a bunch of gates like the
adr/obpi system."* `currency` is the one exception the design allows, because a
stale `currency` chore asserts something false.

**Staleness is read without running the chore.** `gz chores status` renders each
chore's band — `overdue`, `due`, `unmeasured`, `paused` or `current` — from its
declaration and the PASS blocks `gz chores run` appends to `CHORE-LOG.md`, and
session orientation announces the due and overdue ones (GHI #936). An
`elapsed-time` chore is due `periodDays` after its last passing run; a
`content-delta` chore is due from the first commit touching a declared
`staleness.surfaces` path after it. Declare the surfaces the chore actually
inspects: too broad and it is always due, too narrow and its decay is hidden.

**A chore whose criteria gate on elapsed time declares its scan record.**
`scripts/check_proof_freshness.py` dates such a chore by the last change to its
declared `staleness.artifacts`, the file its procedure writes, and never by
`CHORE-LOG.md`. The gate is itself a criterion of `gz chores run`, and a PASS
block is written only when every criterion passes, so a gate reading PASS blocks
left an overdue chore that no run could clear. A bare run inside the period also
wrote a fresh block and pushed the clock back without a scan. `gz chores status`
dates a chore that declares a record the same way (GHI #935). An uncommitted edit
to the record counts as now, so recovery is: do the scan, run the chore, commit both.

---

## The Four Rungs

`rung` answers where the chore stops, and it is the chore's **writing
license**. It is independent of class. The ladder is ordered, lowest first;
`audit_chore_rung_conformance` enforces that order, and this table is checked
against it.

| Rung | Writes | Ends with |
|------|--------|-----------|
| `observe` | nothing | a finding, and a recommendation or a declared reason there is none |
| `propose` | a plan artifact, never the subject | a recommendation the operator, or a paired repair chore, applies |
| `repair` | the subject; safe changes by default | the subject clean, and a result that says whether it already was |
| `operator-only-repair` | the subject, never in an automatic run | an operator-initiated repair; any repair that touches canon lives here |

**Pick the rung by asking whether one side is the declared authority** — not
whether the chore audits or repairs. When the correct output is derivable, the
chore can repair: `frontmatter-ledger-coherence` rewrites frontmatter because
the ledger is Layer-2 truth. When neither side is presumptively right,
resolving it is a ruling, so the chore proposes and stops:
`control-surface-rule-conflicts`. Set the rung by the repair's consequences,
never by the finding's severity, and never by how capable the agent is.

**Stopping at data is a defect.** A chore that stops below `repair` still hands
the operator something to act on. One that deliberately never repairs declares
`remediation.category: no_fix_planned` with its reason — "no repair" is a
declared value, never an absence. A detection chore that stops at a plan
artifact for a paired repair chore is a legitimate shape (operator, verbatim:
*"that split is fine, it makes room for pause and operator consultation"*).

`idempotent` is a separate license — **scheduling**: whether the chore may run
on a cadence. A chore can be safe to schedule and unsafe to write.

---

## Class Declaration (registry fields, GHI #999)

**Every registered chore carries a class declaration.** A chore's nature is
declared as metadata on its registry entry, never left to its name or its prose.
The model is `ChoreDeclaration` in
`src/gzkit/commands/chores_declaration.py`; the design, its sources and its
rationale are in `docs/governance/chore-class-system.md`.

| Key | Values | Answers |
|-----|--------|---------|
| `class` | `conformance` · `coherence` · `curation` · `mining` · `currency` | Why the chore exists, and what its staleness costs |
| `rung` | `observe` · `propose` · `repair` · `operator-only-repair` | Where it stops — the **writing** license |
| `idempotent` | `true` · `false` | Safe to re-run on a cadence — the **scheduling** license |
| `staleness` | `{signal, periodDays, surfaces, artifacts, graceDays, paused}`; `signal` is `accumulated-work` · `content-delta` · `elapsed-time`; `periodDays` required for `elapsed-time`; `surfaces` (repo-relative POSIX paths, never `.`) required for `content-delta` and refused on any other signal; `artifacts` (repo-relative POSIX paths, never a `CHORE-LOG.md`) is the scan record an `elapsed-time` chore's procedure writes, required by `scripts/check_proof_freshness.py` for a chore its criteria gate and refused on any other signal | What makes it due |
| `remediation` | `{category, details}`; `category` is `vendor_fix` · `workaround` · `no_fix_planned` · `none_available`; `details` non-empty | What repair means — "no repair" is a declared value, never an absence |
| `nonAuthority` | non-empty text | What it refuses to touch, and why |
| `governingRule` | `.gzkit/rules/<file>.md` (optionally ` § <clause>`) or `none` | The rule it serves |

```json
{
    "slug": "example-rule-conflicts",
    "class": "coherence",
    "rung": "propose",
    "idempotent": true,
    "staleness": {"signal": "content-delta", "surfaces": [".gzkit/rules"], "graceDays": 7},
    "remediation": {"category": "no_fix_planned", "details": "A rule conflict is a ruling; the chore recommends and stops."},
    "nonAuthority": "Never edits either conflicting rule; resolving the conflict is the operator's.",
    "governingRule": "none"
}
```

**Declaring any key commits the chore to all of them.** A partial or malformed
declaration fails closed with a `chores[<slug>].<key>` blocker.

**Declaring a rung commits the workflow to stages.** Every `###` step under the
chore's `## Workflow` ends `— <stage>`, where the stage is one of the rungs, and no
step's stage may rank above the chore's `rung` (operator ruling 2026-09-13):

```markdown
### 1. Scan — observe
### 2. Draft the fix list — propose
```

A declared chore with a stageless step, an unknown stage, or a step past its rung
fails `tests/governance/test_chore_rung_conformance.py`. The check compares the two
declarations and never reads posture from prose, so a mislabelled step is its limit.

**An undeclared chore does not run.** `gz chores run` refuses it, `gz chores
list` counts the undeclared estate, and `gz check` fails on it through
`tests/governance/test_chore_rung_conformance.py`. Absence warned while no chore
was declared and flipped to refusal once every registered chore carried a
declaration (operator ruling 2026-09-13, *"Warn, flip at step 5"*).
Authorization does not expire.

---

## Acceptance Criteria Format

The `acceptance.json` file uses this schema:

```json
{
  "criteria": [
    {
      "type": "exitCodeEquals",
      "command": "uv run -m unittest -q",
      "expected": 0
    },
    {
      "type": "outputNotContains",
      "command": "uvx ruff check src/gzkit --select E722",
      "notContains": "E722",
      "description": "No bare except clauses"
    }
  ]
}
```

Supported types:

- `exitCodeEquals` — Command must exit with specific code
- `outputContains` — Command output must contain string
- `outputNotContains` — Command output must not contain string
- `fileExists` — File must exist at path

Commands must not contain shell operators (`&&`, `||`, `|`, `<`, `>`).
Split compound commands into separate criteria.

---

## If You're Unsure

**ASK THE HUMAN:**

- "Should I create a new chore or add to an existing one?"
- "Should this chore live in canonical (`src/gzkit/chores/`) or only as a
  project overlay (`.gzkit/chores/`)?"
- "What lane should this chore be?"
- "Where should I store this proof artifact?"

---

## Related

- ADR-0.0.21 — `docs/design/adr/foundation/ADR-0.0.21-chores-as-gzkit-surface/`
- Rule — `.gzkit/rules/chores.md`
- Manpage — `docs/user/manpages/chores.md`
- Runbook — `docs/user/runbook.md` § Chores Commands
