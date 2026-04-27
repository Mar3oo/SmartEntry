from app.core.contracts import PipelineInput, ExtractionResult, ExtractionMetadata


def test_pipeline_input():
    data = PipelineInput(
        file_id="123", file_path="data/uploads/test.pdf", file_type="pdf"
    )
    assert data.file_type == "pdf"


def test_extraction_result():
    result = ExtractionResult(
        text="Hello world", metadata=ExtractionMetadata(source="pdf", pages=1)
    )
    assert result.text == "Hello world"
