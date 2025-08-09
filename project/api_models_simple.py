"""
Simplified API Models for Flask-RESTX Documentation
"""

from flask_restx import fields

# Simple response models without nested dictionaries
def get_models(api):
    """Get all API models registered with the namespace"""
    
    # User models
    user_model = api.model('User', {
        'id': fields.Integer(required=True, description='User ID'),
        'username': fields.String(required=True, description='Username'),
        'nama': fields.String(required=True, description='Full name'),
        'nim': fields.String(description='Student ID number'),
        'role': fields.String(required=True, description='User role')
    })

    user_register_model = api.model('UserRegister', {
        'username': fields.String(required=True, description='Username', example='john_doe'),
        'password': fields.String(required=True, description='Password', example='securepassword123'),
        'nama': fields.String(required=True, description='Full name', example='John Doe'),
        'nim': fields.String(description='Student ID number', example='123456789'),
        'role': fields.String(description='User role', default='mahasiswa')
    })

    user_login_model = api.model('UserLogin', {
        'username': fields.String(required=True, description='Username', example='john_doe'),
        'password': fields.String(required=True, description='Password', example='securepassword123')
    })

    # Response models
    success_response_model = api.model('SuccessResponse', {
        'success': fields.Boolean(required=True, description='Operation success status'),
        'message': fields.String(required=True, description='Response message')
    })

    error_response_model = api.model('ErrorResponse', {
        'success': fields.Boolean(required=True, description='Operation success status', default=False),
        'message': fields.String(required=True, description='Error message')
    })

    # Login response
    login_data_model = api.model('LoginData', {
        'user': fields.Nested(user_model),
        'access_token': fields.String(required=True, description='JWT access token')
    })

    login_response_model = api.model('LoginResponse', {
        'success': fields.Boolean(required=True, description='Login success status'),
        'message': fields.String(required=True, description='Response message'),
        'data': fields.Nested(login_data_model)
    })

    # Health response
    health_response_model = api.model('HealthResponse', {
        'success': fields.Boolean(required=True, description='Health status'),
        'message': fields.String(required=True, description='Health message'),
        'status': fields.String(required=True, description='Application status')
    })

    # Dosen models
    dosen_model = api.model('Dosen', {
        'id': fields.Integer(required=True, description='Dosen ID'),
        'nama_dosen': fields.String(required=True, description='Dosen name'),
        'mata_kuliah': fields.String(required=True, description='Subject taught'),
        'user_id': fields.Integer(required=True, description='Associated user ID')
    })

    dosen_create_model = api.model('DosenCreate', {
        'nama_dosen': fields.String(required=True, description='Dosen name', example='Dr. Jane Smith'),
        'mata_kuliah': fields.String(required=True, description='Subject taught', example='Web Programming'),
        'username': fields.String(required=True, description='Login username', example='dr_jane'),
        'password': fields.String(required=True, description='Login password', example='securepassword123')
    })

    dosen_update_model = api.model('DosenUpdate', {
        'nama_dosen': fields.String(description='Dosen name', example='Dr. Jane Smith'),
        'mata_kuliah': fields.String(description='Subject taught', example='Web Programming')
    })

    dosen_list_response_model = api.model('DosenListResponse', {
        'success': fields.Boolean(required=True, description='Operation success status'),
        'message': fields.String(required=True, description='Response message'),
        'data': fields.List(fields.Nested(dosen_model))
    })

    # Booking models
    booking_model = api.model('Booking', {
        'id': fields.Integer(required=True, description='Booking ID'),
        'nama_mahasiswa': fields.String(required=True, description='Student name'),
        'nim': fields.String(required=True, description='Student ID number'),
        'dosen_id': fields.Integer(required=True, description='Dosen ID'),
        'tanggal': fields.String(required=True, description='Consultation date', example='2024-01-15'),
        'jam': fields.String(required=True, description='Consultation time', example='14:00:00'),
        'topik_konsultasi': fields.String(required=True, description='Consultation topic'),
        'status': fields.String(required=True, description='Booking status')
    })

    booking_create_model = api.model('BookingCreate', {
        'nama_mahasiswa': fields.String(required=True, description='Student name', example='John Doe'),
        'nim': fields.String(required=True, description='Student ID number', example='123456789'),
        'dosen_id': fields.Integer(required=True, description='Dosen ID', example=1),
        'tanggal': fields.String(required=True, description='Consultation date (YYYY-MM-DD)', example='2024-01-15'),
        'jam': fields.String(required=True, description='Consultation time (HH:MM:SS)', example='14:00:00'),
        'topik_konsultasi': fields.String(required=True, description='Consultation topic', example='Discussion about final project')
    })

    booking_update_model = api.model('BookingUpdate', {
        'tanggal': fields.String(description='Consultation date (YYYY-MM-DD)', example='2024-01-15'),
        'jam': fields.String(description='Consultation time (HH:MM:SS)', example='14:00:00'),
        'topik_konsultasi': fields.String(description='Consultation topic', example='Discussion about final project'),
        'status': fields.String(description='Booking status (dosen only)')
    })

    booking_list_response_model = api.model('BookingListResponse', {
        'success': fields.Boolean(required=True, description='Operation success status'),
        'message': fields.String(required=True, description='Response message'),
        'data': fields.List(fields.Nested(booking_model))
    })

    # Profile models
    profile_update_model = api.model('ProfileUpdate', {
        'nama': fields.String(description='Full name', example='John Doe Updated'),
        'username': fields.String(description='Username', example='john_doe_new'),
        'password': fields.String(description='New password', example='newsecurepassword123')
    })

    password_change_model = api.model('PasswordChange', {
        'current_password': fields.String(required=True, description='Current password'),
        'new_password': fields.String(required=True, description='New password (min 6 characters)')
    })

    # Generic data response
    data_response_model = api.model('DataResponse', {
        'success': fields.Boolean(required=True, description='Operation success status'),
        'message': fields.String(required=True, description='Response message'),
        'data': fields.Raw(description='Response data')
    })

    return {
        'user_model': user_model,
        'user_register_model': user_register_model,
        'user_login_model': user_login_model,
        'success_response_model': success_response_model,
        'error_response_model': error_response_model,
        'login_data_model': login_data_model,
        'login_response_model': login_response_model,
        'health_response_model': health_response_model,
        'dosen_model': dosen_model,
        'dosen_create_model': dosen_create_model,
        'dosen_update_model': dosen_update_model,
        'dosen_list_response_model': dosen_list_response_model,
        'booking_model': booking_model,
        'booking_create_model': booking_create_model,
        'booking_update_model': booking_update_model,
        'booking_list_response_model': booking_list_response_model,
        'profile_update_model': profile_update_model,
        'password_change_model': password_change_model,
        'data_response_model': data_response_model
    }
