from datetime import datetime, timezone, date
from sqlalchemy import Column, Integer, String, Date, Boolean, Float, Text, DateTime, UniqueConstraint
from app.models.base import Base


class HabitRecord(Base):
	__tablename__ = 'habit_records'
	__table_args__ = (
		UniqueConstraint('name', 'date', name='uq_habit_name_date'),
	)

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(100), nullable=False, index=True)
	date = Column(Date, nullable=False, default=lambda: date.today())
	completed = Column(Boolean, default=False)
	value = Column(Float, nullable=True)
	notes = Column(Text, nullable=True)
	created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

	def to_dict(self):
		return {
			'id': self.id,
			'name': self.name,
			'date': self.date.isoformat() if self.date else None,
			'completed': self.completed,
			'value': self.value,
			'notes': self.notes,
			'created_at': self.created_at.isoformat() if self.created_at else None,
		}
