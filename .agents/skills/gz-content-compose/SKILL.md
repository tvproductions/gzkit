---
name: gz-content-compose
description: Validate and stage a candidate rendition from the corpus via gz content compose. Use when the agent has made compression decisions (drop/combine/rewrite of compressible corpus entries toward the declared setpoint) and wants the tool to validate invariant-floor compliance, compute byte evidence, write the candidate artifact, and emit a ledger event.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-09-25
metadata:
  skill-version: "1.1.0"
model: sonnet
gz_command: gz content compose
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
grep "composition_candidate_emitted" .gzkit/ledger.jsonl
```

7. The candidate flows to the advisor-QC loop (OBPI-24) and operator attestation
   (OBPI-22) before promotion to a committed rendition.

## Before commit: the retention map

`gz content commit` enforces a retention gate (ADR-0.35.0 § Decision item 10,
GHI #1090/#1091; manpage `content` § "Retention gate: `--retention-map`") when
the candidate drops a block the consumer's prior **committed** rendition
carried. The gate proves only bytes; whether the extraction was independent,
whether a KEPT span carries its quote's meaning, and whether the operator
actually ruled each drop live in this procedure, not in the tool. Before
running `commit`:

1. **Find the removed blocks before committing.** Compare the consumer's
   committed rendition `.gzkit/renditions/<surface>/<consumer>.md` with the
   candidate block by block (a block is a heading, paragraph, list item or
   table row; a fenced code block is one block); every prior block whose text
   does not appear in the candidate is removed. No committed rendition, or no
   removed block, means no map is needed. `gz content commit` has **NO dry
   run**: without a map it exits 3 and names each removed block, but when
   nothing was removed it **PROMOTES** (exit 0) — never run it as a probe
   with attestation words the operator did not say.
2. **Dispatch an independent reviewer** — a different model from the author
   wherever one is available; otherwise a fresh-context agent, and say so —
   to extract the binding conditions of each removed block, verbatim. The
   reviewer's identity goes in `extracted_by`; it must differ from
   `mapped_by`.
3. **The author (you) maps each condition**: KEPT with the verbatim candidate
   span that carries it, or DROPPED with a reason; sentences that bind
   nothing go in `non_binding` with a reason. Every meaningful character of
   each removed block must be covered.
4. **The reviewer verifies every KEPT pair** (quote -> span) for sameness of
   meaning, and every `non_binding` exemption; the tool checks only byte
   presence. Record the reviewer's verdict on each pair, and present it to
   the operator alongside the DROPPED ids in step 5.
5. **Present every DROPPED condition to the operator by id** (e.g. `C2`),
   with its quote and reason, and obtain the operator's own words ruling
   each drop. Never author attestation text the operator did not say.
6. **Commit with `--retention-map <file>`** and the operator's words in
   `--attestation-text`, which must contain every DROPPED id at a token
   boundary. On exit 3, read every named violation and repair the map; never
   delete a condition to make the refusal go away.

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
- Promote the candidate (`gz content commit`) except through § Before commit: the retention map, with the operator's own attestation words
- Rewrite or drop `tier: invariant` entries in the candidate text
- Claim compose is complete without running `gz content compose` and confirming `exit 0`
- Edit `AGENTS.md`, `CLAUDE.md`, or any mirror during this skill — rendered surfaces are never touched
- Mark a condition KEPT at a candidate span that does not carry its removed quote's meaning — byte presence is not sameness of meaning
- Author or paraphrase the operator's drop ruling — a DROPPED condition's attestation words must be the operator's own, never invented on their behalf
