import pytest
from decimal import Decimal

from api.constants import TIER_2_TERM, TIER_1_TERM, TIER_2_RATE, TIER_1_RATE
from api.rules.offer import compute_offer, compute_monthly_payment
from api.models import ApplicationStatus, ApplicationStatusReason


# ---- monthly payment tests ----
@pytest.mark.parametrize(
    "principal, rate, term, expected",
    [
        (Decimal("10000"), float("0"),   TIER_2_TERM, Decimal("416.67")),   # 0% APR
        (Decimal("25000"), float("20"),  TIER_2_TERM, Decimal("1272.40")),  # Spec tier-2 example
        (Decimal("25000"), float("10"),  TIER_1_TERM, Decimal("806.68")),   # Spec tier-1 example
    ],
)
def test_compute_monthly_payment(principal, rate, term, expected):
    assert compute_monthly_payment(principal, rate, term) == expected


# ---- decision rule tests ----
@pytest.mark.parametrize(
    "amount, open_credit_line, expected_status, expected_term, expected_rate",
    [
        # Rule 2: < 10 credit lines → 36mo at 10%
        (Decimal("10000"), 0,  ApplicationStatus.APPROVED.value, TIER_1_TERM, Decimal(TIER_1_RATE)),
        (Decimal("25000"), 9,  ApplicationStatus.APPROVED.value, TIER_1_TERM, Decimal(TIER_1_RATE)),

        # Rule 3: 10..50 credit lines → 24mo at 20%
        (Decimal("25000"), 10, ApplicationStatus.APPROVED.value, TIER_2_TERM, Decimal(TIER_2_RATE)),
        (Decimal("50000"), 50, ApplicationStatus.APPROVED.value, TIER_2_TERM, Decimal(TIER_2_RATE)),

        # requested amount boundary test cases
        (Decimal("10000"), 10, ApplicationStatus.APPROVED.value, TIER_2_TERM, Decimal(TIER_2_RATE)), # Min amount, Tier 2
        (Decimal("50000"), 9, ApplicationStatus.APPROVED.value, TIER_1_TERM, Decimal(TIER_1_RATE)), # Max amount, Tier 1
        (Decimal("10000.00"), 25, ApplicationStatus.APPROVED.value, TIER_2_TERM, Decimal(TIER_2_RATE)), # Exact min, mid tier 2
    ],
)
def test_compute_offer_approvals(amount, open_credit_line, expected_status, expected_term, expected_rate):
    decision = compute_offer(amount, open_credit_line)
    assert decision.status.value == expected_status
    assert decision.offer is not None
    assert decision.offer.term_months == expected_term
    assert decision.offer.interest_rate == expected_rate


@pytest.mark.parametrize(
    "amount, open_credit_lines, expected_reason",
    [
        (Decimal("9999.99"), 10, ApplicationStatusReason.REQUEST_AMOUNT_OUT_OF_BOUNDS),   # < $10k
        (Decimal("50000.01"), 10, ApplicationStatusReason.REQUEST_AMOUNT_OUT_OF_BOUNDS),  # > $50k
        (Decimal("25000"), 51, ApplicationStatusReason.CREDIT_LINES_OUT_OF_BOUNDS),     # > 50 open credit lines
    ],
)
def test_compute_offer_denials(amount, open_credit_lines, expected_reason):
    decision = compute_offer(amount, open_credit_lines)
    assert decision.status.value == ApplicationStatus.DENIED.value
    assert decision.offer is None
    assert decision.reason is not None
    assert decision.reason == expected_reason
