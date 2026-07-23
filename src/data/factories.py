
from dataclasses import dataclass, field

from faker import Faker

fake = Faker()


@dataclass
class EmployeeData:
    first_name: str = field(default_factory=fake.first_name)
    last_name: str = field(default_factory=fake.last_name)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

@dataclass
class ReportData:
    report_name: str = field(
        default_factory = lambda: f"Report {fake.unique.word().title()} "
                                  f"{fake.random_int(10000, 99999)}"
    )


def build_employee(**overrides) -> EmployeeData:
    data = EmployeeData()
    for key, value in overrides.items():
        setattr(data, key, value)
    return data

def build_report_name(**overrides) -> ReportData:
    data = ReportData()
    for key, value in overrides.items():
        setattr(data, key, value)
    return data

