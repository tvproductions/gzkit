# Codex instruction delivery audit — 2026-09-12

Persona: spec-reviewer. Read-only fixed-scope delivery audit. Snapshot: `464dd4ff8fa2ee12d98afe99a867280e1b82b431`. Installed CLI: `codex-cli 0.154.0`.

**Root AGENTS.md is delivered whole. The hierarchy is not always delivered whole.** The configured 65,536-byte project-document limit is shared by the files Codex combines for its starting directory. The installed runtime truncates the source and tests chains in the sampled nested starts. This is separate from the model context window and says nothing about a supposed one-quarter context comparison with Claude.

## Observed native project instructions

Fresh native `codex debug prompt-input` renderings; no model task started. All four attempts inside the filesystem sandbox exited 1 with `Operation not permitted`. Authorized read-only execution outside that sandbox succeeded, retaining existing config/trust and using only a temporary `sqlite_home` override. The JSON companion retains measurements, hashes, selected config and hook state; raw prompts were removed.

| Starting directory | File | Disk bytes | Source bytes actually included |
|---|---|---:|---:|
| repository root | AGENTS.md | 48,511 | 48,511 |
| src/gzkit/commands | AGENTS.md | 48,511 | 48,511 |
| src/gzkit/commands | src/AGENTS.md | 7,458 | 7,458 |
| src/gzkit/commands | src/gzkit/AGENTS.md | 22,651 | 9,567 |
| src/gzkit/commands | src/gzkit/commands/AGENTS.md | 17,505 | 0 |
| tests | AGENTS.md | 48,511 | 48,511 |
| tests | tests/AGENTS.md | 30,284 | 17,025 |
| docs/governance | AGENTS.md | 48,511 | 48,511 |
| docs/governance | docs/AGENTS.md | 3,463 | 3,463 |
| docs/governance | docs/governance/AGENTS.md | 3,867 | 3,867 |

The command-directory run cuts the parent file mid-sentence at `Every unit of labor traceable to a T`; its own commands instruction file is not reached. The tests run cuts in mutation-test doctrine at `a mutant that does not im`. Source bytes reach 65,536 in each capped run. Codex's inserted blank-line separators add four bytes in the commands chain and two in the tests chain, so the measured inner blocks are 65,540 and 65,538 bytes respectively. This is not evidence that the configured cap is larger. The uncapped docs/governance inner block is 55,845 bytes, including four separator bytes.

The root-only delivery witness in `src/gzkit/governance/trust_audits/codex_delivery_witness.py:204` probes from the project root. Its success does not establish nested-chain survival. Its parser at line 119 counts one combined INSTRUCTIONS block, not per-file contributions. This audit measured each contribution in sequence against the actual file bytes.

`config/read` confirms the project `.codex` layer is active, `project_doc_max_bytes=65536`, `project_doc_fallback_filenames=[]`, `instructions=null`, `developer_instructions=null`, and `model_instructions_file=null`. `model_context_window=null` means no configured value was returned, not a zero-size window. The user config marks this repository trusted. Neither trust nor configuration was changed.

## What loads, and when

Official Codex guidance says native discovery builds a chain at startup: global instruction file, then project root through starting working directory; it takes at most one file per directory, preferring AGENTS.override.md, then AGENTS.md, then configured fallback names. Empty files are skipped. Files later in the chain have nearer-directory precedence. [Official AGENTS documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

- **Global instruction prose:** `/Users/jeff/.codex/AGENTS.md` exists but is empty: zero bytes. Its override is absent. The ancestor directories above the repository contain neither AGENTS.md nor AGENTS.override.md in this inspection. These are separate from platform/developer instructions injected by the app.
- **Root instructions:** 48,511 source bytes, 48,229 characters, observed in full. A root-start prompt does not eagerly include all descendant AGENTS.md files.
- **Nested instructions:** conditional on the starting chain and cumulative budget, with actual examples above. Later explicit tool reads can add file contents to the conversation; those are not the same mechanism as startup discovery. This audit did not establish that changing an individual shell tool's working directory refreshes the native instruction chain.
- **CLAUDE.md and `.claude/rules`:** no Codex fallback is configured for CLAUDE.md. These files are not native Codex instruction sources merely because they exist. Claude's `@AGENTS.md` import syntax is present in the generated redirects; it does not make those redirects Codex instruction inputs. The root and nested shared AGENTS files are Codex's corresponding native route.
- **Other Markdown, ADRs, handoffs, corpus/renditions, JSON, referenced rationale and scripts:** discoverable sources, not automatically injected in full by a link or filename. Their contents arrive through a selected skill, an explicit read, or a hook's rendered selection.

This inspection witnesses prompt assembly by the installed CLI. It does not dump this already-running desktop conversation, its history, hidden platform instructions, tool schemas, screenshots, compaction, or total token use. Delivery establishes availability to the model, not obedience, retention, or successful execution.

## How repository rules reach each surface

Read producer: `src/gzkit/rules/__init__.py:404-478,523-618,855-867`. Canonical `.gzkit/rules` is read directly. Shared rules with extractable directory prefixes become combined nested AGENTS.md bodies. Prefix extraction stops before the first wildcard; literal filenames produce no subtree. Vendor mirror prefixes are excluded from this nested-authoring route. Sync also emits sibling CLAUDE.md imports of those shared bodies and renders the canonical rules to Claude paths-frontmatter files.

Examples: CLI doctrine scoped `src/gzkit/commands/**` appears in the commands subtree file; source-level policies appear in src/AGENTS.md and src/gzkit/AGENTS.md; tests/AGENTS.md combines several rules. The JSON records all classified rules and all 27 tracked AGENTS file sizes.

Five canonical rules have no generated subtree route under this classifier:

| Rule | Reason |
|---|---|
| governance-core | `**/*` is global |
| hexagonal-architecture | `**/*.py` has no directory prefix; classifier calls it global |
| pythonic | `**/*.py` has no directory prefix; classifier calls it global |
| agents-md-map-doctrine | literal root filenames plus a vendor-mirror prefix |
| changelog-release-notes | literal root filenames |

That is a producer-route observation, not a claim that every clause is absent: root AGENTS may repeat some policy and an agent may explicitly read the canonical source. It does mean that `.gzkit/rules` existence alone is not evidence of native Codex loading. Claude's delivered `paths` files and Codex's directory-prefix aggregation are materially different selection mechanisms.

## Skills and other prompt overhead

Each native probe delivered a **22,179-byte skills-instructions developer block** containing the catalog and discovery guidance. The measured catalog contained 91 file-addressed entries across discovered locations. The complete SKILL.md bodies were not embedded wholesale. The sample pipeline entry names its skill and a shortened description plus its location. Root-alias numbering is runtime-local and differs from this agent's injected catalog; no repository-only catalog count is asserted.

Official docs describe name/description/path discovery followed by full-body loading when a skill is selected; the initial list has its own model-dependent budget. [Official skills documentation](https://learn.chatgpt.com/docs/build-skills)

Therefore `.agents/skills` holds deliverable on-demand bodies, not 91 bodies' worth of baseline prompt. `.gzkit/skills` is repository canon; sync materializes mirrors, and native catalog discovery points to the available skill paths. A skill's own AGENTS.md or referenced documents can add further content when encountered; neither is included simply because SKILL.md metadata is listed. This audit changed no skill body or metadata.

The native root rendering also contained separate permissions, collaboration, multi-agent, recommended-plugin and environment blocks; their byte measurements are in JSON. These must not be conflated with the 48,511-byte root file, the 65,536-byte project-document setting, or complete runtime context.

No tokenizer was available in the project Python environment (`tiktoken` not installed). This report gives UTF-8 bytes and Unicode character counts only. It offers no byte/4 token conversion and no numerical Claude/context-capacity ratio.

## Hook context is conditional, not currently automatic

Native `hooks/list` recognizes all three project hooks without project errors: orientation SessionStart, handoff-advisement SessionStart, and verifier PreToolUse. **All three are enabled but `trustStatus=untrusted`.** Project trust is already present; exact-hook trust is a separate condition. Official docs state untrusted non-managed hooks are skipped until reviewed. [Official hooks documentation](https://learn.chatgpt.com/docs/hooks)

- Orientation registration matches startup/resume/clear/compact, timeout 30s, `additionalContextLimit=6000`. Prior direct output at `/tmp/gz-codex-orientation-output.txt` measures **19,505 bytes / 19,383 characters**. This is historical direct-handler output, not newly observed automatic dispatch. I did not re-run the orientation main: despite its read-only-sounding module introduction, `collect_obpi_locks` invokes the canonical reaper (`scripts/session_orientation.py:920-941`), which can mutate lock/accounting state.
- Handoff advisement registration matches the same lifecycle events, timeout 10s, no custom context threshold. Calling its existing read-only renderer now yields **1,098 bytes / 1,092 characters**, `truncated=False`, under the renderer's 4,000-character budget. This measures the rendered selection, not full handoff content or lifecycle injection. `src/gzkit/hooks/codex.py:141-156` returns it as `additionalContext`; `src/gzkit/session_start.py:86-121,165-219` selects and renders the advisement.
- Verifier PreToolUse returns a deny reason on matching violations; it is conditional control feedback, not an always-loaded instruction document.

Codex's hook limit is an approximate token threshold; default 2,500 per message, independently applied to handlers. Oversized context spills to a file with a shorter preview. The orientation's 6,000 setting is not 6,000 bytes, and a source-file or stdout measurement does not establish how much lifecycle context arrived. [Official hook-output documentation](https://learn.chatgpt.com/docs/hooks#large-hook-output)

The 2026-09-12 parity report's distinction between registration/direct execution and trusted dispatch remains accurate. This audit supplies fresh native trust evidence and fresh handoff-renderer size without activating hooks.

## Practical result

The next delivery work has three independently demonstrated subjects: cumulative nested-chain truncation, canonical rule classes without a native subtree route, and untrusted project hooks. Reducing skill bodies would not reduce the measured 22,179-byte initial catalog because those bodies are loaded later. Any changes require their own reviewed scope; none were made here. A byte cap, catalog size, and hook-output threshold describe different stages of delivery, and none alone measures the user's effective context window or agent compliance.
