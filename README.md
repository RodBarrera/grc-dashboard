# GRC Compliance Dashboard

Plataforma para gestionar el cumplimiento de seguridad de la información de una
organización: mapea **activos** a **controles** de marcos reconocidos
(ISO/IEC 27001:2022, NIST CSF, CIS), registra **riesgos**, adjunta **evidencias**
y muestra en un **tablero** el nivel de cumplimiento y los gaps, con un
**reporte ejecutivo** exportable.

> Proyecto de portafolio que une desarrollo full stack con gobierno, riesgo y
> cumplimiento (GRC), bajo un enfoque *security by design*.

## Por qué este proyecto

La mayoría de las soluciones de GRC son hojas de cálculo. Este proyecto demuestra
cómo modelar el problema como una aplicación real: control de acceso por roles,
trazabilidad de evidencias, métricas de madurez y seguridad incorporada desde el
diseño.

## Stack

- **Backend:** Django 6 + Django REST Framework
- **Base de datos:** PostgreSQL (SQLite como fallback local)
- **Frontend:** React *(en construcción)*
- **Infraestructura:** Docker + Docker Compose

## Estado / Roadmap

- [x] **Paso 1 — Cimientos:** estructura del repo, backend que arranca, endpoint de salud, Docker.
- [ ] **Paso 2 — Modelo de datos:** Frameworks, Controles, Activos, Riesgos, Evidencias.
- [ ] **Paso 3 — Dataset ISO 27001:** carga de los controles del Anexo A.
- [ ] **Paso 4 — API REST:** serializers, vistas y endpoints.
- [ ] **Paso 5 — Autenticación y roles:** auditor / responsable de control.
- [ ] **Paso 6 — Frontend React:** dashboard, gráficos y formularios.
- [ ] **Paso 7 — Reporte ejecutivo:** exportación a PDF.

## Cómo ejecutar (desarrollo local)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # ajusta los valores
python manage.py migrate
python manage.py runserver
```

Verifica que responde:

```bash
curl http://127.0.0.1:8000/api/health/
# {"status": "ok", "service": "grc-dashboard-api"}
```

## Cómo ejecutar (Docker)

```bash
cp backend/.env.example backend/.env   # ajusta los valores
docker compose up --build
```

## Decisiones de seguridad

- Secretos y credenciales fuera del código, leídos de variables de entorno.
- `DEBUG` desactivable por entorno; `ALLOWED_HOSTS` configurable.
- Validadores de contraseña de Django activos.
- Permisos por defecto en DRF: requiere autenticación.
- (Próximamente) control de acceso por roles y validación de cada input.

## Estructura

```
grc-dashboard/
├── backend/
│   ├── config/         # settings, urls, wsgi
│   ├── compliance/     # app principal de cumplimiento
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml
└── README.md
```

## Licencia

MIT — uso libre con atribución.
