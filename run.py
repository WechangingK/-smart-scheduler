import webbrowser
import threading
from app import create_app

app = create_app()

if __name__ == '__main__':
	# 延迟 1.5 秒自动打开浏览器
	threading.Timer(1.5, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
	app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
