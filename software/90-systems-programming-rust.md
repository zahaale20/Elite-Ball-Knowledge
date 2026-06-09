# Systems Programming in Rust — Safety Without a Garbage Collector

> **Why this exists.** The software at the heart of an autonomous vehicle lives in a brutal regime: it must be fast enough to close a control loop in microseconds, deterministic enough that no garbage collector can pause it mid-maneuver, and correct enough that a memory bug does not become a crashed aircraft. For forty years the only language that delivered the speed and determinism was C or C++ — and the price was a permanent vulnerability to use-after-free, buffer overflows, and data races, the class of bug behind the majority of critical security vulnerabilities ever shipped. Rust is the first mainstream language to break that tradeoff: it gives you C-level performance and control with a compiler that *statically proves* whole categories of those bugs cannot occur. If you build software that flies, drives, or shoots, the ability to get memory safety without paying a GC tax is not a luxury — it is the new baseline. This module makes you fluent in the model that delivers it.

> **What mastering it makes you.** The engineer who can write a lock-free telemetry pipeline or an embedded flight-controller driver that the compiler *guarantees* is free of data races and dangling pointers — and who can explain, precisely, why C++ cannot make that promise. As Rust enters the Linux kernel, Android, and defense codebases, that fluency is becoming a hiring differentiator.

Rust is the natural successor to the real-time C++ discipline of [04-foundations-modern-cpp-realtime.md](../foundations/04-modern-cpp-realtime.md): it enforces, at compile time, the manual rules that document recommends you follow by hand. The safety-assurance arguments of [09-foundations-safety-assurance.md](../foundations/09-safety-assurance.md) are exactly what Rust's guarantees let you make with evidence, and the systems-thinking of [01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md) is what tells you *when* the borrow checker's friction is worth it. This module anchors the systems-language portion of the "Software, Compute & Infrastructure" band and pairs with [91-software-compilers-and-languages.md](91-compilers-and-languages.md) (how Rust's safety is implemented in the compiler), [92-software-performance-engineering.md](92-performance-engineering.md) (Rust's zero-cost abstractions), [65-engineering-embedded-firmware.md](../engineering/65-embedded-firmware.md) (embedded Rust on bare metal), and [12-career-software-engineering.md](../career/12-software-engineering.md) (where Rust skills land you).

---

## 1. The problem Rust solves: the safety–control tradeoff

Programming languages historically forced a choice along one axis:

```
        manual memory mgmt                      automatic (GC)
   ◄───────────────────────────────────────────────────────────►
   C, C++                                          Java, Go, Python
   fast, deterministic,                            safe, but pauses,
   UNSAFE (UB, races, UAF)                          overhead, less control
```

Manual languages (C/C++) give you total control over memory and timing — and total responsibility, which humans discharge imperfectly. Microsoft and Google have both reported that ~70% of their serious security vulnerabilities are memory-safety bugs. Garbage-collected languages (Java, Go) remove that class of bug but introduce a runtime that pauses the program at unpredictable moments and stands between you and the hardware — unacceptable in a hard-real-time control loop.

Rust's thesis is that this tradeoff is false. The information needed to manage memory safely — *who owns this data and how long does it live* — is available at compile time. So Rust pushes the bookkeeping into the **type system and the compiler**. You get manual-language performance and determinism, and the compiler refuses to build code that would commit the unsafe acts. No GC, no runtime pauses, no use-after-free. The cost is paid once, by the programmer, at compile time, in the form of the borrow checker's discipline.

---

## 2. Ownership — the core idea

Every value in Rust has exactly one **owner** — a single variable responsible for it. When the owner goes out of scope, the value is deterministically dropped (its destructor runs, its memory freed). There is no GC because there does not need to be: the compiler knows, statically, exactly where every value dies.

```rust
fn main() {
    let s = String::from("telemetry");  // s owns the heap allocation
    let t = s;                           // ownership MOVES to t; s is now invalid
    // println!("{}", s);                // COMPILE ERROR: value borrowed after move
    println!("{}", t);                   // fine: t is the owner
}                                        // t dropped here, heap freed — exactly once
```

This *move* semantics is the foundation. Assigning `s` to `t` does not copy the heap buffer (that would be expensive) and does not create two owners (that would risk a double-free). It transfers ownership and invalidates the source. The compiler tracks this; using `s` after the move is a compile error, not a runtime crash. The single-owner rule makes double-free *structurally impossible*.

For values that are cheap to duplicate (integers, bools) the `Copy` trait makes assignment copy instead of move. For deliberate deep copies you call `.clone()` explicitly — Rust makes the expensive operation *visible* rather than hidden, a recurring theme.

---

## 3. Borrowing & the rules that prevent races

You cannot move ownership every time a function needs to look at data — that would be unusable. Instead you **borrow**: take a reference. Borrowing is governed by two rules the **borrow checker** enforces at compile time, and these two rules are the whole magic:

> **At any given time, you may have *either* one mutable reference (`&mut T`) *or* any number of immutable references (`&T`) — never both.**
> **Every reference must always be valid (never outlive the data it points to).**

```rust
fn main() {
    let mut buf = vec![1, 2, 3];

    let a = &buf;          // immutable borrow
    let b = &buf;          // another immutable borrow — fine, both read-only
    println!("{:?} {:?}", a, b);

    let m = &mut buf;      // mutable borrow — OK now that a, b are no longer used
    m.push(4);
    // let c = &buf;       // ERROR if it overlapped m: can't borrow while &mut exists
}
```

This single constraint — "shared XOR mutable" — is what eliminates **data races at compile time**. A data race requires two threads accessing the same memory, at least one writing, without synchronization. Rust's rule makes the "shared + mutating" precondition impossible to express in safe code. The compiler that prevents your iterator from being invalidated when you push to a vector is the *same* compiler that prevents two threads from racing on a counter. Memory safety and thread safety fall out of one elegant rule.

This is why the famous "fearless concurrency" claim holds: in most GC languages, data races are runtime bugs you find with luck and a debugger. In Rust they do not compile.

---

## 4. Lifetimes — making "valid reference" checkable

The borrow checker proves references stay valid using **lifetimes**: compile-time annotations describing how long a reference is good for. Most of the time the compiler infers them ("lifetime elision") and you write nothing. They surface when a function returns a reference and the compiler needs to know which input it borrows from.

```rust
// "The returned reference lives as long as BOTH inputs ('a is the shorter)."
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

Lifetimes are *not* a runtime cost — they are erased after type-checking. They are purely a proof obligation: a way for you to tell the compiler, and the compiler to verify, that you are not returning a reference to data that is about to be freed. The classic C bug of returning a pointer to a stack local is, in Rust, a compile error:

```rust
fn dangling() -> &String {        // ERROR: missing lifetime / returns ref to local
    let s = String::from("oops");
    &s                            // s dies at end of function; ref would dangle
}
```

The mental model: lifetimes let the compiler do the dataflow analysis that a careful C programmer does in their head — except the compiler never gets tired and never misses a case.

---

## 5. Concurrency — `Send`, `Sync`, and shared state done right

Rust extends ownership across threads with two marker traits the compiler checks automatically:

- **`Send`** — a type is safe to *move* to another thread.
- **`Sync`** — a type is safe to *share by reference* (`&T`) across threads.

The compiler refuses to send a non-`Send` type across a thread boundary. This is how you get a *compile error* instead of a heisenbug. To actually share mutable state, you compose ownership primitives whose types encode the safety requirement:

```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    // Arc: atomically reference-counted shared ownership.
    // Mutex: interior mutability guarded by a lock.
    let counter = Arc::new(Mutex::new(0u64));
    let mut handles = vec![];

    for _ in 0..8 {
        let c = Arc::clone(&counter);
        handles.push(thread::spawn(move || {
            let mut n = c.lock().unwrap();   // lock() returns a guard; data is
            *n += 1;                          // only reachable through the guard
        }));                                  // guard dropped here → lock released
    }
    for h in handles { h.join().unwrap(); }
    println!("{}", *counter.lock().unwrap()); // 8
}
```

The brilliance: the data inside a `Mutex` is *only reachable through the lock guard*. You cannot forget to lock, because the type system will not give you the data otherwise. Compare to C++, where a `std::mutex` and the data it protects are two unrelated objects and nothing stops you from touching the data without the lock. Rust makes the correct usage the *only* expressible usage. For lock-free work, the `crossbeam` and `tokio` ecosystems build on these same guarantees; async/await gives you millions of cheap concurrent tasks without OS threads.

---

## 6. Zero-cost abstractions & `unsafe`

Rust's high-level features compile down to the same machine code you would write by hand — **zero-cost abstractions**, the principle inherited from C++ ([04-foundations-modern-cpp-realtime.md](../foundations/04-modern-cpp-realtime.md)). An iterator chain is not slower than a hand-written loop; it monomorphizes and optimizes to identical assembly:

```rust
// This functional pipeline...
let sum: u64 = data.iter().filter(|&&x| x > 0).map(|&x| x as u64).sum();
// ...compiles to a tight loop with no allocations, no vtable, no overhead.
```

Generics are monomorphized (a fresh specialized copy per concrete type, like C++ templates) so there is no dynamic dispatch unless you ask for it with `dyn Trait`. Traits give you polymorphism; the optimizer inlines through them.

When you genuinely need to do something the borrow checker cannot verify — dereference a raw pointer, call into C, touch a memory-mapped register — you write an **`unsafe` block**. `unsafe` does *not* turn off the rest of Rust's checks; it narrowly grants a few extra abilities and tells the human: *you* are now responsible for upholding the invariants the compiler normally proves. The discipline is to wrap `unsafe` in a small, audited, safe API.

```rust
// Reading a memory-mapped peripheral register on bare metal: inherently unsafe,
// because the compiler cannot know a raw address is valid. Wrap it safely.
fn read_status(reg: *const u32) -> u32 {
    unsafe { core::ptr::read_volatile(reg) }   // volatile: not optimized away
}
```

The cultural rule: minimize `unsafe`, isolate it, document the invariant each block relies on, and expose a safe interface so the rest of the codebase stays provably sound. A typical application has almost none; a driver or allocator has a little, carefully fenced.

---

## 7. Embedded Rust — bare metal without the runtime

Rust runs with **no operating system and no heap** via `#![no_std]`, making it a direct C replacement for microcontrollers — exactly the STM32-class targets of [65-engineering-embedded-firmware.md](../engineering/65-embedded-firmware.md). The embedded ecosystem encodes hardware safety into types:

- **Peripheral Access Crates (PACs)** generated from the chip's register description, so register fields are typed, not magic bit-masks.
- **Hardware Abstraction Layers (HALs)** built on the `embedded-hal` traits, so a driver written against "any SPI bus" is portable across chips.
- **Ownership of peripherals**: a `Peripherals::take()` returns a singleton you can only acquire once — the type system prevents two parts of your firmware from configuring the same UART simultaneously, a classic embedded bug.

```rust
#![no_std]
#![no_main]
use cortex_m_rt::entry;
use stm32f4xx_hal::{pac, prelude::*};

#[entry]
fn main() -> ! {
    let dp = pac::Peripherals::take().unwrap();      // owned once, ever
    let gpioa = dp.GPIOA.split();
    let mut led = gpioa.pa5.into_push_pull_output();  // pin's type now encodes its mode
    let clocks = dp.RCC.constrain().cfgr.sysclk(168.MHz()).freeze();
    let mut delay = dp.TIM2.delay_ms(&clocks);
    loop {
        led.toggle();
        delay.delay_ms(500_u32);
    }
}
```

Crucially, embedded Rust keeps the borrow checker. The "shared XOR mutable" rule that prevents data races between threads *also* governs the trickiest embedded hazard: shared state between your main loop and an interrupt handler. Rust frameworks like RTIC use the type system to prove your ISR and main code cannot corrupt shared data — the kind of bug that costs days in C, eliminated at compile time. There is `no_std` async too (Embassy), bringing cheap concurrency to microcontrollers.

---

## 8. When to choose Rust vs. C++ — an honest decision

Rust is not a religion; it is an engineering tradeoff. Choose deliberately.

| Factor | Favors **Rust** | Favors **C++** |
|---|---|---|
| Memory-safety stakes | High (security-critical, networked, lives at risk) | Lower / fully sandboxed |
| New code vs. existing | Greenfield, or a clean module boundary | Vast existing C++ codebase |
| Ecosystem / libraries | Modern web, CLI, networking, crypto | Mature: ROS, CUDA, vendor SDKs, sim, CAD |
| Team familiarity | Willing to invest in the learning curve | Deep existing C++ expertise |
| Certification path | Emerging (Ferrocene qualifies Rust for ISO 26262/IEC 61508) | Established (MISRA, DO-178C tooling, AUTOSAR) |
| Compile times | Slower (the price of the checks) | Faster incremental builds |
| Concurrency complexity | High — fearless concurrency pays off most | Simple/sequential |

**Reach for Rust** when memory safety is a hard requirement, when you are writing new networked or concurrent systems software, or when a single memory bug is catastrophic — telemetry servers, ground-station backends, security-sensitive parsers, new device drivers. **Stay with C++** when you must integrate deeply with an existing C++/ROS/CUDA ecosystem, when your team's expertise and the certification toolchain are C++-shaped, or when the cost of rewriting working, audited code exceeds the benefit. The pragmatic answer in defense and robotics today is increasingly *both*: a stable C++ core with new safety-critical components written in Rust, talking across a clean FFI boundary. The borrow checker is most valuable exactly where the stakes are highest — which is precisely the autonomy and defense software this curriculum is about. The deeper "how does the compiler actually prove all this" lives in [91-software-compilers-and-languages.md](91-compilers-and-languages.md).

---

## Sources & further study

- **Steve Klabnik & Carol Nichols, *The Rust Programming Language* ("the Book")** — free, official, and the best place to internalize ownership and borrowing.
- **Jon Gjengset, *Rust for Rustaceans*** — the intermediate-to-expert text: lifetimes, `unsafe`, trait objects, and how it really works.
- **Jim Blandy, Jason Orendorff & Leonora Tindall, *Programming Rust*** — a rigorous systems-programmer's tour.
- **The Embedded Rust Book** and **the Discovery / `embedded-hal` docs** — bare-metal Rust from first blink.
- **Aaron Turon, "Fearless Concurrency" (Rust blog)** — the clearest essay on why ownership eliminates data races.
- **The Rustonomicon** — the dark-arts guide to `unsafe` and upholding invariants by hand.
- **Ferrocene documentation** — Rust qualified for safety-critical (ISO 26262 / IEC 61508), relevant to [09-foundations-safety-assurance.md](../foundations/09-safety-assurance.md).

> Framing note: Every memory-safety bug Rust prevents at compile time is a 3 a.m. incident that never happens, a CVE never filed, a crashed vehicle never crashed. The language asks you to pay an honest, visible cost up front — the borrow checker's friction — in exchange for moving an entire class of catastrophic failures from "found in production, sometimes" to "cannot be built." For software that flies and fights, that trade is one of the best deals in engineering, and the engineer who can wield it fluently writes the code other people can finally trust.
