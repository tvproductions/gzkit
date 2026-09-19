# Empty-tier documentation repair evidence

Dated 2026-09-19; GHI #1047. Persona: main-session.

Authority: `ce234a0fbebbb1e5eef379ddb235777b6a477824` (GHI #724) established
the adopter opt-in. Current `SmokeConfig` and `smoke_gate` preserve it.
The finding is omitted documentation consumers of that settled behavior.

| Required state / consumer | Observed evidence |
|---|---|
| Empty tier, required absent | Temporary project call returned 0, advisory guidance. |
| Empty tier, required false | Temporary project call returned 0, advisory guidance. |
| Empty tier, required true | Temporary project call returned 3, breach recovery. |
| Executable behavior unchanged | AST comparison against baseline, removing docstrings, was identical for both source files and the test module. |
| Policy explanations agree | Independent reviewer accepted rule, skill, manpage, audit row, history and docstrings against the three-state contract. |
| Delivered explanations agree | Packaged rule and three skill mirrors byte-equivalent; Claude rule has generated header; nested tests instructions contain the complete amended body. |

Observed checks:

```text
uv run --no-sync python -m unittest tests.test_smoke_gate.EmptyTierIsABreachWhenRequired tests.test_smoke_gate.MarkerIsMetadataOnly
Ran 6 tests in 0.004s
OK

uv run -m unittest tests.test_smoke_gate -q
Ran 13 tests
OK

uv run gz validate --surfaces --advisory-scorecard
All validations passed (2 scopes)
```

The second test run was performed by the independent reviewer. No new behavioral
test was added for prose-only changes; existing semantic tests already cover the
opt-in boundary. No heavy runtime contract changed and no Gate-5 attestation is
claimed. Historical quotations remain dated history with the clarification above
them. The review found no unresolved member of the scoped documentation family.

Full staged repository verification and the resulting commit are recorded in
the GHI closure evidence after execution; the focused results above are not
presented as a substitute for that gate.
