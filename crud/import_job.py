from sqlalchemy.orm import Session

from models.import_job import ImportJob


def create_import_job(
    db: Session,
    filename: str,
) -> ImportJob:
    import_job = ImportJob(filename=filename)

    db.add(import_job)
    db.commit()
    db.refresh(import_job)

    return import_job


def get_import_job(
    db: Session,
    import_job_id: int,
):
    return (
        db.query(ImportJob)
        .filter(ImportJob.id == import_job_id)
        .first()
    )