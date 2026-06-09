# Cybersecurity Engineering — Threat Models, Defense & Hardening

> **Why this exists.** An autonomous defense system is, by definition, a target. The same
> connectivity that lets a fleet coordinate lets an adversary attempt to take it over; the same
> software that flies the vehicle can be exploited to crash, hijack, or exfiltrate it. In a
> contested environment the threat is not a script kiddie but a capable, resourced adversary who
> will probe the supply chain, the radio link, the ground station, and every interface. Security
> is not a feature you add at the end — it is a property you design in from the threat model
> outward, and a system that is not secure is not safe, no matter how good its control loops are.
> The engineer who thinks like an attacker and builds like a defender is the one whose system
> survives contact with a real adversary.
>
> **What mastering it makes you.** The engineer who threat-models before writing code; who knows
> the OWASP and memory-safety vulnerability classes cold and writes code that avoids them; who
> builds defense in depth and assumes breach; who hardens the network, the host, and the supply
> chain; and who designs for zero trust so that one compromised node does not become a
> compromised fleet.

This module hardens everything else in the band: the services of
[80-software-distributed-systems-deep.md](80-software-distributed-systems-deep.md), the links of
[83-software-networking-and-protocols.md](83-software-networking-and-protocols.md), the data of
[84-software-databases-and-data-engineering.md](84-software-databases-and-data-engineering.md),
and the models of [85-software-mlops-and-ml-infrastructure.md](85-software-mlops-and-ml-infrastructure.md).
It rests on the cryptography of [87-software-cryptography-applied.md](87-software-cryptography-applied.md),
extends the operational digital-resilience and OPSEC of [36-trust-safety-opsec-and-digital-resilience.md](36-trust-safety-opsec-and-digital-resilience.md),
connects to the EW/jamming threat of [27-autonomy-counter-uas-ew.md](27-autonomy-counter-uas-ew.md)
and [26-autonomy-gnss-jamming-spoofing.md](26-autonomy-gnss-jamming-spoofing.md), shares the
memory-safety concerns of [04-foundations-modern-cpp-realtime.md](04-foundations-modern-cpp-realtime.md),
the engineering rigor of [12-career-software-engineering.md](12-career-software-engineering.md),
and the assurance mindset of [09-foundations-safety-assurance.md](09-foundations-safety-assurance.md).

---

## Table of Contents

1. [Thinking like an adversary — the threat model](#1-thinking-like-an-adversary--the-threat-model)
2. [The vulnerability classes that actually matter](#2-the-vulnerability-classes-that-actually-matter)
3. [Memory safety and the systems layer](#3-memory-safety-and-the-systems-layer)
4. [Authentication, authorization, and secrets](#4-authentication-authorization-and-secrets)
5. [Network and host hardening](#5-network-and-host-hardening)
6. [Zero trust and defense in depth](#6-zero-trust-and-defense-in-depth)
7. [Secure SDLC, supply chain, and detection](#7-secure-sdlc-supply-chain-and-detection)
8. [Practice this week](#8-practice-this-week)
9. [Sources & further study](#9-sources--further-study)

---

## 1. Thinking like an adversary — the threat model

You cannot defend what you have not modeled. A **threat model** answers: what are we protecting,
from whom, and how might they get in? The structured method is **STRIDE**:

| Threat | Violates | Example against an autonomy system |
|---|---|---|
| **S**poofing | Authentication | fake ground station sends commands |
| **T**ampering | Integrity | altered firmware or telemetry |
| **R**epudiation | Non-repudiation | operator denies issuing a command |
| **I**nformation disclosure | Confidentiality | intercepted mission data |
| **D**enial of service | Availability | flooded link, jammed radio |
| **E**levation of privilege | Authorization | sensor node gains command authority |

The **CIA triad** — Confidentiality, Integrity, Availability — names what you defend; STRIDE names
how it's attacked. The discipline is to enumerate **trust boundaries** (every place data crosses
from less-trusted to more-trusted: the radio link, the API, the file parser) and ask what an
attacker who controls the untrusted side can do.

```
 Trust boundaries (where you must validate everything crossing):
   [ adversary RF ] ══▶ │radio│ ══▶ [ flight computer ] ══▶ │bus│ ══▶ [ actuators ]
                        ▲ authenticate + validate here, not after
```

Two mindsets to internalize: **assume breach** (design so a single compromise is contained, not
catastrophic) and **attacker economics** (you do not need perfect security, you need to make
attack cost exceed attacker value — but against a nation-state adversary that bar is very high).

---

## 2. The vulnerability classes that actually matter

The **OWASP Top 10** catalogs the web vulnerability classes; the same root causes recur in
embedded and backend systems. The ones that bite hardest:

- **Injection (SQL, command, etc.):** untrusted input interpreted as code. Cause: mixing data
  and instructions. Fix: parameterized queries / prepared statements, never string-concatenate
  input into a query or shell command.
- **Broken authentication / session management:** weak credentials, predictable tokens, no
  rotation. Fix: strong auth, short-lived tokens, MFA.
- **Broken access control:** the most common serious flaw — a user reaching data or actions they
  shouldn't. Fix: enforce authorization server-side on *every* request, deny by default.
- **Security misconfiguration:** default passwords, open ports, verbose errors, permissive CORS.
- **Vulnerable dependencies:** the bug is in a library you imported (Log4Shell). Fix: SBOM,
  dependency scanning, patch discipline.
- **SSRF / deserialization / insecure design:** the application is tricked into acting as a proxy
  or into instantiating attacker-controlled objects.

```python
# WRONG: string-built SQL is an injection hole.
cur.execute(f"SELECT * FROM users WHERE name = '{name}'")   # ' OR '1'='1

# RIGHT: parameterized query -- data can never be parsed as SQL.
cur.execute("SELECT * FROM users WHERE name = %s", (name,))
```

The unifying lesson: **never trust input, and never let data become code.** Validate, canonicalize,
and bound every input at the trust boundary — the software analogue of the safety-case rigor in
[09-foundations-safety-assurance.md](09-foundations-safety-assurance.md).

---

## 3. Memory safety and the systems layer

In C and C++ — the languages of flight software ([04-foundations-modern-cpp-realtime.md](04-foundations-modern-cpp-realtime.md))
— the dominant vulnerability class is **memory unsafety**, responsible for ~70% of severe CVEs at
Microsoft and Google. The classics:

- **Buffer overflow:** writing past an array's bounds, corrupting adjacent memory or the return
  address (the basis of classic stack-smashing).
- **Use-after-free / double-free:** dereferencing memory that was already released.
- **Integer overflow → undersized allocation → overflow.** A size calculation wraps, a small
  buffer is allocated, and a large copy overflows it.
- **Format string / out-of-bounds read** (Heartbleed: an unchecked length leaked memory contents).

```
 Stack smashing:
   [ local buffer ][ saved frame ptr ][ RETURN ADDRESS ]
        write past ───────────────────▶ overwrite ret → jump to attacker code
```

Defenses, layered:

- **Mitigations** (raise the cost, don't eliminate): stack canaries, ASLR (randomized addresses),
  DEP/NX (non-executable stack), CFI (control-flow integrity). These make exploitation harder, not
  impossible.
- **Safer language constructs:** `std::vector`/`std::array` with bounds checks, smart pointers,
  no raw `strcpy`; static analysis and sanitizers (ASan, UBSan, fuzzing).
- **Memory-safe languages:** **Rust** eliminates whole classes (use-after-free, data races) at
  compile time via ownership and borrowing, which is why it is increasingly chosen for new
  security-critical and even flight-adjacent code. The strategic move for new development is
  Rust-or-bust on the trust boundary.

Memory safety is not optional in a targeted system — an exploitable overflow in a network-facing
parser is a remote vehicle takeover.

---

## 4. Authentication, authorization, and secrets

- **Authentication** (who are you) vs **authorization** (what may you do) — keep them distinct.
  Authenticate with strong, phishing-resistant factors; authorize with **least privilege** and
  **deny by default**.
- **Tokens & sessions:** short-lived, signed (JWT with proper validation — verify the signature
  and `alg`, never trust the client), rotated, scoped. Long-lived bearer tokens are a liability.
- **Secrets management:** never hard-code keys or passwords in source or images. Use a secrets
  manager (Vault, cloud KMS), inject at runtime, rotate regularly, and audit access. A leaked key
  in a git history is a breach waiting to be found.
- **Mutual TLS (mTLS):** both sides present certificates, so a node proves its identity, not just
  the server — essential for service-to-service and vehicle-to-ground trust
  ([87-software-cryptography-applied.md](87-software-cryptography-applied.md)).

```yaml
# Least privilege: a sensor node may publish telemetry but never issue commands.
role: sensor-node
allow:
  - publish: telemetry/*
deny:
  - publish: commands/*       # elevation of privilege blocked by policy, not hope
  - read:    mission/secret/*
default: deny                 # anything not explicitly allowed is refused
```

The recurring failure is **broken access control**: enforcing permissions in the UI but not the
API, or trusting a client-supplied role. Enforce authorization **server-side, on every request,**
against the authenticated identity — never the client's claim.

---

## 5. Network and host hardening

Reduce the **attack surface** — every open port, running service, and installed package is a
potential entry point.

**Network:**
- **Segmentation:** put the flight-critical bus, the mission computer, and the management plane on
  separate networks/VLANs so a breach of one doesn't reach the others (the architecture mirrors
  the partitioning of [82-software-real-time-operating-systems.md](82-software-real-time-operating-systems.md)).
- **Firewalls / allowlists:** default-deny inbound; allow only required flows. Egress filtering
  catches exfiltration and command-and-control callbacks.
- **Encrypt everything in transit** (TLS/mTLS, encrypted radio) so interception yields nothing.

**Host:**
- **Minimal base image / distroless:** fewer packages = fewer CVEs. No shell, no compilers in
  production images.
- **Least privilege at runtime:** drop root, drop Linux capabilities, read-only filesystem,
  seccomp/AppArmor/SELinux to restrict syscalls; **eBPF**-based tools (Falco, Cilium) for runtime
  detection and policy enforcement at the kernel level.
- **Patch discipline:** known-CVE exploitation is the most common breach vector; a fast,
  reliable patch pipeline beats any clever defense.

```
 Hardening = shrink + isolate + monitor:
   shrink   → minimal image, close ports, remove services
   isolate  → segment networks, drop privileges, sandbox (seccomp/SELinux)
   monitor  → eBPF runtime detection, logs to a tamper-evident store
```

---

## 6. Zero trust and defense in depth

The old model — a hard perimeter and a soft, trusted interior — fails the moment one node is
breached or one link is in adversary territory. **Zero trust** replaces it: *never trust, always
verify*; every request is authenticated, authorized, and encrypted regardless of network location.

Core tenets:
- **Verify explicitly** every access (identity, device posture, context), not once at a gateway.
- **Least-privilege access** with just-in-time, just-enough permissions.
- **Assume breach:** micro-segment, encrypt end-to-end, and limit blast radius so a compromised
  sensor cannot command an effector.

**Defense in depth** layers independent controls so no single failure is fatal:

```
   perimeter (firewall)
     └─ network segmentation (VLAN/micro-seg)
          └─ host hardening (seccomp, least priv)
               └─ app security (input validation, authz)
                    └─ data security (encryption, access control)
                         └─ detection & response (logging, eBPF, SIEM)
   an attacker must defeat EVERY layer; you must hold ANY one
```

This is the security expression of the same philosophy that runs through the safety
([09-foundations-safety-assurance.md](09-foundations-safety-assurance.md)) and distributed-failure
([80-software-distributed-systems-deep.md](80-software-distributed-systems-deep.md)) modules:
assume things fail, contain the damage, and degrade into a known-safe state.

---

## 7. Secure SDLC, supply chain, and detection

Security is a lifecycle, not a gate.

- **Secure SDLC:** threat-model in design; secure-code and review in development; SAST/DAST and
  dependency scanning in CI; pentest before release; monitor in production. "Shift left" — the
  cheapest bug to fix is the one caught in design.
- **Supply chain:** modern attacks target *how you build*, not just what you run (SolarWinds,
  xz-utils). Defenses: a **Software Bill of Materials (SBOM)**, pinned and verified dependencies,
  signed artifacts and provenance (Sigstore, SLSA), reproducible builds, and hardened CI/CD with
  least-privilege runners. In defense, supply-chain integrity is a national-security concern, not a
  hygiene checkbox.
- **Detection & response:** assume some attacks succeed. Centralized, **tamper-evident logging**
  (append-only, off-host), anomaly detection, and an incident-response plan with practiced
  runbooks. Mean-time-to-detect and mean-time-to-respond are the metrics that matter once
  prevention fails.

```
 Secure SDLC:
  design ─▶ develop ─▶ build/CI ─▶ release ─▶ operate
   threat   secure     SAST/DAST   pentest    monitor +
   model    coding     SBOM, sign  gate       respond
   ◀────────── feedback: every incident hardens the earlier stages ──────────
```

---

## 8. Practice this week

1. Build a STRIDE threat model for a small vehicle-to-ground system: enumerate assets, trust
   boundaries, and one mitigation per STRIDE category.
2. Write a deliberately injectable endpoint, exploit it, then fix it with parameterized queries
   and input validation; do the same for a command-injection path.
3. Compile a C program with a buffer overflow; exploit it with and without ASLR/stack canaries to
   see what each mitigation costs the attacker; then rewrite the parser in Rust and show the class
   is gone.
4. Harden a container: start from distroless, drop root and capabilities, add a seccomp profile,
   and scan the image for CVEs; document the attack-surface reduction.
5. Generate an SBOM for a real project, scan it for known CVEs, and set up signed builds with
   Sigstore.

---

## 9. Sources & further study

- **Anderson — *Security Engineering*.** The definitive, systems-level treatment; free online and
  endlessly re-readable.
- **Shostack — *Threat Modeling: Designing for Security*.** The practical STRIDE method.
- **Stuttard & Pinto — *The Web Application Hacker's Handbook*.** How web attacks actually work.
- **OWASP Top 10 & OWASP ASVS.** The living catalog of vulnerability classes and verification
  requirements.
- **Erickson — *Hacking: The Art of Exploitation*.** Memory-corruption exploitation from first
  principles — understand the attack to build the defense.
- **NIST SP 800-207 (Zero Trust Architecture) & SP 800-53.** The authoritative frameworks.
- **SLSA framework & Sigstore docs.** Supply-chain integrity in practice.
- **MITRE ATT&CK.** The adversary tactics-and-techniques knowledge base for detection.

> Framing note: Security is not a wall you build once — it is an adversarial process against an
> opponent who adapts, and a system is exactly as secure as its weakest reachable boundary. The
> engineers who field systems that survive contact with a real adversary threat-model from the
> outside in, refuse to let data become code, choose memory safety where the stakes are highest,
> assume every component will eventually be breached, and design so that when one falls the rest
> hold — because a system that is not secure is not safe, and in a contested environment, not safe
> means lost.
