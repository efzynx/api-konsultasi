"""
Flask-RESTX API Configuration
"""

from flask_restx import Api
from flask import Blueprint

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Configure Flask-RESTX API
api = Api(
    api_bp,
    version='1.0',
    title='API Konsultasi Documentation',
    description='Interactive API documentation for the Consultation Booking System',
    doc='/docs/',
    contact='Fauzan',
    contact_email='me@efzyn.my.id',
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"'
        }
    },
    security='Bearer'
)

# Import and register namespaces
from project.api.auth import auth_ns
from project.api.dosen import dosen_ns
from project.api.booking import booking_ns
from project.api.user import user_ns
from project.api.profile import profile_ns

api.add_namespace(auth_ns, path='/auth')
api.add_namespace(dosen_ns, path='/dosen')
api.add_namespace(booking_ns, path='/booking')
api.add_namespace(user_ns, path='/user')
api.add_namespace(profile_ns, path='/profile')
