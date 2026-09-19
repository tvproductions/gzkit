# Three-pillars repair evidence

Dated 2026-09-19. Parent: [implementation plan](three-pillars-implementation-plan-2026-09-19.md).
Baseline: `d6bc23d0ebef83a1b3391c521e35931f5f8013b6`.
Persona: main-session — craftsperson, governance-aware, whole-file reasoning, direct.

Two study leads were independently reproduced, checked against current intent
and terminal historical ownership, and repaired through separate defect GHIs.
Neither alters the acceptance authority or initiates feature work.

## GHI #1049: equivalent mirror-path refusal

Before repair, with an existing generated file:

```text
'.claude/rules/example.md' ['Allowed path is a generated vendor mirror; edit canonical surface instead: .claude/rules/example.md -> .gzkit/rules/example.md']
'./.claude/rules/example.md' []
```

The shared helper now removes one literal `./` before both classification and
canonical-tail slicing. It keeps dotfile roots and the existing mirror roster.
All three consumers retain their existing control flow: plan audit, authored
brief validation, and promotion's post-write checks with its existing force
behavior. Manpages describe refusal and CREATE boundaries.

| Failure mechanism / preserved behavior | Committed witness |
|---|---|
| Relative prefix changes mirror classification or canonical suffix | `TestVendorMirrorCanonical.test_relative_prefix_preserves_canonical_advice_for_every_mirror` |
| Existence or brief/plan CREATE bypasses shared consumer refusal | `TestRelativeMirrorPaths.test_brief_and_plan_creates_cannot_exempt_relative_mirrors` |
| Normalization accidentally refuses a legitimate canonical CREATE | `TestRelativeMirrorPaths.test_relative_canonical_creates_remain_valid` |

RED, before the source edit:

```text
Ran 45 tests in 0.035s
FAILED (failures=85)
```

GREEN, including relevant existing consumer tests:

```text
Ran 110 tests in 0.073s
OK
```

Independent review ran the focused 45-test suite and a separate real-brief probe
covering 150 mirror combinations plus two promotion canonical CREATE controls.
It found no remaining contract gap. The matrix covers the five existing mappings,
both spellings, root/trailing/file/nested/glob forms and missing/existing/CREATE
states. No general traversal or symlink-policy guarantee is claimed.

## GHI #1050: configured source-root discovery

Before repair, real collectors received configuration with `source_root=lib`:

```text
loaded_source_root: lib
relocated_only_collector: []
relocated_only_command: {"valid": true, "issues": []} exit: 0
both_trees_collector: [{"path": "src/gzkit/bad.py", "issue": "unmapped path literal: \"artifacts/stale-default-missing\""}]
```

The collector now selects `config.paths.source_root / gzkit`, preserving its
package boundary, recursion, literal classifier and module-local exemptions.
The manpage describes that population. The configured value selects the source
tree; it does not widen which literals are exempt.

| Failure mechanism / preserved behavior | Committed witness |
|---|---|
| Stale default source substitutes for configured nested source | `TestConfiguredSourceRoot.test_configured_root_replaces_default_and_scans_nested_modules` |
| Omission propagates a false valid JSON result and successful exit | `TestConfiguredSourceRoot.test_command_rejects_unmapped_literal_in_configured_source` |
| Existing classification, default layout and local exemptions | Existing classes in `tests/test_config_paths.py`, included in the 23-test run |

RED and GREEN:

```text
Ran 2 tests in 0.005s
FAILED (failures=2)

Ran 23 tests in 0.436s
OK
```

The same reproduction after repair reports only
`lib/gzkit/nested/bad.py`, `valid: false`, exit 1, whether or not the stale
`src/gzkit` tree is present. Independent review additionally exercised the
command with real configuration/manifest acquisition and no mocks: invalid
configured source yielded exit 1; replacing the violation with an existing
exemption yielded `valid: true`, exit 0, despite stale default-tree and other
package violations. No remaining contract gap was found.

## Completion boundary

The focused observations above are not a substitute for full quality gates.
The landing commit and individual GHI closure comments carry the full staged
check result, verified ARB receipt IDs and guarded sync evidence. The design
drafts remain proposals; these two repairs do not establish complete impact
or dependency discovery.

## Required-gate blocker: GHI #1051

The first full unittest attempt lost a worker while importing
`content.advisor_qc`: it imports `arb.paths`, whose package initializer imports
`arb.validator`, which eagerly imported the partially initialized writer's
`SCHEMA_ID`. A separate fresh interpreter reproduced exit 1. None of these
source files was changed by #1049 or #1050. The stalled attempt was interrupted
and retained as failed receipt `arb-step-unittest-e287b55408e545a998ed67cff51ff870`
(exit 130), not counted as successful verification.

The validator now resolves the writer-owned schema identifier at validation
time, removing the eager cycle without copying its value or changing the public
ARB exports. The new
`TestAdvisorVerdictReceiptsValidate.test_fresh_import_orders_can_record_and_validate`
executes fresh writer-first and ARB-first processes, creates an actual verdict
receipt and validates it through the public API. RED: one test failed before
the correction. GREEN: all 18 focused writer/validator and advisor-QC tests pass.
Independent review repeated both import orders, public exports and actual
zero-score receipt validation with no remaining contract gap.

This is a separately tracked gate recovery, not a newly selected feature or a
claim to fix every import cycle. Open #1039 describes different skills modules
and is not discharged here.
