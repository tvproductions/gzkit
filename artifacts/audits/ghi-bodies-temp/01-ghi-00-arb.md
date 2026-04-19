## Class of failure

`.gzkit/rules/arb.md:58-64` lists example ARB invocations. Line 62:
`uv run gz arb ty check . --exclude 'features/**'`

This is the exact command `.gzkit/rules/attestation-enrichment.md:67-72` forbids as the GHI #199 anti-pattern. The rule file meant to teach operators and agents how to use ARB actively recommends the broken command.

An agent reading `arb.md` and copying the example will produce a receipt whose `step.command` diverges from the canonical `gz typecheck` gate (`ty check src`) — exactly the failure #199 closed.

## Evidence

`.gzkit/rules/arb.md:58-64`:
```
uv run gz arb ruff
uv run gz arb ruff --fix
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb ty check . --exclude 'features/**'
uv run gz arb coverage run -m unittest discover -s tests -t .
```

`.gzkit/rules/attestation-enrichment.md:67-72`:

> `gz arb typecheck` (added under GHI #199) wraps `uv run ty check src` — the same command `gz typecheck` and `gz closeout` invoke. Do not author heavy-lane type-check receipts via `gz arb ty check <custom-scope>`; the receipt will drift from the gate and the attestation claim will be post-hoc false.

## Fix plan

Replace `arb.md:62` with:
```
uv run gz arb typecheck    # wraps `ty check src` per attestation-enrichment.md
```

Also add a one-line cross-reference at the top of the `## Available Commands` section pointing at the canonical command table in `attestation-enrichment.md` so future drift between the two files is self-evident.

## Routing

Direct-fix per `.gzkit/rules/defect-fix-routing.md`. ≤5 lines, single file, in-flight defect, unit-testable. Commit: `fix(rules): align arb.md example with attestation-enrichment canon (GHI #225)`.

## Tracked under

Umbrella GHI #224 (4.7 regression — governance surface hardening).
