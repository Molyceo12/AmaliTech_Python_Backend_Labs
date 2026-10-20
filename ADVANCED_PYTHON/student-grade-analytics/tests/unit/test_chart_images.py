"""Tests for the matplotlib PNG charts."""

from pathlib import Path

import pytest
from matplotlib.figure import Figure
from pytest_mock import MockerFixture

from grade_analytics.analytics import build_report
from grade_analytics.exceptions import ReportWriteError
from grade_analytics.models import Course, GradeReport, LoadedData, Student
from grade_analytics.visualization import MatplotlibVisualizer, ReportVisualizer
from tests.helpers import CHART_FILES

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


@pytest.fixture(name="report")
def fixture_report(sample_students: list[Student]) -> GradeReport:
    """A real report built from the sample students."""
    data = LoadedData(sample_students, {"CS101": Course("CS101", "Intro", 4)}, [])
    return build_report(data)


def test_visualizer_implements_interface() -> None:
    """MatplotlibVisualizer is a ReportVisualizer."""
    assert isinstance(MatplotlibVisualizer(), ReportVisualizer)


def test_every_chart_is_saved_as_png(report: GradeReport, tmp_path: Path) -> None:
    """All five charts are written, in order, as real PNG files."""
    written = MatplotlibVisualizer().render(report, tmp_path / "charts")
    assert [path.name for path in written] == CHART_FILES
    for path in written:
        assert path.read_bytes().startswith(PNG_SIGNATURE)


def test_empty_report_draws_nothing(tmp_path: Path) -> None:
    """Charts without data are skipped instead of drawing empty plots."""
    empty = build_report(LoadedData([], {}, []))
    assert not MatplotlibVisualizer().render(empty, tmp_path)
    assert not list(tmp_path.iterdir())


def test_save_error_raises_report_write_error(
    report: GradeReport, tmp_path: Path, mocker: MockerFixture
) -> None:
    """An OS error while saving a chart raises ReportWriteError."""
    mocker.patch.object(Figure, "savefig", side_effect=OSError("disk full"))
    with pytest.raises(ReportWriteError, match="disk full"):
        MatplotlibVisualizer().render(report, tmp_path)
