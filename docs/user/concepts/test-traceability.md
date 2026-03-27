# Test Traceability

Requirement-level test traceability connects governance specifications to
implementation proof via the `@covers` decorator and the `gz covers` CLI.

Canonical source: [ADR-0.21.0](../../design/adr/pre-release/ADR-0.21.0-tests-for-spec/ADR-0.21.0-tests-for-spec.md)

---

## Purpose

Code coverage tools measure line execution but say nothing about whether the
code fulfills its governance requirements. A test that exercises every line
of a function may not verify the specific behavior that a REQ demands.

The `@covers` pattern makes the connection explicit: each test declares which
requirement it proves, and tooling aggregates, reports, and audits the linkage.

This is the Test-to-Spec edge of the governance triangle defined in ADR-0.20.0.

---

## The @covers Decorator

`@covers` is a metadata-only decorator. It does not change test behavior ---
it registers a linkage record mapping a test function to a governance
requirement.

### How It Works

1. The decorator validates the REQ identifier format (`REQ-X.Y.Z-NN-MM`)
2. It verifies the REQ exists in the extracted brief-defined requirement set
3. It registers a `LinkageRecord` in the global linkage registry
4. The decorated function runs unchanged

### Example 1: Basic Annotation

```python
from gzkit.traceability import covers


class TestPoolPromotion(unittest.TestCase):

    @covers("REQ-0.6.0-01-01")
    def test_pool_source_preserved(self):
        """Verify that promotion preserves the pool source reference."""
        promoted = promote_adr("ADR-pool.my-feature", semver="0.6.0")
        self.assertEqual(promoted.promoted_from, "ADR-pool.my-feature")
```

This tells the traceability system: "This test proves REQ-0.6.0-01-01 from
OBPI-0.6.0-01."

### Example 2: Multiple REQs on One Test

A single test can cover multiple requirements when they are tightly coupled:

```python
class TestCoversCLI(unittest.TestCase):

    @covers("REQ-0.21.0-03-01")
    @covers("REQ-0.21.0-03-02")
    def test_covers_json_output_includes_rollups(self):
        """Verify JSON output contains both ADR and OBPI rollups."""
        report = run_covers_command("--json")
        self.assertIn("by_adr", report)
        self.assertIn("by_obpi", report)
```

Stack decorators when one test function genuinely proves multiple requirements.

### Example 3: Targeted REQ Coverage

```python
class TestAuditIntegration(unittest.TestCase):

    @covers("REQ-0.21.0-04-01")
    def test_audit_check_includes_coverage_section(self):
        """Verify audit-check JSON output includes coverage data."""
        result = run_audit_check("ADR-0.21.0", json_output=True)
        self.assertIn("coverage", result)
        self.assertGreater(result["coverage"]["total_reqs"], 0)
```

Each `@covers` annotation ties one test to one REQ. The scanner discovers
these annotations statically via AST parsing --- no test execution required.

---

## REQ Identifier Format

REQ identifiers follow a strict format: `REQ-<semver>-<obpi>-<criterion>`.

| Component | Example | Meaning |
|-----------|---------|---------|
| Prefix | `REQ-` | Fixed prefix |
| SemVer | `0.21.0` | Parent ADR version |
| OBPI item | `03` | OBPI sequence number |
| Criterion | `02` | Acceptance criterion index |

Full example: `REQ-0.21.0-03-02` = ADR-0.21.0, OBPI-03, criterion #2.

The decorator validates this format at decoration time and raises
`ValueError` for malformed identifiers. It also verifies that the REQ
actually exists in an OBPI brief --- references to non-existent REQs are
rejected, preventing silent coverage pollution.

---

## Reporting with gz covers

The `gz covers` command scans test files and reports coverage at three
granularity levels:

```bash
# All-REQ coverage summary
gz covers

# Coverage for a single ADR
gz covers ADR-0.21.0

# Coverage for a single OBPI
gz covers OBPI-0.21.0-03

# Machine-readable JSON output
gz covers --json
```

See [gz covers command reference](../commands/covers.md) for full usage.

---

## Migration Guide: Adding @covers to Existing Tests

Adopting `@covers` is incremental. Existing tests without the decorator
continue to work --- they are simply reported as "uncovered" in coverage
reports. No tests break when you start using `@covers`.

### Step 1: Identify REQs for Your ADR

Check which requirements exist in your OBPI briefs:

```bash
gz covers ADR-0.15.0 --json
```

The output shows `total_reqs` and `covered_reqs`. Uncovered REQs are
your migration targets.

### Step 2: Map Tests to REQs

For each uncovered REQ, find the test that proves it. A test "covers" a
REQ when it directly verifies the behavior described in the acceptance
criterion.

| REQ | Acceptance criterion | Candidate test |
|-----|---------------------|----------------|
| REQ-0.15.0-03-01 | "Given a pool ADR, promotion preserves source" | `test_pool_source_preserved` |
| REQ-0.15.0-03-02 | "Given promotion, semver is assigned" | `test_semver_assigned_on_promote` |

### Step 3: Add Decorators

Import and apply:

```python
from gzkit.traceability import covers


class TestPoolPromotion(unittest.TestCase):

    @covers("REQ-0.15.0-03-01")
    def test_pool_source_preserved(self):
        # existing test body unchanged
        ...
```

### Step 4: Verify

```bash
# Confirm the REQ is now covered
gz covers ADR-0.15.0

# Run tests to confirm nothing broke
uv run -m unittest tests.test_promotion -v
```

### Tips for Incremental Adoption

- **Start with the current OBPI.** Annotate tests for the work you are doing
  now. Do not batch-annotate the entire test suite in one pass.
- **One decorator per REQ.** If a test covers two REQs, use two `@covers`
  decorators. If two tests cover the same REQ, that is fine --- both will
  appear in the coverage report.
- **Do not force coverage.** If no test directly proves a REQ, that is a
  signal the REQ may need a new test --- not that an existing test should be
  relabeled.

---

## Language-Agnostic Proof Metadata Contract

The `@covers` decorator is the Python-native mechanism, but gzkit's
traceability doctrine is not limited to Python. Non-Python test stacks
can declare equivalent REQ linkage using comment-based or configuration-based
annotations.

**This is a first-class supported pattern** --- not an afterthought or
hidden footnote. Any test stack that can emit structured metadata can
participate in the traceability framework.

### Equivalent Annotation Patterns

#### Comment-Based (Any Language)

Use a structured comment containing `@covers` followed by the REQ identifier:

```javascript
// @covers REQ-0.15.0-03-01
test("pool source is preserved after promotion", () => {
  const promoted = promoteAdr("ADR-pool.my-feature", "0.15.0");
  expect(promoted.promotedFrom).toBe("ADR-pool.my-feature");
});
```

```go
// @covers REQ-0.15.0-03-01
func TestPoolSourcePreserved(t *testing.T) {
    promoted := PromoteADR("ADR-pool.my-feature", "0.15.0")
    assert.Equal(t, "ADR-pool.my-feature", promoted.PromotedFrom)
}
```

```shell
# @covers REQ-0.15.0-03-01
test_pool_source_preserved() {
    result=$(gz adr promote ADR-pool.my-feature --semver 0.15.0)
    assert_contains "$result" "promoted_from: ADR-pool.my-feature"
}
```

The key contract: the comment must contain `@covers` followed by a valid
`REQ-X.Y.Z-NN-MM` identifier on the same line.

#### Frontmatter-Based (Markdown/YAML Test Specs)

For test specifications written in Markdown or YAML:

```yaml
# test-spec.yaml
tests:
  - name: pool source preserved
    covers: REQ-0.15.0-03-01
    steps:
      - action: promote ADR-pool.my-feature
      - assert: promoted_from equals ADR-pool.my-feature
```

#### Configuration-Based (Test Manifests)

For test frameworks that use external configuration:

```json
{
  "test": "test_pool_source_preserved",
  "covers": ["REQ-0.15.0-03-01"],
  "file": "tests/test_promotion.go"
}
```

### Runtime Discovery Status

**Non-Python proof metadata is doctrinally supported but remains
runtime-undiscovered until a future ADR adds ingestion support.**

Today, only the Python `@covers` decorator is scanned and reported by
`gz covers`. Comment-based, frontmatter-based, and configuration-based
annotations are valid governance proof for human review and audit, but they
do not appear in automated coverage reports.

A future ADR will add scanner plugins for non-Python annotation patterns.
Until then:

- Non-Python annotations **are** valid proof in manual audits
- Non-Python annotations **do not** appear in `gz covers` output
- Non-Python annotations **should** follow the patterns above for
  forward-compatibility with future automated discovery
- Any runtime ingestion of non-Python proof metadata without a new ADR
  is invalid and should be treated as doctrinal drift

---

## How It Fits Together

```text
OBPI Brief              Test File                gz covers
┌──────────────┐       ┌──────────────────┐     ┌─────────────┐
│ REQ-X.Y.Z-01 │◄──────│ @covers("REQ-..") │────►│ Covered: Y  │
│ REQ-X.Y.Z-02 │  no   │                  │     │ Covered: N  │
│              │  link  │                  │     │             │
└──────────────┘       └──────────────────┘     └─────────────┘
       │                                               │
       ▼                                               ▼
   gz adr audit-check ◄─── coverage data ────── coverage rollup
```

1. OBPI briefs define requirements (`REQ-X.Y.Z-NN-MM`)
2. Tests declare which REQs they prove via `@covers`
3. The scanner discovers annotations via AST (no test execution)
4. `gz covers` reports coverage at ADR/OBPI/REQ levels
5. `gz adr audit-check` integrates coverage into the audit pipeline

---

## Related

- [gz covers command reference](../commands/covers.md)
- [OBPIs concept](obpis.md)
- [Gates concept](gates.md)
- [Daily Workflow](workflow.md)
- [Operator Runbook](../runbook.md)
