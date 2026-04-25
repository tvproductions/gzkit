# Cross-Platform Test Cleanup

Eliminate raw shutil.rmtree() in tearDown; use context managers for Windows safety.

## Quick Start

```bash
uv run -m unittest -q
```

## Lane

**medium**
