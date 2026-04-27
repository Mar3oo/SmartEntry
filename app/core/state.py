from typing import Optional, Dict, List
from pydantic import BaseModel

from app.core.contracts import PipelineInput, ExtractionResult


class PipelineState(BaseModel):
    # =========================
    # Core identity
    # =========================
    file_id: str
    input: PipelineInput

    # =========================
    # Processing stages
    # =========================
    extraction: Optional[ExtractionResult] = None
    structured_data: Optional[Dict] = None
    validated_data: Optional[Dict] = None
    mapped_data: Optional[Dict] = None

    # =========================
    # Errors
    # =========================
    errors: List[str] = []
