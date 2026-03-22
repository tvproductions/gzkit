---
id: REQ-[ADR]-[NN]
parent_adr: ADR-[NNN]
checklist_item: [N]
status: Not Started
author: [Your Name]
date: [YYYY-MM-DD]
---

# REQ [NN]: [Requirement Title]

**From:** ADR-[NNN] requirements checklist item #[N]

## Objective

<!-- One sentence: what does "done" look like for this requirement? -->

[What concrete deliverable does this requirement produce?]

## Allowed Paths

<!-- What files/modules will you create or modify? -->

- `path/to/new_file.py` — [what it does]
- `path/to/existing_file.py` — [what changes]
- `tests/test_feature.py` — [what tests]

## Denied Paths

<!-- What files/modules are OUT OF SCOPE for this requirement? -->

- `path/to/unrelated/` — [why excluded]

## Constraints

<!-- Specific constraints. Use MUST/MUST NOT language. -->

1. MUST [constraint]
2. MUST [constraint]
3. MUST NOT [constraint]

## Acceptance Criteria

<!-- Testable checkboxes. Every box must be checkable with a test or demo. -->

- [ ] [Criterion — something you can verify with a test]
- [ ] [Criterion — something you can demonstrate]
- [ ] [Criterion]
- [ ] All tests pass: `[test command]`

## Verification

<!-- Commands to prove the requirement is complete. Copy-paste and run. -->

```bash
# Run tests
[your test command]

# Specific verification
[command that demonstrates the feature works]
```

## Notes

<!-- Optional: anything useful for implementation — links, patterns to follow,
     known gotchas. Remove this section if empty. -->
