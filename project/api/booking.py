"""
Booking API endpoints with Flask-RESTX documentation
"""

from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from project.models import Booking, Dosen, User
from project import db
from project.api_models_simple import get_models

# Create namespace
booking_ns = Namespace("booking", description="Booking management operations")

# Get models
models = get_models(booking_ns)
booking_response_model = models["booking_model"]
booking_create = models["booking_create_model"]
booking_update = models["booking_update_model"]
booking_list_response = models["booking_list_response_model"]
success_response = models["success_response_model"]
error_model = models["error_response_model"]


@booking_ns.route("/")
class BookingList(Resource):
    @booking_ns.doc("get_all_bookings", security="Bearer")
    @booking_ns.marshal_with(booking_list_response)
    @booking_ns.response(401, "Unauthorized", error_model)
    @booking_ns.response(500, "Internal Server Error", error_model)
    @jwt_required()
    def get(self):
        """Get all bookings (filtered by user role)"""
        try:
            current_user_id = get_jwt_identity()
            claims = get_jwt()
            user_role = claims.get("role")

            if user_role == "dosen":
                # Dosen can see bookings for their consultations
                dosen = Dosen.query.filter_by(user_id=current_user_id).first()
                if not dosen:
                    return {
                        "success": False,
                        "message": "Data dosen tidak ditemukan",
                    }, 404

                bookings = Booking.query.filter_by(dosen_id=dosen.id).all()
            else:
                # Mahasiswa can see their own bookings
                user = User.query.get(current_user_id)
                if not user:
                    return {"success": False, "message": "User tidak ditemukan"}, 404

                bookings = Booking.query.filter_by(nim=user.nim).all()

            result = [booking.to_json() for booking in bookings]
            return {
                "success": True,
                "message": "Data booking berhasil diambil",
                "data": result,
            }
        except Exception as e:
            return {"success": False, "message": f"Gagal mengambil data: {str(e)}"}, 500

    @booking_ns.doc("create_booking", security="Bearer")
    @booking_ns.expect(booking_create, validate=True)
    @booking_ns.marshal_with(success_response, code=201)
    @booking_ns.response(400, "Validation Error", error_model)
    @booking_ns.response(401, "Unauthorized", error_model)
    @booking_ns.response(403, "Forbidden - Dosen cannot create bookings", error_model)
    @booking_ns.response(404, "Dosen Not Found", error_model)
    @jwt_required()
    def post(self):
        """Create new booking (mahasiswa only)"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get("role")

        # Only mahasiswa can create bookings
        if user_role != "mahasiswa":
            return {
                "success": False,
                "message": "Hanya mahasiswa yang dapat membuat booking",
            }, 403

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
            return {"success": False, "message": "Data tidak lengkap"}, 400

        # Check if dosen exists
        dosen = Dosen.query.get(data["dosen_id"])
        if not dosen:
            return {"success": False, "message": "Dosen tidak ditemukan"}, 404

        try:
            from datetime import datetime

            # Parse date and time strings
            tanggal = datetime.strptime(data["tanggal"], "%Y-%m-%d").date()
            jam = datetime.strptime(data["jam"], "%H:%M:%S").time()

            new_booking = Booking(
                nama_mahasiswa=data["nama_mahasiswa"],
                nim=data["nim"],
                dosen_id=data["dosen_id"],
                tanggal=tanggal,
                jam=jam,
                topik_konsultasi=data["topik_konsultasi"],
                status="pending",
            )
            db.session.add(new_booking)
            db.session.commit()

            return {
                "success": True,
                "message": "Booking berhasil dibuat",
                "data": new_booking.to_json(),
            }, 201
        except ValueError as e:
            return {
                "success": False,
                "message": f"Format tanggal atau jam tidak valid: {str(e)}",
            }, 400
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Gagal membuat booking: {str(e)}",
            }, 500


@booking_ns.route("/<int:id>")
@booking_ns.param("id", "Booking ID")
class BookingDetail(Resource):
    @booking_ns.doc("update_booking", security="Bearer")
    @booking_ns.expect(booking_update, validate=True)
    @booking_ns.marshal_with(success_response)
    @booking_ns.response(400, "Validation Error", error_model)
    @booking_ns.response(401, "Unauthorized", error_model)
    @booking_ns.response(403, "Forbidden", error_model)
    @booking_ns.response(404, "Booking Not Found", error_model)
    @jwt_required()
    def put(self, id):
        """Update booking"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get("role")

        booking = Booking.query.get_or_404(id)
        data = request.get_json()

        if not data:
            return {"success": False, "message": "Request body tidak boleh kosong"}, 400

        # Authorization check
        if user_role == "mahasiswa":
            # Mahasiswa can only edit their own bookings and cannot change status
            user = User.query.get(current_user_id)
            if not user or booking.nim != user.nim:
                return {
                    "success": False,
                    "message": "Anda tidak memiliki akses untuk mengubah booking ini",
                }, 403

            # Mahasiswa cannot change status
            if "status" in data:
                return {
                    "success": False,
                    "message": "Mahasiswa tidak dapat mengubah status booking",
                }, 403

        elif user_role == "dosen":
            # Dosen can only edit bookings for their consultations
            dosen = Dosen.query.filter_by(user_id=current_user_id).first()
            if not dosen or booking.dosen_id != dosen.id:
                return {
                    "success": False,
                    "message": "Anda tidak memiliki akses untuk mengubah booking ini",
                }, 403

        # Update booking data
        try:
            from datetime import datetime

            if "tanggal" in data:
                booking.tanggal = datetime.strptime(data["tanggal"], "%Y-%m-%d").date()
            if "jam" in data:
                booking.jam = datetime.strptime(data["jam"], "%H:%M:%S").time()
            if "topik_konsultasi" in data:
                booking.topik_konsultasi = data["topik_konsultasi"]
            if "status" in data and user_role == "dosen":
                booking.status = data["status"]

            db.session.commit()
            return {"success": True, "message": "Booking berhasil diubah"}
        except ValueError as e:
            return {
                "success": False,
                "message": f"Format tanggal atau jam tidak valid: {str(e)}",
            }, 400
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Gagal mengubah booking: {str(e)}",
            }, 500

    @booking_ns.doc("delete_booking", security="Bearer")
    @booking_ns.marshal_with(success_response)
    @booking_ns.response(401, "Unauthorized", error_model)
    @booking_ns.response(403, "Forbidden", error_model)
    @booking_ns.response(404, "Booking Not Found", error_model)
    @jwt_required()
    def delete(self, id):
        """Delete booking"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get("role")

        booking = Booking.query.get_or_404(id)

        # Authorization check
        if user_role == "mahasiswa":
            # Mahasiswa can only delete their own bookings
            user = User.query.get(current_user_id)
            if not user or booking.nim != user.nim:
                return {
                    "success": False,
                    "message": "Anda tidak memiliki akses untuk menghapus booking ini",
                }, 403

        elif user_role == "dosen":
            # Dosen can delete bookings for their consultations
            dosen = Dosen.query.filter_by(user_id=current_user_id).first()
            if not dosen or booking.dosen_id != dosen.id:
                return {
                    "success": False,
                    "message": "Anda tidak memiliki akses untuk menghapus booking ini",
                }, 403

        db.session.delete(booking)
        db.session.commit()
        return {"success": True, "message": "Booking berhasil dihapus"}
