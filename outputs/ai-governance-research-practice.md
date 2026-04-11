# AI governance practice research — organizational and frontier-lab mechanisms

## 1. Short scope note
This note focuses on **publicly documented governance mechanisms that leading AI labs and major deployers say they use or have formally proposed**, with emphasis on primary documents: preparedness / safety frameworks, system or model cards, deployment gating, red-teaming, access controls, monitoring, incident / noncompliance reporting, and governance oversight. It intentionally does **not** treat regulation, academic critique, or broad conceptual governance literature as the main object of study.

## 2. Numbered source list
1. **Anthropic, “Responsible Scaling Policy Version 3.0”** — 2026-02-24
   https://anthropic.com/responsible-scaling-policy/rsp-v3-0
2. **Anthropic, “System Card: Claude Opus 4 & Claude Sonnet 4”** — 2025
   https://www.anthropic.com/claude-4-system-card
3. **OpenAI, “Preparedness Framework Version 2”** — 2025-04-15
   https://cdn.openai.com/pdf/18a02b5d-6b67-4cec-ab64-68cdfbddebcd/preparedness-framework-v2.pdf
4. **OpenAI, “Operator System Card”** — 2025-01-23
   https://openai.com/index/operator-system-card
5. **Google DeepMind, “Updating the Frontier Safety Framework”** — 2025-02-04
   https://deepmind.google/discover/blog/updating-the-frontier-safety-framework/
6. **Google DeepMind, “Gemini 3.1 Pro - Model Card”** — 2026-02-19
   https://deepmind.google/models/model-cards/gemini-3-1-pro/
7. **Microsoft, “Transparency Note for Azure OpenAI in Microsoft Foundry Models”** — undated/current Microsoft Learn
   https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/transparency-note
8. **Microsoft, “Microsoft Foundry risk and safety evaluations Transparency Note”** — undated/current Microsoft Learn
   https://learn.microsoft.com/en-us/azure/foundry/concepts/safety-evaluations-transparency-note
9. **AWS, “Amazon Bedrock abuse detection”** — undated/current AWS documentation
   https://docs.aws.amazon.com/bedrock/latest/userguide/abuse-detection.html
10. **AWS, “How Amazon Bedrock Guardrails works”** — undated/current AWS documentation
   https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-how.html

## 3. Comparison table

| Organization | Governance mechanisms | Evidence type | Limits / caveats | Source refs |
|---|---|---|---|---|
| **Anthropic** | Responsible Scaling Policy (RSP); capability-threshold-based safeguards; current **ASL-3 protections** including classifier guards, trusted-user exemptions/access controls, red-teaming, bug bounties, threat intelligence, and security controls; recurring **Risk Reports** every 3–6 months; external review for certain high-capability/significantly redacted reports; **Responsible Scaling Officer**; Board + Long-Term Benefit Trust notification/approval paths; anonymous noncompliance reporting; annual third-party procedural compliance review. Claude 4 system card also describes **pre-deployment safety testing** and explicit **AI Safety Level determination** for release decisions. | Formal policy plus release-specific system card. | Strong on stated governance structure, but much remains self-described; public docs do not show full internal execution logs or incident history. Risk Reports are promised/structured, but public visibility depends on publication and redactions. | [1], [2] |
| **OpenAI** | **Preparedness Framework** with Tracked Categories (bio/chem, cyber, AI self-improvement), High/Critical thresholds, **Capabilities Reports** and **Safeguards Reports**; **Safety Advisory Group (SAG)** recommendations with Board Safety & Security Committee oversight; commitment not to deploy High-capability systems without safeguards and to **halt further development** at Critical until safeguards/security controls are specified. Operator system card shows concrete deployment controls: **external and internal red teaming**, limited research-preview deployment, human confirmations for risky actions, proactive refusals for high-risk tasks, website restrictions, prompt-injection monitoring, and post-deployment automated/human abuse review. | Framework + system card with measured deployment evidence. | Stronger evidence of operationalization than framework-only docs, but metrics are from vendor-defined eval sets and not independent audits. Internal deliberation details remain limited. | [3], [4] |
| **Google DeepMind** | **Frontier Safety Framework (FSF)** with Critical Capability Levels (CCLs), recommended security levels, safety buffer logic, fixed-cadence and capability-jump-triggered testing, deployment mitigations tied to a **safety case**, and **corporate governance body approval** before general-availability deployment; continued post-deployment review/update of safeguards. Gemini 3.1 Pro model card reports frontier-safety evaluations across CBRN, cyber, harmful manipulation, ML R&D, and misalignment; notes when models hit **alert thresholds** but remain below CCLs; states mitigations continue in relevant domains. | Framework update + model card reporting concrete evaluation outcomes. | Public reporting is more summary-level than full audit detail; many mitigation specifics are delegated to linked reports or not publicly enumerated. | [5], [6] |
| **Microsoft (Azure OpenAI / Foundry)** | Platform-level governance controls: Microsoft-developed **guardrails/content filters** and **abuse detection models** integrated with Azure OpenAI; limited-access / scoped-use posture for some services; customer guidance for logging, monitoring, prompt isolation, rate limits, and human review. Foundry safety evaluations provide automated **adversarial dataset generation**, risk scoring for harmful content and **direct/indirect jailbreaks**, and stakeholder/auditor sharing of results, with explicit **human-in-the-loop** requirements. | Product transparency notes describing current service behavior and evaluation tooling. | Primarily deployer/platform governance, not frontier-model training governance. Many safeguards are customer-configured or customer-operated, and Microsoft explicitly says customers must run their own evaluations. | [7], [8] |
| **AWS (Amazon Bedrock)** | Current service-side controls include **automated abuse detection** over prompts/outputs, classifier-based harmful-content detection, pattern analysis for potential policy violations, **CSAM detection/blocking/reporting**, and possible suspension/escalation if misuse is detected. **Bedrock Guardrails** apply configurable pre-inference input checks and post-inference output checks, with blocked responses or masking for violations. | Product docs describing active platform controls. | Strong evidence of operating service controls, but this is platform moderation/governance rather than frontier-lab capability gating. No comparable public board-level or preparedness-style governance artifact in these sources. | [9], [10] |

## 4. Brief note on what is public commitment vs demonstrated process
### Mostly public commitment / governance promise
- **Anthropic RSP**: clearly specifies future-facing governance commitments (Risk Reports, external review conditions, governance roles, Board/LTBT pathways, annual procedural review), though it also references protections already in place. [1]
- **OpenAI Preparedness Framework v2**: primarily a commitment framework for how thresholds, safeguards, and governance should work as capabilities rise. [3]
- **Google DeepMind FSF update**: partly a governance commitment document describing how deployment mitigations and safety-case approval should operate. [5]

### Stronger evidence of documented operational process
- **Anthropic Claude 4 system card**: documents pre-deployment testing and an actual release decision under specific AI Safety Levels. [2]
- **OpenAI Operator system card**: strongest operational evidence in this set, because it gives measured results and concrete controls (97% refusal on an internal agentic-harms set, 92% confirmation recall on risky-action tasks, prompt-injection monitor at 99% recall / 90% precision on cited eval sets, limited rollout, post-deployment monitoring). [4]
- **Google DeepMind Gemini 3.1 Pro model card**: documents actual frontier-safety evaluation outcomes by domain and ties them to the FSF threshold structure. [6]
- **Microsoft Azure / Foundry docs**: describe active service controls already integrated into the platform and available eval pipelines, but mostly as deployer tooling rather than frontier-lab self-governance. [7], [8]
- **AWS Bedrock docs**: describe currently running platform controls (automated abuse detection, blocking, masking, CSAM reporting, configurable guardrails), which are real operational controls, though not equivalent to preparedness-style frontier governance. [9], [10]

## 5. Synthesis
Across the organizations with the clearest evidence, a practical governance stack is emerging with recurring elements:
1. **Capability- or risk-threshold frameworks** that tie stronger controls to stronger models (Anthropic ASL thresholds; OpenAI High/Critical thresholds; DeepMind CCLs). [1], [3], [5]
2. **Pre-deployment evaluation and red-teaming**, often including external participants and, increasingly, domain-specific evaluations. [2], [4], [6]
3. **Deployment gating**: explicit statements that release requires post-mitigation risk to remain below a threshold or that deployment must wait for safeguards / approvals. [3], [4], [5]
4. **Operational safeguards on access and use**: classifier guards, trusted-user exemptions, restricted websites/domains, abuse detection, blocked prompts/responses, masking, rate limits, and monitoring. [1], [4], [7], [9], [10]
5. **Transparency artifacts**: system cards, model cards, risk reports, transparency notes, and public framework documents. [1], [2], [4], [6], [7], [8]
6. **Governance / oversight bodies**: named internal review groups or officers plus Board-level oversight in some frontier labs. [1], [3], [5]

The clearest difference across organizations is between **frontier-lab governance** and **deployer/platform governance**:
- **Frontier labs** (Anthropic, OpenAI, Google DeepMind) publish threshold-based preparedness or safety frameworks and connect them to release decisions.
- **Major deployers/platforms** (Microsoft, AWS) publish more about **operational controls**, moderation, evaluation tooling, and customer-facing safety architecture than about frontier-model development governance.

## 6. Bottom line
The strongest primary-document evidence for organizational AI governance in practice is not generic ethics language but a set of recurring mechanisms: **threshold-triggered safeguards, pre-release evals/red-teaming, deployment gating, access controls, monitoring, and public reporting artifacts**. Among the documents reviewed here, **OpenAI’s Operator system card** and **Google DeepMind’s Gemini 3.1 Pro model card** provide the clearest public evidence of measured operational controls, while **Anthropic’s RSP** provides the most explicit internal governance architecture. Microsoft and AWS provide the clearest examples of **deployer-side runtime controls** rather than frontier-capability governance.

## 7. Explicit ledger update note for T3
**T3: completed.** Evidence gathered and synthesized into `outputs/ai-governance-research-practice.md`.
