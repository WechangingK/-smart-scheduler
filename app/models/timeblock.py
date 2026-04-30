from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Date, Time, Boolean, DateTime, ForeignKey
from app.models.base import Base


class TimeBlock(Base):
	__tablename__ = 'time_blocks'

	id = Column(Integer, primary_key=True, autoincrement=True)
	date = Column(Date, nullable=False, index=True)
	task_id = Column(Integer, ForeignKey('tasks.id', ondelete='SET NULL'), nullable=True)
	title = Column(String(200), nullable=False)
	start_time = Column(Time, nullable=False)
	end_time = Column(Time, nullable=False)
	block_type = Column(String(20), default='task')  # task / break / habit / focus / fixed
	is_ai_suggested = Column(Boolean, default=True)
	is_accepted = Column(Boolean, default=False)
	google_event_id = Column(String(200), nullable=True)
	sort_order = Column(Integer, default=0)
	created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

	def to_dict(self):
		return {
			'id': self.id,
			'date': self.date.isoformat() if self.date else None,
			'task_id': self.task_id,
			'title': self.title,
			'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
			'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
			'block_type': self.block_type,
			'is_ai_suggested': self.is_ai_suggested,
			'is_accepted': self.is_accepted,
			'google_event_id': self.google_event_id,
			'sort_order': self.sort_order,
		}
