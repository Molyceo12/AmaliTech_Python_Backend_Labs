"""main.py — CLI entry point for the Employee Payroll Tracker."""

from employee import ContractEmployee, Employee, FullTimeEmployee, Intern
from payroll import generate_payslip, process_payroll
from utils import divider, format_currency, format_header, format_row


def prompt_emp_id(existing_ids: set[str]) -> str:
    """Keep asking until the user enters a valid, unique employee ID made of letters and numbers."""
    while True:
        raw = input("  Employee ID     (e.g. FT001)    : ").strip()
        if not raw:
            print("  ! ID cannot be empty.")
        elif len(raw) > 10:
            print("  ! ID must be 10 characters or fewer.")
        elif not raw.isalnum():
            print("  ! ID must contain only letters and digits (e.g. FT001).")
        elif raw.upper() in existing_ids:
            print(f"  ! ID '{raw.upper()}' is already taken. Use a different ID.")
        else:
            return raw.upper()


def prompt_name() -> str:
    """Keep asking until the user enters a valid name with only letters, spaces, hyphens, or apostrophes."""
    while True:
        raw = input("  Full Name (e.g. Nziza Paul) : ").strip()
        if not raw:
            print("  ! Name cannot be empty.")
        elif len(raw) < 2:
            print("  ! Name must be at least 2 characters.")
        elif len(raw) > 50:
            print("  ! Name must be 50 characters or fewer.")
        elif not all(ch.isalpha() or ch in " -'" for ch in raw):
            print(
                "  ! Name must contain only letters, spaces, hyphens, or apostrophes."
            )
        else:
            return raw.title()


def prompt_float(label: str, min_val: float = 0.0) -> float:
    """Keep asking until the user enters a valid number that is at least min_val."""
    while True:
        try:
            value = float(input(f"  {label}: ").strip())
            if value < min_val:
                print(f"  ! Value must be >= {min_val:,.2f}.")
            else:
                return value
        except ValueError:
            print("  ! Invalid number - enter digits only (e.g. 350000).")


def _add_full_time(existing_ids: set[str]) -> FullTimeEmployee:
    """Collect the employee's details and return a new FullTimeEmployee."""
    print("\n" + format_row("  -- Full-Time Employee --"))
    emp_id = prompt_emp_id(existing_ids)
    name = prompt_name()
    salary = prompt_float("Base Salary (e.g. 350000)          ", min_val=0.01)
    bonus = prompt_float("Monthly Bonus (e.g. 50000, 0 if none)", min_val=0.0)
    return FullTimeEmployee(emp_id, name, salary, bonus)


def _add_contract(existing_ids: set[str]) -> ContractEmployee:
    """Collect the employee's details and return a new ContractEmployee."""
    print("\n" + format_row("  -- Contract Employee --"))
    emp_id = prompt_emp_id(existing_ids)
    name = prompt_name()
    rate = prompt_float("Hourly Rate (e.g. 3000)            ", min_val=0.01)
    hours = prompt_float("Hours Worked (e.g. 160)             ", min_val=0.0)
    return ContractEmployee(emp_id, name, rate, hours)


def _add_intern(existing_ids: set[str]) -> Intern:
    """Collect the intern's details and return a new Intern."""
    print("\n" + format_row("  -- Intern --"))
    emp_id = prompt_emp_id(existing_ids)
    name = prompt_name()
    stipend = prompt_float("Monthly Stipend (e.g. 80000)           ", min_val=0.01)
    return Intern(emp_id, name, stipend)


# Maps menu keys to (display label, factory function) pairs.
_ROLE_MAP: dict[str, tuple[str, callable]] = {
    "1": ("Full-Time Employee", _add_full_time),
    "2": ("Contract Employee", _add_contract),
    "3": ("Intern", _add_intern),
}


def collect_employees() -> list[Employee]:
    """Show the menu, collect employees, and return the list of them."""
    employees: list[Employee] = []
    existing_ids: set[str] = set()
    print(format_header("EMPLOYEE PAYROLL TRACKER"))

    while True:
        print("\n" + format_row("  Select employee type:"))
        for key, (label, _) in _ROLE_MAP.items():
            print(format_row(f"    [{key}] {label}"))
        if employees:  # show exit option only after at least one employee is added
            print(format_row("    [0] Done - generate payroll"))

        choice = input("\n  Your choice: ").strip()

        if choice == "0":
            if not employees:
                print("  ! Invalid choice. Enter 1, 2, or 3.")
            else:
                break
        elif choice in _ROLE_MAP:
            try:
                emp = _ROLE_MAP[choice][1](existing_ids)
                employees.append(emp)
                existing_ids.add(emp.emp_id)
                print("\n" + format_row(f"  + {emp.name} ({emp.emp_id}) added successfully."))
            except ValueError as exc:
                print(f"  ! Error: {exc}")
        else:
            print("  ! Invalid choice. Enter 1, 2, or 3.")

    return employees


def print_all_payslips(employees: list[Employee]) -> None:
    """Print a payslip for every employee in the list."""
    print("\n" + format_header("PAYSLIPS"))
    for emp in employees:
        print(generate_payslip(emp))


def print_summary(payroll_data: list[dict]) -> None:
    """Print a table of all employees with their net pay, plus totals."""
    print("\n" + divider())
    print(format_row(f"{'ID':<8} {'Name':<18} {'Role':<22} {'Net Pay':>10}"))
    print(divider())

    total_gross, total_tax, total_net = 0.0, 0.0, 0.0

    for record in payroll_data:
        line = (
            f"{record['emp_id']:<8} {record['name']:<18} "
            f"{record['role']:<22} {format_currency(record['net']):>10}"
        )
        print(format_row(line))
        total_gross += record["gross"]
        total_tax += record["tax"]
        total_net += record["net"]

    print(divider())
    print(format_row(f"{'TOTALS':<51}{format_currency(total_net):>10}"))
    print(format_row(f"Total Gross : {format_currency(total_gross)}"))
    print(format_row(f"Total Tax   : {format_currency(total_tax)}"))
    print(format_row(f"Total Net   : {format_currency(total_net)}"))
    print(divider())


def main() -> None:
    """Run the whole payroll process: collect employees, show payslips, then show the summary."""
    employees = collect_employees()
    print_all_payslips(employees)
    payroll_data = process_payroll(employees)
    print_summary(payroll_data)


if __name__ == "__main__":
    main()
