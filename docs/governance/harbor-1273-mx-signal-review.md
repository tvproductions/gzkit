<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# GHI #1273 review — the MX signal, audited against the ruled model

**2026-10-31. Status: review written; All three questions ruled. The repair has not begun. No code has changed.** Operator: **g0**. This is the deliverable #1273's closure contract names, a precondition of [RO-12](harbor-pilotage-candidate-2026-10-15.md#repair-orders). Its measurements are dated and taken at `145a44b6b`.

## What this review is

#1273 was filed on 2026-10-26 as an open question: what should *open* mean, and which readers must change? The R&D run answered that question the next day. The operator ruled that the model is defined in the run and that #1273 carries the repair (*"A"*, [decision](../rnd/contractor-kit.md#decision-the-mx-model-is-defined-in-this-run-1273-carries-the-repair)). So this review does not reopen the model. It audits the code against the model and names what the rulings left unsaid.

## What is already ruled

| Point | Ruling | Operator |
|---|---|---|
| Whose condition it is | The repository's. The marker stays committed, so every clone, worktree and CI run is in the condition. | *"A"* |
| The one reading of *on* | Present, parses, bound to a still-open `mx_session_opened`, not `exiting`. Anything else is normal operation at full strength, announced loudly with its cause and a one-command recovery. | *"A"* |
| Modes | One condition with a standby level commanded at entry, hangar or drydock. The marker's `mode` becomes the level. | *"A"* |
| CI | The full-strength run reports and does not fail: a second job with `continue-on-error: true` beside the unchanged blocking job, through `GZKIT_MX_FULL_STRENGTH`. | *"report only, decide within #1273"* |
| No `gz check` at push in safe mode | By design at the drydock level. The skill's "untouched" sentence is stale for that level, and the fix is the skill's own. | *"i don't want any long check at all"* |
| Lint in safe mode | Stays on, pinned at both levels. | *"somebody sweeps up the shop floor every night"* |

## The readers, measured

Live on 2026-10-31 all readers agree, because the marker is healthy: `is_active` True, `is_valid` True, `hangar_demotes` True, `alarms_off` True. They disagree only on the cases below.

| Marker state | `hangar_demotes` | `alarms_off` | `get_banner` | Ruled |
|---|---|---|---|---|
| absent | off | off | none | off |
| unreadable | **on** | off | **"MX MODE ACTIVE"** | off, announced |
| parses, unbound | **on** | **on** in safe mode | **active banner** | off, announced |
| `exiting` | off | off | **active banner** | off |
| bound, level hangar | on | off | hangar | on, slow alarms stay on |
| bound, level drydock | on | on | safe mode | on, slow alarms off |

### Readers that lower protection: they must take the one reading

| Reader | What it reads today | Action |
|---|---|---|
| `checkpoint.hangar_demotes` (`src/gzkit/mx/checkpoint.py:34`) | *"held is None or not held.exiting"*, so unreadable demotes | Conform. Every consumer inherits it: `resolve`, `blocks`, `is_advisory`, `hooks/guards.py`, the `gz check` step seam (`commands/quality.py:195`), `validate_cmd.py:964`, the routing hook, `stop-turn-feedback`, the three rendition audits, and the hardening guards. |
| `alarms.alarms_off` (`src/gzkit/mx/alarms.py:27`) | *"held.mode == "safe" and not held.exiting"*, unbound | Conform. Inherited by the alarm wrapper and `verifier-pipe-gate`. |
| `awareness.get_banner` (`src/gzkit/mx/awareness.py`) and its hook fallback (`src/gzkit/hooks/scripts/mx.py:44`) | Presence; *"an unreadable marker is the hangar"* | Conform. The module is stdlib-only by design so it fires when gz is the patient, and it would need the ledger binding, so the fallback keeps a bare stdlib scan. |

### Readers already bound to the ledger: no change

`mx_renew_cmd` (`commands/mx_cmd.py:484`), `preflight.py:169`, `lock_manager.py:383`, `contract.py:77` (`:115` delegates to it) and `ledger_producer_probe.py:232`. These ask whether the *session* is open, so they keep `is_valid`, which ignores `exiting` on purpose: `gz mx exit` holds the session open through its re-run.

### Readers of the file itself: they keep presence (§ Question 1, ruled)

Four readers refuse or detect on the file's presence, and `is_active` is what makes them safe. The ruled reading was put as a question about what lowers protection. Applied to these four, it would loosen them. See § Question 1.

| Reader | Presence means | If it took the one reading |
|---|---|---|
| `mx_enter_cmd` (`commands/mx_cmd.py:296`) | Refuse a second entry | A corrupted marker admits a second open session, which grounds as *more than one open session*. |
| `mx_exit_cmd` (`commands/mx_cmd.py:406`) | There is something to close | Unchanged in effect: it already refuses an unreadable marker at `:410`. |
| `normal_release_blocked` (`src/gzkit/mx/hardening.py:215`) | Refuse a release | A corrupted marker with an open ledger session could release mid-drydock. |
| `dangling_state_status` (`src/gzkit/mx/hardening.py:306`) | Ledger open, marker absent | Already ruled to keep its meaning (*"a defect in every clone"*). |

## Findings the rulings did not anticipate

1. **The one reading costs about 640 times more per call.** Measured: `hangar_demotes` 0.08 ms, `is_valid` 50.9 ms, because `_open_session_ids` parses all 19,975 lines of a 27.9 MB ledger. `hangar_demotes` runs once per guard. The repair memoizes the scan per process, keyed on the ledger's size and modification time, or every guard pays for it.
2. **The level rename would corrupt the open marker.** `Marker` is `extra="forbid"` and `mode` is `Literal["mx", "safe"]`. A marker holding a new value or field reads as unreadable under the code that does not expect it, and an unreadable marker now means full strength. See § Question 2.
3. **No one-command recovery exists.** The ruling requires one, and `gz mx exit` refuses an unreadable marker. See § Question 3, ruled: a new verb.
4. **At least 48 test fixtures write a marker with no ledger event** (`tests/mx/test_hardening.py` 11, `test_marker.py` 10, `test_checkpoint.py` 8, `tests/governance/test_mx_hardening_audit.py` 7, and more). Each expects demotion and would read as unbound. They need one shared helper that books the event. This is the repair's largest diff.
5. **The handoff claimed a pre-push pass that proves nothing.** It says `a73c70974` *"passed the pre-push gz check"*, but at the drydock level that hook exits 0 without running the check. The handoff stands as written; the Trust Model repair below removes the sentence that invites the claim.
6. **`Marker.mode`'s description is stale.** It says safe mode runs *"guards at full strength (GHI #1244)"*, which the ruling of 2026-10-17 replaced.

## Findings routed elsewhere

- **Solo validator scopes (C5).** `_dispatch_early_return_scopes` (`commands/validate_cmd.py:1363`) has at least 14 branches, not the census's 11, and they own their exit status. They do not read the signal, so they are not readers of it. Run directly they stay at full strength, the safe direction; where `gz check` runs one, its step seam demotes an exit 3. They belong to RO-13's enumerator and R1, which sorts every such site, and this review changes nothing there.
- **A self-test failure demoted as a policy breach (#1289, #1272).** RO-13's F5 owns the uniform exit statuses.
- **The measured traps of 2026-10-26.** Items 1, 2 and 4 are fixed or reverted; item 5's instance is reverted; item 6 is ruled, lint stays on. Item 3 stands: the post-commit recorder appends `artifact_edited` rows during a rebase, and `git rebase --continue` refuses. It is not a signal defect, so it takes its own issue.

## The repair, once the questions are ruled

Each step lands with its RED test, as #1273's closure contract requires.

1. `marker.py`: the one reading of *on*, beside `is_valid` and adding the `exiting` check, with the per-process memo and a typed cause for each off state. The stale `mode` description goes.
2. The shared fixture helper, so the tests below it can move.
3. `hangar_demotes` and `alarms_off` take the one reading. The docstring's *"presence-only reading"* goes. `GZKIT_MX_FULL_STRENGTH` lands here, re-applied by hand from #1263's reference patch, which no longer applies cleanly.
4. `awareness.get_banner` and the hook fallback, with the loud announcement.
5. The recovery verb under `gz mx` (§ Question 3), proposed name `repair`, with its manpage. It takes the required `--attestor`, as `renew` does, because restoring a marker lowers protection again. Three cases: unreadable, or missing with the ledger session open: rewrite the marker from that session's `mx_session_opened` event, which holds every field the marker needs. A marker with no open session behind it: remove it. A healthy marker, or none with no open session: report that and change nothing. Each change books one new ledger event. The announcement and the dangling-state message both name this one verb.
6. The level (§ Question 2): the marker, `--level` beside `--mode`, the banners, the readers.
7. The report-only CI job beside the unchanged blocking job.
8. Canon, in the same commits as the behavior: `mx-mode.md` § Honor the marker, `gz-mx`, `src/gzkit/mx/AGENTS.md`, `gz-session-handoff` § Trust Model naming the drydock-level exception, and the `safe-mode-doctrine.md` sentence *"The code does not yet read this way"*.

The cost was accepted when the reading was ruled: a marker corrupted mid-drydock brings every guard back.

**Mode contract.** The signal is what controls read, not a control. The report-only job is a monitor: operational, on; hangar, on and report-only; drydock, on and report-only. It carries no self-test beyond CI's own run and it is declared here until RO-13's foundation lands.

## Questions for the operator

### Question 1 — the readers of the file itself

**Ruled 2026-10-31: A** (operator: *"a"*). The four readers keep presence.

Do the four readers above take the one reading, or keep presence?

- **A (ruled):** they keep presence. The one reading governs what *lowers* protection; these four *raise* it, so a corrupted marker keeps every refusal. It honors *"a hand-made or corrupted marker lowers nothing"*, and a marker corrupted mid-drydock cannot open a release or a second session.
- **B:** they take the one reading too, as *"every other reader"* says literally. It is simpler to state, and a corrupted marker can then permit a release while the ledger session is open.

### Question 2 — how the level is stored

**Ruled 2026-10-31: A** (operator: *"a"*). A new `level` field, with `mode` read as an alias.

- **A (ruled):** a new `level: hangar | drydock` field in the marker, `mode` read as an alias while the open marker is carried, and the ledger's historical `mode` untouched. The next `gz mx enter` writes `level`, and `--mode` stays accepted beside `--level` with one spelling documented.
- **B:** keep the field named `mode` and change its values.
- **C:** defer the rename to RO-13's F2, which widens the same reader, and land only the one reading now.

### Question 3 — the recovery the announcement names

**Ruled 2026-10-31: B** (operator: *"b"*). A new verb under `gz mx`; its proposed name and behavior are in § The repair, step 5.

- **A:** `git restore .gzkit/mx.json` for an unreadable marker, and for an unbound one `git rm .gzkit/mx.json`, each printed with its cause. No new verb; it rests on the ruling that the marker is committed.
- **B (ruled):** a new verb under `gz mx` that diagnoses and repairs. One spelling for every case, at the cost of a CLI surface and a manpage for a rare event.
