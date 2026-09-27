---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-27T16:40:26Z'
agent: claude-code
session_id: 9c70e8e2-365b-4a4e-9c05-8bcdf332f3a2
continues_from: .gzkit/handoffs/20260927T120013Z-three-ghis-fixed-twenty-filed.md
---

## Current State Summary

This was a design-discussion session, not an implementation session. No source, canon or doctrine file was edited. HEAD is unchanged at b7fed91c0 on main; the only working-tree change is the pre-existing `.gzkit/ledger.jsonl` modification the session started with.

The thread started with the operator's question about requirements and release management and skills packaging (wheel vs. gz-skills vs. Superpowers/MPAS), and narrowed to how gzkit delivers and mirrors skills. Work done:

- Measured the skill catalog (73 canonical skills, 2 project-local) and drafted a wheel / gz-skills / project-local placement table. The operator's later positions (see Important Context) made the gz-skills axis of that table moot: all gzkit skills stay gzkit's.
- Read opencode's skill source to see how a tool ships built-in skills: one in-memory built-in (`customize-opencode`), lowest precedence, overridden by a same-name disk skill, never copied into the user's repo; remote skills fetched at session start into a versioned global cache (`skills.urls`); arbitrary directories via `skills.paths`.
- Verified harness discovery: Claude Code reads `.claude/skills` (no configurable skills path; per-skill symlinks documented); Codex reads `.agents/skills` (symlinks followed for repo/user/admin scope, codex-rs/ext/skills/src/loader/host.rs:165). Neither reads the other's directory.
- Measured the mirroring cost and ran an option-A experiment (vendor skill mirrors gitignored and generated locally): no gate requires committed mirrors, only mirrors on disk.
- Checked two suspected defects: defect 1 (a shipped router naming a withheld skill) was a false positive and was withdrawn; defect 2 was confirmed and filed as GHI #1138.

The predecessor handoff's advised steps (GHI queue, carried items, ADR-0.35.0 initiation, pool ADR bullet) were not presented or ruled on: the operator opened this design thread instead. No `gz handoff decide` was booked for the predecessor.

## Important Context

**This is a discussion to resume, not a set of rulings.** Operator, verbatim: "we don't have rulings as much as a discussion to resume, so take care there". The positions below are the operator's own words from the discussion, carried so the next session does not re-ask them. None is booked in the rulings store, and none has been written into the Magna Carta (`docs/governance/build-to-1.0-campaign-2026-09-20.md`). Treat each as the operator's current stated position, open to refinement, and never as ratified canon.

Operator positions, verbatim:

- On gzkit's identity: "not ALL skills end up driving a gz command, but most will. I want gzkit to be my ultimate toolkit."
- On the packaging split: "I am putting together a "lite" SP, SP-BP, MPAS, gz-skills package where gzkit will remain  its own "heavy" all-in-one approach."
- On gz-skills (the operator also said "confirm" when this was restated back): "no, I am NOT going to onboard ANY gz-skills skills, that whole project will live separately. However, we can keep track of its progress and cross-compare back to gzkit via the local-only skill I described (it will behave like airlineops parity and competitor analysis). We will no longer take any 'gz-skills' onboarding approach. if I see something that could benefit either when we do the scan, we'll talk about it."
- Earlier in the same turn: "Also, I do NOT have to maintain/use gz-skills. It might be better to defer gz-skills be we might want another local-only skill that tracks parity (like the airlineops and the competitor analysis). I think leaving gz-skills out of it is smarter at this time."
- On vendor mirrors and adopters: "A, check which gates assume committed mirrors. discuss the campaign implications separately. However, an adopter WILL need to copy local AND keep up with changes. I think that is smart, but want to discuss."
- On process: "yes, file the defect-2 GHI, but we need more discussion and anything we do must update the magna carta."
- On dogfooding: the operator uses gzkit's skills with Claude Code, Codex and opencode now to build gzkit ("hense the mirroring"), and "gzkit just isn't ready to drive my projects yet."

What the agent withdrew, so it is not re-proposed: every gz-skills onboarding shape it offered (wheel "twin" skills as thin adapters over gzs-* skills; gz-skills as an on-ramp tier with a graduation contract; "gzkit canonical, lite takes extractions"). Also withdrawn: a proposal to move the requirements catalog ahead of ADR-0.35.0, which contradicted the campaign's finish-in-flight-work-first order.

Gotchas:

- A research subagent reported a Claude Code `skillsDir` setting. It does not exist: it is absent from the settings reference, and the skills doc says no configurable skills path exists. Do not build on it.
- The campaign's "Surface mirroring" box attributes about 49% of commits to `gz git-sync` "regenerating five copies of every skill". Measured over the 90 days to 2026-09-27, the 538 `gz git-sync` commits mostly touched docs/ (532 file-changes), `.gzkit/handoffs` (476), the ledger (278) and insights (162); each skill mirror was touched 23 times. The mirrors' real cost is diff weight (12.6% of changed lines, 104k of 828k; 404 of 1841 commits), not commit count. The box's premise needs an operator amendment; the operator asked to discuss campaign implications separately.
- The skill mirrors (`.claude/skills`, `.agents/skills`, `src/gzkit/skills`) are byte-identical to `.gzkit/skills`. The rule mirrors are vendor-transformed, not copies, and are a separate question.
- Current doctrine `.gzkit/rules/skill-surface-sync.md` § Bootstrap semantics makes an adopter's `.gzkit/<surface>/` canonical after `gz init` (the vendored model). The overlay model discussed (shipped bundle canonical, explicit local overrides, generated mirrors) would reverse that and change what `gz init` delivers, so it is ADR-shaped and operator-initiated.
- `.gzkit.json` has opencode `enabled: false`, while the operator targets opencode. opencode reads both `.claude/skills` and `.agents/skills`, so with both mirrors present it loads every skill twice (later wins, warning per duplicate).

Workflow fronts (campaign § Workflow fronts): this thread belongs to the **new R&D** front as a multi-session design thread. It has no design record yet; per the campaign, a multi-session thread is carried as its own named line with a pointer to its design record. The **ghi triage** front gained #1138. The **adr/obpi campaign** and **handoff system** fronts were not inspected this session.

## Decisions Made

No design rulings were booked this session. The operator asked that the thread be carried as a discussion to resume, so the operator's design positions are recorded verbatim in Important Context rather than here, where an operator-ruled marker would promote them into the rulings store as settled.

- [agent-chose] Withdrew suspected defect 1 (the shipped `gz-project` router row naming the withheld `gz-competitor-radar`). `scope_router_rows_for_delivery` drops that row at `gz init`, and `tests/governance/test_skill_delivery_scoping.py` already witnesses the class; the suite ran 16 tests, REAL EXIT 0. The agent had read the wheel copy instead of the delivered output.
- [agent-chose] Filed GHI #1138 through `ghi-author` on the operator's instruction to file the defect-2 GHI. Classified it as the catalog-wide cut of #1034 (per-skill, `gz-flighttest`), labelled defect, runtime and tech-debt, and posted the cross-link on #1034 at authoring time. Rejected: re-opening #1034 (different scope), and enumerating the whole "delivered content names a gzkit-only path" family (#900, #911, #913, #1108, #1114, #915) as individual cross-links; the body names the family once and records that no locus tracks it.
- [agent-chose] Measured option A in two scratch clones outside the repo instead of in the working tree, and did not commit in the clones (a first attempt using a no-verify commit was refused by the harness and dropped). Compared against an unchanged baseline clone so clone-only failures (global git email, uninstalled hooks, the live authorship test) could be separated from the effect of removing the mirrors.
- [agent-chose] Verified both research subagents' key claims against primary sources before relaying them. The Claude Code report's `skillsDir` claim failed verification and was discarded; the Codex symlink claim was confirmed in the Codex source.

## Immediate Next Steps

These are advised steps for the operator to rule on; none is authorized by this handoff.

1. Present this design thread to the operator and ask where to resume. The open questions are: the adopter delivery model (vendored copy vs. overlay; the agent asked whether the operator edits gzkit's skills in place when using gzkit in another project, and it is unanswered); the campaign implications, including amending the "Surface mirroring" box's premise; and when to implement option A for the vendor skill mirrors, which the campaign box owns.
2. Ask whether the thread should get a design record (for example through `gz-design` or `gz-rnd`), since it now spans sessions and the campaign carries such threads by pointer to their record.
3. When positions settle, draft one Magna Carta amendment for operator ratification, because the operator stated that anything done must update the Magna Carta. Candidate content: the gz-skills separation and project-local parity skill, option A for vendor skill mirrors, the corrected mirroring premise, and whichever delivery model is chosen.
4. Ask the operator how to route GHI #1138: direct GHI repair now, or hold until the delivery-model discussion settles (an overlay model could change which `docs/` references need to ship). Also ask where the untracked "delivered content names a gzkit-only path" family should be tracked.
5. Present the predecessor handoff's advised steps, which were never presented this session (see Pending Work).

## Pending Work / Open Loops

From this thread (not started):

- Option A for the vendor skill mirrors: gitignore `/.claude/skills/` and `/.agents/skills/`, `git rm` the 276 tracked mirror files, add a `uv run gz agent sync control-surfaces` step before `gz check --full` in `.github/workflows/ci.yml`, and decide how fresh clones and cloud agent sessions get their mirrors (possibly the SessionStart hook; whether Claude Code picks up skills a hook creates in the same session is unverified). The campaign "Surface mirroring" box owns this work, and the operator wants the Magna Carta updated with anything done.
- A project-local skill (`project_local: true`) that tracks gz-skills' progress and cross-compares it with gzkit, modeled on `airlineops-parity-scan` and `gz-competitor-radar`. Not designed or authored.
- The wheel copy `src/gzkit/skills` could be assembled at build time instead of committed. `uv run` uses an editable install that reads `importlib.resources.files("gzkit.skills")`, so it would need a development fallback. This falls under the distribution-invariant ADRs (ADR-0.0.31, ADR-0.0.32); not discussed with the operator.
- The adopter delivery model question (vendored vs. overlay) is open, pending the operator's answer about in-place skill edits.
- GHI #1138 open and eligible for direct repair; routing awaits the operator.
- opencode is `enabled: false` in `.gzkit.json` although the operator targets it; not raised as a change.

Carried from the predecessor handoff and unpresented this session: #1119 to #1137, plus #1022 and #1060 (re-opened); #1131 awaits an operator ruling on whether gz adr promote should book adr_created; #1136 carries its remaining doc claims. Also carried: #1110, #1113, #1034, #1063, #907. Insights awaiting operator rulings: dry-run brief-drift writes the ledger; OBPI-0.37.0-04's stale Denied Paths note; the rm -rf course-correction. Unasked: the presenter insight that gz complexity advise prints No crossings detected after an all-attested run, the competitor-radar cadence, whether the scaffolding-settings layer needs its own ADR, and the operator's confirmation of the reworded precedent bullet in ADR-pool.harness-factoring-minimal-init (3cad9e3f1). Whether OBPI work on ADR-0.35.0 resumes is the operator's to initiate.

## Verification Checklist

- `gh issue view 1138 --json state,title` and `gh issue view 1034 --json comments` (the cross-link comment is the last one).
- Skill mirrors identical to canonical: `diff -rq .gzkit/skills .claude/skills` and `diff -rq .gzkit/skills .agents/skills` report only `__pycache__` directories present in canonical.
- Defect-1 withdrawal: `uv run python -m unittest tests.governance.test_skill_delivery_scoping` gives 16 tests OK (capture the exit code to a file; a piped unittest is refused by the verifier-pipe gate).
- Mirror cost: `git log --since='90 days ago' --numstat --format=''`, summing lines whose path is under `.claude/skills`, `.claude/rules`, `.agents/`, `src/gzkit/skills|rules|personas|templates|chores`, `AGENTS.md` or `CLAUDE.md`. The measured figure was 12.6% of changed lines on 2026-09-27; re-measure rather than trust it.
- Option-A experiment, reproducible: make two `git clone --local` copies outside the repo; in one, `git rm -r .claude/skills .agents/skills` and gitignore both paths, then run `uv run gz agent sync control-surfaces` and `uv run gz check` in both and compare the failing checks. On 2026-09-27 both clones failed only Authorship policy, Session green gate and one test (`test_live_repository_passes_its_own_authorship_audit`), all clone artifacts. For a clean baseline, set a noreply `user.email` locally and install the hooks in each clone first.
- Defect-2 measurement: run `gz init` in an empty scratch repo and resolve every `docs/*.md` reference in the delivered `.gzkit/skills/**/*.md` against that tree (62 distinct, 0 resolving on 2026-09-27).

## Evidence / Artifacts

- GHI #1138 (filed this session); cross-link comment on GHI #1034.
- `.gzkit/rules/cross-platform.md` (§ Delivered path literals: lists "a repo-relative path" as portable; the gap #1138 names)
- `.gzkit/rules/skill-surface-sync.md` (§ Bootstrap semantics: the adopter copy is canonical after init)
- `src/gzkit/skills/__init__.py` (`project_local` delivery boundary, GHI #915)
- `src/gzkit/sync_surfaces.py` (`sync_pkg_surfaces`, the wheel copy)
- `tests/governance/test_skill_delivery_scoping.py` (router rows and withheld-slug class witness)
- `tests/governance/test_shipped_chore_criteria.py` (the chores-surface sibling guard)
- `.gzkit.json` (vendor roster: claude `.claude`, codex `.agents`, opencode disabled)
- `.github/workflows/ci.yml` (runs `gz check --full` on a fresh checkout; needs a sync step under option A)
- `docs/governance/build-to-1.0-campaign-2026-09-20.md` ("Surface mirroring" box; § Workflow fronts)
- `docs/design/adr/pool/ADR-pool.harness-factoring-minimal-init.md`
- `docs/design/adr/pool/ADR-pool.skill-runtime-authority-inversion.md`
- External sources read: opencode packages/opencode/src/skill/index.ts and discovery.ts (sst/opencode on GitHub); Codex codex-rs/ext/skills/src/loader/host.rs and host_roots.rs (openai/codex on GitHub); the Claude Code skills and settings documentation.

## Settled Rulings

1122 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
