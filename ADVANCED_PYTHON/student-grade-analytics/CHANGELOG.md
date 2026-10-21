# Changelog

All notable changes to the Student Grade Analytics Tool.

## [1.0.0] - 2026-10-21

### Added

- `Grade`, `Student` and `Course` dataclasses, the `ScoreRecord` namedtuple and
  `TypedDict` types for the JSON report
- Collection aggregators: `Counter` grade distribution, `defaultdict` grouping
  by major / year / semester, `OrderedDict` report sections, `deque` rolling
  average
- Exception hierarchy based on `GradeAnalyticsError`
- `RecordReader` interface and `CsvRecordReader` (`pathlib`, context manager,
  `csv.DictReader`, generator); clear errors for missing, unreadable, empty
  and badly formatted files
- Row validation: bad rows are skipped and reported with their line number
- `ReportWriter` interface and `JsonReportWriter` with atomic writes
- Statistics (mean, median, mode, percentile rank), rankings with shared ranks
  for ties, semester trends with a rolling average
- `AnalyticsService` with injected reader, writer and visualizer
- Command line: `grade-analytics data/students.csv` with `--output`, `--top`,
  `--window` and `--no-charts`; exit codes 0 / 1 / 2
- Five PNG charts with matplotlib
- Terminal output in bordered boxes: numbered progress steps and a summary of
  saved files
- Memory comparison of collection approaches (`utils/memory.py`)
- Sample CSV data, 137 tests with 100 % coverage, README, `requirements.txt`
