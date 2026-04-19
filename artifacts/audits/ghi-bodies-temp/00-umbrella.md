## Meta-tracker for the 4.7 governance-surface hardening series

Claude Opus 4.7 shipped 2026-04-16. In the 48 hours since, the repo filed GHIs #186 through #199 plus #217-#223 — a defect velocity ~5× baseline. The pattern is consistent: agents reading the governance surface under 4.7 commit to whatever literal path falls out, even when a 4.6-trained operator expected inference to bend the rule to the situation.

## Scope

This series addresses **model-behavior hygiene** in gzkit's rules and skills canon — the surfaces that sync to Claude Code (`.claude/rules/*`, `.claude/skills/*`) and GitHub Copilot (`.github/instructions/*`). Fixes ship as standard `fix(...)` commits per `.gzkit/rules/defect-fix-routing.md`.

**Explicitly out of scope** (deferred to existing pool ADRs):
- `CLAUDE.md` → `@AGENTS.md` handoff adoption → `ADR-pool.vendor-alignment-claude-code` (chore-promotable tidy item)
- `AGENTS.md` body hardening → same (AGENTS.md-body F1 findings await that chore)
- `.codex/config.toml` activation → `ADR-pool.vendor-alignment-codex`
- Conditional vendor-enablement architecture → `ADR-0.16.0-cms-architecture-formalization`
- Two-mode Universal/Full-Enforcement execution → `ADR-pool.harness-aware-execution-modes`

## Anthropic-published behavioral changes in 4.7

Grounded in the Claude Opus 4.7 System Card (April 2026) §6.2.2.2 and the "Working with Claude Opus 4.7" tutorial:

1. **Cautious system prompts degrade 4.7** — System Card §6.2.2.2: *"Notably, [Opus 4.7] is the first model in this series for which a cautious system prompt lowered instruction-following and adaptability scores — its baseline is already careful enough that added caution tips into over-asking."*
2. **Action-downgrade** — 4.7 "sometimes downgrades action requests into advice or questions — explaining how to squash commits rather than doing it"; cautious prompts amplify this.
3. **Declaring sufficiency without acting** — "I have enough context, let me write the code," then resuming exploration until tool-call cap with nothing written.
4. **Verbosity burying actionable content** — System Card §2.3: *"response verbosity that buried actionable content within pages of text."*
5. **Adaptability is a 4.7 strength** — "reliably diagnoses root causes rather than patching surface symptoms." This is NOT a regression; it is what we want. The failure shape is our text coupling root-cause thinking to OBPI ceremony-mandate.
6. **Tool use is more selective** — operations described in prose without named tool literals get skipped.
7. **Repetition for emphasis backfires** — tutorial guidance: *"write your directions once and clearly."*

## Failure-mode taxonomy — F1 through F10 (governance-surface hygiene, model-agnostic)

Full definitions, Anthropic citations, and fix shapes in `docs/governance/model-regression-taxonomy.md`. Inlined here for chain-completeness:

| Code | Short name | What it is | Strongest citation |
|---|---|---|---|
| **F1** | Vague-inference instructions | Rules phrased as soft inference ("use judgment", "when appropriate") without named observable triggers | T1 — System Card §6.2.2.2 (cautious prompt backfire) |
| **F2** | Cross-surface restatement | Same rule stated in 2+ files, often with drift | T2 — Tutorial ("write once and clearly") |
| **F3** | Tool-use literalism / hesitation | Operations described in prose without naming the tool (Read/Grep/Glob/Edit) | T1 — System Card §6.2.2.2 Efficiency |
| **F4** | Over-ceremony coupled to root-cause thinking | Ceremonies without scope-scaling; 4.7's Adaptability strength gets channeled into ceremony-mandate by our text | T1 (4.7 strength) + T3 (coupling is gzkit-specific) |
| **F5** | Cross-surface contradictions | Two surfaces state incompatible rules; 4.7 literal-reads one path and violates the other | T3 — observed |
| **F6** | Unverifiable vibe claims | Assertions ("table", "comprehensive", "thorough") without a named verification pathway | T1 — System Card §2.3 "confidence calibration" |
| **F7** | Missing negative constraints | Positive specs without a matching "do NOT" that closes the inferred gap | T3 — observed |
| **F8** | Monolithic burying of binding rules | Binding tables/thresholds buried under rationale and narrative prose | T1 — System Card §2.3 **exact phrase** "verbosity that buried actionable content" |
| **F9** | Repetition for emphasis | Same rule stated multiple times within one file for emphasis | T2 — Tutorial |
| **F10** | Implicit cross-file context dependencies | Rules that depend on another rule being loaded without naming specific section or command | T3 — observed |

Tier legend: **T1** = System Card directly names the failure mode; **T2** = Anthropic operator tutorial/news names it; **T3** = observed in gzkit GHI pattern without direct Anthropic citation.

## Limit of text-level remediation

System Card §2.3.6 examples (Mythos Preview): researcher updated CLAUDE.md mid-session to prevent a behavior; the pattern recurred anyway. *"I know the rule — I have six memory files about it — but knowing it doesn't stop me from generating the plausible-sounding version first."* F1-F10 fixes address the governance text surface; they reduce friction but do NOT close model-level tendencies (fabrication, skipped verification). Full mechanical closure requires hooks, `gz validate` checks, receipt-ID attestation, and test anchors — which is why F6's fix shape is "cite a locking test" rather than "rewrite the prose."

## Complement: mechanical enforcement layer (pool-ADR territory, not this series)

The F1-F10 text fixes in this series reduce friction and close contradictions. They do NOT replace mechanical enforcement — per the taxonomy doc, model-level tendencies require hooks, tests, and validators. The complementary mechanical layer is captured in existing pool and pre-release ADRs:

- `ADR-pool.harness-aware-execution-modes` — Mode 2 hook-based enforcement (Claude Code primary)
- `ADR-pool.vendor-alignment-claude-code` — Claude Code specific features (InstructionsLoaded hook, disable-model-invocation, PreToolUse gating, Notification hooks)
- `ADR-pool.prime-context-hooks` — context-management hook family
- `ADR-pool.skill-behavioral-hardening` — skill-level anti-drift
- `ADR-0.16.0-cms-architecture-formalization` (pre-release, Proposed) — vendor manifest schema with selective enablement

These ADRs are not blocked by this series; this series is not blocked by those ADRs. They compose: text layer + mechanical layer. Mechanical affordances reach Claude Code (full Mode 2) and partially Codex (sandbox + approval modes per `ADR-pool.vendor-alignment-codex`); text fixes reach the full AGENTS.md-ecosystem (24+ tools).

## Sub-GHIs

Drafts at `artifacts/audits/4.7-governance-hardening-ghi-drafts.md`.

- **#225** — `arb.md:62` demonstrates the GHI #199 anti-pattern — rule file reproduces the failure it exists to prevent (critical; direct-fix, 5 lines)
- **#226** — F1 vague-inference in `.gzkit/rules/*` — three instances (`chores.md:19`, `defect-fix-routing.md:22`, `cli.md:20`); AGENTS.md-body F1 instances deferred to vendor-alignment chore #231
- **#227** — F2/F9 within-surface restatement — TDD rule 6f drift, Iron Law within-skill collapse, MUST/MUST NOT halving; triple-embed + `@AGENTS.md` adoption deferred to #231
- **#228** — F3 tool-literal coverage in skills — 6 instances where prose describes operations without naming Read/Grep/Glob/Edit
- **#229** — F4 over-ceremony decoupling + F5 cross-surface contradictions in rules — bundle 4 contradictions and the pipeline/router scope-gate addition
- **#230** — F6 output-contract test anchors in skills + F8 within-rules monolith hoisting; AGENTS.md monolith pruning deferred to #231

## Companion (separate track, not part of this series)

- **#231** — Execute vendor-alignment-claude-code tidy items (pool-authorized). Architecture-layer complement: `@AGENTS.md` handoff adoption, AGENTS.md pruning ≤200 lines, `disable-model-invocation` on ceremony skills, Compact Instructions section. Runs at its own pace under `ADR-pool.vendor-alignment-claude-code`.

## Evidence artifacts

- `docs/governance/model-regression-taxonomy.md` — full F1-F10 catalogue with Anthropic citations
- `docs/drafts/claude-code-vs-codex-control-surface-parity.md` — authoritative parity analysis (operator-authored)
- `docs/drafts/claude-code-inventory.md` — 168-row Claude Code feature inventory (operator-authored)
- `artifacts/audits/agent-parity-table.md` — gzkit-specific operational mapping
- `artifacts/audits/4.7-governance-hardening-ghi-drafts.md` — full GHI drafts file
- `artifacts/audits/4.7-system-card/full.txt` — System Card text extract
