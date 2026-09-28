import csv

from email_validator import EmailNotValidError, validate_email
from sqlalchemy.orm import Session

from models.import_error import ImportError
from models.import_job import ImportJob


REQUIRED_COLUMNS = {"name", "email", "age"}


def process_import(
    db: Session,
    import_job: ImportJob,
    file_path: str,
) -> ImportJob:

    import_job.status = "processing"
    db.commit()

    processed_rows = 0
    failed_rows = 0

    with open(
        file_path,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        columns = set(reader.fieldnames or [])

        missing_columns = REQUIRED_COLUMNS - columns

        if missing_columns:
            import_job.status = "failed"
            db.commit()

            raise ValueError(
                f"Missing required columns: {', '.join(sorted(missing_columns))}"
            )

        for row_number, row in enumerate(reader, start=2):

            row_has_error = False

            name = row.get("name", "").strip()
            email = row.get("email", "").strip()
            age = row.get("age", "").strip()

            # Проверяем name
            if not name:
                db.add(
                    ImportError(
                        import_job_id=import_job.id,
                        row_number=row_number,
                        field="name",
                        message="Name is required",
                    )
                )
                row_has_error = True

            # Проверяем email
            if not email:
                db.add(
                    ImportError(
                        import_job_id=import_job.id,
                        row_number=row_number,
                        field="email",
                        message="Email is required",
                    )
                )
                row_has_error = True

            else:
                try:
                    validate_email(
                        email,
                        check_deliverability=False,
                    )
                except EmailNotValidError:
                    db.add(
                        ImportError(
                            import_job_id=import_job.id,
                            row_number=row_number,
                            field="email",
                            message="Invalid email",
                        )
                    )
                    row_has_error = True

            # Проверяем age
            if not age.isdigit():
                db.add(
                    ImportError(
                        import_job_id=import_job.id,
                        row_number=row_number,
                        field="age",
                        message="Age must be an integer",
                    )
                )
                row_has_error = True

            if row_has_error:
                failed_rows += 1
            else:
                processed_rows += 1

    import_job.processed_rows = processed_rows
    import_job.failed_rows = failed_rows
    import_job.status = "completed"

    db.commit()
    db.refresh(import_job)

    return import_job