---
name: gz-content-compose
description: Validate and stage a candidate rendition from the corpus via gz content compose. Use when the agent has made compression decisions (drop/combine/rewrite of compressible corpus entries toward the declared setpoint) and wants the tool to validate invariant-floor compliance, compute byte evidence, write the candidate artifact, and emit a ledger event.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-06-14
model: sonnet
gz_command: gz content compose
skill-version: 1.0.0
---

# gz-content-compose

## Overview

Wield `gz content compose` to validate and stage a **candidate rendition** of a
control surface toward a target consumer (vendor) at the declared compression
setpoint. This is the **compress** stage of the ADR-0.0.37 CMS pipeline:
`corpus → compress → rendition → playback`.

**The tool is deterministic.** NO LLM call, NO network I/O. The
drop/combine/rewrite compression judgment is the **agent's** (this skill is the
LLM surface). The tool validates, accounts bytes, and writes the candidate.

**The tool NEVER writes a rendered surface.** `AGENTS.md`, `CLAUDE.md`, and
their mirrors are byte-unchanged after every compose run. Only the candidate
artifact under `.gzkit/renditions/` and the ledger change.

## Workflow

1. **Read the corpus** for the target surface:
   - `.gzkit/corpus/<surface>.jsonl` — the append-only source of truth
   - Identify `tier: invariant` entries — these MUST appear verbatim in the candidate
   - Identify `tier: compressible` entries — these can be dropped, combined, or rewritten
2. **Know the setpoint** — resolve via `gz validate --setpoint-coherence` or read
   `data/vendor-manifest.json` `content_type_temperatures.<ContentType>.<consumer>`.
   The setpoint is `lite`, `medium`, or `heavy`.
3. **Draft the candidate text** — compress the compressible entries toward the setpoint:
   - `lite`: maximum compression; include only the highest-priority compressible entries
   - `medium`: balanced compression
   - `heavy`: minimal compression; include most compressible content
   - Invariant-tier entries MUST appear verbatim (0-Kelvin floor — no exceptions)
4. **Write the candidate to a temp file** (e.g. `/tmp/candidate.md`)
5. **Run the compose tool** to validate + stage:

```bash
gz content compose <surface> --consumer <vendor> --candidate /tmp/candidate.md
```

6. **Confirm the output** — check byte evidence and candidate path:

```bash
test -s .gzkit/renditions/<surface>/<consumer>.candidate.md
gz ledger tail --event composition_candidate_emitted
```

7. The candidate flows to the advisor-QC loop (OBPI-24) and operator attestation
   (OBPI-22) before promotion to a committed rendition.

## Output Contract

On success (`exit 0`):
- Candidate written to `.gzkit/renditions/<surface>/<consumer>.candidate.md`
- `composition_candidate_emitted` ledger event carrying `surface`, `consumer`,
  `setpoint`, and per-tier byte evidence
- Byte evidence printed to stdout

On failure (`exit 1`):
- No candidate written
- Error to stderr naming the cause (absent corpus / undeclared setpoint / invariant violation)

## Do Not

- Call any Anthropic/LLM API in tool code — the tool is deterministic; this skill IS the LLM surface
- Auto-promote the candidate to a committed rendition — that is OBPI-22 scope
- Rewrite or drop `tier: invariant` entries in the candidate text
- Claim compose is complete without running `gz content compose` and confirming `exit 0`
- Edit `AGENTS.md`, `CLAUDE.md`, or any mirror during this skill — rendered surfaces are never touched
