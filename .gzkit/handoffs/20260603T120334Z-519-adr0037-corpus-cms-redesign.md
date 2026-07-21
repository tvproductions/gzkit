---
mode: CREATE
adr_id: ADR-0.0.37
branch: main
timestamp: "2026-06-03T12:03:34Z"
agent: claude-code
---

<!-- Frontmatter added under GHI #709. This handoff predates the YAML
     frontmatter convention; its metadata lived in the bold body lines and
     the filename, so the validator that governs it could not parse it.
     Every field below is derived from this document or its filename —
     `adr_id` is omitted where the parent is not named, which is legal now.
     Body content is unchanged. -->

# Session Handoff — 2026-06-03T12:03:34Z

**Topic:** ADR-0.0.37 density-dial REDESIGN (corpus → setpoint-compression → invariant tier) + #519 re-anchor
**Author session:** main-session (claude-code, sonnet-4-6)
**Freshness:** Fresh
**A handoff ADVISES; it does not authorize.** Present the advised next steps and obtain explicit operator authorization before executing any of them.

## What happened this session

Started as `/gz-plan-audit OBPI-0.0.37-17` → pre-flight blocked twice, escalated into a full design realignment with the operator. Net outcome: the ADR-0.0.37 density-dial design was **redesigned and re-booked**; OBPI-17-as-scoped is retired; #519 relief re-routed.

**Findings that forced the redesign (empirical, verified):**
1. The render template `src/gzkit/content/templates/agentcontract/claude.md.j2` emits `pillar.lines | join` **verbatim**; every parsed `Bullet.density_min=None`. So the OBPI-11/12 dial is **inert** — `render(lite)==render(medium)==render(heavy)` byte-for-byte.
2. OBPI-17-as-scoped (thin by **dropping whole sections**) collides with **ADR-0.0.33 `bullet-retention`** (in the default `gz check` "Surface fidelity" scope) — max retention-safe section-drop floors the committed root at **~29,885 B** (no real headroom vs the 30,000 budget / 32,768 cap).
3. `# Local Agent Rules` is an **H1** the parser glues into the `Control Surfaces` pillar — dropping Control Surfaces loses Mechanical bullets.

**The operator's corrected, authoritative design (now booked):** append-only **corpus** (source of truth; "remember X" appends, never hand-edits rendered surfaces — like harness user-memories) → **temperature = compression setpoint** per (surface×consumer) → **authoring-time agent compression** (drop/combine/rewrite toward target; advisor-QC'd per ADR-0.0.39; operator-attested) → **committed rendition** → **deterministic playback** (no LLM in render path) + an **invariant tier** (PRIME DIRECTIVE / DO IT RIGHT / NEVER PYTEST — verbatim, never condensed). Sections are **template-defined**, Pydantic enforces conformance. Each capability ships as **tool(s) + wielding skill** (SKILLS-FIRST). Recompose: build-time freshness gate (fail-closed on corpus↔rendition drift) + on-demand compose skill + a chore cadence wrapper; Gate 5 stays human.

## Current state (booked, validated, NOT built)

- **ADR-0.0.37** (`Draft`, amended in place): new **§ Decision Re-Alignment (2026-06-03)** (supersedes the 2026-05-30 density-dial *mechanism*; CIC-1/CIC-2 invariants unchanged); **Checklist re-decomposed 11→20** (each = tool+skill); Scorecard Baseline 12→16 (Final 20); **6 new rejected alternatives**. `uv run gz validate --documents` → PASS.
- **ADR-0.0.33** (`Validated`): new **§ Amendment (2026-06-03)** — Invariant 1 `bullet-retention` is **tier-scoped** (verbatim at invariant tier; advisor-QC receipt + attestation at compressed tiers). Coupled to **OBPI-0.0.37-18**; **attested at that OBPI's Gate 5** (until then original Era-1 contract holds).
- **OBPI-0.0.37-17 brief**: carries an earlier Step-0 amendment (compose.py + vendor-manifest.json scope; REQ-05 baseline; REQ-07 rationale) — now subordinate; 17-as-scoped is retired by the redesign.
- **OBPI-0.0.37-17** was `obpi_created` (via `gz register-adrs ADR-0.0.37`), lock claimed then **released**; pipeline markers cleared. Decision record: `.gzkit/insights/agent-insights.jsonl` `ts=2026-06-03T11:32:52Z`.
- `AGENTS.md` is **unchanged** (probe edits were restored via `git checkout`).

## Known drift (expected — resolved by next step)

ADR-0.0.37 Checklist now reads 11–20 (new meanings) but on-disk brief files are still 11–17 (old). **`gz-obpi-specify` reconciles the brief files** to the new checklist (rewrite 11/12; re-home 13/14 substrate; retire 15/17-as-scoped; add 16–20), restoring the 1:1 mandate.

## Advised next steps (operator authorizes)

1. **Review** the two amended ADRs (`ADR-0.0.37` § Decision Re-Alignment + Checklist; `ADR-0.0.33` § Amendment).
2. **`gz-adr-evaluate ADR-0.0.37`** (gz-design Step 6 quality gate; revise any dimension scoring 1).
3. **`gz-obpi-specify`** to reconcile brief files 11–20 to the new checklist.
4. **Build OBPI-0.0.37-19 FIRST** (#519 Codex-root setpoint + interim operator-attested compressed rendition) so the emergency is not stranded behind the full ~10-OBPI build.
5. Disposition: re-home 11/13/14 substrate; retire 15 and 17-as-scoped; couple OBPI-18 (tier-scoped retention validator) with the ADR-0.0.33 amendment attestation.

## Blockers

- **#519 remains OPEN** — design booked, not built. The relief path is now OBPI-0.0.37-19 (not a section-drop).
- The pre-existing OBPI-09 superseded-but-pending disposition (registry-path migration) is untouched here; route separately at ADR-0.0.37 closeout.

## Verification at handoff

- `uv run gz validate --documents` → PASS.
- `AGENTS.md` byte-unchanged (`git diff --stat AGENTS.md` empty).
- Pending git-sync of the docs/governance change set (ADR-0.0.37, ADR-0.0.33, OBPI-17 brief, return-to-health Snapshot G, insight, ledger, adr-status, plan file).
