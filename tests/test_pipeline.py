from app.core.pipeline import Pipeline
from app.core.contracts import PipelineInput

from app.core.orchestrator import Orchestrator


# Import agents
from app.agents.extraction_agent import ExtractionAgent
from app.agents.validation_agent import ValidationAgent
from app.agents.mapping_agent import MappingAgent

from app.agents.vision_agent import VisionAgent
from app.memory.sqlite_store import SQLiteStore

from app.memory.audit_log import AuditLog


# Mock services
class MockPDFService:
    def extract(self, file_path):
        return {
            "text": "invoice text",
            "blocks": [],
            "metadata": {"source": "pdf", "pages": 1},
        }


class MockOCRService:
    def extract(self, file_path):
        return {
            "text": "image text",
            "blocks": [],
            "metadata": {"source": "ocr", "pages": 1},
        }


class MockLLMService:
    def extract(self, data):
        return {
            "supplier": None,
            "customer": None,
            "invoice": {"invoice_number": "INV-1"},
            "items": [],
            "totals": {"total": 100},
            "currency": "USD",
            "extra_fields": {},
        }


def test_pipeline():

    extraction_agent = ExtractionAgent(
        pdf_service=MockPDFService(),
        ocr_service=MockOCRService(),
        llm_service=MockLLMService(),
    )

    validation_agent = ValidationAgent()

    mapping_agent = MappingAgent(
        profile_path="app/schemas/mapping_profiles/generic_excel.json"
    )

    pipeline = Pipeline(extraction_agent, validation_agent, mapping_agent)

    input_data = PipelineInput(file_id="1", file_path="test.pdf", file_type="pdf")

    state = pipeline.run(input_data)

    assert state.extraction is not None
    assert state.validated_data is not None
    assert state.mapped_data is not None


class MockVisionService:
    def extract(self, data):
        return {
            "supplier": None,
            "customer": None,
            "invoice": {"invoice_number": "IMG-123"},
            "items": [],
            "totals": {"total": 300},
            "currency": "USD",
            "extra_fields": {},
        }


def test_orchestrator_image_path():
    extraction_agent = ExtractionAgent(
        pdf_service=MockPDFService(),
        ocr_service=MockOCRService(),
        llm_service=MockLLMService(),
    )

    vision_agent = VisionAgent(vision_service=MockVisionService())

    validation_agent = ValidationAgent()

    mapping_agent = MappingAgent(
        profile_path="app/schemas/mapping_profiles/generic_excel.json"
    )

    store = SQLiteStore(":memory:")
    audit_log = AuditLog(":memory:")

    orchestrator = Orchestrator(
        extraction_agent, vision_agent, validation_agent, store, audit_log
    )

    input_data = PipelineInput(file_id="1", file_path="image.jpg", file_type="image")

    state = orchestrator.run(input_data, mapping_agent)

    saved = store.get_document("1")

    logs = audit_log.get_logs()

    assert len(logs) == 1
    assert logs[0][0] == "1"  #

    assert saved is not None

    assert saved["structured_data"]["totals"]["total"] == 300

    assert state.structured_data["invoice"]["invoice_number"] == "IMG-123"
