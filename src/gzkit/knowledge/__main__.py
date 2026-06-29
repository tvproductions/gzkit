"""Tracer-slice entry point: ``python -m gzkit.knowledge``.

Generates the OKF orientation bundle over the fixed governance tracer slice
into ``.gzkit/governance/knowledge/``. The canonical operator CLI is OBPI-04's
``gz knowledge generate`` / ``gz knowledge refresh``; this module-execution
entry is a tracer/demo convenience.

This lives in ``__main__.py`` (run as ``python -m gzkit.knowledge``) rather than
a ``generate.py`` ``if __name__ == "__main__"`` block on purpose: the package
``__init__`` eagerly imports ``generate`` (so ``from gzkit.knowledge import
generate_bundle`` works), which would put the submodule in ``sys.modules`` before
``runpy`` executed it — emitting a spurious ``RuntimeWarning`` on the documented
demo command. The package-as-command form is warning-free by construction.
"""

from __future__ import annotations

from gzkit.knowledge.generate import BUNDLE_OUTPUT, TRACER_SLICE, generate_bundle

generate_bundle(TRACER_SLICE, BUNDLE_OUTPUT)
print(f"Bundle generated at {BUNDLE_OUTPUT.as_posix()}")
