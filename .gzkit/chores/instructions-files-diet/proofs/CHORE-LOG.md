# Chore Log — instructions-files-diet

## Run 1 — 2026-04-26 — Pass 1 (Option B)

- **Operator:** g0
- **Trigger:** `/gz-context-diet` skill invocation under GHI #327
- **Pass scope:** Lifts 1, 2, 4, 5, 6 (high-confidence subset). Lifts 3 and 7 deferred to Pass 2.
- **Acceptance result:** 4/5 PASS (lint, documents+surfaces, advisory-scorecard, mkdocs strict). 1 pre-existing FAIL (`uv run -m unittest -q`) — baseline failure unrelated to this chore.
- **Line-count delta:** 1801 → 1768 (−33 net). See `baseline-2026-04-26.txt` and `post-trim-2026-04-26.txt`.
- **Bullet-retention:** zero Mechanical/Promotable bullets removed; advisory-scorecard validates clean. See `bullet-retention-audit.md`.
- **Pointer discipline:** every lift left a `> See [...]` one-line pointer at the origin site.
- **Surfaces touched:**
  - `src/gzkit/templates/agents.md` (canonical AGENTS.md source — sync regenerates AGENTS.md from this template)
  - `.gzkit/rules/tests.md` (canonical rule — sync regenerates `.claude/rules/tests.md`)
  - `docs/governance/agent-contract-rationale.md` (extended with three lifted sections)
  - `docs/governance/operator-economy.md` (new)
  - `docs/governance/tests-rationale.md` (new)
- **Sync:** `uv run gz agent sync control-surfaces` clean; AGENTS.md and `.claude/rules/tests.md` regenerated from canonical sources.
