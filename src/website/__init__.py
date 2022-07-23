from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

database_for_chess = SQLAlchemy()
DB_NAME = "baza.db"


def create_app():

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ChessApp6969'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    database_for_chess.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    create_database(app)

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        database_for_chess.create_all(app=app)
        print('Created Database!')