# Pythonic Design Pattern Detection

Scan the source tree for Java-flavored class shapes that have a cleaner Pythonic refactor target. Pair with `pythonic-design-pattern-application` for the evidence side.

When `design-patterns-en.zip` is available, use its `Python/src/<Pattern>/Conceptual/main.py` examples as the required role-map witness for every disposition.

## Quick Start

```bash
uv run python src/gzkit/chores/pythonic-design-pattern-detection/scan.py \
    --root src \
    --out .gzkit/chores/pythonic-design-pattern-detection/proofs/candidates-$(date +%Y-%m-%d).md
```

## Lane

**lite**
