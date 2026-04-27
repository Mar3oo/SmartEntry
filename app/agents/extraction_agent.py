from app.agents.base_agent import BaseAgent
from app.core.contracts import ExtractionResult
from app.schemas.base_schema import BaseDocumentSchema
from app.core.state import PipelineState


class ExtractionAgent(BaseAgent):
    def __init__(self, pdf_service, ocr_service, llm_service):
        super().__init__("extraction_agent")
        self.pdf_service = pdf_service
        self.ocr_service = ocr_service
        self.llm_service = llm_service

    def _run(self, state: PipelineState) -> PipelineState:
        file_path = state.input.file_path
        file_type = state.input.file_type

        # =========================
        # 1. Raw Extraction
        # =========================
        if file_type == "pdf":
            result = self.pdf_service.extract(file_path)
        elif file_type == "image":
            result = self.ocr_service.extract(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        state.extraction = ExtractionResult(**result)

        # =========================
        # 2. LLM Structuring
        # =========================
        try:
            structured = self.llm_service.extract(
                {"text": state.extraction.text, "blocks": state.extraction.blocks}
            )

            # Validate structure
            doc = BaseDocumentSchema(**structured)

            state.structured_data = doc.model_dump()

        except Exception as e:
            state.errors.append(f"LLM structuring failed: {str(e)}")

        return state
