from fastapi import APIRouter, Query, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional

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


@router.post("/save")
@router.post("/save/")
async def save_document(
    request: Request,
    file_id: Optional[str] = Query(default=None),
):
    try:
        body = await request.json()

        if isinstance(body, dict) and "file_id" in body and "data" in body:
            save_request = SaveDocumentRequest.model_validate(body)
            file_id = save_request.file_id
            state = save_request.data
        elif file_id:
            # Backward compatible shape: /memory/save?file_id=... with the state
            # object as the JSON body.
            state = body
        else:
            return {
                "success": False,
                "data": None,
                "errors": ["file_id and data are required"],
            }

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
