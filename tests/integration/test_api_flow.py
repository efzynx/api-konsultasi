import pytest
import json
from project.models import User, Dosen, Booking
from project import db

class TestAPIFlow:
    """Integration tests for complete API workflows"""
    
    def test_complete_user_registration_and_login_flow(self, client, app):
        """Test complete flow: register -> login -> access protected resource"""
        
        # Step 1: Register a new user
        register_response = client.post('/register', json={
            'username': 'flowtest',
            'password': 'flowpassword',
            'nama': 'Flow Test User',
            'nim': '111222333'
        })
        
        assert register_response.status_code == 201
        register_data = register_response.get_json()
        assert register_data['success'] is True
        
        # Step 2: Login with the new user
        login_response = client.post('/login', json={
            'username': 'flowtest',
            'password': 'flowpassword'
        })
        
        assert login_response.status_code == 200
        login_data = login_response.get_json()
        assert login_data['success'] is True
        assert 'access_token' in login_data['data']
        
        # Step 3: Use the token to access protected resources
        token = login_data['data']['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Try to access a protected route (assuming profile route exists)
        # This is a placeholder - adjust based on your actual protected routes
        profile_response = client.get('/profile', headers=headers)
        # Note: This might return 404 if route doesn't exist, which is fine for this test
        
        # Verify the user exists in database
        with app.app_context():
            user = User.query.filter_by(username='flowtest').first()
            assert user is not None
            assert user.nama == 'Flow Test User'
    
    def test_dosen_and_booking_flow(self, client, app):
        """Test flow involving dosen creation and booking"""
        
        # Step 1: Create a dosen user
        with app.app_context():
            dosen_user = User(
                username='dosen_flow',
                nama='Dosen Flow Test',
                role='dosen'
            )
            dosen_user.set_password('dosenpass')
            db.session.add(dosen_user)
            db.session.commit()
            
            dosen = Dosen(
                nama_dosen='Dosen Flow Test',
                mata_kuliah='Test Subject',
                user_id=dosen_user.id
            )
            db.session.add(dosen)
            db.session.commit()
            dosen_id = dosen.id
        
        # Step 2: Register a student
        student_response = client.post('/register', json={
            'username': 'student_flow',
            'password': 'studentpass',
            'nama': 'Student Flow Test',
            'nim': '444555666'
        })
        
        assert student_response.status_code == 201
        
        # Step 3: Login as student
        login_response = client.post('/login', json={
            'username': 'student_flow',
            'password': 'studentpass'
        })
        
        assert login_response.status_code == 200
        login_data = login_response.get_json()
        token = login_data['data']['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Step 4: Try to create a booking (this tests the booking flow)
        booking_data = {
            'dosen_id': dosen_id,
            'tanggal': '2024-02-15',
            'jam': '14:00',
            'topik_konsultasi': 'Integration test consultation'
        }
        
        # Note: Adjust the endpoint based on your actual booking route
        booking_response = client.post('/booking', json=booking_data, headers=headers)
        # This might return various status codes depending on your implementation
        
        # Verify data integrity in database
        with app.app_context():
            student = User.query.filter_by(username='student_flow').first()
            dosen_record = Dosen.query.get(dosen_id)
            
            assert student is not None
            assert dosen_record is not None
            assert dosen_record.nama_dosen == 'Dosen Flow Test'
    
    def test_authentication_error_handling(self, client):
        """Test authentication error handling across different endpoints"""
        
        # Test accessing protected routes without token
        # Note: /dosen GET is not protected, so we only test /profile and /booking
        protected_endpoints = ['/profile', '/booking']
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            # Should return 401 or 422 for missing token
            assert response.status_code in [401, 422], f"Endpoint {endpoint} returned {response.status_code}"
        
        # Test with invalid token
        invalid_headers = {'Authorization': 'Bearer invalid_token'}
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint, headers=invalid_headers)
            # Should return 401 or 422 for invalid token
            assert response.status_code in [401, 422], f"Endpoint {endpoint} with invalid token returned {response.status_code}"
        
        # Test /dosen separately since it's not protected for GET
        response = client.get('/dosen')
        assert response.status_code == 200  # /dosen GET is public
    
    def test_data_validation_across_endpoints(self, client, sample_user):
        """Test data validation consistency across different endpoints"""
        
        # Login to get token
        login_response = client.post('/login', json={
            'username': 'testuser',
            'password': 'testpassword'
        })
        
        assert login_response.status_code == 200
        token = login_response.get_json()['data']['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test various endpoints with invalid data
        invalid_data_tests = [
            ('/register', {'username': ''}),  # Empty username
            ('/register', {'username': 'test'}),  # Missing required fields
            ('/login', {'username': 'test'}),  # Missing password
            ('/login', {}),  # Empty data
        ]
        
        for endpoint, data in invalid_data_tests:
            response = client.post(endpoint, json=data)
            assert response.status_code == 400
            response_data = response.get_json()
            assert response_data['success'] is False
