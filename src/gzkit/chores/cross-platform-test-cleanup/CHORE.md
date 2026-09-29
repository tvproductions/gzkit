# CHORE: Cross-Platform Test Cleanup (Windows-Safe Patterns)

**Lane:** Lite
**Slug:** `cross-platform-test-cleanup`

---

## Overview

Hold the three mechanical cross-platform scopes green, with the unit suite as the
regression check. Its criteria gate exactly these, and nothing else:

- `uv run gz validate --utf8-prefix` — no `PYTHONUTF8=1 uv run gz` prefix in docs or
  skills; the CLI handles UTF-8 itself.
- `uv run gz validate --line-endings` — no CRLF text surfaces, and `.gitattributes`
  carries its LF rule.
- `uv run gz validate --type-ignores` — no `# type: ignore[<code>]` under `src/` that
  `ty` would silently not honor.

Test-teardown hygiene (raw `shutil.rmtree()` in `tearDown`) was this chore's original
prose subject, but nothing in its criteria reads a `tearDown` body, so it is not
claimed here (GHI #1011).

## Policy and Guardrails

- **Lane:** Lite — repository hygiene through three validator scopes; unit-tier only, no behave/network
- **Timeout:** 300s — explicit per-chore `timeoutSeconds`; GHI #447
- Cross-platform: Windows, macOS, Linux — co-equal (no primary platform)

## Workflow

### 1. Baseline — observe

```bash
uv run gz validate --utf8-prefix --line-endings --type-ignores
```

### 2. Repair — repair

Fix each finding at its source: drop the `PYTHONUTF8=1` prefix, normalize the file
to LF (or add the missing `.gitattributes` rule), and rewrite the suppression in a
form `ty` honors (`.gzkit/rules/pythonic.md` § Type-check suppression syntax).

### 3. Validate — observe

```bash
uv run gz validate --utf8-prefix --line-endings --type-ignores
uv run gz test
```

## Checklist

- [ ] `--utf8-prefix` exits 0
- [ ] `--line-endings` exits 0
- [ ] `--type-ignores` exits 0
- [ ] `uv run gz test` exits 0

## Acceptance Criteria

Criteria live in `acceptance.json`, which `gz chores run` executes; render them with `uv run gz chores plan cross-platform-test-cleanup`. This section explains them and does not restate them (GHI #1002).

## Evidence Commands

```bash
uv run gz validate --utf8-prefix --line-endings --type-ignores > .gzkit/chores/cross-platform-test-cleanup/proofs/validate.txt
```

---

**End of CHORE: Cross-Platform Test Cleanup**
