import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
DATABASE_URL = os.environ.get('DATABASE_URL', f'sqlite:///{os.path.join(DATA_DIR, "scheduler.db")}')

# DeepSeek 默认配置
DEEPSEEK_BASE_URL = 'https://api.deepseek.com/v1'
DEEPSEEK_MODEL = 'deepseek-chat'

# 提醒默认配置
DEFAULT_REMINDER_OFFSET_MINUTES = 30
REMINDER_CHECK_INTERVAL_SECONDS = 60

# 邮件默认配置
DEFAULT_SMTP_PORT = 587
DEFAULT_SMTP_USE_SSL = False

# 日历同步
CALENDAR_SYNC_DAYS_AHEAD = 14

DEBUG = os.environ.get('DEBUG', 'true').lower() == 'true'
