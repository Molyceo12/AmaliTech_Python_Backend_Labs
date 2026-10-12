"""Tests for Employee Payroll Tracker domain models."""

import pytest

from employee import FullTimeEmployee, ContractEmployee, Intern
from payroll import apply_tax, compute_payroll_details


class TestTaxCalculation:
    def test_tax_below_first_bracket(self):
        """Income below 30,000 pays 0% tax."""
        assert apply_tax(20_000) == 0
        assert apply_tax(30_000) == 0

    def test_tax_in_second_bracket(self):
        """Income between 30,001 and 100,000 pays 20% on amount over 30,000."""
        # 50,000: 20,000 * 0.20 = 4,000
        assert apply_tax(50_000) == 4_000
        # 100,000: 70,000 * 0.20 = 14,000
        assert apply_tax(100_000) == 14_000

    def test_tax_in_third_bracket(self):
        """Income above 100,000 pays 30% on amount over 100,000 plus lower brackets."""
        # 400,000: 70,000 * 0.20 + 300,000 * 0.30 = 14,000 + 90,000 = 104,000
        assert apply_tax(400_000) == 104_000
        # 150,000: 70,000 * 0.20 + 50,000 * 0.30 = 14,000 + 15,000 = 29,000
        assert apply_tax(150_000) == 29_000

    def test_tax_negative_raises(self):
        """Negative income raises ValueError."""
        with pytest.raises(ValueError):
            apply_tax(-100)


class TestFullTimeEmployee:
    def test_salary_calculation(self):
        """Full-time salary = base + bonus."""
        emp = FullTimeEmployee("FT001", "John Doe", 350_000, 50_000)
        assert emp.calculate_salary() == 400_000

    def test_payroll_details(self):
        """Full-time payroll includes correct tax and net."""
        emp = FullTimeEmployee("FT001", "John Doe", 350_000, 50_000)
        details = compute_payroll_details(emp)
        assert details["gross"] == 400_000
        assert details["tax"] == 104_000
        assert details["net"] == 296_000


class TestContractEmployee:
    def test_salary_calculation(self):
        """Contract salary = hourly_rate * hours_worked."""
        emp = ContractEmployee("CT001", "Jane Smith", 5_000, 80)
        assert emp.calculate_salary() == 400_000

    def test_payroll_details(self):
        """Contract payroll includes correct tax and net."""
        emp = ContractEmployee("CT001", "Jane Smith", 5_000, 80)
        details = compute_payroll_details(emp)
        assert details["gross"] == 400_000
        assert details["tax"] == 104_000
        assert details["net"] == 296_000


class TestIntern:
    def test_salary_calculation(self):
        """Intern salary = fixed stipend."""
        emp = Intern("IN001", "Bob Wilson", 200_000)
        assert emp.calculate_salary() == 200_000

    def test_payroll_details(self):
        """Intern payroll includes correct tax and net."""
        emp = Intern("IN001", "Bob Wilson", 200_000)
        details = compute_payroll_details(emp)
        assert details["gross"] == 200_000
        # Tax: 0 on first 30,000 + 70,000 * 0.20 + 100,000 * 0.30 = 0 + 14,000 + 30,000 = 44,000
        assert details["tax"] == 44_000
        assert details["net"] == 156_000


class TestEmployeeValidation:
    def test_full_time_negative_salary_raises(self):
        with pytest.raises(ValueError):
            FullTimeEmployee("FT001", "John", -1000, 0)

    def test_contract_negative_rate_raises(self):
        with pytest.raises(ValueError):
            ContractEmployee("CT001", "Jane", -100, 10)

    def test_intern_negative_stipend_raises(self):
        with pytest.raises(ValueError):
            Intern("IN001", "Bob", -500)