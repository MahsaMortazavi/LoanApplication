from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session

from api.helpers import create_application
from api.models import Base, Application, ApplicationStatus
from api.schemas import ApplicationResponse, ApplicationRequest, OfferResponse
from pydantic import BaseModel, EmailStr

# Load vars from .env
load_dotenv()

# DB SETUP
DATABASE_URL = "sqlite:///./app.db"   # creates app.db in /api working dir
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# create tables
Base.metadata.create_all(bind=engine)

def get_db():
    """Database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API SETUP
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"ok": True}


@app.post("/applications", response_model=ApplicationResponse, status_code=201)
def post_application(payload: ApplicationRequest, db: Session = Depends(get_db)):
    """Submit a new application."""
    try:
        app_row: Application = create_application(db, payload)
        resp = ApplicationResponse(
            application_id=app_row.application_id,
            decision=app_row.application_status,
            open_credit_lines=app_row.open_credit_lines,
            offer=(
                OfferResponse(
                    total_amount=app_row.requested_amount,
                    interest_rate=app_row.interest_rate,
                    term_months=app_row.term_months,
                    monthly_payment=app_row.monthly_payment,
                )
                if app_row.application_status is ApplicationStatus.APPROVED
                else None
            ),
            reason=(app_row.reason if app_row.application_status is ApplicationStatus.DENIED else None),
        )
        return resp

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/applications/{application_id}", response_model=ApplicationResponse)
def get_application(application_id: str, db: Session = Depends(get_db)):
    """Retrieve an existing loan application by Application ID."""

    row = db.execute(
        select(Application).where(Application.application_id == application_id)
    ).scalar_one_or_none()

    if not row:
        raise HTTPException(status_code=404, detail="Application not found")

    resp = ApplicationResponse(
        application_id=row.application_id,
        decision=row.application_status,
        open_credit_lines=row.open_credit_lines,
        offer=(
            OfferResponse(
                total_amount=row.requested_amount,
                interest_rate=row.interest_rate,
                term_months=row.term_months,
                monthly_payment=row.monthly_payment,
            )
            if row.application_status is ApplicationStatus.APPROVED
            else None
        ),
        reason=(row.reason if row.application_status is ApplicationStatus.DENIED else None),
    )
    return resp
