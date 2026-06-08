# Power Prompts to Master Building with AI

A field guide to the high-leverage prompts most people never use. These are organized by *intent* — what you're actually trying to accomplish — because the secret to mastering AI isn't memorizing magic words, it's knowing which **move** to make at which moment.

> **Core principle:** The model is a reasoning engine, not a search box. Your job is to give it a *role*, *constraints*, a *thinking process*, and a way to *check its own work*. Almost every prompt below does at least two of those four.

---

## 1. Force the AI to Think Before It Answers

Most people accept the first answer. Experts make the model *reason first*, then answer.

### The "Think step by step, then critique yourself" move
```
Before you answer, do three things:
1. Reason through the problem step by step.
2. List the assumptions you're making.
3. Identify where you're most likely to be wrong.
Then give your final answer, and rate your confidence 0–100%.
```
**Why it works:** Surfaces hidden assumptions and self-flags weak spots so you know what to double-check.

### The "Plan first, code later" move
```
Don't write any code yet. First, write a short technical plan:
the files you'll create/change, the data flow, and the edge cases.
Wait for my approval before implementing.
```
**Why it works:** Catches architectural mistakes before they get baked into 300 lines of code.

### The "Reason from first principles" move
```
Ignore conventional wisdom and common patterns for a moment.
Derive a solution from first principles. What does this problem
*fundamentally* require? Then compare your first-principles answer
to the standard approach and tell me where they differ.
```

---

## 2. Make the AI Interview You

The biggest unlock almost nobody uses: tell the AI to ask *you* questions.

### The "Reverse prompt" move
```
I want to build [X]. Before you start, ask me up to 7 questions
that would most change your approach. Ask them one at a time,
and wait for my answer before the next.
```
**Why it works:** The model fills its context with *your* real constraints instead of guessing. This single technique improves output quality more than any other on this list.

### The "Fill the gaps in my thinking" move
```
Here's my plan: [paste]. What am I not considering?
What questions should I be asking that I'm not?
What will I regret in 6 months?
```

---

## 3. Use Roles and Personas as Reasoning Lenses

A role isn't flavor — it changes which knowledge and standards the model applies.

### The "Panel of experts" move
```
Answer as a panel of three experts who disagree:
a pragmatic senior engineer, a security researcher, and a
performance-obsessed systems programmer. Have them debate,
then synthesize a final recommendation they'd all sign off on.
```
**Why it works:** Surfaces trade-offs a single perspective would hide.

### The "Adversarial reviewer" move
```
You are a hostile staff engineer reviewing this code in a PR.
Your job is to find every real problem: bugs, security holes,
race conditions, bad naming, missing tests. Be specific and
ruthless, but only flag things that are actually wrong.
```

### The "Explain like I'll be tested" move
```
Teach me [concept] as if I have to pass a rigorous oral exam on it
tomorrow. Build from fundamentals, use one concrete example,
then quiz me with 3 questions that expose whether I actually get it.
```

---

## 4. Self-Correction and Verification Loops

The model is far better at *checking* work than producing perfect work in one shot.

### The "Critique and revise" move
```
Now critique your own answer above as if a domain expert wrote
a harsh review of it. List the 3 biggest weaknesses.
Then rewrite the answer to fix them.
```

### The "Red team your own output" move
```
You just gave me this solution. Now try to break it.
What inputs make it fail? What did you assume that might be false?
What happens at scale, under load, or with malicious input?
```

### The "Prove it" move
```
For each claim you made, mark it as [verified], [likely], or
[uncertain]. For anything [uncertain], tell me exactly how I'd verify it.
Do not present guesses as facts.
```
**Why it works:** Directly attacks hallucination by forcing the model to separate knowledge from inference.

---

## 5. Building Software: The High-Leverage Coding Prompts

### The "Constraints first" scaffold
```
Build [feature]. Constraints:
- Language/framework: [...]
- Must NOT change: [...]
- Style: match the existing code in [file]
- Optimize for: readability over cleverness
- Include: tests for the edge cases you identify
Explain any trade-off you make that I might disagree with.
```

### The "Strangler / incremental" move
```
Don't rewrite this. Improve it in the smallest safe steps.
Give me change #1 only, explain why it's safe, and how to verify it
before we move to change #2.
```
**Why it works:** Keeps you in control and makes every change reviewable and reversible.

### The "Explain this codebase" move
```
Act as the engineer who wrote this. Walk me through:
1. The 5-minute mental model of how it works.
2. The non-obvious decisions and *why* they were made.
3. The parts that would bite a new contributor.
Use the actual file and function names.
```

### The "Make it production-grade" move
```
This works, but it's a prototype. List everything standing between
this and production: error handling, logging, tests, security,
observability, failure modes. Prioritize by risk. Then fix the top 3.
```

### The "Rubber duck with a genius" move
```
I have a bug: [describe symptom]. Don't fix it yet.
Ask me diagnostic questions and form hypotheses with me,
ranked by likelihood, until we isolate the root cause.
```

---

## 6. Control the Output Format Precisely

### The "Output contract" move
```
Respond ONLY in this format:
## Summary (2 sentences)
## Steps (numbered)
## Risks (bullets)
## Next action (one sentence)
If you have nothing for a section, write "None".
```

### The "Diff, not essay" move
```
Show me only what changes: the exact lines to add, remove, or edit.
No restated unchanged code, no preamble. Then one line on why.
```

### The "Progressive disclosure" move
```
Give me the answer in three layers:
(1) one sentence, (2) one paragraph, (3) full detail.
I'll tell you how deep to go.
```

---

## 7. Thinking and Strategy Prompts (Beyond Code)

### The "Inversion" move
```
Instead of telling me how to succeed at [goal], tell me the surest
ways to *fail* at it. Then turn each failure into a rule to avoid it.
```

### The "Second-order effects" move
```
If I do [decision], what happens next? Then what happens after that?
Trace the consequences three steps out, including the ones I'd never expect.
```

### The "Steelman the opposite" move
```
I believe [X]. Make the strongest possible case for the opposite of [X],
strong enough that a smart person would be persuaded.
Then tell me which view actually has better evidence.
```

### The "10x / 10% constraint" move
```
Solve this two ways: first with 10x the resources, then with 1/10th.
The extreme constraints will reveal what actually matters.
```

---

## 8. Meta-Prompts: Make the AI Improve Your Prompts

### The "Upgrade my prompt" move
```
Here's a prompt I'm about to use: [paste].
Rewrite it to get a dramatically better result. Then explain
what you changed and why. Then ask me anything you still need.
```
**Why it works:** The model knows what makes prompts effective better than you do. Let it teach you.

### The "What should I have asked?" move
```
Based on everything in this conversation, what's the most valuable
question I haven't thought to ask you yet? Answer it.
```

### The "Build me a reusable prompt template" move
```
Turn this one-off request into a reusable template with
{{placeholders}} I can fill in next time, plus notes on when to use it.
```

---

## 9. Context-Loading Power Moves

### The "Prime with examples" move
```
Here are 2 examples of the style/quality I want: [A], [B].
Now produce a third in the same spirit. Match the voice, depth, and format.
```
**Why it works:** Showing beats telling. Two good examples outperform a paragraph of description.

### The "Persistent rules" move
```
For the rest of this conversation, always follow these rules:
- [rule 1]
- [rule 2]
Confirm you understand, then we'll begin.
```

### The "Memory dump then synthesize" move
```
I'm going to paste a lot of messy context. Don't respond to it yet —
just say "ready" after each chunk. When I say "GO", synthesize it all
into [the thing I need].
```

---

## 10. The Habits That Separate Masters from Beginners

1. **Iterate, don't restart.** Refine in the same thread so context compounds. A 5th-iteration answer beats a fresh first try.
2. **Make it ask questions.** If you only adopt one habit, adopt the reverse-prompt (Section 2).
3. **Always demand self-critique.** The second draft, after a critique, is almost always the one worth keeping.
4. **Show, don't just tell.** Examples of what "good" looks like beat adjectives every time.
5. **Separate planning from doing.** Approve the plan before any code is written.
6. **Ask it to flag uncertainty.** Never let guesses masquerade as facts.
7. **Give it a way to check itself.** Tests, verification steps, "prove it" — these turn a confident guesser into a reliable collaborator.

---

### One prompt to rule them all (a starter you can paste today)
```
You are an expert collaborator on [task].
Step 1: Ask me the 5 questions that most change your approach,
        one at a time.
Step 2: Write a short plan and wait for my approval.
Step 3: Execute in small, verifiable steps.
After each step, critique your own work, flag any uncertainty,
and tell me how to verify it before continuing.
```

Master these, and you stop *using* AI and start *directing* it.

---

## 11. Why These Moves Work (The Mechanisms)

The prompts above aren't magic words — each exploits a real property of how large
language models behave. Knowing the *mechanism* lets you invent your own moves.

- **Chain-of-thought / "think step by step"** — models allocate more intermediate
  computation when they generate reasoning tokens before an answer, measurably
  improving multi-step accuracy. (Wei et al., 2022.)
- **Self-consistency & self-critique** — sampling or re-examining an answer and
  reconciling improves reliability over a single greedy pass. (Wang et al., 2022.)
- **Few-shot / in-context examples** — two good examples constrain the output
  distribution far more sharply than adjectives. (Brown et al., 2020.)
- **Role prompting** — a persona shifts which region of the model's training
  distribution it samples from (standards, vocabulary, defaults).
- **Reverse-prompting (let it interview you)** — fills the context window with
  *your* real constraints, the single biggest driver of output relevance.
- **ReAct / tool use** — interleaving reasoning with actions (search, code,
  retrieval) grounds answers in facts and reduces hallucination. (Yao et al., 2022.)
- **Verification framing ("prove it", "mark uncertainty")** — forces the model to
  separate retrieved knowledge from inference, exposing where it's guessing.

### The transferable principle
Give the model **(1) a role, (2) constraints, (3) a thinking process, and (4) a
way to check itself.** Any prompt that does two or more of these will outperform
a bare question. Everything above is a recombination of those four levers.

---

## 12. Going Fast Without Letting AI Hide the Fundamentals

This is the section that matters most for *your* path. The ten-year mastery plan
([02-ten-year-mastery-plan.md](02-ten-year-mastery-plan.md)) has one
non-negotiable principle: **use AI to go faster, never to skip the
understanding.** A model that writes your EKF for you is an accelerant if you can
re-derive it, and a liability if you can't. The difference is *discipline*, and
it's almost entirely about how you prompt.

### The rule: AI may scaffold, you must own
- **Generate, then re-derive.** Let the model produce the quaternion update or the
  PID anti-windup logic — then close it and re-derive the key step yourself. If
  you can't, you don't understand it yet, and you've found your study target.
- **Never paste code you can't debug at 3 a.m.** On a real Pixhawk, a bug you
  don't understand is a crash you can't fix. The cost of hidden fundamentals is
  paid in hardware.
- **Ask for the *why*, not just the *what*.** Every accept should come with a
  one-paragraph explanation you could give in an interview
  ([17-career-interview-prep.md](17-career-interview-prep.md)).

### Prompts that force understanding instead of outsourcing it
**The "teach me as you build" move**
```
Implement [thing]. As you go, narrate the reasoning like a tutor:
why each design choice, what the alternative was, and what would
break if I did it the naive way. End with 3 questions that test
whether I actually understand it — and don't give the answers yet.
```

**The "no-code-until-I-can-derive-it" move**
```
Before writing any code for [algorithm], walk me through the math
from first principles. Stop at each step and ask me to predict the
next line. Only write the implementation after I've reasoned through
the derivation with you.
```

**The "find my gap" move**
```
Here's my explanation of how [concept] works: [paste my words].
Don't be polite — find every place my mental model is wrong,
incomplete, or hand-wavy. Then give me the minimal correction
for each, and one exercise that would close the gap.
```

> The tell of mastery: you could rebuild the thing the AI gave you on a whiteboard,
> from memory, under questioning. If you can't, you haven't learned — you've
> *borrowed*. Prompt accordingly.

---

## 13. Domain Prompt Library: Autonomy, Embedded, Controls, Estimation

High-leverage prompts tuned for the actual work of building a PX4/Pixhawk + Pi 5
autonomy stack. Cross-reference the technical guides:
[22-autonomy-px4-sitl.md](22-autonomy-px4-sitl.md),
[23-autonomy-onboard-system.md](23-autonomy-onboard-system.md),
[25-autonomy-control-theory.md](25-autonomy-control-theory.md),
[28-autonomy-gnc.md](28-autonomy-gnc.md).

### Controls
```
Act as a flight-controls engineer. I have a [quadplane/multirotor]
with [mass, arm length, prop data]. Derive the attitude-rate PID
starting points from first principles, explain the physical meaning
of each gain, and tell me the failure mode of getting each one wrong.
Then give me a safe SITL tuning sequence, innermost loop first.
```

### State estimation
```
You are an estimation specialist. Explain why PX4's EKF2 fuses
[GPS + baro + mag + IMU] the way it does. Walk through one
measurement-update step with real units. Then list the top 5 ways
this filter diverges in flight and the telemetry signature of each.
```

### Embedded / real-time
```
Act as a real-time embedded reviewer. This runs in a [1 kHz] control
loop on [STM32 / Pi 5]. Flag anything that allocates, blocks, takes a
lock, or has unbounded latency on the hot path. For each, give the
deterministic alternative. Assume a missed deadline can crash an aircraft.
```

### ROS 2 / middleware
```
I'm wiring [node A] to [node B] over ROS 2 with [DDS QoS settings].
Explain how messages can be dropped or delayed under this config,
what QoS profile fits a [safety-critical command vs. telemetry] topic,
and how I'd prove the latency budget holds.
```

### Simulation / SITL
```
Design a SITL test that would catch [specific failure, e.g. GPS-denied
drift] before it ever reaches hardware. Specify the scenario, the
injected fault, the pass/fail metric, and the log fields I'd assert on.
```

### Sensor fusion / GNSS resilience
```
Act as a navigation engineer hardening against GPS jamming/spoofing.
Given [my sensor suite], propose a fusion strategy that degrades
gracefully when GNSS is denied. Rank the options by added complexity
vs. resilience, and tell me how I'd test each in SITL and on bench.
```
*(See [26-autonomy-gnss-jamming-spoofing.md](26-autonomy-gnss-jamming-spoofing.md).)*

---

## 14. Debugging From Logs & Telemetry

The model is excellent at pattern-matching a wall of logs *if you frame it right*.
The trick is to make it form ranked hypotheses before touching code.

### The "diagnose from the log" move
```
Here is a [PX4 ULog excerpt / dmesg / stack trace]: [paste].
Don't propose a fix yet. First: (1) summarize what the system was
doing, (2) list the anomalies in order of when they appear,
(3) give 3 ranked root-cause hypotheses with the evidence for each,
(4) tell me the single next datum that would best discriminate
between them. Then wait.
```

### The "bisect with me" move
```
This worked at commit [A] and fails at [B]. Help me bisect:
given these symptoms, which changes in that range are most suspect
and why? Propose the order to test them to converge fastest.
```

### The "timeline reconstruction" move
```
From these timestamped logs, reconstruct an exact timeline of events
leading to [the failure]. Mark each entry as cause, symptom, or
unrelated noise. Flag any gap where I'm missing instrumentation.
```

**Discipline note:** make it cite the *specific log line* for every claim
("[verified] line 412 shows EKF innovation spike"). A hypothesis with no log
anchor is a guess — see the "Prove it" move in Section 4.

---

## 15. Code Review & Hardening for Real-Time / Embedded

Generic "review this code" gets generic results. Constrain the reviewer to your
actual failure domain.

### The "hostile flight-software reviewer" move
```
You are a skeptical flight-software reviewer signing off before a
test flight. Review this for: undefined behavior, integer/float
overflow, unit mismatches, unchecked return codes, blocking calls on
the control path, and any state that isn't safe under sudden RC loss
or power glitch. Only flag real defects. For each, give severity and
the exact fix.
```

### The "make it production-grade for hardware" move
```
This passes in SITL. List everything between here and flying it on
real hardware: watchdog behavior, failsafe paths, sensor-dropout
handling, init-order assumptions, and what happens if [subsystem]
is slow or absent. Prioritize by what could destroy the aircraft,
then fix the top 3.
```

### The "concurrency audit" move
```
Audit this for data races and priority inversions across these
threads/tasks: [list]. Show me the shared state, who writes it,
and where a lock is missing or held too long on the hot path.
```

---

## 16. Learning a Hard Concept (Without Outsourcing Understanding)

For the genuinely hard stuff — Lie algebra for attitude, MPC, factor graphs —
use the model as a relentless tutor, not an answer key.

### The "Feynman gauntlet" move
```
I want to truly understand [concept]. Teach it in four passes:
(1) the intuition with one physical analogy,
(2) the math, derived, not stated,
(3) a worked numeric example I can check by hand,
(4) quiz me with 3 questions that expose fake understanding —
    wait for my answers, then grade them harshly and fill gaps.
```

### The "compare the approaches" move
```
For [problem], compare [approach A] vs [approach B] vs [C] on:
assumptions, compute cost, failure modes, and when each is the
right call in a flight stack. Give me the one-line heuristic for
choosing, and the trap of each.
```

### The "from paper to code to intuition" move
```
Here's a paper/algorithm: [link or paste]. Give me (1) the core
idea in plain language, (2) the one equation that does the real
work, (3) a minimal reference implementation, and (4) the assumption
that, if violated, makes the whole thing fail. Then quiz me on (4).
```

Pair these with the deliberate-practice cadence in
[02-ten-year-mastery-plan.md](02-ten-year-mastery-plan.md): the AI accelerates the
loop, but the *re-derivation* is what writes it to memory.

---

## 17. Red-Teaming a Design

Before you commit to an architecture, make the model attack it harder than any
reviewer will.

### The "pre-mortem" move
```
It's 12 months from now and my [autonomy architecture] failed
catastrophically in the field. Write the incident report explaining
what went wrong and why — the most likely failure, not the dramatic
one. Then turn each cause into a design change I should make now.
```

### The "adversary's playbook" move
```
You are an adversary trying to defeat this [counter-UAS / nav]
system. Given its design, how would you spoof, jam, saturate, or
deceive it? Rank your attacks by ease and impact. Then tell me the
cheapest mitigations that close the biggest gaps.
```
*(See [27-autonomy-counter-uas-ew.md](27-autonomy-counter-uas-ew.md).)*

### The "what breaks at the boundary" move
```
List every assumption this design makes about its inputs, timing,
environment, and hardware. For each, tell me what happens the moment
it's violated, and whether the failure is safe, recoverable, or fatal.
```

---

## 18. Prompt Patterns — A Compact Taxonomy

Once you see the *patterns*, you stop collecting prompts and start composing them.
Every effective prompt is one or more of these:

| Pattern | What it does | Canonical trigger |
|---|---|---|
| **Role assignment** | Selects the standards/vocabulary the model applies | "Act as a flight-controls engineer…" |
| **Plan-then-act** | Separates design from implementation | "Don't code yet. Write the plan first." |
| **Reverse-prompt** | Loads *your* constraints into context | "Ask me the questions that change your approach." |
| **Constraint stack** | Bounds the solution space explicitly | "Must NOT change X; optimize for Y." |
| **Self-critique loop** | Trades one good pass for two | "Critique your answer, then rewrite it." |
| **Verification framing** | Separates knowledge from guessing | "Mark each claim [verified]/[uncertain]." |
| **Few-shot priming** | Shows the target shape | "Here are 2 examples; produce a third." |
| **Persona panel** | Surfaces trade-offs via disagreement | "Three experts who disagree, then synthesize." |
| **Output contract** | Forces a parseable shape | "Respond ONLY in this format…" |
| **Inversion / pre-mortem** | Finds failure before it happens | "How would this most likely fail?" |

**Composition is the skill.** A great working prompt is often *role + constraint
stack + plan-then-act + verification* fused into one. The libraries above are just
common, useful fusions.

---

## 19. Pitfalls & Anti-Patterns

The failure modes that quietly cost you the most:

- **Accepting confident prose as fact.** Fluency is not accuracy. Always pair a
  claim with a verification path — especially for numbers, APIs, and physics.
- **Hallucinated APIs / functions.** Models invent plausible-looking calls. For
  any library function, confirm it exists before you build on it.
- **Letting it own the fundamentals.** The Section 12 trap: shipping code you
  can't re-derive. On hardware, this is a latent crash.
- **Stale knowledge.** A model's training has a cutoff; framework behavior,
  PX4 params, and ROS 2 APIs drift. Treat anything version-specific as a
  hypothesis to check against current docs.
- **Context rot in long threads.** After many turns the model loses the thread —
  re-state the goal and constraints, or start a clean thread with a tight summary.
- **Over-trusting a single pass.** One greedy answer is the weakest mode the model
  has. Critique-and-revise (Section 4) is nearly free and almost always better.
- **Prompt-injection from pasted content.** If you paste logs, web text, or files,
  hostile instructions inside them can hijack the model. Treat pasted content as
  *data to analyze*, not commands to follow — and say so in the prompt.
- **Outsourcing judgment.** The model proposes; *you* decide. Architecture, safety
  trade-offs, and what's "good enough to fly" are yours to own.

---

## 20. Cross-Links

- [02-ten-year-mastery-plan.md](02-ten-year-mastery-plan.md) — the principle this file serves: AI accelerates, never replaces, understanding.
- [22-autonomy-px4-sitl.md](22-autonomy-px4-sitl.md) / [23-autonomy-onboard-system.md](23-autonomy-onboard-system.md) — the stack the domain prompts target.
- [24-autonomy-test-scaffold.md](24-autonomy-test-scaffold.md) — turning the AI's tests into a real harness.
- [25-autonomy-control-theory.md](25-autonomy-control-theory.md) / [28-autonomy-gnc.md](28-autonomy-gnc.md) — the fundamentals you must own, not outsource.
- [12-career-software-engineering.md](12-career-software-engineering.md) / [17-career-interview-prep.md](17-career-interview-prep.md) — where "can you explain what you built?" gets tested.

---

## Sources & Citations

**Foundational papers (mechanisms behind the moves)**
- Wei et al. — *Chain-of-Thought Prompting Elicits Reasoning in LLMs* (arXiv:2201.11903).
- Wang et al. — *Self-Consistency Improves Chain-of-Thought Reasoning* (arXiv:2203.11171).
- Brown et al. — *Language Models are Few-Shot Learners* (GPT-3, arXiv:2005.14165).
- Yao et al. — *ReAct: Synergizing Reasoning and Acting in LLMs* (arXiv:2210.03629).
- Kojima et al. — *Large Language Models are Zero-Shot Reasoners* ("let's think step by step", arXiv:2205.11916).
- Madaan et al. — *Self-Refine: Iterative Refinement with Self-Feedback* (arXiv:2303.17651).
- Bai et al. — *Constitutional AI* (self-critique framing, arXiv:2212.08073).

**Practical guides (vendor-authoritative)**
- OpenAI — Prompt engineering guide: https://platform.openai.com/docs/guides/prompt-engineering
- Anthropic — Prompt engineering overview: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview
- Google — Prompting guidance: https://ai.google.dev/gemini-api/docs/prompting-intro
- *Prompt Engineering Guide* (community): https://www.promptingguide.ai
- OWASP — *Top 10 for LLM Applications* (prompt injection & related risks): https://owasp.org/www-project-top-10-for-large-language-model-applications/

*Techniques generalize across current frontier models, but exact behavior varies by model and version — test prompts against the model you actually use.*
