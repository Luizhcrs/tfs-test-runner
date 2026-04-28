from pathlib import Path
import pytest
from openpyxl import Workbook

from tfs_test_runner.parse import parse_xlsx, _norm_header, _find_columns, _clean


def test_norm_header():
    assert _norm_header("  Work Item ID ") == "work item id"
    assert _norm_header(None) == ""
    assert _norm_header("Step  Action") == "step action"


def test_find_columns_required():
    headers = ["ID", "Work Item Type", "Title", "Step Action"]
    cols = _find_columns(headers)
    assert cols == {"id": 0, "type": 1, "title": 2, "action": 3}


def test_find_columns_missing_raises():
    with pytest.raises(ValueError, match="missing required columns"):
        _find_columns(["id", "title"])


def test_clean_normalizes():
    assert _clean("  hello\xa0world  ") == "hello world"
    assert _clean(None) == ""
    assert _clean(123) == "123"


def test_parse_xlsx_minimal(tmp_path: Path):
    wb = Workbook()
    ws = wb.active
    ws.append(["ID", "Work Item Type", "Title", "Test Step",
               "Step Action", "Step Expected", "Area Path", "Assigned To", "State"])
    ws.append([1, "Test Case", "TC One", None, None, None, "Area\\X", "user@x", "Design"])
    ws.append([None, None, None, "1", "Click button", "Button clicked", None, None, None])
    ws.append([None, None, None, "2", "Verify result", "Pass", None, None, None])
    ws.append([2, "Test Case", "TC Two", None, None, None, "Area\\Y", None, "Design"])
    ws.append([None, None, None, "1", "Login", "Logged in", None, None, None])
    f = tmp_path / "in.xlsx"
    wb.save(f)

    cases = parse_xlsx(f)
    assert len(cases) == 2
    assert cases[0]["id"] == "1"
    assert cases[0]["title"] == "TC One"
    assert len(cases[0]["steps"]) == 2
    assert cases[0]["steps"][0]["action"] == "Click button"
    assert cases[1]["id"] == "2"
    assert len(cases[1]["steps"]) == 1


def test_parse_xlsx_skips_blank_rows(tmp_path: Path):
    wb = Workbook()
    ws = wb.active
    ws.append(["ID", "Work Item Type", "Title", "Step Action"])
    ws.append([1, "Test Case", "TC", None])
    ws.append([None, None, None, None])  # blank
    ws.append([None, None, None, "Step here"])
    f = tmp_path / "in.xlsx"
    wb.save(f)

    cases = parse_xlsx(f)
    assert len(cases) == 1
    assert len(cases[0]["steps"]) == 1
