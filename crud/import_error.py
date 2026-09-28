from sqlalchemy.orm import Session

from models.import_error import ImportError


def get_import_errors(
    db: Session,
    import_job_id: int,
):
    return (
        db.query(ImportError)
        .filter(ImportError.import_job_id == import_job_id)
        .all()
    )