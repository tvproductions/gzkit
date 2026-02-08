# Commands

All commands use the `gz` prefix.

Command reference pages are gzkit's manpages and are part of Gate 3 proof.

---

## Governance

| Command | Description |
|---------|-------------|
| [`gz init`](init.md) | Initialize gzkit in your project |
| [`gz prd`](prd.md) | Create a Product Requirements Document |
| [`gz constitute`](constitute.md) | Create a constitution |
| [`gz specify`](specify.md) | Create an implementation brief |
| [`gz plan`](plan.md) | Create an Architecture Decision Record |
| [`gz implement`](implement.md) | Run Gate 2 (tests) and record results |
| [`gz gates`](gates.md) | Run applicable gates for the current lane |
| [`gz status`](status.md) | Show gate status for current work |
| [`gz state`](state.md) | Query ledger and artifact relationships |
| [`gz git-sync`](git-sync.md) | Sync branch with guarded lint/test/git ritual |
| [`gz attest`](attest.md) | Record human attestation |
| [`gz migrate-semver`](migrate-semver.md) | Record SemVer ID renames in the ledger |
| [`gz register-adrs`](register-adrs.md) | Register existing ADR files missing from ledger |

---

## Quality

| Command | Description |
|---------|-------------|
| `gz check` | Run all quality checks |
| `gz lint` | Run linting |
| `gz format` | Auto-format code |
| `gz test` | Run tests |
| `gz typecheck` | Run type checking |

---

## Maintenance

| Command | Description |
|---------|-------------|
| `gz validate` | Validate governance artifacts |
| `gz agent sync control-surfaces` | Regenerate control surfaces |
| `gz tidy` | Run maintenance checks |

Compatibility aliases:
`gz sync` and `gz agent-control-sync` map to `gz agent sync control-surfaces` and print deprecation guidance.

---

## Utilities

| Command | Description |
|---------|-------------|
| `gz interview <type>` | Guided document creation |
| `gz skill new <name>` | Create a new skill |
| `gz skill list` | List available skills |

---

## Global Options

All commands support:

| Option | Description |
|--------|-------------|
| `--help` | Show command help |
| `--version` | Show gzkit version |
