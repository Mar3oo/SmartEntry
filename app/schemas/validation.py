from typing import List

from app.schemas.base_schema import BaseDocumentSchema


class ValidationError(Exception):
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__("Validation failed")


def validate_document(doc: BaseDocumentSchema) -> BaseDocumentSchema:
    errors = []

    # =========================
    # Validate totals
    # =========================
    if doc.totals:
        if doc.totals.total is not None and doc.totals.total < 0:
            errors.append("Total amount cannot be negative")

        if doc.totals.subtotal is not None and doc.totals.subtotal < 0:
            errors.append("Subtotal cannot be negative")

        if doc.totals.tax is not None and doc.totals.tax < 0:
            errors.append("Tax cannot be negative")

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
            expected = item.quantity * item.unit_price
            if abs(expected - item.total_price) > 0.01:
                errors.append(f"Item {idx}: total_price mismatch (expected {expected})")

    # =========================
    # Final check
    # =========================
    if errors:
        raise ValidationError(errors)

    return doc
