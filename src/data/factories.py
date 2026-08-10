from dataclasses import dataclass, field

from faker import Faker

fake = Faker()


@dataclass
class EmployeeData:
    first_name: str = field(default_factory=fake.first_name)
    middle_name: str = ""
    last_name: str = field(default_factory=fake.last_name)
    employee_id: str = field(default_factory=lambda: str(fake.unique.random_number(digits=6)))

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def to_payload(self) -> dict:
        return {
            "firstName": self.first_name,
            "middleName": self.middle_name,
            "lastName": self.last_name,
            "empPicture": None,
            "employeeId": self.employee_id,
        }


@dataclass
class UserData:
    username: str = field(default_factory=lambda: fake.unique.user_name())
    password: str = "Kivpassword1!"
    user_role_id: int = 2
    status: bool = True

    def to_payload(self) -> dict:
        return {
            "username": self.username,
            "password": self.password,
            "userRoleId": self.user_role_id,
            "status": self.status,
        }


@dataclass
class ReportData:
    report_name: str = field(
        default_factory=lambda: f"Report {fake.unique.word().title()} "
                                 f"{fake.random_int(10000, 99999)}"
    )


def build_employee(**overrides) -> EmployeeData:
    data = EmployeeData()
    for key, value in overrides.items():
        setattr(data, key, value)
    return data


def build_user(**overrides) -> UserData:
    data = UserData()
    for key, value in overrides.items():
        setattr(data, key, value)
    return data


def build_report_name(**overrides) -> ReportData:
    data = ReportData()
    for key, value in overrides.items():
        setattr(data, key, value)
    return data