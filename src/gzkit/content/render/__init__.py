"""Public render entrypoint — ADR-0.0.34 § Decision item #2."""

from .pipeline import TemplateNotFound, render

__all__ = ["TemplateNotFound", "render"]
