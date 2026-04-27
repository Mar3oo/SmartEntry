from app.core.contracts import PipelineInput
from app.core.state import PipelineState


class Pipeline:
    def __init__(self, extraction_agent, validation_agent, mapping_agent):
        self.extraction_agent = extraction_agent
        self.validation_agent = validation_agent
        self.mapping_agent = mapping_agent

    def run(self, input_data: PipelineInput) -> PipelineState:
        state = PipelineState(file_id=input_data.file_id, input=input_data)

        # =========================
        # Step 1 — Extraction + Structuring
        # =========================
        state = self.extraction_agent.run(state)

        if state.errors:
            return state

        # =========================
        # Step 2 — Validation
        # =========================
        state = self.validation_agent.run(state)

        if state.errors:
            return state

        # =========================
        # Step 3 — Mapping
        # =========================
        state = self.mapping_agent.run(state)

        return state
