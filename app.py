from flask import Flask, request, jsonify
from models import db # 从 models.py 导入 db 对象
from user_routes import user_bp

app = Flask(__name__)
# ... app.config 设置 ...
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_fitness.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app) # 在这里将 db 对象与 app 实例绑定

# 注册蓝图
app.register_blueprint(user_bp) # <-- 注册蓝图

# 您可以在这里添加其他蓝图的注册，例如：
# from routes.activity_routes import activity_bp
# app.register_blueprint(activity_bp, url_prefix='/api/v1/activities') # 可以添加 URL 前缀

# 数据库初始化 (通常在 app.py 启动时执行一次)
with app.app_context():
    db.create_all()

# 如果有其他非 API 的普通路由，可以继续放在这里，但通常很少
@app.route('/')
def index():
    return "Smart Fitness Backend is running!"
# --- 应用启动入口 ---
if __name__ == '__main__':
    # 确保您已安装所有依赖：pip install Flask Flask-SQLAlchemy Werkzeug
    # 运行此文件即可启动 Flask 应用，并在控制台看到服务地址
    app.run(debug=True, port=5000) # 开启调试模式，开发时方便查看错误和自动重载