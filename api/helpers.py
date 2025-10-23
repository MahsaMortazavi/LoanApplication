from decimal import Decimal
from random import randint
from select import select

from api.models import Borrower, Application
from api.rules.offer import compute_offer
from api.schemas import BorrowerRequest, ApplicationRequest

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.security import encrypt_ssn, hash_ssn


def find_or_create_borrower(db: Session, b: BorrowerRequest) -> Borrower:
    """
    Check if borrower exists by matching ALL fields.
    If exact match found, reuse, Otherwise create new borrower.
    This preserves historical borrower state for each application.
    """

    existing = db.execute(
        select(Borrower).where(
            Borrower.first_name == b.first_name,
            Borrower.last_name == b.last_name,
            Borrower.email == b.email,
            Borrower.phone == b.phone,
            Borrower.ssn_hash == hash_ssn(b.ssn),
            Borrower.address_street == b.address_street,
            Borrower.city == b.city,
            Borrower.state == b.state,
            Borrower.zip_code == b.zip_code,
        )
    ).scalar_one_or_none()

    if existing:
        return existing

    new_borrower = Borrower(
        first_name=b.first_name,
        last_name=b.last_name,
        email=b.email,
        phone=b.phone,
        ssn_encrypted=encrypt_ssn(b.ssn),
        ssn_hash=hash_ssn(b.ssn),
        address_street=b.address_street,
        city=b.city,
        state=b.state,
        zip_code=b.zip_code,
    )
    db.add(new_borrower)
    db.flush()
    return new_borrower


def create_application(db: Session, request: ApplicationRequest) -> Application:
    """
    Create application with credit check performed at application time.
    """
    borrower = find_or_create_borrower(db, request.borrower)

    # Credit check happens per application
    open_credit_lines = randint(0, 100)

    # Calculate offer based on application's open credit lines and request amount
    loan_decision = compute_offer(
        requested_amount=request.requested_amount,
        open_credit_lines=open_credit_lines
    )

    application_record = Application(
            borrower_id=borrower.id,
            requested_amount=Decimal(request.requested_amount),
            application_status=loan_decision.status,
            reason=loan_decision.reason,
            open_credit_lines=open_credit_lines,
            # Offer fields (nullable if denied)
            interest_rate=(
                Decimal(str(loan_decision.offer.interest_rate))
                if loan_decision.offer else None
            ),
            term_months=(loan_decision.offer.term_months if loan_decision.offer else None),
            monthly_payment=(
                Decimal(loan_decision.offer.monthly_payment)
                if loan_decision.offer else None
            ),
        )

    db.add(application_record)
    db.commit()
    db.refresh(application_record)
    return application_record