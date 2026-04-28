from app.core.pipeline import Pipeline
from app.core.contracts import PipelineInput
from app.core.state import PipelineState
from app.memory.sqlite_store import SQLiteStore
from app.memory.audit_log import AuditLog
from app.memory.embeddings import EmbeddingService
from app.memory.chroma_client import ChromaClient


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

        # AI Memory Components
        self.embedding_service = EmbeddingService()
        self.vector_db = ChromaClient()

        # inject into store so pipeline can use it
        self.store.embedding_service = self.embedding_service
        self.store.vector_db = self.vector_db

    def run(self, input_data: PipelineInput, mapping_agent) -> PipelineState:

        # =========================
        # STEP 0 — FILE MEMORY CHECK
        # =========================
        try:
            saved = self.store.get_document(input_data.file_id)

            if saved:
                print("🔁 Using saved pipeline state for:", input_data.file_id)

                state = PipelineState(
                    file_id=input_data.file_id,
                    input=input_data,
                )

                state.structured_data = saved.get("structured_data")
                state.validated_data = saved.get("validated_data")
                state.mapped_data = saved.get("mapped_data")

                return state

        except Exception as e:
            print("Memory read failed:", str(e))

        # =========================
        # Choose agent
        # =========================
        if input_data.file_type == "pdf":
            primary_agent = self.extraction_agent
        elif input_data.file_type == "image":
            primary_agent = self.vision_agent
        else:
            raise ValueError(f"Unsupported file type: {input_data.file_type}")

        # =========================
        # Build pipeline
        # =========================
        pipeline = Pipeline(
            extraction_agent=primary_agent,
            validation_agent=self.validation_agent,
            mapping_agent=mapping_agent,
        )

        # =========================
        # Execute pipeline
        # =========================
        state = pipeline.run(input_data)

        # ❗ Stop if errors
        if state.errors:
            return state

        # =========================
        # 🔥 VECTOR MEMORY SAVE (semantic)
        # =========================
        try:
            if state.extraction and state.extraction.text:
                text = state.extraction.text[:1000]

                embedding = self.embedding_service.embed(text)

                if embedding:
                    supplier_name = None
                    if state.structured_data:
                        supplier_name = (
                            state.structured_data.get("supplier", {}) or {}
                        ).get("name")

                    self.vector_db.add(
                        doc_id=state.file_id,
                        embedding=embedding,
                        metadata={"supplier": supplier_name},
                    )

        except Exception as e:
            print("Embedding save failed:", str(e))

        # =========================
        # 🔥 SUPPLIER MEMORY LEARNING
        # =========================
        try:
            if state.structured_data:
                supplier = state.structured_data.get("supplier", {}) or {}
                supplier_name = supplier.get("name")

                if supplier_name:
                    supplier_key = f"supplier::{supplier_name.lower().strip()}"

                    self.store.save_document(
                        supplier_key,
                        {
                            "structured_data": state.structured_data,
                            "mapped_data": state.mapped_data,
                        },
                    )

                    print(f"🧠 Learned supplier pattern: {supplier_name}")

        except Exception as e:
            print("Supplier memory save failed:", str(e))

        # =========================
        # 🔥 SAVE FULL PIPELINE STATE
        # =========================
        try:
            self.store.save_document(
                file_id=state.file_id,
                data={
                    "structured_data": state.structured_data,
                    "validated_data": state.validated_data,
                    "mapped_data": state.mapped_data,
                },
            )
        except Exception as e:
            state.errors.append(f"Memory save failed: {str(e)}")

        # =========================
        # Audit logging
        # =========================
        status = "success" if not state.errors else "failed"

        try:
            self.audit_log.log(
                file_id=state.file_id,
                status=status,
                errors=state.errors,
            )
        except Exception:
            pass

        return state
