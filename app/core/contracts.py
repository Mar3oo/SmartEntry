"""
contracts.py

This file defines ALL shared interfaces between:
- Pipeline (services + orchestrator)
- AI Agents
- LLM services

⚠️ RULES:
- Do NOT change this file without team agreement
- All modules must respect these interfaces exactly
"""

from typing import TypedDict, Literal, List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.base_schema import BaseDocumentSchema


# =========================
# 1. INPUT CONTRACT
# =========================


class PipelineInput(BaseModel):
    file_id: str
    file_path: str
    file_type: Literal["pdf", "image"]


# =========================
# 2. EXTRACTION CONTRACT
# =========================


class TextBlock(BaseModel):
    text: str
    bbox: Optional[List[float]] = Field(
        default=None, description="Bounding box [x1, y1, x2, y2]"
    )
    page: Optional[int] = None


class ExtractionMetadata(BaseModel):
    source: Literal["pdf", "ocr"]
    pages: Optional[int] = None


class ExtractionResult(BaseModel):
    text: str
    blocks: List[TextBlock] = []
    metadata: ExtractionMetadata


# =========================
# 3. AGENT FLOW CONTRACT
# =========================


class AgentState(BaseModel):
    file_id: str

    # raw input
    input: PipelineInput

    # extracted content
    extraction: Optional[ExtractionResult] = None

    # intermediate outputs
    structured_data: Optional[dict] = None
    validated_data: Optional[dict] = None
    mapped_data: Optional[dict] = None

    # errors
    errors: List[str] = []
