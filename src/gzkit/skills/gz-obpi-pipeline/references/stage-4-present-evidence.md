<!-- Stage 4 procedure, served by the runtime at stage entry (OBPI-0.35.0-17). Every block below is verbatim from the attested baseline of .gzkit/skills/gz-obpi-pipeline/SKILL.md (body sha256 fe97fe3139282b0ceec5b11866e97efad11761d8e35a5e4977c84f3d6b388367), selected by data/obpi_pipeline_control_inventory.json: the stage's own section first, then every block from another section holding a control whose applies_at names this stage. Nothing is reworded. -->

# Stage 4: Present Evidence — served procedure

### Stage 4: Present Evidence

Stage 4 is three steps and one bounded loop:

```
4a author the packet → 4a-v replay the packet → 4b independent review → pass condition met?
   ├─ yes → present 4a + 4a-v + 4b together → await attestation
   └─ no  → ONE repair round (§ The review window) → re-enter at 4a
```

You do not get to skip 4b because your own evidence looks green. Your evidence
looking green is *why* 4b exists. You are not the exception. The sequence admits
no size, lane, or kind exception. An earlier turn or equivalent successful execution
does not invalidate review by itself; the acceptance consumer decides applicability.

#### The pass condition — stated once

**One authority.** Stage 4 passes when this command reports ready, and only then may
attestation be solicited:

```bash
uv run gz obpi acceptance {OBPI-SLUG} status --stage stage4 --json
```

Everything under this heading explains that verdict. None of it is a second test to
satisfy separately, and the rest of Stage 4 does not restate it. If this prose and the
command disagree, the command governs and the disagreement is a defect to report.

**Binding rule:** No OBPI reaches attestation without an independent adversary
review applicable to its current proof claims, with explicit closure of required
findings. A Stage 4 that solicits attestation while required Step 4b approval or
closure is missing violates the gate. A turn boundary alone requires no repeat. There is no
OBPI too small, too authoring-only, or too obviously-correct to exempt — those
are the precise descriptors that precede a skipped check.

**Step 4b closes on independent confirmation of the corrected state (operator ruling 2026-09-05).** Operator verbatim: "I think we want that as a matter of course moving forward. I don't want 12 iterations like with OBPI-0.35.0-04, but I don't think we should attest without the fixes creating a clean adversarial (4b) review."

The prior 2026-09-03 rule said: "A round returning no critical and no high IN-SCOPE findings converges the gate." This ruling supersedes that severity-only stopping condition: do not solicit completion attestation while any finding against the agreed OBPI requirements remains unresolved, or while a claimed fix has only the implementing agent's confirmation. A non-refuting verdict on the earlier state does not independently verify later repairs, including repairs to evidence or missing witnesses.

**Readiness is derived; historical verdicts are immutable (GHI #985).** Run:

```bash
uv run gz obpi acceptance {OBPI-SLUG} status --stage stage4 --json
```

Readiness requires current valid proof, accepted spec/quality/adversarial reviews
for every obligation, and independently verified closure of all mapped findings.
The ledger-backed single-driver declaration retains its documented Stage-2
spec/quality exception; proof and Step-4b closure remain mandatory.
An unchanged obligation cannot lose its finding because an auxiliary audit was
removed. An edit confined to recognized history sections does not invalidate executable proof.
The earlier GHI #964 standing-line convention is superseded as a gate: preserve
existing historical words, but never edit a Markdown verdict to change readiness.
`gz obpi precomplete` and completion consume the durable records.

**Clean means no unresolved in-scope findings, not absence of all limitations.** Accepted residual risks and future ADR-wide obligations remain disclosed separately; they are not failed present-tense OBPI requirements. Filing a GHI alone does not discharge an unmet requirement. A newly proposed boundary change requires operator ruling and independent revalidation; the implementing agent cannot move a finding outside scope to clear the gate. Before soliciting attestation, the retained independent review set must supply applicable approval and explicit closure on the corrected proof claims. Raw verdict wording alone neither grants approval nor reopens a closed obligation. Scope-boundary disclosures may remain, provided the adversary distinguishes them from unresolved findings.

Do not redispatch merely to remove harmless caveat wording after independent
closure is established. If a follow-up exposes the same root cause again, use
the design-escalation rule below. The runtime checks proof identities, current
input digests, and explicit closure links. Whether an oracle or control fulfills
the requirement remains the independent reviewer's judgment.

**Act on mapped findings before attestation.** A current counterexample or missing
required proof returns its obligation to repair, regardless of verdict or severity.
After repair, execute proof and import independent closure. Historical refutations
and auxiliary commentary with no unmet obligation do not require another repair or
review. Retain their provenance and present the applicable review set alongside
Step 4a; never relabel a required gap as auxiliary to clear acceptance.

**The gate consumes current closure (GHI #985).** A resolution string or new
caller-supplied verdict cannot discharge an open finding. Repair its obligation,
execute current proof, and import independent closure before soliciting
attestation. Historical refutations do not block a correctly closed current
state merely because their original words remain in the brief.

#### The review window, the bound, and the exit

**Know what stales a review before you touch anything.** Proof and review currency is
ONE digest over the whole audited population — `src/`, `tests/`, `features/`, `data/`,
`scripts/`, the canonical rules and schemas, the workflows and config files — plus the
brief's contract (`acceptance_execution.input_digest`). It is not per-obligation. Any
edit under those paths, however small and however unrelated, stales EVERY proof and
EVERY imported review for this OBPI at once. Edits confined to the brief's recognized
history sections and its Change Log do not move it. This is why an unplanned edit
between 4a and 4b costs a full round, and why the order below is binding.

**A round reviews a frozen subject.** Before dispatching 4b — first round or follow-up:

1. Finish every edit. Nothing is left to tidy afterwards.

2. Run `acceptance prove` for every obligation (a repair stales them all; see above).

3. Refresh the packet (`gz obpi present-evidence`) and replay it (Step 4a-v).

4. Record `git status --short` and the reviewed revision in the dispatch prompt.

5. Dispatch. From dispatch until the review is imported, edit nothing under the
   audited population: not the source, not a test, not a data file, not a rule, and
   do not `gz git-sync` in other work. An edit inside the window spends the round.

**When a round returns findings, run ONE repair round.** Collect all of them first.
Repair them as one batch (§ Repair the whole obligation, below). Then repeat steps 1–5
once, dispatching the focused follow-up described below — never one dispatch per
finding, and never a fresh unrestricted review.

After fixing a finding, obtain a focused independent Step 4b follow-up. Supply the prior findings, the changed artifacts and evidence, and the unchanged scope/threat-model boundary. The adversary must verify each claimed closure and check the affected requirements for regressions; it must not restart an unrestricted search for stronger guarantees. Record the actual new verdict and receipt, with each prior finding's disposition and demonstrated evidence. Preserve earlier rounds as history. Never request a preferred verdict or relabel `CORROBORATED-WITH-CAVEATS` as clean yourself.

**Repair the whole obligation before redispatch (GHI #984).** Carry the accepted
finding back through the existing implementation and verification stages. Trace
the relevant producers, consumers, fresh/retry paths, early returns and cleanup;
use the states needed by the requirement, not an unlimited neighboring audit.
A retry retaining its journal does not prove it restores durability before
witnessing. A rejection does not prove which guard caused it. Recheck affected
controls when a repair adds another guard that could mask them. Preserve the
complete finding and the execution record beside its closure, rather than
replacing it with a new explanatory claim.

For an operator-initiated OBPI, authorized corrections continue within its
approved scope; the initiation rule is not a new permission checkpoint for
each finding. A real requirement/allowlist/threat-model amendment still needs
the existing operator ruling. Repeated roots trigger the design escalation
below, not a round cap or a waived defect. Auxiliary diagnostic errors may be
removed from the acceptance argument when no requirement depends on them;
retain their history and every still-relevant finding. If required proof does
depend on the diagnostic, repair and verify it before using its result.

**The loop is bounded, and it has an exit.** Two focused follow-up rounds after the
first Step 4b round is the limit — three rounds in all (operator ruling 2026-09-18,
verbatim: "N=2"). When the limit is reached with a mapped finding still open, or when a round repeats the
prior round's root (next paragraph), stop dispatching:

```bash
uv run gz obpi block {OBPI-SLUG} \
  --reason "<which findings remain open, and after how many rounds>" \
  --next-action "<the design or scope decision the operator owes>"
```

Then present the open findings, what each round changed, and one recommendation. This
is the second legitimate stop in the pipeline (§ The Iron Law), not a premature summary:
another round without a decision is the failure, and recording that a human is needed
is the honest act (§ Blocked on the Operator).

**When a round repeats the prior round's ROOT, stop dispatching and escalate the DESIGN (operator ruling 2026-09-03).** Compare each round's `Weakest point` against the last. If it names the same root cause at a different surface, another fix cycle will surface it again one layer deeper: stop, and put the design decision to the operator (§ Behavior Rules — Always #9). Measured: rounds 2, 3 and 4 each patched a different surfacing of one root cause — provenance inferred from a witness's self-consistent claims rather than chained to prior ledger state — at roughly 3h per cycle; the operator ruled the design in a single exchange and it closed in one pass. Round 4's fix also INTRODUCED round 5's critical, which is the signature of patching a surfacing rather than the design.

#### Normal Mode — HUMAN GATE

**Trigger:** "Present OBPI Acceptance Ceremony" task becomes next pending. Mark `in_progress`.

**Narrator dispatch** (per § Persona Dispatch). Stage 4 evidence composition is the narrator's function — "evidence-to-decision," "operator-value-framing," "every word load-bearing." Dispatch a `narrator` subagent with the populated template fields (Value Narrative input, REQ coverage table from Stage 3, ARB receipts from quality gates) and instruct it to render the final attestation surface per the template below. The narrator dispatch has no recording channel yet (§ Persona Dispatch, GHI #846); do not improvise one through `SubagentDispatchRecord`, which accepts Stage-2 roles only.

**Compose from inspected evidence (GHI #984).** Give the narrator the actual
artifact paths and observed results, including limits, not only a success
summary. Keep one current REQ proof table; preserve prior rounds separately as
history tied to their reviewed state. The Proof cell states what the observation
establishes and any unresolved limitation. Do not invent counts, line references,
failure mechanisms, independence claims, or claims about the remedy's benefit.
Tool-emitted output establishes only what its method measures. Interpretation
must be identified as interpretation and supported; reproduction alone does not
make its method sound. Expected output may explain a planned demonstration but
cannot substitute for observed output in the Key Proof of completed work.

Load `gz obpi acceptance {OBPI-SLUG} status --stage stage4 --json` and give the
narrator its canonical obligations, current proof IDs, open findings, and imported
review records. The missing adversarial review blocks final readiness until 4b
runs; it does not prevent preparing 4a. Cite those proof IDs in the REQ table.
Preserve their executed payloads rather than reconstructing another evidence
classification. Packet replay remains a separate check of displayed transcripts.

Run `gz obpi present-evidence {OBPI-SLUG} --json` to generate Step-4a review input.
It exits 3 on proof blockers; when Stage-2 proof is ready and only Step-4b closure
is pending, it exits 0 with `attestable: false` and separate `review_blockers`.
Give that packet to the adversary. Do not confuse successful packet generation
with permission to solicit attestation. After importing independent approval and
finding closure, refresh the packet; final validation requires both proof and
review blockers to clear.

Present evidence using the **exact template below**. This is the human's attestation surface — they cannot provide attestation without seeing this output. Every field is mandatory. Do not omit, reorder, or freeform this.

**Required output template:**

```
## Stage 4: Present OBPI Acceptance Ceremony (Normal Mode — HUMAN GATE)

**1. Value Narrative**

<What problem existed before this OBPI? What capability exists now? 2-3 sentences.>

**2. Key Proof**

<One concrete command and its observed output. Cite the executed proof record.
Expected output is not evidence of completed work.>

**3. Evidence**

**Quality checks:**

> **Rendering rule (GHI #293):** Markdown table cells overflow in Claude
> Code's renderer when ARB-wrapped invocations embed their nested
> sub-command (e.g. `uv run gz arb step --name unittest -- uv run -m
> unittest discover -s tests/governance`). When a Command cell would
> exceed ~40 characters, hold a short label in the cell (e.g. `arb:unittest`,
> `arb:ruff`) and render the full incantation in a fenced code block
> beneath the table. Place the receipt ID in the Result cell. Operators
> attest against this table — overflow erodes legibility.

| Check | Command | Result |
|-------|---------|--------|
| Tests | `arb:unittest` (see below) | <N>/<N> pass — receipt `arb-step-unittest-<id>` |
| Lint | `arb:ruff` (see below) | clean — receipt `arb-ruff-<id>` |
| Typecheck | `arb:typecheck` (see below) | clean — receipt `arb-step-typecheck-<id>` |
| OBPI tests | `arb:unittest-scoped` (see below) | <N>/<N> pass — receipt `arb-step-unittest-<id>` |
| <brief-specific> | `<short-label>` (see below) | <result> — receipt `<id>` |

```bash

# arb:unittest — full unittest sweep

uv run gz arb step --name unittest -- uv run unittest-parallel -t . -s tests --buffer

# arb:ruff — lint

uv run gz arb ruff

# arb:typecheck — static type check

uv run gz arb typecheck

# arb:unittest-scoped — OBPI-scoped tests

uv run gz arb step --name unittest -- uv run -m unittest tests.<test_module> -v

```

Short Command cells (under ~40 characters, e.g. `uv run gz lint` or
`uv run gz test`) may stay inline without a fenced block — the rule
fires only when the incantation would overflow.

**Files created:**
- <path> (<description>)

**Files modified:**
- <path> (<description>)

**REQ coverage:** (every row populated; every cell concrete; BEHAVIOR rows verified by Stage 3 Phase 1b)

> **Rendering rule (GHI #301, generalizes GHI #293):** The REQ coverage
> table is the canonical single form — render it as a markdown table and
> nothing else. Do **not** append a plain-text labeled-list duplicate of
> the same rows beneath the table. When Claude Code's renderer truncates
> a cell, the fix is to shorten the cell, not to add a second rendering.
> When any cell (Mechanism, `@covers` location, Test Coverage) would
> exceed ~40 characters — long structural assertions like
> `test -d .gzkit/chores/<slug>/proofs && test -s ...`, multi-flag `uv run` invocations,
> file lists, or SHA-bearing paths — hold a short label in the cell
> (e.g. `req-01:absence-check`, `req-02:scoped-tests`) and render the
> full incantation in a single fenced code block beneath the table,
> keyed by the same label. One render, one form. The labeled-list
> fallback is the operator-confusion vector the rule exists to prevent.

| REQ | Kind | Mechanism | Proof location | Proof | Result |
|-----|------|-----------|----------------|-------|--------|
| REQ-X.Y.Z-NN-01 | BEHAVIOR | <function/mechanism> | `tests/<file>.py:<line>` or `TestClass.test_method` | <test class> (N tests) | Pass |
| REQ-X.Y.Z-NN-02 | SUPPORT | <artifact> | `<ledger event type>` + `gz validate --<scope>` | event cites path; validator admits shape | Pass |
| REQ-X.Y.Z-NN-03 | STRUCTURAL-FENCE | <invariant> | parent-ADR `## Boundary Invariants` anchor | audited at ADR closeout | Pass |

If any row uses short labels for long cells, expand them in a single fenced block immediately after the table:

```text

# req-01:scoped-tests — REQ-X.Y.Z-NN-01 (BEHAVIOR) Proof

uv run -m unittest tests.<module> -v

# req-02:support-proof — REQ-X.Y.Z-NN-02 (SUPPORT) Proof

uv run gz validate --<scope>   # structural validator admits the artifact's shape

```

The **Proof location** column is proof-channel specific, not always `@covers`. For BEHAVIOR REQs cite the `@covers` test location; for SUPPORT REQs cite the ledger event type/path and the `gz validate` scope; for STRUCTURAL-FENCE REQs cite the parent-ADR `## Boundary Invariants` anchor. A missing BEHAVIOR `@covers` location is a blocker — the Phase 1b parity gate will fail and the pipeline will not advance. **A non-BEHAVIOR REQ must never be forced into a unit test to fill the cell** (GHI #571).

**4. Awaiting attestation.** Do NOT proceed to Stage 5 until human responds.
```

**Every field above MUST be populated.** Do not skip the evidence table. Do not skip REQ coverage. Do not skip files created/modified. The human needs all of this to make an attestation decision. **This template is Step 4a — the agent's presentation. It is necessary but not sufficient: an agent authoring its own evidence is the GHI #643 fabrication surface. Step 4b is mandatory before attestation.**

#### Step 4a-v — Re-run the packet's own transcripts (GHI #942)

Write the composed packet to `.gzkit/evidence/<OBPI-ID>.stage4a.md`, then run it back
through the tool before presenting it:

```bash
uv run gz obpi verify-packet .gzkit/evidence/<OBPI-ID>.stage4a.md
```

Exit 0 = VERIFIED. Exit 3 = a pasted line did not reproduce; repair the packet and
re-run. Present the verdict alongside 4a and 4b — the operator attests against all
three.

**Why replay is separate from Step 4b.** 4b re-derives the *claim* from the REQs and
the repository; historically it was not handed the *packet*, so a fabricated transcript passed an
adversary that never looks at it. Observed 2026-09-02 on OBPI-0.35.0-04: a `$` block
rendered `gz covers --json` output with keys the command does not emit (`obpi_id`,
`coverage_pct`) around figures that were themselves correct — the numbers came from
the dispatch prompt and the *evidence was constructed around them*. It was caught only
because a human happened to re-run the commands.

**The authoring contract.** A `$` prompt is a claim — *"I ran this and this came
back"* — and every one of them is re-executed:

- **Paste only what the command produced.** The comparison is containment, so
  abridging and re-indenting are fine; a line the command never wrote is a blocker.

- **Elide what cannot reproduce.** A timestamp or a freshly minted receipt id is
  written `...`, never pasted. Pasting an unreproducible line is what fails.

- **Cite proof commands as transcripts.** A command offered as proof of a REQ goes
  under a `$` prompt with its output. The second half of the same observed instance
  was a REQ-08 proof command that returns nothing when run — as a transcript that is
  a `witnesses nothing` blocker; left bare it is only reported.

- **For a silent assert-shaped probe, show the status:** `$ <cmd>; echo "exit $?"`.
  The exit code is the information the reader needs, and it reproduces. **Then paste the
  line it emits.** The probe moves the status out of the process — the shell exits 0
  because `echo` succeeded — so a packet that appends the probe and omits the `exit 1` it
  printed is presenting a failing command as success again. Omitting it is a blocker, and
  `...` does not satisfy it: elision is for output that cannot reproduce, never for output
  you would rather not show.

- **A fenced shell block with no `$` claims no output** and is never re-run — that is
  what the `arb:` incantation blocks are, and their result is carried by the receipt
  rows. They are listed back as citations so the operator sees what was *not*
  witnessed.

- **A failing command cannot be presented as success.** A non-zero exit is a blocker
  outright, because containment alone lets a packet quote only the success lines of a
  command that failed — every quoted line reproduces, and the omission is the lie. To
  show a RED run, use the status form above **and paste the status it prints**; the
  convention is not the enforcement, and the check holds you to both halves.

- **Do not pipe a verifier into a filter.** The shell reports the filter's status, so a
  failing suite would replay green. Use `set -o pipefail` or redirect to a file.

**Reach, stated plainly.** Replay verifies *displayed output against command output*. It
does **not** prove the packet is **complete** — that the transcripts chosen are the ones
the REQs needed — nor that its **interpretation** is correct, that a reproducing command
demonstrates what the prose around it claims. It does not verify a command cited without a
prompt, and the piped-verifier guard covers recognized verifiers only, not every generic
command piped without `pipefail`. Those judgments stay with Step 4b and the operator.

#### Step 4b — Independent Adversarial Validation (GHI #643) — MANDATORY, NON-SKIPPABLE

**WHY THIS GATE EXISTS AT ALL — and why the second model is CODEX specifically.**

GHI #643: an agent presented Stage-4 evidence claiming the OBPI's central deliverable was
built and working. It was not built. `run_meta_validator()` discovered **zero** production
claims, and that was found only at Stage 5 by an operator who happened to run the brief's own
`## Demo`. **The operator had already attested "completed" against the fabricated evidence.**
No mechanical gate fired. Operator verdict, verbatim: *"you have outright lied, repeatedly, at
the pipeline's stage 4."*

That is the whole reason this gate is here. Step 4a is a model reporting on its own work, and
a model that has fabricated a deliverable will fabricate the evidence for it just as fluently.
So a SECOND model, which did not write the code and has no stake in the story, goes and checks
whether the thing actually exists and actually works.

**Codex, because a Claude checking Claude is the same eyes twice.** The failure mode is not
carelessness — it is a shared blind spot. An independent Claude subagent has a fresh context
and still shares this model's priors about what "looks right", so it can miss exactly what
this model missed. A different vendor's model does not inherit those priors. That is the only
reason the tier order is binding rather than a preference: tier 1 is not "the better tool",
it is *the different eyes*.

Read those two paragraphs before writing a Step-4b prompt. Every prompt this skill has
produced was built from the § Dispatch contract below, so an error there reproduces perfectly,
round after round, in every OBPI — and the one that sat there for ten weeks inverted the
purpose above into its opposite.

**What Step 4b is FOR (read this before writing any prompt).**

**Step 4b is an ACCEPTANCE REVIEW.** The decision it supports is: *"Does this
implementation correctly fulfill the bounded requirements?"* Therefore its purpose
must be independent corroboration.

Refutation remains essential, but as a METHOD:

1. Re-derive the claim independently.

2. Try hard to falsify it within the declared scope.

3. Demonstrate the intended behavior positively.

4. Corroborate only if both directions hold.

> **Purpose:** independently corroborate correctness.
> **Method:** adversarially attempt to falsify it.
> **Boundary:** the brief, requirements, and threat model.
> **Pass condition:** positive behavior demonstrated and independent closure of findings
> against the agreed requirements and their required proof, per § The pass condition above.

That gives the operator EVIDENCE FOR AN ATTESTATION DECISION, instead of an
unbounded argument.

**THE REVIEWER REPLAYS IN A DISPOSABLE WRITABLE CHECKOUT (operator instruction 2026-09-10,
GHI #961).** Step 4b judges executed proof, and judging it by reading is weaker than judging it
by running it. `codex-companion.mjs:414` still pins `sandbox: "read-only"` on the
`adversarial-review` path, so that subcommand can never replay a mutation. **It is no longer the
Step-4b dispatch.** The `task` path honours `--write` (`codex-companion.mjs:491`,
`sandbox: request.write ? "workspace-write" : "read-only"`), takes `--cwd`, and accepts
`--prompt-file`.

Point that writable sandbox at a THROWAWAY COPY of the reviewed source, never at the operator's
tree. Build it first:

```bash
uv run gz obpi adversary-workspace <OBPI-ID>
```

It copies tracked content at `HEAD` plus uncommitted modifications, prints a `source_digest` over
the materialized file set, and prints the dispatch below already pointed at the checkout. Measured
2026-09-10 under `task --write --cwd <checkout>`: `tempfile.mkdtemp()` returns a real path, a write
inside the checkout succeeds, and a write to the active repository is **refused**
(`operation not permitted`). The active checkout is protected by the sandbox boundary itself, not
by asking the reviewer nicely.

Dispatch, ARB-wrapped as always:

```bash
uv run gz arb step --name codexadversary --max-output-chars -1 -- \
  node "$HOME/.claude/plugins/cache/openai-codex/codex/<ver>/scripts/codex-companion.mjs" \
  task --write --cwd <checkout> --prompt-file <prompt.md>
```

Tier 1 is unaffected: the argv is still `node .../codex-companion.mjs`, `receipt_proves_cross_vendor`
walks past `node`, and `data/mandated_tier1_dispatch.json` declares this surface alongside the
read-only one. The plugin remains the only tier-1 dispatch surface — this changes which of its
subcommands Step 4b uses, never the vendor boundary, and `codex exec` stays FORBIDDEN.

**Ask for the replay, and take nothing on faith.** Instruct the reviewer to run the baseline, apply
the recorded substitution, observe the named test fail on its OWN ASSERTION, restore the source
byte-identically, and re-run. It reports those observations in a `replay` array on its
`gzkit.acceptance.review.v1` object — obligation, proof id, workspace digest, selectors, mutation
label, three runs, and the source digest before and after. Ingestion REFUSES a claim the record
does not support: a baseline that was not green, a failure whose class is `error` rather than
`assertion`, a selector that executed zero tests, a record with no substitution, a source not
restored, or a digest naming some other tree. Absence of the block claims nothing and is left
alone — silence is honest, only a claim is checked. Delete the checkout when the round ends.

**This constrains a technique. It does not lower the pass condition.** GHI #643's fabricated
evidence was entirely plausible ON READING — that is what made it fabricable, and running the
Demo is what exposed it. Demonstration is the point of this gate. An agent that softens
*"positive behavior demonstrated"* because some technique is unavailable has confused the
reviewer's tooling with the gate's objective, which is the same error the June-24 framing made
in the other direction.

**The June-24 framing confused the reviewer's TECHNIQUE with its OBJECTIVE.**
*"Your job is to refute"* creates a motivated critic that can continually expand
the attacker, or move outside the requirements, until something fails. It also
produces the exact measured pathology: on OBPI-0.35.0-04, six rounds tested
refusal paths while none demonstrated that the feature still worked.

Step 4a is authored by the same agent that may have fabricated it, so Step 4b does
not take 4a's word for anything: it RE-DERIVES the completion claim from the REQs
and the repository and must paste observed command output for every check. The
operator attests holding **both** outcomes.

**Confirmation must be EARNED, not inferred from silence.** "I looked and found nothing" is
not a confirmation. A corroborating round demonstrates, with pasted output, that each guard
FIRES when it should AND does NOT fire when it should not — a legitimate operation still
succeeds. A guard never made to fire is a guard not confirmed; a refusal path never exercised
with a legitimate input is a false-positive risk not ruled out. Ask for both
directions explicitly: six rounds on OBPI-0.35.0-04 tested refusals and not one asked whether the
feature still worked.

**The adversary must satisfy three properties AND be selected by the binding tier order.** The properties — *independent context + does-not-trust-4a framing (re-derive from the REQs and the repo; adversarial probing as method) + evidence-backed (pastes real command output)* — are necessary but NOT sufficient: "independent context" does not make the vendor interchangeable. A Claude validating Claude satisfies all three properties and still shares this agent's failure modes, which is the exact blind spot Step 4b exists to break. Vendor order is therefore **binding, not advisory** — you do not get to pick a lower tier because it is the frictionless path.

**Tier order (binding). You MUST attempt tier 1 and may only drop a tier after establishing its precondition:**

1. **Codex** — REQUIRED FIRST: a different-vendor model shares none of this agent's blind spots. **Dispatch through the Codex plugin's writable `task` path, exactly as shown in § THE REVIEWER REPLAYS IN A DISPOSABLE WRITABLE CHECKOUT above** — it is the only plugin subcommand that can replay a mutation, and the only one that returns the reviewer's output verbatim, which the acceptance importer requires. `/codex:adversarial-review` remains a mandated tier-1 surface (`data/mandated_tier1_dispatch.json`) and its receipt proves the tier, but it is read-only and renders a summary, so a review object authored through it does not survive transport (observed 2026-09-10: import refused, `exit 3`). Do not use it for Step 4b. Run the dispatch in the **foreground** (a single blocking call — no polling; use `timeout: 600000`, reviews run ~7–8 min); if you detach it, read progress via the **`/codex:status <task-id>`** slash command. Do NOT hand-roll a `node codex-companion.mjs status` poll loop — that is the low-level plumbing, not the published surface (operator-flagged, 2026-07-15). The general `codex:rescue` / `codex:codex-rescue` agent is an acceptable fallback dispatch path when you need a bespoke confirmation prompt. Before dropping to tier 2, you MUST check availability — run `codex:setup` (or the companion `setup --json`) and read `ready`. If `ready: true`, Codex is available and tier 2/3 are **forbidden**.

2. **Independent Claude subagent** — permitted ONLY when the tier-1 availability check returned `ready: false` (Codex not installed / not authenticated / unreachable). Dispatch a fresh `general-purpose` agent (separate context) with the same confirmation-framed prompt. Using this tier without a checked, genuine tier-1 unavailability is a Step 4b bypass of the same class as skipping 4b entirely (GHI #678).

3. **Human-as-adversary** — degraded floor: if neither fires, say so explicitly ("adversarial validation ran in degraded human-only mode") so the operator knows the independent check did not run.

> **⚠ Clear prop before firing up the tier-1 Codex adversary.** The Codex runtime (`openai/codex-plugin-cc`) routes every rescue through a long-lived, shared broker process that can silently wedge — a stale/hung broker is reused without a health check, and the adversarial job then **hangs indefinitely with no output** (the job log reaches "Turn started" and never completes; upstream `openai/codex-plugin-cc` #509). Before dispatching, *clear prop*: if a prior run may have left one wedged, reset it — `rm -f ~/.claude/plugins/data/codex-openai-codex/state/<workspace-slug>/broker.json` and kill any stray `app-server-broker` / `codex app-server` processes — then run `codex:setup` and confirm `ready: true`. **A wedged broker is NOT a genuine tier-1 unavailability.** `codex:setup` checks only the binary + auth, so it reports `ready: true` even when the broker is hung; the true signature is `ready: true` but a `task` that emits nothing within ~30s. In that case clear prop and retry tier 1 — do **not** record it as `ready: false` and drop to tier 2, which would be a tier-order bypass (GHI #678).

**Record the tier and why.** Preserve the actual reviewer execution and observed
fallback reason in the acceptance record. Completion carries its derived tier
and provenance into the `adversarial_validation` event (GHI #676, #985).
A caller declaration cannot promote a same-vendor execution to tier 1 or replace
missing review evidence. "The Claude subagent was convenient" is not a fallback
reason. `gz obpi complete` takes no tier, reviewer or fallback-reason flag
(GHI #1163); the acceptance record is the only source.

**Acceptance transport preserves that tier order (GHI #985).** The acceptance
importer derives tier from actual execution; do not put a caller-authored `tier`
in the review JSON. A native Claude adversarial fallback includes
`fallback_reason` naming the observed tier-1 unavailability. Native Claude spec
and quality execution needs no fallback reason. If the operator explicitly acts
as the degraded human adversary after reviewing current proof and findings,
record their exact ruling with `gz obpi acceptance {OBPI-SLUG} human-review
--attestor g0 --ruling '<verbatim judgment>'`. This records the current proof
approval and finding closure as tier 3, without inventing an agent receipt.
Never infer that ruling from permission to implement or repair, and retain the
separate completion attestation. Completion records the resulting derived tier.

> ### 🛑 THE PLUGIN IS THE ONLY TIER-1 DISPATCH SURFACE (operator directive, 2026-08-25)
>
> **`codex exec` is FORBIDDEN as a tier-1 invocation.** Dispatch through OpenAI's Codex
> plugin for Claude Code — its runtime `codex-companion.mjs`, on the `task --write` path
> shown above for Step 4b — and nothing else. Wrapping the raw binary in
> `gz arb step` is NOT an acceptable substitute, and this section used to show exactly
> that, which is how the violation happened.
>
> **Measured cost of one hand-rolled run (2026-08-25, OBPI-0.35.0-02):** ~15 minutes
> wedged at 0.07s CPU because `codex exec` blocked on an unredirected stdin — a state
> `codex:setup` reports as `ready: true`; then a 500KB undifferentiated blob that had to
> be `sed`-sliced to find the verdict; then a re-run **refused outright** by an upstream
> cyber filter (*"This content was flagged for possible cybersecurity risk"*) because a
> hand-written refute prompt named Unicode bypass techniques. The plugin path, launched
> against the identical work, streamed structured findings with severity and confidence
> and surfaced a **high**-severity defect the hand-rolled run had missed entirely.
>
> The failure was not the agent forgetting the rule — the rule was stated here and then
> contradicted three paragraphs later by a worked example using the forbidden form. An
> agent following the example is following this skill. **Never reintroduce a `codex exec`
> incantation to this file, even as an illustration.**

**Prove the tier; nothing declares it (GHI #765, #780, #985).** The tier is derived
from the argv the reviewer run executed, never from a flag or a name. Wrap the PLUGIN
invocation in ARB, then import that run:

```bash
uv run gz arb step --name codexadversary --max-output-chars -1 -- \
  node "$HOME/.claude/plugins/cache/openai-codex/codex/<ver>/scripts/codex-companion.mjs" \
  task --write --cwd <checkout> --prompt-file <prompt.md>
# → arb step name=codexadversary exit_status=0 receipt=.../arb-step-codexadversary-<hash>.json
uv run gz obpi acceptance <OBPI> review --receipt arb-step-codexadversary-<hash>
```

The executed output must contain the structured acceptance judgment described
below. The receipt's successful exit alone cannot establish acceptance.

The importer **resolves** the receipt: it must record `exit_status: 0`, and its
`step.command` must invoke an agent. The scan walks past a bounded set of runtime
wrappers (`node`, `npx`, `python`, `uv`, ...) to the binary they front and **stops at
the first non-wrapper**, so the mandated plugin dispatch `node .../codex-companion.mjs`
proves tier 1 while a vendor named only in the adversary's PROMPT does not (GHI #884).

If the run cannot be ARB-wrapped there is no receipt to import, and that is a
**tier-2 outcome**: run the native Claude fallback under ARB with `fallback_reason`
naming the observed unavailability. Reaching for `codex exec` to make a receipt appear
is the substitution this gate exists to catch.

**Dispatch contract.** Give the adversary the completion CLAIM (the brief's REQs
and what the agent says it built), the actual Step-4a packet path, source/test
paths, relevant raw execution artifacts, and prior findings with dispositions.
Identify the reviewed revision and dirty-tree artifact identities. Give the gzkit
tools as its framework — `gz obpi present-evidence <OBPI>`, `gz covers <OBPI> --json`,
the scoped tests, the brief's Demo, `git status --short` and `git diff` — subject to
the documented execution limits above. Instruct it to **INDEPENDENTLY CONFIRM THE
IMPLEMENTATION IS CORRECT**, probing the bounded requirements in both directions.
Judge whether each cited method supports its acceptance claim, not just whether
its output reproduces. For each finding, name the violated requirement or
required-proof claim, the counterexample or concrete evidence gap, and the
relevant verification. Review allegations also need source/observed support;
do not adopt an explanation solely because another reviewer wrote it.

Require `CORROBORATED` | `CORROBORATED-WITH-CAVEATS` | `NOT-CORROBORATED`, the
separate verdict token, output for checks it executed, artifact references for
records it inspected, an explicit statement of what it could NOT confirm, and
a "Weakest point" section. An auxiliary audit is not automatically a new
deliverable. Determine a finding's relevance by the acceptance claim it affects,
not the document or review round where it originated.

Also supply the current acceptance status JSON and require exactly one
`gzkit.acceptance.review.v1` object in the actual reviewer output, rendered with
`gzkit.acceptance_context.acceptance_review_frame("adversarial", <status json>)`:
the Stage-2 frame, carrying the schema, identities and import rules (GHI #1095).
Explicitly list `accepted_proof_ids` for the proof the reviewer approves; never
infer this set from a global verdict. The `accepted`/`refuted` verdict is retained
as review history. Mapped findings and explicit proof approvals govern readiness,
so an auxiliary observation cannot revoke an approved requirement through its
wording. Mapped findings retain stable IDs. A verified repair emits a closure
containing `finding_id`, `obligation_id`, and the current `proof_id`. Record the review through `gz obpi acceptance ... review --receipt ...`, including
truthful refutations, so the next round receives the same outstanding obligations.

**Two transport facts that decide what actually reaches it (measured 2026-09-04, re-measured 2026-09-10 on the writable path, GHI #961).** The suite runs under the venv interpreter, never `uv run` — uv cannot initialize its cache in the sandbox. Inside the disposable checkout, run it as `PYTHONPATH=<checkout>/src <repo>/.venv/bin/python -m unittest <selector>`; the editable install points at the ORIGINAL `src`, so without that `PYTHONPATH` the reviewer would mutate the copy and import the original — a replay that proves nothing. `gz obpi adversary-workspace` prints the exact invocation. Second: the `task` path DOES take `--prompt-file` and stdin, so the positional-only limitation belongs to `adversarial-review` alone and no longer applies; still name large artifacts BY PATH and let the reviewer open them. And where `renderReviewResult` collapses a review to a rendered summary, `renderTaskResult` (`lib/render.mjs:315`) emits the reviewer's `rawOutput` **verbatim** — which is why the review object now reaches the ARB receipt the importer reads. Observed 2026-09-10: a complete, correct review object authored through `adversarial-review` was lost in transport and the import refused it (`exit 3`).

> **`not-refuted` IS the corroborated state — it is phrased passively, not missing.** Operator
> ruling 2026-09-04, verbatim: *"NOT-REFUTED is arguably a passive way of saying CORROBORATED"*.
> A model that attacked the implementation and could not break it has corroborated it, so
> `CORROBORATED` records as `not-refuted` and that is a faithful record, NOT a rounding. An
> earlier revision of this note claimed the enum "has no corroboration state" and that the
> mapping was a documented lie-by-rounding; both were wrong (GHI #954, narrowed by its own
> author). No change to `gz obpi complete` is warranted.
>
> Still require BOTH lines from the adversary — the `CORROBORATED | CORROBORATED-WITH-CAVEATS |
> NOT-CORROBORATED` line and the enum word — because the distinction that matters is
> *attacked hard and demonstrated working* versus *looked and found nothing*, and that
> distinction lives in the PROMPT's demand for positive demonstration, never in the verdict
> word. Two rounds can both land on `not-refuted` and mean entirely different things; the
> pasted evidence is what tells them apart. Record the outcome by importing the review (`gz obpi acceptance <OBPI> review --receipt <run-id>`); `gz obpi complete` writes the `adversarial_validation` event from the accepted review — the ledger event is the durable record, not a dispatch marker.

**Bound the claim BEFORE the first round, or the gate cannot converge (operator ruling 2026-09-03).** An adversary instructed to REFUTE will escalate the attacker one notch each round, so an ABSOLUTE claim ("no X can occur without Y") is unrefutable-in-bounded-time by construction. For any OBPI whose subject is a trust chain, provenance, or a tamper-evidence property, the brief MUST carry a `## Threat Model` section BEFORE Step 4b is first dispatched, naming what an attacker may do and what is an accepted residual — and the dispatch prompt MUST state that boundary and forbid the adversary from reporting an out-of-scope attack as a finding. Measured on OBPI-0.35.0-04: five rounds, 53 minutes of adversary compute across a 12.5-hour wall clock (7%); the rest was fix cycles. Rounds 4 and 5 spent ~9 hours hardening attacks whose reproduction required appending arbitrary rows to `.gzkit/ledger.jsonl` — strictly inside a residual the operator had already accepted for `.gzkit/ownership/`, the same directory and the same access. `docs/governance/trust-doctrine.md` covers AGENT trust-chain poisoning and declares no filesystem threat model, so nothing bounded the adversary and the agent never asked whether the attacker was in scope.

Wait for the human to respond "Accepted", "Completed", "attest completed", or equivalent. Do NOT proceed until attestation is received.

Do NOT mark ceremony task `completed` until attestation is received.

**When attestation arrives, immediately invoke `gz obpi complete` (Stage 5 Step 2) with the operator's phrase in `--attestation-text`.** The operator's short phrase is the attestation; the pipeline must not pause to ask for longer text and must not print runbook-style instructions for the operator to execute. Enrich the attestation text per `AGENTS.md` § Attestation (em-dash + concrete session evidence + receipt IDs) before passing it through.

**Human rejects:** Record feedback, return to Stage 2 with corrections.

**MANDATORY TRANSITION → Stage 5.** Once attestation is received, proceed to Stage 5 immediately. Do not summarize. Do not wait.

## Controls carried into Stage 4 from other sections

| `narrator` | Composes the Stage 4 evidence packet in operator-value framing — value narrative, key proof, evidence table, REQ coverage rendered for the human's attestation decision | Stage 4 (Present Evidence) — see § Stage 4 |

```
THE PIPELINE IS NOT COMPLETE UNTIL STAGE 5 FINISHES.
```

Every stage flows into the next. No "stop and summarize" between stages. No pause except the Stage 4 human attestation in Normal mode — and that pause comes only **after** Step 4b (the independent adversary) has run and its verdict is on the table. Soliciting attestation with Step 4b skipped is not a valid pause; it is a gate bypass. If you have not reached the end of Stage 5, you are not done — and violating the spirit of this rule is violating the rule. One other stop is legitimate: when Stage 4's round bound is reached or a round repeats the prior round's root, record `gz obpi block` and put the decision to the operator (§ Stage 4 — The review window, the bound, and the exit). That is the pipeline working, not a premature summary.

These thoughts mean STOP — you are about to break the pipeline:

| "The hook blocked me, I'll work around it" | Hook blocks are signals. Diagnose the cause. NEVER create marker files manually to bypass. |

| "The operator said `attest completed` — maybe they want me to explain what to do next" | No. `attest completed` IS the attestation. Run `gz obpi complete` immediately with that phrase (enriched per § Attestation) in `--attestation-text`. Do not produce runbook-style instructions for the operator to execute. |

| "My Step 4a evidence is green — tests pass, REQs covered — so I can present it and await attestation" | STOP. Green-on-your-own-evidence is the EXACT state Step 4b exists to distrust. You authored that evidence; you are the GHI #643 fabrication surface. You may NOT solicit attestation until applicable independent approval and closure have been imported for the current proof claims. Confidence from the authoring agent is worth zero at this gate. |

| "Step 4b is probably overkill for this small/authoring-only/obviously-correct OBPI" | Step 4b is expected on every lane, size and kind, and `gz obpi complete` refuses on every lane until the acceptance record holds a current independent adversarial review (`acceptance_store.completion_review`, GHI #985). "Obviously correct" is the precise feeling that precedes a hollow-test or fabricated-evidence skip. Dispatch the adversary. You are not the exception. |

| "I'll present Step 4a now and run the adversary after the operator responds / in the next turn" | Sequence violation. The adversary runs BEFORE attestation, not after — the operator attests holding the adversary's verdict. Presenting 4a as the terminal step of the turn, with 4b deferred, is the skip this gate forbids. Dispatch any missing required review before soliciting attestation; retain already applicable imported review. |

| "An independent Claude subagent is fine for 4b — I don't need Codex" | Tier-order bypass (GHI #678). A Claude validating Claude shares this agent's blind spots — the exact failure Step 4b exists to break. Codex (tier 1) is REQUIRED first; tier 2 is permitted ONLY after a checked `ready: false`. Run `codex:setup`; if `ready: true`, the Claude subagent is forbidden. "It was convenient" is not a fallback reason. |

| "The adversary is there to find problems, so a round that confirms the feature works is a soft round" | Inverted. A second model CONFIRMING the first model's implementation is correct is the entire point of Step 4b; probing is how that confirmation is earned. A round that only lists what it broke, and never demonstrates the feature doing its job, has not done the job. |

| "The adversary refuted again, so I'll fix these findings and re-run" | Check its `Weakest point` against the previous round FIRST. If it names the same root, another fix cycle surfaces it one layer deeper — that is three rounds and ~9 hours in the measured case. Stop and put the design to the operator. |

| "I'll tell the adversary to REFUTE the claim — that's what adversarial means" | It is not, and this exact wording cost OBPI-0.35.0-04 six rounds. A model told "your job is to REFUTE this, not to confirm it" will escalate until something falls, and its best available outcome is "I could not refute it" — absence of evidence, never confirmation. Prompt for independent confirmation, with probing as the method. |

| "This is a security property, so the claim should be absolute" | An absolute claim cannot be refuted in bounded time: the adversary escalates the attacker until something falls. Declare the threat model in the brief FIRST, state it in the prompt, and forbid out-of-scope findings — otherwise the gate never converges. |

| "The adversary found something, so the OBPI cannot pass" | Apply the September 5 independent-closure rule below: every finding against the agreed requirements or their required proof needs a disposition and independent closure. Severity alone does not clear it. Track independent discoveries without silently making them acceptance prerequisites; never dismiss a relevant finding merely because it arose in an auxiliary audit. |

| "The round refuted, but I fixed everything it found — I'll complete and explain the fixes in `--adversary-resolution`" | **Refused, and a resolution string does not change that (GHI #960).** *"refuted is an outcome, but it is an input into if(4a && 4b) pass; else: loop"* (operator, 2026-09-04). Execute proof for the repaired obligation and import explicit independent closure. The current acceptance records determine readiness; preserve the original refutation as history. |

| "The block says refuted can't complete, so I'll pass `not-refuted` since the findings are fixed anyway" | A caller-supplied word cannot close a finding. Import the independent review's actual executed output with its original finding IDs and current proof IDs. `gz obpi acceptance ... status --stage stage4` derives readiness; historical verdicts remain unchanged. |

The pipeline executes 5 stages sequentially. **Stage 4 behavior depends on execution mode** — all other stages are autonomous.

```text
┌──────────────────────────────────────────────────────────────┐
│  Stage 1: LOAD CONTEXT       (autonomous)                    │
│  Stage 2: IMPLEMENT          (autonomous)                    │
│  ├─ DO NOT STOP HERE. Proceed to Stage 3.                    │
│  Stage 3: VERIFY             (autonomous)                    │
│  ├─ DO NOT STOP HERE. Proceed to Stage 4.                    │
│  Stage 4: PRESENT EVIDENCE   (human gate — universal)        │
│  ├─ WAIT for human attestation, then Stage 5.                │
│  Stage 5: SYNC AND ACCOUNT   (autonomous)                   │
│  └─ Pipeline complete. NOW you may report status.            │
└──────────────────────────────────────────────────────────────┘

Stage 4 = HUMAN GATE (wait for attestation) — universal per ADR-0.0.36
```

| Human rejects attestation | Record feedback, return to Stage 2 with corrections |

**Lock bracket:** Lock is claimed at Stage 1 and surrendered by `gz obpi complete` at Stage 5, or by an abort surrender.

On an abort the lock is surrendered with a recorded category (GHI #1167):

```bash
uv run gz obpi lock release {OBPI-SLUG} --abandon <category>:<reason>
```

A release without `--abandon` exits 3 and leaves the lock in place
(`.gzkit/rules/token-block-discipline.md` § Sub-Invariant 5). `--force` waives
the ownership check only. A session handoff is not an exchange record and
discharges nothing. The categories are a closed enum, listed in
`docs/user/manpages/obpi-lock-release.md`; if none describes the abort, do not
pick one that misdescribes it. Leave the lock held, name it in the handoff and
report it to the operator; a lock past its TTL is reaped with its own register
entry.

**Handoff creation:** On any abort, after the surrender, run `/gz-session-handoff` to preserve context for the next session.

**When the next legitimate action is a human's, say so in the ledger and stop.**

```bash
uv run gz obpi block {OBPI-SLUG} \
  --reason "<what cannot proceed without a human>" \
  --next-action "<the concrete decision the operator owes>"
```

While the block stands, `gz obpi pipeline` refuses to launch against the OBPI
(exit 3) and `gz obpi precomplete` reports it instead of `READY`. The operator
clears it with their own words:

```bash
uv run gz obpi unblock {OBPI-SLUG} --ruling "<decision>" --operator "<who>"
```

**No attestor is required to record a block.** Requiring a human to authorize
the statement *"a human is needed"* would reproduce the deadlock it exists to
break. The ruling that clears it is the operator's; the observation that one is
needed is the agent's, and recording it is the honest act.

Use one writer per governed checkout. Read-only investigation may run independently.
Only the operator initiates OBPI work; separate sessions do not grant initiation.
Capture the contract and input components before review and verify applicability
before consuming it. Sequence shared acceptance/schema writes outside review windows.
If another run changes the subject, identify affected evidence before continuing.
Never stash, pop, reset, revert, or sync another active run's work to clean the tree.

All OBPIs require per-OBPI human attestation (universal per ADR-0.0.36).

If a pipeline hook blocks a write, that means the pipeline is not active or evidence is missing. The correct response is to diagnose the cause — NOT to manually create marker files or ledger entries to bypass the hook. Manually creating files to bypass hooks defeats the entire enforcement mechanism.
