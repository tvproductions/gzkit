# gz governance render

Render a governance surface from the constitutional invariant registry.

## NAME

gz governance render — render AGENTS.md (or another target) from the
constitutional invariant registry, with drift detection.

## SYNOPSIS

```text
gz governance render --target <target> [--check] [--stdout]
```

## DESCRIPTION

`gz governance render` projects the constitutional invariant registry at
`.gzkit/invariants/` into a governance surface. Output is byte-deterministic:
the same registry state and template always produce identical bytes.

This command is the stand-alone producer of rendered governance surfaces
(ADR-0.0.37, OBPI-0.0.37-02). Drift validation (`gz validate --invariant-coherence`)
is wired by OBPI-0.0.37-03 and consumes this command's output.

### Targets

`--target agents-md` is the only accepted render target at this time.
Other targets (skill READMEs, persona files) are forward-references for
future feature ADRs.

## OPTIONS

`--target agents-md`
: Required. The governance surface to render. Currently `agents-md` is the
  only supported target.

`--check`
: Read the current file at the target path, re-render from the registry,
  byte-compare the two, and exit without writing. Exits 0 on byte-identical
  match. Exits 3 on drift and prints a unified diff of the first 50
  differing lines to stderr. Does not modify any file.

`--stdout`
: Emit rendered bytes to stdout without writing the target file. Used by
  drift validators and integration tests.

## EXAMPLES

Check whether AGENTS.md is in sync with the invariant registry:

```
gz governance render --target agents-md --check
```

Stream rendered bytes to stdout for inspection:

```
gz governance render --target agents-md --stdout
```

Confirm byte-determinism across two invocations:

```
diff <(gz governance render --target agents-md --stdout) \
     <(gz governance render --target agents-md --stdout) \
  && echo "byte-identical"
```

Write rendered output to AGENTS.md (after template migration in OBPI-09):

```
gz governance render --target agents-md
```

## EXIT CODES

| Code | Meaning |
|------|---------|
| 0 | Success (or `--check` finds no drift) |
| 1 | Unsupported target or other error |
| 3 | `--check` mode detected drift between committed file and rendered output |

## SEE ALSO

- `gz validate --invariant-coherence` (OBPI-0.0.37-03) — fail-closed drift validator
- brief reconcile command (planned, OBPI-0.0.37-06) — reconcile OBPI briefs against project shape
- [`AGENTS.md`](../../AGENTS.md) — the rendered output target (migrated in OBPI-09)
