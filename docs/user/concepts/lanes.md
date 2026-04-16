# Lanes

Lanes determine which gates must be satisfied.

---

## Lane Matrix

| Lane | Required gates | Typical trigger |
|------|----------------|-----------------|
| Lite | 1, 2 | Internal implementation, documentation, process, or template changes that do not alter an external runtime contract |
| Heavy | 1, 2, 3, 4, 5 | Command, API, schema, or other runtime-contract changes used by humans or external systems |

---

## When to Choose Which Lane

| Project type | Lane | Why |
|-------------|------|-----|
| Internal library (no public API) | Lite | No external consumers to break; TDD is sufficient proof |
| Internal tool or script | Lite | Scope is contained; documentation and BDD add overhead without audience |
| CLI with external users | Heavy | Command contracts are public surfaces; docs and acceptance tests protect adopters |
| Public API or SDK | Heavy | Breaking changes affect downstream projects; full gate coverage required |
| Schema or data model change | Heavy | Persistence contracts outlive code; human attestation catches silent drift |
| Documentation-only change | Lite | No runtime behavior changed; ADR + review is sufficient |

**Rule of thumb:** if someone outside your team could notice the change
broke something, use Heavy. If the blast radius is your own codebase, Lite.

You can upgrade from Lite to Heavy mid-ADR if scope expands (e.g., an
internal refactor grows into a public API change). Downgrading from Heavy
to Lite requires explicit justification in the ADR's Q&A section.

---

## Heavy-Lane Gate 4 Detail

Heavy lane requires BDD verification (Gate 4) to pass.

---

## Operational Implication

Even when lane requirements differ, the closeout habit order remains consistent:

1. Orientation
2. Execute through `uv run gz obpi pipeline` (wrapper skill `/gz-obpi-pipeline` remains available)
3. Verification/tool use
4. Human attestation when required
5. Guarded `git sync`
6. OBPI completion accounting
7. ADR closeout and post-attestation audit later

---

## Related

- [Gates](gates.md)
- [Workflow](workflow.md)
