from flask import Blueprint, request, jsonify
import validators
from .models import user_schema, User, Post, Comment
from . import db
from flask_jwt_extended import create_refresh_token, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import cloudinary
import cloudinary.uploader
from flask_bcrypt import Bcrypt

user = Blueprint('user', __name__)

CORS(user)
bcrypt = Bcrypt()

cloudinary.config(
    cloud_name="de49puo0s",
    api_key="282637876839251",
    api_secret="J8d0CPLJ4b6f_4uAtjgMVe4hEI0"
)

default = "http://res.cloudinary.com/de49puo0s/image/upload/v1656062130/q8azx8vnrpdehxjkh4bh.jpg"


@user.route("/login", methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        refresh = create_refresh_token(identity=user.id)
        access = create_access_token(identity=user.id)

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


@user.route("", methods=['GET'])
@jwt_required()
def user_details():
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user).first()
    return user_schema.jsonify(user), 200


@user.route("/<username>", methods=['GET'])
def other_users_details(username):
    user = User.query.filter_by(username=username).first()
    return user_schema.jsonify(user), 200


@user.route("/register", methods=['POST'])
def register():
    username = request.json['username']
    email = request.json['email']
    about = request.json['about']
    password1 = request.json['password1']
    password2 = request.json['password2']
    picture = request.json['picture']
    gender = request.json['gender']
    pronouns = request.json['pronouns']

    if len(username) < 3:
        return jsonify({"message": "Username must be greater than two characters!", 'success': False}), 400
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({"message": "User already exists!", 'success': False}), 409
    if not validators.email(email):
        return jsonify({"message": "Email not valid!", 'success': False}), 400
    if User.query.filter_by(email=email).first() is not None:
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

    user = User(username, email, about, password, url, gender, pronouns)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User Created!", 'success': True}), 201


@user.route("/update", methods=['PUT'])
@jwt_required()
def update_user():
    username = request.json['username']
    email = request.json['email']
    about = request.json['about']
    picture = request.json['picture']
    gender = request.json['gender']
    pronouns = request.json['pronouns']

    if len(username) < 3:
        return jsonify({"message": "Username must be greater than two characters!"}), 400
    if not validators.email(email):
        return jsonify({"message": "Email not valid!"}), 400
    if not gender:
        return jsonify({"message": "Select a gender!"}), 400

    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user).first()
    posts = Post.query.filter_by(user_id=current_user).all()
    comments = Comment.query.filter_by(user_id=current_user).all()

    if picture:
        cloud_picture = cloudinary.uploader.upload(picture)
        url = cloud_picture.get("url")
    else:
        url = default

    user.username = username
    user.email = email
    user.about = about
    user.picture = url
    user.gender = gender
    user.pronouns = pronouns

    if posts:
        for post in posts:
            post.username = username
            post.user_image = picture

    if comments:
        for comment in comments:
            comment.username = username
            comment.user_image = picture

    db.session.commit()

    return jsonify({"message": "Profile Updated!", "success": True}), 202


@user.route("/delete", methods=['DELETE'])
@jwt_required()
def delete_user():
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user).first()
    posts = Post.query.filter_by(user_id=current_user).all()
    comments = Comment.query.filter_by(user_id=current_user).all()

    db.session.delete(user)
    if posts:
        for post in posts:
            db.session.delete(post)

    if comments:
        for comment in comments:
            db.session.delete(comment)

    db.session.commit()

    return jsonify({"message": "User deleted!", "success": True}), 204


@user.route("/refresh", methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)
    return jsonify({"access": access}), 200
