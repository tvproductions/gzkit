---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-31T14:11:23Z'
agent: claude-code
session_id: 57210dc7-83fb-40a3-9a94-ea9e9e06a611
continues_from: .gzkit/handoffs/20260831T093259Z-control-surface-family-four-closed-one-landed.md
---

## Current State Summary

Tree is clean; HEAD is `3c255459`, ONE COMMIT AHEAD of origin/main and NOT YET PUSHED (`git rev-list --left-right --count origin/main...HEAD` returns `0 1`). No active locks, no pipeline marker, no OBPI scope, no open TASK.

The session resumed the predecessor handoff, booked two operator rulings, and landed one commit:

- `3c255459` fix(vendors): retire the Copilot declarations and stop the mirror leaking CLAUDE.md (GHI #924, GHI #925) — 92 files, +234/-747

GHI #836 was closed as fixed. GHI #922 received a routing ruling recorded as a comment and DELIBERATELY LEFT OPEN. GHI #924 and #925 are implemented and committed but still OPEN, because the commit is unpushed and closing them should cite a SHA that exists on origin.

THE HEADLINE FINDING, AND IT IS THE PREDECESSOR'S FINDING REPRODUCING. The predecessor recorded that three of seven items it touched were open issues whose work had shipped days earlier and nobody closed. Re-deriving all nine remaining family premises against the tree found a FOURTH: GHI #836 was fixed by `b8625502` roughly twelve hours after it was filed, and sat open for eleven days. Its own second comment, the sibling-cut note, was posted ten hours AFTER the fix was already on main. Four of eleven family members have now been found already-fixed-but-open. That is a large part of why the family reads as incoherent.

## Important Context

`render_rule_for_copilot` IS LOAD-BEARING AND WAS DELIBERATELY NOT REMOVED. It renders no Copilot SURFACE any more, so it looks like dead code and removing it was the first instinct. `_classify_canonical_rules` is documented as equivalent to it BY CONSTRUCTION, and the nested `AGENTS.md` generation runs on the `applyTo` and `.instructions.md` vocabulary that renderer defines. Deleting it is a separate refactor with real behavioural risk. The `renderer` argument on `render_rules_to_dir` stays for the same reason. A future session reading "Copilot is retired" and finding this will want to delete it; read the classifier docstring first.

`.agents` CANNOT EXERCISE THE FOREIGN-ROOT EXCLUSION, AND A TEST WAS WRITTEN AGAINST IT BEFORE THIS WAS MEASURED. `_is_vendor_mirror_prefix` filters `.claude`, `.agents`, `.github/instructions` and `.github/skills` out of `subtree_prefixes` before the nested writer ever sees them. So a rule scoped to `.agents` produces NO subtree at all, and the exclusion is unreachable there. `.opencode` is a declared vendor root that is NOT a mirror root, which is why the test moved there. Measured: the `.github` and `.opencode` globs both yield prefixes; the `.agents` glob yields an empty list.

THE COUPLED SURFACE THAT ONLY A RUN WOULD HAVE FOUND. `_validate_mirror_skill_assets` demanded byte parity on every canonical asset, so once the mirror stopped delivering `CLAUDE.md` into foreign roots the audit demanded exactly the file the exclusion forbids, and `uv run gz agent sync control-surfaces` failed closed on a correctly-synced tree. Nothing in a diff review would have surfaced it; running the sync did. This is AGENTS.md DO IT RIGHT 1a in its literal form.

A MECHANICAL EDIT PASS CORRUPTED TEST SEMANTICS AND HAD TO BE REVERTED. A paren-depth scanner written to strip Copilot fixture lines mis-parsed docstrings containing brackets, and stripped the mirror-root POSITIONAL ARGUMENT out of multi-line `_write_skill` calls, leaving syntactically valid calls that wrote to the wrong root. `git checkout -- tests/` and a correct statement-aware pass followed. A mechanical pass over test fixtures MUST distinguish an element of a tuple from an argument of a call; the two look identical line-by-line.

THE MANPAGE TEMPLATE LIST WAS ALREADY STALE BEFORE THIS CHANGE. Two operator-facing docs claimed 11 canonical template slugs and omitted `changelog` and `release_notes`; the real set was 13 before this commit and 12 after. Both now cite the shipped template package directory as the authority rather than freezing a count, per the governance-core rule that a value written in Markdown is illustrative, never authoritative.

INHERITED CAUTIONS THAT STILL BIND. `uv run gz validate --transcribed-adr-counts` refuses a live ADR count transcribed into a handoff; cite `uv run gz adr status` output instead. Any commit touching source or tests needs a `Task:` trailer. A verifier piped into another process is refused by the verifier-pipe-gate hook; use `set -o pipefail`, or capture to a file and echo the real exit.

COMMIT TRAILER CONVENTION, STILL UNRULED. The harness asks for a `Claude-Session:` trailer; recent repo commits carry none and the repo uses `Task:` in slug form. This session followed repo convention. Carried forward from the predecessor unchanged.

## Decisions Made

- [operator-ruled] Resume the handoff by re-deriving all nine remaining family GHI premises against the tree and reporting a disposition table, executing no other advised step (verbatim: "Proceed with step 1 only"). Booked to Layer 2 via the handoff decide verb.
- [operator-ruled] Execute the recommended next steps that followed that report (verbatim: "doo recommended next steps"). Spelling preserved. Booked to Layer 2 as a second ruling against the same document.
- [operator-ruled] GHI #922 retargets into ADR-0.35.0 rather than staying a validator patch or being left parked, chosen against those two alternatives after measurement showed the witness audits the adopter bootstrap template rather than gzkit's Layer-1 corpus.
- [operator-ruled] Land GHI #924 and GHI #925 as ONE commit rather than two, because the two remedies read one derivation from opposite ends and an intermediate commit would be a tree where the GitHub directory has left the foreign-vendor set while the mirror does not yet honour the exclusion.
- [agent-chose] Did NOT close GHI #922 as superseded despite the retarget ruling, because ADR-0.35.0 cannot yet absorb the scope: no brief mentions the shape witness, and the nearest brief's structural fence scopes its new validator to owned sections only. The ghi-close dead-letter prohibition makes open-with-blocker the honest state, so the ruling was recorded as a comment instead.
- [agent-chose] Gave the GitHub directory its sibling Claude redirect rather than putting the question to the operator, because the foreign-root derivation's own stated ground, that foreign trees carry their own vendor's discovery convention, stops applying once no agent vendor declares that directory. Canon ruled it, so it was acted on and the rule named, per AGENTS.md Operator Economy of Effort item 7.
- [agent-chose] Kept the Copilot rule renderer and the renderer argument, against the instinct to delete apparent dead code, because the nested-AGENTS.md classifier is defined as equivalent to that renderer by construction.
- [agent-chose] Moved two test subjects rather than deleting the tests, because the properties under test are real and needed live subjects: the foreign-root exclusion moved to `.opencode`, and the canon-not-derived-view plan test now deletes the rendered Claude rules directory.
- [agent-chose] Superseded the Copilot pool ADR via frontmatter status plus a dated note, following the 16 pool ADRs already using that status, because no withdraw verb exists for pool ADRs.
- [agent-chose] Triaged rather than swept the documentation hits: 41 stale skill-doc mirror rows, three init manpage claims, the validate manpage surface list and one storage-tiers row were repaired; dated records under the design tree and prose describing vendor harnesses in the world were left as written.

## Immediate Next Steps

1. PUSH `3c255459`, THEN CLOSE GHI #924 AND GHI #925 separately, one disposition and one comment each, never batched. Both are implemented, committed and gate-green; they are open only because the commit is not yet on origin and a close comment should cite a SHA that exists there. Evidence for both closes is already gathered: the quality gate at exit 0, 9128 tests OK, receipts `arb-ruff-be191a0a0b00449cbdad312a6ec7e50f`, `arb-step-typecheck-809aa2f8ae3b4f70a9bc01e3c9326ecd`, `arb-step-unittest-59b358a2db3a483b8ffd33ed5ca4b782`.
2. RE-DERIVE ANY REMAINING FAMILY GHI PREMISE BEFORE WORKING IT. This is now measured four times over two sessions, not a caution. The open family is GHI #921, #907, #873, #815 and #922, plus whatever remains after step 1. Read the surface each body cites and confirm the defect is still present before planning around it.
3. Decide whether GHI #873's ownership paragraph gets corrected on the issue. Its body says the replacement-row producer is scoped to OBPI-0.35.0-02 and that the question should be ruled before that brief lands. That brief HAS landed attested-completed and ships retraction rows only; no brief in ADR-0.35.0 owns a replacement-row producer, and the corpus holds zero such rows. The gate the issue set has already passed unremarked, so nothing downstream will force the ruling.
4. Extend ADR-0.35.0's Feature Checklist with the witness-repoint item and its matching brief, if and when you want GHI #922 to move. Under the IRON LAW only the operator initiates that, via the gz-obpi-pipeline skill. Until it exists, GHI #922 stays open with its blocker recorded.
5. Hold the long-standing operator-held items: the design spike, and whether a delivery-cap breach on must-survive canon stays advisory (GHI #815), which is the one family item that has DEGRADED, from 385 bytes over the codex cap when filed to 14,108 bytes over today, with a second must-survive section now affected.

## Pending Work / Open Loops

UNPUSHED: `3c255459` is one commit ahead of origin/main. Nothing else in the tree is dirty.

OPEN, implemented and awaiting only the push and their closes: GHI #924 (Copilot declarations retired) and GHI #925 (skill mirror leaked a Claude discovery file into Codex's surface root).

OPEN by deliberate agent decision, with the operator's routing ruling recorded on it: GHI #922. It cannot close as superseded until ADR-0.35.0 carries a checklist item that absorbs the scope. Its premise is also UNDERSTATED rather than stale: the shape witness audits the 23,886-byte adopter bootstrap template, which is templated on the project name, while calling it the canonical Layer-1 surface. gzkit's root contract is 46,876 bytes and byte-identical to its committed rendition. No trust audit shape-checks the Layer-1 corpus at all.

OPEN by deliberate disposition from the predecessor session: GHI #873, ruled an operator-led fold-algebra amendment. Nothing further is agent-workable. Its reachability is still latent, with zero replacement rows and no producer in the source tree, but for a different reason than its body states.

OPEN, partially discharged: GHI #921. The grandfather debt named in its Observed section is DRAINED, at zero entries with a zero baseline count, and the version-chain lift is COMPLETE, with two further commits landing after the body's last recorded progress. The canonical rules tree is 190,622 bytes, down from the 220,524 its body recorded. Remaining: the bullet-narrative compression pass, gated at the instructions-files-diet chore's consult gate, plus the corpus half held for the ADR-0.35.0 discussion. The 90-percent contradiction it names is STILL LIVE, with both statements rendering in the root contract.

OPEN, live and untouched: GHI #907. The authorship arm is 112 lines reading one git config value; no file-content witness exists in the trust-audit package.

OPEN, live and WIDENING: GHI #815. Measured today at 46,876 bytes rendered against the 32,768-byte codex cap, 14,108 bytes over, against the 385 its body records. Two must-survive sections are now affected rather than one: the operator-doctrine canon block straddles the cap, and the architectural-boundaries section starts entirely past it. Both remedies remain owned elsewhere and both are unavailable, one parked post-1.0 and the other blocked on the registry-projection migration.

OPEN, unruled and carried forward unchanged: whether commits should carry the harness-requested session trailer alongside the repo's task trailer.

CLOSED THIS SESSION: GHI #836 [settled], disposition fixed, citing `b8625502`. That fix commit carries no issue trailer, so the commit-to-issue direction of the audit chain does not exist and cannot be created without rewriting landed history. The gap is named in the close comment as the reason the fix stayed invisible for eleven days.

PRE-EXISTING and untouched: the quality gate reports 697 unlinked specs and 21 unjustified code changes as advisory drift.

## Verification Checklist

Run these before trusting any claim above.

`git rev-list --left-right --count origin/main...HEAD` expects `0 1`, one unpushed commit. A `0 0` means the push already happened; anything else means work landed after this document was written.

`git status --short` expects empty output.

`git log --oneline -1` expects `3c255459` at authoring time.

`uv run gz obpi lock list` expects no active locks.

`uv run gz check` expects exit 0. Pipe it only with `set -o pipefail`, or capture to a file and echo the real exit; the verifier-pipe-gate hook refuses a bare pipe.

`uv run unittest-parallel -t . -s tests --buffer` expects 9128 tests OK.

`uv run gz agent sync control-surfaces` expects exit 0 with no stale mirror-only recovery block. That block is what the GHI #925 fix made visible, and its absence now is the repaired state.

`find .agents .gemini .opencode -name CLAUDE.md` expects NO output, which is the foreign-root exclusion invariant. The GitHub directory SHOULD carry one; it is no longer a declared vendor root.

`uv run python -m unittest tests.test_rules tests.test_skills_audit` expects OK, the covering set for the mirror exclusion and the redirect placement.

`uv run gz validate --instructions-files-budget` expects exit 0 with three advisory warnings; the byte figures there are the live GHI #815 measurement.

`gh issue list --state open --limit 40` re-derives family membership rather than trusting the ids listed above.

`uv run gz handoff rulings --search "copilot"` checks the settled corpus before re-arguing any vendor question.

## Evidence / Artifacts

Surfaces changed and committed this session (92 files):

- `src/gzkit/config.py` — the Copilot vendor block and the three Copilot path fields removed
- `src/gzkit/sync_surfaces.py` — the Copilot instructions writer, the ignore-file writer, and the sync branch that called them
- `src/gzkit/sync_skills.py` — `_forbidden_mirror_names` added; `sync_skill_mirror` and `find_stale_mirror_paths` now consult it
- `src/gzkit/skills_mirror.py` — the parity audit taught the same exclusion
- `src/gzkit/schemas/manifest.json` — the Copilot vendor and path keys removed
- `src/gzkit/validate_pkg/sync_parity.py` — Copilot entries removed from the surface-root census
- `src/gzkit/personas/__init__.py` — the Copilot persona adapter and its registry entry
- `data/distribution_baseline_manifest.json` — the Copilot template entry
- `.gzkit/manifest.json` — the Copilot vendor and path keys
- `.gzkit.json` — the Copilot vendor declaration
- `docs/design/adr/pool/ADR-pool.vendor-alignment-copilot.md` — superseded with a dated note
- `docs/user/manpages/init.md` — hook, template-slug and ignore-file claims repaired
- `docs/user/manpages/validate.md` — sync-parity surface list repaired
- `docs/user/runbook.md` — template-slug list repaired
- `docs/governance/storage-tiers.md` — the retired mirror row removed

Deleted: `src/gzkit/hooks/copilot.py`, `src/gzkit/templates/copilot.md`, `.gzkit/templates/copilot.md`.

Surfaces read and verified, not changed:

- `src/gzkit/rules/__init__.py` — the foreign-vendor-root derivation, the vendor-mirror prefix filter, and the Copilot renderer that was deliberately retained
- `src/gzkit/governance/trust_audits/agents_md_map_conformance.py` — the mispointed witness behind the GHI #922 finding
- `src/gzkit/governance/trust_audits/authorship.py` — the GHI #907 arm, still reading git config alone
- `src/gzkit/commands/register.py` — one of the two unguarded witness loops GHI #926 carries
- `src/gzkit/commands/adr_demote.py` — the other
- `src/gzkit/commands/content/retire.py` — read to establish it emits retraction rows only

Handoff chain and Layer-2 records:

- `.gzkit/handoffs/20260831T093259Z-control-surface-family-four-closed-one-landed.md` — the resumed predecessor
- `.gzkit/ledger.jsonl` — two handoff-resume-decided rows booking this session's rulings
- `.gzkit/handoffs/rulings.jsonl` — the append-only settled-ruling store

## Settled Rulings

636 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
