# Consent Drift Ledger — Pass D run 2026-07-16

Context-free prohibitions (CF-1 … CF-6 from `doctrine-map.md`) walked against
180 allow rules across both permission surfaces. Deny rules take precedence over
allow, so a hit covered by a deny is `neutralized`, not `live`.

| Doctrine | Citation | Prohibited | Allow rule (verbatim) | Source | Severity | Neutralizing deny |
|---|---|---|---|---|---|---|
| CF-1 | `AGENTS.md:247 § Execution Rules` | bare python / python3 | — | — | **clean** | no allow rule grants this |
| CF-2 | `AGENTS.md:145 § Never #10` | --no-verify / git commit -n | — | — | **clean** | no allow rule grants this |
| CF-3 | `AGENTS.md:94 § STDLIB-FIRST; tests.md:16` | pytest | — | — | **clean** | no allow rule grants this |
| CF-4 | `AGENTS.md:322 § Local Agent Rules` | PYTHONUTF8=1 uv run gz | — | — | **clean** | no allow rule grants this |
| CF-5 | `AGENTS.md:137 § Never #2` | Edit of .gzkit/ledger.jsonl | — | — | **clean** | no allow rule grants this |
| CF-6 | `AGENTS.md:342 § Operator Doctrine` | git checkout -b / git switch -c | — | — | **clean** | no allow rule grants this |

## Counts

- **live** (no deny covers it): **0**
- rows total: 6
- allow rules walked: 180 (180 local + 0 shared)
- deny rules consulted: 6

## Reading this ledger

A short ledger is **not** evidence of a clean surface. Three of nine command-shaped
prohibitions in `AGENTS.md` are structurally invisible to this pass, and broad allow
rules are invisible regardless of doctrine. See `unwitnessable.md` — it is a required
acceptance artifact for exactly this reason.
