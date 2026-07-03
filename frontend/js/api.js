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

async function apiPostSkrining(daftarGejala) {
  const res = await fetch(`${API_BASE_URL}/api/skrining`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ gejala: daftarGejala }),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error || "Terjadi kesalahan pada server");
  }
  return data;
}
