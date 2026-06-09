# Networking & Protocols — From Packets to Real-Time Telemetry

> **Why this exists.** A fielded autonomous system is a conversation: a vehicle talks to a ground
> station, sensors talk to a flight computer, nodes in a mesh talk to each other, and every one
> of those conversations happens over a channel that is slow, lossy, jittery, and sometimes
> jammed. Whether telemetry arrives in 20 ms or 2 s, in order or scrambled, at all or never, is
> decided by choices made deep in the network stack — TCP vs UDP vs QUIC, multicast vs unicast,
> DDS QoS settings, MTU and fragmentation. The engineer who understands networking from the
> packet up can diagnose why the video froze, why the swarm desynced, and why the control link
> stuttered — and design transports that degrade gracefully instead of falling off a cliff.
>
> **What mastering it makes you.** The engineer who knows exactly which layer is lying when
> comms break; who chooses TCP for a config upload and UDP for a control stream *for reasons*;
> who tunes ROS 2/DDS QoS to match the mission; who reasons about latency, jitter, and
> bandwidth as a budget; and who designs telemetry that survives a degraded, intermittent, and
> contested link.

This module is the wire-level foundation under the mesh and comms systems of
[05_distributed_systems_comms_mesh.md](05_distributed_systems_comms_mesh.md), the transport
beneath the distributed agreement of [80-software-distributed-systems-deep.md](80-software-distributed-systems-deep.md),
and the link whose jitter the real-time loops of [82-software-real-time-operating-systems.md](82-software-real-time-operating-systems.md)
and [04-foundations-modern-cpp-realtime.md](04-foundations-modern-cpp-realtime.md) must tolerate.
It connects to the GNSS/jamming reality of [26-autonomy-gnss-jamming-spoofing.md](26-autonomy-gnss-jamming-spoofing.md)
and the EW threat of [27-autonomy-counter-uas-ew.md](27-autonomy-counter-uas-ew.md), the security
hardening of [86-software-cybersecurity-engineering.md](86-software-cybersecurity-engineering.md)
and [36-trust-safety-opsec-and-digital-resilience.md](36-trust-safety-opsec-and-digital-resilience.md),
the crypto that secures it in [87-software-cryptography-applied.md](87-software-cryptography-applied.md),
and the engineering practice of [12-career-software-engineering.md](12-career-software-engineering.md).

---

## Table of Contents

1. [The layered model and why it matters](#1-the-layered-model-and-why-it-matters)
2. [IP, addressing, and routing](#2-ip-addressing-and-routing)
3. [TCP — reliability and its cost](#3-tcp--reliability-and-its-cost)
4. [UDP, QUIC, and real-time transport](#4-udp-quic-and-real-time-transport)
5. [Latency, jitter, and bandwidth math](#5-latency-jitter-and-bandwidth-math)
6. [Pub/sub, multicast, and DDS/ROS 2](#6-pubsub-multicast-and-ddsros-2)
7. [Mesh networking and degraded links](#7-mesh-networking-and-degraded-links)
8. [Practice this week](#8-practice-this-week)
9. [Sources & further study](#9-sources--further-study)

---

## 1. The layered model and why it matters

Networking is layered so that each layer can change independently and fail distinctly. The OSI
model is the teaching frame; the TCP/IP model is what ships.

```
 OSI                TCP/IP            Robotics example          Fails as...
 ─────────────────  ───────────────   ───────────────────────   ─────────────────────
 7 Application      Application       MAVLink, DDS, gRPC        wrong schema, stale data
 6 Presentation       │               CBOR/protobuf encode     encoding mismatch
 5 Session            │               WebSocket session        dropped session
 4 Transport        Transport         TCP / UDP / QUIC          loss, reorder, HOL block
 3 Network          Internet          IP routing, multicast     no route, TTL expiry, NAT
 2 Data Link        Link              Wi-Fi/MANET MAC, ARP      contention, hidden node
 1 Physical         Link              RF, fiber, copper         noise, jamming, fade
```

The single most useful debugging habit: when comms break, **ask which layer is lying.** Ping
works (L3 fine) but the app is silent (L4–7 problem). Ping fails (L1–3). Packets arrive but
garbled (L1 SNR or L2 framing). Encapsulation — each layer wrapping the one above in its own
header — is why a single byte of payload can carry 60+ bytes of overhead, which matters enormously
on a narrowband tactical link.

---

## 2. IP, addressing, and routing

**IP** moves packets between hosts using addresses (IPv4 32-bit, IPv6 128-bit) and **routing** —
each router forwards toward the destination using its routing table, hop by hop, with a
decrementing **TTL** to kill loops. Key concepts that bite robotics:

- **Subnets and CIDR:** `192.168.3.0/24` is 256 addresses; the mask decides who is "local"
  (direct L2) vs "remote" (via a gateway). Misconfigured subnets are the classic "can't reach
  the drone" bug.
- **NAT:** private addresses behind one public IP break peer-to-peer assumptions — a node behind
  NAT can initiate but not be reached, which complicates mesh and requires relays or hole-punching.
- **Multicast:** one sender, many receivers via a group address (e.g. `239.x.x.x`); the network
  replicates packets only where needed. This is how DDS and ROS 2 do efficient discovery and
  fan-out instead of N unicast copies — but many Wi-Fi/MANET links handle multicast poorly
  (sent at the lowest rate, no ACK), a frequent swarm gotcha.
- **MTU and fragmentation:** the maximum packet size (~1500 B Ethernet). Oversize packets
  fragment; a single lost fragment loses the whole packet. Path MTU discovery and keeping
  messages under the MTU avoid this.

---

## 3. TCP — reliability and its cost

TCP gives a **reliable, ordered, congestion-controlled byte stream**. It achieves this with:

- **Three-way handshake** (SYN, SYN-ACK, ACK) to establish state — one round-trip of setup
  latency before any data.
- **Sequence numbers + ACKs + retransmission:** lost segments are detected and resent.
- **Sliding window + flow control:** sender respects the receiver's buffer.
- **Congestion control** (Reno, CUBIC, BBR): probes for bandwidth, backs off on loss. On a lossy
  *wireless* link this is a problem — TCP interprets RF loss as congestion and throttles, even
  though the bandwidth is there.

The hidden cost for real-time data is **head-of-line (HOL) blocking**: because TCP delivers
in order, one lost segment stalls *everything* behind it until it's retransmitted — a single
dropped packet can freeze a video stream for a full RTT. This is why you almost never run a
real-time control or video stream over plain TCP on a contested link.

```
 TCP HOL blocking:
   sent:  [1][2][3][4][5]
   lost:      X            (segment 2)
   recv buffer holds 3,4,5 but delivers nothing until 2 is resent → stall
```

Use TCP for things that must be *complete and ordered* and can tolerate latency: firmware
uploads, configuration, mission plans, logs.

---

## 4. UDP, QUIC, and real-time transport

**UDP** is a thin wrapper over IP: datagrams, no handshake, no retransmission, no ordering, no
congestion control. It can lose, duplicate, and reorder — and that is exactly what you want for
real-time streams, because **fresh data beats complete data**: a control loop wants the *latest*
state, not a retransmitted stale one. You add back only the reliability you need at the app
layer (sequence numbers to drop stale packets, forward error correction, selective ACKs).

```
 Stream type           Transport choice          Why
 ────────────────────  ────────────────────────  ──────────────────────────────
 Control commands      UDP + seq + small FEC      latest wins; no HOL stall
 Live video            UDP/RTP                     drop late frames, don't stall
 Telemetry stream      UDP (or DDS best-effort)    freshness > completeness
 Firmware / config     TCP / QUIC reliable         must be complete and ordered
 Request/response API   gRPC over HTTP/2 or QUIC    structured, multiplexed
```

**QUIC** (the transport under HTTP/3) is the modern best-of-both: it runs over UDP but provides
TCP-like reliability *per stream*, so a loss in one stream doesn't HOL-block the others;
0-RTT/1-RTT connection setup; and built-in TLS 1.3 encryption. It's increasingly used where you
want multiplexed reliable streams without TCP's single-stream HOL penalty. **gRPC** (over
HTTP/2, soon QUIC) gives typed, multiplexed RPC with protobuf — a common choice for structured
service-to-service calls, contrasted with the streaming pub/sub of DDS.

---

## 5. Latency, jitter, and bandwidth math

Three quantities define a link's fitness for a job. Total one-way latency decomposes as:

$$
L = d_{\text{prop}} + d_{\text{trans}} + d_{\text{queue}} + d_{\text{proc}}
$$

- **Propagation** $d_{\text{prop}} = \text{distance}/v$ — speed-of-light floor (~3.3 µs/km in
  fiber, ~3.3 µs/km in air). A geostationary satellite hop is ~250 ms *each way* — unavoidable.
- **Transmission** $d_{\text{trans}} = \text{bits}/\text{bandwidth}$ — time to clock the packet
  onto the wire. Big packets on a slow link dominate here.
- **Queueing** $d_{\text{queue}}$ — waiting in router buffers; the variable, congestion-dependent
  term, and the main source of **jitter** (and of bufferbloat).
- **Processing** $d_{\text{proc}}$ — serialization, crypto, stack traversal.

**Bandwidth-delay product** $BDP = \text{bandwidth} \times RTT$ is the amount of data "in flight"
and sets the window size needed to keep a pipe full. **Throughput** under loss (TCP) is roughly:

$$
\text{Throughput} \approx \frac{MSS}{RTT \cdot \sqrt{p}}
$$

where $p$ is loss probability — showing why long-RTT, lossy links cripple TCP. For control,
**jitter** matters more than mean latency (a controller can compensate constant delay, not random
delay), so you measure the *distribution's tail* and often add a small jitter buffer that trades
a little latency for smoothness.

---

## 6. Pub/sub, multicast, and DDS/ROS 2

Robotics middleware overwhelmingly uses **publish/subscribe**: producers publish to topics,
consumers subscribe, decoupled in space and time. The dominant standard is **DDS** (Data
Distribution Service), which underlies **ROS 2**.

DDS's power is its **Quality of Service (QoS)** contract, negotiated per topic:

| QoS policy | Options | Use |
|---|---|---|
| Reliability | `BEST_EFFORT` / `RELIABLE` | sensor stream vs command |
| Durability | `VOLATILE` / `TRANSIENT_LOCAL` | late-joiner gets last value |
| History | `KEEP_LAST(n)` / `KEEP_ALL` | ring buffer vs full queue |
| Deadline | period | detect a missing publisher |
| Liveliness | lease + assert | failure detection |

```yaml
# ROS 2 QoS: a control topic wants reliable, shallow, and deadline-monitored;
# a high-rate sensor wants best-effort so a lost sample never stalls the stream.
control_qos:
  reliability: RELIABLE
  history: KEEP_LAST
  depth: 1
  deadline_ms: 20        # alarm if no command within 20 ms
sensor_qos:
  reliability: BEST_EFFORT
  history: KEEP_LAST
  depth: 5
```

DDS discovery and fan-out use **multicast**, which is efficient on a wired LAN but problematic
over Wi-Fi/MANET (multicast is unACKed and sent at base rate) — a real cause of swarm desync, and
why production deployments often switch DDS to unicast discovery or use a different transport on
the radio link. This is the software-protocol counterpart to the physical mesh discussion in
[05_distributed_systems_comms_mesh.md](05_distributed_systems_comms_mesh.md).

---

## 7. Mesh networking and degraded links

A tactical environment is **DDIL**: Disconnected, Intermittent, Limited-bandwidth. Design for it:

- **Mesh routing (MANET):** nodes relay for each other so the network heals around losses.
  Proactive protocols (OLSR) keep routes ready; reactive ones (AODV) find routes on demand;
  hybrid is common. Routing churn under mobility is the hard part.
- **Store-and-forward / DTN:** when there is no end-to-end path, buffer data and forward it when
  a link appears (delay-tolerant networking, as on deep-space and contested links).
- **Adaptive bitrate & graceful degradation:** drop video resolution before dropping the control
  link; prioritize critical traffic with DiffServ/QoS marking so commands beat telemetry beats
  video under contention.
- **Forward error correction (FEC):** add redundancy so the receiver reconstructs lost packets
  without a retransmit round-trip — essential when RTT is long or the link is one-way.
- **Jamming resilience:** frequency hopping, spread spectrum, and directional antennas
  ([27-autonomy-counter-uas-ew.md](27-autonomy-counter-uas-ew.md)); the software must tolerate the
  blackouts these create, so all protocols above assume the link *will* drop.

```
 Priority under contention (DiffServ-style):
   1. safety/abort commands     (always get through)
   2. control / state           (latest-wins UDP)
   3. compressed telemetry      (best-effort)
   4. video                     (adaptive, droppable)
```

The architectural rule for fielded comms: **assume every link fails**, and make the system's
behavior on link loss a *designed*, safe default (loiter, return-to-base, autonomous continuation)
rather than an accident — the same philosophy as the failure handling in
[80-software-distributed-systems-deep.md](80-software-distributed-systems-deep.md) and the safety
cases of [09-foundations-safety-assurance.md](09-foundations-safety-assurance.md).

---

## 8. Practice this week

1. Capture a MAVLink or ROS 2 session in Wireshark; identify each layer's headers on one packet
   and compute the payload-to-overhead ratio for a small message on a narrowband link.
2. Send a real-time stream over TCP and over UDP across a link with 5% induced packet loss
   (`tc netem`); measure end-to-end latency and demonstrate TCP's head-of-line stall vs UDP's
   fresh-but-lossy delivery.
3. Configure two ROS 2 nodes with `RELIABLE` vs `BEST_EFFORT` QoS under loss and observe the
   difference in latency and message completeness.
4. Model a satellite link: compute propagation + transmission + queueing latency and the
   bandwidth-delay product, then size the window/buffer needed to keep it full.

---

## 9. Sources & further study

- **Kurose & Ross — *Computer Networking: A Top-Down Approach*.** The standard, intuition-first
  networking textbook.
- **Tanenbaum & Wetherall — *Computer Networks*.** The comprehensive reference, bottom-up.
- **Stevens — *TCP/IP Illustrated, Vol. 1*.** Packet-level mastery; indispensable for debugging.
- **RFC 9000 (QUIC), RFC 9114 (HTTP/3).** The modern transport, from the source.
- **OMG DDS specification & ROS 2 QoS documentation.** The pub/sub middleware that runs real
  robots.
- **Peterson & Davie — *Computer Networks: A Systems Approach*.** Strong on systems design
  tradeoffs.
- **Comer — *Internetworking with TCP/IP*.** Classic, thorough treatment of IP and routing.

> Framing note: A network is not a wire that either works or doesn't — it is a layered set of
> promises, each of which can break in its own way, over a physical medium that is fundamentally
> unreliable. The engineers who field autonomy on contested links do not assume the network; they
> choose each transport for what it actually guarantees, budget latency and jitter as carefully
> as mass and power, prioritize the bytes that keep the vehicle safe, and design every protocol
> so that when the link dies — and it will — the system does something deliberate, not something
> random.
