<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# RO-2 specification — one identity seam for every reader

**2026-10-18. Status: specified; tranche 1 not started.** Operator: **g0**. Repair order RO-2 of the
[harbor pilotage drydock](harbor-pilotage-candidate-2026-10-15.md#repair-orders), mandate item 2:
give REQ, TASK and release identity independent of the ADR, by alias and resolver, renaming nothing
before 1.0. This is phase 1 of [`ADR-pool.identifier-ladder-migration`](../design/adr/pool/ADR-pool.identifier-ladder-migration.md),
pulled forward by R5. It changes no identifier, and the 1.0 rename (that ADR's phase 2) is not part of it.

## Rulings

Operator selections of 2026-10-18, each recorded as an insight (scope `drydock-ro2`):

- **Shape:** *"One RO, tranches (Rec.)"*. RO-2 stays one order, cut into the five tranches below.
  Each tranche is one act. Tranches 2 to 5 may land in parallel on cheaper sessions once tranche 1
  is in.
- **Witness:** *"Ratchet to zero (Rec.)"*. A validator finds every id-grammar pattern and
  spelling-derived parent outside the seam. Today's sites seed a baseline that may only shrink and
  takes no additions. RO-2 closes when the baseline is empty.

## The population, measured 2026-10-18

RO-2's row said nine grammar copies. That figure has no recorded measurement and understates the
population roughly tenfold.

| Measure | Value |
|---|---|
| Python files under `src/gzkit` naming `ADR-` or `OBPI-` | 371 (command 1) |
| Test files with `@covers` REQ bindings | 358 (command 2) |
| Scenario REQ tags | 415, 343 distinct (command 3) |
| Single-line compiled id patterns | 83 (command 4) |
| Independent grammar copies, multi-line and inline included | about 118 (REQ 23, TASK 10, OBPI about 42, ADR about 55), plus 7 in JSON schemas; read by hand |
| Sites deriving a parent from an id's spelling | 28 (OBPI→ADR 6, REQ→OBPI/ADR 10, TASK→REQ/OBPI/ADR 12), plus about 9 reverse ADR→children prefix scans; read by hand |
| Resolver paths | about 14; read by hand |

```bash
grep -rlE 'ADR-|OBPI-' src/gzkit --include='*.py' | wc -l                       # 1
grep -rlE '@covers\(.REQ-|covers\("REQ-' tests | wc -l                          # 2
grep -rhoE '@REQ-[0-9.]+-[0-9]+-[0-9]+' features | wc -l                         # 3
grep -rnE 're\.compile\(|pattern=' src/gzkit | grep -E 'ADR-|OBPI-|REQ-|TASK-' | grep -c '\.py:'   # 4
```

Tranche 1's validator replaces the hand counts with its own baseline. The hand figures are
illustrative, and the baseline file is the authority.

**What exists to build on.**

- `Ledger.canonicalize_id` (`src/gzkit/ledger.py`) folds `artifact_renamed` events through
  `obpi_lifecycle.fold_renames`. It has 56 call sites.
- `artifact_prefix.active_prefix_matches` (GHI #1162) expands a short id and drops parked or
  withdrawn keys when an active one remains. The handoff citation checker and
  `common.resolve_obpi` use it.
- A canonical grammar body exists only for REQ (`triangle.REQ_ID_BODY`, strict, GHI #615) and for
  numeric TASK (`tasks.TaskId`, loose). OBPI and ADR have none, and the slug TASK form is spelled
  only inside `tasks._ANY_TASK_TRAILER_RE`.
- `core/models.py` carries an identity layer (`AdrId`, `ObpiId`, `ReqId`, `TaskId`,
  `IDENTITY_MODELS`) from ADR-0.0.10 (OBPI-0.0.10-02). It is attested and imported by no source
  module. Its `ReqId` is loose where `triangle.ReqId` is strict.

**Defects the inventory surfaced** (recorded as insights; direct fixes under `AGENTS.md` § Defect-fix
routing, independent of the tranches):

- `obpi_audit_cmd._derive_adr_id` uses `rsplit("-", 1)`, so `OBPI-0.28.0-01-context-core` gives
  `ADR-0.28.0-01-context`.
- `commands/task.py:146` resolves a short OBPI id without `project_root`, ignoring the parked flag,
  so `OBPI-0.28.0-01` can be booked in short form (the GHI #653 divergence).
- `pipeline_markers.find_obpi_brief` and `obpi_precomplete.resolve_brief_path` glob `{id}*.md` with
  no `-` separator and take the first match, so `OBPI-0.28.0-1` matches items -10 to -19. This is
  tranche 3's to close.

## The seam

**Home.** The identity layer in `src/gzkit/core/models.py`, extended rather than replaced
(`hexagonal-architecture.md` rule 8, *prefer subsumption to a parallel model*). ADR-0.0.10's attested
REQs over it are repaired at the surface, never deleted (`docs/governance/attested-req-subject-retirement.md`).
A resolver that reads the ledger lives beside it in the core and takes the ledger and the project
root as parameters (rule 4).

**It provides three things, and nothing outside it spells an id grammar or derives a parent:**

1. **One grammar body per kind**, exported as pattern text and as typed parsers:
   - ADR: the full form `ADR-<semver>-<slug>`, the short form `ADR-<semver>`, the pool form
     `ADR-pool.<slug>`, and the foundation test (`0.0.x`).
   - OBPI: the full form `OBPI-<semver>-<NN>-<slug>` and the short form `OBPI-<semver>-<NN>`.
   - REQ: `REQ-<semver>-<NN>-<MM>`.
   - TASK: the numeric form `TASK-<semver>-<NN>-<MM>-<PP>` and the slug form `TASK-<kebab>[-#<ghi>]`.

   Widths are settled once, in the seam. The strict `\d{2}` that both JSON schemas and
   `triangle` already pin is the starting point. A width change that would reject a live id
   (ledger, briefs, `@covers`, tags) is a finding put to the operator, never applied silently.
   `triangle.REQ_ID_BODY` and `tasks.TaskId` re-export from the seam, so existing imports keep
   working. The two JSON schemas take their patterns from the seam, by generation or by a test
   asserting byte equality.
2. **One resolver**, `resolve(id) -> Resolution`, built on the rename fold and
   `active_prefix_matches`:
   - It returns the canonical id, its kind, and whether it is active, parked or withdrawn.
   - A short id expands only across a `-` separator.
   - An id that stays ambiguous among active keys fails closed with every candidate named. It never
     takes a first match.
   - A reused numeric prefix is told apart by slug, by `artifact_renamed`, and by parked or
     withdrawn state. The fixture is `OBPI-0.28.0-01`: parked `chores-cli` under
     `ADR-pool.chores-system-maturity-absorption`, live `context-core` under
     `ADR-0.28.0-focused-context-loader`.
3. **One parent lookup**, `parent_of(id)`, that reads stored fields:
   - an OBPI's `parent` from its `obpi_created` event or brief frontmatter;
   - a TASK's `obpi_id` and REQ from its `task_started` event;
   - a REQ's containing brief from the brief index.

   Deriving a parent from an id's spelling survives only inside the seam, as the fallback for an
   artifact with no stored field. It is marked and counted, and it shrinks as RO-3's `member_of`
   lands.

## The witness

Tranche 1 lands `gz validate --id-seam`, one scope in the default `gz check`:

- **The scan.** AST over `src/gzkit/**/*.py`:
  - every string literal handed to `re.compile`, `re.match`, `re.search`, `re.fullmatch`,
    `re.findall` or `re.sub`, or to a `pattern=` keyword, that encodes an `ADR-`, `OBPI-`, `REQ-` or
    `TASK-` grammar;
  - every slice, `split` or `rsplit` on a value the scan can tie to an id.

  Code inside the seam module is exempt. Embedded hook scripts (`src/gzkit/hooks/scripts/`) are
  scanned as the strings they are, or listed in the baseline as one row each.
- **The baseline.** `data/id_seam_baseline.json` lists today's sites keyed by file and enclosing
  symbol, never by line number, so an unrelated edit does not churn it. It is registered in
  `data/waiver_ratchet_registry.json` as a `shrink-ratchet` with its `baseline_count`. A site that is
  not in the baseline fails the scope. A row whose site is gone must be deleted, so the baseline
  cannot carry dead rows.
- **The resolution check.** Every `@covers` REQ, every scenario REQ tag, and every OBPI and ADR id
  in brief frontmatter resolves through `resolve` to exactly one active canonical id, or to a parked
  or withdrawn one recorded as such.
- **Close condition.** The baseline is empty; the resolution check passes; `gz check` passes.

## Tranches

Each tranche is one act under § Records of the contract: one commit with a `Task:` trailer
(`TASK-ro2-<slug>`), a failing test observed first, `gz arb red --commit` with its verdict, a
passage-log row with before and after counts read from the baseline, and every reader it touches
moved in the same commit.

| # | Scope | Done when |
|---|---|---|
| 1 | The seam (grammar bodies, `resolve`, `parent_of`), the JSON schemas tied to it, `gz validate --id-seam` with its baseline and registry entry, and the resolution check | The baseline is seeded and committed. The resolution check passes. The `OBPI-0.28.0-01` fixture resolves both ways, and an ambiguous short id fails closed. |
| 2 | REQ and TASK readers: the 23 REQ and 10 TASK copies, and the slug TASK form | No REQ or TASK row remains in the baseline |
| 3 | OBPI readers and brief finders, the separator-less globs included | No OBPI row remains |
| 4 | ADR readers and package finders | No ADR row remains |
| 5 | The 28 parent-recovery sites and the reverse prefix scans, through `parent_of` | No spelling-derived parent remains outside the seam. The baseline is empty, and RO-2 closes. |

**Boundaries.** RO-2 renames nothing, writes no `artifact_renamed` event, changes no grammar a live id
depends on without an operator ruling, and authors no catalog entry (that is RO-3). `tests/` and
`features/` are read by the resolution check but are not scanned for copies. A copy found there is a
finding for the tranche that owns its kind.

**Known uncertainties.**

- Whether `obpi_precomplete.resolve_obpi_at_entry` adds logic beyond `resolve_obpi_file`.
- Whether the embedded hook scripts duplicate shipped hook files.
- Whether any test or feature parses ids by regex.

Tranche 1 reads each of these before it seeds the baseline.

## Before-figures

The requirements-model baselines of 2026-10-18 (passage log) stand as RO-2's before-figures for the
trace key: 361 of 736 test files carry `@covers`; 731 REQs have no test; 1,340 of 19,241 ledger
events name a REQ. They are re-read when RO-2 closes.
