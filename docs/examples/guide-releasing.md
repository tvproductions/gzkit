# How to Release GZKit

## Overview

GZKit has two distribution channels:

| Channel | Command | Who It's For |
|---------|---------|-------------|
| **GitHub Release** | Download `gz.exe` from Releases page | Students — zero Python install needed |
| **PyPI** | `uv tool install gzkit` or `pip install gzkit` | Developers who already have Python/uv |

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

## Optional: Publishing to PyPI

The release workflow has a commented-out `pypi` job. To enable it:

1. Create a PyPI account at [pypi.org](https://pypi.org)
2. Generate an API token (Account Settings → API tokens)
3. Add the token as a GitHub repository secret named `PYPI_TOKEN`
4. Uncomment the `pypi` job in `.github/workflows/release.yml`

After that, every tagged release will also publish to PyPI.

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
