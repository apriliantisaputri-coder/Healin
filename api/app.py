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

app = Flask(__name__)

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
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return response



@app.route("/api/gejala", methods=["GET"])
def daftar_gejala():
    """Mengembalikan daftar gejala yang dikenali sistem, untuk
    ditampilkan sebagai checklist pada formulir frontend."""
    return jsonify(sorted(SEMUA_GEJALA)), 200


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

    return (
        jsonify(
            {
                "kondisi": hasil["kondisi"],
                "skor": hasil["skor"],
                "explanation_trace": hasil["explanation_trace"],
                "rekomendasi": get_rekomendasi(hasil["kondisi"]),
            }
        ),
        200,
    )


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(debug=True)
