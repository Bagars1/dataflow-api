from sqlalchemy import Column, ForeignKey, Integer, String

from database.database import Base


class ImportError(Base):
    __tablename__ = "import_errors"

    id = Column(Integer, primary_key=True, index=True)
    import_job_id = Column(Integer, ForeignKey("import_jobs.id"), nullable=False)
    row_number = Column(Integer, nullable=False)
    field = Column(String, nullable=False)
    message = Column(String, nullable=False)