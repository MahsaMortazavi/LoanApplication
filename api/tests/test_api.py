import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from decimal import Decimal
from api.schemas import BorrowerRequest, ApplicationRequest

TEST_DATABASE_URL = "sqlite:///./test_app.db"


# helper functions
def create_valid_borrower(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="555-123-4567",
        ssn="123-45-6789",
        address_street="123 Main St",
        city="New York",
        state="NY",
        zip_code="10001"
) -> BorrowerRequest:
    """Create a valid BorrowerRequest for testing happy paths."""
    return BorrowerRequest(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        ssn=ssn,
        address_street=address_street,
        city=city,
        state=state,
        zip_code=zip_code
    )


def create_borrower_dict(**overrides) -> dict:
    """Create borrower dict with defaults, for testing edge cases and invalid data."""
    defaults = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "555-123-4567",
        "ssn": "123-45-6789",
        "address_street": "123 Main St",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001"
    }
    defaults.update(overrides)
    return defaults

# Validation tests

@pytest.mark.parametrize("invalid_data,expected_field", [
    ({"email": "not-an-email"}, "email"),
    ({"email": ""}, "email"),
    ({"ssn": "123"}, "ssn"),  # Too short
    ({"ssn": "abc-de-fghi"}, "ssn"),  # Invalid format
    ({"phone": "123"}, "phone"),  # Too short
    ({"state": "X"}, "state"),  # Too short
    ({"state": "XXX"}, "state"),  # Too long
])
def test_invalid_borrower_data(client, test_db, invalid_data, expected_field):
    """Test that invalid borrower data is rejected."""
    borrower = create_borrower_dict(**invalid_data)
    payload = {
        "borrower": borrower,
        "requested_amount": 25000
    }

    response = client.post("/applications", json=payload)
    assert response.status_code == 422
    # Verify the error mentions the problematic field
    error_detail = str(response.json())
    assert expected_field in error_detail.lower()


    def test_missing_required_field(client):
        payload = {
            "borrower": create_borrower_dict(email=None),  # Missing required field
            "requested_amount": 25000
        }
        response = client.post("/applications", json=payload)
        assert response.status_code == 422