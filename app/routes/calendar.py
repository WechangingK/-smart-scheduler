from datetime import date, timedelta
from flask import Blueprint, request, Response
from app.models.base import SessionLocal
from app.models.timeblock import TimeBlock

bp = Blueprint('calendar', __name__)


@bp.route('/ics', methods=['GET'])
def export_ics():
	days = request.args.get('days', 14, type=int)
	today = date.today()
	end_date = today + timedelta(days=days)

	db = SessionLocal()
	try:
		blocks = db.query(TimeBlock).filter(
			TimeBlock.date >= today,
			TimeBlock.date <= end_date,
		).order_by(TimeBlock.date, TimeBlock.start_time).all()

		lines = [
			'BEGIN:VCALENDAR',
			'VERSION:2.0',
			'PRODID:-//SmartSchedule//CN',
			'CALSCALE:GREGORIAN',
			'METHOD:PUBLISH',
			'X-WR-CALNAME:智能日程',
			'X-WR-TIMEZONE:Asia/Shanghai',
			'BEGIN:VTIMEZONE',
			'TZID:Asia/Shanghai',
			'BEGIN:STANDARD',
			'DTSTART:19700101T000000',
			'TZOFFSETFROM:+0800',
			'TZOFFSETTO:+0800',
			'TZNAME:CST',
			'END:STANDARD',
			'END:VTIMEZONE',
		]

		for b in blocks:
			title = b.title.replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,')
			s = b.start_time.strftime('%H%M%S')
			e = b.end_time.strftime('%H%M%S')
			d = b.date.strftime('%Y%m%d')

			lines.extend([
				'BEGIN:VEVENT',
				f'DTSTART;TZID=Asia/Shanghai:{d}T{s}',
				f'DTEND;TZID=Asia/Shanghai:{d}T{e}',
				f'SUMMARY:{title}',
				'BEGIN:VALARM',
				'TRIGGER:-PT15M',
				'ACTION:DISPLAY',
				f'DESCRIPTION:即将开始: {title}',
				'END:VALARM',
				'END:VEVENT',
			])

		lines.append('END:VCALENDAR')

		return Response(
			'\r\n'.join(lines),
			mimetype='text/calendar',
			headers={'Content-Disposition': 'attachment; filename=schedule.ics'},
		)
	finally:
		db.close()
