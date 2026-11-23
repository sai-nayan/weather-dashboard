# Phase 9: DevSecOps & Image Security

**Course:** DevOps & Automation Lab (ENSP461)  
**Project:** End-to-End Cloud-Native Weather Dashboard  

---

## 🎯 Overview

Phase 9 integrates comprehensive DevSecOps practices across the entire software delivery lifecycle:
1. **Container Security & Least Privilege**: Hardened, non-root user execution in production containers.
2. **Role-Based Access Control (RBAC)**: Kubernetes ServiceAccount, Role, and RoleBinding enforcing least-privilege access within the cluster.
3. **Static Application Security Testing (SAST)**: Automated code flaw and vulnerability audits using Bandit.
4. **Container Image Vulnerability Scanning**: Automated CVE vulnerability detection using Trivy.
5. **Secret & Credential Protection**: Automated detection of hardcoded secrets and externalized Kubernetes Secret management.

---

## 🔒 1. Kubernetes Role-Based Access Control (RBAC)

The application runs under a dedicated service account with scoped, least-privilege role permissions:

- **Manifest**: [`kubernetes/rbac.yaml`](../kubernetes/rbac.yaml)
- **ServiceAccount**: `weather-dashboard-sa`
- **Role**: `weather-dashboard-role`
  - Read access (`get`, `list`, `watch`) to `configmaps` and `secrets`
  - Read access (`get`, `list`) to `pods` for telemetry
  - No permission to create, delete, or escalate cluster-level privileges
- **RoleBinding**: `weather-dashboard-rolebinding` attaches the role to the service account.

```bash
# Apply RBAC configuration
kubectl apply -f kubernetes/rbac.yaml
```

---

## 🛡️ 2. Automated Security Scanning Scripts

A cross-platform security scanning suite is provided for local and CI environments:

- **Linux / macOS**: `./scripts/security-scan.sh`
- **Windows PowerShell**: `.\scripts\security-scan.ps1`

### Scan Scope:
1. **Secret & Key Leak Detection**: Audits repository files for unencrypted AWS access keys, GitHub tokens, and private keys.
2. **SAST Code Security (Bandit)**: Scans Python codebase for SQL injection risks, insecure deserialization, and dangerous standard library functions.
3. **Container CVE Scan (Trivy)**: Scans target Docker images for known CVEs with High and Critical severity filtering.
4. **RBAC & Security Context Verification**: Confirms `fsGroup` volume ownership and dedicated `ServiceAccount` configuration.

---

## 🔄 3. CI/CD DevSecOps Pipeline Integration

In [`Jenkinsfile`](../Jenkinsfile), two dedicated automated security stages are integrated:

```groovy
stage('Security Code Analysis (SAST - Phase 9)') {
    steps {
        echo 'Stage 6: Running Static Application Security Testing (Bandit / Flake8)'
        // Generates reports/bandit-report.json
    }
}

stage('Image Vulnerability Scanning (Trivy - Phase 9)') {
    steps {
        echo 'Stage 8: Scanning Docker image for CVE vulnerabilities (Trivy)'
        // Runs trivy image --severity HIGH,CRITICAL ${DOCKER_IMAGE}:${DOCKER_TAG}
    }
}
```

---

## 🐳 4. Docker Image Hardening

The production [`Dockerfile`](../Dockerfile) enforces multiple defense-in-depth measures:
- **Non-Root Execution**: Runs under unprivileged user `appuser` (UID/GID 1000).
- **Minimal Attack Surface**: Uses `python:3.13-slim` base image.
- **Cache Optimization**: `pip install --no-cache-dir` removes installation caches.
- **Built-in Healthcheck**: Verifies `/health` endpoint every 30s.
