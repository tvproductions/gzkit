# AI governance T4 research: critiques, implementation gaps, and effectiveness evidence

## 1. Short scope note

This note focuses on where AI governance appears to fail in practice, what critics dispute, and what empirical evidence currently exists on effectiveness, incident reporting, auditing, transparency, and accountability. It distinguishes **empirical evidence** from **analytical** and **normative** critiques. I used available `web_search` and `fetch_content` tools; an `alpha` paper-search tool was not exposed in this environment, so paper retrieval relied on accessible primary papers and policy reports.

## 2. Numbered source list

1. **The Bureaucratic Challenge to AI Governance: An Empirical Assessment of Implementation at U.S. Federal Agencies** (2023)
   https://dho.stanford.edu/wp-content/uploads/AIES-Bureaucratic-Challenge.pdf
2. **Auditing Work: Exploring the New York City algorithmic bias audit regime** (2024)
   https://facctconference.org/static/papers24/facct24-74.pdf
3. **Auditing of AI: Legal, Ethical and Technical Approaches** (2023)
   https://link.springer.com/article/10.1007/s44206-023-00074-y
4. **NTIA Artificial Intelligence Accountability Policy Report** (2024)
   https://www.ntia.gov/sites/default/files/publications/ntia-ai-report-final.pdf
5. **Voluntary AI Commitments** (White House commitments text) (2023)
   https://bidenwhitehouse.archives.gov/wp-content/uploads/2023/09/Voluntary-AI-Commitments-September-2023.pdf
6. **Do AI Companies Make Good on Voluntary Commitments to the White House?** (2025)
   https://arxiv.org/pdf/2508.08345
7. **Adverse Event Reporting for AI: Developing the Information Infrastructure Government Needs to Learn and Act** (2025)
   https://hai.stanford.edu/policy/adverse-event-reporting-for-ai-developing-the-information-infrastructure-government-needs-to-learn-and-act
8. **AI Incident Database - OECD.AI** (ongoing database page)
   https://oecd.ai/en/catalogue/tools/ai-incident-database
9. **AI Index Report 2025, Chapter 3: Responsible AI** (2025)
   https://hai.stanford.edu/assets/files/hai_ai-index-report-2025_chapter3_final.pdf
10. **A Closer Look at the Existing Risks of Generative AI: Mapping the Who, What, and How of Real-World Incidents** (2025)
    https://ojs.aaai.org/index.php/AIES/article/download/36655/38793
11. **On the Limitations of Compute Thresholds as a Governance Strategy** (2024)
    https://arxiv.org/abs/2407.05694v1
12. **The Governance Misspecification Problem** (2024)
    https://law-ai.org/the-governance-misspecification-problem/
13. **Quantifying Detection Rates for Dangerous Capabilities: A Theoretical Model of Dangerous Capability Evaluations** (2024)
    https://arxiv.org/pdf/2412.15433
14. **Risk Thresholds for Frontier AI** (2024)
    https://arxiv.org/pdf/2406.14713

## 3. Evidence table

| Problem / critique | Evidence or example | Source refs | Is this empirical, analytical, or normative? |
|---|---|---|---|
| 1. **Implementation gap between governance mandates and practice** | Stanford/Ho et al. assessed three binding U.S. federal AI governance laws and found **fewer than 40% of 45 legal requirements** could be publicly verified as implemented. It also found **nearly half of agencies failed to publish AI use-case inventories**, and about **88% of agencies likely subject to AI-plan requirements had not published plans** by late 2022. | [1] | **Empirical** |
| 2. **Transparency mandates often fail even when legally required** | In the same federal-agency study, many agencies with demonstrable AI use still failed to disclose inventories or strategic plans, showing a gap between headline principles and administrative execution. | [1] | **Empirical** |
| 3. **Weak state capacity is itself a governance bottleneck** | The Stanford study attributes weak implementation to lack of expertise, weak leadership prioritization, ambiguous mandates, and insufficient personnel. This shows governance failure can stem from state capacity, not only corporate resistance. | [1] | **Empirical + analytical** |
| 4. **Auditing lacks mature standards and evidence of effectiveness** | Mökander’s review concludes AI auditing is growing fast but remains under-standardized; claims that systems have been “audited” are hard to verify without shared baselines, and there is a “large discrepancy” between attention to auditing and empirical evidence on its feasibility/effectiveness. | [3] | **Analytical (review of field)** |
| 5. **Audits can become box-ticking and produce false reassurance** | Drawing on the history of safety audits, Mökander notes audits can become box-ticking exercises, create false security, and still fail to prevent harms; access constraints from IP/privacy also limit what auditors can actually inspect. | [3] | **Analytical** |
| 6. **Audit regimes can fail because key terms are vague** | FAccT 2024 analysis of NYC Local Law 144 found the regime “failed to create an effective auditing regime”: the law did not clearly define AEDTs or independent auditors, so vendors, employers, and auditors effectively defined the regime themselves. | [2] | **Empirical (interviews/case study)** |
| 7. **Transparency-only audit regimes may not protect affected people** | The NYC audit study argues LL144 relied on a faulty transparency-driven theory of change: publishing bias-audit reports did **not** require firms to stop using biased tools or remediate them, so public disclosure alone did not reliably protect job applicants. | [2] | **Empirical + analytical** |
| 8. **Industry can narrow scope through lobbying and interpretation** | The NYC study reports lobbying and legal narrowing of what counts as an AEDT, to the point many companies considered themselves exempt. This is a concrete enforcement-evasion failure mode. | [2] | **Empirical** |
| 9. **Auditors often cannot get the data they need** | Interviewees in the NYC study reported “enormous practical and cultural challenges” getting access to employer/vendor data. Some vendors resisted disclosure; NDAs and weak regulator guidance worsened access problems. | [2] | **Empirical** |
| 10. **No clear oversight of auditors means ‘who audits the auditors?’ remains unresolved** | The NYC study found disagreement over what a legitimate auditor is and what services are compatible with independence. That weakens confidence that audit outputs are comparable or trustworthy. | [2], [3], [4] | **Empirical + analytical** |
| 11. **Voluntary governance lacks consequences and verifiability** | NTIA’s 2024 accountability report explicitly argues the U.S. needs more than voluntary measures: accountability needs information flow, independent evaluation, and **consequences** (liability, regulation, market pressure). It recommends mandatory independent evaluations for some high-risk systems and says voluntary frameworks alone are not compliance mechanisms. | [4] | **Analytical / policy analysis** |
| 12. **Public commitments without disclosure are weak accountability instruments** | The 2025 study of voluntary commitments says future commitments should require firms to proactively disclose implementation in verifiable ways. It reports structural shortcomings in current voluntary governance because commitments are public but implementation evidence often is not. | [6] | **Empirical + analytical** |
| 13. **Observed implementation of voluntary commitments is uneven and often poor** | The same study scores 16 companies on public evidence of implementing major voluntary commitments and reports an **average score of 17%**; for one commitment, **11 of 16 companies scored 0%**. That is unusually concrete evidence that public voluntary governance often lacks observable follow-through. | [6] | **Empirical** |
| 14. **Voluntary commitments can shift attention away from present harms toward future capabilities** | Hooker argues compute-threshold governance and related frontier approaches are shortsighted because they focus on future compute levels while deployed systems already cause harms. This can bias governance toward hypothetical future risk and away from present accountability. | [11] | **Analytical** |
| 15. **Capability/compute thresholds are unstable proxies for actual risk** | Hooker argues the relationship between compute and risk is highly uncertain and rapidly changing; emergent capabilities are hard to predict, so governance that treats compute as a stable risk proxy is likely to miss real harms or mis-target regulation. | [11] | **Analytical** |
| 16. **Proxy-based frontier governance can become misspecified** | The governance-misspecification analysis argues terms like “frontier AI” and “compute thresholds” can become overinclusive or underinclusive as technology changes, making rules ineffective or counterproductive. | [12] | **Analytical** |
| 17. **Threshold-based monitoring can fail because testing lags reality** | The detection-rates paper models dangerous-capability testing and finds failures can show up as biased estimates or lagged threshold monitoring; uncertainty and lab competition worsen these failures. This directly supports critiques that threshold governance may miss when systems cross risk-relevant lines. | [13] | **Analytical / modeling** |
| 18. **Even pro-threshold work prefers risk thresholds to capability thresholds in principle** | The GovAI paper says risk thresholds are more principled than capability thresholds, though harder to measure reliably. That is notable because even sympathetic work treats capability thresholds as a second-best proxy rather than an ideal governance target. | [14] | **Analytical** |
| 19. **Post-deployment learning is currently weak; governments often ‘fly blind’** | Stanford’s adverse-event-reporting brief argues pre-deployment testing cannot anticipate all real-world harms, while current post-deployment information largely remains private. Without reporting infrastructure, policymakers cannot learn systematically from failures. | [7] | **Analytical / policy analysis** |
| 20. **Current incident reporting is fragmented, voluntary, and incomplete** | The Stanford brief states existing lessons from social media and AI show harms are often not systematically monitored or reported; it advocates adverse-event reporting precisely because existing reporting leaves governments blind. | [7] | **Analytical** |
| 21. **Public incident databases are useful but inherently incomplete** | The 2025 generative-AI incidents paper warns that publicly reported incident databases are likely **not representative** because of reporting bias; harms may be over- or under-reported depending on visibility and salience. | [10] | **Empirical caveat + analytical** |
| 22. **Reported AI incidents continue to rise, but this is an ambiguous signal** | AI Index 2025 reports **233 AI incident reports in 2024**, a **56.4% increase** over 2023. This is evidence of persistent harm visibility, but not necessarily true growth in underlying harm because reporting practices also change. | [9] | **Empirical** |
| 23. **Generative-AI harms often fall on people who did not choose to use the system** | In a systematic analysis of **499 publicly reported generative-AI incidents**, CMU researchers find most incidents harm **non-interacting stakeholders** rather than the end user, undermining governance models that assume users/internal deployers are the main risk-bearers. | [10] | **Empirical** |
| 24. **Malicious use is a major real-world failure mode, not an edge case** | In the same 499-incident study, malicious use is one of the most prevalent sociotechnical failure modes, especially for autonomy, political/economic, psychological, and financial harms (e.g., deepfake fraud, impersonation, nonconsensual sexual imagery). | [10] | **Empirical** |
| 25. **Current governance frameworks underweight downstream and third-party harms** | The CMU incident study finds harms frequently accrue to third parties, communities, or society, not to the direct user. That creates accountability gaps when governance focuses on developer-user relationships only. | [10] | **Empirical + analytical** |
| 26. **Incident reporting and accountability require access, datasets, compute, and trained evaluators** | NTIA emphasizes that even where audits are mandated, the accountability ecosystem needs data, compute, researcher access, evaluator certification, and public-sector capacity. Weak infrastructure therefore becomes an enforcement problem. | [4] | **Analytical / policy analysis** |
| 27. **Transparency without access is weak accountability** | NTIA repeatedly notes disclosure must be paired with access for researchers, evaluators, and regulators; otherwise opacity, IP, privacy, and secrecy block meaningful external scrutiny. | [4] | **Analytical** |
| 28. **There is a live dispute over whether auditing can do more than produce ritualized assurance** | Mökander presents optimism about independent audits if properly structured, but also notes caution: some limitations are intrinsic, and policymakers should remain realistic about what auditing can achieve even under best practices. | [3] | **Analytical** |
| 29. **Voluntary governance is disputed because firms control too much of the evidence base** | Both NTIA and Stanford’s adverse-event reporting brief stress that post-deployment performance information is currently concentrated in private companies; this creates asymmetry that weakens both voluntary governance and public oversight. | [4], [7] | **Analytical** |
| 30. **Normative critique often outruns empirical proof** | Several criticisms of audits or voluntary governance are strongly plausible, but Mökander notes empirical substantiation of audit effectiveness/limits remains thin. The strongest current evidence is case-based (e.g., federal implementation failures, NYC LL144, incident datasets), not broad causal proof of what governance works best. | [1], [2], [3], [10] | **Analytical about evidence quality** |

## 4. Key contradictions or unresolved debates

1. **Auditing is central in governance design, but proof of audit effectiveness is still limited.**
   - Proponents treat audits as a core accountability tool.
   - Critics argue audits can devolve into compliance theater or transparency theater.
   - Current strongest evidence shows implementation problems and access problems, not robust cross-sector evidence that audits reduce harms.

2. **Incident counts are evidence of visible harm, but not clean measures of underlying harm.**
   - Rising incident reports support concern that harms are persistent and substantial.
   - But public incident databases are affected by reporting bias, media salience, and inconsistent definitions.

3. **Voluntary commitments may improve coordination, but usually lack verifiable proof and sanctions.**
   - Supporters view them as fast, flexible, and innovation-compatible.
   - Critics point out that without standardized disclosure, independent verification, or penalties, they often provide weak accountability.
   - The 2025 commitments study strengthens the critique by showing low public-evidence scores.

4. **Capability/compute thresholds are administratively attractive, but may be substantively misaligned with risk.**
   - Thresholds are easier to operationalize than direct risk measures.
   - Yet multiple sources argue they are unstable proxies, can lag technological change, and may redirect attention away from real deployed harms.

5. **Pre-deployment testing is necessary but not sufficient.**
   - Nearly all serious governance proposals rely on evaluations before release.
   - But both incident evidence and policy analysis show many important harms emerge only in deployment, meaning post-deployment reporting and monitoring are indispensable.

6. **Transparency is repeatedly treated as a solution, but often functions only as an input.**
   - Disclosure can support scrutiny, litigation, market pressure, and research.
   - But transparency without enforcement powers, data access, remediation duties, or public capacity often does not produce accountability on its own.

7. **Current evidence is much stronger on failure modes than on successful governance interventions.**
   - We have concrete evidence of implementation failure, under-reporting, weak observability, malicious use, and non-user harms.
   - We have far less rigorous evidence showing which specific governance instruments reliably reduce those harms across contexts.

## 5. Explicit ledger update note for T4

**T4: completed** — evidence-backed account assembled on implementation gaps, critiques of voluntary governance, auditing limits, capability-threshold governance concerns, enforcement/accountability weaknesses, and available empirical evidence on incidents and harms.
**Caveat:** alpha-tool use was **blocked by tool availability in this environment**, but the task itself is completed using accessible primary papers, official reports, and policy analyses via web/fetch retrieval.
