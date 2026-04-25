from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date


class Party(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    tax_id: Optional[str] = None


class LineItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None
    product_code: Optional[str] = None


class PaymentInfo(BaseModel):
    method: Optional[str] = None  # cash, card, transfer
    bank_name: Optional[str] = None
    iban: Optional[str] = None
    swift: Optional[str] = None


class BaseDocumentSchema(BaseModel):
    # -------- Document Info --------
    document_type: Optional[str] = Field(
        None, description="invoice, receipt, report, etc."
    )
    document_id: Optional[str] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    currency: Optional[str] = None

    # -------- Parties --------
    seller: Optional[Party] = None
    buyer: Optional[Party] = None

    # -------- Financials --------
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    discount: Optional[float] = None
    total: Optional[float] = None

    # -------- Items --------
    items: Optional[List[LineItem]] = None

    # -------- Payment --------
    payment_info: Optional[PaymentInfo] = None

    # -------- Metadata --------
    notes: Optional[str] = None
    raw_text: Optional[str] = None  # useful for debugging
    confidence_score: Optional[float] = None

    # -------- Flexible Catch-All --------
    extra_fields: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Any fields not covered by schema"
    )
