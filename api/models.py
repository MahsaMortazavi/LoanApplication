from typing import List
import enum
from sqlalchemy import String, Integer, Float, Text, DateTime, CheckConstraint, ForeignKey, Numeric, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from api.utils import generate_uuid

class Base(DeclarativeBase):
    pass

class ApplicationStatus(str, enum.Enum):
    APPROVED = "approved"
    DENIED = "denied"

    def __str__(self):
        return self.value


class ApplicationStatusReason(str, enum.Enum):
    REQUEST_AMOUNT_OUT_OF_BOUNDS = "Requested amount out of bounds (<10k or >50k)"
    CREDIT_LINES_OUT_OF_BOUNDS = "Credit lines greater than 50"
    OTHER = "Unable to compute offer"

    def __str__(self):
        return self.value


class Borrower(Base):
    __tablename__ = "borrowers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # for internal use only - no public exposure
    borrower_id: Mapped[str] = mapped_column(String(50), unique=True, index=True,
                                           default=lambda: generate_uuid(prefix="borrower"),
                                           nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)

    address_street: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)
    zip_code: Mapped[str] = mapped_column(String, nullable=False)

    ssn_encrypted: Mapped[str] = mapped_column(String, nullable=False)
    ssn_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)   # hex sha256 → 64 chars

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    applications: Mapped[List["Application"]] = relationship(
        back_populates="borrower"
    )


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # for internal use only - no public exposure
    application_id: Mapped[str] = mapped_column(String(50), unique=True, index=True,
                                           default=lambda: generate_uuid(prefix="application"),
                                           nullable=False)
    borrower_id: Mapped[int] = mapped_column(ForeignKey("borrowers.id"), nullable=False)
    open_credit_lines: Mapped[int] = mapped_column(Integer, nullable=False)

    requested_amount: Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)
    application_status: Mapped[ApplicationStatus] = mapped_column(Enum(ApplicationStatus),
                                                                  nullable=False)
    reason: Mapped[ApplicationStatusReason] = mapped_column(Enum(ApplicationStatusReason), nullable=True)
    interest_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    term_months: Mapped[int] = mapped_column(Integer, nullable=True)
    monthly_payment: Mapped[float] = mapped_column(Numeric(7, 2), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    borrower: Mapped["Borrower"] = relationship(back_populates="applications")

    __table_args__ = (
        CheckConstraint('term_months > 0 AND term_months <= 360', name='valid_term'),
        CheckConstraint('interest_rate >= 0 AND interest_rate <= 99.99', name='valid_interest_rate'),
        CheckConstraint('open_credit_lines >= 0 AND open_credit_lines <= 100', name='open_credit_lines_range'),
    )
