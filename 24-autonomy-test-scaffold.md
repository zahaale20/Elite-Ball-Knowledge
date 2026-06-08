# Test scaffold

> Tests on this program are **risk prevention**, not bug-counting. Every test
> here exists to stop a specific bad thing from reaching a powered airframe: a
> mission that arms without GPS, a transition that stalls, a policy gate that
> lets a command through it should have denied. If you can't name the failure
> mode a test defends against, the test isn't earning its place. This file is
> the practical companion to the foundations in
> [06-foundations-simulation-test-verification.md](06-foundations-simulation-test-verification.md);
> read that for the theory, read this for how it lands in `drone/test/`.

Tests are organized by what they require to run:

| Folder              | Needs                            | What lives here                                                       |
| ------------------- | -------------------------------- | --------------------------------------------------------------------- |
| `unit/`             | `pytest`, project venv only      | Pure-logic tests: auth, waypoint validation, mission math, JPEG framing, telemetry shaping |
| `integration/`      | PX4 SITL (`gz_tiltrotor`)        | End-to-end: onboard service \u2194 SITL \u2194 MAVSDK                          |
| `exploratory/`      | Operator notes                   | Free-form charters (GPS loss mid-mission, transition brownout)        |

## Running unit tests

```bash
source ~/pixhawk/.venv/bin/activate
pip install pytest pytest-asyncio   # if not already installed
pytest drone/test/unit -v
```

Tests that depend on `fastapi`, `mavsdk`, or `opencv-python` skip cleanly
on hosts that don't have those installed (e.g. a macOS dev laptop before
the venv is created), so this suite is safe to run anywhere. Pure-logic
tests (`test_vtol_demo.py` math, `test_jpeg.py`) run without any project
dependencies.

## Running integration tests (Stage 1 acceptance)

```bash
# Terminal 1
cd ~/PX4-Autopilot && make px4_sitl gz_tiltrotor

# Terminal 2
source ~/pixhawk/.venv/bin/activate
python -m drone.onboard.server --conn udp://:14540 &

# Terminal 3
pytest drone/test/integration -v
```

Stage 1 integration tests are deliberately thin -- they only assert that the
onboard service can reach SITL, that `/api/state` reports `connected=true`,
and that the `vtol_demo` mission completes without `ABORT`. Deeper coverage
lands with the Stage 4 airframe params.

## Test philosophy

- **Risk prevention first.** Every test should name a failure mode it's
  defending against (top of file or top of the test).
- **Layered coverage.** Unit covers logic, integration covers wiring,
  acceptance covers operator workflows, exploratory covers what tests can't.
- **User-perspective validation.** Acceptance tests are written from the
  ground-station operator's point of view, not the API's.
- **Boundaries everywhere.** Waypoint validators, transition timeouts,
  airspeed/altitude clamps -- test the edges.

### The pyramid (and why this shape)

```
              ▲  fewer, slower, higher-fidelity
              │        ┌───────────────┐
   exploratory│        │  exploratory  │  human judgment, charters
              │     ┌──┴───────────────┴──┐
   acceptance │     │     acceptance      │  operator workflows (Playwright + SITL)
              │  ┌──┴─────────────────────┴──┐
  integration │  │       integration         │  module ↔ SITL wiring
              │┌─┴───────────────────────────┴─┐
        unit  ││            unit               │  pure logic, exhaustive boundaries
              │└───────────────────────────────┘
              │  more, faster, cheaper
```

The shape is deliberate. Unit tests are cheap and deterministic, so you write
many and run them on every save. Acceptance and exploratory tests are expensive
(they need SITL, a browser, or a human), so you write few and run them at gates.
Inverting this — lots of slow end-to-end tests, few unit tests — gives you a
suite that is slow, flaky, and tells you *that* something broke without telling
you *where*. See [06-foundations-simulation-test-verification.md](06-foundations-simulation-test-verification.md)
for the full verification taxonomy this maps onto.

### What each layer *proves*

| Layer | Proves | Does **not** prove | Example here |
| ----- | ------ | ------------------ | ------------ |
| **Unit** | a pure function is correct at its boundaries | that modules talk to each other | waypoint validator rejects lat > 90 |
| **Integration** | modules + PX4 SITL wire together | the operator can actually fly it | onboard service reaches SITL, `/api/state` `connected=true` |
| **Acceptance** | the operator workflow works end to end | every edge case | login → upload 4-WP mission → watch RTL+land on the map |
| **Exploratory** | things you didn't think to assert | anything repeatable | GPS loss mid-transition, malformed-JSON mission upload |

The mental model: each layer assumes the layer below it already passed. An
acceptance test should never fail for a reason a unit test could have caught —
if it does, you're missing a unit test.

### How to write a test that names its failure mode

A test name and docstring should make the defended risk obvious to someone who
has never seen the code. Per this project's house style, test comments are
**full, clear sentences** stating the risk and the expected behavior.

```python
def test_preflight_refuses_to_arm_without_gps_lock():
    """Failure mode: arming without a GPS fix lets the vehicle launch with no
    position estimate, which on a real airframe means an immediate flyaway.

    This test proves the constitution gate denies an arm command when the
    vehicle reports no GPS lock, and that the denial carries an explainable
    reason rather than silently timing out.
    """
    state = world_state(gps_locked=False, home_set=False)
    verdict = policy_gate(command=Arm(), state=state)
    assert verdict.allowed is False
    # The operator must learn *why* arming was refused, not just that it was.
    assert "gps" in verdict.reason.lower()
```

Contrast a weak test — `test_arm()` with a bare `assert result` — which proves
nothing about *which* risk is covered and silently rots when behavior changes.
Every test in `drone/test/` should be readable as a sentence: *"this defends
against X by asserting Y at boundary Z."*

### Boundary and edge coverage

Most real failures live at the edges, so the validators get tested *at* their
limits, not in their comfortable middle.

| Validator | Inside (pass) | Boundary (must pin) | Outside (must reject) |
| --------- | ------------- | ------------------- | --------------------- |
| Latitude | 0.0 | ±90.0 exactly | ±90.0001, NaN, None |
| Longitude | 0.0 | ±180.0 exactly | ±180.0001 |
| Altitude clamp | mid-range | min and max exactly | below min, above ceiling |
| Transition airspeed | cruise | blend threshold exactly | below stall |
| Waypoint count | 4 | 0 and the max | negative, over max |
| Battery reserve | full | exactly the RTL reserve | one tick below reserve |

Rule of thumb: for every numeric clamp, write the test at `min`, `min-ε`, `max`,
and `max+ε`. The off-by-one and the open/closed-interval bug both hide exactly
there.

### Fault injection

Real flights fail by sensors dropping out, links going quiet, and JSON arriving
malformed. Integration and exploratory tests inject those faults deliberately
rather than waiting to discover them in the field.

| Injected fault | Where | Expected behavior |
| -------------- | ----- | ----------------- |
| GPS lost mid-mission | SITL param / message drop | vehicle holds / RTLs, never continues blind |
| Telemetry link stall | drop the WS consumer | shaper keeps cadence; reconnect is clean |
| Malformed mission JSON | `/api/mission` upload | rejected with a 4xx + reason, never partially applied |
| Battery below reserve | spoofed state | policy gate denies further commands, triggers RTL |
| Brown-out during transition | SITL | logged; vehicle reverts to a safe sub-state |
| Auth token missing/invalid | REST request | command denied at the gate, logged |

Each of these maps to an exploratory charter (below) first, then graduates to a
repeatable integration test once you understand the failure well enough to
assert on it.

### Property-based testing

For pure logic with a large input space, example-based tests miss cases you
didn't imagine. Property tests (Hypothesis) generate inputs and assert
*invariants* that must hold for all of them.

```python
from hypothesis import given, strategies as st

@given(
    lat=st.floats(min_value=-90, max_value=90, allow_nan=False),
    lon=st.floats(min_value=-180, max_value=180, allow_nan=False),
)
def test_valid_coordinates_always_round_trip(lat, lon):
    """Property: any in-range coordinate that the validator accepts must
    survive serialization to a mission frame and back unchanged, so we never
    silently corrupt an operator's waypoint on the wire.
    """
    wp = make_waypoint(lat, lon)
    assert from_json(to_json(wp)) == wp
```

Good invariants to assert here: validators never accept out-of-range values;
telemetry frames always serialize to valid JSON; the policy gate is
**default-deny** for any state it can't evaluate; the decision log's hash chain
verifies for any sequence of appends.

### Continuous integration

Stage 7 wires this suite into GitHub Actions so nothing merges without proof.

| CI job | Runs | Gate |
| ------ | ---- | ---- |
| lint + types | ruff / mypy (drone), eslint / tsc (ground-station) | style + type errors block merge |
| unit | `pytest drone/test/unit`, `vitest` | fast, runs on every push |
| integration | onboard service ↔ SITL (`gz_tiltrotor --headless`) | runs on PR; slower |
| dependency scan | audit Python + npm deps | known CVEs block merge |

The unit layer is the contract for "green means safe to keep working"; the
integration layer is the contract for "safe to consider for a hardware gate."
Acceptance and exploratory runs happen at stage gates, not on every commit,
because they need a browser and a human respectively.

### Exploratory charters

Exploratory testing is structured, not random. Each charter is a one-line
mission with notes committed under `drone/test/exploratory/`.

```
CHARTER: Explore GPS loss during the forward transition
  to discover whether the vehicle holds a safe sub-state
  and whether the operator sees the degraded fix in time.

NOTES:
  - dropped GPS at TRANSITION_TO_FW; vehicle ...
  - operator pill still showed FW for N seconds → file follow-up
  - candidate for a repeatable integration test: yes (assert sub-state revert)
```

A charter that uncovers a reproducible failure becomes an integration test. A
charter that uncovers a *judgment* gap (e.g. "the operator couldn't tell") feeds
back into the UI or telemetry design, not into an assertion.

### Fixtures and test data builders

Tests are only trustworthy if their inputs are obvious. Build world states and
commands with small named helpers so each test reads as a sentence and a reader
sees exactly which boundary is in play.

```python
def world_state(**overrides):
    """Build a default-healthy vehicle state, then override only the fields a
    test cares about, so each test states its precondition explicitly rather
    than hiding it in a large literal.
    """
    base = dict(
        gps_locked=True, home_set=True, battery_frac=0.9,
        airspeed=18.0, mode="HOLD", inside_geofence=True,
    )
    base.update(overrides)
    return State(**base)

# A reader sees instantly that *only* the GPS condition is under test.
denied = policy_gate(Arm(), world_state(gps_locked=False))
```

The rule: a test should override the *one* field whose effect it is proving and
inherit healthy defaults for everything else. Tests that construct a giant state
literal hide which input actually drives the assertion.

### Anti-patterns — what NOT to test (and how not to)

| Anti-pattern | Why it's bad | Do instead |
| ------------ | ------------ | ---------- |
| `time.sleep()` to "wait for SITL" | flaky; lockstep ≠ wall-clock | poll vehicle state/telemetry with a timeout |
| Asserting on log strings | breaks on harmless wording changes | assert on structured verdict/reason fields |
| One test asserting ten things | failure doesn't localize | one risk per test, named |
| Testing MAVSDK / PX4 itself | not your code; slow | test *your* logic and *your* wiring |
| Mocking the policy gate in its own test | proves the mock, not the gate | test the real pure function |
| Snapshot-testing the whole telemetry frame | brittle; fails on every field add | assert the fields the contract guarantees |

The throughline: assert on **behavior and structure**, never on incidental
wording or timing. A test that fails when you rename a log message is noise.

### Mapping tests to roadmap stages

Coverage isn't uniform across the program — it deepens as the stages do
([21-autonomy-vtol-roadmap.md](21-autonomy-vtol-roadmap.md)).

| Stage | Test focus | Layer emphasis |
| ----- | ---------- | -------------- |
| 1 (SITL up) | service reaches SITL; `vtol_demo` completes without `ABORT` | thin integration + unit scaffolding |
| 2 (custom SDF) | VTOL sub-state pill sourced correctly; transition observability | integration |
| 4 (airframe params) | allocation/mixer signs; transition thresholds | unit (pure allocation) + integration |
| 5 (bench) | preflight gate, failsafe logic, calibration checks | unit + exploratory |
| 6 (first flight) | go/no-go checklist encoded; HITL replay assertions | acceptance + integration |
| 7 (CI hardening) | auth, mission-upload origin, full suite in Actions | all layers in CI |
| 8 (mission expansion) | geofence breach → correct failsafe; BVLOS logging | integration + property |

Stage 1's integration tests are deliberately thin (see above) precisely because
the deep allocation behavior they would assert on doesn't exist until Stage 4.
Writing those tests early would mean asserting against the throwaway
`gz_tiltrotor` stand-in.

### A worked example: testing the policy gate

The constitution gate ([23-autonomy-onboard-system.md](23-autonomy-onboard-system.md))
is the highest-value unit-test target in the codebase — it is a pure function
guarding the only path to the vehicle. Cover it like the safety control it is.

```python
import pytest

# Each row is (command, state-override, must_allow, reason_substring) and names
# the exact failure mode the row defends against in a comment.
CASES = [
    # Arming with no GPS would launch with no position estimate → flyaway.
    (Arm(), dict(gps_locked=False), False, "gps"),
    # Arming with no home means RTL has nowhere to return to.
    (Arm(), dict(home_set=False), False, "home"),
    # A transition below stall airspeed drops the wing → loss of the airframe.
    (TransitionFW(), dict(airspeed=2.0), False, "airspeed"),
    # A command that would cross the geofence must never reach the vehicle.
    (Goto(lat=0, lon=999), dict(), False, "geofence"),
    # A fully healthy state must still allow a legal arm, or the gate is useless.
    (Arm(), dict(), True, ""),
]

@pytest.mark.parametrize("command,override,must_allow,reason", CASES)
def test_policy_gate_enforces_constitution(command, override, must_allow, reason):
    """Failure mode: any gap in the gate lets an unsafe command reach PX4. This
    table proves each constitution rule denies the unsafe case, allows the
    healthy case, and attaches an explainable reason to every denial.
    """
    verdict = policy_gate(command, world_state(**override))
    assert verdict.allowed is must_allow
    if not must_allow:
        assert reason in verdict.reason.lower()

def test_policy_gate_is_default_deny_on_unknown_state():
    """Failure mode: a state the gate can't evaluate must never fall through to
    'allow'. This proves the gate denies rather than guesses when inputs are
    missing or malformed.
    """
    verdict = policy_gate(Arm(), state=None)
    assert verdict.allowed is False
```

Note the shape: a parametrized table where **each row names its failure mode**,
explicit coverage of the healthy/allowed path (so the gate can't pass by denying
everything), and a dedicated default-deny test for the unevaluable case.

### Coverage is a map, not a number

A coverage percentage tells you which lines ran, not which risks are defended.
Chase *risk* coverage instead:

- Every constitution rule has at least one deny test and the allow path is
  exercised.
- Every numeric clamp is tested at `min`, `max`, and just outside both.
- Every fault-injection row above has either an automated test or a logged
  exploratory charter.
- The decision-log hash chain has a property test proving tamper-evidence.

100% line coverage with none of those is a worse suite than 70% with all of
them. See [06-foundations-simulation-test-verification.md](06-foundations-simulation-test-verification.md)
for how this risk-first stance generalizes beyond this repo.

---

## Sources & Citations

- pytest & pytest-asyncio: https://docs.pytest.org  ·  https://pytest-asyncio.readthedocs.io
- Hypothesis (property-based testing): https://hypothesis.readthedocs.io
- Playwright (end-to-end UI): https://playwright.dev
- PX4 SITL (integration target): https://docs.px4.io/main/en/simulation/
- vitest (ground-station unit tests): https://vitest.dev
- Testing taxonomy (unit/integration/acceptance/exploratory): Kaner et al.,
  *Lessons Learned in Software Testing*; Cohn, *Succeeding with Agile* (the test pyramid).
- Exploratory testing & charters: Bach & Bolton, session-based test management; Whittaker, *Exploratory Software Testing*.
- Property-based testing: Claessen & Hughes, *QuickCheck*; Hypothesis docs (above).
- Companion guides: sim/test foundations [06-foundations-simulation-test-verification.md](06-foundations-simulation-test-verification.md), SITL target [22-autonomy-px4-sitl.md](22-autonomy-px4-sitl.md), onboard policy/decision log [23-autonomy-onboard-system.md](23-autonomy-onboard-system.md), safety assurance [09-foundations-safety-assurance.md](09-foundations-safety-assurance.md).

*Test layout and philosophy reflect the author's `pixhawk/drone/test/` scaffold.*
