
import logging
import re
import uuid

from playwright.sync_api import APIRequestContext, Playwright

logger = logging.getLogger(__name__)


class ApiClient:
    def __init__(self, playwright: Playwright, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.context: APIRequestContext = playwright.request.new_context(base_url=self.base_url)

    def _check_response(self, response, action:str) -> dict:
        if response.status >= 400:
            raise RuntimeError(f"API login failed with status {response.status}")
        return response.json()


    def login(self, username: str, password: str) -> None:
        login_page = self.context.get("/web/index.php/auth/login")
        token_match = re.search(r'name="_token"\s+value="([^"]+)"', login_page.text())
        token = token_match.group(1) if token_match else ""

        response = self.context.post(
            "/web/index.php/auth/login",
            form={"username": username, "password": password, "_token": token},
        )
        if response.status >= 400:
            raise RuntimeError(f"API login failed with status {response.status}")
        logger.info("API session authenticated as '%s'", username)

    def get_employees(self, name_filter: str = "") -> dict:
        response = self.context.get(
            "/web/index.php/api/v2/pim/employees",
            params={"nameOrId": name_filter} if name_filter else {},
        )
        if response.status >= 400:
            raise RuntimeError(f"Failed to fetch employees: {response.status}")
        return response.json()

    def delete_employee(self, employee_id: str) -> None:
        response = self.context.delete(f"/web/index.php/api/v2/pim/employees/{employee_id}")
        logger.info("Delete employee %s -> status %s", employee_id, response.status)

    def create_employee(self, payload: dict) -> dict:
        body_payload = {
            "middleName": "",
            "empPicture": None,
            "employeeId": str(uuid.uuid4().int)[:6],
            **payload
        }

        if "firstName" not in body_payload or "lastName" not in body_payload:
            raise ValueError("employee create payload requires 'firstName' and 'lastName'")
        response = self.context.post("/web/index.php/api/v2/pim/employees",
                                     data=body_payload)
        body = self._check_response(response, "Create Employee")
        logger.info(
            "Created employee %s %s -> empNumber=%s",
            body_payload["firstName"], body_payload["lastName"],
            body["data"]["empNumber"]
        )
        return body["data"]

    def dispose(self) -> None:
        self.context.dispose()
