# First proposed CMS batch

Status: proposed; no instruction canon changed. Owner: g0. Route: GHI #921.

These three replacements preserve the named operating boundaries while removing incident narratives from the recurring root contract. Original corpus entries remain in append-only history. The exact original and proposed texts follow; this is a review packet, not a committed rendition.

Combined source-text reduction: **5,409 UTF-8 bytes**, from 7,084 to 1,675 bytes. Root-file projection: 48,511 to 43,102 bytes before any formatting or provenance-pointer overhead. This batch alone does not repair the nested commands-chain cap.

After selection, retire/capture the specific entries through CMS commands, compose against the current complete rendition, obtain advisory review, commit content and synchronize generated surfaces. Verify invariant floor, ownership/coverage, surface parity, and actual native delivery. A fresh generated baseline currently drops uncaptured material (#983); do not publish it as a shortcut.

The separate proposals that change judgment policy, including replacing the unbounded all-docs/all-code requirement, are not included in this batch.

## D09 — merge subject fence, purposes, and cooperation

Root lines 366–368; 2,734 → 764 bytes.

Source entries:

- `corpus-operator-doctrine-verbatim-canon-2026-08-17T11:20:29.341500+00:00` (invariant; Promotable)
- `corpus-operator-doctrine-verbatim-canon-2026-08-17T11:20:36.600648+00:00` (invariant; Promotable)
- `corpus-operator-doctrine-verbatim-canon-2026-08-17T11:55:49.945606+00:00` (invariant; Promotable)

Original:

```markdown
- Three distinct systems collide on the word 'handoff' in code and MUST NOT be conflated. Operator canon, verbatim: 'transit (how we enter and leave the designed ecosystem); exchange (noting block vacation and an observation report of what happened); handoff (synthetic memory refresh, from agent session to agent session, for context management). Three vital features, that, as it turns out, are vital for campaign success.' Each owns a different SUBJECT: transit is the ECOSYSTEM (airlock membrane, ADR-0.33.0); exchange is ONE BLOCK's occupancy (OBPI token, ADR-0.0.41); handoff is ONE SESSION (ADR-0.0.65). 'handoff' is critical ONLY to the session system — on the token side 'exchange' substitutes, and the token block system is the sole mechanism by which features are implemented (the airlock's Build door). Never infer system membership from a shared field name, path, or directory: the citing EVENT type is the discriminator.
- The airlock's purpose is FOUR things, operator verbatim (2026-08-17 architecture-review interview): 'an awareness and synthetic memory approach to keep an agent oriented about its actions within the system... control movement within the project when the agent enters that environment... keep the agent focused and oriented, watch for contamination, and monitor results/disturbance.' It is NOT a verification gate — that reading was raised by an agent review and OVERTURNED. Three of the four purposes appear NOWHERE in ADR-0.33.0: measured 2026-08-17 against the ADR body, 'orientation' 0, 'contamination' 0, 'awareness' 0, 'synthetic memory' 0 occurrences; the ADR names only prosthetic memory (4 occurrences) and the disturbance-monitoring arm. That absence is a CAPTURE GAP in the ADR, never a change of purpose — never cite ADR-0.33.0 as the complete statement of what the airlock is for, and never infer from its silence that a purpose was dropped.
- The airlock and the handoff COOPERATE to provide synthetic memory (operator, 2026-08-17); they are not merely fenced apart by subject. The three-system fence — transit is the ECOSYSTEM, exchange is ONE BLOCK's occupancy, handoff is ONE SESSION — states what must never be CONFLATED. It does not state what they do TOGETHER, so a reader who meets only the fence learns the separation and misses the join: transit orients an entering agent to the ecosystem's current shape, the handoff carries the prior session's model forward, and NEITHER ALONE gives an agent a resident model of the project. Cooperation is a REFINEMENT of the fence, never drift from it — the fence forbids inferring system membership from a shared name, and it never forbade the systems from serving one purpose. Designed at OBPI-0.37.0-05-session-entry-door.
```

Proposed replacement:

```markdown
- Keep three subjects distinct: transit is ecosystem movement through the airlock (ADR-0.33.0); exchange is one block’s occupancy (ADR-0.0.41); handoff is session memory (ADR-0.0.65). Classify by the citing event type, never a shared field name or path. Token blocks implement features through the airlock’s Build door. The airlock provides awareness and synthetic memory, controls project movement, keeps the agent focused and watches for contamination, and monitors results/disturbance; it is not a verification gate. ADR-0.33.0 incompletely captures those purposes; silence does not revoke them. Transit supplies current ecosystem orientation and handoff carries the prior session model; they cooperate, and neither alone supplies a resident project model.
```

## D10 — retain root-contract topology

Root lines 370–370; 1,141 → 313 bytes.

Source entries:

- `corpus-operator-doctrine-verbatim-canon-2026-08-17T21:46:58.710673+00:00` (invariant; Judgment)

Original:

```markdown
- AGENTS.md is the agent harness default and the ROOT contract (operator verbatim 2026-08-17: 'claude reads AGENTS.md too — the lite rendition serves both'; 'agents.md is more universal than stubborn anthropic. So, agents.md is the agent harness default.'). There is exactly ONE rendered AgentContract — root AGENTS.md — and the lite rendition serves EVERY harness, because it must fit the smallest vendor delivery cap. Per-vendor AgentContract renditions are FORBIDDEN: AgentContract may never carry multi-vendor routes or per-vendor temperatures in data/vendor-manifest.json. Vendor-specific material belongs in that vendor's own surface (.claude/rules/**), never in a second AGENTS.md. This is OLD GROUND, not a new ruling: docs/governance/agent-control-surface-rendering-substrate.md:211 has named the root vendor since authoring ('gz content render agent_contract --vendor=root'). It drifted to a per-consumer shape because the doctrine carried no mechanical witness and the same file's § Agent Orientation Index row — a Layer-3 description of the implementation — out-ranked the Layer-1 worked example three artifacts deep.
```

Proposed replacement:

```markdown
- Root AGENTS.md is the sole rendered AgentContract and the default for every harness, including Claude. Its lite rendition fits the smallest vendor delivery cap. Forbid per-vendor AgentContract routes or temperatures in data/vendor-manifest.json; vendor-specific material belongs in that vendor’s own surface.
```

## D14 — merge authorization and execution boundary

Root lines 375–376; 3,209 → 598 bytes.

Source entries:

- `corpus-operator-doctrine-verbatim-canon-2026-08-21T09:33:42.074142+00:00` (invariant; Mechanical)
- `corpus-operator-doctrine-verbatim-canon-2026-08-23T14:33:19.685636+00:00` (invariant; Judgment)

Original:

```markdown
- IRON LAW — ONLY THE OPERATOR INITIATES OBPI WORK. Operator verbatim (2026-08-23): 'NEVER, EVER, EVER, EVER DO OBPI WORK ON YOUR OWN. NEVER!'; 'OBPI WORK WILL NOW ONLY BE OPERATOR INITIATED WORK THAT I EXECUTE VIA THE SKILL.'; 'ONLY THE OPERATOR CAN INITIATE ANY OBPI WORK.'; 'NEVER START ANY OF IT ON YOUR OWN. NEVER'. The operator initiates AND executes OBPI work via the gz-obpi-pipeline skill. The agent never starts any part of it. This covers EVERY arm, not merely the pipeline run: claiming or releasing an OBPI lock, launching or clearing a pipeline marker, starting/completing/blocking TASKs, dispatching implementers or reviewers, and editing an OBPI brief. THIS SUPERSEDES THE PRIOR READING of 'NEVER work an OBPI without running it through the gz-obpi-pipeline skill' — that rule constrained HOW an agent works an OBPI and was fully satisfiable by an agent who started the work itself, which is precisely the loophole that produced the violation. An operator instruction naming a narrow task that happens to fall inside an OBPI's scope ('bind the @covers') is NOT initiation of OBPI work: do the narrow task by the direct path, or STOP and surface that it would require the OBPI machinery, then wait for the operator to initiate. Measured instance 2026-08-23: told to bind @covers decorators, an agent escalated that into a full pipeline run — plan-audit receipt, lock claim, pipeline marker, eight auto-started TASKs, implementer plus two-stage reviewer dispatch — then abandoned the lock and later completed and blocked those eight TASKs, none of it asked for. The residue blocked an unrelated push on a historical ledger row that append-only semantics forbid repairing. (Advisory — no mechanical witness distinguishes operator-initiated from agent-initiated OBPI work today.)
- NEVER work an OBPI without running it through the gz-obpi-pipeline skill (operator verbatim 2026-08-21: 'you are NEVER to work on an obpi without runnung the skill'; 'its because you worked on this obpi without invoking the skill, I came back using the skill' — spelling preserved). Invoking the skill and then running Stage 2 INLINE is the violation: the stages are not a checklist to narrate, the implementer dispatch and the two-stage spec-reviewer + quality-reviewer review ARE the work, and that review is what catches hollow tests and REQ coverage bound to the wrong subject. Measured cost of one violation: three tier-1 adversary passes found what one review pass should have — five covering tests that survived deliberately broken production behavior, and a root-contract fence asserting cardinality where doctrine required identity, so a coherent re-vendoring passed validation and all five fence tests. THE PROXIMATE CAUSE IS THE RULE'S REAL SUBJECT: a session-level harness instruction conflicted with a skill-mandated governance gate and the agent resolved it SILENTLY against the skill. A harness instruction NEVER licenses skipping a governed gate — surface the conflict to the operator (Behavior Rules — Always #9) and let them rule. Mechanically fenced by .claude/hooks/pipeline-gate.py, which refuses src/** writes once the pipeline marker's current_stage moves past 'implement'.
```

Proposed replacement:

```markdown
- Only the operator initiates and executes OBPI work through gz-obpi-pipeline. Never independently claim/release OBPI locks, create/clear pipeline markers, start/complete/block TASKs, dispatch OBPI implementers/reviewers, or edit briefs. A narrow task inside an OBPI scope is not OBPI initiation: do it directly, or stop if it requires the machinery. Once initiated, follow the skill’s implementer dispatch and spec-reviewer then quality-reviewer review; never substitute inline Stage 2. A harness instruction cannot excuse skipping a governed stage: surface the conflict for an operator ruling.
```
