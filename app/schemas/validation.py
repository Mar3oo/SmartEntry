from typing import List

from app.schemas.base_schema import BaseDocumentSchema


class ValidationError(Exception):
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__("Validation failed")


def validate_document(doc: BaseDocumentSchema) -> BaseDocumentSchema:
    errors = []

    # =========================
    # Validate totals (UPDATED)
    # =========================
    if doc.totals:
        if doc.totals.net_total is not None and doc.totals.net_total < 0:
            errors.append("Net total cannot be negative")

        if doc.totals.vat is not None and doc.totals.vat < 0:
            errors.append("VAT cannot be negative")

        if doc.totals.gross_total is not None and doc.totals.gross_total < 0:
            errors.append("Gross total cannot be negative")

    # =========================
    # Validate line items
    # =========================
    for idx, item in enumerate(doc.items):
        if item.quantity is not None and item.quantity < 0:
            errors.append(f"Item {idx}: quantity cannot be negative")

        if item.unit_price is not None and item.unit_price < 0:
            errors.append(f"Item {idx}: unit_price cannot be negative")

        if item.total_price is not None and item.total_price < 0:
            errors.append(f"Item {idx}: total_price cannot be negative")

        # consistency check
        if (
            item.quantity is not None
            and item.unit_price is not None
            and item.total_price is not None
        ):
            expected = round(item.quantity * item.unit_price, 2)

            if abs(expected - item.total_price) > 0.01:
                # FIX instead of fail
                item.total_price = expected

    # =========================
    # Auto-fix totals
    # =========================
    if doc.items:
        calculated = round(sum(i.total_price or 0 for i in doc.items), 2)

        if doc.totals:
            if doc.totals.net_total is None:
                doc.totals.net_total = calculated

            if doc.totals.gross_total is None and doc.totals.vat is not None:
                doc.totals.gross_total = round(doc.totals.net_total + doc.totals.vat, 2)

    # =========================
    # Final check
    # =========================
    if errors:
        raise ValidationError(errors)

    return doc
