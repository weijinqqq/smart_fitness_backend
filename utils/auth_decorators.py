from functools import wraps
from flask import request, jsonify, g, current_app # 导入 g 对象
import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({
                "error": "Unauthorized",
                "message": "需要有效的认证Token。",
                "status_code": 401
            }), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            g.user_id = data['user_id'] # 将 user_id 存储在 Flask 的全局 g 对象中
        except jwt.ExpiredSignatureError:
            return jsonify({
                "error": "Unauthorized",
                "message": "Token已过期。",
                "status_code": 401
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "error": "Unauthorized",
                "message": "无效的Token。",
                "status_code": 401
            }), 401
        except Exception as e:
            return jsonify({
                "error": "Internal Server Error",
                "message": f"Token解析错误：{str(e)}",
                "status_code": 500
            }), 500

        return f(*args, **kwargs)
    return decorated