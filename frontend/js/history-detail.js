/* =========================================================
   HEAL.IN — DETAIL RIWAYAT PEMERIKSAAN
   Menampilkan satu riwayat (dari /history/<id>) beserta
   explanation trace Forward Chaining apa adanya -- tampilan
   saja yang diubah, logika trace TIDAK disentuh.
   ========================================================= */

const INDO_MONTHS = [
  "Januari", "Februari", "Maret", "April", "Mei", "Juni",
  "Juli", "Agustus", "September", "Oktober", "November", "Desember",
];

const BADGE_CLASS = {
  "Normal": "normal",
  "Stres Ringan": "ringan",
  "Stres Berat": "berat",
  "Kecemasan": "kecemasan",
  "Potensi Depresi": "depresi",
};

// Selaras dengan label checkbox pada questionnaire.html (rules/gejala_list.py).
const GEJALA_LABELS = {
  sulit_tidur: "Sulit tidur",
  mudah_lelah: "Mudah lelah",
  sakit_kepala: "Sakit kepala berulang",
  sulit_konsentrasi: "Sulit berkonsentrasi",
  mudah_lupa: "Mudah lupa",
  pikiran_negatif: "Pikiran negatif berulang",
  cemas_berlebihan: "Cemas berlebihan",
  mudah_marah: "Mudah marah",
  sedih_berkepanjangan: "Merasa sedih berkepanjangan",
  putus_asa: "Merasa putus asa",
  kehilangan_motivasi: "Kehilangan motivasi belajar",
  menarik_diri: "Menarik diri dari lingkungan sosial",
  penurunan_produktivitas: "Penurunan produktivitas",
};

function formatTanggalIndo(isoString) {
  const d = new Date(isoString);
  return `${d.getDate()} ${INDO_MONTHS[d.getMonth()]} ${d.getFullYear()}`;
}

const session = healinGetSession();

const loadingState = document.getElementById("loadingState");
const errorState = document.getElementById("errorState");
const detailState = document.getElementById("detailState");

function showError(title, message) {
  loadingState.classList.add("d-none");
  detailState.classList.add("d-none");
  errorState.classList.remove("d-none");
  document.getElementById("errorTitle").textContent = title;
  document.getElementById("errorMessage").textContent = message;
}

function render(data) {
  loadingState.classList.add("d-none");
  errorState.classList.add("d-none");
  detailState.classList.remove("d-none");

  const badgeClass = BADGE_CLASS[data.detected_condition] || "normal";
  const badge = document.getElementById("kondisiBadge");
  badge.textContent = data.detected_condition;
  badge.className = `riwayat-badge ${badgeClass}`;
  badge.style.fontSize = ".85rem";
  badge.style.padding = ".4rem 1rem";

  document.getElementById("kondisiTitle").textContent = `Hasil: ${data.detected_condition}`;

  document.getElementById("infoTanggal").textContent = formatTanggalIndo(data.examination_date);
  document.getElementById("infoNama").textContent = data.user_full_name;
  document.getElementById("infoKondisi").textContent = data.detected_condition;
  document.getElementById("infoTingkat").textContent = data.severity || "—";

  const gejalaList = document.getElementById("gejalaList");
  gejalaList.innerHTML = "";
  (data.selected_symptoms || []).forEach((kode) => {
    const li = document.createElement("li");
    li.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>
      <span>${GEJALA_LABELS[kode] || kode}</span>
    `;
    gejalaList.appendChild(li);
  });

  const timeline = document.getElementById("traceTimeline");
  timeline.innerHTML = "";
  const trace = data.explanation_trace || [];
  trace.forEach((jejak, idx) => {
    const li = document.createElement("li");
    const isLast = idx === trace.length - 1;
    if (isLast) li.classList.add("final");
    li.innerHTML = `
      <div class="rule-code">${jejak.kondisi} (skor ${jejak.skor})</div>
      <div class="rule-desc">${jejak.aturan}</div>
    `;
    timeline.appendChild(li);
  });
  if (trace.length > 0) {
    const kesimpulan = document.createElement("li");
    kesimpulan.classList.add("final");
    kesimpulan.innerHTML = `
      <div class="rule-code">Kesimpulan: ${data.detected_condition}</div>
    `;
    timeline.appendChild(kesimpulan);
  }

  const rekomendasiList = document.getElementById("rekomendasiList");
  rekomendasiList.innerHTML = "";
  (data.recommendation || []).forEach((saran) => {
    const li = document.createElement("li");
    li.textContent = saran;
    rekomendasiList.appendChild(li);
  });
}

async function init() {
  const params = new URLSearchParams(window.location.search);
  const id = params.get("id");

  if (!id) {
    showError("Riwayat tidak ditemukan.", "ID riwayat tidak diberikan pada URL.");
    return;
  }

  try {
    const data = await apiGetHistoryDetail(id);
    render(data);
  } catch (err) {
    if (err.status === 403) {
      showError("Akses ditolak.", "Anda tidak memiliki akses ke riwayat ini.");
    } else if (err.status === 404) {
      showError("Riwayat tidak ditemukan.", "Riwayat yang Anda cari mungkin sudah dihapus.");
    } else {
      showError("Gagal memuat riwayat.", err.message);
    }
  }
}

init();
