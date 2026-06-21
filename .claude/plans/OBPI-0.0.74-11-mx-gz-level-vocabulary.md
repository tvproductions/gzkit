# Plan — OBPI-0.0.74-11-mx-gz-level-vocabulary

**OBPI:** OBPI-0.0.74-11-mx-gz-level-vocabulary
**Parent ADR:** ADR-0.0.74-mx-mode-maintenance-hangar (foundation, heavy)
**Lane:** Heavy (ships a runtime-contract surface: the single `GZ_<LEVEL>` vocabulary)

## Context

The MX shared checkpoint (`src/gzkit/mx/checkpoint.py`, OBPI-02) currently speaks
a binary vocabulary — a guard is either fail-closed or advisory (`is_advisory`).
A binary flag cannot express "this is drift, not a defect" or "wrong-design vs
wrong-build," so the V.I.B.E.S. drift band has nowhere to live. This OBPI lands
the `GZ_<LEVEL>` severity vocabulary the substrate items 12–14 route against.

STDLIB-FIRST is the binding rationale (ADR § Alternatives rejection (f)): the
ladder reuses Python `logging`'s numeric constants rather than re-inventing a
kernel/syslog 0–7 ladder. The one rung Python omits — `NOTICE = 25` — is the
agent-fidelity / V.I.B.E.S. drift band.

Decision item 11 (verbatim): "The `GZ_<LEVEL>` severity vocabulary. Backed by
Python `logging` (STDLIB-FIRST): CRITICAL 50 / ERROR 40 / WARNING 30 / NOTICE 25
/ INFO 20 / DEBUG 10. NOTICE (25 — the rung Python omits) is the agent-fidelity /
drift band, the V.I.B.E.S. rung. Grounding threshold: effective severity
`>= ERROR` grounds (blocks); below ERROR is visible-but-non-grounding. The
checkpoint (item 2) resolves the effective level against this one vocabulary."

## Files

- `src/gzkit/mx/levels.py` **CREATE** — the `GZ_<LEVEL>` vocabulary: ladder
  reusing `logging.*` constants + `NOTICE = 25`, `GROUNDING_THRESHOLD = ERROR`,
  and the `grounds(level)` predicate.
- `tests/mx/test_levels.py` **CREATE** — unit tests for the stdlib-equality
  ladder, the `NOTICE = 25` drift rung, and the grounding boundary at ERROR.

No edit to `checkpoint.py`: REQ-11-03 is a `[structural-fence]` whose proof
channel is the parent ADR § Boundary Invariants #2 (audited at ADR closeout),
not a per-OBPI code change. The disposition/guards-emit-levels wiring is owned
by OBPI-12 (Denied Paths). The `gate5_invariants` never-relax list is owned by
OBPI-03 (Denied Paths).

## Steps

1. **RED:** author `tests/mx/test_levels.py` with three behavior assertions —
   ladder rungs equal `logging.*` constants, `NOTICE = 25` sits between INFO and
   WARNING (and Python's `logging` has no NOTICE), and `grounds()` grounds iff
   `>= ERROR`. Run; watch import-fail (no `levels.py` yet) for the right reason.
2. **GREEN:** author `src/gzkit/mx/levels.py` — reference `logging.CRITICAL/
   ERROR/WARNING/INFO/DEBUG` directly (never hand-typed), add `NOTICE = 25`,
   `GROUNDING_THRESHOLD = ERROR`, and `grounds(level) -> bool` returning
   `level >= GROUNDING_THRESHOLD`. Run tests to GREEN.
3. **Verify:** ruff, typecheck, unittest, `gz covers` parity for REQ-11-01/02.

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
test -f src/gzkit/mx/levels.py
test -f tests/mx/test_levels.py
uv run python -c "from gzkit.mx import levels; print('NOTICE', levels.NOTICE, '| grounds(ERROR)', levels.grounds(levels.ERROR), '| grounds(NOTICE)', levels.grounds(levels.NOTICE))"
```

## Notes

### Destination-in-mind (Step 6a disclosure)

Before writing this plan I had already formed the implementation shape: a flat
module of module-level integer constants aliased to `logging.*` plus a single
`grounds()` predicate keyed to `GROUNDING_THRESHOLD = ERROR`. The brief's Demo
line (`levels.NOTICE`, `levels.grounds(...)`) pins the public surface, so the
approach was nearly fully determined by the brief itself.

### Rejected alternatives

- **An `IntEnum` for the ladder.** Rejected: the brief's Demo and REQ-11-01
  ("numeric values MUST equal the stdlib constants") want bare module-level
  ints equal to `logging.*`; an enum wraps the values and complicates equality
  with the stdlib constants. Simplicity-first (AGENTS.md Rule 10).
- **Registering the level name via `logging.addLevelName(NOTICE, "NOTICE")`.**
  Rejected for THIS OBPI: no REQ requires a named logging level, and log
  rendering is OBPI-06's concern (the MX log). Surgical-changes (Rule 11).
- **Editing `checkpoint.py` to make `is_advisory` leveled.** Rejected: that is
  the disposition wiring owned by OBPI-12 and the gate5_invariants list owned by
  OBPI-03 — both Denied Paths here. REQ-11-03 is a fence, not a code edit.
