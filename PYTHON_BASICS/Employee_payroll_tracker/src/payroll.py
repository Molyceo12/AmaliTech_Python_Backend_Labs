"""payroll.py — payroll tax calculations, payslips, and batch processing."""

from employee import Employee
from utils import SCREEN_WIDTH, format_currency, divider, format_row


# Rwanda RRA monthly PAYE brackets: (lower_bound, upper_bound, rate)
_TAX_BRACKETS: list[tuple[float, float, float]] = [
    (0, 30_000, 0.00),
    (30_000, 100_000, 0.20),
    (100_000, float("inf"), 0.30),
]


def apply_tax(monthly_gross: float) -> float:
    """Calculate the monthly tax for a given gross pay using Rwanda's tax bands."""
    if monthly_gross < 0:
        raise ValueError(f"monthly_gross cannot be negative, got {monthly_gross}.")
    tax = 0.0
    for lower, upper, rate in _TAX_BRACKETS:
        if monthly_gross <= lower:
            break  # income does not reach this bracket — stop early
        taxable_in_band = min(monthly_gross, upper) - lower
        tax += taxable_in_band * rate
    return tax


def compute_payroll_details(employee: Employee) -> dict:
    """Work out an employee's gross pay, tax, and net pay, and return them in a dictionary."""
    gross = employee.calculate_salary()
    tax = apply_tax(gross)
    net = gross - tax
    return {
        "emp_id": employee.emp_id,
        "name": employee.name,
        "role": employee.role(),
        "gross": gross,
        "tax": tax,
        "net": net,
    }


def generate_payslip(employee: Employee) -> str:
    """Create a neatly formatted payslip for an employee and return it as text."""
    data = compute_payroll_details(employee)
    lines = [
        divider(),
        format_row("PAYSLIP".center(SCREEN_WIDTH - 6)),
        divider(),
        format_row(f"ID     : {data['emp_id']}"),
        format_row(f"Name   : {data['name']}"),
        format_row(f"Role   : {data['role']}"),
        divider(),
        format_row(f"Gross  : {format_currency(data['gross'])}"),
        format_row(f"Tax    : {format_currency(data['tax'])}"),
        format_row(f"Net    : {format_currency(data['net'])}"),
        divider(),
    ]
    return "\n".join(lines)


def process_payroll(employees: list[Employee]) -> list[dict]:
    """Calculate payroll details for every employee in the list and return the results."""
    return [compute_payroll_details(emp) for emp in employees]
