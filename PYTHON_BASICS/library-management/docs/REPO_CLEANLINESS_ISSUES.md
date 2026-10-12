# Repository Cleanliness & Documentation Issues

## Issue 1: README Claims pytest but No Tests Exist
**File:** `README.md` (both labs)
**Problem:** README documents `poetry run pytest` as test command, but `tests/` directory is empty or missing. Either write tests or remove the line.

## Issue 2: Payroll Sample Output Incorrect
**File:** `README.md` (payroll lab)
**Problem:** 
- Sample output shows tax = 90,000 but actual code calculates 104,000
- Sample output shows currency as `$` but README says `RWF` (Rwandan Franc)

## Issue 3: Compiled Python Files Committed
**Files:** Multiple `__pycache__/` directories tracked in git
**Problem:** `.pyc` bytecode files should not be committed. Need to:
1. Add `__pycache__/` to `.gitignore`
2. Remove from tracking: `git rm -r --cached <path>/__pycache__`

## Issue 4: Both Labs in Single Commit
**Problem:** All changes for both labs committed together. Should commit incrementally per milestone/feature for clean history.

## Issue 5: Missing .gitignore
**Problem:** No `.gitignore` file exists in repository root to exclude `__pycache__/`, `.pytest_cache/`, `*.pyc`, virtual environments, etc.