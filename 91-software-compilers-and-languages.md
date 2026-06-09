# Compilers & Language Implementation — How Code Becomes Execution

> **Why this exists.** Every line of control law, every perception kernel, every telemetry parser you write is fiction until a compiler turns it into the specific bytes a processor will execute. Most engineers treat that translation as a black box — and then are mystified when their "optimized" C++ runs slower than expected, when a Rust iterator compiles to a tight loop, or when a single missing keyword changes the generated assembly tenfold. The compiler is not magic; it is a pipeline of well-understood transformations, and understanding that pipeline is the difference between *hoping* your code is fast and *knowing* why it is or isn't. For autonomy and defense software, where you fight for microseconds in a control loop and need to reason about exactly what the hardware does, compiler literacy is performance literacy. This module opens the black box.

> **What mastering it makes you.** The engineer who reads the assembly the compiler emitted, recognizes why the optimizer did or didn't vectorize the loop, and writes source that the compiler can turn into the machine code you actually wanted. The person who can build a small DSL for mission scripting, understand why one language is fast and another slow, and never again be at the mercy of a toolchain they don't comprehend.

Compilers are where the abstractions of every language in this curriculum meet the silicon of [65-engineering-embedded-firmware.md](65-engineering-embedded-firmware.md). The performance gains you chase in [92-software-performance-engineering.md](92-software-performance-engineering.md) are almost all *compiler* gains; the safety guarantees of [90-software-systems-programming-rust.md](90-software-systems-programming-rust.md) are *enforced* by a compiler's static analysis; the real-time determinism of [04-foundations-modern-cpp-realtime.md](04-foundations-modern-cpp-realtime.md) depends on knowing what code the compiler generates. The first-principles habit of [01_first_principles_systems_engineering.md](01_first_principles_systems_engineering.md) — refusing to treat any layer as unopenable — is exactly the mindset this module rewards. It pairs with [91-software-compilers-and-languages.md](91-software-compilers-and-languages.md)'s siblings across the band and with the career framing of [12-career-software-engineering.md](12-career-software-engineering.md).

---

## 1. The pipeline — six stages from text to execution

A compiler is a pipeline that lowers a high-level program through progressively simpler representations until it reaches machine code. The canonical stages:

```
source text
   │  ┌─────────────┐
   ├─►│  1. Lexer   │  → token stream      (front end:
   │  ├─────────────┤                       language-specific)
   ├─►│  2. Parser  │  → abstract syntax tree (AST)
   │  ├─────────────┤
   ├─►│ 3. Semantic │  → typed, checked AST
   │  │   analysis  │
   │  ├─────────────┤
   ├─►│ 4. IR gen   │  → intermediate representation  ──┐ (middle end:
   │  ├─────────────┤                                   │  language- AND
   ├─►│ 5. Optimize │  → optimized IR                   │  target-neutral)
   │  ├─────────────┤                                 ──┘
   └─►│ 6. Codegen  │  → target machine code  (back end: target-specific)
      └─────────────┘
```

The deep architectural idea is the **front end / middle end / back end split**, joined by a shared **intermediate representation (IR)**. The front end knows about *your language*; the back end knows about *the target CPU*; the IR in the middle knows about neither. This is why LLVM can compile C, C++, Rust, Swift, and Julia (many front ends) to x86, ARM, RISC-V, and GPUs (many back ends) — each language writes one front end to IR, each chip gets one back end from IR, and the expensive optimizations are written *once* against the IR. Without this split you would need (languages × targets) compilers; with it you need (languages + targets) pieces.

---

## 2. Lexing — text into tokens

The lexer (scanner) reads the raw character stream and groups it into **tokens** — the atomic words of the language: keywords, identifiers, literals, operators, punctuation. It discards whitespace and comments and reports the position of each token for later error messages.

```
source:   let thrust = 0.85 * mass;
tokens:   LET  IDENT("thrust")  EQ  FLOAT(0.85)  STAR  IDENT("mass")  SEMI
```

Lexing is formally a **regular language** problem, which is why it's implemented with finite automata (or regex engines). Each token type is a regular expression; the lexer is the union of those expressions, compiled to a state machine that consumes input in $O(n)$ — linear in source length.

```rust
// A minimal hand-written lexer fragment (the core loop of real ones).
enum Tok { Let, Ident(String), Float(f64), Star, Eq, Semi }

fn next_token(src: &[u8], i: &mut usize) -> Option<Tok> {
    while *i < src.len() && src[*i].is_ascii_whitespace() { *i += 1; }   // skip ws
    let c = *src.get(*i)?;
    match c {
        b'*' => { *i += 1; Some(Tok::Star) }
        b'=' => { *i += 1; Some(Tok::Eq) }
        b';' => { *i += 1; Some(Tok::Semi) }
        b'0'..=b'9' => { /* scan a float literal */ Some(Tok::Float(/*...*/ 0.0)) }
        b'a'..=b'z' => { /* scan an identifier or keyword */ Some(Tok::Ident(/*...*/ String::new())) }
        _ => None,
    }
}
```

In production you rarely hand-write lexers; tools like `flex`, or in Rust the `logos` crate, generate the state machine from declarations.

---

## 3. Parsing — tokens into structure

The parser imposes **grammatical structure** on the flat token stream, producing an **Abstract Syntax Tree (AST)** that captures the program's hierarchy and operator precedence. This is fundamentally harder than lexing because programming languages are **context-free**, not regular — you need a stack (recursion) to match nested parentheses and blocks, which a finite automaton cannot do.

For `2 + 3 * 4`, the parser must know `*` binds tighter than `+` and build the tree that means $2 + (3 \times 4)$, not $(2+3) \times 4$:

```
        (+)
       /   \
     2     (*)
          /   \
         3     4
```

The two dominant strategies:

- **Recursive descent** (top-down) — one function per grammar rule, mutually recursive. Readable, hand-writable, and what most production compilers (including GCC, Clang, and rustc) actually use. Operator precedence is handled with a "Pratt parser" / precedence climbing.
- **Bottom-up (LR/LALR)** — table-driven, generated by tools like `yacc`/`bison`. Handles more grammars automatically but produces opaque error messages.

```rust
// Recursive descent for expressions with precedence (sketch).
fn parse_expr(p: &mut Parser, min_bp: u8) -> Expr {
    let mut lhs = parse_atom(p);                 // a number or (expr)
    while let Some((l_bp, r_bp)) = infix_binding_power(p.peek()) {
        if l_bp < min_bp { break; }              // precedence climbing
        let op = p.next();
        let rhs = parse_expr(p, r_bp);           // recurse for the right side
        lhs = Expr::Binary(op, Box::new(lhs), Box::new(rhs));
    }
    lhs
}
```

The AST is the boundary object: everything after the parser operates on trees, never on text again.

---

## 4. Semantic analysis — meaning and types

A syntactically valid program can still be nonsense: `"hello" * 3.0`, calling an undeclared function, using a moved value (the Rust borrow check of [90-software-systems-programming-rust.md](90-software-systems-programming-rust.md)). **Semantic analysis** walks the AST and checks meaning:

- **Name resolution / scoping** — bind each identifier to its declaration; reject undeclared names.
- **Type checking** — verify operations are applied to compatible types; this is where most of a language's safety guarantees are enforced.
- **Type inference** — deduce types not written explicitly (Hindley–Milner in ML/Haskell, local inference in Rust/Swift/C++ `auto`).
- **Borrow / lifetime checking** — Rust's signature analysis, proving the ownership rules.

Type checking is, formally, a system of **typing rules**. A rule like "if $e_1 : \text{int}$ and $e_2 : \text{int}$ then $e_1 + e_2 : \text{int}$" is applied bottom-up over the AST. The strength of a type system is precisely the strength of the theorems the compiler proves about your program before it ever runs — which is why a strongly-typed language catches at compile time what a dynamic language discovers in production. This stage is also where a compiler builds the **symbol table** and annotates the tree with resolved types, feeding everything downstream.

---

## 5. Intermediate representation — the workhorse

The compiler now lowers the typed AST into an **IR**: a simpler, more uniform form designed for analysis and transformation rather than human reading. The dominant design is **Static Single Assignment (SSA)** form, where every variable is assigned exactly once. SSA makes dataflow explicit — each use points to exactly one definition — which is what makes optimizations both correct and fast to compute.

LLVM IR is the most important IR in the industry. It is a typed, RISC-like, target-independent assembly:

```llvm
; LLVM IR for: int add_scaled(int a, int b) { return a + b * 2; }
define i32 @add_scaled(i32 %a, i32 %b) {
entry:
  %0 = mul i32 %b, 2          ; b * 2
  %1 = add i32 %a, %0         ; a + (b*2)
  ret i32 %1                  ; SSA: %0 and %1 each defined once
}
```

Branches and loops, where a variable could have come from two paths, are reconciled with **φ (phi) nodes** that say "this value is the one from whichever predecessor block we came from." SSA + phi is the representation nearly every modern optimizer reasons over. The IR is also where the front-end/back-end seam lives: rustc and clang both *emit* LLVM IR, and from here the path to x86 or ARM is shared.

---

## 6. Optimization — making it fast (and correct)

The optimizer rewrites IR into equivalent-but-better IR. Each transformation is a **pass**; production compilers run dozens, ordered carefully because passes enable each other. The classics:

| Pass | What it does |
|---|---|
| **Constant folding** | Evaluate compile-time-known expressions: `2 * 60 * 60` → `7200`. |
| **Dead code elimination** | Remove computations whose results are never used. |
| **Common subexpression elimination** | Compute `a*b` once if it appears twice. |
| **Inlining** | Replace a call with the callee's body — *the* enabling optimization; it exposes everything else. |
| **Loop-invariant code motion** | Hoist work that doesn't change out of the loop. |
| **Strength reduction** | Replace expensive ops with cheap ones (`x*2` → `x<<1`). |
| **Vectorization** | Fuse scalar loop iterations into SIMD instructions (see [92-software-performance-engineering.md](92-software-performance-engineering.md)). |
| **Register allocation** | Map the unlimited SSA values onto the CPU's finite physical registers (a graph-coloring problem). |

The **iron law** of optimization: a transformation is legal only if it preserves observable behavior. This is why `-O2` is safe but why `volatile` (Section on embedded in [65-engineering-embedded-firmware.md](65-engineering-embedded-firmware.md)) and memory-ordering matter — they tell the optimizer which behaviors are observable and must not be reordered. It's also the root of undefined behavior's power: when the standard says a program "must not" do X, the optimizer is *allowed to assume* X never happens, and optimizes accordingly — which is why a signed-overflow UB bug can make code vanish.

Optimization is why understanding the compiler is performance work. The same source, with `-O0` vs `-O3`, can differ by 10× because inlining + vectorization + LICM together transform an idiomatic loop into a handful of SIMD instructions. You write *for* the optimizer.

---

## 7. Code generation & the AOT/JIT spectrum

The back end lowers optimized IR to a specific **instruction set architecture (ISA)** — x86-64, ARM (AArch64), RISC-V — performing instruction selection (IR ops → real instructions), instruction scheduling (ordering to hide latency in the CPU pipeline), and register allocation. The output is an object file the linker stitches into an executable.

There are two fundamental execution strategies, and the tradeoff defines a language's character:

```
                Compile time        Run time
AOT (C, C++,    ┌──────────────┐    ┌──────────────┐
Rust, Go):      │ full optimize│ →  │ run native   │   fast start, max optimize,
                │ → native exe │    │ machine code │   no runtime info
                └──────────────┘    └──────────────┘

JIT (Java/JVM,  ┌──────────────┐    ┌──────────────────────────┐
C#, V8/JS,      │ → bytecode   │ →  │ interpret; profile HOT   │   adapts to actual
PyPy):          │              │    │ paths; compile them to   │   data, slower start,
                └──────────────┘    │ native at run time       │   runtime overhead
                                    └──────────────────────────┘
```

- **Ahead-of-Time (AOT)** compiles fully to native code before running. Predictable, no warm-up, no runtime — the only acceptable model for hard-real-time and embedded ([04-foundations-modern-cpp-realtime.md](04-foundations-modern-cpp-realtime.md)).
- **Just-in-Time (JIT)** ships bytecode, interprets it, *profiles which code is hot*, and compiles those paths to native at run time — using information unavailable AOT (actual branch frequencies, real types in a dynamic language). This is how the JVM and V8 make Java and JavaScript fast, but it costs warm-up time and unpredictable pauses (disqualifying for a control loop). The interpreter–compiler hybrid is why "interpreted" languages aren't necessarily slow.

LLVM underpins much of both worlds: AOT for Clang/Rust/Swift, and JIT (via ORC/MCJIT) for engines and the GPU compilers that turn your CUDA kernels into SASS.

---

## 8. Why this matters — and building your own small language

Compiler literacy pays off constantly, even if you never write a compiler:

- **Performance reasoning** — when you understand inlining and vectorization you write code the optimizer can actually accelerate, and you read the emitted assembly (via `godbolt.org`, the Compiler Explorer) to confirm it (the core method of [92-software-performance-engineering.md](92-software-performance-engineering.md)).
- **Debugging** — understanding SSA and optimization passes explains "impossible" bugs where the optimizer exploited undefined behavior.
- **Language choice** — AOT vs JIT, static vs dynamic types, monomorphization vs dynamic dispatch are all compiler properties that determine fitness for a task.
- **Domain-specific languages** — you will, eventually, want a small language: a mission-scripting DSL, a config language, a sensor-calibration format. The lexer→parser→evaluator pipeline above is exactly how you build one, and a tree-walking interpreter is a weekend project once the pipeline is in your bones.

```python
# A complete tree-walking interpreter core — the whole compiler pipeline in miniature.
def evaluate(node, env):
    match node:
        case ("num", v):           return v
        case ("var", name):        return env[name]
        case ("add", a, b):        return evaluate(a, env) + evaluate(b, env)
        case ("mul", a, b):        return evaluate(a, env) * evaluate(b, env)
        case ("let", name, val, body):
            env2 = {**env, name: evaluate(val, env)}
            return evaluate(body, env2)
# lex(text) -> tokens ; parse(tokens) -> AST ; evaluate(AST, {}) -> result.
# Every real compiler is this, scaled up and with codegen instead of eval.
```

The grand lesson is the one from [01_first_principles_systems_engineering.md](01_first_principles_systems_engineering.md): there is no magic, only layers. The compiler is a layer you can open, and once opened it stops being a source of mystery and becomes a tool you wield — the layer that turns the languages of this entire curriculum into the execution that makes a vehicle fly.

---

## Sources & further study

- **Robert Nystrom, *Crafting Interpreters*** — free online, the single best on-ramp: build a complete language twice (tree-walk, then bytecode VM). Start here.
- **Aho, Lam, Sethi & Ullman, *Compilers: Principles, Techniques, and Tools* ("the Dragon Book")** — the rigorous classic; reference for the theory.
- **Andrew Appel, *Modern Compiler Implementation in ML/C/Java*** — a tighter, more practical path through a real compiler.
- **The LLVM documentation and *LLVM Language Reference*** — the IR and pass infrastructure that runs the industry; pair with the LLVM "Kaleidoscope" tutorial.
- **Matt Godbolt's Compiler Explorer (godbolt.org)** — not a book but essential: watch source become assembly interactively.
- **Engineering a Compiler, Cooper & Torczon** — excellent on optimization and SSA.
- **Niklaus Wirth, *Compiler Construction*** — short, elegant, recursive-descent purism.

> Framing note: The compiler is the most consequential program you use every day and never think about. Treat it as a black box and you are forever surprised by your own code's performance and behavior; open it and you gain a superpower — the ability to write source *for the machine you actually have*, to read what was generated, and to build new languages when the existing ones don't fit. For an engineer chasing microseconds in an autonomy loop, that is not academic. It is the difference between guessing and knowing.
