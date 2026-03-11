# gz obpi validate

Validate one OBPI brief for completion readiness.

---

## Usage

```bash
gz obpi validate <path-to-obpi-brief>
```

The argument is a filesystem path to the OBPI brief. Relative paths resolve from
the current workspace root.

---

## Runtime Behavior

`gz obpi validate` is the pre-completion gate for OBPI brief files whose
frontmatter `status` is `Completed`.

For completed briefs it fails closed on:

- missing or empty `Allowed Paths`
- changed files outside the OBPI allowlist
- missing or placeholder `Implementation Summary`
- missing or placeholder `Key Proof`
- missing git-sync readiness prerequisites
- missing heavy/foundation human-attestation evidence

Git-sync validation uses a syncable-state contract. Dirty work is allowed when
the changed files remain in scope; hard blockers such as "not a git repo",
merge-head state, or unsafe `SKIP` values are not.

Text mode prints `BLOCKERS:` followed by one blocker per line and exits `1`
when validation fails. Passing validation exits `0`.

---

## Example

```bash
uv run gz obpi validate docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/obpis/OBPI-0.11.0-02-obpi-completion-validator-and-git-sync-gate.md
```

```text
OBPI Validation Failed: OBPI-0.11.0-02-obpi-completion-validator-and-git-sync-gate.md
BLOCKERS:
- Changed-files audit found out-of-allowlist path: docs/user/runbook.md. Amend the OBPI or revert the change.
- Refusing completion validation with SKIP that can bypass xenon complexity checks.
```
