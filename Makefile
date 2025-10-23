.PHONY: setup gen-keys run-api run-web test clean

PYTHON := $(shell which python3)

# 1. Setup: create venv + install requirements
setup:
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	@echo "✅ Virtual environment created and requirements installed."

# Generate encryption keys for SSN
gen-keys:
	@python3 -c "import os, base64; print('SSN_ENC_KEY='+base64.urlsafe_b64encode(os.urandom(32)).decode())" > .env
	@python3 -c "import os, base64; print('SSN_HASH_KEY='+base64.urlsafe_b64encode(os.urandom(32)).decode())" >> .env
	@echo ".env file created with SSN_ENC_KEY and SSN_HASH_KEY"

# Run FastAPI backend
run-api:
	. .venv/bin/activate && uvicorn api.main:app --reload

# Run frontend (React via Vite)
run-web:
	cd web && npm install && npm run dev

# Run pytest tests
test:
	. .venv/bin/activate && pytest -v

# Clean generated files
clean:
	rm -rf .venv test_app.db .pytest_cache __pycache__ .coverage
	rm -f .env
