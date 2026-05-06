"""Refactor-archetype rule loader for the complexity advisor (OBPI-0.0.29-02).

Per ADR-0.0.29 § Decision rationale #1 + #7, refactor-archetype detection rules
are doctrine, not code: they live as a JSON rule table at
``data/advisor_archetype_rules.json``, validated by the JSON Schema mirror at
``src/gzkit/schemas/advisor_archetype_rules.json``. Amendments flow through
the doctrine-amendment-protocol pool stub forward-referenced from ADR-0.0.27.

The loader returns frozen Pydantic models so the engine's first-match-wins
evaluation cannot accidentally mutate a rule mid-evaluation, and so the rule
shape is enforced twice (JSON Schema at load, Pydantic at construct).
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Literal

from jsonschema import Draft202012Validator
from pydantic import BaseModel, ConfigDict, Field, model_validator

from gzkit.complexity.advisor.diagnosis import DoctrinalFrame, RefactorArchetype

__all__ = [
    "CANONICAL_RULE_TABLE_PATH",
    "CANONICAL_SCHEMA_PATH",
    "ArchetypeRule",
    "AstPredicate",
    "MetricPredicate",
    "load_archetype_rules",
]

_PROJECT_ROOT: Path = Path(__file__).resolve().parents[4]
CANONICAL_RULE_TABLE_PATH: Path = _PROJECT_ROOT / "data" / "advisor_archetype_rules.json"
CANONICAL_SCHEMA_PATH: Path = (
    _PROJECT_ROOT / "src" / "gzkit" / "schemas" / "advisor_archetype_rules.json"
)


class MetricPredicate(BaseModel):
    """Match clause naming the (metric, band) crossings a rule fires on."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    metrics: tuple[str, ...] = Field(min_length=1)
    bands: tuple[Literal["block", "warn", "advise"], ...] = Field(min_length=1)

    def matches(self, metric: str, band: str) -> bool:
        return metric in self.metrics and band in self.bands


class AstPredicate(BaseModel):
    """Match clause naming the AST shape a rule fires on.

    At least one field must be supplied; the engine evaluates every supplied
    field against the target node and returns ``True`` only when every check
    holds (conjunctive, not disjunctive).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    node_kind: str | None = None
    min_param_count: int | None = Field(default=None, ge=1)
    min_branch_count: int | None = Field(default=None, ge=1)
    min_argument_count: int | None = Field(default=None, ge=1)
    min_class_attributes: int | None = Field(default=None, ge=1)
    min_method_calls: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def _at_least_one_clause(self) -> AstPredicate:
        if all(
            value is None
            for value in (
                self.node_kind,
                self.min_param_count,
                self.min_branch_count,
                self.min_argument_count,
                self.min_class_attributes,
                self.min_method_calls,
            )
        ):
            msg = "AstPredicate must declare at least one match clause"
            raise ValueError(msg)
        return self

    def matches(self, node: ast.AST) -> bool:
        if self.node_kind is not None and type(node).__name__ != self.node_kind:
            return False
        if self.min_param_count is not None and _count_params(node) < self.min_param_count:
            return False
        if self.min_branch_count is not None and _count_branches(node) < self.min_branch_count:
            return False
        if self.min_argument_count is not None and _count_arguments(node) < self.min_argument_count:
            return False
        if (
            self.min_class_attributes is not None
            and _count_class_attributes(node) < self.min_class_attributes
        ):
            return False
        return not (
            self.min_method_calls is not None and _count_method_calls(node) < self.min_method_calls
        )


class ArchetypeRule(BaseModel):
    """One row of the refactor-archetype rule table."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    archetype: RefactorArchetype
    metric_predicate: MetricPredicate
    ast_predicate: AstPredicate
    doctrinal_frame: DoctrinalFrame


def load_archetype_rules(path: Path | None = None) -> tuple[ArchetypeRule, ...]:
    """Load and validate the rule table at ``path`` (default: canonical path).

    Validates against the JSON Schema mirror first (collecting every error in
    one pass; no silent truncation), then constructs frozen Pydantic
    ``ArchetypeRule`` instances. Raises :class:`ValueError` on schema failure;
    raises :class:`pydantic.ValidationError` on Pydantic-level failure.
    """

    target = path if path is not None else CANONICAL_RULE_TABLE_PATH
    schema_text = CANONICAL_SCHEMA_PATH.read_text(encoding="utf-8")
    schema = json.loads(schema_text)
    validator = Draft202012Validator(schema)
    rule_text = target.read_text(encoding="utf-8")
    payload = json.loads(rule_text)
    errors = sorted(validator.iter_errors(payload), key=lambda err: list(err.path))
    if errors:
        formatted = "; ".join(_format_schema_error(err) for err in errors)
        msg = f"advisor_archetype_rules.json failed JSON Schema validation: {formatted}"
        raise ValueError(msg)
    return tuple(ArchetypeRule.model_validate(rule) for rule in payload)


def _format_schema_error(error: object) -> str:
    path = getattr(error, "path", None)
    message = getattr(error, "message", str(error))
    if path:
        path_str = "/".join(str(part) for part in path)
        return f"{path_str}: {message}"
    return str(message)


def _count_params(node: ast.AST) -> int:
    if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
        return 0
    args = node.args
    return (
        len(args.posonlyargs)
        + len(args.args)
        + len(args.kwonlyargs)
        + (1 if args.vararg is not None else 0)
        + (1 if args.kwarg is not None else 0)
    )


def _count_branches(node: ast.AST) -> int:
    return sum(
        1
        for descendant in ast.walk(node)
        if isinstance(descendant, ast.If | ast.For | ast.While | ast.Match)
        and descendant is not node
    )


def _count_arguments(node: ast.AST) -> int:
    if not isinstance(node, ast.Call):
        return 0
    return len(node.args) + len(node.keywords)


def _count_class_attributes(node: ast.AST) -> int:
    if not isinstance(node, ast.ClassDef):
        return 0
    return sum(1 for stmt in node.body if isinstance(stmt, ast.Assign | ast.AnnAssign))


def _count_method_calls(node: ast.AST) -> int:
    return sum(
        1
        for descendant in ast.walk(node)
        if isinstance(descendant, ast.Call) and descendant is not node
    )
