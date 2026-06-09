# Module 04 — Modern C++ & Real-Time Embedded

> **Why this file exists.** This is curriculum Module 02 — the language and discipline of
> flight-critical autonomy. Your [`pixhawk/drone/`](../01-mastery-curriculum.md) stack is
> Python today: a FastAPI onboard service, MAVSDK/pymavlink, glue around the IMX500 and the
> GPS-denied nav pipeline. Python is the right tool for *prototyping decisions* and talking
> to humans. It is the *wrong* tool for the 400 Hz inner loops that keep a tilt-tricopter in
> the air. PX4 itself — the autopilot under your Pixhawk 6C — is tens of thousands of lines
> of C++ running under a hard real-time scheduler with zero dynamic allocation in the flight
> path. To read that code, debug it, contribute to it, or move your own performance-critical
> modules down onto the metal, you must think in C++ *and* in real-time systems. Mastering
> this file makes you the person who can take the track-fusion filter you prototyped in
> Python and ship it as a deterministic C++ module that hits its deadline every single cycle
> — which is exactly the boundary between "hobbyist with a drone" and "engineer Anduril /
> Shield AI / Skydio will hire."
>
> **What this makes you.** Fluent in the language flight software is written in; able to
> reason about memory, cache, threads, and deadlines; and disciplined enough to know *why*
> garbage collection and `malloc` are banned from a control loop. Not a language tourist — an
> engineer who can be trusted with the loop that, if it misses, the aircraft falls.

**Companion code.** We anchor to the real autonomy stack in this repository — the VTOL
tilt-tricopter (Pixhawk 6C + Raspberry Pi 5), FastAPI onboard service over MAVSDK/pymavlink,
on-sensor IMX500 inference, GPS-denied navigation (visual odometry + map-matching), track
fusion, world memory, a constitution-gated command policy, and a hash-chained
tamper-evident decision log. The worked example in §8 rewrites your `perception/` track-fusion
filter in C++ and binds it back to the Python service. Read alongside
[12-career-software-engineering.md](../career/12-software-engineering.md) (the engineering craft
around the code), [25-autonomy-control-theory.md](../autonomy/25-control-theory.md) and
[28-autonomy-gnc.md](../autonomy/28-gnc.md) (the loops that demand real-time), and
[06-foundations-simulation-test-verification.md](06-simulation-test-verification.md)
(how you prove the rewrite is correct).

---

## Table of Contents

1. [Why C++/Rust for flight software](#1-why-crust-for-flight-software)
2. [The C++ mental model — ownership, RAII, the type system](#2-the-c-mental-model--ownership-raii-the-type-system)
3. [Smart pointers & move semantics](#3-smart-pointers--move-semantics)
4. [Templates & the STL](#4-templates--the-stl)
5. [Build systems — CMake & the toolchain](#5-build-systems--cmake--the-toolchain)
6. [Undefined behavior & sanitizers](#6-undefined-behavior--sanitizers)
7. [Computer systems — memory, processes, scheduling](#7-computer-systems--memory-processes-scheduling)
8. [Concurrency — threads, atomics, lock-free](#8-concurrency--threads-atomics-lock-free)
9. [Real-time systems — deadlines, jitter, determinism](#9-real-time-systems--deadlines-jitter-determinism)
10. [Worked example — track-fusion in C++, bound to Python](#10-worked-example--track-fusion-in-c-bound-to-python)
11. [Practice this week](#11-practice-this-week)
12. [Sources & Citations](#sources--citations)

---

## 1. Why C++/Rust for flight software

### 1.1 The two-language reality of every autonomy company

Walk into Anduril, Shield AI, Skydio, or the autonomy group at any prime and you find the
same split your own repo already has by instinct:

```
   PROTOTYPE / DECISION LAYER          FLIGHT-CRITICAL / INNER LOOP
   ──────────────────────────          ────────────────────────────
   Python, sometimes Julia             C++ (dominant), Rust (rising)
   FastAPI, MAVSDK glue                PX4 modules, custom estimators
   IMX500 orchestration                attitude/rate control @ 400 Hz+
   mission logic, ground tools         the EKF, the mixer, drivers
   "is this decision correct?"         "did we hit the deadline?"
```

You already live this: your `policy/` and FastAPI service are Python because the questions
there are about *correctness and human interface*; PX4 under your Pixhawk is C++ because the
questions there are about *determinism and timing*. The skill this module builds is the
ability to cross that line deliberately — to take a module that has earned its place in the
prototype layer and move it down where the deadlines are hard.

### 1.2 Why not just Python everywhere?

Three physics-grade reasons, not preferences:

1. **The Global Interpreter Lock and the garbage collector make timing non-deterministic.**
   Python can pause your thread at an arbitrary moment to collect garbage. A 5 ms GC pause in
   a 2.5 ms control period means a missed deadline, which on a multirotor means a transient
   loss of stabilization. You cannot *bound* Python's worst-case latency, and real-time is
   about the worst case, never the average.
2. **Dynamic allocation is unbounded and fragmenting.** Every Python object is heap-allocated
   and reference-counted. `malloc`/`free` have unbounded worst-case time and fragment memory
   over hours of flight. Flight loops forbid allocation entirely (§9).
3. **Overhead.** Interpreted dispatch, boxed numbers, and object headers cost 10–100× the CPU
   and memory of equivalent C++. On a power- and thermal-limited Pi 5 or an even smaller
   flight MCU, that overhead is endurance you don't have.

> **The honest framing.** Python isn't "slow and bad"; it's *non-deterministic and
> allocation-heavy*, which is fatal **only** in the hard-real-time path. Use it everywhere
> else. The engineering judgment — *which code actually has a hard deadline?* — is the whole
> game, and it's a [systems-engineering](01-first_principles_systems_engineering.md) call.

### 1.3 C++ vs Rust — the live debate

| Dimension | C++ | Rust |
|---|---|---|
| Maturity in flight | PX4, ArduPilot, almost all primes | growing (some new autonomy stacks, drivers) |
| Memory safety | manual; UB is real and deadly (§6) | **compiler-enforced** ownership, no data races |
| Ecosystem / tooling | enormous, Eigen, ROS, vendor SDKs | younger but excellent; `cargo` is a joy |
| Learning cost | high (decades of features) | high (the borrow checker fights you early) |
| Why it still wins today | incumbency + ecosystem + you *must* read it | safety guarantees that eliminate whole bug classes |

The pragmatic answer for *you*: **learn C++ first, because the code you must read and the
jobs you want are C++.** Learn enough Rust to follow the safety arguments and to be credible
when a team chooses it for a new component. Rust's ownership model is, conveniently, the same
idea C++ teaches through RAII (§2) — so learning C++ ownership deeply makes Rust click later.

---

## 2. The C++ mental model — ownership, RAII, the type system

C++ gives you total control over memory and timing. That power is why it flies aircraft and
why it can crash them. The discipline that makes it safe is **RAII**, and it is the single
most important idea in the language.

### 2.1 The stack vs the heap — know where every byte lives

```
   STACK                                 HEAP
   ─────                                 ────
   automatic lifetime (scope)            manual lifetime (new/delete, or smart ptr)
   allocation = move a pointer (free)    allocation = malloc (slow, unbounded WCET)
   freed automatically at scope exit     leaked if you forget to free
   tiny, fixed size (overflow = crash)   large, fragmentable
   PERFECT for real-time loops           DANGEROUS in real-time loops (§9)
```

A control-loop value — the latest IMU sample, a 3×3 covariance — lives on the **stack** or in
a pre-allocated buffer. The moment you reach for `new` inside a flight loop, stop: you've
imported the heap's unbounded worst case into a path that has a deadline.

### 2.2 RAII — Resource Acquisition Is Initialization

The idea in one sentence: **tie every resource (memory, file, lock, socket, GPIO) to the
lifetime of an object, so it is released automatically when the object goes out of scope.**
The constructor acquires; the destructor releases. You cannot forget to clean up, because the
language cleans up for you — even when an exception unwinds the stack.

```cpp
// Without RAII: a leak waiting to happen.
void bad() {
    Lock* l = new Lock(mutex);   // acquire
    if (sensor_failed()) return; // ...and we just leaked the lock. Deadlock next cycle.
    delete l;                    // only runs on the happy path
}

// With RAII: correctness by construction.
void good() {
    std::lock_guard<std::mutex> l(mutex); // acquire in constructor
    if (sensor_failed()) return;          // destructor releases the lock automatically
}                                         // released here too. No leak path exists.
```

RAII is *why* C++ can be trusted with flight resources: the cleanup is not a thing you
remember, it is a thing the type system guarantees. Every smart pointer, every lock guard,
every file stream in §3–§4 is an application of this one principle. (And it's exactly the
guarantee Rust's ownership model promotes from "convention" to "compiler error.")

### 2.3 const-correctness and the type system as a contract

C++'s type system is your first line of defense — use it to make illegal states
unrepresentable:

- **`const` everything you don't mutate.** A `const Covariance&` parameter tells the compiler
  *and the reader* "this function will not change your matrix." The compiler enforces it. In a
  shared estimator, const-correctness is how you prove a reader can't corrupt the filter state.
- **Strong types over raw primitives.** A bare `float yaw` invites the NED/ENU frame bug from
  [Module 03](03-mathematics.md). A `struct YawNED { float rad; };` makes the
  frame part of the type, so a frame mismatch is a *compile error*, not a crash at altitude.
- **`enum class` for modes**, not magic ints — the compiler catches an invalid flight mode.

> **Senior tell.** Juniors comment "// position is in NED here." Seniors encode it in the
> type so the comment can't go stale and the compiler enforces it. Push invariants into types;
> let the build fail instead of the aircraft.

---

## 3. Smart pointers & move semantics

Manual `new`/`delete` is the historic source of C++'s worst bugs: leaks, double-frees,
use-after-free. Modern C++ (C++11 onward) makes raw owning pointers a code smell. You express
*ownership* in the type.

### 3.1 The three pointers and what each says about ownership

| Type | Meaning | Use in your stack |
|---|---|---|
| `std::unique_ptr<T>` | **sole** owner; moves, never copies | the default — one owner of a driver, a buffer |
| `std::shared_ptr<T>` | **shared** ownership; reference-counted | only when lifetime is genuinely shared (rare in flight) |
| `T*` / `T&` (raw, non-owning) | "I observe but don't own" | function parameters that just read |

The rule that prevents most memory bugs: **own with `unique_ptr`, pass by reference, share
only when you truly must.** `shared_ptr`'s atomic reference count costs time and its
nondeterministic destruction (whoever drops the last reference runs the destructor) is a
hazard in real-time code — prefer `unique_ptr`.

```cpp
// Ownership is visible in the signature. No leaks possible.
std::unique_ptr<Estimator> make_estimator(const Config& cfg) {
    return std::make_unique<Estimator>(cfg); // allocated once, owner returned
}                                            // caller owns it; destroyed automatically

void run(const Estimator& est);  // borrows, doesn't own — clearly a reader
```

### 3.2 Move semantics — transfer without copying

A 1080p camera frame or a large point cloud is expensive to copy. **Move semantics** let you
*transfer ownership* of an object's guts (its heap buffer) instead of duplicating them — you
hand over the pointer and null out the source. This is the difference between copying a
megabyte and copying a pointer.

```cpp
std::vector<Detection> detections = run_imx500();      // owns a big buffer
process(std::move(detections));  // hand the buffer over — O(1), no megabyte copy
// 'detections' is now empty/valid-but-unspecified; the callee owns the data
```

Why you care in autonomy:

- **Zero-copy data flow.** Moving frames/detections between pipeline stages instead of
  copying keeps latency and memory bandwidth low — directly relevant to the IMX500 → track
  fusion path.
- **`unique_ptr` is move-only by design** — that's how the type system enforces "sole owner."
- **Return big objects by value, cheaply.** Modern C++ moves (or elides) the return, so
  `std::vector<Track> fuse(...)` is fast and clean.

> **The mental model.** Copy = "make a second one." Move = "give you mine and forget I had
> it." In a real-time pipeline you move; you copy only when you genuinely need an independent
> duplicate.

---

## 4. Templates & the STL

### 4.1 Templates — write once, the compiler specializes

A template is a *compile-time* recipe: write an algorithm or container once over a type
parameter `T`, and the compiler stamps out a specialized, fully-optimized version for each
concrete type. No runtime dispatch cost — the abstraction is free at runtime.

```cpp
template <typename T, int N>
struct Vec {                       // a fixed-size vector, no heap, real-time safe
    T data[N];
    T dot(const Vec& o) const {
        T s = 0;
        for (int i = 0; i < N; ++i) s += data[i] * o.data[i];
        return s;
    }
};
// Vec<float,3> for a body-frame velocity; Vec<double,6> for an SE(3) tangent vector.
```

This is exactly how **Eigen** — the linear-algebra library under most flight code and under
the math of [Module 03](03-mathematics.md) — gives you matrix expressions that
compile down to tight, allocation-free loops. Templates are why C++ can be both high-level
*and* fast: the genericity is resolved at build time, leaving no overhead at flight time.

### 4.2 The STL — containers and algorithms you must own

| Component | What it is | Real-time note |
|---|---|---|
| `std::vector<T>` | dynamic array | great — but `reserve()` up front to avoid mid-loop reallocation |
| `std::array<T,N>` | fixed-size array, on the stack | **preferred in flight loops** — no heap, no surprises |
| `std::span<T>` | non-owning view over contiguous memory | pass buffers without copying or owning |
| `std::map` / `std::unordered_map` | trees / hash tables | allocate per insert — keep **out** of hard loops |
| `<algorithm>` | `sort`, `transform`, `accumulate`, … | express intent clearly; let the compiler optimize |

The discipline: **the STL is wonderful in the prototype/decision layer and on the Pi-side
service; in the hard loop you restrict yourself to fixed-size, pre-allocated containers** so
that no operation can trigger a heap allocation (§9). Knowing *which* STL operations allocate
is a core real-time skill — `vector::push_back` past capacity allocates; `array` never does.

### 4.3 RAII + templates + STL = the modern C++ idiom

Put the three together and you get code that is high-level to read, free at runtime, and safe
by construction: `std::lock_guard` (RAII) protecting a `std::array` (no-alloc) of `Vec<float,3>`
(template) processed by `std::transform` (STL algorithm). That sentence is what idiomatic
modern flight-adjacent C++ looks like.

---

## 5. Build systems — CMake & the toolchain

Real flight software is not one file; it's hundreds, with dependencies (Eigen, the vendor
SDK, your modules), multiple targets (the Pi-side service, a SITL build, the cross-compiled
firmware), and a test build. **CMake** is the de-facto standard that orchestrates this.

### 5.1 What the toolchain actually does

```
   source.cpp ──preprocess──► expanded ──compile──► object.o ──link──► executable
       │            │                       │                     │
   #includes   macros expanded      one .o per .cpp        resolve symbols,
   pulled in                        (parallelizable)       pull in libraries
```

Understanding this pipeline is how you decode build errors: a *compile* error is in one file's
syntax/types; a *linker* error ("undefined reference") means a symbol was declared but never
defined or a library wasn't linked. Confusing the two wastes hours.

### 5.2 A minimal but real CMake setup

```cmake
cmake_minimum_required(VERSION 3.16)
project(track_fusion LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)            # modern C++; 20 if your toolchain supports it
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Eigen3 REQUIRED)        # the matrix library from Module 03

add_library(track_fusion src/track_fusion.cpp)
target_link_libraries(track_fusion PUBLIC Eigen3::Eigen)

# A separate target for the Python binding (see §10)
find_package(pybind11 REQUIRED)
pybind11_add_module(track_fusion_py src/bindings.cpp)
target_link_libraries(track_fusion_py PRIVATE track_fusion)

# Build the same code with sanitizers in a debug config (see §6)
target_compile_options(track_fusion PRIVATE
    $<$<CONFIG:Debug>:-fsanitize=address,undefined -g -O1>)
target_link_options(track_fusion PRIVATE
    $<$<CONFIG:Debug>:-fsanitize=address,undefined>)
```

You don't need to be a CMake wizard, but you must be able to: add a source file, link a
library, set the C++ standard, and turn on sanitizers for the debug build. Those four cover
90% of daily work.

### 5.3 Debug vs Release — and the trap

`-O0 -g` (Debug): no optimization, full symbols — for debugging and sanitizers. `-O2`/`-O3`
(Release): full optimization — what flies. The trap that bites everyone: **a bug that vanishes
in Debug and appears in Release is almost always undefined behavior** (§6) that the optimizer
is "exploiting." That observation is your first diagnostic instinct, not a mystery.

---

## 6. Undefined behavior & sanitizers

### 6.1 What UB is and why it's uniquely dangerous

**Undefined behavior** is any operation the C++ standard places no constraints on:
dereferencing a null/dangling pointer, reading uninitialized memory, signed overflow,
out-of-bounds access, a data race. The compiler is *allowed to assume UB never happens* and
optimizes accordingly — so UB doesn't reliably crash. It can:

- work perfectly in Debug and corrupt memory in Release,
- work on your laptop and fail on the Pi's ARM target,
- work for 9,000 flight-loop iterations and crash on the 9,001st.

This is why UB is the nightmare of flight software: it produces **intermittent, environment-
dependent, non-reproducible** failures — the worst kind to chase when the symptom is "the
aircraft occasionally twitched."

### 6.2 The sanitizers — make UB loud and reproducible

You do not hunt UB by staring at code. You compile with **sanitizers** that instrument the
binary to catch it the instant it happens:

| Sanitizer | Catches | When to run |
|---|---|---|
| **ASan** (AddressSanitizer) | buffer overflow, use-after-free, leaks | every debug/test build |
| **UBSan** (UndefinedBehaviorSanitizer) | signed overflow, bad casts, null deref, misalignment | every debug/test build |
| **TSan** (ThreadSanitizer) | **data races** between threads | concurrency tests (§8) |
| **MSan** (MemorySanitizer) | reads of uninitialized memory | targeted, picky setup |

```bash
# Build the track-fusion tests with ASan+UBSan and run them.
cmake -DCMAKE_BUILD_TYPE=Debug -B build && cmake --build build
./build/track_fusion_tests          # ASan aborts with a stack trace at the first violation
```

> **The rule.** Your CI runs the test suite under ASan+UBSan, and the concurrency tests under
> TSan. A green test suite that has never been run under sanitizers is *not* evidence of
> memory safety — it's evidence you haven't looked. This habit is what
> [Module 06 (sim/test/verification)](06-simulation-test-verification.md) and
> your [testing instincts](../career/12-software-engineering.md) demand, and it ties directly to
> the safety case in [Module 09](09-safety-assurance.md).

### 6.3 Rust's pitch, restated

Most of the table above — use-after-free, data races, dangling pointers — Rust makes
*impossible at compile time* via its ownership and borrowing rules. That's the safety argument
for Rust in new flight components: it moves bugs you'd otherwise catch (maybe) with TSan into
errors you cannot even build. When a team picks Rust, this is why; you should be able to make
that argument and weigh it against C++'s ecosystem incumbency.

---

## 7. Computer systems — memory, processes, scheduling

You cannot reason about real-time without understanding the machine underneath. This is the
*CS:APP* core, compressed to what flight software demands.

### 7.1 The memory hierarchy — why cache, not clock speed, often rules

```
   FASTEST, SMALLEST                                   SLOWEST, LARGEST
   ─────────────────                                   ────────────────
   registers  →  L1 (~1ns) → L2 (~4ns) → L3 (~12ns) → RAM (~100ns) → disk/flash (~ms)
   each step down is ~10× slower and ~10× bigger
```

The headline fact: **a cache miss to RAM costs ~100× an L1 hit.** On a tight loop, *how your
data is laid out in memory* can matter more than the algorithm's big-O. Two consequences you
will act on:

- **Structure of Arrays (SoA) beats Array of Structures (AoS) for hot loops.** If your track
  fusion iterates over 200 tracks touching only their positions, store positions
  contiguously (`float x[200]; float y[200];`) so each cache line is full of useful data,
  not interleaved fields you skip. This single layout choice routinely doubles throughput.
- **Predictable, sequential access** lets the hardware prefetcher hide latency; random
  pointer-chasing (linked lists, `std::map`) defeats it. Another reason flat arrays win in
  the hot path.

### 7.2 Processes vs threads — the isolation/speed tradeoff

| | Process | Thread |
|---|---|---|
| Memory | **isolated** (own address space) | **shared** with siblings |
| Crash blast radius | contained — one process dying doesn't corrupt another | a bad thread can corrupt the whole process |
| Communication | IPC (sockets, shared mem) — explicit, slower | shared variables — fast, but needs locking (§8) |
| Context-switch cost | higher | lower |

The architecture lesson: **isolate by process where a fault must be contained, share by thread
where you need speed and tight coupling.** Your design already reflects this — the Python
FastAPI service is a separate process from PX4 precisely so a crash or stall in your higher-
level logic *cannot* take down the flight controller. That process boundary is a safety
boundary, and it ties straight to the [systems-engineering](01-first_principles_systems_engineering.md)
principle that failures should be contained at interfaces.

### 7.3 System calls — crossing into the kernel

A syscall (read a file, send a packet, sleep, `mmap`) traps into the kernel. It's far more
expensive than a function call and, worse for real-time, it can **block** for an unbounded
time (waiting on I/O). The rule: **no blocking syscalls in a hard real-time loop.** Do your
I/O — telemetry, logging, the hash-chained decision-log writes — on a *separate* thread or
process so the control loop never waits on the kernel. This is why your decision log appends
asynchronously rather than synchronously inside any timing-critical path.

### 7.4 Linux scheduling — average-fair vs real-time

Default Linux (the CFS scheduler) optimizes *fairness and throughput*, not deadlines — it may
delay your thread to be fair to others. For real-time work on the Pi you use **real-time
scheduling policies** (`SCHED_FIFO`/`SCHED_RR`) with priorities, plus a **PREEMPT_RT** kernel
to bound how long the kernel itself can delay you. Knowing this is how you make a Linux
companion computer carry a soft-real-time load (VO, nav) without a true RTOS — and knowing its
*limits* is how you decide what must instead live on the Pixhawk's RTOS (§9).

---

## 8. Concurrency — threads, atomics, lock-free

Autonomy is inherently concurrent: a sensor thread, an estimator thread, a control thread, a
telemetry/logging thread, all running at once. Getting concurrency right is where most
hard-to-find bugs live.

### 8.1 The core hazard — data races

A **data race** is two threads accessing the same memory at the same time with at least one
write, and no synchronization. It is **undefined behavior** (§6): not "you read a slightly
stale value," but "the compiler and CPU may do anything." Torn reads of a multi-word value, a
half-updated covariance matrix consumed by the controller — these are the failures.

```cpp
// RACE: estimator writes state, controller reads it, no sync. UB.
State g_state;                       // shared
void estimator() { g_state = update(...); }   // writer
void controller() { auto x = g_state; act(x); } // reader — may see a torn, half-written State
```

### 8.2 The synchronization toolkit, weakest-coupling first

| Tool | Use it for | Real-time cost |
|---|---|---|
| `std::mutex` + `lock_guard` | protect a shared structure (RAII, §2.2) | can **block**; risks priority inversion (§9) |
| `std::atomic<T>` | a single lock-free value (a flag, a counter, a pointer swap) | non-blocking, cheap |
| condition variable | "wake me when data is ready" | blocks by design (use off the hot path) |
| **lock-free queue** (SPSC ring buffer) | hand data from one thread to another | **bounded, non-blocking** — ideal for flight |

### 8.3 The flight-software pattern — a lock-free ring buffer

The preferred way to move data between a producer (sensor/estimator) and a consumer
(controller/logger) in real-time code is a **single-producer/single-consumer (SPSC) lock-free
ring buffer**: a fixed-size array with atomic head/tail indices. No locks, no blocking, no
allocation, bounded worst-case time — exactly the four properties §9 demands.

```cpp
// Sketch of the idea (real ones handle memory ordering carefully).
template <typename T, size_t N>
class SpscRing {
    std::array<T, N> buf_;                 // pre-allocated — no heap in the loop
    std::atomic<size_t> head_{0}, tail_{0};
public:
    bool push(const T& v) {                // producer thread only
        size_t h = head_.load(std::memory_order_relaxed);
        size_t n = (h + 1) % N;
        if (n == tail_.load(std::memory_order_acquire)) return false; // full
        buf_[h] = v;
        head_.store(n, std::memory_order_release);  // publish
        return true;
    }
    bool pop(T& out) {                     // consumer thread only
        size_t t = tail_.load(std::memory_order_relaxed);
        if (t == head_.load(std::memory_order_acquire)) return false; // empty
        out = buf_[t];
        tail_.store((t + 1) % N, std::memory_order_release);
        return true;
    }
};
```

This single structure is how a sensor thread feeds the estimator, and the estimator feeds the
controller, without ever taking a lock in the timing-critical path. Memory-ordering
(`acquire`/`release`) is the subtle part — get it wrong and you reintroduce a race that **only
TSan will reliably catch** (§6.2). That's why concurrency code is the canonical use case for
ThreadSanitizer.

### 8.4 The concurrency commandments

1. Prefer message-passing (the ring buffer) over shared mutable state.
2. If you must share, protect with the **smallest** lock for the **shortest** time.
3. Never hold a lock across a blocking call or a long computation.
4. Test concurrency code under **TSan**; a passing test without it proves nothing.
5. Establish a **lock ordering** and never deviate — inconsistent ordering is how deadlocks
   are born.

---

## 9. Real-time systems — deadlines, jitter, determinism

This is the heart of the module. "Real-time" does **not** mean "fast." It means **the answer
is wrong if it arrives late.** Correctness includes timing.

### 9.1 Hard vs soft real-time

```
   HARD REAL-TIME                         SOFT REAL-TIME
   ──────────────                         ──────────────
   missing a deadline = system failure    missing occasionally = degraded quality
   attitude/rate control @ 400+ Hz        video display, telemetry rate
   the mixer driving the motors           map-matching update cadence
   lives on the Pixhawk RTOS              tolerable on the Pi/Linux
```

The engineering act is **classifying each loop**: hard loops go on the deterministic RTOS
(your Pixhawk); soft loops can live on Linux (your Pi). Misclassifying a hard loop onto a
non-deterministic platform is a latent crash.

### 9.2 The metrics that define real-time quality

| Metric | Meaning | Why it matters |
|---|---|---|
| **Deadline** | the time by which a result must be ready | miss it in a hard loop → instability |
| **Latency** | input-to-output delay | adds phase lag → erodes control stability margin ([Module 25](../autonomy/25-control-theory.md)) |
| **Jitter** | variation in latency cycle-to-cycle | unpredictability is *worse* than constant delay; controllers hate jitter |
| **WCET** | Worst-Case Execution Time | the *only* number real-time cares about — you size for the worst, never the average |

> **The mindset shift.** Performance engineering optimizes the *average*. Real-time
> engineering bounds the *worst case*. A loop that's 0.5 ms on average but spikes to 6 ms once
> a second is **broken** for a 2.5 ms deadline, even though its average looks excellent.
> Everything below exists to make the worst case bounded and small.

### 9.3 Why GC and dynamic allocation are banned in flight loops

Now the §1 claims become precise:

- **Garbage collection** introduces pauses at times *you don't control and can't bound* —
  directly an unbounded WCET. (This is the deepest reason raw Python/Java can't run a hard
  loop.)
- **`malloc`/`free`** have **unbounded worst-case time** (they may walk free lists, take a
  global lock, or ask the kernel for more memory) and **fragment** the heap over hours of
  flight until an allocation fails. An allocation failure mid-flight is catastrophic.

The flight discipline, therefore:

```
   ALLOCATE ALL MEMORY UP FRONT (at init), THEN NEVER AGAIN IN THE LOOP.
   • fixed-size arrays / object pools, sized for the worst case
   • no new/delete, no STL container growth, no string formatting in the hot path
   • the loop touches only pre-allocated, stack or pool memory  → bounded, deterministic
```

This is exactly why §8's ring buffer is a *fixed-size* array and §4.2 pushed `std::array` over
`std::vector` in the hot path. Every real-time idiom in this module traces back to this single
commandment: **no surprises in the timing-critical path.**

### 9.4 Priority inversion — the bug that nearly killed Mars Pathfinder

A classic, real failure mode: a **low**-priority thread holds a lock that a **high**-priority
thread needs; a **medium**-priority thread preempts the low one, so the high-priority thread
is stuck waiting on a lock held by a thread that can't run. The high-priority deadline is
missed. (This literally caused Mars Pathfinder's repeated resets in 1997.) The fix is
**priority inheritance** — the lock-holder temporarily inherits the waiter's priority so it
can finish and release. The deeper lesson: **locks and hard real-time mix badly**, which is
*why* §8.3's lock-free ring buffer is the preferred pattern in flight code.

### 9.5 RTOS concepts — what the Pixhawk gives you that Linux doesn't

PX4 on your Pixhawk runs on **NuttX**, a real-time OS. What an RTOS guarantees that stock
Linux does not:

- **Bounded, deterministic interrupt and scheduling latency** — you know the worst-case time
  from "sensor interrupt" to "your handler runs."
- **Strict priority preemption** — the highest-priority ready task runs *now*, period.
- **Priority inheritance** built into its mutexes (§9.4).
- **No demand paging / no surprise page faults** stalling a loop.

That is why the hard 400 Hz+ control loop lives on the Pixhawk, while your VO/nav/perception —
soft-real-time, allocation-tolerant, compute-hungry — lives on the Pi 5 under PREEMPT_RT
Linux. Knowing which guarantees you need is how you draw that line correctly. The split is a
[systems-engineering tradeoff](01-first_principles_systems_engineering.md), made on the basis
of deadlines.

---

## 10. Worked example — track-fusion in C++, bound to Python

Time to do the thing this whole module is for: take a real, performance-critical module from
your Python stack — the **track-fusion filter** in `perception/` — and reimplement its hot
path in C++, then bind it back so the rest of your Python service calls it unchanged. This is
the exact pattern autonomy companies use: **Python orchestration, C++ inner loop.**

### 10.1 Why track fusion is the right candidate

Track fusion runs the Mahalanobis-gated, Bayesian association from
[Module 03 §3.4](03-mathematics.md) over every detection against every track,
every frame. In Python, with hundreds of tracks at a high IMX500 frame rate, it (a) allocates
constantly, (b) runs interpreted matrix math, and (c) jitters with the GC. It has a soft
deadline (keep up with the frame rate) and a clear, bounded computation — a textbook candidate
to push to C++.

### 10.2 The shape of the rewrite

```
   PYTHON (unchanged)                    C++ MODULE (new, fast, deterministic)
   ─────────────────                     ─────────────────────────────────────
   FastAPI service                       TrackFuser class:
   IMX500 detections  ──pybind11──►        • fixed-size pool of Tracks (no alloc, §9.3)
   world memory                            • Eigen for the covariance math (§4.1)
   constitution gate  ◄──results──         • SoA layout for cache (§7.1)
   decision log                            • SPSC ring buffer in (§8.3)
```

### 10.3 The C++ core (sketch)

```cpp
#include <Eigen/Dense>
#include <array>

struct Track {
    Eigen::Vector3f pos;        // state we care about in the hot loop
    Eigen::Matrix3f P;          // covariance (SPD, kept healthy — Module 03 §2.7)
    float confidence;
    bool active;
};

class TrackFuser {
    static constexpr int kMaxTracks = 256;
    std::array<Track, kMaxTracks> tracks_;   // ALL memory pre-allocated at construction (§9.3)

public:
    // Gate + associate one detection. No heap, bounded work, deterministic.
    int associate(const Eigen::Vector3f& z, const Eigen::Matrix3f& R) const {
        int best = -1;
        float best_d2 = kGateThreshold;            // chi-square gate (Module 03 §3.4)
        for (int i = 0; i < kMaxTracks; ++i) {
            if (!tracks_[i].active) continue;
            const Eigen::Vector3f y = z - tracks_[i].pos;     // innovation
            const Eigen::Matrix3f S = tracks_[i].P + R;       // innovation covariance
            const float d2 = y.transpose() * S.ldlt().solve(y); // Mahalanobis^2 (solve, not invert!)
            if (d2 < best_d2) { best_d2 = d2; best = i; }
        }
        return best;   // index of best-matching track, or -1 if none gated
    }
    // update(), spawn(), prune() omitted — same no-alloc discipline.
};
```

Note the §-callbacks baked in: pre-allocated array (§9.3), Eigen templates (§4.1), `ldlt().solve()`
instead of forming an inverse (Module 03 §2.4/§2.7), the chi-square gate (Module 03 §3.4). The
math you learned and the systems discipline you learned meet in one function.

### 10.4 The binding (pybind11)

```cpp
#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>     // automatic numpy ⇄ Eigen conversion
namespace py = pybind11;

PYBIND11_MODULE(track_fusion_py, m) {
    py::class_<TrackFuser>(m, "TrackFuser")
        .def(py::init<>())
        .def("associate", &TrackFuser::associate);  // numpy arrays in, int out
}
```

### 10.5 Calling it from your existing Python service

```python
import track_fusion_py
import numpy as np

fuser = track_fusion_py.TrackFuser()           # one C++ object, owned by Python
# ... inside the perception callback, unchanged orchestration:
idx = fuser.associate(detection_xyz, meas_cov) # runs the C++ hot loop, returns the matched track
if idx < 0:
    spawn_new_track(detection_xyz)             # Python still owns the high-level policy
```

### 10.6 The payoff — and how you *prove* it

The Python service, the constitution gate, and the decision log are untouched; only the hot
loop moved down to deterministic, allocation-free C++. But "it's faster" is a claim, and a
senior backs claims with evidence:

1. **Correctness first.** Golden-test the C++ output against the Python original on recorded
   detection logs — identical associations on the same inputs, bit-for-bit where the math
   allows. (This is the behavioral-fidelity check your
   [verification module](06-simulation-test-verification.md) demands of any
   rewrite.)
2. **Run the C++ tests under ASan+UBSan** (§6.2) and the threaded integration under TSan.
3. **Measure WCET, not average** (§9.2) — log per-call timing under worst-case track counts and
   confirm the tail latency fits the frame deadline. *Then* you can say it's real-time.

That sequence — port the hot loop, bind it back, prove correctness, prove timing — is the
repeatable move you'll make again for the VO inner loop and the EKF. Master it once here.

---

## 11. Practice this week

1. **RAII (§2.2).** Write a `ScopedTimer` that prints elapsed time in its destructor. Use it
   to instrument the track-fusion loop. Feel how the destructor *always* runs.
2. **Smart pointers & moves (§3).** Write a function returning a `std::unique_ptr<Estimator>`;
   try to copy it (compile error), then move it (works). Internalize move-only ownership.
3. **Sanitizers (§6).** Deliberately write an off-by-one array access and a use-after-free.
   Build with `-fsanitize=address,undefined` and read the reports. Memorize what they look
   like so you recognize them under pressure.
4. **Cache layout (§7.1).** Implement the track loop once as Array-of-Structures and once as
   Structure-of-Arrays; benchmark both at 256 tracks. Measure the cache effect yourself.
5. **Concurrency (§8.3).** Implement the SPSC ring buffer. Feed it from a producer thread,
   drain it from a consumer thread, and run the whole thing under **TSan**. Get it to green.
6. **Real-time (§9).** Instrument your current Python track fusion: log per-frame latency for
   a minute and plot the histogram. Find the GC/allocation spikes. *That tail is the reason
   this module exists.*
7. **The rewrite (§10).** Port the `associate()` hot path to C++, bind it with pybind11, and
   golden-test it against the Python version on a recorded log. Ship Python-orchestration +
   C++-inner-loop.

When these are routine, you can read PX4's C++ without flinching and move any prototype loop
onto the metal with a straight face — which is the bar these companies actually hire against.

---

## Sources & Citations

**C++ language & idioms**
- Stroustrup, B. — *A Tour of C++* (3rd ed.), Addison-Wesley (the fast, modern overview by the language's creator — start here).
- Meyers, S. — *Effective Modern C++*, O'Reilly (the canonical guide to C++11/14 idioms: smart pointers, move semantics, `auto`, concurrency).
- Stroustrup, B. — *The C++ Programming Language* (4th ed.), Addison-Wesley (the deep reference).
- Williams, A. — *C++ Concurrency in Action* (2nd ed.), Manning (threads, atomics, memory model, lock-free — the source for §8).
- ISO C++ Core Guidelines (Stroustrup & Sutter): https://isocpp.github.io/CppCoreGuidelines/

**Computer systems**
- Bryant, R. & O'Hallaron, D. — *Computer Systems: A Programmer's Perspective* (CS:APP), Pearson (memory hierarchy, processes, linking, the machine model behind §7).
- Tanenbaum & Bos — *Modern Operating Systems*, Pearson (scheduling, processes vs threads, syscalls).
- Drepper, U. — *What Every Programmer Should Know About Memory* (free PDF) — the deep dive behind §7.1.

**Real-time & embedded**
- Liu, J. — *Real-Time Systems*, Prentice Hall (deadlines, scheduling theory, WCET, priority inversion).
- Buttazzo, G. — *Hard Real-Time Computing Systems*, Springer (scheduling algorithms, the formal real-time foundation).
- Reeves, G. — *What Really Happened on Mars Pathfinder* (the canonical priority-inversion case study): https://www.cs.unc.edu/~anderson/teach/comp790/papers/mars_pathfinder_long_version.html

**Rust (the safety alternative)**
- Klabnik & Nichols — *The Rust Programming Language* (free: https://doc.rust-lang.org/book/) — ownership, borrowing, fearless concurrency.

**Build, tooling & binding**
- CMake documentation: https://cmake.org/cmake/help/latest/
- Eigen (linear algebra for flight code): https://eigen.tuxfamily.org
- pybind11 (C++ ⇄ Python binding, used in §10): https://pybind11.readthedocs.io
- Clang/GCC sanitizers (ASan/UBSan/TSan): https://clang.llvm.org/docs/AddressSanitizer.html

**Flight-software source to read**
- PX4 Autopilot (C++ flight stack on NuttX, runs on your Pixhawk): https://github.com/PX4/PX4-Autopilot
- NuttX RTOS: https://nuttx.apache.org

---

*End of Module 04. Inline references to the FastAPI service, `perception/` track fusion, the
IMX500 path, the VO inner loop, the constitution gate, and the hash-chained decision log point
at the author's own `pixhawk/drone/` project and are kept as code references. Do the §10
rewrite for real — port one hot loop, bind it, prove correctness and timing — because the gap
between knowing this module and having shipped it is the entire difference these companies pay
for.*
