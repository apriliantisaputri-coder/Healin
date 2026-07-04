/**
 * Mesin inferensi Forward Chaining Heal.In -- versi JavaScript (client-side).
 *
 * Ini adalah PORTING 1:1 dari engine Python (engine/knowledge_engine.py +
 * rules/*.py yang berbasis Experta) supaya hasil skrining bisa dihitung
 * LANGSUNG di browser, tanpa perlu menjalankan backend Flask sama sekali.
 * Nilai gejala, skor, salience, dan teks aturan IF-THEN SENGAJA disalin
 * persis dari kode Python agar hasilnya selalu identik.
 *
 * Kalau suatu saat aturan di rules/*.py diubah, lakukan perubahan yang
 * sama di sini juga.
 */

const SEMUA_GEJALA = [
  "sulit_tidur", "mudah_lelah", "sakit_kepala",
  "sulit_konsentrasi", "mudah_lupa", "pikiran_negatif",
  "cemas_berlebihan", "mudah_marah", "sedih_berkepanjangan", "putus_asa",
  "kehilangan_motivasi", "menarik_diri", "penurunan_produktivitas",
];

// Setiap grup diurutkan dari salience TERTINGGI ke TERENDAH, sama seperti
// urutan firing pada Experta (Potensi Depresi paling prioritas / paling
// parah, Normal paling rendah). Di dalam satu grup, urutan aturan mengikuti
// urutan deklarasi pada file Python aslinya.
const RULE_GROUPS = [
  {
    kondisi: "Potensi Depresi",
    salience: 50,
    rules: [
      { mandatory: ["sedih_berkepanjangan", "kehilangan_motivasi"], skor: 48,
        aturan: "IF sedih_berkepanjangan AND kehilangan_motivasi THEN Potensi Depresi" },
      { mandatory: ["putus_asa", "kehilangan_motivasi", "menarik_diri"], skor: 50,
        aturan: "IF putus_asa AND kehilangan_motivasi AND menarik_diri THEN Potensi Depresi" },
      { mandatory: ["sedih_berkepanjangan", "menarik_diri"], skor: 46,
        aturan: "IF sedih_berkepanjangan AND menarik_diri THEN Potensi Depresi" },
      { mandatory: ["putus_asa", "penurunan_produktivitas"], skor: 46,
        aturan: "IF putus_asa AND penurunan_produktivitas THEN Potensi Depresi" },
      { mandatory: ["sedih_berkepanjangan", "pikiran_negatif", "kehilangan_motivasi"], skor: 50,
        aturan: "IF sedih_berkepanjangan AND pikiran_negatif AND kehilangan_motivasi THEN Potensi Depresi" },
      { mandatory: ["putus_asa", "sedih_berkepanjangan"], skor: 50,
        aturan: "IF putus_asa AND sedih_berkepanjangan THEN Potensi Depresi" },
    ],
  },
  {
    kondisi: "Stres Berat",
    salience: 40,
    rules: [
      { mandatory: ["sulit_tidur", "cemas_berlebihan", "sulit_konsentrasi", "kehilangan_motivasi"], skor: 40,
        aturan: "IF sulit_tidur AND cemas_berlebihan AND sulit_konsentrasi AND kehilangan_motivasi THEN Stres Berat" },
      { mandatory: ["mudah_lelah", "sakit_kepala", "sulit_konsentrasi", "mudah_marah"], skor: 38,
        aturan: "IF mudah_lelah AND sakit_kepala AND sulit_konsentrasi AND mudah_marah THEN Stres Berat" },
      { mandatory: ["sulit_tidur", "mudah_marah", "penurunan_produktivitas"], skor: 36,
        aturan: "IF sulit_tidur AND mudah_marah AND penurunan_produktivitas THEN Stres Berat" },
      { mandatory: ["pikiran_negatif", "sulit_konsentrasi", "mudah_lelah", "sulit_tidur"], skor: 38,
        aturan: "IF pikiran_negatif AND sulit_konsentrasi AND mudah_lelah AND sulit_tidur THEN Stres Berat" },
      { mandatory: ["cemas_berlebihan", "mudah_marah", "sulit_tidur", "penurunan_produktivitas"], skor: 40,
        aturan: "IF cemas_berlebihan AND mudah_marah AND sulit_tidur AND penurunan_produktivitas THEN Stres Berat" },
    ],
  },
  {
    kondisi: "Kecemasan",
    salience: 30,
    rules: [
      { mandatory: ["cemas_berlebihan", "sulit_tidur", "mudah_marah"], skor: 30,
        aturan: "IF cemas_berlebihan AND sulit_tidur AND mudah_marah THEN Kecemasan" },
      { mandatory: ["cemas_berlebihan", "sakit_kepala"], skor: 26,
        aturan: "IF cemas_berlebihan AND sakit_kepala THEN Kecemasan" },
      { mandatory: ["cemas_berlebihan", "pikiran_negatif"], skor: 28,
        aturan: "IF cemas_berlebihan AND pikiran_negatif THEN Kecemasan" },
      { mandatory: ["cemas_berlebihan", "menarik_diri"], skor: 28,
        aturan: "IF cemas_berlebihan AND menarik_diri THEN Kecemasan" },
      { mandatory: ["cemas_berlebihan", "mudah_lupa", "sulit_konsentrasi"], skor: 30,
        aturan: "IF cemas_berlebihan AND mudah_lupa AND sulit_konsentrasi THEN Kecemasan" },
    ],
  },
  {
    kondisi: "Stres Ringan",
    salience: 20,
    rules: [
      { mandatory: ["sulit_tidur", "cemas_berlebihan", "sulit_konsentrasi"], skor: 20,
        aturan: "IF sulit_tidur AND cemas_berlebihan AND sulit_konsentrasi THEN Stres Ringan" },
      { mandatory: ["sulit_tidur", "mudah_lelah"], skor: 18,
        aturan: "IF sulit_tidur AND mudah_lelah THEN Stres Ringan" },
      { mandatory: ["sakit_kepala", "sulit_konsentrasi"], skor: 18,
        aturan: "IF sakit_kepala AND sulit_konsentrasi THEN Stres Ringan" },
      { mandatory: ["mudah_lelah", "penurunan_produktivitas"], skor: 18,
        aturan: "IF mudah_lelah AND penurunan_produktivitas THEN Stres Ringan" },
      { mandatory: ["sulit_konsentrasi", "mudah_lupa"], skor: 18,
        aturan: "IF sulit_konsentrasi AND mudah_lupa THEN Stres Ringan" },
    ],
  },
  {
    kondisi: "Normal",
    salience: 5,
    rules: [
      { mandatory: ["mudah_lelah"], forbidden: ["sulit_tidur", "cemas_berlebihan", "sedih_berkepanjangan"], skor: 5,
        aturan: "IF mudah_lelah AND NOT sulit_tidur AND NOT cemas_berlebihan AND NOT sedih_berkepanjangan THEN Normal" },
      { mandatory: ["sakit_kepala"], forbidden: ["sulit_konsentrasi", "cemas_berlebihan"], skor: 5,
        aturan: "IF sakit_kepala AND NOT sulit_konsentrasi AND NOT cemas_berlebihan THEN Normal" },
      { mandatory: ["mudah_lupa"], forbidden: ["sulit_konsentrasi", "pikiran_negatif"], skor: 5,
        aturan: "IF mudah_lupa AND NOT sulit_konsentrasi AND NOT pikiran_negatif THEN Normal" },
    ],
  },
];

const REKOMENDASI = {
  "Normal": [
    "Pertahankan pola tidur dan aktivitas yang sudah baik.",
    "Lakukan jeda singkat di sela belajar agar tetap segar.",
  ],
  "Stres Ringan": [
    "Terapkan teknik manajemen waktu sederhana (mis. to-do list harian).",
    "Latihan pernapasan/relaksasi singkat sebelum tidur.",
    "Jaga pola tidur yang teratur.",
  ],
  "Stres Berat": [
    "Kurangi beban aktivitas yang menumpuk dan atur prioritas tugas.",
    "Coba teknik relaksasi terpandu atau olahraga ringan secara rutin.",
    "Pertimbangkan konsultasi dengan konselor kampus apabila gejala berlanjut.",
  ],
  "Kecemasan": [
    "Latihan pernapasan dalam (deep breathing) saat cemas muncul.",
    "Batasi paparan pemicu kecemasan yang berlebihan (mis. scrolling berita larut malam).",
    "Rujukan konsultasi ke konselor kampus disarankan.",
  ],
  "Potensi Depresi": [
    "Segera bicarakan kondisi ini dengan orang terdekat yang dipercaya.",
    "Sangat disarankan untuk berkonsultasi dengan psikolog atau tenaga medis profesional.",
    "Hindari mengambil keputusan besar sendirian saat kondisi belum stabil.",
  ],
};

function getRekomendasi(namaKondisi) {
  return REKOMENDASI[namaKondisi] || REKOMENDASI["Normal"];
}

/**
 * Menjalankan satu sesi inferensi forward chaining di browser.
 * @param {string[]} daftarGejala - daftar kode gejala yang dicentang user.
 * @returns {{kondisi: string, skor: number, explanation_trace: Array}}
 */
function runInferenceLocal(daftarGejala) {
  const gejalaSet = new Set(daftarGejala);
  const explanationTrace = [];
  let terbaik = null; // { kondisi, skor, aturan }

  for (const grup of RULE_GROUPS) {
    for (const rule of grup.rules) {
      const cocokWajib = rule.mandatory.every((g) => gejalaSet.has(g));
      const cocokLarangan = (rule.forbidden || []).every((g) => !gejalaSet.has(g));
      if (cocokWajib && cocokLarangan) {
        const entry = { kondisi: grup.kondisi, skor: rule.skor, aturan: rule.aturan };
        explanationTrace.push(entry);
        if (!terbaik || entry.skor > terbaik.skor) {
          terbaik = entry;
        }
      }
    }
  }

  if (!terbaik) {
    return {
      kondisi: "Normal",
      skor: 0,
      explanation_trace: [
        {
          kondisi: "Normal",
          skor: 0,
          aturan: "Tidak ada aturan yang aktif -> default kondisi Normal",
        },
      ],
    };
  }

  return {
    kondisi: terbaik.kondisi,
    skor: terbaik.skor,
    explanation_trace: explanationTrace,
  };
}

/**
 * Setara dengan response endpoint POST /api/skrining, tapi dihitung
 * sepenuhnya di browser (sinkron, dibungkus Promise supaya pemanggilnya
 * tetap bisa pakai `await` seperti sebelumnya saat masih memanggil API).
 * @param {string[]} daftarGejala
 */
function jalankanSkriningLocal(daftarGejala) {
  const tidakDikenali = daftarGejala.filter((g) => !SEMUA_GEJALA.includes(g));
  if (!Array.isArray(daftarGejala) || daftarGejala.length === 0) {
    return Promise.reject(new Error("Minimal pilih 1 gejala"));
  }
  if (tidakDikenali.length > 0) {
    return Promise.reject(new Error(`Gejala tidak dikenali: ${tidakDikenali.join(", ")}`));
  }

  const hasil = runInferenceLocal(daftarGejala);
  const rekomendasi = getRekomendasi(hasil.kondisi);

  return Promise.resolve({
    kondisi: hasil.kondisi,
    skor: hasil.skor,
    explanation_trace: hasil.explanation_trace,
    rekomendasi,
  });
}
