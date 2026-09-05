# Unsupported-directory-barrier correction evidence

Persona: implementer. This is one reviewable correction in the isolated
`/private/tmp/gzkit-obpi04-assessment-4dt92ti0/correction` copy. The live checkout,
other snapshots, ledger, markers, locks, and OBPI completion state were not edited.

The governing plan at 234–236 says:

> Establish durable journal absence before deleting or reusing dependent recovery files,
> including when the journal is already absent on entry. Failure to establish that boundary
> preserves the files and exits non-zero.

The removed branch instead said:

> The unavailable case is DISCLOSED and the run proceeds; every other errno is a real fault and still refuses.

The correction restores the former disposition. Unsupported/invalid directory-sync
errors use the existing preservation and exit-2 refusals. Classification selects
a truthful capability remedy: an unchanged retry cannot repair the missing
operation; preserve recovery material and use an environment where the required
directory sync succeeds before retrying. Existing transient-fault guidance stays.

## Changed files

- `src/gzkit/commands/content/unown.py`: remove the unsupported-error warning/return;
  route through existing refusal branches; share the two branches' capability
  remedy; remove comments claiming unsupported errors authorize weaker cleanup.
- `src/gzkit/content/ownership.py`: correct the errno-classification documentation
  and state that the existing Windows no-op does not establish equivalent
  durability. The shared writer/barrier implementation is unchanged.
- `tests/commands/test_content_unown.py`: replace the unauthorized warning-success
  test with three behavior tests, keeping the transient-failure test. Each new
  test exercises `EINVAL`, `ENOSYS`, `ENOTSUP`, and `EOPNOTSUPP` by failing actual
  directory `os.fsync` calls while allowing regular-file fsync to execute.
- `docs/user/manpages/content.md`: document preservation/exit 2 for unsupported
  required operations and the non-transient remedy, with Windows explicitly
  unproved.

## RED then GREEN

All commands ran with this working directory and environment:

```bash
cd /private/tmp/gzkit-obpi04-assessment-4dt92ti0/correction
export UV_CACHE_DIR=/tmp/gzkit-health-uv-cache
export PYTHONPATH=/private/tmp/gzkit-obpi04-assessment-4dt92ti0/correction/src:/private/tmp/gzkit-obpi04-assessment-4dt92ti0/correction
```

Before production edits:

```bash
uv run --no-sync --project /Users/jeff/Documents/Code/gzkit python -B -m unittest -v tests.commands.test_content_unown.TestUnavailableBarrierPreservesRecoveryMaterial
```

Observed **exit 1; 4 methods; 24 assertion/subtest failures; zero errors**.
The failures show new snapshot creation on fresh entry or deletion of the real
retained snapshot/extract on cleanup. The existing transient-failure test passed.
Full output: `correction-unsupported-red.log`.

After the source correction, the same focused class returned **exit 0; 4 methods
passed** (`correction-unsupported-green.log`). The final tests additionally check
that the declaration bytes remain unchanged after each refused retry.

Final scoped baseline:

```bash
uv run --no-sync --project /Users/jeff/Documents/Code/gzkit python -B -m unittest -v tests.commands.test_content_unown tests.content.test_ownership tests.commands.test_validate_ownership_declarations
```

Observed **exit 0; 183 tests passed**, including the final strengthened tests.
Full output: `correction-scoped-tests.log`.

Each new behavior test executes two faulted retries and then a healed retry for
each named errno. Faulted runs attempt the directory fsync, retain byte-identical
dependents, preserve declaration/ledger, and exit 2. After healing, fresh work
completes; already-witnessed cleanup leaves exactly one witness and canonical
loader acceptance. A healed cleanup-only invocation may return the existing
already-unowned exit 1 after clearing the residue; it is not treated as a new
transition or an unresolved storage fault.

Final static checks, each observed exit 0:

```bash
uv run --no-sync --project /Users/jeff/Documents/Code/gzkit ruff check src/gzkit/commands/content/unown.py src/gzkit/content/ownership.py tests/commands/test_content_unown.py
uv run --no-sync --project /Users/jeff/Documents/Code/gzkit ruff format --check src/gzkit/commands/content/unown.py src/gzkit/content/ownership.py tests/commands/test_content_unown.py
uv run --no-sync --project /Users/jeff/Documents/Code/gzkit ty check src/gzkit/commands/content/unown.py src/gzkit/content/ownership.py tests/commands/test_content_unown.py
```

Ruff and ty reported `All checks passed!`; format reported `3 files already formatted`.
Imports of `gzkit.commands.content.unown`, `gzkit.content.ownership`, and the fixture
module were explicitly observed under the `correction` copy.

## Final file identity and limits

| File | SHA-256 |
|---|---|
| `src/gzkit/commands/content/unown.py` | `99f7c18d01e4f0ad03cfeebea36bf383e14bfcf88cf8106e68bd8cab2fee8e64` |
| `src/gzkit/content/ownership.py` | `93dfb8c3b3df1dadfa3d16dc477dbb0aee33abeb632c1d770d2b257c46cc591d` |
| `tests/commands/test_content_unown.py` | `39e57c88a1d0ab282f34c7fda451732d7f0394738caeb3497a5c011c358f61db` |
| `docs/user/manpages/content.md` | `9cdd47e646ce4fe5d5d4a1fdb357b2e72bda570c54ff56279e6b1eb681b7d105` |

This proves scoped POSIX OS-fault handling and retry behavior, not a physical
power-loss experiment or actual NFS-host behavior. Equivalent Windows durability
remains unproved and its implementation is unchanged. Accepted ledger exceptions
#952/#953 remain unchanged. No new recovery state, exit code, platform policy,
full-suite claim, commit, or OBPI-completion claim is introduced.
