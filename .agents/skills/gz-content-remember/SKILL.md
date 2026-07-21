---
name: gz-content-remember
description: Capture an addressed entry into a surface's append-only corpus via gz content remember, never editing a rendered surface. Use when an operator says "remember X" for a control surface (AGENTS.md, CLAUDE.md) or an agent course-correction should persist to the corpus source of truth.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-06-05
metadata:
  skill-version: "0.1.0"
model: haiku
gz_command: gz content remember
---

# gz content remember

## Overview

Wield `gz content remember` to append one addressed, provenanced entry to a surface's
append-only corpus store at `.gzkit/corpus/<surface>.jsonl`. This is the **write path** of
the ADR-0.0.37 corpus pipeline (`corpus → compress → rendition → playback`): capture grows
the source of truth; deterministic playback remains the sole writer of rendered surfaces.
Capture NEVER edits AGENTS.md, CLAUDE.md, or any mirror — that is the load-bearing invariant.

## Workflow

1. Identify the target **surface** (an existing control surface, e.g. `AGENTS.md`) and the
   **section** the entry belongs to. The section is matched against the surface's
   template-defined sections (kebab-case `Pillar` ids); a title like `"Behavior Rules"` is
   normalized to `behavior-rules` automatically.
2. Choose the **tier**: `invariant` (emitted verbatim at every compression setpoint — for
   omnipresent rules like PRIME DIRECTIVE) or `compressible` (default; condensable prose).
3. Run the capture:

   ```bash
   gz content remember <surface> --section <id> --text "<prose>" \
     [--tier invariant|compressible] [--classification Mechanical|Promotable|Judgment|Ambiguous] \
     [--origin <provenance>]
   ```

4. The command fails closed (non-zero exit, no write) when the surface is unknown or the
   section resolves to no template-defined section — an unaddressable entry is never stored.

## Validation

- A new line is appended to `.gzkit/corpus/<surface>.jsonl` (the file/dir is created on first use).
- The rendered surface is byte-unchanged.
- A `corpus_entry_appended` ledger event is emitted carrying `surface`, `section`, `entry_id`, `tier`.

## Example

```bash
# Remember a compressible note for AGENTS.md (never touches AGENTS.md itself)
gz content remember AGENTS.md --section "Behavior Rules" \
  --text "Prefer stdlib JSONL for append-only stores." --tier compressible

# Remember an invariant-tier rule (emitted verbatim at every setpoint)
gz content remember AGENTS.md --section prime-directive \
  --text "YOU OWN THE WORK COMPLETELY." --tier invariant
```
