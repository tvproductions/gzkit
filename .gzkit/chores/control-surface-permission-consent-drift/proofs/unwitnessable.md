# Unwitnessable Ledger — Pass D

> Chore: `control-surface-permission-consent-drift` (Lite lane, audit-only, advisory)
> Run: **2026-08-09**. Supersedes the 2026-08-01 ledger.

**This artifact is the point of the chore as much as the drift ledger** (CHORE.md § 4).
It is the honest record of what was *not* checked, and it is what stops a reader from
mistaking a six-row drift ledger for a clean permission surface.

**14 entries here against 6 drift rows.** Most of this surface is not auditable by
this mechanism, and the unauditable part contains the more dangerous class.

---

## Context-dependent prohibitions — the hard ceiling

Permission rules are context-free string matches. Where doctrine forbids an action
*in a context*, the sanctioned and forbidden invocations are byte-identical.

**U1 — `gh issue create` — LOAD-BEARING, NOT DRIFT.**
`.gzkit/rules/gh-cli.md`: *"**`gh issue create` is forbidden as a direct agent
invocation** … The prohibition is on the **caller**, not the string."*
`AGENTS.md` § Always #13 says the same. But `/ghi-author` invokes `gh issue create`
at `SKILL.md:199` as its own final step, so `Bash(gh issue:*)` is what makes the
*sanctioned* path work. Denying the pattern would break the only legitimate way to
file a GHI. Recorded permanently so no future run raises it as a row.

**U6 — verifier pipes.** `.gzkit/rules/tests.md` § Verification exit-code integrity:
*"NEVER pipe `unittest`/`behave`/`mkdocs --strict` … through `tail`/`head`/`grep`."*
The tokens are prohibited only in a *pipeline position*, never as commands, and
standalone `grep` is load-bearing for every read verb in this audit.
**A T2 witness exists and it is not the permission surface:** the
`verifier-pipe-gate.py` `PreToolUse` hook over `Bash` (GHI #589) refuses a verifier
in any non-final stage. Correctly enforced elsewhere.

**U7 — MX entry.** `.gzkit/rules/mx-mode.md` § Do Not: *"Do not invoke `gz mx enter`
or `gz mx exit` directly in a shell step — use the `gz-mx` skill."* The skill's own
sanctioned execution shells the identical string; the discriminator is the caller.

**U8 — audit ordering.** `.gzkit/rules/adr-audit.md` § Do Not: *"Do not run
`gz audit` before attestation."* A temporal precondition against ledger state.
Permission rules are stateless string matches with no access to gate history.

---

## Broad-rule blindness — the more dangerous class

A drift row can only be raised against a rule that *mentions* the prohibited token.
These grant the prohibited action while naming nothing this pass can match.

**U2 — `Bash(git *)`.** Permits `git checkout -b feature/foo`, against
`AGENTS.md` § Operator Doctrine (verbatim 2026-06-16: *"Never create feature
branches — work directly on main"*), and `git push --force`, against
`gh-cli.md` § Prohibited without explicit approval. Neither prohibition's tokens
appear in the rule. This is § Known coverage limits #2 verbatim.

**U3 — `Bash(uv run *)`.** Subsumes every governed CLI verb — `gz obpi complete`,
`gz attest`, `gz adr emit-receipt`. Any prohibition about *how* a governance verb is
reached (Never #9: *"Run every stage through the governing skill, not via direct
CLI"*) has no token the matcher can see. Enforcement for these lives inside the CLI.

**U4 — in-place writers.** `Bash(sed:*)`, `Bash(do sed:*)`, `Bash(perl -i -pe ' *)`.
General writers that can target `.gzkit/ledger.jsonl` or
`.gzkit/insights/agent-insights.jsonl` without naming them. **The two strongest
write-path prohibitions in the corpus — Never #2 (do not modify the ledger directly)
and Always #11 (never hand-append the insights jsonl) — are therefore unauditable
against these grants, even though no allow rule mentions either path.**
Partially mitigated elsewhere: `forbid_manual_ledger_edits` in
`src/gzkit/hooks/guards.py` rejects non-append staged ledger edits at commit time.

**U5 — `Bash(gh api:*)`.** A generic GitHub transport. It can express every item in
`gh-cli.md` § Prohibited without explicit approval — settings mutation
(`-X PATCH /repos/…`), secret write (`-X PUT /repos/…/actions/secrets/…`), PR merge
(`-X PUT /repos/…/pulls/…/merge`) — while naming none of them. `Bash(git *)`'s
equivalent on the GitHub surface.

**U11 — dispatch primitives.** `Bash(xargs -I {} bash -c "…")`,
`Bash(xargs -I {} sh -c '…')`, `Bash(for f:*)`, `Bash(for dir:*)`, `Bash(for cmd:*)`,
`Bash(for skill:*)`, `Bash(for mirror:*)`, `Bash(while read:*)`, `Bash(do)`,
`Bash(do sed:*)`, `Bash(do basename:*)`, `Bash(bash /tmp/time_tests.sh)`.
The body of a loop or a `bash -c` string is not a token the matcher inspects, so any
prohibited command executed inside one is unmatchable **by construction** — a
second-order form of § Known coverage limits #2.

**U12 — `Read(//Users/jeff/**)`, `Read(//opt/homebrew/**)`, `Read(//tmp/**)`.**
Whole-home read consent. The operator-PII rule governs *writing* the address into
repo-bound artifacts, so no prohibition token matches a read grant — but the grant
widens the surface from which PII can enter context in the first place. No doctrine
hook exists to hang a row on.

---

## Category the mechanism does not reach

**U9 — `uvx` invocations vs "Always use `uv run` for Python commands".**
`Bash(uvx ty:*)`, `Bash(uvx xenon:*)`, `Bash(uvx radon *)`,
`Bash(uvx unittest-parallel *)`, `Bash(uvx ruff check src tests)`,
`Bash(uvx ruff format --check .)` are literally non-`uv run` Python invocations under
standing consent. **Not raised as a row:** `.gzkit/rules/chores.md` § 3 Apply Advice
*prescribes* `uvx ty check . --exclude 'features/**'`, so the grants are load-bearing.
The inconsistency is **rule-vs-rule**, which is Pass A's subject
(`control-surface-rule-conflicts`), not permission drift. Raising it here would be
pattern-matching a prohibition whose scope its own sibling surface contests.

**U13 — prohibitions with no command or path token at all.**
`.gzkit/rules/tests.md` (*"unit tests MUST use `tempfile` temp DBs; NEVER use
live/production databases"*, *"NEVER use raw `shutil.rmtree()` in tearDown"*);
`.gzkit/rules/adr-audit.md` (*"Never backfill a cosmetic `@covers` decorator"*);
`AGENTS.md` § Operator Doctrine (*"Never spin up an ADR or OBPI merely to discharge a
GHI"*); `AGENTS.md` § Never #1/#8 (Gate 5 bypass). These govern code content,
artifact semantics, or process choice. The permission surface cannot express them in
either direction — not a gap in this pass, a category the mechanism does not reach.

---

## Scope boundaries of the pass itself

**U10 — permission surfaces outside CHORE § 2's scope.** `~/.claude/settings.json`
(user-level; read this run only far enough to confirm it declares
`permissions.defaultMode: "auto"` with no `allow`/`deny` keys), enterprise/managed
settings, and session-level permission-mode overrides. **Any of these can moot every
row in the drift ledger by changing whether prompts fire at all.** This pass reads
none of them beyond that one confirmation.

> Relayed as a finding, not acted on: the subagent that performed this walk reported
> a session-level flag that disables permission prompting wholesale as belonging to
> this category. It is named here only to record that the category exists and is
> unaudited. This chore neither recommends nor uses it.

**U14 — the local surface is gitignored and single-machine.**

```
$ git check-ignore -v .claude/settings.local.json
.gitignore:54:.claude/settings.local.json	.claude/settings.local.json
```

CHORE § Known coverage limits #3. Findings are a snapshot of one machine, not
reproducible in CI, and **no git history exists to date any grant or recover the
session that produced it** — the same unrecoverable-origin condition the chore's
founding `Bash(python3:*)` case had. Every "always allow" click converts a one-time
situational judgment into a permanent rule that outlives its context, with no record
of the context.
