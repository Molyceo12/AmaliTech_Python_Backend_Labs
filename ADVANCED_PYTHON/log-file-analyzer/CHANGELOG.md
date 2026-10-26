# Changelog

All notable changes to the Log File Analyzer.

## [Unreleased]

### Added

- `skipped_by_ip` in the report: `find_ip` (`re.search`) names the client of
  each skipped line; lines with no IPv4 address count as `unknown`
- `referrer_ips` in the report: `find_all_ips` (`re.findall`) counts the IPv4
  addresses found inside referrer URLs

### Changed

- `is_valid_url` accepts an IPv4 host, e.g. `http://10.0.0.5/admin`
- `parse_line` now uses the validators: a line with an invalid IP (e.g.
  `999.1.1.1`) is skipped, a referrer that is not an http(s) URL becomes
  `null`, and emails in the URL are masked as `***@***`
- The memory comparison builds its large log at `data/large_access.log`
  (git-ignored) instead of `output/`, which now holds only run results

### Removed

- Unused helpers whose requirement is already met by code the app runs:
  `is_valid_email` (email pattern used by `mask_emails`), `by_ip`,
  `in_time_range` and the `only_success` / `only_redirects` /
  `only_client_errors` / `only_server_errors` / `only_get` / `only_post`
  partials (`only_errors` and the `--status` / `--method` filters remain)
- `parse_line_strict` and its `LogParseError`, which nothing called

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
- `LogReader`, `LogParser` and `ReportWriter` abstract classes with
  `FileLogReader`, `ApacheLogParser` and `JsonReportWriter`, injected into
  the analyzer service
- Analyzer service, JSON report writer and the `log-analyzer` command with
  filters, paging and bordered terminal output
- Application log file with levels (`output/log-analyzer.log`, `--log-file`);
  warnings and errors also in the terminal, everything with `-v`
- Generator vs. list memory comparison (`log_analyzer.utils.memory`)
- 203 tests with 100 % coverage, README, `requirements.txt`
