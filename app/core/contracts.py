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
from app.schemas.base_schema import BaseDocumentSchema


# =========================================================
# 🔹 1. INPUT CLASSIFICATION
# =========================================================

InputType = Literal["pdf", "scanned_pdf", "image"]


def classify_input(file_path: str) -> InputType:
    """
    Decide the type of input file.

    Returns:
        "pdf"          → clean digital PDF (Path A)
        "scanned_pdf"  → PDF with images (Path B)
        "image"        → photo / noisy input (Path C)
    """
    ...


# =========================================================
# 🔹 2. PIPELINE OUTPUT → AGENTS INPUT
# =========================================================


class ExtractionInput(TypedDict):
    """
    This is the ONLY thing the pipeline sends to agents.
    """

    text: str
    source_type: Literal["pdf", "ocr", "image"]
    metadata: Optional[Dict[str, Any]]  # optional debug info


# =========================================================
# 🔹 3. PDF SERVICES
# =========================================================


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from clean PDF (pdfplumber).

    Path A
    """
    ...


def extract_images_from_pdf(file_path: str) -> List[str]:
    """
    Convert scanned PDF into images (PyMuPDF).

    Returns:
        List of image file paths
    """
    ...


# =========================================================
# 🔹 4. OCR SERVICE
# =========================================================


def extract_text_from_image(image_path: str) -> str:
    """
    Extract raw text from image using OCR (EasyOCR).
    """
    ...


# =========================================================
# 🔹 5. IMAGE PREPROCESSING (OPTIONAL)
# =========================================================


def preprocess_image(image_path: str) -> str:
    """
    Apply OpenCV preprocessing (denoise, threshold, etc.)

    Returns:
        Path to processed image
    """
    ...


# =========================================================
# 🔹 6. LLM SERVICES
# =========================================================


def groq_extract(text: str, prompt: str) -> Dict[str, Any]:
    """
    Send text to Groq (LLaMA) and return structured JSON.

    Used by:
        - extraction_agent
        - validation_agent
        - mapping_agent
    """
    ...


def gemini_extract(image_path: str, prompt: str) -> Dict[str, Any]:
    """
    Send image to Gemini Vision model and return structured JSON.

    Used by:
        - vision_agent
    """
    ...


# =========================================================
# 🔹 7. AGENTS INTERFACE
# =========================================================


def extract_document(data: ExtractionInput) -> BaseDocumentSchema:
    """
    Main extraction entry point.

    Behavior:
        if source_type == "pdf" or "ocr":
            → use extraction_agent (Groq)
        if source_type == "image":
            → use vision_agent (Gemini)

    Returns:
        BaseDocumentSchema
    """
    ...


def validate_document(doc: BaseDocumentSchema) -> BaseDocumentSchema:
    """
    Clean and validate extracted data.
    """
    ...


def map_document(doc: BaseDocumentSchema, target_schema: str) -> Dict[str, Any]:
    """
    Convert base schema → company-specific schema.
    """
    ...


# =========================================================
# 🔹 8. FINAL OUTPUT (FOR UI / EXPORT)
# =========================================================


class FinalOutput(TypedDict):
    """
    What the system returns to frontend / API.
    """

    data: Dict[str, Any]
    confidence_score: Optional[float]
    warnings: Optional[List[str]]
