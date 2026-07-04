/**
 * Konfigurasi & helper untuk memanggil REST API Heal.In (Flask).
 * Ganti API_BASE_URL kalau backend dijalankan di alamat/port lain.
 *
 * PENTING: sejak perubahan ini, proses SKRINING (apiGetDaftarGejala &
 * apiPostSkrining) TIDAK lagi memanggil backend Flask -- keduanya
 * dihitung langsung di browser oleh frontend/js/skrining-engine.js
 * (porting 1:1 dari engine Python di engine/ + rules/). Jadi halaman
 * questionnaire.html -> result.html bisa dipakai dan langsung
 * menampilkan hasil TANPA menjalankan server apa pun, termasuk saat
 * file HTML-nya dibuka langsung (double-click / file://).
 *
 * API_BASE_URL & fetch ke Flask di bawah ini hanya masih dipakai oleh
 * fitur Riwayat Pemeriksaan (History) & Login, yang memang butuh
 * database untuk menyimpan data lintas sesi -- fitur itu TETAP opsional
 * dan tidak memengaruhi alur "Lihat Hasil" sama sekali.
 */
const API_BASE_URL = "http://127.0.0.1:5000";

/** Header Authorization: Bearer <token> dari sesi tersimpan (kalau ada). */
function authHeader() {
  const session = typeof healinGetSession === "function" ? healinGetSession() : null;
  return session && session.token ? { Authorization: `Bearer ${session.token}` } : {};
}

/* =========================================================
   AUTENTIKASI BACKEND (Register / Login / Logout)
   ========================================================= */

async function apiRegister({ fullName, email, password, age, studyProgram }) {
  const res = await fetch(`${API_BASE_URL}/api/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      full_name: fullName,
      email,
      password,
      age: age || null,
      study_program: studyProgram || null,
    }),
  });
  const data = await res.json();
  if (!res.ok) {
    const err = new Error(data.error || "Gagal mendaftar.");
    err.status = res.status;
    throw err;
  }
  return data; // { token, expires_at, user }
}

async function apiLogin({ email, password }) {
  const res = await fetch(`${API_BASE_URL}/api/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (!res.ok) {
    const err = new Error(data.error || "Email atau kata sandi salah.");
    err.status = res.status;
    throw err;
  }
  return data; // { token, expires_at, user }
}

async function apiLogout() {
  const res = await fetch(`${API_BASE_URL}/api/logout`, {
    method: "POST",
    headers: { ...authHeader() },
  });
  if (!res.ok && res.status !== 401) {
    throw new Error("Gagal keluar dari sesi.");
  }
  return true;
}

async function apiGetDaftarGejala() {
  // Diambil dari engine lokal (skrining-engine.js), bukan dari server.
  return [...SEMUA_GEJALA].sort();
}

async function apiPostSkrining(daftarGejala, user) {
  // Dihitung sepenuhnya di browser -- lihat skrining-engine.js.
  const hasil = await jalankanSkriningLocal(daftarGejala);

  // Simpan ke Riwayat Pemeriksaan di backend secara BEST-EFFORT saja:
  // kalau user login (token dikirim lewat Authorization header) DAN
  // backend Flask kebetulan sedang menyala, hasil akan tersinkron ke
  // History. Kalau backend mati/tidak ada, ini gagal secara diam-diam
  // (tidak melempar error) supaya alur "Lihat Hasil" tidak pernah
  // terganggu oleh ada/tidaknya server.
  if (user && user.email) {
    fetch(`${API_BASE_URL}/api/skrining`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeader() },
      body: JSON.stringify({
        gejala: daftarGejala,
        user_email: user.email,
        user_nama: user.nama,
      }),
    }).catch(() => {
      /* Backend tidak tersedia -- abaikan, hasil tetap tampil dari engine lokal. */
    });
  }

  return hasil;
}

/* =========================================================
   RIWAYAT PEMERIKSAAN (History) — ADITIF, tidak mengubah
   fungsi apiPostSkrining/apiGetDaftarGejala di atas.
   Mengikuti pola yang sama: kirim user_email dari sesi
   localStorage (healinGetSession()) supaya backend tahu
   riwayat siapa yang boleh diakses.
   ========================================================= */

async function apiGetHistoryList({ page = 1, perPage = 10, q = "" } = {}) {
  const params = new URLSearchParams({ page, per_page: perPage });
  if (q) params.set("q", q);

  const res = await fetch(`${API_BASE_URL}/history?${params.toString()}`, {
    headers: { ...authHeader() },
  });
  const data = await res.json();
  if (!res.ok) {
    const err = new Error(data.error || "Gagal mengambil riwayat pemeriksaan");
    err.status = res.status;
    throw err;
  }
  return data;
}

async function apiGetHistoryDetail(historyId) {
  const res = await fetch(`${API_BASE_URL}/history/${historyId}`, {
    headers: { ...authHeader() },
  });
  const data = await res.json();
  if (!res.ok) {
    const err = new Error(data.error || "Gagal mengambil detail riwayat");
    err.status = res.status;
    throw err;
  }
  return data;
}

async function apiDeleteHistory(historyId) {
  const res = await fetch(`${API_BASE_URL}/history/${historyId}`, {
    method: "DELETE",
    headers: { ...authHeader() },
  });
  const data = await res.json();
  if (!res.ok) {
    const err = new Error(data.error || "Gagal menghapus riwayat");
    err.status = res.status;
    throw err;
  }
  return data;
}
