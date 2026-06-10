# Foundation Models for Robotics — VLA Models, LLMs as Planners & End-to-End Policies

> **Why this exists.** For decades robot autonomy was a tower of hand-engineered modules — perception, mapping, planning, control — each painstakingly tuned for a narrow domain. Foundation models threaten to collapse that tower. A single large network pretrained on internet-scale vision, language, and (increasingly) robot data can be prompted to perceive, reason, plan, and even *act* across tasks it was never explicitly programmed for. Vision-Language-Action (VLA) models take a camera image and a natural-language instruction and output motor commands. LLMs decompose "make me a coffee" into executable subgoals. This is the most disruptive shift in robotics since deep learning — and also the most dangerous, because these models are confident, opaque, and prone to hallucinate actions with no physical grounding. Mastering this band means harnessing their generality while ruthlessly bounding their failure modes.
>
> **What mastering it makes you.** The engineer who can wire a foundation model into a real robot's control loop *safely* — extracting its open-world generalization while keeping a verifiable safety layer between its hallucinations and the actuators.

Foundation models for robotics sit at the apex of the autonomy stack, consuming the perception of [20-autonomy-computer-vision.md](20-computer-vision.md) and [11-autonomy-perception-deep.md](11-perception-deep.md), subsuming or replacing parts of the planning of [10-autonomy-planning-decision.md](10-planning-decision.md), and commanding the control of [09-autonomy-gnc.md](09-gnc.md). They are the cutting edge of the learning lineage in [01-autonomy-ml-ai.md](01-ml-ai.md), are pretrained and validated through the sim-to-real methods of [23-autonomy-sim-to-real.md](23-sim-to-real.md), and must be compressed to run onboard via [25-autonomy-edge-inference-deployment.md](25-edge-inference-deployment.md). Their prompting craft connects to [01-ai-power-prompts.md](../tooling/01-ai-power-prompts.md); their attention math rests on [03-foundations-mathematics.md](../foundations/03-mathematics.md).

---

## 1. What "Foundation Model" Means for a Robot

A foundation model is a large neural network **pretrained on broad data at scale** such that it can be *adapted* (prompted or fine-tuned) to many downstream tasks. For robotics, three lineages matter:

| Model class | Input → Output | Role in the robot |
|---|---|---|
| **LLM** | text → text | High-level task planning, reasoning, code generation |
| **VLM** (vision-language) | image + text → text | Open-vocabulary perception, scene description, affordance grounding |
| **VLA** (vision-language-action) | image + text → **actions** | End-to-end policy: perceive + reason + act in one network |

The radical move is the third: a network that emits *motor commands* directly. The promise is **generalization** — because the model has seen millions of objects and instructions, it can handle a mug it never saw in a kitchen it never visited, something a hand-tuned pipeline cannot. The peril is that it does so with no separable, verifiable reasoning you can audit.

```
   "Pick up the red block and put it in the bowl"
                    │ language instruction
                    ▼
   ┌──────────────────────────────────────────┐
   │     Foundation model (VLA)                │
   │  image tokens + text tokens → transformer │
   │  → discretized action tokens              │
   └──────────────────────────────────────────┘
                    │ Δpose / gripper per step
                    ▼
        Robot executes (under a safety layer)
```

---

## 2. The Transformer Substrate

Every model here is a **transformer**, and its engine is self-attention (shared with chapter 59). Tokens — whether text subwords, image patches, or action chunks — attend to each other:

$$\text{Attention}(Q,K,V) = \operatorname{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V$$

The unification that makes VLAs possible is **tokenizing everything into one sequence**: image patches become visual tokens, the instruction becomes text tokens, and — crucially — *robot actions are discretized into action tokens* (e.g., each of the 7 DoF binned into 256 values). The robot policy then becomes ordinary next-token prediction, training with the same cross-entropy loss as a language model:

$$\mathcal{L} = -\sum_t \log p_\theta(a_t \mid a_{<t}, \text{image}, \text{instruction})$$

This is why a coffee-shop LLM architecture can drive a robot arm: *control is reframed as sequence modeling*. The autoregressive generation of actions inherits both the strengths (in-context flexibility, scale) and the weaknesses (hallucination, no built-in physics) of language models.

---

## 3. LLMs as Planners

The most mature deployment is the **LLM as a high-level planner**: decompose a vague natural-language goal into a sequence of executable skills, where each skill is a pre-built, verified controller (grasp, navigate, place).

- **SayCan** (Google 2022) pairs an LLM's *semantic* score for each candidate skill ("how useful is this skill for the goal?") with a learned *affordance* value ("how likely is this skill to succeed here, right now?"), and picks the skill maximizing the product:
$$a^* = \arg\max_a \; \underbrace{p_{LLM}(a \mid \text{instruction})}_{\text{useful?}} \cdot \underbrace{V_{aff}(a, s)}_{\text{possible?}}$$
This grounds the LLM's suggestions in physical feasibility — the model can't propose grabbing an object that isn't there because the affordance value vetoes it.

- **Code-as-policy** (Code as Policies, ProgPrompt): the LLM writes *executable code* calling perception and control APIs, turning planning into program synthesis with loops, conditionals, and error handling.
- **ReAct / inner-monologue**: interleave reasoning steps with environment feedback, letting the model replan when a step fails.

```
  Instruction: "clear the table"
        │ LLM decomposes (grounded by affordances)
        ▼
   1. detect objects        → perception API
   2. for each object:
        grasp(object)        → skill, vetoed if affordance low
        place(object, bin)   → skill
   3. verify table empty     → perception API, replan if not
```

The architectural virtue: the LLM provides *open-ended reasoning* while the skills provide *verified execution*. The safety layer lives at the skill boundary — the LLM can only invoke vetted primitives, never raw torques.

---

## 4. Vision-Language-Action Models — End-to-End

The frontier collapses perception, planning, and control into one network trained on robot demonstrations:

- **RT-1 / RT-2** (Google): RT-2 co-fine-tunes a large VLM on *both* internet vision-language data and robot trajectories, so web knowledge ("which object is a dinosaur") transfers to manipulation. Actions are output as text tokens.
- **OpenVLA, Octo, RT-X / Open X-Embodiment**: open models trained on the pooled **Open X-Embodiment** dataset (1M+ trajectories across dozens of robots), demonstrating cross-embodiment transfer — one model controlling many different robot bodies.
- **π0 (Physical Intelligence), diffusion policies**: instead of discrete action tokens, model the *continuous* action distribution. **Diffusion Policy** (Chi et al. 2023) generates action sequences by iterative denoising, capturing multimodal behavior (there are many valid ways to grasp) that a single-mode regressor cannot:
$$\mathbf{a}^{k-1} = \mathbf{a}^k - \gamma\,\epsilon_\theta(\mathbf{a}^k, k, \text{obs}) + \mathcal{N}(0, \sigma^2 I)$$
(reverse diffusion over the action chunk, conditioned on observations).

| Model | Action representation | Key idea |
|---|---|---|
| RT-1 | discrete tokens | transformer over image+instruction history |
| RT-2 | discrete tokens | VLM co-trained on web + robot data |
| OpenVLA / Octo | discrete / continuous | open, cross-embodiment, fine-tunable |
| Diffusion Policy / π0 | continuous (denoising) | multimodal action generation |

The payoff is **data-driven generalization** to novel objects and instructions. The cost is enormous data appetite, opacity, and latency — a 7B-parameter VLA running at a few Hz is a real constraint on a fast robot (chapter 64).

---

## 5. Affordances & Grounding

The bridge between language and action is **grounding**: connecting the symbol "handle" to the *pixels* of a handle and the *motor primitive* of grasping it. An **affordance** is what an object offers an agent to do — a handle affords grasping, a button affords pushing.

VLMs ground language to regions via open-vocabulary detection/segmentation (**Grounding DINO**, **SAM**, **OWL-ViT**): given the phrase "the blue cup," return the mask. Affordance models go further, predicting *where and how* to interact — grasp points, contact regions, pushing directions. This grounding is what keeps a foundation-model planner tethered to physical reality: the language model proposes, the grounded perception disposes.

The failure of grounding is the failure of the whole stack: if the model confidently grounds "the apple" onto a red ball, it will execute a perfectly-formed grasp of the wrong object. Grounding errors are *silent and confident* — the hallmark danger of this entire band.

---

## 6. Limitations & Why They're Dangerous

Foundation models in the control loop carry failure modes that are categorically different from classical autonomy, and a master engineer must hold them front-of-mind:

- **Hallucination as action.** An LLM that invents a plausible-sounding but false fact is annoying in chat; a VLA that confidently emits a plausible-but-wrong motor command is dangerous. There is no native uncertainty calibration on the action.
- **No physics guarantee.** The model has no built-in notion of dynamics, collision, or constraint satisfaction. It can output a trajectory that violates joint limits or drives into a wall.
- **Distribution shift.** Performance degrades, often silently, outside the training distribution — a new lighting condition, a novel object, an unusual instruction phrasing.
- **Opacity.** You cannot inspect *why* it chose an action; classical planners expose a cost and a search tree, VLAs expose a logit.
- **Latency & compute.** Billion-parameter models are slow; a safety-critical loop cannot wait 300 ms for an action.
- **Prompt injection / adversarial inputs.** A malicious instruction or a doctored image can hijack behavior — a genuine security surface on a physical machine.

```
   ┌──────────────────────────────┐
   │ Foundation model (powerful,  │   proposes action a_t
   │ general, but UNTRUSTED)       │
   └──────────────┬───────────────┘
                  │ a_t
        ┌─────────▼──────────┐
        │ SAFETY LAYER       │  ← classical, verifiable
        │ • collision check  │
        │ • constraint/limit │   veto or project a_t into safe set
        │ • CBF / reachability│
        │ • runtime monitor  │
        └─────────┬──────────┘
                  │ a_t^safe
                  ▼  actuators
```

**The architectural principle:** treat the foundation model as a *powerful but untrusted advisor*, never as the final authority. A classical, verifiable safety layer — collision checking, joint-limit clamping, control-barrier functions, reachability-based filtering, runtime monitors — sits between the model and the actuators and has veto power. This mirrors the safety-assurance discipline of [09-foundations-safety-assurance.md](../foundations/09-safety-assurance.md): the generality lives in the untrusted layer; the guarantees live in the trusted one.

---

## 7. Testing Foundation-Model Robots

> Per the house testing discipline, testing here is overwhelmingly *risk prevention*: the model will generalize impressively and then fail catastrophically and confidently, so the test regime must hunt the confident failure, not celebrate the average success.

| Level | Target | Method |
|---|---|---|
| **Unit** | Tokenization, action decoding, safety-layer veto logic | Deterministic checks on each component |
| **Grounding** | Correct object/region grounding | Open-vocab benchmarks; assert correct mask for instruction |
| **Skill** | Each primitive controller in isolation | Classical skill validation (it's verifiable) |
| **Closed-loop sim** | End-to-end task success across scenes | Isaac Sim / sim suites, many seeds/objects |
| **Safety layer** | Veto fires on every unsafe proposal | Inject unsafe model outputs; assert they're blocked |
| **OOD / adversarial** | Behavior on novel objects, phrasings, prompt injection | Distribution-shift suites, adversarial prompts/images |
| **Acceptance** | Mission success *with zero safety violations* | Statistical task suite; safety violations are hard fails |
| **Exploratory** | Discover hallucinated-action triggers | Red-teaming the model in the loop |

**Boundary cases to force:** instructions referencing absent objects (does it hallucinate a grasp or abstain?), ambiguous instructions ("the cup" when two are present), out-of-distribution objects, adversarial/injected instructions, and model outputs that violate joint limits or collide. The **non-negotiable acceptance criterion**: a safety violation is a *hard failure regardless of task success* — a robot that completes the task while almost crushing a hand has failed. Frame the safety layer's test coverage as the primary deliverable; the model's task performance is secondary to the guarantee that its mistakes never reach the actuators.

```python
def test_safety_layer_vetoes_hallucinated_grasp():
    # Risk: model confidently commands a grasp toward empty space / a person.
    obs = scene_with_no_target()                 # the named object is absent
    action = vla_model(obs, instruction="pick up the red block")
    safe_action = safety_layer(action, obs)      # classical, verifiable filter
    # Acceptance: the unsafe/ungrounded action is blocked, not executed.
    assert safety_layer.was_vetoed(action), "hallucinated action reached actuators"
    assert safe_action in {NO_OP, ABSTAIN}       # robot holds, asks, or stops
```

---

## 8. The Practical Stack

- **LLM/VLM planners:** GPT-4o / Claude / Gemini class models via API, open models (Llama, Qwen-VL); **SayCan**, **Code as Policies**, **Inner Monologue** as orchestration patterns.
- **VLA models:** **RT-2**, **OpenVLA**, **Octo**, **π0**, **Diffusion Policy** — most have open weights and fine-tuning code.
- **Grounding:** **Grounding DINO**, **SAM / SAM2**, **OWL-ViT**, **CLIP** for open-vocabulary perception.
- **Data:** **Open X-Embodiment**, **DROID**, **RT-X** datasets; collected via teleoperation and sim ([23-autonomy-sim-to-real.md](23-sim-to-real.md)).
- **Infra:** PyTorch + Hugging Face; **TensorRT-LLM / ONNX** for onboard serving ([25-autonomy-edge-inference-deployment.md](25-edge-inference-deployment.md)); ROS 2 for the safety layer and skill execution.

---

## Sources & further study

- **Bommasani et al. (2021), "On the Opportunities and Risks of Foundation Models"** — the term-defining report.
- **Ahn et al. (2022), "Do As I Can, Not As I Say: Grounding Language in Robotic Affordances" (SayCan).**
- **Brohan et al. (2022/2023), "RT-1" and "RT-2: Vision-Language-Action Models."**
- **Open X-Embodiment Collaboration (2023), "Open X-Embodiment: Robotic Learning Datasets and RT-X Models."**
- **Kim et al. (2024), "OpenVLA: An Open-Source Vision-Language-Action Model."** **Octo Team (2024), "Octo."** **Black et al. (2024), "π0."**
- **Chi et al. (2023), "Diffusion Policy: Visuomotor Policy Learning via Action Diffusion,"** RSS.
- **Liang et al. (2023), "Code as Policies."** **Huang et al. (2022), "Inner Monologue."**
- **Vaswani et al. (2017), "Attention Is All You Need"** — the transformer foundation.

> Framing note: Foundation models give robots something they never had — open-world common sense and the ability to be *told* what to do in plain language. But they give it wrapped in confident opacity, with no native sense of physics or its own ignorance. The mature engineer is neither a skeptic who dismisses the generality nor an enthusiast who pipes logits to motors. They build a two-layer machine: an untrusted genius proposing, a trusted guardian disposing — and they spend their hardest engineering not on the genius, but on the guardian.

---

## ⚡ The Insider Layer — What the Field Knows but Rarely Writes Down

The demo reels are dazzling and the success rates in the tables are real — for the tasks, objects, and camera angles that were tested. Behind the excitement is a field that knows its own bottlenecks intimately and rarely foregrounds them in the abstract.

### The data wall is the whole game

Language models scaled because the internet is a free corpus of text. Robotics has no such corpus — **there is almost no internet-scale robot *action* data**, and the action you need (joint torques, gripper commands, contact events) is not lying around to be scraped. Open X-Embodiment stitched together demonstrations across dozens of labs and embodiments, but it is heterogeneous in robot, action space, camera, and frequency, which makes it powerful and messy at once. The real bottleneck is **teleoperation**: every hour of training data costs an hour of a human driving a robot, and that does not scale like a web crawl. When you read "foundation model for robotics," read "a model starved for the one modality it most needs." Whoever solves scalable action-data collection — sim, play data, human video with learned embodiment transfer — wins the decade.

### Latency forces an architecture, and that architecture is action chunking

A 7B-parameter VLA runs at a handful of hertz; a stable controller needs hundreds. You cannot close a 100 Hz loop on a model that thinks five times a second. The field's answer is **action chunking**: the big model emits a *sequence* of future actions (a chunk) at low frequency, and a fast, dumb low-level controller executes/interpolates them. This isn't just a performance hack — chunking also reduces the compounding error of single-step prediction and smooths the multimodal jitter of token-by-token decoding (the insight behind ACT and Diffusion Policy). If you architect a VLA as a per-timestep oracle, you will be defeated by latency before you reach the lab.

### Diffusion vs. tokenized policies — the field hasn't converged

Two camps, both legitimate. **Tokenized autoregressive** policies (RT-2 lineage) discretize actions into tokens and reuse the entire LLM/VLM stack and its web-scale pretraining — cheap to build on, but discretization is coarse and decoding multimodal actions is awkward. **Diffusion policies** model the action distribution directly, handle multimodality (several valid ways to do a task) gracefully, and produce smooth trajectories — but add denoising compute and lose the clean reuse of language pretraining. Picking one is a real engineering decision with no settled winner; treat anyone who tells you it's obvious with suspicion.

### Generalization is real but oversold, and the failure modes are mundane

The headline claim is open-world generalization; the field-tested reality is that success rates on genuinely novel objects, scenes, and **camera viewpoints** are modest and brittle. Move the camera 20 cm, add a distractor object, change the lighting, and watch the number fall. Most deployed systems quietly **fine-tune on a few hundred in-domain demonstrations** (often with LoRA) rather than running zero-shot — zero-shot is largely a paper posture. And the evaluation situation is a genuine crisis: there is no standard physical benchmark, real-robot eval is slow and irreproducible, and every group reports different tasks, so cross-paper number comparisons are close to meaningless. Be the engineer who runs their own eval on their own robot.

### Hallucinated affordances and why LLM-as-planner deploys first

These models will **confidently emit an action for something they cannot actually do** — grasp an object that's out of reach, "open" a drawer that's locked — because they have no native grounding in physics or their own capability. The conceptual fix (SayCan) is to multiply the model's *semantic* proposal by a learned *value/affordance* estimate of whether it can be executed now: say what's helpful **and** feasible. This is why, in 2025-era practice, the **LLM-as-planner** pattern (decompose language into a sequence of *verified* skill primitives, à la SayCan / Code as Policies) is more deployable than end-to-end VLA: the language layer is auditable text you can read and gate, and the skills underneath are tested code with their own safety envelopes.

### The product is the guardian, not the genius

The hard, unsexy engineering — and the thing that separates a viral clip from a fielded system — is the **safety layer between the model and the actuators**: workspace and joint limits, force/torque ceilings, collision checking, watchdog timeouts, and a human-reachable e-stop. Never pipe logits to motors. Budget your best people for the runtime monitor that catches the confident hallucination before it reaches the world; the foundation model is the easy half to integrate.
