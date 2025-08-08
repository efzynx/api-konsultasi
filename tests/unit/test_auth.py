import pytest
import json
from project.models import User
from project import db

class TestAuthRoutes:
    """Test cases for authentication routes"""
    
    def test_register_success(self, client, app):
        """Test successful user registration"""
        response = client.post('/register', json={
            'username': 'newuser',
            'password': 'newpassword',
            'nama': 'New User',
            'nim': '987654321'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'Registrasi mahasiswa berhasil' in data['message']
        
        # Verify user was created in database
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.nama == 'New User'
            assert user.nim == '987654321'
            assert user.role == 'mahasiswa'
    
    def test_register_missing_data(self, client):
        """Test registration with missing required data"""
        response = client.post('/register', json={
            'username': 'incomplete'
            # Missing password and nama
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'tidak lengkap' in data['message']
    
    def test_register_duplicate_username(self, client, sample_user):
        """Test registration with existing username"""
        response = client.post('/register', json={
            'username': 'testuser',  # Already exists
            'password': 'newpassword',
            'nama': 'Another User'
        })
        
        assert response.status_code == 409
        data = response.get_json()
        assert data['success'] is False
        assert 'sudah terdaftar' in data['message']
    
    def test_login_success(self, client, sample_user):
        """Test successful login"""
        response = client.post('/login', json={
            'username': 'testuser',
            'password': 'testpassword'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'Login berhasil' in data['message']
        assert 'access_token' in data['data']
        assert 'user' in data['data']
        
        # Verify user data in response
        user_data = data['data']['user']
        assert user_data['username'] == 'testuser'
        assert user_data['nama'] == 'Test User'
        assert user_data['role'] == 'mahasiswa'
    
    def test_login_missing_credentials(self, client):
        """Test login with missing credentials"""
        response = client.post('/login', json={
            'username': 'testuser'
            # Missing password
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'diperlukan' in data['message']
    
    def test_login_invalid_credentials(self, client, sample_user):
        """Test login with invalid credentials"""
        response = client.post('/login', json={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'salah' in data['message']
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post('/login', json={
            'username': 'nonexistent',
            'password': 'password'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'salah' in data['message']
    
    def test_register_without_nim(self, client, app):
        """Test registration without NIM (should work for dosen)"""
        response = client.post('/register', json={
            'username': 'dosen1',
            'password': 'dosenpass',
            'nama': 'Dosen Test'
            # No NIM provided
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        
        # Verify user was created without NIM
        with app.app_context():
            user = User.query.filter_by(username='dosen1').first()
            assert user is not None
            assert user.nim is None
            assert user.role == 'mahasiswa'  # Default role
