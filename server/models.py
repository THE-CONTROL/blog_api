from flask import Blueprint
from datetime import datetime
from . import db
from flask_marshmallow import Marshmallow

models = Blueprint('models', __name__)

ma = Marshmallow()


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_name = db.Column(db.String(1000), nullable=False, unique=True)
    email = db.Column(db.String(1000), nullable=False, unique=True)
    about = db.Column(db.String(1000))
    password = db.Column(db.String(1000), nullable=False)
    picture = db.Column(db.String(1000))
    gender = db.Column(db.String(1000))
    pronouns = db.Column(db.String(1000))
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, admin_name, email, about, password, picture, gender, pronouns):
        self.admin_name = admin_name
        self.email = email
        self.about = about
        self.password = password
        self.picture = picture
        self.gender = gender
        self.pronouns = pronouns


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(1000), nullable=False, unique=True)
    email = db.Column(db.String(1000), nullable=False, unique=True)
    about = db.Column(db.String(1000))
    password = db.Column(db.String(1000), nullable=False)
    picture = db.Column(db.String(1000))
    gender = db.Column(db.String(1000))
    pronouns = db.Column(db.String(1000))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship("Post", backref="user")
    comments = db.relationship("Comment", backref="user")

    def __init__(self, username, email, about, password, picture, gender, pronouns):
        self.username = username
        self.email = email
        self.about = about
        self.password = password
        self.picture = picture
        self.gender = gender
        self.pronouns = pronouns


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    heading = db.Column(db.String(1000))
    content = db.Column(db.String(1000))
    image = db.Column(db.String(1000))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship("Comment", backref="post")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user_image = db.Column(db.String(1000))
    username = db.Column(db.String(1000))

    def __init__(self, heading, content, image, user_id, user_image, username):
        self.heading = heading
        self.content = content
        self.image = image
        self.user_id = user_id
        self.user_image = user_image
        self.username = username


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000))
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_image = db.Column(db.String(1000))
    username = db.Column(db.String(1000))

    def __init__(self, content, post_id, user_id, user_image, username):
        self.content = content
        self.post_id = post_id
        self.user_id = user_id
        self.user_image = user_image
        self.username = username


class AdminSchema(ma.Schema):
    class Meta:
        fields = ('id', 'admin_name', 'email', 'about', 'password', 'picture', 'gender', 'pronouns', 'date')


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'email', 'about', 'password', 'picture', 'gender', 'pronouns', 'date')


class PostSchema(ma.Schema):
    class Meta:
        fields = ('id', 'heading', 'content', 'image', 'user_id', 'date', 'user_image', 'username')


class CommentSchema(ma.Schema):
    class Meta:
        fields = ('id', 'content', 'post_id', 'user_id', 'date', 'user_image', 'username')


admin_schema = AdminSchema()
admins_schema = AdminSchema(many=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

post_schema = PostSchema()
posts_schema = PostSchema(many=True)

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)
