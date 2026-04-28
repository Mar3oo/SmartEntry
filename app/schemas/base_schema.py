from typing import List, Optional
from pydantic import BaseModel, Field


# =========================
# CORE ENTITIES
# =========================


class CompanyInfo(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    tax_id: Optional[str] = None


class InvoiceInfo(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None


class LineItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None


class Totals(BaseModel):
    # New structure
    net_total: Optional[float] = None
    vat: Optional[float] = None
    gross_total: Optional[float] = None

    # Keep legacy compatibility (optional but smart)
    # subtotal: Optional[float] = None
    # tax: Optional[float] = None
    # total: Optional[float] = None


# =========================
# MAIN DOCUMENT SCHEMA
# =========================


class BaseDocumentSchema(BaseModel):
    supplier: Optional[CompanyInfo] = None
    customer: Optional[CompanyInfo] = None

    invoice: Optional[InvoiceInfo] = None

    items: List[LineItem] = []
    totals: Optional[Totals] = None

    currency: Optional[str] = None

    # Allow extension later
    extra_fields: Optional[dict] = Field(
        default_factory=dict, description="Custom fields per company"
    )
