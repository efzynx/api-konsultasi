from flask import Blueprint, request, jsonify
from project.models import User
from project import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password') or not data.get('nama') or not data.get('nim'):
        return jsonify({'succes': False, 'message': 'Data tidak lengkap!'}), 400
    if User.query.filter_by(username=data['username']).first() or User.query.filter_by(nim=data['nim']).first():
        return jsonify({'succes': False, 'message': 'Username atau NIM sudah terdaftar'}), 409
    
    new_user = User(
        username=data['username'],
        nama=data['nama'],
        nim=data['nim'],
        role=data.get('dosen', 'mahasiswa')
    )
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify ({'succes': True, 'message': 'Berhasil mendaftar'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'succes': False, 'message': 'Username dan password diperlukan!'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'succes': False, 'message': 'Username atau password salah'}), 401
    
    user_data = {
        'id': user.id,
        'username': user.username,
        'nama': user.nama,
        'nim': user.nim,
        'role': user.role
    }
    return jsonify({'succes': True, 'data': user_data, 'message': 'Login Berhasil'}), 200