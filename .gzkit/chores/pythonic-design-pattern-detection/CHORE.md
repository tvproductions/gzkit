# CHORE: Pythonic Design Pattern Detection

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `pythonic-design-pattern-detection`

---

## Why this chore exists

`pythonic-refactoring` (ruff + ty) catches idiom-level drift. `complexity-reduction-xenon` and `module-sloc-cap-radon` catch metric-level drift. Neither catches *structural* drift — class-shaped Java-flavored code that mechanical metrics rate as "fine" but a Pythonic eye sees as a Strategy class that should be a function, a Singleton that should be a module-level constant, or a Visitor ladder that should be a `match` statement.

This chore is **post-post-implementation**: runs after ADR closeout and after `pythonic-refactoring` has zeroed ruff/ty, asking *given the code is idiomatic line-by-line, is the **shape** Pythonic?*

Pair with `pythonic-design-pattern-application` — detection surfaces candidates; application captures the refactor with mechanical-delta evidence. Both are wielded by skills (`pythonic-pattern-detect`, `pythonic-pattern-apply`) so an agent can route into the work via skill discovery rather than chore-slug recall.

## Pythonic-first absorption stance

The catalogue at `https://refactoring.guru/design-patterns/python` is the absorption surface for the GoF taxonomy. We **learn** from it; we do not **adopt** its class hierarchies. Each entry below cites the canonical Python example URL so an agent walking through a refactor can show the reference shape, then write the Pythonic equivalent.

This is the same relationship gzkit has with `click` (per AGENTS.md § Stdlib-First Doctrine): we measure the design metrics to inform doctrine; we do not depend on the surface.

## Full pattern catalogue (all 22)

Detection mode key:
- **AST** — scanner has a mechanical detector; matches appear in the report automatically
- **Reference** — pattern is in the catalogue for absorption but admits no robust mechanical signal; agent applies human-eye review

### Creational

| Pattern | Detection | Pythonic refactor target | refactoring.guru reference |
|---------|-----------|---------------------------|----------------------------|
| Abstract Factory | AST | Module of factory functions or `dataclass` registry | `/abstract-factory/python/example` |
| Builder | AST | `dataclass`/Pydantic + `@classmethod` factory | `/builder/python/example` |
| Factory Method | Reference | Module-level factory function or `@classmethod.from_*` | `/factory-method/python/example` |
| Prototype | AST | `copy.deepcopy` or `dataclasses.replace` | `/prototype/python/example` |
| Singleton | AST | Module-level constant or `functools.cache` | `/singleton/python/example` |

### Structural

| Pattern | Detection | Pythonic refactor target | refactoring.guru reference |
|---------|-----------|---------------------------|----------------------------|
| Adapter | AST (shared with Proxy) | `typing.Protocol` + duck typing or `__getattr__` forwarding | `/adapter/python/example` |
| Bridge | Reference | Composition of independent abstractions; pass impl as parameter | `/bridge/python/example` |
| Composite | AST | Recursive `dataclass` tree (only when truly hierarchical) | `/composite/python/example` |
| Decorator | AST (class form) | Function decorator + `functools.wraps` | `/decorator/python/example` |
| Facade | AST (static-only) | Module-level functions | `/facade/python/example` |
| Flyweight | Reference | `functools.cache` / `weakref.WeakValueDictionary` | `/flyweight/python/example` |
| Proxy | AST (shared with Adapter) | `__getattr__` forwarding or `typing.Protocol` | `/proxy/python/example` |

### Behavioral

| Pattern | Detection | Pythonic refactor target | refactoring.guru reference |
|---------|-----------|---------------------------|----------------------------|
| Chain of Responsibility | AST | List of handler functions, iterated until one returns non-`None` | `/chain-of-responsibility/python/example` |
| Command | AST | `functools.partial` or closure | `/command/python/example` |
| Iterator | AST | Generator function (`yield`) | `/iterator/python/example` |
| Mediator | AST | Module-level event bus or `asyncio.Queue` | `/mediator/python/example` |
| Memento | AST | `copy.deepcopy` snapshot or `dataclasses.replace` | `/memento/python/example` |
| Observer | AST | Callable list or `weakref.WeakSet` | `/observer/python/example` |
| State | AST | Plain attribute + `match`/dispatch table | `/state/python/example` |
| Strategy | AST | First-class function or `Callable[..., R]` | `/strategy/python/example` |
| Template Method | AST | Pass a callable; or use composition over inheritance | `/template-method/python/example` |
| Visitor | AST (two detectors) | `@functools.singledispatch` or `match` statement | `/visitor/python/example` |

Plus one Python-idiom signal not on the GoF list:

| Signal | Detection | Pythonic refactor target |
|--------|-----------|---------------------------|
| Context-manager-as-class | AST | `@contextlib.contextmanager` generator (Python idiom — not GoF) |
| isinstance dispatch chain | AST | `match` or `@functools.singledispatch` (Visitor adjacency) |

## Policy and Guardrails

- **Lane:** Lite — read-only scan, no contract change
- **No false-positive forcing:** scanner reports candidates; operator decides per-candidate whether the Pythonic rewrite genuinely helps
- **Pair-with-application:** every candidate that is applied must produce evidence under `pythonic-design-pattern-application`
- **Per-candidate disposition:** every flagged candidate gets one of `applied` | `deferred` | `not-pythonic-rewrite` recorded inline in the candidates report
- **Tests stay green:** scanner runs against the source tree; no source mutation
- **Reference-mode patterns:** Bridge, Flyweight, Factory Method are catalogued for absorption; agent does eye-review against `CHORE.md` rather than expecting AST hits

## Workflow

### 1. Run the scanner

```bash
uv run python src/gzkit/chores/pythonic-design-pattern-detection/scan.py \
    --root src \
    --out .gzkit/chores/pythonic-design-pattern-detection/proofs/candidates-$(date +%Y-%m-%d).md
```

### 2. Cross-reference complexity hotspots

```bash
uvx xenon --max-absolute B src/ > .gzkit/chores/pythonic-design-pattern-detection/proofs/xenon-hotspots-$(date +%Y-%m-%d).txt 2>&1 || true
```

A scanner candidate that *also* shows up in xenon's B-band hotspot list jumps to the top of the apply queue: structural rewrite has both a structural and a metric reason to land.

### 3. Reference-mode eye-review

For Bridge, Flyweight, and Factory Method (catalogue-only patterns), open the relevant `refactoring.guru/design-patterns/<slug>/python/example` example side-by-side with any module ranked B-or-worse by xenon. Note candidates inline in the same report under a `## Reference-mode candidates` section.

### 4. Triage and disposition

For each candidate (AST or reference-mode), mark one of:

- `applied` — operator/agent applied the Pythonic rewrite (route to `pythonic-design-pattern-application` for evidence capture)
- `deferred` — opportunity is real but parked (note the GHI tracking the deferral)
- `not-pythonic-rewrite` — class shape is genuinely the right fit (e.g. State machine with many states; Composite tree that is truly hierarchical)

Empty triage is a defect: every flagged candidate gets a disposition before the chore is considered done for this period.

### 5. Validate

```bash
uv run -m unittest -q
uv run python src/gzkit/chores/pythonic-design-pattern-detection/scan.py --self-test
```

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run -m unittest -q` | 0 |
| exitCodeEquals | `uv run python src/gzkit/chores/pythonic-design-pattern-detection/scan.py --self-test` | 0 |

## Anti-patterns (do not do)

- Forcing a Pythonic rewrite onto code where the class shape is genuinely the right fit (State machines with many transitions; Composite trees that are truly hierarchical; Strategy where the strategy holds significant configuration state)
- Treating the candidate list as a backlog to grind through — judgment per candidate, always
- Backfilling a `not-pythonic-rewrite` disposition without naming the concrete reason
- Running the scanner on `tests/` (test classes legitimately use `__init__` + single-test-method shape — already excluded by default)
- Letting reference-mode patterns lapse to "we don't detect those" — the catalogue exists so the agent can eye-review against it; skipping the eye-review collapses the post-post-implementation contract back to mechanical-only

## Run Log

| Run Date | AST Candidates | Reference Notes | Applied | Deferred | Not-Pythonic | Notes |
|----------|----------------|------------------|---------|----------|--------------|-------|
| _YYYY-MM-DD_ | _N_ | _N_ | _N_ | _N_ | _N_ | _scope notes_ |

---

**End of CHORE: Pythonic Design Pattern Detection**
