---
paths:
  - "src/airlineops/warehouse/**"
---

# SQL Hygiene — Stdlib sqlite3 (Warehouse, Unified Scope)

Policy source of truth: docs/developer/policy/sql_stdlib_sqlite.md

Chore and governance references:

- Chore brief: docs/design/briefs/chores/CHORE-sql-hygiene-query-normalization/CHORE-sql-hygiene-query-normalization.md (v2.0.0)
- Opsdev entry: config/opsdev.chores.json → slug: sql-hygiene-query-normalization (lane: Heavy)

## Scope

This instructions file applies to:

- SELECT queries and read-only SQL patterns
- DML: INSERT, UPDATE, DELETE, UPSERT/REPLACE
- DDL: CREATE/ALTER/DROP TABLE, CREATE/DROP INDEX
- PRAGMA and maintenance: foreign_keys, journal_mode, VACUUM, ANALYZE
- Under `src/airlineops/warehouse/**`
- Within the context of the "sql-hygiene-query-normalization" chore (unified v2.0.0)

## Guardrails (Mandatory)

### Required Practices

| Rule                     | Requirement                                                 |
| ------------------------ | ----------------------------------------------------------- |
| **Stdlib only**          | Use `sqlite3` only for warehouse SQL                        |
| **Parameterization**     | All data values MUST use `?` placeholders                   |
| **No string formatting** | Never use f-strings, `.format()`, or concatenation for data |
| **Row factory**          | Connection objects MUST set `row_factory = sqlite3.Row`     |
| **Explicit connections** | Helpers MUST accept explicit `sqlite3.Connection`           |
| **Grep-able SQL**        | Keep SQL text explicit (no ORM or query-builder layers)     |
| **Preserve behavior**    | Refactors must not change query semantics or results        |

### Examples: Data Parameterization

```python
# ❌ WRONG - Data in f-string
period = "2024-Q3"
sql = f"SELECT * FROM bts_db10 WHERE period = '{period}'"
rows = conn.execute(sql).fetchall()

# ✅ RIGHT - Data via parameters
period = "2024-Q3"
sql = "SELECT * FROM bts_db10 WHERE period = ?"
rows = conn.execute(sql, (period,)).fetchall()
```

### Examples: Identifier Validation

```python
# ❌ WRONG - Unvalidated identifier
def get_count(conn, table_name):
    return conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]

# ✅ RIGHT - Validated identifier
ALLOWED_TABLES = {"bts_db10", "bts_db28", "faa_nasr"}

def get_count(conn, table_name):
    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table: {table_name}")
    return conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
```

### Examples: Connection Passing

```python
# ❌ WRONG - Implicit connection
def select_one(sql, params):
    conn = sqlite3.connect("database.db")  # FORBIDDEN
    return conn.execute(sql, params).fetchone()

# ✅ RIGHT - Explicit connection
def select_one(conn, sql, params):
    return conn.execute(sql, params).fetchone()
```

### DDL/Mutation constraints

- DDL must be idempotent; prefer CREATE IF NOT EXISTS / DROP IF EXISTS where appropriate.
- Prefer derived DDL (from JSON/Pydantic schema) when available.
- DML helpers must accept explicit connections and parameters; no implicit connection opening.
- PRAGMA/maintenance must live in dedicated helpers or setup paths, not in hot code paths.

## Canonical Helper Surface

Prefer these primitive helpers (or their existing equivalents):

- execute(conn, sql, params)
- select_one(conn, sql, params)
- select_all(conn, sql, params)
- count_rows(conn, table)
- count_rows_where(conn, table, where_sql, params)
- aggregate_scalar(conn, sql, params)
- table_exists(conn, table)
- pragma_table_info(conn, table)

Rules:

- It is OK to replace inline conn.execute(...).fetchone() with select_one(...).
- It is OK to replace inline conn.execute(...).fetchall() with select_all(...).
- Do not introduce new “primitive” helpers without a brief; build pattern-helpers on top.

For DML/DDL/PRAGMA changes, prefer the existing helpers that encapsulate safe patterns; add only when governed by a brief.

## Identifier Safety (Tables / Columns)

Dynamic identifiers (table names, column names) are allowed only when:

- They are validated against a small, explicit whitelist or mapping.
- Unknown identifiers raise ValueError (or equivalent) instead of being passed through.

Pattern:

- Interpolate only the validated identifier into SQL (table/column name).
- All runtime values still go through ? parameters.

Example pattern (conceptual):

- OK: f"SELECT COUNT(\*) AS n FROM {table} WHERE {column} = ?" after whitelist check.
- NOT OK: building WHERE clauses from arbitrary strings or dicts.

## Allowed Refactor Patterns (SELECT only)

When normalizing SQL in src/airlineops/warehouse/\*\*, you MAY:

- Replace duplicated COUNT queries with a small, explicit helper (count_where(...)) that:
    - Validates table and column names against a whitelist.
    - Uses ? for value parameters.
- Extract table existence checks into a helper that:
    - Uses sqlite_master and SELECT 1 ... LIMIT 1.
    - Validates the table_name against a whitelist.
- Extract period/year/month filters into helpers that:
    - Append fixed WHERE fragments like AND year = ? AND month = ?.
    - Take the base SQL string and additional parameters; do not synthesize arbitrary conditions.
- Replace repeated execute → fetchall/fetchone patterns with select_all / select_one.

## Forbidden Patterns

Do NOT introduce or retain:

- Any SQL where data values are injected via f-strings, .format(), or string concatenation.
- Dynamic WHERE clauses assembled from arbitrary dicts, kwargs, or free-form text.
- Helpers that generate arbitrary SQL from keyword arguments (mini-ORMs, query builders).
- Implicit connection creation inside lower-level helpers (e.g., calling sqlite3.connect() inside a helper).
- Backend changes or non-stdlib DB libraries in this path.

## Out of Scope (Handled by Other Chores)

The following must NOT be added, changed, or removed under this instructions file:

- DDL: CREATE/ALTER/DROP TABLE, CREATE/DROP INDEX, schema migrations.
- DML: INSERT, UPDATE, DELETE, UPSERT, bulk-load operations.
- Maintenance: VACUUM, ANALYZE, PRAGMA changes (journal_mode, synchronous, etc.).

Any requested changes in these areas require:

- A separate chore brief (e.g., sql-mutation-discipline, schema-migration-discipline).
- Explicit human review and updated policy references.

## Testing and Semantics

- After a SQL refactor, existing tests must still pass; add tests if gaps are exposed.
- Prefer table-driven tests for new helpers (e.g., multiple parameter sets through one function).
- If a refactor would change query meaning or result shape, STOP and surface BLOCKERS instead of guessing.

## When Uncertain

- If a change is ambiguous under this policy, annotate the call site with:

    # requires human review: SQL refactor ambiguous under sql_stdlib_sqlite policy

- Defer the refactor rather than invent behavior.
- Point humans at docs/developer/policy/sql_stdlib_sqlite.md for final decisions.
