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

*Techniques generalize across current frontier models, but exact behavior varies by model and version — test prompts against the model you actually use.*
