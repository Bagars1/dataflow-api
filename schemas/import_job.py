from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ImportJobResponse(BaseModel):
    id: int
    filename: str
    status: str
    processed_rows: int
    failed_rows: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ImportStatisticsResponse(BaseModel):
    total_imports: int
    successful_imports: int
    imports_with_errors: int
    total_processed_rows: int
    total_failed_rows: int

class ImportJobListResponse(BaseModel):
    id: int
    filename: str
    status: str
    processed_rows: int
    failed_rows: int