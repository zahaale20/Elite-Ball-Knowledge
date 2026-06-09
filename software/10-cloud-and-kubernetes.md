# Cloud & Kubernetes — Orchestrating Compute at Scale

> **Why this exists.** Autonomy does not stop at the vehicle. Behind every fleet of drones is a backplane of compute: services that ingest telemetry, run map builds, retrain perception models, serve mission plans, and fan results back out to the edge. That backplane has to survive machine failures, absorb traffic spikes during an operation, deploy new code dozens of times a day without dropping a connection, and do it on hardware you are renting by the second. Kubernetes is the operating system of that backplane — the layer that turns a pile of unreliable machines into one reliable computer. If you cannot reason about how a container gets scheduled, how a service finds its peers, or why your pod got evicted at 2 a.m., you do not control your own infrastructure; you are a tourist in it. This module makes you the engineer who owns the platform.

> **What mastering it makes you.** The person who can take a service from a laptop to a self-healing, autoscaling, multi-region deployment — and explain, to the dollar and the millisecond, what it costs and how fast it responds. Infrastructure fluency is the multiplier that lets a small team operate like a large one.

Cloud and Kubernetes are where the distributed-systems theory of [05_distributed_systems_comms_mesh.md](../foundations/05-distributed_systems_comms_mesh.md) becomes operational reality, and where the reliability practices of [09-software-observability-and-sre.md](09-observability-and-sre.md) are actually enforced. The first-principles decomposition of [01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md) is what keeps a cluster from becoming an incomprehensible mess, and the career leverage of platform skills is laid out in [03-career-software-engineering.md](../career/03-software-engineering.md). This module sits at the center of the "Software, Compute & Infrastructure" band and pairs with [14-software-api-and-system-design.md](14-api-and-system-design.md) (what the services expose), [13-software-performance-engineering.md](13-performance-engineering.md) (why a pod is slow), and [25-autonomy-edge-inference-deployment.md](../autonomy/25-edge-inference-deployment.md) (the edge end of the cloud-to-edge spectrum).

---

## 1. Why containers — the unit of modern deployment

Before containers, "it works on my machine" was a genuine engineering hazard: an app depended on a specific OS, libraries, and config that the production host might not match. A **container** solves this by packaging the application *and its entire userspace dependency tree* into one immutable image, isolated by the Linux kernel.

A container is not a VM. A virtual machine virtualizes hardware and runs a full guest OS — gigabytes, seconds-to-boot. A container shares the host kernel and isolates only the process view, using two kernel primitives:

- **Namespaces** — isolate *what a process can see*: its own PID space, network stack, mount table, users. The process believes it is alone on the machine.
- **cgroups (control groups)** — isolate *what a process can use*: CPU shares, memory limits, I/O bandwidth. This is how a container is capped.

```
┌──────────── VM model ────────────┐   ┌────────── Container model ──────────┐
│ App A │ App B │ App C            │   │  App A   │  App B  │  App C          │
│ Guest │ Guest │ Guest OS  (GBs)  │   │  bins/libs (MBs, per container)      │
│  OS   │  OS   │                  │   ├──────────────────────────────────────┤
├───────┴───────┴──────────────────┤   │      Container runtime (containerd)  │
│          Hypervisor               │   ├──────────────────────────────────────┤
├───────────────────────────────────┤  │        Shared Host Kernel            │
│            Host Kernel             │   ├──────────────────────────────────────┤
│            Hardware               │   │            Hardware                  │
└───────────────────────────────────┘  └──────────────────────────────────────┘
```

The image is built declaratively and is **immutable** — the same bytes run in test and prod, which is what makes the whole reproducibility argument hold.

```dockerfile
# Multi-stage build: compile in a fat image, ship a tiny one.
FROM rust:1.78 AS build
WORKDIR /src
COPY . .
RUN cargo build --release            # produces /src/target/release/telemetry-svc

FROM gcr.io/distroless/cc-debian12   # no shell, no package manager: tiny attack surface
COPY --from=build /src/target/release/telemetry-svc /telemetry-svc
USER 65532:65532                     # never run as root
EXPOSE 8080
ENTRYPOINT ["/telemetry-svc"]
```

Multi-stage builds and distroless base images are the difference between a 1.2 GB image full of compilers and a 25 MB image with almost nothing to exploit — a security and cost win at once.

---

## 2. The orchestration problem & Kubernetes' answer

One container on one host is easy. A thousand containers across two hundred hosts, where hosts die, traffic spikes, and you redeploy hourly, is the **orchestration problem**: scheduling, health-checking, restarting, networking, scaling, and rolling out — automatically. Kubernetes (K8s) is the dominant answer, and its core design idea is the **reconciliation loop**.

You declare *desired state* ("I want 5 replicas of this service"). Kubernetes continuously compares desired state to *observed state* and takes action to close the gap. A node dies, two replicas vanish, the controller notices 3 ≠ 5 and schedules two more — with no human involved. This is the same control-loop thinking as [06-autonomy-control-theory.md](../autonomy/06-control-theory.md): measure error, drive it to zero, forever.

$$ \text{action} = \text{controller}(\;\text{desired\_state} - \text{observed\_state}\;) $$

```
        ┌──────────────── Control Plane ─────────────────┐
        │  API Server  ◄──►  etcd (the state of truth)   │
        │      ▲                                          │
        │      │      Scheduler   Controller Manager      │
        └──────┼──────────────────────────────────────────┘
               │ (declarative API: "I want 5 replicas")
   ┌───────────┼───────────────┬───────────────────────────┐
   ▼           ▼               ▼                            ▼
 Node 1      Node 2          Node 3        ...            Node N
 kubelet     kubelet         kubelet                      kubelet
 [pod][pod]  [pod]           [pod][pod][pod]              [pod]
```

The control plane is the brain: the **API server** is the only front door, **etcd** is the consistent key-value store holding all cluster state, the **scheduler** decides which node a new pod lands on, and **controllers** run the reconciliation loops. On each worker node, the **kubelet** is the agent that actually starts and supervises containers.

---

## 3. The primitives you must know cold

Kubernetes is a small number of composable objects. Memorize these; everything else is built from them.

| Object | What it is |
|---|---|
| **Pod** | Smallest deployable unit: one or more tightly-coupled containers sharing a network namespace and storage. The atom of scheduling. |
| **ReplicaSet** | Keeps *N* identical pods running. You rarely create these directly. |
| **Deployment** | Manages ReplicaSets to give you **rolling updates** and rollbacks. The workhorse for stateless services. |
| **StatefulSet** | Like a Deployment but with stable identities and storage — for databases, queues. |
| **DaemonSet** | One pod per node — for log shippers, node agents. |
| **Service** | A stable virtual IP + DNS name that load-balances across a changing set of pods. |
| **Ingress / Gateway** | L7 HTTP routing from outside the cluster to Services. |
| **ConfigMap / Secret** | Inject configuration and credentials without rebuilding the image. |
| **Job / CronJob** | Run-to-completion and scheduled batch work (e.g., nightly map builds). |
| **PersistentVolume / Claim** | Decouple durable storage from pod lifecycle. |

The key indirection is the **Service**. Pods are mortal — they get IPs that vanish on restart. A Service gives clients a stable name; behind it, a controller keeps the set of healthy backend pod IPs (the "endpoints") current. Clients talk to the name; Kubernetes handles the churn.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: perception }
spec:
  replicas: 4
  selector: { matchLabels: { app: perception } }
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxUnavailable: 0, maxSurge: 1 }   # zero-downtime deploy
  template:
    metadata: { labels: { app: perception } }
    spec:
      containers:
      - name: perception
        image: registry.internal/perception:v2.15
        resources:                       # the scheduler & autoscaler depend on these
          requests: { cpu: "500m", memory: "512Mi" }   # what I'm guaranteed
          limits:   { cpu: "2",    memory: "1Gi"  }     # my hard ceiling
        readinessProbe:                  # "am I ready for traffic?"
          httpGet: { path: /healthz, port: 8080 }
          initialDelaySeconds: 5
        livenessProbe:                   # "am I alive, or should you kill me?"
          httpGet: { path: /livez, port: 8080 }
```

`requests` vs `limits` is the single most consequential pair of numbers. **Requests** are what the scheduler reserves (and what bin-packing uses); **limits** are the hard cap (exceed the memory limit and the kernel OOM-kills your pod). Probes are how Kubernetes distinguishes "starting up" from "broken" — get the readiness probe wrong and you route traffic into a pod that isn't ready, or never send traffic to a healthy one.

---

## 4. Scheduling — where does a pod actually go?

The scheduler turns a pod's requirements into a node assignment in two phases: **filtering** (which nodes *can* run this pod?) then **scoring** (which is *best*?).

Filtering removes nodes lacking enough requested CPU/memory, nodes that don't match a `nodeSelector`, or nodes whose **taints** the pod doesn't **tolerate**. Scoring then ranks survivors by spreading load, honoring affinity rules, and bin-packing efficiency. The controls you actually reach for:

- **Resource requests** — the primary input; under-request and you over-pack and cause contention, over-request and you waste money.
- **Node affinity / selectors** — "this GPU job only runs on GPU nodes."
- **Taints & tolerations** — a node *repels* pods unless they explicitly tolerate it (e.g., dedicate GPU nodes to inference workloads).
- **Pod (anti-)affinity** — "spread my replicas across availability zones so one zone failure doesn't take all of them" — directly buys you the redundancy your SLO needs.
- **Topology spread constraints** — the modern, declarative way to express even spreading.

```yaml
affinity:
  podAntiAffinity:                         # don't put two replicas in the same zone
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector: { matchLabels: { app: perception } }
      topologyKey: topology.kubernetes.io/zone
```

When a node is over-committed and memory runs out, the kubelet **evicts** pods by QoS class: `BestEffort` (no requests/limits) dies first, then `Burstable`, and `Guaranteed` (requests == limits) is protected longest. Setting requests == limits for critical services is how you buy survival priority.

---

## 5. Networking — the part that breaks at 2 a.m.

Kubernetes networking rests on one demanding rule: **every pod gets its own IP, and every pod can reach every other pod without NAT.** This flat model is implemented by a **CNI plugin** (Calico, Cilium, etc.) that programs routes across nodes — increasingly using eBPF in the kernel for speed.

Layered on top:

- **Service / ClusterIP** — the in-cluster virtual IP, implemented by `kube-proxy` (iptables) or eBPF, load-balancing to endpoint pods.
- **DNS (CoreDNS)** — `perception.default.svc.cluster.local` resolves to the Service IP. Service discovery is just DNS.
- **Ingress / Gateway API** — L7 routing, TLS termination, path/host-based routing from the internet in.
- **NetworkPolicy** — the firewall: by default everything can talk to everything (bad); a NetworkPolicy is how you enforce zero-trust segmentation so the public API can't reach the database directly.

```yaml
# Default-deny ingress, then allow only the gateway to reach perception.
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: perception-allow }
spec:
  podSelector: { matchLabels: { app: perception } }
  policyTypes: [Ingress]
  ingress:
  - from:
    - podSelector: { matchLabels: { app: gateway } }
    ports: [{ port: 8080 }]
```

A **service mesh** (Istio, Linkerd) takes this further by injecting a sidecar proxy next to every pod, giving you mTLS between services, retries, circuit breaking, and per-call traces — without changing app code. Powerful, but it adds latency and operational weight; reach for it when you genuinely need mesh-wide mТLS and traffic control, not by default.

---

## 6. Scaling & self-healing

Kubernetes scales on two axes, and the distinction matters.

- **Horizontal Pod Autoscaler (HPA)** — adds/removes *pod replicas* based on a metric (CPU, or custom metrics like queue depth). This is the default for stateless services.
- **Vertical Pod Autoscaler (VPA)** — adjusts a pod's *requests/limits*. Useful for right-sizing, awkward alongside HPA on the same metric.
- **Cluster Autoscaler / Karpenter** — adds/removes *nodes* when pods can't be scheduled or nodes sit idle. This is where cloud spend actually moves.

The HPA replica calculation is a proportional controller:

$$ \text{desiredReplicas} = \left\lceil \text{currentReplicas} \times \frac{\text{currentMetric}}{\text{targetMetric}} \right\rceil $$

If 4 replicas average 80% CPU against a 50% target, the HPA wants $\lceil 4 \times 80/50 \rceil = 7$ replicas. Scale **on the metric that reflects user pain** — for a queue worker, scale on queue depth (a leading indicator), not CPU (a lagging one). Autoscaling has lag (probe interval + pod start time), so it complements but never replaces the capacity planning in [09-software-observability-and-sre.md](09-observability-and-sre.md).

Self-healing is the reconciliation loop in action: liveness probe fails → kubelet restarts the container; node goes unreachable → controller reschedules its pods elsewhere; a `PodDisruptionBudget` ensures voluntary disruptions (a node drain) never take more replicas down at once than your SLO allows.

---

## 7. Infrastructure as Code & GitOps

Clicking in a cloud console does not scale and is not auditable. **Infrastructure as Code (IaC)** declares infrastructure in version-controlled files so that environments are reproducible, reviewable, and diffable.

- **Terraform / OpenTofu** — provision the *cloud* substrate: VPCs, the cluster itself, IAM, databases. Declarative, with a state file tracking reality.
- **Helm / Kustomize** — template and parameterize the *Kubernetes* manifests so the same chart deploys to dev/staging/prod with different values.
- **GitOps (Argo CD, Flux)** — the repo *is* the desired state; an in-cluster controller continuously reconciles the live cluster to match Git. A deploy becomes a merged pull request; a rollback becomes a `git revert`. This closes the loop: the same reconciliation philosophy Kubernetes uses internally now governs how you change the cluster itself.

```hcl
# Terraform: a node pool for GPU inference, declaratively.
resource "google_container_node_pool" "gpu" {
  name       = "gpu-inference"
  cluster    = google_container_cluster.primary.id
  node_count = 2
  node_config {
    machine_type = "n1-standard-8"
    guest_accelerator { type = "nvidia-tesla-t4"  count = 1 }
    taint { key = "nvidia.com/gpu" value = "present" effect = "NO_SCHEDULE" }
  }
}
```

The discipline: **no manual changes to production.** If it isn't in Git, it doesn't exist — because the next reconciliation will erase it. This is the operational embodiment of the reproducibility argument from [06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md).

---

## 8. Cost, and the edge-vs-cloud decision

Cloud compute is rented; the bill is an engineering output, not an afterthought.

| Lever | Mechanism |
|---|---|
| **Right-sizing** | Set requests near real usage; over-requesting wastes reserved capacity. |
| **Spot / preemptible nodes** | 60–90% cheaper, can be reclaimed — perfect for fault-tolerant batch (map builds, training). |
| **Autoscaling to zero** | Scale dev environments and bursty jobs down when idle. |
| **Reserved / committed use** | Discounts for predictable baseline load. |
| **Bin-packing efficiency** | Fewer, fuller nodes beat many empty ones; this is the cluster autoscaler's job. |
| **Egress awareness** | Cross-region and internet egress bandwidth is often the silent dominant cost. |

The deeper architectural question for autonomy is **edge vs. cloud**, and it is a first-principles tradeoff, not a fashion:

| Dimension | Edge (on-vehicle / on-prem) | Cloud (datacenter) |
|---|---|---|
| Latency | Microseconds–milliseconds | Tens–hundreds of ms (RTT) |
| Connectivity needed | None (autonomous) | Constant |
| Compute available | Constrained (SWaP-limited) | Effectively unlimited |
| Data gravity | Process where data is born | Move data to compute |
| Failure independence | Survives comms loss | Dies with the link |

A drone's control loop and obstacle avoidance **must** be at the edge — you cannot round-trip to a datacenter at 200 ms when a wire is 5 meters away (the SWaP-constrained inference reality of [25-autonomy-edge-inference-deployment.md](../autonomy/25-edge-inference-deployment.md)). But fleet-wide map fusion, model retraining, and long-horizon mission planning belong in the cloud, where compute is cheap and data aggregates. The mature architecture is a **continuum**: time-critical and connectivity-independent work at the edge, heavy and aggregating work in the cloud, with Kubernetes increasingly spanning both (K3s/KubeEdge run the same orchestration model on small edge devices). Designing *where each computation lives* is the central systems-engineering decision of [01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md) applied to compute.

---

## Sources & further study

- **Kelsey Hightower, Brendan Burns & Joe Beda, *Kubernetes: Up and Running*** — the canonical introduction by people who built it.
- **Brendan Burns, *Designing Distributed Systems*** — patterns (sidecar, ambassador, adapter) that explain *why* K8s looks the way it does.
- **Bilgin Ibryam & Roland Huß, *Kubernetes Patterns*** — the design-pattern catalog for real workloads.
- **Liz Rice, *Container Security*** — namespaces, cgroups, and how containers are actually isolated (and broken out of).
- **Yevgeniy Brikman, *Terraform: Up & Running*** — the practical IaC bible.
- **The official Kubernetes documentation** — genuinely excellent; the concepts section is required reading.
- **Cilium / eBPF docs** — for the modern, kernel-level networking and observability future.
- **Google SRE book, capacity chapters** — ties cloud scaling back to the reliability math in [09-software-observability-and-sre.md](09-observability-and-sre.md).

> Framing note: Kubernetes is not a tool you learn so you can list it on a resume; it is the reification of a single powerful idea — declare what you want, and let a relentless control loop make reality match. Master that idea and the manifests become details. The engineer who understands the reconciliation loop, the requests/limits economy, and the edge-vs-cloud continuum can wield a fleet of machines as confidently as a firmware engineer wields a single chip — and that leverage is what lets a handful of people build infrastructure that once took an army.
