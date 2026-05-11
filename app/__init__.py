from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import boto3

db = SQLAlchemy()
login_manager = LoginManager()

def get_s3_client():
    from config import Config
    s3 = boto3.client(
        's3',
        aws_access_key_id=Config.AWS_ACCESS_KEY,
        aws_secret_access_key=Config.AWS_SECRET_KEY,
        region_name=Config.AWS_REGION
    )
    return s3

def create_app():
    from config import Config
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    from app.routes import main
    app.register_blueprint(main)

    return app