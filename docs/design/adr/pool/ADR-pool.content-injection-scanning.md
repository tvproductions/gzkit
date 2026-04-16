---
id: ADR-pool.content-injection-scanning
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: nousresearch/hermes-agent skills_guard.py memory_tool.py
---

# ADR-pool.content-injection-scanning: Content-Layer Injection Detection for Skills and Governance Artifacts

## Status

Pool

## Date

2026-04-16

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Add regex-based content scanning for prompt injection, exfiltration patterns,
and destructive commands in skill files, memory writes, and governance
artifacts so that content-layer attacks are detected before they reach the
agent's context window.

---

## Target Scope

- Implement a content scanner with pattern categories: prompt injection (role hijack, system message spoofing), exfiltration (curl/wget with secrets, credential store access, DNS exfiltration, env variable dumping), destructive commands (recursive delete, force push, database drop), obfuscation (invisible Unicode characters, base64-encoded payloads, homograph URLs).
- Scan triggers: skill file load (before SKILL.md enters context), `agent-insights.jsonl` writes, ledger attestation text, any user-provided string passed to `--attestation-text` or `--evidence-json` CLI flags.
- Define trust tiers for skill sources: `canonical` (`.gzkit/skills/` — trusted, scan advisory), `user` (user-contributed — scan enforced, findings block load), `external` (third-party — scan enforced, dangerous findings block load).
- Add `gz scan <path>` CLI surface for on-demand content scanning.
- Emit scan results as structured findings (pattern ID, category, severity, file, line, matched text).

---

## Non-Goals

- No code-level static analysis (bandit, semgrep) — that is ADR-pool.agentic-security-review's scope.
- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No runtime monitoring — this is pre-load content scanning, not execution-time detection.
- No machine-learning-based detection — regex patterns are deterministic, auditable, and fast.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: ADR-pool.agentic-security-review (code-layer scanning; this ADR covers content-layer scanning — complementary attack surfaces), ADR-pool.skill-behavioral-hardening (hardened skills are less likely to contain injection patterns, but scanning catches what hardening misses)

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Pattern categories and severity thresholds are agreed upon.
3. Trust tier model for skill sources is accepted.

---

## Inspired By

[NousResearch/hermes-agent](https://github.com/nousresearch/hermes-agent) —
implements five security layers: `path_security.py` (traversal validation),
`approval.py` (~40 regex patterns for dangerous commands),
`tirith_security.py` (content-level threat scanning), `skills_guard.py`
(~50 threat patterns across exfiltration, injection, destruction, obfuscation
categories with trust-level policy: builtin/trusted/community/agent-created),
and memory injection scanning in `memory_tool.py` (invisible Unicode, role
hijack phrases, curl/wget with secret variables). The layered approach —
different scanners at different trust boundaries — is the transferable pattern.

---

## Notes

- Hermes's `skills_guard.py` uses ~50 regex patterns across 6 categories. Not all apply to gzkit — filter for patterns relevant to governance artifacts (e.g., exfiltration and injection patterns matter; persistence and lateral movement patterns are less relevant in a CLI tool).
- Hermes scans memory writes for invisible Unicode characters (zero-width spaces, RTL overrides). This is cheap to implement and catches a real attack vector where injected instructions are visually hidden.
- The scanner should be fast enough to run on every skill load without perceptible latency. Regex scanning over a typical SKILL.md (~2KB) is sub-millisecond.
- Consider: should scan findings be ledger events? A detected injection attempt in an attestation string is a governance-significant event worth recording.
