import logging
import os

import pytest
import yaml
from playwright.sync_api import Playwright

from src.api.api_client import ApiClient
from src.pages.login_page import LoginPage
from src.pages.pim.employee_pages import EmployeeListPage

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
