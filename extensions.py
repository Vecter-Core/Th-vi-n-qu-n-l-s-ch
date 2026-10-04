"""Các extension Flask dùng chung (định nghĩa riêng để tránh import tuần hoàn)."""
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
