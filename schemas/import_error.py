from pydantic import BaseModel


class ImportErrorResponse(BaseModel):
    row_number: int
    field: str
    message: str