from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Time, Boolean, Float
from app.models.base import Base


class Task(Base):
	__tablename__ = 'tasks'

	id = Column(Integer, primary_key=True, autoincrement=True)
	title = Column(String(200), nullable=False)
	description = Column(Text, nullable=True)
	priority = Column(String(10), default='medium')  # low / medium / high
	status = Column(String(20), default='pending')  # pending / completed / cancelled
	category = Column(String(100), nullable=True, index=True)
	due_date = Column(DateTime, nullable=True, index=True)
	estimated_minutes = Column(Integer, nullable=True)
	actual_minutes = Column(Integer, nullable=True)
	energy_level = Column(String(10), nullable=True)  # low / medium / high
	preferred_time_start = Column(Time, nullable=True)
	preferred_time_end = Column(Time, nullable=True)
	is_recurring = Column(Boolean, default=False)
	recurrence_rule = Column(String(200), nullable=True)
	completed_at = Column(DateTime, nullable=True)
	created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
	updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

	def to_dict(self):
		return {
			'id': self.id,
			'title': self.title,
			'description': self.description,
			'priority': self.priority,
			'status': self.status,
			'category': self.category,
			'due_date': self.due_date.isoformat() if self.due_date else None,
			'estimated_minutes': self.estimated_minutes,
			'actual_minutes': self.actual_minutes,
			'energy_level': self.energy_level,
			'preferred_time_start': self.preferred_time_start.strftime('%H:%M') if self.preferred_time_start else None,
			'preferred_time_end': self.preferred_time_end.strftime('%H:%M') if self.preferred_time_end else None,
			'is_recurring': self.is_recurring,
			'recurrence_rule': self.recurrence_rule,
			'completed_at': self.completed_at.isoformat() if self.completed_at else None,
			'created_at': self.created_at.isoformat() if self.created_at else None,
			'updated_at': self.updated_at.isoformat() if self.updated_at else None,
		}
