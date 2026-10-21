# Changelog

All notable changes to the Log File Analyzer.

## [1.0.0] - 2026-10-21

### Added

- Compiled regex patterns with named groups for the common and combined
  Apache/Nginx log formats
- IP, email and URL validation patterns; `re.sub()` cleaning helpers
- `LogEntry` dataclass, report `TypedDict`s and a `LogAnalyzerError`
  exception hierarchy
- Sample logs (1,500 lines plus a malformed file) built by a fixed-seed script
- Functional pipeline: `map()` transforms, `filter()` predicates with
  `functools.partial()`, `reduce()` aggregations, `pipe` / `compose`
- Generator-based file reading, `itertools.chain` for several files and a
  `Batches` custom iterator
- `itertools.groupby`, `islice`, `takewhile` and `dropwhile` helpers for
  grouping, pagination and time windows
- `@timer`, `@cache` (`functools.lru_cache`) and `@log_call` decorators,
  chained on the analyzer run
- Analyzer service, JSON report writer and the `log-analyzer` command with
  filters, paging and bordered terminal output
- Generator vs. list memory comparison (`log_analyzer.utils.memory`)
- 180 tests with 100 % coverage, README, `requirements.txt`
