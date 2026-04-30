from flask import Blueprint, request, jsonify
from app.models.base import SessionLocal
from app.models.timeblock import TimeBlock
from app.models.task import Task
from app.services.schedule_optimizer import generate_daily_schedule
from datetime import date, datetime

bp = Blueprint('schedule', __name__)


@bp.route('/daily', methods=['GET'])
def get_daily_schedule():
	date_str = request.args.get('date', date.today().isoformat())
	db = SessionLocal()
	try:
		blocks = db.query(TimeBlock).filter(
			TimeBlock.date == date_str
		).order_by(TimeBlock.start_time).all()
		return jsonify([b.to_dict() for b in blocks])
	finally:
		db.close()


@bp.route('/optimize', methods=['POST'])
def optimize_schedule():
	data = request.get_json(silent=True) or {}
	date_str = data.get('date', date.today().isoformat())
	target_date = datetime.fromisoformat(date_str).date()

	db = SessionLocal()
	try:
		pending_tasks = db.query(Task).filter(
			Task.status == 'pending'
		).all()

		result = generate_daily_schedule(db, target_date, pending_tasks)

		if result.get('success') and result.get('blocks'):
			db.query(TimeBlock).filter(
				TimeBlock.date == target_date,
				TimeBlock.is_ai_suggested == True
			).delete()

			for i, block_data in enumerate(result['blocks']):
				block = TimeBlock(
					date=target_date,
					task_id=block_data.get('task_id'),
					title=block_data['title'],
					start_time=datetime.strptime(block_data['start_time'], '%H:%M').time(),
					end_time=datetime.strptime(block_data['end_time'], '%H:%M').time(),
					block_type=block_data.get('type', 'task'),
					is_ai_suggested=True,
					sort_order=i,
				)
				db.add(block)
			db.commit()

			all_blocks = db.query(TimeBlock).filter(
				TimeBlock.date == target_date
			).order_by(TimeBlock.start_time).all()

			return jsonify({
				'success': True,
				'blocks': [b.to_dict() for b in all_blocks],
				'analysis': result.get('analysis', ''),
			})

		return jsonify({
			'success': False,
			'message': result.get('message', '日程优化失败'),
			'fallback': [b.to_dict() for b in result.get('fallback_blocks', [])],
		})
	finally:
		db.close()


@bp.route('/blocks/<int:block_id>', methods=['PUT'])
def update_block(block_id):
	db = SessionLocal()
	try:
		block = db.get(TimeBlock, block_id)
		if not block:
			return jsonify({'error': '时间块不存在'}), 404

		data = request.get_json(silent=True)
		if not data:
			return jsonify({'error': '无效的请求数据'}), 400

		if 'start_time' in data:
			block.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
		if 'end_time' in data:
			block.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
		if 'title' in data:
			block.title = data['title']
		if 'is_accepted' in data:
			block.is_accepted = data['is_accepted']

		db.commit()
		db.refresh(block)
		return jsonify(block.to_dict())
	finally:
		db.close()
