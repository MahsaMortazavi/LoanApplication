from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, constr, Field

from api.models import ApplicationStatus


class BorrowerRequest(BaseModel):
    first_name: constr(min_length=1)
    last_name: constr(min_length=1)
    email: EmailStr
    phone: constr(min_length=7, max_length=25)
    ssn: constr(min_length=9, max_length=11, pattern=r'^\d{9}$|^\d{3}-\d{2}-\d{4}$')  # display only
    address_street: constr(min_length=1)
    city: constr(min_length=1)
    state: constr(min_length=2, max_length=2)
    zip_code: constr(min_length=1)


class ApplicationRequest(BaseModel):
    # Borrower fields (we create or reuse borrower)
    borrower: BorrowerRequest
    requested_amount: Decimal = Field(gt=0, decimal_places=2)


class OfferResponse(BaseModel):
    total_amount: Decimal
    interest_rate: float
    term_months: int
    monthly_payment: Decimal

    model_config = {"from_attributes": True}

class ApplicationResponse(BaseModel):
    application_id: str
    decision: ApplicationStatus
    open_credit_lines: int
    offer: Optional[OfferResponse] = None
    reason: Optional[str] = None

    model_config = {"from_attributes": True}