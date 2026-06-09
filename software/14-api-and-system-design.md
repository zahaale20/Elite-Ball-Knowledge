# API & System Design — Designing Software That Scales and Lasts

> **Why this exists.** Software systems live or die at their seams. A perception module, a planner, a ground station, a fleet-management backend — each is built by a different team on a different schedule, and the only thing holding them together is the *interfaces* between them. A well-designed API is a contract that lets those teams move independently for years; a badly designed one is a tax paid on every future change, a source of outages, and eventually the reason a system gets thrown away and rewritten. Beyond the interface, *system design* is the discipline of arranging components, data stores, and message flows so the whole thing stays fast, available, and affordable as load grows from ten vehicles to ten thousand. This is also the skill that gatekeeps senior engineering roles: the system-design interview is where companies decide whether you can be trusted to architect, not just code. This module makes you fluent in both the craft and the framework.

> **What mastering it makes you.** The engineer who designs an API that teams are still happily building on five years later, who can take "build a telemetry ingestion system for 10,000 vehicles" and produce a defensible architecture with explicit tradeoffs on a whiteboard, and who reasons about consistency, latency, and failure the way a structural engineer reasons about load paths.

API and system design is where the first-principles decomposition of [01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md) is applied to software boundaries, and where the distributed-systems theory of [05_distributed_systems_comms_mesh.md](../foundations/05-distributed_systems_comms_mesh.md) becomes concrete design choices. The reliability targets of [09-software-observability-and-sre.md](09-observability-and-sre.md) are what your design must meet; the orchestration of [10-software-cloud-and-kubernetes.md](10-cloud-and-kubernetes.md) is where it runs; the performance budgets of [13-software-performance-engineering.md](13-performance-engineering.md) are what each call must respect. This module is the architectural keystone of the "Software, Compute & Infrastructure" band and is the single most valuable preparation for the senior-engineering interviews in [03-career-software-engineering.md](../career/03-software-engineering.md). It pairs with [15-software-testing-and-verification-deep.md](15-testing-and-verification-deep.md) (testing the contracts you design).

---

## 1. What makes an interface good

An API (Application Programming Interface) is a *contract*: a promise about what a caller can rely on, independent of how the implementation works. The defining property of a good contract is that it lets the two sides change independently. The principles, in rough priority order:

- **Hide implementation; expose intent.** The caller should see *what* they can do, never *how* it's done. Every implementation detail you leak becomes a thing you can never change. This is information hiding (Parnas) applied to software boundaries.
- **Make the easy thing correct and the wrong thing hard.** Good APIs guide callers into the pit of success — sensible defaults, types that make illegal states unrepresentable.
- **Consistency over cleverness.** Uniform naming, ordering, and error conventions mean a caller who learns one endpoint can guess the rest.
- **Minimal surface area.** Every public method is a forever-promise. The smallest API that satisfies the use cases is the best one; you can always add later, but you can never quietly remove.
- **Hard to misuse.** Joshua Bloch's test: the signature itself should resist error. Prefer `transfer(from, to, amount)` with distinct types over three interchangeable strings.

The litmus test for any interface: *can I change the implementation completely without any caller noticing?* If yes, the abstraction is sound. If a caller depends on a side effect, an ordering, or a leaked field, the seam is already cracked.

---

## 2. Synchronous styles: REST vs. gRPC vs. GraphQL

Most service-to-service communication is request/response. Three dominant styles, each with a clear niche.

| | **REST (HTTP/JSON)** | **gRPC (HTTP/2 + Protobuf)** | **GraphQL** |
|---|---|---|---|
| Data format | JSON (human-readable) | Protocol Buffers (binary) | JSON over a query language |
| Contract | OpenAPI (optional) | `.proto` (mandatory, typed) | Schema (typed) |
| Performance | Good | Excellent (binary, multiplexed, streaming) | Variable |
| Best for | Public/web APIs, broad reach | Internal microservices, low latency, streaming | Aggregating many sources for varied clients |
| Streaming | Awkward (SSE/polling) | First-class (bidirectional) | Subscriptions |
| Browser-native | Yes | No (needs gRPC-Web proxy) | Yes |

**REST** organizes the world as *resources* identified by URLs, manipulated with HTTP verbs. Its discipline is using the protocol correctly:

```
GET    /v1/vehicles/074            → fetch (safe, cacheable, no side effects)
GET    /v1/vehicles?status=active  → list/filter (paginate the result!)
POST   /v1/vehicles                → create (returns 201 + Location)
PUT    /v1/vehicles/074            → full replace (idempotent)
PATCH  /v1/vehicles/074            → partial update
DELETE /v1/vehicles/074            → remove (idempotent)
```

HTTP status codes are part of the contract: `2xx` success, `4xx` *you* (the caller) erred — don't retry unchanged, `5xx` *we* (the server) erred — retry may help. Conflating them (returning `200` with an error body) breaks every generic client and proxy.

**gRPC** defines a strongly-typed contract in a `.proto` file, generates client/server stubs in any language, and rides binary Protobuf over multiplexed HTTP/2 — making it the default for internal, latency-sensitive, high-volume service meshes and for streaming telemetry:

```protobuf
service TelemetryService {
  rpc StreamTelemetry(stream TelemetryPoint) returns (Ack);   // client streaming
  rpc GetVehicle(VehicleId) returns (Vehicle);
}
message TelemetryPoint { string vehicle_id = 1; double lat = 2; double lon = 3;
                         double alt = 4; int64 ts_ms = 5; }   // field numbers are the contract
```

The Protobuf field *numbers* (not names) are the wire contract — which is the key to gRPC's clean versioning story (Section 4). **GraphQL** lets clients ask for exactly the fields they want in one round trip, solving over- and under-fetching for diverse front ends — at the cost of server complexity and harder caching. Choose by the question "who is the caller and what do they need," not by fashion.

---

## 3. Idempotency — the property that makes networks survivable

Networks lose messages. A client sends "charge $50 / arm the payload / create the order," the request succeeds, but the *response* is lost — so the client retries. Without idempotency, the action happens twice. **Idempotency** is the property that performing an operation N times has the same effect as performing it once, and it is the single most important reliability property in distributed API design.

```
Client                    Server
  │  POST /transfer  ───────►│  $50 moved ✓
  │  (response lost)    ✗◄────┤
  │  POST /transfer  ───────►│  ← without idempotency: $100 moved! BUG
  │  (retry)
```

The standard mechanism is an **idempotency key**: the client generates a unique key per logical operation and sends it; the server records "I've processed key K → here's the result," and a retry with the same key returns the *stored* result instead of re-executing.

```
POST /v1/transfers
Idempotency-Key: 9f1c-uas074-arm-2026-06-09T14:22  ← same key on every retry
{ "amount": 50, "to": "..." }

Server logic:
  if seen(key): return stored_result(key)     # retry → no double effect
  result = execute(request)
  store(key, result); return result
```

Note that HTTP semantics already encode idempotency expectations: `GET`, `PUT`, `DELETE` are *defined* as idempotent; `POST` is not — which is exactly why `POST` needs an explicit idempotency key. Designing every state-changing operation to be safely retryable is what lets clients, load balancers, and message queues retry freely — the foundation of at-least-once delivery and resilient systems. This is the API-level expression of the fault tolerance discussed in [05_distributed_systems_comms_mesh.md](../foundations/05-distributed_systems_comms_mesh.md).

---

## 4. Versioning & evolution — APIs are forever

The moment another team depends on your API, you can no longer change it freely. Versioning is how you evolve a contract without breaking existing callers. The distinction that governs everything:

- **Backward-compatible (non-breaking)** changes — add an *optional* field, add a new endpoint, add a new enum value clients can ignore. Old clients keep working. Do these freely.
- **Backward-incompatible (breaking)** changes — remove or rename a field, change a type, make an optional field required, change semantics. These break existing callers and require a new version.

```
Safe (additive):                    Breaking (needs new version):
  + add optional "battery_pct"        − remove "voltage"
  + add GET /v1/vehicles/{id}/health  − rename "lat" → "latitude"
  + add enum value GRACEFUL_LAND      − change "altitude" m → ft
```

Strategies, in rough order of preference:

1. **Additive evolution (best)** — design for extension so most changes are non-breaking. Protobuf shines here: new fields get new numbers, old clients ignore unknown fields, and you *never reuse a field number*. This is why gRPC systems can evolve for years without "v2."
2. **URI versioning** — `/v1/`, `/v2/`. Explicit and cache-friendly; common for public REST APIs. Run v1 and v2 side by side during a deprecation window.
3. **Header / media-type versioning** — `Accept: application/vnd.api.v2+json`. Cleaner URLs, less discoverable.

Whatever you choose, the professional obligations are: a published **deprecation policy** (how long old versions live), **never breaking within a major version**, and clear migration docs. Treat the contract as a public promise — because to the teams depending on it, it is.

---

## 5. The scaling toolkit — primitives of system design

When load grows, you reach for a small set of well-understood primitives. Knowing what each buys *and costs* is the core of system design.

| Primitive | What it buys | What it costs |
|---|---|---|
| **Horizontal scaling** | More throughput by adding stateless replicas | Requires statelessness; coordination |
| **Load balancer** | Spreads traffic, removes dead instances | A component to make HA itself |
| **Caching** | Massive read latency/throughput win | Staleness; invalidation is *hard* |
| **CDN** | Serves static/edge content near users | Only for cacheable content |
| **Replication** | Read scaling + durability/availability | Replication lag, consistency questions |
| **Sharding/partitioning** | Scales writes & data beyond one machine | Cross-shard queries are painful; rebalancing |
| **Message queue** | Decoupling, buffering, async work, leveling spikes | Eventual consistency; delivery semantics |
| **Rate limiting** | Protects from overload & abuse | Must choose limits, handle rejection |

Two ideas dominate the toolkit:

**Caching** is the highest-leverage performance move and the hardest to get right — "there are only two hard things in computer science: cache invalidation and naming things." A cache trades freshness for speed; the design questions are *where* (client, CDN, app-tier, database), *eviction* (LRU/LFU/TTL), and *invalidation* (the part that causes bugs). Cache only what tolerates staleness, and make the staleness window explicit.

**Asynchronous messaging** decouples producers from consumers via a queue or log (Kafka, NATS, SQS, RabbitMQ). A telemetry ingester writes to a log and returns immediately; downstream consumers (storage, alerting, ML training) process at their own pace. This levels traffic spikes, isolates failures, and enables independent scaling — at the price of **eventual consistency** and a hard choice of delivery semantics:

```
at-most-once   : may drop, never duplicate   (fine for high-rate sensor samples)
at-least-once  : never drop, may duplicate   (default; REQUIRES idempotency, §3)
exactly-once   : the holy grail; expensive, narrow, often "effectively-once" via dedup
```

The recurring lesson: **every scaling primitive trades a property you had for one you need.** There is no free scaling — only deliberate exchanges, which is precisely the systems-engineering reasoning of [01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md).

---

## 6. Consistency, availability, and the laws you can't cheat

Distributed design runs into theorems, not preferences. **CAP** states that when the network *partitions* (and it will), a system must choose between **Consistency** (every read sees the latest write) and **Availability** (every request gets a response). You cannot have both during a partition.

```
        Partition happens. You must pick:
   CP (consistency)              AP (availability)
   refuse/err to avoid           answer with possibly
   stale reads                   stale data
   e.g. etcd, ZooKeeper,         e.g. Cassandra, DynamoDB,
   leader-based DBs              DNS, shopping carts
```

The mature view is **PACELC**: *if* Partitioned, trade A vs C; *else* (normal operation) trade Latency vs Consistency. Strong consistency costs latency even when the network is healthy, because it requires coordination (consensus, quorums). Most real systems therefore live on a **spectrum** — strong consistency where correctness demands it (a vehicle's armed/disarmed state, a financial ledger), eventual consistency where availability and latency matter more (telemetry history, a fleet dashboard). The design skill is knowing *which data needs which*, per field, not per system.

This is where idempotency (Section 3) and async messaging (Section 5) pay off: they are how you build *available, eventually-consistent* systems that still behave correctly under retries and reordering.

---

## 7. The system-design interview framework

Senior interviews ask open-ended design questions ("design a URL shortener," "design telemetry ingestion for 10,000 vehicles") to see whether you reason about tradeoffs. It is not about the "right" answer — it is about structured thinking. A reliable framework:

```
1. CLARIFY (req'ts)   ──►  Functional: what must it do?
   2-3 min                 Non-functional: scale, latency, consistency, availability?
                           Pin down: read/write ratio, peak QPS, data size.
2. ESTIMATE            ──►  Back-of-envelope: QPS, storage/day, bandwidth.
   (Little's law, capacity math from §5 and 88-...)
3. API / DATA MODEL   ──►  Define the key endpoints (§2) and the schema.
4. HIGH-LEVEL DESIGN  ──►  Boxes & arrows: clients → LB → services → stores/queues.
5. DEEP-DIVE          ──►  Pick the hard part (sharding? caching? consistency?)
                           and go deep with explicit tradeoffs.
6. BOTTLENECKS        ──►  Where does it break at 10×? Single points of failure?
                           How do you observe it (88-...)? How does it degrade?
```

Worked sketch — *telemetry ingestion for 10,000 vehicles at 10 Hz*:

- **Estimate:** $10{,}000 \times 10 = 100{,}000$ writes/s; each point ~50 bytes → 5 MB/s → ~430 GB/day. This number drives every later choice.
- **Ingest path:** vehicles → gRPC client-streaming (Section 2) → stateless ingest service behind a load balancer → append to a partitioned log (Kafka), partitioned by `vehicle_id` so one vehicle's stream is ordered. Return immediately (async, Section 5).
- **Storage:** a time-series database (sharded by time + vehicle) for the 100k/s write load; reads are mostly recent-window and analytical.
- **Consistency:** telemetry history is **AP/eventually consistent** (Section 6) — a dashboard a second stale is fine; *command* paths (arm/disarm) are a separate, strongly-consistent service.
- **Reliability:** at-least-once delivery + idempotent writes keyed on `(vehicle_id, ts)` (Section 3) so retries don't duplicate points; SLOs and burn-rate alerts per [09-software-observability-and-sre.md](09-observability-and-sre.md).
- **Bottleneck at 10×:** the log partitions and the time-series write path; mitigate with more partitions and pre-aggregation (downsampling) for old data.

Every decision is justified by a number and a tradeoff. That is what the interview — and the actual job — is testing.

---

## 8. Design for change and failure — the senior mindset

The throughline of this module is that **good design optimizes for the future, not the demo.** Two disciplines separate senior architects from competent coders:

- **Design for change.** Requirements will shift; the question is whether your seams let you adapt cheaply. Stable interfaces (Section 1) and additive evolution (Section 4) are how a system survives years of changing requirements without a rewrite. Loose coupling (async messaging, clear contracts) means a change in one service doesn't ripple through ten others.
- **Design for failure.** Everything fails — machines, networks, dependencies, your own deploys. Resilient design assumes it: timeouts on every remote call (never wait forever), retries *with backoff and jitter* on idempotent operations, **circuit breakers** that stop hammering a dead dependency, **graceful degradation** (serve stale cache or reduced features rather than nothing), and **bulkheads** that isolate failures so one overloaded subsystem can't sink the rest. A system that assumes its dependencies are reliable *is* the outage waiting to happen.

The deepest principle, shared with [01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md): you are not designing a static artifact, you are designing something that must evolve and degrade gracefully under conditions you cannot fully predict. The interfaces you draw and the failure modes you plan for are load-bearing decisions that determine whether the system lasts five years or gets rewritten in eighteen months. Master that, and you are no longer writing code — you are architecting systems.

---

## Sources & further study

- **Martin Kleppmann, *Designing Data-Intensive Applications*** — the single most important systems-design book of the decade; consistency, replication, partitioning, and the theory behind it all. Read it twice.
- **Alex Xu, *System Design Interview*, Vol. 1 & 2** — the practical interview framework with worked problems; the fastest path to interview-ready.
- **Sam Newman, *Building Microservices*** — service boundaries, contracts, and the organizational reality of distributed systems.
- **Joshua Bloch, "How to Design a Good API and Why It Matters"** (talk + paper) — the definitive short treatment of interface design.
- **Roy Fielding's dissertation, Ch. 5** — the actual definition of REST (most "REST" APIs aren't).
- **The gRPC and Protocol Buffers documentation** — for the typed-contract, additive-evolution model.
- **Google API Design Guide (AIP)** — a battle-tested, opinionated style guide for resource-oriented APIs.
- **Brendan Burns, *Designing Distributed Systems*** — patterns that connect this module to [10-software-cloud-and-kubernetes.md](10-cloud-and-kubernetes.md).

> Framing note: Code is where you spend your hours; interfaces and architecture are where you spend your *years*. A clever function can be rewritten in an afternoon, but a bad API contract or a wrong consistency choice metastasizes through every team that builds on it and is paid for in outages and rewrites long after you've forgotten you made it. The engineers who get trusted to design systems are the ones who think in contracts, tradeoffs, and failure modes — and that is exactly the muscle this module builds.
