import sys
from pathlib import Path
from unittest.mock import Mock, patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = PROJECT_ROOT / "frontend"
sys.path.insert(0, str(FRONTEND_ROOT))

from api_client import APIError, SmartEntryAPI, normalize_profile
from state import diff_records, rows_from_response_data


def make_response(status_code=200, body=None, headers=None, content=b""):
    response = Mock()
    response.status_code = status_code
    response.headers = headers or {}
    response.content = content
    response.text = str(body or "")
    response.json.return_value = body or {}
    return response


def test_save_corrections_sends_documented_payload():
    client = SmartEntryAPI(base_url="http://api.test")
    response = make_response(body={"success": True, "errors": []})

    with patch("requests.post", return_value=response) as post:
        result = client.save_corrections("file-1", [{"invoice": "INV-1"}])

    assert result["success"] is True
    assert post.call_args.kwargs["json"] == {
        "file_id": "file-1",
        "data": {"mapped_data": [{"invoice": "INV-1"}]},
    }


def test_process_document_sends_profile_and_file_context():
    client = SmartEntryAPI(base_url="http://api.test")
    response = make_response(body={"success": True, "data": [], "errors": []})

    with patch("requests.post", return_value=response) as post:
        result = client.process_document(
            file_id="file-1",
            file_path="data/uploads/invoice.pdf",
            file_type="pdf",
            profile="odoo",
        )

    assert result["success"] is True
    assert post.call_args.args[0] == "http://api.test/process"
    assert post.call_args.kwargs["json"] == {
        "file_id": "file-1",
        "file_path": "data/uploads/invoice.pdf",
        "file_type": "pdf",
        "profile": "odoo.json",
    }


def test_export_excel_returns_download_content_and_filename():
    client = SmartEntryAPI(base_url="http://api.test")
    response = make_response(
        headers={
            "content-type": (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
            "content-disposition": 'attachment; filename="invoice.xlsx"',
        },
        content=b"xlsx",
    )

    with patch("requests.post", return_value=response):
        content, filename = client.export_excel(
            file_id="file-1",
            file_path="data/uploads/invoice.pdf",
            file_type="pdf",
            profile="sap",
        )

    assert content == b"xlsx"
    assert filename == "invoice.xlsx"


def test_export_excel_raises_clean_error_for_backend_failure():
    client = SmartEntryAPI(base_url="http://api.test")
    response = make_response(
        headers={"content-type": "application/json"},
        body={"success": False, "errors": ["No data to export"]},
    )

    with patch("requests.post", return_value=response):
        try:
            client.export_excel(
                file_id="file-1",
                file_path="data/uploads/invoice.pdf",
                file_type="pdf",
            )
        except APIError as exc:
            assert str(exc) == "Excel export failed."
            assert exc.details == ["No data to export"]
        else:
            raise AssertionError("Expected APIError")


def test_save_corrections_falls_back_to_trailing_slash_backend():
    client = SmartEntryAPI(base_url="http://api.test")
    method_not_allowed = make_response(
        status_code=405,
        body={"detail": "Method Not Allowed"},
    )
    success = make_response(body={"success": True, "errors": []})

    with patch("requests.post", side_effect=[method_not_allowed, success]) as post:
        result = client.save_corrections("file-1", [{"invoice": "INV-1"}])

    assert result["success"] is True
    assert post.call_args_list[0].args[0] == "http://api.test/memory/save"
    assert post.call_args_list[1].args[0] == "http://api.test/memory/save/"


def test_save_corrections_falls_back_to_legacy_query_payload():
    client = SmartEntryAPI(base_url="http://api.test")
    validation_error = make_response(status_code=422, body={"detail": "bad body"})
    success = make_response(body={"success": True, "errors": []})

    with patch("requests.post", side_effect=[validation_error, success]) as post:
        result = client.save_corrections("file-1", [{"invoice": "INV-1"}])

    assert result["success"] is True
    assert post.call_args_list[1].kwargs["params"] == {"file_id": "file-1"}
    assert post.call_args_list[1].kwargs["json"] == {
        "mapped_data": [{"invoice": "INV-1"}]
    }


def test_rows_from_response_data_supports_mapped_rows_and_nested_invoices():
    mapped_rows = rows_from_response_data([{"invoice_number": "INV-1"}])
    nested_rows = rows_from_response_data(
        {
            "invoice": {"invoice_number": "INV-2"},
            "items": [{"description": "Widget", "quantity": 2}],
            "totals": {"total": 25},
            "currency": "USD",
        }
    )

    assert mapped_rows == [{"invoice_number": "INV-1"}]
    assert nested_rows == [
        {
            "currency": "USD",
            "invoice.invoice_number": "INV-2",
            "totals.total": 25,
            "description": "Widget",
            "quantity": 2,
        }
    ]


def test_edit_tracking_counts_changed_cells():
    changes = diff_records(
        [{"invoice_number": "INV-1", "total": 100}],
        [{"invoice_number": "INV-1", "total": 125}],
    )

    assert changes == [
        {
            "row": 1,
            "field": "total",
            "original": 100,
            "edited": 125,
        }
    ]


def test_profile_names_are_normalized_for_backend():
    assert normalize_profile("odoo") == "odoo.json"
    assert normalize_profile("sap.json") == "sap.json"
