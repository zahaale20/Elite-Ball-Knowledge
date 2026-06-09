# Twenty Underrated, High-Impact Products You Should Already Be Using

> **Why this exists.** Most "best tools" lists are popularity contests — they tell you about products you already know. The leverage is in the *gap*: tools whose **impact-to-awareness ratio** is absurdly high, where a single afternoon of adoption changes how fast you build, learn, or ship for years. The people who feel ten times more productive than you are rarely smarter; they have quietly assembled a stack of these. This module writes that stack down. Every entry is a *real, available* product (as of mid-2026), chosen because it is **genuinely high-impact and genuinely under-known** relative to that impact — not the thing everyone already tweets about.

> **What internalizing it makes you.** Someone who treats *tooling as a force multiplier*, who can smell a 10× tool before it is famous, and who has removed the friction that silently taxes everyone else — slow installs, brittle infra, lost notes, forgotten knowledge, manual glue work. The goal is not to collect tools; it is to **delete recurring friction permanently**.

This folder is the practical complement to the strategy and skills bands: where [13-companies-skills-to-beat-them.md](../companies/13-skills-to-beat-them.md) tells you *what* to be good at, this tells you *what to install Tuesday morning*. Several entries connect directly to your autonomy stack ([01-autonomy-ml-ai.md](../autonomy/01-ml-ai.md), [03-px4-sitl.md](../autonomy/03-px4-sitl.md)) and to your learning system ([01-mastery-curriculum.md](../01-mastery-curriculum.md)).

---

## How to read this

Three honest rules govern tool adoption, and this list is built around them:

1. **A tool only counts if it removes friction you feel repeatedly.** A clever tool you use once is a toy. The entries below target *recurring* costs — every install, every sync, every fact you forget, every GPU you can't afford.
2. **Adopt at the boundary, not the core.** The cheapest place to try a tool is on a side project or a single workflow. None of these require you to rewrite your life.
3. **Beware the churn.** Tooling moves fast; some of these will be acquired, renamed, or surpassed. The *category* each occupies is the durable insight — when a given product fades, find its successor in the same niche.

Each entry follows the same shape: **what it is → why it's high-impact → why people miss it → how to start → who it's for.**

> **A note on honesty.** This space moves quickly. Treat version-specific claims as "true at time of writing, verify before you bet on it," and prefer the *category* logic over brand loyalty.

---

## Table of contents

**Band A — AI & compute building blocks**
1. [uv — Python tooling that is finally fast](#1-uv--python-tooling-that-is-finally-fast)
2. [Ollama — run real LLMs on your own machine](#2-ollama--run-real-llms-on-your-own-machine)
3. [vLLM — serve models at serious throughput](#3-vllm--serve-models-at-serious-throughput)
4. [Modal — serverless GPUs without owning a cluster](#4-modal--serverless-gpus-without-owning-a-cluster)
5. [DuckDB — a data warehouse in a single file](#5-duckdb--a-data-warehouse-in-a-single-file)

**Band B — Robotics & autonomy leverage**
6. [Rerun — see your multimodal robot data](#6-rerun--see-your-multimodal-robot-data)
7. [Foxglove — observability for robots](#7-foxglove--observability-for-robots)

**Band C — Dev & infrastructure force-multipliers**
8. [Tailscale — your own private network in minutes](#8-tailscale--your-own-private-network-in-minutes)
9. [Zed — a genuinely fast, AI-native editor](#9-zed--a-genuinely-fast-ai-native-editor)
10. [Aider — an AI pair programmer in your terminal](#10-aider--an-ai-pair-programmer-in-your-terminal)
11. [Caddy — HTTPS that just works](#11-caddy--https-that-just-works)
12. [Cloudflare developer platform — the edge as a computer](#12-cloudflare-developer-platform--the-edge-as-a-computer)

**Band D — Knowledge, learning & output**
13. [Anki — never forget anything on purpose](#13-anki--never-forget-anything-on-purpose)
14. [NotebookLM — a research assistant grounded in *your* sources](#14-notebooklm--a-research-assistant-grounded-in-your-sources)
15. [Obsidian — a knowledge base you actually own](#15-obsidian--a-knowledge-base-you-actually-own)
16. [Excalidraw — think with your hands](#16-excalidraw--think-with-your-hands)
17. [Zotero — never lose a citation again](#17-zotero--never-lose-a-citation-again)

**Band E — Personal leverage & ops**
18. [Raycast — your computer at the speed of thought](#18-raycast--your-computer-at-the-speed-of-thought)
19. [ElevenLabs — production-grade voice on demand](#19-elevenlabs--production-grade-voice-on-demand)
20. [Syncthing — sync your files without the cloud](#20-syncthing--sync-your-files-without-the-cloud)

[The meta-skill: building your own stack](#the-meta-skill-building-your-own-stack) · [Sources & further study](#sources--further-study)

---

## Band A — AI & compute building blocks

### 1. uv — Python tooling that is finally fast

- **What it is.** A single Rust-based tool (from Astral, the Ruff team) that replaces `pip`, `virtualenv`, `pip-tools`, `pipx`, and much of `poetry` — installing packages and resolving environments tens to hundreds of times faster.
- **Why it's high-impact.** Python's packaging has been the silent tax on every data/ML/robotics project for a decade: slow installs, broken environments, "works on my machine." `uv` makes environment creation effectively instant and reproducible, which compounds across every project you ever touch.
- **Why people miss it.** Packaging is unglamorous; most people assume the pain is inherent to Python and never look for an escape. It also arrived recently and quietly.
- **How to start.** Install it, then `uv venv` and `uv pip install -r requirements.txt`, or `uv run script.py` for instant ephemeral environments. Migrate one repo and feel the difference.
- **Who it's for.** Anyone who writes Python — especially ML/autonomy work with heavy dependency trees (PyTorch, OpenCV, ROS bridges). Pairs directly with the perception work in [01-autonomy-ml-ai.md](../autonomy/01-ml-ai.md).

### 2. Ollama — run real LLMs on your own machine

- **What it is.** A one-command runtime for downloading and running open-weight LLMs (Llama, Mistral, Qwen, Gemma, and many more) locally, with a clean local API.
- **Why it's high-impact.** It turns your laptop or workstation into a private, offline, zero-marginal-cost AI server. No data leaves the machine — which matters enormously for **export-controlled or classified-adjacent work** ([20-ethics-export-control.md](../career/20-ethics-export-control.md)) where you legally cannot paste content into a cloud API.
- **Why people miss it.** Many assume "real" AI requires a frontier cloud model and a credit card; they never discover how capable a 7–14B model is for summarization, drafting, and code on a decent GPU or Apple Silicon.
- **How to start.** `ollama run qwen2.5` (or similar), then point any OpenAI-compatible client at `localhost:11434`. You already have it installed — wire it into a script and build a private assistant over your own notes.
- **Who it's for.** Anyone handling sensitive data, working offline (think field/SCIF constraints), or who wants unlimited experimentation without per-token billing.

### 3. vLLM — serve models at serious throughput

- **What it is.** A high-performance inference engine for LLMs whose key innovation, *paged attention*, manages the KV-cache like an operating system manages memory — dramatically increasing the number of concurrent requests a GPU can serve.
- **Why it's high-impact.** When you go from "demo on my laptop" (Ollama) to "serve this to a team or a product," throughput and cost per token decide whether it's viable. vLLM is the standard bridge from prototype to production self-hosting.
- **Why people miss it.** It lives one layer below the chat UIs everyone sees; if you've never had to *host* a model, you've never had a reason to find it.
- **How to start.** `vllm serve <model>` exposes an OpenAI-compatible endpoint. Benchmark concurrent requests against a naive loop to see the paged-attention win.
- **Who it's for.** Anyone deploying open models for more than one user, or estimating the real cost of an AI feature.

### 4. Modal — serverless GPUs without owning a cluster

- **What it is.** A platform where you decorate ordinary Python functions and they run in the cloud on the GPUs/CPUs you request, scaling to zero when idle — no Docker, Kubernetes, or infra glue to write.
- **Why it's high-impact.** It collapses the distance between "I have an idea that needs an A100 for ten minutes" and "it's running." You pay only for execution, so expensive experiments become casual.
- **Why people miss it.** People assume GPU access requires either a cloud-console PhD or a five-figure rig. Serverless GPU is a recent category many haven't internalized.
- **How to start.** Wrap a training or batch-inference function, request a GPU, and `modal run` it. Use it for the heavy training in the RL/perception modules ([17-reinforcement-learning.md](../autonomy/17-reinforcement-learning.md)) instead of melting your laptop.
- **Who it's for.** Solo builders and small teams who need elastic compute without an MLOps department. (Competitors: Runpod, Replicate, Baseten — same category.)

### 5. DuckDB — a data warehouse in a single file

- **What it is.** An in-process analytical (OLAP) database — "SQLite for analytics." No server; it queries CSV, Parquet, and JSON directly, often faster than the pandas code people reach for.
- **Why it's high-impact.** It makes gigabytes of data interactive on a laptop with plain SQL, and embeds anywhere (Python, CLI, browser via WASM). It quietly replaces a whole zoo of brittle data scripts.
- **Why people miss it.** "Database" connotes servers and ops, so analysts default to pandas and engineers default to Postgres; the in-process analytical niche is new to most.
- **How to start.** `duckdb` then `SELECT * FROM 'logs/*.parquet'` — point it straight at your flight-log or telemetry exports and aggregate without an ETL step.
- **Who it's for.** Anyone wrangling logs, telemetry, or experiment results — including parsing the data products from [05-test-scaffold.md](../autonomy/05-test-scaffold.md).

---

## Band B — Robotics & autonomy leverage

### 6. Rerun — see your multimodal robot data

- **What it is.** An open-source visualization SDK and viewer purpose-built for *temporal, multimodal* data — log points, images, 3D poses, tensors, and scalars with a few lines of code and scrub through time.
- **Why it's high-impact.** In robotics and CV, the bottleneck is rarely the algorithm — it's *seeing what the system saw* at the moment it failed. Rerun turns "print and guess" debugging into a synchronized 3D/2D timeline, collapsing days of investigation.
- **Why people miss it.** It's young, and many roboticists still hand-roll matplotlib or wrestle with heavier legacy tools, unaware a lightweight purpose-built option exists.
- **How to start.** `rr.log("camera", rr.Image(...))` and `rr.log("pose", rr.Transform3D(...))` inside your perception loop, then scrub. Wire it into the VIO/SLAM work in [22-visual-inertial-odometry.md](../autonomy/22-visual-inertial-odometry.md) and [12-slam-and-mapping.md](../autonomy/12-slam-and-mapping.md).
- **Who it's for.** Anyone building perception, estimation, or planning where data is spatial and time-indexed.

### 7. Foxglove — observability for robots

- **What it is.** A visualization and debugging platform for robotics data (ROS 1/2, MCAP, custom schemas) with composable panels, dashboards, and recording playback — local or web.
- **Why it's high-impact.** It's the "Grafana + Chrome DevTools" of a robot: you compose exactly the plots, 3D scenes, and message inspectors you need, then replay a logged mission to find the moment things diverged. This is the difference between fleet debugging that scales and one that doesn't.
- **Why people miss it.** Teams often limp along with default RViz layouts and ad-hoc rosbag scripts, not realizing how much a real observability layer accelerates incident triage.
- **How to start.** Open an MCAP/rosbag recording, build a layout with a 3D panel + plots + raw messages, and save it as a reusable workspace. Connects naturally to the assurance discipline in [05-test-scaffold.md](../autonomy/05-test-scaffold.md).
- **Who it's for.** Anyone running ROS-based systems or analyzing recorded missions — pairs with Rerun (Rerun for tight code-loop introspection, Foxglove for mission/fleet observability).

---

## Band C — Dev & infrastructure force-multipliers

### 8. Tailscale — your own private network in minutes

- **What it is.** A mesh VPN built on WireGuard that connects all your devices (and servers, and a teammate's laptop) into one secure private network with near-zero configuration, regardless of NAT or firewalls.
- **Why it's high-impact.** "How do I reach my home GPU box / the drone's companion computer / a cloud VM securely from anywhere?" becomes a solved, two-minute problem. It quietly eliminates a whole genre of networking pain (port forwarding, bastion hosts, fragile VPN configs).
- **Why people miss it.** Networking is intimidating; people assume secure remote access is an enterprise-IT ordeal and never discover how trivial mesh networking has become.
- **How to start.** Install on two devices, log in, and they can reach each other by name immediately. SSH into your training box from a café as if it were local; expose a companion computer on a vehicle for field debugging.
- **Who it's for.** Anyone with more than one machine, a home lab, or remote hardware. (Open-source self-hosted alternative: Headscale.)

### 9. Zed — a genuinely fast, AI-native editor

- **What it is.** A code editor written in Rust by the creators of Atom, built for speed, real-time collaboration, and built-in AI assistance.
- **Why it's high-impact.** Editor latency is a tax you pay thousands of times a day. Zed's responsiveness — and its native, non-bolted-on AI and pairing — make it a credible daily driver, not a curiosity.
- **Why people miss it.** VS Code's gravity is immense; most developers never seriously evaluate an alternative even when a faster one exists.
- **How to start.** Open your current project in it for a week of real work; pay attention to keystroke latency and the collaboration features. Keep VS Code for its extension ecosystem if needed — the point is to *feel* what fast costs you elsewhere.
- **Who it's for.** Developers who value latency and want first-class AI/collab without a pile of plugins.

### 10. Aider — an AI pair programmer in your terminal

- **What it is.** An open-source command-line tool that pairs an LLM with your git repository: it reads your code, proposes edits across files, and commits them with sensible messages — model-agnostic (cloud or, via Ollama, fully local).
- **Why it's high-impact.** It brings agentic, repo-aware editing into the terminal-and-git workflow many serious engineers prefer, with a clean audit trail (every change is a commit you can review or revert). Combined with Ollama it's a *private* coding agent.
- **Why people miss it.** Attention concentrates on a few GUI AI editors; a scriptable, terminal-native, model-agnostic agent flies under the radar.
- **How to start.** `aider` inside a git repo, describe a change, review the diff, accept or reject. Point it at a local model for sensitive code.
- **Who it's for.** Terminal-and-git developers who want AI assistance without leaving their workflow or sending code to a third party.

### 11. Caddy — HTTPS that just works

- **What it is.** A web server and reverse proxy that obtains and renews TLS certificates automatically by default — production HTTPS from a config file a few lines long.
- **Why it's high-impact.** "Set up a secure web service" is, for most people, an afternoon of Nginx + certbot + cron + renewal anxiety. Caddy makes it a two-line `Caddyfile`. The friction it removes is the reason so many side projects never ship behind a real domain.
- **Why people miss it.** Nginx/Apache are the defaults everyone learned; automatic-HTTPS-by-default is a genuinely newer idea that hasn't displaced muscle memory.
- **How to start.** A `Caddyfile` of `example.com { reverse_proxy localhost:8080 }` gives you a live, auto-renewing HTTPS site. Use it to put a clean front on a Modal/Ollama-backed service.
- **Who it's for.** Anyone self-hosting a service, demo, or internal tool.

### 12. Cloudflare developer platform — the edge as a computer

- **What it is.** A suite — Workers (serverless compute at the edge), R2 (S3-compatible object storage with no egress fees), Pages, D1, and Tunnel (expose a local service publicly without opening a port) — that treats the global edge as a programmable computer.
- **Why it's high-impact.** It removes both *cost* surprises (R2's no-egress model upends storage economics) and *ops* surprises (Workers and Tunnel deploy globally with almost no infrastructure). Tunnel alone — securely exposing `localhost` to a teammate or webhook in seconds — is a daily quality-of-life win.
- **Why people miss it.** People know Cloudflare as "the thing in front of websites" and never realize it's become a full developer platform.
- **How to start.** Deploy a Worker "hello world," move a bucket of artifacts to R2 to feel the egress savings, and use `cloudflared tunnel` to share a local demo.
- **Who it's for.** Anyone shipping web services, storing large artifacts (datasets, model weights), or needing to expose local work safely.

---

## Band D — Knowledge, learning & output

### 13. Anki — never forget anything on purpose

- **What it is.** A spaced-repetition flashcard system that schedules each card for review at the precise interval research suggests you're about to forget it — converting study time into durable memory.
- **Why it's high-impact.** This is the single highest-leverage *learning* tool in this list, and it underwrites this entire repository. The bottleneck in mastering a field is not exposure; it's **retention**. Anki makes forgetting a solved problem, which is how medical students hold thousands of facts and how you can actually keep the math from [03-mathematics.md](../foundations/03-mathematics.md).
- **Why people miss it.** It's old, the interface is unglamorous, and "flashcards" sounds like school. People underestimate it precisely because it isn't shiny.
- **How to start.** Make cards as you read these guides — one fact or one equation per card, in your own words. Review daily for ten minutes. Compounding does the rest.
- **Who it's for.** Anyone trying to *master* anything, including this curriculum. See the learning method in [01-mastery-curriculum.md](../01-mastery-curriculum.md).

### 14. NotebookLM — a research assistant grounded in *your* sources

- **What it is.** A tool (from Google) that lets you upload your own documents — PDFs, notes, transcripts — and ask questions answered *only* from those sources, with citations, plus generated summaries and audio overviews.
- **Why it's high-impact.** It attacks the worst failure mode of chatbots — confident hallucination — by grounding answers in *material you trust*. Drop a stack of papers or your own notes in and interrogate them; the citations let you verify every claim.
- **Why people miss it.** It's quieter than the headline chatbots and people assume all AI is the same "ask anything" box, missing the grounded-RAG distinction.
- **How to start.** Upload a few of these study-guide files plus the papers behind them and ask cross-cutting questions; check it against the [Sources](#sources--further-study). (Self-hosted, private alternatives exist — pair Ollama with a local RAG tool when sources are sensitive.)
- **Who it's for.** Anyone synthesizing a body of literature — exactly the research mode behind [12-technical-communication.md](../career/12-technical-communication.md).

### 15. Obsidian — a knowledge base you actually own

- **What it is.** A note-taking app over a folder of plain Markdown files on your disk, with bidirectional links and a graph view — local-first, no lock-in.
- **Why it's high-impact.** Because the data is *just Markdown files you own*, your second brain outlives any company. Linking notes turns a pile of notes into a navigable web of ideas — the same structure these cross-linked guides use.
- **Why people miss it.** The note-taking market is loud and churns constantly; the "it's just your own Markdown files" simplicity reads as boring next to flashier cloud apps.
- **How to start.** Point it at a folder (this very repo would work) and start linking related notes with `[[wikilinks]]`. Watch the graph reveal connections you didn't plan.
- **Who it's for.** Anyone building durable personal knowledge who refuses vendor lock-in. (Plain-text alternatives: Logseq, or just Markdown + grep.)

### 16. Excalidraw — think with your hands

- **What it is.** A virtual whiteboard with a deliberately hand-drawn aesthetic for diagrams, architectures, and sketches — free, fast, and exportable, with a local/offline mode.
- **Why it's high-impact.** Thinking visually is underrated; a quick architecture sketch resolves arguments and exposes gaps that prose hides. Excalidraw removes all friction from "let me just draw it," which is why it shows up in so many good design discussions.
- **Why people miss it.** People reach for heavyweight diagramming suites and bounce off the friction, concluding diagramming is slow — when a frictionless tool was a tab away.
- **How to start.** Sketch the `sense → perceive → estimate → decide → act` loop from [01-mastery-curriculum.md](../01-mastery-curriculum.md) before your next design review. Keep diagrams in your repo next to the code.
- **Who it's for.** Anyone who designs systems, explains them, or thinks better with a picture.

### 17. Zotero — never lose a citation again

- **What it is.** A free, open-source reference manager that captures papers and their metadata from the browser, organizes a searchable library, stores PDFs, and generates citations/bibliographies in any style.
- **Why it's high-impact.** Serious technical work generates a sprawl of papers; without a system, you re-find the same reference five times and can't cite cleanly. Zotero turns your reading into a permanent, searchable, citable asset — and it's *yours*, not locked in a publisher's silo.
- **Why people miss it.** It feels like an "academics only" tool; engineers underestimate how much research-grade reading their work actually involves.
- **How to start.** Install the browser connector, save every paper you open behind these guides, and let your library become the backbone of your technical writing ([12-technical-communication.md](../career/12-technical-communication.md)).
- **Who it's for.** Anyone who reads and cites papers — every entry in the [autonomy](../autonomy) band leans on a literature you should be capturing.

---

## Band E — Personal leverage & ops

### 18. Raycast — your computer at the speed of thought

- **What it is.** A keyboard-driven launcher (macOS) that replaces Spotlight and absorbs a hundred small tasks — app switching, clipboard history, snippets, window management, scripts, calculations, and extensions — behind one hotkey.
- **Why it's high-impact.** It removes the *micro-friction* that silently consumes your day: reaching for the mouse, hunting for a window, re-typing the same boilerplate. Each save is tiny; the aggregate over a career is enormous, and it keeps you in flow ([16-productivity-deep-work.md](../career/16-productivity-deep-work.md)).
- **Why people miss it.** The default Spotlight is "good enough," so people never feel the gap until they see someone fly through their machine.
- **How to start.** Replace Spotlight, turn on clipboard history and window management, and add two or three extensions you'd actually use. (Cross-platform alternatives: Albert, Flow Launcher, Ulauncher.)
- **Who it's for.** Anyone on a keyboard all day who values flow over friction.

### 19. ElevenLabs — production-grade voice on demand

- **What it is.** A text-to-speech and voice-cloning platform whose output is convincingly natural across many languages, with an API.
- **Why it's high-impact.** It collapses the cost of producing spoken audio — narration, accessibility, training material, prototyping a voice interface — from a studio booking to an API call. For anyone who teaches or documents, it turns written material into listenable material instantly.
- **Why people miss it.** Voice AI doesn't trend the way chat does, so its leap in quality went underappreciated by people outside media/content.
- **How to start.** Convert one of these guides into an audio walkthrough for your commute, or prototype a spoken status read-out for a system. **Use responsibly** — voice cloning carries real consent and impersonation risks ([20-ethics-export-control.md](../career/20-ethics-export-control.md)).
- **Who it's for.** Educators, content makers, accessibility-minded builders, and anyone prototyping voice interfaces.

### 20. Syncthing — sync your files without the cloud

- **What it is.** Open-source, peer-to-peer, continuous file synchronization between your own devices — encrypted in transit, with no central server and no third party storing your data.
- **Why it's high-impact.** It gives you Dropbox-like convenience with *zero* cloud exposure and no storage bill — which is exactly what you need for **sensitive, large, or export-controlled data** that legally or practically can't live on a consumer cloud. Datasets, model weights, and field logs sync directly between your machines.
- **Why people miss it.** "File sync = cloud" is so ingrained that the peer-to-peer alternative is invisible to most people.
- **How to start.** Install on two devices, share a folder, and watch it stay in sync directly — pair it with Tailscale (#8) so the devices can always find each other.
- **Who it's for.** Anyone moving large or sensitive files between their own machines without trusting a cloud provider.

---

## The meta-skill: building your own stack

The twenty products above are *instances*; the durable skill is the **habit of hunting for leverage**. A few principles to keep after specific tools fade:

```
   THE LEVERAGE LOOP
   notice recurring friction ──► search for a category-killer tool
        ▲                                      │
        │                                      ▼
   delete the friction permanently ◄── adopt at the boundary, then standardize
```

- **Audit your friction quarterly.** Once a quarter, list the three things that most slowed you down. Each is a tool-shaped hole.
- **Prefer open, local, and exportable** when the data is sensitive or you want longevity — a recurring theme here (Ollama, Obsidian, Syncthing, Zotero, DuckDB). It protects you from both lock-in and compliance landmines.
- **Standardize what works.** A tool you adopt and then forget to use is wasted. Bake winners into your defaults, your dotfiles, and your team's setup docs.
- **Watch the category, not the brand.** Every entry here names alternatives on purpose. When a product is acquired and enshittified, you already know the niche to re-shop.

The compounding is the point: each removed friction frees attention for the deep work the rest of this repository is about — and the people who out-build you have simply been running this loop longer.

---

## Sources & further study

These are starting points; verify current details before depending on any specific product, as this space changes quickly.

- **Astral (uv, Ruff)** — official docs and the Astral blog on Python tooling performance.
- **Ollama** — `ollama.com` model library and docs; see also the local-inference threads in [01-autonomy-ml-ai.md](../autonomy/01-ml-ai.md).
- **vLLM** — the project docs and the *PagedAttention* paper for the KV-cache mechanism.
- **Modal / Runpod / Replicate** — serverless-GPU provider docs; compare pricing and cold-start behavior.
- **DuckDB** — official docs and the "friendlier SQL" guides; benchmarks vs. pandas/Postgres for analytical queries.
- **Rerun & Foxglove** — both projects' docs and example galleries; connect to [12-slam-and-mapping.md](../autonomy/12-slam-and-mapping.md) and [22-visual-inertial-odometry.md](../autonomy/22-visual-inertial-odometry.md).
- **Tailscale / Headscale** — WireGuard and Tailscale docs on mesh networking and NAT traversal.
- **Zed, Aider, Caddy, Cloudflare** — each project's documentation; for Aider, review its model-configuration guide to wire in a local Ollama model.
- **Anki** — the manual, plus the spaced-repetition literature (Ebbinghaus forgetting curve, SM-2 family of algorithms); the learning method in [01-mastery-curriculum.md](../01-mastery-curriculum.md).
- **NotebookLM, Obsidian, Excalidraw, Zotero** — official docs; for grounded/RAG concepts see [01-autonomy-ml-ai.md](../autonomy/01-ml-ai.md).
- **Raycast, ElevenLabs, Syncthing** — official docs; review ElevenLabs' and your jurisdiction's guidance on voice-cloning consent ([20-ethics-export-control.md](../career/20-ethics-export-control.md)).

> **Cross-references in this repo:** [01-mastery-curriculum.md](../01-mastery-curriculum.md) (the learning system these tools serve) · [13-companies-skills-to-beat-them.md](../companies/13-skills-to-beat-them.md) (what to be good at) · [16-productivity-deep-work.md](../career/16-productivity-deep-work.md) (protecting the flow these tools enable) · [20-ethics-export-control.md](../career/20-ethics-export-control.md) (the compliance guardrails on local vs. cloud).
