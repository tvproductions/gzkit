# gz issue

Cross-repo defect/enhancement filing wrapper for gzkit-owned surfaces.

## NAME

gz-issue — file a GHI at `tvproductions/gzkit` from any consuming
repository, with an auto-stamped provenance trailer.

## SYNOPSIS

```text
gz issue file --title TITLE --body BODY \
              [--defect | --enhancement] [--dry-run]
```

## DESCRIPTION

`gz issue file` operationalizes the `Safeguard circumvention` failure
shape (codified in `.gzkit/rules/agent-failure-modes.md`) at the
cross-repo defect-filing surface. When an agent or operator working
inside a gzkit-consuming repository surfaces a defect in a gzkit-owned
artifact — the `gz` CLI itself, schemas under `src/gzkit/schemas/`,
validator scopes, ledger event semantics, files under `.gzkit/**` or
`src/gzkit/**` — the right authorization path is to file the GHI
directly at `tvproductions/gzkit` with provenance, not at the
consuming repo's tracker.

The wrapper:

1. Resolves the consuming repo's slug from `git remote -v` (`origin`
   takes precedence; SSH and HTTPS URL forms are both handled; a
   trailing `.git` suffix is stripped).
2. Reads the running gzkit version from the package metadata.
3. Composes a provenance trailer of shape
   `Filed from <owner>/<repo> running gz vX.Y.Z` and prepends it to
   the user-supplied body, separated by a blank line.
4. Validates that the body references at least one gzkit-owned
   surface marker: `gz <verb>`, `.gzkit/`, `src/gzkit/`, or
   `gzkit.<module>`. If no marker is present, the wrapper
   **hard-rejects** with exit code 1 and a diagnostic naming every
   checked marker. This closes the misrouting failure class
   structurally — an agent cannot file a misrouted issue even by
   accident.
5. Routes the issue against `tvproductions/gzkit` regardless of the
   consuming repo's `git remote`.
6. Applies either the `defect` (default) or `enhancement` label per
   the mutually-exclusive flag pair.

When `--dry-run` is set, the wrapper prints the composed body, the
target repo, the label, and the title to stdout and exits without
invoking `gh issue create` — useful for previewing the auto-stamp
output and for the BDD coverage scenarios that must not contact the
live tracker.

## OPTIONS

- `--title TITLE` — Issue title (required).
- `--body BODY` — Issue body in markdown (required). Must reference
  at least one gzkit-owned surface marker.
- `--defect` — Apply the `defect` label (default when neither flag
  is supplied; mutually exclusive with `--enhancement`).
- `--enhancement` — Apply the `enhancement` label (mutually
  exclusive with `--defect`).
- `--dry-run` — Preview the composed body, target, and label
  without invoking `gh issue create`.

Common:

- `--quiet`, `-q` — Suppress non-error output.
- `--verbose`, `-v` — Enable verbose output.
- `--debug` — Enable debug mode with full tracebacks.

## EXIT STATUS

- `0` — Success (issue created, or dry-run preview emitted).
- `1` — User/config error: body references no gzkit-owned surface,
  no `git remote` available, mutually-exclusive flags both supplied.
- `2` — System/IO error: `gh` subprocess failed (auth, network,
  GitHub API error). Stderr from `gh` propagates verbatim.
- `3` — Policy breach (reserved).

## EXAMPLES

Preview before live filing (recommended for first use):

```bash
gz issue file \
  --title "validator scope X mishandles inherited frontmatter" \
  --body "gz validate --documents miscounts adr-status drift in nested OBPIs" \
  --defect \
  --dry-run
```

File a live enhancement against gzkit:

```bash
gz issue file \
  --title "expose --json on gz issue file" \
  --body "src/gzkit/commands/issue_cmd.py could grow a --json affordance for chaining" \
  --enhancement
```

Body without a gzkit-surface marker (hard-rejected):

```bash
gz issue file \
  --title "consumer auth flow regression" \
  --body "the login helper in our app crashes after deploy" \
  --defect
# Exit 1: issue body references no gzkit-owned surface — expected at
# least one of: `gz <verb>`, `.gzkit/`, `src/gzkit/`, `gzkit.<module>`.
```

## SECURITY AND PRIVACY

- The auto-stamped trailer composes only the consumer repo slug and
  the gzkit version. **The operator's email is never derived,
  inferred, or written into the trailer or the body.** This honors
  `AGENTS.md` § Local Agent Rules — Operator PII.
- The wrapper invokes `gh issue create --repo tvproductions/gzkit`
  via `subprocess.run` with list-form argv (no `shell=True`). `gh`
  authentication is the operator's responsibility (verify with
  `gh auth status`).

## RELATED

- `.gzkit/rules/gh-cli.md` § Cross-repo filing — the doctrine
  subsection this wrapper operationalizes.
- `.gzkit/rules/agent-failure-modes.md` § Safeguard circumvention —
  the failure shape the wrapper closes.
- ADR-0.0.23-agent-failure-mode-taxonomy — parent ADR (Decision §4).
- GHI #316 — source brief.
