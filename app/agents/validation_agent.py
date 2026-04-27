from app.agents.base_agent import BaseAgent
from app.schemas.base_schema import BaseDocumentSchema
from app.schemas.validation import validate_document, ValidationError
from app.core.state import PipelineState


class ValidationAgent(BaseAgent):
    def __init__(self):
        super().__init__("validation_agent")

    def _run(self, state: PipelineState) -> PipelineState:
        if not state.structured_data:
            state.errors.append("No structured data to validate")
            return state

        try:
            # Convert to schema
            doc = BaseDocumentSchema(**state.structured_data)

            # Validate
            validated = validate_document(doc)

            # Store result
            state.validated_data = validated.model_dump()

        except ValidationError as e:
            state.errors.extend(e.errors)

        except Exception as e:
            state.errors.append(f"Validation error: {str(e)}")

        return state
