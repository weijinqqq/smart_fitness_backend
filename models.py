from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash # 用于密码哈希
from datetime import datetime #D的依赖
import json

db = SQLAlchemy() # 初始化 db 变量，它将在 app.py 中与 Flask 应用绑定

class User(db.Model):
    __tablename__ = 'users' # 定义表名为 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False) # 存储密码哈希值
    # 可以根据需求添加其他字段，例如：
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    age = db.Column(db.Integer)
    # fitness_goal = db.Column(db.String(200))

    def __repr__(self):
        return f'<User {self.username}>'

    # 用于设置密码，将明文密码哈希后存储
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # 用于验证密码，比较明文密码和存储的哈希值
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

#数据库模型

#运动记录数据模型activities
class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False) #运动类型
    duration_minutes = db.Column(db.Integer, nullable=False) #运动时长
    calories_burned = db.Column(db.Integer, nullable=False) #卡路里消耗
    distance_km = db.Column(db.Float, nullable=True)  # 可以是 Float 类型，允许为 None
    activity_date = db.Column(db.DateTime, default=datetime.utcnow) #记录时间

    def to_dict(self):
        #将模型对象转换为字典，用于JSON响应
        return {
            "id": self.id,
            "activity_type": self.activity_type,
            "duration_minutes": self.duration_minutes,
            "calories_burned": self.calories_burned,
            "distance_km": self.distance_km,
            "activity_date": self.activity_date.isoformat()
        }

#健身计划数据模型plans
class FitnessPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    plan_name = db.Column(db.String(100), nullable=False) #计划名称
    description = db.Column(db.Text) #计划描述
    content = db.Column(db.JSON)  # 存储计划详情
    is_preset = db.Column(db.Boolean, default=False)  # 是否为系统预设
    created_at = db.Column(db.DateTime, default=datetime.utcnow) #创建时间

    def to_dict(self):
        #将模型对象转换为字典，用于JSON响应
        plan_content = self.content
        if plan_content is None:
            plan_content = {}  # 或者 None，取决于前端期望
        elif isinstance(plan_content, str):
            # 如果 content 意外地是字符串（例如，旧数据或手动插入的非JSON字符串），尝试解析
            try:
                plan_content = json.loads(plan_content)
            except json.JSONDecodeError:
                plan_content = {"error": "Invalid JSON content"}  # 或者其他默认值

        return {
            "id": self.id,
            "plan_name": self.plan_name,
            "description": self.description,
            "content": plan_content,
            "is_preset": self.is_preset,
            "created_at": self.created_at.isoformat()
        }