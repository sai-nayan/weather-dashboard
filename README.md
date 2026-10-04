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
| **Phase 2** | Continuous Integration & Automated Testing | Jenkins, Pytest | Upcoming |
| **Phase 3** | Containerization & Multi-stage Builds | Docker, Docker Compose | Upcoming |
| **Phase 4** | Container Orchestration & Scaling | Kubernetes, Helm | Upcoming |
| **Phase 5** | Configuration Management | Ansible | Upcoming |
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

Detailed git commands, logs, and conflict resolution walkthroughs are documented in [GIT_WORKFLOW.md](GIT_WORKFLOW.md).

---

## 🚀 Quickstart (Local Development)

### Prerequisites
- Python 3.11+ (Conda environment recommended)
- Git

### Running with Conda
```bash
# Activate existing conda environment
conda activate default

# Install or verify requirements
pip install -r requirements.txt

# Run database migrations & start application
python run.py
```

The application runs on `http://127.0.0.1:5050`.

### Running Tests
```bash
pytest -v tests/
```
