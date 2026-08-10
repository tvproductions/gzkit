"""BDD steps for gz validate --kind-invariance scenarios (OBPI-0.0.35-04).

@covers REQ-0.0.35-04-02
@covers REQ-0.0.35-04-03
@covers REQ-0.0.35-04-04
@covers REQ-0.0.35-04-05
"""

from __future__ import annotations

import os
from pathlib import Path

from behave import given

_SUBSTANTIVE_BODY = (
    "Without this ADR, the project would not be the project because the kind "
    "taxonomy is the load-bearing decision that distinguishes app-system "
    "identity from named capability. This is a port: every implementation "
    "must honor the foundation/feature contract.\n"
)

_PLACEHOLDER_BODY = (
    '_[Author: Answer the invariance test in one sentence: "Without this ADR, '
    'would the project still be the project?" State yes and name the invariance.]_\n'
    "\n"
    "_[Port-vs-adapter framing: Is this ADR a port (an abstract contract every "
    "implementation must honor) or an adapter (one implementation behind an "
    "existing port)?]_\n"
)


def _write_adr(
    root: Path,
    adr_id: str,
    *,
    kind: str,
    body: str,
    subdir: str = "foundation",
) -> Path:
    adr_dir = root / "docs" / "design" / "adr" / subdir / adr_id
    adr_dir.mkdir(parents=True, exist_ok=True)
    adr_file = adr_dir / f"{adr_id}.md"
    adr_file.write_text(
        f"---\n"
        f"id: {adr_id}\n"
        f"status: Draft\n"
        f"kind: {kind}\n"
        f"lane: lite\n"
        f"---\n\n"
        f"# {adr_id}: Test ADR\n\n"
        f"{body}",
        encoding="utf-8",
    )
    return adr_file


@given("a minimal project with a foundation ADR carrying a substantive Why-foundation-tier section")
def step_foundation_adr_substantive(context) -> None:
    """Foundation ADR with the heading and a substantive body."""
    root: Path = context._tmpdir
    body = f"## Why foundation tier?\n\n{_SUBSTANTIVE_BODY}\n## Intent\n\nTest intent.\n"
    _write_adr(root, "ADR-0.0.99-test-substantive", kind="foundation", body=body)
    os.chdir(root)


@given("a minimal project with a foundation ADR missing the Why-foundation-tier section")
def step_foundation_adr_missing_section(context) -> None:
    """Foundation ADR without the heading."""
    root: Path = context._tmpdir
    body = "## Intent\n\nTest intent without the required section.\n"
    _write_adr(root, "ADR-0.0.99-test-missing", kind="foundation", body=body)
    os.chdir(root)


@given(
    "a minimal project with a foundation ADR carrying a placeholder-only "
    "Why-foundation-tier section"
)
def step_foundation_adr_placeholder_body(context) -> None:
    """Foundation ADR with the heading but only unfilled author prompts."""
    root: Path = context._tmpdir
    body = f"## Why foundation tier?\n\n{_PLACEHOLDER_BODY}\n## Intent\n\nTest intent.\n"
    _write_adr(root, "ADR-0.0.99-test-placeholder", kind="foundation", body=body)
    os.chdir(root)


@given("a minimal project with only a feature ADR")
def step_feature_adr_only(context) -> None:
    """Feature-kind ADR -- should not be enumerated by the validator."""
    root: Path = context._tmpdir
    body = "## Intent\n\nFeature ADR has no section requirement.\n"
    _write_adr(
        root,
        "ADR-0.99.0-test-feature",
        kind="feature",
        body=body,
        subdir="pre-release",
    )
    os.chdir(root)
