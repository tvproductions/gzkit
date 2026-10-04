---
name: gz-content-remember
description: Capture an addressed entry into a surface's append-only corpus via gz content remember, never editing a rendered surface. Use when an operator says "remember X" for a control surface (AGENTS.md, CLAUDE.md) or an agent course-correction should persist to the corpus source of truth.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-08-21
metadata:
  skill-version: "0.2.0"
model: haiku
gz_command: gz content remember
---

# gz content remember

## Overview

Wield `gz content remember` to append one addressed, provenanced entry to a surface's
append-only corpus store at `.gzkit/corpus/<surface>.jsonl`. This is the **write path** of
the corpus pipeline (`corpus → compress → rendition → playback`): capture grows the source
of truth; deterministic playback remains the sole writer of rendered surfaces. Capture
NEVER edits AGENTS.md, CLAUDE.md, or any mirror — that is the load-bearing invariant.

The live owner is `ADR-0.35.0-canon-entry-corpus-landing`. The pipeline originated under
`ADR-0.0.37`, which went terminal 2026-07-18 (§ Terminal Disposition, Split-and-Supersede)
with its registry-spine OBPIs permanently withdrawn — cite the successor, never the
terminal ADR, when routing work.

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
     [--origin <provenance>] [--witness <who-vouches>]
   ```

   `--origin` records HOW the capture arrived (a GHI, a session id, an operator-directive
   date). `--witness` records WHO vouches for it. Both are recorded provenance, never gates.
4. The command fails closed (non-zero exit, no write) when the surface is unknown or the
   section resolves to no template-defined section — an unaddressable entry is never stored.

## Capture is half the job — know what it leaves behind

`remember` moves the corpus and nothing else. The committed rendition now no longer derives
from the corpus, so **`gz check` goes RED immediately** on `gz validate
--rendition-freshness` and, for an `invariant`-tier entry, `--rendition-floor-coherence`.
That is expected, not a defect: the tool prints the drift warning itself. Landing the entry
is the rest of the chain, and an ordinary session runs it rather than leaving the tree red:

```bash
gz content compose <surface> --consumer <vendor> --candidate <file>   # /gz-content-compose
gz content advise-rendition <surface> --consumer <vendor> --score N --explanation "..."
gz content commit <surface> --consumer <vendor> --attestor <who> --attestation-text "<verbatim>"
gz agent sync control-surfaces                                        # playback writes the surface
```

**Adding a corpus entry is ATTESTED** (operator ruling 2026-08-17): `gz content commit`
fail-closes without `--attestor` and `--attestation-text` when canon moved. Attestation
attaches to the canon change, never to the Layer-3 rendition, and it is **corpus
attestation — never call it Gate 5** (that name is reserved for OBPI/ADR completion,
ADR-0.0.36). Pass the operator's verbatim words unchanged; never invent them.

**Capture must never be blocked** (`ADR-0.35.0` § Decision 7): losing the operator's words
is strictly worse than a red tree. If the chain above cannot be finished this session,
`remember` still runs first.

## Validation

- A new line is appended to `.gzkit/corpus/<surface>.jsonl` (the file/dir is created on first use).
- The rendered surface is byte-unchanged (`git diff --stat -- AGENTS.md CLAUDE.md` is empty).
- A `corpus_entry_appended` ledger event is emitted carrying `surface`, `section`, `entry_id`, `tier`.

## Example

```bash
# Remember a compressible note for AGENTS.md (never touches AGENTS.md itself)
gz content remember AGENTS.md --section "Behavior Rules" \
  --text "Prefer stdlib JSONL for append-only stores." --tier compressible

# Remember an invariant-tier operator directive with provenance
gz content remember AGENTS.md --section operator-doctrine-verbatim-canon \
  --text "YOU OWN THE WORK COMPLETELY." --tier invariant \
  --classification Promotable --origin operator-directive-2026-08-21
```

## Related Skills

- `gz-content-compose` — the next step; stages and validates the candidate rendition
- `gz-advisor-qc` — records the information-retained-per-byte verdict the operator cites
- `gz-agent-sync` — playback; the sole writer of rendered surfaces and their mirrors
- `gz-insights-remember` — for a session-local course-correction that is NOT canon
