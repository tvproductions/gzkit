# gz adr demote

Demote a feature or foundation ADR back to pool — the inverse of `gz adr promote`. Strips `kind`/`semver` from frontmatter, moves the ADR file from `pre-release/` or `foundation/` to `pool/`, deletes the source package directory (briefs, closeout form), and emits an `artifact_renamed` ledger event with `reason="pool_demotion"`.

Authored under GHI #521 as the Day-0 tooling prerequisite for the get-out-of-jail prequel sweep (GHI #520).

---

## Usage

```bash
gz adr demote <ADR-ID> --ghi <NUMBER> [OPTIONS]
```

---

## Options

| Option | Type | Description |
|--------|------|-------------|
| `--ghi` | int | **Required.** GitHub Issue number this demotion is tracked under. Every demotion must be auditable. |
| `--note` | string | Free-text operator rationale; stored in the ledger event extras. |
| `--operator` | string | Operator identity (name only; never email per Local Agent Rules). Defaults to omitted. |
| `--dry-run` | flag | Show planned actions without writing files or ledger events. |
| `--json` | flag | Emit a structured JSON result payload to stdout. |
| `--force` | flag | Override the dependent-children safety check (exit 3). Orphans any ADRs whose `parent:` frontmatter points at the demoted ADR. |
| `--on-collision` | choice | How to handle a pre-existing pool file at the target slug. `fail` (default) blocks; `keep-pool` deletes the source feature/foundation package and leaves the existing pool ADR untouched. The ledger event records `collision_resolution: "keep-pool"` when this path is taken. |

---

## Behavior (Enforced)

1. Source ADR must be `feature` or `foundation` kind with a valid `semver` field. Pool ADRs are rejected (already pool — nothing to demote).
2. Pool target id is derived as `ADR-pool.<slug>`, where `<slug>` comes from the source ADR's id (`ADR-X.Y.Z-<slug>` → `<slug>`).
3. Target file path: `docs/design/adr/pool/ADR-pool.<slug>.md`.
4. **Collision check.** If the pool target file already exists, the demotion is rejected (exit 1) by default. Passing `--on-collision keep-pool` resolves the collision by deleting the source feature/foundation package and leaving the existing pool ADR untouched; the ledger event records the resolution.
5. **Frontmatter strip.** `kind`, `semver`, and frontmatter `date` are removed. `id` is rewritten to the pool id. `status` is set to `Pool`. Other fields (`lane`, `parent`, `inspired_by`, etc.) are preserved.
6. **OBPI briefs deleted.** Per the 2026-05-23 get-out-of-jail prequel Q1=b decision, pool ADRs carry no OBPIs by doctrine; brief files under `<source-dir>/obpis/` are deleted via the source-dir removal. Briefs are re-authored if the ADR is later re-promoted.
7. **Source directory removed.** The entire `docs/design/adr/{pre-release,foundation}/<source-id>/` directory is deleted (taking the briefs, closeout form, and any other authoring artifacts with it).
8. **Dependent children check** (fail-closed). If any other non-pool ADR has `parent: <source-id>` in its frontmatter, demotion is rejected with exit 3. Pass `--force` to orphan those children deliberately.
9. **Ledger event.** A single `artifact_renamed` event is appended with `reason="pool_demotion"` and the following extras:

   ```json
   {
     "prior_kind": "feature",
     "prior_semver": "0.27.0",
     "demoted_at": "<RFC 3339 UTC timestamp>",
     "ghi": 520,
     "operator": "<optional>",
     "note": "<optional>"
   }
   ```

Per state doctrine (Layer 2 ledger = source of truth for state transitions), the demote event is the canonical record of the prior life. Pool files do not carry `previously:` frontmatter; `gz state <pool-id>` is the query path.

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Demotion completed (or dry-run succeeded). |
| 1 | User/config error: missing `--ghi`, pool target collision, ADR already pool, missing `kind`/`semver`. |
| 2 | System/IO error: frontmatter parse failure, ledger write failure. |
| 3 | Policy breach: dependent children exist; `--force` overrides. |

---

## Examples

```bash
# Preview demotion (mandatory --ghi)
gz adr demote ADR-0.27.0-arb-receipt-system-absorption --ghi 520 --dry-run

# Short-form ADR id resolves the same source
gz adr demote ADR-0.27.0 --ghi 520 --dry-run

# Apply demotion with operator-supplied rationale
gz adr demote ADR-0.27.0 --ghi 520 --note "prequel queue collapse"

# JSON output for scripted sweeps
gz adr demote ADR-0.27.0 --ghi 520 --json

# Override dependent-children safety (orphans the children)
gz adr demote ADR-0.27.0 --ghi 520 --force

# Resolve a pool-slug collision by keeping the existing pool ADR
gz adr demote ADR-0.42.0 --ghi 520 --on-collision keep-pool
```

---

## See Also

- `gz adr promote` — the forward inverse motion.
- `docs/governance/get-out-of-jail-plan-2026-05-23.md` § Prequel (Day 0) — the canonical destination doc.
- GHI [#520](https://github.com/tvproductions/gzkit/issues/520) — the 24-ADR sweep this verb enables.
- GHI [#521](https://github.com/tvproductions/gzkit/issues/521) — the tracking GHI for this verb's authoring.
