# project/routes/dosen.py
# Berisi endpoint untuk mendapatkan, menambah, MENGUBAH, dan MENGHAPUS data dosen.

from flask import Blueprint, jsonify, request
from project.models import Dosen, User, Booking
from project import db

dosen_bp = Blueprint('dosen', __name__)

# Fungsi ini menangani method GET
@dosen_bp.route('/dosen', methods=['GET'])
def get_all_dosen():
    try:
        all_dosen = Dosen.query.all()
        result = [dosen.to_json() for dosen in all_dosen]
        return jsonify({'success': True, 'message': 'Data dosen berhasil diambil', 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Gagal mengambil data: {str(e)}'}), 500

# Fungsi ini menangani method POST
@dosen_bp.route('/dosen', methods=['POST'])
def add_dosen():
    data = request.get_json()
    required_fields = ['nama_dosen', 'mata_kuliah', 'username', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'success': False, 'message': 'Data nama_dosen, mata_kuliah, username, dan password diperlukan'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'message': 'Username sudah terdaftar'}), 409

    try:
        # 1. Buat akun login untuk dosen di tabel users
        new_user_dosen = User(
            username=data['username'],
            nama=data['nama_dosen'],
            role='dosen'
        )
        new_user_dosen.set_password(data['password'])
        db.session.add(new_user_dosen)
        db.session.flush() # Untuk mendapatkan ID dari user yang baru dibuat

        # 2. Buat entri di tabel dosen dan hubungkan dengan user_id
        new_dosen = Dosen(
            nama_dosen=data['nama_dosen'],
            mata_kuliah=data['mata_kuliah'],
            user_id=new_user_dosen.id # Menghubungkan ke akun user
        )
        db.session.add(new_dosen)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Dosen berhasil ditambahkan'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Gagal menambahkan dosen: {str(e)}'}), 500

# ENDPOINT BARU: Untuk mengubah data dosen
@dosen_bp.route('/dosen/<int:id>', methods=['PUT'])
def update_dosen(id):
    dosen = Dosen.query.get_or_404(id)
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': 'Request body tidak boleh kosong'}), 400

    dosen.nama_dosen = data.get('nama_dosen', dosen.nama_dosen)
    dosen.mata_kuliah = data.get('mata_kuliah', dosen.mata_kuliah)

    # Jika nama dosen diubah, ubah juga nama di akun user-nya agar konsisten
    if 'nama_dosen' in data:
        user = User.query.get(dosen.user_id)
        if user:
            user.nama = data['nama_dosen']

    db.session.commit()
    return jsonify({'success': True, 'message': 'Data dosen berhasil diubah'})

# ENDPOINT BARU: Untuk menghapus data dosen
@dosen_bp.route('/dosen/<int:id>', methods=['DELETE'])
def delete_dosen(id):
    dosen = Dosen.query.get_or_404(id)
    user = User.query.get(dosen.user_id)

    try:
        # Hapus semua booking yang terkait dengan dosen ini terlebih dahulu
        Booking.query.filter_by(dosen_id=id).delete()
        
        # Hapus data dosen dari tabel Dosen
        db.session.delete(dosen)
        
        # Hapus akun login dosen dari tabel User
        if user:
            db.session.delete(user)
            
        db.session.commit()
        return jsonify({'success': True, 'message': 'Dosen dan semua data terkait berhasil dihapus'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Gagal menghapus dosen: {str(e)}'}), 500
