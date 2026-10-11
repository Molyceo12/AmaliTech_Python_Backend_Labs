"""Base employee module."""

from abc import ABC, abstractmethod


class Employee(ABC):
    """Base class for all types of employees."""

    def __init__(self, staff_id: str, full_name: str, starting_salary: float) -> None:
        if not staff_id or not staff_id.strip():
            raise ValueError("Employee ID cannot be empty.")
        if not full_name or not full_name.strip():
            raise ValueError("Employee name cannot be empty.")

        self.emp_id = staff_id.strip().upper()
        self.name = full_name.strip()
        self.base_salary = starting_salary

    @property
    def base_salary(self) -> float:
        """Get the base salary."""
        return self._base_salary

    @base_salary.setter
    def base_salary(self, amount: float) -> None:
        """Check and set the base salary."""
        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            raise ValueError(
                f"Base salary must be a number, got {type(amount).__name__}."
            )
        if amount <= 0:
            raise ValueError(f"Base salary must be greater than 0, got {amount}.")
        self._base_salary = float(amount)

    @abstractmethod
    def calculate_salary(self) -> float:
        """Calculate and return monthly gross salary."""

    @abstractmethod
    def role(self) -> str:
        """Return the employee job title."""

    @property
    @abstractmethod
    def is_tax_exempt(self) -> bool:
        """Return True if this employee does not pay income tax."""

    def __str__(self) -> str:
        """Format employee info as a readable string."""
        return f"{self.role()} | {self.emp_id} — {self.name}"

    def __repr__(self) -> str:
        """Format employee info for debugging."""
        return f"{self.__class__.__name__}(emp_id={self.emp_id!r}, name={self.name!r})"


class FullTimeEmployee(Employee):
    """Full-time employee with base salary and bonus."""

    def __init__(
        self, staff_id: str, full_name: str, starting_salary: float, bonus_pay: float = 0.0
    ) -> None:
        super().__init__(staff_id, full_name, starting_salary)
        self.bonus = bonus_pay

    @property
    def bonus(self) -> float:
        """Get the bonus amount."""
        return self._bonus

    @bonus.setter
    def bonus(self, amount: float) -> None:
        """Check and set the bonus amount."""
        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            raise ValueError(f"bonus must be a number, got {type(amount).__name__}.")
        if amount < 0:
            raise ValueError(f"bonus must be at least 0, got {amount}.")
        self._bonus = float(amount)

    def calculate_salary(self) -> float:
        """Calculate total monthly pay: base salary plus bonus."""
        return self._base_salary + self._bonus

    def role(self) -> str:
        """Return the job title."""
        return "Full-Time Employee"

    @property
    def is_tax_exempt(self) -> bool:
        """Full-time employees pay income tax."""
        return False


class ContractEmployee(Employee):
    """Contract employee paid by the hour."""

    def __init__(
        self, staff_id: str, full_name: str, hourly_rate: float, hours_worked: float
    ) -> None:
        super().__init__(staff_id, full_name, hourly_rate)
        self.hours_worked = hours_worked

    @property
    def hourly_rate(self) -> float:
        """Get the hourly rate (stored in base salary)."""
        return self._base_salary

    @property
    def hours_worked(self) -> float:
        """Get the number of hours worked."""
        return self._hours_worked

    @hours_worked.setter
    def hours_worked(self, hours: float) -> None:
        """Check and set hours worked."""
        if not isinstance(hours, (int, float)) or isinstance(hours, bool):
            raise ValueError(
                f"hours_worked must be a number, got {type(hours).__name__}."
            )
        if hours < 0:
            raise ValueError(f"hours_worked must be at least 0, got {hours}.")
        self._hours_worked = float(hours)

    def calculate_salary(self) -> float:
        """Calculate total pay: hourly rate multiplied by hours worked."""
        return self._base_salary * self._hours_worked

    def role(self) -> str:
        """Return the job title."""
        return "Contract Employee"

    @property
    def is_tax_exempt(self) -> bool:
        """Contract employees pay income tax."""
        return False


class Intern(Employee):
    """Intern receiving a fixed monthly stipend."""

    def __init__(self, staff_id: str, full_name: str, stipend: float) -> None:
        super().__init__(staff_id, full_name, stipend)

    @property
    def stipend(self) -> float:
        """Get the intern stipend (stored in base salary)."""
        return self._base_salary

    def calculate_salary(self) -> float:
        """Calculate total pay: returns the fixed stipend directly."""
        return self._base_salary

    def role(self) -> str:
        """Return the job title."""
        return "Intern"

    @property
    def is_tax_exempt(self) -> bool:
        """Interns pay income tax."""
        return False
