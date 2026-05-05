"""BDD steps for the complexity-doctrine link-integrity validator.

Covers ``features/complexity_doctrine_links.feature`` (OBPI-0.0.27-07).

@covers REQ-0.0.27-07-01
@covers REQ-0.0.27-07-02
@covers REQ-0.0.27-07-03
@covers REQ-0.0.27-07-04
"""

from __future__ import annotations

from pathlib import Path

from behave import given, then, when

_DISTILLED_DIR = Path("docs/governance/complexity")
_CLUSTER_ADR_DIR = Path("docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine")
_FIXTURE_ADR_NAME = "ADR-0.0.27-exemplar-corpus-doctrine.md"


def _write_distilled_file(workspace: Path, revision: int) -> None:
    """Author a distilled-characteristics document inside the workspace.

    The document carries the canonical frontmatter the validator reads
    (``corpus_revision``) plus a `## Metric: \\`radon_cc\\`` heading whose
    backtick-fenced identifier slugifies to the canonical anchor
    ``radon-cc`` consumed by the citation contract.
    """
    target_dir = workspace / _DISTILLED_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "distilled-characteristics-2026-05-04.md"
    target.write_text(
        f"---\ncorpus_revision: {revision}\n---\n\n"
        "# Distilled characteristics — 2026-05-04\n\n"
        "## Metric: `radon_cc`\n\n"
        "p90 = 7.00 (corpus boundary).\n",
        encoding="utf-8",
    )


def _write_cluster_adr(workspace: Path, citation: str) -> None:
    """Author a fixture cluster-ADR body containing one citation line."""
    target_dir = workspace / _CLUSTER_ADR_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / _FIXTURE_ADR_NAME
    target.write_text(
        "---\nid: ADR-0.0.27\nstatus: Draft\nkind: foundation\n---\n\n"
        "# ADR-0.0.27 — fixture\n\n"
        f"Citation: {citation}\n",
        encoding="utf-8",
    )


def _workspace(_context) -> Path:
    """The workspace root is the current working directory (set by
    ``before_scenario`` in ``features/environment.py``).
    """
    return Path.cwd()


@given("a complexity-doctrine fixture with a well-formed citation")
def step_fixture_well_formed(context):
    workspace = _workspace(context)
    _write_distilled_file(workspace, revision=1)
    _write_cluster_adr(
        workspace,
        "docs/governance/complexity/distilled-characteristics-2026-05-04.md "
        "§ radon-cc (corpus revision 1)",
    )


@given("a complexity-doctrine fixture with a missing distilled file")
def step_fixture_missing_file(context):
    workspace = _workspace(context)
    _write_distilled_file(workspace, revision=1)
    _write_cluster_adr(
        workspace,
        "docs/governance/complexity/distilled-characteristics-1999-01-01.md "
        "§ radon-cc (corpus revision 1)",
    )


@given("a complexity-doctrine fixture with an unresolved anchor")
def step_fixture_unresolved_anchor(context):
    workspace = _workspace(context)
    _write_distilled_file(workspace, revision=1)
    _write_cluster_adr(
        workspace,
        "docs/governance/complexity/distilled-characteristics-2026-05-04.md "
        "§ nonexistent-metric (corpus revision 1)",
    )


@given("a complexity-doctrine fixture with a non-portable corpus revision")
def step_fixture_non_portable(context):
    workspace = _workspace(context)
    # Distilled file is at corpus revision 4; citation cites revision 1.
    # Default supported window is 2 -> revision 1 is non-portable at current=4.
    _write_distilled_file(workspace, revision=4)
    _write_cluster_adr(
        workspace,
        "docs/governance/complexity/distilled-characteristics-2026-05-04.md "
        "§ radon-cc (corpus revision 1)",
    )


@given("a complexity-doctrine fixture with a speculative-skip marker")
def step_fixture_speculative_skip(context):
    """Citation forward-references a planned distillation; the speculative
    marker on the preceding line tells the validator to skip it.
    """
    workspace = _workspace(context)
    _write_distilled_file(workspace, revision=1)
    target_dir = workspace / _CLUSTER_ADR_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / _FIXTURE_ADR_NAME
    target.write_text(
        "---\nid: ADR-0.0.27\nstatus: Draft\nkind: foundation\n---\n\n"
        "# ADR-0.0.27 — fixture\n\n"
        "<!-- gz-validate-skip: complexity-doctrine-links -->\n"
        "Citation: docs/governance/complexity/distilled-characteristics-9999-01-01.md "
        "§ unlanded-metric (corpus revision 1)\n",
        encoding="utf-8",
    )


@when('I check that the file "{path}" contains "{text}"')
def step_check_file_contains(context, path: str, text: str):
    """Assert a file in the project root (not the workspace tmpdir) contains
    a substring. Used by the manpage / command-doc REQ-07 scenario which
    verifies the canonical command doc documents the new flag.
    """
    project_root = Path(context._original_cwd)
    target = project_root / path
    assert target.is_file(), f"Doc surface missing: {target}"
    body = target.read_text(encoding="utf-8")
    assert text in body, f"Expected {text!r} in {path}; not found."
    context._doc_check_passed = True


@then("the file is documented")
def step_file_documented(context):
    assert getattr(context, "_doc_check_passed", False), (
        "Doc-check step did not record a pass; see the When step above."
    )
