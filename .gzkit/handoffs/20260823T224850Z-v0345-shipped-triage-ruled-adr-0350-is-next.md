---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-23T22:48:50Z'
agent: claude-code
session_id: 86ab03f9-6852-4985-9379-18e0b7cbbe79
continues_from: 20260823T204005Z-stranded-clone-reconciled-and-dossier-rebased.md
---

## Current State Summary

Session resumed the handoff `20260823T204005Z-stranded-clone-reconciled-and-dossier-rebased.md`, verified its claims against live state, booked the operator's ruling via `gz handoff decide`, and worked its advised steps in the order the operator set. Triage of the five open handoff GHIs is complete and is the session's primary deliverable. One new GHI was filed (#871) and left open with a blocker. The stale Movement A header in the active campaign was corrected on an operator ruling. Patch release **v0.34.5** shipped end to end — 31 GHIs, tagged, published, and swept clean by the release audit that same release delivered.

Branch `main` is clean and synced at 0/0 with `origin/main` at `b6f3da459`. No OBPI or ADR work was initiated this session; per the IRON LAW that is operator-initiated only, and the operator has sequenced ADR-0.35.0 for a fresh session.

## Important Context

**`ADR-0.35.0-canon-entry-corpus-landing` is the next work, and the campaign says so in its own arithmetic.** Movement B is TOPMOST *and gated*; Movement A is HELD as a Movement while its ADR-0.35.0 box holds the in-flight feature position. ADR order is absolute (operator verbatim, campaign line 49: *"i will NOT go out of adr order, whatsoever."*). Three feature ADRs were open with unlanded OBPIs when this was written — 0.35.0, 0.36.0, 0.37.0, in that order. Read every landed count from `uv run gz adr status <ADR-ID>`; none is transcribed here, because a figure in this document is the one a resuming session acts on.

**`ADR-0.38.0` is NOT a free slot.** The active campaign allocates it to Movement E — portability plus the `flighttest` verb, created 2026-08-17, operator verbatim *"Wait for ADR-0.38.0 in strict order."* The tech-debt dossier routes two findings to `rehome:ADR-0.38.0`, which names a semver with an unrelated owner. That is recorded as a correction comment on GHI #871, not as an edit to its body.

**The handoff tech-debt work is GHI-routed and sequenced behind ADR-0.35.0** by operator ruling this session. Canon supports it directly: a GHI is the work order and the receipt, and no ADR or OBPI is spun up to discharge one.

**Two of four declared pre-commit hook types were missing on this clone** and were re-installed mid-session. The clone was repointed to `origin/main` on 2026-08-23 during the stranded-clone reconciliation and hooks were never re-run, so `prepare-commit-msg` and `post-commit` were absent while `gz check` reported green. This is the live reproduction of GHI #851 and was recorded there.

**The CHANGELOG `[Unreleased]` block was empty at release time**, so all 31 v0.34.5 entries were authored during the ceremony rather than accumulated during the cycle. The coverage cross-check then passed exactly (31 qualified, 31 cited, zero gaps). The accumulate-as-you-go half of that workflow is not happening and nothing enforces it.

**`git add -A` refuses trailer-governed scope.** A version bump touches `src/gzkit/__init__.py`, so `gz git-sync --apply` blocks rather than sweeping a src change under a `chore:` message. The release must be committed under its own `release:` message with a `Task: TASK-gz-patch-release` trailer first; this is precedent, not a workaround.

## Decisions Made

- [operator-ruled] Proceed on the resumed handoff with GHI triage first, then stop for a ruling on what to pull (verbatim: "Proceed — triage first").
- [operator-ruled] Record the two ADR-0.38.0-routed dossier findings in one GHI carrying the routing conflict itself, rather than parking them or appending to the existing pool ADR (verbatim: "One GHI recording the routing conflict").
- [operator-ruled] Correct the stale Movement A header in the active campaign (verbatim: "correct stale header, then I'll decide. report back").
- [operator-ruled] Ship v0.34.5 as a patch release on the drafted narrative (verbatim: "that looks good, let's do that as a patch release (it is substantial)").
- [operator-ruled] Route the remaining handoff tech-debt work through GHIs, sequenced after ADR-0.35.0 (verbatim: "we want to move the handoff tech debt work forward. I think it can all be GHI'd. It won't come before 0.35.0 though.").
- [agent-chose] Filed GHI #871 OPEN with a blocker comment naming three concrete operator actions, rather than closing it `superseded` against a destination nobody had chosen. The `ghi-author` doctrine prefers same-session routing; open-with-blocker is the honest state when the destination cannot yet exist.
- [agent-chose] Recorded the ADR-0.38.0 allocation error as a correction COMMENT on #871 rather than editing its body, so the original reasoning and its repair both stand.
- [agent-chose] Carried a disambiguation clause into the corrected campaign header rather than writing `HELD` alone. Bare `HELD` would have replaced one misreading with its inverse — that ADR-0.35.0 should not be worked — which is the live sequencing question.
- [agent-chose] Committed the campaign correction as its own commit ahead of the release, so the release record stays a clean projection of the closed-GHI set.
- [agent-chose] Installed the two missing pre-commit hook types and recorded the reproduction on the existing GHI #851 rather than filing a sibling issue, since it is the same finding rather than a new cut.
- [agent-chose] Ranked the hook-witness GHI above the handoff GHIs in triage because its defect was live and measurable on this clone, not merely reported.

## Immediate Next Steps

1. **Open the ADR-0.35.0 session.** `ADR-0.35.0-canon-entry-corpus-landing` is the in-flight feature; read its landed count and which OBPI is already in progress from `uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing`, never from a figure transcribed here. **OPERATOR-INITIATED ONLY** — the IRON LAW forbids an agent starting any arm of OBPI work, including claiming the lock, launching a marker, or starting a TASK. Run it through the `gz-obpi-pipeline` skill.
2. **File the two unfiled dossier GHIs.** The CREATE destination collision (Critical, `src/gzkit/handoff_api.py:960` — `path.write_text` preceded only by `mkdir`, no `exists()` guard, no slug constraint) and the empty `branch`/`agent` identity on CREATE (High, cross-references #813). Step 0 prior art was run for the first on 2026-08-23 and was clear; re-run it, since #871 has landed since.
3. **GHI the remaining handoff tech debt**, per the operator ruling, sequenced after ADR-0.35.0. Four dossier findings route to the `skill-command-doc-parity` and `skill-authoring-quality` chores; the highest-value single fix is `src/gzkit/cli/parser_handoff.py`, which contradicts itself 51 lines apart — line 35 says the resume gate was retired and gates nothing, line 86 tells operators only `proceed` lifts the gate, and line 86 is published CLI contract.
4. **Rule the bearing-projection design question** (dossier finding `governance-bearing-not-projected`, High). It is the one item in the set that is not repair-shaped: a four-verdict advisory bearing projection sits close to the resume gate retired 2026-08-15 on the principle that a handoff advises rather than gates. Nothing can be worked on it until the operator says where advisory ends.
5. **Decide whether the CHANGELOG should accumulate during the cycle** rather than being authored at release time. Nothing enforces the `[Unreleased]` block, and it was empty at v0.34.5.

## Pending Work / Open Loops

- **GHI #871 open with a blocker comment.** Two dossier findings (one Critical, one High) have no permitted destination: corrective-rehome doctrine sends them to a feature ADR, ascending-semver order withholds every slot above the one in flight, and ADR-0.38.0 is allocated to Movement E. The operator's GHI-routing ruling this session is effectively blocker option 3 and should be booked on the issue.
- **Two dossier findings still unfiled** — CREATE destination collision, and empty `branch`/`agent` identity on CREATE.
- **Three of the five triaged handoff GHIs are gated on operator rulings, not engineering.** #870 asks traversal versus constraint; #851 asks whether a missing recorder should fail a tree closed; #767 states outright that its design is unratified and must not be built ahead of.
- **#767 gates #766 by an explicit ordering constraint** — retiring the mechanical bookmark removes the only reliable transcript citer in the system, so the transcript channel lands first. They cannot be pulled in the other order.
- **The campaign § Topmost line cross-references "§ Amendments 2026-08-16 (latest)"**, which never matched the `(latest)` marker and now points at a date two entries down. Flagged to the operator, deliberately not edited — Magna Carta amendments are operator-ratified.
- **Branch `pre-rewrite-main-20260823` and the scratchpad file backups remain and are disposable**, carried from the predecessor handoff.
- **Archive retention is unresolved by design** — whether archive means isolated-entry retention or atomic closed-chain compaction. Last measured at 11 movable, 87 lock-protected, 111 chain-protected.
- **Whether `gz init --update` should re-seed the ledger merge driver on existing adopter clones** is carried unresolved from the predecessor chain.

## Verification Checklist

```bash
git rev-list --left-right --count HEAD...origin/main   # expect 0 0
git status --short                                     # expect clean
uv run gz validate --version-release                   # v0.34.5 tagged, reachable, documented
uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing   # the next work; read the count here, never transcribed
uv run gz obpi lock list                               # confirm no lock is held before initiating
gh issue list --state open --limit 100                 # #871 and the handoff queue
```

Confirm the pre-commit hook set is still complete before committing — two of the four declared types were missing on this clone earlier today:

```bash
grep -n 'default_install_hook_types' .pre-commit-config.yaml
ls .git/hooks/ | grep -vE '\.sample$'                  # expect pre-commit, pre-push, prepare-commit-msg, post-commit
```

Re-confirm the unfiled Critical still stands before filing its GHI: the write in `create_handoff` (`src/gzkit/handoff_api.py`) should still have no destination guard, and `validate_handoff_document` should still resolve to exactly one call site inside that function.

## Evidence / Artifacts

Patch release **v0.34.5**, committed as `b6f3da459` and published as GitHub release v0.34.5:

- `RELEASE_NOTES.md` — curated narrative, 31 GHIs
- `CHANGELOG.md` — exhaustive projection, 31 entries, coverage cross-check exact
- `docs/releases/PATCH-v0.34.5.md` — manifest
- `pyproject.toml`, `src/gzkit/__init__.py`, `README.md` — version synced 0.34.4 to 0.34.5

Campaign header correction, committed as `0151ae638`:

- `docs/governance/build-to-1.0-campaign-2026-08-16.md` — § 6 Movement A header, plus a new § Amendments entry dated 2026-08-23

Dossier carried forward unchanged from the predecessor session:

- `.gzkit/audits/tech-debt/2026-08-23/report.md`
- `.gzkit/audits/tech-debt/2026-08-23/findings.json`

Predecessor handoff this session resumed and ruled on:

- `.gzkit/handoffs/20260823T204005Z-stranded-clone-reconciled-and-dossier-rebased.md`

GitHub artifacts authored this session: GHI #871 filed with a blocker comment and a correction comment; cross-link comment on #804; live-reproduction evidence comment on #851.

Observed at close: `uv run gz validate --version-release` exit 0; `uv run gz validate --changelog` exit 0; `uv run gz lint` exit 0; `uv run mkdocs build --strict` exit 0; focused governance suite `uv run -m unittest` 96 tests OK.

## Settled Rulings

501 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
