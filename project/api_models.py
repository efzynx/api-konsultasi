"""
API Models and Schemas for Flask-RESTX Documentation
"""

from flask_restx import Model, fields

# Base response models
success_response = {
    "success": fields.Boolean(required=True, description="Operation success status"),
    "message": fields.String(required=True, description="Response message"),
}

error_response = {
    "success": fields.Boolean(
        required=True, description="Operation success status", default=False
    ),
    "message": fields.String(required=True, description="Error message"),
}

# User models
user_model = {
    "id": fields.Integer(required=True, description="User ID"),
    "username": fields.String(required=True, description="Username"),
    "nama": fields.String(required=True, description="Full name"),
    "nim": fields.String(description="Student ID number"),
    "role": fields.String(
        required=True, description="User role", enum=["mahasiswa", "dosen"]
    ),
}

user_register_model = {
    "username": fields.String(
        required=True, description="Username", example="john_doe"
    ),
    "password": fields.String(
        required=True, description="Password", example="securepassword123"
    ),
    "nama": fields.String(required=True, description="Full name", example="John Doe"),
    "nim": fields.String(description="Student ID number", example="123456789"),
    "role": fields.String(
        description="User role", default="mahasiswa", enum=["mahasiswa", "dosen"]
    ),
}

user_login_model = {
    "username": fields.String(
        required=True, description="Username", example="john_doe"
    ),
    "password": fields.String(
        required=True, description="Password", example="securepassword123"
    ),
}

login_data_model = {
    "user": fields.Nested(user_model),
    "access_token": fields.String(required=True, description="JWT access token"),
}

login_response_model = {
    "success": fields.Boolean(required=True, description="Login success status"),
    "message": fields.String(required=True, description="Response message"),
    "data": fields.Nested(login_data_model),
}

# Dosen models
dosen_model = {
    "id": fields.Integer(required=True, description="Dosen ID"),
    "nama_dosen": fields.String(required=True, description="Dosen name"),
    "mata_kuliah": fields.String(required=True, description="Subject taught"),
    "user_id": fields.Integer(required=True, description="Associated user ID"),
}

dosen_create_model = {
    "nama_dosen": fields.String(
        required=True, description="Dosen name", example="Dr. Jane Smith"
    ),
    "mata_kuliah": fields.String(
        required=True, description="Subject taught", example="Web Programming"
    ),
    "username": fields.String(
        required=True, description="Login username", example="dr_jane"
    ),
    "password": fields.String(
        required=True, description="Login password", example="securepassword123"
    ),
}

dosen_update_model = {
    "nama_dosen": fields.String(description="Dosen name", example="Dr. Jane Smith"),
    "mata_kuliah": fields.String(
        description="Subject taught", example="Web Programming"
    ),
}

dosen_list_response_model = {
    "success": fields.Boolean(required=True, description="Operation success status"),
    "message": fields.String(required=True, description="Response message"),
    "data": fields.List(fields.Nested(dosen_model)),
}

# Booking models
booking_model = {
    "id": fields.Integer(required=True, description="Booking ID"),
    "nama_mahasiswa": fields.String(required=True, description="Student name"),
    "nim": fields.String(required=True, description="Student ID number"),
    "dosen_id": fields.Integer(required=True, description="Dosen ID"),
    "dosen_info": fields.Nested(dosen_model, description="Dosen information"),
    "tanggal": fields.String(
        required=True, description="Consultation date", example="2024-01-15"
    ),
    "jam": fields.String(
        required=True, description="Consultation time", example="14:00:00"
    ),
    "topik_konsultasi": fields.String(required=True, description="Consultation topic"),
    "status": fields.String(
        required=True,
        description="Booking status",
        enum=["pending", "approved", "rejected"],
    ),
}

booking_create_model = {
    "nama_mahasiswa": fields.String(
        required=True, description="Student name", example="John Doe"
    ),
    "nim": fields.String(
        required=True, description="Student ID number", example="123456789"
    ),
    "dosen_id": fields.Integer(required=True, description="Dosen ID", example=1),
    "tanggal": fields.String(
        required=True,
        description="Consultation date (YYYY-MM-DD)",
        example="2024-01-15",
    ),
    "jam": fields.String(
        required=True, description="Consultation time (HH:MM:SS)", example="14:00:00"
    ),
    "topik_konsultasi": fields.String(
        required=True,
        description="Consultation topic",
        example="Discussion about final project",
    ),
}

booking_update_model = {
    "tanggal": fields.String(
        description="Consultation date (YYYY-MM-DD)", example="2024-01-15"
    ),
    "jam": fields.String(
        description="Consultation time (HH:MM:SS)", example="14:00:00"
    ),
    "topik_konsultasi": fields.String(
        description="Consultation topic", example="Discussion about final project"
    ),
    "status": fields.String(
        description="Booking status (dosen only)",
        enum=["pending", "approved", "rejected"],
    ),
}

booking_list_response_model = {
    "success": fields.Boolean(required=True, description="Operation success status"),
    "message": fields.String(required=True, description="Response message"),
    "data": fields.List(fields.Nested(booking_model)),
}

# Profile models
profile_update_model = {
    "nama": fields.String(description="Full name", example="John Doe Updated"),
    "username": fields.String(description="Username", example="john_doe_new"),
    "password": fields.String(
        description="New password", example="newsecurepassword123"
    ),
}

# Generic response models
generic_success_response_model = {
    "success": fields.Boolean(required=True, description="Operation success status"),
    "message": fields.String(required=True, description="Response message"),
}

data_response_model = {
    "success": fields.Boolean(required=True, description="Operation success status"),
    "message": fields.String(required=True, description="Response message"),
    "data": fields.Raw(description="Response data"),
}

# Health check model
health_response_model = {
    "success": fields.Boolean(required=True, description="Health status"),
    "message": fields.String(required=True, description="Health message"),
    "status": fields.String(required=True, description="Application status"),
}
