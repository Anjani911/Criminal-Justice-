# AI Crime Intelligence Platform Backend

FastAPI backend for the Karnataka State Crime Records Bureau (SCRB) AI Crime Intelligence Platform. This application acts as the backend intelligence layer over the FIR database and handles analytical processing, criminal network analytics, and AI-assisted investigation querying.

## Technology Stack
* **Python**: 3.12+
* **Web Framework**: FastAPI
* **ORM**: SQLAlchemy 2.0
* **Database**: PostgreSQL (defaults to SQLite for local development)
* **Migrations**: Alembic
* **Data Science & Graphs**: Pandas, Scikit-learn, NetworkX
* **AI API**: Google Gemini (generativeai SDK)

---

## Folder Structure
```
backend/
├── app/
│   ├── ai/            # LLM query processing, intent detection, SQL generation
│   ├── analytics/     # SQL analytics engine and statistical queries
│   ├── api/           # REST endpoints and controllers
│   ├── auth/          # Authentication & Authorization (JWT, Role-Based Access)
│   ├── database/      # Connection configurations and session setup
│   ├── models/        # SQLAlchemy ORM models
│   ├── schemas/       # Pydantic validation schemas
│   ├── services/      # Business logic services (Repository pattern consumer)
│   ├── utils/         # Helper functions, config loaders, loggers
│   └── main.py        # Entrypoint for FastAPI app
├── requirements.txt   # Dependencies list
├── .env.example       # Template environment variables
├── .env               # Development environment variables (ignored in version control)
└── README.md          # Technical documentation
```

---

## Getting Started

### 1. Prerequisites
Ensure you have Python 3.12+ installed on your system.

### 2. Install Dependencies
It is highly recommended to run the project in a virtual environment:
```bash
python -m venv venv
# On Windows PowerShell
.\venv\Scripts\Activate.ps1
# On Linux/macOS
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Environment Setup
Copy the template `.env.example` file and configure it:
```bash
cp .env.example .env
```
Ensure that the `DATABASE_URL` is set to `sqlite:///./crime_intelligence.db` for rapid local testing or pointing to your PostgreSQL instance.

### 4. Run the Backend Server
Start the development server with Uvicorn:
```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Once running, you can access:
* **API Home**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **API Documentation (ReDoc)**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
