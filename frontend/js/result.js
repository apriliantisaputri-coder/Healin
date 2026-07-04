/* =========================================================
   HEAL.IN — RESULT DASHBOARD (js/result.js)
   ADITIF: file baru, tidak mengubah js/api.js, js/auth.js,
   js/questionnaire.js. Membaca hasil skrining dari
   sessionStorage("healin_hasil") -- format yang sama persis
   yang sudah dikirim questionnaire.js sebelumnya, ditambah
   dua field baru yang bersifat opsional (durasi_detik,
   waktu_selesai) yang sudah ditambahkan secara aditif di
   questionnaire.js.
   ========================================================= */

/* ---------- 1. Katalog gejala (persis rules/gejala_list.py) ---------- */
const GEJALA_META = {
  sulit_tidur:            { label: "Sulit tidur atau tidur tidak nyenyak", kategori: "fisik" },
  mudah_lelah:            { label: "Sering merasa lelah tanpa alasan jelas", kategori: "fisik" },
  sakit_kepala:           { label: "Sering sakit kepala", kategori: "fisik" },
  sulit_konsentrasi:      { label: "Sulit berkonsentrasi saat belajar", kategori: "kognitif" },
  mudah_lupa:             { label: "Mudah lupa hal-hal kecil", kategori: "kognitif" },
  pikiran_negatif:        { label: "Sering muncul pikiran negatif", kategori: "kognitif" },
  cemas_berlebihan:       { label: "Merasa cemas atau khawatir berlebihan", kategori: "emosional" },
  mudah_marah:            { label: "Mudah marah atau tersinggung", kategori: "emosional" },
  sedih_berkepanjangan:   { label: "Merasa sedih berkepanjangan", kategori: "emosional" },
  putus_asa:              { label: "Merasa putus asa", kategori: "emosional" },
  kehilangan_motivasi:    { label: "Kehilangan motivasi/semangat", kategori: "perilaku" },
  menarik_diri:           { label: "Menarik diri dari lingkungan sosial", kategori: "perilaku" },
  penurunan_produktivitas:{ label: "Penurunan produktivitas dalam aktivitas", kategori: "perilaku" },
};
const TOTAL_GEJALA = Object.keys(GEJALA_META).length;

/* ---------- 2. Katalog 24 rule (persis rules/*.py) ---------- */
const RULE_CATALOG = [
  { id: "N01", kondisi: "Normal", skor: 5,  aturan: "IF mudah_lelah AND NOT sulit_tidur AND NOT cemas_berlebihan AND NOT sedih_berkepanjangan THEN Normal" },
  { id: "N02", kondisi: "Normal", skor: 5,  aturan: "IF sakit_kepala AND NOT sulit_konsentrasi AND NOT cemas_berlebihan THEN Normal" },
  { id: "N03", kondisi: "Normal", skor: 5,  aturan: "IF mudah_lupa AND NOT sulit_konsentrasi AND NOT pikiran_negatif THEN Normal" },

  { id: "R01", kondisi: "Stres Ringan", skor: 20, aturan: "IF sulit_tidur AND cemas_berlebihan AND sulit_konsentrasi THEN Stres Ringan" },
  { id: "R02", kondisi: "Stres Ringan", skor: 18, aturan: "IF sulit_tidur AND mudah_lelah THEN Stres Ringan" },
  { id: "R03", kondisi: "Stres Ringan", skor: 18, aturan: "IF sakit_kepala AND sulit_konsentrasi THEN Stres Ringan" },
  { id: "R04", kondisi: "Stres Ringan", skor: 18, aturan: "IF mudah_lelah AND penurunan_produktivitas THEN Stres Ringan" },
  { id: "R05", kondisi: "Stres Ringan", skor: 18, aturan: "IF sulit_konsentrasi AND mudah_lupa THEN Stres Ringan" },

  { id: "B01", kondisi: "Stres Berat", skor: 40, aturan: "IF sulit_tidur AND cemas_berlebihan AND sulit_konsentrasi AND kehilangan_motivasi THEN Stres Berat" },
  { id: "B02", kondisi: "Stres Berat", skor: 38, aturan: "IF mudah_lelah AND sakit_kepala AND sulit_konsentrasi AND mudah_marah THEN Stres Berat" },
  { id: "B03", kondisi: "Stres Berat", skor: 36, aturan: "IF sulit_tidur AND mudah_marah AND penurunan_produktivitas THEN Stres Berat" },
  { id: "B04", kondisi: "Stres Berat", skor: 38, aturan: "IF pikiran_negatif AND sulit_konsentrasi AND mudah_lelah AND sulit_tidur THEN Stres Berat" },
  { id: "B05", kondisi: "Stres Berat", skor: 40, aturan: "IF cemas_berlebihan AND mudah_marah AND sulit_tidur AND penurunan_produktivitas THEN Stres Berat" },

  { id: "K01", kondisi: "Kecemasan", skor: 30, aturan: "IF cemas_berlebihan AND sulit_tidur AND mudah_marah THEN Kecemasan" },
  { id: "K02", kondisi: "Kecemasan", skor: 26, aturan: "IF cemas_berlebihan AND sakit_kepala THEN Kecemasan" },
  { id: "K03", kondisi: "Kecemasan", skor: 28, aturan: "IF cemas_berlebihan AND pikiran_negatif THEN Kecemasan" },
  { id: "K04", kondisi: "Kecemasan", skor: 28, aturan: "IF cemas_berlebihan AND menarik_diri THEN Kecemasan" },
  { id: "K05", kondisi: "Kecemasan", skor: 30, aturan: "IF cemas_berlebihan AND mudah_lupa AND sulit_konsentrasi THEN Kecemasan" },

  { id: "D01", kondisi: "Potensi Depresi", skor: 48, aturan: "IF sedih_berkepanjangan AND kehilangan_motivasi THEN Potensi Depresi" },
  { id: "D02", kondisi: "Potensi Depresi", skor: 50, aturan: "IF putus_asa AND kehilangan_motivasi AND menarik_diri THEN Potensi Depresi" },
  { id: "D03", kondisi: "Potensi Depresi", skor: 46, aturan: "IF sedih_berkepanjangan AND menarik_diri THEN Potensi Depresi" },
  { id: "D04", kondisi: "Potensi Depresi", skor: 46, aturan: "IF putus_asa AND penurunan_produktivitas THEN Potensi Depresi" },
  { id: "D05", kondisi: "Potensi Depresi", skor: 50, aturan: "IF sedih_berkepanjangan AND pikiran_negatif AND kehilangan_motivasi THEN Potensi Depresi" },
  { id: "D06", kondisi: "Potensi Depresi", skor: 50, aturan: "IF putus_asa AND sedih_berkepanjangan THEN Potensi Depresi" },
];
const MAX_SKOR_GLOBAL = Math.max(...RULE_CATALOG.map((r) => r.skor)); // 50

/* ---------- 3. Metadata tiap kondisi (warna & risiko) ---------- */
const KONDISI_META = {
  "Normal": {
    tingkatClass: "tingkat-normal", risiko: "Rendah", textColor: "#355F2E", barColor: "#355F2E",
    ringkasan: "Berdasarkan gejala yang Anda pilih, sistem tidak mendeteksi indikasi stres, kecemasan, maupun depresi yang signifikan. Pertahankan pola hidup sehat dan tetap rutin memantau kondisi mental Anda.",
  },
  "Stres Ringan": {
    tingkatClass: "tingkat-ringan", risiko: "Rendah - Sedang", textColor: "#8a6d1c", barColor: "#c9a227",
    ringkasan: "Berdasarkan gejala yang Anda pilih, sistem mendeteksi bahwa tingkat stres Anda berada pada kategori ringan. Kondisi ini masih dapat dikelola melalui pola hidup sehat, manajemen waktu, dan aktivitas relaksasi.",
  },
  "Kecemasan": {
    tingkatClass: "tingkat-cemas", risiko: "Sedang", textColor: "#5f3aa3", barColor: "#5f3aa3",
    ringkasan: "Sistem mendeteksi pola gejala yang mengarah pada kecemasan, ditandai dengan rasa cemas berlebihan yang disertai gejala penyerta lain. Latihan relaksasi dan pengelolaan pemicu kecemasan disarankan.",
  },
  "Stres Berat": {
    tingkatClass: "tingkat-berat", risiko: "Tinggi", textColor: "#a35318", barColor: "#a35318",
    ringkasan: "Sistem mendeteksi kombinasi beberapa gejala lintas kategori (fisik, kognitif, emosional, perilaku) yang muncul bersamaan, mengindikasikan tingkat stres yang cukup berat. Mengurangi beban aktivitas dan mempertimbangkan konsultasi disarankan.",
  },
  "Potensi Depresi": {
    tingkatClass: "tingkat-depresi", risiko: "Tinggi", textColor: "#a33333", barColor: "#a33333",
    ringkasan: "Sistem mendeteksi pola gejala emosional dan perilaku yang mengarah pada potensi depresi. Kondisi ini perlu mendapat perhatian lebih serius -- konsultasi dengan psikolog atau tenaga profesional sangat disarankan.",
  },
};
const KONDISI_SEVERITY_SCORE = { "Normal": 10, "Stres Ringan": 35, "Kecemasan": 55, "Stres Berat": 75, "Potensi Depresi": 90 };

/* ---------- 4. Kontribusi tiap gejala ke 5 dimensi radar ---------- */
const DIMENSI_LABELS = ["Stress", "Kecemasan", "Depresi", "Kualitas Tidur", "Mood"];
const DIMENSI_KEYS = ["stress", "kecemasan", "depresi", "tidur", "mood"];
const DIMENSI_ICON = { stress: "🧠", kecemasan: "😰", depresi: "😔", tidur: "🌙", mood: "😊" };
const GEJALA_DIMENSI_WEIGHT = {
  sulit_tidur:             { stress: 15, tidur: 45, mood: 5 },
  mudah_lelah:             { stress: 15, tidur: 12, mood: 5 },
  sakit_kepala:            { stress: 15 },
  sulit_konsentrasi:       { stress: 18, kecemasan: 5 },
  mudah_lupa:              { stress: 10 },
  pikiran_negatif:         { stress: 10, kecemasan: 15, depresi: 15, mood: 10 },
  cemas_berlebihan:        { kecemasan: 40, stress: 10, mood: 5 },
  mudah_marah:             { kecemasan: 12, mood: 15, stress: 5 },
  sedih_berkepanjangan:    { depresi: 40, mood: 25 },
  putus_asa:               { depresi: 35, mood: 20 },
  kehilangan_motivasi:     { depresi: 15, mood: 15, stress: 5 },
  menarik_diri:            { depresi: 20, mood: 10, kecemasan: 5 },
  penurunan_produktivitas: { stress: 15, mood: 5 },
};
/* Garis referensi ilustratif (bukan data agregat sungguhan -- ditandai jelas di UI) */
const REF_MAHASISWA = { stress: 50, kecemasan: 45, depresi: 35, tidur: 48, mood: 52 };
const REF_NASIONAL  = { stress: 42, kecemasan: 38, depresi: 30, tidur: 40, mood: 45 };

/* ---------- Util ---------- */
function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

function severityBand(v) {
  if (v < 34) return { label: "Ringan", bg: "#DCEBD9", fg: "var(--primary)" };
  if (v < 67) return { label: "Sedang", bg: "#F3EBC8", fg: "#8a6d1c" };
  return { label: "Tinggi", bg: "#F4DCC8", fg: "#a35318" };
}

function formatTanggalIndo(date) {
  const bulan = ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"];
  const jam = String(date.getHours()).padStart(2, "0");
  const menit = String(date.getMinutes()).padStart(2, "0");
  return `${date.getDate()} ${bulan[date.getMonth()]} ${date.getFullYear()}, ${jam}:${menit} WIB`;
}

function formatDurasi(detik) {
  if (!detik || detik <= 0) return "—";
  const m = Math.floor(detik / 60);
  const s = detik % 60;
  return m > 0 ? `${m} menit ${s} detik` : `${s} detik`;
}

function showToast(msg) {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2600);
}

/* ---------- Hitung skor 5 dimensi dari gejala yang dipilih ---------- */
function hitungDimensi(gejalaDipilih) {
  const totals = { stress: 0, kecemasan: 0, depresi: 0, tidur: 0, mood: 0 };
  gejalaDipilih.forEach((g) => {
    const w = GEJALA_DIMENSI_WEIGHT[g];
    if (!w) return;
    Object.keys(w).forEach((dim) => { totals[dim] += w[dim]; });
  });
  Object.keys(totals).forEach((k) => { totals[k] = clamp(Math.round(totals[k]), 0, 100); });
  return totals;
}

/* ---------- Confidence: gabungan rasio rule terpenuhi & skor relatif ---------- */
function hitungConfidence(hasil) {
  const rulesForKondisi = RULE_CATALOG.filter((r) => r.kondisi === hasil.kondisi);
  const rulesFired = (hasil.explanation_trace || []).filter((t) => t.kondisi === hasil.kondisi).length;
  const ruleRatio = rulesForKondisi.length ? rulesFired / rulesForKondisi.length : 0;
  const maxSkorKondisi = rulesForKondisi.length ? Math.max(...rulesForKondisi.map((r) => r.skor)) : MAX_SKOR_GLOBAL;
  const skorRatio = maxSkorKondisi ? hasil.skor / maxSkorKondisi : 0;
  const conf = Math.round(100 * (0.5 * ruleRatio + 0.5 * skorRatio));
  return clamp(conf, 30, 98);
}

/* ---------- Parse "IF a AND b AND c THEN X" -> {ifPart, thenPart} ---------- */
function parseAturan(aturan) {
  const idx = aturan.indexOf(" THEN ");
  const ifPartRaw = idx >= 0 ? aturan.slice(3, idx) : aturan; // drop leading "IF "
  const thenPart = idx >= 0 ? aturan.slice(idx + 6) : "";
  const kondisiParts = ifPartRaw.split(/\s+AND\s+|\s+OR\s+/).map((s) => s.trim().replace(/^NOT\s+/, "TIDAK ")).filter(Boolean);
  return { kondisiParts, thenPart };
}

/* =========================================================
   MAIN RENDER
   ========================================================= */
function render() {
  const raw = sessionStorage.getItem("healin_hasil");
  document.getElementById("loadingState").classList.add("d-none");

  if (!raw) {
    document.getElementById("emptyState").classList.remove("d-none");
    return;
  }

  let hasil;
  try {
    hasil = JSON.parse(raw);
  } catch {
    document.getElementById("emptyState").classList.remove("d-none");
    return;
  }

  document.getElementById("resultState").classList.remove("d-none");

  const meta = KONDISI_META[hasil.kondisi] || KONDISI_META["Normal"];
  const gejalaDipilih = hasil.gejala_dipilih || [];
  const confidence = hitungConfidence(hasil);
  const skorPercent = clamp(Math.round((hasil.skor / MAX_SKOR_GLOBAL) * 100), 0, 100);
  const dims = hitungDimensi(gejalaDipilih);

  renderRingkasan(hasil, meta, confidence, skorPercent, gejalaDipilih);
  renderRadar(dims, gejalaDipilih);
  renderGejala(gejalaDipilih);
  renderTimeline(hasil, confidence);
  renderRekomendasi(hasil);
  renderAnalisisAI(hasil, dims, gejalaDipilih);
  renderFactorBars(dims);
  renderGauge(confidence);
  renderComparison(hasil);
  setupModal(hasil);
  setupActions(hasil);
}

/* ---------- CARD 1 ---------- */
function renderRingkasan(hasil, meta, confidence, skorPercent, gejalaDipilih) {
  const kv = document.getElementById("kondisiValue");
  kv.textContent = hasil.kondisi;
  kv.style.color = meta.textColor;

  const badge = document.getElementById("riskBadge");
  badge.textContent = `Tingkat Risiko: ${meta.risiko}`;
  badge.className = `hd-risk-badge detect-tag ${meta.tingkatClass}`;

  document.getElementById("summaryText").textContent = meta.ringkasan;

  document.getElementById("scoreValue").innerHTML = `${skorPercent}<span>/100</span>`;
  const scoreBar = document.getElementById("scoreBar");
  scoreBar.style.background = meta.barColor;
  requestAnimationFrame(() => { scoreBar.style.width = skorPercent + "%"; });

  document.getElementById("confValue").innerHTML = `${confidence}<span>%</span>`;
  requestAnimationFrame(() => { document.getElementById("confBar").style.width = confidence + "%"; });

  const tanggal = hasil.waktu_selesai ? new Date(hasil.waktu_selesai) : new Date();
  document.getElementById("statTanggal").textContent = formatTanggalIndo(tanggal);
  document.getElementById("statDurasi").textContent = formatDurasi(hasil.durasi_detik);
  document.getElementById("statJumlah").textContent = `${gejalaDipilih.length} dari ${TOTAL_GEJALA} gejala`;
}

/* ---------- CARD 2: Radar (SVG buatan sendiri) ---------- */
let radarState = { user: true, mahasiswa: true, nasional: true };

function polar(cx, cy, r, angleDeg) {
  const rad = ((angleDeg - 90) * Math.PI) / 180;
  return [cx + r * Math.cos(rad), cy + r * Math.sin(rad)];
}

function buildPolygonPoints(values, cx, cy, maxR) {
  const n = values.length;
  return values.map((v, i) => {
    const r = (clamp(v, 0, 100) / 100) * maxR;
    const [x, y] = polar(cx, cy, r, (360 / n) * i);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
}

function renderRadar(dims, gejalaDipilih) {
  const cx = 175, cy = 170, maxR = 130;
  const n = DIMENSI_LABELS.length;
  const values = DIMENSI_KEYS.map((k) => dims[k]);

  let rings = "";
  [0.25, 0.5, 0.75, 1].forEach((f) => {
    const pts = DIMENSI_LABELS.map((_, i) => polar(cx, cy, maxR * f, (360 / n) * i).join(",")).join(" ");
    rings += `<polygon points="${pts}" fill="none" stroke="#E5E7EB" stroke-width="1"/>`;
  });

  let axes = "";
  let labels = "";
  DIMENSI_LABELS.forEach((label, i) => {
    const [x2, y2] = polar(cx, cy, maxR, (360 / n) * i);
    axes += `<line x1="${cx}" y1="${cy}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}" stroke="#E5E7EB" stroke-width="1"/>`;
    const [lx, ly] = polar(cx, cy, maxR + 22, (360 / n) * i);
    labels += `<text x="${lx.toFixed(1)}" y="${ly.toFixed(1)}" font-size="11.5" font-weight="600" fill="var(--text-dark)" text-anchor="middle" dominant-baseline="middle">${label}</text>`;
  });

  const userPts = buildPolygonPoints(values, cx, cy, maxR);
  const mhsPts = buildPolygonPoints(DIMENSI_KEYS.map((k) => REF_MAHASISWA[k]), cx, cy, maxR);
  const nasPts = buildPolygonPoints(DIMENSI_KEYS.map((k) => REF_NASIONAL[k]), cx, cy, maxR);

  let pointDots = "";
  DIMENSI_KEYS.forEach((k, i) => {
    const v = dims[k];
    const r = (clamp(v, 0, 100) / 100) * maxR;
    const [x, y] = polar(cx, cy, r, (360 / n) * i);
    pointDots += `<circle class="hd-radar-point" data-dim="${k}" data-idx="${i}" cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="5" fill="var(--primary)" stroke="#fff" stroke-width="2"/>`;
  });

  const svg = `
    <svg viewBox="0 0 350 340" xmlns="http://www.w3.org/2000/svg">
      ${rings}${axes}
      <polygon id="radarNasional" points="${nasPts}" fill="none" stroke="#94A3B8" stroke-width="1.5" stroke-dasharray="4 3"/>
      <polygon id="radarMahasiswa" points="${mhsPts}" fill="none" stroke="#94A3B8" stroke-width="1.5" stroke-dasharray="2 2" opacity="0.7"/>
      <polygon id="radarUser" points="${userPts}" fill="#16A34A" fill-opacity="0.18" stroke="var(--primary)" stroke-width="2.4"/>
      ${pointDots}
      ${labels}
    </svg>`;
  document.getElementById("radarWrap").innerHTML = svg;

  // Tooltip
  const tooltip = document.getElementById("radarTooltip");
  const wrap = document.querySelector(".hd-radar-svg-wrap");
  document.querySelectorAll(".hd-radar-point").forEach((dot) => {
    dot.addEventListener("mouseenter", (e) => {
      const dim = dot.dataset.dim;
      const v = dims[dim];
      const band = severityBand(v);
      tooltip.innerHTML = `<b>${DIMENSI_LABELS[DIMENSI_KEYS.indexOf(dim)]}</b><br>Nilai: ${v}/100<br>Kategori: ${band.label}<br>${dimensiPenjelasan(dim)}`;
      tooltip.classList.add("show");
    });
    dot.addEventListener("mousemove", (e) => {
      const rect = wrap.getBoundingClientRect();
      tooltip.style.left = (e.clientX - rect.left + 14) + "px";
      tooltip.style.top = (e.clientY - rect.top - 10) + "px";
    });
    dot.addEventListener("mouseleave", () => tooltip.classList.remove("show"));
  });

  // Legend toggle
  const legend = document.getElementById("radarLegend");
  legend.innerHTML = `
    <button data-key="user"><span class="dot" style="background:var(--primary);"></span>Skor Anda</button>
    <button data-key="mahasiswa"><span class="dot" style="background:#94A3B8;"></span>Rata-rata Mahasiswa</button>
    <button data-key="nasional"><span class="dot" style="background:#94A3B8; opacity:.6;"></span>Rata-rata Nasional</button>
  `;
  legend.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", () => {
      const key = btn.dataset.key;
      radarState[key] = !radarState[key];
      btn.classList.toggle("off", !radarState[key]);
      const svgId = key === "user" ? "radarUser" : key === "mahasiswa" ? "radarMahasiswa" : "radarNasional";
      const el = document.getElementById(svgId);
      if (el) el.style.display = radarState[key] ? "" : "none";
    });
  });

  // Mini score cards
  const miniWrap = document.getElementById("miniScores");
  miniWrap.innerHTML = DIMENSI_KEYS.map((k, i) => {
    const v = dims[k];
    const band = severityBand(v);
    return `
      <div class="hd-mini-score">
        <div class="emoji">${DIMENSI_ICON[k]}</div>
        <div class="body">
          <div class="top-row"><span>${DIMENSI_LABELS[i]}</span><span>${v}/100</span></div>
          <div class="hd-mini-bar"><span style="background:${band.fg};" data-w="${v}"></span></div>
        </div>
        <span class="cat" style="background:${band.bg}; color:${band.fg};">${band.label}</span>
      </div>`;
  }).join("");
  requestAnimationFrame(() => {
    miniWrap.querySelectorAll(".hd-mini-bar > span").forEach((el) => { el.style.width = el.dataset.w + "%"; });
  });

  // Insight otomatis
  const maxKey = DIMENSI_KEYS.reduce((a, b) => (dims[a] >= dims[b] ? a : b));
  const maxIdx = DIMENSI_KEYS.indexOf(maxKey);
  let insight = `${DIMENSI_LABELS[maxIdx]} menjadi aspek dengan skor tertinggi dibanding dimensi lainnya (${dims[maxKey]}/100).`;
  if (dims.tidur >= 45 && maxKey !== "tidur") {
    insight += " Kualitas tidur juga mulai menunjukkan penurunan sehingga disarankan memperbaiki pola istirahat.";
  }
  document.getElementById("radarInsight").textContent = insight;
}

function dimensiPenjelasan(dim) {
  const map = {
    stress: "Tingkat tekanan dari beban akademik/aktivitas sehari-hari.",
    kecemasan: "Kadar rasa cemas atau khawatir berlebihan.",
    depresi: "Indikasi kesedihan berkepanjangan atau kehilangan motivasi.",
    tidur: "Seberapa terganggu kualitas tidur Anda.",
    mood: "Fluktuasi suasana hati secara umum.",
  };
  return map[dim] || "";
}

/* ---------- CARD 4: Gejala checklist ---------- */
function renderGejala(gejalaDipilih) {
  const grid = document.getElementById("gejalaGrid");
  const checkSvg = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>`;
  grid.innerHTML = gejalaDipilih.map((g) => {
    const label = (GEJALA_META[g] && GEJALA_META[g].label) || g;
    return `<div class="hd-gejala-item">${checkSvg}<span>${label}</span></div>`;
  }).join("") || `<p class="text-muted">Tidak ada gejala tercatat.</p>`;
  document.getElementById("gejalaTotal").textContent = `${gejalaDipilih.length} dari ${TOTAL_GEJALA} gejala`;
}

/* ---------- CARD 3: Explanation Trace timeline ---------- */
function renderTimeline(hasil, confidence) {
  const timeline = document.getElementById("timeline");
  const trace = hasil.explanation_trace || [];
  const rulesForKondisi = RULE_CATALOG.filter((r) => r.kondisi === hasil.kondisi).length;
  const rulesFired = trace.filter((t) => t.kondisi === hasil.kondisi).length;

  let html = `
    <div class="hd-tnode" style="animation-delay:0s;">
      <div class="hd-tnode-dot start">▶</div>
      <div class="hd-tnode-card">
        <div class="row1"><span class="ttl">Mulai Analisis</span></div>
        <div class="desc">Sistem mulai memproses ${(hasil.gejala_dipilih || []).length} gejala yang Anda pilih.</div>
      </div>
    </div>`;

  trace.forEach((t, i) => {
    const rule = RULE_CATALOG.find((r) => r.aturan === t.aturan);
    const parsed = parseAturan(t.aturan);
    const ruleId = rule ? rule.id : `T${i + 1}`;
    html += `
      <div class="hd-tnode" style="animation-delay:${(i + 1) * 0.12}s;">
        <div class="hd-tnode-dot ok">✓</div>
        <div class="hd-tnode-card" data-idx="${i}">
          <div class="row1">
            <span class="ttl">Rule ${ruleId} Aktif</span>
            <span class="hd-chevron">▾</span>
          </div>
          <div class="desc">${parsed.kondisiParts.join(" DAN ")} → ${parsed.thenPart}</div>
          <div class="hd-tnode-detail">
            <div class="kv"><span class="k">Status</span><span>✓ Terpenuhi</span></div>
            <div class="kv"><span class="k">Skor</span><span>${t.skor}</span></div>
            <div class="kv"><span class="k">Evidence</span><span>${parsed.kondisiParts.length} kondisi cocok</span></div>
            <div class="kv"><span class="k">Aturan</span><code>${t.aturan}</code></div>
          </div>
        </div>
      </div>`;
  });

  html += `
    <div class="hd-tnode" style="animation-delay:${(trace.length + 1) * 0.12}s;">
      <div class="hd-tnode-dot final">★</div>
      <div class="hd-tnode-card">
        <div class="row1"><span class="ttl">Diagnosis &amp; Confidence</span></div>
        <div class="desc"><strong>${hasil.kondisi}</strong> — tingkat keyakinan ${confidence}%. Rekomendasi tindak lanjut telah dibuat.</div>
      </div>
    </div>`;

  timeline.innerHTML = html;

  timeline.querySelectorAll(".hd-tnode-card[data-idx]").forEach((card) => {
    card.addEventListener("click", () => {
      card.classList.toggle("expanded");
      card.querySelector(".hd-tnode-detail").classList.toggle("open");
    });
  });

  document.getElementById("finalKondisi").textContent = hasil.kondisi;
  document.getElementById("statConfidence").textContent = confidence + "%";
  document.getElementById("statRuleAktif").textContent = rulesFired;
  document.getElementById("statRuleDiperiksa").textContent = RULE_CATALOG.length;
  document.getElementById("statRuleGagal").textContent = RULE_CATALOG.length - trace.length;
}

/* ---------- CARD 6: Rekomendasi ---------- */
function pilihIkon(text) {
  const t = text.toLowerCase();
  if (t.includes("tidur")) return "🛌";
  if (t.includes("relaksasi") || t.includes("napas") || t.includes("pernapasan") || t.includes("meditasi")) return "🧘";
  if (t.includes("olahraga")) return "🏃";
  if (t.includes("tugas") || t.includes("prioritas") || t.includes("waktu") || t.includes("to-do")) return "📅";
  if (t.includes("konsultasi") || t.includes("psikolog") || t.includes("konselor") || t.includes("profesional") || t.includes("medis")) return "💬";
  return "✅";
}
function judulRekom(text) {
  const t = text.toLowerCase();
  if (t.includes("tidur")) return "Tidur Berkualitas";
  if (t.includes("relaksasi") || t.includes("napas") || t.includes("pernapasan") || t.includes("meditasi")) return "Teknik Relaksasi";
  if (t.includes("olahraga")) return "Olahraga Ringan";
  if (t.includes("tugas") || t.includes("prioritas") || t.includes("waktu") || t.includes("to-do")) return "Manajemen Tugas";
  if (t.includes("konsultasi") || t.includes("psikolog") || t.includes("konselor") || t.includes("profesional") || t.includes("medis")) return "Konsultasi Profesional";
  return "Langkah Mandiri";
}
function estimasiWaktu(text) {
  const t = text.toLowerCase();
  if (t.includes("tidur")) return "Setiap malam";
  if (t.includes("relaksasi") || t.includes("napas") || t.includes("pernapasan") || t.includes("meditasi")) return "10 menit/hari";
  if (t.includes("olahraga")) return "3x seminggu";
  if (t.includes("tugas") || t.includes("prioritas") || t.includes("waktu") || t.includes("to-do")) return "Harian";
  if (t.includes("konsultasi") || t.includes("psikolog") || t.includes("konselor") || t.includes("profesional") || t.includes("medis")) return "Sesegera mungkin";
  return "Fleksibel";
}

function renderRekomendasi(hasil) {
  const grid = document.getElementById("rekomGrid");
  const list = hasil.rekomendasi || [];
  grid.innerHTML = list.map((text, i) => {
    const isUrgent = /konsultasi|psikolog|konselor|profesional|medis/i.test(text);
    const prioritas = isUrgent || i === 0 ? "tinggi" : "sedang";
    return `
      <div class="hd-rekom-card">
        <span class="hd-ai-pill">Recommended by AI</span>
        <span class="emoji">${pilihIkon(text)}</span>
        <h4>${judulRekom(text)}</h4>
        <p>${text}</p>
        <div class="hd-rekom-meta">
          <span class="hd-priority ${prioritas}">Prioritas ${prioritas === "tinggi" ? "Tinggi" : "Sedang"}</span>
          <span class="hd-time-pill">${estimasiWaktu(text)}</span>
        </div>
      </div>`;
  }).join("");
}

/* ---------- CARD 5: Analisis AI ---------- */
function renderAnalisisAI(hasil, dims, gejalaDipilih) {
  const kategoriCount = { fisik: 0, kognitif: 0, emosional: 0, perilaku: 0 };
  gejalaDipilih.forEach((g) => {
    const kat = GEJALA_META[g] && GEJALA_META[g].kategori;
    if (kat) kategoriCount[kat] += 1;
  });
  const dominanKategori = Object.keys(kategoriCount).reduce((a, b) => (kategoriCount[a] >= kategoriCount[b] ? a : b));
  const maxDim = DIMENSI_KEYS.reduce((a, b) => (dims[a] >= dims[b] ? a : b));
  const maxDimIdx = DIMENSI_KEYS.indexOf(maxDim);

  const kategoriLabel = { fisik: "fisik", kognitif: "kognitif", emosional: "emosional", perilaku: "perilaku" };

  const narasi = `Berdasarkan pola jawaban, gejala yang paling dominan berada pada dimensi ${kategoriLabel[dominanKategori]}, ` +
    `dengan skor tertinggi pada aspek ${DIMENSI_LABELS[maxDimIdx].toLowerCase()} (${dims[maxDim]}/100). ` +
    `Kondisi ini terdeteksi sebagai <strong>${hasil.kondisi}</strong> dengan ${gejalaDipilih.length} dari ${TOTAL_GEJALA} gejala yang cocok. ` +
    `Apabila kondisi ini berlangsung dalam waktu lama tanpa penanganan, sistem menyarankan langkah pencegahan sejak dini.`;
  document.getElementById("aiNarasi").innerHTML = narasi;

  document.getElementById("aiFaktorDominan").textContent = DIMENSI_LABELS[maxDimIdx];

  const prioritasMap = {
    "Normal": "Pertahankan pola hidup sehat",
    "Stres Ringan": "Manajemen waktu & tidur",
    "Kecemasan": "Latihan relaksasi rutin",
    "Stres Berat": "Kurangi beban & pertimbangkan konsultasi",
    "Potensi Depresi": "Konsultasi profesional segera",
  };
  document.getElementById("aiPrioritas").textContent = prioritasMap[hasil.kondisi] || "Pantau kondisi secara berkala";

  // Trend diisi ulang oleh renderComparison() setelah data riwayat didapat.
  document.getElementById("aiTrend").textContent = "Menganalisis…";
}

/* ---------- CARD 8: Faktor bar chart ---------- */
function renderFactorBars(dims) {
  const arr = DIMENSI_KEYS.map((k, i) => ({ key: k, label: DIMENSI_LABELS[i], val: dims[k] }))
    .sort((a, b) => b.val - a.val);
  const total = arr.reduce((s, d) => s + d.val, 0) || 1;
  const wrap = document.getElementById("factorBars");
  wrap.innerHTML = arr.map((d) => {
    const pct = Math.round((d.val / total) * 100);
    const band = severityBand(d.val);
    return `
      <div class="hd-bar-row">
        <span class="lbl">${d.label}</span>
        <div class="track"><span data-w="${pct}" style="background:${band.fg};"></span></div>
        <span class="pct">${pct}%</span>
      </div>`;
  }).join("");
  requestAnimationFrame(() => {
    wrap.querySelectorAll(".track > span").forEach((el) => { el.style.width = el.dataset.w + "%"; });
  });
}

/* ---------- CARD 9: Gauge ---------- */
function renderGauge(confidence) {
  const r = 80, cx = 100, cy = 100;
  const circumference = Math.PI * r; // setengah lingkaran
  const offset = circumference * (1 - confidence / 100);
  const svg = `
    <svg viewBox="0 0 200 115" width="220">
      <path d="M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}" fill="none" stroke="#E5E7EB" stroke-width="16" stroke-linecap="round"/>
      <path id="gaugeArc" d="M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}" fill="none" stroke="var(--primary)" stroke-width="16" stroke-linecap="round"
        stroke-dasharray="${circumference}" stroke-dashoffset="${circumference}" style="transition: stroke-dashoffset 1.2s cubic-bezier(.2,.8,.2,1);"/>
    </svg>`;
  document.getElementById("gaugeSvgWrap").innerHTML = svg;
  requestAnimationFrame(() => {
    setTimeout(() => { document.getElementById("gaugeArc").setAttribute("stroke-dashoffset", offset); }, 60);
  });

  document.getElementById("gaugeNum").textContent = confidence + "%";
  const label = confidence >= 80 ? "Sangat Yakin" : confidence >= 55 ? "Cukup Yakin" : "Perlu Data Tambahan";
  document.getElementById("gaugeLbl").textContent = label;
  document.getElementById("gaugeDesc").textContent =
    confidence >= 80
      ? "Sistem memperoleh keyakinan tinggi karena sebagian besar rule utama berhasil dipenuhi."
      : "Sebagian rule terpenuhi -- pertimbangkan mengisi skrining lagi jika gejala berubah untuk hasil yang lebih akurat.";
}

/* ---------- CARD 7: Perbandingan riwayat ---------- */
async function renderComparison(hasil) {
  const body = document.getElementById("comparisonBody");
  const session = healinGetSession();
  if (!session || !session.email) {
    body.innerHTML = `<div class="hd-empty-note">Masuk untuk melihat perbandingan dengan skrining sebelumnya.</div>`;
    return;
  }
  try {
    const res = await apiGetHistoryList(session.email, { page: 1, perPage: 8 });
    const items = (res.data || []).slice().reverse(); // lama -> baru
    if (items.length <= 1) {
      body.innerHTML = `<div class="hd-empty-note">Ini adalah skrining pertama Anda. Belum ada riwayat sebelumnya untuk dibandingkan.</div>`;
      document.getElementById("aiTrend").textContent = "Data pertama";
      return;
    }

    const values = items.map((it) => KONDISI_SEVERITY_SCORE[it.detected_condition] ?? 30);
    const w = 460, h = 150, pad = 30;
    const stepX = (w - pad * 2) / (values.length - 1);
    const maxV = 100;
    const pts = values.map((v, i) => {
      const x = pad + stepX * i;
      const y = h - pad - (v / maxV) * (h - pad * 1.6);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    });
    const lastVal = values[values.length - 1];
    const prevVal = values[values.length - 2];
    let trend = "stabil", trendLabel = "Stabil";
    if (lastVal > prevVal + 3) { trend = "naik"; trendLabel = "Naik"; }
    else if (lastVal < prevVal - 3) { trend = "turun"; trendLabel = "Turun"; }

    const dots = pts.map((p, i) => {
      const [x, y] = p.split(",");
      return `<circle cx="${x}" cy="${y}" r="4" fill="var(--primary)"/>`;
    }).join("");

    const svg = `
      <svg viewBox="0 0 ${w} ${h}" width="100%" height="150">
        <polyline points="${pts.join(" ")}" fill="none" stroke="var(--primary)" stroke-width="2.4"/>
        ${dots}
      </svg>`;

    body.innerHTML = `
      <div class="d-flex align-items-center justify-content-between mb-2">
        <span class="text-muted small">Skor stres (skala 0-100), ${items.length} skrining terakhir</span>
        <span class="hd-trend-chip ${trend}">${trendLabel}</span>
      </div>
      ${svg}`;

    document.getElementById("aiTrend").textContent = trendLabel;
  } catch (err) {
    body.innerHTML = `<div class="hd-empty-note">Belum ada riwayat yang dapat dibandingkan.</div>`;
    document.getElementById("aiTrend").textContent = "Data pertama";
  }
}

/* ---------- Modal: Lihat Semua Rule ---------- */
function setupModal(hasil) {
  const overlay = document.getElementById("ruleModalOverlay");
  const body = document.getElementById("ruleModalBody");
  const firedSet = new Set((hasil.explanation_trace || []).map((t) => t.aturan));
  let activeFilter = "semua";

  function draw() {
    let rules = RULE_CATALOG;
    if (activeFilter === "terpenuhi") rules = rules.filter((r) => firedSet.has(r.aturan));
    else if (activeFilter === "tidak") rules = rules.filter((r) => !firedSet.has(r.aturan));
    else if (activeFilter === "diagnosis") rules = rules.filter((r) => r.kondisi === hasil.kondisi);

    body.innerHTML = rules.map((r) => {
      const ok = firedSet.has(r.aturan);
      return `
        <div class="hd-mrule">
          <div class="head">
            <span class="id">${r.id} · ${r.kondisi}</span>
            <span class="status ${ok ? "yes" : "no"}">${ok ? "✓ Terpenuhi" : "Tidak terpenuhi"}</span>
          </div>
          <div class="txt">${r.aturan} <em>(skor ${r.skor})</em></div>
        </div>`;
    }).join("") || `<p class="text-muted">Tidak ada rule pada filter ini.</p>`;
  }

  document.getElementById("btnLihatSemuaRule").addEventListener("click", () => {
    overlay.classList.remove("d-none");
    draw();
  });
  document.getElementById("ruleModalClose").addEventListener("click", () => overlay.classList.add("d-none"));
  overlay.addEventListener("click", (e) => { if (e.target === overlay) overlay.classList.add("d-none"); });

  document.getElementById("ruleFilters").querySelectorAll(".hd-mfilter").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".hd-mfilter").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      activeFilter = btn.dataset.filter;
      draw();
    });
  });
}

/* ---------- Tombol aksi (simpan / unduh) ---------- */
function setupActions(hasil) {
  const session = healinGetSession();

  function saveHandler() {
    if (session && session.email) {
      showToast("Hasil skrining ini sudah tersimpan otomatis ke riwayat akun Anda.");
    } else {
      showToast("Masuk terlebih dahulu agar hasil dapat tersimpan ke riwayat.");
    }
  }
  document.getElementById("btnSaveHistory").addEventListener("click", saveHandler);

  function printHandler() { window.print(); }
  document.getElementById("btnDownloadPdf").addEventListener("click", printHandler);
  document.getElementById("btnDownloadPdf2").addEventListener("click", printHandler);
}

render();
