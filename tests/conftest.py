import os
from datetime import date, time

import pytest

from project import create_app, db
from project.models import Booking, Dosen, User


class TestConfig:
    """Test configuration class"""

    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "test-jwt-secret-key"
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    TESTING = True


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def sample_user(app):
    """Create a sample user for testing."""
    with app.app_context():
        user = User(
            username="testuser", nama="Test User", nim="123456789", role="mahasiswa"
        )
        user.set_password("testpassword")
        db.session.add(user)
        db.session.commit()

        # Refresh the user to ensure it's attached to the session
        db.session.refresh(user)
        return user


@pytest.fixture
def sample_dosen_user(app):
    """Create a sample dosen user for testing."""
    with app.app_context():
        user = User(username="dosenpak", nama="Pak Dosen", role="dosen")
        user.set_password("dosenpassword")
        db.session.add(user)
        db.session.commit()

        dosen = Dosen(
            nama_dosen="Pak Dosen", mata_kuliah="Pemrograman Web", user_id=user.id
        )
        db.session.add(dosen)
        db.session.commit()

        # Refresh both objects to ensure they're attached to the session
        db.session.refresh(user)
        db.session.refresh(dosen)
        return user, dosen


@pytest.fixture
def sample_booking(app):
    """Create a sample booking for testing."""
    with app.app_context():
        # Create user within the same context
        user = User(
            username="testuser_booking",
            nama="Test User Booking",
            nim="123456789",
            role="mahasiswa",
        )
        user.set_password("testpassword")
        db.session.add(user)
        db.session.commit()

        # Create dosen user within the same context
        dosen_user = User(
            username="dosenpak_booking", nama="Pak Dosen Booking", role="dosen"
        )
        dosen_user.set_password("dosenpassword")
        db.session.add(dosen_user)
        db.session.commit()

        dosen = Dosen(
            nama_dosen="Pak Dosen Booking",
            mata_kuliah="Pemrograman Web",
            user_id=dosen_user.id,
        )
        db.session.add(dosen)
        db.session.commit()

        booking = Booking(
            nama_mahasiswa=user.nama,
            nim=user.nim,
            dosen_id=dosen.id,
            tanggal=date(2024, 1, 15),
            jam=time(10, 0),
            topik_konsultasi="Test consultation",
            status="pending",
        )
        db.session.add(booking)
        db.session.commit()

        # Refresh all objects
        db.session.refresh(user)
        db.session.refresh(dosen_user)
        db.session.refresh(dosen)
        db.session.refresh(booking)
        return booking


@pytest.fixture
def auth_headers(client, sample_user):
    """Get authentication headers for testing protected routes."""
    response = client.post(
        "/login", json={"username": "testuser", "password": "testpassword"}
    )
    data = response.get_json()
    token = data["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
