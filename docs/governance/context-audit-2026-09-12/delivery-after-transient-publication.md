# Native Codex delivery after D09/D10/D14 publication

Measured 2026-09-12, HEAD `4535839bb47d27456ccbafea0170bc7f17b88b71`, with the current working-tree root hash `f53831450e7f0a5457966e83a16f8be7b6fdb016b255e58946211109cdffc1ac`. Native read-only `codex debug prompt-input` and app-server `config/read` / `hooks/list` probes used temporary SQLite state. All requests completed successfully. No model task started; no repository, configuration or trust changes were made.

**The 42,442-byte root now arrives whole. Subtree truncation remains.** The effective project-document cap is still 65,536 bytes, applied cumulatively to source bytes. Blank-line separators add two bytes per join to the rendered inner block.

| Start | File | Disk bytes | Included bytes | Result |
|---|---|---:|---:|---|
| Root | AGENTS.md | 42,442 | 42,442 | Whole |
| src/gzkit/commands | AGENTS.md | 42,442 | 42,442 | Whole |
| src/gzkit/commands | src/AGENTS.md | 7,458 | 7,458 | Whole |
| src/gzkit/commands | src/gzkit/AGENTS.md | 22,651 | 15,636 | Partial: 7,015 bytes missing |
| src/gzkit/commands | src/gzkit/commands/AGENTS.md | 17,505 | 0 | Not reached |
| tests | AGENTS.md | 42,442 | 42,442 | Whole |
| tests | tests/AGENTS.md | 30,284 | 23,094 | Partial: 7,190 bytes missing |

Commands-start source bytes total 65,536; joined inner block is 65,540 bytes. Tests-start source bytes total 65,536; joined inner block is 65,538 bytes. Root-only inner block is 42,442 bytes.

The command chain still ends inside task-discovery material in src/gzkit/AGENTS.md, at the sentence beginning `Every reader derives from TaskId.parse`. The test chain now reaches task lineage material and ends in a reference beginning `docs/governance/agent-contrac`. The JSON retains exact tails and per-file hashes; it contains no full raw prompts.

## Comparison boundaries

The original audit observed 48,511 bytes. The parent reports an independent working-tree reversion before publication reduced the immediate prepublication root to 47,851 bytes. The approved publication therefore reduces that immediate baseline by **5,409 bytes**, not 6,069. The net historical-to-current difference is 6,069 bytes, including the unrelated 660-byte change.

Compared with the historical native probe, source-parent delivery increases from 9,567 to 15,636 bytes and test-file delivery from 17,025 to 23,094 bytes. Those are net historical comparisons, not isolated causal measurements of this publication. Commands-specific delivery remains zero.

The native skills-instructions block now measures 22,172 bytes. Its earlier 22,179-byte figure is historical; this audit makes no causal claim about that seven-byte change and does not change any skill bodies.

## Current hooks: zero recognized project handlers

`hooks/list` currently returns **an empty project-hooks list**, with no project errors. The only returned warning concerns a plugin SessionEnd timeout; it is not a project-handler error. This differs from the historical observation of three registered, untrusted project hooks.

The current `.codex/hooks.json` is 592 bytes and has the older command-array / inject shape under SessionStart and UserPromptSubmit. Native registration is therefore absent in the measured state. Project `.codex` configuration remains active and `features.hooks=true`; enabled infrastructure does not establish a recognized handler. No automatic orientation or handoff-context delivery is claimed.

The prior three-handler trust result and prior orientation stdout size must not be presented as current. This probe did not run any hook, restore the earlier integration, or alter trust.

## Limits

These measurements witness the installed CLI's startup instruction assembly for three starting directories. They do not measure the running desktop conversation's complete context, refresh behavior after later shell-directory changes, token usage, model obedience, or a Claude context-window ratio. Disk existence and root-only delivery are insufficient evidence for subtree instruction survival.
