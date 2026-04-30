"""DeepSeek API 客户端"""
import json
import re
import requests
from app.models.base import SessionLocal
from app.models.config_model import Config

DEEPSEEK_BASE_URL = 'https://api.deepseek.com/v1'


def _get_api_key():
	db = SessionLocal()
	try:
		c = db.query(Config).filter(Config.key == 'deepseek_api_key').first()
		return c.value if c else None
	finally:
		db.close()


def _get_model():
	db = SessionLocal()
	try:
		c = db.query(Config).filter(Config.key == 'deepseek_model').first()
		return c.value if c else 'deepseek-chat'
	finally:
		db.close()


def chat_completion(messages, system_prompt=None, temperature=0.7, max_tokens=2048, response_format=None):
	"""
	调用 DeepSeek Chat API
	返回: (success: bool, content: str|dict, error: str|None)
	"""
	api_key = _get_api_key()
	if not api_key:
		return False, None, '请先在设置中配置 DeepSeek API Key'

	headers = {
		'Authorization': f'Bearer {api_key}',
		'Content-Type': 'application/json',
	}

	full_messages = []
	if system_prompt:
		full_messages.append({'role': 'system', 'content': system_prompt})
	full_messages.extend(messages)

	body = {
		'model': _get_model(),
		'messages': full_messages,
		'temperature': temperature,
		'max_tokens': max_tokens,
	}

	if response_format:
		body['response_format'] = response_format

	try:
		resp = requests.post(
			f'{DEEPSEEK_BASE_URL}/chat/completions',
			headers=headers,
			json=body,
			timeout=60,
		)
		resp.raise_for_status()
		data = resp.json()
		content = data['choices'][0]['message']['content']

		if response_format and response_format.get('type') == 'json_object':
			try:
				return True, json.loads(content), None
			except json.JSONDecodeError:
				match = re.search(r'\{[\s\S]*\}', content)
				if match:
					try:
						return True, json.loads(match.group()), None
					except json.JSONDecodeError:
						pass
				return True, content, f'JSON 解析失败: {content[:200]}'

		return True, content, None
	except requests.exceptions.Timeout:
		return False, None, 'DeepSeek API 请求超时'
	except requests.exceptions.RequestException as e:
		return False, None, f'DeepSeek API 请求失败: {str(e)}'
