from flask import Blueprint, request, jsonify
from app.models.base import SessionLocal
from app.models.config_model import Config
from app.services.email_sender import send_test_email
from app.services.reminder import check_reminders_now

bp = Blueprint('settings', __name__)


SENSITIVE_KEYS = {'deepseek_api_key', 'smtp_password', 'google_token_json', 'google_credentials_json', 'encryption_key'}


@bp.route('', methods=['GET'])
def get_settings():
	db = SessionLocal()
	try:
		configs = db.query(Config).all()
		result = {}
		for c in configs:
			# 敏感信息返回脱敏值
			if c.key in SENSITIVE_KEYS and c.value:
				result[c.key] = '***已设置***'
			else:
				result[c.key] = c.value
		return jsonify(result)
	finally:
		db.close()


@bp.route('', methods=['PUT'])
def update_settings():
	data = request.get_json(silent=True)
	if not data:
		return jsonify({'error': '无效的请求数据'}), 400

	db = SessionLocal()
	try:
		for key, value in data.items():
			# 跳过脱敏的占位值
			if value and str(value).startswith('***'):
				continue

			config = db.query(Config).filter(Config.key == key).first()
			str_value = str(value).strip() if value is not None else None
			if config:
				config.value = str_value
			else:
				config = Config(key=key, value=str_value)
				db.add(config)
		db.commit()
		return jsonify({'message': '设置已更新'})
	finally:
		db.close()


@bp.route('/test-email', methods=['POST'])
def test_email():
	data = request.get_json(silent=True) or {}
	recipient = data.get('recipient')

	if not recipient:
		return jsonify({'error': '请提供测试邮箱地址'}), 400

	success, message = send_test_email(recipient)
	return jsonify({'success': success, 'message': message})


@bp.route('/check-reminders', methods=['POST'])
def trigger_reminders():
	count = check_reminders_now()
	return jsonify({'message': f'已检查提醒，发送了 {count} 条通知', 'count': count})
