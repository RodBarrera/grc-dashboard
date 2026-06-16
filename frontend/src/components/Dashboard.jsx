import { useEffect, useState } from "react";
import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";
import { fetchDashboard } from "../api";

const RISK_COLORS = {
  "Crítico": "var(--critical)",
  "Alto": "var(--high)",
  "Medio": "var(--medium)",
  "Bajo": "var(--low)",
};

function Gauge({ value }) {
  const data = [
    { name: "done", value: value },
    { name: "rest", value: Math.max(0, 100 - value) },
  ];
  return (
    <div className="gauge-wrap">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            innerRadius={78}
            outerRadius={96}
            startAngle={90}
            endAngle={-270}
            stroke="none"
          >
            <Cell fill="var(--accent)" />
            <Cell fill="var(--surface-2)" />
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <div className="gauge-center">
        <span className="gauge-value">{value}%</span>
        <span className="gauge-label">cumplimiento</span>
      </div>
    </div>
  );
}

export default function Dashboard({ user, onLogout }) {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchDashboard()
      .then(setStats)
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return (
      <div className="center-state">
        {error}
      </div>
    );
  }
  if (!stats) {
    return <div className="center-state">Cargando métricas…</div>;
  }

  const c = stats.controls;
  const role =
    user.is_superuser ? "ADMIN" : (user.roles[0] || "SIN ROL").toUpperCase();

  return (
    <>
      <div className="topbar">
        <div className="brand">
          <h1>GRC Dashboard</h1>
          <span className="tag">ISO 27001:2022</span>
        </div>
        <div className="user-box">
          <span>{user.username}</span>
          <span className="role">{role}</span>
          <button className="btn" onClick={onLogout}>
            Salir
          </button>
        </div>
      </div>

      <div className="dashboard">
        {/* Hero: gauge + métricas clave */}
        <p className="eyebrow">Postura de cumplimiento</p>
        <div className="hero">
          <div className="card gauge-card">
            <Gauge value={stats.compliance_percentage} />
          </div>
          <div className="card stat-grid">
            <div className="stat">
              <span className="num">{c.total}</span>
              <span className="lbl">Controles del marco</span>
              <span className="sub">{c.not_assessed} sin evaluar</span>
            </div>
            <div className="stat">
              <span className="num" style={{ color: "var(--implemented)" }}>
                {c.implemented}
              </span>
              <span className="lbl">
                <span className="dot" style={{ background: "var(--implemented)" }} />
                Implementados
              </span>
              <span className="sub">{c.partial} parciales</span>
            </div>
            <div className="stat">
              <span className="num">{stats.assets.total}</span>
              <span className="lbl">Activos registrados</span>
            </div>
            <div className="stat">
              <span className="num" style={{ color: "var(--critical)" }}>
                {stats.risks.open}
              </span>
              <span className="lbl">
                <span className="dot" style={{ background: "var(--critical)" }} />
                Riesgos abiertos
              </span>
              <span className="sub">{stats.risks.total} en total</span>
            </div>
          </div>
        </div>

        {/* Dominios */}
        <div className="card domains">
          <p className="eyebrow">Cumplimiento por dominio</p>
          {stats.by_domain.map((d) => (
            <div className="domain-row" key={d.domain}>
              <div>
                <div className="domain-name">{d.domain}</div>
                <div className="domain-count">
                  {d.implemented}/{d.total} controles
                </div>
              </div>
              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{ width: `${d.percentage}%` }}
                />
              </div>
              <div className="domain-pct">{d.percentage}%</div>
            </div>
          ))}
        </div>

        {/* Riesgos */}
        <p className="eyebrow">Riesgos por clasificación</p>
        <div className="risk-grid">
          {["Crítico", "Alto", "Medio", "Bajo"].map((rating) => (
            <div className="risk-cell" key={rating}>
              <div className="rnum" style={{ color: RISK_COLORS[rating] }}>
                {stats.risks.by_rating[rating] ?? 0}
              </div>
              <div className="rlbl">{rating}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
