"""ICS 日历文件生成器 - 适配小米/华为/苹果日历 WebCal 订阅"""
from datetime import datetime, date, timezone
from uuid import uuid4

# 亚洲/上海时区定义（小米日历需要明确的 VTIMEZONE）
VTIMEZONE = (
	'BEGIN:VTIMEZONE\r\n'
	'TZID:Asia/Shanghai\r\n'
	'BEGIN:STANDARD\r\n'
	'DTSTART:19700101T000000\r\n'
	'TZOFFSETFROM:+0800\r\n'
	'TZOFFSETTO:+0800\r\n'
	'TZNAME:CST\r\n'
	'END:STANDARD\r\n'
	'END:VTIMEZONE'
)


def generate_ics_from_blocks(blocks: list) -> str:
	"""从时间块列表生成 ICS 格式字符串，适配小米日历"""
	now_utc = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

	lines = [
		'BEGIN:VCALENDAR',
		'VERSION:2.0',
		'PRODID:-//SmartSchedule//CN',
		'CALSCALE:GREGORIAN',
		'METHOD:PUBLISH',
		'X-WR-CALNAME:智能日程',
		'X-WR-TIMEZONE:Asia/Shanghai',
		'X-WR-CALDESC:AI智能日程',
		VTIMEZONE,
	]

	for b in blocks:
		uid = str(uuid4())

		if isinstance(b.get('date'), (date, datetime)):
			event_date = b['date']
		elif isinstance(b.get('date'), str):
			event_date = datetime.fromisoformat(b['date']).date()
		else:
			event_date = date.today()

		start_dt = _format_dt(event_date, b['start_time'])
		end_dt = _format_dt(event_date, b['end_time'])

		type_labels = {'task': '任务', 'focus': '深度工作', 'break': '休息', 'habit': '习惯', 'fixed': '固定'}
		categories = type_labels.get(b.get('block_type', ''), '')
		title = _escape_ics_text(b.get('title', '无标题'))

		lines.extend([
			'BEGIN:VEVENT',
			f'UID:{uid}',
			f'DTSTAMP:{now_utc}',
			f'DTSTART;TZID=Asia/Shanghai:{start_dt}',
			f'DTEND;TZID=Asia/Shanghai:{end_dt}',
			f'SUMMARY:{title}',
		])

		if categories:
			lines.append(f'CATEGORIES:{categories}')

		lines.extend([
			'BEGIN:VALARM',
			'TRIGGER:-PT15M',
			'ACTION:DISPLAY',
			f'DESCRIPTION:即将开始: {title}',
			'END:VALARM',
			'END:VEVENT',
		])

	lines.append('END:VCALENDAR')
	return '\r\n'.join(lines)


def _format_dt(event_date, time_str: str) -> str:
	hours, minutes = time_str.split(':')
	dt = datetime(event_date.year, event_date.month, event_date.day,
				  int(hours), int(minutes))
	return dt.strftime('%Y%m%dT%H%M%S')


def _escape_ics_text(text: str) -> str:
	text = text.replace('\\', '\\\\')
	text = text.replace(';', '\\;')
	text = text.replace(',', '\\,')
	text = text.replace('\n', '\\n')
	return text
