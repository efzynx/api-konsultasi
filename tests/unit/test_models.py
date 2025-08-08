import pytest
from project.models import User, Dosen, Booking
from project import db
from datetime import date, time

class TestUserModel:
    """Test cases for User model"""
    
    def test_user_creation(self, app):
        """Test user creation"""
        with app.app_context():
            user = User(
                username='testuser',
                nama='Test User',
                nim='123456789',
                role='mahasiswa'
            )
            user.set_password('testpassword')
            
            assert user.username == 'testuser'
            assert user.nama == 'Test User'
            assert user.nim == '123456789'
            assert user.role == 'mahasiswa'
            assert user.password != 'testpassword'  # Should be hashed
    
    def test_password_hashing(self, app):
        """Test password hashing and verification"""
        with app.app_context():
            user = User(username='test', nama='Test', role='mahasiswa')
            user.set_password('secret')
            
            assert user.check_password('secret') is True
            assert user.check_password('wrong') is False
    
    def test_user_to_json(self, app, sample_user):
        """Test user JSON serialization"""
        with app.app_context():
            json_data = sample_user.to_json()
            
            assert 'id' in json_data
            assert json_data['username'] == 'testuser'
            assert json_data['nama'] == 'Test User'
            assert json_data['nim'] == '123456789'
            assert json_data['role'] == 'mahasiswa'
            assert 'password' not in json_data  # Password should not be in JSON

class TestDosenModel:
    """Test cases for Dosen model"""
    
    def test_dosen_creation(self, app, sample_dosen_user):
        """Test dosen creation"""
        with app.app_context():
            user, dosen = sample_dosen_user
            
            assert dosen.nama_dosen == 'Pak Dosen'
            assert dosen.mata_kuliah == 'Pemrograman Web'
            assert dosen.user_id == user.id
    
    def test_dosen_to_json(self, app, sample_dosen_user):
        """Test dosen JSON serialization"""
        with app.app_context():
            user, dosen = sample_dosen_user
            json_data = dosen.to_json()
            
            assert 'id' in json_data
            assert json_data['nama_dosen'] == 'Pak Dosen'
            assert json_data['mata_kuliah'] == 'Pemrograman Web'
            assert json_data['user_id'] == user.id

class TestBookingModel:
    """Test cases for Booking model"""
    
    def test_booking_creation(self, app, sample_booking):
        """Test booking creation"""
        with app.app_context():
            assert sample_booking.nama_mahasiswa == 'Test User Booking'
            assert sample_booking.nim == '123456789'
            assert sample_booking.tanggal == date(2024, 1, 15)
            assert sample_booking.jam == time(10, 0)
            assert sample_booking.topik_konsultasi == 'Test consultation'
            assert sample_booking.status == 'pending'
    
    def test_booking_to_json(self, app):
        """Test booking JSON serialization"""
        with app.app_context():
            # Create all objects within the same context to avoid session issues
            user = User(
                username='testuser_json',
                nama='Test User JSON',
                nim='123456789',
                role='mahasiswa'
            )
            user.set_password('testpassword')
            db.session.add(user)
            db.session.commit()
            
            dosen_user = User(
                username='dosenpak_json',
                nama='Pak Dosen JSON',
                role='dosen'
            )
            dosen_user.set_password('dosenpassword')
            db.session.add(dosen_user)
            db.session.commit()
            
            dosen = Dosen(
                nama_dosen='Pak Dosen JSON',
                mata_kuliah='Pemrograman Web',
                user_id=dosen_user.id
            )
            db.session.add(dosen)
            db.session.commit()
            
            booking = Booking(
                nama_mahasiswa=user.nama,
                nim=user.nim,
                dosen_id=dosen.id,
                tanggal=date(2024, 1, 15),
                jam=time(10, 0),
                topik_konsultasi='Test consultation',
                status='pending'
            )
            db.session.add(booking)
            db.session.commit()
            
            json_data = booking.to_json()
            
            assert 'id' in json_data
            assert json_data['nama_mahasiswa'] == 'Test User JSON'
            assert json_data['nim'] == '123456789'
            assert json_data['tanggal'] == '2024-01-15'
            assert json_data['jam'] == '10:00:00'
            assert json_data['topik_konsultasi'] == 'Test consultation'
            assert json_data['status'] == 'pending'
            assert 'dosen_info' in json_data
            assert json_data['dosen_info']['nama_dosen'] == 'Pak Dosen JSON'
    
    def test_booking_dosen_relationship(self, app):
        """Test booking-dosen relationship"""
        with app.app_context():
            # Create all objects within the same context
            dosen_user = User(
                username='dosenpak_rel',
                nama='Pak Dosen Rel',
                role='dosen'
            )
            dosen_user.set_password('dosenpassword')
            db.session.add(dosen_user)
            db.session.commit()
            
            dosen = Dosen(
                nama_dosen='Pak Dosen Rel',
                mata_kuliah='Pemrograman Web',
                user_id=dosen_user.id
            )
            db.session.add(dosen)
            db.session.commit()
            
            booking = Booking(
                nama_mahasiswa='Test Student',
                nim='123456789',
                dosen_id=dosen.id,
                tanggal=date(2024, 1, 15),
                jam=time(10, 0),
                topik_konsultasi='Test consultation',
                status='pending'
            )
            db.session.add(booking)
            db.session.commit()
            
            # Test the relationship
            assert booking.dosen == dosen
            assert booking in dosen.bookings
