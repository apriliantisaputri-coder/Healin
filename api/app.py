"""
Endpoint Flask untuk sistem pakar Heal.In.

Jalankan dengan:
    flask --app api.app run
atau:
    python api/app.py
Server dapat diakses di http://localhost:5000
"""

import os
import sys

# Pastikan folder root proyek (healin_backend/) ikut masuk ke sys.path,
# supaya import "engine.*" dan "rules.*" tetap berhasil walaupun file
# ini dijalankan langsung dengan `python api/app.py` dari dalam folder api/.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request  # noqa: E402

from engine.knowledge_engine import run_inference  # noqa: E402
from rules.gejala_list import SEMUA_GEJALA  # noqa: E402
from rules.rekomendasi import get_rekomendasi  # noqa: E402

# --------------------------------------------------------------------- #
# Menyajikan folder frontend/ langsung dari Flask (agar pengguna tidak
# perlu menjalankan server terpisah untuk frontend, misalnya Live
# Server). Dengan ini, membuka http://127.0.0.1:5000/ sudah otomatis
# menampilkan index.html beserta seluruh halaman/aset lain (css, js,
# gambar) di frontend/, DAN endpoint /api/* tetap berjalan di origin
# yang sama -- jadi tidak akan ada lagi error CORS/"Failed to fetch"
# akibat frontend & backend dibuka dari alamat yang berbeda.
# --------------------------------------------------------------------- #
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")


@app.route("/")
def serve_frontend_index():
    return app.send_static_file("index.html")


# --------------------------------------------------------------------- #
# Konfigurasi database PostgreSQL (fondasi untuk fitur Login, History,
# Dashboard, dan penyimpanan hasil skrining ke depan).
#
# PENTING: inisialisasi ini bersifat aditif -- tidak mengubah, memindah,
# atau menghapus endpoint /api/gejala, /api/skrining, /api/health yang
# sudah dipakai frontend. Jika koneksi database gagal (mis. PostgreSQL
# belum dinyalakan), aplikasi TETAP berjalan dan endpoint di atas tetap
# berfungsi seperti biasa -- hanya fitur yang butuh database yang akan
# terpengaruh. Pesan error yang jelas dicetak ke log, aplikasi tidak
# crash tanpa informasi.
# --------------------------------------------------------------------- #
from config import Config  # noqa: E402
from models import db  # noqa: E402
from models import models as _models  # noqa: E402,F401  (registrasi tabel ke db.metadata)
from models.models import Condition, ExaminationHistory, User  # noqa: E402
from api.auth_utils import (  # noqa: E402
    get_authenticated_user,
    hash_password,
    issue_token,
    require_auth,
    verify_password,
)

app.config.from_object(Config)
db.init_app(app)

try:
    from flask_migrate import Migrate

    migrate = Migrate(app, db)
except ImportError:
    print(
        "[Heal.In] Flask-Migrate belum terinstal -- jalankan "
        "'pip install -r requirements.txt' untuk mengaktifkan fitur "
        "migrasi database (flask db init/migrate/upgrade)."
    )

with app.app_context():
    try:
        # Percobaan koneksi ringan ke PostgreSQL agar masalah konfigurasi
        # (host/port/kredensial salah, server belum menyala, dsb) segera
        # terlihat jelas di log saat aplikasi start, alih-alih baru
        # muncul samar saat salah satu fitur database diakses nanti.
        from sqlalchemy import text

        with db.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print(f"[Heal.In] Koneksi database '{Config.DATABASE_NAME_FOR_LOG}' OK.")
    except Exception as exc:  # noqa: BLE001
        print(
            "[Heal.In] PERINGATAN: gagal terhubung ke database PostgreSQL "
            f"('{Config.DATABASE_NAME_FOR_LOG}'). Endpoint skrining "
            "(/api/gejala, /api/skrining) tetap berjalan normal karena "
            "tidak bergantung pada database, tetapi fitur yang butuh "
            "penyimpanan data (Login, History, Dashboard) tidak akan "
            f"berfungsi sampai koneksi database diperbaiki. Detail error: {exc}"
        )

# Mengizinkan frontend statis (mis. dibuka lewat Live Server di port lain)
# memanggil API ini dari origin yang berbeda.
try:
    from flask_cors import CORS

    CORS(app)
except ImportError:  # fallback manual jika flask-cors belum terinstal

    @app.after_request
    def _add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
        return response


@app.route("/api/gejala", methods=["GET"])
def daftar_gejala():
    """Mengembalikan daftar gejala yang dikenali sistem, untuk
    ditampilkan sebagai checklist pada formulir frontend."""
    return jsonify(sorted(SEMUA_GEJALA)), 200


def _simpan_riwayat_pemeriksaan(user_email, user_nama, gejala, hasil, rekomendasi):
    """Simpan satu hasil skrining ke tabel ``examination_history`` (PostgreSQL).

    Dipanggil TEPAT SEKALI per request /api/skrining, setelah proses
    inferensi Forward Chaining selesai (``hasil`` sudah final). Fungsi
    ini murni efek samping (side effect) penyimpanan riwayat -- ia
    TIDAK mengubah ``hasil`` maupun response yang dikirim ke frontend,
    dan TIDAK menyentuh rule engine Experta / algoritma Forward Chaining.

    Aturan:
    - Jika pengguna belum login (``user_email`` kosong), riwayat TIDAK
      disimpan. Frontend sudah menegakkan "wajib login" lewat
      ``healinRequireAuth()`` di questionnaire.html/result.html
      (lihat frontend/js/auth.js) -- mekanisme itu tidak diubah sama
      sekali di sini.
    - Karena satu klik "Lihat Hasil" = satu kali panggilan endpoint ini
      (tombol submit dinonaktifkan saat memproses, dan halaman Result
      hanya membaca sessionStorage tanpa memanggil API lagi saat
      di-refresh), maka satu sesi skrining otomatis menghasilkan tepat
      satu baris riwayat -- tidak ada mekanisme tambahan yang
      diperlukan untuk mencegah duplikasi di titik ini.
    - Jika penyimpanan ke database gagal (mis. PostgreSQL belum
      menyala/kredensial salah), error dicatat ke log backend dan
      TIDAK dilempar ke pemanggil, supaya hasil skrining tetap bisa
      ditampilkan ke pengguna seperti biasa.

    Sejak ditambahkannya autentikasi backend asli (lihat api/auth_utils.py
    dan endpoint /api/register, /api/login), fungsi ini lebih diarahkan
    untuk dipakai bersama pengguna yang sudah punya akun ter-hash di
    tabel ``users`` (bukan sekadar dibuat on-the-fly seperti sebelumnya).
    Jika email yang dikirim belum terdaftar, baris ``users`` tetap
    dibuat sebagai fallback (mis. dipanggil dari skenario lama), tetapi
    tanpa password_hash (akun semacam ini tidak bisa dipakai login
    lewat /api/login sampai mendaftar ulang secara normal).
    """
    if not user_email:
        print(
            "[Heal.In] Riwayat skrining TIDAK disimpan: pengguna belum login "
            "(user_email tidak dikirim oleh frontend)."
        )
        return

    try:
        user = User.query.filter_by(email=user_email).first()
        if user is None:
            user = User(
                full_name=user_nama or user_email,
                email=user_email,
                password_hash="",
            )
            db.session.add(user)
            db.session.flush()  # supaya user.id tersedia untuk FK di bawah

        kondisi_nama = hasil["kondisi"]
        condition = Condition.query.filter_by(condition_name=kondisi_nama).first()
        severity = condition.severity if condition is not None else None

        riwayat = ExaminationHistory(
            user_id=user.id,
            detected_condition=kondisi_nama,
            severity=severity,
            selected_symptoms=gejala,
            explanation_trace=hasil["explanation_trace"],
            recommendation=rekomendasi,
        )
        db.session.add(riwayat)
        db.session.commit()
        print(
            f"[Heal.In] Riwayat skrining tersimpan (user_id={user.id}, " f"kondisi={kondisi_nama})."
        )
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        print(
            "[Heal.In] PERINGATAN: gagal menyimpan riwayat skrining ke "
            f"PostgreSQL. Hasil skrining tetap ditampilkan ke pengguna seperti "
            f"biasa. Detail error: {exc}"
        )


@app.route("/api/skrining", methods=["POST"])
def skrining():
    """Menerima daftar gejala yang dicentang pengguna, menjalankan
    mesin inferensi Forward Chaining, dan mengembalikan hasil skrining
    beserta penjelasan alur penalaran (explanation trace)."""
    data = request.get_json(silent=True) or {}
    gejala = data.get("gejala", [])

    if not isinstance(gejala, list) or len(gejala) == 0:
        return jsonify({"error": "Minimal pilih 1 gejala"}), 422

    tidak_dikenali = [g for g in gejala if g not in SEMUA_GEJALA]
    if tidak_dikenali:
        return jsonify({"error": f"Gejala tidak dikenali: {tidak_dikenali}"}), 422

    hasil = run_inference(gejala)
    rekomendasi = get_rekomendasi(hasil["kondisi"])

    # Titik penyimpanan riwayat: TEPAT setelah inferensi Forward Chaining
    # selesai (hasil final) dan rekomendasi akhir sudah didapat -- lihat
    # docstring _simpan_riwayat_pemeriksaan() di atas. Dibungkus try/except
    # di dalam fungsi tersebut sehingga kegagalan database tidak pernah
    # menggagalkan response di bawah ini.
    # Utamakan identitas dari token sesi (Authorization: Bearer <token>)
    # kalau pengguna sedang login lewat autentikasi backend yang baru;
    # fallback ke user_email/user_nama pada body request untuk menjaga
    # kompatibilitas mundur dengan alur lama.
    authed_user = get_authenticated_user()
    if authed_user is not None:
        user_email = authed_user.email
        user_nama = authed_user.full_name
    else:
        user_email = (data.get("user_email") or "").strip().lower() or None
        user_nama = (data.get("user_nama") or "").strip() or None
    _simpan_riwayat_pemeriksaan(user_email, user_nama, gejala, hasil, rekomendasi)

    return (
        jsonify(
            {
                "kondisi": hasil["kondisi"],
                "skor": hasil["skor"],
                "explanation_trace": hasil["explanation_trace"],
                "rekomendasi": rekomendasi,
            }
        ),
        200,
    )


# --------------------------------------------------------------------- #
# Autentikasi backend (Register / Login / Logout / Me) -- ADITIF.
#
# Menggantikan mekanisme lama yang murni "demo/frontend-only" (password
# polos di localStorage, tanpa verifikasi server) dengan autentikasi
# sungguhan: password di-hash (werkzeug.security), dan sesi login
# direpresentasikan sebagai token acak yang disimpan di kolom
# users.auth_token + users.token_expires_at (lihat api/auth_utils.py).
# TIDAK menyentuh /api/gejala, /api/skrining (selain penambahan dukungan
# token di bawah), /api/health, maupun rule engine Experta.
# --------------------------------------------------------------------- #


@app.route("/api/register", methods=["POST"])
def register():
    """Daftarkan akun baru. Password di-hash sebelum disimpan; TIDAK
    pernah menyimpan password dalam bentuk teks polos."""
    data = request.get_json(silent=True) or {}
    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    age = data.get("age")
    study_program = (data.get("study_program") or "").strip() or None

    if not full_name or not email or not password:
        return jsonify({"error": "Nama lengkap, email, dan kata sandi wajib diisi."}), 422
    if len(password) < 6:
        return jsonify({"error": "Kata sandi minimal 6 karakter."}), 422

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({"error": "Email ini sudah terdaftar. Silakan masuk saja."}), 409

    try:
        age_value = int(age) if age not in (None, "") else None
    except (TypeError, ValueError):
        return jsonify({"error": "Usia harus berupa angka."}), 422

    token, expires_at = issue_token()
    user = User(
        full_name=full_name,
        email=email,
        password_hash=hash_password(password),
        age=age_value,
        study_program=study_program,
        auth_token=token,
        token_expires_at=expires_at,
    )
    db.session.add(user)
    db.session.commit()

    return (
        jsonify(
            {
                "token": token,
                "expires_at": expires_at.isoformat(),
                "user": {"id": user.id, "full_name": user.full_name, "email": user.email},
            }
        ),
        201,
    )


@app.route("/api/login", methods=["POST"])
def login():
    """Verifikasi email + kata sandi, lalu terbitkan token sesi baru."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email dan kata sandi wajib diisi."}), 422

    user = User.query.filter_by(email=email).first()
    if user is None or not verify_password(password, user.password_hash):
        return jsonify({"error": "Email atau kata sandi salah."}), 401

    token, expires_at = issue_token()
    user.auth_token = token
    user.token_expires_at = expires_at
    db.session.commit()

    return (
        jsonify(
            {
                "token": token,
                "expires_at": expires_at.isoformat(),
                "user": {"id": user.id, "full_name": user.full_name, "email": user.email},
            }
        ),
        200,
    )


@app.route("/api/logout", methods=["POST"])
@require_auth
def logout(current_user):
    """Cabut token sesi yang sedang dipakai (invalidasi di sisi server)."""
    current_user.auth_token = None
    current_user.token_expires_at = None
    db.session.commit()
    return jsonify({"message": "Berhasil keluar."}), 200


@app.route("/api/me", methods=["GET"])
def me():
    """Cek status sesi saat ini. Mengembalikan 401 kalau token tidak
    ada, salah, atau sudah kedaluwarsa -- dipakai frontend untuk
    memvalidasi sesi tersimpan saat halaman dimuat."""
    user = get_authenticated_user()
    if user is None:
        return jsonify({"error": "Sesi tidak valid atau sudah kedaluwarsa."}), 401
    return jsonify({"id": user.id, "full_name": user.full_name, "email": user.email}), 200


# --------------------------------------------------------------------- #
# Fitur Riwayat Pemeriksaan (History) -- ADITIF, membaca data yang sudah
# tersimpan di tabel examination_history lewat _simpan_riwayat_pemeriksaan()
# di atas. TIDAK menyentuh /api/gejala, /api/skrining, /api/health,
# maupun rule engine Experta / algoritma Forward Chaining sama sekali.
#
# Endpoint di bawah ini dilindungi token sesi asli (lihat require_auth
# pada api/auth_utils.py): permintaan tanpa header ``Authorization:
# Bearer <token>``, dengan token salah, atau token sudah kedaluwarsa
# akan direspons 401 -- inilah yang membuat skenario pengujian "tanpa
# token / token kadaluarsa -> 401" pada Bab 4.3.b laporan benar-benar
# teruji terhadap mekanisme sungguhan. Kepemilikan data (user hanya
# bisa melihat/menghapus riwayat miliknya sendiri) tetap ditegakkan di
# backend dengan mencocokkan user_id pemilik riwayat terhadap
# current_user hasil autentikasi token, bukan sekadar mengandalkan
# frontend.
# --------------------------------------------------------------------- #

INDO_MONTHS = [
    "Januari",
    "Februari",
    "Maret",
    "April",
    "Mei",
    "Juni",
    "Juli",
    "Agustus",
    "September",
    "Oktober",
    "November",
    "Desember",
]


def _format_tanggal_indo(dt):
    """Format datetime -> "20 Juli 2026" (dipakai untuk pencarian by tanggal)."""
    return f"{dt.day} {INDO_MONTHS[dt.month - 1]} {dt.year}"


def _get_user_by_email(email):
    if not email:
        return None
    return User.query.filter_by(email=email).first()


@app.route("/history", methods=["GET"])
@require_auth
def get_history_list(current_user):
    """Mengembalikan riwayat pemeriksaan milik pengguna yang sedang login
    (diurutkan tanggal terbaru -> terlama), mendukung pencarian sederhana
    (tanggal/kondisi) dan pagination supaya tidak memuat seluruh data
    sekaligus. Identitas pengguna diambil dari token sesi (require_auth),
    bukan dari parameter user_email yang mudah dipalsukan di sisi klien."""
    user = current_user

    try:
        page = max(int(request.args.get("page", 1)), 1)
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = max(min(int(request.args.get("per_page", 10)), 50), 1)
    except (TypeError, ValueError):
        per_page = 10

    q = (request.args.get("q") or "").strip().lower()

    from sqlalchemy import desc

    base_query = ExaminationHistory.query.filter_by(user_id=user.id)

    if q:
        # Pencarian mencakup nama kondisi maupun tanggal dalam format
        # Indonesia (mis. "20 juli"). Karena data yang difilter hanya
        # milik SATU pengguna (bukan seluruh tabel), jumlahnya kecil,
        # jadi pencocokan tanggal dilakukan di Python setelah diambil
        # dari database.
        semua = base_query.order_by(desc(ExaminationHistory.examination_date)).all()
        hasil_pencarian = [
            r
            for r in semua
            if q in r.detected_condition.lower()
            or q in _format_tanggal_indo(r.examination_date).lower()
        ]
        total = len(hasil_pencarian)
        total_pages = max((total + per_page - 1) // per_page, 1)
        page = min(page, total_pages)
        items = hasil_pencarian[(page - 1) * per_page : (page - 1) * per_page + per_page]
    else:
        ordered_query = base_query.order_by(desc(ExaminationHistory.examination_date))
        total = ordered_query.count()
        total_pages = max((total + per_page - 1) // per_page, 1)
        page = min(page, total_pages)
        items = ordered_query.offset((page - 1) * per_page).limit(per_page).all()

    data = [
        {
            "id": r.id,
            "examination_date": r.examination_date.isoformat(),
            "detected_condition": r.detected_condition,
            "severity": r.severity,
            "recommendation_summary": (r.recommendation or [None])[0],
        }
        for r in items
    ]

    return (
        jsonify(
            {
                "data": data,
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            }
        ),
        200,
    )


@app.route("/history/<int:history_id>", methods=["GET"])
@require_auth
def get_history_detail(history_id, current_user):
    """Mengembalikan detail satu riwayat pemeriksaan, HANYA apabila
    riwayat tersebut milik pengguna yang sedang login (diautentikasi
    lewat token sesi, bukan parameter user_email)."""
    user = current_user

    riwayat = ExaminationHistory.query.get(history_id)
    if riwayat is None:
        return jsonify({"error": "Riwayat tidak ditemukan."}), 404
    if riwayat.user_id != user.id:
        # Mencegah user membuka history milik pengguna lain lewat
        # perubahan URL (mis. /history/5 -> /history/6).
        return jsonify({"error": "Anda tidak memiliki akses ke riwayat ini."}), 403

    return (
        jsonify(
            {
                "id": riwayat.id,
                "examination_date": riwayat.examination_date.isoformat(),
                "user_full_name": user.full_name,
                "detected_condition": riwayat.detected_condition,
                "severity": riwayat.severity,
                "selected_symptoms": riwayat.selected_symptoms,
                "explanation_trace": riwayat.explanation_trace,
                "recommendation": riwayat.recommendation,
            }
        ),
        200,
    )


@app.route("/history/<int:history_id>", methods=["DELETE"])
@require_auth
def delete_history(history_id, current_user):
    """Menghapus satu riwayat pemeriksaan, HANYA apabila riwayat
    tersebut milik pengguna yang sedang login (diautentikasi lewat
    token sesi, bukan parameter user_email)."""
    user = current_user

    riwayat = ExaminationHistory.query.get(history_id)
    if riwayat is None:
        return jsonify({"error": "Riwayat tidak ditemukan."}), 404
    if riwayat.user_id != user.id:
        return jsonify({"error": "Anda tidak memiliki akses untuk menghapus riwayat ini."}), 403

    try:
        db.session.delete(riwayat)
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({"error": f"Gagal menghapus riwayat: {exc}"}), 500

    return jsonify({"message": "Riwayat berhasil dihapus."}), 200


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(debug=True)
