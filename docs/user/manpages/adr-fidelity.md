# gz adr fidelity

Run an ADR's Fidelity Assertions against the running system and report
observed-vs-expected exit code per assertion.

## NAME

gz-adr-fidelity — parse the `## Fidelity Assertions` block from an ADR
Decision, execute each command, and compare observed exit to expected exit.

## SYNOPSIS

```text
gz adr fidelity ADR-ID [--check]
```

## DESCRIPTION

`gz adr fidelity` reads the `## Fidelity Assertions` markdown table from
an ADR's Decision section, runs each command via a shell-less subprocess
call (`shlex.split` + `subprocess.run`), and reports the result of each
assertion:

- **claim** — what the assertion tests
- **command** — the command that was run
- **expected exit** — the exit code the command must return
- **observed exit** — the actual exit code returned
- **result** — `PASS` when observed equals expected, `FAIL` otherwise

The gate exits 0 when every assertion passes and 1 when any assertion
fails.  Use `--check` to verify the block is parseable without running
any commands.

Every ADR Decision must carry a runnable `## Fidelity Assertions` block
(ADR-0.0.73 Boundary Invariant #4); this command enforces that requirement
and is invoked by both the closeout and audit ceremonies (OBPI-0.0.73-04).

## OPTIONS

- `ADR-ID` — ADR identifier (e.g. `ADR-0.0.73-verification-layer-binding-audit`); required.
- `--check` — parse-only: verify the block exists and is well-formed; no commands are run.
- `--quiet` / `-q` — suppress non-error output.
- `--verbose` / `-v` — enable verbose output.
- `--debug` — enable debug mode with full tracebacks.

## EXIT CODES

| Code | Meaning |
|------|---------|
| 0 | All assertions passed (or `--check` block parseable) |
| 1 | One or more assertions failed |
| 2 | ADR file not found or could not be resolved |
| 3 | `## Fidelity Assertions` block absent or malformed |

## EXAMPLES

Run all assertions for an ADR and report results:

```text
gz adr fidelity ADR-0.0.73-verification-layer-binding-audit
```

Verify the block is parseable without running commands:

```text
gz adr fidelity ADR-0.0.73-verification-layer-binding-audit --check
```

## SEE ALSO

- `gz adr audit-check` — verify OBPI completion and evidence for an ADR
- `gz closeout` — closeout ceremony that invokes this gate
- `gz audit` — post-attestation audit that invokes this gate
- ADR-0.0.73 — Verification Layer Binding Audit (parent ADR)
