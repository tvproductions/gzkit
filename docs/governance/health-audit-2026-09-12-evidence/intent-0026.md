# ADR-0.0.26 intent trace — 2026-09-12

Source snapshot: `464dd4ff8fa2ee12d98afe99a867280e1b82b431`. Fixed sample selected after three prior axes. The complete ADR Decision and Checklist were read before this trace's implementation reading. Context and status commands exited 0; context generation is not claimed as a complete read of every bundled line.

## Intent and observed result

1. Decision1: “`gz-adr-evaluate` invocations emit a canonical `adr-evaluation` ledger event”. **Fulfilled for inspected producer/history.** `src/gzkit/commands/adr_promote.py:458–504` appends the canonical event with dimensions, scores, failed challenges and timestamp. Existing live events triggered the actual validation failure; no new evaluation was emitted by this diagnosis. The producer stores the supplied short/full ID, which the consumer compares literally. This observation does not certify semantic evaluation quality.
2. Decision2: “`gz-justify` invocation is required before the parent artifact's lifecycle can advance to `Pending` (or the next gate).” **Correction.** The standalone scope correctly refuses missing evidence, but a zero-byte matching file discharges it and permits Draft→Proposed through the real injected lifecycle object. A filename does not witness the required reasoning. The current CLI rejects ADR anchors in favor of GHI/OBPI/draft instances; the evidence relationship needs reconciliation. Existing six gate tests pass; their positive fixture is not a completed eight-section walkthrough. The narrow checklist says an artifact “exists”, but the parent Decision requires invocation, and current root canon explicitly rejects presence as proof of procedure. Parent intent governs this decomposition loss.
3. Decision3: a chore “runs periodically over recent `adr-evaluation` events and `gz-justify` artifacts” and emits proposals when a pattern recurs “≥3 times across distinct artifacts.” **Correction.** Its Run clustering command executes only fixture tests. The existing public clustering library can process the repository and emit six temporary proposals, but the recurring chore does not invoke that operation on live inputs. Keep library capability distinct from operational wiring. The term “recent” lacks a runtime cutoff; the audit does not invent one.

Decision4/5's complete publication/provenance loop was not exhaustively exercised. No proposal GHI was automatically published by the clustering probe and no rule was promoted. Two independent corrective work orders were filed through ghi-author: [GHI #996](https://github.com/tvproductions/gzkit/issues/996), [GHI #997](https://github.com/tvproductions/gzkit/issues/997). Both carry bounded closure contracts and remain unselected for implementation.

## Lifecycle and evidence attribution

`gz adr status ADR-0.0.26` reports heavy, Validated, 5/5 attested_completed, READY. The unchecked ADR checklist and stale brief body status cannot override those Layer-2 receipts.

An independent attribution defect exists in `OBPI-0.0.26-02-justify-binding-gate.md`: its Human Attestation and Implementation Summary describe OBPI-0.0.24-04 receipt-binding BDD work. Raw ledger line4637, event `obpi_receipt_emitted`, id `OBPI-0.0.26-02-justify-binding-gate`, timestamp `2026-05-03T18:23:01.602500+00:00`, has the same unrelated OBPI-0.0.24-04 text in `evidence.attestation_text` and unrelated feature paths in `value_narrative`/`key_proof`. Thus it is not only frontmatter staleness. The record establishes that an attestation was recorded; the attached enrichment does not establish this binding implementation's proof. Preserve operator words and append-only history; investigate/correct attribution through governed means, never silently rewrite the ledger or revoke the operator's attestation.

`src/gzkit/lifecycle.py:113–123` calls the validator when project_root is injected and source state is Pending/Draft. Its inspected production caller `commands/audit_cmd.py:350` uses Completed→Validated, outside that condition. This is a coverage lead, not an exhaustive assertion about every lifecycle path. GHI996's closure contract requires entry-point coverage to be resolved during repair.

## Exact probe and output

This is a disclosed ad-hoc diagnostic, not a new gate. It copies one real evaluation and threshold file to a temporary project, invokes the real validator and lifecycle object with no ledger sink, and hashes the live ledger before/after. Temporary evidence is removed. No synthetic justification was written into the repository.

```python
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.governance.trust_audits.evaluation_justify_binding import validate_evaluation_justify_binding
from gzkit.lifecycle import LifecycleStateMachine

live = Path('/Users/jeff/Documents/Code/gzkit/.gzkit/ledger.jsonl')
before = hashlib.sha256(live.read_bytes()).hexdigest()
artifact = 'ADR-0.35.0-canon-entry-corpus-landing'
event = [json.loads(line) for line in live.read_text().splitlines() if json.loads(line).get('event') == 'adr-evaluation' and json.loads(line).get('id') == artifact][-1]
with TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / '.gzkit').mkdir()
    (root / '.gzkit/ledger.jsonl').write_text(json.dumps(event) + '\n')
    (root / 'data').mkdir()
    (root / 'data/eval_feedback_thresholds.json').write_bytes(Path('data/eval_feedback_thresholds.json').read_bytes())
    def errors():
        return len(validate_evaluation_justify_binding(artifact, root))
    result = {'evaluation_id': artifact, 'evaluation_ts': event['ts'], 'missing_artifact_errors': errors()}
    sm = LifecycleStateMachine(project_root=root)
    try:
        sm.transition(artifact, 'ADR', 'Draft', 'Proposed')
        result['injected_lifecycle_missing_artifact'] = 'allowed'
    except ValueError:
        result['injected_lifecycle_missing_artifact'] = 'blocked'
    target = root / 'artifacts/justify/adr-0-35-0-canon-entry-corpus-landing-empty.md'
    target.parent.mkdir(parents=True)
    target.touch()
    result['empty_matching_file_bytes'] = target.stat().st_size
    result['empty_matching_file_errors'] = errors()
    result['injected_lifecycle_empty_artifact'] = sm.transition(artifact, 'ADR', 'Draft', 'Proposed')['to_state']
result['live_ledger_unchanged'] = before == hashlib.sha256(live.read_bytes()).hexdigest()
print(json.dumps(result, indent=2))
```

```json
{
  "evaluation_id": "ADR-0.35.0-canon-entry-corpus-landing",
  "evaluation_ts": "2026-08-07T22:56:46.036392+00:00",
  "missing_artifact_errors": 1,
  "injected_lifecycle_missing_artifact": "blocked",
  "empty_matching_file_bytes": 0,
  "empty_matching_file_errors": 0,
  "injected_lifecycle_empty_artifact": "Proposed",
  "live_ledger_unchanged": true
}
```

Existing gate tests: `uv run --no-sync --no-cache python -m unittest tests.governance.test_justify_binding_gate -v` exited0: six tests, 0.005s, OK. These are fixture evidence, not proof that the live records are satisfied.

## Clustering trace evidence

The independent reviewer read the full ADR claim, library, tests and executable callers. Root also opened the actual criterion loop (`commands/chores.py:420–450`), `run_cluster` body (`chores/eval_feedback_cluster_lib.py:319–405`) and proposal consumer (`commands/chores_propose_ghi_cmd.py:50–70`). Both acceptance manifests prescribe unittest plus layout validation. Every clustering invocation in the prescribed tests uses TemporaryDirectory; two tests inspect registration/layout only. The other inspected caller is a BDD step inside its isolated scenario workspace.

```text
$ uv run --no-sync --no-cache -m unittest tests/chores/test_eval_feedback_cluster.py -q
Ran 10 tests in 0.103s
OK

Invocation: run_cluster(Path.cwd(), proofs_dir=<temporary directory>)
Ledger: .gzkit/ledger.jsonl
Justify root: artifacts/justify
Proposals emitted: 6
dim:Architectural Alignment:critical: 14 distinct artifacts
dim:Decision Justification:critical: 10 distinct artifacts
dim:Problem Clarity:critical: 12 distinct artifacts
dim:Feature Checklist:critical: 5 distinct artifacts
jk:not sure: 5 distinct artifacts
jk:uncertain: 5 distinct artifacts
Proposal files in temporary output: 6
```

The public API probe used all canonical defaults except temporary output, via `uv run --no-sync --no-cache python -B`. An empty output directory means these counts do not establish novelty relative to existing repository proposals. Proposal quality was not assessed; all matching historical evaluation events are read, without a recency filter. No live proposal, canon, ledger or OBPI state was changed.
