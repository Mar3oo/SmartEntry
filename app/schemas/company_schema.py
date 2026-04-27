from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CompanySchema(BaseModel):
    # =========================
    # Identity
    # =========================
    company_id: str

    # =========================
    # Required fields (dot paths)
    # =========================
    required_fields: List[str] = Field(
        default_factory=list, description="Fields that must be present in document"
    )

    # =========================
    # Default values
    # =========================
    default_currency: Optional[str] = None

    # =========================
    # Custom fields
    # =========================
    custom_fields: Dict[str, Any] = Field(
        default_factory=dict, description="Extra fields specific to this company"
    )
