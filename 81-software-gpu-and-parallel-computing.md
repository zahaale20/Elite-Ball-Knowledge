# GPU & Parallel Computing — Programming the Massively Parallel Machine

> **Why this exists.** Every modern autonomy stack lives or dies on throughput: perception
> networks, SLAM back-ends, sensor fusion, planning, and simulation all demand floating-point
> rates that no serial CPU can reach. The GPU is the workhorse — thousands of cores executing
> the same instruction across vast data — but it punishes naive code mercilessly. A kernel that
> ignores the memory hierarchy can run 50× slower than one that respects it, on the exact same
> silicon. The engineer who understands the CUDA execution model, the roofline, occupancy, and
> the memory wall is the one who turns a research model that runs at 3 FPS into a fielded one
> that runs at 60 FPS on an embedded Jetson within a power budget.
>
> **What mastering it makes you.** The engineer who profiles before optimizing; who reads a
> roofline plot and knows whether a kernel is compute-bound or memory-bound; who coalesces
> global memory accesses, exploits shared memory, hides latency with occupancy, and chooses the
> right parallel pattern (map, reduce, scan, stencil) for the problem instead of fighting the
> hardware.

This module powers the perception and learning of [20-autonomy-ml-ai.md](20-autonomy-ml-ai.md),
feeds the ML-serving infrastructure of [85-software-mlops-and-ml-infrastructure.md](85-software-mlops-and-ml-infrastructure.md),
and complements the low-latency CPU real-time work of
[04-foundations-modern-cpp-realtime.md](04-foundations-modern-cpp-realtime.md) and
[82-software-real-time-operating-systems.md](82-software-real-time-operating-systems.md). It is
the compute engine behind the simulation in
[06-foundations-simulation-test-verification.md](06-foundations-simulation-test-verification.md),
shares the software-engineering discipline of [12-career-software-engineering.md](12-career-software-engineering.md),
and the platform-ecosystem strategy of [42-companies-nvidia-platform-ecosystem.md](42-companies-nvidia-platform-ecosystem.md)
explains why CUDA is a moat. Networked many-GPU training connects to
[80-software-distributed-systems-deep.md](80-software-distributed-systems-deep.md).

---

## Table of Contents

1. [Why GPUs — latency vs throughput](#1-why-gpus--latency-vs-throughput)
2. [The CUDA execution model](#2-the-cuda-execution-model)
3. [The memory hierarchy](#3-the-memory-hierarchy)
4. [Writing and launching a kernel](#4-writing-and-launching-a-kernel)
5. [Occupancy, warps, and divergence](#5-occupancy-warps-and-divergence)
6. [The roofline model](#6-the-roofline-model)
7. [Parallel patterns](#7-parallel-patterns)
8. [Multi-GPU and the bigger picture](#8-multi-gpu-and-the-bigger-picture)
9. [Practice this week](#9-practice-this-week)
10. [Sources & further study](#10-sources--further-study)

---

## 1. Why GPUs — latency vs throughput

A CPU is a **latency machine**: a few powerful cores with deep pipelines, big caches, branch
predictors, and out-of-order execution, all engineered to finish *one* thread as fast as
possible. A GPU is a **throughput machine**: thousands of simpler cores that tolerate latency by
having so much parallel work in flight that something is always ready to run.

```
 CPU                           GPU
 ┌──────┬──────┐               ┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐
 │ big  │ big  │  4-64 cores   │░│░│░│░│░│░│░│░│░│░│░│░│  thousands of
 │ core │ core │  huge cache   ├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤  tiny cores
 └──────┴──────┘  OOO, BP      │░│░│░│░│░│░│░│░│░│░│░│░│  SIMT, latency-hiding
```

The consequence: GPUs win when you have **massive data parallelism** — the same operation over
millions of independent elements (a convolution, a matmul, a particle update). They lose on
serial, branchy, pointer-chasing code. The art is restructuring your problem into the GPU's
shape.

---

## 2. The CUDA execution model

CUDA exposes a **SIMT** (Single Instruction, Multiple Thread) model with a clean hierarchy:

```
 Grid
 ├── Block (0,0)  Block (1,0)  ...      blocks run independently, any order
 │     ├── Warp 0 (32 threads, lockstep)
 │     ├── Warp 1
 │     └── ...
 └── ...
```

- **Thread:** the smallest unit; has its own registers and program counter.
- **Warp:** 32 threads that execute the *same instruction* in lockstep on a SIMD lane. This is
  the real hardware scheduling unit.
- **Block (thread block):** up to 1024 threads that share **shared memory** and can synchronize
  via `__syncthreads()`. A block runs entirely on one Streaming Multiprocessor (SM).
- **Grid:** all blocks for one kernel launch. Blocks are independent — the runtime schedules
  them across SMs in any order, which is *why* GPUs scale to bigger chips transparently.

Indexing maps the logical grid onto data:

$$
\text{global\_id} = \text{blockIdx.x} \times \text{blockDim.x} + \text{threadIdx.x}
$$

The key mental shift from CPU code: you do not write a loop over elements — you write the body of
the loop *once*, and the hardware runs it across the grid.

---

## 3. The memory hierarchy

Performance on a GPU is overwhelmingly a memory story. The hierarchy, fastest to slowest:

| Memory | Scope | Latency (approx) | Notes |
|---|---|---|---|
| Registers | per-thread | ~1 cycle | Fastest; spilling to local memory is a perf cliff |
| Shared memory / L1 | per-block | ~30 cycles | Programmer-managed scratchpad; bank conflicts hurt |
| L2 cache | device | ~200 cycles | Shared across SMs |
| Global (HBM/GDDR) | device | ~400–800 cycles | Huge bandwidth (TB/s) but high latency |
| Host (PCIe) | CPU↔GPU | microseconds | The cliff: minimize transfers, overlap with compute |

Two rules dominate:

1. **Coalesce global accesses.** When the 32 threads of a warp read 32 *consecutive* addresses,
   the hardware fuses them into one or two memory transactions. Strided or random access
   serializes into many transactions — easily a 10–30× slowdown.
2. **Stage through shared memory.** Load a tile of global data into shared memory once, let the
   block reuse it many times, then write back. This is the single most important optimization
   for matmul, convolution, and stencils.

```
 Coalesced (fast):   thread 0→addr 0, t1→addr 1, ... t31→addr 31  => 1 transaction
 Strided (slow):     thread 0→addr 0, t1→addr 16, ...             => up to 32 transactions
```

---

## 4. Writing and launching a kernel

A canonical tiled SAXPY/vector add, then the idea of tiling for reuse:

```cpp
// Elementwise y = a*x + y, one thread per element. The grid-stride loop
// lets a single launch cover arrays larger than the grid.
__global__ void saxpy(int n, float a, const float* x, float* y) {
    for (int i = blockIdx.x * blockDim.x + threadIdx.x;
         i < n;
         i += blockDim.x * gridDim.x) {       // grid-stride: portable across GPU sizes
        y[i] = a * x[i] + y[i];               // coalesced if x,y are contiguous
    }
}

void launch(int n, float a, const float* dx, float* dy) {
    int threads = 256;                        // multiple of warp size (32)
    int blocks  = (n + threads - 1) / threads;
    saxpy<<<blocks, threads>>>(n, a, dx, dy); // asynchronous w.r.t. host
    cudaDeviceSynchronize();                  // wait + surface errors
}
```

Tiled matrix multiply is the textbook case where shared memory turns a memory-bound kernel into
a compute-bound one:

```cpp
// Each block computes one TILE x TILE output tile, staging A and B tiles
// into shared memory so each loaded element is reused TILE times.
template <int TILE>
__global__ void matmul(const float* A, const float* B, float* C, int N) {
    __shared__ float As[TILE][TILE];
    __shared__ float Bs[TILE][TILE];
    int row = blockIdx.y * TILE + threadIdx.y;
    int col = blockIdx.x * TILE + threadIdx.x;
    float acc = 0.0f;
    for (int t = 0; t < N / TILE; ++t) {
        As[threadIdx.y][threadIdx.x] = A[row * N + t * TILE + threadIdx.x];
        Bs[threadIdx.y][threadIdx.x] = B[(t * TILE + threadIdx.y) * N + col];
        __syncthreads();                       // ensure tiles are fully loaded
        for (int k = 0; k < TILE; ++k)
            acc += As[threadIdx.y][k] * Bs[k][threadIdx.x];
        __syncthreads();                       // before overwriting the tiles
    }
    C[row * N + col] = acc;
}
```

In practice you would not hand-write matmul — you'd call cuBLAS/CUTLASS or let a compiler
(Triton, XLA) generate it — but understanding *why* the tiled version is fast is essential to
reasoning about any kernel.

---

## 5. Occupancy, warps, and divergence

**Occupancy** is the ratio of active warps on an SM to the hardware maximum. Higher occupancy
gives the scheduler more warps to hide memory latency — while one warp stalls on a load, another
runs. But occupancy is bounded by the scarcest resource per SM: registers per thread, shared
memory per block, or block count. Using fewer registers and less shared memory raises occupancy
but may reduce per-thread efficiency; it is a balance you *measure*, not guess.

$$
\text{occupancy} = \frac{\text{active warps per SM}}{\text{max warps per SM}}
$$

**Warp divergence** is the SIMT tax: if threads in a warp take different branches of an `if`, the
hardware executes *both* paths with the inactive lanes masked off, serializing them. Divergent,
data-dependent branching inside a warp can halve throughput. Mitigations: restructure so threads
in a warp follow the same path; sort/bucket data; use predication for short branches.

```
 if (cond) { A } else { B }   with mixed cond in a warp:
   step 1: lanes where cond → run A, others idle
   step 2: lanes where !cond → run B, others idle      (both paths cost time)
```

---

## 6. The roofline model

The roofline model tells you, before you optimize, whether a kernel is **compute-bound** or
**memory-bound**. Define **arithmetic intensity** $I$ as FLOPs per byte of DRAM traffic:

$$
I = \frac{\text{FLOPs}}{\text{bytes from DRAM}}, \qquad
P_{\text{attainable}} = \min\!\left(P_{\text{peak}},\; I \times BW_{\text{peak}}\right)
$$

```
 Attainable
 GFLOP/s ▲
         │              ___________ peak compute (flat roof)
         │            /
         │          /  ← memory-bound region (slope = BW)
         │        /
         └──────/──────────────────────────▶ arithmetic intensity (FLOP/byte)
              ridge point
```

- Left of the **ridge point** (low intensity): you are **memory-bound** — adding more FLOPs is
  free; the fix is reducing/caching memory traffic (tiling, fusion).
- Right of it: you are **compute-bound** — the fix is using faster math units (tensor cores,
  fused multiply-add, lower precision).

This single plot redirects optimization effort correctly. SAXPY ($I \approx 0.17$) is hopelessly
memory-bound; dense matmul ($I \propto N$) becomes compute-bound at large $N$. Profile, locate
the kernel on the roofline, then choose the matching optimization.

---

## 7. Parallel patterns

Most GPU work decomposes into a handful of reusable patterns:

- **Map:** independent per-element work (activation functions, color conversion). Trivially
  parallel.
- **Reduce:** combine all elements into one (sum, max). Done as a tree in $O(\log n)$ depth;
  watch for bank conflicts and use warp-shuffle reductions for the last 32 elements.
- **Scan (prefix sum):** running totals; the backbone of stream compaction, sorting, and sparse
  ops. Blelloch's work-efficient scan is the classic.
- **Stencil:** each output depends on a neighborhood (convolution, PDE solvers, image filters).
  Shared-memory tiling with halo regions is the standard approach.
- **Gather/scatter:** indirect indexing; the source of uncoalesced-access pain — reorder data
  when possible.
- **Sort:** radix sort on GPU is bandwidth-bound and extremely fast; underpins spatial hashing
  for [51-autonomy-slam-and-mapping.md](51-autonomy-slam-and-mapping.md)-style nearest-neighbor.

Knowing the pattern tells you the expected complexity, the bottleneck, and the optimized library
(Thrust, CUB, cuDNN) to reach for instead of reinventing it.

---

## 8. Multi-GPU and the bigger picture

When one GPU is not enough — large-model training or big simulations — you scale out, and the
distributed-systems concerns of [80-software-distributed-systems-deep.md](80-software-distributed-systems-deep.md)
return:

- **Data parallelism:** replicate the model on each GPU, split the batch, **all-reduce** the
  gradients (NCCL ring/tree all-reduce). Communication overlaps with backward-pass compute.
- **Model/tensor parallelism:** split a single huge layer across GPUs (Megatron-style) when it
  doesn't fit in one device's memory.
- **Pipeline parallelism:** assign different layers to different GPUs and stream micro-batches.

Interconnect matters as much as the GPUs: NVLink/NVSwitch (hundreds of GB/s) vs PCIe (tens) vs
Ethernet/InfiniBand across nodes. The all-reduce communication cost often becomes the scaling
ceiling — Amdahl's law applies to the serial/communication fraction:

$$
\text{speedup} = \frac{1}{(1-p) + \frac{p}{N}}
$$

For embedded autonomy (Jetson, Orin) the constraint flips: a single GPU under a tight **power
and thermal** budget ([72-engineering-thermal-management.md](72-engineering-thermal-management.md)),
where INT8 quantization and TensorRT optimization buy the frames-per-watt the mission needs.

---

## 9. Practice this week

1. Write a naive and a coalesced version of a transpose kernel; profile both with Nsight Compute
   and explain the bandwidth difference from the memory-transaction count.
2. Implement tiled matmul; vary `TILE` and plot achieved GFLOP/s; locate your kernel on the
   roofline and confirm where it crosses from memory- to compute-bound.
3. Build a block reduction with shared memory and then a warp-shuffle version; measure the
   speedup from eliminating the final `__syncthreads()` rounds.
4. Quantize a small CNN to INT8 with TensorRT and measure frames-per-watt on an embedded GPU vs
   FP32 — connect the result to the power budget of a real airframe.

---

## 10. Sources & further study

- **Kirk & Hwu — *Programming Massively Parallel Processors*.** The definitive CUDA textbook;
  patterns, memory, occupancy, case studies.
- **Williams, Waterman & Patterson — *Roofline: An Insightful Visual Performance Model*.** The
  roofline paper.
- **NVIDIA CUDA C++ Programming Guide & Best Practices Guide.** The authoritative reference for
  the execution and memory model.
- **Bryant & O'Hallaron — *Computer Systems: A Programmer's Perspective (CSAPP)*.** Memory
  hierarchy, caches, and the cost model underneath everything here.
- **Hennessy & Patterson — *Computer Architecture: A Quantitative Approach*.** SIMD, GPUs, and
  the quantitative method.
- **Harris — *Optimizing Parallel Reduction in CUDA* (NVIDIA talk).** A masterclass in iterative
  kernel optimization.
- **Nsight Systems / Nsight Compute docs.** Learn to profile — measurement before optimization.

> Framing note: A GPU is not a magic accelerator you sprinkle on slow code — it is a specific
> machine with a specific shape, and performance is the reward for reshaping your problem to fit
> it. The engineers who field real-time perception on embedded hardware do not guess; they
> profile, place each kernel on the roofline, respect the memory hierarchy, and trade precision
> for frames-per-watt with their eyes open — because in the field, throughput within a power
> budget is the whole game.
