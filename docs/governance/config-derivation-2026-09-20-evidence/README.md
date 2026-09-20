# Config-derivation census — re-run instructions

```bash
uv run python docs/governance/config-derivation-2026-09-20-evidence/census.py
```

Read-only. Reads `data/*.json` and `src/gzkit/**/*.py` from the working tree and
writes nothing. No network, no `gh`, no ledger write.

**This script carries no literals from its authoring date.** Every figure is
derived from the tree at run time, so running it on a later tree reports that
tree. The percentages in
[`../config-derivation-census-2026-09-20.md`](../config-derivation-census-2026-09-20.md)
are a dated observation of the 2026-09-20 tree — re-run rather than trusting them.

## What it measures, and what it deliberately does not

It asks **where a value came from**, never **who reads it**. Ownership is already
answered: `data/config_registry.json` fail-closes on an undeclared registry and
verifies each declared owner actually references the file.

A registry counts as `cites-authority` only when a provenance field points
somewhere a reader can go — a `docs/**.md` path, an `ADR-`, a `GHI #N`, or an
operator ruling. Prose explaining what a field *means* scores `prose-only`: that
is documentation, not derivation, and the distinction is the whole census.

`$schema` is not provenance. It declares shape, never origin.

## Known bounds

- `THRESHOLD_NAME_RE` is deliberately broad, so the constant population includes
  implementation details alongside policy knobs. The census reports the
  population; a reader judges individual rows.
- Duplicate detection groups by constant name with a leading underscore stripped.
  Two constants sharing a name in different modules may be genuinely independent
  — `DEFAULT_TIMEOUT_SECONDS` at 30.0 in the complexity advisor and 3.0 in
  `justify/evidence` is flagged as disagreeing, and may well be correct in both.
  The flag means *nothing reconciles these*, never *one of them is wrong*.
- It reads top-level `data/*.json` only. Nested config and per-chore JSON are out
  of scope.
