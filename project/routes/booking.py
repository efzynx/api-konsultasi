# file: project/routes/booking.py
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from project import db
from project.models import Booking, Dosen, User

booking_bp = Blueprint("booking", __name__)


@booking_bp.route("/booking", methods=["GET"])
@jwt_required()
def get_all_bookings():
    user_id = get_jwt_identity()
    claims = get_jwt()
    user_role = claims.get("role")

    query = Booking.query

    if user_role == "mahasiswa":
        user_nim = claims.get("nim")
        if not user_nim:
            return (
                jsonify(
                    {"success": False, "message": "NIM tidak ditemukan untuk mahasiswa"}
                ),
                400,
            )
        query = query.filter_by(nim=user_nim)
    elif user_role == "dosen":
        dosen_profile = Dosen.query.filter_by(user_id=user_id).first()
        if not dosen_profile:
            return (
                jsonify({"success": False, "message": "Profil dosen tidak ditemukan"}),
                404,
            )
        query = query.filter_by(dosen_id=dosen_profile.id)

    all_bookings = query.order_by(Booking.tanggal.desc(), Booking.jam.desc()).all()
    result = [booking.to_json() for booking in all_bookings]
    return jsonify(
        {"success": True, "message": "Data booking berhasil diambil", "data": result}
    )


@booking_bp.route("/booking", methods=["POST"])
@jwt_required()
def create_booking():
    data = request.get_json()
    required_fields = [
        "nama_mahasiswa",
        "nim",
        "dosen_id",
        "tanggal",
        "jam",
        "topik_konsultasi",
    ]
    if not all(field in data for field in required_fields):
        return jsonify({"success": False, "message": "Data input tidak lengkap"}), 400

    try:
        new_booking = Booking(
            nama_mahasiswa=data["nama_mahasiswa"],
            nim=data["nim"],
            dosen_id=data["dosen_id"],
            tanggal=datetime.strptime(data["tanggal"], "%Y-%m-%d").date(),
            jam=datetime.strptime(data["jam"], "%H:%M:%S").time(),
            topik_konsultasi=data["topik_konsultasi"],
        )
        db.session.add(new_booking)
        db.session.commit()
        return jsonify({"success": True, "message": "Booking berhasil dibuat"}), 201
    except Exception as e:
        return (
            jsonify({"success": False, "message": f"Gagal membuat booking: {str(e)}"}),
            500,
        )


@booking_bp.route("/booking/<int:id>", methods=["PUT"])
@jwt_required()
def update_booking(id):
    booking = Booking.query.get_or_404(id)
    user_id = get_jwt_identity()
    claims = get_jwt()
    user_role = claims.get("role")
    data = request.get_json()

    # Validasi Hak Akses
    if user_role == "mahasiswa" and booking.nim != claims.get("nim"):
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Akses ditolak: Anda bukan pemilik booking ini",
                }
            ),
            403,
        )

    dosen_profile = Dosen.query.filter_by(user_id=user_id).first()
    if user_role == "dosen" and (
        not dosen_profile or booking.dosen_id != dosen_profile.id
    ):
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Akses ditolak: Anda bukan dosen yang bersangkutan",
                }
            ),
            403,
        )

    # Logika Pembaruan Berdasarkan Peran
    if user_role == "dosen":
        if "status" in data and data["status"] in ["approved", "rejected", "pending"]:
            booking.status = data["status"]
        else:
            return (
                jsonify(
                    {"success": False, "message": "Dosen hanya dapat mengubah status"}
                ),
                400,
            )
    elif user_role == "mahasiswa":
        booking.tanggal = datetime.strptime(
            data.get("tanggal", str(booking.tanggal)), "%Y-%m-%d"
        ).date()
        booking.jam = datetime.strptime(
            data.get("jam", str(booking.jam)), "%H:%M:%S"
        ).time()
        booking.topik_konsultasi = data.get(
            "topik_konsultasi", booking.topik_konsultasi
        )

    db.session.commit()
    return jsonify(
        {
            "success": True,
            "message": "Booking berhasil diubah",
            "data": booking.to_json(),
        }
    )


@booking_bp.route("/booking/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_booking(id):
    booking = Booking.query.get_or_404(id)
    claims = get_jwt()
    user_role = claims.get("role")

    # Hanya mahasiswa pemilik booking yang bisa menghapus
    if user_role != "mahasiswa" or booking.nim != claims.get("nim"):
        return jsonify({"success": False, "message": "Akses ditolak"}), 403

    db.session.delete(booking)
    db.session.commit()
    return jsonify({"success": True, "message": "Booking berhasil dihapus"})
