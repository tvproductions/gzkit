---
applyTo: "config/calendars.json,src/**/calendar*.py,src/**/period*.py,src/**/calendars*.py,tests/**/test_*calendar*.py,tests/**/test_*period*.py,features/**airac*.feature"
---

# Calendars & Period Labels (authoritative pointers)

- **Source of truth:** `config/calendars.json`
- Supported types & labels:
    - `monthly` → `YYYY-MM`
    - `quarterly` → `YYYY-Qn`
    - `db28` → `YYYY-MM` (admissible per DB28 lag window)
    - `airac` → `Cycle####` (28-day cycles; do not equate to months)
    - `static` → `STATIC` (or canonical version)
    - `daily` → `YYYY-MM-DD`
- Rules:
    - Compute **admissibility** and labels via calendars.json; **do not** hard-code math.
    - **PREZIP-first** ingest; use resolver only when PREZIP is unavailable.
    - Orchestrators and planners **must** consult calendars.json.

## Verify

- Period selection/filters match calendars.json for the active dataset.
