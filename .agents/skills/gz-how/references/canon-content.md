# Canon content

You are here when AGENTS.md or another canon-sourced control surface should say
something different. Rendered surfaces are playback of an append-only corpus;
edit the corpus, never the rendering.

## Steps

1. **`gz-content-remember`** — `uv run gz content remember` appends the entry
   to the surface's corpus.
2. **`gz-content-compose`** — `uv run gz content compose` stages a candidate
   rendition, checks the invariant floor and computes the byte evidence.
3. **`gz-advisor-qc`** — judges the information kept per byte and records the
   verdict with `uv run gz content advise-rendition`. Advisory, never gating.
4. **Attest and commit** — `uv run gz content commit` promotes the candidate
   under the operator's attestation.
5. **`gz-agent-sync`** — play the committed rendition back onto the surfaces.

## Branches

- **Per-turn instructions have grown heavy** → **`gz-context-diet`** lifts
  narrative out of AGENTS.md, CLAUDE.md and the rules into `docs/governance/`.
- **Retire an entry** → `uv run gz content retire`.

## Only you can

Attest the addition or removal of canon. A re-render of unchanged canon needs no
attestation.

## Then

[Commit and sync](commit-and-sync.md).
