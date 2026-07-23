# OrangeHRM Test Automation Framework

End-to-end UI + API automation framework for the [OrangeHRM public demo](https://opensource-demo.orangehrmlive.com),
built with **Python + Playwright + pytest**.

## Why this structure

- **Page Object layer (`src/pages`)** — one class per page, all Playwright
  interaction lives here. Tests never touch a locator directly.
- **API layer (`src/api`)** — reuses the app's own session to call internal
  endpoints for fast test-data setup/teardown, avoiding slow UI-only flows.
- **Data layer (`src/data`)** — Faker-based factories generate unique data
  per run. This matters because the demo instance is **public and shared**:
  hardcoded names would collide with other people's test runs.
- **Fixtures (`tests/conftest.py`)** — a session-scoped login generates a
  `storage_state` once; per-test contexts reuse it, so tests start on an
  authenticated dashboard instead of repeating the login UI every time.
- **Markers** (`smoke`, `regression`, `ui`, `api`) — let CI run a fast smoke
  suite on every push and a full regression nightly.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium

cp .env.example .env             # adjust if needed
```

## Running tests

```bash
pytest                           # everything
pytest -m smoke                  # fast critical-path checks
pytest -m regression             # full regression suite
pytest -m api                    # API tests only
pytest tests/ui/test_login.py -v
pytest --headed --slowmo=300     # watch it run
```

Failure artifacts (trace, screenshot, video) are saved under `test-results/`
automatically — open a trace with:

```bash
playwright show-trace test-results/<test-name>/trace.zip
```

## Reporting

Allure results are written to `allure-results/`. To view a local report:

```bash
pip install allure-pytest
allure serve allure-results
```

## A note on the target environment

`opensource-demo.orangehrmlive.com` is a **public, shared** instance — data
created by this suite is visible to everyone else testing against it at the
same time, and the app doesn't reset between runs. That's why:

- test data is always uniquely generated (Faker), never hardcoded;
- tests that create data clean up after themselves in the same test;
- `--reruns=1` is enabled in `pytest.ini` to absorb occasional flakiness
  from a public, sometimes-slow, third-party-hosted demo — not to mask
  real bugs.

## What's next

This is a skeleton, not the full suite. Natural next additions:
- More PIM/Leave/Admin module coverage
- Visual regression on the dashboard
- Cross-browser matrix in CI (firefox/webkit)
- Parallel execution (`pytest-xdist`)
