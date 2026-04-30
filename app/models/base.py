from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


class Base(DeclarativeBase):
	pass


engine = None
SessionLocal = None


def init_db(app):
	global engine, SessionLocal
	engine = create_engine(
		app.config['DATABASE_URL'],
		connect_args={'check_same_thread': False} if 'sqlite' in app.config['DATABASE_URL'] else {},
		echo=app.config.get('DEBUG', False)
	)
	SessionLocal = sessionmaker(bind=engine)
	Base.metadata.create_all(bind=engine)
