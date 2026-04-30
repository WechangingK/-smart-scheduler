"""智能日程规划引擎"""
import json
from datetime import date, datetime, time
from app.services.deepseek import chat_completion

SYSTEM_PROMPT = """你是一个个人时间管理专家。根据用户的任务列表和数据，为用户规划一天的理想日程。

规划原则：
1. 高优先级任务安排在精力最好的时段（通常是上午）
2. 深度工作安排在上午9-11点，下午2-4点
3. 低精力任务安排在下午4点后
4. 每工作90分钟安排10-15分钟休息
5. 午餐时间安排在12:00-13:00
6. 如果有习惯（如跑步、阅读），也安排固定时间
7. 输出严格JSON格式，不要有任何额外文本"""


def generate_daily_schedule(db_session, target_date: date, tasks: list):
	"""
	生成每日智能日程
	tasks: Task 对象列表
	返回: dict with 'success', 'blocks', 'analysis', 'message'
	"""
	if not tasks:
		return fallback_schedule(target_date, tasks, '没有待办任务，无法生成日程')

	task_descriptions = []
	for t in tasks:
		desc = {
			'id': t.id,
			'title': t.title,
			'priority': t.priority,
			'estimated_minutes': t.estimated_minutes or 60,
			'energy_level': t.energy_level or 'medium',
			'category': t.category or '未分类',
		}
		if t.preferred_time_start:
			desc['preferred_time_start'] = t.preferred_time_start.strftime('%H:%M')
		if t.preferred_time_end:
			desc['preferred_time_end'] = t.preferred_time_end.strftime('%H:%M')
		task_descriptions.append(desc)

	user_message = f"""请为 {target_date.isoformat()} (周{['一','二','三','四','五','六','日'][target_date.weekday()]}) 规划日程。

待办任务:
{json.dumps(task_descriptions, ensure_ascii=False, indent=2)}

输出格式:
{{
  "blocks": [
    {{"title": "任务标题", "start_time": "09:00", "end_time": "10:00", "type": "task", "task_id": 任务ID, "reason": "安排原因"}}
  ],
  "analysis": "今日日程分析总结"
}}

注意:
- task_id 对应上面任务的 id 字段，如果没有对应任务则填 null
- type 可选: task/focus/break/habit/fixed
- 每个任务至少安排预估的时间长度"""

	success, content, error = chat_completion(
		messages=[{'role': 'user', 'content': user_message}],
		system_prompt=SYSTEM_PROMPT,
		temperature=0.3,
		max_tokens=4096,
		response_format={'type': 'json_object'},
	)

	if success and isinstance(content, dict):
		return {
			'success': True,
			'blocks': content.get('blocks', []),
			'analysis': content.get('analysis', ''),
		}

	return fallback_schedule(target_date, tasks, error or 'AI 日程生成失败')


def fallback_schedule(target_date: date, tasks: list, message: str):
	"""降级方案：按规则排序"""
	priority_order = {'high': 0, 'medium': 1, 'low': 2}
	sorted_tasks = sorted(tasks, key=lambda t: priority_order.get(t.priority, 1))

	start_hour = 9
	blocks = []
	for t in sorted_tasks:
		mins = t.estimated_minutes or 60
		end_hour = start_hour + max(mins // 60, 1)
		end_min = mins % 60
		blocks.append({
			'title': t.title,
			'start_time': f'{start_hour:02d}:00',
			'end_time': f'{end_hour:02d}:{end_min:02d}',
			'type': 'task',
			'task_id': t.id,
			'reason': '按优先级排序',
		})
		start_hour = end_hour
		if start_hour == 12:
			blocks.append({
				'title': '午餐休息',
				'start_time': '12:00',
				'end_time': '13:00',
				'type': 'break',
				'task_id': None,
				'reason': '',
			})
			start_hour = 13
		if start_hour >= 18:
			break

	return {
		'success': False,
		'message': message,
		'blocks': [],
		'fallback_blocks': blocks,
	}
