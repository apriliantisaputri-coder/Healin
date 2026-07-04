/* =========================================================
   HEAL.IN — AUTH (BACKEND, TOKEN-BASED)
   Login/daftar sekarang memanggil backend Flask (/api/register,
   /api/login, /api/logout, /api/me). Password TIDAK PERNAH disimpan
   di localStorage -- hanya token sesi (hasil terbitan server) dan
   info tampilan (nama, email) yang disimpan, untuk dipakai kembali
   sebagai header "Authorization: Bearer <token>" pada pemanggilan
   API berikutnya (skrining & riwayat).
   ========================================================= */

const HEALIN_SESSION_KEY = "healin_session";

function healinGetSession() {
  try {
    return JSON.parse(localStorage.getItem(HEALIN_SESSION_KEY));
  } catch {
    return null;
  }
}

/** Simpan sesi setelah register/login berhasil. `authResult` adalah
 * response dari apiRegister()/apiLogin(): { token, expires_at, user }. */
function healinSetSession(authResult) {
  localStorage.setItem(
    HEALIN_SESSION_KEY,
    JSON.stringify({
      token: authResult.token,
      expiresAt: authResult.expires_at,
      nama: authResult.user.full_name,
      email: authResult.user.email,
    })
  );
}

function healinClearSession() {
  localStorage.removeItem(HEALIN_SESSION_KEY);
}

/** True kalau ada sesi tersimpan dan belum lewat waktu kedaluwarsanya
 * (pengecekan cepat di klien; validasi sesungguhnya tetap di server
 * lewat /api/me atau endpoint yang dilindungi require_auth). */
function healinHasValidLocalSession() {
  const session = healinGetSession();
  if (!session || !session.token) return false;
  if (session.expiresAt && new Date(session.expiresAt) <= new Date()) {
    return false;
  }
  return true;
}

/** Ambil parameter ?redirect=... dari URL saat ini. */
function healinGetRedirectParam() {
  const params = new URLSearchParams(window.location.search);
  return params.get("redirect") || "index.html";
}

/** Pasang di halaman yang wajib login (mis. questionnaire.html). */
function healinRequireAuth() {
  const session = healinGetSession();
  if (!healinHasValidLocalSession()) {
    healinClearSession();
    const current = window.location.pathname.split("/").pop() || "index.html";
    window.location.href = `sign-in.html?redirect=${encodeURIComponent(current)}`;
    return null;
  }
  return session;
}

/**
 * Isi slot navbar (elemen dengan id="authNavSlot") dengan tautan
 * "Masuk / Daftar" atau nama pengguna + tombol "Keluar", tergantung
 * status sesi saat ini.
 */
function healinInitNavAuthState() {
  const riwayatNavItem = document.getElementById("riwayatNavItem");
  if (riwayatNavItem) {
    riwayatNavItem.classList.toggle("d-none", !healinHasValidLocalSession());
  }

  const slot = document.getElementById("authNavSlot");
  if (!slot) return;
  const session = healinHasValidLocalSession() ? healinGetSession() : null;

  if (session) {
    const firstName = session.nama.split(" ")[0];
    slot.outerHTML = `
      <li class="nav-item"><span class="nav-link" style="color:var(--hijau-700) !important; font-weight:600;">Hai, ${firstName}</span></li>
      <li class="nav-item ms-lg-2"><a href="#" id="healinLogoutBtn" class="btn-healin-outline">Keluar</a></li>
    `;
    document.getElementById("healinLogoutBtn").addEventListener("click", async (e) => {
      e.preventDefault();
      try {
        await apiLogout();
      } catch {
        /* Server mungkin tidak menyala -- tetap hapus sesi lokal. */
      }
      healinClearSession();
      window.location.href = "index.html";
    });
  } else {
    healinClearSession();
    slot.outerHTML = `
      <li class="nav-item"><a class="nav-link" href="sign-in.html">Masuk</a></li>
      <li class="nav-item ms-lg-2"><a class="btn-healin" href="sign-up.html">Daftar</a></li>
    `;
  }
}

document.addEventListener("DOMContentLoaded", healinInitNavAuthState);
