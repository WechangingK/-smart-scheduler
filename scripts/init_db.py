"""初始化数据库 - 创建所有表"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

app = create_app()

with app.app_context():
	from app.models.base import Base, engine
	Base.metadata.create_all(bind=engine)
	print('数据库初始化完成！')
	print(f'数据库位置: {app.config["DATABASE_URL"]}')
