# Edge Inference & Onboard Deployment — Running Models on Power-Constrained Hardware

> **Why this exists.** Every chapter in this band produces a model — a detector, a VIO front-end, a VLA policy — and none of them matter if they can't run *on the robot*, in real time, within a power and thermal budget that a battery and a small heatsink can sustain. The cloud is not an option when a drone is in a GPS-denied tunnel, when a missile has 50 ms to decide, or when a self-driving car cannot gamble its passengers' lives on an LTE link. Edge inference is the unglamorous, decisive discipline of taking a model that was trained on a 700-watt datacenter GPU and making it run on a 15-watt embedded module — faster, smaller, and *deterministically* — without losing the accuracy that justified building it. This is where machine learning meets the brutal physics of milliamps, milliseconds, and millijoules.
>
> **What mastering it makes you.** The engineer who can take any model and answer, with numbers, "will this run on our hardware inside our latency and power budget?" — and then make it true through quantization, pruning, and ruthless systems engineering.

Edge deployment is the final, mandatory stage for every learned component in this curriculum: the vision of [20-autonomy-computer-vision.md](20-computer-vision.md), the point-cloud nets of [21-autonomy-lidar-radar-processing.md](21-lidar-radar-processing.md), the VIO of [22-autonomy-visual-inertial-odometry.md](22-visual-inertial-odometry.md), and the foundation models of [24-autonomy-foundation-models-robotics.md](24-foundation-models-robotics.md) all bottleneck here. It realizes the training of [01-autonomy-ml-ai.md](01-ml-ai.md) on real silicon, enforces the real-time guarantees the control loops of [09-autonomy-gnc.md](09-gnc.md) and planners of [10-autonomy-planning-decision.md](10-planning-decision.md) depend on, lives inside the onboard architecture of [04-autonomy-onboard-system.md](04-onboard-system.md), and rests on the numerical foundations of [03-foundations-mathematics.md](../foundations/03-mathematics.md) and the real-time systems craft of [04-foundations-modern-cpp-realtime.md](../foundations/04-modern-cpp-realtime.md).

---

## 1. The Constraints That Define the Problem

Onboard deployment is an optimization under hard physical constraints. The objective is to meet an accuracy floor while satisfying *all* of:

| Constraint | Why it bites | Typical edge target |
|---|---|---|
| **Latency** | Control loops have deadlines; late = unstable | < 10–50 ms per inference |
| **Throughput** | Sensor frame rate must be kept up with | 30–200 Hz |
| **Power** | Battery life, thermal limits | 5–30 W for the whole compute |
| **Memory** | Embedded RAM is tiny vs. datacenter | 4–32 GB, often shared |
| **Determinism** | Safety needs *bounded worst-case* latency | jitter-bounded, not just fast-on-average |
| **Thermal** | Throttling silently destroys performance | sustained, not peak |

The defining tension: a model is judged in the datacenter by **average accuracy**; it is judged on the robot by **worst-case latency at a fixed power and accuracy floor**. These are different objectives, and the gap between them is the entire discipline.

```
   DATACENTER MODEL                EDGE-DEPLOYED MODEL
   ┌──────────────────┐  compress  ┌──────────────────┐
   │ FP32, 7B params  │ ─────────► │ INT8, pruned,     │
   │ 700 W, ~unlimited│            │ fused, 15 W,      │
   │ latency flexible │            │ 8 ms p99, bounded │
   └──────────────────┘            └──────────────────┘
   accuracy: 100%                  accuracy: ~99% (the goal: lose almost none)
```

---

## 2. Quantization — The Highest-Leverage Tool

Models train in 32-bit float (FP32) but rarely *need* that precision to run. **Quantization** maps weights and activations to low-bit integers (INT8, INT4) or low-bit floats (FP16, BF16, FP8), shrinking memory ~4× and accelerating math 2–4× on hardware with integer/tensor cores — usually with negligible accuracy loss.

The affine INT8 mapping from a real value $r$ to an integer $q$:
$$q = \operatorname{round}\!\left(\frac{r}{s}\right) + z, \qquad r \approx s\,(q - z)$$
where $s$ (scale) and $z$ (zero-point) are chosen per-tensor or per-channel from the observed value range $[r_{min}, r_{max}]$:
$$s = \frac{r_{max} - r_{min}}{q_{max} - q_{min}}, \qquad z = q_{min} - \operatorname{round}\!\left(\frac{r_{min}}{s}\right)$$

A quantized matmul runs in integer arithmetic and rescales once at the end — far cheaper in energy and silicon than float. Two regimes:

- **Post-Training Quantization (PTQ):** quantize a trained model directly. Needs a small **calibration set** to estimate activation ranges. Fast, no retraining; may lose accuracy on sensitive models. **GPTQ/AWQ** are advanced PTQ methods for LLMs/VLAs.
- **Quantization-Aware Training (QAT):** simulate quantization *during* training (fake-quant nodes), letting the network learn to compensate. Recovers most accuracy, especially at INT4; costs a retraining run.

| Precision | Memory vs FP32 | Speed | Accuracy risk | Use |
|---|---|---|---|---|
| FP16 / BF16 | 2× smaller | ~2× | negligible | safe default on GPU |
| INT8 | 4× smaller | 2–4× | small (calibrate well) | production edge standard |
| INT4 | 8× smaller | 3–4× | real — use QAT/GPTQ | large models, LLM/VLA |

The single most important practical fact: **quantize, then re-measure accuracy on a representative set.** Quantization error is data-dependent; a model that's fine on average can degrade badly on the rare, safety-critical input — exactly the boundary case the house testing discipline targets.

---

## 3. Pruning & Sparsity — Removing What's Unused

Trained networks are over-parameterized; many weights contribute nothing. **Pruning** removes them.

- **Unstructured pruning** zeros individual weights (those with smallest magnitude). Achieves high sparsity but yields irregular matrices that most hardware can't accelerate — a "fast" sparse model that runs slowly because the GPU still touches every element.
- **Structured pruning** removes whole channels, filters, attention heads, or layers. Lower max sparsity but produces a *smaller dense* model that runs faster on real hardware. This is what ships.
- **Hardware-aware sparsity**: NVIDIA's **2:4 structured sparsity** (2 of every 4 weights zero) is accelerated natively by Ampere+ tensor cores — a sweet spot of sparsity the silicon actually rewards.

The iterative recipe: train → prune the least-important structures → fine-tune to recover accuracy → repeat. The **lottery-ticket** insight (Frankle & Carbin) is that dense networks contain sparse subnetworks that train to comparable accuracy — pruning finds them.

```
   prune → fine-tune → prune → fine-tune  (gradual, recovers accuracy)
   ┌────────────────────────────────────────────┐
   │ ████████  full   →  ██_██_██  structured   │
   │ dense filters       pruned filters → smaller│
   └────────────────────────────────────────────┘
```

**Knowledge distillation** is the complementary compression: train a small "student" model to mimic a large "teacher's" soft outputs, transferring accuracy into a cheaper architecture. The loss matches the teacher's softened logits (temperature $T$):
$$\mathcal{L}_{KD} = (1{-}\alpha)\,\mathcal{L}_{CE}(y, \sigma(z_s)) + \alpha\,T^2\,\mathrm{KL}\big(\sigma(z_t/T)\,\|\,\sigma(z_s/T)\big)$$

---

## 4. Graph Optimization & Compilation

Beyond shrinking the model, the *execution graph* is optimized by a compiler. The dominant path:

1. **Export** from PyTorch/TF to **ONNX** (Open Neural Network Exchange) — a portable, framework-agnostic graph.
2. **Compile** with a target-specific optimizer — **TensorRT** (NVIDIA), **ONNX Runtime**, **TVM**, **OpenVINO** (Intel), **CoreML** (Apple), **TFLite** (mobile).

Key graph transformations:
- **Operator fusion:** merge conv+bias+ReLU into one kernel — fewer memory round-trips, the biggest practical speedup. Memory bandwidth, not FLOPs, is usually the bottleneck.
- **Kernel auto-tuning:** pick the fastest implementation for *this* layer shape on *this* GPU (TensorRT profiles and selects).
- **Precision calibration:** fold in INT8/FP16 with per-layer precision choices.
- **Memory planning:** reuse buffers across the graph to fit tight RAM.
- **Constant folding & dead-code elimination.**

```
   PyTorch model
        │ torch.onnx.export
        ▼
   ONNX graph ──► TensorRT builder ──► optimized engine (.plan)
                    │ fuse ops          │ INT8/FP16
                    │ tune kernels      │ memory plan
                    │ select precision  ▼
                                   runs at p99 = 8 ms on Jetson
```

The payoff is large and free of accuracy cost — fusion and tuning routinely deliver 2–5× over a naive framework forward pass. *Always* deploy through a compiler; running raw PyTorch onboard leaves most of the hardware on the table.

---

## 5. The Hardware — Knowing Your Silicon

Edge AI runs on a zoo of accelerators, each with a different sweet spot:

| Platform | Type | Power | Robotics use |
|---|---|---|---|
| **NVIDIA Jetson** (Orin/Xavier/Nano) | embedded GPU + tensor cores + DLA | 7–60 W | the default for drones/robots; CUDA + TensorRT |
| **Google Coral / Edge TPU** | INT8 ASIC | ~2 W | ultra-low-power vision |
| **Qualcomm / mobile NPU** | SoC NPU | 1–5 W | phones, lightweight robots |
| **Hailo / specialized NPUs** | dataflow ASIC | 2–5 W | efficient CNN inference |
| **Embedded x86 + GPU / FPGA** | flexible | 15–60 W | larger ground vehicles |

The Jetson family dominates robotics because it pairs a CUDA GPU (runs anything) with **DLA** (deep-learning accelerators for fixed-function efficiency) and tensor cores for INT8/FP16. A key skill is *partitioning* the workload — heavy convs on the GPU, some layers on the DLA, classical CV on the CPU — to maximize total throughput within the shared power envelope. Memory is typically *unified* (shared CPU/GPU RAM), so memory pressure and bandwidth contention, not raw FLOPs, often govern real performance.

---

## 6. Latency Budgets & Determinism

A robot's perception-to-action pipeline has a **latency budget** — a total time from sensor sample to actuator command that the control loop's stability tolerates. Inference is one term in that budget:

$$t_{total} = t_{sense} + t_{preproc} + t_{inference} + t_{postproc} + t_{plan} + t_{actuate} \;\le\; T_{deadline}$$

Two truths follow. First, **inference is rarely the only cost** — preprocessing (resize, normalize, format conversion), memory copies (host↔device), and postprocessing (NMS, decoding) can dominate; profile the *whole* pipeline, not just `model.forward()`. Second, for safety-critical loops what matters is the **worst-case (p99/p100) latency, not the average** — a planner that's 5 ms on average but 80 ms once a second will destabilize a controller during that spike.

**Determinism** is therefore as important as speed. Sources of jitter to hunt and eliminate:
- Dynamic memory allocation in the hot path (pre-allocate everything).
- Garbage collection / Python in the loop (use C++/compiled runtimes for the real-time path — see [04-foundations-modern-cpp-realtime.md](../foundations/04-modern-cpp-realtime.md)).
- Thermal throttling (the GPU silently slows when hot — test sustained, not burst).
- OS scheduling jitter (real-time kernel, CPU affinity, isolated cores).
- Variable-iteration algorithms (NMS, dynamic-shape models) — bound or batch them.

```
   Deadline = 33 ms (30 Hz control)
   ├ sense    2 ┤
   ├ preproc  3 ┤
   ├ infer    8 ┤ ← what we optimized
   ├ postproc 4 ┤
   ├ plan     6 ┤
   ├ actuate  2 ┤
   └ slack    8 ┘  ← margin for p99 spikes; if negative, you WILL miss deadlines
```

---

## 7. The Deployment Workflow End-to-End

A disciplined pipeline from trained model to flight:

```
1. Train (FP32, datacenter)            → baseline accuracy A0
2. Export to ONNX                      → verify numerical parity vs PyTorch
3. Compress:
      PTQ/QAT to INT8/FP16             → accuracy A1, re-measure on rep set
      structured prune + fine-tune     → accuracy A2
      (optional) distill to student    → accuracy A3
4. Compile (TensorRT) on TARGET device → fused, tuned engine
5. Profile on hardware:
      throughput, p50/p99 latency, power, thermal-sustained
6. Validate:
      accuracy on edge == accuracy floor?  latency budget met at p99?
7. Integrate into ROS 2 / onboard stack, close the loop
8. Field-test under real thermal/power/vibration conditions
```

The non-obvious discipline is *re-validating accuracy after every compression step on a representative — ideally safety-weighted — dataset*, and *profiling on the actual target device under sustained thermal load*, never on a desktop GPU. Numbers from the wrong device or a cold chip are fiction.

---

## 8. Testing Edge Deployments

> Per the house testing discipline, edge testing is risk prevention against two silent killers: accuracy quietly lost to quantization on the rare critical input, and latency quietly blown on the worst-case frame. Both pass an "average" test and fail in the field.

| Level | Target | Method |
|---|---|---|
| **Numerical parity** | ONNX/engine matches PyTorch within tolerance | Same inputs, assert output diff < ε |
| **Quantization accuracy** | INT8/INT4 model meets accuracy floor | Re-evaluate on representative + safety-critical set |
| **Latency (worst-case)** | p99/p100 within budget | Profile on target, many frames, report tail not mean |
| **Throughput** | Keeps up with sensor rate | Sustained run at full frame rate |
| **Power / thermal** | Within envelope, no throttle collapse | Long soak test, monitor clocks & temp |
| **Determinism** | Bounded jitter | Measure latency distribution, assert bounded |
| **Integration** | Closed-loop stability with real latency | Hardware-in-the-loop, sim ([23-autonomy-sim-to-real.md](23-sim-to-real.md)) |
| **Exploratory** | Inputs that blow latency or accuracy | Adversarial-shape / worst-case-content mining |

**Boundary cases to force:** the input that produces the *most* detections (max NMS time — worst-case latency), the input where quantization error is largest (often high-dynamic-range or rare-class), a fully thermally-soaked device (post-throttle clocks), a cold-start first inference (engine warm-up is slow), and concurrent load (other processes contending for the unified memory bus). The acceptance criterion is dual and strict: **accuracy floor met on the worst-case input AND p99 latency under deadline on the thermally-soaked target.** Average-case green dashboards mean nothing here.

```python
def test_p99_latency_under_thermal_soak():
    # Risk: model is fast cold but throttles hot, blowing the control deadline.
    engine = load_tensorrt_engine("detector_int8.plan", device="jetson_orin")
    soak_device(minutes=20)                      # reach sustained thermal state
    lat = [engine.infer(worst_case_frame()).latency_ms for _ in range(2000)]
    p99 = percentile(lat, 99)
    # Acceptance: tail latency, on a HOT device, fits the budget with margin.
    assert p99 < DEADLINE_MS - SAFETY_MARGIN, f"p99={p99} blows deadline when hot"
    # And accuracy must survive INT8 on the safety-critical subset, not just avg.
    assert accuracy(engine, safety_critical_set()) >= ACC_FLOOR
```

---

## 9. The Practical Stack

- **Export / interchange:** **ONNX**, `torch.onnx`, ONNX Runtime.
- **Compilers / runtimes:** **TensorRT** + **TensorRT-LLM** (NVIDIA), **TVM**, **OpenVINO** (Intel), **TFLite** (mobile), **CoreML** (Apple), **Hailo SDK**.
- **Quantization tools:** PyTorch FX/`torch.ao.quantization`, NVIDIA **TensorRT Model Optimizer**, **GPTQ/AWQ** for LLMs, **bitsandbytes**.
- **Profiling:** **Nsight Systems/Compute**, `trtexec`, `tegrastats` (Jetson power/thermal), PyTorch profiler.
- **Hardware:** NVIDIA **Jetson Orin** (robotics default), Google **Coral**, **Hailo**, mobile NPUs.
- **Integration:** **ROS 2** with C++ real-time nodes ([04-foundations-modern-cpp-realtime.md](../foundations/04-modern-cpp-realtime.md)), `isaac_ros` GEMs for accelerated perception.

---

## Sources & further study

- **Jacob et al. (2018), "Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference"** — the foundational INT8 paper.
- **Han, Mao & Dally (2016), "Deep Compression"** — pruning + quantization + Huffman coding, the classic.
- **Frankle & Carbin (2019), "The Lottery Ticket Hypothesis."**
- **Hinton, Vinyals & Dean (2015), "Distilling the Knowledge in a Neural Network."**
- **Frantar et al. (2023), "GPTQ"** and **Lin et al. (2023), "AWQ"** — LLM/VLA quantization.
- **NVIDIA TensorRT & Jetson developer documentation; Nsight Systems profiling guides.**
- **Sze, Chen, Yang & Emer (2017), "Efficient Processing of Deep Neural Networks: A Tutorial and Survey,"** *Proc. IEEE* — the systems-level survey.
- **MLPerf Inference / MLPerf Tiny** benchmarks for edge performance methodology.

> Framing note: Edge inference is where machine-learning ambition meets the unforgiving arithmetic of a battery and a heatsink. The model that wins a benchmark in the cloud is not the model that flies — the model that flies is the one that survives quantization without losing the rare critical case, fits the latency budget at its hottest and slowest, and never jitters past a deadline. Master this and you become the person who turns research into something that actually leaves the ground; neglect it and the smartest autonomy in the world stays stranded on a desktop GPU.

---

## ⚡ The Insider Layer — What the Field Knows but Rarely Writes Down

The quantization papers report top-1 accuracy and the vendor slides quote TOPS. Neither prepares you for the afternoon your INT8 model still recalls cars at 99% but drops night-time pedestrians, or the week your demo was fast on the bench and throttled to half speed inside the airframe.

### You are memory-bandwidth bound, not compute bound

The most useful mental model on the edge is the **roofline**: plot achievable performance against *operational intensity* (FLOPs per byte moved). At batch=1 — which is every real-time robot — inference is almost always **memory-bandwidth bound**, dominated by the time to stream weights from DRAM, not by the multiply-accumulates. This reframes everything: you quantize INT8/FP16 primarily to move *fewer bytes*, not to do cheaper math, and a model with fewer parameters can beat a model with fewer FLOPs. If you optimize FLOPs while ignoring bytes, you'll "speed up" a network and see no wall-clock improvement, then wonder why.

### Quantization protects average accuracy and can quietly murder the tail

Post-training INT8 with a good calibration set is usually fine for CNNs — *usually*. The trap is that aggregate accuracy can stay flat while the **rare safety-critical class collapses**: the pedestrian-at-night recall, the small-distant-object AP. Always evaluate quantization on the tail metric you actually care about, not top-1. Two more hard-won facts: the **calibration set must be representative** of deployment (calibrate on daytime, deploy at night, and you've built a cliff), and **transformers/LLMs/VLAs don't PTQ cleanly** because of outlier activation channels — you need per-channel schemes or SmoothQuant/AWQ/GPTQ, and you keep softmax, LayerNorm, and often the final layer in higher precision. On Jetson, reach for **FP16 first**: it's a near-free 2× with negligible accuracy loss and none of INT8's calibration drama.

### Thermal throttling is the benchmark you didn't run

The single most common way an edge demo lies is **peak vs. sustained**. The first 30 seconds run at full clocks; then the SoC hits its thermal limit and silently down-clocks, and your 30 ms inference becomes 60 ms — exactly when the mission is longest. **Benchmark at thermal steady state, inside the real enclosure, at the real ambient temperature**, not on the bench with a desk fan. Lock power mode (`nvpmodel`) and clocks (`jetson_clocks`) so you're measuring a defined operating point, and report the throttled number as the real one. A heatsink and airflow are part of the inference pipeline.

### The p99.9, not the mean, is what the control loop feels

Safety lives in the worst case. Average latency is a marketing number; a control loop that misses its deadline at the 99.9th percentile is an unstable control loop. **Jitter** comes from page faults, the CPU frequency governor, preemption by other processes, and garbage-collected runtimes. The countermeasures are systems hygiene, not ML: lock pages in memory (`mlock`), pin and isolate CPUs (`isolcpus`, thread affinity), pre-allocate everything, avoid the GIL in the hot path, and consider an RT kernel. Profile with **Nsight Systems**, never a Python `time.time()` — the latter measures the interpreter, not the GPU.

### Pruning underdelivers; distillation overdelivers

The lottery-ticket literature is beautiful and **unstructured pruning rarely buys real speed**, because commodity hardware can't exploit scattered zeros — you need structured sparsity the silicon actually supports (e.g., Ampere's 2:4) to see wall-clock gains. In practice **knowledge distillation** is the more reliable compressor: train a small student to mimic a big teacher and you often keep more accuracy per millisecond than pruning the big one. Structured channel pruning works, but budget time to fine-tune back the lost accuracy.

### Trust nothing until you validate after conversion

The phrase every edge engineer learns to fear: "it matches in PyTorch but TensorRT gives different outputs." Layer fusion, reduced-precision accumulation, and kernel autotuning all perturb numerics, and a **TensorRT engine is built for one specific GPU/driver — it does not transfer** between Jetson models, so build on target. Custom ops drag you into plugin hell. The non-negotiable habit: after every export/conversion, run an **end-to-end numerical diff** on a held-out set and gate on the tail metric. The model that flies is the one you re-verified on the silicon it will actually fly on — at its hottest, slowest, and most jittery.
