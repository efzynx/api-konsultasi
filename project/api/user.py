"""
User API endpoints with Flask-RESTX documentation
"""

from flask import request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource

from project import db
from project.api_models_simple import get_models
from project.models import User

# Create namespace
user_ns = Namespace("user", description="User management operations")

# Get models
models = get_models(user_ns)
user_response_model = models["user_model"]
success_response = models["success_response_model"]
error_model = models["error_response_model"]
data_response = models["data_response_model"]


@user_ns.route("/me")
class CurrentUser(Resource):
    @user_ns.doc("get_current_user", security="Bearer")
    @user_ns.marshal_with(data_response)
    @user_ns.response(401, "Unauthorized", error_model)
    @user_ns.response(404, "User Not Found", error_model)
    @jwt_required()
    def get(self):
        """Get current user information"""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return {"success": False, "message": "User tidak ditemukan"}, 404

        return {
            "success": True,
            "message": "Data user berhasil diambil",
            "data": user.to_json(),
        }


@user_ns.route("/all")
class AllUsers(Resource):
    @user_ns.doc("get_all_users", security="Bearer")
    @user_ns.marshal_with(data_response)
    @user_ns.response(401, "Unauthorized", error_model)
    @user_ns.response(403, "Forbidden - Admin access required", error_model)
    @user_ns.response(500, "Internal Server Error", error_model)
    @jwt_required()
    def get(self):
        """Get all users (admin access)"""
        try:
            # Note: You might want to add admin role check here
            current_user_id = get_jwt_identity()
            claims = get_jwt()
            user_role = claims.get("role")

            # For now, allowing dosen to see all users
            # You can modify this based on your requirements
            if user_role not in ["dosen"]:
                return {
                    "success": False,
                    "message": "Akses ditolak. Hanya dosen yang dapat melihat semua user",
                }, 403

            all_users = User.query.all()
            result = [user.to_json() for user in all_users]

            return {
                "success": True,
                "message": "Data semua user berhasil diambil",
                "data": result,
            }
        except Exception as e:
            return {"success": False, "message": f"Gagal mengambil data: {str(e)}"}, 500


@user_ns.route("/<int:user_id>")
@user_ns.param("user_id", "User ID")
class UserDetail(Resource):
    @user_ns.doc("get_user_by_id", security="Bearer")
    @user_ns.marshal_with(data_response)
    @user_ns.response(401, "Unauthorized", error_model)
    @user_ns.response(403, "Forbidden", error_model)
    @user_ns.response(404, "User Not Found", error_model)
    @jwt_required()
    def get(self, user_id):
        """Get user by ID"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get("role")

        # Users can only see their own data, unless they are dosen
        if user_role != "dosen" and str(current_user_id) != str(user_id):
            return {
                "success": False,
                "message": "Anda tidak memiliki akses untuk melihat data user ini",
            }, 403

        user = User.query.get(user_id)
        if not user:
            return {"success": False, "message": "User tidak ditemukan"}, 404

        return {
            "success": True,
            "message": "Data user berhasil diambil",
            "data": user.to_json(),
        }

    @user_ns.doc("delete_user", security="Bearer")
    @user_ns.marshal_with(success_response)
    @user_ns.response(401, "Unauthorized", error_model)
    @user_ns.response(403, "Forbidden", error_model)
    @user_ns.response(404, "User Not Found", error_model)
    @user_ns.response(500, "Internal Server Error", error_model)
    @jwt_required()
    def delete(self, user_id):
        """Delete user (admin access)"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get("role")

        # Only dosen can delete users (you might want to add admin role)
        if user_role != "dosen":
            return {
                "success": False,
                "message": "Akses ditolak. Hanya dosen yang dapat menghapus user",
            }, 403

        # Prevent self-deletion
        if str(current_user_id) == str(user_id):
            return {
                "success": False,
                "message": "Anda tidak dapat menghapus akun sendiri",
            }, 403

        user = User.query.get(user_id)
        if not user:
            return {"success": False, "message": "User tidak ditemukan"}, 404

        try:
            db.session.delete(user)
            db.session.commit()
            return {"success": True, "message": "User berhasil dihapus"}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": f"Gagal menghapus user: {str(e)}"}, 500


@user_ns.route("/mahasiswa")
class MahasiswaList(Resource):
    @user_ns.doc("get_all_mahasiswa", security="Bearer")
    @user_ns.marshal_with(data_response)
    @user_ns.response(401, "Unauthorized", error_model)
    @user_ns.response(403, "Forbidden", error_model)
    @user_ns.response(500, "Internal Server Error", error_model)
    @jwt_required()
    def get(self):
        """Get all mahasiswa users"""
        try:
            current_user_id = get_jwt_identity()
            claims = get_jwt()
            user_role = claims.get("role")

            # Only dosen can see all mahasiswa
            if user_role != "dosen":
                return {
                    "success": False,
                    "message": "Akses ditolak. Hanya dosen yang dapat melihat data mahasiswa",
                }, 403

            mahasiswa_users = User.query.filter_by(role="mahasiswa").all()
            result = [user.to_json() for user in mahasiswa_users]

            return {
                "success": True,
                "message": "Data mahasiswa berhasil diambil",
                "data": result,
            }
        except Exception as e:
            return {"success": False, "message": f"Gagal mengambil data: {str(e)}"}, 500
