from app.schemas.responses import ProcessResponse
from app.schemas.base_schema import BaseDocumentSchema


def test_process_response():
    doc = BaseDocumentSchema()

    response = ProcessResponse(success=True, data=doc)

    assert response.success is True
