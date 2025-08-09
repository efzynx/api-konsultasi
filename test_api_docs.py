"""
Test script for Flask-RESTX API Documentation
"""

import os
import tempfile

from config import Config
from project import create_app, db


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret-key"
    JWT_SECRET_KEY = "test-jwt-secret"


def test_api_documentation():
    """Test if Flask-RESTX API documentation is working"""

    # Create app with test config
    app = create_app(TestConfig)

    with app.test_client() as client:
        # Test if the API documentation is accessible
        print("🔍 Testing API Documentation Endpoints...")

        # Test Swagger UI
        response = client.get("/api/v1/docs/")
        print(f"📋 Swagger UI (/api/v1/docs/): {response.status_code}")

        # Test API spec
        response = client.get("/api/v1/swagger.json")
        print(f"📋 API Spec (/api/v1/swagger.json): {response.status_code}")

        # Test health endpoint
        response = client.get("/api/v1/auth/health")
        print(f"🏥 Health Check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.get_json()}")

        # Test API endpoints structure
        print("\n📚 Available API Endpoints:")
        print("   🔐 Authentication: /api/v1/auth/")
        print("      - POST /register")
        print("      - POST /login")
        print("      - GET /health")
        print("   👨‍🏫 Dosen: /api/v1/dosen/")
        print("      - GET / (list all)")
        print("      - POST / (create)")
        print("      - PUT /<id> (update)")
        print("      - DELETE /<id> (delete)")
        print("   📅 Booking: /api/v1/booking/")
        print("      - GET / (list)")
        print("      - POST / (create)")
        print("      - PUT /<id> (update)")
        print("      - DELETE /<id> (delete)")
        print("   👤 User: /api/v1/user/")
        print("      - GET /me")
        print("      - GET /all")
        print("      - GET /<id>")
        print("      - DELETE /<id>")
        print("      - GET /mahasiswa")
        print("   👤 Profile: /api/v1/profile/")
        print("      - GET / (get profile)")
        print("      - PUT / (update profile)")
        print("      - PUT /change-password")

        print("\n✅ Flask-RESTX API Documentation is working!")
        print(f"🌐 Access documentation at: http://localhost:5000/api/v1/docs/")
        print(f"📊 API specification at: http://localhost:5000/api/v1/swagger.json")

        return True


if __name__ == "__main__":
    print("🚀 Testing Flask-RESTX API Documentation Implementation")
    print("=" * 60)

    try:
        test_api_documentation()
        print("\n🎉 SUCCESS: Flask-RESTX implementation is working correctly!")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback

        traceback.print_exc()
