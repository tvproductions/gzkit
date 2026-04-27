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

The local `design-patterns-en.zip` Python examples are the internal absorption surface for the GoF taxonomy. We **learn** from the examples; we do not **adopt** their class hierarchies. Each entry below cites the archive path so an agent walking through a refactor can inspect the example shape, map the roles, then write the Pythonic equivalent.

This is the same relationship gzkit has with `click` (per AGENTS.md § Stdlib-First Doctrine): we measure the design metrics to inform doctrine; we do not depend on the surface.

## Python example corpus

The local examples archive is the required example corpus when present:

```bash
export DESIGN_PATTERNS_ARCHIVE="/Users/jeff/Library/Mobile Documents/com~apple~CloudDocs/Design_Patterns_Book/design-patterns-en.zip"
unzip -l "$DESIGN_PATTERNS_ARCHIVE" 'Python/src/*/Conceptual/*'
```

For every candidate, read the matching `Python/src/<Pattern>/Conceptual/main.py`
and `Output.txt` from that archive before deciding disposition. The example is
not a target to paste into gzkit. It is a role map: identify the pattern roles
the example teaches, then decide which Python standard construct collapses those
roles most honestly in gzkit code.

Required per-candidate notes:

- **Example path:** the `Python/src/.../main.py` path inspected
- **Output path:** the matching `Output.txt` path, when present
- **Role map:** the example's named roles in one sentence
- **Pythonic collapse:** the stdlib/Python construct that replaces the class
  structure, or the concrete reason the class structure remains warranted

Do not mark a candidate `not-pythonic-rewrite` until the archive example has
been read. Absence of an AST hit is not evidence of Pythonic shape; the example
corpus is the human-eye review surface.

## Full pattern example table (all 22)

Detection mode key:
- **AST** — scanner has a mechanical detector; matches appear in the report automatically
- **Reference** — pattern is in the example corpus but admits no robust mechanical signal; agent applies human-eye review

### Creational

| Pattern | Detection | Pythonic refactor target | Python archive example |
|---------|-----------|---------------------------|------------------------|
| Abstract Factory | AST | Module of factory functions or `dataclass` registry | `Python/src/AbstractFactory/Conceptual/main.py` |
| Builder | AST | `dataclass`/Pydantic + `@classmethod` factory | `Python/src/Builder/Conceptual/main.py` |
| Factory Method | Reference | Module-level factory function or `@classmethod.from_*` | `Python/src/FactoryMethod/Conceptual/main.py` |
| Prototype | AST | `copy.deepcopy` or `dataclasses.replace` | `Python/src/Prototype/Conceptual/main.py` |
| Singleton | AST | Module-level constant or `functools.cache` | `Python/src/Singleton/Conceptual/ThreadSafe/main.py` and `Python/src/Singleton/Conceptual/NonThreadSafe/main.py` |

### Structural

| Pattern | Detection | Pythonic refactor target | Python archive example |
|---------|-----------|---------------------------|------------------------|
| Adapter | AST (shared with Proxy) | `typing.Protocol` + duck typing or `__getattr__` forwarding | `Python/src/Adapter/Conceptual/object/main.py` and `Python/src/Adapter/Conceptual/class/main.py` |
| Bridge | Reference | Composition of independent abstractions; pass impl as parameter | `Python/src/Bridge/Conceptual/main.py` |
| Composite | AST | Recursive `dataclass` tree (only when truly hierarchical) | `Python/src/Composite/Conceptual/main.py` |
| Decorator | AST (class form) | Function decorator + `functools.wraps` | `Python/src/Decorator/Conceptual/main.py` |
| Facade | AST (static-only) | Module-level functions | `Python/src/Facade/Conceptual/main.py` |
| Flyweight | Reference | `functools.cache` / `weakref.WeakValueDictionary` | `Python/src/Flyweight/Conceptual/main.py` |
| Proxy | AST (shared with Adapter) | `__getattr__` forwarding or `typing.Protocol` | `Python/src/Proxy/Conceptual/main.py` |

### Behavioral

| Pattern | Detection | Pythonic refactor target | Python archive example |
|---------|-----------|---------------------------|------------------------|
| Chain of Responsibility | AST | List of handler functions, iterated until one returns non-`None` | `Python/src/ChainOfResponsibility/Conceptual/main.py` |
| Command | AST | `functools.partial` or closure | `Python/src/Command/Conceptual/main.py` |
| Iterator | AST | Generator function (`yield`) | `Python/src/Iterator/Conceptual/main.py` |
| Mediator | AST | Module-level event bus or `asyncio.Queue` | `Python/src/Mediator/Conceptual/main.py` |
| Memento | AST | `copy.deepcopy` snapshot or `dataclasses.replace` | `Python/src/Memento/Conceptual/main.py` |
| Observer | AST | Callable list or `weakref.WeakSet` | `Python/src/Observer/Conceptual/main.py` |
| State | AST | Plain attribute + `match`/dispatch table | `Python/src/State/Conceptual/main.py` |
| Strategy | AST | First-class function or `Callable[..., R]` | `Python/src/Strategy/Conceptual/main.py` |
| Template Method | AST | Pass a callable; or use composition over inheritance | `Python/src/TemplateMethod/Conceptual/main.py` |
| Visitor | AST (two detectors) | `@functools.singledispatch` or `match` statement | `Python/src/Visitor/Conceptual/main.py` |

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
- **Reference-mode patterns:** Bridge, Flyweight, Factory Method are covered by the example corpus; agent does eye-review against `CHORE.md` rather than expecting AST hits

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

For Bridge, Flyweight, and Factory Method (example-only patterns), open the matching `Python/src/<Pattern>/Conceptual/main.py` from the archive side-by-side with any module ranked B-or-worse by xenon. Note candidates inline in the same report under a `## Reference-mode candidates` section.

### 4. Triage and disposition

For each candidate (AST or reference-mode), mark one of:

- `applied` — operator/agent applied the Pythonic rewrite (route to `pythonic-design-pattern-application` for evidence capture)
- `deferred` — opportunity is real but parked (note the GHI tracking the deferral)
- `not-pythonic-rewrite` — class shape is genuinely the right fit (e.g. State machine with many states; Composite tree that is truly hierarchical)

Empty triage is a defect: every flagged candidate gets a disposition before the chore is considered done for this period.

Disposition rows must include the Python example evidence:

```markdown
- Example: `Python/src/Strategy/Conceptual/main.py`
- Output: `Python/src/Strategy/Conceptual/Output.txt`
- Role map: Context delegates ordering behavior to interchangeable strategy objects.
- Pythonic collapse: replace strategy subclasses with named callables because gzkit only needs behavior injection, not stateful strategy objects.
- Disposition: applied -> `.gzkit/chores/pythonic-design-pattern-application/proofs/application-...md`
```

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
- Letting reference-mode patterns lapse to "we don't detect those" — the example corpus exists so the agent can eye-review against it; skipping the eye-review collapses the post-post-implementation contract back to mechanical-only
- Citing pattern names without reading the local Python example from the archive — the chore requires role-level comparison, not memory recall

## Run Log

| Run Date | AST Candidates | Reference Notes | Applied | Deferred | Not-Pythonic | Notes |
|----------|----------------|------------------|---------|----------|--------------|-------|
| _YYYY-MM-DD_ | _N_ | _N_ | _N_ | _N_ | _N_ | _scope notes_ |

---

**End of CHORE: Pythonic Design Pattern Detection**
