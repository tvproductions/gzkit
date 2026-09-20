# R&D run — big-picture-skill

> Diamond 1 of the double diamond. This record defines the problem and names what is
> warranted; it produces no fan-out artifact and authorizes none. Opened 2026-09-19T23:54Z.

**Challenge.** Operator g0, in the conversation preceding explicit invocation:

> I had asked previously, at some design junction, for some facility that could occassionally tell the big picture story of gzkit (or any adopting project for that matter). magna carta was an attempt to get some cohesion towards a 1.0. But this would be a persistent skill that tried to take the operator back up to a "mile high/high altitude" perspective of the project. A model should be pretty good at that and taking those might provide good overall architecture/design insight.
>
> Yes, the example you just ran would work. we could refine it. think of a report to the project's investors, how are we coming along and what is the value we are building?

## source · explicit invocation

Operator g0, current conversation · read 2026-09-19.

> yes [$gz-rnd](/Users/jeff/Documents/Code/gzkit/.agents/skills/gz-rnd/SKILL.md) on this big picture skill idea. see above

This opens the R&D run. Earlier discussion is carried as cited conversation material;
this record was opened at invocation, not retrospectively presented as a contemporaneous
record of those earlier turns.

## source · reporting lifecycle and presentation

Operator g0, current conversation before invocation · read 2026-09-19.

> yes, but I also liked how you presented in your example above. I see it as a distinct skill of its own. with its own logging, report rotation, etc. Of course, everything always goes to the ledger, but still. discuss.

## decision · distinct portable skill with durable reporting

The operator explicitly selects a distinct skill for gzkit and adopting projects. Its
purpose is a high-altitude account of progress, value, and architecture/design insight,
with the earlier example's combination of narrative and supporting evidence. Its own
logging, report rotation, and ledger accounting are required parts of the design.
The verbatim rulings are in the challenge and source entry above. A status mode alone
does not satisfy this framing.

The prior assistant suggestions about permanent retention, report fingerprints, revisions,
current-report views, and comparison with earlier judgments remain design proposals.
Invocation of this run does not independently ratify every suggested mechanism.

## source · R&D ledger implementation boundary

[R&D discipline](../governance/rnd-discipline.md), § Ledger events — designed, not built
· read 2026-09-19.

> None of this is built, and the vocabulary must not be declared ahead of its producer.

This run must investigate supported accounting mechanisms before proposing an implementation
route. No R&D event is emitted by this record; the new reporting skill's ledger requirement
is a design requirement, not a claim that its producer already exists.

## decision · skill and documentation are independent valid outputs

Operator g0, current conversation · 2026-09-19:

> of the five fanouts, skills/docs/etc are valid outputs.

The five artifact-producing routes plus no action comprise the six-row map. The skill,
documentation, and related surfaces route is a first-class possible outcome; it does
not require an ADR as a prerequisite. Research into accounting does not preselect an ADR
route. Downstream production remains subject to the run's eventual disposition and sign-off.

## decision · operator initiation with agent suggestions

Operator g0, current conversation · 2026-09-19:

> B - but still operator initiated.

The operator selected the offered model: on request, with agent suggestions. An agent
may suggest a report at a meaningful milestone or change in direction and explain why
it would help. Only an explicit operator instruction starts the reporting run. Neither
elapsed time, an agent suggestion, nor a detected milestone authorizes generation or
publication. No scheduled or automatic run is commissioned by this decision.

## decision · retain reports and preserve the interpretive purpose

Operator g0, current conversation · 2026-09-19:

> yes, retain, I don't see running it every day, but it is easy for me to lose sight of the forest. The magna carta is useful to steer forward, but "what does this all mean" and "what does this look like from up high" is a different purpose. Yes, retain the reports.

Retain every published report. Rotation manages the current report and historical access,
not deletion after a count or age threshold. The operator anticipates occasional use;
this does not establish a schedule.

The report's central purpose is interpretation and perspective: what the accumulated work
means and what the whole project looks like from above. Magna Carta's forward-steering
purpose is distinct. A report may inform later steering decisions, but its value is not
contingent on producing a new work queue or changing campaign priority.

## source · existing reporting mechanisms research

[Complete research report](big-picture-skill/sources/reporting-mechanisms.md)
· received and read 2026-09-19; preserved verbatim as authored by the research agent.

> Consequently a saved report must not be described as ledger-published merely because it was committed. This is a concrete design constraint for the user's ledger requirement, not grounds to widen the classifier silently.

> A saved model interpretation is not reproducible merely by rerunning the model. Preserving the exact report permits later examination of what it claimed.

The full cited report is the source; these excerpts identify the questions relevant to
publication and retained history without replacing it with a reconstructed summary.

## decision · save and log when presented; research instruction quality

Operator g0, current conversation · 2026-09-19:

> yes, and strong models are good at this task so long as the skill provides the right instructions - we may want to review best practices and other guidance. Yes, "save and log when presented."

Save and log the completed report when it is presented. Publication records the assessment
received; it does not imply operator endorsement of its conclusions. Preserve later
corrections or disagreements with explicit linkage to the original report.

Research best practices and primary guidance on model instructions and executive synthesis
before settling the reporting contract. The operator identifies strong-model capability
and instruction quality as central to the proposed skill; no specific model is selected.

## source · executive reporting guidance

[Research and source links](big-picture-skill/sources/executive-reporting-guidance.md)
· read 2026-09-19 (America/Chicago).

IFRS Foundation, [integrated reporting FAQs](https://www.ifrs.org/issued-standards/integrated-reporting/faqs/):

> qualitative and quantitative disclosures, because each provides context for the other

Financial Reporting Council, [materiality guidance](https://www.frc.org.uk/library/research-and-insights/materiality/embed-a-materiality-mindset/):

> Are underperforming businesses and adverse events given sufficient prominence compared to success stories?

These external sources inform proposed instruction principles. They are not operator
authority, and no corporate reporting framework is adopted by citing them.

## source · model instruction guidance research

[Complete research report](big-picture-skill/sources/model-instruction-guidance.md)
· received and read 2026-09-19 (America/Chicago); preserved verbatim as authored.

Anthropic, [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices):

> Prefer general instructions over prescriptive steps.

Anthropic, [evaluation guidance](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests):

> Design evals that mirror your real-world task distribution.

The report separates primary guidance, local authoring constraints, and application
recommendations. Its proposed flexible narrative, examples, and evaluation approach remain
recommendations for discussion, not automatically adopted doctrine.

## decision · consistent coverage with flexible storytelling

Operator g0, current conversation · 2026-09-19 (America/Chicago):

> do this, go with research advice, be flexible: "**My recommendation is consistent coverage with flexible storytelling:** every report addresses purpose, value, trajectory, architecture, and uncertainty, but the model chooses the structure that best explains the project. A compact evidence appendix supports the readable account."

Adopt the quoted writing contract: every report covers purpose, value, trajectory,
architecture, and uncertainty; its organization follows the explanatory needs of the
project. A compact evidence appendix supports the account. Examples teach perspective
and presentation without requiring identical headings or conclusions across projects.

The research-informed approach grounds interpretation in evidence, gives contrary evidence
appropriate weight, and evaluates explanatory usefulness separately from factual support.
The operator's approval concerns this design direction; it does not close the remaining
publication-mechanism question or initiate downstream implementation.

## decision · operator funds delivery

Operator g0, current conversation · 2026-09-19 (America/Chicago), verbatim message:

> **Approve the R&D outcome. Write and deliver&#x20;****`gz-big-picture`****, including its report retention and ledger logging.”**

The operator funds the distinct skill and supporting documentation, including the
publication mechanism needed to satisfy retention and ledger logging. This explicitly
commissions downstream production; no ADR or OBPI initiation is inferred or required
as an extra prerequisite to the authorized work.

**commissions:** disposition 4 — write and deliver the skill, its references and coupled
report-publication support, including retention and ledger logging.

## decision · publication mechanism resolved for delivery

Research established that saving or committing these reports does not itself produce
publication provenance. Use a narrowly scoped report-publication command that preserves
the supplied Markdown, records its identity and content digest through the ledger,
and rebuilds current/history views from witnessed publications. Preserve every report
at its configured project documentation location. Stable publication identity permits
retry without duplicate events; conflicting reuse fails rather than changing history.

This is the implementation choice completing the operator-approved requirement, not
a new generic reporting platform. It preserves the skill/docs route. An ADR is not
selected: the choice is local and reversible, and does not meet all three R&D ADR
admission conditions. The operator's explicit delivery instruction covers the coupled
runtime support; no pool work or OBPI machinery is initiated.

## Disposition map

Final dispositions after the operator's delivery approval. Production is downstream
of this research run and limited to the commissioned outcome.

| # | Disposition | State | What | Reason |
|---|---|---|---|---|
| 1 | ADR / OBPI | not pursued | No initiation | Local reversible publication support does not meet all three ADR admission conditions; explicit delivery is commissioned under row 4. |
| 2 | GHI / direct fix | not pursued | No repair commissioned | The current request defines a capability; research must establish any existing intent owner before calling a gap a defect. |
| 3 | chore | not pursued | No scheduled maintenance | Persistent availability does not itself commission a schedule or chore. |
| 4 | control surface, rule, doc, skill, hook | commissioned | Distinct skill, documentation and coupled publication support | Operator explicitly approved writing and delivering the skill, retention and ledger logging. |
| 5 | one-shot refactoring | not pursued | None identified | Revisit only if research establishes a necessary architectural change. |
| 6 | no action | not pursued | Do not abandon the idea | Operator funded delivery. |

## Close

**Challenge restated.** Give an operator of gzkit or any adopting project an occasional,
high-altitude interpretation of its purpose, value, trajectory, architecture and
uncertainty. Preserve the account and its provenance so later reports can revisit
earlier judgments. This complements forward steering with understanding of the whole.

**Frontier.** Empty. Operator-only initiation, permitted suggestions, permanent retention,
publication when presented, flexible storytelling with consistent coverage, evidence
appendix and the publication mechanism are resolved. Remaining implementation and
verification are downstream production under disposition 4.

**Sign-off.** Fund — the verbatim operator delivery approval is recorded above. That
instruction remains effective as the publication mechanism is concretized; no repeated
approval is requested for the same outcome.

## What this record does not license

Only disposition 4 is commissioned. No ADR/OBPI initiation, chore, or unrelated reporting
platform is authorized. Report event vocabulary lands with its functioning producer;
this record emits no unbuilt R&D event. GHI #1028 remains held. Existing no-pool-build
and no-ADR-0.36.0-execution boundaries stand.
