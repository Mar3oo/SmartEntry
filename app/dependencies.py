from app.core.orchestrator import Orchestrator
from app.agents.extraction_agent import ExtractionAgent
from app.agents.vision_agent import VisionAgent
from app.agents.validation_agent import ValidationAgent
from app.agents.mapping_agent import MappingAgent

from app.memory.sqlite_store import SQLiteStore
from app.memory.audit_log import AuditLog

# Services (IMPORTANT: wrappers aligned with contract)
from app.services.pdf.pdfplumber_service import PDFService
from app.services.ocr.easyocr_service import OCRService
from app.services.llm.groq_service import GroqService
from app.services.llm.gemini_service import GeminiService


def get_orchestrator():
    # =========================
    # Services
    # =========================
    pdf_service = PDFService()
    ocr_service = OCRService()
    groq_service = GroqService()
    gemini_service = GeminiService()

    # =========================
    # Agents
    # =========================
    extraction_agent = ExtractionAgent(
        pdf_service=pdf_service, ocr_service=ocr_service, llm_service=groq_service
    )

    vision_agent = VisionAgent(vision_service=gemini_service)
        pdf_service=pdf_service,
        ocr_service=ocr_service,
        llm_service=groq_service
    )

    vision_agent = VisionAgent(
        vision_service=gemini_service
    )

    validation_agent = ValidationAgent()

    mapping_agent = MappingAgent(
        profile_path="app/schemas/mapping_profiles/generic_excel.json"
    )

    # =========================
    # Memory / Logging
    # =========================
    store = SQLiteStore()
    audit_log = AuditLog()

    # =========================
    # Orchestrator
    # =========================
    orchestrator = Orchestrator(
        extraction_agent=extraction_agent,
        vision_agent=vision_agent,
        validation_agent=validation_agent,
        store=store,
        audit_log=audit_log,
    )

    return orchestrator, mapping_agent
        audit_log=audit_log
    )

    return orchestrator, mapping_agent
