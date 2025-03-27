from sqlalchemy import Integer, String, DateTime, func, ForeignKey, Float
from base import Base
from sqlalchemy.sql.functions import now
from sqlalchemy.orm import mapped_column
from Quiz import Quiz

class Question(Base):
    __tablename__ = "questions"
    id = mapped_column(Integer, primary_key=True)
    exam_id = mapped_column(Integer, ForeignKey(Quiz.id), nullable=False)
    text = mapped_column(String(255), nullable=False)
    order = mapped_column(Integer, nullable=False)
    correct_answer = mapped_column(String(255), nullable=False)
    score = mapped_column(Float, nullable=False)
    timestamp = mapped_column(String(255), nullable=False)
    date_created = mapped_column(DateTime, default=func.now(), nullable=False)
    trace_id = mapped_column(String(255), nullable=False)

    def __init__(self, exam_id, text, order, correct_answer, score, timestamp, trace_id):
        self.exam_id = exam_id
        self.text = text
        self.order = order
        self.correct_answer = correct_answer
        self.score = score
        self.timestamp = timestamp
        self.trace_id = trace_id


    def to_dict(self):
        return {
            "id": self.id,
            "exam_id": self.exam_id,
            "text": self.text,
            "order": self.order,
            "correct_answer": self.correct_answer,
            "score": self.score,
            "timestamp": self.timestamp,
            "trace_id": self.trace_id
        }
