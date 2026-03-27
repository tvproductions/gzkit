# gz typecheck

Run static type checks using ty.

## Usage

```bash
gz typecheck [OPTIONS]
```

## Description

Performs static type analysis on Python code using ty. Detects type mismatches, missing annotations, and incompatible assignments. Ensures type safety across the codebase.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | No type errors found |
| 1 | Type errors detected |
