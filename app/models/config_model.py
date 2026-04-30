from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.models.base import Base


class Config(Base):
	__tablename__ = 'configs'

	id = Column(Integer, primary_key=True, autoincrement=True)
	key = Column(String(100), unique=True, nullable=False)
	value = Column(Text, nullable=True)
	updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

	def to_dict(self):
		return {
			'id': self.id,
			'key': self.key,
			'value': self.value,
			'updated_at': self.updated_at.isoformat() if self.updated_at else None,
		}
