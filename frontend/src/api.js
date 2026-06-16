// Capa de acceso a la API. El token se guarda en localStorage para mantener
// la sesión entre recargas. Todas las peticiones a la API pasan por el proxy
// de Vite (/api -> backend Django).

const TOKEN_KEY = "grc_token";
const USER_KEY = "grc_user";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getUser() {
  const raw = localStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}

export function saveSession(data) {
  localStorage.setItem(TOKEN_KEY, data.token);
  localStorage.setItem(
    USER_KEY,
    JSON.stringify({
      username: data.username,
      roles: data.roles,
      is_superuser: data.is_superuser,
    })
  );
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export async function login(username, password) {
  const res = await fetch("/api/login/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "No se pudo iniciar sesión.");
  }
  return res.json();
}

export async function fetchDashboard() {
  const res = await fetch("/api/dashboard/", {
    headers: { Authorization: "Token " + getToken() },
  });
  if (res.status === 401) {
    clearSession();
    throw new Error("Sesión expirada. Vuelve a iniciar sesión.");
  }
  if (!res.ok) throw new Error("No se pudieron cargar las métricas.");
  return res.json();
}
