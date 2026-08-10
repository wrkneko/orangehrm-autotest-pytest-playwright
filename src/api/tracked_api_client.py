


class TrackedApiClient:
    def __init__(self, api_client, cleanup):
        self._api_client = api_client
        self._cleanup = cleanup

    def __getattr__(self, name):
        return getattr(self._api_client, name)

    def create_employee(self, payload):
        employee = self._api_client.create_employee(payload)
        self._cleanup["employee"](employee["empNumber"])
        return employee

    def create_user(self, payload):
        user = self._api_client.create_user(payload)
        self._cleanup["user"](user["id"])
        return user

    def create_employee_with_login(self, employee_payload, user_payload):
        result = self._api_client.create_employee_with_login(employee_payload, user_payload)
        self._cleanup["employee"](result["employee"]["empNumber"])
        self._cleanup["user"](result["user"]["id"])
        return result