# Comparative sources

Primary or original sources inspected on 2026-08-23:

- Matt Pocock handoff skill:
  https://github.com/mattpocock/skills/blob/main/skills/productivity/handoff/SKILL.md
- Matt Pocock phase-boundary model:
  https://github.com/mattpocock/skills/blob/main/skills/engineering/ask-matt/PHASE-BOUNDARIES.md
- Proposed verification discipline for Matt Pocock's handoff:
  https://github.com/mattpocock/skills/issues/306
- LangGraph persistence and checkpointing:
  https://docs.langchain.com/oss/python/langgraph/persistence
- Claude Code project and auto memory:
  https://code.claude.com/docs/en/memory
- Cursor repository-scoped memories:
  https://docs.cursor.com/en/context/memories
- Aider repository map:
  https://aider.chat/docs/repomap.html
- Cline Memory Bank source:
  https://github.com/cline/prompts/blob/main/.clinerules/memory-bank.md
- Handoff Debt research:
  https://arxiv.org/abs/2606.02875
- Superpowers plan-aware session handoff proposal:
  https://github.com/obra/superpowers/issues/931
- Superpowers chain-of-handoffs proposal:
  https://github.com/obra/superpowers/issues/2153

Comparative conclusion:

gzkit is the strongest complete repository-governed handoff implementation in
this examined set. LangGraph has a narrower but material advantage in exact,
transactional runtime checkpointing, pending-write recovery, replay, and forks.
Matt Pocock has a narrower advantage in minimal portability, explicit targeting
to the incoming session, and phase-boundary choice. Claude/Cursor have a
narrower advantage in automatic loading or extraction. Aider has a narrower
advantage in automatic code-topology reconstruction. None combines those
narrow advantages with gzkit's lineage, governance, decision attribution,
issue awareness, exit bookmarks, archive protections, and extensive regression
suite.
