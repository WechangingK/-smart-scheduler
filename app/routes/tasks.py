from flask import Blueprint, request, jsonify
from app.models.base import SessionLocal
from app.models.task import Task
from datetime import datetime, timezone

bp = Blueprint('tasks', __name__)


@bp.route('', methods=['GET'])
def list_tasks():
	db = SessionLocal()
	try:
		query = db.query(Task)
		status = request.args.get('status')
		category = request.args.get('category')
		date_str = request.args.get('date')

		if status:
			query = query.filter(Task.status == status)
		if category:
			query = query.filter(Task.category == category)
		if date_str:
			query = query.filter(Task.due_date >= f'{date_str}T00:00:00')
			query = query.filter(Task.due_date <= f'{date_str}T23:59:59')

		tasks = query.order_by(
			Task.priority == 'high',
			Task.due_date.is_(None),
			Task.due_date
		).all()
		return jsonify([t.to_dict() for t in tasks])
	finally:
		db.close()


@bp.route('', methods=['POST'])
def create_task():
	data = request.get_json(silent=True)
	if not data or not data.get('title'):
		return jsonify({'error': '标题不能为空'}), 400

	db = SessionLocal()
	try:
		task = Task(
			title=data['title'],
			description=data.get('description'),
			priority=data.get('priority', 'medium'),
			category=data.get('category'),
			due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
			estimated_minutes=data.get('estimated_minutes'),
			energy_level=data.get('energy_level'),
			preferred_time_start=data.get('preferred_time_start'),
			preferred_time_end=data.get('preferred_time_end'),
			is_recurring=data.get('is_recurring', False),
			recurrence_rule=data.get('recurrence_rule'),
		)
		db.add(task)
		db.commit()
		db.refresh(task)
		return jsonify(task.to_dict()), 201
	finally:
		db.close()


@bp.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
	db = SessionLocal()
	try:
		task = db.get(Task, task_id)
		if not task:
			return jsonify({'error': '任务不存在'}), 404
		return jsonify(task.to_dict())
	finally:
		db.close()


@bp.route('/<int:task_id>', methods=['PUT'])
def update_task(task_id):
	db = SessionLocal()
	try:
		task = db.get(Task, task_id)
		if not task:
			return jsonify({'error': '任务不存在'}), 404

		data = request.get_json(silent=True)
		if not data:
			return jsonify({'error': '无效的请求数据'}), 400

		for field in ['title', 'description', 'priority', 'status', 'category',
					  'estimated_minutes', 'actual_minutes', 'energy_level',
					  'preferred_time_start', 'preferred_time_end',
					  'is_recurring', 'recurrence_rule']:
			if field in data:
				setattr(task, field, data[field])

		if 'due_date' in data:
			task.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None

		db.commit()
		db.refresh(task)
		return jsonify(task.to_dict())
	finally:
		db.close()


@bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
	db = SessionLocal()
	try:
		task = db.get(Task, task_id)
		if not task:
			return jsonify({'error': '任务不存在'}), 404
		db.delete(task)
		db.commit()
		return jsonify({'message': '任务已删除'})
	finally:
		db.close()


@bp.route('/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
	db = SessionLocal()
	try:
		task = db.get(Task, task_id)
		if not task:
			return jsonify({'error': '任务不存在'}), 404

		data = request.get_json(silent=True) or {}
		task.status = 'completed'
		task.completed_at = datetime.now(timezone.utc)
		task.actual_minutes = data.get('actual_minutes', task.estimated_minutes)
		db.commit()
		db.refresh(task)
		return jsonify(task.to_dict())
	finally:
		db.close()
