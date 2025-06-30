from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

# 1. 初始化 Flask 应用
app = Flask(__name__)

# 2. 配置数据库
# __file__ 获取当前文件路径，os.path.abspath 获取绝对路径
# os.path.dirname 获取目录路径，os.path.join 拼接路径
# SQLite 数据库文件将存放在项目根目录
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'smart_fitness.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 禁用跟踪对象修改的通知

db = SQLAlchemy(app)

# 3. 定义数据库模型 (例如 用户模型)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False) # 简化，实际应使用更长的哈希值
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# 4. 创建数据库表 (在应用启动时执行一次)
# 注意：首次运行此代码时，会创建 smart_fitness.db 数据库文件和 users 表。
# 之后再次运行，如果表已存在，不会重复创建。
with app.app_context():
    db.create_all()

# 5. 定义一个简单的API路由 (示例：注册用户)
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({'message': 'Missing username, password or email'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 409

    # 实际项目中，password 应进行哈希处理
    new_user = User(username=username, password_hash=password, email=email) # 简化处理
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

# 6. 运行 Flask 应用
if __name__ == '__main__':
    app.run(debug=True, port=5000) # port=5000 是默认端口，可以修改