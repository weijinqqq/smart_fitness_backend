# routes/forum.py 论坛路由

from flask import Blueprint, request, jsonify, g
from models import db, Post, Comment, User  # 导入 Post, Comment, User 模型
from utils.auth_decorators import token_required
from sqlalchemy.exc import IntegrityError  # 导入 IntegrityError 用于处理数据库约束错误

# 创建蓝图
forum_bp = Blueprint('forum_bp', __name__)


# --- 创建新帖子 API ---
# POST /forum/posts
@forum_bp.route('/forum/posts', methods=['POST'])
@token_required
def create_post():
    """
    创建新帖子API
    请求体: JSON {title, content}
    响应: 201 Created 或错误信息
    """
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    user_id = g.user_id  # 从认证信息中获取用户ID

    if not title or not content:
        return jsonify({
            "error": "Missing required fields",
            "message": "Title and content are required to create a post."
        }), 400

    try:
        new_post = Post(user_id=user_id, title=title, content=content)
        db.session.add(new_post)
        db.session.commit()
        return jsonify({
            "message": "Post created successfully",
            "post_id": new_post.id,
            "title": new_post.title
        }), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Database Error",
            "message": "Failed to create post due to database constraint."
        }), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


# --- 获取所有帖子 API ---
# GET /forum/posts
@forum_bp.route('/forum/posts', methods=['GET'])
def get_all_posts():
    """
    获取所有帖子API
    支持分页、排序、筛选 (待扩展)
    响应: 200 OK，返回帖子列表
    """
    # 暂时不加认证，允许所有用户浏览帖子，如果需要登录才能看，则添加 @token_required
    # @token_required

    # 可以添加查询参数进行分页和筛选，例如:
    # page = request.args.get('page', 1, type=int)
    # per_page = request.args.get('per_page', 10, type=int)
    # query = Post.query.order_by(Post.created_at.desc()) # 默认按创建时间倒序
    # posts = query.paginate(page=page, per_page=per_page, error_out=False)
    # posts_list = [post.to_dict() for post in posts.items]

    posts = Post.query.order_by(Post.created_at.desc()).all()
    posts_list = [post.to_dict() for post in posts]  # 不包含评论，如果需要则 post.to_dict(include_comments=True)

    return jsonify({
        "count": len(posts_list),
        "posts": posts_list
    }), 200


# --- 获取单个帖子详情 API ---
# GET /forum/posts/<post_id>
@forum_bp.route('/forum/posts/<int:post_id>', methods=['GET'])
def get_post_detail(post_id):
    """
    获取单个帖子详情及其评论API
    响应: 200 OK 或 404 Not Found
    """
    # 暂时不加认证，允许所有用户浏览帖子，如果需要登录才能看，则添加 @token_required
    # @token_required

    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Not Found", "message": "Post not found."}), 404

    # 返回帖子详情，并包含其所有评论
    return jsonify({
        "message": "Post retrieved successfully",
        "data": post.to_dict(include_comments=True)  # 包含评论
    }), 200


# --- 更新帖子 API ---
# PUT /forum/posts/<post_id>
@forum_bp.route('/forum/posts/<int:post_id>', methods=['PUT'])
@token_required
def update_post(post_id):
    """
    更新帖子API
    请求体: JSON {title, content}
    响应: 200 OK 或错误信息
    """
    data = request.get_json()
    user_id = g.user_id  # 当前认证用户ID

    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Not Found", "message": "Post not found."}), 404

    # 授权检查：只有发帖人才能更新帖子
    if post.user_id != user_id:
        return jsonify({"error": "Forbidden", "message": "You are not authorized to update this post."}), 403

    if 'title' in data:
        post.title = data['title']
    if 'content' in data:
        post.content = data['content']

    try:
        db.session.commit()
        return jsonify({
            "message": "Post updated successfully",
            "data": post.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


# --- 删除帖子 API ---
# DELETE /forum/posts/<post_id>
@forum_bp.route('/forum/posts/<int:post_id>', methods=['DELETE'])
@token_required
def delete_post(post_id):
    """
    删除帖子API
    响应: 200 OK 或 204 No Content 或错误信息
    """
    user_id = g.user_id  # 当前认证用户ID

    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Not Found", "message": "Post not found."}), 404

    # 授权检查：只有发帖人才能删除帖子
    if post.user_id != user_id:
        return jsonify({"error": "Forbidden", "message": "You are not authorized to delete this post."}), 403

    try:
        db.session.delete(post)
        db.session.commit()
        return jsonify({"message": "Post deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


# --- 创建评论 API ---
# POST /forum/posts/<post_id>/comments
@forum_bp.route('/forum/posts/<int:post_id>/comments', methods=['POST'])
@token_required
def create_comment(post_id):
    """
    为帖子创建评论API
    请求体: JSON {content}
    响应: 201 Created 或错误信息
    """
    data = request.get_json()
    content = data.get('content')
    user_id = g.user_id  # 当前认证用户ID

    if not content:
        return jsonify({"error": "Missing required fields", "message": "Comment content is required."}), 400

    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Not Found", "message": "Post not found."}), 404

    try:
        new_comment = Comment(post_id=post_id, user_id=user_id, content=content)
        db.session.add(new_comment)
        db.session.commit()
        return jsonify({
            "message": "Comment created successfully",
            "comment_id": new_comment.id,
            "content": new_comment.content
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


# --- 删除评论 API ---
# DELETE /forum/comments/<comment_id>
@forum_bp.route('/forum/comments/<int:comment_id>', methods=['DELETE'])
@token_required
def delete_comment(comment_id):
    """
    删除评论API
    响应: 200 OK 或 204 No Content 或错误信息
    """
    user_id = g.user_id  # 当前认证用户ID

    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({"error": "Not Found", "message": "Comment not found."}), 404

    # 授权检查：只有评论的作者才能删除评论
    if comment.user_id != user_id:
        return jsonify({"error": "Forbidden", "message": "You are not authorized to delete this comment."}), 403

    try:
        db.session.delete(comment)
        db.session.commit()
        return jsonify({"message": "Comment deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500