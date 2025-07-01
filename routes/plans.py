#健身计划路由

from flask import Blueprint, request, jsonify
from app.models import FitnessPlan, db
from app.utils import auth_required

# 创建蓝图，用于组织健身计划相关路由
bp = Blueprint('plans', __name__)

@bp.route('/fitness_plans/preset', methods=['GET'])
def get_preset_plans():
    """
    获取系统预设健身计划API
    无需认证，所有用户可访问
    """
    try:
        # 查询所有预设计划
        preset_plans = FitnessPlan.query.filter_by(is_preset=True).all()
        
        return jsonify({
            "count": len(preset_plans),
            "plans": [plan.to_dict() for plan in preset_plans]
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Database error",
            "message": str(e)
        }), 500

@bp.route('/users/<int:user_id>/fitness_plans', methods=['POST'])
@auth_required
def create_or_select_plan(user_id):
    """
    用户创建或选择健身计划API
    两种方式:
    1. 选择现有预设计划: 提供plan_id
    2. 创建新计划: 提供plan_name和content
    """
    # 验证请求用户只能操作自己的数据
    current_user_id = getattr(request, 'current_user_id', None)
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

@bp.route('/users/<int:user_id>/fitness_plans', methods=['GET'])
@auth_required
def get_user_plans(user_id):
    """
    获取用户的所有健身计划API
    只返回用户自定义计划（非预设）
    """
    # 验证请求用户只能访问自己的数据
    current_user_id = getattr(request, 'current_user_id', None)
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
