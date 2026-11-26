---
name: gz-content-remember
description: Use when the operator says "remember X" for a control surface; captures the entry into its corpus, never the rendered file.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-11-26
metadata:
  skill-version: "0.3.0"
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
That is expected, not a defect: the tool prints the drift warning itself, ending with the
next step. Landing the entry is the rest of the chain, and an ordinary session runs it
rather than leaving the tree red:

```bash
uv run gz content land <surface> --attestor <who> --attestation-text "<verbatim>" --dry-run
uv run gz content land <surface> --attestor <who> --attestation-text "<verbatim>"
uv run gz agent sync control-surfaces    # playback writes the surface
```

`land` regenerates every consumer routed for the surface from the corpus and publishes them
under one attestation (ADR-0.35.0 § Decision 6). Its refusals name their recovery; one that
names a consumer with no committed rendition sends you to `gz-content-compose` to bootstrap it.

**Adding a corpus entry is ATTESTED** (operator ruling 2026-08-17): `gz content land`
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

- `gz-content-compose` — hand compression toward a setpoint, or bootstrapping a consumer `land` refuses
- `gz-advisor-qc` — records the information-retained-per-byte verdict on a hand-composed candidate
- `gz-agent-sync` — playback; the sole writer of rendered surfaces and their mirrors
- `gz-insights-remember` — for a session-local course-correction that is NOT canon
