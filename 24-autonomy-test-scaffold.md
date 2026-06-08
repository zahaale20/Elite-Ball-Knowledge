# Test scaffold

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

---

## Sources & Citations

- pytest & pytest-asyncio: https://docs.pytest.org  ·  https://pytest-asyncio.readthedocs.io
- Hypothesis (property-based testing): https://hypothesis.readthedocs.io
- Playwright (end-to-end UI): https://playwright.dev
- PX4 SITL (integration target): https://docs.px4.io/main/en/simulation/
- vitest (ground-station unit tests): https://vitest.dev
- Testing taxonomy (unit/integration/acceptance/exploratory): Kaner et al.,
  *Lessons Learned in Software Testing*; Cohn, *Succeeding with Agile* (the test pyramid).

*Test layout and philosophy reflect the author's `pixhawk/drone/test/` scaffold.*
