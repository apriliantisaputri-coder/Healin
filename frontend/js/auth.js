/* =========================================================
   HEAL.IN — AUTH (DEMO, FRONTEND-ONLY)
   Login/daftar disimpan di localStorage browser. Ini BUKAN
   otentikasi yang aman (password tidak di-hash, tidak ada
   verifikasi server) — cukup untuk mendemokan alur UI
   "harus sign in sebelum skrining" sebelum backend auth
   asli dibuat.
   ========================================================= */

const HEALIN_USERS_KEY = "healin_users";
const HEALIN_SESSION_KEY = "healin_session";

function healinGetUsers() {
  try {
    return JSON.parse(localStorage.getItem(HEALIN_USERS_KEY)) || [];
  } catch {
    return [];
  }
}

function healinSaveUsers(users) {
  localStorage.setItem(HEALIN_USERS_KEY, JSON.stringify(users));
}

function healinGetSession() {
  try {
    return JSON.parse(localStorage.getItem(HEALIN_SESSION_KEY));
  } catch {
    return null;
  }
}

function healinSetSession(user) {
  localStorage.setItem(
    HEALIN_SESSION_KEY,
    JSON.stringify({ nama: user.nama, email: user.email })
  );
}

function healinClearSession() {
  localStorage.removeItem(HEALIN_SESSION_KEY);
}

/** Ambil parameter ?redirect=... dari URL saat ini. */
function healinGetRedirectParam() {
  const params = new URLSearchParams(window.location.search);
  return params.get("redirect") || "index.html";
}

/** Pasang di halaman yang wajib login (mis. questionnaire.html). */
function healinRequireAuth() {
  const session = healinGetSession();
  if (!session) {
    const current = window.location.pathname.split("/").pop() || "index.html";
    window.location.href = `sign-in.html?redirect=${encodeURIComponent(current)}`;
  }
  return session;
}

/**
 * Isi slot navbar (elemen dengan id="authNavSlot") dengan tautan
 * "Masuk / Daftar" atau nama pengguna + tombol "Keluar", tergantung
 * status sesi saat ini.
 */
function healinInitNavAuthState() {
  const slot = document.getElementById("authNavSlot");
  if (!slot) return;
  const session = healinGetSession();

  // authNavSlot itself is an <li> placeholder; we replace it entirely
  // with the real <li> item(s) so the markup stays valid (no <li> inside <li>).
  if (session) {
    const firstName = session.nama.split(" ")[0];
    slot.outerHTML = `
      <li class="nav-item"><span class="nav-link" style="color:var(--hijau-700) !important; font-weight:600;">Hai, ${firstName}</span></li>
      <li class="nav-item ms-lg-2"><a href="#" id="healinLogoutBtn" class="btn-healin-outline">Keluar</a></li>
    `;
    document.getElementById("healinLogoutBtn").addEventListener("click", (e) => {
      e.preventDefault();
      healinClearSession();
      window.location.href = "index.html";
    });
  } else {
    slot.outerHTML = `
      <li class="nav-item"><a class="nav-link" href="sign-in.html">Masuk</a></li>
      <li class="nav-item ms-lg-2"><a class="btn-healin" href="sign-up.html">Daftar</a></li>
    `;
  }
}

document.addEventListener("DOMContentLoaded", healinInitNavAuthState);