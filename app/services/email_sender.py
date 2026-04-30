"""邮件发送服务 - 使用 Python 内置 smtplib"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.models.base import SessionLocal
from app.models.config_model import Config


def _get_config(db, key, default=None):
	c = db.query(Config).filter(Config.key == key).first()
	return c.value.strip() if c and c.value else default


def _get_smtp_config(db) -> dict:
	return {
		'server': _get_config(db, 'smtp_server', 'smtp.gmail.com').strip(),
		'port': int(_get_config(db, 'smtp_port', '587')),
		'user': _get_config(db, 'smtp_user', '').strip(),
		'password': _get_config(db, 'smtp_password', '').strip(),
		'sender': _get_config(db, 'sender_email', '').strip(),
	}


def send_email(to: str, subject: str, html_body: str, smtp_config: dict = None) -> tuple:
	"""
	发送邮件
	返回 (success: bool, message: str)
	"""
	if smtp_config is None:
		db = SessionLocal()
		try:
			smtp_config = _get_smtp_config(db)
		finally:
			db.close()

	if not smtp_config.get('user') or not smtp_config.get('password'):
		return False, 'SMTP 配置不完整，请先在设置中配置邮箱'

	msg = MIMEMultipart('alternative')
	msg['Subject'] = subject
	msg['From'] = smtp_config.get('sender', smtp_config['user'])
	msg['To'] = to
	msg.attach(MIMEText(html_body, 'html', 'utf-8'))

	try:
		port = smtp_config['port']
		use_ssl = port == 465

		if use_ssl:
			server = smtplib.SMTP_SSL(smtp_config['server'], port, timeout=15)
		else:
			server = smtplib.SMTP(smtp_config['server'], port, timeout=15)
			server.starttls()

		server.login(smtp_config['user'], smtp_config['password'])
		server.sendmail(msg['From'], to, msg.as_string())
		server.quit()
		return True, '邮件发送成功'
	except smtplib.SMTPAuthenticationError:
		return False, 'SMTP 认证失败，请检查邮箱和密码/授权码'
	except smtplib.SMTPException as e:
		return False, f'SMTP 错误: {str(e)}'
	except Exception as e:
		return False, f'发送失败: {str(e)}'


def send_test_email(to: str) -> tuple:
	"""发送测试邮件"""
	html = """
	<h2>📅 智能日程管理 - 测试邮件</h2>
	<p>如果您收到这封邮件，说明邮箱配置成功！</p>
	<p>系统将会在以下场景发送通知：</p>
	<ul>
		<li>任务到期前提醒</li>
		<li>每日日程汇总</li>
		<li>习惯打卡提醒</li>
	</ul>
	<hr>
	<p style="color: #8892a4; font-size: 12px;">由智能日程管理Agent自动发送</p>
	"""
	return send_email(to, '[测试] 智能日程管理 - 邮件配置验证', html)


def send_reminder_email(to: str, task_title: str, task_due: str, reminder_text: str) -> tuple:
	"""发送任务提醒邮件"""
	html = f"""
	<h2>⏰ 任务提醒</h2>
	<div style="background: #f8f9fc; padding: 16px; border-radius: 8px; margin: 12px 0;">
		<h3 style="margin: 0 0 8px 0;">{task_title}</h3>
		<p style="margin: 0; color: #8892a4;">⏱️ 截止时间: {task_due}</p>
	</div>
	<p>{reminder_text}</p>
	<hr>
	<p style="color: #8892a4; font-size: 12px;">由智能日程管理Agent自动发送</p>
	"""
	return send_email(to, f'[提醒] {task_title}', html)
