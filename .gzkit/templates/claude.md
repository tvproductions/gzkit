# CLAUDE.md

> **Doctrine:** CLAUDE.md redirects to AGENTS.md. The Claude-specific addenda below extend the universal contract; they do not replace it. (GHI #525.)

@AGENTS.md

### Invariant 10a — skill-tool-invoke-same-turn

When a skill step names a tool (`EnterPlanMode`, `ExitPlanMode`, etc.), invoke it in the same turn. Ending the turn with "Required next step" instead of calling the tool is a violation. **(Advisory — no mechanical witness, and none is planned.)** A check would have to attribute a turn's tool calls to a skill step's semantics; gzkit models neither a turn nor a skill's step graph (the unmodelled-caller ground of `advisory-rules-audit.md` row 62b). Scored **Judgment** at row 53a; it had sat unrowed in that audit's prose as "promotable" with the signal-to-noise objection already recorded and no observed instance. Reclassify on a named session where a skill step named a tool, the turn ended without it, and nothing caught it.

### Model tuning

Effort is a dial to re-baseline per workload, never a fixed default — on Opus 5 the effort/quality curve is non-monotonic (Claude Opus 5 System Card § 8.4: FrontierCode peaks at `medium` and *declines* above `high` because the model makes out-of-scope edits; § 8.5: FrontierBench peaks at `xhigh`). Start at `high`, sweep, and hold the scope boundary explicit — an in-prompt scope instruction "recovered performance on most of these tasks" (§ 8.4). Reserve `max` for genuinely hard problems. Per-turn thinking prompts: *"Think carefully and step-by-step"* (hard) or *"Prioritize responding quickly"* (light). See [`docs/governance/opus-tuning.md`](docs/governance/opus-tuning.md) for full calibration guidance; GPT-side sessions calibrate via [`docs/governance/gpt-tuning.md`](docs/governance/gpt-tuning.md) (gzkit runs with either vendor; current cards registry-rotated in `data/frontier_model_cards.json`).

## Compact Instructions

When compacting context (`/compact`), preserve:

- Active pipeline ID and current stage (from `uv run gz obpi status <OBPI-ID>`)
- Active OBPI ID and brief status (lane, gates passed, attestation state)
- Gate pass/fail state for the current ADR (from `uv run gz status`)
- Pending attestation requirements (which Gate 5 awaits human witness)
- Any unresolved defects or blockers (GHIs in scope, insights logged)
- The current TASK ID if one is open (`uv run gz task list --active`)

The ledger (`.gzkit/ledger.jsonl`) is the system-of-record; compaction must
not drop references to live ledger events for the current session's ADR.
