# Unwitnessable Ledger — Pass D

> Chore: `control-surface-permission-consent-drift` (Lite lane, advisory)
> Run: **2026-10-10**, maintenance visit E. Supersedes the 2026-08-09 ledger.

**This artifact is the point of the chore as much as the drift ledger** (CHORE.md § 4). It is
the record of what was not checked. **20 entries here against 0 drift rows.**

## A. Context-dependent prohibitions — the hard ceiling (12)

Permission rules are context-free string matches. Where doctrine forbids an act in a context,
the sanctioned and forbidden invocations are the same string. Numbers are `doctrine-map.md` rows.

| # | Prohibition | Why no pattern can audit it |
|---|---|---|
| U1 (17) | `gh issue create` outside `ghi-author` | the skill's own Step 5 runs the identical command; **load-bearing, never drift** |
| U2 (18) | independent OBPI lock, TASK, marker, dispatch or brief acts | the operator's initiation is the context; `gz obpi lock claim` is the same string either way |
| U3 (19) | Gate 5 by anyone but the operator | `--attestor g0 --attestation-text "…"` is typed by the agent relaying the operator; the words are the witness, not the command |
| U4 (20) | launching unrequested implementation | no command names "unrequested" |
| U5 (21) | masking a verifier's exit status | position in a pipeline; **this one has a mechanical witness**, the `verifier-pipe-gate` PreToolUse hook on `Bash` |
| U6 (22) | `gz mx enter` / `exit` outside the skill | same string from the skill and from a shell step |
| U7 (23) | `gz audit` before attestation | temporal; the verb is reported to refuse an unattested ADR (not observed this run) |
| U8 (24) | reaping a lock before expiry | `--force` is the operator's flag; the string does not say who typed it |
| U9 (25) | filing a GHI to satisfy a trailer | motive |
| U10 (26) | editing the security registry without a sensitivity declaration | the declaration lives in a brief or a commit body |
| U11 (27) | an ordinary session resizing a render surface | "ordinary" is the context |
| U12 (28) | silent threshold edits | validator-witnessed, not permission-expressible |

## B. Broad allow rules this pass structurally cannot audit (4)

A drift row needs a rule that mentions the token. These four mention none and cover a great deal.

**U13 — `Bash(uv run gz:*)`.** Every `gz` verb, including the ones rows U2, U3, U6 and U7 reserve
to the operator or to a skill: `gz obpi lock claim`, `gz task start`, `gz obpi complete --attestor`,
`gz attest`, `gz obpi repudiate`, `gz mx enter`, `gz audit`, and the outward-facing
`gz git-sync --apply` (commits and pushes), `gz issue file` (creates an issue) and
`gz content land --attestor` (changes canon). The file's own `_comment` says mutating and
outward-facing commands "are deliberately absent so they still prompt". Under this rule they
do not prompt. This session ran `gz git-sync --apply` after every visit and landed the corpus three
times with `gz content land --attestor g0` (the landings are in the ledger); both strings match it.

**U14 — `Bash(uv run -m:*)`.** Any module: `uv run -m gzkit <verb>` is U13 again by another
spelling, and `uv run -m pytest` and `uv run -m pip` are covered without being named
(doctrine rows 1 and 7).

**U15 — `Bash(find:*)`.** `find` with `-delete` or `-exec` is a write channel under a rule the
`_comment` calls read-only.

**U16 — `Bash(cat:*)`, `head`, `tail`, `grep`, `rg`, `jq` against the `Read(...)` deny rules.**
Whether a `Read(.env)` deny stops `cat .env` under a standing `Bash(cat:*)` allow was **not
tested** (it would mean reading a secret-shaped file to find out). Recorded as unknown.

## C. Limits found by observing the session that ran this audit (4)

**U17 — The permission prompt is not an interposition point in every session.** The harness
reported this session as running in an auto permission mode. Commands that no allow rule grants
ran in it: `git commit`, `git add`, `gh issue create`, `gh issue comment`, and a bare interpreter.
Whether any prompt was shown to the operator cannot be observed from inside the session. The
chore's premise, that the prompt is "the one mechanical interposition point", holds only for a
session whose mode prompts; the permission files say nothing about the others.

**U18 — A context-free prohibition was broken 40 times with nothing observing it.** Doctrine row 1
("always `uv run` for Python commands"): the session ran `python3` 39 times and `python` once,
counted from its own transcript (530 Bash calls). No allow rule grants it, no deny rule forbids
it, no hook looks for it, and `gz validate --utf8-prefix` checks documents, not commands.
Insight scope `session/uv-run-rule`. Two written procedures breach the same clause:
`gz-deps-upgrade/SKILL.md:85` and `frontier-model-card-currency/CHORE.md:103`.

**U19 — File writes through `Bash` bypass every write hook and all path-scoped rule loading.**
The hooks that guard writes are matched on `Write|Edit|NotebookEdit`. This session made 96
file-writing Bash calls and no Edit or Write call across maintenance visits A to D, so
`pipeline-gate`, `obpi-completion-validator`, `instruction-router`, `session-staleness-check`,
`post-edit-ruff` and `ledger-writer` never fired. `chores.md` loaded into the session for the
first time when this run used a file tool on a `.gzkit/chores/` path, after 36 Bash calls had
written into that tree. One consequence was observed the same day: an edit to the generated
`src/gzkit/chores/` copy of a library was silently reverted by the next sync. August recorded the
class in one sentence ("A `cp` is a file write the hook layer does not observe"); this is its
measured size. Insight scope `hooks/bash-write-blindness`.

**U20 — A path-scoped rule does not load when its subject is a command.** `gh-cli.md` is scoped to
`.github/**`, `docs/design/adr/**` and one source file. Running `gh issue comment` touches none
of them, so the rule that governs the command is not in context when the command runs. This
session posted a comment on GHI #997 whose last paragraph narrates progress, which the rule
forbids ("A comment is not a place to narrate progress"). The comment is a dated record and is
not edited.

## Known coverage limits (CHORE.md, restated verbatim in the summary)

Context-dependence, broad-rule blindness, CI-blindness and curated-list drift. Section C adds a
fifth that the chore text does not name: **mode-blindness** (U17).
