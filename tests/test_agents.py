from app.core.contracts import PipelineInput
from app.agents.mapping_agent import MappingAgent
from app.agents.base_agent import BaseAgent
from app.agents.extraction_agent import ExtractionAgent
from app.agents.validation_agent import ValidationAgent
from app.core.state import PipelineState
from app.agents.vision_agent import VisionAgent


class DummyAgent(BaseAgent):
    def __init__(self):
        super().__init__("dummy")

    def _run(self, state: PipelineState) -> PipelineState:
        state.structured_data = {"test": True}
        return state


def test_base_agent():
    state = PipelineState(
        file_id="1",
        input=PipelineInput(file_id="1", file_path="test.pdf", file_type="pdf"),
    )

    agent = DummyAgent()
    new_state = agent.run(state)

    assert new_state.structured_data["test"] is True


class MockPDFService:
    def extract(self, file_path):
        return {
            "text": "hello",
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


# def test_extraction_agent():
#     state = PipelineState(
#         file_id="1",
#         input=PipelineInput(file_id="1", file_path="test.pdf", file_type="pdf"),
#     )

#     agent = ExtractionAgent(pdf_service=MockPDFService(), ocr_service=MockOCRService())

#     new_state = agent.run(state)

#     assert new_state.extraction.text == "hello"


def test_validation_agent_valid():
    state = PipelineState(
        file_id="1",
        input=PipelineInput(file_id="1", file_path="test.pdf", file_type="pdf"),
        structured_data={
            "items": [{"quantity": 2, "unit_price": 10, "total_price": 20}],
            "totals": {"total": 20},
        },
    )

    agent = ValidationAgent()
    new_state = agent.run(state)

    assert new_state.validated_data is not None
    assert new_state.errors == []


def test_validation_agent_invalid():
    state = PipelineState(
        file_id="1",
        input=PipelineInput(file_id="1", file_path="test.pdf", file_type="pdf"),
        structured_data={
            "items": [{"quantity": 2, "unit_price": 10, "total_price": 50}],
            "totals": {"total": -10},
        },
    )

    agent = ValidationAgent()
    new_state = agent.run(state)

    assert len(new_state.errors) > 0


def test_mapping_agent():
    state = PipelineState(
        file_id="1",
        input=PipelineInput(file_id="1", file_path="test.pdf", file_type="pdf"),
        validated_data={
            "invoice": {"invoice_number": "INV-1", "invoice_date": "2024-01-01"},
            "totals": {"total": 100},
            "currency": "USD",
        },
    )

    agent = MappingAgent(profile_path="app/schemas/mapping_profiles/generic_excel.json")

    new_state = agent.run(state)

    assert new_state.mapped_data["invoice_number"] == "INV-1"
    assert new_state.mapped_data["total"] == 100


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


def test_extraction_agent():
    state = PipelineState(
        file_id="1",
        input=PipelineInput(file_id="1", file_path="test.pdf", file_type="pdf"),
    )

    agent = ExtractionAgent(
        pdf_service=MockPDFService(),
        ocr_service=MockOCRService(),
        llm_service=MockLLMService(),
    )

    new_state = agent.run(state)

    assert new_state.extraction is not None
    assert new_state.structured_data is not None


class MockVisionService:
    def extract(self, data):
        return {
            "supplier": None,
            "customer": None,
            "invoice": {"invoice_number": "IMG-1"},
            "items": [],
            "totals": {"total": 200},
            "currency": "USD",
            "extra_fields": {},
        }


def test_vision_agent():
    state = PipelineState(
        file_id="1",
        input=PipelineInput(file_id="1", file_path="image.jpg", file_type="image"),
    )

    agent = VisionAgent(vision_service=MockVisionService())

    new_state = agent.run(state)

    assert new_state.structured_data["invoice"]["invoice_number"] == "IMG-1"
