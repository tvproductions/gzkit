# Harness Engineering — gzkit Appraisal

> **Source:** Birgitta Böckeler, ["Harness Engineering"](https://martinfowler.com/articles/harness-engineering.html), martinfowler.com (2026)
>
> **Companion:** Böckeler + Chris Ford video deep-dive on the "sensors" axis of harness engineering (linked from the article)
>
> **Authored:** 2026-04-26 in design dialogue. Companion to the [improvement plan handoff](../../.gzkit/handoffs/2026-04-26-harness-engineering-improvement-plan.md). This appraisal is the substantive evaluation; the handoff is the routing artifact that decomposes the appraisal into Wave 1 / 2 / 3 work.

## Framing

Böckeler's frame is a 2×2: **feed-forward (guides) vs feedback (sensors)** crossed with **inferential (LLM-judged) vs computational (deterministic)**. The thesis is that "harness engineering" — the practice of wrapping a coding agent in this 2×2 of supports — is what distinguishes successful agent-driven engineering from "reckless vibe coding" that compounds entropy over time. The mechanism is a steering loop where humans reinvest in the harness whenever a class of failure surfaces: name the failure, push it from inferential (LLM judge) to computational (deterministic check) wherever possible, then delete the guide that became redundant.

gzkit IS a harness-engineering project by design. The `MAKE LLM STOCHASTIC VIBES INERT` mantra in `AGENTS.md` is the harness-engineering thesis stated as canon. The 5:1 governance-to-output ratio is the product, not overhead. This appraisal evaluates how well gzkit instantiates that thesis, where its specific instantiation is unusually strong, where it has named gaps, and where the article reveals blindspots gzkit doesn't currently surface.

## The 2×2, Mapped to gzkit

|  | Inferential (LLM-judged) | Computational (deterministic) |
|---|---|---|
| **Feed-forward (guides)** | `AGENTS.md`, `CLAUDE.md`, `.claude/rules/**`, `.gzkit/skills/**`, ADRs, OBPI briefs, personas | `gz` CLI surface, `ruff --fix`, `ty`, pre-commit hooks, ARB-canonical step commands, OBPI pipeline runtime |
| **Feedback (sensors)** | `quality-reviewer` / `spec-reviewer` subagents (invoked manually) | `gz validate --<scope>` (≥12 scopes), `gz check`, `gz cli audit`, `gz adr audit-check`, ARB receipts, ledger reconciliation, coverage floor (40%) |

## Where gzkit Is Exceptional

- **ARB receipts pin observed evidence, not narrative.** Böckeler's "GPU→CPU" lift — push from probabilistic claim to deterministic check — is exactly what `arb-step-*` receipts encode. The canonical-invocation table in `AGENTS.md § Attestation` closes drift that would otherwise be invisible. This is unusually rigorous compared to typical agent setups.
- **Promotable→Mechanical lifecycle is explicit.** `docs/governance/advisory-rules-audit.md` classifies every rule as Mechanical / Promotable / Judgment / Ambiguous and tracks promotions under GHIs. This is the article's central recommendation institutionalized — it makes the LLM-to-deterministic ladder Chris Ford described into a continuous practice rather than a one-time conversion.
- **Self-testing meta-sensors.** `gz validate --advisory-scorecard` fails when a rule file lands without a scorecard entry. This is exactly the kind of harness-fitness check the article gestures at — the harness contains a check that the harness itself was extended correctly.
- **Reinvestment in the harness is visibly tracked.** Almost every invariant in `.claude/rules/**` carries a GHI number (#195, #234, #270, #307, #322, #323, etc.). The "reinvestment vs reckless vibing" delta Chris named is the gzkit working pattern, evidenced in the rule files themselves.
- **Test semantics over strings (Invariant 6f).** The `tests.md` rule, plus the eval-awareness corollary about audit-helper naming, addresses precisely Böckeler's "test pinning string instead of purpose" concern. The naming of the failure class is unusually precise.
- **Custom validator messages with rationale.** Rules like `.claude/rules/pythonic.md` on `# type: ignore` syntax mirror her custom-lint-message pattern (positive prompt injection telling the agent *why* and *how to recover*).
- **Operator Economy of Effort** directly answers the article's bottleneck-shifted-to-human concern: draft → review → decide → attest is the same shape as her "stack sensors so the human only adjudicates exceptions."

## Where gzkit Can Improve

- **No in-session sidecar.** Sensors are gated at commit, OBPI completion, or `gz check`. There is no live process watching edits and feeding deltas back to the agent during a session — the most distinctive thing in Böckeler's experiment. The OBPI pipeline is ceremony, not continuous quality feedback. This is a real gap; agents work blind between gate transitions.
- **Mutation testing is absent.** Coverage floor (40%) is a weak signal — exactly the failure mode Böckeler demonstrated (100% statement coverage, zero unit tests, missing assertions). gzkit's own Invariant 6f names this problem; the mechanical defense is missing. `cosmic-ray` (cross-platform; `mutmut` requires `fork()` and is Unix-only) is the natural fit. Already booked as `OBPI-0.31.0-07-mutate` (port from airlineops `src/opsdev/commands/mutation_tools.py`).
- **Property-based testing is absent.** `hypothesis` would catch logic gaps in the kind of derivation code gzkit has (semver/lifecycle/REQ-ID resolution, ledger event derivation, ARB receipt parsing). The `unittest`-over-`pytest` decision in STDLIB-FIRST DOCTRINE is principled but eliminates one path to property testing without acknowledging the cost.
- **Fuzz testing is absent.** Less critical for gzkit's surface but worth naming as a gap.
- **Inferential sensors are deliberately suppressed but not replaced.** `quality-reviewer` and `spec-reviewer` exist as subagents but aren't part of any pipeline stage. The anti-vibing posture is principled, but the article's point is that LLM-judges are good for *fuzzy* dimensions where deterministic checks can't reach. Foregoing them entirely cedes coverage of architectural-smell, naming-quality, abstraction-leakage failure classes.
- **Code-mods / language-server integration is light.** `ruff --fix` and direct edits dominate. No JetBrains MCP, no OpenRewrite-style migrations. For repeated patterns (e.g. the `# type: ignore[code]` sweep in GHI #197, the `PYTHONUTF8=1` purge in GHI #275), code-mods would be lower-vibing than agent rewrites.
- **Dependency freshness as a continuous sensor is missing.** STDLIB-FIRST prevents *adding* dependencies poorly; it doesn't tell you when existing ones rotted.
- **No sensor-health aggregator surface.** `gz status` and `gz state` show governance state, not "which `gz validate` scopes are currently red and what's the delta from last commit." Böckeler's sidecar dashboard had this; gzkit operators have to run `gz check` and read.

## Blindspots The Article Reveals

1. **Harness fitness is unmeasured.** No data on which `gz validate --*` scopes ever fire, how often, or whether the cost of each is justified. The advisory scorecard classifies rules but doesn't measure their hit rate. "Sensor debt" is a real concept; gzkit doesn't track it.
2. **The guides-vs-sensors balance has never been tested.** Böckeler's sharpest question — *"with good sensors, how many guides could we delete?"* — is not asked of `AGENTS.md`. The contract argues at length why it must be heavy ("Why this contract is not minimal") but the argument is *a priori*. There is no experiment showing which markdown content is load-bearing vs redundant given the validator surface.
3. **"Illusion of quality" via heavy gates.** A green `gz check` + ARB receipts can produce false confidence that the gate covenant equals correctness. Foundation-kind brief-level attestation is gzkit's defense, but it's a *human* defense — the system is asking the operator to be the discriminator at exactly the moment the operator's attention has been most economized away. This is the seatbelt-paradox version Chris pushed back on, but in gzkit's case it's worth taking seriously: the OBPI ceremony rhythm could lull the witness.
4. **Behavior-correctness vs harness-correctness is conflated.** Tests pass, gates green, ledger consistent — gzkit can verify all that with high rigor. None of it answers *"does the code do what was needed?"* Böckeler's note ("there was an error in my functional specification") applies. gzkit's BDD layer (`features/`) is the closest answer but is REQ-derived, so the same misconception in the brief produces a passing scenario.
5. **Sensor sprawl has no bounding rule.** No invariant says "every new validator scope must displace, fold into, or measurably reduce a prior one." Surface area grows monotonically. `gz-context-diet` is a *manual* response; the systemic pressure to add a new check on every observed failure is unbalanced by any pressure to remove redundant ones.
6. **The `unittest`-over-`pytest` decision has an unacknowledged property-testing cost.** `hypothesis` is mature on `pytest`, awkward on `unittest`. STDLIB-FIRST is principled, but the doctrine doesn't name what it foregoes.
7. **Production runtime feedback is undoctrinated for downstream gzkit-governed projects.** gzkit binds dependency, testing, and CLI doctrine on adopters; it doesn't bind anything about how those projects wire production telemetry back into their own harness loops. This is the article's fourth deployment tier; gzkit is silent on it.

## The Sharpest Tension

The article's framing is that **guides anticipate, sensors observe**. gzkit invests massively in both. If you read `AGENTS.md` and the rules together, the outer harness here is *very* thick — among the thickest I've seen. The cost is paid every turn; the payoff is real (the GHI ledger shows defects caught the surface previously missed). But until gzkit can show *which* guides are still load-bearing in the presence of the current validator surface, the contract is heavier than it has to be on at least one axis. That's the highest-leverage place to look — not adding more, but proving (or disproving) that some current guide is now reachable from sensors alone, then deleting it.

The two concrete additions that emerged as highest-priority from this appraisal: **mutation testing as a `gz validate --mutation` scope** (closes the Invariant 6f gap mechanically) and **an in-session sensor sidecar** that streams `gz validate` deltas to the agent during edits. Both are on the [improvement plan](../../.gzkit/handoffs/2026-04-26-harness-engineering-improvement-plan.md) — mutation testing in Wave 1 (already booked as `OBPI-0.31.0-07-mutate`), sidecar in Wave 2 (`ADR-pool.harness-sidecar`).

## External Validation — Greyling on Claude Code (recursive case)

> **Source:** Cobus Greyling, ["98% of Claude Code Is Not AI"](https://github.com/cobusgreyling/98-percent-claude-code-not-ai), summarizing a 46-page reverse-engineering study of Claude Code's TypeScript codebase (paper cited by Greyling at `arxiv:2604.14228`; the blog is the consulted artifact).
>
> **Framing:** Greyling's thesis is structural rather than 2×2 — a codebase-ratio breakdown. By the community estimate Greyling cites, ~1.6% of Claude Code's codebase is AI decision logic; ~98.4% is operational infrastructure organized into five subsystems (permissions, context management, safety layers, extensibility, session persistence). The headline: *"The harness is the product. The model is a commodity input."*

### Triangulation with Böckeler

Böckeler's 2×2 (feed-forward vs feedback × inferential vs computational) and Greyling's five-subsystem ratio framing are independent published harness theses. Both converge on gzkit's stance: heavy harness investment is the production-reliability story; "lighter ceremony" is not the relevant tradeoff axis. The gaps Böckeler exposes (in-session sidecar, mutation testing, property testing, harness-fitness measurement) are reinforced, not contradicted, by Greyling's framing — the per-tool-call permission gate Greyling describes is the runtime analog of the in-session sidecar Böckeler identifies as gzkit's largest gap.

The independent convergence is itself the doctrinal signal: two unrelated 2026 publications, different framings, same conclusion — the harness is the product. gzkit canonicalized the same claim in `AGENTS.md § MAKE LLM STOCHASTIC VIBES INERT` operative claim 1 (*"5:1 governance-to-output ratio is the product, not overhead"*) before either external source landed.

### gzkit as the recursive case

Claude Code's harness wraps the model; gzkit's meta-harness wraps Claude Code's outputs in governance state. The same logic that justifies Claude Code's 98.4% operational infrastructure justifies gzkit's 5:1 governance-to-output ratio — the audit surface is wider, so the harness must be thicker. **gzkit's own runtime sits at the asymptote of this principle: ~100% governance scaffolding, 0% AI decision logic in `src/gzkit/`.** gzkit does not call the LLM in its own runtime; the LLM operates *through* gzkit's meta-harness via the upstream Claude Code harness. The recursive framing: *Claude Code makes the harness the product; gzkit makes the audit trail the harness's product.*

### Subsystem mapping

| Greyling subsystem (Claude Code, Layer 1) | gzkit Layer-2 analog | Time-scale | Note |
|---|---|---|---|
| Permissions (deny-first, ML classifier, 7 modes) | Gate covenant (Gates 1–5, sensitivity matrix) | per-ceremony, not per-tool-call | Different tier — permission asks *"can this tool run now"*; gate asks *"is this work complete"*. The per-tool-call axis is delegated to Claude Code's permission system. |
| Context management (5-layer compaction) | SessionStart re-injection + `gz-context-diet` skill + `gz validate --instructions-files-budget` | authoring-time + session-start | Runtime compaction is delegated to Claude Code; gzkit budgets the *persistent instruction surface* so doctrine drift doesn't eat the window. |
| Safety (structural, 93% rubber-stamping insight) | Advisory-rules-audit scorecard; Promotable→Mechanical ladder | continuous | The independently-arrived-at insight — see [`advisory-rules-audit.md` § Why this audit exists](advisory-rules-audit.md). gzkit's "9 silent failures over weeks" outage is the local-evidence version of Greyling's "users approve 93% of permission prompts." |
| Extensibility (skills, hooks, MCP, plugins) | Skill catalog + 3-mirror sync + personas | continuous | gzkit invests further by mechanizing mirror-drift fail-closed (`gzkit.hooks.guards.forbid_skill_sync_drift`, scorecard row #33). |
| Session persistence (transcripts, settings) | Ledger-of-truth (T2 source-of-truth) + session handoffs | persistent | **Kind shift, not just extension.** Claude Code's session is for replay; gzkit's ledger is *load-bearing governance state* that outlives the agent — state-doctrine `§` "derived views are never source-of-truth" applies. |

### What this triangulation does NOT change

Greyling's analysis reinforces the existing Böckeler-derived improvement plan; it does not unlock new mechanical promotion candidates beyond what's already tracked in the advisory scorecard. The honest output of this triangulation is doctrinal clarity (the recursive framing) and external validation (two independent published theses converge), not new validator scopes. The Böckeler-identified concrete additions — mutation testing (Wave 1, `OBPI-0.31.0-07-mutate`) and in-session sensor sidecar (Wave 2, `ADR-pool.harness-sidecar`) — remain the highest-priority structural moves; the Greyling axis adds an external second-opinion that they are correct, not a third item.

## Cross-References

- Source: <https://martinfowler.com/articles/harness-engineering.html>
- Greyling axis source: <https://github.com/cobusgreyling/98-percent-claude-code-not-ai>
- Improvement plan handoff: [`.gzkit/handoffs/2026-04-26-harness-engineering-improvement-plan.md`](../../.gzkit/handoffs/2026-04-26-harness-engineering-improvement-plan.md)
- Booked work: [`OBPI-0.31.0-07-mutate`](../design/adr/pre-release/ADR-0.31.0-new-cli-command-absorption/obpis/OBPI-0.31.0-07-mutate.md)
- Doctrine roots cited: `AGENTS.md` §§ MAKE LLM STOCHASTIC VIBES INERT, STDLIB-FIRST DOCTRINE, OPERATOR ECONOMY OF EFFORT, Attestation; `.claude/rules/tests.md` § Invariant 6f; `docs/governance/advisory-rules-audit.md`; `docs/governance/state-doctrine.md`
