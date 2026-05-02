# gz issue file

File a defect or enhancement at `tvproductions/gzkit` from any consuming
repository, with an auto-stamped provenance trailer.

---

## Usage

```bash
gz issue file --title TITLE --body BODY \
              [--defect | --enhancement] [--dry-run]
```

---

## Runtime Behavior

The wrapper resolves the consuming repo's slug from `git remote -v`
(`origin` precedence; SSH and HTTPS forms; `.git` suffix stripped),
reads the running gzkit version from package metadata, prepends a
`Filed from <slug> running gz vX.Y.Z` trailer to the body, validates
that the body references at least one gzkit-owned surface marker
(`gz <verb>`, `.gzkit/`, `src/gzkit/`, `gzkit.<module>`), and either
previews the result (`--dry-run`) or invokes `gh issue create --repo
tvproductions/gzkit` with the chosen label.

Bodies that reference no gzkit-owned surface are **hard-rejected**
(exit 1) — the misrouting class is closed structurally per
`.gzkit/rules/agent-failure-modes.md` § Safeguard circumvention.

The default label is `defect`. `--defect` and `--enhancement` are
mutually exclusive.

---

## Options

| Flag | Description |
|------|-------------|
| `--title TITLE` | Issue title (required). |
| `--body BODY` | Issue body in markdown (required). |
| `--defect` | Apply the `defect` label (default). |
| `--enhancement` | Apply the `enhancement` label. |
| `--dry-run` | Preview composed body, target repo, and label without invoking `gh`. |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (issue created or dry-run preview emitted). |
| 1 | User/config error (body references no gzkit surface; no git remote; mutually-exclusive flag conflict). |
| 2 | System/IO error (`gh` subprocess failure). |
| 3 | Reserved (policy breach). |

---

## Examples

Preview before live filing:

```bash
gz issue file \
  --title "validator scope X mishandles inherited frontmatter" \
  --body "gz validate --documents miscounts adr-status drift" \
  --defect \
  --dry-run
```

File a live enhancement:

```bash
gz issue file \
  --title "expose --json on gz issue file" \
  --body "src/gzkit/commands/issue_cmd.py could grow a --json affordance" \
  --enhancement
```

---

## Related

- Manpage: `docs/user/manpages/gz-issue.md`
- Doctrine: `.gzkit/rules/gh-cli.md` § Cross-repo filing
- Failure shape: `.gzkit/rules/agent-failure-modes.md` § Safeguard circumvention
- Parent ADR: ADR-0.0.23-agent-failure-mode-taxonomy
- Source brief: GHI #316
