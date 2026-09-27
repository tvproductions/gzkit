# Defects and GHIs

An on-ramp: work that arrives as a finding rather than a plan. You are here when
something is wrong, drifted or missing.

## Steps

1. **Route it** by `AGENTS.md` § Defect-fix routing:
   - small, one surface, surfaced in flight, covered by a unit test → fix it
     directly, a `fix(<scope>): …` commit with a `Task:` trailer;
   - an authored OBPI brief owns the surface → report the brief and wait for
     the operator's ruling;
   - otherwise → file it.
2. **File it.** **`ghi-author`** — prior-art lookup first, then an issue with
   evidence and a closure contract. From an adopter repository, a defect in gzkit
   itself goes through **`gz-issue-file`**.
3. **Rank the queue.** **`ghi-triage`** reads every open issue and orders them.
4. **Fix and close.** **`ghi-close`** does the work, verifies it and closes the
   issue citing the commit. A GHI authorizes direct repair; it needs no ADR.

## Branches

- **The operator corrected you in flight** → **`gz-insights-remember`** records
  the course-correction before the corrected work completes.
- **A discovery or defect to note, not fix now** → `gz-insights-remember`.
- **The finding is a whole missing capability** → a pool ADR; see
  [Idea to ADR](idea-to-adr.md).
- **The gap is in a shipped surface's intent** → it is a correction under its
  owning ADR, not an enhancement.

## Only you can

Select which issue is worked next, and rule where routing is unclear.

## Then

[Commit and sync](commit-and-sync.md); later, [Release](release.md) collects the
closed issues.
