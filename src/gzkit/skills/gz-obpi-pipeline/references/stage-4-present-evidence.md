<!-- Stage 4 procedure, served by the runtime at stage entry (OBPI-0.35.0-17; cut over in OBPI-0.35.0-20). Rendered from data/obpi_pipeline_control_inventory.json by gzkit.governance.pipeline_procedure_render: the stage's own section first, then every block from another section holding a control whose applies_at names this stage. Every control is verbatim from the attested baseline of .gzkit/skills/gz-obpi-pipeline/SKILL.md (072317673, body sha256 fe97fe3139282b0ceec5b11866e97efad11761d8e35a5e4977c84f3d6b388367); passages the inventory classes as rationale are in docs/governance/obpi-pipeline-control-rationale.md under the control they explain, and a control that applies elsewhere is left out of its block here. Reworded, each with its reason in the inventory: I-028, S4-002, S4-032, S4-033, S4-045. Do not edit by hand: tests/governance/test_pipeline_procedure_render.py holds this file to the render. -->

# Stage 4: Present Evidence — served procedure

### Stage 4: Present Evidence

Stage 4 is three steps and one bounded loop:

```
4a author the packet → 4a-v replay the packet → 4b independent review → pass condition met?
   ├─ yes → present 4a + 4a-v + 4b together → await attestation
   └─ no  → ONE rework round (§ The review window) → re-enter at 4a
```

You do not get to skip 4b because your own evidence looks green. You are not the exception. The sequence admits
no size, lane, or kind exception. An earlier turn or equivalent successful execution
does not invalidate review by itself; the acceptance consumer decides applicability.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-003

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

**Step 4b closes on independent confirmation of the corrected state (operator ruling 2026-09-05).**

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-009

This ruling supersedes that severity-only stopping condition: do not solicit completion attestation while any finding against the agreed OBPI requirements remains unresolved, or while a claimed fix has only the implementing agent's confirmation. A non-refuting verdict on the earlier state does not independently verify later repairs, including repairs to evidence or missing witnesses.

**Readiness is derived; historical verdicts are immutable (GHI #985).** Run:

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-012

```bash
uv run gz obpi acceptance {OBPI-SLUG} status --stage stage4 --json
```

Readiness requires current valid proof, accepted spec/quality/adversarial reviews
for every obligation, and independently verified closure of all mapped findings.
The ledger-backed single-driver declaration retains its documented Stage-2
spec/quality exception; proof and Step-4b closure remain mandatory.
An unchanged obligation cannot lose its finding because an auxiliary audit was
removed. An edit confined to recognized history sections does not invalidate executable proof.
preserve
existing historical words, but never edit a Markdown verdict to change readiness.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-014, § S4-016

**Clean means no unresolved in-scope findings, not absence of all limitations.** Accepted residual risks and future ADR-wide obligations remain disclosed separately; they are not failed present-tense OBPI requirements. Filing a GHI alone does not discharge an unmet requirement. A newly proposed boundary change requires operator ruling and independent revalidation; the implementing agent cannot move a finding outside scope to clear the gate. Before soliciting attestation, the retained independent review set must supply applicable approval and explicit closure on the corrected proof claims. Raw verdict wording alone neither grants approval nor reopens a closed obligation. Scope-boundary disclosures may remain, provided the adversary distinguishes them from unresolved findings.

Do not redispatch merely to remove harmless caveat wording after independent
closure is established. If a follow-up exposes the same root cause again, use
the design-escalation rule below. Whether an oracle or control fulfills
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
history sections and its Change Log do not move it.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-024

**A round reviews a frozen subject.** Before dispatching 4b — first round or follow-up:

1. Finish every edit. Nothing is left to tidy afterwards.
2. Run `acceptance prove` for every obligation (a repair stales them all; see above).
3. Refresh the packet (`gz obpi present-evidence`) and replay it (Step 4a-v).
4. Record `git status --short` and the reviewed revision in the dispatch prompt.
5. Dispatch. From dispatch until the review is imported, edit nothing under the
   audited population: not the source, not a test, not a data file, not a rule, and
   do not `gz git-sync` in other work. An edit inside the window spends the round.

**When a round returns findings, run ONE rework round.** Collect all of them first.
Rework them as one batch (§ Repair the whole obligation, below). Then repeat steps 1–5
once, dispatching the focused buy-back described below — never one dispatch per
finding, and never a fresh unrestricted review.

After the rework, obtain the buy-back: a focused independent Step 4b follow-up, limited to the findings. Supply the prior findings, the changed artifacts and evidence, and the unchanged scope/threat-model boundary. The adversary must verify each claimed closure and check the affected requirements for regressions; it must not restart an unrestricted search for stronger guarantees. Record the actual new verdict and receipt, with each prior finding's disposition and demonstrated evidence. Preserve earlier rounds as history. Never request a preferred verdict or relabel `CORROBORATED-WITH-CAVEATS` as clean yourself.

**Repair the whole obligation before redispatch (GHI #984).** Carry the accepted
finding back through the existing implementation and verification stages. Trace
the relevant producers, consumers, fresh/retry paths, early returns and cleanup;
use the states needed by the requirement, not an unlimited neighboring audit.
Recheck affected
controls when a repair adds another guard that could mask them. Preserve the
complete finding and the execution record beside its closure, rather than
replacing it with a new explanatory claim.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-034

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

Then present the open findings, what each round changed, and one recommendation.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-044

**When a round repeats the prior round's ROOT, stop dispatching and escalate the DESIGN (operator ruling 2026-09-03).** Compare each round's `Weakest point` against the last. If it names the same root cause at a different surface, another rework round will surface it again one layer deeper: stop, and put the design decision to the operator (§ Behavior Rules — Always #9).

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-045

#### Normal Mode — HUMAN GATE

**Trigger:** "Present OBPI Acceptance Ceremony" task becomes next pending. Mark `in_progress`.

**Narrator dispatch** (per § Persona Dispatch). Dispatch a `narrator` subagent with the populated template fields (Value Narrative input, REQ coverage table from Stage 3, ARB receipts from quality gates) and instruct it to render the final attestation surface per the template below. do not improvise one through `SubagentDispatchRecord`, which accepts Stage-2 roles only.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-047, § S4-049

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
review records. Cite those proof IDs in the REQ table.
Preserve their executed payloads rather than reconstructing another evidence
classification.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-057

Run `gz obpi present-evidence {OBPI-SLUG} --json` to generate Step-4a review input.
Give that packet to the adversary. Do not confuse successful packet generation
with permission to solicit attestation. After importing independent approval and
finding closure, refresh the packet; final validation requires both proof and
review blockers to clear.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-060

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

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-082

```bash
uv run gz obpi verify-packet .gzkit/evidence/<OBPI-ID>.stage4a.md
```

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-083

Exit 0 = VERIFIED. Exit 3 = a pasted line did not reproduce; repair the packet and
re-run. Present the verdict alongside 4a and 4b — the operator attests against all
three.

**The authoring contract.** A `$` prompt is a claim — *"I ran this and this came
back"* — and every one of them is re-executed:

- **Paste only what the command produced.** The comparison is containment, so
  abridging and re-indenting are fine; a line the command never wrote is a blocker.

- **Elide what cannot reproduce.** A timestamp or a freshly minted receipt id is
  written `...`, never pasted. Pasting an unreproducible line is what fails.

- **Cite proof commands as transcripts.** A command offered as proof of a REQ goes
  under a `$` prompt with its output.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-089

- **For a silent assert-shaped probe, show the status:** `$ <cmd>; echo "exit $?"`.
**Then paste the
  line it emits.** Omitting it is a blocker, and
  `...` does not satisfy it: elision is for output that cannot reproduce, never for output
  you would rather not show.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-090, § S4-091

- **A fenced shell block with no `$` claims no output** and is never re-run — that is
  what the `arb:` incantation blocks are, and their result is carried by the receipt
  rows. They are listed back as citations so the operator sees what was *not*
  witnessed.

- **A failing command cannot be presented as success.** A non-zero exit is a blocker
  outright, To
  show a RED run, use the status form above **and paste the status it prints**;

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-094, § S4-095

- **Do not pipe a verifier into a filter.** The shell reports the filter's status, so a
  failing suite would replay green. Use `set -o pipefail` or redirect to a file.

#### Step 4b — Independent Adversarial Validation (GHI #643) — MANDATORY, NON-SKIPPABLE

**WHY THIS GATE EXISTS AT ALL — and why the second model is CODEX specifically.**

Read those two paragraphs before writing a Step-4b prompt.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-098

**What Step 4b is FOR (read this before writing any prompt).**

**Step 4b is an ACCEPTANCE REVIEW.** The decision it supports is: *"Does this
implementation correctly fulfill the bounded requirements?"* Therefore its purpose
must be independent corroboration.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-097

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

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-104

**THE REVIEWER REPLAYS IN A DISPOSABLE WRITABLE CHECKOUT (operator instruction 2026-09-10,
GHI #961).** **It is no longer the
Step-4b dispatch.**

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-105, § S4-106

Point that writable sandbox at a THROWAWAY COPY of the reviewed source, never at the operator's
tree. Build it first:

```bash
uv run gz obpi adversary-workspace <OBPI-ID>
```

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-108

Dispatch, ARB-wrapped as always:

```bash
uv run gz arb step --name codexadversary --max-output-chars -1 -- \
  node "$HOME/.claude/plugins/cache/openai-codex/codex/<ver>/scripts/codex-companion.mjs" \
  task --write --cwd <checkout> --prompt-file <prompt.md>
```

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-110

The plugin remains the only tier-1 dispatch surface — this changes which of its
subcommands Step 4b uses, never the vendor boundary, and `codex exec` stays FORBIDDEN.

**Ask for the replay, and take nothing on faith.** Instruct the reviewer to run the baseline, apply
the recorded substitution, observe the named test fail on its OWN ASSERTION, restore the source
byte-identically, and re-run. It reports those observations in a `replay` array on its
`gzkit.acceptance.review.v1` object — obligation, proof id, workspace digest, selectors, mutation
label, three runs, and the source digest before and after. Delete the checkout when the round ends.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-113

**This constrains a technique. It does not lower the pass condition.**

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-115

Step 4a is authored by the same agent that may have fabricated it, so Step 4b does
not take 4a's word for anything: it RE-DERIVES the completion claim from the REQs
and the repository and must paste observed command output for every check. The
operator attests holding **both** outcomes.

**Confirmation must be EARNED, not inferred from silence.** "I looked and found nothing" is
not a confirmation. A corroborating round demonstrates, with pasted output, that each guard
FIRES when it should AND does NOT fire when it should not — a legitimate operation still
succeeds. Ask for both
directions explicitly:

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-119, § S4-120

**The adversary must satisfy three properties AND be selected by the binding tier order.** Vendor order is therefore **binding, not advisory** — you do not get to pick a lower tier because it is the frictionless path.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-121

**Tier order (binding). You MUST attempt tier 1 and may only drop a tier after establishing its precondition:**

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-123

1. **Codex** — REQUIRED FIRST: **Dispatch through the Codex plugin's writable `task` path, exactly as shown in § THE REVIEWER REPLAYS IN A DISPOSABLE WRITABLE CHECKOUT above** Do not use it for Step 4b. Run the dispatch in the **foreground** (a single blocking call — no polling; use `timeout: 600000`, if you detach it, read progress via the **`/codex:status <task-id>`** slash command. Do NOT hand-roll a `node codex-companion.mjs status` poll loop The general `codex:rescue` / `codex:codex-rescue` agent is an acceptable fallback dispatch path when you need a bespoke confirmation prompt. Before dropping to tier 2, you MUST check availability — run `codex:setup` (or the companion `setup --json`) and read `ready`. If `ready: true`, Codex is available and tier 2/3 are **forbidden**.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-124, § S4-125, § S4-127, § S4-129

2. **Independent Claude subagent** — permitted ONLY when the tier-1 availability check returned `ready: false` (Codex not installed / not authenticated / unreachable). Dispatch a fresh `general-purpose` agent (separate context) with the same confirmation-framed prompt. Using this tier without a checked, genuine tier-1 unavailability is a Step 4b bypass of the same class as skipping 4b entirely (GHI #678).
3. **Human-as-adversary** — degraded floor: if neither fires, say so explicitly ("adversarial validation ran in degraded human-only mode") so the operator knows the independent check did not run.

> **⚠ Clear prop before firing up the tier-1 Codex adversary.** Before dispatching, *clear prop*: if a prior run may have left one wedged, reset it — `rm -f ~/.claude/plugins/data/codex-openai-codex/state/<workspace-slug>/broker.json` and kill any stray `app-server-broker` / `codex app-server` processes — then run `codex:setup` and confirm `ready: true`. **A wedged broker is NOT a genuine tier-1 unavailability.** In that case clear prop and retry tier 1 — do **not** record it as `ready: false` and drop to tier 2, which would be a tier-order bypass (GHI #678).

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-137, § S4-139

**Record the tier and why.** Preserve the actual reviewer execution and observed
fallback reason in the acceptance record.
A caller declaration cannot promote a same-vendor execution to tier 1 or replace
missing review evidence. "The Claude subagent was convenient" is not a fallback
reason. `gz obpi complete` takes no tier, reviewer or fallback-reason flag
(GHI #1163); the acceptance record is the only source.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-141

**Acceptance transport preserves that tier order (GHI #985).** The acceptance
importer derives tier from actual execution; do not put a caller-authored `tier`
in the review JSON. A native Claude adversarial fallback includes
`fallback_reason` naming the observed tier-1 unavailability. Native Claude spec
and quality execution needs no fallback reason. If the operator explicitly acts
as the degraded human adversary after reviewing current proof and findings,
record their exact ruling with `gz obpi acceptance {OBPI-SLUG} human-review
--attestor g0 --ruling '<verbatim judgment>'`.
Never infer that ruling from permission to implement or repair, and retain the
separate completion attestation.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-147

> ### 🛑 THE PLUGIN IS THE ONLY TIER-1 DISPATCH SURFACE (operator directive, 2026-08-25)
>
> **`codex exec` is FORBIDDEN as a tier-1 invocation.** Dispatch through OpenAI's Codex
> plugin for Claude Code — its runtime `codex-companion.mjs`, on the `task --write` path
> shown above for Step 4b — and nothing else. Wrapping the raw binary in
> `gz arb step` is NOT an acceptable substitute
>
>
>
> **Never reintroduce a `codex exec`
> incantation to this file, even as an illustration.**

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-149, § S4-151, § S4-152

**Prove the tier; nothing declares it (GHI #765, #780, #985).** The tier is derived
from the argv the reviewer run executed, never from a flag or a name. Wrap the PLUGIN
invocation in ARB, then import that run:

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-153

```bash
uv run gz arb step --name codexadversary --max-output-chars -1 -- \
  node "$HOME/.claude/plugins/cache/openai-codex/codex/<ver>/scripts/codex-companion.mjs" \
  task --write --cwd <checkout> --prompt-file <prompt.md>
# → arb step name=codexadversary exit_status=0 receipt=.../arb-step-codexadversary-<hash>.json
uv run gz obpi acceptance <OBPI> review --receipt arb-step-codexadversary-<hash>
```

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-155

The executed output must contain the structured acceptance judgment described
below. The receipt's successful exit alone cannot establish acceptance.

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

Inside the disposable checkout, run it as `PYTHONPATH=<checkout>/src <repo>/.venv/bin/python -m unittest <selector>`; still name large artifacts BY PATH and let the reviewer open them.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-162, § S4-163

>
>
> Still require BOTH lines from the adversary — the `CORROBORATED | CORROBORATED-WITH-CAVEATS |
> NOT-CORROBORATED` line and the enum word Record the outcome by importing the review (`gz obpi acceptance <OBPI> review --receipt <run-id>`);

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-164, § S4-165

**Bound the claim BEFORE the first round, or the gate cannot converge (operator ruling 2026-09-03).** For any OBPI whose subject is a trust chain, provenance, or a tamper-evidence property, the brief MUST carry a `## Threat Model` section BEFORE Step 4b is first dispatched, naming what an attacker may do and what is an accepted residual — and the dispatch prompt MUST state that boundary and forbid the adversary from reporting an out-of-scope attack as a finding.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S4-166

Wait for the human to respond "Accepted", "Completed", "attest completed", or equivalent. Do NOT proceed until attestation is received.

Do NOT mark ceremony task `completed` until attestation is received.

**When attestation arrives, immediately invoke `gz obpi complete` (Stage 5 Step 2) with the operator's phrase in `--attestation-text`.** The operator's short phrase is the attestation; the pipeline must not pause to ask for longer text and must not print runbook-style instructions for the operator to execute. Enrich the attestation text per `AGENTS.md` § Attestation (em-dash + concrete session evidence + receipt IDs) before passing it through.

**Human rejects:** Record feedback, return to Stage 2 with corrections.

**MANDATORY TRANSITION → Stage 5.** Once attestation is received, proceed to Stage 5 immediately. Do not summarize. Do not wait.

## Controls carried into Stage 4 from other sections

| `narrator` | Composes the Stage 4 evidence packet in operator-value framing — value narrative, key proof, evidence table, REQ coverage rendered for the human's attestation decision | Stage 4 (Present Evidence) — see § Stage 4 |

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § I-009

```
THE PIPELINE IS NOT COMPLETE UNTIL STAGE 5 FINISHES.
```

Every stage flows into the next. No "stop and summarize" between stages. No pause except the Stage 4 human attestation in Normal mode — and that pause comes only **after** Step 4b (the independent adversary) has run and its verdict is on the table. Soliciting attestation with Step 4b skipped is not a valid pause; it is a gate bypass. If you have not reached the end of Stage 5, you are not done — and violating the spirit of this rule is violating the rule. One other stop is legitimate: when Stage 4's round bound is reached or a round repeats the prior round's root, record `gz obpi block` and put the decision to the operator (§ Stage 4 — The review window, the bound, and the exit).

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § I-016

These thoughts mean STOP — you are about to break the pipeline:

| "The hook blocked me, I'll work around it" | Hook blocks are signals. Diagnose the cause. NEVER create marker files manually to bypass. |
| "The operator said `attest completed` — maybe they want me to explain what to do next" | No. `attest completed` IS the attestation. Run `gz obpi complete` immediately with that phrase (enriched per § Attestation) in `--attestation-text`. Do not produce runbook-style instructions for the operator to execute. |
| "My Step 4a evidence is green — tests pass, REQs covered — so I can present it and await attestation" | STOP. Green-on-your-own-evidence is the EXACT state Step 4b exists to distrust. You authored that evidence; you are the GHI #643 fabrication surface. You may NOT solicit attestation until applicable independent approval and closure have been imported for the current proof claims. Confidence from the authoring agent is worth zero at this gate. |
| "Step 4b is probably overkill for this small/authoring-only/obviously-correct OBPI" | Step 4b is expected on every lane, size and kind, and `gz obpi complete` refuses on every lane until the acceptance record holds a current independent adversarial review (`acceptance_store.completion_review`, GHI #985). "Obviously correct" is the precise feeling that precedes a hollow-test or fabricated-evidence skip. Dispatch the adversary. You are not the exception. |
| "I'll present Step 4a now and run the adversary after the operator responds / in the next turn" | Sequence violation. The adversary runs BEFORE attestation, not after — the operator attests holding the adversary's verdict. Presenting 4a as the terminal step of the turn, with 4b deferred, is the skip this gate forbids. Dispatch any missing required review before soliciting attestation; retain already applicable imported review. |
| "An independent Claude subagent is fine for 4b — I don't need Codex" | Tier-order bypass (GHI #678). A Claude validating Claude shares this agent's blind spots — the exact failure Step 4b exists to break. Codex (tier 1) is REQUIRED first; tier 2 is permitted ONLY after a checked `ready: false`. Run `codex:setup`; if `ready: true`, the Claude subagent is forbidden. "It was convenient" is not a fallback reason. |
| "The adversary is there to find problems, so a round that confirms the feature works is a soft round" | Inverted. A second model CONFIRMING the first model's implementation is correct is the entire point of Step 4b; probing is how that confirmation is earned. A round that only lists what it broke, and never demonstrates the feature doing its job, has not done the job. |
| "The adversary refuted again, so I'll fix these findings and re-run" | Check its `Weakest point` against the previous round FIRST. If it names the same root, another rework round surfaces it one layer deeper — that is three rounds and ~9 hours in the measured case. Stop and put the design to the operator. |
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
report it to the operator

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § T-024

**Handoff creation:** On any abort, after the surrender, run `/gz-session-handoff` to preserve context for the next session.

**When the next legitimate action is a human's, say so in the ledger and stop.**

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § T-026

```bash
uv run gz obpi block {OBPI-SLUG} \
  --reason "<what cannot proceed without a human>" \
  --next-action "<the concrete decision the operator owes>"
```

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § T-027

The operator
clears it with their own words:

```bash
uv run gz obpi unblock {OBPI-SLUG} --ruling "<decision>" --operator "<who>"
```

**No attestor is required to record a block.**

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § T-030

Use one writer per governed checkout. Read-only investigation may run independently.
Only the operator initiates OBPI work; separate sessions do not grant initiation.
Capture the contract and input components before review and verify applicability
before consuming it. Sequence shared acceptance/schema writes outside review windows.
If another run changes the subject, identify affected evidence before continuing.
Never stash, pop, reset, revert, or sync another active run's work to clean the tree.

All OBPIs require per-OBPI human attestation (universal per ADR-0.0.36).

If a pipeline hook blocks a write, that means the pipeline is not active or evidence is missing. The correct response is to diagnose the cause — NOT to manually create marker files or ledger entries to bypass the hook. Manually creating files to bypass hooks defeats the entire enforcement mechanism.
