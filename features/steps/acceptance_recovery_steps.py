"""Process-level controls for GHI 985; all mutations stay inside disposable projects."""

import io
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from behave import given, then, when
from rich.console import Console
from tests.test_acceptance_execution import REQ, SELECTOR, TEST, ExecutionFixture
from tests.test_acceptance_store import OBPI, captured_receipt

from gzkit.acceptance_execution import prove
from gzkit.acceptance_store import (
    acceptance_ledger,
    acceptance_status,
    initialize,
    load_history,
    record_proof,
    record_review,
)
from gzkit.commands.obpi_acceptance import _execute_proof
from gzkit.commands.obpi_stages import _run_pipeline_ceremony_stage
from gzkit.mutation_witness import Mutation


@given("a disposable acceptance project")
def acceptance_project(context):
    fixture = ExecutionFixture()
    fixture.setUp()
    context.add_cleanup(fixture.doCleanups)
    fixture.write(".gzkit.json", json.dumps({"paths": {"design_root": "design"}}))
    fixture.brief = fixture.brief.rename(fixture.brief.with_name(f"{OBPI}.md"))
    initialize(fixture.root, OBPI, "implementer-session")
    context.acceptance_fixture = fixture


def _approve(fixture, proof):
    for stage in ("spec", "quality", "adversarial"):
        record_review(fixture.root, OBPI, captured_receipt(proof, stage))


@when("a required finding is repaired and independently closed")
def repaired_finding(context):
    fixture = context.acceptance_fixture
    old = fixture.run_proof()
    assert old.valid, old.evidence
    record_proof(fixture.root, OBPI, old)
    finding = {
        "id": "required-boundary",
        "obligation_id": REQ,
        "kind": "missing-proof",
        "description": "Negative inputs require an independent literal expectation.",
    }
    record_review(fixture.root, OBPI, captured_receipt(old, findings=[finding], verdict="refuted"))
    fixture.write(
        "tests/test_engine.py",
        TEST.replace(
            "self.assertEqual(double(2), 4)",
            "self.assertEqual(double(2), 4)\n        self.assertEqual(double(-2), -4)",
        ),
    )
    proof = fixture.run_proof()
    assert proof.valid, proof.evidence
    record_proof(fixture.root, OBPI, proof)
    _approve(fixture, proof)
    assert not acceptance_status(fixture.root, OBPI).ready
    closure = {"finding_id": finding["id"], "obligation_id": REQ, "proof_id": proof.id}
    record_review(fixture.root, OBPI, captured_receipt(proof, closures=[closure]))
    context.accepted_proof = proof


@then("equivalent proof reexecution preserves readiness through reload")
def repeated_proof(context):
    fixture = context.acceptance_fixture
    repeated = fixture.run_proof()
    assert repeated.id != context.accepted_proof.id
    assert repeated.claim_digest == context.accepted_proof.claim_digest
    record_proof(fixture.root, OBPI, repeated)
    assert len(load_history(fixture.root, OBPI).proofs) == 3
    status = acceptance_status(fixture.root, OBPI)
    assert status.ready, status.blockers


@then("the real ceremony requests human attestation")
def ceremony_requests_attestation(context):
    fixture = context.acceptance_fixture
    output = io.StringIO()
    with patch("gzkit.commands.obpi_stages.console", Console(file=output)):
        _run_pipeline_ceremony_stage(
            project_root=fixture.root,
            plans_dir=fixture.root / ".claude/plans",
            obpi_id=OBPI,
            obpi_content=fixture.brief.read_text(),
            resolved_parent="ADR-0.1.0-engine",
            requires_human_attestation=True,
            attestor=None,
            evidence_json=None,
        )
    assert "Human attestation required." in output.getvalue(), output.getvalue()
    assert {event.event for event in acceptance_ledger(fixture.root).read_all()} == {
        "acceptance_recorded"
    }


@then("both CLI entrypoints report ready with successful process exits")
def ready_process_exits(context):
    fixture = context.acceptance_fixture
    entrypoints = ([sys.executable, "-m", "gzkit"], [str(Path(sys.executable).with_name("gz"))])
    for entrypoint in entrypoints:
        for stage in ("stage2", "stage4"):
            result = subprocess.run(
                [*entrypoint, "obpi", "acceptance", OBPI, "status", "--stage", stage, "--json"],
                cwd=fixture.root,
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
            )
            assert result.returncode == 0, result.stdout + result.stderr
            assert json.loads(result.stdout)["ready"], result.stdout


@when("a shared oracle and an independent oracle face the same production defect")
def shared_oracle(context):
    fixture = context.acceptance_fixture
    fixture.write(
        "src/engine.py",
        "def expected(value):\n    return value * 2\n\n"
        "def double(value):\n    return expected(value)\n",
    )
    fixture.write(
        "tests/test_engine.py",
        TEST.replace("import double", "import double, expected").replace(
            "double(2), 4", "double(2), expected(2)"
        ),
    )
    context.shared_proof = fixture.run_proof()
    fixture.write("tests/test_engine.py", TEST)
    context.independent_proof = fixture.run_proof()


@then("only the independently derived expectation supplies proof")
def independent_oracle(context):
    shared = json.loads(context.shared_proof.evidence)["sweep"]["witnesses"][0]
    independent = json.loads(context.independent_proof.evidence)["sweep"]["witnesses"][0]
    assert shared["outcome"] == "survived" and not context.shared_proof.valid
    assert independent["outcome"] == "killed" and context.independent_proof.valid
    assert independent["failing_tests"] == [SELECTOR]


@when("proof execution times out after activation with {newline} source bytes")
def interrupted_proof(context, newline):
    import gzkit.mutation_witness as witness

    fixture = context.acceptance_fixture
    source = fixture.root / "src/engine.py"
    original = b"def double(value):\n    return value * 2\n"
    if newline == "CRLF":
        original = original.replace(b"\n", b"\r\n")
    source.write_bytes(original)
    specification = fixture.write(
        "controls.json",
        json.dumps(
            {
                "req_id": REQ,
                "source": "src/engine.py",
                "selectors": [SELECTOR],
                "mutations": [
                    {
                        "find": "return value * 2",
                        "replace": "return value * 3",
                        "label": "wrong multiplier",
                        "expected_tests": [SELECTOR],
                    }
                ],
            }
        ),
    )
    original_run = witness._run

    def interrupted(*args, **kwargs):
        if source.read_bytes() != original:
            assert source.read_bytes() == original.replace(b"value * 2", b"value * 3")
            context.activation_observed = True
            raise subprocess.TimeoutExpired("synthetic post-activation timeout", 600)
        return original_run(*args, **kwargs)

    context.activation_observed = False
    with patch.object(witness, "_run", side_effect=interrupted):
        try:
            _execute_proof(fixture.root, OBPI, str(specification))
        except subprocess.TimeoutExpired:
            pass
        else:
            raise AssertionError("Injected active-mutation interruption was not propagated")
    context.original_bytes = original
    context.proof_specification = specification


@then("no proof is recorded and the original source is restored exactly")
def restored_without_credit(context):
    fixture = context.acceptance_fixture
    assert context.activation_observed
    assert (fixture.root / "src/engine.py").read_bytes() == context.original_bytes
    assert load_history(fixture.root, OBPI).proofs == []


@then("a subsequent clean execution records valid proof")
def recovered_execution(context):
    fixture = context.acceptance_fixture
    _, successful = _execute_proof(fixture.root, OBPI, str(context.proof_specification))
    assert successful
    assert len(load_history(fixture.root, OBPI).proofs) == 1
    assert load_history(fixture.root, OBPI).proofs[0].valid


def _control(fixture, find, replace):
    return prove(
        fixture.root,
        fixture.brief,
        REQ,
        source=Path("src/engine.py"),
        selectors=[SELECTOR],
        mutations=[
            Mutation(find=find, replace=replace, label="bounded control", expected_tests=[SELECTOR])
        ],
    )


@when("the production control breaks module import")
def module_import_failure(context):
    context.invalid_proof = _control(
        context.acceptance_fixture,
        "def double(value):",
        "import definitely_missing_acceptance_dependency\ndef double(value):",
    )


@then("that execution supplies no valid behavioral proof")
def invalid_behavior(context):
    proof = context.invalid_proof
    assert not proof.valid
    witness = json.loads(proof.evidence)["sweep"]["witnesses"][0]
    assert witness["outcome"] in ("invalid", "inconclusive")


@when("an earlier diagnostic assertion masks the contract assertion")
def diagnostic_masking(context):
    fixture = context.acceptance_fixture
    source = 'LABEL = "ok"\ndef double(value):\n    return value * 2\n'
    broken = 'LABEL = "wrong"\ndef double(value):\n    return value * 3\n'
    fixture.write("src/engine.py", source)
    test = TEST.replace("import double", "import double, LABEL").replace(
        "self.assertEqual(double(2), 4)",
        'self.assertEqual(LABEL, "ok", "diagnostic-only")\n        '
        'self.assertEqual(double(2), 4, "contract-required")',
    )
    fixture.write("tests/test_engine.py", test)
    context.masked = _control(fixture, source, broken)
    fixture.write(
        "tests/test_engine.py",
        test.replace('self.assertEqual(LABEL, "ok", "diagnostic-only")\n        ', ""),
    )
    context.unmasked = _control(fixture, source, broken)


@then("the failure trace distinguishes diagnostic masking from required sensitivity")
def failure_causality(context):
    masked = json.loads(context.masked.evidence)["sweep"]["witnesses"][0]
    unmasked = json.loads(context.unmasked.evidence)["sweep"]["witnesses"][0]
    assert masked["outcome"] == unmasked["outcome"] == "killed"
    assert "diagnostic-only" in masked["output_tail"]
    assert "contract-required" not in masked["output_tail"]
    assert "contract-required" in unmasked["output_tail"]
    # Classification observes assertion identity, not arbitrary semantic adequacy.
    # The masked observation must be rejected by independent semantic review.
