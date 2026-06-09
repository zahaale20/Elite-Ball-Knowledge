# Applied Cryptography — Confidentiality, Integrity & Trust

> **Why this exists.** Every secured link, signed firmware image, authenticated command, and
> trusted identity in a defense system rests on cryptography. When a vehicle accepts a command,
> something must prove it came from the real operator and was not altered in flight; when
> telemetry crosses a contested link, something must keep it unreadable to an interceptor; when
> you push a firmware update, something must prove the binary is genuine and not a trojan.
> Cryptography provides these guarantees — confidentiality, integrity, authenticity — but only if
> applied correctly, and the history of security is largely a history of correct primitives used
> incorrectly. The engineer who understands what each tool guarantees, and the pitfalls that void
> those guarantees, is the one who can build trust into a system that an adversary is actively
> trying to subvert.
>
> **What mastering it makes you.** The engineer who never rolls their own crypto but knows
> exactly which standard primitive to use and how; who can explain why a hash is not encryption,
> why ECB leaks structure, and why nonce reuse is catastrophic; who reasons about key exchange,
> signatures, and PKI; and who builds TLS/mTLS, signed updates, and secure storage that hold up
> against a capable adversary.

This module is the mathematical backbone of the security engineering in
[86-software-cybersecurity-engineering.md](86-cybersecurity-engineering.md), the
confidentiality and integrity layer over the networks of
[83-software-networking-and-protocols.md](83-networking-and-protocols.md), and the trust
that the distributed systems of [80-software-distributed-systems-deep.md](80-distributed-systems-deep.md)
and the data stores of [84-software-databases-and-data-engineering.md](84-databases-and-data-engineering.md)
depend on. It underpins the OPSEC and resilience of [36-trust-safety-opsec-and-digital-resilience.md](../information-environment/36-trust-safety-opsec-and-digital-resilience.md),
secures the model supply chain of [85-software-mlops-and-ml-infrastructure.md](85-mlops-and-ml-infrastructure.md),
relates to the GNSS authentication problem of [26-autonomy-gnss-jamming-spoofing.md](../autonomy/26-gnss-jamming-spoofing.md),
and applies the rigor of [12-career-software-engineering.md](../career/12-software-engineering.md)
and [09-foundations-safety-assurance.md](../foundations/09-safety-assurance.md). The math foundations
sit in [03-foundations-mathematics.md](../foundations/03-mathematics.md).

---

## Table of Contents

1. [The three guarantees and Kerckhoffs's principle](#1-the-three-guarantees-and-kerckhoffss-principle)
2. [Symmetric encryption](#2-symmetric-encryption)
3. [Hashes and message authentication](#3-hashes-and-message-authentication)
4. [Asymmetric cryptography](#4-asymmetric-cryptography)
5. [Key exchange and forward secrecy](#5-key-exchange-and-forward-secrecy)
6. [PKI, certificates, and TLS](#6-pki-certificates-and-tls)
7. [Practical pitfalls and the future](#7-practical-pitfalls-and-the-future)
8. [Practice this week](#8-practice-this-week)
9. [Sources & further study](#9-sources--further-study)

---

## 1. The three guarantees and Kerckhoffs's principle

Cryptography provides distinct, separable guarantees — confusing them is the root of most misuse:

| Guarantee | Question answered | Primitive |
|---|---|---|
| **Confidentiality** | Can an eavesdropper read it? | Encryption (AES, ChaCha20) |
| **Integrity** | Was it altered? | Hash + MAC (SHA-2, HMAC) |
| **Authenticity** | Who sent it? | MAC (shared key) or signature (public key) |
| **Non-repudiation** | Can the sender deny it? | Digital signature only |

Encryption alone does **not** give integrity — an attacker can flip ciphertext bits and corrupt
the plaintext undetectably unless you also authenticate. This is why modern systems use
**authenticated encryption** (AEAD), which combines both.

**Kerckhoffs's principle** is the foundational rule: *the security must rest entirely in the key,
not in the secrecy of the algorithm.* Assume the adversary knows your design; only the key is
secret. The corollary every engineer must obey: **never roll your own crypto.** Use vetted,
standard, open implementations (libsodium, the platform's TLS), because subtle flaws invisible to
the designer are found by adversaries — and the danger is not the math, it is the *implementation
and usage*.

---

## 2. Symmetric encryption

In **symmetric** crypto, the same secret key encrypts and decrypts. It is fast (gigabytes/sec
with hardware AES) and used for bulk data.

- **Block ciphers (AES):** encrypt fixed 128-bit blocks. The **mode of operation** matters
  enormously:
  - **ECB (never use):** encrypts each block independently, so identical plaintext blocks produce
    identical ciphertext — it leaks structure (the infamous "ECB penguin" is still visible).
  - **CTR / GCM:** turn the block cipher into a stream by encrypting a counter; **GCM** adds
    authentication (it is AEAD), and is the modern default.
- **Stream ciphers (ChaCha20):** generate a keystream XORed with plaintext; fast in software,
  paired with **Poly1305** for authentication (ChaCha20-Poly1305 is the other modern AEAD,
  preferred where AES hardware is absent).

The non-negotiable rule for stream/counter modes is **never reuse a nonce (IV) with the same
key.** Reuse XORs two keystreams together and can reveal both plaintexts and, for GCM, forge
authentication. Nonce reuse has broken WEP, real TLS stacks, and more.

```python
# Authenticated encryption (AEAD): one call gives confidentiality AND integrity.
# A fresh random nonce per message is mandatory -- never reuse one with a key.
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

key   = AESGCM.generate_key(bit_length=256)
aesgcm = AESGCM(key)
nonce = os.urandom(12)                       # 96-bit nonce, unique per message
ct = aesgcm.encrypt(nonce, b"ARM motors", b"hdr")   # associated data authenticated, not encrypted
pt = aesgcm.decrypt(nonce, ct, b"hdr")              # raises if tampered -- integrity enforced
```

Always prefer an **AEAD** mode (AES-GCM, ChaCha20-Poly1305). "Encrypt-then-MAC" with separate
primitives is correct if done carefully, but AEAD removes the footgun.

---

## 3. Hashes and message authentication

A **cryptographic hash** (SHA-256, SHA-3, BLAKE2/3) maps arbitrary input to a fixed-size digest
with three properties:

- **Pre-image resistance:** given $h$, infeasible to find $m$ with $H(m)=h$.
- **Second pre-image resistance:** given $m$, infeasible to find $m' \neq m$ with $H(m')=H(m)$.
- **Collision resistance:** infeasible to find *any* $m \neq m'$ with $H(m)=H(m')$.

A hash gives **integrity** (detect change) but **not authenticity** by itself — an attacker who
changes the message can recompute the hash. Critically, a hash is **not encryption**: it is
one-way and has no key.

- **MAC (HMAC):** a keyed hash, $\text{HMAC}(k, m)$, proves the message came from someone holding
  $k$ — integrity *and* authenticity with a shared key. (Do not use a bare `H(k \,\|\, m)` — it is
  vulnerable to length-extension; HMAC's nested construction fixes this.)
- **Password hashing is different:** use a *slow*, salted, memory-hard function — **Argon2**,
  scrypt, or bcrypt — *not* SHA-256. The goal is to make brute-forcing expensive. A unique
  per-password **salt** defeats rainbow tables; the work factor is tuned so each guess costs the
  attacker real time and memory.

$$
\text{collision work} \approx 2^{n/2} \;\text{(birthday bound)} \Rightarrow \text{SHA-256 gives} \approx 2^{128}\ \text{security}
$$

Hashes also build Merkle trees (tamper-evident logs, blockchains, Git), content addressing, and
the integrity checks behind signed firmware.

---

## 4. Asymmetric cryptography

**Public-key** crypto uses a *key pair*: a **public key** anyone may know and a **private key**
kept secret. It solves the problem symmetric crypto cannot: establishing trust between parties who
have never shared a secret.

- **Encryption direction:** encrypt with the *public* key, decrypt with the *private* key → only
  the holder can read (confidentiality to a recipient).
- **Signature direction:** sign with the *private* key, verify with the *public* key → proves the
  holder authored it, unforgeable, and gives **non-repudiation** (only signatures do).

Two families:

- **RSA:** security rests on the hardness of factoring large integers. Simple to understand, but
  large keys (3072+ bits) and slower.
- **Elliptic-curve (ECDSA, Ed25519, ECDH):** equivalent security at far smaller keys (a 256-bit
  curve ≈ 3072-bit RSA), faster, and now the default. **Ed25519** is the modern signature
  standard — fast, misuse-resistant, deterministic.

$$
\text{RSA: factor } n = pq \text{ is hard} \qquad \text{ECC: solve } Q = kP \text{ (discrete log) is hard}
$$

Asymmetric crypto is **slow**, so it is never used for bulk data. Instead it does two things and
hands off: it **exchanges a symmetric key** (then AES does the bulk) and it **signs** (a hash of
the data, not the data itself). This hybrid pattern is the architecture of essentially every
secure protocol.

```
 Hybrid encryption (how real systems work):
   1. asymmetric: exchange/establish a fresh symmetric session key
   2. symmetric (AES-GCM): encrypt the actual bulk data, fast
   3. signature (Ed25519) over a hash: authenticate + integrity
```

---

## 5. Key exchange and forward secrecy

How do two parties agree on a shared secret over a channel an adversary is recording?
**Diffie-Hellman** key exchange: each picks a private value, exchanges public values, and both
compute the same shared secret that an eavesdropper cannot derive.

$$
\text{Alice: } A = g^a,\quad \text{Bob: } B = g^b,\quad \text{shared} = B^a = A^b = g^{ab}
$$

Modern systems use the elliptic-curve variant **ECDH** (e.g. X25519). The crucial property to
demand is **forward secrecy**: use *ephemeral* keys (ECDHE) generated fresh per session and
discarded after. Then even if the long-term private key is later stolen, *past* recorded sessions
stay secret — the adversary who records everything today cannot decrypt it tomorrow with a stolen
key. For a system operating in contested space where traffic is assumed recorded, forward secrecy
is not optional.

Authentication must be bolted onto raw DH, or you get a **man-in-the-middle**: the adversary does
a separate exchange with each side. The fix is to *sign* the exchange (or authenticate it via a
pre-shared certificate / PKI) — which is exactly what TLS does.

---

## 6. PKI, certificates, and TLS

Public-key crypto answers "is this the private-key holder?" but not "is this key really the
ground station's?" **Public Key Infrastructure (PKI)** answers the second with **certificates**: a
**Certificate Authority (CA)** signs a binding of {identity → public key}. You trust the CA, so
you trust what it signs, forming a **chain of trust** up to a root.

```
 Root CA (trusted anchor, in your trust store)
   └─ signs Intermediate CA
        └─ signs  "groundstation.mil"  cert (identity + public key)
   verify: walk chain to a trusted root, check signatures, validity, revocation
```

**TLS** is the protocol that assembles all of the above into a secure channel, and the **TLS 1.3
handshake** is the canonical applied-crypto flow:

```
 TLS 1.3 handshake (simplified):
   Client ──ClientHello + key share (ECDHE)──▶ Server
   Client ◀─ServerHello + key share + cert + signature── Server
   both derive session keys from ECDHE (forward secret)
   server cert verified against PKI chain (authenticity)
   ──▶ AES-GCM / ChaCha20-Poly1305 encrypted application data (confidentiality + integrity)
```

It combines ECDHE (forward-secret key exchange), a signed certificate (PKI authenticity), and
AEAD (bulk confidentiality+integrity) — every primitive in this module, composed correctly.
**mTLS** adds a client certificate so *both* sides authenticate, which is how vehicle↔ground and
service↔service trust is established in a zero-trust architecture
([86-software-cybersecurity-engineering.md](86-cybersecurity-engineering.md)).
**Revocation** (CRL/OCSP) handles compromised certs, and **certificate pinning** hardens against a
rogue or compromised CA — important when the threat model includes nation-state adversaries.

---

## 7. Practical pitfalls and the future

The math is rarely broken; the *usage* is. The recurring failures:

- **Rolling your own crypto** — the cardinal sin; use libsodium / platform TLS.
- **Nonce/IV reuse** — catastrophic for CTR/GCM/stream ciphers.
- **Weak or no randomness** — keys/nonces from a predictable RNG are guessable; always use a CSPRNG
  (`/dev/urandom`, `getrandom`). Bad randomness has broken real wallets and TLS keys.
- **Missing integrity** — encrypting without authenticating; use AEAD.
- **Non-constant-time comparison** — comparing MACs/secrets with `==` leaks via timing; use
  constant-time comparison.
- **Hardcoded / unrotated keys, expired certs, ignored validation errors** — operational rot that
  voids the math.
- **Downgrade attacks** — forcing a weak cipher/version; disable legacy protocols.

```python
# Timing-safe comparison: never compare secrets/MACs with '==' (it short-circuits
# and leaks how many bytes matched via timing).
import hmac
ok = hmac.compare_digest(received_tag, expected_tag)   # constant-time
```

**The quantum horizon:** a large quantum computer would break RSA and ECC (via Shor's algorithm)
but only weaken symmetric crypto (Grover's gives a square-root speedup, so AES-256 stays strong).
**Post-quantum cryptography** (lattice-based ML-KEM/Kyber, ML-DSA/Dilithium, now NIST-standardized)
is being deployed in **hybrid** mode (classical + PQC) precisely because adversaries can *record
now, decrypt later* — a real concern for long-lived defense data. Forward secrecy and PQC together
are the answer to the recording adversary.

---

## 8. Practice this week

1. Encrypt the same image in ECB and in GCM; visualize both and explain why ECB leaks structure
   and why GCM also detects tampering (flip a ciphertext bit and watch decryption fail).
2. Demonstrate nonce reuse on AES-CTR: XOR two ciphertexts made with the same key+nonce and
   recover relationships between the plaintexts.
3. Implement an ECDH (X25519) key exchange between two parties, derive a session key, and use it
   for AES-GCM; then add Ed25519 signatures and show how that stops a man-in-the-middle.
4. Hash a password with SHA-256 and with Argon2; benchmark guess cost for each and explain why
   only the slow, salted, memory-hard function is acceptable.
5. Stand up a mini-PKI: create a root CA, sign a server cert, run a TLS server, and verify the
   chain — then break it (expired cert, wrong CA) and confirm the client refuses.

---

## 9. Sources & further study

- **Aumasson — *Serious Cryptography*.** The best modern practitioner's book; primitives,
  protocols, and pitfalls without heavy math.
- **Ferguson, Schneier & Kohno — *Cryptography Engineering*.** How to apply crypto correctly in
  real systems; required reading for builders.
- **Katz & Lindell — *Introduction to Modern Cryptography*.** The rigorous, proof-based foundation.
- **Boneh & Shoup — *A Graduate Course in Applied Cryptography* (free online).** Deep and current.
- **libsodium / NaCl documentation.** The misuse-resistant library you should actually use.
- **RFC 8446 (TLS 1.3).** The protocol that composes every primitive here, from the source.
- **NIST PQC standards (FIPS 203/204/205) & *Cryptographic Right Answers* (Latacora).** What to use
  today and tomorrow.

> Framing note: Cryptography is not where systems usually break — the primitives are strong; the
> *usage* is where they fall. The engineers who build trust into contested systems never invent
> their own algorithms, compose vetted primitives correctly, treat nonces and randomness and key
> handling as life-or-death details, demand forward secrecy against an adversary who records
> everything, and remember that a perfect cipher behind a hardcoded key, a reused nonce, or an
> ignored certificate error protects nothing at all.
