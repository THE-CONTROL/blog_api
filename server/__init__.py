from flask import Flask
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_jwt_extended import JWTManager

DB_NAME = "control.db"

db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'Random'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'Random'
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=5)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=9000)

    db.init_app(app)

    from .admin import admin
    from .user import user
    from .post import post
    from .comment import comment

    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(user, url_prefix='/user')
    app.register_blueprint(post, url_prefix='/posts')
    app.register_blueprint(comment, url_prefix='/comments')

    from .models import Admin, User, Post, Comment

    create_database(app)

    jwt.init_app(app)

    return app


def create_database(app):
    if not path.exists('server/' + DB_NAME):
        db.create_all(app=app)
