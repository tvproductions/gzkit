---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-29T17:32:44Z'
agent: claude-code
continues_from: 20260829T132918Z-repo-deletion-recovery-v0347.md
---

## Current State Summary

Instruction-surface cleansing session under GHI #921. Three commits landed: 5c042f64 (settings.local.json backup hook), c3d527fe (relocating that hook out of .claude/hooks so `gz agent sync` stops stripping it), and 1c547c64 (governance-core.md cleansed 16,885 -> 8,324 B with a genuine re-score). GHI #921 was filed and cross-linked to sibling #815.

Uncommitted and gates-green: a changelog lift across 17 canonical rules removing 29,259 B (13.3%) from `.gzkit/rules/`, proven content-neutral by diff (only version-marker and rule-version blockquote lines changed). `gz validate --bullet-retention --pointer-anchors --surfaces --rule-version-markers` exits 0. `gz validate --advisory-scorecard` correctly exits 1 with 15 errors: 12 ledger rules bumped past their scored version and 3 grandfathered rules that lost their pin. Those 15 re-scores are the outstanding work on this branch.

Root cause of "rules are not CMS-governed" was found and is small: `data/vendor-manifest.json` `surface_content_types` declares only `AGENTS.md`, and `src/gzkit/content/composer.py:30` hardcodes `content_type: str = "AgentContract"` without ever calling `content_type_for_surface`. The `Rule` content type, its `claude: heavy` temperature, the corpus store and the rule template all already exist and work.

## Important Context

Measured surface, corrected during the session. True always-loaded per-turn context is 57,808 B: root AGENTS.md 46,876 + CLAUDE.md 2,554 + governance-core.md 8,378. Only governance-core.md is scoped `paths: "**/*"`; the other 25 rules load on path match. Nested AGENTS.md total 324,372 B across 23 distinct authored files. Skills are 608,523 B across 70 files and are on-demand, so they are out of scope by operator ruling.

Nested AGENTS.md are NOT loaded by Claude Code. Proven empirically this session: a Read of `src/gzkit/config.py` loaded six `.claude/rules/*.md` files whose `paths:` frontmatter matches `src/**`, and did NOT load `src/gzkit/AGENTS.md` (23,242 B, same directory). Root AGENTS.md reaches Claude only because CLAUDE.md contains an `@AGENTS.md` import. The mechanism Claude honors for directory-scoped instruction is `.claude/rules/*.md` with `paths:` frontmatter. This makes 277,496 B across 22 nested AGENTS.md inert for Claude while remaining live for Codex, which reads AGENTS.md natively.

Two hard constraints govern any further compression. First, `--bullet-retention` pins Mechanical-class scorecard bullets VERBATIM (ADR-0.0.33 Invariant 1): dropping the single word "appearing" from a governance-core bullet failed the gate at exit 3. Second, `advisory_scorecard` fails closed when a rule bumps past its Coverage Ledger version, so bump and re-score must land in the same commit.

The vendor manifest already encodes Claude-first: `content_type_routes` sends every content type to `claude` alone, with AgentContract to `root`. Nothing routes to copilot. `.gzkit.json` carries no `vendors` key, so `copilot.enabled` and `codex.enabled` are both False by default, yet every vendor tree is written anyway because `vendor_aware = _has_manifest_vendors(project_root)` is False and each sync branch reads `if not vendor_aware or config.vendors.<x>.enabled`.

## Decisions Made

- [operator-ruled] gzkit is a Claude-first apparatus that uses Codex strategically for adversarial review (verbatim: "we are supporting claude and codex - that's it"). Copilot support is to be dropped; anything beyond the Claude/Codex core is abandoned to save time and energy.
- [operator-ruled] There can be only one root AGENTS.md (verbatim: "I agree that there can only be one"), settling the question of what content type the 22 nested AGENTS.md map to. They are not AgentContract renditions.
- [operator-ruled] Everything the agent consumes at context load must be corpus-governed and rendered, never hand-edited (verbatim: "we are not to make direct edits, the cms / corpus system is the rule"). Scope is the context-loaded tier: AGENTS.md family, rules, CLAUDE.md. Skills are excluded because they are operator-driven and load on demand.
- [operator-ruled] Nothing stays grandfathered (verbatim: "nothing should be grandfathered, all require the new cleansing treatment/process"). All 25 audited rules take a real score, emptying data/advisory_scorecard_grandfather.json.
- [operator-ruled] Bump and re-score rather than lift silently, because changing language warrants re-review.
- [operator-ruled] Size and trim gates come out of `gz check`; correctness fences stay. Removed: surface_weight, surface_delivery_witness, instructions_files_budget. Retained: bullet_retention, rendition_floor_coherence, invariant_coherence, agents_md_map_conformance criteria (a), (b), (c).
- [operator-ruled] The instructions-files-diet chore becomes the load-bearing, operator-owned surface that holds trim targets and attends to overages, rather than a per-turn gate (verbatim: "If we gate this per turn, we introduce too much friction").
- [operator-ruled] Trim targets stay in data/instructions_files_budget.json as the JSON authority, restructured from per-file numbers to per-tier targets.
- [operator-ruled] This work is not new ADR work; it is a GHI (verbatim: "This is not new ADR work, associate it with a GHI and do the work"), which produced GHI #921.
- [operator-ruled] The corpus-ownership half of GHI #921 routes to ADR-0.35.0, extended by the operator, rather than to a fresh ADR (verbatim: "if 0.35.0 owns this, then we'll want to adjust/extend it to accommodate my new design instructions").
- [agent-chose] Lifted version chains to docs/governance/rule-version-history.md and bullet narrative to a new docs/governance/governance-core-rationale.md, following the established rule-rationale.md convention rather than inventing a new home.
- [agent-chose] Ran a mechanical content-neutrality proof after each lift. The first attempt sliced from the rule-version blockquote to the next heading, which silently deleted 24 lines from mx-mode.md and content from six other rules; the proof caught it and the whole lift was reverted and redone against contiguous blockquote lines only.
- [agent-chose] Did not seed corpora for the remaining rules, because compose cannot yet address a non-AgentContract surface and a corpus nothing renders from would be a second source of truth.

## Immediate Next Steps

1. Rule on the composer/manifest defect routing. `data/vendor-manifest.json` needs `surface_content_types` entries for every context-bearing surface, and `src/gzkit/content/composer.py` must call `content_type_for_surface(surface)` instead of defaulting `content_type` to "AgentContract". Roughly three source lines plus data. It is direct-fix sized under GHI #921, but it changes a runtime contract, which the routing table sends to ceremony. Operator decides which.
2. Run the design spike on nested instructions (see Pending Work). Nothing else in the corpus onboarding can be sequenced until it is settled, because it decides what the 22 nested AGENTS.md become.
3. Complete the 15 outstanding re-scores so `gz validate --advisory-scorecard` returns to exit 0, then commit the 17-rule changelog lift. The lift is content-neutral and gates-green; only the scorecard blocks it.
4. Decide the fate of the single probe corpus entry at `.gzkit/corpus/.gzkit/rules/governance-core.md.jsonl`. It is correct and provenanced but is one entry of roughly fifteen that rule needs, and compose would validate a candidate against that partial set.
5. Drop Copilot. Add a `vendors` block to `.gzkit.json` enabling claude and codex only, confirm `_has_manifest_vendors` then makes `vendor_aware` True, and remove `.github/skills`, `.github/instructions`, `.github/personas` and `.github/AGENTS.md` — 971,876 B across 273 files. `.agents/` is retained because it is Codex's surface root.

## Pending Work / Open Loops

DESIGN SPIKE REQUIRED — what to do about nested instructions. This is the largest open question and it blocks the corpus onboarding.

The finding: nested AGENTS.md files are not loaded by Claude Code, proven this session by a Read of `src/gzkit/config.py` that pulled six path-scoped `.claude/rules/*.md` files and did not pull `src/gzkit/AGENTS.md` from the same directory. That leaves 277,496 B across 22 files authored, synced, mirrored four times, and never read by the primary harness. They remain live for Codex, which reads AGENTS.md natively.

Questions the spike must settle:
- Do nested AGENTS.md become path-scoped `.claude/rules/*.md` renditions for Claude while remaining AGENTS.md renditions for Codex, from one shared corpus per scope? That is the shape the CMS naturally supports and it would make the two harnesses provably agree, where today they are two hand-maintained bodies of text that can silently diverge.
- If so, what content type owns a directory-scoped agent doc? It cannot be AgentContract, because canon holds there is exactly one rendered AgentContract and per-vendor AgentContract renditions are forbidden. A new type, or a reuse of Rule with a `paths:` value drawn from the directory.
- Which of the 22 nested files earn survival at all? Several are large enough to be suspect on their own terms: tests/AGENTS.md 32,578 B, docs/design/adr/AGENTS.md 29,130 B, src/gzkit/AGENTS.md 23,242 B.
- What prevents regrowth? No gate today counts corpora against surfaces, so the twenty-second ungoverned file is exactly as invisible as the second.

Other open loops:
- 15 rule re-scores outstanding; `gz validate --advisory-scorecard` exits 1 until they land.
- 3 rules lose their grandfather pin and need real first scores: model-selection.md, security-sensitivity.md, skill-surface-sync.md. `data/advisory_scorecard_grandfather.json` should reach zero entries when the pass completes.
- The advisory scorecard's own prose reads "The remaining 23 canonical rules" where the true grandfathered count is 12, and `baseline_count: 23` in the JSON is stale with it.
- The retired "<90% sure" framing still renders at AGENTS.md line 123 while line 363 records the operator superseding it. Both entries are live in the corpus; the superseding entry never retired the superseded one. Retiring it touches `.gzkit/corpus/AGENTS.md.jsonl`, which is in the allowlist of OBPI-0.35.0-03 (status Active), so it is operator-initiated work.
- Gate 5 and human attestation are restated ten times in root AGENTS.md.
- `.claude/settings.local.json` was lost with the repo and is unrecoverable. It was reconstructed from 203 transcripts as 24 allow rules and is now snapshotted outside the repo on SessionStart and Stop.

## Verification Checklist

Run these before trusting any claim in this handoff.

uv run gz validate --bullet-retention --pointer-anchors --surfaces --rule-version-markers
  Expect exit 0. This is the gate set the uncommitted 17-rule lift already passes.

uv run gz validate --advisory-scorecard
  Expect exit 1 with 15 errors until the re-scores land. Anything else means the tree moved.

git log --oneline -4
  Expect 1c547c64, c3d527fe, 5c042f64 at the top of main.

git status --short
  Expect roughly 92 modified paths: 17 canonical rules plus their three generated mirror families, and the appended ledger.

gh issue view 921 --json state,title
  Expect OPEN. Confirms the work order still stands.

uv run gz agent sync control-surfaces
  Expect exit 0 and no divergent mirrors. Run after any canonical rule edit.

python3 -c "import json; print(json.load(open('data/vendor-manifest.json'))['surface_content_types'])"
  Expect a single entry mapping AGENTS.md to AgentContract. That one line is the registry gap.

Verify the nested-AGENTS.md finding by using the Read tool on any file under src/gzkit and observing which instruction files load. Bash reads do not trigger directory-scoped memory, so the Read tool is required to reproduce it.

## Evidence / Artifacts

Committed this session:
- `scripts/settings_local_backup.py` — settings.local.json snapshot hook, relocated from .claude/hooks so sync preserves its registration
- `.claude/settings.json` — SessionStart and Stop registrations for that hook
- `docs/governance/governance-core-rationale.md` — new expansion doc carrying governance-core's lifted worked examples
- `docs/governance/rule-version-history.md` — lifted version chains
- `docs/governance/advisory-rules-audit.md` — Coverage Ledger row for governance-core moved to 0.14.0, plus the re-score record

Uncommitted, gates-green:
- `.gzkit/rules/` — 17 canonical rules carrying the changelog lift, 29,259 B removed

Probe artifact, disposition undecided:
- `.gzkit/corpus/` — now holds a second store beside AGENTS.md.jsonl, keyed under a nested .gzkit/rules path for governance-core, carrying one entry that proves rule surfaces are capturable

Defect sites for the composer fix:
- `data/vendor-manifest.json` — surface_content_types declares only AGENTS.md
- `src/gzkit/content/composer.py` — content_type defaults to AgentContract and content_type_for_surface is never called

Governance:
- GHI #921 — the work order, cross-linked to sibling #815

## Settled Rulings

593 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
