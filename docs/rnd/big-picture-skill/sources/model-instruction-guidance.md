# Model instruction guidance for high-altitude project synthesis

Research date: 2026-09-19. Persona: main-session — craftsperson, governance-aware, whole-file-reasoning, direct. Provenance: R&D run `big-picture-skill`. This is source research and design advice, not a skill implementation or operator ruling. The three external sources below are official Anthropic guidance, read live on this date. Each quotation is short; guidance is separated from recommendations.

## Primary guidance

### Clear outcomes, examples, and evidence grounding

Source: [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), sections General principles, Long context prompting, Thinking and reasoning.

> “Prefer general instructions over prescriptive steps.”

The guide recommends explicit output expectations and explaining their purpose. Examples should resemble the task but vary enough to avoid accidental pattern copying. Its long-document advice separates source content and metadata, places the final query after long inputs, and extracts relevant quotations before analysis. It cautions that model-specific techniques require evaluation before transfer to another model.

Application recommendation: state the audience, purpose, and desired explanatory quality, then supply the operator-liked report as an example. Add an adopter example from a different domain so gzkit vocabulary does not become the expected content. Ask for supported conclusions and a compact evidence appendix, allowing the narrative's structure to fit the project. Source quotations belong in evidence preparation; the reader need not receive a quotation-heavy executive report.

### Instruction altitude and context selection

Source: [Anthropic, Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), sections The anatomy of effective context and Context retrieval and agentic search.

> “The optimal altitude strikes a balance: specific enough to guide behavior effectively, yet flexible enough to provide the model with strong heuristics”

The article describes competing problems: brittle procedural prompts and vague instructions that assume missing context. It recommends starting with sufficient, economical instructions and extending them in response to observed failures. Canonical, varied examples are preferable to an exhaustive edge-case inventory. Context selection matters because large windows still have attention limits.

Application recommendation: the skill should orient the model around value, trajectory, and design coherence without dictating an exhaustive report-production algorithm. Gather evidence that can change the assessment, follow consequential contradictions, and retain source locations for deeper inspection. A compressed prior report should help comparison but not replace current evidence. This does not authorize skipping reads required by repository canon.

### Evaluation that matches the real reporting task

Source: [Anthropic, Define success criteria and build evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests), sections Define your success criteria, Eval design principles, Grade your evaluations.

> “Design evals that mirror your real-world task distribution.”

The guide accepts consistent qualitative rubrics alongside quantitative measures and identifies relevance, coherence, context use, and audience-appropriate style as separate dimensions. It includes long, missing, and ambiguous inputs among edge cases. Mechanical grading works for exact properties; nuanced judgments can use human or model grading, with model-grader reliability established first.

Application recommendation: compare candidate instructions on actual report cases rather than test for prescribed headings. Useful cases include strong delivery with poor user outcomes, sparse adopter evidence, stale campaign claims, and a prior forecast contradicted by later results. Evaluate factual support separately from explanatory value. Operator preference is necessary evidence of usefulness; a self-awarded numerical score does not establish it.

## Local authoring constraints

Read in full: [skill-authoring rule](../../../../.gzkit/rules/skill-authoring.md) and [Claude tuning](../../../governance/opus-tuning.md). These remain the repository authority for any eventual authored skill; provider pages are supporting research, not instructions overriding canon.

The rule requires scope and stop conditions, one home per meaning, conditional material behind reference pointers, and positive behavioral guidance. It rejects redundant re-check instructions where mechanical witnesses exist. Claude tuning distinguishes model effort from quality and makes calibration model-specific. Accordingly this research recommends neither a fixed effort setting nor an extra verification-agent ceremony. This track did not re-audit GPT tuning or select a model.

## Recommended design posture

The most important instruction is the report's intellectual task: explain how observed changes alter the project's ability to fulfill its purpose, and what that implies for its design and direction. This is a recommendation derived from the user's challenge, not an Anthropic quotation.

The report should leave room for a thesis that differs between runs. A coherent argument may be encouraging, mixed, or adverse; the investor framing must not push the model toward promotion. The audience is investing attention and resources, so uncertainty and opportunity cost belong in the account.

The operator-liked example is a strong starting specimen. Treat it as evidence of the desired altitude and presentation, not as a mandatory set of claims about every project. In particular, a different adopter may need a story about user adoption, scientific capability, or operational reliability rather than governance machinery.

Keep authorship guidance, report lifecycle rules, and historical research distinct. Publication metadata can be mechanically precise while the narrative remains flexible. A later reporting series should reveal whether its judgments improve understanding over time, including when earlier judgments were wrong.

No new files outside this research report, ledger events, report infrastructure, or skill implementation were produced by this track.
