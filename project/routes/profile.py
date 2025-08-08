# file: project/routes/profile.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from project import db
from project.models import Booking, Dosen, User

profile_bp = Blueprint("profile", __name__)


# Endpoint untuk mendapatkan data profil pengguna saat ini
@profile_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User tidak ditemukan"}), 404
    return jsonify({"success": True, "data": user.to_json()})


# Endpoint untuk mengubah data profil pengguna saat ini
@profile_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if not data:
        return (
            jsonify({"success": False, "message": "Request body tidak boleh kosong"}),
            400,
        )

    # Update nama
    if "nama" in data:
        user.nama = data["nama"]
        # Jika user adalah dosen, update juga nama di tabel dosen agar konsisten
        if user.role == "dosen":
            dosen_profile = Dosen.query.filter_by(user_id=user.id).first()
            if dosen_profile:
                dosen_profile.nama_dosen = data["nama"]

    # Update username (cek duplikasi)
    if "username" in data and data["username"] != user.username:
        if User.query.filter_by(username=data["username"]).first():
            return (
                jsonify({"success": False, "message": "Username sudah digunakan"}),
                409,
            )
        user.username = data["username"]

    # Update password (hanya jika diisi)
    if "password" in data and data["password"]:
        user.set_password(data["password"])

    db.session.commit()
    return jsonify({"success": True, "message": "Profil berhasil diperbarui"})


# Endpoint untuk menghapus akun pengguna saat ini
@profile_bp.route("/profile", methods=["DELETE"])
@jwt_required()
def delete_profile():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    try:
        # Jika user adalah dosen, hapus juga semua booking yang terkait dengannya
        if user.role == "dosen":
            dosen_profile = Dosen.query.filter_by(user_id=user.id).first()
            if dosen_profile:
                Booking.query.filter_by(dosen_id=dosen_profile.id).delete()

        # Menghapus user akan otomatis menghapus profil dosen terkait karena 'cascade'
        db.session.delete(user)
        db.session.commit()
        return jsonify({"success": True, "message": "Akun berhasil dihapus"})
    except Exception as e:
        db.session.rollback()
        return (
            jsonify({"success": False, "message": f"Gagal menghapus akun: {str(e)}"}),
            500,
        )
