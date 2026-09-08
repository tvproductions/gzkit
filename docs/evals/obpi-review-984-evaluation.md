# GHI #984 instruction scenario evaluation

Date: 2026-09-08. This samples decisions under pipeline instructions; it does not
execute an OBPI, certify a review, or measure elapsed time saved.

## Method

Two separate agents received the same [eight cases](obpi-review-984-scenarios.json)
and response contract. One read the canonical pipeline skill from repository HEAD
`1cef5d80` (version 6.50.0); the other read the working candidate (version 6.51.0).
The candidate was sampled before the final review corrected the refutation
recovery message and the skill's Stage-5 boundary-amendment and capability wording;
this sample does not evaluate those subsequent edits. They did not receive the
parent conversation or each other's responses. They
returned proposed actions, evidence needs, and stopping points. The preserved
[baseline response](obpi-review-984-baseline.json) and
[candidate response](obpi-review-984-candidate.json) are their original outputs,
not reevaluations after comparison.

The author assessed these responses against the case obligations below. This is
a qualitative reading, not an automated score or an independent efficacy study.

## Observed decisions

| Case | Required distinction | Baseline and candidate response |
|---|---|---|
| `partial_retry_repair` | Journal retention does not discharge retry durability | Both require completing the durability obligation before witness emission |
| `invalid_required_red` | Invalid supplied proof differs from reviewer tool limits | Both classify the false assertion-RED claim as a finding and keep execution limits separate |
| `auxiliary_audit` | Auxiliary tooling does not determine a finding's relevance | Both permit withdrawal of unsupported classifier proof while retaining the REQ-02 test defect |
| `failure_attribution` | A killed mutation does not identify its detector | Both require observed attribution and reject exclusivity inferred from equal length |
| `reviewer_environment` | Audit records within the permitted division of work | Both reject an identical impossible rerun and require independent inspection of the supplied evidence |
| `corrected_state` | A prior verdict cannot certify subsequent repairs | Both require focused independent closure and reject a round-count waiver |
| `claim_vs_implementation` | A false demonstration claim differs from a production defect | Both correct test provenance and examine the generator invariant before accepting the defect allegation |
| `authorized_continuation` | Existing authorization persists within approved work | Both continue the initiated repair and reserve real scope conflicts for the operator |

Both responses state `acceptance_ready: false` in every case. The cases all leave
some repair or review unperformed; this sample contains no fully completed case
testing whether an agent actually stops after sufficient evidence.

The candidate's failure-attribution answer calls for repairing the fixture to
reach the new assertion, while the baseline makes the stronger control conditional
on needing that claim. The case does not establish whether that assertion is the
only required proof route. This difference cannot support a claim that the revised
instructions eliminate unnecessary proof work.

## Result and limits

Both sets of answers preserve the central distinctions in these cases. There is
no observed improvement over baseline on those distinctions. The repair removes
concrete contradictions in instruction output and supplies more explicit evidence
handoff guidance; this evaluation does not establish that agents follow it better
or that future acceptance takes fewer rounds.

There is one response per instruction version, with no repeated sampling,
controlled model comparison, real implementation, or follow-through observation.
The cases explicitly disclose many of the defects they ask the agent to classify.
They test stated decisions, not independent discovery, artifact delivery, or
correct execution. Deterministic prompt and refusal tests are separate output
contract checks and likewise do not prove agent compliance.
