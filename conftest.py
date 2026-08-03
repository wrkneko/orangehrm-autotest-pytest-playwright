import html as html_lib
import logging
import os

import pytest
import yaml
from playwright.sync_api import Playwright


from src.api.api_client import ApiClient
from src.pages.login_page import LoginPage
from src.pages.pim.employee_pages import EmployeeListPage

from dotenv import load_dotenv

try:
    import allure
except ImportError:  # allure-pytest is optional
    allure = None

load_dotenv() # for local test runs purpose

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def _load_config() -> dict:
    env = os.getenv("TEST_ENV", "demo")
    config_path = os.path.join("config", "env", f"{env}.yaml")
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def config() -> dict:
    return _load_config()


@pytest.fixture(scope="session")
def base_url(config) -> str:
    # Environment variable wins, so CI can override without touching yaml.
    return os.getenv("BASE_URL", config["base_url"])


@pytest.fixture(scope="session")
def credentials(config) -> dict:
    return {
        "username": os.getenv("ORANGEHRM_USER", config["credentials"]["username"]),
        "password": os.getenv("ORANGEHRM_PASSWORD", config["credentials"]["password"]),
    }


@pytest.fixture(scope="session")
def reports_test_data() -> dict:
    with open("config/data/reports.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture
def login_page(page, base_url) -> LoginPage:
    """Fresh, unauthenticated login page — for login/negative-path tests."""
    return LoginPage(page, base_url).open()


@pytest.fixture(scope="session")
def storage_state_path(browser, base_url, credentials, tmp_path_factory) -> str:
    """
    Logs in once per test session in a throwaway context and persists the
    resulting storage_state to disk. Individual tests then spin up a new
    context pre-loaded with this state, so they start straight from an
    authenticated dashboard instead of repeating the login UI flow.
    """
    state_path = tmp_path_factory.mktemp("auth") / "state.json"
    context = browser.new_context()
    page = context.new_page()

    lp = LoginPage(page, base_url).open()
    lp.login(credentials["username"], credentials["password"])
    lp.assert_login_successful()

    context.storage_state(path=str(state_path))
    context.close()
    return str(state_path)


@pytest.fixture
def authenticated_page(browser, base_url, storage_state_path):
    context = browser.new_context(storage_state=storage_state_path)
    page = context.new_page()
    page.goto(f"{base_url}/web/index.php/dashboard/index")
    yield page
    context.close()


@pytest.fixture(scope="session")
def api_client(playwright: Playwright, base_url, credentials):
    client = ApiClient(playwright, base_url)
    client.login(credentials["username"], credentials["password"])
    yield client
    client.dispose()


@pytest.fixture
def employee_cleanup(authenticated_page, base_url):
    employee_ids: list[str] = []

    yield employee_ids.append

    if not employee_ids:
        return

    list_page = EmployeeListPage(authenticated_page, base_url)
    for employee_id in employee_ids:
        try:
            list_page.cleanup_employee(employee_id)
        except Exception:
            logger.exception("Failed to clean up employee %s", employee_id)

AI_BASE_URL = "https://openrouter.ai/api/v1"
AI_TIMEOUT_SECONDS = 30
AI_MAX_ANALYSES = int(os.getenv("AI_MAX_ANALYSES", "10"))

_ai_client = None
_ai_analyses_done = 0


def _get_ai_client():
    """Build the client on first use rather than at import.

    At import time a missing AI_TOKEN raises and takes down collection for the
    entire suite — including every test that has nothing to do with the AI.
    """
    global _ai_client

    if _ai_client is not None:
        return _ai_client

    token = os.getenv("AI_TOKEN")
    if not token or not os.getenv("AI_MODEL"):
        return None

    from openai import OpenAI

    _ai_client = OpenAI(
        api_key=token,
        base_url=AI_BASE_URL,
        timeout=AI_TIMEOUT_SECONDS,
        max_retries=1,
    )
    return _ai_client


def _analyse_failure(item, call, report) -> str | None:
    """Ask the model what went wrong. Returns None when unavailable."""
    global _ai_analyses_done

    if _ai_analyses_done >= AI_MAX_ANALYSES:
        return None

    client = _get_ai_client()
    if client is None:
        logger.info("AI analysis skipped: AI_TOKEN or AI_MODEL is not set.")
        return None

    prompt = f"""You are a senior automation QA engineer.
    Test '{item.name}' failed with this error:
    {call.excinfo.exconly()}.
    Traceback:
    {report.longreprtext[-1500:]}

    In couple sentences: is this a real bug, a flaky test,
    or a broken locator or config issue?
    Suggest the most likely root cause.
    """

    response = client.chat.completions.create(
        model=os.getenv("AI_MODEL"),
        messages=[{"role": "user", "content": prompt}],
    )
    _ai_analyses_done += 1
    return response.choices[0].message.content


def _attach_feedback(item, report, feedback: str) -> None:
    """Publish the commentary to whichever reporters are active."""
    pytest_html = item.config.pluginmanager.getplugin("html")
    if pytest_html is not None:
        block = f"<div><b>AI Feedback:</b><pre>{html_lib.escape(feedback)}</pre></div>"
        report.extras = [
            *getattr(report, "extras", []),
            pytest_html.extras.html(block),
        ]

    if allure is not None:
        allure.attach(
            feedback,
            name="AI failure analysis",
            attachment_type=allure.attachment_type.TEXT,
        )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    try:
        feedback = _analyse_failure(item, call, report)
    except Exception as exc:
        logger.warning("AI failure analysis unavailable for %s: %s", item.name, exc)
        return

    if not feedback:
        return

    try:
        _attach_feedback(item, report, feedback)
    except Exception:
        logger.exception("Could not attach AI feedback for %s", item.name)
