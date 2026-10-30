# AmaliTech Labs Solution

This repository contains solutions for the AmaliTech Apprenticeship program.

## Lab Overview

| Module | Lab Name | Purpose | Key Concepts | Run Command (inside lab dir) |
|---|---|---|---|---|
| Module 1 | Employee Payroll Tracker | Command-line system to manage employee types and generate payslips. | Inheritance, Polymorphism, Abstraction, Encapsulation | `python src/main.py` |
| Module 1 | Library Management | CLI application for managing a library's books, members, and loans. | Abstract Base Classes, Composition, File I/O | `python src/main.py` |
| Advanced Python | Student Grade Analytics Tool | CLI that analyses student grades from CSV and writes a JSON report with charts. | Counter, defaultdict, OrderedDict, deque, dataclasses, namedtuples, TypedDict, generators | `python -m poetry run grade-analytics data/students.csv` |
| Advanced Python | Log File Analyzer | CLI that parses Apache/Nginx access logs with regex and writes an analytics report. | Regex, map/filter/reduce, functools.partial, generators, itertools, decorators | `python -m poetry run log-analyzer data/access.log` |
| Database Fundamentals | E-Commerce Analytics Pipeline | PostgreSQL, Redis and MongoDB pipeline with ACID orders, analytics reports and index benchmarks. | 3NF schema, psycopg2 pooling, transactions, JSONB, Redis cache, pymongo, RANK/CTE, EXPLAIN ANALYZE | `python -m poetry run ecommerce demo` |

## Getting Started

### Prerequisites
- Python 3.8+
- Poetry (Recommended)

### Installation

```bash
git clone https://github.com/Molyceo12/AmaliTech_Python_Backend_Labs.git
cd AmaliTech_Python_Backend_Labs
```

### Running a Specific Lab

```bash
cd PYTHON_BASICS/Employee_payroll_tracker
python src/main.py
```

## Technologies
- Language: Python 3
- Testing: pytest
- Management: Poetry
- Version Control: Git