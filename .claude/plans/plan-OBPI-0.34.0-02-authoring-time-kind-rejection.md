# Plan — OBPI-0.34.0-02-authoring-time-kind-rejection

**OBPI:** `OBPI-0.34.0-02-authoring-time-kind-rejection`
**Parent ADR:** `ADR-0.34.0-foundation-sunset`
**Lane:** Heavy

## Context

Parent ADR § Decision item #2 (verbatim): "authoring-time-kind-rejection: Reject
'gz plan create --kind foundation' and 'gz adr promote --kind foundation' at the
command layer with three-part guardrail-feedback prose (what failed / why
forbidden: foundation kind closed ADR-0.34.0 / next step: --kind feature or
pool). Close the authoring doors while leaving the schema enum intact for
grandfathered validation. (heavy lane: CLI authoring-behavior change)."

The `foundation` kind is SEALED, not deleted. `src/gzkit/schemas/adr.json`'s
`kind` enum and the argparse `choices=[...]` lists keep `foundation` so the ~51
grandfathered on-disk foundation ADRs still validate, and so the handler
receives the value and can emit real recovery prose (argparse's bare
"invalid choice" cannot carry three-part prose).

## Files

**Modified (in brief Allowed Paths):**

- `src/gzkit/commands/plan.py` — `_validate_kind_and_semver` (line 151;
  called pre-I/O at line 354).
- `src/gzkit/commands/adr_promote.py` — `_validate_promotion_kind_semver`
  (line 54; called pre-I/O at line 324).

**Created:**

- `tests/commands/test_foundation_kind_closed.py` — REQ-derived coverage for
  all three REQs.

**Explicitly NOT touched (brief Denied Paths):**

- `src/gzkit/schemas/adr.json` (enum keeps `foundation`)
- `src/gzkit/cli/parser_*.py` (argparse `choices` keep `foundation`;
  help-text coherence is OBPI-0.34.0-03's sweep)
- `data/foundation_grandfather.json`, `gz validate --taxonomy` scope

## Steps

### Step 1 — RED: closed-kind rejection for `gz plan create` (REQ-0.34.0-02-01)

Write `TestPlanCreateClosedFoundationKind` asserting `_validate_kind_and_semver(
"foundation", "0.0.99", adrs_root)` raises `SystemExit` with a non-zero code, and
that captured console output carries all three prose parts:

- (a) what failed — names `--kind foundation` as the requested value
- (b) why forbidden — cites `ADR-0.34.0` and the kind being closed to new authoring
- (c) governed next step — names both `--kind feature` and `--kind pool`

Assertions derive from REQ-0.34.0-02-01 semantics (three-part prose per
`.claude/rules/guardrail-feedback-prose.md`), not from a run of the code.
Watch it fail on an assertion — the symbol already exists and imports cleanly,
so the red is assertion-level, not an ImportError.

### Step 2 — GREEN: seat the guard in `plan.py`

In `_validate_kind_and_semver`, insert the closed-kind rejection **after** the
`kind is None` check and **before** the `kind == "foundation"` semver check.
Ordering is load-bearing: seated last, `--kind foundation --semver 0.34.0` would
emit the semver-binding error and send the operator to fix a semver for a kind
they may not author at all. Match the file's existing `console.print(...)` +
`sys.exit(1)` style.

### Step 3 — RED: closed-kind rejection for `gz adr promote` (REQ-0.34.0-02-02)

Write `TestAdrPromoteClosedFoundationKind` asserting
`_validate_promotion_kind_semver("foundation", "0.0.99")` raises `SystemExit`
non-zero with the same three-part prose. Watch the assertion-level red.

### Step 4 — GREEN: seat the guard in `adr_promote.py`

Insert after the `kind is None` check, before the existing `kind == "pool"`
check. Match the file's `console.print(...)` + `raise SystemExit(1)` style.

### Step 5 — RED/GREEN: non-widening + grandfathered validation (REQ-0.34.0-02-03)

Two assertions:

- **Non-widening (REQ-4 fence):** `_validate_kind_and_semver("feature",
  "0.34.0", ...)` and `("pool", ...)` still return normally — the closure did
  not widen to the other two kinds. Also assert `foundation` is still present
  in the `adr.json` `kind` enum (the seal-not-delete invariant REQ-1 fences).
- **Grandfathered set (REQ-0.34.0-02-03):** `uv run gz validate --documents`
  over the on-disk `docs/design/adr/foundation/` set still exits zero.

Note on `--taxonomy`: OBPI-0.34.0-01 left `gz validate --taxonomy` at a
deliberate interim red (exit 3, 74 `foundation_kind_closed` findings) because
manifest roster population is OBPI-0.34.0-04. REQ-0.34.0-02-03's covering
assertion therefore binds to `--documents`, and the `--taxonomy` half is
recorded as pre-existing-red-by-design with the finding types asserted
unchanged by this OBPI (this OBPI must not add or remove taxonomy findings).
Surface this to the operator at Stage 4 rather than silently narrowing the REQ.

### Step 6 — REFACTOR + coupled surfaces

- `uv run ruff check . --fix && uv run ruff format .`
- Gate 3 (Heavy): check whether `docs/user/manpages/**` for `gz plan create` /
  `gz adr promote` document `--kind foundation` as available. Per the brief,
  coordinate with OBPI-0.34.0-03's coupled-surface sweep — touch docs here only
  if a manpage would now state something false; otherwise leave to -03 and note
  it in evidence.

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
```

Plus per-REQ RED witnesses (`uv run gz arb red --req ... --obpi ...`) and
`uv run gz covers OBPI-0.34.0-02-authoring-time-kind-rejection --json`.

## Step 6a — Plan-Before-Exploration Disclosure

**Destination-in-mind.** Before writing this plan I had already formed the
conclusion that the guard belongs inside the two existing `_validate_*` helpers
rather than at a new seam. That destination came from the brief itself, which
names both helper functions and their approximate line numbers in its Allowed
Paths — so the plan is admittedly a reconstruction of a destination the brief
handed me. The exploration I did afterward (reading both handlers, their call
sites at `plan.py:354` / `adr_promote.py:324`, and their existing rejection
prose) was confirmatory: it verified pre-I/O ordering satisfies REQ-3, and it
surfaced one thing the brief did not pin — the *within-function* guard ordering
relative to the semver check, which changes which error an operator sees.

**Rejected alternatives.**

1. *Delete `foundation` from the schema `kind` enum.* Rejected — invalidates all
   ~51 grandfathered ADRs at once. Already rejected in the parent ADR's own
   alternatives list (#1), and fenced by brief Denied Paths.
2. *Drop `foundation` from argparse `choices`.* Rejected — argparse would emit a
   bare `invalid choice: 'foundation'` with no rule citation and no next step,
   failing `.claude/rules/guardrail-feedback-prose.md`. The brief fences this
   explicitly.
3. *Extract a shared `_reject_closed_kind` helper into
   `gzkit/commands/common.py`.* Tempting — both files already carry a duplicated
   `_FOUNDATION_SEMVER_RE` with a TODO naming exactly that extraction. Rejected:
   `common.py` is outside the brief's Allowed Paths, and AGENTS.md § DO IT RIGHT
   Rule 11 (surgical changes) forbids adjacent refactor. Two short guards is the
   correct shape here; the extraction belongs to whichever OBPI legitimately
   owns that surface.
4. *Seat the rejection in a validator (`gz validate --taxonomy`) instead of the
   command layer.* Rejected — that catches the ADR after it is written. The ADR
   § Decision says "at the command layer," and REQ-3 requires failing before any
   file write.
5. *Guard the whole `plan create` command entry rather than the kind helper.*
   Rejected — the helper is already invoked pre-I/O and is where the sibling
   kind rejections live; a second seam would fragment the kind-validation story.
