from typing import Any, Optional
from pydantic import BaseModel

from src.schemas.generic import ApiEnvelope


class CreateEmployeePayload(BaseModel):
    firstName: str
    middleName: Optional[str] = None
    lastName: str
    empPicture: Optional[str] = None
    employeeId: Optional[str] = None


class EmployeeData(BaseModel):
    empNumber: int
    firstName: str
    lastName: str
    middleName: Optional[str] = None
    employeeId: Optional[str] = None
    terminationId: Optional[Any] = None


CreateEmployeeResponse = ApiEnvelope[EmployeeData]