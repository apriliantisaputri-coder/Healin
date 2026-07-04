/* =========================================================
   HEAL.IN — RIWAYAT PEMERIKSAAN (History list page)
   Mengambil data dari backend (/history) yang membaca tabel
   examination_history milik pengguna yang sedang login.
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

function formatTanggalIndo(isoString) {
  const d = new Date(isoString);
  return `${d.getDate()} ${INDO_MONTHS[d.getMonth()]} ${d.getFullYear()}`;
}

const session = healinGetSession();

const loadingState = document.getElementById("loadingState");
const emptyState = document.getElementById("emptyState");
const emptySearchState = document.getElementById("emptySearchState");
const listState = document.getElementById("listState");
const riwayatGrid = document.getElementById("riwayatGrid");
const paginationBar = document.getElementById("paginationBar");
const searchInput = document.getElementById("searchInput");
const toast = document.getElementById("toast");
const confirmModal = document.getElementById("confirmModal");
const btnBatalHapus = document.getElementById("btnBatalHapus");
const btnKonfirmasiHapus = document.getElementById("btnKonfirmasiHapus");

let state = { page: 1, perPage: 10, q: "", pendingDeleteId: null };
let searchDebounceTimer = null;

function hideAllStates() {
  loadingState.classList.add("d-none");
  emptyState.classList.add("d-none");
  emptySearchState.classList.add("d-none");
  listState.classList.add("d-none");
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2600);
}

function renderCard(item) {
  const badgeClass = BADGE_CLASS[item.detected_condition] || "normal";
  const tanggal = formatTanggalIndo(item.examination_date);
  const ringkasan = item.recommendation_summary || "Tidak ada ringkasan rekomendasi.";

  const card = document.createElement("div");
  card.className = "riwayat-card";
  card.innerHTML = `
    <div class="riwayat-card-head">
      <span class="riwayat-tanggal">${tanggal}</span>
      <span class="riwayat-badge ${badgeClass}">${item.detected_condition}</span>
    </div>
    <h3 class="riwayat-kondisi">${item.detected_condition}</h3>
    <p class="riwayat-ringkasan">${ringkasan}</p>
    <div class="riwayat-actions">
      <a href="history-detail.html?id=${item.id}" class="btn-healin-outline">Lihat Detail</a>
      <button class="btn-hapus" data-id="${item.id}">Hapus</button>
    </div>
  `;
  card.querySelector(".btn-hapus").addEventListener("click", () => openConfirmModal(item.id));
  return card;
}

function renderPagination(meta) {
  paginationBar.innerHTML = "";
  if (meta.total_pages <= 1) return;

  const makeBtn = (label, page, opts = {}) => {
    const btn = document.createElement("button");
    btn.textContent = label;
    if (opts.active) btn.classList.add("active");
    if (opts.disabled) btn.disabled = true;
    btn.addEventListener("click", () => {
      state.page = page;
      loadHistory();
    });
    return btn;
  };

  paginationBar.appendChild(makeBtn("‹ Sebelumnya", meta.page - 1, { disabled: meta.page <= 1 }));
  for (let p = 1; p <= meta.total_pages; p += 1) {
    paginationBar.appendChild(makeBtn(String(p), p, { active: p === meta.page }));
  }
  paginationBar.appendChild(makeBtn("Berikutnya ›", meta.page + 1, { disabled: meta.page >= meta.total_pages }));
}

async function loadHistory() {
  hideAllStates();
  loadingState.classList.remove("d-none");

  try {
    const result = await apiGetHistoryList({
      page: state.page,
      perPage: state.perPage,
      q: state.q,
    });

    hideAllStates();

    if (result.total === 0 && !state.q) {
      emptyState.classList.remove("d-none");
      return;
    }
    if (result.total === 0 && state.q) {
      emptySearchState.classList.remove("d-none");
      return;
    }

    riwayatGrid.innerHTML = "";
    result.data.forEach((item) => riwayatGrid.appendChild(renderCard(item)));
    renderPagination(result);
    listState.classList.remove("d-none");
  } catch (err) {
    hideAllStates();
    emptySearchState.classList.remove("d-none");
    emptySearchState.querySelector("h2").textContent = "Gagal memuat riwayat.";
    emptySearchState.querySelector("p").textContent = err.message;
  }
}

function openConfirmModal(id) {
  state.pendingDeleteId = id;
  confirmModal.classList.remove("d-none");
}
function closeConfirmModal() {
  state.pendingDeleteId = null;
  confirmModal.classList.add("d-none");
}

btnBatalHapus.addEventListener("click", closeConfirmModal);
confirmModal.addEventListener("click", (e) => {
  if (e.target === confirmModal) closeConfirmModal();
});

btnKonfirmasiHapus.addEventListener("click", async () => {
  const id = state.pendingDeleteId;
  if (!id) return;
  btnKonfirmasiHapus.disabled = true;
  btnKonfirmasiHapus.textContent = "Menghapus...";

  try {
    await apiDeleteHistory(id);
    closeConfirmModal();
    showToast("Riwayat berhasil dihapus.");
    // Jika halaman saat ini jadi kosong setelah hapus & bukan halaman
    // pertama, mundur satu halaman supaya tidak menampilkan grid kosong.
    if (riwayatGrid.children.length === 1 && state.page > 1) {
      state.page -= 1;
    }
    loadHistory();
  } catch (err) {
    closeConfirmModal();
    showToast(err.message || "Gagal menghapus riwayat.");
  } finally {
    btnKonfirmasiHapus.disabled = false;
    btnKonfirmasiHapus.textContent = "Hapus";
  }
});

searchInput.addEventListener("input", () => {
  clearTimeout(searchDebounceTimer);
  searchDebounceTimer = setTimeout(() => {
    state.q = searchInput.value.trim();
    state.page = 1;
    loadHistory();
  }, 350);
});

loadHistory();
