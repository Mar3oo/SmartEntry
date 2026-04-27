from app.memory.sqlite_store import SQLiteStore

from app.memory.correction_store import CorrectionStore

from app.memory.schema_memory import SchemaMemory


def test_sqlite_store():
    store = SQLiteStore(":memory:")

    store.save_document(file_id="123", raw_text="hello", structured_data={"total": 100})

    result = store.get_document("123")

    assert result is not None
    assert result["raw_text"] == "hello"
    assert result["structured_data"]["total"] == 100


def test_correction_store():
    store = CorrectionStore(":memory:")

    store.save_correction(
        file_id="1", original_data={"total": 100}, corrected_data={"total": 120}
    )

    result = store.get_correction("1")

    assert result is not None
    assert result["corrected_data"]["total"] == 120


def test_schema_memory():
    store = SchemaMemory(":memory:")

    schema = {"invoice_number": "invoice.invoice_number", "total": "totals.total"}

    store.save_schema("company_1", schema)

    result = store.get_schema("company_1")

    assert result is not None
    assert result["total"] == "totals.total"
