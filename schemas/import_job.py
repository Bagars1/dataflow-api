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