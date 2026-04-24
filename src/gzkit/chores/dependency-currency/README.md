# Dependency Currency

Scan gzkit's external tooling (uv, ruff, ty, pre-commit hook pins, pydantic/rich/behave runtime deps, GitHub Actions runner pins) against upstream latest releases and emit a drift report. Scan-only — operator applies bumps. Lite lane. Never touches gzkit's own version surfaces or the `requires-python` floor.
