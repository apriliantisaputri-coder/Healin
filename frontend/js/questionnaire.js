// Catat waktu mulai pengisian formulir (ADITIF, tidak mengubah logic
// wizard/step di bawah). Dipakai murni untuk menampilkan "Durasi Skrining"
// di halaman result.html -- kalau key ini sudah ada (mis. user reload
// halaman di tengah pengisian), tidak ditimpa supaya durasi tetap akurat.
if (!sessionStorage.getItem("healin_start_time")) {
  sessionStorage.setItem("healin_start_time", String(Date.now()));
}

const TOTAL_STEP = 4;
let currentStep = 1;

const stepLabels = {
  1: "Gejala Fisik",
  2: "Gejala Kognitif",
  3: "Gejala Emosional",
  4: "Gejala Perilaku",
};

const stepLabelEl = document.getElementById("stepLabel");
const stepPercentEl = document.getElementById("stepPercent");
const progressBar = document.getElementById("progressBar");
const btnBack = document.getElementById("btnBack");
const btnNext = document.getElementById("btnNext");
const btnSubmit = document.getElementById("btnSubmit");
const errorBox = document.getElementById("errorBox");
const form = document.getElementById("gejalaForm");

function showStep(step) {
  document.querySelectorAll(".step-panel").forEach((panel) => {
    panel.classList.toggle("active", Number(panel.dataset.step) === step);
  });

  const percent = Math.round((step / TOTAL_STEP) * 100);
  stepLabelEl.textContent = `Langkah ${step} dari ${TOTAL_STEP} · ${stepLabels[step]}`;
  stepPercentEl.textContent = `${percent}%`;
  progressBar.style.width = `${percent}%`;

  btnBack.disabled = step === 1;
  btnNext.classList.toggle("d-none", step === TOTAL_STEP);
  btnSubmit.classList.toggle("d-none", step !== TOTAL_STEP);
  errorBox.classList.add("d-none");
}

btnNext.addEventListener("click", () => {
  if (currentStep < TOTAL_STEP) {
    currentStep += 1;
    showStep(currentStep);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
});

btnBack.addEventListener("click", () => {
  if (currentStep > 1) {
    currentStep -= 1;
    showStep(currentStep);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
});

// Efek visual saat checkbox dicentang
document.querySelectorAll(".gejala-option").forEach((opt) => {
  const checkbox = opt.querySelector("input");
  const sync = () => opt.classList.toggle("checked", checkbox.checked);
  checkbox.addEventListener("change", sync);
  sync();
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const dipilih = Array.from(form.querySelectorAll('input[name="gejala"]:checked')).map((el) => el.value);

  if (dipilih.length === 0) {
    errorBox.textContent = "Pilih minimal 1 gejala sebelum melihat hasil.";
    errorBox.classList.remove("d-none");
    return;
  }

  btnSubmit.disabled = true;
  btnSubmit.textContent = "Memproses...";

  try {
    const session = healinGetSession(); // dari js/auth.js, sudah dimuat di questionnaire.html
    const hasil = await apiPostSkrining(dipilih, session);

    // Durasi skrining (detik) -- ADITIF, hanya dipakai untuk ditampilkan
    // di result.html, tidak memengaruhi payload yang dikirim ke API.
    const mulai = Number(sessionStorage.getItem("healin_start_time")) || Date.now();
    const durasiDetik = Math.max(0, Math.round((Date.now() - mulai) / 1000));

    sessionStorage.setItem(
      "healin_hasil",
      JSON.stringify({ ...hasil, gejala_dipilih: dipilih, durasi_detik: durasiDetik, waktu_selesai: Date.now() })
    );
    sessionStorage.removeItem("healin_start_time");
    window.location.href = "result.html";
  } catch (err) {
    errorBox.textContent = `Gagal terhubung ke server: ${err.message}. Pastikan backend Flask sudah berjalan di ${API_BASE_URL}.`;
    errorBox.classList.remove("d-none");
    btnSubmit.disabled = false;
    btnSubmit.textContent = "Lihat Hasil";
  }
});

showStep(currentStep);
