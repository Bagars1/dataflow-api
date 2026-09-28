# DataFlow API

A FastAPI service for CSV file import, data validation, error tracking, and import status management.

## Features

* CSV file upload
* Import job creation and status tracking
* CSV column validation
* Row-level data validation
* Email validation
* Import error storage
* Import result retrieval
* Import error retrieval
* PostgreSQL database
* SQLAlchemy ORM
* Alembic database migrations
* Pytest test suite

## Tech Stack

* Python 3.13
* FastAPI
* SQLAlchemy
* PostgreSQL
* Alembic
* Pydantic
* Pytest

## Project Structure

```text
dataflow_api/
│
├── alembic/
│   └── versions/
│
├── crud/
│   ├── import_error.py
│   └── import_job.py
│
├── database/
│   └── database.py
│
├── models/
│   ├── import_error.py
│   └── import_job.py
│
├── routers/
│   └── imports.py
│
├── schemas/
│   ├── import_error.py
│   └── import_job.py
│
├── services/
│   └── file_processor.py
│
├── tests/
│   └── test_imports.py
│
├── uploads/
├── .env
├── .gitignore
├── alembic.ini
├── main.py
├── requirements.txt
└── README.md
```

## Setup

### 1. Clone the repository

```bash
git clone git@github.com:Bagars1/dataflow-api.git
cd dataflow-api
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/dataflow
```

Update the PostgreSQL username, password, host, port, and database name for your environment.

## Database Setup

Make sure PostgreSQL is running and the `dataflow` database exists.

Apply Alembic migrations:

```powershell
alembic upgrade head
```

To check whether the database schema matches the SQLAlchemy models:

```powershell
alembic check
```

To create a new migration after changing the models:

```powershell
alembic revision --autogenerate -m "Describe your change"
```

## Run the Application

Start the development server:

```powershell
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

OpenAPI schema:

```text
http://127.0.0.1:8000/openapi.json
```

## API Endpoints

### Upload and process a CSV

```text
POST /imports/
```

The endpoint:

1. Accepts a CSV file
2. Saves the file to the uploads directory
3. Creates an import job
4. Validates the CSV structure
5. Validates row data
6. Stores validation errors
7. Returns the import result

Example response:

```json
{
  "id": 7,
  "filename": "test_data.csv",
  "status": "completed",
  "processed_rows": 2,
  "failed_rows": 2,
  "created_at": "2026-09-28T10:33:10.758231"
}
```

### Get an import

```text
GET /imports/{import_id}
```

Returns the status and summary of a specific import.

### Get import errors

```text
GET /imports/{import_id}/errors
```

Returns validation errors for a specific import.

Example:

```json
[
  {
    "row_number": 4,
    "field": "age",
    "message": "Age must be an integer"
  },
  {
    "row_number": 5,
    "field": "name",
    "message": "Name is required"
  },
  {
    "row_number": 5,
    "field": "email",
    "message": "Invalid email"
  }
]
```

## CSV Validation

The imported CSV must contain these columns:

```text
name
email
age
```

The current validation rules are:

* `name` is required
* `email` is required and must have a valid format
* `age` must be an integer

Only `.csv` files are accepted.

## Error Handling

The API returns `400 Bad Request` for invalid input such as:

### Unsupported file type

```json
{
  "detail": "Only CSV files are supported"
}
```

### Missing required column

```json
{
  "detail": "Missing required columns: age"
}
```

The API returns `404 Not Found` when an import does not exist:

```json
{
  "detail": "Import not found"
}
```

## Running Tests

Run the complete test suite with:

```powershell
python -m pytest
```

The project currently contains tests covering:

* unsupported file type
* missing CSV columns
* valid CSV imports
* invalid CSV rows
* retrieving an import
* missing import
* retrieving import errors
* imports without errors

## Database Models

### ImportJob

Stores information about an import:

* ID
* filename
* status
* processed row count
* failed row count
* creation timestamp

### ImportError

Stores validation errors for an import:

* import job ID
* row number
* field
* error message

## Development Notes

Uploaded files are stored locally in the `uploads/` directory.

The `.env`, virtual environment, uploaded files, and other local development artifacts are excluded from Git using `.gitignore`.

## License

This project is for educational and portfolio purposes.
