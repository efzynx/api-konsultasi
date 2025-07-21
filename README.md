# API Booking Jadwal Konsultasi Dosen

Ini adalah backend API untuk aplikasi mobile "Booking Jadwal Konsultasi Dosen". API ini dibangun menggunakan Python dengan framework Flask dan dirancang untuk di-deploy menggunakan Docker. API ini menyediakan semua fungsionalitas yang dibutuhkan, mulai dari otentikasi pengguna hingga manajemen jadwal konsultasi (CRUD).

Proyek ini dibuat sebagai pemenuhan tugas Ujian Akhir Semester (UAS) mata kuliah Mobile Computing.

## Fitur

-   **Otentikasi Pengguna**: Registrasi untuk mahasiswa dan login untuk semua peran (mahasiswa & dosen).
-   **Manajemen Dosen (CRUD)**: Admin dapat menambah, melihat, mengubah, dan menghapus data dosen.
-   **Manajemen Mahasiswa (CRUD)**: Admin dapat melihat daftar mahasiswa, dan pengguna dapat mengubah serta menghapus akunnya.
-   **Manajemen Booking (CRUD)**: Mahasiswa dapat membuat, melihat, mengubah, dan membatalkan jadwal konsultasi.
-   **Modular**: Struktur proyek yang rapi dan mudah dikelola.
-   **Siap Produksi**: Dilengkapi dengan konfigurasi Docker dan Gunicorn untuk deployment yang mudah dan andal.

---

## Instalasi & Konfigurasi

Anda bisa menjalankan proyek ini dengan dua cara: secara lokal untuk development atau menggunakan Docker untuk simulasi produksi/deployment.

### 1. Instalasi Lokal (Untuk Development)

**Prasyarat:**
-   Python 3.8+
-   Server MariaDB/MySQL
-   Virtual Environment

**Langkah-langkah:**

1.  **Clone repository:**
    ```bash
    git clone https://github.com/username/nama-repo.git
    cd nama-repo
    ```

2.  **Buat dan aktifkan virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install semua dependensi:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Konfigurasi database:**
    - Buat database baru di MariaDB/MySQL Anda.
    - Buat file `.env` dan isi dengan konfigurasi koneksi database Anda.
      ```env
      SECRET_KEY=kunci_rahasia_untuk_development
      DATABASE_URL=mysql+pymysql://user_db:password_db@localhost/nama_db
      ```

5.  **Jalankan aplikasi:**
    ```bash
    python run.py
    ```
    API akan berjalan di `http://127.0.0.1:5000`.

### 2. Instalasi dengan Docker (Untuk Produksi/Deployment)

**Prasyarat:**
-   Docker
-   Docker Compose

**Langkah-langkah:**

1.  **Clone repository** ke server atau lokal Anda.

2.  **Buat file `.env`** di direktori utama. File ini akan digunakan oleh Docker Compose untuk mengkonfigurasi semua service.
    ```env
    # Gunakan kunci yang sangat acak dan panjang untuk produksi
    SECRET_KEY=kunci_rahasia_produksi_yang_sangat_panjang_dan_aman

    # Variabel untuk aplikasi Flask (perhatikan host 'db')
    DATABASE_URL=mysql+pymysql://user_db_anda:password_db_anda@db:3306/nama_db_anda

    # Variabel untuk service database di docker-compose
    MYSQL_ROOT_PASSWORD=password_root_yang_sangat_aman
    MYSQL_DATABASE=nama_db_anda
    MYSQL_USER=user_db_anda
    MYSQL_PASSWORD=password_db_anda
    ```

3.  **Jalankan Docker Compose:**
    ```bash
    sudo docker compose up -d --build
    ```
    Perintah ini akan membangun image, membuat container untuk aplikasi dan database, dan menjalankannya di background. API akan dapat diakses melalui port 5000 di server Anda.

---

## Struktur Proyek

```
/
├── .env                  # File konfigurasi (tidak di-commit)
├── .gitignore            # Mengabaikan file yang tidak perlu
├── compose.yaml          # Konfigurasi Docker Compose untuk produksi
├── Dockerfile            # Resep untuk membangun image aplikasi
├── requirements.txt      # Daftar dependensi Python
├── run.py                # Titik masuk untuk menjalankan server development
├── wsgi.py               # Titik masuk untuk server produksi (Gunicorn)
└── /project/
    ├── __init__.py       # App Factory: menginisialisasi aplikasi dan rute
    ├── models.py         # Definisi model database (SQLAlchemy)
    └── /routes/
        ├── auth.py       # Rute untuk /register dan /login
        ├── booking.py    # Rute CRUD untuk /booking
        ├── dosen.py      # Rute CRUD untuk /dosen
        └── user.py       # Rute CRUD untuk /user dan /mahasiswa
```

---

## Dokumentasi API

Base URL: `http://127.0.0.1:5000` (Lokal) atau `https://api.domainanda.com` (Produksi)

### Otentikasi

#### `POST /register`
Mendaftarkan akun baru khusus untuk mahasiswa.
- **Body (JSON):**
  ```json
  {
      "username": "mahasiswa_baru",
      "password": "passwordrahasia",
      "nama": "Nama Lengkap Mahasiswa",
      "nim": "200403010010"
  }
  ```
- **Respons Sukses (201):**
  ```json
  {
      "success": true,
      "message": "Registrasi mahasiswa berhasil"
  }
  ```

#### `POST /login`
Login untuk semua peran (mahasiswa dan dosen).
- **Body (JSON):**
  ```json
  {
      "username": "mahasiswa_baru",
      "password": "passwordrahasia"
  }
  ```
- **Respons Sukses (200):**
  ```json
  {
      "success": true,
      "message": "Login berhasil",
      "data": {
          "id": 1,
          "nama": "Nama Lengkap Mahasiswa",
          "nim": "200403010010",
          "role": "mahasiswa",
          "username": "mahasiswa_baru"
      }
  }
  ```

### Mahasiswa

#### `GET /mahasiswa`
Mendapatkan daftar semua user dengan peran 'mahasiswa'.
- **Respons Sukses (200):**
  ```json
  {
      "success": true,
      "data": [
          {
              "id": 1,
              "nama": "Nama Lengkap Mahasiswa",
              "nim": "200403010010",
              "role": "mahasiswa",
              "username": "mahasiswa_baru"
          }
      ]
  }
  ```

#### `PUT /user/{id}`
Mengubah data user (mahasiswa atau dosen).
- **URL Params:** `id` -> ID user yang akan diubah.
- **Body (JSON):**
  ```json
  {
      "nama": "Nama Baru",
      "password": "password_baru_jika_ingin_diubah"
  }
  ```
- **Respons Sukses (200):** `{"success": true, "message": "Data user berhasil diubah"}`

#### `DELETE /user/{id}`
Menghapus akun mahasiswa.
- **URL Params:** `id` -> ID user mahasiswa yang akan dihapus.
- **Respons Sukses (200):** `{"success": true, "message": "User mahasiswa berhasil dihapus"}`

### Dosen

#### `POST /dosen`
Menambahkan dosen baru (hanya oleh admin).
- **Body (JSON):**
  ```json
  {
      "nama_dosen": "Dr. Nama Dosen, M.Kom",
      "mata_kuliah": "Nama Mata Kuliah",
      "username": "username_dosen",
      "password": "password_dosen"
  }
  ```
- **Respons Sukses (201):** `{"success": true, "message": "Dosen berhasil ditambahkan"}`

#### `GET /dosen`
Mendapatkan daftar semua dosen.
- **Respons Sukses (200):**
  ```json
  {
      "success": true,
      "data": [
          {
              "id": 1,
              "nama_dosen": "Dr. Nama Dosen, M.Kom",
              "mata_kuliah": "Nama Mata Kuliah",
              "user_id": 2
          }
      ]
  }
  ```

#### `PUT /dosen/{id}`
Mengubah data dosen.
- **URL Params:** `id` -> ID dosen yang akan diubah.
- **Body (JSON):**
  ```json
  {
      "nama_dosen": "Nama Dosen Baru, M.Sc.",
      "mata_kuliah": "Mata Kuliah Baru"
  }
  ```
- **Respons Sukses (200):** `{"success": true, "message": "Data dosen berhasil diubah"}`

#### `DELETE /dosen/{id}`
Menghapus data dosen beserta akun login dan semua booking terkait.
- **URL Params:** `id` -> ID dosen yang akan dihapus.
- **Respons Sukses (200):** `{"success": true, "message": "Dosen dan semua data terkait berhasil dihapus"}`

### Booking

#### `POST /booking`
Membuat jadwal booking konsultasi baru.
- **Body (JSON):**
  ```json
  {
      "nama_mahasiswa": "Nama Mahasiswa",
      "nim": "NIM Mahasiswa",
      "dosen_id": 1,
      "tanggal": "YYYY-MM-DD",
      "jam": "HH:MM:SS",
      "topik_konsultasi": "Topik yang akan dibahas"
  }
  ```
- **Respons Sukses (201):** `{"success": true, "message": "Booking berhasil dibuat"}`

#### `GET /booking`
Mendapatkan daftar semua jadwal booking.
- **Respons Sukses (200):**
  ```json
  {
      "success": true,
      "data": [
          {
              "id": 1,
              "nama_mahasiswa": "Nama Mahasiswa",
              "nim": "NIM Mahasiswa",
              "dosen_id": 1,
              "dosen_info": {
                  "id": 1,
                  "nama_dosen": "Dr. Nama Dosen, M.Kom",
                  "mata_kuliah": "Nama Mata Kuliah",
                  "user_id": 2
              },
              "tanggal": "YYYY-MM-DD",
              "jam": "HH:MM:SS",
              "topik_konsultasi": "Topik yang akan dibahas",
              "status": "pending"
          }
      ]
  }
  ```

#### `PUT /booking/{id}`
Mengubah data booking (misal: status oleh dosen).
- **URL Params:** `id` -> ID booking yang akan diubah.
- **Body (JSON):**
  ```json
  {
      "status": "approved"
  }
  ```
- **Respons Sukses (200):** `{"success": true, "message": "Booking berhasil diubah", ...}`

#### `DELETE /booking/{id}`
Menghapus/membatalkan jadwal booking.
- **URL Params:** `id` -> ID booking yang akan dihapus.
- **Respons Sukses (200):** `{"success": true, "message": "Booking berhasil dihapus"}`
