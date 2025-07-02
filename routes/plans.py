#健身计划路由
from utils.auth_decorators import token_required
from flask import Blueprint, request, jsonify, g
from models import FitnessPlan, db


# 创建蓝图，用于组织健身计划相关路由
plan_bp = Blueprint('plan_bp', __name__)

#---获取所有预设计划API---
@plan_bp.route('/fitness_plans/preset', methods=['GET'])
def get_preset_plans():
    """
    获取系统预设健身计划API
    无需认证，所有用户可访问
    """
    try:
        # 调试点 1: 查询前
        print("DEBUG: Attempting to query preset plans...")
        preset_plans = FitnessPlan.query.filter_by(is_preset=True).all()
        # 调试点 2: 查询后
        print(f"DEBUG: Found {len(preset_plans)} preset plans.")

        plans_list = []
        for plan in preset_plans:
            # 调试点 3: 尝试转换每个计划
            try:
                plan_dict = plan.to_dict()
                plans_list.append(plan_dict)
                print(f"DEBUG: Successfully converted plan ID {plan.id} to dict.")
            except Exception as e_convert:
                print(f"ERROR: Failed to convert plan ID {plan.id} to dict: {e_convert}")
                # 如果转换失败，可以跳过这个计划或返回一个错误提示
                # 为了调试，这里我们直接让它继续，看是否是某个特定计划的问题
                plans_list.append({"id": plan.id, "error": str(e_convert)})  # 临时添加错误信息
                continue  # 继续处理下一个计划

        # 调试点 4: 准备返回 JSON
        print(f"DEBUG: Final plans_list prepared: {plans_list}")

        return jsonify({
            "count": len(plans_list),
            "plans": plans_list
        }), 200

    except Exception as e:
        # 调试点 5: 捕获到更上层的错误
        print(f"ERROR: An unexpected error occurred in get_preset_plans: {e}")
        return jsonify({
            "error": "Database error",
            "message": str(e)
        }), 500


#---为用户创建计划API---
@plan_bp.route('/users/<int:user_id>/fitness_plans', methods=['POST'])
@token_required # 认证用户
def create_or_select_plan(user_id):
    """
    用户创建或选择健身计划API
    两种方式:
    1. 选择现有预设计划: 提供plan_id
    2. 创建新计划: 提供plan_name和content
    """
    # 验证请求用户只能操作自己的数据
    current_user_id = g.user_id
    if user_id != current_user_id:
        return jsonify({
            "error": "Unauthorized",
            "message": "You can only manage your own fitness plans"
        }), 403
    
    data = request.get_json()
    
    # 验证必要字段
    if 'plan_id' not in data and ('plan_name' not in data or 'content' not in data):
        return jsonify({
            "error": "Missing required fields",
            "message": "Either provide plan_id to select existing, or plan_name and content to create new"
        }), 400
    
    try:
        if 'plan_id' in data:
            # 用户选择现有预设计划
            existing_plan = FitnessPlan.query.get(data['plan_id'])
            
            if not existing_plan:
                return jsonify({
                    "error": "Not found",
                    "message": "Plan with provided ID does not exist"
                }), 404
            
            # 创建用户副本（非预设）
            new_plan = FitnessPlan(
                user_id=user_id,
                plan_name=existing_plan.plan_name,
                description=existing_plan.description,
                content=existing_plan.content,
                is_preset=False  # 标记为用户自定义计划
            )
        else:
            # 用户创建全新计划
            # 验证 plan_name 和 content 是否存在，因为上面已经判断了，这里可以简化
            if 'plan_name' not in data or 'content' not in data:
                return jsonify({
                    "error": "Missing required fields",
                    "message": "plan_name and content are required to create a new plan"
                }), 400
            new_plan = FitnessPlan(
                user_id=user_id,
                plan_name=data['plan_name'],
                description=data.get('description', ''),
                content=data['content'],
                is_preset=False
            )
        
        # 保存到数据库
        db.session.add(new_plan)
        db.session.commit()
        
        return jsonify({
            "message": "Fitness plan created/selected successfully",
            "plan_id": new_plan.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Database error",
            "message": str(e)
        }), 500

#---获取用户健身计划API---
@plan_bp.route('/users/<int:user_id>/fitness_plans', methods=['GET'])
@token_required # 认证用户
def get_user_plans(user_id):
    """
    获取用户的所有健身计划API
    只返回用户自定义计划（非预设）
    """
    # 验证请求用户只能访问自己的数据
    current_user_id = g.user_id
    if user_id != current_user_id:
        return jsonify({
            "error": "Unauthorized",
            "message": "You can only access your own fitness plans"
        }), 403
    
    try:
        # 查询用户的所有非预设计划
        user_plans = FitnessPlan.query.filter_by(user_id=user_id, is_preset=False).all()
        
        return jsonify({
            "count": len(user_plans),
            "plans": [plan.to_dict() for plan in user_plans]
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Database error",
            "message": str(e)
        }), 500


# --- 更新用户计划 API ---
# 规范：PUT /users/<user_id>/fitness_plans/<plan_id>
@plan_bp.route('/users/<int:user_id>/fitness_plans/<int:plan_id>', methods=['PUT'])  # <-- 修正这里，改为完整路径
@token_required  # 认证用户
def update_user_fitness_plan(user_id, plan_id):
    """
    更新用户健身计划API
    请求体: JSON {status, end_date, etc.}
    响应: 200 OK 或错误信息
    """
    current_user_id = g.user_id

    if current_user_id != user_id:
        return jsonify({
            "error": "Forbidden",
            "message": "无权更新其他用户的健身计划。",
            "status_code": 403
        }), 403

    user_plan = FitnessPlan.query.filter_by(id=plan_id, user_id=user_id, is_preset=False).first()

    if not user_plan:
        return jsonify({
            "error": "Not Found",
            "message": "未找到指定健身计划或无权访问。",
            "status_code": 404
        }), 404

    data = request.get_json()

    if 'status' in data:
        user_plan.status = data['status']
    if 'end_date' in data:
        user_plan.end_date = data['end_date']

    try:
        db.session.commit()
        return jsonify({
            "message": "健身计划更新成功！",
            "data": {
                "plan_id": user_plan.id,
                "user_id": user_plan.user_id,
                "plan_name": user_plan.plan_name,
                "status": getattr(user_plan, 'status', None),
                "end_date": getattr(user_plan, 'end_date', None)
            },
            "status_code": 200
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "message": f"健身计划更新失败：{str(e)}", "status_code": 500}), 500
