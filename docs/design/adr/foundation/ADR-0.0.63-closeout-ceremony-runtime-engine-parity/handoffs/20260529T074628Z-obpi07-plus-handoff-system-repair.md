---
mode: CREATE
adr_id: ADR-0.0.63
branch: main
timestamp: "2026-05-29T07:46:28Z"
agent: claude-code
obpi_id: OBPI-0.0.63-07
session_id: salvation-phase-i-adr-0.0.63
continues_from: 20260529T071016Z-obpi07-done-obpi01-next.md
---

<!-- Token-block register fields (HandoffFrontmatter forbids them as keys; kept in body per
     token-block-discipline § Register-Entry Minimum-Information Rule "in frontmatter or body"):
     last lock-event timestamp: 2026-05-29T06:23:53Z (OBPI-0.0.63-07 lock claim, since released) ;
     last commit SHA at handoff: 06b9cd80 ; branch state: main, synced with origin/main. -->

## ADR / OBPI (full identifiers)

- Parent ADR package: `ADR-0.0.63-closeout-ceremony-runtime-engine-parity`
- This OBPI: `OBPI-0.0.63-07-verify-stage-command-shape-gate` (Completed)

## Current State Summary

Supersedes `20260529T071016Z-obpi07-done-obpi01-next.md` as the current state. Two
threads ran this session: the **ADR-0.0.63 thread** (OBPI-0.0.63-07 landed) and a
**handoff-system repair side-quest** (operator-initiated after observing the handoff
machinery was half-wired). Both are at clean checkpoints; tree synced with origin.

ADR-0.0.63 thread:
- **OBPI-0.0.63-07 (verify-stage-command-shape-gate): COMPLETE — attested, synced.** ADR-0.0.63 is **2/7**. Details in the chained predecessor handoff.

Handoff-system repair side-quest (all committed + pushed):
- **Orientation reader fixed** (commit `2ab33914`, `fix(orientation): … (GHI #529)`): `collect_handoff` now unions `.gzkit/handoffs/` + every `{ADR-package}/handoffs/` (newest-by-frontmatter-timestamp wins) and filters to files carrying `adr_id` frontmatter, so non-handoff `.md` (e.g. the generated `.gzkit/handoffs/AGENTS.md`) can never be surfaced as "the most-recent handoff". 3 new tests; 21/21 orientation tests pass.
- **Both ADR-0.0.63 handoff frontmatters corrected** to the short canonical `adr_id: ADR-0.0.63` / `obpi_id: OBPI-0.0.63-07` forms the `HandoffFrontmatter` model requires (they previously used the full package slug and failed `validate_handoff_document`).
- **Pool ADR authored + registered**: `ADR-pool.handoff-system-consolidation` (visible in `gz adr report` Pool table) — captures the full handoff-system scope.
- **GHI #529 closed `superseded`** citing the pool ADR + commit `2ab33914`.
- **GHI #565 filed** (unrelated to handoffs): 40 pre-existing brief `## Verification` compound-command violations the OBPI-07 gate surfaces.

Last action succeeded: `gz git-sync --apply` reported `dirty=False`, tree synced.

## Important Context

- **SKILL DISCIPLINE (operator correction, twice).** Invoke skills via the Skill tool; reading/replicating a SKILL.md by hand is NOT using the skill. This session's handoff was first hand-authored (caught by the operator) — routing it through `validate_handoff_document` immediately exposed invalid frontmatter. Logged in `agent-insights.jsonl` (scope `skill-invocation-discipline`). Pre-action gate: when a task maps to a skill, the first action is `Skill(<name>)`.
- **Handoff-system doctrine conflict is UNRESOLVED (deliberately).** `.gzkit/handoffs/` (token-block / OBPI-0.0.41-03) vs `{ADR-package}/handoffs/` (gz-session-handoff skill) are both declared canonical. The orientation union-scan is forward-compatible with either; the decision is a `foundation`-shaping choice deferred to `ADR-pool.handoff-system-consolidation` promotion. Do NOT pick one unilaterally.
- **gz-session-handoff programmatic API is vaporware.** `create_handoff`/`scaffold_handoff`/`list_handoffs`/`resume_handoff`/`load_handoff_chain` are documented at `tests.governance.test_session_handoff` but that module does not exist. Only `src/gzkit/handoff_validation.py::validate_handoff_document` is backed by code — use it to gate any hand-authored handoff. Building the real API is OBPI-02 of the pool ADR.
- **All OBPI-07 Important Context still applies** — see chained predecessor for: BI-1 spine reuse, `--brief-command-shape` is opt-in (not default `gz check`), Demo sections must be exit-0 for closeout binding, `--attestor-present` + `--from=sync` mechanics, pre-commit src/tests with `Task:` trailer, OBPI-06 `req_evidence` schema blocker.

## Decisions Made

- **Decision:** Route the remaining handoff-system work to a POOL ADR, not a direct fix or active ADR. **Rationale:** architectural absence + unresolved doctrine conflict; ghi-author doctrine routes such findings to a registered pool ADR. **Alternatives rejected:** leave union-scan as terminal (masks the conflict); active foundation ADR now (operator chose pool/backlog).
- **Decision:** Close GHI #529 `superseded` rather than leave it open. **Rationale:** pool ADR is a registered destination; a GHI is observation-routing, not an implementation tracker (ghi-close doctrine). **Alternative rejected:** keep open until the system ships (shadow-tracker anti-pattern).
- **Decision:** Fix the orientation reader as a direct fix (commit `2ab33914`), not via the pool ADR. **Rationale:** the reader bug (≤2 files, in-flight, 300 `fix(` precedents) is a bounded defect; the union-scan is doctrine-neutral. **Alternative rejected:** bundle into the pool ADR (over-ceremony for a 2-file fix).

## Immediate Next Steps

1. **OBPI-0.0.63-01 (step-advance-gate-5-enforcement)** — the ADR-0.0.63 thread's next unit. Owns `closeout_ceremony.py` (state machine, BI-3 anchor); wire OBPI-02's demo-receipt binding here. Run `/gz-plan-audit OBPI-0.0.63-01` then the `gz-obpi-pipeline` skill.
2. **Then in order:** 03 (proof-binding) → 05 (dual-runtime collapse) → 06 (req-evidence schema — resolve blocker) → 04 (wording fix) → `gz-adr-closeout-ceremony` for ADR-0.0.63.
3. **Before each Stage 5:** pre-commit src/tests with a `Task:` trailer, then complete via `gz obpi pipeline <id> --from=sync --attestor "g0" --evidence-json '<json with accept_uncovered for non-BEHAVIOR REQs>'`.
4. **Audit each remaining OBPI `## Demo`** for exit-0 closeout-binding safety before ADR closeout.

## Pending Work / Open Loops

- **5 OBPIs remain in ADR-0.0.63:** 01, 03, 05, 06 (blocked on `req_evidence` schema), 04.
- **`ADR-pool.handoff-system-consolidation`** — parked backlog. Promotion decides the canonical handoff location, builds the real programmatic API, adds the `gz handoff` CLI verb, aligns the orientation reader. Provisional 4-OBPI plan in the ADR's Notes.
- **GHI #565** — 40 pre-existing brief Verification compound commands; precondition for promoting `--brief-command-shape` to default `gz check`.
- **Pre-existing repo-wide `gz check` failure (NOT this ADR):** GHI #561 (`ADR-0.0.64` `REQ-0.0.64-05-06` lacks a `gz validate --<scope>` citation → `--req-kind-discipline` fails). Will block ADR-0.0.63 closeout's quality pipeline; needs the 0.0.64 owner. Do NOT blind-fix.
- **GHIs to close at ADR-0.0.63 closeout:** #539, #540 (OBPI-02), #550 (verify the OBPI-07 authoring-gate close satisfies it), #516 (relabel/close per OBPI-01/03).
- **`_extract_gz_verb_chain` positional-capture demo-loss bug** — tracked in `agent-insights.jsonl`; route at closeout.

## Verification Checklist

- [ ] `git branch --show-current` returns `main`; tree clean
- [ ] `uv run gz adr status ADR-0.0.63-closeout-ceremony-runtime-engine-parity` shows 02 + 07 `attested_completed`, others `pending`/`draft`
- [ ] `uv run python scripts/session_orientation.py` "Most-recent handoff" resolves to a real handoff (not `AGENTS.md`)
- [ ] `uv run -m unittest tests.scripts.test_session_orientation` → 21 pass
- [ ] `uv run gz adr report` shows `ADR-pool.handoff-system-consolidation` in the Pool table
- [ ] `gh issue view 529` is closed (superseded); `gh issue view 565` is open
- [ ] `python -c "from gzkit.handoff_validation import validate_handoff_document"` imports cleanly

## Evidence / Artifacts

- `scripts/session_orientation.py` — `collect_handoff` union-scan + `_looks_like_handoff` filter (commit `2ab33914`)
- `tests/scripts/test_session_orientation.py` — 3 new tests (exclusion, ADR-package discovery, union)
- `docs/design/adr/pool/ADR-pool.handoff-system-consolidation.md` — handoff-system pool ADR
- `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/handoffs/20260529T071016Z-obpi07-done-obpi01-next.md` — chained predecessor (OBPI-07 detail)
- `.gzkit/insights/agent-insights.jsonl` — `skill-invocation-discipline` improvement + OBPI-07 40-violation finding
- Commits this session: `6b85ebbc` (OBPI-07 code), `2ab33914` (orientation fix); pool ADR + GHI-close synced via `gz git-sync` ceremony commits through `06b9cd80`
- GHIs: #529 closed superseded → ADR-pool.handoff-system-consolidation (path above); #565 filed (brief-command-shape debt)

## Environment State

Python 3.13 / uv. Model: Opus 4.8. No feature branch — work lands on `main` via `gz git-sync`.
