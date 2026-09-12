# GZKit / Dark Software Factory --- Conversation Transcript

**User:** I was reading about... the guy who was talking about trying
the dark software factory last year. They pretty much said it gets too
complex for the agent to keep up. I feel like that's what I'm
experiencing. GZKit is almost too complex for the agent to be trusted to
do real work. The guy made the 12 Factor Agents repository on GitHub.

**Assistant:** It sounds like Dex Horthy from HumanLayer. The important
part of the dark-factory experience isn't simply that models make
mistakes. A change can pass today and quietly make tomorrow's change
harder. That rhymes with what you've been describing in GZKit.

**User:** I don't think it even does the slice effectively. I might not
be slicing it down narrowly enough like Matt Pocock suggests. He's not
unique in that suggestion. I studied all those books when this stuff was
new to me in the 90s and 2000s. It was a wondrous time to onboard the
craft. I wouldn't say the craft is dead, but it's easy to get detached
from the craft.

**Assistant:** Sounds less like you're missing the right blog post and
more like the unit you're handing over isn't actually stable in
practice. If a slice can't be changed safely by someone who wasn't there
yesterday, it may be a successful patch rather than a stable slice.

**User:** What's interesting is every time I have my structures
inspected, they usually pass muster. I've structured and guided my
agentic structures off emerging best practices, although I realize I
sometimes have to sunset practices that have become less good.

\[The conversation briefly shifts to recurring Bluetooth interference in
a drive-through and on stretches of road, then returns to GZKit.\]

**User:** Back to Dex Horthy. That's the guy. I discovered him sometime
last year. Twelve Factor Agents is picking up from Twelve-Factor App.

**Assistant:** He leans on the twelve-factor app ideas and reworks them
for agents, especially keeping state and behavior explicit.

**User:** At the World AI Conference in San Francisco this summer, Matt
talked about how to write a good skill. I'm looking for an elusive Holy
Grail in suggestions and corrections. But it's taking longer for an OBPI
to resolve with checks and balances.

**Assistant:** That's a little like spec drift. The longer it takes, the
more the target moves. You can shrink the unit again or freeze behavior
with a very explicit contract. Which side feels like it's slipping more,
scope or specification?

**User:** It's hard to tell because they were tightly bounded. About six
months ago I broke OBPIs into named requirements and tasks. I work
loosely with an agent to scope ADRs. I may not have enough discipline
when I spec an ADR. I'm really using ADR for spec and plan. I started
using some of these terms last summer, so I may not use them all
correctly, but they serve the same hierarchical goal---varying gear
ratios. They're larger and smaller gears in the same works. It takes
multiple days to finish an OBPI now. It used to take under an hour, then
multiple hours, then a good part of a day. I have a real job, but I
spend appreciable time mornings and evenings driving these agents. It
looks like it'll take a year for GZKit to mature. I wonder whether
people are putting more time and tokens in, running dark factories, or
have teams dividing and conquering. Anything real that you try to do
correctly takes a long time.

**Assistant:** When the work is real and the system is already dense,
each change drags more context in. That cost is real.

**User:** A lot of people aren't demonstrating sophisticated systems. It
feels like simplistic systems, or benchmarks about one-shotting. We
don't have apples-to-apples real-world accounting. There's confusion,
misdirection and hype. The earliest days of the web were probably like
this. Humans will sample, decide what's important, drop details, focus
on details and abstract details like we always have. It's difficult when
you're embedded in the prior paradigm or two and understood a lot about
them. Inside five years almost everything's changed.

**Assistant:** The ground keeps shifting and your footing never quite
sets.

**User:** We don't know that caring about the craft is misplaced. The
narrative is that we don't need people and AI will do it all. Yet
long-running principles re-emerge. There are persistent problems and
they end up interrelated.

**Assistant:** Whether or not the current narrative holds, the
fundamentals keep showing back up.

**User:** A Berkeley computer science guy at the World AI thing was
talking ontologies: Pydantic for shape and type checking on the input
and then against an ontology in the back. GZKit has plans for all this.
It just takes forever to build. Does language matter because models'
training sets reflect how they approach construction? Does a broad
language like Python matter more?

**Assistant:** Language still matters, but differently. The model's
prior is shaped by language, and language is part of the risk surface. A
permissive stack gives a sloppy agent more room to do damage.
Constraints become guardrails, taking some correctness out of the
agent's judgment and putting it into the system.

**User:** I'm talking about strong agents---frontier models released
within the last three or four months or weeks.

**Assistant:** With that in mind, training prior matters less.
Mainstream languages are well represented. The question is less "can it
write the language?" and more "can it avoid slowly corrupting the system
over time?" Language constraints help, but they don't supply missing
architectural memory. Even with top-end models, the next step probably
isn't a cleaner language but more intent made executable or checkable.

**User:** I regularly audit GZKit against frontier models. I'm not doing
anything wrong. Despite all my years as an academic, I don't ever have
to live with or babysit a system year on year. We make complete systems
in a semester. Research is similar: you create a program of research,
publish a paper, and then it becomes an artifact others extrapolate
from, extend or critique. Unless it's a long-running hard-science,
life-science or engineering endeavor, you don't carry it continuously.
Despite teaching this stuff, I haven't had to live with a complex
project I kept after. I may be experiencing pains I teach students about
but don't have lived instincts for.

**Assistant:** There's a difference between knowing the pattern and
carrying the system. GZKit may be teaching you the second one.

**User:** What are the common pains? Am I just encountering things
full-throated human teams would have encountered?

**Assistant:** Most of your pains match what human teams report: spec
drift, hidden coupling, regressions from missing context. Human teams
lose global understanding too; people leave and organizations change.
The twist is that you hit it solo. The agent boosts your throughput
without giving you a team.

**User:** I heard somebody discuss Peter Naur's "Programming as Theory
Building": the programmer develops a theory of the system and expresses
that theory through code. Some people are postulating that we don't need
to be connected to the code. Then Dex Horthy says they had to shut down
their dark or dim factory because it became a tangled mess. I think the
agent absolutely makes a tangled mess. Then you burn much more time or
tokens grinding agents to pick up the kinks and curls. There's
stochasticity inherent to what we're doing. It feels like epicycles and
Copernican heliocentrism versus geocentrism. I return to that because I
studied Kuhn's Structure of Scientific Revolutions as a PhD student.

**Assistant:** I get the Kuhn analogy: the messy in-between phase before
a stable paradigm. Naur's point was that the program is the theory in
programmers' heads, not the text. Agentic work challenges that. Maybe
the theory gets reconstructed just in time. But Dex's experience
suggests reconstruction isn't the same as continuous ownership. If each
fix adds epicycles, that may be the signal, not the noise. Naur might
ask: where does the theory live now---in your head, or in a shifting
pile that no one continuously holds?

**User:** Every design facet of GZKit is driven by my prompting,
inquiry, curiosity, design needs and goals. Nothing was truly shaped
without me directing it. I hold a theory at a level, but I don't hold
the deep earned theory of sweat equity. In a normal system distributed
across humans, they don't uniformly hold that either. They might
understand contracts better. That's one thing I'm probably not doing
enough: design by contract, bringing in software engineering and
architecture principles. You're still conducting a flight end to end
with a modern jet airliner even if aids and assists are greater. The
theory of the flight must reside in those in command. The more solo you
go, the more you shrink command and the burden of command. I think
that's a book I have. Is "The Burden of Command" a book title?

**Assistant:** "The Burden of Command" is a real title and a fitting
phrase: more automation, yet more accountability. You can distribute
theory through contracts and tests instead of total personal
understanding. Command becomes designing constraints, not holding the
entire system in your head.

**User:** Whose book is it? I think I own it, but refresh me.

\[The conversation returns to the Dark Software Factory before that
title question is resolved.\]

**User:** All right, back to the Dark Software Factory.

**Assistant:** What matters from Dex's dark-factory story isn't just
"agents make mistakes." Over time, the cost shifted from writing code to
understanding and repairing code. Early on, throughput was the
bottleneck. Now it's system coherence. The question might not be "How do
I get the agent to go faster?" but "How small does its jurisdiction have
to become as the system ages?"

**User:** "How small does its jurisdiction have to become, as the system
ages?"

**Assistant:** I think that question may be more important than "how
small should the task be?" Task size and jurisdiction are not the same
thing. A tiny task can have a large blast radius if it gives the agent
effective jurisdiction over many modules, abstractions, persistence,
tests and shared helpers. As GZKit ages, task size may need to decrease
somewhat while permitted jurisdiction decreases dramatically.

Perhaps the OBPI hierarchy isn't fundamentally wrong. The missing
boundary may be below it:

OBPI → requirement → task → authorized change surface.

The last item says: you may accomplish this task, but you are authorized
to modify these specific components/contracts. Everything else is
read-only. If the task requires crossing that boundary, stop and report
the dependency rather than fixing it.

This connects with Naur. You possess the intentional theory of GZKit.
What you lack is complete possession of the implementation theory
created by thousands of individual agent decisions. Each new session
reconstructs a partial theory from artifacts.

Contracts, invariants, architecture tests, ADRs and jurisdiction
boundaries therefore become more important as the system matures.
They're compressed pieces of theory that survive the disappearance of
the programmer who held them.

Tiny tasks reduce local reasoning difficulty, but if every tiny task
permits the agent to roam the repository, you've reduced task size
without reducing systemic risk. An experiment would be to keep one
well-shaped OBPI as-is but give each implementation task an explicit
change budget---files/modules it may modify, contracts it must preserve,
observable behaviors it may change, and conditions requiring
stop-and-escalate. If the validator/repair tail collapses, GZKit's
scaling problem may not principally be decomposition. It may be
jurisdiction.

**User:** Repeat the last thing you said.

**Assistant:** Task size and jurisdiction aren't the same. You can give
an agent a tiny task, but if doing it lets it roam across six modules
and refactor them, that's a small task with a big blast radius. As GZKit
ages, the agent's allowed jurisdiction probably has to shrink a lot,
even if the task feels small.

**User:** Is this similar to tracer bullets? I think The Pragmatic
Programmer talks about that.

**Assistant:** There's a family resemblance. Tracer bullets from Hunt
and Thomas are about driving a thin, end-to-end slice through the real
system to learn from reality. Jurisdiction is slightly different:
constraining where the agent is allowed to change things. A useful
hybrid is a thin vertical behavior plus an exact change surface---tracer
bullet with guardrails.

**User:** I have the airlock system. I just haven't gotten to it in
GZKit.

**Assistant:** The airlock fits cleanly. The thin tracer path can cross
the system, but the airlock forces a stop whenever the agent needs to
step outside authorized territory. That turns "just keep going" into
"pause here and make the boundary explicit."

**User:** Does that have basis in the literature---practitioner or
scholarly?

**Assistant:** It has roots, though more as a convergence than a single
named pattern. Change impact analysis addresses ripple effects.
Parnas-style modularity concerns what needs to change and what must not.
The airlock also resembles least privilege for design changes: narrow
permissions, explicit scoping and controlled boundary crossings.
Applying the combination directly to development agents is newer.

**User:** Which one---the jurisdiction part?

**Assistant:** Exactly: bounding the authorized surface of change and
forcing explicit boundary crossings.

**User:** What categories, segments of thinking, articles and concepts
can we pull in directly?

**Assistant:** Six bodies of work: modularity and information hiding,
plus DDD bounded contexts; change impact analysis; design by contract
and invariants; least privilege and capability-based security; Feathers'
seams and safe change; and cognitive load and ownership boundaries from
Team Topologies. Reduced to a kernel: change point, jurisdiction,
invariant, escalation.

**User:** Pull the four as-is. Keep them bare deliverables.

**Assistant:** Change point, jurisdiction, invariant, escalation.

**User:** What concepts are behind them?

**Assistant:** For change point: seams and safe change. For
jurisdiction: information hiding and least privilege. For invariant:
design by contract. For escalation: change-impact analysis and
controlled handoffs.

**User:** Let's start cooking something up. Tutor me more, dig deeper
into the resources. I'm going to forward this whole conversation into
the next GZKit session to see what improvements we can make---maybe not
make anything new, but see how we can beef up what we have.

**Assistant:** The valuable move is not to add machinery but sharpen the
thinking behind each of the four. Anchor on Parnas: which design
decisions are we hiding and protecting? Use Feathers for change point:
the narrowest seam where behavior can legitimately change. For
invariants, go beyond "tests pass" into preconditions, postconditions
and architectural invariants. For escalation, stop with an impact
argument: "I was authorized here; here's why that isn't enough; here's
the dependency and likely surface." Jurisdiction should constrain
mutation, not understanding. The agent should be able to read broadly
but write narrowly. Ask the next GZKit agent to study what's already
there in these four senses before proposing anything new.

**User:** You said one source was Parnas and somebody named Feathers.

**Assistant:** David Parnas wrote the classic on decomposing systems
into modules. Michael Feathers wrote Working Effectively with Legacy
Code. Together they give boundary logic and safe entry points for
change.

**User:** There are additional authors, right?

**Assistant:** Bertrand Meyer for design by contract; Robert Arnold and
Shawn Bohner for change impact analysis; Eric Evans for bounded context;
Matthew Skelton and Manuel Pais for cognitive load and ownership
boundaries.

**User:** Give me some authors and articles or books.

**Assistant:** David Parnas, "On the Criteria to be Used in Decomposing
Systems into Modules." Michael Feathers, Working Effectively with Legacy
Code. Bertrand Meyer, Object-Oriented Software Construction. Robert
Arnold and Shawn Bohner, Software Change Impact Analysis. Eric Evans,
Domain-Driven Design. Martin Fowler's refactoring work. Matthew Skelton
and Manuel Pais, Team Topologies. Hunt and Thomas, The Pragmatic
Programmer. Peter Naur, "Programming as Theory Building."

**User:** Let's break a few down. Pick the first one and go deeper.

**Assistant:** Start with Parnas. The key move in the 1972 paper is that
modules should hide design decisions or knowledge, not merely code. That
reframes jurisdiction as the set of design decisions an agent is allowed
to disturb. The question becomes not "how many files did it touch?" but
"did it cross an information-hiding boundary?" For a GZKit session:
which design decision is in play, and can this change be fully localized
behind the existing contract? If not, that's an escalation trigger.

**User:** I want to improve GZKit, but does this always behave well
under changing code? Why do the answers keep pouring into straight
code-oriented thinking?

**Assistant:** I've been collapsing GZKit into just the code base, and
that's too narrow. The same jurisdiction problem applies to ADRs,
validators, workflows, rules, prompts---not just code. The refined
question is: which decisions or artifacts is the agent allowed to
change, and what must remain invariant? That keeps us from fixating on
files and missing a silent rules change that rewrites the ground under
your feet.

**User:** Of course, we do make sure that they continue to align and
resonate.

**Assistant:** Alignment and resonance matter. I'd phrase it as
coherence across artifacts. The invariant isn't just tests passing; it's
that ADRs, validators, workflows and code tell the same story. When they
don't, that's an escalation, not a clever fix.

**User:** So that's what Parnas gives us. Do you tend to revisit the
same sources because they're canonical or seminal, or because they best
match what I typically ask about?

**Assistant:** A bit of both, but more the second. Those sources recur
because your questions orbit durable concerns and they fit. But there's
a risk of forcing everything through familiar lenses. It may be worth
mixing in control theory, safety engineering and socio-technical systems
to test whether old frames still hold.

**User:** Parnas must have peers that help round out the shapes and
demarcations, so we know the paradigmatic constellation or clustering
and where boundaries are.

**Assistant:** Exactly. Parnas is part of a modularity constellation.
Dijkstra on separation of concerns, Wirth on stepwise refinement, Myers
and Constantine on cohesion and coupling, Brooks on conceptual
integrity. Together they define a cluster around decomposing and
containing change. Then you cross a boundary to contracts, maintenance,
domain boundaries and cognition. Map that terrain rather than just
adding names. That keeps us from forcing a new agentic control problem
into a 1970s module frame.

**User:** For the four main concerns you identified, that's turning into
the shape of an analytical pass through GZKit, then decisions around it.
That would be a good addition because I'm going to pick this
conversation up and use it as a starter with a computer agent.

**Assistant:** Treat the four concerns as lenses, not features. For each
lens, map what GZKit already has, note gaps, and tie each to its own
constellation. Tell the next agent explicitly: don't add mechanisms
first. First do the mapping and call out genuine gaps.

**User:** We'd want to remember how to shape these, even if I don't
shape them all here in voice chat, then create an analytic shape to
apply in an investigative pass through GZKit.

**Assistant:** For each of the four, keep the same skeleton: concern,
governing question, intellectual lineage, current GZKit mechanisms,
evidence to inspect, failure signatures, and boundaries. Then the pass
becomes disciplined: inventory, map evidence to lenses, mark gaps and
overlaps, test against failure patterns, then decide. Cross-cutting
question: "Is this explicit enough that a fresh agent can reconstruct it
without relying on tacit memory?" That makes the artifact an analytic
tool, not a design spec.

**User:** What I hope to get is refinement of existing GZKit
affordances. It would be a health check, opportunity check, analytic
check, strategic/tactical check, etc.

**Assistant:** Exactly. Frame the pass not as a gap hunt but as a
capability and control review. For each concern: health check,
opportunity check, strategic fit, tactical tweak, and retirement. Has
something outlived its assumptions? That turns it into a controlled
systems audit---no reflex to add; see what to strengthen or retire.

**User:** I need a full transcript of this conversation for download
please.
