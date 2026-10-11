# Consent Drift Ledger — Pass D

> Chore: `control-surface-permission-consent-drift` (Lite lane, advisory)
> Run: **2026-10-10**, maintenance visit E. Supersedes the 2026-08-09 ledger.

A drift row is an allow rule that **mentions** a command token a context-free prohibition
forbids. Sixteen context-free doctrine rows (`doctrine-map.md` rows 1 to 16) were walked against
25 allow rules.

## Rows

| Severity | Count |
|---|---|
| `live` | **0** |
| `neutralized` | 0 |
| `historical` | 0 |

**No allow rule on either surface names a prohibited token.** The walk, row by row:

| Doctrine row | Tokens | Allow rules mentioning a token |
|---|---|---|
| 1 `uv run` for Python | `python`, `python3`, `pip` | none |
| 2 ledger only through `gz` | writers to `.gzkit/ledger.jsonl` | none |
| 3 commit through hooks | `--no-verify`, `commit -n`, `hooksPath`, `SKIP=` | none; no `git commit` or `git push` is allowed at all |
| 4 `PYTHONUTF8=1` prefix | `PYTHONUTF8=1` | none |
| 5 operator PII | `git config user.email`, `--author` | none |
| 6 no branches | `git checkout -b`, `git switch -c`, `git branch`, `git merge` | none; allowed git verbs are `status`, `log`, `diff`, `show`, `rev-parse`, `rev-list`, `fetch` |
| 7 no pytest | `pytest` | none |
| 8, 9, 10 generated surfaces | writes, `cp`, `mv` into mirrors and package copies | none |
| 11 suppression writers | `--add-noqa`, `--add-ignore` | none |
| 12 raw SQL | `sqlite3`, `psql` | none |
| 13 `gh` settings, secrets, force push, PR merge | `gh repo`, `gh secret`, `gh auth`, `git push --force`, `gh pr merge` | none; allowed `gh` verbs are `issue list`, `issue view`, `run list`, `run view` |
| 14 `gh` verbs outside the rule's allowlist | `gh issue edit` | none. Note the reverse: `gh issue view` is granted here and prescribed by skills, and `gh-cli.md` § Allowed commands does not list it |
| 15 release notes by hand | writes to `RELEASE_NOTES.md`, `CHANGELOG.md` | none |
| 16 harness session trailer | `Claude-Session:` | none |

## The August rows, accounted for

D1 (`SKIP=gitleaks … git-sync`), D2 (five `cp` grants into mirrors), D3, D4, D5 (`live`) and D6
(`neutralized`) all lived in the 180-rule local file. That file was lost and rebuilt on
2026-08-29 with 25 rules; none of the six survives. They are **closed by reconstruction**, not
by a repair: nothing was decided about them. The `SKIP=` channel behind D1 is still undefended
by any deny rule (see `settings-patch.md`).

## Reading this ledger

An empty drift ledger measures what a string match can see. Read it beside
[`unwitnessable.md`](unwitnessable.md), which this run grew from 14 entries to 20, and beside
the observed breaches recorded there: a clean permission file did not stop a context-free
prohibition from being broken 40 times in the session that produced this ledger.
