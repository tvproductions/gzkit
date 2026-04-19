## Tidy items authorized by ADR-pool.vendor-alignment-claude-code

The pool ADR explicitly notes: *"Tidy items (CLAUDE.md pruning, disable-model-invocation, Compact Instructions, Notification hooks) can proceed as chores without waiting for promotion."* This issue tracks execution of those tidies.

Standalone scope — **NOT part of** the 4.7 governance-surface hardening series (umbrella #224). This is architecture-layer work that complements the text-layer fixes in that series.

## Scope

1. **Adopt `@AGENTS.md` handoff in CLAUDE.md** per Claude Code docs ([memory#agents-md](https://code.claude.com/docs/en/memory#agents-md); `docs/drafts/claude-code-inventory.md` row 58):
   - Add `@AGENTS.md` at top of CLAUDE.md
   - Remove the `<!-- BEGIN agents.local.md -->` / `<!-- END agents.local.md -->` embed block (comes via chain since AGENTS.md already embeds `agents.local.md`)
   - Reduce CLAUDE.md to `@AGENTS.md` + genuinely Claude-Code-specific addendum
   - Run `gz agent sync control-surfaces`
   - Verify with `/memory` in a Claude Code session (confirm AGENTS.md appears in loaded-files list)

2. **Prune AGENTS.md to ≤200 lines** (currently 306) per Claude Code's 200-line soft guidance (inventory row 51):
   - Move meta-justification (L13-22 "Why this contract is not minimal") to `docs/governance/contract-rationale.md`
   - Move skills catalogue (L172-198) to `docs/user/skills-catalogue.md`
   - Hoist AGENTS.md-body F1 findings (the 5 instances the 4.7 GHI-01 deferred): `AGENTS.md:22` "Use judgment", `:127` "Preserve human intent", `:128` "Aggressively offload", `:207` Gate 4 "Manual check", `:234` "After plan approval" — each gets a mechanical-trigger rewrite
   - **Verify with `/context`** (claude-code-inventory row 45) — Claude Code's per-session diagnostic showing live token usage by category. Makes the ≤200-line target empirically checkable during the fix, not aspirational.

3. **Add `disable-model-invocation: true`** to ceremony/side-effect skills (gz-attest, gz-closeout, gz-audit, gz-gates, git-sync) — inventory rows 48, 71. Keeps descriptions out of every-turn context; ~2K tokens saved per session.

4. **Add Compact Instructions section** to CLAUDE.md (inventory row 43) so context compaction preserves governance state (active pipeline, OBPI ID, gate status, pending attestations).

## Routing

Multi-commit chore under `ADR-pool.vendor-alignment-claude-code`. Not a single GHI fix; execute as discrete commits per tidy item. Each commit: `chore(vendor-alignment-cc): <item summary>`.

## Related

- **Parent pool ADR:** `ADR-pool.vendor-alignment-claude-code` (2026-03-15)
- **Complementary umbrella:** Umbrella GHI #224 (4.7 governance-surface hardening — text layer)
- **Inventory reference:** `docs/drafts/claude-code-inventory.md` (168-row Claude Code feature inventory)
- **Parity analysis:** `docs/drafts/claude-code-vs-codex-control-surface-parity.md`

## Why separate from the 4.7 series

The 4.7 series ships text-level hygiene fixes (F1-F10 per `docs/governance/model-regression-taxonomy.md`) in `.gzkit/rules/*` and `.gzkit/skills/*`. These tidy items are architecture-layer changes to `CLAUDE.md`, `AGENTS.md`, and skill metadata — different blast radius, different routing. Keeping them on separate tracks lets the 4.7 text fixes ship fast while architecture adjustments proceed at their own pace under the vendor-alignment ADR.
