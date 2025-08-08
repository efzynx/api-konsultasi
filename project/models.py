# project/models.py
# Di sini kita mendefinisikan semua struktur tabel database menggunakan SQLAlchemy ORM.

from werkzeug.security import check_password_hash, generate_password_hash

from project import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nama = db.Column(db.String(255), nullable=False)
    nim = db.Column(db.String(20), unique=True, nullable=True)
    role = db.Column(db.String(50), nullable=False, default="mahasiswa")

    dosen_profile = db.relationship(
        "Dosen", backref="user_account", uselist=False, cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    # FUNGSI BARU: Untuk mengubah data user menjadi format JSON
    def to_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "nama": self.nama,
            "nim": self.nim,
            "role": self.role,
        }


class Dosen(db.Model):
    __tablename__ = "dosen"
    id = db.Column(db.Integer, primary_key=True)
    nama_dosen = db.Column(db.String(255), nullable=False)
    mata_kuliah = db.Column(db.String(255), nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False
    )

    def to_json(self):
        return {
            "id": self.id,
            "nama_dosen": self.nama_dosen,
            "mata_kuliah": self.mata_kuliah,
            "user_id": self.user_id,
        }


class Booking(db.Model):
    __tablename__ = "booking_konsultasi"
    id = db.Column(db.Integer, primary_key=True)
    nama_mahasiswa = db.Column(db.String(255), nullable=False)
    nim = db.Column(db.String(20), nullable=False)
    dosen_id = db.Column(db.Integer, db.ForeignKey("dosen.id"), nullable=False)
    tanggal = db.Column(db.Date, nullable=False)
    jam = db.Column(db.Time, nullable=False)
    topik_konsultasi = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="pending")

    dosen = db.relationship(
        "Dosen", foreign_keys=[dosen_id], backref=db.backref("bookings", lazy=True)
    )

    def to_json(self):
        return {
            "id": self.id,
            "nama_mahasiswa": self.nama_mahasiswa,
            "nim": self.nim,
            "dosen_id": self.dosen_id,
            "dosen_info": self.dosen.to_json() if self.dosen else None,
            "tanggal": self.tanggal.strftime("%Y-%m-%d"),
            "jam": self.jam.strftime("%H:%M:%S"),
            "topik_konsultasi": self.topik_konsultasi,
            "status": self.status,
        }
