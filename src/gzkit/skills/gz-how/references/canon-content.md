# Canon content

You are here when AGENTS.md or another canon-sourced control surface should say
something different. Rendered surfaces are playback of an append-only corpus;
edit the corpus, never the rendering.

## Steps

1. **`gz-content-remember`** — `uv run gz content remember` appends the entry
   to the surface's corpus.
2. **Attest and land** — `uv run gz content land <surface>` regenerates every
   routed consumer from the corpus and publishes them under the operator's one
   corpus attestation.
3. **`gz-agent-sync`** — play the committed rendition back onto the surfaces.

## Branches

- **Compress toward a setpoint, or bootstrap a consumer `land` refuses** →
  **`gz-content-compose`** stages a hand-composed candidate, **`gz-advisor-qc`**
  records its retention verdict, and `uv run gz content commit` promotes it.
- **Per-turn instructions have grown heavy** → **`gz-context-diet`** lifts
  narrative out of AGENTS.md, CLAUDE.md and the rules into `docs/governance/`.
- **Retire an entry** → `uv run gz content retire`, then land it as in step 2.

## Only you can

Attest the addition or removal of canon. A re-render of unchanged canon needs no
attestation.

## Then

[Commit and sync](commit-and-sync.md).
