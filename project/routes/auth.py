# file: project/routes/auth.py
from flask import Blueprint, request, jsonify
from project.models import User
from project import db
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password') or not data.get('nama'):
        return jsonify({'success': False, 'message': 'Data username, password, dan nama tidak lengkap'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'message': 'Username sudah terdaftar'}), 409

    new_user = User(
        username=data['username'],
        nama=data['nama'],
        nim=data.get('nim'),
        role='mahasiswa'
    )
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Registrasi mahasiswa berhasil'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'success': False, 'message': 'Username dan password diperlukan'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'success': False, 'message': 'Username atau password salah'}), 401
    
    # PERBAIKAN: Gunakan ID sebagai identity dan sisanya sebagai additional_claims
    additional_claims = {"role": user.role, "nim": user.nim}
    # access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
    
    response_data = {
        'user': user.to_json(),
        'access_token': access_token
    }
    return jsonify({'success': True, 'message': 'Login berhasil', 'data': response_data})
