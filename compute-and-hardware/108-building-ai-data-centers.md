# Building AI Data Centers — Power, Cooling, Networking & the Real Constraints

> **Why this exists.** Every frontier model, every inference API call, every "agent" you build runs on physical buildings that consume the power of a small city and reject the heat of an industrial furnace. The bottleneck in AI is no longer the chip — TSMC and NVIDIA can make more silicon — it is *getting megawatts to a slab of land and getting the heat back out.* Most engineers treat the data center as an abstraction ("the cloud"), and so they cannot reason about cost, latency, scaling limits, or where the next decade of value accrues. This module rips the roof off the building and shows you the substation, the busbar, the coolant loop, and the fabric.
> **What mastering it makes you.** Someone who can read an AI infrastructure announcement and immediately ask the right question — "where's the power coming from and when does it interconnect?" — instead of being dazzled by GPU counts. You become fluent in the units that actually govern the industry: MW, kW/rack, PUE, $/MWh, GB/s per GPU, and $/token. That fluency is rare, it compounds, and it is exactly what separates people who *talk* about AI from people who *build the substrate it runs on.*

This module sits at the intersection of silicon, power, and thermodynamics. It builds on [81-software-gpu-and-parallel-computing.md](../software/81-gpu-and-parallel-computing.md) (what the GPUs actually do), [72-engineering-thermal-management.md](../engineering/72-thermal-management.md) (how heat moves), and [68-engineering-power-electronics.md](../engineering/68-power-electronics.md) (transformers, rectification, conversion losses). It is consumed by [85-software-mlops-and-ml-infrastructure.md](../software/85-mlops-and-ml-infrastructure.md) and [89-software-cloud-and-kubernetes.md](../software/89-cloud-and-kubernetes.md), which schedule workloads onto this iron. The strategic frame comes from [42-companies-nvidia-platform-ecosystem.md](../companies/42-nvidia-platform-ecosystem.md) (who controls the stack) and [08-foundations-company-strategy-moat.md](../foundations/08-company-strategy-moat.md) (where the durable moats are). Its sequel — [109-compute-distributed-data-centers-and-startup-ideas.md](109-distributed-data-centers-and-startup-ideas.md) — uses everything here to dissect a real distributed-compute startup and propose better bets.

---

## 1. The thesis: it's a power building, not a computer building

The single most important reframe: **a modern AI data center is a power-conversion and heat-rejection plant that happens to contain GPUs.** The compute is the easy part to procure. The hard parts — the parts with multi-year lead times, regulatory friction, and physics limits — are *electricity in* and *heat out.*

Consider the cost of delay. A GB200-class GPU depreciates over ~4–6 years and costs tens of thousands of dollars. If it sits in a warehouse for 18 months waiting on a grid interconnection, you have burned a third of its useful life to zero output. This is why the operative phrase across the industry in 2025–2026 is **"speed-to-power"** — not FLOPS, not even cost, but *how fast can you energize a megawatt of capacity.* Whoever solves speed-to-power wins; whoever has stranded GPUs loses.

```
        OLD MENTAL MODEL                NEW (CORRECT) MENTAL MODEL
   ┌────────────────────────┐      ┌────────────────────────────────┐
   │   "We need more chips"  │      │  "We need more MW, energized    │
   │   GPU = scarce resource │ ───► │   sooner, with heat-out solved" │
   │   power = a line item   │      │  GPU = abundant if power exists │
   └────────────────────────┘      └────────────────────────────────┘
```

Everything below follows from this thesis.

---

## 2. Anatomy of an AI data center: chip → rack → pod → hall

AI infrastructure is built in a strict hierarchy of aggregation. Each level has its own power, cooling, and networking design point.

| Level | Unit | Rough scale (2026, training-class) | Power | Cooling |
|-------|------|-----------------------------------|-------|---------|
| Accelerator | 1 GPU (e.g., Blackwell B200) | ~1000 W TDP | ~1 kW | liquid cold plate |
| Compute tray | 2–4 GPUs + 1–2 CPUs | 4–8 kW | local | direct-to-chip |
| Rack | 1 NVL72-class rack (72 GPUs) | **~120–140 kW** | rack | liquid, CDU-fed |
| Pod | 8–16 racks, one fabric domain | 1–2 MW | row | facility water loop |
| Hall / data center | many pods | **50–500+ MW** | site | chillers + towers |

The **GB200 NVL72** is the canonical reference object of this era. It is a single liquid-cooled rack containing 72 Blackwell GPUs and 36 Grace CPUs, wired together by NVLink into what NVIDIA markets as "one giant GPU." It draws roughly **120 kW in a single rack** — about *30× the density of a typical enterprise rack from 2018* (which was ~4–6 kW). That density jump is the entire story of why cooling and power had to be reinvented.

```
   NVL72 RACK (schematic)
   ┌─────────────────────────────┐
   │  Switch tray (NVLink spine) │  ← 9 NVLink switch trays
   ├─────────────────────────────┤
   │  Compute tray ×18           │  ← 72 GPUs / 36 Grace CPUs total
   │  (each: 4 GPU + 2 CPU)      │
   ├─────────────────────────────┤
   │  Power shelves / busbar     │  ← DC busbar runs vertically
   ├─────────────────────────────┤
   │  Manifold: coolant in/out   │  ← quick-disconnects to CDU
   └─────────────────────────────┘
        ~120 kW in one rack
```

At 120 kW/rack, a single row of 8 racks is ~1 MW. A 100 MW hall is therefore ~800 such racks plus networking, storage, and overhead — a building you can walk in minutes that consumes more power than 70,000 US homes.

---

## 3. The power problem: why an AI hall is 100+ MW and why that's hard

### 3.1 The arithmetic of demand

$$
P_{\text{hall}} = N_{\text{racks}} \times P_{\text{rack}} \times \text{PUE}
$$

For 800 racks at 120 kW with a PUE of 1.2:

$$
P_{\text{hall}} = 800 \times 120\,\text{kW} \times 1.2 = 115{,}200\,\text{kW} \approx 115\,\text{MW}
$$

The largest announced training campuses (xAI's Colossus in Memphis, Meta's clusters, OpenAI/Oracle's Stargate sites) target **multiple gigawatts**. A gigawatt is the output of a large nuclear reactor. We are now building *individual computers that need reactor-scale power.*

### 3.2 Why the grid says "no, and not for years"

You cannot simply ask the utility for 200 MW. Large-load interconnection requires:

- **A grid impact study** (does the local transmission network have headroom? usually not).
- **Substation construction or upgrade** — a 230 kV / 33 kV substation is a multi-year, $50–150M project with custom **large power transformers (LPTs)** that themselves have **2–4 year lead times** globally because there are few manufacturers.
- **Transmission upgrades** that may require new high-voltage lines, which trigger permitting, right-of-way, and environmental review.

The result: **interconnection queues in many US grid regions now stretch 4–7 years.** This is the true bottleneck. It is why operators chase locations with *existing* power — retired coal plants (grid tie already built), regions with surplus generation (the Pacific Northwest, parts of Texas/ERCOT), or anywhere a substation already has spare capacity.

### 3.3 On-site and "bring your own power"

Because the grid is slow, operators increasingly **bring their own generation**:

- **Natural gas turbines on-site** (xAI famously deployed mobile gas turbines in Memphis to energize Colossus while waiting on the utility — controversial on emissions, but it solved speed-to-power).
- **Behind-the-meter deals** co-locating directly at a power plant (this is a central theme of [109-compute-distributed-data-centers-and-startup-ideas.md](109-distributed-data-centers-and-startup-ideas.md)).
- **Nuclear**: SMRs (small modular reactors) and restarts of plants like Three Mile Island (Microsoft) and Crane Clean Energy. Long timelines but the only carbon-free firm power at scale.
- **Solar + massive battery** for partial load, rarely the full answer because training wants firm 24/7 power.

> The strategic insight: **power procurement has become a core competency of AI labs.** OpenAI, Microsoft, Amazon, Google, and xAI now employ energy traders and nuclear deal teams. The org chart of an "AI company" now contains people who think in MWh.

---

## 4. Power distribution: from the utility line to the chip

Once you have power at the fence, you must deliver it to the silicon with minimal loss and maximum reliability. The chain:

```
 UTILITY (e.g., 230 kV)
     │  transmission
     ▼
 [ SUBSTATION ]  step down 230 kV → 33/13.8 kV (medium voltage)
     │
     ▼
 [ MV SWITCHGEAR ]  distribute around the site
     │
     ▼
 [ TRANSFORMERS ]  step down to ~480 V (US) / 415 V (EU) AC
     │
     ▼
 [ UPS ]  battery/flywheel ride-through + clean power
     │
     ▼
 [ PDU / RPP ]  power distribution unit → branch circuits
     │
     ▼
 [ RACK BUSBAR ]  vertical busway, often rectified to ~50 VDC / HVDC
     │
     ▼
 [ POWER SHELF ]  AC→DC, deliver to compute trays
     │
     ▼
 [ VRM on board ]  ~50 V → ~0.8 V at hundreds of amps into the GPU
```

### 4.1 Every conversion costs you

Each transformation step (AC→AC, AC→DC, DC→DC) loses 1–5%. Multiply them and you see why **efficiency is cumulative**:

$$
\eta_{\text{total}} = \eta_{\text{tx}} \times \eta_{\text{UPS}} \times \eta_{\text{PDU}} \times \eta_{\text{shelf}} \times \eta_{\text{VRM}}
$$

A poorly designed chain at $0.97^5 \approx 0.86$ wastes 14% of all energy *before a single FLOP*. This is why hyperscalers push toward **higher-voltage DC distribution** (e.g., 800 VDC architectures NVIDIA is championing for the Rubin generation) — fewer conversions, less copper, less loss. See [68-engineering-power-electronics.md](../engineering/68-power-electronics.md) for the device physics.

### 4.2 The $P = CV^2f$ reality at the chip

At the transistor level, dynamic power follows:

$$
P_{\text{dyn}} = \alpha C V^2 f
$$

where $\alpha$ is activity factor, $C$ switched capacitance, $V$ supply voltage, $f$ clock. Voltage's *quadratic* term is why every power-saving lever (DVFS, undervolting, lower-voltage process nodes) targets $V$. But at the rack and hall level, you cannot undervolt your way out of 120 kW — you must *deliver and remove* it. The chip designers fight the $V^2$; the facility engineers fight the heat.

---

## 5. Cooling: why >100 kW/rack forces liquid

### 5.1 The density cliff

Air has miserable heat capacity and a hard practical limit. Once a rack exceeds **~30–50 kW**, air cooling becomes absurd — you need hurricane-velocity airflow and huge plenums. At 120 kW, air is simply *impossible*. The physics:

$$
Q = \dot{m} \, c_p \, \Delta T
$$

To remove 120 kW with air ($c_p \approx 1.0\,\text{kJ/kg·K}$, $\Delta T \approx 15\,\text{K}$) you'd need:

$$
\dot{m} = \frac{Q}{c_p \Delta T} = \frac{120}{1.0 \times 15} = 8\,\text{kg/s of air} \approx 6.6\,\text{m}^3/\text{s per rack}
$$

That is a gale. Water, by contrast, has ~4× the specific heat *and* ~800× the density, so the same heat moves in a trickle.

### 5.2 The cooling ladder

| Method | Practical density | How it works | Trade-off |
|--------|------------------|--------------|-----------|
| **Air** (CRAC/CRAH) | up to ~30 kW/rack | chilled air, hot/cold aisles | simple, low density, high PUE |
| **Rear-door heat exchanger** | up to ~50 kW/rack | water coil on rack door | retrofit-friendly, transitional |
| **Direct-to-chip (DLC)** | 50–150+ kW/rack | cold plates on GPU/CPU, coolant loop | **the 2026 standard**; needs CDU + plumbing |
| **Immersion** | 100–200+ kW/rack | boards submerged in dielectric fluid | extreme density, messy servicing, slow adoption |

**Direct-to-chip liquid cooling (DLC)** has won for the GB200/Blackwell generation. Cold plates sit directly on the GPUs; a **CDU (Coolant Distribution Unit)** circulates a clean secondary loop (often water/glycol) through the racks and exchanges heat with a **facility water loop** that ultimately rejects to chillers, dry coolers, or cooling towers.

```
   CHIP ── cold plate ── secondary loop ── [ CDU ] ── facility loop ── [ chiller / tower ] ── atmosphere
            (in rack)      (clean, ~25-45°C)   (heat exchanger)   (warmer, dirtier)
```

### 5.3 Water is the second scarce resource

Cooling towers evaporate water. A large campus can consume **millions of gallons per day**, which is why **site selection now optimizes for water as well as power** — and why dry-cooler and closed-loop designs (which trade water for slightly worse efficiency) are rising in water-stressed regions. The two scarce inputs of the AI era are **electrons and water.**

---

## 6. PUE and the efficiency math

**Power Usage Effectiveness** is the industry's headline efficiency metric:

$$
\text{PUE} = \frac{\text{Total facility power}}{\text{IT (compute) power}}
$$

- PUE = 2.0 → for every watt of compute you burn a watt on cooling/overhead (bad, ~2010 era).
- PUE = 1.5 → typical legacy enterprise.
- PUE = 1.1–1.2 → modern hyperscale with liquid cooling and good climate.
- PUE = 1.0 → theoretical floor (impossible; it means zero overhead).

Liquid cooling's biggest win is slashing the cooling term. A worked example for a 100 MW IT load:

| PUE | Total draw | Overhead | Annual overhead cost @ $60/MWh |
|-----|-----------|----------|-------------------------------|
| 1.5 | 150 MW | 50 MW | ~$26.3M/yr wasted |
| 1.2 | 120 MW | 20 MW | ~$10.5M/yr |
| 1.1 | 110 MW | 10 MW | ~$5.3M/yr |

Dropping PUE from 1.5 to 1.1 on a 100 MW site saves ~$21M/year *and* frees 40 MW of interconnect for actual compute. At today's power scarcity, **freeing MW is worth more than the dollar savings.** Caveat: PUE is gameable and ignores water (WUE) and carbon (CUE); treat it as necessary but not sufficient.

---

## 7. Networking: the fabric is the real bottleneck for training

A single GPU is useless for frontier training; the model is *sharded* across thousands of them, and they must exchange gradients every step. The interconnect — the **fabric** — determines whether 10,000 GPUs behave like one machine or like 10,000 lonely cards.

### 7.1 Three tiers of interconnect

```
   ┌─────────────────────────────────────────────┐
   │  NVLink  (intra-rack, GPU↔GPU)               │  ~1.8 TB/s per GPU (Blackwell)
   │  → ties 72 GPUs into "one giant GPU"         │
   ├─────────────────────────────────────────────┤
   │  Scale-out fabric (rack↔rack, pod↔pod)       │
   │  InfiniBand (NDR 400G/XDR 800G)  OR          │
   │  Spectrum-X Ethernet (800G)                  │
   ├─────────────────────────────────────────────┤
   │  Frontend / storage network (north-south)    │  data loading, checkpoints
   └─────────────────────────────────────────────┘
```

### 7.2 InfiniBand vs Spectrum-X Ethernet

| | InfiniBand (NDR/XDR) | Spectrum-X Ethernet |
|--|---------------------|---------------------|
| Origin | HPC pedigree, lossless | Ethernet made AI-grade |
| Congestion control | mature, hardware | adaptive routing, RoCE tuned |
| Lock-in | NVIDIA/Mellanox stack | more open, multi-vendor-ish |
| Why chosen | lowest latency, proven at scale | cheaper, familiar ops, "good enough" |

Both are NVIDIA-owned product lines (Mellanox acquisition) — a reminder from [42-companies-nvidia-platform-ecosystem.md](../companies/42-nvidia-platform-ecosystem.md) that NVIDIA sells you the GPU *and* the network *and* the switches. The moat is the **system**, not the chip.

### 7.3 Rail-optimized topology and why it matters

Training communication is dominated by **all-reduce** (summing gradients across all GPUs). The network is built **rail-optimized**: each GPU connects to the same "rail" (leaf switch position) so that collective operations traverse predictable, balanced paths. A fat-tree / rail-optimized Clos minimizes the worst-case hop count.

The killer metric is **bisection bandwidth** — if you cut the cluster in half, how much bandwidth crosses the cut. Training scales only if bisection bandwidth keeps pace with GPU count. The communication time for one all-reduce step:

$$
t_{\text{comm}} \approx \frac{2(N-1)}{N} \cdot \frac{S}{B}
$$

where $S$ is the model/gradient size per GPU and $B$ is effective per-GPU bandwidth. As clusters grow, $t_{\text{comm}}$ can dominate $t_{\text{compute}}$ — at which point **you are not compute-bound, you are network-bound.** Every idle GPU waiting on gradients is money burning. This is why the fabric, not the GPU, is often the true ceiling on training throughput.

---

## 8. Training clusters vs inference fleets: two different buildings

These are frequently conflated. They are *architecturally opposite.*

| Dimension | Training cluster | Inference fleet |
|-----------|-----------------|-----------------|
| Job shape | one giant synchronous job | millions of tiny independent requests |
| Network need | extreme east-west (all-reduce) | mostly north-south (user traffic) |
| Latency sensitivity | throughput matters, not per-step latency | **user-facing latency is everything** |
| Failure impact | one node fails → whole job stalls (checkpoint) | one node fails → reroute, no big deal |
| Geography | centralize for fabric density | **distribute near users** for latency |
| Power profile | steady, near-100% utilization | spiky, follows daily demand curve |
| Hardware | top-end (B200/GB200) | often cheaper/smaller (L40S, RTX PRO, older gen) |

This distinction is the *hinge* for the next module. **Training wants to be one enormous centralized machine. Inference wants to be everywhere, close to users.** The economic and physical logic of distributing inference to the grid edge — and whether it actually works — is exactly what [109-compute-distributed-data-centers-and-startup-ideas.md](109-distributed-data-centers-and-startup-ideas.md) interrogates.

---

## 9. Redundancy and reliability: N+1, 2N, Tier levels

Data centers are rated by the Uptime Institute Tier system, driven by redundancy of power and cooling paths.

| Tier | Redundancy | Availability | Annual downtime | Typical use |
|------|-----------|-------------|-----------------|-------------|
| I | none | 99.671% | ~28.8 hr | dev/test |
| II | partial | 99.741% | ~22 hr | small biz |
| III | N+1, concurrently maintainable | 99.982% | ~1.6 hr | enterprise |
| IV | 2N, fault tolerant | 99.995% | ~0.4 hr | mission-critical |

- **N** = exactly enough capacity to carry the load.
- **N+1** = one spare unit (one extra UPS, one extra CDU). Survives a single failure.
- **2N** = fully mirrored, independent A/B paths. Survives any single fault and allows maintenance with zero downtime.

The AI twist: **training clusters often run *lower* redundancy than traditional enterprise.** Why? Because a training job already checkpoints, and a stalled job is recoverable — so paying 2N capex for a workload that tolerates restarts is wasteful. Inference, by contrast, is user-facing revenue and trends toward higher redundancy. Redundancy is an *economic* decision tied to the cost of downtime, not a virtue in itself.

---

## 10. Site selection: chasing electrons and water

Putting it all together, site selection is a multi-constraint optimization:

```
   SITE SCORE = f(
       available_MW_now,          ← speed-to-power (dominant)
       interconnect_timeline,     ← years to energize
       power_$/MWh,               ← opex over 5-10 yr
       water_availability,        ← cooling
       climate (cold = free cooling),
       fiber_proximity,           ← network egress
       land_cost,
       latency_to_users,          ← inference only
       permitting_friction,       ← regulatory speed
       tax_incentives
   )
```

This is why the map of AI data centers clusters around: **retired power plants** (instant grid tie), **ERCOT/Texas** (cheap, fast-permitting, abundant gas + wind), **the Nordics** (free cooling, hydro), **Virginia ("Data Center Alley")** for legacy fiber + cloud gravity, and increasingly **anywhere with a willing utility and surplus generation.** The asymmetric founders covered in [47-companies-startup-asymmetric-playbook.md](../companies/47-startup-asymmetric-playbook.md) win by finding *stranded* power others overlooked.

---

## 11. Capex/TCO breakdown: where the money actually goes

A rough decomposition of total cost of ownership for a large AI data center over its life. **The GPUs dominate capex, but power dominates the *lifetime* picture.**

$$
\text{TCO} = C_{\text{GPU}} + C_{\text{facility}} + \sum_{t=1}^{T}\frac{(E_{\text{power}} + E_{\text{opex}} + E_{\text{network}})}{(1+r)^t}
$$

| Component | Share of upfront capex (rough) | Notes |
|-----------|-------------------------------|-------|
| GPUs + networking gear | **55–70%** | the headline number; depreciates in 4–6 yr |
| Power infra (substation, UPS, gen) | 12–20% | long lead, hard to add later |
| Cooling (CDUs, chillers, plumbing) | 8–15% | liquid raised this share |
| Building shell + land | 5–10% | cheapest part |
| **Lifetime power (opex)** | *not capex* — can rival GPU cost over 5 yr | the silent giant |

A 100 MW site at $60/MWh runs ~$52.6M/year *just for electricity*. Over a 5-year GPU life that is **~$263M in power** — often comparable to or exceeding the building shell and cooling capex combined. **Cheap power is a structural moat.** A site at $30/MWh beats a site at $70/MWh by hundreds of millions over its life, regardless of how good your software is. This is the financial spine of [08-foundations-company-strategy-moat.md](../foundations/08-company-strategy-moat.md) applied to compute.

---

## 12. Where the industry is heading

1. **Higher voltage, fewer conversions.** 800 VDC rack distribution (NVIDIA's roadmap) to cut copper and loss as racks head toward 200–600 kW (Rubin / Rubin Ultra generation).
2. **Liquid everywhere, then warm-water and waste-heat reuse.** Rejecting 40 °C water lets you heat district networks (already done in the Nordics). PUE approaches its floor; the frontier shifts to *total* energy utilization.
3. **Power becomes the product.** Nuclear restarts, SMRs, behind-the-meter gas, and grid-scale storage deals. AI labs become energy companies.
4. **Geographic bifurcation.** Centralized gigawatt *training* campuses near cheap firm power; distributed *inference* near users (the subject of file 109).
5. **The interconnect arms race continues.** NVLink scale-up, photonics/co-packaged optics to beat the copper-reach wall, optical circuit switching.
6. **Grid co-design.** Data centers as flexible loads — curtailing during grid stress, providing demand response — turning the liability of huge load into a grid asset.

The constant through all of it: **the constraint is power and speed-to-power, not chips.** Memorize that and you will out-reason most of the industry.

---

## Sources & further study

- **The Uptime Institute** — Tier Standard (Topology & Operational Sustainability); annual Global Data Center Survey for real PUE/availability numbers.
- **ASHRAE TC 9.9** — *Thermal Guidelines for Data Processing Environments* and liquid-cooling guidelines (the canonical engineering reference for cooling envelopes).
- **The Open Compute Project (OCP)** — open specs for racks, power shelves, and the emerging 800 VDC / liquid-cooling standards; read the contributions from Meta, Microsoft, NVIDIA.
- **NVIDIA GTC keynotes (2024–2026)** — Jensen Huang on GB200 NVL72, NVLink, Spectrum-X, and the 800 VDC Rubin roadmap; the primary source for density and fabric numbers.
- **Semianalysis (Dylan Patel)** — deep, numbers-driven teardowns of cluster cost, networking, and power; the best independent analysis of AI datacenter economics.
- **"The Datacenter as a Computer"** — Barroso, Clidaras, Hölzle (Google) — the foundational text on warehouse-scale machines.
- **EPRI and IEA reports (2024–2026)** on data-center electricity demand and grid-interconnection constraints — for the macro power picture.
- **Texas ERCOT and PJM interconnection-queue data** — to see the multi-year queues with your own eyes.

> Framing note: When you read "Company X is building a 1 GW AI cluster," do not picture chips. Picture a substation that took four years to permit, a transformer with a three-year lead time, a million gallons of water a day, and a coolant loop carrying away the heat of an industrial smelter. The chip is the part everyone talks about because it's the part they can buy. The moat is everything *around* the chip — and that is the part most engineers, and most journalists, never see.
