# Pythonic Design Pattern Detection

Scan the source tree for Java-flavored class shapes that have a cleaner Pythonic refactor target. Pair with `pythonic-design-pattern-application` for the evidence side.

## Quick Start

```bash
uv run python src/gzkit/chores/pythonic-design-pattern-detection/scan.py \
    --root src \
    --out .gzkit/chores/pythonic-design-pattern-detection/proofs/candidates-$(date +%Y-%m-%d).md
```

## Lane

**lite**
