"""CalDAV 同步服务 - 嵌入 Radicale WSGI 到 Flask，手机直接同步"""
import os
import json
from datetime import date, datetime
from uuid import uuid4

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CALDAV_DIR = os.path.join(BASE_DIR, 'caldav')
COLLECTIONS_DIR = os.path.join(CALDAV_DIR, 'collections')
COLLECTION_ROOT = os.path.join(COLLECTIONS_DIR, 'collection-root')
CALDAV_USER = 'admin'
CALENDAR_DIR = os.path.join(COLLECTION_ROOT, CALDAV_USER, 'smart-schedule')


def init_caldav():
	os.makedirs(CALENDAR_DIR, exist_ok=True)
	props_file = os.path.join(CALENDAR_DIR, '.Radicale.props')
	if not os.path.exists(props_file):
		props_data = json.dumps({
			'C:supported-calendar-component-set': 'VEVENT,VTODO',
			'D:displayname': '智能日程',
			'D:description': 'AI智能排程',
			'tag': 'VCALENDAR',
		})
		with open(props_file, 'w', encoding='utf-8') as f:
			f.write(props_data)


def get_radicale_app():
	"""获取 Radicale WSGI 应用，嵌入 Flask"""
	import radicale
	import radicale.config
	import radicale.app

	config_path = os.path.join(CALDAV_DIR, 'radicale.conf')
	os.environ['PYTHONUTF8'] = '1'

	# 直接使用 radicale 的 Application
	config = radicale.config.load([(config_path, False)])
	app = radicale.Application(config)
	return app


def sync_blocks_to_caldav(blocks: list):
	"""将时间块写入 CalDAV 存储"""
	init_caldav()

	for f in os.listdir(CALENDAR_DIR):
		if f.endswith('.ics'):
			os.remove(os.path.join(CALENDAR_DIR, f))

	for b in blocks:
		event_date = b.get('date', date.today())
		if isinstance(event_date, str):
			event_date = datetime.fromisoformat(event_date).date()

		start = f'{event_date.strftime("%Y%m%d")}T{_fmt_time(b.get("start_time", "09:00"))}'
		end = f'{event_date.strftime("%Y%m%d")}T{_fmt_time(b.get("end_time", "10:00"))}'
		title = _escape(b.get('title', '无标题'))

		ics = '\r\n'.join([
			'BEGIN:VCALENDAR',
			'VERSION:2.0',
			'PRODID:-//SmartSchedule//CalDAV//CN',
			'BEGIN:VEVENT',
			f'UID:{uuid4()}',
			f'DTSTART;TZID=Asia/Shanghai:{start}',
			f'DTEND;TZID=Asia/Shanghai:{end}',
			f'SUMMARY:{title}',
			'BEGIN:VALARM',
			'TRIGGER:-PT15M',
			'ACTION:DISPLAY',
			f'DESCRIPTION:即将开始: {title}',
			'END:VALARM',
			'END:VEVENT',
			'END:VCALENDAR',
		])

		uid = b.get('id', str(uuid4()))
		with open(os.path.join(CALENDAR_DIR, f'{uid}.ics'), 'w', encoding='utf-8') as f:
			f.write(ics)


def _fmt_time(time_str: str) -> str:
	if isinstance(time_str, str):
		return time_str.replace(':', '') + '00'
	return '090000'


def _escape(text: str) -> str:
	return text.replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,')
