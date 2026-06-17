# Plan: OBPI-0.0.73-03-fidelity-assertions-and-gate

## Context

OBPI-0.0.73-03 delivers Part 3 of ADR-0.0.73: the `FidelityAssertion` frozen
Pydantic model + `## Fidelity Assertions` block parser + `gz adr fidelity <ADR>`
command that RUNS assertions against the running system and compares
observed-vs-expected exit codes. One standalone gate; manpage + gz cli audit green.

ADR Decision Part 3 (verbatim):
> `## Fidelity Assertions` block + `gz adr fidelity <ADR>` gate (in
> `src/gzkit/fidelity.py` + `src/gzkit/commands/adr_fidelity.py`). Every ADR
> Decision ships a `## Fidelity Assertions` block: runnable commands that
> exercise the ADR's thesis against the real system, each with an expected exit.
> `gz adr fidelity <ADR>` RUNS them. `FidelityAssertion` is a frozen Pydantic
> model: `{adr_id, claim, command, expected_exit, observed, result}`. This is
> one standalone gate.

## Files

**CREATE:**
- `src/gzkit/fidelity.py` — FidelityAssertion model + parser + runner
- `src/gzkit/commands/adr_fidelity.py` — gz adr fidelity command
- `tests/governance/test_adr_fidelity.py` — unit tests (RED before GREEN)
- `docs/user/manpages/adr-fidelity.md` — manpage

**MODIFY:**
- `src/gzkit/cli/parser_artifacts.py` — register adr fidelity subcommand
- `docs/user/manpages/index.md` — add gz adr fidelity row to governance table
- `mkdocs.yml` — add navigation entry

**READ (no modification):**
- `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md` — first Fidelity Assertions consumer; the parent ADR

## Steps

### Step 1: Write failing tests (RED phase)

Create `tests/governance/test_adr_fidelity.py` with tests derived from brief
REQs before writing any implementation:

- REQ-0.0.73-03-01 [BEHAVIOR]: FidelityAssertion frozen=True extra="forbid" and
  has all six fields (adr_id, claim, command, expected_exit, observed, result);
  mutation raises; unknown field raises.
- REQ-0.0.73-03-02 [BEHAVIOR]: Parser extracts one FidelityAssertion per row
  from the `## Fidelity Assertions` table in an ADR's Decision section. Use an
  in-memory ADR fixture with a known 2-row table; verify two assertions returned
  with correct claim/command/expected_exit.
- REQ-0.0.73-03-03 [BEHAVIOR]: result="pass" when observed==expected_exit;
  result="fail" otherwise. observed and result are set by the runner.
- REQ-0.0.73-03-04 [BEHAVIOR]: When any assertion's observed exit != expected,
  the gate reports it as failed AND the function/command exits non-zero.

Decorate each test with `@covers("REQ-0.0.73-03-NN")` from `gzkit.traceability`.

### Step 2: Create `src/gzkit/fidelity.py` (GREEN phase)

```python
# FidelityAssertion: frozen Pydantic model, extra="forbid"
# Fields: adr_id: str, claim: str, command: str, expected_exit: int,
#         observed: int | None, result: str | None  (None before gate runs)

# parse_fidelity_assertions(adr_path: Path) -> list[FidelityAssertion]
#   - Extracts ## Fidelity Assertions block from ADR Decision section
#   - Parses the markdown table (columns: Claim | Command | Expected exit)
#   - Returns one FidelityAssertion per data row (observed=None, result=None)
#   - Raises ValueError if block is absent or table is malformed

# run_fidelity_gate(
#     assertions: list[FidelityAssertion],
#     adr_id: str,
# ) -> list[FidelityAssertion]
#   - For each assertion: subprocess.run(shlex.split(command), capture_output=True)
#   - Sets observed = returncode
#   - Sets result = "pass" if observed == expected_exit else "fail"
#   - Returns updated list (Pydantic frozen: create new instances via model_copy)
```

The parser must handle the ADR-0.0.73 Fidelity Assertions table format exactly
as authored. The `## Fidelity Assertions` block lives inside `## Decision`; the
parser should scan for the H2 heading `## Fidelity Assertions` and read the
table that follows it.

### Step 3: Create `src/gzkit/commands/adr_fidelity.py`

```python
# adr_fidelity_cmd(adr: str, check_only: bool = False) -> None
#   - resolve_adr_file(adr) to get the ADR path
#   - parse_fidelity_assertions(adr_path) — raises if block absent
#   - If check_only: print "Fidelity block parseable: N assertions" and exit 0
#   - Otherwise: run_fidelity_gate(assertions, adr_id)
#   - Report each assertion: claim, command, expected, observed, result (pass/fail)
#   - Print summary: N pass, M fail
#   - sys.exit(1) if any result == "fail"
```

### Step 4: Register `adr fidelity` in `src/gzkit/cli/parser_artifacts.py`

1. Add to the `_LAZY_DISPATCH` dict (or equivalent lazy map):
   `"adr_fidelity_cmd": "gzkit.commands.adr_fidelity"`
2. After the existing adr subparser registrations, add:
   ```python
   p_adr_fidelity = adr_commands.add_parser(
       "fidelity",
       help="Run an ADR's Fidelity Assertions against the running system",
       description="Parse and run the ## Fidelity Assertions block from an ADR's Decision.",
       epilog=build_epilog([
           "gz adr fidelity ADR-0.0.73-verification-layer-binding-audit",
           "gz adr fidelity ADR-0.0.73-verification-layer-binding-audit --check",
       ]),
   )
   p_adr_fidelity.add_argument("adr", help="ADR identifier (e.g. ADR-0.0.73-...)")
   p_adr_fidelity.add_argument(
       "--check",
       action="store_true",
       help="Parse-only: verify the Fidelity Assertions block is parseable (no commands run)",
   )
   p_adr_fidelity.set_defaults(
       func=lambda a: _lazy("adr_fidelity_cmd")(adr=a.adr, check_only=a.check)
   )
   ```

### Step 5: Create `docs/user/manpages/adr-fidelity.md`

Manpage covering: NAME, SYNOPSIS, DESCRIPTION, OPTIONS, EXIT CODES, EXAMPLES.
Follow the adr-audit-check.md structure. Include the `--check` flag.
Exit codes: 0 = all assertions pass (or --check, block parseable),
1 = any assertion fails, 2 = ADR file not found, 3 = block absent/malformed.

### Step 6: Update `docs/user/manpages/index.md`

Add `gz adr fidelity` row to the Governance table after `gz adr audit-check`:
```
| [`gz adr fidelity`](adr-fidelity.md) | Run ADR Fidelity Assertions against the running system |
```

### Step 7: Update `mkdocs.yml`

Add after the `gz adr audit-check` entry (line ~128):
```yaml
- gz adr fidelity: user/manpages/adr-fidelity.md
```

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
test -f src/gzkit/fidelity.py
test -f src/gzkit/commands/adr_fidelity.py
test -f tests/governance/test_adr_fidelity.py
```

## Notes

- `FidelityAssertion` fields `observed` and `result` are `None` before the gate
  runs; use `int | None` and `str | None` in Pydantic with `default=None`.
  This allows parsed-but-unrun assertions to exist as valid model instances.
- The parser targets the H2 heading `## Fidelity Assertions` inside the ADR
  file directly (not scoped to `## Decision`); the heading is unique enough.
- shlex.split() the command string before passing to subprocess.run() — matches
  the OBPI pipeline's single-program, shell-less invocation contract.
- The `--check` mode must NOT run any subprocess commands — parse only.
- Maintain exit-code discipline: 0=all pass, 1=any fail, non-zero for errors.
