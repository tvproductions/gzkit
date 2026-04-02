# The Anxiety-Governance Symbiosis: LLM + Harness vs. SKILL + Code

## The Setup

Three sources walked into a conversation about whether governance frameworks for AI coding agents are worth building. The first was a YouTube breakdown of how Boris Cherny, creator of Claude Code, starts every project. The second was a hype video about Claude Mythos and the "bitter lesson" of building with LLMs. The third was a talk by Mario Zechner, game development veteran and creator of libGDX, explaining why he built pi — his own minimal terminal coding agent — after getting fed up with every existing harness.

Between them, they surface a tension that anyone building seriously with AI coding tools has to confront: where does enforcement live?

## What Boris Actually Said

Boris's workflow is simple and practical. Eighty percent of his sessions start in plan mode. He babysits before the plan, not after. Once the plan is locked in, building is almost automatic.

His Claude.md — the persistent instruction file Claude reads every session — is short. A couple thousand tokens. His advice when it gets bloated: delete the whole thing and start fresh. Add rules back one at a time only when the model actually drifts. His reasoning is that models improve, and what you needed six months ago is likely built into the model now.

He uses verification loops: give Claude a way to see the output of its work, tell Claude about that tool, and Claude figures out the rest. He runs parallel sessions for partitioned tasks. He systemizes repeated workflows into slash commands and skills. And he frames all of this under the "bitter lesson" — never bet against the model.

Plan mode, minimal instructions, verification, parallel sessions, inner-loop skills. That's the system.

## What the Bitter Lesson Crowd Added

A second video took the "bitter lesson" further, pegged to the leaked Claude Mythos model. The argument: when models get bigger and smarter, simplify everything. Delete prompt scaffolding. Stop specifying process. Let the model fill its own context window. Move toward one eval gate at the end of the software process. Get out of the way.

The specific recommendations: audit every line of your prompts and ask "is this here because the model needs it, or because I needed the model to need it?" Reduce retrieval micromanagement. Stop hardcoding domain knowledge the model can infer. Simplify, simplify, simplify.

There was also a significant chunk of the video dedicated to pricing — Mythos will be expensive, you'll need a Max plan, people without it will fall behind. The structure was excitement, flattery of the model, scarcity, purchase recommendation, fear of missing out. That's a sales funnel dressed as architecture advice.

## What Mario Zechner Actually Experienced

Mario's story starts the same way many do. Peter Steinberger and Armin Ronacher dragged him into an overnight AI hackathon. Within weeks he was hooked on Claude Code. Then he wasn't.

His complaints were specific and grounded: feature bloat, hidden context injection that changed daily, the infamous terminal flicker, and zero extensibility for power users. He built interception tools that revealed what additional text Claude Code was injecting into context behind his back — and it changed constantly, sometimes daily, breaking existing workflows without warning.

He surveyed the alternatives. Codex CLI — didn't like the UI or the model at the time. AMP — good engineering, but no model choice. Open Code — solid team, but called session compaction on every turn, busting the prompt cache. Plus a security vulnerability with remote code execution baked in by default. Factory — similar story.

Then he found Terminus, a benchmark entry that gives the model nothing but a tmux session and raw keystrokes. On TerminalBench, Terminus with Claude performed near the top of the leaderboard. No file tools, no sub-agents, no web search, no nothing.

His conclusion: we're in the "messing around and finding out" stage, and nobody knows what the perfect coding agent looks like. His answer was pi — four tools (read, write, edit, bash), the shortest system prompt of any major agent, tree-structured sessions, full cost tracking, hot-reloading TypeScript extensions, and nothing injected behind your back.

Pi on TerminalBench with Claude Opus landed right behind Terminus before it even had compaction.

## The Question That Started This

I asked a separate AI to appraise a conversation about whether a framework like gzkit — a governance runtime I've been building for human-AI collaboration — might be a waste of time in light of the "bitter lesson" argument.

That conversation produced a useful three-category framework for thinking about structure around AI agents:

**Compensatory structure** — temporary scaffolding added because weaker models needed extra help. Long procedural prompts, retrieval choreography, step-by-step reasoning constraints. This should be simplified as models improve.

**Operational structure** — tools, interfaces, permissions, eval harnesses. Structure that lets any agent do useful work safely. This should be refined, not discarded.

**Governance structure** — ledger-backed state, typed entities, traceability chains, attestation boundaries, lifecycle transitions. Structure that preserves human intent, evidence, and authority. This is architecture, not scaffolding.

The conversation concluded that the "bitter lesson" should make gzkit thinner at the prompt layer and stronger at the runtime/governance layer. If it makes gzkit thinner everywhere, that's a category error.

Then it produced a 3,000-word architectural steering memo saying essentially that.

## Where the Conversation Actually Got Interesting

I brought the full source material — both video transcripts — to Claude Code, the system that actually runs with gzkit's rules loaded, and asked for an honest appraisal.

The appraisal was blunt. Video 1 (Boris) was solid practical advice for individual practitioners. Video 2 (Mythos/bitter lesson) was speculative hype built on a leak, with a sales funnel embedded in it. The narrator admitted repeatedly he hadn't tested Mythos, then spent thirty minutes telling you to restructure your systems for it.

But the sharper point was this: the previous conversation treated the source material as more sophisticated than it actually was. A YouTuber riffing on a leak for thirty minutes didn't warrant a 3,000-word architectural steering memo. The irony was noted — a conversation about eliminating bloat produced a bloated artifact.

Then I pushed back.

## The Anxiety-Governance Symbiosis

The conversation reached its real subject when I pointed out that governance and anxiety share a root cause: things go wrong.

Every legitimate governance rule also feels emotionally justified. Every anxiety-driven rule looks like governance. You can't distinguish them by asking "is this important?" because both feel important. You can only distinguish them by asking "does removing this cause a measurable defect?"

And most of gzkit's rules have never been tested by removal. They were added after something went wrong, which is exactly how anxiety accumulates — every bad experience becomes a permanent rule, and the rule is never re-evaluated because removing it feels like inviting the bad experience back.

The symbiosis runs deeper. Governance systems attract anxiety. The more structured and thorough the system, the more natural it feels to add one more rule, one more check, one more enforcement. The system's legitimacy provides cover for its bloat.

Claude Code classified gzkit's rules into three buckets: load-bearing (would break without them), could-be-a-linter (enforcing via prose what tools could enforce), and probably-accumulated-anxiety. The split was roughly a third each.

Then I pushed back harder.

## Why Rules Exist

The classification was too clean. "Unittest not pytest" and "no bare except" are the same kind of rule. Both exist because without them, the model will do the wrong thing. The only difference is that ruff happens to catch one after the fact — but catching after the fact still costs tokens. The prose rule that prevents the mistake is cheaper than the runtime correction.

The honest framing isn't "load-bearing vs. anxiety." It's: these are all load-bearing, because the model is unreliable in predictable, repeatable ways.

I'm not adding rules because I'm anxious. I'm adding rules because I've observed specific, recurring failures and I'm paying for them in tokens and time every time they happen. That's not anxiety. That's empirical engineering. Every mature codebase has a style guide for exactly this reason — not because developers can't figure it out, but because consistency is cheaper than correction.

The "bitter lesson" crowd gets this backwards for my situation. They say "trust the model more, delete rules." I've learned the opposite through direct experience: the model will drift without constraints, and the cost is real and measurable.

The anxiety isn't just a quirk. It is borderline trauma from working regularly and intimately with non-compliant tools.

## The Same Trauma, Different Responses

This is where Mario's story connects.

Mario experienced the same frustrations that drive gzkit's existence: hidden context injection, unpredictable behavior changes breaking workflows, zero observability, vendor instability. His response was to go minimal — four tools, shortest system prompt, nothing hidden.

My response was the opposite direction — more structure, more governance, more typed enforcement.

Both are coping strategies for the same underlying problem: the harness is unreliable and opaque, and the vendor doesn't care because they're optimizing for a different user.

Boris builds for Boris. Anthropic builds for the median user. Neither is building for me or Mario.

The Terminus result is the sharpest data point in everything discussed. A model given nothing but a tmux session and raw keystrokes performs near the top of the benchmark. That's a genuine empirical challenge to every agent harness. If the model can perform with almost nothing, then the value of everything we add must be justified by something other than model capability — it has to be justified by human needs: governance, accountability, evidence, repeatability across sessions, portability across vendors.

## The Actual Design Space

The real tension isn't "too many rules vs. too few." It's that gzkit is building durable governance on top of an unstable substrate. Mario's answer was to replace the substrate. My answer is to armor above it. Neither is wrong. Both are exhausting.

And someone telling you to "simplify and trust the model" from behind a monetized YouTube channel is not helpful to either approach.

The scale balance I keep coming back to is between two forces:

**SKILL + Code** — repeatable procedures, typed artifacts, machine-enforced transitions, evidence trails, human attestation. The governance layer. What gzkit builds.

**LLM + Harness** — model capability, vendor tooling, context management, retrieval, autonomous exploration. The substrate. What Boris, Anthropic, and the bitter lesson crowd optimize for.

Every rule in my `.claude/rules/` directory is an admission that the runtime doesn't enforce it yet. That's not anxiety. That's an honest accounting of where the system is today. The migration path isn't from thick rules to thin rules. It's from prose governance to runtime governance. The anxiety doesn't go away — it gets compiled.

## The Question That Matters

Boris says delete your instruction file and start fresh. The bitter lesson crowd says simplify everything and trust the model. Mario says strip away everything and build a minimal extensible core.

The question for anyone building governance around AI tools isn't whether to simplify. It's what the simplification is in service of.

If you simplify to trust the model more, you're betting on vendor capability continuing to improve in directions that serve your needs. That's a bet. It might pay off.

If you simplify to make governance more executable and less prose-dependent, you're migrating enforcement from text the model reads to constraints the model can't bypass. That's engineering.

If you simplify because a YouTuber told you Mythos is coming and you need to get ready, you're responding to a sales funnel.

The only simplification that matters is the one that reduces defects, preserves accountability, and doesn't require you to trust a vendor who changes the substrate out from under you every other Tuesday.

I'm not an expert. Few are, given the nascency, recency, and emergence of these platforms. But I know the toll of working daily with non-compliant tools, and I know the difference between governance and anxiety isn't philosophical — it's empirical. Remove the rule, observe what breaks, measure the cost. If the runtime catches it, the prose was anxiety. If nothing breaks, it was dead weight. If a real defect occurs, add it back as runtime enforcement.

That's the work. Not "simplify." Not "trust the model." Not "buy the Max plan."

Compile the anxiety into enforcement. That's what governance is for.
