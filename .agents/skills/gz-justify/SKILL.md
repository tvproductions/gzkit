---
name: gz-justify
persona: main-session
description: Pre-execution reasoning walkthrough for GHIs, OBPIs, and drafts. Invoke before implementation when confidence is <90%, when a gz-adr-evaluate score lands below 3.0, or when scope boundaries feel ambiguous. The CLI renders an 8-section markdown scaffold pre-populated with anchor evidence; you fill each `_[To be filled]_` block with grounded reasoning cited from the gathered evidence, then commit or attach the filled artifact to downstream governance.
category: obpi-pipeline
lifecycle_state: active
owner: gzkit-governance
last_reviewed: "2026-04-22"
gz_command: justify
metadata:
  skill-version: "6.0.0"
  govzero-framework-version: "v6"
  version-consistency-rule: "Skill major version tracks GovZero major. Minor increments for governance rule changes. Patch increments for tooling/template improvements."
  govzero_layer: "Layer 1 - Evidence Gathering"
---

# gz-justify

Pre-execution reasoning walkthrough. Run it when confidence is low, when scope is unclear, or when a prior evaluation (gz-adr-evaluate) flagged structural weakness. The verb renders a grounded scaffold from anchor evidence; the skill instructs you to fill it honestly, not to invent.

## Purpose

Claude Code agents rationalize their way past Prime Directive invariant 11 ("if <90% sure, ask the human") more than any other behavioral rule. The cost is confident-wrong-direction work — implementations that burn context and get discarded because an unstated assumption was wrong.

`gz justify <anchor>` closes the loop mechanically. It:

- Resolves an anchor (GHI, OBPI, or literal draft) and gathers five sources of evidence — matching rules, ledger events, recent commits, related anchors, and the regression taxonomy.
- Renders an 8-section scaffold whose first line is the YAML frontmatter delimiter `---`, with each reasoning block pre-populated with the gathered evidence and a `_[To be filled]_` prompt.
- Validates the filled walkthrough on the return trip via `gz justify validate <file>`.

This skill is the operator-facing ritual that turns the verb into discipline: it tells you *when* to invoke, *how* to fill, and *what counts as fabrication*.

## Common Rationalizations

Each row pairs the rationalization with the honest rebuttal.

| Rationalization | Rebuttal |
|---|---|
| "I already understand the brief — writing a walkthrough is busywork." | If you understood the brief you could fill all eight sections in under three minutes. Do so, and you have evidence. Skip, and you have a story. |
| "The anchor is obvious; I'll justify later." | Later means after a wrong-direction pass has already been committed. The walkthrough's value is pre-execution; post-hoc it is narrative. |
| "The confidence threshold is subjective — I can always claim 90%." | The threshold is self-reported. Lying to the threshold is worse than failing it — the invariant exists precisely because agents confidently mis-estimate their own confidence. |
| "My previous anchor is similar enough." | Similar is not the same. Rerun justify on this anchor; let the evidence tell you what's different. |
| "I'll fill it in if the operator asks." | Then the walkthrough is theater for the operator, not evidence for you. Fill it for your own execution. |

## Red Flags

Stop if any of the following apply. Each is a defect, not a judgment call.

| Red Flag | Why it's a defect |
|---|---|
| You are about to fabricate a filled reasoning block — invent a rule citation, synthesize a commit reference, paraphrase an anchor quote that isn't actually there. | Fabrication poisons the trust chain. The walkthrough becomes a reporting-pathway artifact (Lindsey et al. 2025) that is structurally separate from execution — exactly the failure mode `attestation-enrichment.md` names. If the evidence isn't there, write `_[No evidence in gathered sources]_` instead of inventing. |
| You are copy-pasting reasoning from a previous walkthrough and retargeting it to this anchor. | Cross-anchor reuse is the adjacent rationalization the CLI was built to prevent. If two anchors really do share reasoning, cite the first walkthrough's artifact path — don't restate the reasoning. |
| You are filling blocks before reading the anchor body the CLI embedded in Section 1. | Section 1 pre-populates anchor-body citations specifically so your reasoning can ground in them. Skipping the read step is the defining move of vibe coding (see `AGENTS.md` § DO IT RIGHT, items 2 (6b) and 5 (6e)). |
| You are declaring the walkthrough complete without running `gz justify validate <file>`. | The validator checks structural completeness (no unfilled ordinals). Skipping it means the artifact can silently ship with `_[To be filled]_` still in the body. |
| Your weighted confidence in "I know what I'm doing here" is >=90% — but you cannot point to a specific filled reasoning block that would convince a skeptical reader. | Subjective confidence without evidence is the rationalization the walkthrough exists to neutralize. Run the CLI anyway; if the walkthrough genuinely takes 90 seconds because the anchor is that clear, you've spent 90 seconds and have a cite-able artifact. |

## Persona

Active persona: `main-session` — craftsperson, governance-aware, whole-file-reasoning, direct. See `.gzkit/personas/main-session.md`. The walkthrough is whole-file-reasoning applied to a single change instance: you see the anchor and its evidence as one unit before you touch a line.

## Trust Model

`gz justify` is Layer 1 — evidence gathering. The CLI does not make reasoning claims on your behalf; it assembles the grounding surface you need to make them. Filling the walkthrough is co-authorship between the CLI (evidence) and the agent (reasoning). The filled artifact becomes durable evidence consumable by downstream governance — plan-audit receipts, OBPI brief verification, ADR closeout walkthroughs.

The contract is one-way: the CLI promises byte-stable scaffolds (identical input produces identical output; see `gzkit.justify.walkthrough.render_markdown`). You promise that every filled block grounds in the evidence the CLI gathered.

## Invocation

Default rendering (stdout):

```bash
uv run -m gzkit justify GHI-195
uv run -m gzkit justify OBPI-0.0.19-04-skill-and-upstream-integrations
```

Persist the scaffold (auto-path `artifacts/justify/<slug>-<timestamp>.md`):

```bash
uv run -m gzkit justify GHI-195 --save
```

Persist to an explicit path:

```bash
uv run -m gzkit justify OBPI-0.0.19-04 --output artifacts/justify/obpi-04-pre-exec.md
```

Literal draft (anchor not yet booked):

```bash
uv run -m gzkit justify --draft "consider extracting the parser into its own module" --draft-slug "extract-parser" --save
```

Validate a filled walkthrough on return:

```bash
uv run -m gzkit justify validate artifacts/justify/obpi-04-pre-exec.md
uv run -m gzkit justify validate artifacts/justify/obpi-04-pre-exec.md --json
```

The CLI rejects ADR anchors (`ADR-X.Y.Z`) by design — ADRs are governance packages, not change instances. Invoke on the tracking GHI or an OBPI under the ADR.

## When to Use

Invoke `gz justify` at any of the following moments. The upstream skills surface these automatically so you don't have to remember.

- **OBPI pipeline Stage 1→2**, when your self-reported confidence in the planned implementation is <90% (Prime Directive invariant 11). The `gz-obpi-pipeline` skill's Stage 1→2 Confidence Gate routes here.
- **After a gz-adr-evaluate run lands below 3.0** on an ADR with a tracking GHI or at least one OBPI. The `gz-adr-evaluate` skill appends a footer pointing to `uv run -m gzkit justify <parent-GHI-or-first-OBPI>`.
- **Before promoting a pool ADR** into active work — run justify on the tracking GHI to surface hidden ambiguity before you commit the lane/kind.
- **Mid-pipeline, when scope feels ambiguous** — if you are about to guess at whether a change crosses brief boundaries (see `.gzkit/rules/defect-fix-routing.md`), run justify on the in-flight OBPI and fill the scope boundary section before continuing.
- **At your own discretion**, when a task description contains hedging language ("probably", "should be able to", "I think") or when an operator request is ambiguous. The walkthrough is cheap; the wrong-direction pass is expensive.

Do not use it for governance ceremony steps that already have dedicated skills (plan-audit, OBPI completion, closeout). Those surfaces already produce receipts. `gz justify` is the pre-execution reasoning layer, not a substitute for any of them.

## Procedure

1. **Invoke the CLI on the anchor.** Pick the most specific anchor available: an OBPI if one exists, otherwise the tracking GHI, otherwise `--draft` + `--draft-slug`. Use `--save` if you want the artifact persisted to `artifacts/justify/`, `--output <path>` if you want an explicit destination.
2. **Read the rendered scaffold in full before touching a line.** Section 1 contains anchor-body citations, section 7 contains ledger/rule/commit evidence. These are your grounding sources. If a section's evidence list is empty, note it — you may need to gather evidence yourself before filling that section honestly.
3. **For each `_[To be filled]_` block, use the Edit tool to replace the placeholder with grounded reasoning.** Every filled block MUST cite evidence the CLI gathered or evidence you verified by reading the anchor body. If a section has no supporting evidence in the gathered sources and none available elsewhere, write `_[No evidence in gathered sources]_` and move on — do not invent.
4. **Preserve the 8-section structure.** Do not add sections, rename headings, or collapse sections. The downstream validator parses by ordinal.
5. **Save the artifact** via `--save` or `--output`, or commit the edited file in place if you rendered to an explicit path.
6. **Run the round-trip validator** — `uv run -m gzkit justify validate <file>`. Exit 0 means every section is filled. Exit 1 lists unfilled ordinals; go back to step 3 for each.
7. **Cite the artifact in downstream governance.** Plan receipts, OBPI brief Key Proof sections, and ADR defense briefs all accept walkthrough paths as evidence. The artifact is the durable proof that the pre-execution reasoning happened.

The whole loop should take 3-10 minutes on a well-understood anchor and 15-30 minutes on an ambiguous one. If it takes less than 3 minutes, you probably rationalized through step 2 — re-read the scaffold before committing.

## Acceptance Criteria

The skill's own completion contract — the state in which a walkthrough can be cited as evidence.

- [ ] The walkthrough artifact exists at a known path (either `artifacts/justify/<slug>-<ts>.md` or an explicit `--output` destination).
- [ ] `uv run -m gzkit justify validate <file>` exits 0 (every section is filled).
- [ ] No filled reasoning block contains fabricated citations or paraphrased-into-existence evidence. Empty-source sections are marked `_[No evidence in gathered sources]_` rather than invented.
- [ ] The artifact path is cited in the consuming governance surface (plan receipt, OBPI brief Key Proof, ADR defense brief, etc.).

## Related Skills

- **`gz-adr-evaluate`** — sources the low-score suggestion that routes to `uv run -m gzkit justify <parent-GHI-or-first-OBPI>` when weighted score < 3.0.
- **`gz-obpi-pipeline`** — Stage 1→2 Confidence Gate routes here when self-reported confidence is <90%.
- **`gz-plan-audit`** — downstream consumer; filled walkthrough artifacts are acceptable evidence in plan receipts.
- **`gz-design`** — upstream; if the anchor is a draft concept, run `gz-design` first to book the artifact, then `gz-justify` on the booked identifier.

## Related ADRs

- **ADR-0.0.19** — Pre-execution reasoning walkthrough. This skill is the operator-facing expression of that ADR's capability.
