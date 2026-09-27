# Surface integrity

You are here when a governance surface may be invalid or out of step: a manifest,
the ledger, a document, a mirror, CLI docs, configured paths or artifact ids.

## Steps

- **Governance validators** → **`gz-validate`**. A bare `uv run gz validate`
  runs the default tier, which `gz check` also runs; any other scope runs only
  when its flag is named.
- **CLI docs** → **`gz-cli-audit`**: every command has a manpage, an index
  link, and docs that agree with the parser.
- **Configured paths** → **`gz-check-config-paths`**.
- **Bare ids the ledger still carries after a file gained its slug** →
  **`gz-migrate-semver`**: preview, then append rename events on approval.

## Branches

- **A brief against the tree** → `gz-obpi-brief-drift`, in
  [OBPI delivery](obpi-delivery.md).
- **Mirrors out of step** → `gz-agent-sync`, in
  [Commit and sync](commit-and-sync.md).
- **A failure the validator cannot explain** → [Repair](repair.md).

## Only you can

Approve bulk ledger writes such as a rename migration; the ledger cannot be
un-appended.

## Then

[Commit and sync](commit-and-sync.md).
