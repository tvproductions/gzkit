# PLAN: Go Runtime Migration with uv Ecosystem Parity

## Metadata

- Date: 2026-02-12
- Status: Draft execution plan
- Scope: Migrate `gzkit` implementation from Python to Go while preserving governance behavior
- Governance classification: Foundation (not product feature)
- Parent ADR linkage: `docs/design/adr/pool/ADR-pool.go-runtime-parity.md` (pool)

---

## Decision Framing

The product value is governance extraction, not Python itself. Therefore:

1. Governance contracts are authoritative.
2. Runtime language is replaceable.
3. Migration succeeds only when behavior is equivalent.

---

## Non-Negotiable Contracts

Freeze these before writing production Go command handlers:

1. CLI contract:
   Command names, args/options, default behavior, stdout/stderr shape, exit codes.
2. Ledger contract:
   Event schema, required fields, append-only semantics, timestamp conventions.
3. Artifact contract:
   Generated paths, filenames, template sections, and id naming rules.
4. Gate contract:
   Gate 1-5 semantics, lane behavior, and command-level verification behavior.

Deliverable: `contracts/` fixtures + conformance tests that can run against both runtimes.

---

## uv Parity Target Matrix

The goal is functional parity, not tool-name parity.

| Capability | Current Python/uv Pattern | Go Ecosystem Equivalent | Parity Requirement |
|---|---|---|---|
| Install deps + lock | `uv sync` + `uv.lock` | `go mod tidy` + `go.sum` | Deterministic, reproducible module graph |
| Run CLI locally | `uv run gz ...` | `go run ./cmd/gz ...` | Same behavior + exit codes |
| Run tests | `uv run -m unittest ...` | `go test ./...` | Same scenarios + pass criteria |
| Run one-off tools (`uvx`) | `uvx ruff ...` | `go run module@version ...` or `go install module@version` | Version-pinned tooling |
| Lint | `uvx ruff check` | `golangci-lint run` | Blocking lint gate with stable config |
| Format | `uvx ruff format` | `gofmt -w` (+ optional `goimports`) | Auto-format in CI + local workflow |
| Type checking | Python runtime + ty | Go compile-time type system (`go test`/`go build`) | Compile + test must fail on type issues |
| Task runner | ad hoc `uv run ...` commands | `Taskfile.yml` (Task) or Make | Single command UX for contributors |
| Release binaries | Python package/script entrypoint | `goreleaser` | Cross-platform binary artifacts |
| Multi-module workspace | N/A today | `go work` (if split into multiple modules) | Optional; only if repo split is needed |

Recommended stack for high `uv`-like ergonomics:

- Core: `go`, `go mod`, `go test`, `go run`
- Workflow layer: `Taskfile.yml`
- Quality: `golangci-lint`
- Release: `goreleaser`

---

## Phased Migration Plan

## Phase 0: Contract Freeze (Week 1)

1. Snapshot CLI behavior fixtures from current Python `gz`.
2. Freeze ledger schema with sample valid/invalid vectors.
3. Freeze artifact generation fixtures for `init`, `prd`, `constitute`, `specify`, `plan`.
4. Add conformance harness that can execute against a configurable binary/command.

Exit gate:

- Conformance harness validates Python baseline with zero failures.

## Phase 1: Go Skeleton + Read-only Commands (Week 2)

1. Create Go module and `cmd/gz` entrypoint.
2. Implement `state`, `status`, `validate` in Go.
3. Run conformance checks in CI against Python and Go for these commands.

Exit gate:

- Read-only command parity is green across macOS + Linux + Windows.

## Phase 2: Artifact Writers (Weeks 3-4)

1. Implement `init`, `prd`, `constitute`, `specify`, `plan` in Go.
2. Validate generated files byte-stably where practical, structurally where dynamic.
3. Enforce ledger append parity for corresponding events.

Exit gate:

- Artifact and ledger parity checks all green.

## Phase 3: Execution Commands (Weeks 5-6)

1. Implement `gates`, `attest`, `git-sync`/`sync-repo`, and quality command wrappers.
2. Keep external tool commands configurable per platform.
3. Add failure-mode parity tests (missing files, invalid args, command failures).

Exit gate:

- Exit code parity + error-message class parity + ledger parity.

## Phase 4: Shadow and Cutover (Week 7)

1. Ship Go binary as opt-in while Python remains default.
2. Run shadow mode in CI for one full cycle.
3. Promote Go as default after parity threshold is met.

Cutover criteria:

1. 100% pass on contract tests.
2. No schema drift in ledger events.
3. No critical UX regressions in docs/runbook commands.

---

## Repo Changes to Schedule Next

1. Add `cmd/gz/` and `internal/` layout for Go runtime.
2. Add `contracts/cli`, `contracts/ledger`, `contracts/artifacts` fixtures.
3. Add `Taskfile.yml` with parity targets:
   - `task test`
   - `task lint`
   - `task format`
   - `task conformance`
4. Add CI matrix for Python baseline + Go parity jobs.

---

## Risks and Mitigations

1. Risk: Semantic drift during rewrite.
   Mitigation: Contract-first conformance harness and blocked merge on parity failures.
2. Risk: Tooling sprawl vs `uv` simplicity.
   Mitigation: One user-facing `task` command layer; hide raw tool complexity.
3. Risk: Governance artifacts get coupled to runtime internals.
   Mitigation: Keep templates/schemas/docs runtime-agnostic and contract-tested.

---

## Immediate Next Actions

1. Create a pool ADR specifically for runtime migration (proposed: `ADR-pool.go-runtime-parity`).
2. Promote to a foundation SemVer ADR when prioritized.
3. Create OBPIs only after promotion out of pool.
4. Stand up empty Go CLI skeleton and conformance harness scaffold under the promoted ADR.
