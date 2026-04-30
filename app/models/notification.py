from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.models.base import Base


class NotificationLog(Base):
	__tablename__ = 'notification_logs'

	id = Column(Integer, primary_key=True, autoincrement=True)
	type = Column(String(20), nullable=False)  # email / system
	title = Column(String(200), nullable=False)
	message = Column(Text, nullable=True)
	recipient = Column(String(200), nullable=True)
	status = Column(String(20), default='pending')  # pending / sent / failed
	error_message = Column(Text, nullable=True)
	scheduled_for = Column(DateTime, nullable=True)
	sent_at = Column(DateTime, nullable=True)
	created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

	def to_dict(self):
		return {
			'id': self.id,
			'type': self.type,
			'title': self.title,
			'message': self.message,
			'recipient': self.recipient,
			'status': self.status,
			'error_message': self.error_message,
			'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
			'sent_at': self.sent_at.isoformat() if self.sent_at else None,
			'created_at': self.created_at.isoformat() if self.created_at else None,
		}
