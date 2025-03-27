from sqlalchemy import Integer, String, DateTime, func, ForeignKey, Float
from base import Base
from sqlalchemy.sql.functions import now
from sqlalchemy.orm import mapped_column

class Quiz(Base):
    __tablename__ = "quizzes"
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(50), nullable=False)
    description = mapped_column(String(255), nullable=False)
    time_limit = mapped_column(Integer, nullable=False)
    timestamp = mapped_column(String(255), nullable=False)
    date_created = mapped_column(DateTime, default=func.now(), nullable=False)
    trace_id = mapped_column(String(255), nullable=False)


    def __init__(self, name, description, time_limit, timestamp, trace_id):
        self.name = name
        self.description = description
        self.time_limit = time_limit
        self.timestamp = timestamp
        self.trace_id = trace_id


    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "time_limit": self.time_limit,
            "timestamp": self.timestamp,
            "trace_id": self.trace_id
        }