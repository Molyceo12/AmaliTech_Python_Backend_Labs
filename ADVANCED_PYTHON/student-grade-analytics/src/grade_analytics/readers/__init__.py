"""Reading data files: the reader interface and its CSV implementation."""

from grade_analytics.readers.base import RawRecord, RecordReader
from grade_analytics.readers.csv_reader import (
    REQUIRED_HEADERS,
    CsvRecordReader,
    open_data_file,
)
from grade_analytics.readers.student_builder import build_students, parse_record

__all__ = [
    "REQUIRED_HEADERS",
    "CsvRecordReader",
    "RawRecord",
    "RecordReader",
    "build_students",
    "open_data_file",
    "parse_record",
]
