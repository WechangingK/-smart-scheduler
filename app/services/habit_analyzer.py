"""习惯分析引擎"""
from datetime import date, timedelta
from collections import defaultdict
from sqlalchemy import func
from app.models.habit import HabitRecord
from app.services.deepseek import chat_completion


def get_habit_stats(db_session) -> list:
	"""计算各习惯统计数据"""
	today = date.today()
	thirty_days_ago = today - timedelta(days=30)

	records = db_session.query(HabitRecord).filter(
		HabitRecord.date >= thirty_days_ago
	).order_by(HabitRecord.name, HabitRecord.date).all()

	habits_data = defaultdict(list)
	for r in records:
		habits_data[r.name].append(r)

	stats = []
	for name, recs in habits_data.items():
		days_with_data = len(recs)
		completed_days = sum(1 for r in recs if r.completed)

		# 计算连续天数
		streak = 0
		dates = sorted(set(r.date for r in recs if r.completed), reverse=True)
		for i, d in enumerate(dates):
			expected = today - timedelta(days=i)
			if d == expected:
				streak += 1
			else:
				break

		# 趋势判断（比较前15天和后15天）
		first_half = sum(1 for r in recs if r.completed and r.date <= thirty_days_ago + timedelta(days=15))
		second_half = sum(1 for r in recs if r.completed and r.date > thirty_days_ago + timedelta(days=15))

		if second_half > first_half + 1:
			trend = 'up'
		elif second_half < first_half - 1:
			trend = 'down'
		else:
			trend = 'stable'

		stats.append({
			'name': name,
			'completion_rate': round(completed_days / max(days_with_data, 1), 2),
			'streak': streak,
			'total_days': days_with_data,
			'completed_days': completed_days,
			'trend': trend,
			'average_value': round(sum(r.value for r in recs if r.value) / max(sum(1 for r in recs if r.value), 1), 1) if any(r.value for r in recs) else None,
		})

	return stats


def analyze_habits_with_ai(db_session, stats: list) -> dict | None:
	"""使用 AI 分析习惯数据，提供改进建议"""
	if not stats:
		return None

	system_prompt = """你是一个习惯养成教练。分析用户的日常习惯记录数据，提供个性化的改进建议。返回严格 JSON 格式。"""

	user_message = f"""请分析以下习惯数据，给出改进建议：

习惯数据（近30天）：
{__import__('json').dumps(stats, ensure_ascii=False, indent=2)}

请对每个习惯给出建议，输出格式：
{{
  "habits": [
    {{"name": "习惯名", "suggestion": "改进建议（简洁，20字以内）"}}
  ],
  "overall_assessment": "整体评价",
  "next_week_focus": "下周重点关注"
}}"""

	success, content, error = chat_completion(
		messages=[{'role': 'user', 'content': user_message}],
		system_prompt=system_prompt,
		temperature=0.5,
		max_tokens=2048,
		response_format={'type': 'json_object'},
	)

	if success and isinstance(content, dict):
		return content
	return None
