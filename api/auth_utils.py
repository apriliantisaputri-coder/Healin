"""
Utilitas autentikasi backend Heal.In.

Modul ini ADITIF -- dibuat untuk mengisi fondasi autentikasi backend
asli (register/login dengan password ter-hash + token sesi) yang
dideskripsikan pada laporan (Bab III.d "Rancangan Antarmuka - Sign In/
Sign Up" dan Bab IV.5 "Tampilan Halaman Login"), tanpa mengubah rule
engine Experta maupun endpoint skrining (/api/gejala, /api/skrining,
/api/health) yang sudah berjalan.

Sebelumnya sistem login hanya berjalan di frontend (localStorage,
password polos, tanpa verifikasi server) -- lihat komentar lama pada
frontend/js/auth.js. Modul ini menggantikan itu dengan mekanisme nyata:
    1. Password di-hash dengan werkzeug.security (PBKDF2), tidak pernah
       disimpan sebagai teks polos.
    2. Saat login berhasil, server menerbitkan token acak (secrets.
       token_urlsafe) yang disimpan di kolom users.auth_token beserta
       waktu kedaluwarsanya (users.token_expires_at).
    3. Endpoint yang butuh login memvalidasi token ini lewat header
       ``Authorization: Bearer <token>`` menggunakan decorator
       require_auth(). Token yang tidak ada, salah, atau sudah
       kedaluwarsa akan direspons dengan HTTP 401 -- inilah yang
       menjadikan skenario "Permintaan tanpa token / token kadaluarsa
       -> 401" pada Bab 4.3.b laporan benar-benar diuji terhadap
       mekanisme sungguhan, bukan sekadar parameter user_email kosong.

Tidak menambah dependensi baru (hanya memakai `secrets` dari stdlib dan
`werkzeug.security` yang sudah otomatis terpasang bersama Flask), sesuai
ruang lingkup proyek (Bab 1.4) yang menghindari infrastruktur tambahan.
"""

import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

# Masa berlaku token sesi. Sengaja dibuat pendek (bukan berbulan-bulan)
# supaya skenario "token kadaluarsa" pada pengujian benar-benar bisa
# ditunjukkan/direproduksi, bukan sekadar teori.
TOKEN_LIFETIME = timedelta(hours=12)


def hash_password(plain_password: str) -> str:
    """Bungkus generate_password_hash agar pemanggilnya tidak perlu tahu
    algoritma spesifik yang dipakai (memudahkan penggantian di masa depan)."""
    return generate_password_hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, plain_password)


def issue_token() -> tuple[str, datetime]:
    """Buat token sesi baru + waktu kedaluwarsanya."""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + TOKEN_LIFETIME
    return token, expires_at


def get_bearer_token() -> str | None:
    """Ambil token dari header ``Authorization: Bearer <token>``."""
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    token = header[len("Bearer ") :].strip()
    return token or None


def get_authenticated_user():
    """Kembalikan objek User yang tokennya valid & belum kedaluwarsa,
    atau None kalau tidak ada/tidak valid/sudah kedaluwarsa.

    Import model di dalam fungsi (bukan di top-level) untuk menghindari
    import melingkar antara api/app.py <-> api/auth_utils.py."""
    from models.models import User

    token = get_bearer_token()
    if not token:
        return None

    user = User.query.filter_by(auth_token=token).first()
    if user is None:
        return None
    if user.token_expires_at is None or user.token_expires_at < datetime.utcnow():
        return None
    return user


def require_auth(view_func):
    """Decorator: wajibkan header Authorization berisi token sesi yang
    valid & belum kedaluwarsa. Mengembalikan 401 kalau tidak ada token,
    token salah, atau token sudah kedaluwarsa -- sesuai skenario
    pengujian API pada Bab 4.3.b laporan.

    User yang berhasil diautentikasi dioper ke view lewat kwarg
    ``current_user`` supaya view tidak perlu query ulang.
    """

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user = get_authenticated_user()
        if user is None:
            return (
                jsonify(
                    {"error": "Autentikasi diperlukan: token tidak ada atau sudah kedaluwarsa."}
                ),
                401,
            )
        return view_func(*args, current_user=user, **kwargs)

    return wrapper
