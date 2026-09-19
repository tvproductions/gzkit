# Current native delivery — 2026-09-19

Persona: main-session. Work order: GHI #1046. Baseline:
`da741ef0d6c924c4b6b62bd75f8c1431faddcae2`.

**All four sampled native instruction chains arrive whole.** Installed
`codex-cli 0.155.1` rendered fresh prompts with `codex debug prompt-input` from
the root, commands, tests and governance-docs directories. No model task was
started. Existing trust/configuration were retained; only `sqlite_home` was
redirected to temporary storage. Raw prompts remain temporary, not published.

| Starting directory | Source bytes | Native inner-block bytes | Exact full chain |
|---|---:|---:|---|
| Root | 19,872 | 19,872 | yes |
| src/gzkit/commands | 55,368 | 55,374 | yes |
| tests | 35,959 | 35,961 | yes |
| docs/governance | 27,331 | 27,335 | yes |

Inner blocks include two newline separator bytes between files. The comparison
checks equality with the complete ordered source chain, not a substring or a
size threshold. [delivery.json](delivery.json) retains per-file hashes, offsets,
byte counts and whole-chain equality, plus hashes of native prompts.

A separate invocation overrode `project_doc_max_bytes=12000` on the command line
only. It returned exactly the first 12,000 source bytes, and full-chain equality
failed as expected. This negative control verifies the measurement detects
truncation. Neither the configured repository cap nor trust settings changed.

The [September 12 audit](../../governance/context-audit-2026-09-12/delivery.md)
observed commands/tests truncation on CLI 0.154.0 with a 48,511-byte root.
Current root is 19,872 bytes. The old truncation finding is historical, not a
current failure in these sampled paths. Both repository and CLI changed, so
this is an observed before/after state, not an isolated causal experiment.

Every current probe also carries a 22,187-byte native skills-instructions block.
That is catalog/discovery material, not the sum of available skill bodies.
Do not compare it with the repository-only Claude metadata estimate as though
they measured the same consumer or with a byte/4 estimate of model tokens.

This witnesses installed CLI prompt assembly. It does not inspect the complete
active desktop conversation, establish automatic hook execution, prove native
Claude delivery, test instruction refresh after a tool changes directory, or
show that a model obeys the delivered instructions. Existing hook registrations
and source-size measurements are not substituted for those observations.
