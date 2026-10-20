"""Tests for the analytics service, with the reader and writer mocked."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from grade_analytics.exceptions import DataFileNotFoundError
from grade_analytics.models import RowProblem
from grade_analytics.readers import RawRecord, RecordReader
from grade_analytics.services import AnalyticsService
from grade_analytics.visualization import ReportVisualizer
from grade_analytics.writers import ReportWriter
from tests.helpers import ROW_DATA

Mocks = tuple[MagicMock, MagicMock]


@pytest.fixture(name="mocks")
def fixture_mocks(mocker: MockerFixture) -> Mocks:
    """Return a mock reader (one good row, one bad row) and a mock writer."""
    reader: MagicMock = mocker.create_autospec(RecordReader, instance=True)
    reader.read.return_value = iter(
        [RawRecord(2, ROW_DATA), RawRecord(3, {**ROW_DATA, "score": "bad"})]
    )
    writer: MagicMock = mocker.create_autospec(ReportWriter, instance=True)
    writer.write.return_value = Path("out/report.json")
    return reader, writer


def test_run_reads_analyses_and_writes(mocks: Mocks) -> None:
    """The service reads the input, builds the report and writes it once."""
    reader, writer = mocks
    result = AnalyticsService(reader, writer, top_n=3).run("in.csv", "out/report.json")

    reader.read.assert_called_once_with("in.csv")
    writer.write.assert_called_once_with(result.report, "out/report.json")
    assert result.report["total_students"] == 1
    assert result.output_path == Path("out/report.json")
    assert not result.chart_paths  # no visualizer given


def test_run_draws_charts_next_to_the_report(
    mocks: Mocks, mocker: MockerFixture
) -> None:
    """With a visualizer, charts are drawn once into the report's folder."""
    reader, writer = mocks
    visualizer: MagicMock = mocker.create_autospec(ReportVisualizer, instance=True)
    visualizer.render.return_value = [Path("out/grade_distribution.png")]

    result = AnalyticsService(reader, writer, visualizer).run("in.csv", "out.json")

    visualizer.render.assert_called_once_with(result.report, Path("out"))
    assert result.chart_paths == [Path("out/grade_distribution.png")]


def test_run_returns_skipped_rows(mocks: Mocks) -> None:
    """Problems from bad rows are passed back to the caller."""
    result = AnalyticsService(*mocks).run("in.csv", "out.json")
    assert result.problems == [RowProblem(3, "score 'bad' is not a number")]


def test_reader_errors_stop_the_run(mocks: Mocks) -> None:
    """A file error from the reader propagates and nothing is written."""
    reader, writer = mocks
    reader.read.side_effect = DataFileNotFoundError("missing")
    with pytest.raises(DataFileNotFoundError):
        AnalyticsService(reader, writer).run("missing.csv", "out.json")
    writer.write.assert_not_called()
