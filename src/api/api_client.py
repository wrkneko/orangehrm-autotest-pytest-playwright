import logging
import re

from playwright.sync_api import APIRequestContext, Playwright
from pydantic import BaseModel, ValidationError

from src.schemas.employee import CreateEmployeeResponse, GetEmployeesResponse
from src.schemas.user import CreateUserResponse

logger = logging.getLogger(__name__)


class ApiClient:
    def __init__(self, playwright: Playwright, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.context: APIRequestContext = playwright.request.new_context(base_url=self.base_url)

    def _check_response(self, response, action: str, schema: type[BaseModel] | None = None) -> dict:
        if response.status >= 400:
            raise RuntimeError(
                f"{action} failed with status {response.status}: {response.text()}")
        body = response.json()
        if schema is not None:
            self._validate_schema(body, schema, action)
        return body

    def _validate_schema(self, body: dict, schema: type[BaseModel], action: str) -> None:
        try:
            schema.model_validate(body)
        except ValidationError as e:
            raise AssertionError(
                f"{action}: response does not match expected schema {schema.__name__}:\n{e}"
            ) from e

    def login(self, username: str, password: str) -> None:
        login_page = self.context.get("/web/index.php/auth/login")
        token_match = re.search(r':token="&quot;([^&]+)&quot;"', login_page.text())
        if not token_match:
            raise RuntimeError("Could not extract CSRF token from login page — page markup may have changed")
        token = token_match.group(1)

        response = self.context.post(
            "/web/index.php/auth/validate",
            form={"_token": token, "username": username, "password": password},
        )
        if response.status >= 400:
            raise RuntimeError(f"API login failed with status {response.status}")
        if "/auth/login" in response.url:
            raise RuntimeError(
                f"API login failed: credentials rejected for '{username}' "
                f"(redirected back to login page)"
            )
        logger.info("API session authenticated as '%s'", username)

    def get_employees(self, name_filter: str = "") -> dict:
        response = self.context.get(
            "/web/index.php/api/v2/pim/employees",
            params={"nameOrId": name_filter} if name_filter else {},
        )
        return self._check_response(response, "Fetch employees", schema=GetEmployeesResponse)

    def create_employee(self, payload: dict) -> dict:
        if "firstName" not in payload or "lastName" not in payload:
            raise ValueError("create_employee payload requires 'firstName' and 'lastName'")

        response = self.context.post("/web/index.php/api/v2/pim/employees", data=payload)
        body = self._check_response(response, "Create employee", schema=CreateEmployeeResponse)
        logger.info(
            "Created employee %s %s -> empNumber=%s",
            payload["firstName"], payload["lastName"], body["data"]["empNumber"],
        )
        return body["data"]

    def create_user(self, payload: dict) -> dict:
        required = {"username", "password", "empNumber"}
        missing = required - payload.keys()
        if missing:
            raise ValueError(
                f"create_user payload missing required fields: {missing}")

        response = self.context.post("/web/index.php/api/v2/admin/users", data=payload)
        body = self._check_response(response, "Create user", schema=CreateUserResponse)
        user = body["data"]
        logger.info(
            "Created user '%s' (id=%s) for empNumber=%s",
            user["userName"], user["id"], payload["empNumber"],
        )
        return user

    def create_employee_with_login(self, employee_payload: dict, user_payload: dict) -> dict:
        employee = self.create_employee(employee_payload)
        user_payload = {"empNumber": employee["empNumber"], **user_payload}
        user = self.create_user(user_payload)
        return {"employee": employee, "user": user}

    def delete_employee(self, employee_id: int) -> dict:
        return self.delete_employees([employee_id])

    def delete_employees(self, employee_ids: list[int]) -> dict:
        response = self.context.delete(
            "/web/index.php/api/v2/pim/employees",
            data={"ids": employee_ids},
        )
        logger.info("Deleted employees %s", employee_ids)
        return self._check_response(response, f"Delete employees {employee_ids}")

    def delete_user(self, user_id: int) -> dict:
        return self.delete_users([user_id])

    def delete_users(self, user_ids: list[int]) -> dict:
        response = self.context.delete(
            "/web/index.php/api/v2/admin/users",
            data={"ids": user_ids},
        )
        logger.info("Deleted users %s", user_ids)
        return self._check_response(response, f"Deleted users: {user_ids}")

    def dispose(self) -> None:
        self.context.dispose()
