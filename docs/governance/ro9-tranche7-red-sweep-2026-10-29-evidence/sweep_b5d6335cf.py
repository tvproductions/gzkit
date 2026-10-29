"""Sweep b5d6335cf's surviving hunks against the current tests (operator ruling "a")."""  # noqa: INP001 — a dated evidence script run by path, never imported as a package

import json
import sys
from pathlib import Path

from gzkit.mutation_witness import Mutation, run_mutation_sweep

ROOT = Path.cwd()
T = "tests.commands.test_init."
UV = T + "TestInitBuildsTheProjectThroughUv."
FAILS = T + "TestUvSkeletonFailsWithRecovery."
REPAIR = T + "TestInitRepairBuildsAndSeeds."
SEED = T + "TestSeedDisciplineBaseline."
NON_SRC = UV + "test_non_src_source_root_moves_the_package_and_tells_uv_build"
RERUN = 'and re-run `gz init`."\n        )\n'

INIT = [
    Mutation(
        label="init_cmd:407-414 no-floor refusal",
        find=RERUN + "        raise GzCliError(msg)\n    return match.group(1)",
        replace=RERUN + '        return "3.14"\n    return match.group(1)',
        expected_tests=[FAILS + "test_missing_python_floor_refuses_to_pin_one"],
    ),
    Mutation(
        label="init_cmd:426-442 uv-missing refusal",
        find="raise GzCliError(msg) from exc\n    if result.returncode",
        replace="return\n    if result.returncode",
        expected_tests=[FAILS + "test_missing_uv_names_the_install_step"],
    ),
    Mutation(
        label="init_cmd:442-450 uv-failure refusal",
        find=(
            'then re-run `gz init`."\n        )\n        raise GzCliError(msg)\n\n\ndef _uv_project'
        ),
        replace='then re-run `gz init`."\n        )\n        return\n\n\ndef _uv_project',
        expected_tests=[FAILS + "test_failing_uv_command_names_the_command_and_stops"],
    ),
    Mutation(
        label="init_cmd:483-489 non-src move",
        find='    if source_root != "src":\n        # uv lays',
        replace="    if False:\n        # uv lays",
        expected_tests=[NON_SRC],
    ),
    Mutation(
        label="init_cmd:487-488 empty src removed",
        find=(
            "        with contextlib.suppress(OSError):\n"
            '            (project_root / "src").rmdir()\n'
        ),
        replace="",
        expected_tests=[NON_SRC],
    ),
    Mutation(
        label="init_cmd:492-495 governance README",
        find="    if not readme_existed:\n",
        replace="    if False:\n",
        expected_tests=[UV + "test_readme_points_at_the_agent_contract"],
    ),
    Mutation(
        label="init_cmd:500 CI workflow",
        find="    if not workflow.exists():\n",
        replace="    if False:\n",
        expected_tests=[UV + "test_ci_workflow_runs_uv_with_the_lock_checked"],
    ),
    Mutation(
        label="init_cmd:827-830 seed dry-run",
        find='    if dry_run:\n        return f"Would seed',
        replace='    if False:\n        return f"Would seed',
        expected_tests=[REPAIR + "test_repair_dry_run_plans_the_seed_without_writing_it"],
    ),
    Mutation(
        label="init_cmd:1156-1162 repair seeds",
        find=(
            "            _scaffold_gitignore(project_root, dry_run=dry_run),\n"
            "            _seed_astral_baseline(project_root, dry_run=dry_run),\n"
        ),
        replace="            _scaffold_gitignore(project_root, dry_run=dry_run),\n",
        expected_tests=[REPAIR + "test_repair_seeds_a_missing_baseline"],
    ),
    Mutation(
        label="init_cmd:1345 repair takes project type",
        find=(
            "            attestor_handle=attestor_handle,\n"
            "            project_type=project_type,\n"
            "        )\n        return\n"
        ),
        replace="            attestor_handle=attestor_handle,\n        )\n        return\n",
        expected_tests=[REPAIR + "test_repair_builds_the_requested_project_type"],
    ),
]
PARSER = [
    Mutation(
        label="parser_governance:175 project type passed",
        find="            project_type=a.project_type,\n",
        replace="",
        expected_tests=[UV + "test_each_project_type_builds_its_uv_shape"],
    ),
    Mutation(
        label="parser_governance:123 help example (accepted: help text)",
        find='                "gz init --project-type package",\n',
        replace="",
        expected_tests=[UV + "test_each_project_type_builds_its_uv_shape"],
    ),
]
ASTRAL = [
    Mutation(
        label="astral_discipline:642-643 existing baseline kept",
        find="    if path.exists():\n        return None\n    counts",
        replace="    counts",
        expected_tests=[SEED + "test_existing_baseline_is_left_untouched"],
    ),
    Mutation(
        label="astral_discipline:652 row count returned",
        find="    return len(rows)\n\n\ndef audit_astral_discipline",
        replace="    return None\n\n\ndef audit_astral_discipline",
        expected_tests=[SEED + "test_returns_the_number_of_rows_it_wrote"],
    ),
    Mutation(
        label="astral_discipline:64 __all__ entry (accepted: export list)",
        find='    "seed_discipline_baseline",\n]',
        replace="]",
        expected_tests=[SEED + "test_returns_the_number_of_rows_it_wrote"],
    ),
]
COMMAND = [sys.executable, "-m", "unittest", "-v", "tests.commands.test_init"]

report = []
for source, mutations in (
    ("src/gzkit/commands/init_cmd.py", INIT),
    ("src/gzkit/cli/parser_governance.py", PARSER),
    ("src/gzkit/governance/trust_audits/astral_discipline.py", ASTRAL),
):
    sweep = run_mutation_sweep(ROOT, ROOT / source, mutations, COMMAND)
    sys.stdout.write(
        f"== {source}: baseline_green={sweep.baseline_green} conclusive={sweep.is_conclusive}\n"
    )
    for witness in sweep.witnesses:
        sys.stdout.write(f"  {witness.outcome:<12} {witness.label}  {witness.reason}\n")
    report.append(sweep.model_dump(mode="json"))
Path(sys.argv[1]).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
