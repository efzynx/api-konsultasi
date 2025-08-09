"""
Profile API endpoints with Flask-RESTX documentation
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from project.models import User
from project import db
from project.api_models_simple import get_models

# Create namespace
profile_ns = Namespace("profile", description="User profile management operations")

# Get models
models = get_models(profile_ns)
profile_update = models["profile_update_model"]
success_response = models["success_response_model"]
error_model = models["error_response_model"]
data_response = models["data_response_model"]
password_change_model = models["password_change_model"]


@profile_ns.route("/")
class UserProfile(Resource):
    @profile_ns.doc("get_profile", security="Bearer")
    @profile_ns.marshal_with(data_response)
    @profile_ns.response(401, "Unauthorized", error_model)
    @profile_ns.response(404, "User Not Found", error_model)
    @jwt_required()
    def get(self):
        """Get current user profile"""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return {"success": False, "message": "User tidak ditemukan"}, 404

        return {
            "success": True,
            "message": "Data profil berhasil diambil",
            "data": user.to_json(),
        }

    @profile_ns.doc("update_profile", security="Bearer")
    @profile_ns.expect(profile_update, validate=True)
    @profile_ns.marshal_with(success_response)
    @profile_ns.response(400, "Validation Error", error_model)
    @profile_ns.response(401, "Unauthorized", error_model)
    @profile_ns.response(404, "User Not Found", error_model)
    @profile_ns.response(409, "Username Already Exists", error_model)
    @profile_ns.response(500, "Internal Server Error", error_model)
    @jwt_required()
    def put(self):
        """Update current user profile"""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return {"success": False, "message": "User tidak ditemukan"}, 404

        data = request.get_json()

        if not data:
            return {"success": False, "message": "Request body tidak boleh kosong"}, 400

        try:
            # Update nama if provided
            if "nama" in data:
                user.nama = data["nama"]

            # Update username if provided
            if "username" in data:
                # Check if username already exists (excluding current user)
                existing_user = User.query.filter(
                    User.username == data["username"], User.id != current_user_id
                ).first()

                if existing_user:
                    return {
                        "success": False,
                        "message": "Username sudah digunakan oleh user lain",
                    }, 409

                user.username = data["username"]

            # Update password if provided
            if "password" in data:
                if len(data["password"]) < 6:
                    return {
                        "success": False,
                        "message": "Password minimal 6 karakter",
                    }, 400
                user.set_password(data["password"])

            db.session.commit()

            return {"success": True, "message": "Profil berhasil diperbarui"}

        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Gagal memperbarui profil: {str(e)}",
            }, 500


@profile_ns.route("/change-password")
class ChangePassword(Resource):
    @profile_ns.doc("change_password", security="Bearer")
    @profile_ns.expect(password_change_model, validate=True)
    @profile_ns.marshal_with(success_response)
    @profile_ns.response(400, "Validation Error", error_model)
    @profile_ns.response(401, "Unauthorized", error_model)
    @profile_ns.response(404, "User Not Found", error_model)
    @profile_ns.response(500, "Internal Server Error", error_model)
    @jwt_required()
    def put(self):
        """Change user password with current password verification"""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return {"success": False, "message": "User tidak ditemukan"}, 404

        data = request.get_json()

        if not data or not data.get("current_password") or not data.get("new_password"):
            return {
                "success": False,
                "message": "Current password dan new password diperlukan",
            }, 400

        # Verify current password
        if not user.check_password(data["current_password"]):
            return {"success": False, "message": "Password saat ini salah"}, 400

        # Validate new password
        if len(data["new_password"]) < 6:
            return {
                "success": False,
                "message": "Password baru minimal 6 karakter",
            }, 400

        # Check if new password is different from current
        if user.check_password(data["new_password"]):
            return {
                "success": False,
                "message": "Password baru harus berbeda dari password saat ini",
            }, 400

        try:
            user.set_password(data["new_password"])
            db.session.commit()

            return {"success": True, "message": "Password berhasil diubah"}

        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Gagal mengubah password: {str(e)}",
            }, 500
