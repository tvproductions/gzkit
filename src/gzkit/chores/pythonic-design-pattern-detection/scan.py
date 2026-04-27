"""AST-based Pythonic design pattern opportunity scanner.

Walks a Python source tree and emits a markdown report enumerating
candidates where a Java-flavored class shape has a cleaner Pythonic
refactor target. Stdlib only; cross-platform; UTF-8 safe.

Coverage targets all 22 GoF patterns catalogued at
https://refactoring.guru/design-patterns/python — those that admit a
mechanical AST signal are detected; the rest are catalogued in CHORE.md
as reference-only entries with their `python/example` URL for absorption.

Usage:
    python scan.py --root src --out proofs/candidates-YYYY-MM-DD.md
    python scan.py --self-test
"""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import sys
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import NamedTuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


REFACTORING_GURU = "https://refactoring.guru/design-patterns"


class Candidate(NamedTuple):
    file: Path
    line: int
    class_name: str
    pattern: str
    signal: str
    pythonic_target: str
    guru_url: str


def _public_methods(cls: ast.ClassDef) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [
        node
        for node in cls.body
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        and not (node.name.startswith("__") and node.name.endswith("__"))
    ]


def _all_methods(cls: ast.ClassDef) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [node for node in cls.body if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)]


def _has_method(cls: ast.ClassDef, name: str) -> bool:
    return any(m.name == name for m in _all_methods(cls))


def _has_decorator(node: ast.FunctionDef | ast.AsyncFunctionDef, name: str) -> bool:
    for dec in node.decorator_list:
        if isinstance(dec, ast.Name) and dec.id == name:
            return True
        if isinstance(dec, ast.Attribute) and dec.attr == name:
            return True
    return False


def _is_protocol_or_abc(cls: ast.ClassDef) -> bool:
    for base in cls.bases:
        if isinstance(base, ast.Name) and base.id in {"Protocol", "ABC", "ABCMeta"}:
            return True
        if isinstance(base, ast.Attribute) and base.attr in {"Protocol", "ABC", "ABCMeta"}:
            return True
    return False


def _detect_strategy(cls: ast.ClassDef) -> str | None:
    publics = _public_methods(cls)
    if len(publics) != 1:
        return None
    if not _has_method(cls, "__init__"):
        return None
    if _is_protocol_or_abc(cls):
        return None
    return f"Class with __init__ + exactly one public method ({publics[0].name!r})"


def _detect_singleton(cls: ast.ClassDef) -> str | None:
    has_instance_factory = any(
        m.name in {"getInstance", "get_instance", "instance"} for m in _all_methods(cls)
    )
    has_class_var_instance = False
    for stmt in cls.body:
        targets: list[ast.expr] = []
        if isinstance(stmt, ast.AnnAssign):
            targets = [stmt.target]
        elif isinstance(stmt, ast.Assign):
            targets = list(stmt.targets)
        for t in targets:
            if isinstance(t, ast.Name) and t.id in {"_instance", "__instance"}:
                has_class_var_instance = True
    if has_instance_factory and has_class_var_instance:
        return "Class-level _instance attr + factory method (getInstance/get_instance/instance)"
    if has_instance_factory:
        return "Singleton-style factory method (getInstance/get_instance/instance) on a class"
    return None


def _detect_iterator(cls: ast.ClassDef) -> str | None:
    if _has_method(cls, "__iter__") and _has_method(cls, "__next__"):
        return "Class defines both __iter__ and __next__"
    return None


def _detect_decorator_class(cls: ast.ClassDef) -> str | None:
    init = next((m for m in _all_methods(cls) if m.name == "__init__"), None)
    if init is None or not _has_method(cls, "__call__"):
        return None
    args = init.args.args
    non_self_args = [a for a in args if a.arg != "self"]
    if len(non_self_args) == 1 and non_self_args[0].arg in {"fn", "func", "f", "callable"}:
        return f"__init__(self, {non_self_args[0].arg}) + __call__ (callable wrapper class)"
    return None


def _detect_context_manager_class(cls: ast.ClassDef) -> str | None:
    if not (_has_method(cls, "__enter__") and _has_method(cls, "__exit__")):
        return None
    publics = _public_methods(cls)
    if len(publics) <= 1:
        return "Class defines __enter__ + __exit__ with at most one other method"
    return None


def _detect_facade_class(cls: ast.ClassDef) -> str | None:
    methods = _all_methods(cls)
    if not methods:
        return None
    if any(m.name == "__init__" for m in methods):
        return None
    publics = _public_methods(cls)
    if not publics:
        return None
    if all(_has_decorator(m, "staticmethod") for m in publics):
        return f"All {len(publics)} public methods are @staticmethod, no __init__"
    return None


def _detect_observer_class(cls: ast.ClassDef) -> str | None:
    method_names = {m.name for m in _all_methods(cls)}
    triads = [
        {"subscribe", "unsubscribe", "notify"},
        {"attach", "detach", "notify"},
        {"add_listener", "remove_listener", "notify"},
        {"register", "unregister", "notify"},
    ]
    for triad in triads:
        if triad.issubset(method_names):
            return f"Class defines observer triad: {sorted(triad)}"
    return None


def _detect_command_class(cls: ast.ClassDef) -> str | None:
    publics = _public_methods(cls)
    if len(publics) != 1:
        return None
    if publics[0].name not in {"execute", "run", "do", "perform"}:
        return None
    if not _has_method(cls, "__init__"):
        return None
    return f"Class with __init__ + single {publics[0].name!r} method"


def _detect_builder_class(cls: ast.ClassDef) -> str | None:
    publics = _public_methods(cls)
    if len(publics) < 2:
        return None
    chain_methods = [
        m
        for m in publics
        if m.name.startswith(("with_", "set_", "add_"))
        and any(
            isinstance(stmt, ast.Return)
            and isinstance(stmt.value, ast.Name)
            and stmt.value.id == "self"
            for stmt in ast.walk(m)
        )
    ]
    if len(chain_methods) >= 2:
        names = sorted(m.name for m in chain_methods)
        return f"Class has >=2 chain methods returning self ({names})"
    return None


def _detect_abstract_factory(cls: ast.ClassDef) -> str | None:
    publics = _public_methods(cls)
    create_methods = [m for m in publics if m.name.startswith(("create_", "make_", "build_"))]
    if len(create_methods) < 2:
        return None
    if len(create_methods) < len(publics) // 2 + 1:
        return None
    names = sorted(m.name for m in create_methods)
    return f"Class with >=2 factory methods ({names})"


def _detect_prototype(cls: ast.ClassDef) -> str | None:
    if _has_method(cls, "clone") or _has_method(cls, "copy"):
        publics = {m.name for m in _public_methods(cls)}
        if "clone" in publics:
            return "Class defines a `clone()` method"
        if "copy" in publics and not any(
            isinstance(b, ast.Name) and b.id in {"dict", "list", "set"} for b in cls.bases
        ):
            return "Class defines a `copy()` method (Prototype-shaped)"
    return None


def _detect_composite(cls: ast.ClassDef) -> str | None:
    methods = {m.name for m in _all_methods(cls)}
    pairs = [
        ({"add", "remove"}, "add/remove"),
        ({"add_child", "remove_child"}, "add_child/remove_child"),
        ({"append", "remove"}, "append/remove"),
    ]
    for pair, label in pairs:
        if not pair.issubset(methods):
            continue
        for stmt in ast.walk(cls):
            if isinstance(stmt, ast.Assign):
                for t in stmt.targets:
                    if (
                        isinstance(t, ast.Attribute)
                        and isinstance(t.value, ast.Name)
                        and t.value.id == "self"
                        and t.attr in {"children", "_children", "subtree", "items"}
                    ):
                        return (
                            f"Class with {label} methods + self.{t.attr} container "
                            "(recursive structure)"
                        )
    return None


def _detect_chain_of_responsibility(cls: ast.ClassDef) -> str | None:
    methods = {m.name for m in _all_methods(cls)}
    next_setters = {"set_next", "set_successor", "link"}
    handlers = {"handle", "handle_request", "process"}
    if methods & next_setters and methods & handlers:
        used_setter = (methods & next_setters).pop()
        used_handler = (methods & handlers).pop()
        return f"Class with {used_setter}() + {used_handler}() (handler-chain shape)"
    return None


def _detect_visitor_accept(cls: ast.ClassDef) -> str | None:
    accept = next(
        (m for m in _all_methods(cls) if m.name == "accept"),
        None,
    )
    if accept is None:
        return None
    args = [a.arg for a in accept.args.args]
    if "visitor" in args or len(args) == 2:
        return "Class defines `accept(self, visitor)` method (Visitor element shape)"
    return None


def _detect_visitor_dispatch(cls: ast.ClassDef) -> str | None:
    visit_methods = [m for m in _public_methods(cls) if m.name.startswith("visit_")]
    if len(visit_methods) >= 2:
        names = sorted(m.name for m in visit_methods)
        return f"Class with >=2 visit_* methods ({names})"
    return None


def _detect_template_method(cls: ast.ClassDef) -> str | None:
    methods = _all_methods(cls)
    abstract_methods = [m for m in methods if _has_decorator(m, "abstractmethod")]
    concrete_methods = [
        m for m in methods if not _has_decorator(m, "abstractmethod") and m.name != "__init__"
    ]
    if not abstract_methods or not concrete_methods:
        return None
    abstract_names = {m.name for m in abstract_methods}
    for concrete in concrete_methods:
        for node in ast.walk(concrete):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "self"
                and node.func.attr in abstract_names
            ):
                return (
                    f"Class with @abstractmethod + concrete `{concrete.name}` "
                    f"calling self.{node.func.attr}() (Template Method shape)"
                )
    return None


def _detect_state(cls: ast.ClassDef) -> str | None:
    methods = {m.name for m in _all_methods(cls)}
    if "set_state" in methods or "transition_to" in methods or "change_state" in methods:
        for stmt in ast.walk(cls):
            if isinstance(stmt, ast.Assign):
                for t in stmt.targets:
                    if (
                        isinstance(t, ast.Attribute)
                        and isinstance(t.value, ast.Name)
                        and t.value.id == "self"
                        and t.attr in {"state", "_state"}
                    ):
                        return "Class with set_state/transition_to + self.state assignment"
    return None


def _detect_memento(cls: ast.ClassDef) -> str | None:
    methods = {m.name for m in _all_methods(cls)}
    save_names = {"save", "save_state", "create_memento", "snapshot"}
    restore_names = {"restore", "restore_state", "set_memento", "rollback"}
    saves = methods & save_names
    restores = methods & restore_names
    if saves and restores:
        return f"Class pairs save-side ({sorted(saves)}) with restore-side ({sorted(restores)})"
    return None


def _detect_mediator(cls: ast.ClassDef) -> str | None:
    methods = {m.name for m in _all_methods(cls)}
    if "notify" in methods and ("register" in methods or "add_colleague" in methods):
        notify = next(m for m in _all_methods(cls) if m.name == "notify")
        args = [a.arg for a in notify.args.args]
        if len(args) >= 3:
            arg_list = ", ".join(args[1:])
            return f"Class with `notify({arg_list})` + register/add_colleague (Mediator shape)"
    return None


def _detect_adapter_or_proxy(cls: ast.ClassDef) -> str | None:
    init = next((m for m in _all_methods(cls) if m.name == "__init__"), None)
    if init is None:
        return None
    non_self = [a.arg for a in init.args.args if a.arg != "self"]
    if len(non_self) != 1:
        return None
    wrappee = non_self[0]
    if wrappee not in {"adaptee", "wrappee", "target", "real_subject", "subject", "service"}:
        return None
    publics = _public_methods(cls)
    if not publics:
        return None
    delegating = 0
    for m in publics:
        for node in ast.walk(m):
            if (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Attribute)
                and isinstance(node.value.value, ast.Name)
                and node.value.value.id == "self"
                and node.value.attr == wrappee
            ):
                delegating += 1
                break
    if delegating >= max(1, len(publics) // 2):
        return (
            f"Class with __init__(self, {wrappee}) + "
            f"{delegating} method(s) delegating to self.{wrappee}"
        )
    return None


CLASS_DETECTORS: tuple[tuple[str, object, str, str], ...] = (
    (
        "Strategy",
        _detect_strategy,
        "First-class function or `Callable[..., R]`",
        "/strategy/python/example",
    ),
    (
        "Singleton",
        _detect_singleton,
        "Module-level constant or `functools.cache`",
        "/singleton/python/example",
    ),
    (
        "Abstract Factory",
        _detect_abstract_factory,
        "Module of factory functions or `dataclass` registry",
        "/abstract-factory/python/example",
    ),
    (
        "Prototype",
        _detect_prototype,
        "`copy.deepcopy` or `dataclass.replace`",
        "/prototype/python/example",
    ),
    (
        "Builder",
        _detect_builder_class,
        "`dataclass`/Pydantic + `@classmethod` factory",
        "/builder/python/example",
    ),
    ("Iterator", _detect_iterator, "Generator function (`yield`)", "/iterator/python/example"),
    (
        "Decorator (class)",
        _detect_decorator_class,
        "Function decorator + `functools.wraps`",
        "/decorator/python/example",
    ),
    (
        "Context manager (class)",
        _detect_context_manager_class,
        "`@contextlib.contextmanager` generator (Python idiom — not GoF)",
        "/decorator/python/example",
    ),
    (
        "Facade (static-only class)",
        _detect_facade_class,
        "Module-level functions",
        "/facade/python/example",
    ),
    (
        "Adapter / Proxy",
        _detect_adapter_or_proxy,
        "`typing.Protocol` + duck typing or `__getattr__` forwarding",
        "/adapter/python/example",
    ),
    (
        "Composite",
        _detect_composite,
        "Recursive `dataclass` tree (only when truly hierarchical)",
        "/composite/python/example",
    ),
    (
        "Chain of Responsibility",
        _detect_chain_of_responsibility,
        "List of handler functions, iterated until one returns a non-`None` result",
        "/chain-of-responsibility/python/example",
    ),
    ("Command", _detect_command_class, "`functools.partial` or closure", "/command/python/example"),
    (
        "Mediator",
        _detect_mediator,
        "Module-level event bus or `asyncio.Queue`",
        "/mediator/python/example",
    ),
    (
        "Memento",
        _detect_memento,
        "`copy.deepcopy` snapshot / `dataclass.replace`",
        "/memento/python/example",
    ),
    (
        "Observer",
        _detect_observer_class,
        "Callable list or `weakref.WeakSet`",
        "/observer/python/example",
    ),
    ("State", _detect_state, "Plain attribute + `match`/dispatch table", "/state/python/example"),
    (
        "Template Method",
        _detect_template_method,
        "Pass a callable; or use composition over inheritance",
        "/template-method/python/example",
    ),
    (
        "Visitor (accept)",
        _detect_visitor_accept,
        "`@functools.singledispatch` or `match` statement",
        "/visitor/python/example",
    ),
    (
        "Visitor (visit_* dispatch)",
        _detect_visitor_dispatch,
        "`@functools.singledispatch` or `match` statement",
        "/visitor/python/example",
    ),
)


def _count_isinstance_in_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> int:
    return sum(
        1
        for n in ast.walk(node)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "isinstance"
    )


def _detect_isinstance_chain(
    func: ast.FunctionDef | ast.AsyncFunctionDef,
) -> str | None:
    count = _count_isinstance_in_function(func)
    if count >= 3:
        return f"Function `{func.name}` contains {count} isinstance() calls"
    return None


def scan_file(path: Path, source: str) -> Iterator[Candidate]:
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for pattern, detector, target, suffix in CLASS_DETECTORS:
                signal = detector(node)  # type: ignore
                if signal:
                    yield Candidate(
                        file=path,
                        line=node.lineno,
                        class_name=node.name,
                        pattern=pattern,
                        signal=signal,
                        pythonic_target=target,
                        guru_url=REFACTORING_GURU + suffix,
                    )

        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            chain = _detect_isinstance_chain(node)
            if chain:
                yield Candidate(
                    file=path,
                    line=node.lineno,
                    class_name=node.name,
                    pattern="isinstance dispatch chain",
                    signal=chain,
                    pythonic_target="`match` statement or `@functools.singledispatch`",
                    guru_url=REFACTORING_GURU + "/visitor/python/example",
                )


def scan_root(root: Path, exclude: Iterable[str]) -> list[Candidate]:
    excludes = tuple(exclude)
    candidates: list[Candidate] = []
    for path in sorted(root.rglob("*.py")):
        rel_parts = path.relative_to(root.parent if root.parent != root else root).parts
        if any(part in excludes for part in rel_parts):
            continue
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        candidates.extend(scan_file(path, source))
    return candidates


def render_report(candidates: list[Candidate], root: Path, scanned_count: int) -> str:
    today = dt.date.today().isoformat()
    lines: list[str] = [
        f"# Pythonic Design Pattern Candidates — {today}",
        "",
        f"- **Scanned root:** `{root}`",
        f"- **Files scanned:** {scanned_count}",
        f"- **Candidates flagged:** {len(candidates)}",
        "",
    ]
    if not candidates:
        lines.extend(
            [
                "`NO_CANDIDATES_DETECTED`",
                "",
                "No Java-flavored class shapes detected by mechanical signal. "
                "The catalogue includes patterns whose detection is reference-only "
                "(Bridge, Flyweight, Factory Method as a generic shape) — those "
                "require human-eye review against `CHORE.md`'s catalogue table.",
                "",
            ]
        )
        return "\n".join(lines) + "\n"
    by_pattern: dict[str, list[Candidate]] = {}
    for c in candidates:
        by_pattern.setdefault(c.pattern, []).append(c)
    lines.extend(
        [
            "## Summary",
            "",
            "| Pattern | Count | Pythonic target |",
            "|---------|-------|-----------------|",
        ]
    )
    for pattern in sorted(by_pattern):
        first = by_pattern[pattern][0]
        lines.append(f"| {pattern} | {len(by_pattern[pattern])} | {first.pythonic_target} |")
    lines.extend(["", "## Candidates", ""])
    for pattern in sorted(by_pattern):
        lines.extend([f"### {pattern}", ""])
        for c in by_pattern[pattern]:
            try:
                rel = c.file.relative_to(Path.cwd())
            except ValueError:
                rel = c.file
            lines.extend(
                [
                    f"- **{rel.as_posix()}:{c.line}** — `{c.class_name}`",
                    f"  - Signal: {c.signal}",
                    f"  - Pythonic target: {c.pythonic_target}",
                    f"  - Absorption ref: {c.guru_url}",
                    "  - Disposition: _[applied | deferred | not-pythonic-rewrite]_",
                    "  - Notes: _[fill in]_",
                    "",
                ]
            )
    return "\n".join(lines) + "\n"


_SELF_TEST_FIXTURES: tuple[tuple[str, str, str], ...] = (
    (
        "Strategy",
        "class PriceStrategy:\n"
        "    def __init__(self, rate):\n"
        "        self.rate = rate\n"
        "    def apply(self, amount):\n"
        "        return amount * self.rate\n",
        "PriceStrategy",
    ),
    (
        "Singleton",
        "class Logger:\n"
        "    _instance = None\n"
        "    @classmethod\n"
        "    def get_instance(cls):\n"
        "        if cls._instance is None:\n"
        "            cls._instance = cls()\n"
        "        return cls._instance\n",
        "Logger",
    ),
    (
        "Abstract Factory",
        "class WidgetFactory:\n"
        "    def create_button(self): return None\n"
        "    def create_window(self): return None\n"
        "    def create_panel(self): return None\n",
        "WidgetFactory",
    ),
    (
        "Prototype",
        "class Document:\n"
        "    def __init__(self, body):\n"
        "        self.body = body\n"
        "    def clone(self):\n"
        "        return Document(self.body)\n",
        "Document",
    ),
    (
        "Builder",
        "class QueryBuilder:\n"
        "    def __init__(self):\n"
        "        self.where = []\n"
        "    def with_filter(self, f):\n"
        "        self.where.append(f)\n"
        "        return self\n"
        "    def with_limit(self, n):\n"
        "        self.limit = n\n"
        "        return self\n"
        "    def build(self):\n"
        "        return self.where\n",
        "QueryBuilder",
    ),
    (
        "Iterator",
        "class Counter:\n"
        "    def __init__(self, n):\n"
        "        self.n = n\n"
        "        self.i = 0\n"
        "    def __iter__(self):\n"
        "        return self\n"
        "    def __next__(self):\n"
        "        if self.i >= self.n:\n"
        "            raise StopIteration\n"
        "        self.i += 1\n"
        "        return self.i\n",
        "Counter",
    ),
    (
        "Decorator (class)",
        "class Memoize:\n"
        "    def __init__(self, fn):\n"
        "        self.fn = fn\n"
        "        self.cache = {}\n"
        "    def __call__(self, *args):\n"
        "        if args not in self.cache:\n"
        "            self.cache[args] = self.fn(*args)\n"
        "        return self.cache[args]\n",
        "Memoize",
    ),
    (
        "Context manager (class)",
        "class Lock:\n"
        "    def __enter__(self):\n"
        "        return self\n"
        "    def __exit__(self, exc_type, exc, tb):\n"
        "        return False\n",
        "Lock",
    ),
    (
        "Facade (static-only class)",
        "class StringUtils:\n"
        "    @staticmethod\n"
        "    def upper(s):\n"
        "        return s.upper()\n"
        "    @staticmethod\n"
        "    def lower(s):\n"
        "        return s.lower()\n",
        "StringUtils",
    ),
    (
        "Adapter / Proxy",
        "class LegacyAdapter:\n"
        "    def __init__(self, adaptee):\n"
        "        self.adaptee = adaptee\n"
        "    def request(self):\n"
        "        return self.adaptee.specific_request()\n"
        "    def status(self):\n"
        "        return self.adaptee.get_status()\n",
        "LegacyAdapter",
    ),
    (
        "Composite",
        "class TreeNode:\n"
        "    def __init__(self):\n"
        "        self.children = []\n"
        "    def add(self, c):\n"
        "        self.children.append(c)\n"
        "    def remove(self, c):\n"
        "        self.children.remove(c)\n",
        "TreeNode",
    ),
    (
        "Chain of Responsibility",
        "class AuthHandler:\n"
        "    def set_next(self, h):\n"
        "        self.next = h\n"
        "        return h\n"
        "    def handle(self, req):\n"
        "        if self.next:\n"
        "            return self.next.handle(req)\n",
        "AuthHandler",
    ),
    (
        "Command",
        "class SaveCommand:\n"
        "    def __init__(self, target, data):\n"
        "        self.target = target\n"
        "        self.data = data\n"
        "    def execute(self):\n"
        "        self.target.write(self.data)\n",
        "SaveCommand",
    ),
    (
        "Mediator",
        "class ChatRoom:\n"
        "    def __init__(self):\n"
        "        self.users = []\n"
        "    def register(self, u):\n"
        "        self.users.append(u)\n"
        "    def notify(self, sender, event):\n"
        "        for u in self.users:\n"
        "            if u is not sender:\n"
        "                u.receive(event)\n",
        "ChatRoom",
    ),
    (
        "Memento",
        "class Editor:\n"
        "    def __init__(self):\n"
        "        self.text = ''\n"
        "    def save_state(self):\n"
        "        return self.text\n"
        "    def restore_state(self, s):\n"
        "        self.text = s\n",
        "Editor",
    ),
    (
        "Observer",
        "class EventBus:\n"
        "    def __init__(self):\n"
        "        self.subs = []\n"
        "    def subscribe(self, fn):\n"
        "        self.subs.append(fn)\n"
        "    def unsubscribe(self, fn):\n"
        "        self.subs.remove(fn)\n"
        "    def notify(self, event):\n"
        "        for fn in self.subs:\n"
        "            fn(event)\n",
        "EventBus",
    ),
    (
        "State",
        "class Connection:\n"
        "    def __init__(self):\n"
        "        self.state = 'closed'\n"
        "    def transition_to(self, s):\n"
        "        self.state = s\n",
        "Connection",
    ),
    (
        "Template Method",
        "from abc import ABC, abstractmethod\n"
        "class Pipeline(ABC):\n"
        "    @abstractmethod\n"
        "    def step_one(self): ...\n"
        "    def run(self):\n"
        "        self.step_one()\n",
        "Pipeline",
    ),
    (
        "Visitor (accept)",
        "class Element:\n    def accept(self, visitor):\n        return visitor.visit(self)\n",
        "Element",
    ),
    (
        "Visitor (visit_* dispatch)",
        "class JsonRenderer:\n"
        "    def visit_int(self, n):\n"
        "        return str(n)\n"
        "    def visit_str(self, s):\n"
        "        return repr(s)\n"
        "    def visit_list(self, lst):\n"
        "        return ','.join(map(str, lst))\n",
        "JsonRenderer",
    ),
    (
        "isinstance dispatch chain",
        "def render(node):\n"
        "    if isinstance(node, int):\n"
        "        return str(node)\n"
        "    elif isinstance(node, list):\n"
        "        return ','.join(str(x) for x in node)\n"
        "    elif isinstance(node, dict):\n"
        "        return '{...}'\n"
        "    return repr(node)\n",
        "render",
    ),
)

_NEGATIVE_FIXTURES: tuple[str, ...] = (
    "class Empty:\n    pass\n",
    "from typing import Protocol\nclass P(Protocol):\n    def do(self, x): ...\n",
    "from dataclasses import dataclass\n@dataclass\nclass Point:\n    x: int\n    y: int\n",
    "def double(x):\n    return x * 2\n",
)


def run_self_test() -> int:
    errors: list[str] = []
    for expected_pattern, source, expected_name in _SELF_TEST_FIXTURES:
        candidates = list(scan_file(Path("<fixture>"), source))
        matching = [c for c in candidates if c.pattern == expected_pattern]
        if not matching:
            errors.append(
                f"FIXTURE MISS: expected pattern {expected_pattern!r} on {expected_name!r}, "
                f"got {[c.pattern for c in candidates]}"
            )
            continue
        if matching[0].class_name != expected_name:
            errors.append(
                f"FIXTURE NAME MISMATCH for {expected_pattern!r}: "
                f"expected {expected_name!r}, got {matching[0].class_name!r}"
            )
    for source in _NEGATIVE_FIXTURES:
        candidates = list(scan_file(Path("<negative>"), source))
        if candidates:
            errors.append(
                f"NEGATIVE FIXTURE FALSE POSITIVE: "
                f"{[(c.class_name, c.pattern) for c in candidates]}"
            )
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 1
    print(f"OK ({len(_SELF_TEST_FIXTURES)} positive, {len(_NEGATIVE_FIXTURES)} negative)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("src"), help="Source tree to scan")
    parser.add_argument("--out", type=Path, help="Markdown output path")
    parser.add_argument(
        "--exclude",
        action="append",
        default=["__pycache__", ".pytest_cache", "tests", "features"],
        help="Path parts to exclude (repeatable)",
    )
    parser.add_argument("--self-test", action="store_true", help="Run embedded fixture self-test")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    if args.out is None:
        parser.error("--out is required when not running --self-test")

    if not args.root.exists():
        print(f"error: --root {args.root} does not exist", file=sys.stderr)
        return 2

    file_count = sum(1 for _ in args.root.rglob("*.py"))
    candidates = scan_root(args.root, args.exclude)
    report = render_report(candidates, args.root, file_count)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(f"wrote {len(candidates)} candidates to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
