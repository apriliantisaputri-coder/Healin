/**
 * Konfigurasi & helper untuk memanggil REST API Heal.In (Flask).
 * Ganti API_BASE_URL kalau backend dijalankan di alamat/port lain.
 */
const API_BASE_URL = "http://127.0.0.1:5000";

async function apiGetDaftarGejala() {
  const res = await fetch(`${API_BASE_URL}/api/gejala`);
  if (!res.ok) throw new Error("Gagal mengambil daftar gejala dari server");
  return res.json();
}

async function apiPostSkrining(daftarGejala, user) {
  // `user` (opsional) = { nama, email } dari sesi login saat ini
  // (lihat healinGetSession() di js/auth.js). Dikirim HANYA supaya
  // backend bisa mengaitkan hasil skrining ini dengan user_id yang
  // benar saat menyimpan riwayat pemeriksaan -- tidak mengubah
  // endpoint, tidak mengubah alur inferensi, dan sepenuhnya
  // backward-compatible (kalau tidak dikirim, backend cukup tidak
  // menyimpan riwayat, seperti sebelum perubahan ini).
  const payload = { gejala: daftarGejala };
  if (user && user.email) {
    payload.user_email = user.email;
    payload.user_nama = user.nama;
  }

  const res = await fetch(`${API_BASE_URL}/api/skrining`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error || "Terjadi kesalahan pada server");
  }
  return data;
}
