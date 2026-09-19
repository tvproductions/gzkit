"""Configured source populations, with default/override controls (GHI #1054)."""

import io
import json
import tempfile
import unittest
from contextlib import chdir, redirect_stdout
from pathlib import Path

from gzkit.commands.ontology import ontology_resense_cmd, ontology_sense_cmd
from gzkit.ledger import Ledger
from gzkit.ontology.source import build_source_anchor_index, detect_orphan_gaps
from gzkit.ontology.unified import project_all


class TestOntologySourceRoots(unittest.TestCase):
    def _source(self, root: Path, folder: str, req: str) -> Path:
        source = root / folder
        source.mkdir(parents=True)
        (source / "entry.py").write_text(
            f'from helper import run\n@surface("{req}")\ndef entry():\n    return run()\n',
            encoding="utf-8",
        )
        (source / "helper.py").write_text("def run():\n    return 1\n", encoding="utf-8")
        return source

    def _assert_population(self, root: Path, req: str, override: Path | None = None) -> None:
        index = build_source_anchor_index(override, write=False)
        self.assertEqual([(a.source_path, a.req_id) for a in index.anchors], [("entry.py", req)])
        self.assertTrue(
            any(e.target == "helper.py" and e.target_is_unit for e in index.coupling_edges)
        )
        gaps = detect_orphan_gaps(override, known_reqs={req})
        self.assertEqual((gaps.orphan_reqs, gaps.unknown_anchor_reqs), ((), ()))
        projection = project_all(Ledger(root / ".gzkit/ledger.jsonl"), source_root=override)
        self.assertIn(req, projection.graph.node_ids())
        self.assertTrue(projection.fidelity.source.complete)
        self.assertIn(
            "2 discoverable source unit(s); 1 source->REQ", projection.fidelity.source.detail
        )

    def test_configured_population_from_root_and_nested_directory(self) -> None:
        for decoy in (False, True):
            for nested in (False, True):
                with self.subTest(decoy=decoy, nested=nested), tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    (root / ".gzkit").mkdir()
                    (root / ".gzkit.json").write_text(
                        json.dumps({"paths": {"source_root": "lib"}}), encoding="utf-8"
                    )
                    source = self._source(root, "lib", "REQ-0.32.0-07-01")
                    if decoy:
                        self._source(root, "src", "REQ-0.32.0-07-02")
                    with chdir(source if nested else root):
                        self._assert_population(root, "REQ-0.32.0-07-01")
                        output = io.StringIO()
                        with redirect_stdout(output):
                            ontology_sense_cmd(as_json=True)
                        output = io.StringIO()
                        with redirect_stdout(output):
                            ontology_sense_cmd(as_json=True)
                        payload = json.loads(output.getvalue())
                        self.assertTrue(payload["fidelity"]["source"]["complete"])
                        self.assertIn("1 source->REQ", payload["fidelity"]["source"]["detail"])
                        snapshot = json.loads(
                            (root / ".gzkit/ontology/last_sweep.json").read_text(encoding="utf-8")
                        )
                        self.assertIn("REQ-0.32.0-07-01", snapshot["node_ids"])
                        self.assertNotIn("REQ-0.32.0-07-02", snapshot["node_ids"])
                        self.assertFalse((source / ".gzkit").exists())
                        output = io.StringIO()
                        with redirect_stdout(output):
                            ontology_resense_cmd(as_json=True)
                        self.assertEqual(
                            json.loads(output.getvalue()),
                            {
                                "added_nodes": [],
                                "removed_nodes": [],
                                "added_edges": [],
                                "removed_edges": [],
                            },
                        )

    def test_missing_config_retains_src_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gzkit").mkdir()
            source = self._source(root, "src", "REQ-0.32.0-07-01")
            with chdir(source):
                self._assert_population(root, "REQ-0.32.0-07-01")

    def test_explicit_source_root_overrides_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gzkit").mkdir()
            (root / ".gzkit.json").write_text(
                json.dumps({"paths": {"source_root": "lib"}}), encoding="utf-8"
            )
            self._source(root, "lib", "REQ-0.32.0-07-01")
            override = self._source(root, "other", "REQ-0.32.0-07-02")
            with chdir(root):
                self._assert_population(root, "REQ-0.32.0-07-02", override)
