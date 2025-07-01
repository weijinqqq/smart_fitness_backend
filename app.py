import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, User

# --- Flask 应用配置 ---
app = Flask(__name__)

# 配置 SQLite 数据库文件路径
# os.path.abspath(__file__) 获取当前文件（app.py）的绝对路径
# os.path.dirname() 获取该文件所在的目录
# os.path.join() 拼接路径，将 smart_fitness.db 放在项目根目录下
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'smart_fitness.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 禁用事件追踪，减少内存消耗

#将从 models.py 导入的 db 对象与 app 实例绑定
db.init_app(app)



# --- 数据库创建/更新 ---
# 在应用上下文启动时创建所有数据库表
with app.app_context():
    db.create_all()


# --- API 接口定义 ---

# 用户注册 API (POST /register)
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json() # 获取前端发送的 JSON 数据
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # 1. 数据校验 (简单示例，实际项目需要更严格的验证，例如邮箱格式)
    if not username or not email or not password:
        return jsonify({
            "error": "Bad Request",
            "message": "用户名、邮箱和密码不能为空。",
            "status_code": 400
        }), 400

    # 2. 验证用户名和邮箱的唯一性
    if User.query.filter_by(username=username).first():
        return jsonify({
            "error": "Conflict",
            "message": "用户名已被占用。",
            "status_code": 409
        }), 409
    if User.query.filter_by(email=email).first():
        return jsonify({
            "error": "Conflict",
            "message": "邮箱已被注册。",
            "status_code": 409
        }), 409

    # 3. 创建新用户实例并保存到数据库
    new_user = User(username=username, email=email)
    new_user.set_password(password) # 使用 set_password 方法哈希密码

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            "message": "用户注册成功！",
            "data": {
                "user_id": new_user.id,
                "username": new_user.username
            },
            "status_code": 201
        }), 201 # 201 Created
    except Exception as e:
        db.session.rollback() # 如果发生错误，回滚事务
        return jsonify({
            "error": "Internal Server Error",
            "message": f"注册失败：{str(e)}",
            "status_code": 500
        }), 500


# 用户登录 API (POST /login)
@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # 1. 数据校验
    if not username or not password:
        return jsonify({
            "error": "Bad Request",
            "message": "用户名和密码不能为空。",
            "status_code": 400
        }), 400

    # 2. 查询 Users 表验证用户凭据
    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password): # 使用 check_password 方法验证密码
        # 登录成功，实际项目中这里通常会生成 session 或 JWT token
        return jsonify({
            "message": "登录成功！",
            "data": {
                "user_id": user.id,
                "username": user.username
            },
            "status_code": 200
        }), 200
    else:
        # 登录失败
        return jsonify({
            "error": "Unauthorized",
            "message": "用户名或密码不正确。",
            "status_code": 401
        }), 401

# --- 获取个人信息 API (GET /users/<user_id>) ---
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_info(user_id):
    # 根据 user_id 查询用户
    user = User.query.get(user_id)

    if user:
        # 如果找到用户，返回用户信息
        return jsonify({
            "message": "获取用户成功",
            "data": {
                "user_id": user.id,
                "username": user.username,
                "email": user.email
                # 根据 User 模型中实际存储的字段，添加更多信息
                # "height": user.height,
                # "weight": user.weight,
                # "age": user.age
            },
            "status_code": 200
        }), 200 # 200 OK
    else:
        # 如果未找到用户
        return jsonify({
            "error": "Not Found",
            "message": "未找到指定ID的用户。",
            "status_code": 404
        }), 404 # 404 Not Found

# --- 更新个人信息 API (PUT /users/<user_id>) ---
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user_info(user_id):
    # 根据 user_id 查询用户
    user = User.query.get(user_id)

    if not user:
        # 如果未找到用户
        return jsonify({
            "error": "Not Found",
            "message": "未找到指定ID的用户。",
            "status_code": 404
        }), 404 # 404 Not Found

    data = request.get_json() # 获取前端发送的 JSON 数据

    # 允许更新的字段，根据您的 User 模型实际字段来调整
    # 注意：通常不建议直接通过这个接口更新密码，密码更新应该有单独的接口
    # 并且，用户名和邮箱的更新也可能需要额外的唯一性验证和流程
    if 'username' in data:
        # 如果尝试更新用户名，需要进行唯一性校验
        new_username = data['username']
        if new_username != user.username and User.query.filter_by(username=new_username).first():
            return jsonify({
                "error": "Conflict",
                "message": "新用户名已被占用。",
                "status_code": 409
            }), 409
        user.username = new_username

    if 'email' in data:
        # 如果尝试更新邮箱，需要进行唯一性校验
        new_email = data['email']
        if new_email != user.email and User.query.filter_by(email=new_email).first():
            return jsonify({
                "error": "Conflict",
                "message": "新邮箱已被占用。",
                "status_code": 409
            }), 409
        user.email = new_email

    # 根据您的 User 模型，可以添加更多可更新的字段
    if 'height' in data:
         user.height = data['height']
    if 'weight' in data:
         user.weight = data['weight']
    if 'age' in data:
         user.age = data['age']
    if 'fitness_goal' in data:
         user.fitness_goal = data['fitness_goal']

    try:
        db.session.commit() # 提交更改到数据库
        return jsonify({
            "message": "用户信息更新成功！",
            "data": {
                "user_id": user.id,
                "username": user.username,
                "email": user.email
                # 返回更新后的最新用户信息
            },
            "status_code": 200
        }), 200 # 200 OK
    except Exception as e:
        db.session.rollback() # 如果发生错误，回滚事务
        return jsonify({
            "error": "Internal Server Error",
            "message": f"用户信息更新失败：{str(e)}",
            "status_code": 500
        }), 500


# --- 应用启动入口 ---
if __name__ == '__main__':
    # 确保您已安装所有依赖：pip install Flask Flask-SQLAlchemy Werkzeug
    # 运行此文件即可启动 Flask 应用，并在控制台看到服务地址
    app.run(debug=True, port=5000) # 开启调试模式，开发时方便查看错误和自动重载