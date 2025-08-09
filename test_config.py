"""
Test configuration for Flask-RESTX API testing
Uses SQLite instead of MySQL for testing purposes
"""

import os
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test_konsultasi.db"
    SECRET_KEY = "test-secret-key-for-testing"
    JWT_SECRET_KEY = "test-jwt-secret-key-for-testing"
    JWT_ACCESS_TOKEN_EXPIRES = False  # Tokens don't expire in testing
    WTF_CSRF_ENABLED = False
