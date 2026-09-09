"""Execute acceptance proof against canonical obligations and exact inputs (GHI #985).

The conservative input roster deliberately invalidates proof on any source, test,
fixture, rule or configuration change. Evidence/history prose is not a dependency.
These executions establish observations; independent review still judges whether
an oracle and its negative control express the requirement.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
import uuid
from pathlib import Path

import yaml

from gzkit.acceptance import Obligation, Proof
from gzkit.config import GzkitConfig
from gzkit.frontmatter import read_frontmatter
from gzkit.governance.req_coverage import discover_covers
from gzkit.mutation_witness import Mutation, _test_observations, run_mutation_sweep
from gzkit.req_kind_fence import resolve_fence_proof
from gzkit.req_kind_support import resolve_support_proof
from gzkit.triangle import ReqEntity, extract_reqs_from_brief

# These sections carry workflow history, not the contract being accepted. All
# other sections are conservatively included, including unknown new headings.
_NARRATIVE = (
    "evidence",
    "human attestation",
    "attestation block",
    "completion checklist",
    "tracked defects",
    "review history",
    "historical",
    "step 4",
    "stage 4",
)
_IGNORED_PARTS = {"__pycache__", ".pytest_cache", ".ruff_cache", ".git", ".venv"}
# CI definitions are part of the conservative input audit population, not a
# configured resource being loaded. Keep this declaration local (GHI #938).
_AUDIT_SUBJECT_LITERALS: tuple[str, ...] = (".github/workflows",)
_CONFIG_FILES = (
    ".gzkit.json",
    ".gzkit/manifest.json",
    "pyproject.toml",
    "uv.lock",
    "setup.cfg",
    "setup.py",
    "tox.ini",
    "ruff.toml",
    ".ruff.toml",
    "mypy.ini",
    "Makefile",
    "requirements.txt",
    ".python-version",
)


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def proof_claim_digest(root: Path, payload: dict) -> str:
    """Fingerprint specification and results, excluding only occurrence noise.

    Keep control outcomes, actual assertion output, selectors and invocation.
    Unittest elapsed time and isolated cache paths do not change the claim.
    Versioned fingerprints are produced afresh, never inferred for legacy rows.
    """

    def stable(value: object) -> object:
        if isinstance(value, dict):
            return {key: stable(item) for key, item in value.items() if key != "pycache_prefix"}
        if isinstance(value, list):
            return [stable(item) for item in value]
        if isinstance(value, str):
            return re.sub(r"(Ran \d+ tests? in )\d+(?:\.\d+)?s", r"\1<elapsed>s", value).replace(
                str(root.resolve()), "<project>"
            )
        return value

    return "v1:" + _sha(_json(stable(payload)).encode())


def execution_conditions_digest(keys: tuple[str, ...]) -> str:
    """Hash only explicitly declared environment dependencies, without exposing values."""
    return _sha(_json({key: os.environ.get(key) for key in keys}).encode())


def _inside(root: Path, path: Path) -> Path:
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f"Acceptance input escapes project: {path}")
    return resolved


def _normative_body(content: str) -> str:
    """Retain normative sections while excluding explicit evidence/history sections."""
    lines: list[str] = []
    excluded = False
    fence: str | None = None
    for line in content.splitlines():
        stripped = line.strip()
        marker = re.match(r"^(`{3,}|~{3,})(.*)$", stripped)
        if marker:
            delimiter, suffix = marker.groups()
            if fence is None:
                fence = delimiter
            elif delimiter[0] == fence[0] and len(delimiter) >= len(fence) and not suffix.strip():
                fence = None
        if fence is None and line.startswith("## "):
            title = line[3:].strip().casefold()
            excluded = title in _NARRATIVE
        if not excluded:
            # Completion checkbox state is accounting, not changed intent.
            lines.append(re.sub(r"^(-\s+)\[[xX ]\]", r"\1[ ]", line))
    return "\n".join(lines).strip()


def _frontmatter_parts(content: str) -> tuple[str, str]:
    lines = content.replace("\ufeff", "").splitlines()
    end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    return "\n".join(lines[1:end]), "\n".join(lines[end + 1 :])


def _brief_contract(root: Path, brief_path: Path) -> tuple[dict, list[ReqEntity]]:
    brief = _inside(root, brief_path)
    content = brief.read_text(encoding="utf-8")
    frontmatter = read_frontmatter(content)
    if not frontmatter.is_readable:
        raise ValueError(f"Brief frontmatter is not readable: {brief}")
    raw, body = _frontmatter_parts(content)
    metadata = yaml.safe_load(raw)
    if not isinstance(metadata, dict) or not metadata.get("id") or not metadata.get("parent"):
        raise ValueError("Acceptance requires an identified brief and parent ADR")
    reqs = extract_reqs_from_brief(content, parent_obpi=metadata["id"])
    ids = [str(req.id) for req in reqs]
    roster = metadata.get("reqs")
    if not reqs or len(ids) != len(set(ids)):
        raise ValueError("Acceptance requires unique parsed requirements")
    if not isinstance(roster, list) or len(roster) != len(ids) or set(roster) != set(ids):
        raise ValueError("Brief requirement roster disagrees with parsed acceptance criteria")
    if any(req.taxonomy_kind is None for req in reqs):
        raise ValueError("Every acceptance obligation must declare its proof kind")
    config = GzkitConfig.load(root / ".gzkit.json")
    adr_root = _inside(root, Path(config.paths.adrs))
    candidates = list(adr_root.rglob(f"{metadata['parent']}.md"))
    if len(candidates) != 1:
        raise ValueError("Acceptance requires exactly one canonical parent ADR")
    parent = _inside(root, candidates[0])
    parent_content = parent.read_text(encoding="utf-8")
    if read_frontmatter(parent_content).is_readable:
        parent_content = _frontmatter_parts(parent_content)[1]
    contract = {
        "brief": brief.relative_to(root.resolve()).as_posix(),
        "id": metadata["id"],
        "parent": metadata["parent"],
        "brief_contract": _normative_body(body),
        "metadata": {
            key: metadata[key]
            for key in (
                "lane",
                "kind",
                "sensitivity",
                "allowed_paths",
                "denied_paths",
                "verification",
            )
            if key in metadata
        },
        "parent_path": parent.relative_to(root.resolve()).as_posix(),
        "parent_contract": _normative_body(parent_content),
        "requirements": [
            {"id": str(r.id), "kind": r.taxonomy_kind, "statement": r.description} for r in reqs
        ],
    }
    return contract, reqs


def canonical_obligations(root: Path, brief_path: Path) -> list[Obligation]:
    """Read obligations through the existing REQ parser and validate its complete roster."""
    root = root.resolve()
    contract, reqs = _brief_contract(root, brief_path)
    digest = _sha(_json(contract).encode())
    return [
        Obligation.model_validate(
            {
                "id": str(req.id),
                "kind": req.taxonomy_kind,
                "statement": req.description,
                "authority": f"{contract['brief']}#acceptance-criteria",
                "contract_digest": digest,
            }
        )
        for req in reqs
    ]


def _input_paths(root: Path) -> tuple[set[Path], Path, Path]:
    config = GzkitConfig.load(root / ".gzkit.json")
    source = _inside(root, Path(config.paths.source_root))
    tests = _inside(root, Path(config.paths.tests_root))
    paths = {source, tests}
    for name in (
        "features",
        "data",
        "scripts",
        config.paths.canonical_rules,
        config.paths.canonical_schemas,
        ".github/workflows",
        *_CONFIG_FILES,
    ):
        paths.add(_inside(root, Path(name)))
    return paths, source, tests


def _file_roster(root: Path) -> dict[str, str]:
    """Hash every file in the audited input population, by content.

    Added and deleted files change the roster because absent members are
    recorded as ``missing`` and present ones by content digest -- git is never
    consulted.
    """
    paths, _, _ = _input_paths(root)
    roster: dict[str, str] = {}
    for path in sorted(paths):
        members = sorted(path.rglob("*")) if path.is_dir() else [path]
        roster[path.relative_to(root).as_posix()] = "directory" if path.is_dir() else "missing"
        for member in members:
            if any(part in _IGNORED_PARTS for part in member.relative_to(root).parts):
                continue
            if member.is_symlink():
                raise ValueError(f"Acceptance dependency symlinks are unsupported: {member}")
            if member.is_file():
                _inside(root, member)
                roster[member.relative_to(root).as_posix()] = _sha(member.read_bytes())
    return roster


def digest_components(root: Path, brief_path: Path) -> dict[str, str]:
    """Return the two terms :func:`input_digest` composes, separately digested.

    Callers refusing a stale record use this to name WHICH term moved. The
    previous single opaque digest forced every refusal to say "stale file
    contents", which sent a reader looking for a file change that need not
    exist (GHI #989).
    """
    root = root.resolve()
    contract, _ = _brief_contract(root, brief_path)
    return {
        "files": _sha(_json(_file_roster(root)).encode()),
        "contract": _sha(_json(contract).encode()),
    }


def input_digest(root: Path, brief_path: Path) -> str:
    """Hash the reviewed INPUTS: the audited file population and the contract.

    Ledger/receipts are excluded because proof execution appends to them. SUPPORT
    resolvers must be re-run when readiness is evaluated.

    The executing process's environment is deliberately NOT hashed (GHI #989).
    This digest answers "were these the reviewed inputs", and a reviewer's own
    ``os.environ``, interpreter build, and platform string are provenance of its
    execution, never identity of what it read. Hashing them made an
    independently-executed review structurally unimportable: the mandated tier-1
    cross-vendor adversary, a CI runner, and a second terminal each recompute a
    different digest from a byte-identical tree, so the record they produce is
    refused for a reason unrelated to whether anything changed. Execution
    context stays recorded in each proof's own evidence payload, where it is
    provenance rather than a gate.
    """
    return _sha(_json(digest_components(root, brief_path)).encode())


def _covering_selectors(root: Path, req_id: str, tests: Path) -> set[str]:
    result: set[str] = set()
    for ref in discover_covers(req_id, tests):
        path = _inside(root, Path(ref.file_path))
        module = ".".join(path.relative_to(root).with_suffix("").parts)
        result.add(f"{module}.{ref.qualified_name}")
    return result


def _restored_run(root: Path, command: list[str], selectors: list[str]) -> dict:
    with tempfile.TemporaryDirectory() as cache:
        env = dict(os.environ, PYTHONPYCACHEPREFIX=cache)
        run = subprocess.run(
            command,
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            errors="replace",
            check=False,
            timeout=600,
        )  # noqa: S603
    output = (run.stdout or "") + (run.stderr or "")
    executed, failures, count = _test_observations(output)
    return {
        "exit_status": run.returncode,
        "output": output,
        "executed_tests": sorted(executed),
        "tests_run": count,
        "green": run.returncode == 0
        and count > 0
        and not failures
        and set(selectors).issubset(executed),
    }


def _production_control_source(root: Path, source: Path, production: Path, tests: Path) -> Path:
    """Refuse controls that would mutate tests, canon, or files outside production."""
    source = _inside(root, source)
    if (
        not source.is_file()
        or not source.is_relative_to(production)
        or source.is_relative_to(tests)
        or source.suffix != ".py"
        or any(
            part in {".gzkit", "features", "data", "docs", ".github"}
            for part in source.relative_to(root).parts
        )
    ):
        raise ValueError("Semantic mutations must target a project production source file")
    return source


def _validate_behavior_inputs(
    root: Path, req_id: str, source: Path | None, mutations: list[Mutation], selectors: list[str]
) -> Path:
    """Bind each requested control to a full covering test before executing it."""
    _, production, tests = _input_paths(root)
    if not source or not mutations or not selectors or len(set(selectors)) != len(selectors):
        raise ValueError("BEHAVIOR proof requires source, mutations and unique full test selectors")
    source = _production_control_source(root, source, production, tests)
    covering = _covering_selectors(root, req_id, tests)
    if not set(selectors).issubset(covering):
        raise ValueError("Every full test selector must cover the nominated requirement")
    for mutation in mutations:
        if not mutation.expected_tests or not set(mutation.expected_tests).issubset(selectors):
            raise ValueError("Each mutation must nominate full selected covering test IDs")
    return source


def _behavior_evidence(
    root: Path, req_id: str, source: Path | None, mutations: list[Mutation], selectors: list[str]
) -> tuple[dict, bool]:
    """Execute validated controls, repeat the restored baseline, and retain observations."""
    source = _validate_behavior_inputs(root, req_id, source, mutations, selectors)
    command = ["uv", "run", "-m", "unittest", *selectors, "-v"]
    sweep = run_mutation_sweep(
        source=source, mutations=mutations, command=command, project_root=root
    )
    restored = _restored_run(root, command, selectors)
    valid = (
        sweep.baseline_green
        and sweep.is_conclusive
        and sweep.killed == len(mutations)
        and sweep.source_sha256 == sweep.restored_source_sha256
        and set(selectors).issubset(sweep.baseline_executed_tests)
        and restored["green"]
    )
    return {
        "command": command,
        "source": source.relative_to(root).as_posix(),
        "mutations": [mutation.model_dump(mode="json") for mutation in mutations],
        "sweep": sweep.model_dump(mode="json"),
        "restored": restored,
    }, bool(valid)


def prove(
    root: Path,
    brief_path: Path,
    req_id: str,
    *,
    source: Path | None = None,
    mutations: list[Mutation] | None = None,
    selectors: list[str] | None = None,
    environment_keys: tuple[str, ...] = (),
) -> Proof:
    """Execute the required proof channel, returning observed valid or invalid evidence."""
    root = root.resolve()
    obligations = {item.id: item for item in canonical_obligations(root, brief_path)}
    if req_id not in obligations:
        raise ValueError("Requirement is not a canonical acceptance obligation")
    obligation = obligations[req_id]
    if any(not key.strip() or "=" in key for key in environment_keys):
        raise ValueError("Execution condition keys must be nonempty environment names")
    environment_keys = tuple(sorted(set(environment_keys)))
    conditions = execution_conditions_digest(environment_keys)
    before = input_digest(root, brief_path)
    selectors = selectors or []
    mutations = mutations or []
    payload: dict[str, object]
    if obligation.kind == "BEHAVIOR":
        payload, valid = _behavior_evidence(root, req_id, source, mutations, selectors)
    else:
        if source or mutations or selectors:
            raise ValueError("Non-BEHAVIOR obligations use their canonical proof resolver")
        if obligation.kind == "SUPPORT":
            result = resolve_support_proof(obligation.statement, root, req_id=req_id)
            resolver = "gzkit.req_kind_support.resolve_support_proof"
        else:
            result = resolve_fence_proof(req_id, root, obligation.statement)
            resolver = "gzkit.req_kind_fence.resolve_fence_proof"
        payload = {"resolver": resolver, "result": result}
        valid = result == "pass"
    after = input_digest(root, brief_path)
    valid = (
        valid and before == after and conditions == execution_conditions_digest(environment_keys)
    )
    payload.update(
        {
            "input_before": before,
            "input_after": after,
            "environment_keys": environment_keys,
            "conditions_digest": conditions,
        }
    )
    return Proof(
        id=f"proof-{uuid.uuid4().hex}",
        obligation_id=req_id,
        contract_digest=obligation.contract_digest,
        input_digest=before,
        selectors=tuple(selectors),
        evidence=_json(payload),
        valid=valid and before == after,
        claim_digest=proof_claim_digest(root, payload) if valid and before == after else None,
        environment_keys=environment_keys,
        conditions_digest=conditions,
    )
