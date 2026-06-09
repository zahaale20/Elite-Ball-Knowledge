# Real-Time Operating Systems — Determinism, Scheduling & WCET

> **Why this exists.** An autopilot that computes the perfect control output 5 ms too late has
> computed the wrong output. Flight control, motor commutation, sensor sampling, and safety
> interlocks are **hard real-time** problems where correctness is inseparable from timing: the
> answer must be right *and* on time, every time, or the vehicle oscillates, stalls, or falls
> out of the sky. A general-purpose OS like Linux optimizes average throughput and will happily
> let a high-priority control loop wait while it flushes a disk buffer. A real-time operating
> system optimizes the **worst case** and guarantees bounded latency. The engineer who
> understands RTOS scheduling, priority inversion, and worst-case execution time is the one who
> can promise — and prove — that the loop closes on time under every condition.
>
> **What mastering it makes you.** The engineer who picks rate-monotonic or EDF deliberately and
> can compute the schedulability bound; who recognizes priority inversion before it deadlocks a
> Mars rover; who measures jitter rather than averages; who bounds worst-case execution time
> instead of hoping; and who knows when a microcontroller RTOS, a PREEMPT_RT Linux, or a
> partitioned hypervisor is the right substrate.

This module is the timing foundation under the C++ real-time techniques of
[04-foundations-modern-cpp-realtime.md](../foundations/04-modern-cpp-realtime.md), the onboard
control of [25-autonomy-control-theory.md](../autonomy/25-control-theory.md) and
[23-autonomy-onboard-system.md](../autonomy/23-onboard-system.md), and the safety assurance of
[09-foundations-safety-assurance.md](../foundations/09-safety-assurance.md). It complements the
networking timing of [83-software-networking-and-protocols.md](83-networking-and-protocols.md),
contrasts with the throughput focus of [81-software-gpu-and-parallel-computing.md](81-gpu-and-parallel-computing.md),
sits inside the distributed timing of [80-software-distributed-systems-deep.md](80-distributed-systems-deep.md),
and reflects the engineering discipline of [12-career-software-engineering.md](../career/12-software-engineering.md).
Reliability and timing failures connect to [77-engineering-reliability-and-failure-analysis.md](../engineering/77-reliability-and-failure-analysis.md).

---

## Table of Contents

1. [What "real-time" actually means](#1-what-real-time-actually-means)
2. [The RTOS kernel](#2-the-rtos-kernel)
3. [Scheduling — RMS and EDF](#3-scheduling--rms-and-edf)
4. [Priority inversion and its fixes](#4-priority-inversion-and-its-fixes)
5. [Latency, jitter, and the sources of nondeterminism](#5-latency-jitter-and-the-sources-of-nondeterminism)
6. [Worst-case execution time (WCET)](#6-worst-case-execution-time-wcet)
7. [Choosing a real-time substrate](#7-choosing-a-real-time-substrate)
8. [Practice this week](#8-practice-this-week)
9. [Sources & further study](#9-sources--further-study)

---

## 1. What "real-time" actually means

Real-time does **not** mean fast — it means **deterministic**: the system's timing behavior is
predictable and bounded. A 1 kHz loop that *always* completes within 800 µs is real-time; a loop
that usually finishes in 50 µs but occasionally takes 5 ms is not.

| Class | Deadline miss consequence | Example |
|---|---|---|
| Hard real-time | Catastrophic failure | Flight control, motor commutation, airbag |
| Firm real-time | Result useless after deadline, no catastrophe | Frame in a video pipeline |
| Soft real-time | Degraded quality, value decays | UI responsiveness, telemetry display |

The defining metric is the **worst case**, not the average. A flight controller is specified by
its maximum loop latency and maximum jitter, because the airframe's stability margin
([25-autonomy-control-theory.md](../autonomy/25-control-theory.md)) is consumed by *delay*, and
delay is what the worst case measures.

---

## 2. The RTOS kernel

An RTOS is a small kernel whose primary job is **predictable scheduling**. Core features:

- **Preemptive priority scheduling:** the highest-priority ready task always runs; a higher
  task preempts a lower one immediately (bounded preemption latency).
- **Tasks/threads** with fixed or dynamic priorities, each with its own stack.
- **Deterministic primitives:** mutexes, semaphores, message queues, and event flags with
  *bounded* worst-case operation time — no unbounded data structures in the hot path.
- **Tickless or tick-based timing:** a hardware timer drives the scheduler; high-resolution
  timers enable precise periodic release.

```
 Tasks (priority high → low):     Scheduler picks highest-ready:
   T1 (1 kHz control)  ████        time ─▶
   T2 (100 Hz nav)       ██        T1▕T1▕  T1▕ T2 ▕T1▕ T3...
   T3 (10 Hz telemetry)    █       (T1 always preempts T2/T3)
```

Common RTOSes: **FreeRTOS** and **Zephyr** (microcontrollers), **VxWorks** and **QNX**
(avionics, certified), **RTEMS** (space). On Linux, **PREEMPT_RT** turns most of the kernel
preemptible to approach RTOS latencies on rich hardware.

A critical kernel concept is the **interrupt service routine (ISR)**: it must be short and
defer real work to a task (the "top half / bottom half" split), because time spent in an ISR is
time the scheduler cannot run anyone — it directly inflates worst-case latency for *every* task.

---

## 3. Scheduling — RMS and EDF

For periodic tasks with period $T_i$, deadline $D_i$ (often $=T_i$), and worst-case execution
time $C_i$, two classic algorithms dominate.

### 3.1 Rate-Monotonic Scheduling (RMS)

Fixed priorities assigned by **rate**: shorter period → higher priority. RMS is the *optimal
fixed-priority* algorithm. Liu & Layland's sufficient schedulability bound for $n$ tasks:

$$
U = \sum_{i=1}^{n} \frac{C_i}{T_i} \;\le\; n\left(2^{1/n} - 1\right)
$$

The bound is $1.0$ for $n=1$ and decreases to $\ln 2 \approx 0.693$ as $n \to \infty$. So if
total utilization is under ~69%, RMS *always* meets deadlines. Between 69% and 100% you need the
exact **response-time analysis** (iterate $R_i = C_i + \sum_{j \in hp(i)} \lceil R_i/T_j \rceil C_j$
to a fixed point and check $R_i \le D_i$).

### 3.2 Earliest-Deadline-First (EDF)

Dynamic priorities: the task with the nearest absolute deadline runs. EDF is **optimal** for
uniprocessors and schedulable iff:

$$
U = \sum_{i=1}^{n} \frac{C_i}{T_i} \;\le\; 1
$$

EDF achieves full 100% utilization — strictly better than RMS — but is harder to implement,
behaves worse under overload (cascading misses), and is less common in certified avionics where
RMS's predictability and simpler analysis are preferred.

| | RMS | EDF |
|---|---|---|
| Priority | Fixed (by rate) | Dynamic (by deadline) |
| Max utilization | ~0.69–1.0 | 1.0 |
| Overload behavior | Lower-rate tasks miss first (predictable) | Unpredictable cascade |
| Implementation | Simple | More complex |
| Certification | Widely used | Less common |

---

## 4. Priority inversion and its fixes

**Priority inversion** is when a high-priority task is blocked by a low-priority task holding a
shared resource — and a *medium*-priority task, by preempting the low task, indirectly delays the
high one indefinitely. This famously nearly killed the **Mars Pathfinder** mission in 1997: a
high-priority bus-management task blocked on a mutex held by a low-priority meteorological task,
which kept getting preempted by medium-priority comms, triggering watchdog resets.

```
 H (high)  ──wants mutex──▶ BLOCKED ......................... runs (finally)
 M (med)            ─────────── runs, preempting L ─────────
 L (low)   ─holds mutex─▶ preempted by M, can't release ─▶ releases
           inversion window: H waits on L, but M keeps L from running
```

Two standard fixes, both implemented in real RTOS mutexes:

- **Priority inheritance:** while L holds a mutex that H wants, L temporarily *inherits* H's
  priority, so M cannot preempt it. L releases, returns to its base priority, H proceeds. (This
  was the Pathfinder fix — toggled on remotely.)
- **Priority ceiling protocol:** each mutex has a *ceiling* = the highest priority of any task
  that may lock it; a task locking it runs at that ceiling. Prevents both inversion and
  deadlock, at the cost of needing static analysis of who locks what.

The engineering lesson: **never share an unprotected resource between tasks of different
priority without an inheritance/ceiling mutex**, and bound how long any critical section can be
held.

---

## 5. Latency, jitter, and the sources of nondeterminism

- **Latency:** time from an event (sensor sample, timer tick) to the response (control output).
- **Jitter:** variation in that latency across cycles. For control loops, *jitter is often worse
  than latency* — constant delay can be compensated in the controller; random delay cannot.

Sources of nondeterminism, roughly in order of severity on rich hardware:

```
 Source                         Mitigation
 ─────────────────────────────  ─────────────────────────────────────────
 Caches / TLB misses            lock cache lines, deterministic memory layout
 Page faults / swapping         mlockall(), pre-fault, no demand paging
 Dynamic memory (malloc)        pre-allocate pools; no malloc in the hot loop
 Interrupts / ISR storms        IRQ affinity, threaded IRQs, isolate CPUs
 OS scheduler / migration       SCHED_FIFO/RR, CPU pinning, isolcpus
 Branch misprediction, DVFS     disable frequency scaling, warm the path
 GC (managed languages)         avoid GC languages in hard real-time
```

On Linux PREEMPT_RT the recipe is: `mlockall` to lock memory, `SCHED_FIFO` priority, pin the
loop to an isolated core (`isolcpus`/`nohz_full`), disable CPU frequency scaling, and pre-fault
stacks — then *measure* with `cyclictest` and look at the maximum, not the mean.

```cpp
// Make a control thread real-time on PREEMPT_RT Linux: lock memory,
// raise priority, and pin to an isolated CPU so nothing migrates onto it.
void make_realtime(int core) {
    mlockall(MCL_CURRENT | MCL_FUTURE);          // never page out
    sched_param p{};
    p.sched_priority = 80;                        // high SCHED_FIFO priority
    pthread_setschedparam(pthread_self(), SCHED_FIFO, &p);
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(core, &set);                          // isolated, nohz_full core
    pthread_setaffinity_np(pthread_self(), sizeof(set), &set);
}
```

---

## 6. Worst-case execution time (WCET)

Schedulability analysis is only as honest as its $C_i$ — the **worst-case execution time**. WCET
is genuinely hard because modern CPUs are designed to be *fast on average*, not *predictable*:
caches, pipelines, branch predictors, and speculation make execution time data- and
history-dependent.

Two estimation approaches, usually combined:

- **Static analysis:** model the code's control-flow graph and the hardware (cache, pipeline)
  to derive a provable upper bound. Sound (never underestimates) but pessimistic; tools like
  aiT are used in DO-178C avionics.
- **Measurement-based:** run the code on real hardware with worst-case-ish inputs and take the
  maximum plus a safety margin. Realistic but unsound — you may never hit the true worst path.

```
 distribution of observed times       true WCET (may exceed all measurements)
        ▲                                         │
  count │      ▁▃▅█▅▃▁                             ▼
        │   ▁▃█████████▃▁_____________________  ?  | static bound
        └────────────────────────────────────────────▶ execution time
              measured max  ↑ add margin ↑     ↑ provable upper bound
```

Practices that make WCET tractable: avoid recursion and unbounded loops (bound every iteration
count); no dynamic allocation in real-time paths; single-path / constant-time code in the most
critical sections; lock or partition caches; and *budget* each task with margin so transient
overruns don't cascade. This is where real-time software meets the rigor of
[06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md).

---

## 7. Choosing a real-time substrate

```
 Need                                    Choose
 ──────────────────────────────────────  ─────────────────────────────────────
 Tiny MCU, hard RT, low power            FreeRTOS / Zephyr
 Certified avionics (DO-178C)            VxWorks / QNX / integrity, ARINC 653
 Mixed criticality on one box            Partitioning hypervisor (ARINC 653 / Jailhouse)
 Rich OS + soft/firm RT (Linux apps)     PREEMPT_RT Linux + isolcpus
 Space, open source                      RTEMS
```

**Mixed-criticality** systems — where a DO-178C Level A flight controller must coexist with a
non-critical mission computer — use **time and space partitioning** (ARINC 653): each partition
gets a guaranteed CPU time window and isolated memory, so a fault or overrun in the mission
computer cannot steal cycles or corrupt memory from the flight controller. This is the
architecture behind modern integrated modular avionics, and it ties directly to the safety cases
of [09-foundations-safety-assurance.md](../foundations/09-safety-assurance.md).

---

## 8. Practice this week

1. Implement three periodic tasks on FreeRTOS or Zephyr with periods 1/10/100 ms; compute the
   RMS utilization bound and confirm by measurement whether they meet deadlines; then push
   utilization past 0.69 and observe which task misses first.
2. Deliberately construct a priority-inversion scenario with a plain mutex, observe the high
   task starving, then enable priority inheritance and show the inversion window collapse.
3. Run `cyclictest` on stock Linux and on a PREEMPT_RT-tuned core (isolcpus, SCHED_FIFO,
   mlockall) and compare the *maximum* latency — not the average.
4. Take a control function, bound every loop, remove all dynamic allocation, and produce a
   measurement-based WCET with margin; argue why a static bound would be higher.

---

## 9. Sources & further study

- **Liu — *Real-Time Systems*.** The standard graduate text; RMS, EDF, response-time analysis.
- **Buttazzo — *Hard Real-Time Computing Systems*.** Rigorous scheduling theory with practical
  detail on inversion and resource access protocols.
- **Liu & Layland — *Scheduling Algorithms for Multiprogramming in a Hard-Real-Time
  Environment*.** The 1973 paper with the RMS bound.
- **Sha, Rajkumar & Lehoczky — *Priority Inheritance Protocols*.** The inversion fix, theory
  and proof.
- **Reeves — *What Really Happened on Mars* (Pathfinder retrospective).** The canonical priority
  inversion war story.
- **FreeRTOS / Zephyr / QNX documentation.** Real kernels you can run today.
- **Wilhelm et al. — *The Worst-Case Execution-Time Problem* (survey).** WCET methods and tools.

> Framing note: A real-time system is not a fast system — it is an *honest* one, where the
> worst case is bounded and proven rather than hoped for. The engineers who certify flight
> software do not optimize the average; they hunt the tail, kill every source of nondeterminism
> they can, bound the rest, and design so that when something overruns, it overruns inside a
> partition that cannot take the aircraft down with it.
