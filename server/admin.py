from flask import Blueprint, request, jsonify
import validators
from .models import user_schema, users_schema, User, Post, Comment, Admin, admin_schema, posts_schema, comments_schema, \
    post_schema
from . import db
from flask_jwt_extended import create_refresh_token, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import desc
from flask_cors import CORS
import cloudinary
import cloudinary.uploader
from flask_bcrypt import Bcrypt

admin = Blueprint('admin', __name__)

CORS(admin)
bcrypt = Bcrypt()

cloudinary.config(
    cloud_name="de49puo0s",
    api_key="282637876839251",
    api_secret="J8d0CPLJ4b6f_4uAtjgMVe4hEI0"
)

default = "http://res.cloudinary.com/de49puo0s/image/upload/v1656062130/q8azx8vnrpdehxjkh4bh.jpg"


@admin.route("/login", methods=['POST'])
def login():
    admin_name = request.json['admin_name']
    password = request.json['password']

    admin = Admin.query.filter_by(admin_name=admin_name).first()

    if admin and bcrypt.check_password_hash(admin.password, password):
        refresh = create_refresh_token(identity=admin.id)
        access = create_access_token(identity=admin.id)

        return jsonify({
            'user': {
                'refresh': refresh,
                'access': access
            },
            'message': 'Login successful!',
            'success': True
        }), 200

    else:
        return jsonify({'message': 'Check your login details!', 'success': False}), 400


@admin.route("/users/all", methods=['GET'])
@jwt_required()
def all_users():
    page = request.headers.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    all_users = User.query.order_by(desc(User.date)).paginate(page=page, per_page=per_page)
    result = users_schema.dump(all_users.items)

    meta = {
        "page": all_users.page,
        "pages": all_users.pages,
        "total_count": all_users.total,
        "prev_page": all_users.prev_num,
        "next_page": all_users.next_num,
        "has_prev": all_users.has_prev,
        "has_next": all_users.has_next
    }

    return jsonify({"result": result, "meta": meta}), 200


@admin.route("", methods=['GET'])
@jwt_required()
def admin_details():
    current_admin = get_jwt_identity()
    admin = Admin.query.filter_by(id=current_admin).first()
    return admin_schema.jsonify(admin), 200


@admin.route("/user/<username>", methods=['GET'])
@jwt_required()
def users_details(username):
    user = User.query.filter_by(username=username).first()
    return user_schema.jsonify(user), 200


@admin.route("/register", methods=['POST'])
def register():
    admin_name = request.json['admin_name']
    email = request.json['email']
    about = request.json['about']
    password1 = request.json['password1']
    password2 = request.json['password2']
    picture = request.json['picture']
    gender = request.json['gender']
    pronouns = request.json['pronouns']

    if len(admin_name) < 3:
        return jsonify({"message": "Admin name must be greater than two characters!", 'success': False}), 400
    if Admin.query.filter_by(admin_name=admin_name).first() is not None:
        return jsonify({"message": "Admin already exists!", 'success': False}), 409
    if not validators.email(email):
        return jsonify({"message": "Email not valid!", 'success': False}), 400
    if Admin.query.filter_by(email=email).first() is not None:
        return jsonify({"message": "Email already exists!", 'success': False}), 409
    if not gender:
        return jsonify({"message": "Select a gender!", 'success': False}), 400
    if len(password1) < 6:
        return jsonify({"message": "Password must be greater than five characters!", 'success': False}), 400
    if password1 != password2:
        return jsonify({"message": "Passwords don't match!", 'success': False}), 400

    if picture:
        cloud_picture = cloudinary.uploader.upload(picture)
        url = cloud_picture.get("url")
    else:
        url = default

    password = bcrypt.generate_password_hash(password1).decode("utf-8")

    admin = Admin(admin_name, email, about, password, url, gender, pronouns)
    db.session.add(admin)
    db.session.commit()

    return jsonify({"message": "User Created!", 'success': True}), 201


@admin.route("/update", methods=['PUT'])
@jwt_required()
def update_admin():
    admin_name = request.json['admin_name']
    email = request.json['email']
    about = request.json['about']
    picture = request.json['picture']
    gender = request.json['gender']
    pronouns = request.json['pronouns']

    if len(admin_name) < 3:
        return jsonify({"message": "Admin name must be greater than two characters!"}), 400
    if not validators.email(email):
        return jsonify({"message": "Email not valid!"}), 400
    if not gender:
        return jsonify({"message": "Select a gender!"}), 400

    if picture:
        cloud_picture = cloudinary.uploader.upload(picture)
        url = cloud_picture.get("url")
    else:
        url = default

    current_admin = get_jwt_identity()
    admin = Admin.query.filter_by(id=current_admin).first()

    admin.admin_name = admin_name
    admin.email = email
    admin.about = about
    admin.picture = url
    admin.gender = gender
    admin.pronouns = pronouns

    db.session.commit()

    return jsonify({"message": "Profile Updated!", "success": True}), 202


@admin.route("/delete", methods=['DELETE'])
@jwt_required()
def delete_admin():
    current_admin = get_jwt_identity()
    admin = Admin.query.filter_by(id=current_admin).first()
    db.session.delete(admin)
    db.session.commit()
    return jsonify({"message": "User deleted!", "success": True}), 204


@admin.route("/user/delete/<id>", methods=['DELETE'])
@jwt_required()
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    posts = Post.query.filter_by(user_id=id).all()
    comments = Comment.query.filter_by(user_id=id).all()

    if posts:
        for post in posts:
            db.session.delete(post)

    if comments:
        for comment in comments:
            db.session.delete(comment)

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted!", "success": True}), 204


@admin.route("/posts", methods=['GET', 'POST'])
@jwt_required()
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


@admin.route("/user/posts/<username>", methods=['GET'])
@jwt_required()
def user_posts(username):
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


@admin.route("/comments", methods=['GET'])
@jwt_required()
def comments():
    page = request.headers.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    all_comments = Comment.query.order_by(desc(Comment.date)).paginate(page=page, per_page=per_page)
    result = comments_schema.dump(all_comments.items)

    meta = {
        "page": all_comments.page,
        "pages": all_comments.pages,
        "total_count": all_comments.total,
        "prev_page": all_comments.prev_num,
        "next_page": all_comments.next_num,
        "has_prev": all_comments.has_prev,
        "has_next": all_comments.has_next
    }

    return jsonify({"result": result, "meta": meta}), 200


@admin.route("/post/comments/<id>", methods=['GET'])
@jwt_required()
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


@admin.route("/user/comments/<username>", methods=['GET'])
@jwt_required()
def user_comments(username):
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


@admin.route("/posts/<id>", methods=['GET'])
@jwt_required()
def post_details(id):
    post = Post.query.get(id)
    result = post_schema.dump(post)
    return jsonify({"result": result}), 200


@admin.route("/posts/delete/<id>", methods=['DELETE'])
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


@admin.route("/comments/delete/<id>", methods=['DELETE'])
@jwt_required()
def delete_comment(id):
    comment = Comment.query.get(id)
    db.session.delete(comment)
    db.session.commit()
    return jsonify({"message": "Comment deleted!", "success": True}), 204


@admin.route("/refresh", methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)
    return jsonify({"access": access}), 200



