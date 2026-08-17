<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# gzkit Campaign Architecture Review — 2026-08-17

Status: **RETAINED — input to campaign amendment, not itself a campaign.**
Prompt: [`gzkit_campaign_architecture_eval_prompt.md`](gzkit_campaign_architecture_eval_prompt.md)
Basis: `main @ d82206df0`, v0.34.3. Every figure observed by command, not transcribed.
Interview decisions are recorded in § Operator Decisions as they are ruled.

> **This document does not amend the campaign.** It is evidence routed at
> `docs/governance/build-to-1.0-campaign-2026-08-16.md`. Amendment requires an
> operator ruling appended to that plan's § Amendments per its §8.

---

## 1. Measured baseline

| Measure | Value | Method |
|---|---|---|
| Project age | 2026-01-12 → 2026-08-17 (~7 mo) | `git log --reverse` |
| Commits | 2,993 | `git rev-list --count HEAD` |
| Source / test SLOC | 126,841 / 172,891 | `wc -l` |
| CLI verbs (top level) | 59 | `gz --help` |
| `gz validate` flags / registered scopes | 106 / 85 | `gz validate --help` |
| Foundation ADRs | 51 (kind closed/frozen) | dir count |
| Feature ADRs | 36 — 33 `Validated`; 0.35.0 `Draft`, 0.36.0 `Proposed`, 0.37.0 `Draft` | frontmatter |
| Pool ADRs | 199 | dir count |
| OBPI briefs | 542 | find |
| REQs / covered | 2,702 / 1,743 = **64.5%** | `gz covers` |
| Ledger events | 15,038 across **55** emitted types (65 declared, 10 never emitted) | parse |
| ARB receipts | 3,368 | `artifacts/receipts` |
| Handoff files | 373 | `.gzkit/handoffs` |
| Skills | 70 canonical × **5 mirrors** = 350 copies | find |
| BDD features / step files | 67 / 51 | ls |
| Open GHIs | 14 (drained from ~300/mo in April) | `gh issue list` |
| Commit mix, 30d | 627: **271 fix (43%) · 245 chore (39%) · 80 docs (13%) · 16 feat (2.6%)** | `git log --format=%s` |
| Airlock transits | 23 in / 5 out; 20 of 23 EMPTY seam-map | ledger + campaign |
| MCP references in `src/` | **1 file** (a string in `verifier_pipe_gate.py`) | grep |
| Third-party skill support | **0** — no provenance/trust/version/discovery surface | grep |
| Harness hook parity | Claude Code **17** · Codex **2** (orientation inject only) · Copilot **1** | ls |
| Flight-test sorties flown | **0** (skill + 6-sortie manifest + templates; no code, no verb) | find |
| Competitor radar registry | 15 entries, last updated **2026-05-07** (monthly cadence) | `registry.json` |

## 2. Two decisive structural findings

1. **Every `feat` commit in the last 60 days changes gzkit's own governance
   machinery.** Not one adds a capability a consumer project would use on its own
   software. The campaign named this itself (§2: *"gzkit has no external forcing
   function, and its only consumer is its own construction"*) — the diagnosis is
   correct and the Queue does not act on it.

2. **The §5 1.0 gate "one external forcing function exists — at least one
   flight-test sortie flown against a non-gzkit substrate" is carried by no
   Movement checkbox in §6.** It appears in the 1.0 definition and the Rulings
   Register, and nowhere in the work queue. The single gate that would break the
   self-consumption loop is unowned work.

---

## 3. Per-exemplar parity — where gzkit stands, and why

> **Provenance discipline.** Claims about gzkit are observed by command. Claims
> about external projects derive from (a) the operator-authored ecosystem model in
> the review prompt, (b) `artifacts/reports/competitor-radar/` evidence, and
> (c) the campaign's cited 2026-08-16 competitive review. **Where a competitor's
> current-state claim would be speculation it is marked `[unverified]`** — the
> radar is three months stale and a refresh is the correct instrument, not
> recollection.

### 3.1 The causal finding — the radar cannot see five of the ten layers

`artifacts/reports/competitor-radar/registry.json` tracks 15 competitors:

| Tracked category | Entries |
|---|---|
| Spec-driven frameworks / platforms | OpenSpec · GitHub Spec Kit · Better Spec · Specledger · Tessl |
| Agentic IDE | Kiro |
| Contract-driven | Specmatic |
| Agentic methodology | BMAD Method · GSD |
| Skills | Superpowers · Matt Pocock Skills · Agent Skills · Compound Engineering |
| Durable-spec ecosystems | OpenAPI · OpenTelemetry |

**Not tracked, in any category:**

- **Harnesses** — Codex, Claude Code, Pi, OpenCode, Gemini CLI, OpenHands, Cline, Roo, goose, Amp, Factory Droid: zero entries.
- **Tool protocols** — MCP: zero entries.
- **Eval** — SWE-bench, Terminal-Bench, Harbor, DeepSWE: zero entries.
- **Autonomous execution** — Ralph loops, fresh-context orchestration: zero entries.
- **Implementation-contact / evidence capture** — no category exists.

**gzkit is at parity or ahead on every layer its radar images (A, C, E), and
absent on every layer it does not (B, D, F-identity, G-reach, J).** The
correlation is exact across ten layers. This is the instrument determining the
roadmap: a strength pattern can only route to a pool ADR if something noticed it.

Compounding: the radar's cadence is monthly, its last scan is `2026-05-07`
(three months stale), and all six of its suggested MOVEs remain
`pending-operator-session` — including **MOVE-004 "Turn two-stage review into
typed gzkit receipts,"** which is the exact independent-review parity gap
§3.10 records as still open, identified in May and never dispositioned.

### 3.2 Layer A — project intent and durable contracts

| Exemplar | gzkit position | Why |
|---|---|---|
| **GitHub Spec Kit** (`constitute→specify→plan→implement→analyze`; extensible workflow) | **AHEAD** on durability; **BEHIND** on workflow extensibility | gzkit's declared lineage. gzkit closes intent→REQ→proof-channel→ledger, which Spec Kit does not attempt. But Spec Kit's workflow is *data*; gzkit's is 70 skills plus a Python runtime, so an adopter cannot express their own workflow. The README states this as a deliberate choice: *"Workflow specification should make the covenant more executable, not replace it with a YAML-style automation DSL."* Defensible; the cost is unstated. |
| **OpenSpec** (light brownfield proposal/spec/design/tasks/archive) | **BEHIND** on intake | gzkit's smallest unit of intake is an ADR under a PRD under a constitution. There is no sub-ADR proposal shape and no light-touch brownfield entry: `gz init` scaffolds a Python skeleton, 5 mirror trees, and 70 skills. `gz-design`/`gz-prd` are heavier than OpenSpec's whole model. |
| **Specmatic** (contract-driven; OpenAPI as executable contract) | **ABSENT** | gzkit models *governance* contracts, never *interface* contracts. No REQ kind expresses "this API conforms to this schema." Layer H in the wider world increasingly means contract tests; gzkit's three proof channels (BEHAVIOR/SUPPORT/STRUCTURAL-FENCE) cannot express one. |
| **Tessl · Specledger · Better Spec** | **NOT CONTESTED** | Registry/platform shapes. Correct not to contest. |
| **OpenAPI · OpenTelemetry** | **NOT CONTESTED** (tracked as durable-spec exemplars) | Correct — these are patterns to learn from, not competitors. OTel is the closest external analogue to gzkit's ledger and is worth mining for the event-schema-versioning problem gzkit will hit. |

**Layer verdict:** gzkit is the only system in the field that closes intent to
evidence. It is last in the field on intake ergonomics, and it has no concept of
an external interface contract.

### 3.3 Layer B — coding-agent harness

| Exemplar | gzkit position | Why |
|---|---|---|
| **Claude Code** | **AHEAD OF THE FIELD** | 17 hooks across SessionStart/PreToolUse/PostToolUse/Stop/PreCompact/SessionEnd. `PreToolUse` *blocks* — the `verifier-pipe-gate` refused a piped verifier during this review session. `PostToolUse` on Edit/Write feeds 5,133 `artifact_edited` events. Nobody else in the registry uses a harness's hook surface as a governance membrane. |
| **Codex** | **NOMINAL — and incoherently so** | 2 hooks (`.codex/hooks.json`), both `inject: additionalContext` running orientation. **No evidence capture.** Yet Codex is the *required tier-1* reviewer for Step 4b (`gz-obpi-pipeline` SKILL.md: *"Codex (tier 1) is REQUIRED first"*). **gzkit depends on Codex for its most important integrity gate and has no evidence channel from it.** This is the sharpest single incoherence in the repository. |
| **GitHub Copilot** | **SURFACE ONLY** | 1 hook (`ledger-writer.py`), plus `.github/instructions/*.instructions.md` mirroring. |
| **Pi · OpenCode · Kiro · Gemini CLI · OpenHands · Cline · Roo · goose · Amp · Factory Droid** | **ABSENT** | Not adapted, not tracked in the radar, not referenced in `src/`. `GEMINI.md` exists as a mirrored instruction file with no hook or evidence path. |

**Why not at parity:** gzkit has **no harness capability model.** Nothing
declares what a given harness can do — hooks? subagents? MCP? permission
prompts? blocking? — so there is no basis for graceful degradation, and no way to
state which invariants survive a swap. The pool holds `ADR-pool.harness-fitness`
and `ADR-pool.harness-factoring`: the concept was recognised and booked
post-1.0.

**Layer verdict:** deep on one harness, nominal on the one it structurally
depends on, absent on the rest. **Principle 2 (harnesses should be replaceable)
is asserted in five mirrored copies of the doctrine and implemented in one.**

### 3.4 Layer C — skills and reusable agent expertise

| Exemplar | gzkit position | Why |
|---|---|---|
| **Superpowers** (methodology as composable skills) | **AT PARITY on expression · BEHIND on composability** | gzkit's 70 skills *are* its methodology — structurally the same insight, reached independently, and arguably more rigorous (each SKILL.md carries triggers, rationalization tables, red flags). But Superpowers skills install into any Claude Code project; gzkit skills are welded to `gz` verbs and mirrored five ways. **gzkit cannot consume a Superpowers skill under governance.** |
| **Matt Pocock skills** (engineering judgment as portable procedure) | **NOT CONSUMED** | No mechanism exists to admit one. |
| **Agent Skills standard (`SKILL.md`)** | **FORMAT-COMPATIBLE · ECOSYSTEM-INCOMPATIBLE** | gzkit authors 70 conformant `SKILL.md` files with YAML frontmatter, has `gz skill list`, a skill-contract validator, and a staleness gate — **all pointed inward.** For a skill gzkit did not author there is no version pin, content hash, source, allow-list, trust policy, or invocation record. |
| **Compound Engineering** | **NOT CONSUMED** | Tracked in the radar; routed to no live destination. |

**Why:** the root cause is a modeling decision, not an oversight.
`docs/design/lodestar/architectural-identity.md` § *"Skills as Content"* models
skills as a **CMS content type** — gzkit is described there as "a headless CMS
for governance." Once a skill is content inside your CMS, a foreign skill is a
foreign object with no place to sit. The fix is small (identity + policy +
event); the framing is the blocker.

**Layer verdict:** format-compatible, ecosystem-incompatible. **Principle 3
(skills should be composable) currently fails.**

### 3.5 Layer D — tools and external capabilities (MCP)

| Exemplar | gzkit position | Why |
|---|---|---|
| **MCP** | **ABSENT AND UN-DESIGNED** | One file in `src/` mentions MCP, as a string in `verifier_pipe_gate.py`. Zero servers declared, zero policy, zero events. No ADR — active, pool, or otherwise — has MCP as its subject. |
| **Native harness tools** | **GOVERNS ONLY ITS OWN** | gzkit governs the `gz` CLI as *the* tool surface (106 flags, `gz cli audit`, manpage coverage manifest). It governs what it owns and observes nothing it does not. |

**Note on the declared-channel gap:** `.claude/rules/task-discovery.md` lists
`tool_invoked` among the eight validator-enforced worklog event types, but
`tool_invoked` is **not among the 65 event types declared in
`src/gzkit/events.py`.** The channel is documented and does not exist — a
doctrine-declared-without-mechanism instance inside the rule that governs
mechanism declaration.

**Layer verdict:** the largest *conceptual* absence in the system, not merely an
implementation gap. Worth stating the asymmetry plainly: gzkit's evidence spine
would make MCP governance nearly free — *"which server did this agent call, was
it permitted, what returned"* is precisely a ledger event, and gzkit already has
the ledger.

### 3.6 Layer E — spec/process methodologies

| Exemplar | gzkit position | Why |
|---|---|---|
| **Spec Kit · OpenSpec · GSD · BMAD** | **COMPETES WITH — does not accommodate** | The radar's own framing is *"competitors,"* never *integrands.* That is the tell. gzkit is a methodology contesting these, not a substrate hosting them. |
| **Agent OS** (deliberately shrank; let native agents do the mechanics) | **OPPOSITE TRAJECTORY** | Over the same period gzkit grew to 126k SLOC, 106 flags, 70 skills, 59 verbs. Whether that is right depends entirely on the personal-toolkit-vs-public-product question (§5, Decision 0). Agent OS is the strongest external argument for shrinking. |
| **Superpowers as methodology** | **PARALLEL INVENTION** | See §3.4. |

**Why:** methodology and project truth are not separated. The five gates, the two
lanes, the OBPI decomposition matrix, the four modes, the REQ-kind taxonomy — all
welded into the runtime. **Principle 8 (methodology should not become project
truth) is violated by construction**, not by drift.

**Layer verdict:** gzkit is the most opinionated methodology in the field and the
least accommodating substrate. That is a coherent product; it is not the product
the review premise describes.

### 3.7 Layer F — fresh-context execution and orchestration

| Exemplar | gzkit position | Why |
|---|---|---|
| **Ralph loops** (fresh context + external state + executable completion criteria) | **AT OR AHEAD on substance** | gzkit externalises state harder than any exemplar: 373 handoffs, a resume gate that requires an operator ruling before advised steps execute, OBPI locks with TTL warnings, `gz context <ADR-ID>` as a payload loader, 2,702 bounded REQs. This is gzkit's second-strongest layer and it is undersold. |
| **GSD** (context engineering, decomposition, fresh-context execution) | **AT PARITY on decomposition · BEHIND on runtime pluralism** | GSD is multi-runtime by design; gzkit's decomposition is richer (REQ kinds with distinct proof channels) but runs one runtime. |
| **Pi orchestration** | **ABSENT** | Not tracked, not integrated. |
| **Harness-native subagents** | **REIMPLEMENTED** | `pipeline_dispatch.py` (556 lines) dispatches four personas the harness already dispatches. Clearest Failure-Mode-A instance in the repo. |

**BEHIND on identity, which is the load-bearing gap:** there is **no `session`
entity and no agent identity on any ledger event.** 15,038 events, and not one
records which agent, which harness, or which model produced it. The pairing also
leaks: **44 `session_exit_bookmark_skipped` against 0 writes** (GHI #766, open) —
the same unpaired-event family as the airlock's 23-in/5-out.

**Layer verdict:** strong on durable state, **absent on provenance identity**,
over-built on dispatch.

### 3.8 Layer G — implementation contact

**AHEAD OF THE ENTIRE FIELD, on one harness.** 5,133 `artifact_edited` events
originate from a `PostToolUse` hook observing real Edit/Write calls — not from an
agent asserting it edited something. No exemplar in the registry does this;
several have no concept of it. It is the purest expression of *"evidence derives
from reality"* in the repository, and it dies the moment the harness changes.

### 3.9 Layer H — deterministic verification

**AHEAD OF EVERY EXEMPLAR.** 3,368 ARB receipts carrying `exit_status`, git SHA,
dirty flag, stdout tail, duration; a locked `CANONICAL_STEP_COMMANDS` table with
a `RETIRED_STEP_COMMANDS` history so past attestations stay interpretable; the
`@enforces(claim, neg_control)` meta-validator; a shrink-only waiver ratchet;
`verifier-pipe-gate`; 67 BDD features; `@covers` with per-kind proof channels.

**Three specific parity gaps:**

1. **Language-locked.** `CANONICAL_STEP_COMMANDS` is `uv`/`ty`/`unittest`/`mkdocs`. **A non-Python project cannot produce a canonical gzkit receipt.** This alone makes the §5 flight-test gate unsatisfiable against most substrates.
2. **No contract testing** (see Specmatic, §3.2).
3. **Security is an empty canonical command** — `"security": []`. The `security` sensitivity axis exists in doctrine (`.gzkit/rules/security-sensitivity.md`) with no command behind it. Against Trail of Bits / Semgrep skill packs, gzkit has an declared-but-empty channel.

**Layer verdict:** the strongest layer, nearest to adoptable, blocked by a dict.

### 3.10 Layer I — independent agent review

**Design: best in the field. Mechanism: facade by gzkit's own §4 rule.**

The design is genuinely superior to the exemplars — cross-vendor tier order
(Codex tier-1 *required*, Claude subagent forbidden when Codex is ready), the
adversary runs *before* attestation, the verdict passes to the operator
**unedited** via `updatedInput`, and the skill enumerates the rationalizations
agents use to skip it (which means skipping has been observed).

What is missing is the witness. The `gz-obpi-pipeline` SKILL.md states it
plainly: *"The mechanical attestation that these dispatches occurred is governed
by `ADR-pool.obpi-pipeline-dispatch-attestation` … (Pool / HEAVY — awaiting
promotion)."* **17 `adversarial_validation` events exist across 542 OBPI briefs.**
An agent can skip Step 4b and nothing fails closed.

**The parity gap was identified in May 2026 and never dispositioned.** Radar
MOVE-004 — *"Turn two-stage review into typed gzkit receipts,"* sourced from the
Superpowers/Compound Engineering `review-receipts` strength pattern — is still
`pending-operator-session`.

**Layer verdict:** gzkit's own core claim is *"agent assertion is not evidence of
completion."* Self-review is the largest live hole in that claim.

### 3.11 Layer J — eval

| Exemplar | gzkit position | Why |
|---|---|---|
| **SWE-bench · Terminal-Bench · Harbor · DeepSWE** | **NOT TRACKED, NOT REFERENCED** | Zero radar entries, zero mentions in the repo. |
| **Project-specific task suites** | **DESIGNED, NEVER RUN** | `docs/flighttest/manifest.md` is 6 sorties with ordered governed-path steps and expected black-box observables. It is a real eval design, closer in shape to Terminal-Bench than SWE-bench. **0 flown.** No `flighttest` verb, no code. |
| **Executable acceptance environments** | **PARTIAL** | 67 BDD features are behavioral eval for gzkit's own CLI. |
| **Regression evals for agent behavior** | **MISNAMED** | `src/gzkit/eval/` (datasets, scorer, regression baselines, delta gates) is real, working code that scores **the structural shape of gzkit's own instruction files** — `data/eval/skills_eval_golden.json` checks whether a SKILL.md has a *"When to Use"* section. That is rubric-linting of prose, not eval. Calling it `eval` risks believing the layer is occupied. |

**Layer verdict:** least parity of any layer. gzkit has an eval design it hasn't
run, an eval implementation that is misnamed, and no awareness of the eval
ecosystem.

### 3.12 Parity summary

| Layer | Position vs. field | Radar sees it? |
|---|---|---|
| A. Intent & durable contracts | **Ahead** on durability · behind on intake · absent on interface contracts | ✅ |
| B. Harness | **Ahead on one** · nominal on the one it depends on · absent on 10+ | ❌ |
| C. Skills | Format-compatible · **ecosystem-incompatible** | ✅ |
| D. Tools / MCP | **Absent and un-designed** | ❌ |
| E. Methodologies | **Competes, does not accommodate** | ✅ |
| F. Fresh context | **Ahead on state** · absent on identity · over-built on dispatch | ❌ (partly) |
| G. Implementation contact | **Ahead of the entire field**, single-vendor reach | ❌ |
| H. Deterministic verification | **Ahead of the entire field**, language-locked | ❌ |
| I. Independent review | Best design in field · **unwitnessed** | ✅ (routed, never promoted) |
| J. Eval | **Least parity** — designed, unrun, misnamed | ❌ |

**Read the two columns together.** Every ❌ is a layer where gzkit is absent or
single-vendor. Every ✅ is a layer where gzkit is at parity or ahead. The
instrument and the roadmap are the same shape.

---

## 4. GZKit ownership boundary

| Capability | gzkit owns | gzkit integrates | Harness/skill/tool owns | Rationale |
|---|---|---|---|---|
| Append-only typed event ledger | ✅ | | | Nothing else in the stack has durable, replayable project truth. This is the product. |
| Evidence receipts (cmd + exit + SHA + output) | ✅ | | | "Evidence outranks narrative" is only real once mechanized. Uniquely gzkit's. |
| Enforcement-claim negative controls | ✅ | | | Strongest idea in the repo; unclaimed elsewhere in the field. |
| Human attestation semantics | ✅ | | | No exemplar treats attestation as a first-class, non-bypassable, verbatim-preserved act. |
| Intent → REQ → proof-channel traceability | ✅ | | | Spec Kit/OpenSpec stop at specs; gzkit closes to evidence. |
| Finding / ruling / decision entities | ✅ **(build)** | | | The learning loop cannot close without them. Currently absent. |
| Session + agent identity/provenance | ✅ **(build)** | | | Required for "who claimed this." Harnesses will not record it durably. |
| Project verification *vocabulary* | ✅ (declare + lock) | | ✅ (execute) | gzkit locks *which command counts*; the project supplies it; the shell runs it. |
| Skill identity, policy, invocation record | ✅ (thin) | | | Governance must know which skill ran and whether it was permitted. |
| Skill content, procedures, marketplace | | | ✅ Superpowers · Pocock · Anthropic · Vercel | Absorbing these is Failure Mode A. gzkit's 70 skills become *one* library among many. |
| Tool policy + invocation evidence | ✅ (thin) | | | "Which tools were permitted, which fired" is governance. |
| Tool runtime, discovery, transport | | ✅ MCP | ✅ | MCP won. Integrate; own nothing. |
| Interface/API contract verification | | ✅ (Specmatic/OpenAPI shape) | ✅ | Add a REQ proof channel; do not build a contract engine. |
| Context management / compression | | | ✅ harness | Commodity, improving faster than gzkit could. |
| Agent loop, subagents, planning | | ✅ (dispatch *record*) | ✅ harness | Keep the record; drop the ambition. `pipeline_dispatch.py` should shrink. |
| Permissions / sandboxing | | ✅ | ✅ harness | Harnesses do this natively now. |
| Fresh-context execution | | ✅ | ✅ harness | Own the *resumability contract* (handoff + gate — already good), not the loop. |
| Independent review dispatch + findings | ✅ | | | Review as an entity with provenance is governance. |
| Independent review *reasoning* | | ✅ Codex / second harness | ✅ | Cross-vendor is the point; gzkit must never be the reviewer. |
| Eval acceptance environment + result record | ✅ | | | The flight-test manifest is already the right shape. |
| Eval benchmarks/harnesses | | ✅ Terminal-Bench · Harbor | ✅ | Integrate results; build no benchmark. |
| Spec methodology / phase model | | ✅ | ✅ Spec Kit · GSD · BMAD · OpenSpec · Agent OS | Methodology must not become project truth. |
| Security/SAST channel | | ✅ Semgrep · Trail of Bits skills | ✅ | Fill the empty `"security": []`; own no scanner. |
| Multi-surface mirroring of instructions | | | ⛔ **nobody — delete** | 350 SKILL.md copies; ~49% of all commits. Generate at install. |
| Airlock / blast-radius preflight | ⚠️ own the *invariant* | | | Keep "know the blast radius"; the realization is over-built for 23 lifetime uses. |
| Python project scaffolding | | | ⛔ **out of scope** | `gz init --no-skeleton` should become the default. |

---

## 5. Decisions required

Decision 0 was added after the parity pass; it is upstream of the original eight.

| # | Decision | Alternatives | Recommendation | Why it matters now |
|---|---|---|---|---|
| **0** | **Which station on §1's trajectory is 1.0** — *"research instrument + published exemplar → personal toolkit → public product"*? | (a) research instrument/personal toolkit; (b) public product | *awaiting ruling* | Every parity judgment inverts on this. Under (a), non-parity on B/C/D/J is correct and Agent OS's shrink is irrelevant. Under (b), each is 1.0-blocking. §1 states three stations; §5 does not say which one 1.0 is. |
| 1 | Is the external forcing function a 1.0 **gate** or the 1.0 **design driver**? | (a) gate, sequenced last (status quo); (b) driver, sequenced first | (b) | Every sequencing decision follows. §2 argues for (b); §6 implements (a). |
| 2 | Does gzkit own an execution/orchestration layer at all? | (a) yes — "agent runner" as README claims; (b) no — record dispatch, own no loop | (b), and correct the README | The claim is a facade under gzkit's own enforcement rule. Also decides whether `pipeline_dispatch.py` grows or shrinks. |
| 3 | Is the verification vocabulary gzkit's or the project's? | (a) gzkit hardcodes (status quo); (b) project declares, gzkit locks | (b) | Blocks Decision 1. Non-negotiable for any adopter. |
| 4 | Minimum knowledge of a **foreign** skill and tool? | (a) nothing (status quo); (b) name@version + hash + source + policy + invocation event; (c) full registry/trust scoring | (b) | Decides whether layer C/D work is weeks or quarters. (c) is Failure Mode A. |
| 5 | Does Gate 5 fail closed without an independent review disposition? | (a) no — skill prose only (status quo); (b) yes — mechanical witness | (b); promote `ADR-pool.obpi-pipeline-dispatch-attestation` | Self-review is the largest live hole in gzkit's core claim. Radar MOVE-004 has been pending since May. |
| 6 | Is the airlock 1.0 scope or post-1.0? | (a) widen to 4 doors pre-1.0; (b) calibrate only; (c) hold the invariant, defer the mechanism | (c) | Frees Movement B entirely; removes the largest premature-ceremony risk. |
| 7 | What replaces `PRD-GZKIT-1.0.0`? | (a) leave stale; (b) retire; (c) rewrite against revised milestones | (c) | Its Non-Goals forbid multi-agent orchestration while `ADR-0.18.0` ships it. A contradicted doc at the top of the intent hierarchy is a live counter-example to gzkit's thesis. |
| 8 | Is `ADR-0.35.0` gzkit's composition engine or **the adopter's `AGENTS.md` compiler**? | (a) internal (status quo); (b) adopter-facing, same code | (b) | Costs nothing, converts 10 inward OBPIs into a headline outward capability, and respects ADR-order-is-absolute without jumping the queue. |
| **9** | Should the radar registry be widened to the five blind layers? | (a) no — spec/skills scope is deliberate; (b) yes — add harness, tool-protocol, eval, autonomous-execution, evidence-capture categories | (b) | §3.1: the instrument's blind spots and the roadmap's gaps are the same shape. Cheapest structural correction on the board. |

---

## 6. Architectural risks

1. **Self-consumption is compounding and has no natural exit.** 2.6% `feat` rate, 100% of features inward, 7 months. Diagnosed in July; the Queue still sequences three self-governance Movements ahead of the cure.
2. **The radar's blind spots reproduce as roadmap gaps** (§3.1). Ten-for-ten correlation. Three months stale on a monthly cadence, six MOVEs undispositioned.
3. **Codex dependency without a Codex evidence channel.** gzkit's most important integrity gate requires a harness from which it captures nothing.
4. **Single-harness evidence coupling presented as vendor neutrality.** If Claude Code changes its hook contract, Layer 2 goes dark and the ledger degrades to agent narrative.
5. **Python-shaped verification vocabulary blocks gzkit's own 1.0 gate**, and no Movement owns it.
6. **Accidental reinvention at the airlock.** 23 lifetime transits, 20 empty seam-maps, proposed for widening onto ~528 commits/quarter. Its own pre-mortem (*"seam-maps rubber-stamped, GO always reached"*) has already come true in 87% of transits.
7. **Ceremony cost is unmeasured.** 106 flags, 542 briefs, 2,702 REQs, 17 hooks, 70 skills. gzkit measures its own correctness obsessively and its cost per operator-minute not at all. Principle 9 is a measurable claim currently unmeasured.
8. **Unimplemented-design accumulation.** 199 pool ADRs, 25 unlanded OBPIs, 10 declared-never-emitted event types, `tool_invoked` documented but undeclared, 6 sorties/0 flown, a stale PRD. Design outrunning implementation is the drift class gzkit's validators exist to catch, one layer up, unwitnessed.
9. **Review integrity is prose-deep** — `AGENTS.md` Never-#9 without a witness.
10. **"Eval" naming collision** risks believing layer J is occupied.
11. **Doctrine mass as context tax.** `AGENTS.md` is 33 KB and loads every turn, plus governance-core, orientation, and handoff. Principle 7 says context is an architectural resource; gzkit spends a large fixed fraction of every agent's context on its own contract before any work begins.
12. **Migration burden on adopters.** Today's `gz init` hands an adopter gzkit's entire laboratory. The Firewall exists to fix this and is unbuilt.

---

## 7. Proposed revised Road-to-1.0 (contingent on Decision 0)

Five milestones; total scope **smaller** than the current board. Every milestone
produces something an outsider can use or verify.

**M1 — Make gzkit runnable by someone who is not gzkit.** Project-declared,
gzkit-locked verification vocabulary; `--no-skeleton` default; The Firewall
(wheel-borne / battlefield / lab-jig) enforced at scaffold and validate time;
mirroring collapsed to one canonical tree generated at install.
*Invariant:* an adopter inherits gzkit's mechanisms and none of its jigs.
*Acceptance:* `pip install py-gzkit && gz init` in an empty **non-Python** repo
yields a working `gz check`, a valid ARB receipt over that project's own test
command, `--distribution` green, mirror count 1.

**M2 — Fly S1 against a foreign substrate.** `flighttest` as a real verb; the
S1 manifest run to completion. *Invariant:* gzkit's claims are falsifiable by a
run against a substrate it does not control. *Acceptance:* one sortie flown,
black-box evidence collected, squawks filed. **The debrief sets M3–M5 scope** —
not a pre-planned list.

**M3 — Harness Evidence Adapter.** A documented contract — emit
`artifact_edited`, `tool_invoked`, `session_started/ended` with agent identity —
implemented for Claude Code (formalize) and Codex (**close the §3.3
incoherence**). Session + agent identity become first-class ledger fields.
*Acceptance:* one OBPI driven to Gate 5 under two harnesses produces
structurally equivalent traces; a negative control proves an un-adapted harness
produces *no* evidence rather than silently-empty evidence.

**M4 — Skills, tools, review, findings as governed participants.** Skill policy
(name@version + hash + source) + `skill_invoked`; MCP allow-list +
`tool_invoked`; promote `ADR-pool.obpi-pipeline-dispatch-attestation` and add
`review_dispatched`/`review_finding`/`review_disposition`; ship `ADR-0.36.0`
OBPIs 01–08 and **drop OBPI-09** (the `AskUserQuestion` hook — deep
single-harness coupling the skill door already covers); `finding` + `ruling`
entities (Movement D, scoped to two events and one projection).
*Acceptance:* a **Superpowers skill** and an **MCP tool** both appear in the
ledger with provenance; an OBPI cannot reach Gate 5 without a recorded review
disposition (negative control proves it); a settled ruling is machine-queryable.

**M5 — Eval, and 1.0 release.** Reclassify `gzkit/eval` as instruction-surface
linting. Define eval = replayable acceptance environment producing an
`eval_result` event. Run S2 plus one project-specific eval on the foreign
substrate. Release v1.0.0 through the ceremony.

**Explicitly post-1.0:** Movement B's widening, `ADR-0.37.0`, the oversized-module
census, RECALL, the 199-item pool, S3–S6, benchmark integration, contract-test
channel.

---

## 8. The 1.0 demonstration

> A **non-Python repository gzkit does not own** is initialized with
> `pip install py-gzkit && gz init`. It receives gzkit's mechanisms and none of
> its lab jigs, and declares its own verification vocabulary, which gzkit locks.
>
> Intent is recorded as an ADR; one OBPI decomposes it into REQs, each tagged
> with exactly one proof channel. A bounded unit is claimed by a lock and
> assigned to **Harness A**. The agent loads that project's `AGENTS.md`
> (compiled from an addressable corpus, lineage-gated) and invokes **a
> third-party skill gzkit did not author** — permitted by policy, recorded with
> version and content hash — plus **one MCP tool** from the declared allow-list.
>
> Implementation happens. `artifact_edited` flows **from the harness adapter,
> not from the agent's claims.** Verification runs in the project's own locked
> vocabulary and produces ARB receipts with real exit codes and SHAs.
>
> **A fresh-context reviewer on Harness B — a different vendor —** is dispatched;
> its findings land as `review_finding` events with dispositions. Gate 5 cannot
> be reached without them, and a negative control proves the refusal.
>
> A project-specific eval runs and records an `eval_result`. A human attests in
> their own preserved words. A `ruling_issued` event settles one open question.
>
> **Then the harness is closed.** A *third* agent, fresh, on a *third* harness,
> runs `gz context <ADR-ID>` and reconstructs from the ledger alone: what was
> intended, what was done, by which agent under which harness, using which skill
> at which version, verified by which command with which exit code, reviewed by
> whom with what findings, evaluated how, attested by whom in what words, and
> what was decided — **and continues the work.**

gzkit is roughly 70% of the way there. The missing pieces are the foreign
substrate, the harness adapter, foreign skill/tool identity, the review witness,
the eval entity, and the ruling entity.

---

## 9. Final synthesis

**GZKit 1.0 should be:** the durable control, evidence, and evaluation substrate
that lets *someone else's project* run modern agentic development through
commodity harnesses, skills, and tools — and afterward prove, to a fresh agent
with no context, exactly what was intended, done, verified, reviewed, evaluated,
decided, and by whom. Architecturally complete across all ten layers;
implemented narrowly enough that one sortie on one foreign repo demonstrates the
whole loop.

**GZKit should own:** the ledger; evidence receipts binding claims to real exit
codes and SHAs; the enforcement-claim negative-control discipline; human
attestation semantics; intent→REQ→proof-channel traceability; session and agent
identity; findings, rulings, and decisions as distinct entities; the
resumability contract; the policy layer over skills and tools; the acceptance/eval
environment and its results; and the Firewall deciding what an adopter inherits.

**GZKit should deliberately not own:** the agent loop, subagents, context
management, permissions, planning; skill content, procedures, or a marketplace;
tool runtime, discovery, or transport; the spec methodology; benchmark harnesses;
project scaffolding for any language; security scanners; and — the one it
currently owns and must stop — five mirrored copies of its own instruction
surface.

**The most important architectural invariant is:** *no completion claim may rest
on the claimant's own assertion.* Every mechanism worth keeping specializes it —
receipts over "tests pass," `@covers` over "requirement satisfied," negative
controls over "this is enforced," independent review over self-review, human
attestation over agent confidence, `verifier-pipe-gate` over a false green.
Everything that can be cut without weakening that sentence should be cut.

**The largest mistake the current Road-to-1.0 could make is:** continuing to
spend its `feat` budget governing gzkit rather than making gzkit
governable-by-others — and shipping a 1.0 that is architecturally magnificent,
internally consistent, exhaustively self-verified, and impossible for anyone else
to run.

**The single most important change recommended to the campaign is:** give the §5
external-forcing-function gate an owning Movement and sequence it first. Make M1
*"runnable by a non-Python repo gzkit does not own"* and M2 *"fly S1 against
it,"* then let the **debrief** — not further self-inspection — set the scope of
Movements 3–5. This respects ADR-order-is-absolute: it does not jump the ADR
queue, it changes what the next ADRs are about.

**The end-to-end proof that GZKit has reached 1.0 is:** §8, in full — culminating
in a third agent, on a third harness, with no context, reconstructing the entire
chain from the ledger alone and continuing the work.

---

## Corrections after reading primary sources (2026-08-17, post-interview)

> **Cause, stated plainly.** §§1–9 above were built substantially on the campaign's
> *transcriptions* of its ADRs rather than the ADR bodies. Those transcriptions are lossy in
> a consistent direction: **they preserve status, counts, and citations and drop the
> reasoning.** Reading the campaign therefore produced confident, wrong characterizations of
> three feature ADRs. This is Architectural Boundary 6 turned on the reviewer — a transcribed
> view is Layer 3 and never source-of-truth — and it is the operator's in-session correction:
> *"i fear that you riff on things without rereading docs."* Logged as an `improvement`
> insight, `.gzkit/insights/agent-insights.jsonl`, 2026-08-17.

| § | Claim made above | What the primary source says |
|---|---|---|
| 4, E | Airlock is over-built ceremony; hold the invariant, defer the mechanism | `ADR-0.33.0` § Persona: the airlock *"earns trust by **biting**, never by ceremony — a gate that cannot refuse GO is theater."* It is **memory AND gate by design**: Positive #1 is *"Prosthetic memory… it is HANDED the bounded seam-set on entry"*, and the gate is what makes *"map-maintenance an unavoidable byproduct of any work."* The gate exists to keep the memory honest. **Both, deliberately — not ceremony.** |
| 6.6 | 20-of-23 empty seam-maps is an undetected defect whose pre-mortem "came true" | **Disclosed, dated, operator-attested 2026-07-10** as § *Calibration frontier*, naming the exact cause (`reach` returns transitive dependents; leaf OBPI has none; `parent_invariants` never passed) and deliberately holding Stage 1 **diagnostic-only** so a mis-calibrated gate cannot *"2am-wall a real pipeline."* A scheduled residual, not a surprise. |
| E | `ADR-0.37.0` = "6 OBPIs to make a 23-transit mechanism compute non-empty maps"; move post-1.0 | It repairs a **self-granting accounting predicate**: `accounted = inv in brief_text` (`airlock/enter.py:146`) is a substring test over a file **the entering agent controls** — *"the cheapest way to clear six invariants would be to paste six headings."* D2 inverts direction so neither arm is paste-clearable. It also **withdrew its own D1 on measurement** (inverse `reach` returns a constant `{parent ADR, PRD}`, identical across `-01/-02/-05`: *"converts an EMPTY seam-map into a CONSTANT one… ADR-0.33.0 § Negative #1 reproduced inside its own repair"*), and caught the coupled-surface consequence that all six briefs could edit the very Boundary Invariants granting them accounting. **Not tuning.** |
| 5 (Decision 5b) | Framed as an open decision requiring an operator ruling | **Already ruled and recorded** in `ADR-0.36.0` § Intent, operator verbatim: *"step 4b is just for obpi feature work, like handoffs, and the airlock."* Asking for it induced re-adjudication of settled canon — the disease Movement D exists to stop. |
| E, F | Drop `ADR-0.36.0` OBPI-09 (the `AskUserQuestion` door) from 1.0 | OBPI-09 is the **always-on** arm, and *"Install an **always-on '2nd opinion'**"* is the ADR's first sentence. Dropping it guts the thesis. The governing metaphor is **CRM (Crew Resource Management), not adversarial review** — a distinct concept from Step 4b, which the same Intent explicitly scopes to OBPI feature work. **Recommendation withdrawn.** |
| C, 3.4 | "Skills-as-Content is the root cause of skills-interop failure" | `architectural-identity.md` § *Skills as Content* is **ten lines** showing the canonical + four-mirror file layout. It makes **no claim about foreign skills**. The causal story was invented from a heading. The honest finding is a plain **absence** — nothing in the repo addresses foreign skills either way. |
| E | `ADR-0.35.0` is inward plumbing needing an outward reframe | It drains three facades on the surface **every agent loads every turn**: a witness that cannot fail (`composer.py:63-65` reports `compressible_bytes_after` = 22,378 vs `before` = 354 — *"a 63x inflation labelled compression"*), an attested-and-floor-gated `codex.md` setpoint that **nothing plays back** (*"a setpoint with no playback is an unfalsifiable claim"*), and **only 31.2% of AGENTS.md witnessed** (9,966 B of 31,990 B; 8 of 22 sections). The reframe is still worth doing; its **value was mischaracterized**. |
| 3.11 | Eval scorer is deterministic structural scoring, not model-in-loop | **VERIFIED — claim stands.** `_has_section`, `_section_body`, `_count_sections`, `_score_from_ratio`; per-surface scorers dispatched by `SURFACE_SCORERS`. |

**Net effect on the recommendations.** Ruling 0b (airlock stays in 1.0) is **better justified than
this review's own analysis** — declining the deferral was correct. The five layer-parity findings
of §3 stand unchanged; they rest on measured absence (grep, ledger, registry), not on ADR prose.

## Operator Decisions

Recorded as ruled during the review interview. Verbatim operator words preserved.

| # | Decision | Ruling | Operator words | Date |
|---|---|---|---|---|
| 0 | Which trajectory station is 1.0 | **BOTH — public product AND personal toolkit. 1.0 = a complete and contemporary toolkit for agentic work. Scope is negotiable per item; the standard is not.** | *"I want it to be a complete and contemporary toolkit for agentic work, but I am willing to let scope change on some things. public product and personal toolkit."* | 2026-08-17 |
| 0a | Layer scope for the five radar-blind layers (B harness · C foreign skills · D MCP/tools · F agent+session identity · J eval) | **ALL FIVE, PROPERLY BUILT.** Capability-modelled harness adapters, skill trust/provenance policy, real MCP governance, full session/agent model, eval suite with baselines. Not thin instances; not schema-only. | *"All five, properly built"* (selected against a stated cost of "quarters of work" and "highest risk of 1.0 receding") | 2026-08-17 |
| 0b | What comes OUT of 1.0 to fund 0a | **NOTHING. The standard is not negotiable; the calendar is.** 1.0 retains every current §5 gate — including "membrane on the real doors" and "accretion reduced" — plus ruling 0a. Target moves to ≈April 2027 **by declaration, not by slippage.** §5's `FINITE` framing must be re-cut to state the enlarged gate set and a declared date, or it becomes a false claim. | *"Nothing — move the date instead"* | 2026-08-17 |
| 1 | Forcing function: gate or driver | **GATE, in strict ADR order.** Portability + the `flighttest` verb become `ADR-0.38.0`, authored after `0.35.0`/`0.36.0`/`0.37.0` land. ADR-order-is-absolute holds; no exception granted; the pull-ahead and the fly-a-Python-substrate-now options are both **declined**. Accepted consequence, on the record: the forcing function **certifies rather than informs** — the ~25 queued OBPIs are built on internal judgment, and external signal reaches the project ≈95 days out at the observed 3.8-day OBPI rate. **Residual still owed:** §6 has no owning checkbox for this gate; add one reading "flies after `ADR-0.38.0`" so it stops being an unowned 1.0 gate. | *"Wait for ADR-0.38.0 in strict order"* | 2026-08-17 |
| 2 | Execution/orchestration ownership | **HYBRID — adapter by default, runner for integrity gates only.** gzkit invokes the cross-vendor reviewer (Codex) itself and records the verdict; Gate 5 reads gzkit's record, never the subject agent's claim. Rationale: a self-summoned adversary is not an adversary. `pipeline_dispatch.py` shrinks to a recorder for all non-integrity dispatch. Full orchestration is **declined** (Failure Mode A). README's "agent runner" language is narrowed to match, not deleted. | *"Hybrid — runner for integrity gates only"* | 2026-08-17 |
| 3 | Verification vocabulary ownership | **RESOLVED BY 0 — project declares, gzkit locks.** A public product cannot hardcode `uv`/`ty`/`unittest`/`mkdocs`. Blocking for the §5 flight-test gate. | *(implied by 0)* | 2026-08-17 |
| 4 | Foreign skill/tool minimum knowledge | **RESOLVED BY 0a — beyond thin.** "Properly built" means skill trust/provenance policy and real MCP governance, not merely `name@version` + hash + invocation event. | *(implied by 0a)* | 2026-08-17 |
| 5a | Step 4b before Gate 5 on OBPI completion | **MANDATORY, UNCONDITIONAL.** No lane, kind, sensitivity, or sampling exception. Evidence: 28 completions/month and falling; 17 validations returned 6 `not-refuted` / 7 `refuted-with-caveats` / 4 `refuted` — **65% found something**, including a negative control that was itself a gameable facade and two taxonomy scanners that would have shipped a permanent gate inert. ~28 cross-vendor round-trips/month. | *"yes, absolutely yes"* | 2026-08-17 |
| 5b | Step 4b on GHI direct-fix / MX work | **NOT PRESENTLY.** OBPIs are feature implementation — new intended behavior; GHI direct fix is repair and correction. A defective ADR/OBPI revisited via GHI is an **airworthiness directive**, not a new feature. **Step 4b is QC for new feature work**; the gate is part of feature validation through attestation. **Canon-backed, not new doctrine:** AGENTS.md §3 already rules *"MX-produced contract change = patch + AD artifact"* (operator ruling 2026-06-20), and `ADR-0.0.74` seats the FAA/regulator frame. | *"not presently. obpis are feature implementation - new intended behavior. ghi direct fix is repair and correction… akin to an 'airworthiness directive'… So, the 4b gate is QC for new feature work."* | 2026-08-17 |
| 5c | Airlock purpose — **corrects this review's classification** | **NOT a verification gate.** Airlock = *"an awareness and synthetic memory approach to keep an agent oriented about its actions within the system… control movement within the project when the agent enters that environment… keep the agent focused and oriented, watch for contamination, and monitor results/disturbance."* Airlock + handoff **cooperate to provide synthetic memory.** This moves the airlock from §4's "own the invariant, defer the mechanism" to a **Layer F** mechanism gzkit should own — and independently justifies ruling 0b. | *(operator, verbatim above)* | 2026-08-17 |
| 6 | Airlock 1.0 scope | **RESOLVED BY 0b — stays IN.** Movement B and `ADR-0.37.0` retained; the review's recommendation to hold the invariant and defer the mechanism is **declined**. Calibrate-before-widening (Movement B item 0) remains the internal sequence. | *(implied by 0b)* | 2026-08-17 |
| 7 | PRD disposition | **RESOLVED BY 0 — rewrite.** A public product cannot carry a top-of-hierarchy doc whose Non-Goals forbid what ships (`ADR-0.18.0` subagent dispatch). | *(implied by 0)* | 2026-08-17 |
| 8 | `ADR-0.35.0` framing | **RESOLVED BY 0 — adopter-facing `AGENTS.md` compiler.** Same ten OBPIs, outward framing. Zero added cost. | *(implied by 0)* | 2026-08-17 |
| 10 | Movement D absorbs the orientation problem | **YES.** Re-adjudication and mis-orientation are one defect with one mechanism — this plan is what `session_orientation.py` hands every fresh session, and its ADR transcriptions drop the reasoning. | *"Movement D should absorb the orientation problem. a handoff is there to orient a new session from the prior session - it is an advisory shift change orientation."* | 2026-08-17 |
| 11 | Substitution for the simultaneity FAA requires | **a + b + c.** (a) the operator is the overlap — the only party continuous across both sessions; (b) the ledger is the overlap — outgoing verifies its own claims against L2 before exit; (c) time-inverted overlap — incoming books `handoff_discrepancy` findings after working. | *"it really is a + b + c."* | 2026-08-17 |
| 12 | Position Relief Checklist as a gzkit artifact | **YES — per-project and schema-validated**, mirroring FAA's facility-specific checklist. gzkit has one global handoff template today. | *"yes to checklist"* | 2026-08-17 |
| 13 | Handoff authority | **ADVISORY / INFORMATIVE ONLY.** No beat may gate anything. Confirms `OBPI-0.37.0-05`: authorization migrates to the airlock; the handoff keeps only briefing — the `AGENTS.md:345` three-system fence realized in mechanism. Equal responsibility survives via (c), making responsibility *legible* rather than enforced. | *"handoffs are advisory/informative to operator"* | 2026-08-17 |
| 14 | `gz git-sync` after handoff creation | **ALWAYS PERMITTED — never gated.** Restatement of standing canon (`ADR-0.37.0` BI #5 + two forcing-function answers). Verified: `handoff_resume_gate.py:290` `exempts=EXEMPTS_NONE` is **accurate** — its arm is `Write\|Edit\|NotebookEdit`, `git-sync` runs through `Bash`. No defect. | *"a git-sync is always a permitted first operation after a handoff is created"* | 2026-08-17 |
| 15 | `finding` entity in Movement D scope | **YES.** `handoff_discrepancy` as a typed finding; `finding` as a kind distinct from facts, judgments and decisions (§4 / Principle 5). | *"yes, findings in scope for Movement D"* | 2026-08-17 |
| 16 | Campaign amendment | **DRAFTED AND RATIFIED**, incl. three coupled §5/Movement-D body edits. Owed and not done: the flight-test gate's §6 checkbox (a sequencing act). | *"ratify the body edits and git-sync"* | 2026-08-17 |
| 9 | Radar registry widening | **RESOLVED BY 0 + 0a — widen to all five blind layers.** "Contemporary" is a claim holdable only by measuring; §3.1 shows the instrument's blind spots and the roadmap's gaps are the same shape. | *(implied by 0, 0a)* | 2026-08-17 |
