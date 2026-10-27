# Dependency Currency

Check gzkit's external tooling (uv, ruff, ty, pre-commit hook pins, pydantic/rich/behave runtime deps, GitHub Actions runner pins) against upstream latest releases every day, and bring every dependency up to date in the same run through the `gz-deps-upgrade` procedure, gated by `gz check --full`. Lite lane. Never touches gzkit's own version surfaces, the `requires-python` floor or the uv `required-version` floor.
