"""
Business rules and constants for loan application processing.
"""
from decimal import Decimal

# Loan amount limits
MIN_LOAN_AMOUNT = Decimal("10000")
MAX_LOAN_AMOUNT = Decimal("50000")

# Credit line thresholds
# NOTE: Tier 1 and Tier 2 minimums both start at 10 today,
# but are defined separately for clarity and future flexibility.

MIN_CREDIT_LINES_TIER_1 = 10

MIN_CREDIT_LINES_TIER_2 = 10
MAX_CREDIT_LINES_TIER_2 = 50

MAX_CREDIT_LINES = 50

# Tier 1: < 10 credit lines
TIER_1_TERM = 36
TIER_1_RATE = 10.0

# Tier 2: 10-50 credit lines
TIER_2_TERM = 24
TIER_2_RATE = 20.0