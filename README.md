# Weather Dashboard — End-to-End Cloud-Native DevOps Capstone

**Course:** DevOps & Automation Lab (ENSP461)  
**Program:** B. Tech CSE — Semester VII  
**Project Title:** Design and Implementation of an End-to-End DevOps Pipeline for Cloud-Native Application Deployment  
**Selected Application:** Cloud-Native Weather Dashboard  

---

## 📋 Project Overview

The **Weather Dashboard** is a cloud-native web application designed to demonstrate a complete DevOps and DevSecOps lifecycle. It provides live meteorological tracking, location bookmarking, alert threshold monitoring, and search analytics backed by a responsive frontend and RESTful backend APIs.

### Key Functional Features
- **User Authentication:** Registration, secure password hashing, and session management.
- **CRUD Operations:** Create, Read, Update, and Delete saved favorite weather locations with custom alert thresholds and notes.
- **Weather API Engine:** Resilient meteorological data ingestion supporting live coordinates/cities with automatic offline/mock fallback for deterministic test execution.
- **Responsive Web Interface:** Glassmorphic modern layout with real-time UI updates, cards, and modal dialogs.
- **RESTful Endpoints:** Standardized JSON APIs with comprehensive input validation and error handling.
- **Health & Metrics:** Readiness and liveness probes (`/health`) and metrics endpoints (`/metrics`) built for container orchestration.

---

## 🛠️ DevOps Phases Roadmap

| Phase | Milestone | Technology Stack | Status |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Version Control & Branching Strategy** | Git, GitHub | **Completed** |
| **Phase 2** | **Continuous Integration & Automated Testing** | Jenkins, Pytest | **Completed** |
| **Phase 3** | **Containerization & CI/CD Pipeline** | Docker, Docker Compose, Jenkins | **Completed** |
| **Phase 4** | **Container Orchestration & Scaling** | Kubernetes, Helm | **completed** |
| **Phase 5** | **Configuration Management**| Ansible | **completed** |
| **Phase 6** | Infrastructure as Code (IaC) | Terraform | Upcoming |
| **Phase 7** | Application & Infrastructure Monitoring | Prometheus, Grafana | Upcoming |
| **Phase 8** | Centralized Logging | Fluentd / ELK Stack | Upcoming |
| **Phase 9** | DevSecOps & Image Security | SonarQube, Trivy, RBAC | Upcoming |
| **Phase 10** | Zero-Downtime Deployment Strategy | Blue-Green / Canary | Upcoming |
| **Phase 11** | GitOps Automated Delivery | ArgoCD / FluxCD | Upcoming |

---

## 🌿 Phase 1: Git Branching Strategy & Workflow

This repository strictly implements GitFlow branching practices:

```
main (production releases)
 │
 ├── develop (integration & staging)
 │    │
 │    ├── feature/core-models
 │    ├── feature/auth-system
 │    ├── feature/weather-service
 │    ├── feature/crud-locations
 │    ├── feature/ui-dashboard
 │    └── feature/test-suite
```

- **`main`**: Protected production branch containing stable tagged releases (`v1.0.0-phase1`).
- **`develop`**: Integration branch for continuous development.
- **`feature/*`**: Isolated branches for specific modules, merged back via pull requests.
- **Merge Conflict Resolution**: Demonstrated and logged on branch merge histories.

---

## 🐳 Phase 3: Docker Containerization & CI/CD Pipeline

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Host                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │          weather-dashboard container               │  │
│  │  ┌─────────────┐  ┌────────────────────────────┐  │  │
│  │  │  Gunicorn    │  │  Flask Application         │  │  │
│  │  │  WSGI Server │──│  - Auth Routes             │  │  │
│  │  │  Port 5050   │  │  - Weather API             │  │  │
│  │  │  2 Workers   │  │  - Location CRUD           │  │  │
│  │  │  4 Threads   │  │  - Health/Metrics          │  │  │
│  │  └─────────────┘  └────────────────────────────┘  │  │
│  │  ┌─────────────┐  ┌────────────────────────────┐  │  │
│  │  │  SQLite DB   │  │  Application Logs          │  │  │
│  │  │  (Volume)    │  │  (Volume)                  │  │  │
│  │  └─────────────┘  └────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────┘  │
│                        │ Port 5050                       │
└────────────────────────┼────────────────────────────────┘
                         ▼
                   http://localhost:5050
```

### Docker Quick Start

```bash
# Build and start the application
docker compose up --build -d

# Verify container health
docker ps
docker logs weather-dashboard

# Access the application
curl http://localhost:5050/health

# Stop the application
docker compose down

# Stop and remove volumes
docker compose down -v
```

### Docker Configuration Details

| Component | Configuration |
| :--- | :--- |
| **Base Image** | `python:3.11-slim` |
| **WSGI Server** | Gunicorn (2 workers, 4 threads) |
| **Port** | 5050 |
| **User** | Non-root `appuser` (UID 1000) |
| **Health Check** | `curl -f http://localhost:5050/health` every 30s |
| **Volumes** | `weather-data` (SQLite DB), `weather-logs` (logs) |
| **Network** | `weather-net` (bridge) |
| **Restart Policy** | `unless-stopped` |

### Environment Variables

| Variable | Default | Description |
| :--- | :--- | :--- |
| `FLASK_ENV` | `production` | Flask environment mode |
| `PORT` | `5050` | Application listen port |
| `SECRET_KEY` | `change-me-in-production` | Flask secret key |
| `DATABASE_URL` | `sqlite:///instance/weather.db` | Database connection URI |
| `GUNICORN_WORKERS` | `2` | Number of Gunicorn worker processes |
| `GUNICORN_THREADS` | `4` | Threads per worker |
| `GUNICORN_TIMEOUT` | `120` | Worker timeout in seconds |

---

## 🔄 Jenkins CI/CD Pipeline

### Pipeline Architecture

```
Jenkins Pipeline (Weather-Dashboard-CI)
 │
 ├── Stage 1: Checkout Source Code        → git clone from GitHub
 ├── Stage 2: Python Environment Check    → python --version, pip --version
 ├── Stage 3: Install Dependencies        → pip install -r requirements.txt
 ├── Stage 4: Automated Testing           → pytest with JUnit XML reports
 ├── Stage 5: Test Reports Generation     → Publish JUnit results in Jenkins
 ├── Stage 6: Docker Image Build          → docker build -t weather-dashboard
 ├── Stage 7: Docker Container Deployment → docker run on port 5050
 ├── Stage 8: Container Health Check      → curl /health endpoint
 └── Stage 9: Archive Build Artifacts     → zip + archiveArtifacts
```

### Jenkins Setup

The pipeline is configured as the **Weather-Dashboard-CI** job in Jenkins:
- **SCM:** GitHub (`https://github.com/sai-nayan/weather-dashboard.git`)
- **Branch:** `*/main`
- **Pipeline Script:** `Jenkinsfile` from repository root
- **Trigger:** GitHub Push (webhook)
- **Jenkins runs as:** Windows Service
- **Docker access:** Docker Desktop CLI and Engine

### Running the Pipeline

1. Push code to the `main` branch on GitHub
2. Jenkins automatically triggers the pipeline (via webhook) or trigger manually
3. Pipeline executes all 9 stages sequentially
4. View results in Jenkins Blue Ocean or classic UI
5. Application deployed at `http://localhost:5050`

---

## 🚀 Quickstart (Local Development)

### Prerequisites
- Python 3.11+ (Conda environment recommended)
- Git
- Docker Desktop (for containerized deployment)

### Running Locally
```bash
# Activate existing conda environment
conda activate default

# Install or verify requirements
pip install -r requirements.txt

# Run database migrations & start application
python run.py
```

The application runs on `http://127.0.0.1:5050`.

### Running with Docker
```bash
# Build and start
docker compose up --build -d

# Access at http://localhost:5050

# View logs
docker logs -f weather-dashboard

# Stop
docker compose down
```

### Running Tests
```bash
# Run all tests
pytest -v tests/

# Run with JUnit XML output
pytest -v --junitxml=reports/pytest-results.xml tests/

# Run with coverage
pytest -v --cov=app tests/
```

---

## 📁 Project Structure

```
weather-dashboard/
├── app/                          # Flask application package
│   ├── __init__.py               # Application factory
│   ├── models.py                 # SQLAlchemy models (User, FavoriteLocation)
│   ├── routes/
│   │   ├── auth.py               # Authentication endpoints
│   │   ├── locations.py          # CRUD location endpoints
│   │   ├── weather.py            # Weather API endpoints
│   │   └── web.py                # Web UI routes
│   ├── services/
│   │   └── weather_api.py        # Weather API client service
│   ├── static/css/style.css      # Glassmorphic UI stylesheet
│   └── templates/                # Jinja2 HTML templates
│       ├── base.html
│       ├── dashboard.html
│       ├── login.html
│       └── register.html
├── tests/                        # Pytest test suite
│   ├── conftest.py               # Fixtures and test configuration
│   ├── test_auth.py              # Authentication tests
│   ├── test_health.py            # Health/metrics endpoint tests
│   ├── test_locations.py         # Location CRUD tests
│   └── test_weather.py           # Weather API tests
├── docs/
│   └── API_REFERENCE.md          # REST API documentation
├── config.py                     # Environment-specific configs
├── run.py                        # Application entry point
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Production Docker image
├── docker-compose.yml            # Docker Compose orchestration
├── .dockerignore                 # Docker build exclusions
├── Jenkinsfile                   # CI/CD pipeline definition
├── environment.yml               # Conda environment spec
├── .gitignore                    # Git exclusions
└── README.md                     # This file
```

---

## 🔧 Troubleshooting

### Docker Issues

| Issue | Solution |
| :--- | :--- |
| Port 5050 already in use | `docker stop weather-dashboard && docker rm weather-dashboard` |
| Container unhealthy | Check logs: `docker logs weather-dashboard` |
| Build fails on pip install | Verify `requirements.txt` has no typos; rebuild with `--no-cache` |
| Permission denied in container | Ensure Dockerfile uses `chown -R appuser:appuser` before `USER appuser` |
| Volume data stale | Reset with `docker compose down -v && docker compose up --build -d` |

### Jenkins Pipeline Issues

| Issue | Solution |
| :--- | :--- |
| Docker not found in Jenkins | Ensure Docker Desktop is running; Jenkins service user has Docker CLI in PATH |
| pytest not found | Verify `python -m pip install -r requirements.txt` runs successfully |
| Container already exists | Pipeline handles cleanup; check `docker ps -a` manually |
| Health check fails | Increase `ping -n` wait time in Jenkinsfile deployment stage |
| Git checkout fails | Verify GitHub credentials in Jenkins credential store |

### Application Issues

| Issue | Solution |
| :--- | :--- |
| 500 on startup | Check `DATABASE_URL` env var; ensure `instance/` directory is writable |
| Weather data not loading | App uses mock fallback when API key unavailable; this is expected in CI/CD |
| Login not working | Database may need re-initialization; restart container |

---

## 📄 API Reference

See [docs/API_REFERENCE.md](docs/API_REFERENCE.md) for full REST API documentation.

**Key Endpoints:**
- `GET /health` — Application health check
- `GET /metrics` — Telemetry and performance metrics
- `POST /api/auth/register` — User registration
- `POST /api/auth/login` — User login
- `GET /api/auth/me` — Current user profile
- `GET /api/locations` — List saved locations
- `POST /api/locations` — Add a favorite location
- `GET /api/weather?city=<name>` — Fetch weather data

---

## 📝 License

This project is part of the ENSP461 DevOps & Automation Lab coursework.
