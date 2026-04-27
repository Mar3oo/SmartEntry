from app.core.pipeline import Pipeline
from app.core.contracts import PipelineInput
from app.core.state import PipelineState
from app.memory.sqlite_store import SQLiteStore
from app.memory.audit_log import AuditLog


class Orchestrator:
    def __init__(
        self,
        extraction_agent,
        vision_agent,
        validation_agent,
        store: SQLiteStore,
        audit_log: AuditLog,
    ):
        self.extraction_agent = extraction_agent
        self.vision_agent = vision_agent
        self.validation_agent = validation_agent
        self.store = store
        self.audit_log = audit_log

    def run(self, input_data: PipelineInput, mapping_agent) -> PipelineState:

        # =========================
        # Choose agent based on input
        # =========================
        if input_data.file_type == "pdf":
            primary_agent = self.extraction_agent
        elif input_data.file_type == "image":
            primary_agent = self.vision_agent
        else:
            raise ValueError(f"Unsupported file type: {input_data.file_type}")

        # =========================
        # Build pipeline dynamically
        # =========================
        pipeline = Pipeline(
            extraction_agent=primary_agent,  # dynamic
            validation_agent=self.validation_agent,
            mapping_agent=mapping_agent,
        )

        # =========================
        # Execute
        # =========================
        state = pipeline.run(input_data)

        # =========================
        # Save to memory
        # =========================
        try:
            if state.validated_data:
                raw_text = state.extraction.text if state.extraction else ""

                self.store.save_document(
                    file_id=state.file_id,
                    raw_text=raw_text,
                    structured_data=state.validated_data,
                )
        except Exception as e:
            state.errors.append(f"Memory save failed: {str(e)}")

        # =========================
        # Audit logging
        # =========================
        status = "success" if not state.errors else "failed"

        try:
            self.audit_log.log(
                file_id=state.file_id, status=status, errors=state.errors
            )
        except Exception:
            pass  # logging should never break system

        return state
