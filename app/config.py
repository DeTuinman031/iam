# app/config.py
import os

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-change-me")  # used for sessions, CSRF
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://iam_user:iam_pass@localhost:3306/iam"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Login behavior
    REMEMBER_COOKIE_DURATION = 3600 * 24 * 7  # 7 days (tweak later)

    # Where to send unauthenticated users
    LOGIN_VIEW = "auth.login_page"

class DevConfig(Config):
    DEBUG = True

class ProdConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # only over HTTPS
    REMEMBER_COOKIE_SECURE = True