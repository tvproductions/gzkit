"""Pydantic frontmatter models for governance and control-surface content types.

Pure domain models live in ``gzkit.core.models``. This module re-exports
all public symbols for backward compatibility.
"""

from gzkit.core.models import (
    SCHEMA_TO_MODEL,
    AdrFrontmatter,
    ConstitutionFrontmatter,
    InstructionFrontmatter,
    ObpiFrontmatter,
    PrdFrontmatter,
    SkillFrontmatter,
    validate_frontmatter_model,
)

__all__ = [
    "SCHEMA_TO_MODEL",
    "AdrFrontmatter",
    "ConstitutionFrontmatter",
    "InstructionFrontmatter",
    "ObpiFrontmatter",
    "PrdFrontmatter",
    "SkillFrontmatter",
    "validate_frontmatter_model",
]
