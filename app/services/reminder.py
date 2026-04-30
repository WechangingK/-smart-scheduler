"""提醒调度引擎"""
import sched
import time
import threading
from datetime import datetime, timezone, timedelta
from app.models.base import SessionLocal
from app.models.task import Task
from app.models.notification import NotificationLog
from app.models.config_model import Config
from app.services.email_sender import send_reminder_email


class ReminderScheduler:
	def __init__(self):
		self.scheduler = sched.scheduler(timefunc=time.time)
		self._running = False
		self._thread = None

	def start(self):
		if self._running:
			return
		self._running = True
		self._thread = threading.Thread(target=self._run, daemon=True)
		self._thread.start()

	def stop(self):
		self._running = False

	def _run(self):
		while self._running:
			try:
				self._check_reminders()
			except Exception as e:
				print(f'[ReminderScheduler] 检查提醒出错: {e}')
			time.sleep(60)

	def _check_reminders(self):
		db = SessionLocal()
		try:
			offset_minutes = 30
			config = db.query(Config).filter(Config.key == 'reminder_offset_minutes').first()
			if config and config.value:
				try:
					offset_minutes = int(config.value)
				except ValueError:
					pass

			reminder_email = None
			config = db.query(Config).filter(Config.key == 'reminder_email').first()
			if config:
				reminder_email = config.value

			if not reminder_email:
				return

			now = datetime.now(timezone.utc)
			window_start = now
			window_end = now + timedelta(minutes=offset_minutes)

			tasks = db.query(Task).filter(
				Task.status == 'pending',
				Task.due_date != None,
				Task.due_date >= window_start.isoformat(),
				Task.due_date <= window_end.isoformat(),
			).all()

			for task in tasks:
				already_notified = db.query(NotificationLog).filter(
					NotificationLog.type == 'email',
					NotificationLog.title.like(f'%{task.title}%'),
					NotificationLog.status == 'sent',
					NotificationLog.created_at >= now - timedelta(hours=24),
				).first()

				if already_notified:
					continue

				due_str = task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else '未设定'
				reminder_text = f'您的任务 "{task.title}" 即将到期。截止时间: {due_str}。请及时处理！'

				success, error_msg = send_reminder_email(
					reminder_email, task.title, due_str, reminder_text
				)

				log = NotificationLog(
					type='email',
					title=f'[提醒] {task.title}',
					message=reminder_text,
					recipient=reminder_email,
					status='sent' if success else 'failed',
					error_message=error_msg if not success else None,
					scheduled_for=task.due_date,
					sent_at=now if success else None,
				)
				db.add(log)
				db.commit()
		finally:
			db.close()


_scheduler_instance = None


def start_scheduler():
	global _scheduler_instance
	if _scheduler_instance is None:
		_scheduler_instance = ReminderScheduler()
	_scheduler_instance.start()


def stop_scheduler():
	global _scheduler_instance
	if _scheduler_instance:
		_scheduler_instance.stop()


def check_reminders_now() -> int:
	"""立即执行提醒检查，返回发送数量"""
	if _scheduler_instance:
		_scheduler_instance._check_reminders()
		return 1
	scheduler = ReminderScheduler()
	scheduler._check_reminders()
	return 1
