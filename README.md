# Sistem Otomatisasi Sertifikat Webinar (Flask + PostgreSQL)

Project ini menyiapkan aplikasi Flask untuk:
- Integrasi API kehadiran peserta webinar
- Penentuan kelulusan
- Penerbitan sertifikat digital (halaman cetak)

Catatan: Dokumen UAS menyebut SQLite, tetapi implementasi ini memakai PostgreSQL sesuai kebutuhan Anda. Jika tetap perlu SQLite, saya bisa siapkan varian konfigurasi.

## Struktur
- `app/` kode aplikasi
- `app/templates/` halaman UI
- `app/models.py` model database
- `app/services/attendance_api.py` integrasi API
- `migrations/` hasil Flask-Migrate
- `wsgi.py` entry point

## Setup Lokal

1. Buat virtualenv dan install dependencies.
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Siapkan environment.
```bash
cp .env.example .env
```

3. Jalankan migrasi.
```bash
export FLASK_APP=wsgi.py
flask db init
flask db migrate -m "init"
flask db upgrade
```

4. Run app.
```bash
flask --app wsgi.py run --debug
```

## API Kehadiran
Aplikasi mengirim request ke `ATTENDANCE_API_URL` dengan parameter:
- `email` atau `participant_id`

Jika `USE_MOCK_API=1`, data dummy digunakan.

## Auth Admin
- Session login via `/admin/login`
- Token Bearer: gunakan header `Authorization: Bearer <token>` untuk akses endpoint admin (token dibuat via dashboard).
- Admin default dibuat via migrasi:
  - Email: `admin@example.com`
  - Password: `admin123`

## Alur Integrasi
1. Form verifikasi mengirim email/ID
2. Aplikasi memanggil API kehadiran
3. Data disimpan ke database
4. Sistem menentukan kelulusan
5. Jika lulus, nomor sertifikat dibuat otomatis

## Endpoint Aplikasi
- `GET /` landing page
- `GET /events/<id>` detail event + form pendaftaran
- `POST /events/<id>/register` proses daftar
- `GET /invite/<code>` link invitation / referral
- `GET /admin/login` login admin
- `POST /admin/token/regenerate` buat token admin (Bearer)
- `GET/POST /admin/reset` request reset password
- `GET/POST /admin/reset/<token>` reset password
- `GET /admin` dashboard admin
- `GET /admin/events/<id>/registrations` list pendaftar
- `GET /admin/events/<id>/registrations.csv` export CSV
- `POST /admin/events/<id>/meet-generate` generate link Google Meet
- `GET /user/register` registrasi peserta
- `GET /user/login` login peserta
- `GET /user/dashboard` dashboard peserta
- `GET/POST /user/reset` reset password peserta
- `GET/POST /user/reset/<token>` reset password peserta
- `GET /user/profile` profil peserta
- `POST /user/profile/photo` upload foto profil
- `GET /user/verify/<token>` verifikasi email peserta
