# How GPS & Your Phone Know Where You Are

> **Why this exists.** A blue dot appears on your screen and quietly knows where
> you are to within a few meters, anywhere on Earth, for free. This is one of the
> most remarkable engineering achievements in history — it requires atomic clocks
> in orbit, Einstein's relativity, and a chain of timing tricks most people never
> glimpse. But location is also one of the most sensitive things about you, it can
> be jammed or faked, and understanding *how* it works tells you when to trust the
> dot and when not to. Position is the silent input behind navigation, ride-share,
> delivery, fitness tracking, dating apps, and a growing share of warfare.
>
> **What understanding it gives you.** A clear mental model of trilateration and
> timing, an appreciation for why your phone finds you indoors where satellites
> can't reach, and a grounded sense of GPS's accuracy limits and vulnerabilities.

This is the friendly version of the adversarial deep-dive in
[../autonomy/26-gnss-jamming-spoofing.md](../autonomy/26-gnss-jamming-spoofing.md).
It leans on radio fundamentals from
[../engineering/67-rf-and-comms-systems.md](../engineering/67-rf-and-comms-systems.md)
and the noise/error thinking in
[126-statistics-for-everyday-decisions.md](126-statistics-for-everyday-decisions.md).

---

## 1. The Core Idea: Position From Distances

GPS finds you by measuring your **distance to several satellites whose positions
are known**, then solving for the one point consistent with all of them. This is
**trilateration** (not triangulation — it uses distances, not angles).

Build the intuition in stages:

- **One distance:** you know you're somewhere on a sphere around satellite A.
- **Two distances:** the intersection of two spheres is a circle.
- **Three distances:** three spheres intersect at (essentially) **two points** —
  one on Earth, one absurdly in space, so you pick the sensible one.
- **A fourth distance:** needed to solve for **time** (the key twist in §3).

```
   sat A ─── r_A ──╮
                    ╲
   sat B ─── r_B ────●  ← the single point consistent with all distances = YOU
                    ╱
   sat C ─── r_C ──╯
```

So the whole problem reduces to: **how do you measure the distance to a satellite
20,000 km away that you can't see or touch?** The answer is timing.

---

## 2. Distance From Time-of-Flight

GPS satellites broadcast radio signals that travel at the speed of light,
$c \approx 3 \times 10^8$ m/s. If you know *when* a signal left the satellite and
*when* it arrived at you, the distance is simply:

$$\text{distance} = c \times (\text{travel time})$$

Each satellite continuously transmits a message containing **its precise position
and the exact time the signal was sent.** Your receiver notes the arrival time,
subtracts, and multiplies by $c$.

The brutal catch: light is *fast*. The signal takes only ~0.067 seconds to reach
you. An error of just **one microsecond** (a millionth of a second) in timing
becomes a **300-meter** position error. GPS therefore lives or dies on
ludicrously precise time.

---

## 3. The Clock Problem — and the Clever Fix

Each satellite carries an **atomic clock** accurate to billionths of a second.
Your phone does *not* — a cheap quartz clock would be wildly off. So your
receiver's clock has an unknown error.

That unknown is exactly why you need a **fourth satellite.** You have four
unknowns: your position $(x, y, z)$ **plus** your clock error $t$. Four satellites
give four distance equations — just enough to solve for all four. The receiver
finds the single clock correction that makes all the distance measurements
*consistent*, which simultaneously synchronizes your cheap clock to atomic time
and pins your location.

```
   Unknowns:   x, y, z, clock_error      (4 unknowns)
   Equations:  one per satellite distance
   → need at least 4 satellites for a 3-D fix
```

This is the elegant heart of GPS: **a fourth satellite turns your worthless phone
clock into an effectively atomic one.**

---

## 4. Relativity Is Not Optional

GPS is one of the few places everyday life *depends* on Einstein. The satellite
clocks run at a different rate than clocks on the ground for two relativistic
reasons that push in opposite directions:

| Effect | Cause | Direction |
|---|---|---|
| **Special relativity** | Satellites move fast (~14,000 km/h) | Their clocks run *slower* |
| **General relativity** | Weaker gravity at high altitude | Their clocks run *faster* |

The gravity effect dominates; the net is that satellite clocks tick about
**38 microseconds per day** faster than ground clocks. Left uncorrected, that's a
positioning drift of roughly **10 km per day** — GPS would be useless within
hours. Engineers literally pre-adjust the satellite clock rates to compensate.
Your blue dot is daily proof that relativity is real.

---

## 5. Why Your Phone Is Faster and Works Indoors

Raw GPS has two weaknesses: a cold start can take minutes to find satellites, and
the faint signals barely penetrate buildings. Phones solve this by **fusing
multiple positioning systems**, not relying on satellites alone.

### 5.1 Assisted GPS (A-GPS)

Your phone downloads satellite orbit data and rough location *over the cellular
network* instead of waiting to decode it slowly from the weak satellite signal.
This shrinks the time-to-first-fix from minutes to seconds.

### 5.2 Wi-Fi positioning

Companies have mapped the locations of hundreds of millions of Wi-Fi routers.
Your phone sees the names (and signal strengths) of nearby networks, looks them up
in a giant database, and infers position — *without connecting* to any of them.
This works brilliantly **indoors and in dense cities**, exactly where GPS struggles.

### 5.3 Cell-tower positioning

By measuring which towers it can reach and how strongly, the phone triangulates a
coarse position — less precise (hundreds of meters) but available almost anywhere
with signal.

### 5.4 Inertial sensors

Accelerometers, gyroscopes, and the magnetometer (compass) let the phone *dead
reckon* — estimate motion from its own movement — through tunnels and gaps where
all signals drop, until a real fix returns.

```
   PHONE LOCATION = sensor fusion of:
   ┌──────────┬──────────┬───────────┬────────────┐
   │  GPS/GNSS│  Wi-Fi   │ cell towers│  inertial  │
   │ (open sky)│(indoors) │(anywhere)  │(gaps/tunnels)│
   └──────────┴──────────┴───────────┴────────────┘
   blended into one best estimate = the blue dot (+ accuracy circle)
```

The shaded **accuracy circle** around your dot is the phone's honest admission of
uncertainty — small with good GPS, large when it's leaning on cell towers.

---

## 6. It's Not Just GPS — It's GNSS

"GPS" is the American system, but your phone uses several **global navigation
satellite systems (GNSS)** at once:

| System | Operator |
|---|---|
| **GPS** | United States |
| **GLONASS** | Russia |
| **Galileo** | European Union |
| **BeiDou** | China |

Listening to all of them means **more satellites in view**, which improves
accuracy and reliability — especially in cities where buildings block half the sky.

---

## 7. Accuracy, Errors, and Limits

Consumer GPS is typically accurate to about **3–5 meters** in the open, but many
things degrade it:

- **Atmospheric delay:** the ionosphere and troposphere slow the signal slightly
  and unpredictably.
- **Multipath:** in cities, signals bounce off buildings before reaching you,
  arriving "late" and faking a longer distance — the reason your dot jumps around
  among skyscrapers.
- **Satellite geometry:** satellites clustered together give a weaker fix than
  ones spread across the sky.
- **Obstruction:** trees, walls, and canyons block or weaken the faint signals.

For higher precision, systems like **differential GPS** and **RTK** use a fixed
ground station with a known location to measure and cancel these shared errors,
reaching **centimeter** accuracy — the technology behind precision agriculture and
surveying.

---

## 8. Jamming and Spoofing — Trust the Dot Carefully

Because GPS signals arrive from 20,000 km away, they are astonishingly **weak** —
roughly comparable to seeing a dim bulb from a continent away. That weakness makes
them easy to disrupt:

- **Jamming:** flooding the frequency with noise so the receiver hears nothing.
  Cheap jammers can deny GPS over a wide area; this is now common in conflict zones
  and disrupts civilian aviation nearby.
- **Spoofing:** broadcasting *counterfeit* GPS signals that mimic real satellites,
  tricking a receiver into computing a **false position or time.** This is more
  dangerous than jamming because the victim doesn't know they've been fooled.

Defenses include cross-checking against inertial sensors, multiple GNSS
constellations, and consistency tests — the subject of
[../autonomy/26-gnss-jamming-spoofing.md](../autonomy/26-gnss-jamming-spoofing.md).
The everyday lesson: the blue dot is a *very good estimate*, not ground truth, and
in adversarial settings it can be deliberately wrong.

> Worth remembering: GPS also distributes ultra-precise **time**, not just
> position. Power grids, financial trading, and cell networks synchronize to it —
> so GPS disruption is a timing problem, not only a navigation one.

---

## Sources & further study

- *Understanding GPS/GNSS: Principles and Applications* (Kaplan & Hegarty) — the standard reference.
- Greg Milner, *Pinpoint* — the human and historical story of GPS.
- National Geodetic Survey & GPS.gov — accessible official explainers.
- *The Theory of Relativity* (any good intro) — for the clock corrections.
- Bartlett, *Spoofing and Jamming of GNSS* — accessible security overview.

> Framing note: The blue dot feels like magic, but it's a precise chain of physics —
> distances from timing, timing from atomic clocks, clocks corrected for relativity,
> and gaps filled by Wi-Fi, cell, and motion sensors. Understanding the chain
> turns magic into judgment: you know when to trust it, and when the map is lying.
