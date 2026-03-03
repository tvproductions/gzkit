# GEMINI.md (src/gzkit/schemas)

This directory defines the data structures and schema validation rules for the `gzkit` ecosystem.

## Guidelines

- **JSON Schema:** Schemas should conform to standard JSON Schema specifications.
- **Backward Compatibility:** All schema changes must be strictly additive. Breaking changes require a migration strategy (like `migrate_semver`).
- **Validation:** Always use the defined schemas for validation during I/O operations (e.g., in `validate.py`).
