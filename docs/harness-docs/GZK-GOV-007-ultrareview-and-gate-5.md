# GZK-GOV-007: `/ultrareview` and Gate 5 attestation

**Status:** Proposed
**Date:** 2026-04-16
**Author:** Babb, J.
**Related:** GZK-GOV-001 (Five-gate governance model); GZK-GOV-003 (Human attestation template); Sprint and Drift, "Self-Verification Is Not Attestation" (2026-04-16)

---

## Context

Anthropic's 16 April 2026 release of Claude Opus 4.7 describes the model as capable of "devis[ing] ways to verify its own outputs before reporting back" (Anthropic, 2026b). The same release introduces `/ultrareview`, a new Claude Code slash command that produces a dedicated review session flagging bugs and design issues a careful reviewer would catch. Anthropic also extends auto mode to Max users in this release, a permissions option in which Claude makes decisions on the user's behalf during longer tasks without asking for per-step approval. In team workflows where these features are used together, a passing `/ultrareview` is already being treated by some practitioners as sufficient sign-off on a change.

The scholarly literature on intrinsic LLM self-verification does not support treating model self-review as attestation. Huang, Chen, Mishra, Zheng, Yu, Song, and Zhou (2024) showed that intrinsic self-correction on reasoning tasks fails to reliably improve accuracy and sometimes degrades it. Kamoi, Zhang, Zhang, Han, and Zhang (2024) showed that apparent gains in the self-correction literature generally collapse when oracle leakage and matched-compute baselines are controlled for. Panickssery, Bowman, and Feng (2024) demonstrated that LLM evaluators exhibit self-preference bias causally linked to self-recognition.

The Claude Opus 4.7 system card provides direct internal evidence for this last finding. Section 6.3.5 reports Opus 4.7 as showing the most pronounced self-preference bias of any recent Anthropic model, with three of four test conditions reaching statistical significance when the grader was told the transcript author was Claude (Anthropic, 2026a). Any procedure in which Opus 4.7 grades work it produced runs into this bias as a matter of the vendor's own measurement.

Attestation, in the GovZero sense drawn from aviation maintenance, clinical trials, and code review practice, is not equivalent to verification. Verification asks whether an artifact meets a specification. Attestation asks whether a responsible actor, who is not the author of the artifact, will sign their name to the claim that verification occurred and accept consequences if the claim is false. An actor cannot attest to their own work; the authorship structure of attestation is what gives the signature its signal value (Lee & See, 2004).

## Decision

1. `/ultrareview` output is recorded as a pre-attestation artifact under Gate 4 (behavioral specification) in the gzkit repository layout. It is stored at `governance/gate-4/ultrareview/{task-id}.md` with the model, model version, effort level, and timestamp recorded in a frontmatter block.

2. `/ultrareview` output is never accepted as a Gate 5 (human attestation) signature. No configuration flag, environment variable, or command-line option shall be added to gzkit that permits `/ultrareview` output to fulfill Gate 5.

3. The Gate 5 human attestation template (`templates/attestation.md`) is revised to include an explicit acknowledgement line: "I am not the author of the artifact under review; I am signing as an independent reviewer." The attestation is invalid if the reviewer's GitHub handle, commit history for the branch under review, or `/ultrareview` invocation history indicates they produced the artifact.

4. Each `/ultrareview` invocation writes a line to `governance/supervision.log` with the task ID, duration, whether the output was subsequently modified by a human reviewer, and the outcome at Gate 5. This log is the measurement hook for evaluating whether `/ultrareview` is supplementing or displacing human review over time.

5. `/ultrareview` may be cited in the Gate 5 attestation as an input the human reviewer considered, in the same way a static analysis report or test run output can be cited. It cannot be cited as the basis for the attestation.

## Consequences

Teams using gzkit will encounter modest additional friction. A passing `/ultrareview` no longer shortcuts the Gate 5 workflow, and the attestation template requires an additional acknowledgement line. The supervision log adds one filesystem write per `/ultrareview` invocation.

The authorship structure of Gate 5 is preserved. A reviewer cannot inadvertently sign an attestation for their own agent-produced work, because the template forces explicit acknowledgement that they are not the author.

The supervision log provides a dataset for a follow-up analysis at 90 days. The specific question to answer: does the rate of human modification to post-`/ultrareview` artifacts differ from the rate of human modification to pre-`/ultrareview` artifacts on comparable tasks? If the modification rate is similar, `/ultrareview` is supplementing review. If the modification rate is substantially lower for post-`/ultrareview` artifacts and outcome quality is held constant, `/ultrareview` may be quietly displacing review without quality loss, which is a finding worth publishing. If the modification rate is lower and outcome quality degrades, the slash command is displacing review at a cost, and the policy in this note will need revision to discourage use at Gate 4.

This decision does not preclude integrating model self-verification signals at earlier gates. Tool-mediated verification runs (compiler invocations, test harness output, linter results) remain valid Gate 2 artifacts and are distinct from `/ultrareview` in kind, because their verification signal originates outside the model's weights (Kamoi et al., 2024).

## Implementation checklist

- [ ] Add `governance/gate-4/ultrareview/` directory with README explaining the pre-attestation status
- [ ] Update `templates/attestation.md` with the non-authorship acknowledgement line
- [ ] Add `scripts/log_ultrareview.sh` and wire it to the Claude Code hook for `/ultrareview` completion
- [ ] Add a pre-commit check that rejects Gate 5 attestations whose author matches the branch author
- [ ] Add `docs/supervision-log.md` describing the 90-day analysis plan

## References

Anthropic. (2026a). *Claude Opus 4.7 system card*. https://anthropic.com/claude-opus-4-7-system-card

Anthropic. (2026b, April 16). *Introducing Claude Opus 4.7*. https://www.anthropic.com/news/claude-opus-4-7

Huang, J., Chen, X., Mishra, S., Zheng, H. S., Yu, A. W., Song, X., & Zhou, D. (2024). Large language models cannot self-correct reasoning yet. In *Proceedings of the International Conference on Learning Representations (ICLR 2024)*. https://arxiv.org/abs/2310.01798

Kamoi, R., Zhang, Y., Zhang, N., Han, J., & Zhang, R. (2024). When can LLMs actually correct their own mistakes? A critical survey of self-correction of LLMs. *Transactions of the Association for Computational Linguistics*. https://doi.org/10.1162/tacl_a_00713

Lee, J. D., & See, K. A. (2004). Trust in automation: Designing for appropriate reliance. *Human Factors*, *46*(1), 50–80. https://doi.org/10.1518/hfes.46.1.50_30392

Panickssery, A., Bowman, S. R., & Feng, S. (2024). LLM evaluators recognize and favor their own generations. In *Advances in Neural Information Processing Systems 37 (NeurIPS 2024)*. https://arxiv.org/abs/2404.13076
