from flask import Blueprint, request, jsonify
from sqlalchemy import desc
from .models import User, Comment, Post, comments_schema
from . import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import CORS

comment = Blueprint('comment', __name__)

CORS(comment)


@comment.route("/post/<id>", methods=['GET'])
def post_comments(id):
    page = request.headers.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    post_comments = Comment.query.filter_by(post_id=id).paginate(page=page, per_page=per_page)
    result = comments_schema.dump(post_comments.items)

    meta = {
        "page": post_comments.page,
        "pages": post_comments.pages,
        "total_count": post_comments.total,
        "prev_page": post_comments.prev_num,
        "next_page": post_comments.next_num,
        "has_prev": post_comments.has_prev,
        "has_next": post_comments.has_next
    }

    return jsonify({"result": result, "meta": meta}), 200


@comment.route("/user", methods=['GET'])
@jwt_required()
def user_comments():
    current_user = get_jwt_identity()
    page = request.headers.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    user_comments = Comment.query.order_by(desc(Comment.date)).filter_by(user_id=current_user).paginate(page=page, per_page=per_page)
    result = comments_schema.dump(user_comments.items)

    meta = {
        "page": user_comments.page,
        "pages": user_comments.pages,
        "total_count": user_comments.total,
        "prev_page": user_comments.prev_num,
        "next_page": user_comments.next_num,
        "has_prev": user_comments.has_prev,
        "has_next": user_comments.has_next
    }

    return jsonify({"result": result, "meta": meta}), 200


@comment.route("/<username>", methods=['GET'])
def other_user_comments(username):
    page = request.headers.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    user_comments = Comment.query.order_by(desc(Comment.date)).filter_by(username=username).paginate(page=page, per_page=per_page)
    result = comments_schema.dump(user_comments.items)

    meta = {
        "page": user_comments.page,
        "pages": user_comments.pages,
        "total_count": user_comments.total,
        "prev_page": user_comments.prev_num,
        "next_page": user_comments.next_num,
        "has_prev": user_comments.has_prev,
        "has_next": user_comments.has_next
    }

    return jsonify({"result": result, "meta": meta}), 200


@comment.route("/add/<id>", methods=['POST'])
@jwt_required()
def add_comment(id):
    current_user = get_jwt_identity()
    content = request.json['content']
    post = Post.query.get(id)
    user = User.query.filter_by(id=current_user).first()

    if len(content) == 0:
        return jsonify({"message": "Content must not be empty!", "success": False}), 400

    comment = Comment(content, post.id, user.id, user.picture, user.username)
    db.session.add(comment)
    db.session.commit()

    return jsonify({"message": "Comment added!", "success": True}), 201


@comment.route("/update/<id>", methods=['PUT'])
@jwt_required()
def update_comment(id):
    content = request.json['content']
    comment = Comment.query.get(id)

    if len(content) == 0:
        return jsonify({"message": "Content must not be empty!", "success": False}), 400

    comment.content = content
    db.session.commit()

    return jsonify({"message": "Comment updated!", "success": True}), 202


@comment.route("/delete/<id>", methods=['DELETE'])
@jwt_required()
def delete_comment(id):
    comment = Comment.query.get(id)
    db.session.delete(comment)
    db.session.commit()
    return jsonify({"message": "Comment deleted!", "success": True})
