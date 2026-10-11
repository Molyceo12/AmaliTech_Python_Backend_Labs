# AmaliTech Labs Solution

This repository serves as a centralized monorepo containing solutions for the AmaliTech Apprenticeship program. It demonstrates progressive learning across various domains, ranging from fundamental Object-Oriented Programming (OOP) to advanced topics like Test-Driven Development (TDD), Clean Architecture, and Robust CLI handling.

## Lab Overview

The following table provides a high-level summary of the labs completed in this repository, detailing their purpose, key technical concepts, and execution commands.

| Module | Lab Name | Purpose | Key Concepts | Run Command (inside lab dir) |
|---|---|---|---|---|
| Module 1 | Employee Payroll Tracker | Command-line system to manage employee types and generate payslips. | Inheritance, Polymorphism, Abstraction, Encapsulation | `python src/main.py` |
| Module 1 | Library Inventory App | Manages library assets (books, audiobooks), authors, and loans with overdue logic. | Abstract Base Classes, Composition, Date manipulation | `python src/main.py` |
| Module 1 | Student Course System | Administers student enrollments, courses, and grading. | Composition, Data Dictionary Storage, Modular Design | `python main.py` |
| Module 2 | Resilient Data Importer | Robust CLI tool for importing/deduplication of CSV user data into JSON storage. | File I/O, Exception Handling, Generators, Dataclasses | `poetry run python -m resilient_importer.cli data/users.csv` |
| Module 2 | TDD Weather API Stub | A weather service stub designed to demonstrate high-quality software engineering practices. | TDD (Test-Driven Development), SOLID Principles, Clean Architecture | `pytest` |
| Module 3 | Student Grade Analytics | CLI tool for analyzing student grades using advanced collections and generating JSON reports. | Advanced Collections, Dataclasses, IO Context Managers | `python -m student_analytics.main` |
| Module 3 | Log File Analyzer | CLI tool for parsing and analyzing web server logs for insights. | Regex, Generators, Functional Programming | `python -m log_file_analyzer.main` |
| Module 4 | E-Commerce Analytics | Polyglot data pipeline with SQL/NoSQL integration and complex analytics. | Postgres, Redis, MongoDB, JSONB, ETL | (See Lab README) |
| Module 5 | URL Shortener Microservices | Distributed URL shortener backend and web scraping preview microservice. | Django DRF, Celery, Redis, Postgres, Docker | `docker-compose up --build -d` |

## Getting Started

### Prerequisites
- Python 3.8+ (Required for all labs)
- Poetry (Recommended for Module 2 labs)

### Installation
Clone the entire repository to access all labs:

```bash
git clone https://github.com/Molyceo12/AmaliTech_Python_Backend_Labs.git
cd AmaliTech_Python_Backend_Labs
```

### Running a Specific Lab
Navigate to the directory of the specific lab you wish to run and follow the "Run Command" listed in the table above. For Module 2 labs, ensure you install dependencies first:

```bash
# Example for Module 2
cd "PYTHON_BASICS/Resilient Data Importer CLI"
poetry install
poetry shell
```

## Technologies
- Language: Python 3
- Testing: pytest
- Management: Poetry
- Version Control: Git