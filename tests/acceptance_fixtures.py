"""Synthetic current-context fixture for prompt delivery tests only."""

import json

ACCEPTANCE_CONTEXT = json.dumps(
    {
        "input_digest": "bytes-a",
        "input_components": {"files": "files-a", "contract": "contract-a"},
        "contract": {
            "author_id": "implementer",
            "obligations": [
                {
                    "id": "REQ-01",
                    "kind": "BEHAVIOR",
                    "statement": "Reject invalid inputs.",
                    "authority": "brief#REQ-01",
                    "contract_digest": "contract-a",
                }
            ],
        },
        "proofs": [
            {
                "id": "proof-a",
                "obligation_id": "REQ-01",
                "contract_digest": "contract-a",
                "input_digest": "bytes-a",
                "selectors": ["tests.fixture.Case.test_reject"],
                "evidence": "synthetic execution fixture",
                "valid": True,
            }
        ],
        "reviews": [],
        "ready": False,
        "blockers": [],
        "open_findings": [],
        "obligation_ids": ["REQ-01"],
    }
)
