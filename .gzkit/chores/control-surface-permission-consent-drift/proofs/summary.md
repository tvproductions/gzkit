# Pass D Summary — Rule Prose vs. Permission Standing Consent

> Chore: `control-surface-permission-consent-drift` (Lite lane, **advisory — never gating**)
> Scan date: **2026-10-10** (prior scan: 2026-08-09, 62 days before, against a 30-day interval)
> Maintenance visit E of the R&D run `renewing-vows`, admitted by the operator.
> Inputs: `doctrine-map.md`, `permission-inventory.md`, `consent-drift.md`, `unwitnessable.md`,
> `settings-patch.md`

Doctrine map re-derived from the current files, not carried forward (CHORE.md § 1): root
`AGENTS.md` and all 26 authored rules read whole. Surface: 29 prohibitions enumerated, 2 permission
files, 67 rules read verbatim.

## Counts

| Severity | Count |
|---|---|
| `live` | **0** |
| `neutralized` | 0 |
| `historical` | 0 |
| **Unwitnessable entries** | **20** (U1 to U20; 14 in August) |

| Permission surface | allow | deny |
|---|---|---|
| `.claude/settings.json` (committed) | 0 | 42 |
| `.claude/settings.local.json` (gitignored, present) | 25 | 0 |

## Headline: the ledger is empty because the file was rebuilt, and that says little

August's six rows all lived in a 180-rule local file. That file was lost with the repository and
rebuilt on 2026-08-29 with 25 rules. None of the six survives. They are closed by reconstruction;
nothing was decided about them, and the `SKIP=` channel behind the worst of them is still
undefended by any deny rule.

The rebuilt file's own comment says mutating and outward-facing commands are absent "so they
still prompt". Two of its rules, `Bash(uv run gz:*)` and `Bash(uv run -m:*)`, pre-authorize every
`gz` verb, including the commit-and-push, canon-landing and attestation verbs (U13, U14).

## Second finding: three limits measured on the session that ran this audit

- **Mode-blindness (U17).** The session ran in an auto permission mode. Commands no allow rule
  grants ran in it. The permission files describe one mode's prompts and nothing else.
- **A context-free prohibition broken 40 times, unobserved (U18).** "Always `uv run` for Python
  commands": 39 `python3` and 1 `python`, counted from the transcript. No rule, hook or validator
  looks at it.
- **Bash writes bypass every write hook (U19).** 96 file-writing Bash calls, no Edit or Write
  call, across four visits. Six hooks never fired and no path-scoped rule loaded. An edit to a
  generated file was silently reverted by sync the same day.

These are this session's own breaches and they are reported as such.

## Closed and added since August

- Closed by reconstruction: D1 to D6.
- Added to the committed deny list since August: 36 `Read` and `Edit` rules over secret-shaped
  files.
- New doctrine rows: package chore copies, suppression writers, the `gh` allowlist read as
  exhaustive, the closed trailer set.

## Proposed patch

`settings-patch.md`, drafted and **not applied**: sixteen committed deny rules for context-free
prohibitions, with two written procedures that must be repaired first; three options for the
local allow list; one item that is design work, not a patch. Applying any of it is step 6, in a
run the operator starts.

## Known coverage limits (binding — restated verbatim from CHORE.md)

1. **Context-dependence — the hard ceiling.** Much of `AGENTS.md` forbids an action *in a context*: "never call `gh issue create` **outside this skill**" (Always #13), "never X directly", "never X without ceremony". Permission rules are context-free string matches. The sanctioned and forbidden invocations are byte-identical. `Bash(gh issue:*)` is **load-bearing, not drift** — `/ghi-author` invokes `gh issue create` at `SKILL.md:199` as its own final step, and denying it would break the only sanctioned path for filing a GHI. Any context-dependent prohibition is **out of scope for a Pass D row** and belongs in `proofs/unwitnessable.md`.
2. **Broad-rule blindness.** A drift row can only be raised against a rule that *mentions* the prohibited token. `Bash(git *)` permits `git checkout -b feature/foo`, contradicting operator canon (verbatim, 2026-06-16: never create feature branches, work directly on main), but contains no matching substring. Broad rules are the more dangerous class and this pass cannot see them. Record known-broad rules in `proofs/unwitnessable.md` rather than silently passing them.
3. **CI-blindness.** The committed `.claude/settings.json` is checkable anywhere; `.claude/settings.local.json` exists only on the operator's machine. This chore is therefore **local-run only** and its findings are not reproducible in CI. Never wire it to a CI gate.
4. **Curated-list drift.** The doctrine→pattern mapping in `proofs/doctrine-map.md` is hand-maintained and can itself drift from `AGENTS.md`, reproducing the drift failure one level up. Step 1 re-derives the map from the corpus each run rather than trusting the prior run's map.

A fifth, found this run and not yet in the chore text: **mode-blindness** (U17).

## Verification

Read-only except for this chore's `proofs/`. Whether a `Read(...)` deny stops a `cat` under a
standing `Bash(cat:*)` allow was not tested (U16). No settings file was changed.
