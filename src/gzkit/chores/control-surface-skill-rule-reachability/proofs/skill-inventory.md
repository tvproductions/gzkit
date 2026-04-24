# Skill Inventory (Pass B — Control-Surface Skill/Rule Reachability)

Enumerates every `SKILL.md` under `.gzkit/skills/` (56 total, incl. archived). Skill frontmatter uses no `paths:` field (that is rules-only convention); applicability is therefore determined by CLI verbs invoked in body and by the file surfaces the skill procedure modifies.

Body-cited rules = explicit `rules/<file>.md` references in the skill body. CLI verbs listed here are those invoked or referenced in the skill procedure (`uv run gz ...`).

---

## `airlineops-parity-scan` (v1.1.1)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz cli audit`, `gz check-config-paths`, `gz adr audit-check`, `mkdocs build --strict`

## `format` (ARCHIVED)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz format`, `gz check`

## `git-sync` (v1.2.2)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz git-sync`, `gz git-sync --apply`, `gz init`

## `gz-adr-audit` (v6.4.0)

- gz_command: audit
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz adr audit-check`, `gz audit`, `gz cli audit`, `gz gates`, `gz lint`, `gz test`, `gz typecheck`, `gz validate --documents`, `mkdocs build`, `gz adr emit-receipt`, `gz adr report`, `gz check-config-paths`

## `gz-adr-autolink` (v1.1.0)

- gz_command: workflow
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `rg '@covers("ADR-' tests`, `gz adr audit-check`, `gz lint`

## `gz-adr-check` (ARCHIVED)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: —

## `gz-adr-closeout-ceremony` (v7.7.0)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz closeout --ceremony`, `gz closeout --ceremony --ceremony-status`, `gz closeout --ceremony --next`, `gz closeout --ceremony --attest`, `gz closeout`, `gz lint`, `gz test --bdd`, `gz typecheck`, `gz validate --documents`, `mkdocs build --strict`, `gz adr status`, `gz git-sync --apply`, `gh issue list`, `gh issue close`, `gh release create`

## `gz-adr-create` (v6.2.0)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz interview adr`, `gz adr create` (implied)

## `gz-adr-emit-receipt` (v1.0.1)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz adr emit-receipt`

## `gz-adr-evaluate` (v6.2.0)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz adr evaluate`

## `gz-adr-manager` (ARCHIVED)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: —

## `gz-adr-map` (v1.1.0)

- gz_command: state
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz state`, `rg '@covers("ADR-' tests`, `gz adr audit-check`

## `gz-adr-promote` (v1.1.1)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz status`, `gz validate`, `gz adr promote` (implied)

## `gz-adr-recon` (v1.1.0)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz adr status`, `gz adr audit-check`, `gz status`, `gz lint`

## `gz-adr-status` (v1.12.0)

- gz_command: adr status
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz adr report`, `gz adr status`

## `gz-adr-sync` (v6.1.0)

- gz_command: register-adrs
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz register-adrs`, `gz status`

## `gz-adr-verification` (ARCHIVED)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `rg '@covers("ADR-' tests`

## `gz-agent-sync` (v1.1.1)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz agent sync`, `gz skill audit`

## `gz-arb` (v1.0.1)

- gz_command: arb advise
- paths: —
- Body-cited rules: `arb.md`, `attestation-enrichment.md`
- CLI verbs invoked in body: `gz arb ruff`, `gz arb typecheck`, `gz arb step --name unittest`, `gz arb coverage`, `gz arb validate`, `gz arb advise`, `gz arb patterns`

## `gz-attest` (ARCHIVED)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: —

## `gz-audit` (ARCHIVED)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: —

## `gz-check` (v1.4.0)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz lint`, `gz format`, `gz typecheck`, `gz test`, `gz test --bdd`, `gz check`, `gz validate --surfaces`, `gz status`, `gz state`

## `gz-check-config-paths` (— )

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz check-config-paths`

## `gz-chore-runner` (v1.1.1)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz chores list`, `gz chores show`, `gz chores plan`, `gz chores advise`, `gz chores run`, `gz chores audit`

## `gz-cli-audit` (— )

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz cli audit`

## `gz-closeout` (ARCHIVED)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: —

## `gz-constitute` (— )

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz constitute` (implied)

## `gz-design` (v1.1.0)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz status --table`, `gz state --json`

## `gz-gates` (v1.0.0)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz gates`

## `gz-implement` (— )

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz implement` (implied)

## `gz-init` (v6.0.1)

- gz_command: init
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz init`, `gz status`, `gz state`

## `gz-interview` (ARCHIVED)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz interview adr`, `gz interview obpi`, `gz interview prd`

## `gz-migrate-semver` (— )

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz migrate semver` (implied)

## `gz-obpi-audit` (ARCHIVED)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: — (forwards to gz-obpi-reconcile)

## `gz-obpi-brief` (ARCHIVED)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz specify` (referenced)

## `gz-obpi-lock` (v6.0.2)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz obpi lock claim`, `gz obpi lock release`, `gz obpi lock check`, `gz obpi lock list`

## `gz-obpi-pipeline` (v6.8.0)

- gz_command: —
- paths: —
- Body-cited rules: `defect-fix-routing.md`, `attestation-enrichment.md` (inline reference at line 493)
- CLI verbs invoked in body: `gz obpi pipeline`, `gz obpi reconcile`, `gz obpi complete`, `gz obpi lock claim/release`, `gz lint`, `gz typecheck`, `gz test --obpi`, `gz test --bdd`, `gz validate --documents`, `mkdocs build --strict`, `gz covers`, `gz git-sync --apply`, `gz roles --pipeline`

## `gz-obpi-reconcile` (v3.0.3)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz obpi reconcile`, `rg '@covers'`, Grep tool

## `gz-obpi-simplify` (v6.0.4)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz obpi simplify` (implied)

## `gz-obpi-specify` (v1.4.0)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz specify`, `gz obpi validate --adr --authored`, `gz register-adrs`

## `gz-obpi-sync` (ARCHIVED)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: —

## `gz-patch-release` (v1.2.0)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz patch release`, `gz patch release --dry-run`, `gz git-sync --apply`, `gh release create`

## `gz-plan` (v1.0.0)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz plan`, `gz plan create`

## `gz-plan-audit` (v6.2.0)

- gz_command: —
- paths: —
- Body-cited rules: `attestation-enrichment.md`
- CLI verbs invoked in body: `gz plan audit`

## `gz-prd` (— )

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz prd` (implied)

## `gz-register-adrs` (ARCHIVED)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz register-adrs` (referenced)

## `gz-session-handoff` (v6.2.0)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz session handoff` (implied)

## `gz-skill-router` (v6.0.2)

- gz_command: —
- paths: —
- Body-cited rules: `defect-fix-routing.md`
- CLI verbs invoked in body: — (routing table referencing other skills)

## `gz-specify` (RENAMED)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz specify` (referenced)

## `gz-state` (— )

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz state`

## `gz-status` (— )

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz status`

## `gz-tidy` (v1.1.1)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz tidy --check`, `gz tidy --fix`, `gz status`, `gz state`

## `gz-typecheck` (ARCHIVED)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz typecheck` (referenced)

## `gz-validate` (— )

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz validate`

## `lint` (ARCHIVED)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz lint` (referenced)

## `test` (ARCHIVED)

- gz_command: —
- paths: —
- Body-cited rules: —
- CLI verbs invoked in body: `gz test` (referenced)

---

## Notes

- 56 SKILL.md files total. 15 carry `ARCHIVED` or `RENAMED` forwarder shape.
- Only 3 skills cite rules in body: `gz-arb` (arb.md + attestation-enrichment.md), `gz-obpi-pipeline` (defect-fix-routing.md + attestation-enrichment.md), `gz-skill-router` (defect-fix-routing.md), and `gz-plan-audit` (attestation-enrichment.md).
- No skill file uses `paths:` frontmatter. Applicability basis (a) is therefore empty across the matrix; bases (b) CLI-verb and (c) file-surface drive all rows.
