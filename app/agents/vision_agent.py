from app.agents.base_agent import BaseAgent
from app.core.state import PipelineState
from app.schemas.base_schema import BaseDocumentSchema


class VisionAgent(BaseAgent):
    def __init__(self, vision_service):
        super().__init__("vision_agent")
        self.vision_service = vision_service

    def _run(self, state: PipelineState) -> PipelineState:
        file_path = state.input.file_path

        try:
            result = self.vision_service.extract(
                {
                    "file_path": file_path,
                    "ocr_text": None,  # optional for now
                }
            )

            # Validate structure
            doc = BaseDocumentSchema(**result)

            state.structured_data = doc.model_dump()

        except Exception as e:
            state.errors.append(f"Vision extraction failed: {str(e)}")

        return state
