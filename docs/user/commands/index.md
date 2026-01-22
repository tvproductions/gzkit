# Commands

All commands use the `gz` prefix.

---

## Governance

| Command | Description |
|---------|-------------|
| [`gz init`](init.md) | Initialize gzkit in your project |
| [`gz prd`](prd.md) | Create a Product Requirements Document |
| [`gz specify`](specify.md) | Create an implementation brief |
| [`gz plan`](plan.md) | Create an Architecture Decision Record |
| [`gz status`](status.md) | Show gate status for current work |
| [`gz state`](state.md) | Query ledger and artifact relationships |
| [`gz attest`](attest.md) | Record human attestation |

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
| `gz sync` | Regenerate control surfaces |
| `gz tidy` | Run maintenance checks |

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
