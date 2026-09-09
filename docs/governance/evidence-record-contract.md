# Evidence-record contract

> **Status:** proposed, authored 2026-09-08 under an operator ruling. **Not yet ratified and
> not yet mechanically witnessed.** It selects a repair direction for the evidence record; it
> does not attest OBPI-0.35.0-05 and does not authorize Stage 5.

## Origin

OBPI-0.35.0-05 ran eleven Step-4b adversarial rounds. **No round from 8 through 11
demonstrated a production defect.** Every finding was against the *evidence record*, and
rounds 10 and 11 found their defects inside the agent's own repairs to that record — the
defect reproducing within its own fix.

Operator ruling 2026-09-08, verbatim, correcting the agent's proposed remedy:

> **tool-generated evidence does not make false claims structurally impossible.** A command
> can faithfully reproduce a tautology or measure the wrong thing. Interpretation still needs
> independent review.

> Do not prohibit numbers or classifications merely because they appear in analysis—the
> requirement is traceable support and honest qualification.

The agent had claimed that publishing raw artifacts would have made rounds 10 and 11's
findings "structurally impossible." **That claim is withdrawn as untested.**

## The five requirements (binding once ratified)

1. **Preserve raw artifacts and bind them to the revision, command, environment, and actual
   result.** An artifact floating free of the tree that produced it is not evidence.
2. **Each acceptance claim must identify its supporting artifact and explain exactly what the
   observation establishes. Merely naming a command is insufficient.**
3. **Counts, locations, and failure classifications must come from inspected results. Claims
   of isolation, independence, exclusivity, or completeness require specific demonstrations;
   they cannot be inferred from a green run.**
4. **Keep agent interpretation explicitly distinguishable from observed evidence.** Numbers
   and classifications are permitted in analysis; the requirement is traceable support and
   honest qualification, never silence.
5. **Step 4b must judge whether the evidence supports the claim, including whether the
   measuring method itself is sound.**

## Tested against the actual failures of rounds 10 and 11

Per the ruling, the contract is tested rather than asserted. **Round 12
(`arb-step-codexadversary-3e166363a03243adb5fc29f6d71bd7db`) refuted the first version of
this section** for conflating two different things under one "prevented" column, and for
asserting an unmeasured rate reduction. Its correction is adopted: three distinct columns.

- **Auto-enforced** — a mechanism fails closed without author cooperation.
- **Excluded by compliant authoring** — if the author actually performs what the requirement
  demands, this defect does not occur. Nothing forces compliance.
- **Retrospectively detectable** — a reviewer holding the artifacts can fault it. All five
  Yes cells here are *historical* detections that did happen; they are not a guarantee of
  future detection.

| # | Actual failure | Auto-enforced | Excluded by compliant authoring | Retrospectively detectable |
|---|---|---|---|---|
| 1 | Census said **144**; actual **145** (whitelist dropped `self.assertIsInstance`) | **No** | **No** — R1 requires disclosing the method; disclosure does not stop the author choosing an unsound one. The 144 was a faithful run of a wrong method | Yes — round 10 recounted |
| 2 | Literal comparison attributed to `:940`; it is `:939` | **No** | **Yes** — R3 requires locations come from inspected results; inspecting rather than recalling excludes it | Yes — round 10 checked the line |
| 3 | Wrote *"All 17"*, enumerated **16** | **No** | **Yes** — R3 requires a completeness demonstration; counting the enumeration against the inventory excludes it | Yes — round 11 counted |
| 4 | `test_ownership.py:241` misfiled under the shared-parser bound | **No** | **Partial** — R4 excludes presenting a reading *as observation*; it does not make the reading correct. A wrong-but-labelled interpretation survives | Yes — round 11 traced operands |
| 5 | `103/17/25` published from an undisclosed heuristic | **No** | **Yes for the disclosure defect** — R4 requires traceable support and qualification. It does **not** make the classifier correct | Yes — round 11 produced `121/20/4` |

**Conclusion, stated at the strength the evidence carries.** The contract **auto-enforces
nothing** — no requirement here fails closed, and no validator scope is proposed. Three of
five failures would be excluded by compliant authoring, one partially, one not at all. All
five were detected retrospectively by review, which is an observation about rounds 10-12,
**not** a property of this contract.

**Effectiveness is an UNTESTED HYPOTHESIS, not an established consequence.** An earlier
revision of this section asserted that the contract *"reduces the rate of unverified claims
reaching attestation."* **That claim is WITHDRAWN**: no rate was measured before, none has
been measured since, and asserting it repeated the exact remedy-effectiveness overclaim this
document exists to address — the second time in one session (the first was *"structurally
impossible"*). Whether requiring published methods and artifacts changes the rate at which
unsupported claims reach Gate 5 is testable, and untested.

**Named residual.** A claim whose method is disclosed, plausible, and wrong in a way review
does not catch still passes. R5 is a review obligation, not a mechanism. Round 12's own
Weakest point states the residual precisely: *"Publishing a reproducible count establishes
the count under that method; neither a caveat nor earlier successful reviews establishes that
the method supports the intended acceptance claim."*

## Amendments required to existing governing surfaces

| Surface | Current state | Amendment needed |
|---|---|---|
| `gz-obpi-pipeline` SKILL.md § Stage 4 template | REQ table has `Proof location` and `Proof` columns | Add a **what this does NOT establish** column. (An earlier revision called R2 *"unsatisfiable"* without one; round 12 correctly faulted that — the existing `Proof` fields CAN carry the explanation. The amendment is to PROMPT it structurally, not to make it possible.) |
| `gz-obpi-pipeline` SKILL.md § Step 4a-v | Replays `$` transcripts; its own § *Reach* already disclaims completeness and interpretation | Add: the packet must separate **OBSERVED** from **INTERPRETATION**. 4a-v cannot check this and must say so rather than imply coverage |
| `gz-obpi-pipeline` SKILL.md § Step 4b dispatch contract | Requires re-deriving the claim from REQs and repo | Add R5 explicitly: the adversary must judge **whether the measuring method itself is sound**, not only whether the claim reproduces. Rounds 10 and 11 did this without being asked |
| `.gzkit/rules/tests.md` § Verification exit-code integrity | Governs exit codes of verifiers | No amendment. Orthogonal — it governs whether a result is real, not whether a claim about it is supported |
| `.claude/rules/governance-core.md` § *"A value written in a Markdown doc is ILLUSTRATIVE, never authoritative"* | Governs thresholds and state read by execution | **Tension to surface, not resolve.** An evidence packet is prose carrying authoritative measurements. This contract's R1 binding (revision + command + environment + result) is what distinguishes a bound measurement from an illustrative value; whether that satisfies the existing rule is an operator reading, not the agent's |

## What this contract is not

- **Not mechanically witnessed.** Every requirement is a reading. No validator scope is
  proposed here, and inventing one would repeat the doctrine-declared-without-mechanism
  family named in `AGENTS.md`.
- **Not a completion gate.** It changes what a packet must contain, never whether Gate 5
  fires.
- **Not a substitute for Step 4b.** Per the ruling: *"Interpretation still needs independent
  review."*
