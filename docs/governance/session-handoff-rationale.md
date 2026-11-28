# Session handoff: rationale

This page holds the history and reasoning behind rules in the `gz-session-handoff` skill
(`.gzkit/skills/gz-session-handoff/SKILL.md`). The skill keeps the procedure and points here. It was
lifted out on 2026-11-28, when the skill gained the picture and the computed position
(`docs/design/briefs/SPEC-session-handoff-picture.md` § 10, which named this page; the body sat at
its size ceiling, so compression came before growth).

## The resume gate, and why it was retired

The resume gate bound mechanically from 2026-07-16 as `.claude/hooks/handoff-resume-gate.py`, a
PreToolUse refusal on an unruled handoff. Both arms are now gone: `Bash` on 2026-08-14 (*"why is the
handoff gate so picky? it is a reminder of what we were doing and what to do next, not a nanny"*),
and `Write|Edit|NotebookEdit` on 2026-08-15 (*"the handoff should be an advisor, not a gate-keeping
nanny"*). The hook, its generator template and both negative controls (`-bash`, `-write`) were
deleted, because a control asserting enforcement that no longer happens is worse than no control.

The whole arm went because GHI #574, which authorized the gate, quoted the remedy it was meant to
apply, *"place the human at a mechanical gate, **not at every keystroke**"*, and the gate shipped as
a hook on every mutating call. Entry and exit authorization is transit's subject (the airlock,
ADR-0.33.0). A handoff is a synthetic memory refresh, which has no natural blast radius, so the
question of what reading a reminder should prevent never had a principled answer. Its measured
lifetime: 9 lifts and 1 block over the single day refusal-recording existed, against 13
admission-breadth corrections in 29 days.

The read allowlist the skill once carried had no subject once the gate was retired. It needed 13
corrections in 29 days, every one a false refusal of a verification the skill mandated.

## Why `gz handoff decide` is not an attestation

`gz handoff decide` is an acknowledge-and-decide transit, never an attestation (GHI #757). ADR-0.0.33
§ Alternatives rejects that conflation by name: completion attestation is reserved for claims about
completed planned work, and spending that register on an every-transit record cheapens it. The
decision grammar is borrowed from the airlock's `Decision`; the records stay the handoff layer's own.
The predecessor shape was a consent boolean, so an operator who looked and ruled *not yet* left no
record at all, which is why a `hold` is booked too.

## Why resume leads with the position and the picture

The operator asked for three levels of picture from a handoff (2026-10-29, verbatim: *"I, as human,
am interested in those three levels of picture."*), and the specification was accepted on 2026-10-31.
Resumes kept presenting the advised steps and the issue queue instead, and the operator said so on
2026-11-28: *"I asked for this as a part of every handoff resume and still dont have it: current
tactical|operational|strategic position."* The same day the operator ruled the build now rather than
after the handback (*"build it now so every resume shows the position - this should cut down on vibe
coding."*), both an authored picture and computed facts (*"Both (Recommended)"*), and the reading
order (*"left to right: tactical | operational | strategic"*).

The computed position (`gzkit.mx.position`) is there so the author's picture sits beside numbers it
cannot change. Each fact names where it was read. The states of the repair orders are not computed,
because they live only in prose; they stay in the picture until a record carries them.
