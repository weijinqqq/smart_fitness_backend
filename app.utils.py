#认证装饰器

from functools import wraps
from flask import request, jsonify
import jwt
from app import app  # 导入Flask应用实例

def auth_required(f):
    """
    认证装饰器，保护需要登录的API
    从Authorization头获取JWT令牌并验证
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 从请求头获取令牌
        token = request.headers.get('Authorization')
        
        if not token or not token.startswith('Bearer '):
            return jsonify({
                "error": "Unauthorized",
                "message": "Missing or invalid authentication token"
            }), 401
        
        try:
            # 提取并验证JWT令牌
            token = token.split(' ')[1]
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            
            # 将用户ID存储在请求对象中，供路由函数使用
            request.current_user_id = payload['sub']
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                "error": "Token expired",
                "message": "Authentication token has expired"
            }), 401
            
        except jwt.InvalidTokenError:
            return jsonify({
                "error": "Invalid token",
                "message": "Invalid authentication token"
            }), 401
            
        # 调用被装饰的函数
        return f(*args, **kwargs)
        
    return decorated_function
