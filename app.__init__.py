#应用工厂

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

# 创建扩展对象
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()

def create_app():
    """应用工厂函数，创建和配置Flask应用"""
    app = Flask(__name__)
    
    # 从配置文件加载配置
    app.config.from_object('app.config.Config')
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)  # 启用CORS支持
    
    # 注册蓝图
    from app.routes import activities, plans
    app.register_blueprint(activities.bp)
    app.register_blueprint(plans.bp)
    
    return app
