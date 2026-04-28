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
        # 🔥 SIMILARITY REUSE (SAFE)
        # =========================
        try:
            if state.extraction and state.extraction.text:
                text = state.extraction.text[:1000]

                embedding = (
                    self.mapping_agent.store.embedding_service.embed(text)
                    if hasattr(self.mapping_agent.store, "embedding_service")
                    else None
                )

                if embedding:
                    results = (
                        self.mapping_agent.store.vector_db.query(embedding, top_k=1)
                        if hasattr(self.mapping_agent.store, "vector_db")
                        else None
                    )

                    if results and results.get("ids") and results["ids"][0]:
                        similar_id = results["ids"][0][0]

                        print(f"🧠 Similar document found: {similar_id}")

                        similar_doc = self.mapping_agent.store.get_document(similar_id)

                        if similar_doc:
                            # 🔥 SAFE REUSE — ONLY fill missing values
                            current = state.structured_data or {}
                            previous = similar_doc.get("structured_data", {})

                            # Example: currency fallback
                            if not current.get("currency") and previous.get("currency"):
                                current["currency"] = previous["currency"]
                                print("⚡ Reused currency from similar doc")

                            # Example: totals fallback
                            if not current.get("totals") and previous.get("totals"):
                                current["totals"] = previous["totals"]
                                print("⚡ Reused totals from similar doc")

                            state.structured_data = current

        except Exception as e:
            print("Similarity reuse failed:", str(e))
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
