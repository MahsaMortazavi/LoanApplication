# Loan Application API

This is a minimal **FastAPI + React** project for a loan application flow.  
Backend handles loan decisions and encrypted SSN storage, frontend provides a simple form.
---

## Prerequisites
- **Python 3.11+**
- **Node.js + npm** (recommended to install via [nvm](https://github.com/nvm-sh/nvm))
- SQLite (default, built-in)

---

# Loan Application System

A full-stack loan application processing system with automated decision-making.

**Stack**: FastAPI (Python) + React (TypeScript) + SQLite

---

## Prerequisites

- **Python 3.11+**
- **Node.js 18+ + npm** (install via [nvm](https://github.com/nvm-sh/nvm))
- **Make** (pre-installed on macOS/Linux)
- SQLite (built-in)

---

## Quick Start with Makefile

### 1. Setup Backend
```bash
# Create virtual environment and install dependencies
make setup
```

### 2. Generate Encryption Keys
```bash
# Automatically generate SSN encryption keys and create .env file
make gen-keys
```

This creates a `.env` file with:
```env
SSN_ENC_KEY=<generated-key>
SSN_HASH_KEY=<generated-key>
```

### 3. Run Backend
```bash
# Start FastAPI server (with auto-reload)
make run-api
```

Backend runs at: http://127.0.0.1:8000  
API docs at: http://127.0.0.1:8000/docs

### 4. Run Frontend
```bash
# Install dependencies and start React dev server (new terminal)
make run-web
```

Frontend runs at: http://localhost:5173

### 5. Run Tests
```bash
# Backend tests
make test

# Frontend tests (from web/ directory)
cd web && npm test
```

### 6. Clean Up
```bash
# Remove venv, test files, and .env
make clean
```

---

## Manual Setup (Without Makefile)

### Backend Setup

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate encryption keys
python3 -c "import os, base64; print('SSN_ENC_KEY='+base64.urlsafe_b64encode(os.urandom(32)).decode())" > .env
python3 -c "import os, base64; print('SSN_HASH_KEY='+base64.urlsafe_b64encode(os.urandom(32)).decode())" >> .env

# Start API
uvicorn api.main:app --reload
```

### Frontend Setup

```bash
# Install Node.js via nvm
nvm install 20
nvm use 20

# Install dependencies and run
cd web
npm install
npm run dev
```

---

## Available Makefile Commands

| Command | Description |
|---------|-------------|
| `make setup` | Create venv and install Python dependencies |
| `make gen-keys` | Generate SSN encryption keys in `.env` file |
| `make run-api` | Start FastAPI backend server |
| `make run-web` | Install deps and start React frontend |
| `make test` | Run backend pytest tests |
| `make clean` | Remove venv, databases, and generated files |

---

## Running Tests

### Backend Tests
```bash
# Using Makefile
make test

# Or manually
source .venv/bin/activate
pytest -v

# With coverage
pytest --cov=api --cov-report=html
```

### Frontend Tests
```bash
cd web

# Watch mode (interactive)
npm test

# Run once
npm test -- --run

# With coverage
npm run test:coverage
```

---

## Project Structure

```
LoanApplication/
├── api/                    # Backend (FastAPI)
│   ├── rules/             # Business logic
│   ├── tests/             # Backend tests
│   ├── main.py            # API entry point
│   ├── models.py          # Database models
│   └── security.py        # SSN encryption
│
├── web/                   # Frontend (React + TypeScript)
│   ├── src/
│   │   ├── App.tsx        # Main component
│   │   ├── api.ts         # API client
│   │   └── app.test.tsx   # Frontend tests
│   └── package.json
│
├── Makefile               # Automation commands
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (generated)
└── app.db                 # SQLite database
```

---

## Key Features

- ✅ Automated loan approval/denial decisions
- ✅ Encrypted SSN storage (Fernet encryption)
- ✅ Real-time form validation
- ✅ Auto-formatting (phone, SSN, currency)
- ✅ SSN masking in UI (password field)
- ✅ Comprehensive test coverage
- ✅ RESTful API with OpenAPI docs

---

## Security

- **SSN Encryption**: Fernet symmetric encryption at rest
- **SSN Hashing**: SHA-256 for duplicate detection
- **SSN Masking**: Password field hides input in browser
- **Input Validation**: Frontend + Backend validation
- **CORS Protection**: Configured middleware
- **Memory Clearing**: SSN cleared from state after submission

---

## Tech Stack

**Backend**: FastAPI, SQLAlchemy, SQLite, Pydantic, Cryptography, Pytest  
**Frontend**: React, TypeScript, Vite, Vitest, Testing Library  
**Tools**: Make, nvm


## Future Improvements Be Production Ready
- Database: 
  - Switch to PostgreSQL
  - Add Alembic migrations
- Security:
  - Use KMS-managed keys for SSN encryption
- Network:
  - Serve API over HTTPS
- Observability:
  - Add structured logging
  - Improve error handling
- UX/UI:
  - Better form validation and inline errors
  - Improve result cards and Usability design
- Support Admin Tools to view/manage applications
