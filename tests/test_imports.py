import uuid

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def upload_file(content: str, filename: str | None = None):
    if filename is None:
        filename = f"test_{uuid.uuid4().hex}.csv"

    response = client.post(
        "/imports/",
        files={
            "file": (
                filename,
                content.encode("utf-8"),
                "text/csv",
            )
        },
    )

    return response


def test_upload_non_csv_file():
    response = client.post(
        "/imports/",
        files={
            "file": (
                "test.txt",
                b"hello",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Only CSV files are supported"
    }


def test_upload_csv_missing_column():
    csv_content = """name,email
John,john@gmail.com
"""

    response = upload_file(csv_content)

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Missing required columns: age"
    }


def test_upload_valid_csv():
    csv_content = """name,email,age
John,john@gmail.com,35
Anna,anna@gmail.com,28
Mike,mike@gmail.com,41
"""

    response = upload_file(csv_content)

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"
    assert data["processed_rows"] == 3
    assert data["failed_rows"] == 0


def test_upload_csv_with_invalid_rows():
    csv_content = """name,email,age
John,john@gmail.com,35
Mike,mike@gmail.com,abc
,wrong-email,25
"""

    response = upload_file(csv_content)

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"
    assert data["processed_rows"] == 1
    assert data["failed_rows"] == 2
    assert data["id"] is not None


def test_get_import():
    csv_content = """name,email,age
John,john@gmail.com,35
"""

    upload_response = upload_file(csv_content)

    assert upload_response.status_code == 200

    import_id = upload_response.json()["id"]

    response = client.get(f"/imports/{import_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == import_id
    assert data["filename"] is not None
    assert data["status"] == "completed"


def test_get_import_not_found():
    response = client.get("/imports/2147483647")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Import not found"
    }


def test_get_import_errors():
    csv_content = """name,email,age
John,john@gmail.com,35
Mike,mike@gmail.com,abc
,wrong-email,25
"""

    upload_response = upload_file(csv_content)

    assert upload_response.status_code == 200

    import_id = upload_response.json()["id"]

    response = client.get(f"/imports/{import_id}/errors")

    assert response.status_code == 200

    errors = response.json()

    assert len(errors) == 3

    assert {
        "row_number": 3,
        "field": "age",
        "message": "Age must be an integer",
    } in errors

    assert {
        "row_number": 4,
        "field": "name",
        "message": "Name is required",
    } in errors

    assert {
        "row_number": 4,
        "field": "email",
        "message": "Invalid email",
    } in errors


def test_get_import_errors_empty():
    csv_content = """name,email,age
John,john@gmail.com,35
"""

    upload_response = upload_file(csv_content)

    assert upload_response.status_code == 200

    import_id = upload_response.json()["id"]

    response = client.get(f"/imports/{import_id}/errors")

    assert response.status_code == 200
    assert response.json() == []

def test_get_import_statistics():
    valid_csv = """name,email,age
John,john@gmail.com,35
Anna,anna@gmail.com,28
"""

    invalid_csv = """name,email,age
John,john@gmail.com,35
Mike,mike@gmail.com,abc
"""

    response_1 = upload_file(valid_csv)
    response_2 = upload_file(invalid_csv)

    assert response_1.status_code == 200
    assert response_2.status_code == 200

    response = client.get("/imports/statistics")

    assert response.status_code == 200

    data = response.json()

    assert data["total_imports"] >= 2
    assert data["successful_imports"] >= 1
    assert data["imports_with_errors"] >= 1
    assert data["total_processed_rows"] >= 3
    assert data["total_failed_rows"] >= 1


def test_get_imports_with_errors():
    valid_csv = """name,email,age
John,john@gmail.com,35
"""

    invalid_csv = """name,email,age
John,john@gmail.com,35
Mike,mike@gmail.com,abc
"""

    valid_response = upload_file(valid_csv)
    invalid_response = upload_file(invalid_csv)

    assert valid_response.status_code == 200
    assert invalid_response.status_code == 200

    invalid_import_id = invalid_response.json()["id"]

    response = client.get("/imports/with-errors")

    assert response.status_code == 200

    imports = response.json()

    assert any(
        import_job["id"] == invalid_import_id
        for import_job in imports
    )

    assert all(
        import_job["failed_rows"] > 0
        for import_job in imports
    )