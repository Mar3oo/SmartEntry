from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from app.schemas.base_schema import BaseDocumentSchema


# =========================
# BASE RESPONSE
# =========================


class BaseResponse(BaseModel):
    success: bool
    errors: List[str] = []
    meta: Optional[Dict[str, Any]] = None


# =========================
# UPLOAD RESPONSE
# =========================


class UploadResponse(BaseResponse):
    file_id: str
    file_path: str


# =========================
# PROCESS RESPONSE
# =========================


class ProcessResponse(BaseResponse):
    data: Optional[BaseDocumentSchema] = None


# =========================
# SCHEMA RESPONSE
# =========================


class SchemaResponse(BaseResponse):
    schema_definition: Dict[str, Any]
