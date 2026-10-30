# Shape Up (Ryan Singer, Basecamp)

Retrieved by HTTP GET from `https://basecamp.com/shapeup/...` (HTML converted to text locally; no refusal). Access date: 2026-10-30. **Primary** (the book's own online edition). Quotations verbatim.

## Appetite

Source: https://basecamp.com/shapeup/1.2-chapter-03 ("Set Boundaries"). Primary.

> We call this the appetite. You can think of the appetite as a time budget for a standard team size. We usually set the appetite in two sizes:
>
> Small Batch: This is a project that a team of one designer and one or two programmers can build in one or two weeks. We batch these together into a six week cycle (more on that later).
>
> Big Batch: This project takes the same-size team a full six-weeks.
>
> In rare cases where the scope is so big that a six-week project isn’t conceivable, we’ll try to hammer it down by narrowing the problem definition. If we still can’t shrink the scope, we’ll break off a meaningful part of the project that we can shape to a six-week appetite.

> An appetite is completely different from an estimate. Estimates start with a design and end with a number. Appetites start with a number and end with a design. We use the appetite as a creative constraint on the design process.

> This principle, called “fixed time, variable scope,” is key to successfully defining and shipping projects.

Source: same chapter, § "Watch out for grab-bags". Primary.

> When it comes to unclear ideas, the worst offenders are “redesigns” or “refactorings” that aren’t driven by a single problem or use case. When someone proposes something like “redesign the Files section,” that’s a grab-bag, not a project.

> A tell-tale sign of a grab-bag is the “2.0” label. We made the mistake in the past of kicking off a “Files 2.0” project without really considering what that meant. [...] The project turned out to be a mess because we didn’t know what “done” looked like. We recovered by splitting the project into smaller projects, like “Better file previews” and “Custom folder colors.” We set appetites and clear expectations on each project and shipped them successfully.

## The pitch

Source: https://basecamp.com/shapeup/1.5-chapter-06 ("Write the Pitch"). Primary.

> The purpose of the pitch is to present a good potential bet. It’s basically a presentation. The ingredients are all the things that we need to both capture the work done so far and present it in a form that will enable the people who schedule projects to make an informed bet.

> There are five ingredients that we always want to include in a pitch:
>
> Problem — The raw idea, a use case, or something we’ve seen that motivates us to work on this
>
> Appetite — How much time we want to spend and how that constrains the solution
>
> Solution — The core elements we came up with, presented in a form that’s easy for people to immediately understand
>
> Rabbit holes — Details about the solution worth calling out to avoid problems
>
> No-gos — Anything specifically excluded from the concept: functionality or use cases we intentionally aren’t covering to fit the appetite or make the problem tractable

> The best problem definition consists of a single specific story that shows why the status quo doesn’t work. This gives you a baseline to test fitness against.

> That’s not ready to pitch or bet on. A problem without a solution is unshaped work.

> It’s only ready to bet on when problem, appetite, and solution come together.

## No backlog; potential bets

Source: https://basecamp.com/shapeup/2.1-chapter-07 ("Bets, Not Backlogs"). Primary.

> Now that we’ve written a pitch, where does it go? It doesn’t go onto a backlog.

> Before each six-week cycle, we hold a betting table where stakeholders decide what to do in the next cycle. At the betting table, they look at pitches from the last six weeks — or any pitches that somebody purposefully revived and lobbied for again.
>
> Nothing else is on the table. There’s no giant list of ideas to review. There’s no time spent grooming a backlog of old ideas. There are just a few well-shaped, risk-reduced options to review. The pitches are potential bets.

> If we decide to bet on a pitch, it goes into the next cycle to build. If we don’t, we let it go. There’s nothing we need to track or hold on to.
>
> What if the pitch was great, but the time just wasn’t right? Anyone who wants to advocate for it again simply tracks it independently—their own way—and then lobbies for it six weeks later.

> There’s no one backlog or central list and none of these lists are direct inputs to the betting process.

## Betting table, cycle, cool-down

Source: https://basecamp.com/shapeup/2.2-chapter-08 ("The Betting Table"). Primary.

> A cycle gives us a standard project size both for shaping and scheduling.

> Therefore, after each six-week cycle, we schedule two weeks for cool-down. This is a period with no scheduled work where we can breathe, meet as needed, and consider what to do next.

> We call the team that spends the cycle doing one project the big batch team and the team working on a set of smaller projects the small batch team. Small batch projects usually run one or two weeks each. Small batch projects aren’t scheduled individually.

> The betting table is a meeting held during cool-down where stakeholders decide what to do in the next cycle. The potential bets to consider are either new pitches shaped during the last six weeks, or possibly one or two older pitches that someone specifically chose to revive.

> The output of the call is a cycle plan.

> First, bets have a payout. We’re not just filling a time box with tasks until it’s full. [...] We intentionally shape work into a six-week box so there’s something meaningful finished at the end. The pitch defines a specific payout that makes the bet worth making.
>
> Second, bets are commitments. [...]
>
> Third, a smart bet has a cap on the downside. If we bet six weeks on something, the most we can lose is six weeks.

> Teams have to ship the work within the amount of time that we bet. If they don’t finish, by default the project doesn’t get an extension.

> Bring it to the betting table. If a bug is too big to fix during cool-down, it can compete for resources at the betting table.

> The key to managing capacity is giving ourselves a clean slate with every cycle. That means only betting one cycle at a time and never carrying scraps of old work over without first shaping and considering them as a new potential bet.

> What about projects that just can’t be done in one cycle? In that case we still only bet six weeks at a time. Suppose we envision a feature that takes two cycles to ship. We reduce our risk dramatically by shaping a specific six week target, with something fully built and working at the end of that six weeks.

## Scopes (inside a project)

Source: https://basecamp.com/shapeup/3.3-chapter-12 ("Map the Scopes"). Primary.

> We call these integrated slices of the project scopes. We break the overall scope (singular) of the project into separate scopes (plural) that can be finished independently of each other.

> The scopes reflect the meaningful parts of the problem that can be completed independently and in a short period of time—a few days or less. They are bigger than tasks but much smaller than the overall project.

> Scopes arise from interdependencies. The way parts depend on each other determines when you can say a given piece of the work is “done.” You don’t know what the work and interdependencies actually are in advance.

## Checking what landed against the baseline

Source: https://basecamp.com/shapeup/3.5-chapter-14 ("Decide When to Stop"). Primary.

> Instead of comparing up against the ideal, compare down to baseline—the current reality for customers. How do customers solve this problem today, without this feature?

> The must-haves are captured as tasks on the scope. The scope isn’t considered “done” until those tasks are finished. Nice-to-haves can linger on a scope after it’s considered done. They’re marked with a tilde (~) in front.

## Shape as stated

Shape Up's containers are: the **pitch** (problem as a single story, appetite, solution, rabbit holes, no-gos; "a potential bet" whose payout justifies the bet), the **bet** (a commitment of one cycle to a pitch), the **cycle** (six weeks, followed by a two-week **cool-down**), the **cycle plan** (output of the **betting table**, which looks only at recent or deliberately revived pitches), and inside a bet, **scopes** (independently finishable slices discovered during the work) holding tasks. Appetite is a time budget fixed before design; scope varies. There is explicitly no central backlog: unchosen pitches are let go, and anyone may track them privately and re-lobby. Small-batch projects are batched together into one cycle. A project larger than one cycle is bet on one six-week slice at a time. Bugs and similar work either go into cool-down or are pitched to compete at the betting table. Completion is judged against the baseline (current customer reality), with nice-to-haves marked "~". The book has no separate release/version record; the unit that ships is the bet within the cycle.
