# CHORE: Cross-Platform Test Cleanup (Windows-Safe Patterns)

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `cross-platform-test-cleanup`

---

## Overview

Enforce Windows-safe test cleanup patterns. Eliminate raw `shutil.rmtree()` in tearDown methods. Use context managers or safe cleanup patterns throughout.

## Policy and Guardrails

- **Lane:** Lite — test-infra hygiene (Windows-safe cleanup patterns); unit-tier only, no behave/network
- **Timeout:** 300s — explicit per-chore `timeoutSeconds` (was lane-derived 300 under the removed medium tier); GHI #447
- Use `tempfile.TemporaryDirectory()` context managers (preferred)
- Use `pathlib.Path` throughout; no hard-coded path separators
- Cross-platform: Windows, macOS, Linux — co-equal (no primary platform)

## Workflow

### 1. Baseline

Scan for `shutil.rmtree` usage in test tearDown methods.

### 2. Plan

Replace each violation with context manager pattern.

### 3. Implement

```python
# Before (unsafe on Windows):
def tearDown(self):
    shutil.rmtree(self.temp_dir)

# After (safe):
def test_something(self):
    with tempfile.TemporaryDirectory() as temp_dir:
        # test logic here
```

### 4. Validate

```bash
uv run -m unittest -q
uv run coverage report --fail-under=40
```

## Checklist

- [ ] No `shutil.rmtree()` in tearDown methods
- [ ] Context managers used for all temp resources
- [ ] Tests pass on Windows
- [ ] Coverage >=40%

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run -m unittest -q` | 0 |

## Evidence Commands

```bash
uv run -m unittest -v > .gzkit/chores/cross-platform-test-cleanup/proofs/test-results.txt
```

---

**End of CHORE: Cross-Platform Test Cleanup**
