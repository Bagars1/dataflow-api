from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from crud.import_error import get_import_errors

from crud.import_job import (
    create_import_job,
    get_import_job,
    get_import_statistics,
)

from database.database import get_db
from schemas.import_error import ImportErrorResponse
from schemas.import_job import ImportJobResponse, ImportStatisticsResponse
from services.file_processor import process_import


router = APIRouter(prefix="/imports", tags=["Imports"])


@router.post("/", response_model=ImportJobResponse)
def create_import(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    if Path(file.filename).suffix.lower() != ".csv":
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported",
        )

    safe_filename = Path(file.filename).name
    file_path = Path("uploads") / safe_filename

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    import_job = create_import_job(db, safe_filename)

    try:
        process_import(
            db=db,
            import_job=import_job,
            file_path=str(file_path),
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    return import_job


@router.get(
    "/statistics",
    response_model=ImportStatisticsResponse,
)
def read_import_statistics(
    db: Session = Depends(get_db),
):
    return get_import_statistics(db)




@router.get(
    "/{import_id}/errors",
    response_model=list[ImportErrorResponse],
)
def read_import_errors(
    import_id: int,
    db: Session = Depends(get_db),
):
    return get_import_errors(db, import_id)


@router.get(
    "/{import_id}",
    response_model=ImportJobResponse,
)
def read_import(
    import_id: int,
    db: Session = Depends(get_db),
):
    import_job = get_import_job(db, import_id)

    if not import_job:
        raise HTTPException(
            status_code=404,
            detail="Import not found",
        )

    return import_job