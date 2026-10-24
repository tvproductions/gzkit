"""Identity seam scope: one grammar and one resolver, ratcheted to zero (drydock RO-2).

`docs/governance/harbor-ro2-identity-seam.md` § The witness. Three checks:

- **The scan.** An AST pass over ``src/gzkit/**/*.py`` finds every regex literal
  handed to ``re`` or to a ``pattern=`` keyword that encodes an ADR, OBPI, REQ or
  TASK grammar, every ``split``, slice or prefix rewrite of a value named as an
  id (a ``parent`` site), and every f-string that composes an id from parts, a
  parent recovered from parsed fields or a child-prefix scan (a ``compose``
  site; tranche 5 owns both). The seam modules are exempt. An embedded hook script
  (a string handed to ``dedent``) is parsed and scanned as the Python it is.
- **The baseline.** ``data/id_seam_baseline.json`` holds today's sites keyed by
  file and enclosing symbol, never by line, with a site count. A site the baseline
  does not hold fails; so does a row whose sites are gone or fewer, so the
  baseline cannot carry dead rows. It is a registered ``shrink-ratchet``, and
  RO-2 closes when it is empty.
- **The resolution check.** Every ``@covers`` REQ, every scenario REQ tag, and
  every OBPI and ADR id in brief frontmatter resolves through
  :func:`gzkit.core.id_resolver.resolve` to exactly one artifact, active or
  recorded parked or withdrawn.

Registered as ``gz validate --id-seam``; runs in ``gz check`` as the "Identity seam"
step.
"""

import ast
import re
import textwrap
from collections import Counter
from collections.abc import Iterable
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.config import GzkitConfig
from gzkit.core.id_resolver import (
    IdentityContext,
    IdResolutionError,
    brief_files,
    load_identity_context,
    resolve,
)
from gzkit.core.models import IdKind
from gzkit.core.validation_rules import ValidationError
from gzkit.frontmatter import read_frontmatter
from gzkit.ledger import Ledger
from gzkit.registries import RegistryError, load_registry

__all__ = [
    "BASELINE_RELPATH",
    "SEAM_MODULES",
    "SeamSite",
    "audit_id_seam",
    "check_id_resolution",
    "check_seam_baseline",
    "collect_cited_ids",
    "scan_seam_sites",
    "scan_source",
]

#: Read through :func:`gzkit.registries.load_registry`, the one config read seam.
BASELINE_NAME = "id_seam_baseline.json"
BASELINE_RELPATH = f"data/{BASELINE_NAME}"
SEAM_MODULES = frozenset({"src/gzkit/core/models.py", "src/gzkit/core/id_resolver.py"})

_SPEC = "docs/governance/harbor-ro2-identity-seam.md"
_RE_FUNCTIONS = frozenset(
    {"compile", "match", "search", "fullmatch", "findall", "finditer", "sub", "subn", "split"}
)
_SPLITTERS = frozenset({"split", "rsplit", "partition", "rpartition"})
_REWRITERS = frozenset({"replace", "removeprefix", "removesuffix"})
_SEPARATORS = frozenset({"-", "."})
_KINDS = tuple(kind.value for kind in IdKind)
# Built from the kind names, never spelled: a literal here would be a site itself.
_KIND_TOKEN = re.compile("(?<![A-Za-z])(" + "|".join(_KINDS) + ")(?![A-Za-z])")
_ID_NAME = re.compile(r"(?i)(?:^|_)(adr|obpi|req|task)(?:_|$|id$|s$)")
# A name ending in one of these holds prose about an artifact (a REQ's statement), never its id.
_PROSE_NAME = re.compile(r"(?i)_(text|body|summary|title)$")
_MODULE = "<module>"


class SeamSite(BaseModel):
    """One id grammar or spelling-derived parent outside the seam."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    file: str = Field(..., description="Repository-relative POSIX path")
    symbol: str = Field(..., description="Enclosing class/function path, or <module>")
    kind: str = Field(..., description="ADR, OBPI, REQ, TASK, parent, compose, or hook")
    line: int = Field(..., description="Line of the site, for messages only")


def _module_strings(tree: ast.Module) -> dict[str, str]:
    consts: dict[str, str] = {}
    for node in tree.body:
        target = value = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target, value = node.targets[0], node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            target, value = node.target, node.value
        if isinstance(target, ast.Name) and value is not None:
            text = _literal_text(value, consts)
            if text is not None:
                consts[target.id] = text
    return consts


def _literal_text(node: ast.expr, consts: dict[str, str]) -> str | None:
    """Return the literal text an expression spells, or None when it spells none.

    An f-string's interpolations read as ``{}``, so a pattern that embeds a seam
    body contributes only its own literal parts.
    """
    if isinstance(node, ast.Constant):
        return node.value if isinstance(node.value, str) else None
    if isinstance(node, ast.JoinedStr):
        return "".join(
            str(part.value) if isinstance(part, ast.Constant) else "{}" for part in node.values
        )
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = _literal_text(node.left, consts), _literal_text(node.right, consts)
        return None if left is None or right is None else left + right
    if isinstance(node, ast.Name):
        return consts.get(node.id)
    return None


def _grammar_kinds(text: str) -> list[str]:
    if "-" not in text:
        return []
    return sorted(set(_KIND_TOKEN.findall(text)))


def _names_an_id(node: ast.expr) -> bool:
    name = node.id if isinstance(node, ast.Name) else getattr(node, "attr", None)
    return (
        isinstance(name, str)
        and _ID_NAME.search(name) is not None
        and _PROSE_NAME.search(name) is None
    )


def _is_re_call(func: ast.expr) -> bool:
    return (
        isinstance(func, ast.Attribute)
        and func.attr in _RE_FUNCTIONS
        and isinstance(func.value, ast.Name)
        and func.value.id == "re"
    )


def _is_dedent(func: ast.expr) -> bool:
    name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
    return name == "dedent"


def _is_parent_call(node: ast.Call) -> bool:
    func = node.func
    if not isinstance(func, ast.Attribute):
        return False
    first = node.args[0] if node.args else None
    literal = first.value if isinstance(first, ast.Constant) else None
    if func.attr in _SPLITTERS:
        return _names_an_id(func.value) and (first is None or literal in _SEPARATORS)
    if func.attr in _REWRITERS:
        return isinstance(literal, str) and literal.startswith(tuple(f"{k}-" for k in _KINDS))
    return False


def _composes_id(node: ast.JoinedStr) -> bool:
    """Report an id-shaped f-string: ``<KIND>-`` first, then parts, and no whitespace.

    Prose and template lines that mention an id (``f"OBPI-{x} not found"``) carry
    whitespace and are not compositions.
    """
    head = node.values[0] if node.values else None
    if not (isinstance(head, ast.Constant) and isinstance(head.value, str)):
        return False
    if not head.value.startswith(tuple(f"{kind}-" for kind in _KINDS)):
        return False
    literal = "".join(str(p.value) for p in node.values if isinstance(p, ast.Constant))
    return len(node.values) > 1 and not any(char.isspace() for char in literal)


class _Scanner(ast.NodeVisitor):
    def __init__(self, file: str, consts: dict[str, str], prefix: str = "") -> None:
        self.file = file
        self.consts = consts
        self.prefix = prefix
        self.stack: list[str] = []
        self.sites: list[SeamSite] = []
        self.consumed: set[int] = set()

    def _symbol(self) -> str:
        return self.prefix + (".".join(self.stack) or _MODULE)

    def _add(self, kind: str, line: int) -> None:
        self.sites.append(SeamSite(file=self.file, symbol=self._symbol(), kind=kind, line=line))

    def _enter(self, node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    visit_ClassDef = _enter
    visit_FunctionDef = _enter
    visit_AsyncFunctionDef = _enter

    def _add_grammar(self, node: ast.expr | None, line: int) -> None:
        if isinstance(node, ast.JoinedStr):
            self.consumed.add(id(node))
        text = _literal_text(node, self.consts) if node is not None else None
        for kind in _grammar_kinds(text or ""):
            self._add(kind, line)

    def visit_Call(self, node: ast.Call) -> None:
        if _is_re_call(node.func) and node.args:
            self._add_grammar(node.args[0], node.lineno)
        for keyword in node.keywords:
            if keyword.arg == "pattern":
                self._add_grammar(keyword.value, node.lineno)
        if _is_parent_call(node):
            self._add("parent", node.lineno)
        if _is_dedent(node.func) and node.args and isinstance(node.args[0], ast.Constant):
            self._scan_embedded(node.args[0], node.lineno)
        self.generic_visit(node)

    def visit_JoinedStr(self, node: ast.JoinedStr) -> None:
        if id(node) not in self.consumed and _composes_id(node):
            self._add("compose", node.lineno)
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        if isinstance(node.slice, ast.Slice) and _names_an_id(node.value):
            self._add("parent", node.lineno)
        self.generic_visit(node)

    def _scan_embedded(self, node: ast.Constant, line: int) -> None:
        if not isinstance(node.value, str):
            return
        text = textwrap.dedent(node.value)
        try:
            inner = ast.parse(text)
        except SyntaxError:
            if _grammar_kinds(text):
                self._add("hook", line)
            return
        scanner = _Scanner(self.file, _module_strings(inner), prefix=f"{self._symbol()}:")
        scanner.visit(inner)
        self.sites.extend(scanner.sites)


def scan_source(text: str, file: str) -> list[SeamSite]:
    """Return the seam sites in one module's source text."""
    tree = ast.parse(text)
    scanner = _Scanner(file, _module_strings(tree))
    scanner.visit(tree)
    return scanner.sites


def scan_seam_sites(root: Path) -> list[SeamSite]:
    """Return every seam site under ``src/gzkit``, the seam modules excepted."""
    sites: list[SeamSite] = []
    for path in sorted((root / "src" / "gzkit").rglob("*.py")):
        rel = path.relative_to(root).as_posix()
        if rel in SEAM_MODULES or "__pycache__" in path.parts:
            continue
        sites.extend(scan_source(path.read_text(encoding="utf-8"), rel))
    return sites


def _err(artifact: str, message: str) -> ValidationError:
    return ValidationError(type="id_seam", artifact=artifact, message=message)


def check_seam_baseline(sites: Iterable[SeamSite], rows: list[dict]) -> list[ValidationError]:
    """Compare today's sites with the baseline, which may only shrink and must stay exact."""
    current = Counter((site.file, site.symbol, site.kind) for site in sites)
    seeded: dict[tuple[str, str, str], int] = {}
    errors: list[ValidationError] = []
    for row in rows:
        key = (str(row["file"]), str(row["symbol"]), str(row["kind"]))
        if key in seeded:
            errors.append(
                _err(
                    "::".join(key),
                    f"{BASELINE_RELPATH} holds this site twice. The baseline is keyed by file, "
                    f"symbol and kind ({_SPEC} § The witness). Merge the rows into one and "
                    "re-run `uv run gz validate --id-seam`.",
                )
            )
        seeded[key] = int(row["sites"])
    for key, count in sorted(current.items()):
        allowed = seeded.get(key, 0)
        if count > allowed:
            errors.append(
                _err(
                    "::".join(key),
                    f"{count - allowed} {key[2]} id-grammar site(s) outside the identity seam that "
                    f"{BASELINE_RELPATH} does not hold. Nothing outside the seam spells an id "
                    f"grammar or derives a parent from an id's spelling ({_SPEC} § The seam), and "
                    "the baseline only shrinks. Import the grammar body from gzkit.core.models or "
                    "call gzkit.core.id_resolver.resolve / parent_of, then re-run "
                    "`uv run gz validate --id-seam`.",
                )
            )
    for key, count in sorted(seeded.items()):
        have = current.get(key, 0)
        if have < count:
            action = "Delete the row" if have == 0 else f"Lower its sites to {have}"
            errors.append(
                _err(
                    "::".join(key),
                    f"{BASELINE_RELPATH} holds {count} site(s) here and the scan finds {have}. "
                    f"The baseline may not carry dead rows ({_SPEC} § The witness). {action}, "
                    "set the registry's baseline_count in data/waiver_ratchet_registry.json to "
                    "the row count, and re-run `uv run gz validate --id-seam`.",
                )
            )
    return errors


def _bindable_definitions(
    body: list[ast.stmt],
) -> Iterable[ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef]:
    """Yield module- and class-level definitions; a def nested in a function binds nothing.

    A ``@covers`` inside a test body is that test's fixture (``covers()``'s own
    negative tests decorate a throwaway function to watch it refuse), not a binding.
    """
    for node in body:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            yield node
        elif isinstance(node, ast.ClassDef):
            yield node
            yield from _bindable_definitions(node.body)


def _covers_decorations(path: Path, rel: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for node in _bindable_definitions(ast.parse(path.read_text(encoding="utf-8")).body):
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call) or not decorator.args:
                continue
            func = decorator.func
            name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
            first = decorator.args[0]
            if (
                name == "covers"
                and isinstance(first, ast.Constant)
                and isinstance(first.value, str)
            ):
                found.append((f"{rel}:{decorator.lineno}", first.value))
    return found


def collect_cited_ids(root: Path, design_root: str) -> list[tuple[str, str]]:
    """Return ``(source, id)`` for every id the resolution check must resolve."""
    cited: list[tuple[str, str]] = []
    for path in sorted((root / "tests").rglob("*.py")):
        cited.extend(_covers_decorations(path, path.relative_to(root).as_posix()))
    for path in sorted((root / "features").rglob("*.feature")):
        rel = path.relative_to(root).as_posix()
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.lstrip().startswith("@"):
                cited.extend(
                    (f"{rel}:{number}", token[1:])
                    for token in line.split()
                    if token.startswith("@REQ-")
                )
    for path in brief_files(root, design_root):
        rel = path.relative_to(root).as_posix()
        fields = read_frontmatter(path.read_text(encoding="utf-8")).fields
        for key in ("id", "parent"):
            value = fields.get(key, "")
            if value.startswith(("OBPI-", "ADR-")):
                cited.append((f"{rel} ({key})", value))
    return cited


def check_id_resolution(
    cited: Iterable[tuple[str, str]], context: IdentityContext
) -> list[ValidationError]:
    """Fail every cited id the seam's resolver cannot name exactly one artifact for."""
    errors: list[ValidationError] = []
    for source, identifier in dict.fromkeys(cited):
        try:
            resolve(identifier, context)
        except IdResolutionError as exc:
            errors.append(
                _err(
                    source,
                    f"{identifier} does not resolve: {exc}. Every @covers REQ, scenario REQ tag "
                    f"and brief frontmatter OBPI or ADR id names exactly one artifact through "
                    f"the identity seam ({_SPEC} § The witness). Correct the citation to an id "
                    "the ledger and briefs record, then re-run `uv run gz validate --id-seam`.",
                )
            )
    return errors


def audit_id_seam(root: Path) -> list[ValidationError]:
    """Run the scan against the baseline, then the resolution check."""
    config = GzkitConfig.load(root / ".gzkit.json")
    try:
        rows = load_registry(root, BASELINE_NAME)["sites"]
    except (RegistryError, KeyError, TypeError) as exc:
        return [
            _err(
                BASELINE_RELPATH,
                f"{BASELINE_RELPATH} cannot be read ({exc}), so no site outside the identity "
                f"seam is accounted for ({_SPEC} § The witness). Restore it from git and "
                "re-run `uv run gz validate --id-seam`.",
            )
        ]
    errors = check_seam_baseline(scan_seam_sites(root), rows)
    design_root = config.paths.design_root
    context = load_identity_context(Ledger(root / config.paths.ledger), root, design_root)
    errors.extend(check_id_resolution(collect_cited_ids(root, design_root), context))
    return errors
