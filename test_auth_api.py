"""
Unit test end-to-end untuk endpoint autentikasi (register/login/logout)
dan proteksi token pada endpoint riwayat (/history), sesuai skenario
pengujian API pada Bab 4.3.b laporan ("Permintaan tanpa token / token
kadaluarsa -> 401").

Memakai SQLite in-memory (bukan PostgreSQL) supaya test ini bisa
dijalankan langsung tanpa perlu menyalakan server database -- cukup
untuk memverifikasi LOGIKA endpoint (bukan pengujian PostgreSQL itu
sendiri, yang tetap memakai Config asli saat aplikasi berjalan normal).

Jalankan: pytest test_auth_api.py -v
"""

import pytest

from api.app import app, db


@pytest.fixture
def client():
    app.config.update(SQLALCHEMY_DATABASE_URI="sqlite:///:memory:", TESTING=True)
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_register_lalu_login_menghasilkan_token(client):
    resp = client.post(
        "/api/register",
        json={"full_name": "Andi Tes", "email": "andi@test.com", "password": "rahasia123"},
    )
    assert resp.status_code == 201
    assert "token" in resp.get_json()

    resp2 = client.post("/api/login", json={"email": "andi@test.com", "password": "rahasia123"})
    assert resp2.status_code == 200
    assert "token" in resp2.get_json()


def test_login_password_salah_mengembalikan_401(client):
    client.post(
        "/api/register",
        json={"full_name": "Budi", "email": "budi@test.com", "password": "sandiaman"},
    )
    resp = client.post("/api/login", json={"email": "budi@test.com", "password": "salah"})
    assert resp.status_code == 401


def test_register_email_duplikat_mengembalikan_409(client):
    payload = {"full_name": "Citra", "email": "citra@test.com", "password": "sandiaman"}
    client.post("/api/register", json=payload)
    resp = client.post("/api/register", json=payload)
    assert resp.status_code == 409


def test_history_tanpa_token_mengembalikan_401(client):
    """Skenario Bab 4.3.b: 'Permintaan tanpa token' -> 401."""
    resp = client.get("/history")
    assert resp.status_code == 401


def test_history_dengan_token_salah_mengembalikan_401(client):
    """Skenario Bab 4.3.b: 'token kadaluarsa/tidak valid' -> 401."""
    resp = client.get("/history", headers={"Authorization": "Bearer token-tidak-valid"})
    assert resp.status_code == 401


def test_history_dengan_token_valid_mengembalikan_200(client):
    reg = client.post(
        "/api/register",
        json={"full_name": "Dewi", "email": "dewi@test.com", "password": "sandiaman"},
    )
    token = reg.get_json()["token"]

    resp = client.get("/history", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["data"] == []  # belum pernah skrining -> riwayat kosong


def test_logout_membuat_token_lama_tidak_berlaku_lagi(client):
    reg = client.post(
        "/api/register",
        json={"full_name": "Eka", "email": "eka@test.com", "password": "sandiaman"},
    )
    token = reg.get_json()["token"]

    logout_resp = client.post("/api/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout_resp.status_code == 200

    # Token yang sama tidak lagi valid setelah logout.
    resp = client.get("/history", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
