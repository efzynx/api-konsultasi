# project/__init__.py
# File ini berfungsi sebagai "pabrik" aplikasi.
# Tugasnya adalah menginisialisasi Flask, database, dan mendaftarkan semua rute.

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Inisialisasi ekstensi SQLAlchemy
db = SQLAlchemy()

def create_app(config_class=Config):
    """
    Membuat dan mengkonfigurasi instance aplikasi Flask.
    Ini adalah pola 'Application Factory'.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    # Import dan daftarkan Blueprint (rute) dari modul lain
    from project.routes.auth import auth_bp
    from project.routes.dosen import dosen_bp
    from project.routes.booking import booking_bp
    # PERBAIKAN: Import blueprint user yang baru
    from project.routes.user import user_bp

    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(dosen_bp, url_prefix='/')
    app.register_blueprint(booking_bp, url_prefix='/')
    # PERBAIKAN: Daftarkan blueprint user yang baru
    app.register_blueprint(user_bp, url_prefix='/')

    with app.app_context():
        db.create_all()

    return app
