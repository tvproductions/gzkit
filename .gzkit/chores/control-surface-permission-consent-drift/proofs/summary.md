# Pass D Summary — Rule Prose vs. Permission Standing Consent

> Chore: `control-surface-permission-consent-drift` (Lite lane, audit-only, **advisory — never gating**)
> Date: **2026-08-09** (prior run: 2026-08-01)
> Inputs: `doctrine-map.md`, `permission-inventory.md`, `consent-drift.md`, `unwitnessable.md`
> Trigger: `scripts/check_proof_freshness.py` failed closed — proofs predated
> `.gzkit/rules` (last moved 2026-08-08, `9771ec1bd`).

Doctrine map **re-derived from the corpus**, not carried forward (CHORE.md § 1).
Surface: 28 prohibitions enumerated, 2 permission files, 186 rules read verbatim.

## Counts

| Severity | Count | Rows |
|---|---|---|
| `live` | 5 | D1, D2, D3, D4, D5 |
| `neutralized` | 1 | D6 |
| `historical` | 0 | — |
| **Unwitnessable entries** | **14** | U1–U14 |

**The ratio is the finding.** Six auditable rows against fourteen entries this pass
structurally cannot check. Read the drift ledger's length as a measure of what is
auditable, never of what is safe.

| Permission surface | allow | deny |
|---|---|---|
| `.claude/settings.json` (committed) | 0 | 6 |
| `.claude/settings.local.json` (gitignored) | 180 | 0 |

Every deny rule in the project lives in the committed surface; the local surface
carries none.

## Headline: standing consent to commit with the secret scanner disabled

`.claude/settings.local.json:80` grants:

```
Bash(SKIP=gitleaks uv run gz git-sync --apply --lint --test)
```

`gitleaks` is a configured pre-commit hook (`.pre-commit-config.yaml:97`, entry
`gitleaks protect --staged --redact`), so this is a hook bypass by the
**environment-variable channel**. `AGENTS.md` § Never #10 forbids it: *"Never commit
with `--no-verify`. All commits and pushes must run through the configured hooks and
quality gates."*

The deny list blocks the **flag** channel four ways and the **config** channel twice —
so its authors were defending hook-bypass as a category. None of the six mentions
`SKIP` (verified this run). That makes this a gap in the defense, not a category
declined.

The bypassed hook is the secrets scanner, on the repository whose `AGENTS.md`
§ Local Agent Rules records a **2026-04-19 operator-PII leak that required a
`filter-repo` rewrite and force-push to recover.** This is the one grant whose cost
of being wrong has already been paid once.

## Second finding: a write channel the hook layer cannot see

Five grants (row D2) authorize `cp` of skill files into generated mirrors — verbatim
the act `skill-surface-sync.md` § Do Not prohibits. Four copy **mirror → mirror**
(`.github/skills` → `.claude/skills`), so neither side is canonical and the next
`gz agent sync control-surfaces` silently reverts the destination.

Because the write happens under `Bash` rather than `Edit`/`Write`, it also evades
every `PreToolUse`/`PostToolUse` hook in `settings.json` — those match
`Write|Edit|NotebookEdit` only. **A `cp` is a file write the hook layer does not
observe.** That generalizes past this chore.

## Closed since the prior run

The chore's founding case is gone. `Bash(python3:*)` — the 2026-07-16 discovery that
motivated Pass D — is absent from both surfaces (`grep -c python3` → 0, 0), as are
`PYTHONUTF8`, `pytest`, `pip install`, and `sqlite`. Recorded as closed rather than
carried.

## § Known coverage limits — restated verbatim (binding, GHI #690)

A summary that does not restate these overstates what was audited.

1. **Context-dependence — the hard ceiling.** Much of `AGENTS.md` forbids an action
   *in a context*: "never call `gh issue create` **outside this skill**" (Always #13),
   "never X directly", "never X without ceremony". Permission rules are context-free
   string matches. The sanctioned and forbidden invocations are byte-identical.
   `Bash(gh issue:*)` is **load-bearing, not drift** — `/ghi-author` invokes
   `gh issue create` at `SKILL.md:199` as its own final step, and denying it would
   break the only sanctioned path for filing a GHI. Any context-dependent prohibition
   is **out of scope for a Pass D row** and belongs in `proofs/unwitnessable.md`.
2. **Broad-rule blindness.** A drift row can only be raised against a rule that
   *mentions* the prohibited token. `Bash(git *)` permits
   `git checkout -b feature/foo`, contradicting operator canon (verbatim, 2026-06-16:
   never create feature branches, work directly on main), but contains no matching
   substring. Broad rules are the more dangerous class and this pass cannot see them.
   Record known-broad rules in `proofs/unwitnessable.md` rather than silently passing
   them.
3. **CI-blindness.** The committed `.claude/settings.json` is checkable anywhere;
   `.claude/settings.local.json` exists only on the operator's machine. This chore is
   therefore **local-run only** and its findings are not reproducible in CI. Never
   wire it to a CI gate.
4. **Curated-list drift.** The doctrine→pattern mapping in `proofs/doctrine-map.md`
   is hand-maintained and can itself drift from `AGENTS.md`, reproducing the drift
   failure one level up. Step 1 re-derives the map from the corpus each run rather
   than trusting the prior run's map.

## Routing list

Operator canon: a GHI-tracked defect repair routes to **direct fix** — never spin up
an ADR or OBPI to discharge one. All remediation targets are permission surfaces,
which this chore may not edit (§ Policy and Guardrails: read-only).

| # | Row | Target | Fix | Size |
|---|---|---|---|---|
| 1 | **D1** | `.claude/settings.json` deny list | Add `Bash(SKIP=*)` so the environment channel is covered on the same terms as the flag channel. **Prefer this over removing the local grant** — it closes the class, and `settings.json` is the committed, CI-visible surface. | 1 line |
| 2 | **D2** | `.claude/settings.local.json` | Remove the five `cp`-to-mirror grants. They encode a workaround for a sync failure and make the unsanctioned path frictionless. | 5 lines |
| 3 | **D3** | `.claude/settings.json` deny list | Deny the four derived roots (`src/gzkit/{skills,rules,personas,templates}/**`). Deny wins over allow, so the local surface needs no change. | 4 lines |
| 4 | **D4, D5** | operator ruling, then deny | `Bash(gh auth:*)` and `Bash(gh repo:*)` remove the "explicit approval" channel `gh-cli.md` depends on. D5 rests on an interpretive category→verb mapping and should be ruled before acting. | <=2 lines |
| 5 | **U2, U5** | operator ruling | `Bash(git *)` and `Bash(gh api:*)` are the two broadest grants and each can express prohibitions naming no matchable token. Narrowing them is a real ergonomics cost; this is a posture decision, not a defect fix. | — |

**Not routed:** every `U` entry that is load-bearing (U1, U6, U9) or outside the
mechanism's reach (U13). Recorded permanently so future runs do not re-derive them.

## Audit posture

- **Lane:** Lite — audit-only, advisory, and **must never acquire a `gz validate`
  scope without operator ruling** (§ Policy and Guardrails). This run edited exactly
  six files, all under this chore's `proofs/`.
- **Read-only on permission surfaces:** `.claude/settings.json`,
  `.claude/settings.local.json`, `AGENTS.md`, and every rule file were read and not
  modified. Remediation is routed above, not applied.
- **First-party verification:** the D1 headline was re-verified directly by the
  session (grant line number, hook registration, and the absence of any `SKIP` deny),
  not accepted from the reader that surfaced it.
- **Mechanically generated:** `permission-inventory.md` is emitted verbatim from the
  two JSON surfaces; `surface-listing.txt` from the prescribed evidence commands.
  Neither requires judgment to regenerate.
