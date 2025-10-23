from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from api.constants import (
    MIN_LOAN_AMOUNT,
    MAX_LOAN_AMOUNT,
    MIN_CREDIT_LINES_TIER_1,
    MIN_CREDIT_LINES_TIER_2,
    MAX_CREDIT_LINES_TIER_2,
    TIER_1_TERM,
    TIER_1_RATE,
    TIER_2_TERM,
    TIER_2_RATE,
    MAX_CREDIT_LINES
)
from api.models import ApplicationStatus, ApplicationStatusReason

@dataclass
class Offer:
    total_amount: Decimal
    interest_rate: float
    term_months: int
    monthly_payment: Decimal


@dataclass
class LoanDecision:
    status: ApplicationStatus
    offer: Optional[Offer]
    reason: Optional[ApplicationStatusReason]


def compute_monthly_payment(principal: Decimal, interest_rate: float, term_months: int) -> Decimal:
    """
    Amortized monthly payment rounded to cents.

    Args:
    principal: loan amount (>= 0)
    interest_rate: e.g. 10 for 10% APR
    term_months: number of months (> 0)

    Returns:
        Monthly payment rounded to cents

    Formula:
      if r == 0: M = P / n
      else:      M = P * r / (1 - (1 + r)^(-n)),
      where r = (annual_rate_pct / 100) / 12
    """
    if term_months <= 0:
        raise ValueError("term_months must be > 0")

    principal = Decimal(principal)
    monthly_rate = (Decimal(interest_rate) / Decimal("100")) / Decimal("12")

    if monthly_rate == 0:
        monthly_payment = principal / term_months
    else:
        # M = P * r / (1 - (1 + r)^(-n))
        one = Decimal(1)
        denom = one - (one + monthly_rate) ** (Decimal(-term_months))
        monthly_payment = principal * monthly_rate / denom

    return monthly_payment.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def compute_offer(requested_amount: Decimal, open_credit_lines: int) -> LoanDecision:
    """
    Compute loan offer based on business rules.

    Args:
        requested_amount: loan amount (>= 0)
        open_credit_lines: number of credit lines (>= 0)

    Returns:
        LoanDecision
    """
    decision = LoanDecision(
        status=ApplicationStatus.DENIED,
        reason= ApplicationStatusReason.OTHER,
        offer=None
    )

    if open_credit_lines < 0:
        raise ValueError("open_credit_lines cannot be negative")

    # Rule 1: amount bounds
    if requested_amount < MIN_LOAN_AMOUNT or requested_amount > MAX_LOAN_AMOUNT:
        return LoanDecision(
            status=ApplicationStatus.DENIED,
            offer=None,
            reason=ApplicationStatusReason.REQUEST_AMOUNT_OUT_OF_BOUNDS
        )

    # Rule 4: >50 lines → deny
    if open_credit_lines > MAX_CREDIT_LINES:
        return LoanDecision(status=ApplicationStatus.DENIED,
                            offer=None,
                            reason=ApplicationStatusReason.CREDIT_LINES_OUT_OF_BOUNDS
                            )

    # Rule 2: <10 lines → 36mo at 10%
    if open_credit_lines < MIN_CREDIT_LINES_TIER_1:
        term = TIER_1_TERM
        rate = TIER_1_RATE
        monthly_payment = compute_monthly_payment(requested_amount, rate, term)
        return LoanDecision(
            status=ApplicationStatus.APPROVED,
            offer=Offer(requested_amount, rate, term, monthly_payment),
            reason=None
        )

    # Rule 3: 10..50 lines → 24mo at 20%
    if MIN_CREDIT_LINES_TIER_2 <= open_credit_lines <= MAX_CREDIT_LINES_TIER_2:
        term = TIER_2_TERM
        rate = TIER_2_RATE
        monthly_payment = compute_monthly_payment(requested_amount, rate, term)
        return LoanDecision(status=ApplicationStatus.APPROVED,
                            offer=Offer(requested_amount, rate, term, monthly_payment),
                            reason=None
                            )

    # fallback if none of the above are valid
    return decision
