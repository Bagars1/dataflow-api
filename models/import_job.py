from datetime import datetime, UTC

from sqlalchemy import Column, DateTime, Integer, String

from database.database import Base


class ImportJob(Base):
    __tablename__ = "import_jobs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    status = Column(String, nullable=False, default="queued")
    processed_rows = Column(Integer, default=0)
    failed_rows = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))