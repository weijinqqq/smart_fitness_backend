#运动记录路由

from flask import Blueprint, request, jsonify
from app.models import Activity, db
from app.utils import auth_required  # 导入认证装饰器

# 创建蓝图，用于组织运动记录相关路由
bp = Blueprint('activities', __name__)

@bp.route('/activities', methods=['POST'])
@auth_required  # 需要认证的装饰器，保护API
def record_activity():
    """
    记录运动数据API
    请求体: JSON {activity_type, duration_minutes, calories_burned}
    响应: 201 Created 或错误信息
    """
    data = request.get_json()
    
    # 验证必要字段是否存在
    required_fields = ['activity_type', 'duration_minutes', 'calories_burned']
    if not all(field in data for field in required_fields):
        return jsonify({
            "error": "Missing required fields",
            "message": "Required fields: activity_type, duration_minutes, calories_burned"
        }), 400  # 400 Bad Request
    
    try:
        # 从认证装饰器中获取当前用户ID
        user_id = getattr(request, 'current_user_id', None)
        
        # 创建新的运动记录对象
        new_activity = Activity(
            user_id=user_id,
            activity_type=data['activity_type'],
            duration_minutes=data['duration_minutes'],
            calories_burned=data['calories_burned']
        )
        
        # 保存到数据库
        db.session.add(new_activity)
        db.session.commit()
        
        # 返回成功响应
        return jsonify({
            "message": "Activity recorded successfully",
            "activity_id": new_activity.id
        }), 201  # 201 Created
        
    except Exception as e:
        # 发生错误时回滚数据库操作
        db.session.rollback()
        return jsonify({
            "error": "Database error",
            "message": str(e)
        }), 500  # 500 Internal Server Error

@bp.route('/users/<int:user_id>/activities', methods=['GET'])
@auth_required
def get_user_activities(user_id):
    """
    获取用户运动历史API
    支持查询参数: type(运动类型), start_date(开始日期), end_date(结束日期)
    """
    # 验证请求用户只能访问自己的数据
    current_user_id = getattr(request, 'current_user_id', None)
    if user_id != current_user_id:
        return jsonify({
            "error": "Unauthorized",
            "message": "You can only access your own activities"
        }), 403  # 403 Forbidden
    
    # 从URL查询参数获取筛选条件
    activity_type = request.args.get('type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # 构建基础查询
    query = Activity.query.filter_by(user_id=user_id)
    
    # 添加筛选条件
    if activity_type:
        query = query.filter(Activity.activity_type == activity_type)
    
    if start_date:
        query = query.filter(Activity.activity_date >= start_date)
    
    if end_date:
        query = query.filter(Activity.activity_date <= end_date)
    
    # 执行查询
    activities = query.all()
    
    # 返回结果
    return jsonify({
        "count": len(activities),
        "activities": [activity.to_dict() for activity in activities]
    }), 200  # 200 OK
