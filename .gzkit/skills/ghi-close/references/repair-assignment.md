# ghi-close — the operator-ruled repair assignment

Reference material for `ghi-close`, held outside `SKILL.md` because few runs
reach it and the skill body is at its ceiling. It describes the one route from
a GHI to a brief that is not a route correction. Only the operator opens it.

## When it applies

The GHI's finding is that a shipped surface does not fulfil what an ADR
declared. `AGENTS.md` § Operator Doctrine calls that a correction: "discovering
that more is needed to fulfill the intent of a feature is not an enhancement, it
is a correction." It is not the same as broken behaviour in a surface that did
fulfil its intent, which is a direct fix.

## What never opens it

Lane is not route. A GHI-tracked defect repair is a direct fix even when it adds
a CLI surface (`.gzkit/rules/cli.md` § Adding CLI Features;
`docs/governance/rule-version-history.md`). Lane, surface heat, diff size and
the wording of the GHI body never turn a repair into a brief.

## Authority

- The work-order ruling carried by `gz-obpi-pipeline`: an ADR in flight may be
  revised to take more OBPIs, and scope missed from a Validated ADR enters the
  in-flight ADR as a repair assignment that cites the obligation it repairs.
- Campaign plan § Amendments 2026-10-04 (3).
- Operator ruling 2026-10-05, on how the two routes divide defect work: lane is
  not route stands, and only unmet ADR intent can go to a brief, by the
  operator's ruling alone.

## Procedure

1. Do not author a brief or an ADR. Put the finding to the operator with the
   routing facts: the ADR and its lifecycle, the declared-intent sentence the
   surface falls short of, quoted, and the size and surfaces of the repair.
2. The operator rules. A ruling for direct repair returns to Phase 2 as usual.
3. On a ruling for a repair assignment, the brief is authored under the
   in-flight ADR on the operator's direction, and the ADR is revised in the same
   change. This skill does not do that work.
4. Close the GHI `superseded` once `uv run gz obpi status <OBPI-ID>` resolves
   the brief. The close comment says that nothing is implemented, maps each
   clause of the issue's closure contract to a brief criterion, and names every
   clause the brief widens or narrows as a contract amendment.

Close with the default reason. `--reason "not planned"` tells a reader the work
will not be done, which is false for a routed issue.

## Worked instance

GHI #1172 to #1176 were five findings against `ADR-0.13.0`, `ADR-0.18.0` and
`ADR-0.0.41`, all Validated. The operator ruled each into the in-flight
`ADR-0.35.0` as a repair assignment, and they closed `superseded` on 2026-10-05
against `OBPI-0.35.0-15` to `OBPI-0.35.0-20`.
