---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-02T11:34:38Z'
agent: claude-code
continues_from: .gzkit/handoffs/20260902T071330Z-handoff-refresh-no-obpi-brief-touched.md
---

## Current State Summary

Intake review of the Anthropic AI-native SDLC playbook (`/Users/jeff/Downloads/REPORT-ai-native-sdlc-playbook-intake-2026-09-02.md`), then five commits of resulting repair. No OBPI work initiated at any point; no lock claimed, no pipeline marker touched. Tree clean at `344f7189`, pushed to origin/main. Landed this session: `1fe47be9` comparison-doc change-isolation row (GHI #937, closed); `61b474c0` coupled amendment adding control bands to ADR-pool.afk-diagnosis-cloud-routines and a named consumer + two-provenance correction to ADR-pool.session-productivity-metrics; `80fa6abc` .claude/settings.json hardening (deny list 6 -> 42, disableBypassPermissionsMode); `6ed5c9bd` config-paths audit now credits declared PathConfig defaults (GHI #938, sub-shape (a) only, gate still red at 7 findings); `344f7189` project_doc_max_bytes set to 65536 so the agent contract reaches Codex (GHI #815). Full suite 9166 tests OK.

## Important Context

THE HEADLINE FINDING: Codex's project_doc_max_bytes is a SETTING, not a vendor limit. At its 32768 default, AGENTS.md (46,876 B) lost 14,108 B — 30% of the contract — to silent truncation, including the IRON LAW (byte 40,734), ascending-semver ADR order (39,330), the transit/exchange/handoff fence (33,404) and all of Architectural Boundaries (46,281). Codex is the NAMED CROSS-VENDOR ADVERSARY, so the appointed reviewer ran without that canon. Now 65536, 18,660 B headroom. NOT VERIFIED: that a Codex runtime accepts 65536. || ADVERSARY SCOPE, corrected: Step 4b is the OBPI CEREMONY GATE and is heavy-lane-only (`obpi_complete_adversarial.py:292`). The settled ruling scoping it away from GHI/MX work was about stopping agents spinning ceremony for ad-hoc work — it did NOT rule that ad-hoc repair goes unchecked. Adversarial review of repair OUTPUT is unbooked on all three high-volume routes (GHI direct-fix ~470 commits/90d, MX, chores). Campaign :209/:210 book airlock TRANSIT (accounting), ADR-0.36.0 books the critic at DECISION moments. Neither reads the diff. || SETTINGS SPRAWL, measured: six substrates. config.py governs 0 of 42 data/*.json registries; no data_root field; 138 path literals across 62 files, five resolution idioms, no shared loader. PathConfig = 26 hardcoded defaults, 5 of which diverge from live .gzkit.json. manifest.thresholds written by sync_surfaces.py:147-151 and read by nothing. || REPORT DEFECT: the intake report's F-005/F-006 blocker ('pool ADR creation books no Layer-2 event') is VOID — withdrawn by operator ruling on GHI #831 (2026-08-19); `gz register-adrs --pool-only --dry-run` reports none unregistered. The report paraphrased gz-plan/SKILL.md:44, which IS the text of #831's fix, and reported it as the defect it corrects. Quarantined in the metrics ADR amendment so it cannot re-enter canon.

## Decisions Made

- [operator-ruled] Option C for the config work: PROMOTE `ADR-pool.central-config-airlineops-pattern` AND amend the campaign for sequencing (verbatim: "C is smart, but I understand 0.38.0 is not even authored, so we'll need that too"). ADR-0.38.0 (portability + flighttest verb) is reserved-but-unauthored, so the amendment is a TWO-ADR sequencing decision, not one. Rejected: A (promote to 0.39.0 alone — buries config behind 0.35/0.36/0.37/0.38, the opposite of prioritising it) and B (direct repair under GHIs — the GHI #929 precedent, starts now but leaves the architecture homeless across issue threads).
- [operator-ruled] Raise the Codex ceiling now, separately from the config architecture (verbatim: "In the meantime, yes, let's raise that codex cieling", spelling preserved).
- [operator-ruled] Config architecture shape: `.gzkit.json` is gzkit's settings and is appropriate; Claude and Codex require their own settings; `pyproject.toml` is local Python construction, NOT delivered with gzkit and out of scope; `.gzkit` things need consolidation; and — verbatim — "keeping anything within config.py is a mistake, however, having config.py read configs in a uniform manner is good." config.py becomes a LOADER, never a STORE.
- [operator-ruled] Fix the config-paths audit so it does not flag a declared PathConfig default (verbatim: "fix the audit — don't flag a declared PathConfig default"). Sub-shape (b) — .github/skills, .github/instructions, .github/workflows having no PathConfig field — was NOT ruled on and stays open.
- [operator-ruled] Amend both pool ADRs coupled, in one commit; keep the metrics storage-shape tension (Option A vs B) DEFERRED to promotion per the ADR's own rule; resolve the two-provenance question as one `gz metrics` verb with two labelled derivation paths; all four metric groups get bands.
- [operator-ruled] Extend adversaries to increase the quality of all work/repairs in gzkit; the design motivation for ADR-0.36.0 is sound.
- [operator-ruled] Prioritise control-surface/CMS work — already satisfied: the 2026-09-01 amendment made it TOPMOST as ADR-0.35.0 (3/11, BLOCKED).
- [agent-chose] 65536 for project_doc_max_bytes, grounded in `_PROJECT_DOC_BUDGET_CEILING_BYTES = 65536`, the ceiling the budget system already declared after the 2026-07-06 decoupling ruling — not an invented number.
- [agent-chose] Made `config` a REQUIRED parameter of `_collect_source_path_literal_issues`, not optional-with-default, so no future caller can silently regress to manifest-only coverage.
- [agent-chose] `_flatten_config_paths` derives NO parent directories, unlike `_flatten_manifest_paths`. Deriving them would add `.github` and silently exempt every `.github/**` literal — a targeted fix turned into a hole. Pinned by `test_undeclared_sibling_still_flagged`.
- [agent-chose] Wrote only `Read(...)` / `Edit(...)` deny rules. `Write(path)`, `NotebookEdit(path)` and `Glob(path)` are accepted but NEVER consulted per the permissions reference — writing them would have produced silently inert security rules.

## Immediate Next Steps

1. AUTHOR THE CAMPAIGN AMENDMENT for operator ratification implementing option C: promote `ADR-pool.central-config-airlineops-pattern`, and sequence it against `ADR-0.38.0` which is reserved-but-unauthored. Ascending-semver is absolute canon, so the amendment must say explicitly where config sits relative to 0.35.0/0.36.0/0.37.0/0.38.0 rather than leaving it to the next reader. Draft only — the operator ratifies.
2. AUTHOR ADR-0.38.0 (portability + the `flighttest` verb). Campaign :169-170 reserves it, operator verbatim 2026-08-17: "Wait for ADR-0.38.0". It is unauthored, and option C's sequencing cannot be written without it.
3. RULE ON GHI #938 sub-shape (b). `gz check-config-paths` still exits 1 with 7 findings: `.github/skills`, `.github/instructions`, `.github/workflows` have no PathConfig field. Two routes in its blocker comment — first-class PathConfig fields for the GitHub/Copilot surface, or an explicit out-of-domain list the way `sync_parity.py`'s census carries one. Interacts with the Firewall surface-destiny classification (campaign :219).
4. DECIDE whether three surfaced-but-unfiled findings enter the queue. The operator asked about compounding defect volume and none were filed pending that ruling: (a) adversarial review of repair OUTPUT is unbooked on the direct-fix/MX/chore routes; (b) `gz-obpi-pipeline/SKILL.md:66` says "There is no size, lane, or kind exception to Step 4b" while `obpi_complete_adversarial.py:292` has an explicit lane exception; (c) a known FALSE Layer-2 record — `OBPI-0.33.0-06`'s `adversarial_validation` cites a guard test that does not exist, unretracted per campaign :411.
5. VERIFY the Codex cap empirically. 65536 is set and gzkit-side green, but no observed Codex run confirms the runtime accepts it. Until then the delivery claim rests on the key being configurable, not on measurement.

## Pending Work / Open Loops

GHI #938 OPEN — sub-shape (b), 7 findings, gate red. GHI #815 OPEN — the cap is raised but the issue also covers must-survive section ordering; re-scope it against the new live numbers rather than assuming this commit closed it. || ADR-0.35.0 at 3/11, Pending, closeout BLOCKED — OBPI-0.35.0-03 and -08 in_progress, seven pending, -13 carries an open operator question on attestation disposition. IRON LAW: only the operator initiates any of it. || ADR-0.36.0 Proposed, 0/9, nothing runs — no critic script in .claude/hooks/, no AskUserQuestion matcher in .claude/settings.json (re-verified this session while editing that file). || Config sprawl residue not addressed by any commit here: PathConfig's 5 diverging defaults; the absent data_root; 138 unrouted data/*.json literals; `manifest.thresholds` written-and-never-read; `_PROJECT_DOC_BUDGET_CEILING_BYTES` defined only in two test files; `.claude/rules` and `.gzkit/rules` differing in all 25 shared files. || `gz check-config-paths` exits 1 — expected, sub-shape (b). `gz drift` reports 701 unlinked REQs, pre-existing. || Four pool ADRs name config/settings architecture, all unscheduled: central-config-airlineops-pattern, config-schema-settings-absorption, config-evaluation-tooling, polarity-aware-threshold-model. || `ADR-0.0.7-config-first-resolution-discipline` is `Validated` while its own body shows 5 unchecked checklist items and 5 `Pending` OBPI rows — unreconciled, no gate covers it.

## Verification Checklist

uv run gz check-config-paths   # expect exit 1, exactly 7 findings, all .github/{skills,instructions,workflows}; ZERO discovery-index.json findings — a discovery-index finding means 6ed5c9bd regressed
uv run python -m unittest tests.test_codex_config_surface.CodexDocCapCoherenceTest   # cap coherence: toml value == vendor-manifest value, and both clear live AGENTS.md
uv run gz validate --instructions-files-budget   # expect NOTE with headroom, not a breach
uv run unittest-parallel -t . -s tests --buffer   # 9166 tests; use 'set -o pipefail' if piping — verifier-pipe-gate refuses an unguarded pipe
uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing   # read the landed count here, never from a transcribed figure
uv run gz handoff rulings --search 'direct-fix'   # the Step-4b-vs-adversary ruling that was misread this session
git log --oneline 6b6c8a11..HEAD   # the five commits

## Evidence / Artifacts

`.claude/settings.json`
`.codex/config.toml`
`data/vendor-manifest.json`
`src/gzkit/schemas/vendor_manifest.json`
`src/gzkit/sync_surfaces.py`
`src/gzkit/commands/config_paths.py`
`tests/test_config_paths.py`
`tests/test_codex_config_surface.py`
`.gzkit/rules/agents-md-map-doctrine.md`
`docs/design/adr/pool/ADR-pool.afk-diagnosis-cloud-routines.md`
`docs/design/adr/pool/ADR-pool.session-productivity-metrics.md`
`docs/design/adr/pool/ADR-pool.central-config-airlineops-pattern.md`
`docs/examples/comparison-gzkit-speckit-bmad.md`
`.gzkit/insights/agent-insights.jsonl`

## Settled Rulings

661 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
