# /gz-content-compose

Validate and stage a candidate rendition from the corpus via `gz content compose`.
Use when the operator or agent has composed a compressed candidate text and wants
the tool to validate invariant-floor compliance, compute byte evidence, write the
candidate artifact, and emit a ledger event.

---

## Purpose

`gz content compose` is the **compress** stage of the ADR-0.0.37 CMS pipeline
(`corpus → compress → rendition → playback`). The agent supplies the candidate
text (the result of drop/combine/rewrite compression judgment on the compressible
corpus entries); the tool validates, accounts bytes, and writes the candidate to
`.gzkit/renditions/<surface>/<consumer>.candidate.md`.

The tool is **deterministic**: NO LLM call, NO network I/O. The compression
judgment is the agent's. The tool **never writes a rendered surface** —
`AGENTS.md`, `CLAUDE.md`, and mirrors are byte-unchanged after a compose run.

## Invocation

```bash
gz content compose <surface> --consumer <vendor> --candidate <file>
gz content compose AGENTS.md --consumer root --candidate /tmp/candidate.md
cat /tmp/candidate.md | gz content compose AGENTS.md --consumer root
```

- `--consumer` is required; must match a vendor declared in `data/vendor-manifest.json`.
- `--candidate` is the path to the candidate rendition file; omit to read from stdin.
- The command **fails closed** (non-zero exit, no candidate written) when:
  - the corpus store for `<surface>` does not exist
  - the `(surface, consumer)` setpoint is undeclared
  - the candidate drops or rewrites any `tier: invariant` corpus entry

## Validation

- A candidate file is written to `.gzkit/renditions/<surface>/<consumer>.candidate.md`.
- Rendered surfaces (`AGENTS.md`, `CLAUDE.md`, mirrors) are byte-unchanged.
- A `composition_candidate_emitted` ledger event carries `surface`, `consumer`,
  `setpoint`, and per-tier byte evidence.

## Example

```bash
# Compose a candidate for the AGENTS.md corpus toward the Codex (lite) setpoint
gz content compose AGENTS.md --consumer root --candidate /tmp/candidate.md

# Confirm candidate landed; AGENTS.md is byte-unchanged
test -s .gzkit/renditions/AGENTS.md/root.candidate.md
git diff --exit-code AGENTS.md

# Confirm the ledger records the compose event
grep "composition_candidate_emitted" .gzkit/ledger.jsonl
```

## Related

- `gz-content-remember` — the corpus write path (corpus → compose feeds this)
- [`gz content`](../manpages/content.md) — full subcommand reference
- ADR-0.0.37-constitutional-invariant-composition — parent ADR
