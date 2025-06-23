from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Silakan masuk untuk mengakses halaman ini.'

# Import models dan routes di sini untuk menghindari masalah import sirkular
# Mereka membutuhkan 'app' dan 'db' yang sudah diinisialisasi
from app import models, routes

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))