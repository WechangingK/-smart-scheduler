"""日历路由 - ICS 日历订阅 / 下载，适用于小米日历、华为日历等"""
import socket
from datetime import date, timedelta
from flask import Blueprint, request, jsonify, Response, render_template
from app.models.base import SessionLocal
from app.models.timeblock import TimeBlock
from app.services.calendar_ics import generate_ics_from_blocks

bp = Blueprint('calendar', __name__)


def _get_ics_content(days_ahead=14):
	today = date.today()
	end_date = today + timedelta(days=days_ahead)
	db = SessionLocal()
	try:
		blocks = db.query(TimeBlock).filter(
			TimeBlock.date >= today,
			TimeBlock.date <= end_date,
		).order_by(TimeBlock.date, TimeBlock.start_time).all()

		return generate_ics_from_blocks([
			{
				'date': b.date,
				'title': b.title,
				'start_time': b.start_time.strftime('%H:%M'),
				'end_time': b.end_time.strftime('%H:%M'),
				'block_type': b.block_type,
			}
			for b in blocks
		])
	finally:
		db.close()


@bp.route('/ics', methods=['GET'])
def ics_subscription():
	"""ICS 日历订阅"""
	days = request.args.get('days', 14, type=int)
	content = _get_ics_content(days)
	return Response(content, mimetype='text/calendar')


@bp.route('/schedule.ics', methods=['GET'])
def ics_download():
	"""ICS 文件下载（带 .ics 后缀，兼容更多日历App）"""
	days = request.args.get('days', 14, type=int)
	content = _get_ics_content(days)
	return Response(
		content,
		mimetype='text/calendar',
		headers={
			'Content-Disposition': 'attachment; filename=smart_schedule.ics',
			'Cache-Control': 'no-cache',
		}
	)


@bp.route('/download', methods=['GET'])
def download_page():
	"""手机端下载页面"""
	lan_ip = _get_lan_ip()
	return render_template('calendar_download.html', lan_ip=lan_ip)


@bp.route('/status', methods=['GET'])
def calendar_status():
	lan_ip = _get_lan_ip()
	port = 5000
	return jsonify({
		'local_ip': lan_ip,
		'port': port,
		'caldav_url': f'http://{lan_ip}:5000/caldav',
		'caldav_username': 'admin',
		'caldav_password': '123456',
		'subscription_url': f'http://{lan_ip}:{port}/api/calendar/ics',
		'download_url': f'http://{lan_ip}:{port}/api/calendar/schedule.ics',
	})


def _get_lan_ip() -> str:
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.settimeout(0.1)
		s.connect(('10.254.254.254', 1))
		ip = s.getsockname()[0]
		s.close()
		return ip
	except Exception:
		try:
			return socket.gethostbyname(socket.gethostname())
		except Exception:
			return '127.0.0.1'
