# Distributed Systems Deep Dive — Consensus, Consistency & Failure

> **Why this exists.** A single autonomous vehicle is a control problem; a fleet of vehicles,
> ground stations, sensors, and operators is a **distributed system** — and distributed systems
> fail in ways that no amount of single-node correctness can prevent. Messages are lost,
> reordered, and duplicated; clocks disagree; nodes crash and come back with stale state;
> networks partition exactly when the mission needs them most. The engineers who build Lattice,
> Hivemind, and any real command-and-control fabric are paid to make many machines agree on
> *what is true* and *what to do* while the network is being actively degraded. You cannot bolt
> consistency on at the end; it is a property of the architecture from the first line.
>
> **What mastering it makes you.** The engineer who knows precisely which guarantees a system
> can and cannot offer — who can say "this is CP, it will refuse writes during a partition" or
> "this is AP, it will accept writes and reconcile later," and design accordingly; who reaches
> for Raft when they need a replicated log, CRDTs when they need partition-tolerant merge, and
> idempotency when they need exactly-once *effects* on top of at-least-once delivery.

This module is the software backbone of the mesh systems in
[05_distributed_systems_comms_mesh.md](05_distributed_systems_comms_mesh.md), the durable store
behind the world model in [20-autonomy-ml-ai.md](20-autonomy-ml-ai.md), and the reliability
floor that the real-time code of [04-foundations-modern-cpp-realtime.md](04-foundations-modern-cpp-realtime.md)
runs on once it leaves a single box. It connects to the networking physics of
[83-software-networking-and-protocols.md](83-software-networking-and-protocols.md), the storage
internals of [84-software-databases-and-data-engineering.md](84-software-databases-and-data-engineering.md),
the engineering practice of [12-career-software-engineering.md](12-career-software-engineering.md),
and the adversarial threat models of [36-trust-safety-opsec-and-digital-resilience.md](36-trust-safety-opsec-and-digital-resilience.md)
and [86-software-cybersecurity-engineering.md](86-software-cybersecurity-engineering.md). The
GPU and RTOS siblings ([81-software-gpu-and-parallel-computing.md](81-software-gpu-and-parallel-computing.md),
[82-software-real-time-operating-systems.md](82-software-real-time-operating-systems.md)) handle
the *fast* path; this module handles the *agreed* path.

---

## Table of Contents

1. [The eight fallacies and the two hard problems](#1-the-eight-fallacies-and-the-two-hard-problems)
2. [Time, clocks, and ordering](#2-time-clocks-and-ordering)
3. [Consistency models](#3-consistency-models)
4. [CAP, PACELC, and the real tradeoff](#4-cap-pacelc-and-the-real-tradeoff)
5. [Consensus — Paxos and Raft](#5-consensus--paxos-and-raft)
6. [Replication and partitioning](#6-replication-and-partitioning)
7. [Failure detection and recovery](#7-failure-detection-and-recovery)
8. [Idempotency, exactly-once, and sagas](#8-idempotency-exactly-once-and-sagas)
9. [Practice this week](#9-practice-this-week)
10. [Sources & further study](#10-sources--further-study)

---

## 1. The eight fallacies and the two hard problems

Peter Deutsch's **fallacies of distributed computing** are the assumptions that single-machine
intuition smuggles in and that the network then punishes:

1. The network is reliable. 2. Latency is zero. 3. Bandwidth is infinite. 4. The network is
secure. 5. Topology doesn't change. 6. There is one administrator. 7. Transport cost is zero.
8. The network is homogeneous.

Every one of these is *false* in a fielded mesh, and the failure of each maps to a real bug
class. "The network is reliable" → you must handle loss, so you need retries; retries → you
need idempotency; idempotency → you need stable request IDs; and so the architecture grows out
of refusing the fallacy.

The two genuinely hard problems beneath everything else:

- **Agreement under uncertainty.** Two nodes cannot distinguish a crashed peer from a slow peer
  from a partitioned link. This is the root of the FLP impossibility result: in a purely
  asynchronous system, no deterministic protocol can guarantee consensus if even one node may
  fail. Real systems escape FLP by adding *timeouts* (partial synchrony) — accepting that they
  may occasionally be wrong about liveness, never about safety.
- **Ordering without a global clock.** There is no "now" shared across machines, so "which
  event happened first" is not always answerable. You replace wall-clock time with *logical*
  causality.

```
 Single machine            Distributed system
 ──────────────────────    ─────────────────────────────────────
 function call             message that may be lost/dup/reordered
 shared memory             replicated state that can diverge
 one clock                 many clocks that drift
 crash = whole thing dies  partial failure: some nodes alive, some not
 deterministic             nondeterministic interleavings
```

The defining feature is **partial failure**: the thing you call is up, but the thing it depends
on is down, and you find out *late*, via a timeout, not via an exception.

---

## 2. Time, clocks, and ordering

### 2.1 Physical clocks drift

Quartz oscillators drift on the order of $10$–$100$ ppm, i.e. up to ~$8.6$ s/day uncorrected.
NTP disciplines clocks to ~$1$–$10$ ms over WAN, PTP (IEEE 1588) to sub-microsecond on a LAN
with hardware timestamping. But even perfectly synced clocks have **uncertainty** $\varepsilon$:
you never know the true time, only $[t-\varepsilon, t+\varepsilon]$. Google Spanner's TrueTime
makes this explicit and *waits out* the uncertainty (`commit_wait`) to guarantee external
consistency.

### 2.2 Logical clocks (Lamport)

A Lamport clock is a counter $L$ per node with two rules:

- On any local event or send: $L \leftarrow L + 1$.
- On receive of a message carrying timestamp $L_m$: $L \leftarrow \max(L, L_m) + 1$.

This guarantees: if $a \rightarrow b$ (a *happens-before* b) then $L(a) < L(b)$. The converse
does **not** hold — equal-ordering does not imply causality. Lamport gives a total order
consistent with causality, but cannot detect concurrency.

### 2.3 Vector clocks

A vector clock $V$ is an array of counters, one per node. Node $i$ increments $V[i]$ on each
event; on receive it takes the elementwise max then increments its own. Now:

$$
a \rightarrow b \iff V(a) < V(b), \qquad a \parallel b \iff V(a) \not< V(b) \wedge V(b) \not< V(a)
$$

Vector clocks **detect concurrency** (the $\parallel$ case), which is exactly what Dynamo-style
stores need to find conflicting writes. Cost: $O(N)$ space per event.

```python
# Vector clock merge for conflict detection in a replicated store.
def merge(local: dict[str, int], incoming: dict[str, int]) -> dict[str, int]:
    # Take the elementwise maximum of the two version vectors.
    out = dict(local)
    for node, c in incoming.items():
        out[node] = max(out.get(node, 0), c)
    return out

def concurrent(a: dict[str, int], b: dict[str, int]) -> bool:
    # True when neither vector dominates the other -> a genuine conflict.
    a_le_b = all(a.get(n, 0) <= b.get(n, 0) for n in set(a) | set(b))
    b_le_a = all(b.get(n, 0) <= a.get(n, 0) for n in set(a) | set(b))
    return not a_le_b and not b_le_a
```

---

## 3. Consistency models

Consistency is a **contract** about what reads may observe given prior writes. Stronger models
are easier to program against but cost latency and availability.

| Model | Guarantee | Cost | Example |
|---|---|---|---|
| Linearizable | Every op appears to take effect atomically at a point between call and return; reads see latest | High latency, no AP | etcd, Spanner |
| Sequential | All nodes see ops in *some* single order, not necessarily real-time | Medium | older shared-memory |
| Causal | Causally related ops seen in order; concurrent ops may differ per node | Low, partition-tolerant | COPS, some CRDT stores |
| Read-your-writes | You see your own writes | Session-scoped | many web stores |
| Eventual | Replicas converge if writes stop | Lowest | Dynamo, Cassandra (default) |

**Linearizability vs serializability** is a common confusion. Linearizability is about *single
objects* and real-time ordering. Serializability is about *transactions* over multiple objects
executing as if serial. **Strict serializability** is both. A system can be serializable but
not linearizable (a transaction can read a stale snapshot) and vice versa.

The practical rule: pick the **weakest** model that still makes the application correct, because
every step up the strength ladder is paid in coordination round-trips.

---

## 4. CAP, PACELC, and the real tradeoff

The CAP theorem (Brewer, proven by Gilbert & Lynch) states that during a network **P**artition
a system must choose between **C**onsistency (linearizability) and **A**vailability (every
request gets a non-error response):

$$
\text{Partition} \Rightarrow \neg(C \wedge A)
$$

CAP is often misread. It is *not* "pick two of three" all the time — partitions are not a
choice, they happen. The real statement: *when partitioned*, choose C or A. **PACELC** completes
it: **E**lse (no partition) you still trade **L**atency vs **C**onsistency.

```
 PACELC:  if (Partition) then  C  or  A
          else                 L  or  C
```

- **CP systems** (etcd, ZooKeeper, Spanner): refuse writes on the minority side of a partition
  to never violate consistency. The fleet's *authoritative* state (who owns which task) wants
  CP — better to stall than to double-assign a strike.
- **AP systems** (Cassandra, Dynamo): accept writes everywhere, reconcile later. The fleet's
  *sensor track* state wants AP — a slightly stale contact is better than no contact.

This is the central architectural decision in any C2 system: **split state by its CAP needs.**

---

## 5. Consensus — Paxos and Raft

Consensus is the problem of getting a set of nodes to agree on a single value (or a sequence of
values — a *replicated log*) despite crashes. Solve replicated log and you can build a
replicated state machine: feed the same ordered commands to every replica and they stay
identical.

### 5.1 Paxos

Single-decree Paxos has proposers, acceptors, and learners, and proceeds in two phases:

1. **Prepare(n):** proposer picks ballot $n$, asks a majority of acceptors to promise not to
   accept anything lower. Acceptors reply with any value they've already accepted.
2. **Accept(n, v):** proposer sends value $v$ (the highest previously-accepted value, or its
   own if none) to a majority. If a majority accepts, $v$ is chosen.

Safety comes from **majority quorums**: any two majorities intersect, so a value once chosen is
seen by every future round. Paxos is correct but notoriously hard to implement; Multi-Paxos
amortizes phase 1 by electing a stable leader.

### 5.2 Raft — Paxos you can actually build

Raft (Ongaro & Ousterhout) was designed for *understandability*. It decomposes consensus into
**leader election**, **log replication**, and **safety**.

```
   follower ──timeout──▶ candidate ──majority votes──▶ leader
      ▲                      │                            │
      └──────── higher term / new leader ────────────────┘
```

- **Terms** are logical clock epochs; each term has at most one leader.
- A leader appends client commands to its log and replicates via `AppendEntries`. An entry is
  **committed** once stored on a majority; committed entries are applied to the state machine.
- **Election safety:** a candidate only wins if its log is at least as up-to-date as a majority,
  so a leader never lacks a committed entry. The "log matching" property guarantees logs stay
  consistent prefixes.

```rust
// Raft AppendEntries handler skeleton (follower side), illustrating the safety checks.
fn append_entries(&mut self, req: AppendEntries) -> AppendReply {
    // Reject stale leaders: never accept a term older than our own.
    if req.term < self.current_term {
        return AppendReply { term: self.current_term, success: false };
    }
    // A valid heartbeat resets the election timeout and recognizes the leader.
    self.reset_election_timer();
    self.leader_id = Some(req.leader_id);

    // Log-matching: our entry at prev_log_index must match the leader's term.
    if !self.log_matches(req.prev_log_index, req.prev_log_term) {
        return AppendReply { term: self.current_term, success: false };
    }
    // Truncate conflicts and append new entries, then advance commit index.
    self.append_and_truncate(req.entries);
    if req.leader_commit > self.commit_index {
        self.commit_index = req.leader_commit.min(self.last_log_index());
    }
    AppendReply { term: self.current_term, success: true }
}
```

Quorum size matters: with $2f+1$ nodes you tolerate $f$ failures. Five nodes tolerate two
failures and is the common production choice (three is the minimum useful, seven rarely worth
the extra round-trip latency).

---

## 6. Replication and partitioning

**Replication** (copies of the same data for availability/durability) and **partitioning** aka
**sharding** (splitting data across nodes for scale) are orthogonal and usually combined.

### 6.1 Replication strategies

- **Single-leader (primary/replica):** all writes to leader, reads from replicas. Simple, but
  replicas lag (replication lag breaks read-your-writes unless you route reads carefully).
- **Multi-leader:** writes accepted at several leaders, asynchronously merged. Good for
  multi-region/multi-site, but introduces **write conflicts** you must resolve (last-write-wins
  loses data; better: CRDTs or app-level merge).
- **Leaderless (Dynamo):** clients write to $W$ replicas and read from $R$; if $W + R > N$ the
  read and write quorums overlap, so a read sees the latest write. Tunable consistency.

$$
W + R > N \;\Rightarrow\; \text{quorum overlap (strong-ish reads)}
$$

### 6.2 Partitioning

- **Hash partitioning:** key → hash → shard. Even load, but range scans hit every shard.
- **Range partitioning:** keys grouped by range. Efficient scans, risk of hot ranges.
- **Consistent hashing** places nodes and keys on a ring so adding/removing a node moves only
  $K/N$ keys, not all of them — essential for elastic clusters. Virtual nodes smooth the load.

**Rebalancing** and **request routing** (a coordinator, a routing tier, or gossip) are the parts
that bite in production: a naive `hash(key) % N` reshuffles *everything* when $N$ changes.

---

## 7. Failure detection and recovery

You cannot fix what you cannot detect, and detection is fundamentally uncertain.

- **Heartbeats + timeouts:** the basic detector. Timeout too short → false positives (flapping);
  too long → slow detection. Tune to the network's tail latency, not its median.
- **Phi-accrual detector** (Cassandra/Akka): outputs a *suspicion level* $\varphi$ rather than a
  boolean, adapting to observed inter-arrival variance — far better than a fixed threshold on a
  jittery link.
- **Gossip / SWIM:** scalable membership and failure detection by randomized peer probing;
  $O(1)$ messages per node per round, detection in $O(\log N)$ rounds.

Recovery patterns: **write-ahead log + snapshots** for durable state; **lease**-based leadership
so a partitioned old leader steps down when its lease expires (avoiding split-brain double
leaders); **fencing tokens** (monotonic IDs) so a resurrected zombie's late writes are rejected.

```
 Split-brain prevention with fencing:
   storage rejects any write whose token < the highest token it has seen.
   old leader (token 33) ──write(33)──▶ REJECTED (storage saw 34)
   new leader (token 34) ──write(34)──▶ ACCEPTED
```

---

## 8. Idempotency, exactly-once, and sagas

"Exactly-once delivery" is essentially impossible over an unreliable network; what you can build
is **exactly-once *effects*** on top of **at-least-once delivery** plus **idempotency**.

- **Idempotent operations** produce the same result no matter how many times applied. Attach a
  unique request ID; the receiver deduplicates. `SET x=5` is naturally idempotent; `x += 1` is
  not — wrap it with a dedupe key.
- **Outbox pattern:** write the business change and the "message to send" in one local
  transaction, then a relay publishes the outbox — closing the gap where a crash sends a message
  but loses the DB write (or vice versa).
- **Sagas** replace distributed ACID transactions (which need 2PC and block on coordinator
  failure) with a sequence of local transactions plus **compensating actions**. If step 3 of a
  five-step workflow fails, run the compensations for steps 2 and 1.

```
 Saga:  reserve_vehicle ─▶ assign_task ─▶ notify_operator
          │ comp           │ comp           │
          ▼                ▼                ▼
        release         unassign         (best-effort)
```

Two-phase commit (2PC) gives atomicity but is a **blocking** protocol: if the coordinator dies
after `prepare`, participants hold locks indefinitely. Three-phase commit reduces blocking but
not under partitions. For fielded systems, prefer sagas + idempotency over 2PC.

---

## 9. Practice this week

1. Implement a single-decree Paxos and a 3-node Raft in the language of your choice; run them
   under a network simulator that drops, delays, and reorders 20% of messages, and prove no two
   nodes ever commit different values at the same index.
2. Build a leaderless KV store with tunable $N, W, R$; demonstrate that $W+R>N$ gives
   read-after-write and $W+R\le N$ does not.
3. Take a non-idempotent endpoint and make its *effects* exactly-once using a request-ID dedupe
   table and the outbox pattern; kill the process mid-write and show no duplicate or lost effect.
4. Inject a partition into a CP store (etcd) and an AP store (Cassandra) and document the
   observable behavior of each — which refuses, which diverges, how each reconciles.

---

## 10. Sources & further study

- **Kleppmann — *Designing Data-Intensive Applications (DDIA)*.** The single best book on
  replication, partitioning, transactions, and consistency for working engineers.
- **Burns — *Designing Distributed Systems*.** Patterns (sidecar, ambassador, scatter-gather) for
  building real distributed services.
- **Ongaro & Ousterhout — *In Search of an Understandable Consensus Algorithm (Raft)*.** The
  paper; pair with the raft.github.io visualizations.
- **Lamport — *Time, Clocks, and the Ordering of Events* / *Paxos Made Simple*.** The originals.
- **Gilbert & Lynch — CAP proof; Abadi — *PACELC*.** The tradeoff stated rigorously.
- **Shapiro et al. — *Conflict-free Replicated Data Types (CRDTs)*.** Partition-tolerant merge.
- **Tanenbaum & van Steen — *Distributed Systems*.** The comprehensive textbook.
- **Jepsen analyses (jepsen.io).** Empirical consistency testing of real databases — humbling
  and educational, and a model for [06-foundations-simulation-test-verification.md](06-foundations-simulation-test-verification.md).

> Framing note: A distributed system is not a faster computer — it is a *negotiation* among
> machines that disagree about time, truth, and who is alive, conducted over a channel that lies.
> The engineers who build fleet-scale autonomy do not try to abolish that uncertainty; they
> name it, choose precisely which guarantees each piece of state needs, and design so that when
> the network is shot to pieces, the system degrades into a known, safe, recoverable state
> instead of an unknown one.
