from app.schemas.base_schema import BaseDocumentSchema


from app.schemas.company_schema import CompanySchema


def test_base_schema():
    doc = BaseDocumentSchema(
        supplier={"name": "ABC Corp"},
        invoice={"invoice_number": "INV-001"},
        items=[{"description": "Item A", "quantity": 2, "unit_price": 10}],
        totals={"total": 20},
    )

    assert doc.supplier.name == "ABC Corp"
    assert doc.items[0].quantity == 2


def test_company_schema():
    schema = CompanySchema(
        company_id="company_1",
        required_fields=["invoice.invoice_number", "totals.total"],
        default_currency="USD",
    )

    assert schema.company_id == "company_1"
    assert "invoice.invoice_number" in schema.required_fields
