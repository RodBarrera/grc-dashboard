import { useState } from "react";
import { login, saveSession } from "../api";

export default function Login({ onSuccess }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    setError("");
    setLoading(true);
    try {
      const data = await login(username, password);
      saveSession(data);
      onSuccess(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function onKeyDown(e) {
    if (e.key === "Enter") handleSubmit();
  }

  return (
    <div className="login-screen">
      <div className="login-card">
        <p className="eyebrow">ISO/IEC 27001:2022</p>
        <h2>GRC Dashboard</h2>
        <p className="lead">Panel de cumplimiento y gestión de riesgos.</p>

        {error && <div className="error-msg">{error}</div>}

        <div className="field">
          <label htmlFor="u">Usuario</label>
          <input
            id="u"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            onKeyDown={onKeyDown}
            autoFocus
          />
        </div>
        <div className="field">
          <label htmlFor="p">Contraseña</label>
          <input
            id="p"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={onKeyDown}
          />
        </div>
        <button
          className="btn btn-primary"
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? "Verificando…" : "Iniciar sesión"}
        </button>
      </div>
    </div>
  );
}
