from flask import Blueprint, request, jsonify
from sqlalchemy import desc
from .models import User, Post, post_schema, posts_schema, Comment
from . import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import CORS
import cloudinary
import cloudinary.uploader

post = Blueprint('post', __name__)

CORS(post)

cloudinary.config(
    cloud_name="de49puo0s",
    api_key="282637876839251",
    api_secret="J8d0CPLJ4b6f_4uAtjgMVe4hEI0"
)


@post.route("/all", methods=['GET', 'POST'])
def posts():
    page = request.headers.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    all_posts = Post.query.order_by(desc(Post.date)).paginate(page=page, per_page=per_page)
    result = posts_schema.dump(all_posts.items)

    meta = {
        "page": all_posts.page,
        "pages": all_posts.pages,
        "total_count": all_posts.total,
        "prev_page": all_posts.prev_num,
        "next_page": all_posts.next_num,
        "has_prev": all_posts.has_prev,
        "has_next": all_posts.has_next
    }

    return jsonify({"result": result, "meta": meta}), 200


@post.route("/user", methods=['GET'])
@jwt_required()
def user_posts():
    page = request.headers.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    current_user = get_jwt_identity()
    all_posts = Post.query.order_by(desc(Post.date)).filter_by(user_id=current_user).paginate(page=page, per_page=per_page)
    result = posts_schema.dump(all_posts.items)

    meta = {
        "page": all_posts.page,
        "pages": all_posts.pages,
        "total_count": all_posts.total,
        "prev_page": all_posts.prev_num,
        "next_page": all_posts.next_num,
        "has_prev": all_posts.has_prev,
        "has_next": all_posts.has_next
    }

    return jsonify({"result": result, "meta": meta}), 200


@post.route("/user/<username>", methods=['GET'])
def other_user_posts(username):
    page = request.headers.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    all_posts = Post.query.order_by(desc(Post.date)).filter_by(username=username).paginate(page=page, per_page=per_page)
    result = posts_schema.dump(all_posts.items)

    meta = {
        "page": all_posts.page,
        "pages": all_posts.pages,
        "total_count": all_posts.total,
        "prev_page": all_posts.prev_num,
        "next_page": all_posts.next_num,
        "has_prev": all_posts.has_prev,
        "has_next": all_posts.has_next
    }

    return jsonify({"result": result, "meta": meta}), 200


@post.route("/<id>", methods=['GET'])
def post_details(id):
    post = Post.query.get(id)
    result = post_schema.dump(post)
    return jsonify({"result": result}), 200


@post.route("/add", methods=['POST'])
@jwt_required()
def add_post():
    heading = request.json['heading']
    content = request.json['content']
    image = request.json['image']
    current_user = get_jwt_identity()

    if len(heading) < 10:
        return jsonify({"message": "Heading must be greater than nine characters!", "success": False}), 400
    if len(content) < 30:
        return jsonify({"message": "Content must be greater than thirty characters!", "success": False}), 400
    if image:
        cloud_picture = cloudinary.uploader.upload(image)
        url = cloud_picture.get("url")
    else:
        url = image

    user = User.query.filter_by(id=current_user).first()
    posts = Post(heading, content, url, user.id, user.picture, user.username)
    db.session.add(posts)
    db.session.commit()

    return jsonify({"message": "Post Created!", "success": True}), 201


@post.route("/update/<id>", methods=['PUT'])
@jwt_required()
def update_post(id):
    post = Post.query.get(id)
    heading = request.json['heading']
    content = request.json['content']
    image = request.json['image']

    if len(heading) < 10:
        return jsonify({"message": "Heading must be greater than nine characters!", "success": False}), 400
    if len(content) < 30:
        return jsonify({"message": "Content must be greater than thirty characters!", "success": False}), 400

    if image:
        cloud_picture = cloudinary.uploader.upload(image)
        url = cloud_picture.get("url")
    else:
        url = image

    post.heading = heading
    post.content = content
    post.image = url
    db.session.commit()

    return jsonify({"message": "Post updated!", "success": True}), 202


@post.route("/delete/<id>", methods=['DELETE'])
@jwt_required()
def delete_post(id):
    post = Post.query.get(id)
    comments = Comment.query.filter_by(post_id=id).all()

    if comments:
        for comment in comments:
            db.session.delete(comment)

    db.session.delete(post)
    db.session.commit()

    return jsonify({"message": "Post Deleted!", "success": True}), 204
