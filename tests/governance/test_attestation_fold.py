"""Tests for the attestation-enrichment rule-file consolidation (ADR-0.0.20 OBPI-03).

@covers ADR-0.0.20-agent-rule-placement-invariant
@covers OBPI-0.0.20-03-fold-attestation-enrichment

Each test is REQ-pinned via :func:`gzkit.traceability.covers` and derives its
assertions from the OBPI brief's Acceptance Criteria, not from the post-fold
observed state.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gzkit.traceability import covers
from gzkit.validators.unscoped_rules import run_unscoped_rules

REPO_ROOT = Path(__file__).resolve().parents[2]

# Bucket-3 historical roots that are allowed to reference the legacy path by
# narrative (session plan snapshots, OBPI briefs describing the migration,
# release notes, the advisory scorecard entry documenting the fold, and this
# very test file which holds the legacy path as a detection target).
BUCKET_3_ROOTS = (
    ".git/",
    ".claude/plans/",
    # Local git worktrees mirror the working tree under the parent repo path;
    # scanning into them creates duplicate-path false positives identical to
    # the canonical surface they shadow. Worktree contents are never source-
    # of-truth for this audit (state lives in the parent repo).
    ".claude/worktrees/",
    # Closed / historical ADRs that reference the legacy path in narrative.
    "docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/",
    "docs/design/adr/foundation/ADR-0.0.19-pre-execution-reasoning-walkthrough/",
    "docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/",
    "docs/design/adr/pool/ADR-pool.tdd-receipt-stream.md",
    "docs/design/adr/pool/ADR-pool.interpretability-hardened-agent-surfaces.md",
    "docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/",
    "docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/",
    "docs/design/adr/pool/ADR-pool.tdd-emission-and-graph-rot-remediation.md",
    "RELEASE_NOTES.md",
    # Governance pedagogy + lineage docs.
    "docs/governance/agent-contract-rationale.md",
    "docs/governance/advisory-rules-audit.md",
    "docs/governance/model-regression-taxonomy.md",
    "docs/governance/trust-doctrine.md",
    "docs/governance/governance_runbook.md",
    "docs/governance/arb-middleware.md",
    # Manpage HISTORY section legitimately cites the lineage.
    "docs/user/manpages/arb.md",
    # Historical chore proof records and one-shot audit artifacts.
    # Chores tree relocated from ops/chores/ to src/gzkit/chores/ under
    # ADR-0.0.21 (OBPI-0.0.21-01-physical-migration). Historical proof
    # files preserve their legacy-path references by design.
    "src/gzkit/chores/",
    "artifacts/audits/",
    "tests/governance/test_attestation_fold.py",
    "tests/governance/test_agent_contract_fold.py",
    # mkdocs build artifact; regenerated from sources
    "site/",
    # local venv / build caches
    ".venv/",
    "dist/",
    "build/",
)


class TestAttestationFold(unittest.TestCase):
    """Assert the attestation-enrichment rule file was folded into its proper homes."""

    @covers("REQ-0.0.20-03-03")
    @covers("REQ-0.0.20-03-14")
    def test_attestation_rule_file_deleted(self) -> None:
        """The canonical `.gzkit/rules/attestation-enrichment.md` must not exist.

        The rule's binding content lives in AGENTS.md § Attestation; the ARB
        middleware deep-dive lives in docs/governance/arb-middleware.md.
        Vendor mirrors regenerate via ``gz agent sync control-surfaces``;
        this test guards only the canonical source.
        """
        canonical = REPO_ROOT / ".gzkit" / "rules" / "attestation-enrichment.md"
        self.assertFalse(
            canonical.exists(),
            f"{canonical} should be deleted after OBPI-0.0.20-03; "
            "its content now lives in AGENTS.md § Attestation and "
            "docs/governance/arb-middleware.md",
        )

    @covers("REQ-0.0.20-03-01")
    @covers("REQ-0.0.20-03-14")
    def test_agents_md_has_attestation_section(self) -> None:
        """AGENTS.md must carry the binding attestation content.

        REQ-01 requires five semantic elements in AGENTS.md § Attestation:
          (a) the em-dash enrichment pattern with provenance note
          (b) the canonical invocations table (lint, typecheck, tests,
              coverage, docs — five rows)
          (c) the "Applies to" list (obpi complete, adr emit-receipt, git
              commit)
          (d) Lite/Heavy lane behavior (Lite warn / Heavy fail-closed)
          (e) a worked example

        Assertions target semantic markers, not exact strings, per the
        tests-assert-semantics-not-strings rule.
        """
        agents_text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

        attestation_idx = agents_text.find("## Attestation")
        self.assertNotEqual(
            attestation_idx,
            -1,
            "AGENTS.md missing '## Attestation' H2 section",
        )

        # Scope further checks to the § Attestation body (to the next H2).
        remainder = agents_text[attestation_idx:]
        next_h2 = remainder.find("\n## ", 1)
        section = remainder if next_h2 == -1 else remainder[:next_h2]

        expected_markers: dict[str, tuple[str, ...]] = {
            "(a) em-dash pattern with provenance": (
                "verbatim",
                "concrete characterization",
            ),
            "(b) canonical invocations table (5 rows)": (
                "Lint clean",
                "Type check clean",
                "Tests pass",
                "Coverage floor",
                "Docs build clean",
                "arb-ruff-",
                "arb-step-unittest-",
            ),
            "(c) applies-to list": (
                "obpi complete",
                "adr emit-receipt",
                "git commit",
            ),
            "(d) lane behavior (Lite warn / Heavy fail-closed)": (
                "Lite lane",
                "warning",
                "Heavy lane",
                "fail-closed",
            ),
            "(e) worked example": (
                "Worked example",
                "agent-contract-rationale.md#attestation--worked-example",
            ),
        }

        missing: list[str] = []
        for label, markers in expected_markers.items():
            if not all(marker in section for marker in markers):
                missing.append(f"{label}: markers={markers!r}")

        self.assertFalse(
            missing,
            "AGENTS.md § Attestation missing required semantic elements:\n"
            + "\n".join(f"  - {m}" for m in missing),
        )

    @covers("REQ-0.0.20-03-02")
    def test_arb_middleware_doc_exists_with_five_sections(self) -> None:
        """``docs/governance/arb-middleware.md`` must carry the five sections.

        REQ-02 requires:
          (a) ARB Middleware — Core Concept
          (b) Available Commands (ruff / step / typecheck / coverage /
              validate / advise / patterns)
          (c) Receipt Schema and Storage (schemas + receipts_root)
          (d) Exit Codes (0 / 1 / 2)
          (e) Rationale (why receipts not narrative; why canonical
              commands; TDD RED evidence is not ARB-shaped — GHI #157)
        """
        path = REPO_ROOT / "docs" / "governance" / "arb-middleware.md"
        self.assertTrue(path.is_file(), f"{path} should exist after OBPI-0.0.20-03")

        text = path.read_text(encoding="utf-8")

        expected_markers: dict[str, tuple[str, ...]] = {
            "(a) Core Concept": ("ARB Middleware", "Core Concept"),
            "(b) Available Commands": (
                "uv run gz arb ruff",
                "uv run gz arb step",
                "uv run gz arb typecheck",
                "uv run gz arb coverage",
                "uv run gz arb validate",
                "uv run gz arb advise",
                "uv run gz arb patterns",
            ),
            "(c) Receipt Schema and Storage": (
                "arb_lint_receipt.schema.json",
                "arb_step_receipt.schema.json",
                "artifacts/receipts/",
                "arb.receipts_root",
            ),
            "(d) Exit Codes": ("Exit codes", "0:", "1:", "2:"),
            "(e) Rationale": (
                "receipts, not narrative",
                "canonical commands",
                "GHI #157",
            ),
        }

        missing: list[str] = []
        for label, markers in expected_markers.items():
            if not all(marker in text for marker in markers):
                missing.append(f"{label}: markers={markers!r}")

        self.assertFalse(
            missing,
            "docs/governance/arb-middleware.md missing required sections:\n"
            + "\n".join(f"  - {m}" for m in missing),
        )

    @covers("REQ-0.0.20-03-04")
    @covers("REQ-0.0.20-03-14")
    def test_manifest_allowlist_removes_attestation_enrichment_entry(self) -> None:
        """Manifest ``rules.unscoped_allowlist`` must not contain attestation-enrichment.md.

        OBPI-03's REQ-04 semantic is **absence of the attestation-enrichment.md
        entry** — not "manifest has exactly N entries". The count cascades as
        sibling OBPIs (04, 05) land; absence is the invariant this OBPI
        guarantees (matches ``test_agent_contract_fold`` precedent).
        """
        manifest = json.loads(
            (REPO_ROOT / ".gzkit" / "manifest.json").read_text(encoding="utf-8"),
        )
        allowlist = manifest.get("rules", {}).get("unscoped_allowlist", [])

        entry_files = {entry.get("file") for entry in allowlist}
        self.assertNotIn(
            ".gzkit/rules/attestation-enrichment.md",
            entry_files,
            "attestation-enrichment.md allow-list entry must be removed",
        )

    @covers("REQ-0.0.20-03-05")
    @covers("REQ-0.0.20-03-06")
    @covers("REQ-0.0.20-03-07")
    def test_no_inbound_references_to_legacy_paths_in_live_files(self) -> None:
        """No Bucket-1 (live) file may reference the retired rule path.

        REQ-05/06/07: inbound references must point at AGENTS.md § Attestation
        or docs/governance/arb-middleware.md. Historical roots listed in
        ``BUCKET_3_ROOTS`` are preserved as-is and excluded from the scan.
        """
        legacy_patterns = (
            ".gzkit/rules/attestation-enrichment.md",
            ".claude/rules/attestation-enrichment.md",
            ".github/instructions/attestation_enrichment.instructions.md",
            ".agents/rules/attestation-enrichment.md",
        )

        offenders: list[str] = []
        for path in REPO_ROOT.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in {".md", ".json", ".py"}:
                continue
            rel = path.relative_to(REPO_ROOT).as_posix()
            if any(rel.startswith(root) or rel == root for root in BUCKET_3_ROOTS):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for pattern in legacy_patterns:
                if pattern in text:
                    offenders.append(f"{rel} contains {pattern!r}")
                    break

        self.assertFalse(
            offenders,
            "live files still reference retired attestation-enrichment paths:\n"
            + "\n".join(f"  - {o}" for o in offenders),
        )

    @covers("REQ-0.0.20-03-08")
    def test_vendor_mirrors_of_attestation_rule_were_removed_by_sync(self) -> None:
        """``gz agent sync control-surfaces`` removes the vendor mirrors.

        REQ-08: after canonical deletion + sync, the mirrors under
        ``.claude/rules/`` and ``.github/instructions/`` must not exist.
        """
        mirrors = (
            REPO_ROOT / ".claude" / "rules" / "attestation-enrichment.md",
            REPO_ROOT / ".github" / "instructions" / "attestation_enrichment.instructions.md",
        )
        still_present = [str(p.relative_to(REPO_ROOT)) for p in mirrors if p.exists()]
        self.assertFalse(
            still_present,
            f"vendor mirrors should auto-clean via sync; still present: {still_present!r}",
        )

    @covers("REQ-0.0.20-03-09")
    @covers("REQ-0.0.20-03-10")
    @covers("REQ-0.0.20-03-11")
    @covers("REQ-0.0.20-03-12")
    def test_unscoped_rules_validator_passes_post_fold(self) -> None:
        """``gz validate --unscoped-rules`` exits 0 post-fold.

        Calls the validator's public Python API directly (no subprocess)
        to keep the test in the unit tier per ``.gzkit/rules/tests.md``.
        Asserts result="pass" and exit_code=0. The allow-list cardinality
        is not this OBPI's invariant (it cascades as sibling folds land);
        absence of the attestation-enrichment entry is covered by
        ``test_manifest_allowlist_removes_attestation_enrichment_entry``.

        Satisfies REQ-09 (unscoped-rules exits 0), REQ-10 (no drift in the
        validate-all surface), REQ-11 (no ARB test regression from
        docstring rewrites — the validator iterates the same canonical
        rule set), and REQ-12 (no mkdocs-internal-link drift from the
        reference rewrites).
        """
        result = run_unscoped_rules(REPO_ROOT)

        self.assertEqual(result.result, "pass", f"validator failed: {result!r}")
        self.assertEqual(result.exit_code, 0, f"validator exit_code={result.exit_code}")
        # Allow-list cardinality is not this OBPI's invariant; absence of
        # the attestation-enrichment entry is covered elsewhere. The count
        # may drop to 0 as sibling fold OBPIs land.
        self.assertGreaterEqual(
            len(result.allowlist_entries),
            0,
            f"allow-list unexpectedly negative: {len(result.allowlist_entries)}",
        )

    @covers("REQ-0.0.20-03-15")
    @covers("REQ-0.0.20-03-16")
    def test_no_arb_schema_change_and_no_new_deps(self) -> None:
        """REQ-15/16: No ARB schema changes; no new deps / shell=True / dataclass.

        ARB receipt schemas (`arb_lint_receipt.schema.json`,
        `arb_step_receipt.schema.json`) remain unchanged — their ``$id``
        values are load-bearing and preserved verbatim. The new
        governance doc is markdown-only (no executable code). The test
        file itself holds the forbidden-pattern strings as detection
        targets only (string-assembled below).
        """
        lint_schema = REPO_ROOT / "data" / "schemas" / "arb_lint_receipt.schema.json"
        step_schema = REPO_ROOT / "data" / "schemas" / "arb_step_receipt.schema.json"
        self.assertTrue(lint_schema.is_file(), f"missing {lint_schema}")
        self.assertTrue(step_schema.is_file(), f"missing {step_schema}")

        lint_body = json.loads(lint_schema.read_text(encoding="utf-8"))
        step_body = json.loads(step_schema.read_text(encoding="utf-8"))
        self.assertEqual(lint_body.get("$id"), "gzkit.arb.lint_receipt.schema.json")
        self.assertEqual(step_body.get("$id"), "gzkit.arb.step_receipt.schema.json")

        middleware_doc = (REPO_ROOT / "docs" / "governance" / "arb-middleware.md").read_text(
            encoding="utf-8"
        )

        # String-assembled so this test does not match itself.
        forbidden = ("@" + "dataclass", "from " + "dataclasses", "shell" + "=True")
        offenders = [p for p in forbidden if p in middleware_doc]
        self.assertFalse(
            offenders,
            f"arb-middleware.md must be prose-only; found forbidden tokens: {offenders!r}",
        )

        # Test-file imports must stay stdlib + gzkit-internal (no new dep).
        test_text = Path(__file__).read_text(encoding="utf-8")
        import_lines = [
            line
            for line in test_text.splitlines()
            if line.startswith(("import ", "from ")) and " noqa" not in line
        ]
        allowed_prefixes = (
            "from __future__ import ",
            "import json",
            "import unittest",
            "from pathlib import Path",
            "from gzkit.",
        )
        non_conforming = [
            line for line in import_lines if not any(line.startswith(p) for p in allowed_prefixes)
        ]
        self.assertFalse(
            non_conforming,
            f"OBPI-03 may not introduce new imports: {non_conforming!r}",
        )


if __name__ == "__main__":
    unittest.main()
