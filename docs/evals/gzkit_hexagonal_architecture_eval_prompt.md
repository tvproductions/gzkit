# GZKit Hexagonal Architecture Review Prompt (Repeatable)

You are operating inside the `tvproductions/gzkit` repository.

Perform a deep architecture review focused on Hexagonal Architecture (Ports & Adapters), mapping implementation reality against documented architecture rules.

## Goal

Determine how well the repository matches the intended hexagonal design, and identify concrete strengths and violations.

## Required investigation

1. Identify core/domain modules, adapter modules, and port definitions.
2. Identify where external dependencies are imported directly, and whether they are confined to adapters.
3. Verify whether core/domain code depends only on stdlib + pydantic, and whether technology-specific names leak inward.
4. Analyze dependency injection and composition roots, including CLI wiring and whether core/library code constructs concrete adapters.
5. Verify whether ports are `typing.Protocol`, and whether runtime ABCs or concrete coupling are used instead.
6. Provide clear examples of strong separation and weak/violating separation.
7. Conclude whether architecture is consistently clean-core hexagonal, partially consistent, or inconsistent.

## Sources to read first

- `.github/instructions/hexagonal_architecture.instructions.md`
- `docs/governance/hexagonal-architecture.md`
- `tests/policy/test_import_boundaries.py`

Then inspect relevant code under:

- `src/gzkit/core/`
- `src/gzkit/ontology/`
- `src/gzkit/commands/`
- `src/gzkit/cli/`
- other modules that define `Protocol` seams

## Evidence requirements

- Use code-level evidence (file + symbol/line references), not documentation claims alone.
- Build an import inventory of non-stdlib/non-pydantic dependencies across `src/gzkit/`.
- Explicitly list any core-facing contradictions between rule claims and implementation.

## Output format

Produce one report with these sections:

1. **Executive verdict** (1 paragraph + rating: strong / moderate / weak alignment)
2. **Architecture map** (core, adapters, ports table)
3. **Dependency boundary findings** (including import inventory summary)
4. **DI/composition analysis**
5. **Protocol vs ABC/concrete coupling analysis**
6. **Strong examples**
7. **Violations / weak spots**
8. **Prioritized remediation plan** (P0/P1/P2)
9. **Confidence and limits**

## Repeatability metadata

At report top, include:

- Date/time
- Branch and commit SHA
- gzkit version
- Prompt file path used
