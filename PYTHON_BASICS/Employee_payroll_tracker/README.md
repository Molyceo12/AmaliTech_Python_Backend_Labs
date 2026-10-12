# Employee Payroll Tracker

A Python CLI application for computing employee payroll with Rwanda PAYE tax.

Supports three employee types: Full-Time, Contract, and Intern.

## Setup

```bash
python -m poetry install
```

## Usage

```bash
python -m poetry run python src/main.py
```

Or directly:

```bash
python src/main.py
```

## Test

```bash
python -m poetry run pytest
```

## Employee Types

### Full-Time Employee
- Base salary plus monthly bonus
- Pays income tax

### Contract Employee
- Paid by the hour (hourly rate x hours worked)
- Pays income tax

### Intern
- Fixed monthly stipend
- Pays income tax

## Rwanda PAYE Tax Brackets

| Monthly Gross (RWF) | Rate |
|---|---|
| 0 – 30,000 | 0% |
| 30,001 – 100,000 | 20% |
| 100,001+ | 30% |

## How to Use

1. Start the app. The main menu shows three employee types.
2. Type `1` for Full-Time, `2` for Contract, or `3` for Intern.
3. Enter the employee details when prompted:
   - **Full-Time:** ID, name, base salary, monthly bonus
   - **Contract:** ID, name, hourly rate, hours worked
   - **Intern:** ID, name, monthly stipend
4. If you enter invalid input, the app shows an error and re-prompts you.
5. Repeat steps 2-4 to add more employees.
6. Type `0` when done to generate payroll.

## Input Validation

The app validates all input and re-prompts on errors:
- Employee ID: letters and digits only, max 10 characters, must be unique
- Name: letters, spaces, hyphens, apostrophes only, 2–50 characters
- Salary/rate/stipend: must be a positive number

## Sample Output

### Menu

```
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::                    EMPLOYEE PAYROLL TRACKER                    ::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

::   Select employee type:                                        ::
::     [1] Full-Time Employee                                     ::
::     [2] Contract Employee                                      ::
::     [3] Intern                                                 ::

  Your choice: 1

  -- Full-Time Employee --
  Employee ID     (e.g. FT001)    : FT001
  Full Name (e.g. Nziza Paul) : Nziza Paul
  Base Salary (e.g. 350000)          : 350000
  Monthly Bonus (e.g. 50000, 0 if none) : 50000

  + Nziza Paul (FT001) added successfully.

  Your choice: 0
```

### Payslip

```
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::                          PAYSLIP                                ::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: ID     : FT001                                                  ::
:: Name   : Nziza Paul                                             ::
:: Role   : Full-Time Employee                                     ::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Gross  : RWF 400,000.00                                         ::
:: Tax    : RWF 104,000.00                                         ::
:: Net    : RWF 296,000.00                                         ::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
```

### Summary Table

```
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: ID       Name               Role                    Net Pay     ::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: FT001    Nziza Paul         Full-Time Employee      RWF 296,000.00 ::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: TOTALS                                                        RWF 296,000.00 ::
:: Total Gross : RWF 400,000.00                                      ::
:: Total Tax   : RWF 104,000.00                                       ::
:: Total Net   : RWF 296,000.00                                       ::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
```

## Payslip Output

After all employees are entered, a payslip is printed for each one showing gross pay, tax, and net pay. Then a summary table shows all employees with their net pay, plus total gross, total tax, and total net.

## Project Structure

```
src/
  employee.py    — Employee base class and subclasses (Full-Time, Contract, Intern)
  payroll.py     — Tax calculations, payslips, and batch processing
  utils.py       — Formatting helpers (currency, dividers, headers)
  main.py        — CLI entry point
```