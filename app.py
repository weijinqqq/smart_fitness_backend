import os
from flask import Flask
from models import db # 从 models.py 导入 db 对象
from routes.user_routes import user_bp
from routes.activities import activities_bp    # D 负责的运动记录模块
from routes.plans import plan_bp     # D 负责的健身计划模块
from routes.forum import forum_bp # 导入论坛蓝图
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env.py') #关于认证装饰的设置
app = Flask(__name__)
# ... app.config 设置 ...
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_fitness.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') # 从环境变量中获取密钥

if app.config['SECRET_KEY'] is None:
    raise RuntimeError("SECRET_KEY is not set in .env.py file or environment variables.")

db.init_app(app) # 在这里将 db 对象与 app 实例绑定

# 注册蓝图
app.register_blueprint(user_bp) # <注册用户蓝图
app.register_blueprint(activities_bp) # 运动记录模块的路由前缀
app.register_blueprint(plan_bp) # 健身计划模块的路由前缀
app.register_blueprint(forum_bp) # 注册论坛蓝图



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