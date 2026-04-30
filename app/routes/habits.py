from flask import Blueprint, request, jsonify
from app.models.base import SessionLocal
from app.models.habit import HabitRecord
from app.services.habit_analyzer import get_habit_stats, analyze_habits_with_ai
from datetime import date, datetime

bp = Blueprint('habits', __name__)


@bp.route('', methods=['GET'])
def list_habits():
	db = SessionLocal()
	try:
		query = db.query(HabitRecord)
		name = request.args.get('name')
		date_str = request.args.get('date')

		if name:
			query = query.filter(HabitRecord.name == name)
		if date_str:
			query = query.filter(HabitRecord.date == date_str)

		records = query.order_by(HabitRecord.date.desc(), HabitRecord.name).limit(100).all()
		return jsonify([r.to_dict() for r in records])
	finally:
		db.close()


@bp.route('', methods=['POST'])
def upsert_habit():
	data = request.get_json(silent=True)
	if not data or not data.get('name'):
		return jsonify({'error': '习惯名称不能为空'}), 400

	record_date = date.today()
	if data.get('date'):
		record_date = datetime.fromisoformat(data['date']).date()

	db = SessionLocal()
	try:
		record = db.query(HabitRecord).filter(
			HabitRecord.name == data['name'],
			HabitRecord.date == record_date
		).first()

		if record:
			record.completed = data.get('completed', record.completed)
			record.value = data.get('value', record.value)
			record.notes = data.get('notes', record.notes)
		else:
			record = HabitRecord(
				name=data['name'],
				date=record_date,
				completed=data.get('completed', False),
				value=data.get('value'),
				notes=data.get('notes'),
			)
			db.add(record)

		db.commit()
		db.refresh(record)
		return jsonify(record.to_dict()), 200 if record.id else 201
	finally:
		db.close()


@bp.route('/stats', methods=['GET'])
def habit_stats():
	db = SessionLocal()
	try:
		stats = get_habit_stats(db)
		return jsonify(stats)
	finally:
		db.close()


@bp.route('/analyze', methods=['GET'])
def habit_analyze():
	db = SessionLocal()
	try:
		stats = get_habit_stats(db)
		ai_analysis = analyze_habits_with_ai(db, stats)
		return jsonify({'stats': stats, 'ai_analysis': ai_analysis})
	finally:
		db.close()
