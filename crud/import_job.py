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


def get_all_import_jobs(
    db: Session,
):
    return db.query(ImportJob).all()



def get_import_statistics(
    db: Session,
):
    import_jobs = get_all_import_jobs(db)

    total_imports = len(import_jobs)
    successful_imports = 0
    imports_with_errors = 0
    total_processed_rows = 0
    total_failed_rows = 0

    for import_job in import_jobs:
        total_processed_rows += import_job.processed_rows
        total_failed_rows += import_job.failed_rows

        if import_job.failed_rows == 0:
            successful_imports += 1
        else:
            imports_with_errors += 1

    return {
        "total_imports": total_imports,
        "successful_imports": successful_imports,
        "imports_with_errors": imports_with_errors,
        "total_processed_rows": total_processed_rows,
        "total_failed_rows": total_failed_rows,
    }

