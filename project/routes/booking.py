from flask import Blueprint, request, jsonify
from project.models import Booking
from project import db
from datetime import datetime

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/booking', methods=['GET'])
def get_all_bookings():
    nim_filter = request.args.get('nim')
    query = Booking.query
    if nim_filter:
        query = query.filter_by(nim=nim_filter)
    
    all_bookings = query.order_by(Booking.tanggal.desc(), Booking.jam.desc()).all()
    result = [booking.to_json() for booking in all_bookings]
    return jsonify({'success': True, 'message': 'Data booking berhasil diambil', 'data': result})

@booking_bp.route('/booking', methods=['POST'])
def create_booking():
    data = request.get_json()
    required_fields = ['nama_mahasiswa', 'nim', 'dosen_id', 'tanggal', 'jam', 'topik_konsultasi']
    if not all(field in data for field in required_fields):
        return jsonify({'success': False, 'message': 'Data input tidak lengkap'}), 400

    existing_booking = Booking.query.filter_by(
        dosen_id=data['dosen_id'],
        tanggal=data['tanggal'],
        jam=data['jam']
    ).filter(Booking.status != 'rejected').first()

    if existing_booking:
        return jsonify({'success': False, 'message': 'Jadwal sudah dibooking. Pilih waktu lain.'}), 409

    try:
        new_booking = Booking(
            nama_mahasiswa=data['nama_mahasiswa'],
            nim=data['nim'],
            dosen_id=data['dosen_id'],
            tanggal=datetime.strptime(data['tanggal'], '%Y-%m-%d').date(),
            jam=datetime.strptime(data['jam'], '%H:%M:%S').time(),
            topik_konsultasi=data['topik_konsultasi']
        )
        db.session.add(new_booking)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Booking berhasil dibuat'}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': f'Gagal membuat booking: {str(e)}'}), 500

@booking_bp.route('/booking/<int:id>', methods=['PUT'])
def update_booking(id):
    booking = Booking.query.get_or_404(id)
    if booking.status != 'pending':
        return jsonify({'success': False, 'message': f'Tidak dapat mengubah booking dengan status: {booking.status}'}), 403
        
    data = request.get_json()
    
    booking.nama_mahasiswa = data.get('nama_mahasiswa', booking.nama_mahasiswa)
    booking.nim = data.get('nim', booking.nim)
    booking.dosen_id = data.get('dosen_id', booking.dosen_id)
    booking.tanggal = datetime.strptime(data.get('tanggal'), '%Y-%m-%d').date() if data.get('tanggal') else booking.tanggal
    booking.jam = datetime.strptime(data.get('jam'), '%H:%M:%S').time() if data.get('jam') else booking.jam
    booking.topik_konsultasi = data.get('topik_konsultasi', booking.topik_konsultasi)
    booking.status = data.get('status', booking.status)
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Booking berhasil diubah', 'data': booking.to_json()})

@booking_bp.route('/booking/<int:id>', methods=['DELETE'])
def delete_booking(id):
    booking = Booking.query.get_or_404(id)
    if booking.status == 'approved':
        return jsonify({'success': False, 'message': 'Tidak dapat menghapus booking yang sudah disetujui'}), 403

    db.session.delete(booking)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Booking berhasil dihapus'})
