# Does it work?

You are here when the question is not "is this commit green" but "does what we
built do what we meant".

## Steps

- **It feels wobbly or misaligned; governance may not be holding** →
  **`gz-health-audit`** (operator-invoked): four axes in a fixed, cheapest-first
  order.
- **What shipped against what was decided** → **`gz-intent-trace`**: samples
  ADRs, traces intent to the shipped surface, and routes each gap as a
  correction under its owning ADR.
- **Prove a workflow end to end** → **`gz-flighttest`**: one sortie against a
  target repository, with a human Go/No-Go.
- **The wide view** → **`gz-big-picture`** (operator-invoked): what the project
  is, what it is becoming, and where design and reality diverge.

## Branches

- **A gap found** — a shipped surface that misses its declared intent is a
  correction, not an enhancement; see [Defects and GHIs](defects-and-ghis.md).

## Only you can

Start the health audit and the big-picture report; call Go or No-Go on a sortie.

## Then

Route each finding: [Defects and GHIs](defects-and-ghis.md) or
[Idea to ADR](idea-to-adr.md).
