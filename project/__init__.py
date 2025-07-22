# file: project/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_jwt_extended import JWTManager # <-- 1. Tambahkan import ini

# Inisialisasi ekstensi
db = SQLAlchemy()
jwt = JWTManager() # <-- Inisialisasi di luar agar bisa diakses

def create_app(config_class=Config):
    """
    Membuat dan mengkonfigurasi instance aplikasi Flask.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inisialisasi ekstensi dengan aplikasi
    db.init_app(app)
    jwt.init_app(app) # <-- 2. Hubungkan JWTManager dengan aplikasi Anda

    # Import dan daftarkan Blueprint (rute) dari modul lain
    from project.routes.auth import auth_bp
    from project.routes.dosen import dosen_bp
    from project.routes.booking import booking_bp
    from project.routes.user import user_bp
    from project.routes.profile import profile_bp

    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(dosen_bp, url_prefix='/')
    app.register_blueprint(booking_bp, url_prefix='/')
    app.register_blueprint(user_bp, url_prefix='/')
    app.register_blueprint(profile_bp, url_prefix='/')

    with app.app_context():
        db.create_all()

    return app
