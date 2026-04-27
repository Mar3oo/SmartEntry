import pytest
from app.schemas.base_schema import BaseDocumentSchema
from app.schemas.validation import validate_document, ValidationError


def test_valid_document():
    doc = BaseDocumentSchema(
        items=[{"quantity": 2, "unit_price": 10, "total_price": 20}],
        totals={"total": 20},
    )

    validated = validate_document(doc)
    assert validated.totals.total == 20


def test_invalid_document():
    doc = BaseDocumentSchema(
        items=[{"quantity": 2, "unit_price": 10, "total_price": 50}],
        totals={"total": -10},
    )

    with pytest.raises(ValidationError):
        validate_document(doc)
