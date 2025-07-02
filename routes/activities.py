#运动记录路由
from utils.auth_decorators import token_required #导入认证装饰器
from flask import Blueprint, request, jsonify, g
from models import Activity, db

# 创建蓝图，用于组织运动记录相关路由
activities_bp = Blueprint('activities_bp', __name__)

#---记录运动数据API---
@activities_bp.route('/activities', methods=['POST'])
@token_required
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
        #user_id = getattr(request, 'current_user_id', None)
        user_id = g.user_id
        
        # 创建新的运动记录对象
        new_activity = Activity(
            user_id=user_id,
            activity_type=data['activity_type'],
            duration_minutes=data['duration_minutes'],
            calories_burned=data['calories_burned']
            #activity_date 字段如果需要，也要从 data 中获取并传入
            #activity_date=data.get('activity_date')
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

#---获取用户所有运动记录API---
@activities_bp.route('/users/<int:user_id>/activities', methods=['GET'])
@token_required
def get_user_activities(user_id):
    """
    获取用户运动历史API
    支持查询参数: type(运动类型), start_date(开始日期), end_date(结束日期)
    """
    # 验证请求用户只能访问自己的数据
    current_user_id = g.user_id # 获取当前认证用户的ID
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

    # 确保 Activity 模型有 to_dict() 方法
    activities_list = []
    for activity in activities:
        activities_list.append({
            "activity_id": activity.id,
            "user_id": activity.user_id,
            "activity_type": activity.activity_type,
            "duration_minutes": activity.duration_minutes,
            "calories_burned": activity.calories_burned,
            "distance_km": activity.distance_km,
            "activity_date": activity.activity_date.isoformat() if activity.activity_date else None
        })

    # 返回结果
    return jsonify({
        "count": len(activities),
        "activities": [activity.to_dict() for activity in activities]
    }), 200  # 200 OK
# --- 获取指定 ID 的运动记录 API ---
# 规范：GET /activities/<activity_id>
@activities_bp.route('/activities/<int:activity_id>', methods=['GET']) # <-- 修正这里，改为完整路径
@token_required
def get_activity_by_id(activity_id):
    current_user_id = g.user_id

    activity = Activity.query.get(activity_id)

    if not activity:
        return jsonify({
            "error": "Not Found",
            "message": "未找到指定ID的运动记录。",
            "status_code": 404
        }), 404

    if activity.user_id != current_user_id:
        return jsonify({
            "error": "Forbidden",
            "message": "无权访问该运动记录。",
            "status_code": 403
        }), 403

    return jsonify({
        "message": "获取运动记录成功！",
        "data": {
            "activity_id": activity.id,
            "user_id": activity.user_id,
            "activity_type": activity.activity_type,
            "duration_minutes": activity.duration_minutes,
            "calories_burned": activity.calories_burned,
            "distance_km": activity.distance_km,
            "activity_date": activity.activity_date.isoformat() if activity.activity_date else None
        },
        "status_code": 200
    }), 200

# --- 更新指定 ID 的运动记录 API ---
# 规范：PUT /activities/<activity_id>
@activities_bp.route('/activities/<int:activity_id>', methods=['PUT']) # <-- 修正这里，改为完整路径
@token_required
def update_activity_by_id(activity_id):
    current_user_id = g.user_id

    activity = Activity.query.get(activity_id)

    if not activity:
        return jsonify({
            "error": "Not Found",
            "message": "未找到指定ID的运动记录。",
            "status_code": 404
        }), 404

    if activity.user_id != current_user_id:
        return jsonify({
            "error": "Forbidden",
            "message": "无权更新该运动记录。",
            "status_code": 403
        }), 403

    data = request.get_json()

    try:
        activity.activity_type = data.get('activity_type', activity.activity_type)
        activity.duration_minutes = data.get('duration_minutes', activity.duration_minutes)
        activity.calories_burned = data.get('calories_burned', activity.calories_burned)
        activity.distance_km = data.get('distance_km', activity.distance_km)

        db.session.commit()

        return jsonify({
            "message": "运动记录更新成功！",
            "data": {
                "activity_id": activity.id,
                "user_id": activity.user_id,
                "activity_type": activity.activity_type,
                "duration_minutes": activity.duration_minutes,
                "calories_burned": activity.calories_burned,
                "distance_km": activity.distance_km,
                "activity_date": activity.activity_date.isoformat() if activity.activity_date else None
            },
            "status_code": 200
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "message": str(e), "status_code": 500}), 500

# --- 删除指定 ID 的运动记录 API ---
# 规范：DELETE /activities/<activity_id>
@activities_bp.route('/activities/<int:activity_id>', methods=['DELETE']) # <-- 修正这里，改为完整路径
@token_required
def delete_activity(activity_id):
    current_user_id = g.user_id

    activity = Activity.query.get(activity_id)

    if not activity:
        return jsonify({
            "error": "Not Found",
            "message": "未找到指定ID的运动记录。",
            "status_code": 404
        }), 404

    if activity.user_id != current_user_id:
        return jsonify({
            "error": "Forbidden",
            "message": "无权删除该运动记录。",
            "status_code": 403
        }), 403

    try:
        db.session.delete(activity)
        db.session.commit()
        return jsonify({
            "message": "运动记录删除成功！",
            "status_code": 200
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "message": str(e), "status_code": 500}), 500