# Codex context special mission — 2026-09-12

Operator: g0. Status: approved CMS batch was published and verified, then overwritten by a concurrent checkout restore; republishing awaits writer coordination. Remaining proposals are unselected.
Existing route: GHI #921 (instruction diet), #934 (Anthropic card refresh),
#943 (model-specific prompting corrections). Full vendor parity remains under
ADR-pool.vendor-alignment-codex; this side quest does not initiate its OBPIs.

## Measured delivery

The table records the initial audit snapshot. Before publication, the working
tree independently changed: the current root was 47,851 bytes. Every selected
original still matched. The verified, subsequently overwritten publication yielded **42,442 bytes**, saving
**5,409 bytes (11.3%)** against that immediate baseline. See
[publication evidence](publication.json). Native delivery remeasurement follows;
the original hook and cap observations below are historical evidence.

| Surface | Observation | Consequence |
|---|---|---|
| Root AGENTS.md | 48,511 UTF-8 bytes, delivered whole | Primary recurring instruction target |
| Commands starting directory | Parent chain consumes the 65,536-byte cap; commands-specific file receives 0 bytes | Root-only delivery success does not prove subtree delivery |
| Tests starting directory | 17,025 of 30,284 tests-instruction bytes arrive | Tests guidance is truncated |
| Skills | 22,179-byte catalog block; bodies load on demand | Keep catalog metadata separate from selected skill bodies |
| Native project hooks | Three enabled registrations remain untrusted | Registration and direct handler tests do not prove automatic dispatch |

These are installed Codex CLI 0.154.0 prompt-assembly observations, not token
counts, the full desktop conversation, model-context capacity, or proof of
instruction obedience. No numerical comparison with Claude's context capacity
is established. Details and sanitized evidence: [delivery audit](delivery.md).

## Review artifacts

- [Root lines 1–350](root-first.md): all 248 nonblank lines classified, 19 section alternatives.
- [Root lines 351–406](root-doctrine.md): all 56 lines audited, 18 proposal units and corpus mappings.
- [First CMS batch](first-batch-review.md): exact originals and replacements for three system boundaries, the single shared root contract, and operator-only OBPI initiation/execution.
- JSON companions preserve line dispositions, source fingerprints and measurement details.
- [Targeted system-card review](system-card-review.md): nine doctrine surfaces,
  source-specific corrections and remaining consumption work.

The first batch projects 5,409 bytes of source-text savings. Larger section
alternatives include policy changes and are not a validated, composable
rendition. The next line-level area is canonical rules and their repeated
contribution to nested instruction files. Native delivery was audited across
those surfaces; their complete editorial audit remains outstanding.

## Evaluation basis

Retain facts, authority boundaries and project-specific decisions the model
cannot infer. Examine repeated instructions, generic competence coaching,
incident narratives and task-specific recipes for deletion, consolidation or
on-demand placement. An invariant tier controls the write path; it does not
exempt the text from critical review. Preserve runtime controls and distinguish
their witnesses from prose asserting that a procedure ran.

OpenAI's GPT-5.6 guidance recommends removing repeated instructions and testing
one group of changes at a time. It reports roughly 10–15% evaluation gains in
sample internal coding-agent evaluations, explicitly workload-dependent. This
supports an experiment here, not a promised gzkit improvement or an Astra
measurement. [Primary prompting guidance](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.6)

The operator-supplied Anthropic 80% system-prompt deletion claim has not been
verified in this audit and is not used as a premise. Prompting guidance and
system-card evaluations answer different questions. The existing
`frontier-model-card-currency` chore supplies the card-refresh route; mechanical
scan success does not establish that published cards have been consumed into
doctrine.

## Four-front placement

| Front | This mission's disposition |
|---|---|
| Handoff | Carry the audit path, selected/rejected replacements, actual delivery limits and unresolved source ownership across sessions |
| GHI triage | Reuse #921, #934 and #943; #983 constrains safe rendition publication; avoid another umbrella issue |
| ADR/OBPI campaign | Preserve feature ordering and operator initiation; no parity promotion or corpus-onboarding OBPI started |
| New R&D | Compare instruction variants on the same representative tasks; measure delivery, scope adherence, evidence integrity and permission behavior before claiming improvement |

## Publication constraints

The corpus-to-fresh-candidate defect tracked in #983 can omit uncaptured
material. Preserve the current complete rendition during any selected edit and
verify consumers, not just generator self-consistency. Rules currently originate
in `.gzkit/rules`; their corpus onboarding belongs to live ADR-0.35.0 item 12.
Do not invent per-rule CMS support or edit generated AGENTS/mirror files.

The operator selected D09, D10 and D14 verbatim: **Approve D09, D10 and D14**.
Six old entries were retired and three invariant replacements captured through
CMS commands, followed by compose, advisor review, content commit and agent sync.
All other proposals remain unselected. Audit artifacts are not automatically
loaded instruction surfaces. The baseline chore's serial unittest criterion
timed out at its 120-second limit; its five preceding checks passed. A timeout
is not a passing test result.

## Concurrent writer interruption

Git reflog records resets followed by the concurrent GHI #870 commit `4535839bb`. During this work tracked files were reset/restored, and the verified nine-operation CMS publication disappeared. The root returned to 48,511 bytes. No cause is attributed to the timed-out tests: no surviving Python process was found. The exact approved candidate, original snapshot, operation outputs, advisor receipt and transient native-delivery evidence remain available. Republish only after writer coordination, against the restored current complete rendition.

The [transient post-publication delivery report](delivery-after-transient-publication.md) measured 42,442 bytes at that time; it is not the current checkout. [Tests-rule audit](tests-rule.md) completes the next canonical-rule area without applying additional edits.
