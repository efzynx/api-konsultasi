"""
Authentication API endpoints with Flask-RESTX documentation
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from project.models import User
from project import db
from project.api_models_simple import get_models

# Create namespace
auth_ns = Namespace("auth", description="Authentication operations")

# Get models
models = get_models(auth_ns)
register_model = models["user_register_model"]
login_model = models["user_login_model"]
login_response = models["login_response_model"]
success_response = models["success_response_model"]
error_model = models["error_response_model"]
health_model = models["health_response_model"]


@auth_ns.route("/health")
class HealthCheck(Resource):
    @auth_ns.doc("health_check")
    @auth_ns.marshal_with(health_model)
    @auth_ns.response(200, "Success")
    def get(self):
        """Health check endpoint"""
        return {
            "success": True,
            "message": "API Konsultasi is running",
            "status": "healthy",
        }


@auth_ns.route("/register")
class UserRegister(Resource):
    @auth_ns.doc("register_user")
    @auth_ns.expect(register_model, validate=True)
    @auth_ns.marshal_with(success_response, code=201)
    @auth_ns.response(400, "Validation Error", error_model)
    @auth_ns.response(409, "Username Already Exists", error_model)
    def post(self):
        """Register a new user"""
        data = request.get_json()

        # Validation
        if (
            not data
            or not data.get("username")
            or not data.get("password")
            or not data.get("nama")
        ):
            return {
                "success": False,
                "message": "Data username, password, dan nama tidak lengkap",
            }, 400

        # Check if username already exists
        if User.query.filter_by(username=data["username"]).first():
            return {"success": False, "message": "Username sudah terdaftar"}, 409

        # Create new user
        new_user = User(
            username=data["username"],
            nama=data["nama"],
            nim=data.get("nim"),
            role="mahasiswa",
        )
        new_user.set_password(data["password"])
        db.session.add(new_user)
        db.session.commit()

        return {"success": True, "message": "Registrasi mahasiswa berhasil"}, 201


@auth_ns.route("/login")
class UserLogin(Resource):
    @auth_ns.doc("login_user")
    @auth_ns.expect(login_model, validate=True)
    @auth_ns.marshal_with(login_response)
    @auth_ns.response(400, "Validation Error", error_model)
    @auth_ns.response(401, "Invalid Credentials", error_model)
    def post(self):
        """User login"""
        data = request.get_json()

        # Validation
        if not data or not data.get("username") or not data.get("password"):
            return {
                "success": False,
                "message": "Username dan password diperlukan",
            }, 400

        # Find user
        user = User.query.filter_by(username=data["username"]).first()

        # Check credentials
        if not user or not user.check_password(data["password"]):
            return {"success": False, "message": "Username atau password salah"}, 401

        # Create access token
        additional_claims = {"role": user.role, "nim": user.nim}
        access_token = create_access_token(
            identity=str(user.id), additional_claims=additional_claims
        )

        response_data = {"user": user.to_json(), "access_token": access_token}

        return {"success": True, "message": "Login berhasil", "data": response_data}
