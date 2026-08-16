from typing import Any, Optional
from pydantic import BaseModel

from src.schemas.generic import ApiEnvelope


class CreateUserPayload(BaseModel):
    username: str
    password: str
    status: bool
    userRoleId: int
    empNumber: int


class UserEmployeeSummary(BaseModel):
    empNumber: int
    employeeId: Optional[str] = None
    firstName: str
    middleName: Optional[str] = None
    lastName: str
    terminationId: Optional[Any] = None


class UserRole(BaseModel):
    id: int
    name: str
    displayName: str


class UserData(BaseModel):
    id: int
    userName: str
    deleted: bool
    status: bool
    employee: UserEmployeeSummary
    userRole: UserRole


CreateUserResponse = ApiEnvelope[UserData]
