# How to Release GZKit

## Overview

GZKit has two distribution channels:

| Channel | Command | Who It's For |
|---------|---------|-------------|
| **GitHub Release** | Download `gz.exe` from Releases page | Students — zero Python install needed |
| **PyPI** | `uv tool install py-gzkit` or `pip install py-gzkit` | Developers who already have Python/uv |

Both are triggered by pushing a version tag.

## Step-by-Step: Creating a Release

### 1. Bump the version

Edit `pyproject.toml`:

```toml
[project]
version = "0.9.0"  # increment this
```

### 2. Commit the version bump

```bash
git add pyproject.toml
git commit -m "release: v0.9.0"
```

### 3. Tag the commit

```bash
git tag v0.9.0
```

### 4. Push the tag

```bash
git push origin main
git push origin v0.9.0
```

This triggers the release workflow (`.github/workflows/release.yml`), which:

1. Builds `gz.exe` (Windows), `gz-linux`, and `gz-macos` via PyInstaller
2. Creates a GitHub Release with auto-generated release notes
3. Attaches all three binaries to the release

### 5. Verify

Go to `https://github.com/<owner>/gzkit/releases` — you should see the new
release with three downloadable binaries.

## PyPI Publishing

The release workflow publishes `py-gzkit` to PyPI automatically via trusted publishers (OIDC — no tokens needed). This is configured through:

1. A pending publisher on [pypi.org](https://pypi.org/manage/account/publishing/) linking `tvproductions/gzkit` + `release.yml`
2. A `pypi` environment in the GitHub repo settings
3. The `pypi` job in `.github/workflows/release.yml`

Every tagged release publishes to PyPI alongside the GitHub Release.

## Local Build (Testing)

To build a binary locally without pushing a release:

```bash
uv add --dev pyinstaller
uv run pyinstaller gz.spec
# Output: dist/gz.exe (Windows) or dist/gz (macOS/Linux)
```

Test it:

```bash
./dist/gz --help
./dist/gz --version
```

## Versioning Convention

GZKit uses semantic versioning: `MAJOR.MINOR.PATCH`

- **PATCH** (0.8.1): Bug fixes, no new features
- **MINOR** (0.9.0): New features, backward compatible
- **MAJOR** (1.0.0): Breaking changes or "student-ready" milestone

The tag format is `v` + version: `v0.9.0`, `v1.0.0`.
