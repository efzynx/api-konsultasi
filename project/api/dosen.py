"""
Dosen API endpoints with Flask-RESTX documentation
"""

from flask import request
from flask_restx import Namespace, Resource
from project.models import Dosen, User, Booking
from project import db
from project.api_models_simple import get_models

# Create namespace
dosen_ns = Namespace('dosen', description='Dosen management operations')

# Get models
models = get_models(dosen_ns)
dosen_response_model = models['dosen_model']
dosen_create = models['dosen_create_model']
dosen_update = models['dosen_update_model']
dosen_list_response = models['dosen_list_response_model']
success_response = models['success_response_model']
error_model = models['error_response_model']


@dosen_ns.route('/')
class DosenList(Resource):
    @dosen_ns.doc('get_all_dosen')
    @dosen_ns.marshal_with(dosen_list_response)
    @dosen_ns.response(500, 'Internal Server Error', error_model)
    def get(self):
        """Get all dosen"""
        try:
            all_dosen = Dosen.query.all()
            result = [dosen.to_json() for dosen in all_dosen]
            return {
                'success': True,
                'message': 'Data dosen berhasil diambil',
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Gagal mengambil data: {str(e)}'
            }, 500

    @dosen_ns.doc('add_dosen')
    @dosen_ns.expect(dosen_create, validate=True)
    @dosen_ns.marshal_with(success_response, code=201)
    @dosen_ns.response(400, 'Validation Error', error_model)
    @dosen_ns.response(409, 'Username Already Exists', error_model)
    @dosen_ns.response(500, 'Internal Server Error', error_model)
    def post(self):
        """Add new dosen"""
        data = request.get_json()
        required_fields = ['nama_dosen', 'mata_kuliah', 'username', 'password']
        
        if not all(field in data for field in required_fields):
            return {
                'success': False,
                'message': 'Data nama_dosen, mata_kuliah, username dan password diperlukan'
            }, 400

        if User.query.filter_by(username=data['username']).first():
            return {
                'success': False,
                'message': 'Username sudah terdaftar'
            }, 409

        try:
            # Create user account for dosen
            new_user_dosen = User(
                username=data['username'],
                nama=data['nama_dosen'],
                role='dosen'
            )
            new_user_dosen.set_password(data['password'])
            db.session.add(new_user_dosen)
            db.session.flush()  # Get ID from newly created user

            # Create dosen entry
            new_dosen = Dosen(
                nama_dosen=data['nama_dosen'],
                mata_kuliah=data['mata_kuliah'],
                user_id=new_user_dosen.id
            )
            db.session.add(new_dosen)
            db.session.commit()

            return {
                'success': True,
                'message': 'Dosen berhasil ditambahkan'
            }, 201

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Gagal menambahkan dosen: {str(e)}'
            }, 500


@dosen_ns.route('/<int:id>')
@dosen_ns.param('id', 'Dosen ID')
class DosenDetail(Resource):
    @dosen_ns.doc('update_dosen')
    @dosen_ns.expect(dosen_update, validate=True)
    @dosen_ns.marshal_with(success_response)
    @dosen_ns.response(400, 'Validation Error', error_model)
    @dosen_ns.response(404, 'Dosen Not Found', error_model)
    def put(self, id):
        """Update dosen data"""
        dosen = Dosen.query.get_or_404(id)
        data = request.get_json()

        if not data:
            return {
                'success': False,
                'message': 'Request body tidak boleh kosong'
            }, 400

        dosen.nama_dosen = data.get('nama_dosen', dosen.nama_dosen)
        dosen.mata_kuliah = data.get('mata_kuliah', dosen.mata_kuliah)

        # Update user name if dosen name is changed
        if 'nama_dosen' in data:
            user = User.query.get(dosen.user_id)
            if user:
                user.nama = data['nama_dosen']

        db.session.commit()
        return {
            'success': True,
            'message': 'Data dosen berhasil diubah'
        }

    @dosen_ns.doc('delete_dosen')
    @dosen_ns.marshal_with(success_response)
    @dosen_ns.response(404, 'Dosen Not Found', error_model)
    @dosen_ns.response(500, 'Internal Server Error', error_model)
    def delete(self, id):
        """Delete dosen"""
        dosen = Dosen.query.get_or_404(id)
        user = User.query.get(dosen.user_id)

        try:
            # Delete all bookings related to this dosen first
            Booking.query.filter_by(dosen_id=id).delete()

            # Delete dosen data
            db.session.delete(dosen)

            # Delete dosen login account
            if user:
                db.session.delete(user)

            db.session.commit()
            return {
                'success': True,
                'message': 'Dosen dan semua data terkait berhasil dihapus'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Gagal menghapus dosen: {str(e)}'
            }, 500
