# Performance Engineering — Measuring, Profiling & Making Code Fast

> **Why this exists.** In autonomy and defense, performance is not a vanity metric — it is the boundary between a system that works and one that fails. A perception pipeline that runs at 8 Hz instead of 30 Hz cannot track a fast-moving target; a planner that takes 200 ms instead of 20 ms hands the vehicle a stale world; a control loop that misses its deadline because of a cache miss can destabilize a maneuver. Yet most "optimization" is superstition: engineers rewrite code they *guess* is slow, chasing intuitions that are wrong far more often than right, while the real bottleneck sits untouched. Performance engineering replaces guessing with measurement — a rigorous, repeatable discipline of profiling, understanding the machine, and changing only what the data tells you to. This module makes you the engineer who can take a system that misses its deadline and make it hit, and *prove* why.

> **What mastering it makes you.** The person who looks at a flamegraph and immediately sees where the time goes, who knows whether a loop is bound by compute, memory, or branch mispredictions, and who can make code 10× faster by changing data layout rather than rewriting logic. Performance fluency is leverage: it lets a small team run real-time autonomy on hardware a budget can afford.

Performance engineering is where the compiler knowledge of [91-software-compilers-and-languages.md](91-software-compilers-and-languages.md) and the real-time discipline of [04-foundations-modern-cpp-realtime.md](04-foundations-modern-cpp-realtime.md) become quantitative. It is the production-time complement to the observability of [88-software-observability-and-sre.md](88-software-observability-and-sre.md) — the same "measure, don't guess" ethic applied to a single process rather than a fleet. The systems decomposition of [01_first_principles_systems_engineering.md](01_first_principles_systems_engineering.md) tells you *which* performance matters, and the verification rigor of [06-foundations-simulation-test-verification.md](06-foundations-simulation-test-verification.md) keeps your benchmarks honest. This module sits at the heart of the "Software, Compute & Infrastructure" band and pairs with [90-software-systems-programming-rust.md](90-software-systems-programming-rust.md) (zero-cost abstractions), [64-autonomy-edge-inference-deployment.md](64-autonomy-edge-inference-deployment.md) (squeezing models onto edge hardware), and [89-software-cloud-and-kubernetes.md](89-software-cloud-and-kubernetes.md) (why a service is slow at scale).

---

## 1. The discipline: measure, never guess

The cardinal sin of performance work is optimizing without measuring. Knuth's full quote is sharper than the cliché: *"Premature optimization is the root of all evil (or at least most of it) in programming."* The point is not that optimization is bad — it is that optimizing the wrong thing is worse than useless, because it adds complexity and risk while the real bottleneck remains. The professional loop:

```
   ┌──────────────────────────────────────────────────┐
   │ 1. Define the metric & target (e.g. p99 < 20ms)   │
   │ 2. Measure a representative workload (profile)     │
   │ 3. Find the dominant cost (the bottleneck)         │
   │ 4. Form a hypothesis about WHY                     │
   │ 5. Change ONE thing                                │
   │ 6. Re-measure → keep if it helped, revert if not   │
   └───────────────────────┬──────────────────────────┘
                           └──► repeat until target met
```

Two human biases this loop defeats: we are terrible at predicting bottlenecks (the slow part is almost never where you think), and we conflate "this code looks expensive" with "this code costs us time." The data routinely shows 95% of runtime in 5% of the code — and a different 5% than anyone guessed. Performance is an empirical science; the profiler is your instrument.

---

## 2. Amdahl, Gustafson, and the limits of effort

Before you optimize, know the ceiling. **Amdahl's Law** quantifies the maximum speedup from improving one part of a program. If a fraction $p$ of execution can be sped up by factor $s$, the overall speedup is:

$$ \text{speedup} = \frac{1}{(1 - p) + \dfrac{p}{s}} $$

The brutal implication: if a section is only 20% of runtime ($p = 0.2$) and you make it *infinitely* fast ($s \to \infty$), total speedup is capped at $\frac{1}{0.8} = 1.25\times$. You cannot optimize your way past the parts you didn't touch. This is why Section 1's step 3 — *find the dominant cost* — is everything: effort spent on a 5% slice can never yield more than ~5%.

The parallel version is identical and explains why throwing cores at a problem stops helping: if 10% of a workload is inherently serial, no number of cores beats $10\times$.

$$ \text{speedup}_{N\text{ cores}} = \frac{1}{(1-p) + \frac{p}{N}} \xrightarrow{N \to \infty} \frac{1}{1-p} $$

**Gustafson's Law** is the optimistic counterweight: as you add cores you usually also grow the *problem size*, and the serial fraction shrinks relative to the larger parallel work — so weak scaling (bigger problems, more cores) fares better than strong scaling (same problem, more cores). The design lesson: minimize the serial fraction (locks, synchronization, sequential setup), because it is the asymptote that bounds everything.

---

## 3. The memory hierarchy — the dominant cost on real hardware

The single most important fact in modern performance engineering: **the CPU is fast and memory is slow, and the gap is enormous.** A modern core executes several instructions per nanosecond, but a main-memory access costs ~100 ns — hundreds of wasted cycles. The hardware hides this with a hierarchy of caches, and your job is to keep data in the fast levels.

| Level | Typical latency | Size | Relative cost |
|---|---|---|---|
| Register | ~0 (in-pipeline) | bytes | 1 |
| L1 cache | ~1 ns (~4 cycles) | 32–64 KB | ~4 |
| L2 cache | ~4 ns (~12 cycles) | 256 KB–1 MB | ~12 |
| L3 cache | ~15 ns (~40 cycles) | 8–32 MB | ~40 |
| Main memory (DRAM) | ~100 ns (~300 cycles) | GBs | ~300 |
| SSD / NVMe | ~100 µs | TBs | ~300,000 |

Memory moves in **cache lines** (typically 64 bytes), not individual bytes — so touching one `int` pulls in its 16 neighbors. This makes **data layout the highest-leverage optimization there is.** Two principles:

- **Spatial locality** — access memory in contiguous, sequential order so each cache line you pay for is fully used and the hardware *prefetcher* can predict and pre-load the next.
- **Temporal locality** — reuse data while it's still hot in cache.

The famous **Array of Structs (AoS) vs. Struct of Arrays (SoA)** choice is this principle made concrete. If you only need positions, AoS wastes most of every cache line on velocity and mass you didn't ask for:

```cpp
// AoS: one cache line load drags along data you don't use this pass.
struct Particle { float x, y, z; float vx, vy, vz; float mass; };  // 28 bytes
std::vector<Particle> world;          // updating only positions wastes ~57% of each line

// SoA: positions are packed; the prefetcher streams them; SIMD-friendly.
struct World {
    std::vector<float> x, y, z;       // a pass over x[] touches only x data
    std::vector<float> vx, vy, vz, mass;
};
```

Switching a hot loop from AoS to SoA routinely yields 2–4× with no algorithmic change — because you stopped paying for cache lines you didn't use. Linked lists and pointer-chasing data structures are slow for the opposite reason: each `->next` is a likely cache miss with no locality. On real hardware, a "worse" big-O algorithm with good locality often beats a "better" one that chases pointers.

---

## 4. Profiling — finding the truth

A profiler tells you where time actually goes. Two families:

- **Sampling profilers** (`perf`, Instruments, `py-spy`) interrupt the program many times per second and record the call stack. Low overhead, statistically accurate for hot paths, safe to run on production-like loads. The default choice.
- **Instrumenting profilers** (Callgrind, tracing) insert counters around every function. Exact call counts but heavy overhead that can distort timing.

On Linux, `perf` is the workhorse, and its output is best consumed as a **flamegraph** — a visualization where width is time spent and the y-axis is stack depth:

```bash
perf record -F 999 -g ./perception_pipeline      # sample at 999 Hz with call graphs
perf script | stackcollapse-perf.pl | flamegraph.pl > profile.svg
```

```
Flamegraph (width = time spent):
┌──────────────────────────────────────────────────────────┐  main
│ ┌──────────────────────────┐ ┌─────────────────────────┐ │
│ │      run_inference        │ │   filter_pointcloud     │ │
│ │ ┌───────────┐ ┌────────┐  │ │ ┌─────────────────────┐ │ │
│ │ │ gemm (52%)│ │softmax │  │ │ │  memcpy (31%) ◄───── HERE
│ │ └───────────┘ └────────┘  │ │ └─────────────────────┘ │ │
└──┴───────────────────────────┴─┴─────────────────────────┴─┘
```

You read a flamegraph by scanning for the *widest plateaus* — the functions consuming the most cumulative time. That `memcpy` eating 31% is your bottleneck, and it is the kind of thing nobody guesses (a redundant buffer copy), which is exactly the point.

Beyond the call graph, **hardware performance counters** reveal *why* a hot function is slow — whether it's compute-bound, memory-bound, or branch-bound:

```bash
perf stat -e cycles,instructions,cache-misses,branch-misses ./pipeline
#  Instructions Per Cycle (IPC): high (>2) = compute-bound; low (<1) = stalled
#  cache-misses: high = memory-bound → fix data layout (Section 3)
#  branch-misses: high = unpredictable branches → restructure or branchless code
```

IPC (instructions per cycle) is the master diagnostic. A low IPC means the CPU is *stalling* — usually waiting on memory — and the fix is data layout, not algorithm. A high IPC with bad performance means you're doing too much work — and the fix is algorithmic. This is the "roofline" intuition: every kernel is bounded by either compute or memory bandwidth, and you optimize against whichever wall you've hit.

---

## 5. Vectorization (SIMD) — doing more per instruction

Modern CPUs have **SIMD** (Single Instruction, Multiple Data) units that apply one operation to a whole vector of values at once — 4, 8, or 16 floats per instruction (SSE, AVX2, AVX-512 on x86; NEON/SVE on ARM). For the data-parallel loops at the core of perception, filtering, and linear algebra, SIMD is a 4–16× multiplier on throughput.

```
Scalar (1 op per instruction):        SIMD AVX (8 floats per instruction):
  a[0] + b[0] → c[0]                    ┌a0 a1 a2 a3 a4 a5 a6 a7┐
  a[1] + b[1] → c[1]                    │ +  +  +  +  +  +  +  + │  ← one instruction
  a[2] + b[2] → c[2]                    └b0 b1 b2 b3 b4 b5 b6 b7┘
  ... (8 instructions)                  = c0 c1 c2 c3 c4 c5 c6 c7
```

Three ways to get it, in order of preference:

1. **Auto-vectorization** — the compiler does it for you if the loop is simple, has no data dependencies between iterations, and the data is laid out contiguously (SoA from Section 3!). Compile with `-O3 -march=native` and verify on godbolt.org that vector instructions (`vaddps`, `vfmadd…`) actually appear. This is why data layout enables SIMD: the optimizer can only vectorize what it can prove is independent and packed.
2. **Intrinsics** — when the compiler won't cooperate, write SIMD by hand with `_mm256_*` (x86) or `vaddq_*` (NEON). Verbose and non-portable but precise.
3. **Portable SIMD libraries** — `std::simd` (Rust nightly), Highway, xsimd — write once, target many ISAs.

```cpp
// Auto-vectorizes cleanly: contiguous, no cross-iteration dependency.
void scale(float* __restrict out, const float* __restrict in, float k, int n) {
    for (int i = 0; i < n; ++i) out[i] = in[i] * k;   // → AVX vmulps, 8/iter
}
// __restrict promises no aliasing, freeing the optimizer to vectorize.
```

The synergy of this module: SoA layout (Section 3) makes data packed and independent → the optimizer (Section on the compiler, [91-software-compilers-and-languages.md](91-software-compilers-and-languages.md)) auto-vectorizes it → SIMD gives 8× → and you *verified* it in the profiler. Each layer enables the next.

---

## 6. Concurrency, contention & Little's Law

When single-core optimization is exhausted, you parallelize — but parallelism has its own failure modes that performance engineering must measure.

- **Lock contention** — threads serializing on a shared mutex destroy scaling (the serial fraction in Amdahl). Measure it; reduce critical sections; prefer per-thread state, sharding, or lock-free structures.
- **False sharing** — two threads writing different variables that happen to share a 64-byte cache line ping-pong the line between cores, silently killing performance. The fix is padding/alignment so hot per-thread variables live on separate lines.
- **NUMA** — on multi-socket machines, memory attached to a remote socket is slower; pin threads and allocate memory locally.

For systems serving requests, **Little's Law** (from [88-software-observability-and-sre.md](88-software-observability-and-sre.md)) is the performance-capacity bridge:

$$ L = \lambda W $$

Concurrency in flight ($L$) equals arrival rate ($\lambda$) times latency ($W$). It tells you the thread-pool or async-task count a target throughput requires, and it reveals the trap of *throughput vs. latency*: batching raises throughput but raises $W$; if your deadline is on $W$ (a control loop), you cannot batch your way to it. Real-time systems optimize tail latency (p99/p99.9), not average — because the deadline you must hit is the worst case, not the typical one. Tail-latency thinking is the same instinct as Section 1's metric discipline: pick the number that maps to the actual requirement.

---

## 7. Benchmarking discipline — keeping the numbers honest

A wrong benchmark is worse than none, because it gives false confidence. The hazards and their fixes:

| Hazard | Why it lies | Fix |
|---|---|---|
| **Cold cache / warm-up** | First runs include JIT, page faults, cold caches | Discard warm-up iterations; report steady state |
| **Dead-code elimination** | The optimizer deletes your benchmark if the result is unused | Consume the result (`black_box`) so it can't be optimized away |
| **Measurement noise** | Frequency scaling, other processes, thermal throttling | Pin CPU frequency, isolate cores, many samples, report distribution |
| **Unrepresentative input** | Toy data has different cache behavior than production | Benchmark on realistic sizes and access patterns |
| **Reporting the mean** | The mean hides multimodal and tail behavior | Report median + p99 + variance, not just average |

Use a real harness — `criterion` (Rust), Google Benchmark (C++), `pytest-benchmark` (Python) — which handle warm-up, statistical sampling, and outlier detection for you:

```rust
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn bench_filter(c: &mut Criterion) {
    let cloud = make_representative_pointcloud(100_000);   // realistic size
    c.bench_function("voxel_filter", |b| {
        b.iter(|| voxel_filter(black_box(&cloud)))         // black_box defeats DCE
    });
}
criterion_group!(benches, bench_filter);
criterion_main!(benches);
```

The professional standard: benchmarks live in CI and a regression that slows a hot path by >X% fails the build, exactly as a correctness test would (the CI rigor of [94-software-testing-and-verification-deep.md](94-software-testing-and-verification-deep.md)). Performance, once won, must be *defended* — it silently rots otherwise.

---

## 8. A worked mental model — putting it together

Suppose a perception pipeline runs at 12 Hz and must hit 30 Hz. The disciplined attack:

1. **Define the target.** 30 Hz = 33 ms budget per frame, measured at p99 (not mean — a dropped frame is a missed detection).
2. **Profile.** A flamegraph shows 55% in a point-cloud filter, 30% in inference, 15% elsewhere. By Amdahl, even infinitely fast inference caps you at $1/0.7 = 1.43\times$ — so the *filter* is the prize.
3. **Diagnose the filter.** `perf stat` shows IPC = 0.4 and huge cache-misses → it is **memory-bound**, not compute-bound. The structure is AoS, pointer-chasing per point.
4. **Fix the layout.** Convert to SoA, contiguous; the prefetcher now streams it. Cache misses collapse, IPC rises to 2.1.
5. **Vectorize.** With packed, independent data, `-O3 -march=native` auto-vectorizes the inner loop to AVX. Verified on godbolt: `vmulps`/`vfmadd` present.
6. **Re-measure.** Filter drops from 18 ms to 4 ms; total frame from 83 ms to ~24 ms → 41 Hz, target met.
7. **Lock it in.** A criterion benchmark in CI fails if the filter regresses >10%.

No algorithm was rewritten. The win came from *understanding the machine* — caches, layout, SIMD — guided entirely by measurement. That is performance engineering: not heroics, but the relentless application of the loop in Section 1, anchored by the laws of Section 2 and the hardware reality of Section 3.

---

## Sources & further study

- **Brendan Gregg, *Systems Performance: Enterprise and the Cloud*** — the definitive methodology (USE method, profiling, the whole stack). Pair with his flamegraph tooling.
- **Denis Bakhvalov, *Performance Analysis and Tuning on Modern CPUs*** — free, modern, deeply practical on counters, IPC, and the roofline model.
- **Agner Fog's optimization manuals** — the canonical microarchitecture and instruction-timing references.
- **Ulrich Drepper, "What Every Programmer Should Know About Memory"** — the long-form memory-hierarchy bible.
- **Scott Meyers, *Effective C++ / CPU Caches talks*** — "CPU Caches and Why You Care" is a classic primer.
- **Matt Godbolt's Compiler Explorer (godbolt.org)** — verify vectorization and codegen interactively.
- **Intel/ARM optimization reference manuals** — for SIMD intrinsics and microarchitectural detail.

> Framing note: Most engineers believe their code is fast because it *looks* fast; performance engineers know whether it is fast because they *measured* it. The discipline is humbling — the profiler will repeatedly prove your intuitions wrong — and that humility is the source of its power. In autonomy, where a missed frame is a missed target and a blown deadline can crash a vehicle, the engineer who can measure, diagnose, and make the machine do exactly what it's capable of is the one whose systems hold up when the timing actually matters.
