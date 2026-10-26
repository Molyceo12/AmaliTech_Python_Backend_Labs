"""Functional pipeline: map transforms, filters, reduce aggregations."""

from log_analyzer.pipeline.aggregations import (
    count_by,
    count_requests,
    error_rate,
    referrer_ips,
    requests_per_ip,
    requests_per_method,
    requests_per_status,
    requests_per_url,
    top_n,
    total_bytes,
    unique_urls,
)
from log_analyzer.pipeline.filters import (
    Predicate,
    by_method,
    by_status,
    by_status_range,
    in_time_range,
    only_errors,
    select,
    select_all,
)
from log_analyzer.pipeline.pipeline import summarize
from log_analyzer.pipeline.transforms import (
    parse_entries,
    to_record,
    to_records,
)
from log_analyzer.pipeline.windowing import (
    errors_by_status,
    grouped,
    paginate,
    requests_per_hour,
    time_window,
    until,
)

__all__ = [
    "Predicate",
    "by_method",
    "by_status",
    "by_status_range",
    "count_by",
    "count_requests",
    "error_rate",
    "errors_by_status",
    "grouped",
    "in_time_range",
    "only_errors",
    "paginate",
    "parse_entries",
    "referrer_ips",
    "requests_per_hour",
    "requests_per_ip",
    "requests_per_method",
    "requests_per_status",
    "requests_per_url",
    "select",
    "select_all",
    "summarize",
    "time_window",
    "to_record",
    "to_records",
    "top_n",
    "total_bytes",
    "unique_urls",
    "until",
]
