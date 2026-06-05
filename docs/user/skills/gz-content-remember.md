# /gz-content-remember

Capture an addressed entry into a surface's append-only corpus via `gz content remember`, never editing a rendered surface. Use when an operator says "remember X" for a control surface (AGENTS.md, CLAUDE.md) or an agent course-correction should persist to the corpus source of truth.

---

## Purpose

`gz content remember` is the **write path** of the ADR-0.0.37 corpus pipeline
(`corpus → compress → rendition → playback`). It appends one addressed,
provenanced entry to the append-only corpus store at
`.gzkit/corpus/<surface>.jsonl` and emits a `corpus_entry_appended` ledger
event. It **never edits a rendered surface** — capture grows the source of
truth; deterministic playback remains the sole writer of AGENTS.md, CLAUDE.md,
and their mirrors.

## Invocation

```bash
gz content remember <surface> --section <id> --text "<prose>" \
  [--tier invariant|compressible] \
  [--classification Mechanical|Promotable|Judgment|Ambiguous] \
  [--origin <provenance>]
```

- `--section` is normalized to the surface's kebab-case `Pillar` id (so
  `"Behavior Rules"` resolves to `behavior-rules`).
- `--tier invariant` marks entries emitted verbatim at every compression
  setpoint; `--tier` defaults to `compressible`.
- The command **fails closed** (non-zero exit, no entry written) when the
  surface is unknown or the section resolves to no template-defined section.

## Validation

- A new line is appended to `.gzkit/corpus/<surface>.jsonl` (created on first use).
- The rendered surface is byte-unchanged.
- A `corpus_entry_appended` ledger event carries `surface`, `section`, `entry_id`, `tier`.

## Example

```bash
gz content remember AGENTS.md --section "Behavior Rules" \
  --text "Prefer stdlib JSONL for append-only stores." --tier compressible
```

## Related

- [`gz content`](../manpages/content.md) — the command group; see § remember
- ADR-0.0.37 — Constitutional Invariant Composition (corpus pipeline)
- `gz-context-diet` — the read/trim-side counterpart to this write-side skill
