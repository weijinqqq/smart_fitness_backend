from flask import Blueprint, request, jsonify, g, current_app
from models import db, User # 导入 db 和 User 模型
from werkzeug.security import generate_password_hash, check_password_hash
from utils.auth_decorators import token_required
import jwt # 导入 jwt 库
import datetime # 导入 datetime 库

# 创建一个蓝图实例
user_bp = Blueprint('user_bp', __name__)

# --- 用户注册 API ---
@user_bp.route('/register', methods=['POST'])

def register():
    # ... (这里放您之前在 app.py 里的注册 API 代码) ...
    # 注意：这里需要导入 models.py 中的 db 和 User
    # 确保这里能访问到 generate_password_hash 和 check_password_hash
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "Bad Request", "message": "用户名、邮箱和密码不能为空。", "status_code": 400}), 400

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"error": "Conflict", "message": "用户名或邮箱已被占用。", "status_code": 409}), 409

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, password_hash=hashed_password)
    db.session.add(new_user)
    try:
        db.session.commit()
        return jsonify({
            "message": "用户注册成功！",
            "data": {
                "user_id": new_user.id,
                "username": new_user.username
            },
            "status_code": 201
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": f"注册失败：{str(e)}", "status_code": 500}), 500

# --- 用户登录 API ---
@user_bp.route('/login', methods=['POST'])

def login():
    # ... (这里放您之前在 app.py 里的登录 API 代码) ...
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Bad Request", "message": "用户名和密码不能为空。", "status_code": 400}), 400

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        token_payload = {
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # Token 24小时后过期
        }
        # current_app.config['SECRET_KEY'] 从 app.py 中获取
        token = jwt.encode(token_payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({
            "message": "登录成功！",
            "data": {
                "user_id": user.id,
                "username": user.username,
                "access_token": token  # 返回 JWT token
            },
            "status_code": 200
        }), 200
    else:
        return jsonify({"error": "Unauthorized", "message": "用户名或密码不正确。", "status_code": 401}), 401

# --- 获取个人信息 API ---
@user_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required # 认证用户
def get_user_info(user_id):
    # ... (这里放您之前在 app.py 里的获取个人信息 API 代码) ...
    current_user_id = g.user_id # 获取当前认证用户的ID
    # 授权检查：确保认证用户只能获取自己的信息
    if current_user_id != user_id:
        return jsonify({
            "error": "Forbidden",
            "message": "无权访问其他用户的信息。",
            "status_code": 403
        }), 403
    user = User.query.get(user_id)
    if user:
        return jsonify({
            "message": "获取用户成功",
            "data": {
                "user_id": user.id,
                "username": user.username,
                "email": user.email
            },
            "status_code": 200
        }), 200
    else:
        return jsonify({
            "error": "Not Found",
            "message": "未找到指定ID的用户。",
            "status_code": 404
        }), 404

# --- 更新个人信息 API ---
@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required # 认证用户
def update_user_info(user_id):
    current_user_id = g.user_id  # 获取当前认证用户的ID

    # 授权检查：确保认证用户只能更新自己的信息
    if current_user_id != user_id:
        return jsonify({
            "error": "Forbidden",
            "message": "无权更新其他用户的信息。",
            "status_code": 403
        }), 403

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "error": "Not Found",
            "message": "未找到指定ID的用户。",
            "status_code": 404
        }), 404

    data = request.get_json()

    if 'username' in data:
        new_username = data['username']
        if new_username != user.username and User.query.filter_by(username=new_username).first():
            return jsonify({
                "error": "Conflict",
                "message": "新用户名已被占用。",
                "status_code": 409
            }), 409
        user.username = new_username

    if 'email' in data:
        new_email = data['email']
        if new_email != user.email and User.query.filter_by(email=new_email).first():
            return jsonify({
                "error": "Conflict",
                "message": "新邮箱已被占用。",
                "status_code": 409
            }), 409
        user.email = new_email

    try:
        db.session.commit()
        return jsonify({
            "message": "用户信息更新成功！",
            "data": {
                "user_id": user.id,
                "username": user.username,
                "email": user.email
            },
            "status_code": 200
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": f"用户信息更新失败：{str(e)}", "status_code": 500}), 500

# --- 删除个人信息 API ---
# 规范：DELETE /users/<user_id>
@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required # 认证用户
def delete_user(user_id):
    """
    删除指定用户账户API
    响应: 200 OK 或 204 No Content 或错误信息
    """
    current_user_id = g.user_id # 获取当前认证用户的ID

    # 授权检查：确保认证用户只能删除自己的账户
    if current_user_id != user_id:
        return jsonify({
            "error": "Forbidden",
            "message": "无权删除其他用户账户。",
            "status_code": 403
        }), 403

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "error": "Not Found",
            "message": "未找到指定ID的用户。",
            "status_code": 404
        }), 404

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({
            "message": "用户账户删除成功！",
            "status_code": 200
        }), 200 # 也可以返回 204 No Content，但 200 并带消息更明确
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "message": f"用户账户删除失败：{str(e)}", "status_code": 500}), 500

