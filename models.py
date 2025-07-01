from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash # 用于密码哈希

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