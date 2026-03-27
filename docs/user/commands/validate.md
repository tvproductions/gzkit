# gz validate

Validate governance artifacts against schema rules.

## Usage

```bash
gz validate [OPTIONS] [--documents] [--surfaces]
```

## Description

Verifies governance artifacts (ADRs, OBPIs, configuration files) against their schema definitions. Use `--documents` to validate documentation, `--surfaces` to validate CLI surfaces and control surface definitions.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All artifacts valid |
| 1 | Validation errors found |
