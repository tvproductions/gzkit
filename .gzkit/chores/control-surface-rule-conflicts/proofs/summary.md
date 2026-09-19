# Rule-conflict assessment — 2026-09-19

Persona: main-session. Audit population: every Markdown file recursively under `.gzkit/rules/`, plus root `AGENTS.md` and `CLAUDE.md`.

28 files and all 378 unordered pairs were reviewed against baseline `3dc6f613042117838f4f4cad55abe0b2e3044d35`. Three independent partitions retained full-file read records and pair reasoning. After six rule edits, all 147 affected pairs were re-reviewed (154 pairs total, including seven unchanged pairs). The combined record binds current hashes. This establishes coverage of the declared review, not exhaustive semantic correctness.

## Findings and action

Remaining concrete conflicts: blocking 0; episodic 0; theoretical 1 (R01, GHI #1044). There are no evidenced blocking rows to rank as a top five. Chore/MX scope remains an unproven candidate on GHI #943, excluded from concrete-conflict counts.

Four authorized direct-repair work orders corrected five stale prescriptions: GHI #1040 version metadata, #1041 release-approval terminology, #1042 test-tier scope, and #1043's two CLI authoring alternatives. Canonical rules, release-skill metadata, the scorecard and generated deliveries were updated together. No runtime behavior, thresholds, model routing, OBPI state or new gate was introduced. Full before snapshots and independent after reviews are retained alongside this report.

The remaining priority is GHI #1044: distinguish authoring authority from damaged-slug recovery and decide how an otherwise valid local edit is preserved during recovery. Current doctor behavior was traced, not executed against live damaged content. It remains unchanged. The other four control-surface audit chores are not claimed complete by Pass A.

## Evidence and limits

- `rule-inventory.md`: full path, headings, line counts and current SHA-256 per file.
- `review-20260919-part*.json`: initial independent 126-pair partitions.
- `postrepair-20260919-part*.json`: affected-pair review and repair-contract assessment.
- `current-pair-review.json`: merged 378-pair record and changed-surface coverage.
- `repair-before-3dc6f6130/`: full before text, including historical prose.
- `archive/2026-09-12/`: previous audit preserved as a dated record.

Observed checks before repository validation: the old model-selection field map returns `SKA-METADATA-SKILL-VERSION-MISSING`; the nested control returns no issue. The actual test help describes the default as the full unit tier and BDD as an added selector. Full test-handler and alignment-audit bodies were read. Generated mirrors were synchronized through the governed command. Independent reviewers accepted all four documentary closure contracts and found no new contrary actions in affected pairs.

Repository quality results and the chore's actual acceptance outcome are recorded in `CHORE-LOG.md`/the closure comments when executed, not predicted here. Freshness uses committed timestamps: the new audit and rule repairs must land before the tracked replacement proofs can satisfy freshness. Historical proofs are archived, not relabeled fresh.

This work improves instruction consistency. It does not establish improved model performance. The separate three-pillars six-case comparison remains 6/6 for both variants, with no demonstrated benefit; its assessment is `docs/evals/three-pillars-2026-09-19/assessment.md`.
