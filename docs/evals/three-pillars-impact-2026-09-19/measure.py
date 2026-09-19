"""Reproduce GHI #1052's bounded advisory measurement; no production writes."""

import hashlib
import json
import sys
import tempfile
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.ontology.source import AstSourceParser, TreeSitterSourceParser, build_source_anchor_index
from gzkit.ontology.unified import project_all

SEEDS = (
    "gzkit/governance/brief_path_validity.py",
    "gzkit/commands/config_paths.py",
    "gzkit/commands/common.py",
    "gzkit/__main__.py",
)


def roster(source):
    """Hash the complete discovered Python input population."""
    return {
        p.relative_to(source).as_posix(): {"sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in sorted(source.rglob("*.py"))
    }


def views(index, seed, population):
    """Return complete direct, grouped and two-hop candidate populations."""
    incoming = {}
    for edge in index.coupling_edges:
        if edge.target_is_unit:
            incoming.setdefault(edge.target, set()).add(edge.source_path)
    direct = incoming.get(seed, set()) - {seed}
    second = set().union(*(incoming.get(p, set()) for p in direct)) if direct else set()
    two_hop = (direct | second) - {seed}
    packages = {}
    for path in sorted(direct):
        packages.setdefault(str(Path(path).parent), []).append(path)
    return {
        "scanned": seed in population,
        "seed_parse_failed": seed in index.parse_failures,
        "direct_files": sorted(direct),
        "direct_packages": packages,
        "two_hop_files": sorted(two_hop),
        "hidden_files": [],
        "direct_edges": [
            e.model_dump(mode="json")
            for e in index.coupling_edges
            if e.target_is_unit and e.target == seed
        ],
    }


def controls(parser):
    """Exercise roster changes and expose unsupported relationship classes."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        package = root / "pkg"
        package.mkdir()
        target = package / "target.py"
        target.write_text("def value(): return 1\n", encoding="utf-8")
        consumer = package / "consumer.py"
        consumer.write_text("from pkg.target import value\n", encoding="utf-8")

        def build():
            return build_source_anchor_index(root, parser=parser, write=False)

        assert views(build(), "pkg/target.py", roster(root))["direct_files"] == ["pkg/consumer.py"]
        consumer.rename(package / "renamed.py")
        assert views(build(), "pkg/target.py", roster(root))["direct_files"] == ["pkg/renamed.py"]
        (package / "renamed.py").unlink()
        assert views(build(), "pkg/target.py", roster(root))["direct_files"] == []
        consumer.write_text("from .target import value\n", encoding="utf-8")
        relative_omission = views(build(), "pkg/target.py", roster(root))["direct_files"] == []
        consumer.write_text("def broken(\n", encoding="utf-8")
        assert "pkg/consumer.py" in build().parse_failures
        assert not views(build(), "outside.py", roster(root))["scanned"]
        (package / "__init__.py").write_text("from pkg.target import value\n", encoding="utf-8")
        consumer.write_text("from pkg import value\n", encoding="utf-8")
        reexport = views(build(), "pkg/target.py", roster(root))
        assert "pkg/consumer.py" in reexport["two_hop_files"]
        assert "pkg/consumer.py" not in reexport["direct_files"]
        return {
            "add_rename_delete": "pass",
            "parse_failure": "pass",
            "outside_root": "pass",
            "relative_import_omitted": relative_omission,
            "reexport_requires_second_hop": True,
        }


def main():
    """Capture a stable source measurement and compare artifact reachability."""
    root = Path.cwd()
    source = root / GzkitConfig.load(root / ".gzkit.json").paths.source_root
    before = roster(source)
    oracle_path = Path(__file__).with_name("oracle.json")
    oracle = json.loads(oracle_path.read_text(encoding="utf-8"))
    result = {
        "baseline": "08655b31b854e2f016b53bd638e3423e71936c13",
        "measured_at": datetime.now(UTC).isoformat(),
        "python": sys.version,
        "parser_packages": {name: version(name) for name in ("tree-sitter", "tree-sitter-python")},
        "oracle_sha256": hashlib.sha256(oracle_path.read_bytes()).hexdigest(),
        "config_sha256": hashlib.sha256((root / ".gzkit.json").read_bytes()).hexdigest(),
        "source_root": source.relative_to(root).as_posix(),
        "source_roster": before,
        "seeds": list(SEEDS),
        "parsers": {},
    }
    for parser in (AstSourceParser(), TreeSitterSourceParser()):
        index = build_source_anchor_index(source, parser=parser, write=False)
        result["parsers"][type(parser).__name__] = {
            "edge_count": len(index.coupling_edges),
            "parse_failures": list(index.parse_failures),
            "views": {seed: views(index, seed, before) for seed in SEEDS},
            "controls": controls(parser),
        }
    projection = project_all(source_root=source)
    graph = projection.graph
    result["artifact_projection"] = {
        "fidelity": projection.fidelity.model_dump(mode="json"),
        "seeds": {
            seed: {
                "materialized": seed in graph.node_ids(),
                "reachable": sorted(graph.reachable_from(seed)),
            }
            for seed in SEEDS
        },
    }
    assert before == roster(source), "Source changed during measurement; discard result"
    result["source_stable"] = True
    Path(sys.argv[1]).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    comparison = []
    for entry in oracle["seeds"]:
        seed = Path(entry["seed"]).relative_to(source.relative_to(root)).as_posix()
        view = result["parsers"]["TreeSitterSourceParser"]["views"][seed]
        for edge in entry["edges"]:
            path = Path(edge["consumer"])
            consumer = (
                path.relative_to(source.relative_to(root)).as_posix()
                if path.is_relative_to(source.relative_to(root))
                else None
            )
            comparison.append(
                {
                    "seed": entry["seed"],
                    "consumer": edge["consumer"],
                    "kind": edge["kind"],
                    "direct": consumer in view["direct_files"],
                    "two_hop": consumer in view["two_hop_files"],
                    "upstream": edge["kind"].startswith("upstream"),
                }
            )
    Path(sys.argv[1]).with_name("oracle-comparison.json").write_text(
        json.dumps(comparison, indent=2) + "\n", encoding="utf-8"
    )
    for name, data in result["parsers"].items():
        for seed, view in data["views"].items():
            print(
                name,
                seed,
                len(view["direct_files"]),
                len(view["direct_packages"]),
                len(view["two_hop_files"]),
                "hidden=0",
            )


if __name__ == "__main__":
    main()
