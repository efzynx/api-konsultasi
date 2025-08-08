# project/routes/user.py
# Berisi endpoint untuk mengelola data user (mahasiswa/dosen)

from flask import Blueprint, jsonify, request

from project import db
from project.models import User

user_bp = Blueprint("user", __name__)


# ENDPOINT BARU: Untuk melihat daftar semua mahasiswa
@user_bp.route("/mahasiswa", methods=["GET"])
def get_all_mahasiswa():
    try:
        # Ambil semua user yang rolenya 'mahasiswa'
        mahasiswa_list = User.query.filter_by(role="mahasiswa").all()
        # Ubah setiap objek user menjadi format JSON
        result = [user.to_json() for user in mahasiswa_list]
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return (
            jsonify({"success": False, "message": f"Gagal mengambil data: {str(e)}"}),
            500,
        )


# Endpoint untuk mengubah data user (misal: ganti nama atau password)
@user_bp.route("/user/<int:id>", methods=["PUT"])
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json()

    if not data:
        return (
            jsonify({"success": False, "message": "Request body tidak boleh kosong"}),
            400,
        )

    # Update field jika ada di request body
    user.nama = data.get("nama", user.nama)
    user.nim = data.get("nim", user.nim)

    # Jika ada password baru, hash password tersebut
    if "password" in data and data["password"]:
        user.set_password(data["password"])

    db.session.commit()
    return jsonify({"success": True, "message": "Data user berhasil diubah"})


# Endpoint untuk menghapus user (mahasiswa)
@user_bp.route("/user/<int:id>", methods=["DELETE"])
def delete_user(id):
    user = User.query.get_or_404(id)

    # Logika keamanan sederhana: hanya mahasiswa yang bisa dihapus lewat sini.
    # Dosen harus dihapus lewat endpoint /dosen untuk konsistensi data.
    if user.role != "mahasiswa":
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Hanya user mahasiswa yang bisa dihapus melalui endpoint ini",
                }
            ),
            403,
        )

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"success": True, "message": "User mahasiswa berhasil dihapus"})
    except Exception as e:
        db.session.rollback()
        return (
            jsonify({"success": False, "message": f"Gagal menghapus user: {str(e)}"}),
            500,
        )
