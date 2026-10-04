# The four constellations

> Lifted byte-identical from `SKILL.md` § The reading frame on 2026-09-19 (GHI #921). The four-dimension table, the caution that binds every cluster, and the pass stay in the skill.

Each dimension is anchored by the sources the conversation named, marked
*(conv.)*. Saltzer and Schroeder are an operator-requested addition on 2026-09-12,
marked *(operator addition)*. Other additions are the agent's proposals on
operator direction 2026-09-12, pending ratification. This is a map of where the
thinking lives, not a completed literature review. Verify a source and its
claimed application before using it to support an audit finding, inside or
outside the repo. Linked sources support the qualified claims below; their
application to gzkit remains an interpretation to test against local evidence.
Each cluster ends by naming the boundary it crosses into
the next, per the conversation: *"Map that terrain rather than just adding
names."*

**Jurisdiction — the modularity cluster** *(conv., elaborated in the
conversation)*. Parnas 1972 *(conv.)*: a module hides a design decision, so the
boundary that matters is a decision, not a file. Dijkstra (separation of
concerns), Wirth (stepwise refinement), Myers and Constantine (cohesion and
coupling), Brooks (conceptual integrity). With Evans *(conv.)* for the bounded
context and Skelton and Pais *(conv.)* for ownership and cognitive load. The
cluster distinguishes design boundaries from authority boundaries. Saltzer and
Schroeder *(operator addition)*, ["The Protection of Information in Computer
Systems" (1975)](https://web.mit.edu/Saltzer/www/publications/protection/Basic.html),
§ I.A.3(f), supply the least-privilege anchor: grant only the authority needed
for the work. For this audit, compare the agent's available mutation authority
with its authorized change surface; a prose allowlist alone does not prove
enforcement. This application complements information hiding without treating
the two as identical. It crosses into contracts: once the
boundary is drawn, what must hold across it is the invariant lens's question.

**Change point — the seams cluster**. Feathers *(conv.)*, *Working Effectively
with Legacy Code* (2004): a [seam](https://www.informit.com/articles/article.aspx?p=359417&seqNum=2)
permits behavior to be altered without editing at that place; characterization
tests and effect sketches help examine existing behavior and impact. Fowler
*(conv.)*, *Refactoring* (1999; 2nd ed. 2018): change that preserves observable
behavior, and the strangler fig for replacing a surface incrementally. Hunt and
Thomas *(conv.)*, tracer bullets: a thin end-to-end slice through the real
system. Beck, *Test-Driven Development: By Example* (2002): the smallest step
that can fail, then pass, then be cleaned. Lehman, ["Programs, Life Cycles, and
Laws of Software Evolution" (1980)](https://users.ece.utexas.edu/~perry/education/SE-Intro/lehman.pdf),
Table I: continuing evolution can increase complexity unless work counteracts
it. This motivates inspecting coupling; it does not establish that age alone
narrows the legitimate seam. The cluster
decides where change is safe. It crosses into impact: a seam whose effect sketch
leaves the authorized surface is the escalation lens's question.

**Invariant — the contracts cluster**. Meyer *(conv.)*, *Object-Oriented
Software Construction* and "Applying 'Design by Contract'" (1992): preconditions,
postconditions and class invariants as obligations, not comments. Brooks
*(conv.)*, conceptual integrity: one coherent design story. Floyd (1967) and
Hoare (1969): assertions and the axiomatic basis, where pre and postconditions
come from. Hoare, ["Proof of Correctness of Data Representations" (1972)](https://link.springer.com/article/10.1007/BF00289507):
representation correctness is a candidate lens for corpus-to-rendition
preservation. That analogy needs an explicit abstract/concrete mapping and
preservation obligations; a renderer is not automatically such a proof.
Gries, *The Science of
Programming* (1981): the loop invariant as the thing that stays true while the
work moves. Liskov and Wing, "A Behavioral Notion of Subtyping" (1994):
contracts survive substitution, or the substitution is wrong. Ford, Parsons and
Kua, *Building Evolutionary Architectures* (2017): the architectural fitness
function: assessment of a named architectural characteristic. A validator
qualifies only when its measured property serves that architectural objective.
Nygard,
"Documenting Architecture Decisions" (2011): the ADR as the artifact whose
agreement with the code is the coherence this lens tests. The cluster decides
what must hold. It crosses into cognition and maintenance: inspect whether the
next session can reconstruct the invariant and its rationale from the artifacts
and handoff, rather than assuming the artifact alone carries understanding.

**Escalation — the impact-and-control cluster**. Arnold and Bohner *(conv.)*,
*Software Change Impact Analysis* (1996): the discipline of estimating what a
change will touch before making it. Yau, Collofello and MacGregor, "Ripple
Effect Analysis of Software Maintenance" (1978): an early treatment of the same
question. Weiser, "Program Slicing" (1984): dependencies relevant to a specified
program behavior. Compare ontology reach cautiously: graph reachability is not
program slicing without an explicit criterion and adequate data/control-flow
semantics. Letovsky and Soloway, "Delocalized
Plans and Program Comprehension" (1986): why impact escapes the seam, because a
plan is spread across places that do not name each other. Rasmussen, "Risk
management in a dynamic society" (1997): systems migrate toward the boundary of
acceptable performance under pressure; test that explanation against observed
pressures and adaptation rather than equating every discrepancy with migration.
Leveson, [*Engineering a Safer World* (2012)](https://mitpress.mit.edu/9780262533690/engineering-a-safer-world/):
safety as a control problem. Use that proposed lens to inspect control actions,
constraints and feedback. The airlock's purpose remains operator canon:
orientation and synthetic memory, movement control, focus and contamination
awareness, and monitoring results/disturbance. The analogy cannot redefine it
as a verification gate. Ohno, *Toyota Production System* (1988): jidoka and the
andon cord, stop the line and make the problem visible, the practitioner root
of stop-and-report. Hutchins, *Cognition in the Wild* (1995): cognition
distributed across people and artifacts, which is what a controlled handoff
carries. The cluster decides when to stop and what the stop must say. It
crosses back into jurisdiction: an impact argument ends by naming the boundary
that should have been drawn.
