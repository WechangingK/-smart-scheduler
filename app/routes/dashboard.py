from flask import Blueprint, render_template
from app.models.base import SessionLocal
from app.models.task import Task
from app.models.habit import HabitRecord
from app.models.timeblock import TimeBlock
from datetime import date, datetime, timedelta

bp = Blueprint('dashboard', __name__)


@bp.route('/')
def index():
	today = date.today()
	db = SessionLocal()
	try:
		pending_tasks = db.query(Task).filter(
			Task.status == 'pending'
		).order_by(
			Task.priority == 'high',
			Task.due_date.is_(None),
			Task.due_date
		).limit(10).all()

		today_blocks = db.query(TimeBlock).filter(
			TimeBlock.date == today
		).order_by(TimeBlock.start_time).all()

		today_habits = db.query(HabitRecord).filter(
			HabitRecord.date == today
		).all()

		habit_names = list(set(h.name for h in today_habits)) if today_habits else []

		stats = {
			'pending_count': db.query(Task).filter(Task.status == 'pending').count(),
			'today_completed': db.query(Task).filter(
				Task.status == 'completed',
				Task.completed_at >= today.isoformat()
			).count(),
			'habit_streak': _calc_streak(db),
		}
	finally:
		db.close()

	return render_template(
		'index.html',
		tasks=pending_tasks,
		blocks=today_blocks,
		habits=today_habits,
		habit_names=habit_names,
		stats=stats,
		today=today
	)


@bp.route('/tasks')
def tasks_page():
	return render_template('tasks.html')


@bp.route('/habits')
def habits_page():
	return render_template('habits.html', today=date.today())


@bp.route('/schedule')
def schedule_page():
	return render_template('schedule.html', today=date.today())


@bp.route('/settings')
def settings_page():
	return render_template('settings.html')


def _calc_streak(db):
	"""计算当前连续打卡天数"""
	habits = db.query(HabitRecord.date).distinct().order_by(HabitRecord.date.desc()).limit(30).all()
	dates = [h[0] for h in habits]
	streak = 0
	today = date.today()
	for i in range(30):
		check_date = today - timedelta(days=i)
		if check_date in dates:
			streak += 1
		else:
			break
	return streak
