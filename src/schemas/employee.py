from typing import Any, Optional
from pydantic import BaseModel

from src.schemas.generic import ApiEnvelope, PaginatedApiEnvelope


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


class JobTitle(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    isDeleted: Optional[bool] = None


class SubUnit(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class EmpStatus(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class EmployeeListItemDefault(BaseModel):
    empNumber: int
    lastName: str
    firstName: str
    middleName: Optional[str] = None
    employeeId: Optional[str] = None
    terminationId: Optional[Any] = None


# created for case where request is sent with model=detailed, WIP
class EmployeeListItemDetailed(EmployeeListItemDefault):
    jobTitle: JobTitle
    subunit: SubUnit
    empStatus: EmpStatus
    supervisors: list[Any] = []


GetEmployeesResponse = PaginatedApiEnvelope[list[EmployeeListItemDefault]]
GetEmployeesDetailedResponse = PaginatedApiEnvelope[list[EmployeeListItemDetailed]]
