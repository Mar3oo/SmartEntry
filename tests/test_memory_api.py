from fastapi.testclient import TestClient

from app.api.routes import memory
from app.memory.sqlite_store import SQLiteStore


def create_memory_test_client() -> TestClient:
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(memory.router, prefix="/memory")
    return TestClient(app)


def test_memory_save_accepts_documented_payload(monkeypatch):
    store = SQLiteStore(":memory:")
    monkeypatch.setattr(memory, "store", store)

    client = create_memory_test_client()
    payload = {
        "file_id": "invoice-1",
        "data": {
            "mapped_data": [
                {"invoice_number": "INV-1", "total": 125},
            ],
        },
    }

    response = client.post("/memory/save", json=payload)

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert store.get_document("invoice-1") == payload["data"]

    get_response = client.get("/memory/invoice-1")

    assert get_response.status_code == 200
    assert get_response.json()["success"] is True
    assert get_response.json()["data"] == payload["data"]


def test_memory_save_keeps_legacy_query_payload(monkeypatch):
    store = SQLiteStore(":memory:")
    monkeypatch.setattr(memory, "store", store)

    client = create_memory_test_client()
    payload = {"mapped_data": [{"invoice_number": "INV-2"}]}

    response = client.post("/memory/save", params={"file_id": "invoice-2"}, json=payload)

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert store.get_document("invoice-2") == payload


def test_memory_save_returns_clean_error_for_missing_payload(monkeypatch):
    store = SQLiteStore(":memory:")
    monkeypatch.setattr(memory, "store", store)

    client = create_memory_test_client()
    response = client.post("/memory/save", json={"data": {"mapped_data": []}})

    assert response.status_code == 200
    assert response.json() == {
        "success": False,
        "data": None,
        "errors": ["file_id and data are required"],
    }
