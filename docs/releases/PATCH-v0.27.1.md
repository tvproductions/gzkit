# Patch Release: v0.27.1

**Date:** 2026-05-24
**Previous Version:** 0.27.0
**Tag:** v0.27.0

## Build Defect

The v0.27.0 PyPI publish job failed at `uv build`. The repository
tracked an absolute symlink at
`.antigravitycli/2e1004a1-3cdd-475d-b3e1-8c0d922c5801.json ->
/Users/jeff/.gemini/config/projects/...` (a local Gemini CLI artifact
accidentally committed). PyPI's sdist validation rejects external
absolute symlinks, so the wheel/sdist build aborted before upload.

The v0.27.0 GitHub release exists; PyPI did not receive v0.27.0.

## Fix (commit `7c81501f`)

- Added `.antigravitycli/` to `.gitignore`
- Added `[tool.hatch.build.targets.sdist] exclude = [".antigravitycli", ".antigravitycli/**"]`
  to `pyproject.toml`
- Extended `[tool.hatch.build.targets.wheel] exclude` with the same entries
  (defense in depth)
- `git rm` removed the tracked symlink

Verified: `uv build` produces `py_gzkit-0.27.1.tar.gz` + wheel cleanly.

## Operator Approval

Approved by operator at v0.27.1 patch ceremony, 2026-05-24, to ship the
fix as an additive release rather than force-pushing the v0.27.0 tag.

## In-Flight Note

This manifest exists to satisfy `audit_version_release` during the brief
window between the bump commit and `gh release create v0.27.1`
(GHI #217 in-flight allowance).
