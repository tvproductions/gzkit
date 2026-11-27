# gz chores run

Execute one chore and append a dated log entry.

---

## Usage

```bash
gz chores run <slug>
```

---

## Runtime Behavior

- Runs each acceptance criterion in the chore's `acceptance.json`, resolved
  via the project-first → package-fallback resolver (ADR-0.0.21):
  `<project_root>/.gzkit/chores/<slug>/` first, then
  `importlib.resources.files("gzkit.chores")` as the package fallback.
- A criterion's `command` string is split with `shlex` and run without a
  shell; a command holding a shell operator (`&&`, `||`, `|`, `<`, `>`) is
  refused when the registry loads. A `fileExists` criterion checks its `path`.
- Stops at the first failing criterion and writes a dated `PASS` or `FAIL`
  entry to:
  `.gzkit/chores/<slug>/proofs/CHORE-LOG.md` (project-local execution
  evidence is never canonical).
- Returns non-zero on command failure, timeout, or missing executable.
- Refuses a chore with no class declaration before running anything, with a
  `BLOCKERS:` message naming it and exit 1 (GHI #999). Declare it on its
  `registry.json` entry (`.gzkit/chores/README.md` § Class Declaration).

---

## Example

```bash
uv run gz chores run quality-check
```
