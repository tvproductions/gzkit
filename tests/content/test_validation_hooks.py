"""TDD Red-phase tests for OBPI-0.0.34-06 validation hooks.

These tests are intentionally written BEFORE the implementation exists.
They should all fail (error or assertion failure) until:
  - src/gzkit/content/validation/hooks.py is created
  - render() in pipeline.py accepts project_root parameter and calls validate_render
  - content_edit_cmd() in edit.py calls validate_save before atomic write

Covers:
  REQ-0.0.34-06-01 — render() invokes validators; failure raises and aborts
  REQ-0.0.34-06-02 — gz content edit save-path invokes validators before persisting
  REQ-0.0.34-06-03 — Failed validation → non-zero exit, diagnostic names validator id+explanation
  REQ-0.0.34-06-04 — No warn-and-continue path; no logger.warning/warn on fidelity
  REQ-0.0.34-06-05 — Both pipeline.py and edit.py reference the hook module
"""

from __future__ import annotations

import logging
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.content.models import AgentContract
from gzkit.core.validation_rules import ValidationError
from gzkit.traceability import covers


def _make_agent_contract() -> AgentContract:
    """Return a minimal valid AgentContract fixture."""
    return AgentContract(name="Test Agent", purpose="Testing purposes")


def _make_validation_error(
    validator_id: str = "test-validator", artifact: str = "AGENTS.md"
) -> ValidationError:
    """Return a ValidationError fixture with the given validator_id embedded in type."""
    return ValidationError(
        type=validator_id,
        artifact=artifact,
        message=f"Fidelity violation detected by {validator_id}",
    )


class TestFidelityHookError(unittest.TestCase):
    """FidelityHookError carries validator_id and violation attributes."""

    def test_error_carries_validator_id_and_violation(self) -> None:
        """FidelityHookError must expose validator_id and violation attributes."""
        from gzkit.content.validation.hooks import FidelityHookError  # noqa: PLC0415

        exc = FidelityHookError(
            validator_id="surface-weight",
            violation="AGENTS.md exceeds byte budget",
        )
        self.assertEqual(exc.validator_id, "surface-weight")
        self.assertEqual(exc.violation, "AGENTS.md exceeds byte budget")

    def test_error_message_includes_validator_id_and_violation(self) -> None:
        """FidelityHookError.__str__ includes both validator_id and violation text."""
        from gzkit.content.validation.hooks import FidelityHookError  # noqa: PLC0415

        exc = FidelityHookError(
            validator_id="pointer-integrity",
            violation="Dangling reference in rule.md",
        )
        msg = str(exc)
        self.assertIn("pointer-integrity", msg)
        self.assertIn("Dangling reference in rule.md", msg)


class TestValidateRender(unittest.TestCase):
    """validate_render() raises FidelityHookError on violations; passes silently when clean."""

    @covers("REQ-0.0.34-06-01")
    def test_clean_passes_with_no_validators_errors(self) -> None:
        """validate_render() returns None when validators return no errors."""
        from gzkit.content.validation.hooks import validate_render

        project_root = Path(tempfile.gettempdir())

        with patch(
            "gzkit.governance.trust_audits.validate_surface_fidelity",
            return_value=[],
        ):
            # Must not raise
            result = validate_render(project_root=project_root)
            self.assertIsNone(result)

    @covers("REQ-0.0.34-06-01")
    def test_fidelity_violation_raises_hook_error(self) -> None:
        """validate_render() raises FidelityHookError on validator failures."""
        from gzkit.content.validation.hooks import (
            FidelityHookError,
            validate_render,
        )

        project_root = Path(tempfile.gettempdir())
        error = _make_validation_error(validator_id="bullet-retention")

        with (
            patch(
                "gzkit.governance.trust_audits.validate_surface_fidelity",
                return_value=[error],
            ),
            self.assertRaises(FidelityHookError),
        ):
            validate_render(project_root=project_root)

    @covers("REQ-0.0.34-06-03")
    def test_violation_error_names_validator_id(self) -> None:
        """FidelityHookError raised by validate_render carries the validator_id."""
        from gzkit.content.validation.hooks import (
            FidelityHookError,
            validate_render,
        )

        project_root = Path(tempfile.gettempdir())
        error = _make_validation_error(validator_id="scenario-reachability")

        with (
            patch(
                "gzkit.governance.trust_audits.validate_surface_fidelity",
                return_value=[error],
            ),
            self.assertRaises(FidelityHookError) as ctx,
        ):
            validate_render(project_root=project_root)

        exc = ctx.exception
        self.assertEqual(exc.validator_id, "scenario-reachability")
        self.assertEqual(exc.violation, error.message)

    @covers("REQ-0.0.34-06-04")
    def test_no_warning_on_failure(self) -> None:
        """validate_render() must NOT emit logger.warning / logger.warn on fidelity failure."""
        from gzkit.content.validation.hooks import (  # noqa: PLC0415
            FidelityHookError,
            validate_render,
        )

        project_root = Path(tempfile.gettempdir())
        error = _make_validation_error(validator_id="surface-weight")

        with self.assertLogs(level=logging.WARNING) as log_ctx:
            # Inject a dummy warning so assertLogs doesn't fail with "no logs" —
            # we need to detect that the hook itself never adds a WARNING.
            logging.getLogger("test_sentinel").warning("sentinel-only")
            with (
                patch(
                    "gzkit.governance.trust_audits.validate_surface_fidelity",
                    return_value=[error],
                ),
                self.assertRaises(FidelityHookError),
            ):
                validate_render(project_root=project_root)

        # The only warning must be the sentinel — hooks module must not emit WARNING.
        hook_warnings = [
            r for r in log_ctx.output if "hooks" in r.lower() or "fidelity" in r.lower()
        ]
        self.assertEqual(
            hook_warnings,
            [],
            msg=f"validate_render must not emit warnings; got: {hook_warnings}",
        )


class TestValidateSave(unittest.TestCase):
    """validate_save() raises FidelityHookError on violations; passes silently when clean."""

    @covers("REQ-0.0.34-06-02")
    def test_clean_passes_with_no_validator_errors(self) -> None:
        """validate_save() returns None when validate_surface_fidelity returns []."""
        from gzkit.content.validation.hooks import validate_save  # noqa: PLC0415

        project_root = Path(tempfile.gettempdir())

        with patch(
            "gzkit.governance.trust_audits.validate_surface_fidelity",
            return_value=[],
        ):
            result = validate_save(project_root=project_root)
            self.assertIsNone(result)

    @covers("REQ-0.0.34-06-02")
    def test_fidelity_violation_raises_hook_error(self) -> None:
        """validate_save() raises FidelityHookError on validator failures."""
        from gzkit.content.validation.hooks import FidelityHookError, validate_save

        project_root = Path(tempfile.gettempdir())
        error = _make_validation_error(validator_id="pointer-integrity")

        with (
            patch(
                "gzkit.governance.trust_audits.validate_surface_fidelity",
                return_value=[error],
            ),
            self.assertRaises(FidelityHookError),
        ):
            validate_save(project_root=project_root)

    @covers("REQ-0.0.34-06-03")
    def test_violation_error_names_validator_id(self) -> None:
        """FidelityHookError raised by validate_save carries validator_id from the first error."""
        from gzkit.content.validation.hooks import FidelityHookError, validate_save  # noqa: PLC0415

        project_root = Path(tempfile.gettempdir())
        error = _make_validation_error(validator_id="bullet-retention", artifact="CLAUDE.md")

        with (
            patch(
                "gzkit.governance.trust_audits.validate_surface_fidelity",
                return_value=[error],
            ),
            self.assertRaises(FidelityHookError) as ctx,
        ):
            validate_save(project_root=project_root)

        exc = ctx.exception
        self.assertEqual(exc.validator_id, "bullet-retention")
        self.assertEqual(exc.violation, error.message)

    @covers("REQ-0.0.34-06-04")
    def test_no_warning_on_failure(self) -> None:
        """validate_save() must NOT emit logger.warning / logger.warn on fidelity failure."""
        from gzkit.content.validation.hooks import FidelityHookError, validate_save  # noqa: PLC0415

        project_root = Path(tempfile.gettempdir())
        error = _make_validation_error(validator_id="surface-weight")

        with self.assertLogs(level=logging.WARNING) as log_ctx:
            logging.getLogger("test_sentinel").warning("sentinel-only")
            with (
                patch(
                    "gzkit.governance.trust_audits.validate_surface_fidelity",
                    return_value=[error],
                ),
                self.assertRaises(FidelityHookError),
            ):
                validate_save(project_root=project_root)

        hook_warnings = [
            r for r in log_ctx.output if "hooks" in r.lower() or "fidelity" in r.lower()
        ]
        self.assertEqual(
            hook_warnings,
            [],
            msg=f"validate_save must not emit warnings; got: {hook_warnings}",
        )


class TestRenderPipelineWired(unittest.TestCase):
    """render() in pipeline.py calls validate_render when project_root is given."""

    @covers("REQ-0.0.34-06-01")
    @covers("REQ-0.0.34-06-05")
    def test_render_calls_validate_render_when_project_root_given(self) -> None:
        """render(model, vendor, project_root=...) must invoke validate_render exactly once."""
        from gzkit.content.render.pipeline import render  # noqa: PLC0415

        contract = _make_agent_contract()
        project_root = Path(tempfile.gettempdir())

        with patch(
            "gzkit.content.validation.hooks.validate_render",
        ) as mock_validate:
            mock_validate.return_value = None
            render(contract, "root", project_root=project_root)

        mock_validate.assert_called_once()
        call_kwargs = mock_validate.call_args
        # project_root must be forwarded
        self.assertEqual(call_kwargs.kwargs.get("project_root"), project_root)

    @covers("REQ-0.0.34-06-01")
    def test_render_skips_validate_render_when_project_root_is_none(self) -> None:
        """render(model, vendor) with no project_root must NOT call validate_render."""
        from gzkit.content.render.pipeline import render  # noqa: PLC0415

        contract = _make_agent_contract()

        with patch(
            "gzkit.content.validation.hooks.validate_render",
        ) as mock_validate:
            mock_validate.return_value = None
            render(contract, "root")

        mock_validate.assert_not_called()

    @covers("REQ-0.0.34-06-01")
    def test_render_fidelity_violation_propagates_error(self) -> None:
        """render() must propagate FidelityHookError from validate_render — fail-closed."""
        from gzkit.content.render.pipeline import render  # noqa: PLC0415
        from gzkit.content.validation.hooks import FidelityHookError  # noqa: PLC0415

        contract = _make_agent_contract()
        project_root = Path(tempfile.gettempdir())
        hook_error = FidelityHookError(
            validator_id="bullet-retention",
            violation="Retention invariant violated",
        )

        with (
            patch(
                "gzkit.content.validation.hooks.validate_render",
                side_effect=hook_error,
            ),
            self.assertRaises(FidelityHookError),
        ):
            render(contract, "root", project_root=project_root)


class TestEditSaveHookWired(unittest.TestCase):
    """content_edit_cmd() calls validate_save before atomic file write."""

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self._tmp = Path(self._tempdir.name)

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def _canonical_agent_contract_path(self) -> Path:
        """Write a minimal valid AgentContract file for editing."""
        from gzkit.content.render import render  # noqa: PLC0415

        contract = _make_agent_contract()
        p = self._tmp / "agents.md"
        p.write_bytes(render(contract, "root"))
        return p

    def _make_fake_editor(self, file_path: Path) -> object:
        """Return a fake subprocess.run that writes valid AgentContract to the temp file."""
        from gzkit.content.render import render  # noqa: PLC0415

        valid_bytes = render(_make_agent_contract(), "root")

        def fake_editor(args: list[str], **_kwargs: object) -> subprocess.CompletedProcess:
            temp_path = Path(args[-1])
            temp_path.write_bytes(valid_bytes)
            return subprocess.CompletedProcess(args=args, returncode=0)

        return fake_editor

    @covers("REQ-0.0.34-06-02")
    @covers("REQ-0.0.34-06-05")
    def test_save_hook_called_before_write(self) -> None:
        """content_edit_cmd must invoke validate_save before the atomic write."""
        import os  # noqa: PLC0415

        from gzkit.commands.content.edit import content_edit_cmd  # noqa: PLC0415

        file_path = self._canonical_agent_contract_path()
        fake_editor = self._make_fake_editor(file_path)

        call_order: list[str] = []

        def tracking_validate_save(*, project_root: Path) -> None:
            call_order.append("validate_save")

        original_write_bytes = Path.write_bytes

        def tracking_write_bytes(self_path: Path, data: bytes) -> int:
            if self_path.suffix == ".tmp" or self_path == file_path:
                call_order.append("write")
            return original_write_bytes(self_path, data)

        with (
            patch("subprocess.run", side_effect=fake_editor),
            patch(
                "gzkit.content.validation.hooks.validate_save",
                side_effect=tracking_validate_save,
            ),
            patch.object(Path, "write_bytes", tracking_write_bytes),
            patch.dict(os.environ, {"EDITOR": "fake-editor"}),
        ):
            content_edit_cmd(
                file=str(file_path),
                as_type="AgentContract",
                vendor="root",
            )

        validate_pos = call_order.index("validate_save") if "validate_save" in call_order else -1
        write_pos = call_order.index("write") if "write" in call_order else -1

        self.assertGreater(validate_pos, -1, msg="validate_save was never called")
        self.assertGreater(write_pos, -1, msg="write_bytes was never called")
        self.assertLess(
            validate_pos,
            write_pos,
            msg=(
                f"validate_save (pos {validate_pos}) must be called before "
                f"write (pos {write_pos}); order was {call_order}"
            ),
        )

    @covers("REQ-0.0.34-06-02")
    def test_save_hook_blocks_write_on_violation(self) -> None:
        """content_edit_cmd must NOT write to disk when validate_save raises FidelityHookError."""
        import os  # noqa: PLC0415

        from gzkit.commands.content.edit import content_edit_cmd  # noqa: PLC0415
        from gzkit.content.validation.hooks import FidelityHookError  # noqa: PLC0415

        file_path = self._canonical_agent_contract_path()
        original_bytes = file_path.read_bytes()
        fake_editor = self._make_fake_editor(file_path)

        hook_error = FidelityHookError(
            validator_id="surface-weight",
            violation="Surface weight limit exceeded",
        )

        with (
            patch("subprocess.run", side_effect=fake_editor),
            patch(
                "gzkit.content.validation.hooks.validate_save",
                side_effect=hook_error,
            ),
            patch.dict(os.environ, {"EDITOR": "fake-editor"}),
            self.assertRaises(SystemExit) as ctx,
        ):
            content_edit_cmd(
                file=str(file_path),
                as_type="AgentContract",
                vendor="root",
            )

        self.assertNotEqual(ctx.exception.code, 0, msg="Expected non-zero exit on fidelity failure")
        # Original file must be unchanged — the hook blocked the write
        self.assertEqual(
            file_path.read_bytes(),
            original_bytes,
            msg="validate_save violation must prevent any file write",
        )


if __name__ == "__main__":
    unittest.main()
