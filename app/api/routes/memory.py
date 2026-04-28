from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any

from app.memory.sqlite_store import SQLiteStore

router = APIRouter()

store = SQLiteStore()


class SaveDocumentRequest(BaseModel):
    file_id: str
    data: Dict[str, Any]


class CorrectionRequest(BaseModel):
    field: str
    wrong_value: str
    correct_value: str


@router.post("/save/")
def save_document(file_id: str, state: dict):
    try:
        store.save_document(file_id, state)

        return {"success": True, "data": "Full pipeline state saved", "errors": []}

    except Exception as e:
        return {"success": False, "data": None, "errors": [str(e)]}


@router.get("/{file_id}")
def get_document(file_id: str):
    try:
        doc = store.get_document(file_id)

        if not doc:
            return {"success": False, "data": None, "errors": ["Document not found"]}

        return {"success": True, "data": doc, "errors": []}

    except Exception as e:
        return {"success": False, "data": None, "errors": [str(e)]}


@router.post("/learn/")
def learn_correction(request: CorrectionRequest):
    key = f"value_correction:{request.field}:{request.wrong_value}"

    store.save_document(key, {"correct_value": request.correct_value})

    return {"success": True, "data": "Value correction learned", "errors": []}
