# Bounded source-impact measurement

Dated 2026-09-19. Persona: main-session. Investigation:
[GHI #1052](https://github.com/tvproductions/gzkit/issues/1052).
Source baseline: `08655b31b854e2f016b53bd638e3423e71936c13`.
Parent: [implementation plan](../three-pillars-implementation-plan-2026-09-19.md),
row 4. This record measures existing components; it changes no runtime contract.

## Finding and disposition

Package grouping compresses the presentation, but import-only discovery is
insufficient for the proposed change-impact assistance. The config-path command
has live CLI dispatch consumers while both parsers report zero importing source
files. Increasing traversal depth cannot recover a missing relationship type.
Keep the full import view as one source of advisory evidence; do not treat it as
a complete impact answer or a dependency authority for proof currency.

The boundedness question is only partly answered. Counts are measured; actual
human review time and omission reduction in use are not. No numeric cap, new
gate, runtime feature, or successor ADR is justified by these counts alone.

## Method and reproducibility

[measure.py](measure.py) loads the configured source root, discovers and hashes
all Python inputs, freshly builds both existing parser adapters without writing
an index, and verifies that the source roster and bytes remain unchanged during
capture. [results.json](results.json) records that roster, parser package and
Python versions, configuration hash, oracle hash, edges and complete file lists.
The baseline field deliberately identifies this dated experiment; a rerun on a
later checkout requires interpreting its changed hashes, not trusting that label.

Run from the repository root (observed exit 0):

```bash
uv run python docs/evals/three-pillars-impact-2026-09-19/measure.py docs/evals/three-pillars-impact-2026-09-19/results.json
```

This also writes `oracle-comparison.json` alongside the selected output. Use a
`/tmp/` output path to reproduce without replacing the dated committed results. The script does not
write source, persisted indexes, pipeline state or ledger events. Source
stability is measured; the separate unified projection is a live derived view,
not a frozen ledger snapshot. The dated production census has its own ledger
hash in [production-status.md](production-status.md).

An independent reader recorded [oracle.json](oracle.json) before seeing the
measurement output. It contains positive witnessed consumer relationships and
three separately labeled upstream dependencies. It is deliberately not an
exhaustive census. The comparison measures membership of those witnesses in the
candidate file lists, not population recall, precision, or causal relevance of
every candidate. File-level membership does not prove that the same relationship
was resolved: the two-hop match for the CLI re-export is such a case.

## Observed populations

Both adapters scanned 510 Python files, produced 5,903 coupling edges and
reported zero parse failures. They agreed on these four sampled views; that is
adapter agreement, not independent proof of completeness. Edge direction is
importer → imported unit; the table queries incoming edges for each seed.

| Changed unit under configured source root | Direct importing files | Package groups | Files within two incoming hops | Hidden files |
|---|---:|---:|---:|---:|
| `gzkit/governance/brief_path_validity.py` | 9 | 5 | 27 | 0 |
| `gzkit/commands/config_paths.py` | 0 | 0 | 0 | 0 |
| `gzkit/commands/common.py` | 95 | 11 | 127 | 0 |
| `gzkit/__main__.py` | 0 | 0 | 0 | 0 |

The shared helper's 11 groups still contain 95 files. Grouping provides an
initial navigation structure; it does not remove the obligation to inspect
relevant members. The two-hop view expands the population without solving
registry, subprocess or non-Python omissions. No review-time savings are claimed.

Of 25 downstream witnesses in the bounded oracle, 8 appear in the direct view
and 9 in the two-hop view. The three upstream witnesses are excluded from that
denominator. [oracle-comparison.json](oracle-comparison.json) preserves every
row, including omissions. In particular:

- The three witnessed production consumers of the mirror validator appear.
  Its tests and command documentation lie outside the scanned source population.
- `parser_handler_manifest.py` maps the config-path handler to a module string;
  `_lazy` imports that module. `parser_maintenance.py` invokes that registered
  handler. Neither relationship is represented by an ordinary target import.
- Tests invoke the module entry point through subprocess arguments. Zero
  importing source files for `__main__.py` therefore does not mean zero consumers.
- Scaffold text, configuration meaning, documentation, skill invocations and
  executable chore JSON remain separate semantic relationships.

All four source-path queries against the unified artifact graph reported
`materialized: false` and empty reachability. This graph expressly omits coupling
edges and does not materialize every source file. Those empty results are not
comparable evidence of no impact. Artifact lineage remains useful for declared
obligations, with a different node population and relationship meaning.

## Controls and limitations

For each adapter, isolated controls verified that a new absolute-import consumer
appears, a rename replaces its path, deletion removes it, malformed source is
reported as a parse failure, and an outside-root seed is identified as unscanned.
A re-export consumer appeared only in the two-hop view. A relative import was
omitted by both adapters: this is an exposed limitation, not a passing claim of
relative-import coverage. The control assertions fail if the required observed
behavior changes; results retain the unsupported case separately.

The experiment neither resolves arbitrary dynamic loading nor discovers all
runtime data, absent-file, environment, generated or external consumers. It does
not run changed behavior, measure model comprehension, or narrow proof inputs.
The independent oracle records those boundaries instead of defining them away.

## Concrete feature recommendation

Revise the proposed product to a typed advisory change report with three
separately attributed evidence sections: static importing source, known CLI
handler registrations, and test consumers. Keep declared requirement/document
links separate and explicitly distinguish witnessed links from unsupported or
unsearched classes. Use existing parser and handler-manifest evidence; do not
promise a general dynamic-dependency resolver.

Default to direct package groups with full file detail and an optional two-hop
view. An empty section must say which population and relationship types were
searched. Every link needs its actual witness and producer identity. Acceptance
must include the presently missed config-path registry chain and module-entry
subprocess tests, plus parse, roster and high-fanout controls above. A subsequent
feature pilot must measure human review effort and missed-consumer recovery;
this study supplies baseline cases, not that outcome.

This is a revised design recommendation awaiting an operator ruling. It remains
subject to ADR-0.37.0's successor condition and the active campaign sequence.
The investigation can close with its measurement deliverable; the runtime
feature cannot be described as implemented. Retain broad proof currency under
#1029, and leave #1028 open for a normally initiated production OBPI.

## Verification note

The first commit attempt was stopped by the secret scanner: it interpreted the
source hash beside the `handoff_api.py` roster key as a generic API credential.
The value was verified against SHA256 of that source file. Roster entries now
label each value in a `sha256` field, separating path identity from digest type;
no secret was removed or scanner exception added. The capture and required
checks were rerun after this representation change.
