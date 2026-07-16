# control-surface-permission-consent-drift (Pass D)

Audit-only ledger of every context-free prohibition in `AGENTS.md` / `.gzkit/rules/**` vs the standing consent granted by the agent permission surfaces (`.claude/settings.json`, `.claude/settings.local.json`), flagging allow rules that pre-answer a prompt for a forbidden command. Output is `proofs/consent-drift.md` paired with `proofs/unwitnessable.md` — the ledger of what this pass structurally *cannot* audit.

Advisory only, never gating, local-run only (`settings.local.json` is gitignored and absent in CI). Origin: GHI #690.

One of four chores in the control-surface audit sweep. See `control-surface-rule-conflicts` (Pass A), `control-surface-skill-rule-reachability` (Pass B), and `control-surface-rule-vs-check-drift` (Pass C).
