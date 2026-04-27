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

## Cross-References

- Source: <https://martinfowler.com/articles/harness-engineering.html>
- Improvement plan handoff: [`.gzkit/handoffs/2026-04-26-harness-engineering-improvement-plan.md`](../../.gzkit/handoffs/2026-04-26-harness-engineering-improvement-plan.md)
- Booked work: [`OBPI-0.31.0-07-mutate`](../design/adr/pre-release/ADR-0.31.0-new-cli-command-absorption/obpis/OBPI-0.31.0-07-mutate.md)
- Doctrine roots cited: `AGENTS.md` §§ MAKE LLM STOCHASTIC VIBES INERT, STDLIB-FIRST DOCTRINE, OPERATOR ECONOMY OF EFFORT, Attestation; `.claude/rules/tests.md` § Invariant 6f; `docs/governance/advisory-rules-audit.md`; `docs/governance/state-doctrine.md`
