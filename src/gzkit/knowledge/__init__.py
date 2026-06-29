"""gzkit knowledge package — OKF (Open Knowledge Format) orientation layer.

Domain-named package (NOT ``okf``-named) per ADR-0.30.0: OKF-conformance is a
property of the markdown files (reserved ``index.md``/``log.md`` + a ``type``
frontmatter), never a folder/namespace name.

This package houses the typed contracts and (downstream) generator for the
orientation-only OKF documentation-knowledge bundle. Per ADR-0.30.0 Boundary
Invariant 1, nothing here may be consumed as enforcement evidence by any
``gz validate`` / gates / closeout surface — OKF orients, it never proves.
"""

from gzkit.knowledge.concept_frontmatter import ConceptFrontmatter
from gzkit.knowledge.generate import generate_bundle

__all__ = ["ConceptFrontmatter", "generate_bundle"]
