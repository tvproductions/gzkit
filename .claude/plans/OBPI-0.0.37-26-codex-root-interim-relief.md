# Plan — OBPI-0.0.37-26 Codex-root setpoint application + interim attested relief

**OBPI:** `OBPI-0.0.37-26-codex-root-setpoint-application-interim-attested-relief`
**Parent ADR:** `ADR-0.0.37-constitutional-invariant-composition`
**Lane:** Heavy · **Emergency:** GHI #519 (Codex 258K-window context exhaustion)

## Context

`uv run gz check` is RED on `main`: rendered root `AGENTS.md` is 32,651 B / 32,483
chars, over the 30,000 budget (`data/instructions_files_budget.json`) and ~117 B
under Codex's 32,768 B `project_doc_max_bytes` truncation cliff. Three failing
tests (`test_agents_md_and_claude_md_fit_budget_and_codex_cap`,
`test_budget_enforces_codex_cap_and_files_fit`, `test_happy_path_against_lifted_agents_md`)
plus `--instructions-files-budget` and `--agents_md_map_conformance` all trace to
this single overrun. The budget was tightened to 30,000 by this OBPI's checklist
item but the compressing half never landed (lock claimed then released mid-flight),
leaving a half-applied OBPI parking `main` red.

`AGENTS.md` is **rendered**: `render_agents_md` reads `.gzkit/templates/agents.md`
(23,403 B) and substitutes `{local_content}` ← `load_local_content('.gzkit/agents.local.md')`
(9,306 B). Empirical experiment (splice stubbed → rendered → measured): template
alone renders to **23,400 B**, leaving **6,600 B** of headroom for the splice under
the 30,000 budget.

`uv run gz validate --bullet-retention` against the stubbed render named exactly
**18** Mechanical/Promotable scorecard bullets that exist *only* in the splice.
The retention validator (`bullet_retention.py`) matches the **scorecard phrase**
(`advisory-rules-audit.md` col-2) as a normalized substring across the corpus
(`AGENTS.md` + `CLAUDE.md` + `.claude/rules/**`) — so each of the 18 needs only its
short phrase verbatim (~921 B raw / ~1,371 B with scaffolding), not the paragraph
of elaboration the splice currently carries.

## Files (all within brief Allowed Paths)

- `.gzkit/agents.local.md` — **compress** 9,306 B → ≤6,500 B (the only in-scope lever)
- `AGENTS.md` — **regenerated output** of `gz governance render --target agents-md`
- `data/instructions_files_budget.json` — confirm `files["AGENTS.md"] == 30000` (REQ-02)
- `data/vendor-manifest.json` — confirm `content_type_temperatures.AgentContract.codex == "lite"` (REQ-03)
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/renditions/agentcontract-codex-root-interim.md` — interim committed-rendition artifact (REQ-04)
- the brief — evidence sections

## Steps

1. **Compress `.gzkit/agents.local.md`** keeping retention green under the *current*
   whole-surface validator:
   - Keep all 18 retention-critical scorecard phrases verbatim, compressed to a
     terse skeleton (phrase + ADR/GHI citation), shedding multi-sentence elaboration.
   - Keep genuinely-binding non-scorecard directives in compressed form: Operator-PII
     core, DIRECT-FIX MORATORIUM core, import-in-same-edit, foundation nominal-id
     counter-rule, semver-ordering, attestation-enrichment pointer.
   - Drop elaboration that merely duplicates the scorecard or docs/governance pages.
   - Target source ≤6,500 B (verification line 143).
2. **Re-render** `uv run gz governance render --target agents-md`; confirm
   `wc -c AGENTS.md` ≤ 30,000 with headroom.
3. **REQ-02** — confirm `data/instructions_files_budget.json` `files["AGENTS.md"]` ≤ 30,000
   (already 30,000; no edit expected).
4. **REQ-03** — confirm `data/vendor-manifest.json` declares the lean
   `AgentContract.codex` setpoint (`lite`; already present; no edit expected).
5. **REQ-04** — update the interim rendition artifact
   `renditions/agentcontract-codex-root-interim.md` so it captures the committed
   relief payload (the compressed splice / rendered-root snapshot) for OBPI-21/22
   regeneration.
6. **Verify** invariant-coherence, instructions-files-budget, bullet-retention,
   surface-fidelity, documents, brief-reconcile, and full `gz check` all green.

## Verification

```bash
uv run gz validate --documents
uv run gz validate --vendor-manifest
uv run gz validate --instructions-files-budget
uv run gz validate --invariant-coherence
uv run gz validate --bullet-retention
uv run gz validate --surface-fidelity
uv run python -c "from pathlib import Path; s=Path('AGENTS.md').stat().st_size; assert s<=30000, s; print(s)"
uv run python -c "from pathlib import Path; s=Path('.gzkit/agents.local.md').stat().st_size; assert s<=6500, s; print(s)"
test -f docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/renditions/agentcontract-codex-root-interim.md
uv run gz obpi precomplete OBPI-0.0.37-26-codex-root-setpoint-application-interim-attested-relief
uv run gz check
```

## Notes

- **No scope expansion, no OBPI-25 dependency.** Proven empirically: the 18
  retention-critical bullets fit ~1,371 B of the 6,600 B headroom, leaving ~5,200 B
  for terse binding directives. OBPI-26 survives the *current* whole-surface
  retention validator — which is exactly why ADR-0.0.37 §Decision sequenced #26
  FIRST "so the emergency is not stranded."
- All REQs are SUPPORT-kind → proof channel is `artifact_edited` ledger event +
  structural validator, not `@covers` tests. The pre-existing budget tests turn
  green once AGENTS.md fits.
- **Step-6a disclosure.** Destination-in-mind: local-splice compression keeping
  verbatim retention phrases. Rejected: budget→32,768 (truncation-cliff paper-green),
  budget→33,000 (fails cap-invariant test), re-home into `.claude/rules` (out of
  Allowed Paths), land OBPI-25 first (larger; sequenced after #26).
- Render mechanism confirmed by stub experiment (edit splice → `gz governance render`
  → AGENTS.md changed); reverted clean before this plan.
