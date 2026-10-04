# Record — control switchboard, 2026-10-04

> **Reversed in full the same day.** By operator ruling of 2026-10-04 every switch described
> below was turned back on and the central switch itself was removed
> ([campaign plan § Amendments 2026-10-04 (2)](build-to-1.0-campaign-2026-09-20.md#amendments-2026-10-04-2)).
> `.gzkit.json` no longer carries a `disabled` block. The text below is kept as the record of
> what was done and why; none of it describes the current state.

This is a **dated record**, written 2026-10-04 when the switches were flipped. It states
what was switched off, where each switch lives and how to turn one back on. It rules on
nothing. Every list here is illustrative; the switches themselves are the authority:
`.gzkit.json` § `disabled`, `.pre-commit-config.yaml` and `.github/workflows/ci.yml`.
Read those files rather than trusting a name transcribed here.

## Why

The gate-by-gate value read of 2026-10-03
([record](gate-value-read-2026-10-03-evidence/README.md)) found three things with a
recorded history of catching defects behind green tests: the plain checks, the
cross-vendor adversary and the operator's directed audits. Everything else either never
returned a non-pass, returned one about its own paperwork, or kept no record of a catch.
The OBPI-0.35.0-10 trial ([evaluation](obpi-run-cost-2026-10-03-evidence/trial-evaluation.md))
then passed every check, every validator and nine of ten acceptance proofs while failing
independent review on five of ten requirements.

Operator rulings, verbatim and in order (2026-10-04):

> go ahead with the switch-off (can they be turned back on later?)

> no, i want to be able to enable. maybe we turn off then see the effects of turning things
> back on?

> will we build a central switch for this toggle?

> try again

The last was given after the harness refused the first attempt to write the switches.

## The method

Every gzkit control with no recorded catch loses its **automatic standing**: it no longer
runs on its own, refuses nothing, and blocks nothing. Nothing is deleted. Every verb stays
callable, and `gz check --full` still runs the whole estate on demand. Controls are then
turned back on one at a time to see what each one does for the operator. The rule for
automatic standing, adopted from the dismissed reviewer's recommendation:

> Lack of catch history warrants removing automatic authority, not claiming the tool can
> never help.

A switched-off control regains automatic standing on a recorded catch. Deleting a control
still takes the scorecard's named steering-failure evidence; this record deletes nothing.

## The central switch

`.gzkit.json` carries a `disabled` block with four lists. Each name is its own switch.

| List | Who reads it | Effect of a name |
|---|---|---|
| `hooks` | the settings generator and merge in `gzkit.hooks.claude` | the hook is left out of the generated `.claude/settings.json`; a group or phase left empty disappears |
| `skills` | the skill mirrors, the catalog, `gz skill list`, the skill audit | the skill leaves `.claude/skills` and `.agents/skills` and the catalog; `gz skill list --all` still shows it |
| `check_steps` | the `gz check` runner, every scope but `--full` | the step is dropped from the per-change gate and the inner loop |
| `orientation_sections` | `scripts/session_orientation.py` | the section is neither collected nor shown at session start |

The mechanism landed in commit `73e42d63a` with an empty block; the names were written on the
operator's "try again". Tests: `tests/test_disabled_controls.py`.

**To turn one control back on:** delete its name from the list, then run
`uv run gz agent sync control-surfaces` so the settings file and mirrors regenerate. A
re-enabled hook is wired at the next session start.

## What is switched off

Counts as written on 2026-10-04; the files hold the live state.

| Surface | Switched off | Kept |
|---|---:|---|
| Harness hooks | 14 | post-edit-ruff, the session orientation, the settings backup |
| `gz check` steps (per-change gate) | 60 of 67 | Lint, Format, Typecheck, Test, Docs build, Validate default scopes, Authorship policy |
| Skills in the catalog | 52 of 73 active | 21, listed below |
| Orientation sections | 1 | every other section |
| Git pre-commit hooks | 4 | ruff, ty, xenon, interrogate, gitleaks, authorship, the standard fixers, the pre-push `gz check` |
| CI | the full sweep | plain `gz check` plus `behave` |

### Hooks switched off, and what each did

| Hook | What it did |
|---|---|
| plan-audit-gate | blocked leaving plan mode without a passing plan-audit receipt |
| pipeline-gate | refused edits outside an active pipeline's allowlist |
| obpi-completion-validator | gated brief status changes on ledger evidence |
| pipeline-completion-reminder, pipeline-router | steered and nagged the pipeline |
| verifier-pipe-gate | refused a verifier piped into another process; refused three read-only commands on 2026-10-03 |
| stop-turn-feedback | blocked ending a turn on a lint finding; blocked on another agent's file on 2026-10-03 |
| ledger-writer | wrote an `artifact_edited` ledger row per edit, over a third of the ledger |
| instruction-router | surfaced `.github/instructions/*.instructions.md` on edit; that directory is empty |
| session-staleness-check, session-start-advisement, session-exit-bookmark | handoff and bookmark bookkeeping |
| mx-awareness | announced the maintenance hangar on every prompt |
| ghi-triage-chat-silence | backstop for the triage skill |

### `gz check` steps switched off

Every step except the seven kept. Each remains one `gz validate` flag away, and all of them
run under `gz check --full`. The `Validate default scopes` step still runs its ten default
scopes: manifest, surfaces, ledger, instructions, briefs, documents, personas, frontmatter,
version and taxonomy.

### Skills kept in the catalog

gz-check, gz-validate, gz-status, gz-state, gz-adr-status, gz-how, ghi-author, ghi-close,
ghi-triage, gz-insights-remember, gz-session-handoff, gz-patch-release, gz-arb,
gz-obpi-specify, gz-adr-create, gz-agent-sync, gz-init, gz-design, gz-rnd, gz-deps-upgrade,
git-sync. Every other active skill is named in `disabled.skills`, the pipeline skill among
them. A switched-off skill's `SKILL.md` keeps `lifecycle_state: active`: it is switched off
in this project, not retired.

### Git hooks and CI

In `.pre-commit-config.yaml` the hooks `task-trailer-stamp`, `surface-fidelity-cheap`,
`validator-reachability-ratchet` and `ledger-vocabulary-inertness` are commented out under a
dated marker; uncomment a block to re-enable it. The `Task:` trailer is no longer stamped;
the pre-push gate still reads trailers and refuses only the reuse skip, never the push, when
one is missing. In `.github/workflows/ci.yml` the single `gz check --full` step became plain
`gz check` plus `behave`; restore the single step to re-enable the governance sweep in CI.

## What keeps mandatory standing

The plain checks. The ledger and ARB receipts, written by `gz` commands. The REQ-coverage
check at completion. Completion through `gz obpi complete` with the operator's attestation,
Gate 5 unchanged and universal. GHI direct repair. Completion on the reduced route is today's
single-driver path with the human-review operation, which the ledger labels
`degraded-human-only`; making that the normal route is a code change this record does not
make.

## Prose this leaves stale, not edited

`AGENTS.md` is generated playback of the committed rendition and the corpus stack is not
re-landed here, so these sentences stand as written and are now false or in conflict:

- § Execution Rules: "`uv run gz check` is the per-change gate: every quality check except
  `Behave` and `Preflight`".
- § Governance doctrine surfaces: "`uv run gz check` runs every registered validator".
- § OBPI Acceptance Protocol: "Once initiated, follow the skill's implementer dispatch and
  spec-reviewer then quality-reviewer review; never substitute inline Stage 2", which names a
  skill now out of the catalog.
- Campaign plan § Amendments 2026-10-03 (2): "each obpi must be run using the obpi pipeline
  skill". How an initiated OBPI runs is the operator's to rule.

## Not ruled, kept here for a later ruling

The 2026-10-04 draft amendment carried five items the operator did not rule on. In brief:
a freeze on new OBPI initiation and governance-repair campaigns with a named exit; a plain
delivery path of brief, direct implementation, `gz check`, one executing independent review
by a different vendor, and the operator's acceptance; an acceptance record bound to the
commit SHA, the receipt ids, the reviewer's findings and the operator's words, retiring the
acceptance input digest; the disposition of `ADR-0.35.0` and OBPI-0.35.0-10, with hold until
a checkpoint recommended; and a checkpoint after three changes on the path with an archive
trigger if the retained core caught nothing a plain run would have missed. None of these is
in force.

## Unchanged by this record

OBPI-0.35.0-10 stays in progress, uncompleted and unattested, with the trial evaluation as
its record. The campaign plan's Topmost line and the IRON LAW stand. The Codex sanity pass
on the amendment text was not run; the operator did not call for it.

## Reversal of everything at once

Delete the `disabled` block, uncomment the four hooks, restore CI's single step, run the
control-surface sync. Or `git revert` the commit that carries this record.
