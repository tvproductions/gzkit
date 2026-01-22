---
id: {id}
parent: {parent_adr}
item: {item_number}
lane: {lane}
status: Draft
---

# {id}: {title}

## Objective

{objective}

## Parent ADR

- **ADR**: {parent_adr}
- **Checklist Item**: #{item_number}

## Lane

**{lane}**

{lane_requirements}

## Allowed Paths

<!-- What approaches are permitted for this OBPI -->

- TBD

## Denied Paths

<!-- What approaches are explicitly forbidden -->

- TBD

## Requirements

<!-- Fail-closed constraints - if not met, OBPI fails -->

- TBD

## Acceptance Criteria

<!-- Specific, testable criteria for completion -->

- [ ] Criterion 1
- [ ] Criterion 2

## Gate Evidence

<!-- Commands and artifacts that prove completion -->

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 2 (TDD) | Tests pass | `uv run -m pytest tests/` |
