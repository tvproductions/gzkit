# Patch Release: v0.34.5

**Date:** 2026-08-23
**Previous Version:** 0.34.4
**Tag:** v0.34.4

## Qualifying GHIs

| # | Title | Status | Warning |
|---|-------|--------|---------|
| 805 | hooks/handoff: generated resume-gate still documents a Bash arm that was removed | qualified |  |
| 828 | release-tags: audit reads local tags only, so an unpushed tag passes every gate | qualified |  |
| 829 | release-audit: point check on one version, so a lost historical tag is unreachable | qualified |  |
| 830 | release-notes: three published releases are documented nowhere in the repo | qualified |  |
| 831 | gz-adr-create: SKILL.md claims plan create books adr_created for pool | qualified |  |
| 833 | tests: only maintenance.lock is quiesced; index.lock can race copytree | excluded |  |
| 834 | release: re-pushing a tag overwrites its curated release body | excluded |  |
| 835 | gz check: ~46 validator steps run serially, each individually cheap | qualified |  |
| 838 | handoff: Settled Rulings is 85% of the document and re-adjudication still happens | qualified |  |
| 839 | arb red: base commit is HEAD, so already-landed work always witnesses failure_class=none | qualified |  |
| 840 | rendition gates: is_graded_rendition routes by union, so an off-content-type consumer is graded | qualified |  |
| 841 | handoff: steady-state repair grows with the corpus, 3->30 fixes/month | unclassified_reference | GHI #841 is cited in range by a commit whose type is not a closure type; no closure commit claims it. Adjudicate per SKILL.md § Step 1c before publishing |
| 842 | gz obpi complete: receipt stamped before the adversary event written above it | qualified |  |
| 843 | gz mx: hangar demotes gz validate guards but never reaches pre-commit hooks | qualified |  |
| 844 | hooks: write-side gates bind Write|Edit, so Bash file writes bypass all six | qualified |  |
| 845 | gz-obpi-pipeline: Stage-2 dispatch has a read path, no writer, no fail-close | qualified |  |
| 846 | skills: four cite a Superseded pool ADR as 'awaiting promotion' | qualified |  |
| 847 | hooks: four sibling gates still key on file_path, so Bash writes evade them | qualified |  |
| 848 | gz mx: exit orphans its lock, so the hangar is single-use per repo | qualified |  |
| 850 | session-start: the newest handoff is injected before its guard runs | qualified |  |
| 852 | mx: hangar demotes authorship, so the operator-PII guard stops firing | qualified |  |
| 853 | module-size ratchet: no arm reports an entry looser than its module (861 lines unrecorded) | qualified |  |
| 854 | cli doctrine: new-verb obligations described in 3 places, no two agree (4 of 7) | qualified |  |
| 855 | mx-mode: rule names the floor opt-in but not its two mechanisms or when to use which | qualified |  |
| 857 | unittest suite: 4 tests pass only in default order, fail under shuffle | qualified |  |
| 858 | gz check: Handoff documents validator is 19% of the gate and grows every session | qualified |  |
| 859 | gz handoff create: a REFUSED create still writes to the append-only rulings store | qualified |  |
| 860 | behave: @slow tag has no reader, and giving it one is the tier GHI #182 removed | qualified |  |
| 861 | pipeline-dispatch: Stage-2 prompts carry no persona, no Why, and restate contract values | qualified |  |
| 862 | corpus: 7 invariant texts stored twice, so amendment cannot be clean | qualified |  |
| 863 | gz content retire: says no recomposition is implied, then blocks the push | qualified |  |
| 864 | ghi-author: Step 0 cannot see an OBPI brief that owns the same work | qualified |  |
| 867 | obpi-state-machine: PLANNED has no vocabulary term, so Draft->Active is unreachable | qualified |  |
| 869 | task-envelope: commit-locus artifact_edited rows have no attribution channel, so they fail signature (a) unfixably | qualified |  |

## Operator Approval

Approved by gz patch release
