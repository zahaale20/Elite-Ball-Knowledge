# How the Internet Works — From Your Click to the Page

> **Why this exists.** You use the internet thousands of times a day, yet for most people it's pure magic: you type a name, and a page from a machine on the other side of the planet appears in a fraction of a second. That "magic" is actually a beautifully layered system of agreements — addresses, packets, routers, and protocols — each solving one problem and trusting the others to do their part. The whole thing is one of humanity's great collaborative machines, and almost nobody owns or controls it. Understanding it demystifies your daily life and makes you harder to fool about privacy, security, and how the digital world really runs.
> **What understanding it gives you.** You'll be able to reason about why a site is slow, what "the cloud" really is, why public Wi-Fi is risky, what the padlock icon actually means, and where your data goes when you hit Enter. You'll see the internet not as one thing but as a stack of simple ideas working together, and that mental model transfers to almost every digital question you'll ever face.

This pairs naturally with [04-how-ai-and-llms-actually-work.md](04-how-ai-and-llms-actually-work.md) (most AI runs on servers reached over this network) and [../compute-and-hardware/02-building-ai-data-centers.md](../compute-and-hardware/02-building-ai-data-centers.md) (the physical buildings on the far end of your click). For the foundational idea that there's no software without hardware, see [../compute-and-hardware/04-foundations-no-software-without-hardware.md](../compute-and-hardware/04-foundations-no-software-without-hardware.md).

---

## 1. The core idea: a network of networks

"Internet" literally means **inter-network** — a way for separately owned networks (your home Wi-Fi, your phone carrier, a university, a giant company) to talk to each other using a shared set of rules. No one runs the whole thing. It works because everyone agrees to the same **protocols** — like a common postal system where any post office can hand a letter to any other.

The genius of its design is **layering**. Each layer does one job and doesn't care how the layers below it work. Your web browser doesn't know whether your data travels over fiber, copper, or radio — it just trusts the lower layers to deliver. This separation is why the internet could grow from a few research computers to billions of devices without being redesigned.

```
What you think about     →   Layer        →   What it handles
"open this website"          Application      HTTP, your browser, the page
"is this connection safe?"   Security (TLS)   encryption, the padlock
"deliver all of it, in order" Transport (TCP) reliability, ordering
"where does it go?"          Internet (IP)    addresses, routing
"send the actual signal"     Link/Physical    Wi-Fi, fiber, cables, radio
```

We'll follow a single click down and back up this stack.

---

## 2. Names and addresses: DNS

You type `example.com`. But computers don't find each other by name — they use **IP addresses**, numeric labels like `93.184.216.34` (or a longer form in the newer IPv6 system). Names are for humans; numbers are for machines.

The **Domain Name System (DNS)** is the internet's phone book. It translates the human name into the machine address. When you hit Enter:

1. Your device asks a **DNS resolver** (often run by your provider or a public service): "What's the address for example.com?"
2. The resolver, if it doesn't already know, asks a chain of authoritative servers until it finds the answer.
3. The address comes back, and your device can now make the actual connection.

```
You: "example.com?"
   → Resolver → root servers → ".com" servers → example.com's server
   ← "It's 93.184.216.34"
```

This lookup happens in milliseconds and is **cached** (remembered) at every level so it doesn't repeat constantly. DNS is so fundamental that when it breaks, huge swaths of the internet appear "down" even though the actual websites are fine — people just can't find the addresses.

---

## 3. Packets: cutting everything into pieces

Here's a counterintuitive truth: when you load a page or stream a video, your data isn't sent as one continuous stream. It's **chopped into small chunks called packets**, each sent independently.

Each packet is like a postcard with:
- A piece of the data (the payload).
- The destination address (where it's going).
- The source address (where it came from).
- A sequence number (where it fits in the original whole).

Why bother? Because packet-switching is **robust and efficient**:
- If one packet is lost, only that small piece is resent — not the whole file.
- Packets can take **different routes** to the same destination and be reassembled at the end.
- Many conversations can share the same wires at once, interleaving their packets.

This design — invented for resilience — means there's no single fragile "line" between you and a server. The network finds a way, packet by packet, even if parts of it fail.

---

## 4. IP and routers: finding the way

The **Internet Protocol (IP)** defines the addressing and the rules for forwarding packets toward their destination. The workhorses that move packets are **routers** — specialized computers whose entire job is to read a packet's destination and pass it to the next router closer to the goal.

No single router knows the full path. Each just knows "for this destination, the next best hop is *that* direction," like a relay of people each pointing you one step closer. A packet from your laptop might pass through a dozen or more routers — your home router, your provider, a regional hub, an undersea cable, and finally the destination's network.

```
[Your device] → [Home router] → [ISP] → [Regional hub]
   → [Backbone / undersea cable] → [Destination's network] → [Server]
```

This hop-by-hop relay is why the internet is so resilient: if a link goes down, routers reroute around it automatically. It's also why distance and the number of hops affect speed — every hop adds a tiny delay (**latency**).

---

## 5. TCP: making it reliable

IP gets packets *toward* the destination, but it makes no promises — packets can arrive out of order, duplicated, or not at all. That's where the **Transmission Control Protocol (TCP)** comes in. TCP sits on top of IP and turns unreliable packet delivery into a **reliable, ordered stream**.

TCP's tricks:
- **Reassembly** — uses sequence numbers to put packets back in the right order.
- **Acknowledgments** — the receiver confirms what it got; anything unconfirmed is resent.
- **Flow & congestion control** — TCP slows down if the network is congested and speeds up when it's clear, so the internet doesn't collapse under its own traffic.

The connection starts with a quick **three-way handshake** — a "Hello / Hello back / Got it" exchange that sets up the conversation:

```
You → Server:  SYN      ("let's talk")
You ← Server:  SYN-ACK  ("sure, I'm ready")
You → Server:  ACK      ("great, here we go")
```

For things where perfect reliability matters less than speed — live video, gaming, voice calls — a leaner protocol called **UDP** is used instead, trading guaranteed delivery for lower delay. (A dropped frame in a video call is better than a frozen, "catching up" call.)

---

## 6. HTTP: the language of the web

Now the two computers can reliably exchange data — but they need to agree on *what* to say. For websites, that language is **HTTP (HyperText Transfer Protocol)**. It's a simple request/response conversation:

- Your browser sends a **request**: "GET me the page at /index.html."
- The **server** sends back a **response**: a status code (like `200 OK` or the infamous `404 Not Found`) plus the content — HTML, images, scripts.

Your browser then **renders** that content into the visual page you see, fetching additional pieces (images, fonts, code) with more requests as needed. A single modern web page can trigger dozens or hundreds of these requests behind the scenes.

| Status code | Meaning |
|---|---|
| 200 | OK — here's your page |
| 301/302 | Moved — go look over there |
| 404 | Not found — no such page |
| 500 | Server error — the server broke |
| 403 | Forbidden — you're not allowed |

HTTP is **stateless** — each request stands alone, with no memory of the last. To remember you (logins, carts), sites use **cookies**: small tokens your browser stores and sends back, letting the server recognize you across requests.

---

## 7. Servers, the cloud, and CDNs

On the far end of your request is a **server** — fundamentally just a computer whose job is to wait for requests and respond. "The cloud" is a friendly name for **vast warehouses of these servers** (data centers) rented out by companies so others don't have to own physical machines. When you "store files in the cloud," they live on real disks in a real building somewhere — you've just outsourced the hardware.

A clever optimization sits in between: the **Content Delivery Network (CDN)**. Instead of every user fetching content from one distant origin server, CDNs keep **copies of popular content at many locations around the world**. You're served from the nearest copy, slashing distance and load.

```
Without CDN:  Users everywhere → one server in one city (slow, fragile)

With CDN:     User in Tokyo   → copy in Tokyo
              User in Berlin  → copy in Berlin
              User in Lima    → copy in Lima
```

This is why a global site can feel instant everywhere, and why a viral video doesn't melt a single server — the load is spread across thousands of edge copies.

---

## 8. TLS: the padlock and why it matters

By default, packets are like postcards — anyone handling them along the way could read them. **TLS (Transport Layer Security)** wraps the conversation in **encryption**, turning postcards into sealed, tamper-evident envelopes. When you see `https://` and a padlock, TLS is active.

TLS does three things:
- **Encryption** — only you and the server can read the contents; eavesdroppers see scrambled noise.
- **Integrity** — if data is altered in transit, it's detected.
- **Authentication** — a **certificate** (issued by a trusted authority) proves the server really is who it claims, not an impostor.

The clever part is how two strangers agree on a secret key over a public network without anyone listening being able to steal it — using **public-key cryptography**, where a public "lock" anyone can use pairs with a private "key" only the server holds. This is what makes online banking and shopping possible.

> The padlock means the **connection** is encrypted and the site is who it says it is. It does **not** mean the site is honest or safe — scammers can use HTTPS too. It protects the pipe, not the intentions of who's at the other end.

---

## 9. The whole journey in one picture

Let's trace a single click from start to finish:

```
1. You type "example.com" and press Enter.
2. DNS  : name → IP address (93.184.216.34).
3. TCP  : three-way handshake opens a reliable connection.
4. TLS  : handshake sets up encryption (the padlock).
5. HTTP : browser sends "GET /"; the request is...
6. IP   : ...split into packets, addressed, and...
7. Routers: ...relayed hop by hop across networks/oceans.
8. CDN/Server: nearest copy responds with the page content.
9. Packets return, TCP reassembles them in order.
10. Browser renders HTML/CSS/JS into the page you see.
   (All of this, typically, in well under a second.)
```

Every step is a separate, simple agreement. Stacked together, they create something that feels seamless and instant.

---

## 10. Practical takeaways

- **"The internet is slow" usually has a specific cause** — DNS, latency (distance/hops), a busy server, or your local Wi-Fi. The layered model helps you locate it.
- **Public Wi-Fi is safer than it used to be** because most sites now use HTTPS/TLS — but the padlock protects the connection, not your judgment about the site.
- **"The cloud" is just someone else's computers** in a data center. Convenient, but your data physically lives somewhere real, under someone else's control.
- **DNS outages take down "the internet"** for many people even when the actual sites work — they just can't be found.
- **A 404 is the site's fault; a DNS failure is the lookup's fault** — different layers, different fixes.
- **No one controls the whole internet.** Its resilience comes from being a network of independent networks following shared rules.

---

## Sources & further study

- *Tubes: A Journey to the Center of the Internet* — Andrew Blum (the physical internet, vividly told)
- *How the Internet Really Works* — Article 19 / catnip (accessible illustrated guide)
- *Computer Networking: A Top-Down Approach* — Kurose & Ross (the classic textbook, deeper)
- *The Internet Is Not What You Think It Is* — Justin E. H. Smith (philosophical context)
- *Where Wizards Stay Up Late* — Hafner & Lyon (the origin story of the internet)
- Cloudflare's "Learning Center" and the *How DNS Works* comic (free, excellent intros)

> Framing note: The internet is not a single machine but a stack of agreements — names, addresses, packets, reliability, and trust — each solving one problem and assuming the others are handled. Once you see it as layers rather than magic, every digital mystery from a slow page to a privacy question becomes a question of *which layer*, and that single shift makes the whole online world legible.
