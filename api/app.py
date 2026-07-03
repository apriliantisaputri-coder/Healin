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
