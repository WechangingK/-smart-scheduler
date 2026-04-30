from flask import Flask
from app.models.base import init_db, SessionLocal


def create_app(config_path=None):
	app = Flask(__name__)
	app.config.from_object('config')

	if config_path:
		app.config.from_pyfile(config_path)

	init_db(app)

	# 初始化 CalDAV 存储目录
	from app.services.caldav_sync import init_caldav
	init_caldav()

	from app.routes.dashboard import bp as dash_bp
	from app.routes.tasks import bp as task_bp
	from app.routes.habits import bp as habit_bp
	from app.routes.schedule import bp as schedule_bp
	from app.routes.calendar import bp as calendar_bp
	from app.routes.settings import bp as settings_bp

	app.register_blueprint(dash_bp)
	app.register_blueprint(task_bp, url_prefix='/api/tasks')
	app.register_blueprint(habit_bp, url_prefix='/api/habits')
	app.register_blueprint(schedule_bp, url_prefix='/api/schedule')
	app.register_blueprint(calendar_bp, url_prefix='/api/calendar')
	app.register_blueprint(settings_bp, url_prefix='/api/settings')

	return app
