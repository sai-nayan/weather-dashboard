# Phase 10 & Phase 11: Zero-Downtime Deployment & GitOps Automated Delivery

**Course:** DevOps & Automation Lab (ENSP461)  
**Project:** End-to-End Cloud-Native Weather Dashboard  

---

## 🎯 Overview

This document provides complete implementation specifications and operational runbooks for:
- **Phase 10: Zero-Downtime Deployment Strategy** (Blue-Green Deployment & Canary Rollout with Argo Rollouts)
- **Phase 11: GitOps Automated Delivery** (Declarative continuous delivery using ArgoCD, Kustomize overlays, and Helm packaging)

---

## 🔵🟢 Phase 10: Zero-Downtime Deployment Strategy

### 1. Architectural Design

```
                     Internet / Load Balancer
                                │
                                ▼
               ┌─────────────────────────────────┐
               │  Active Service (Port 80/Node)  │
               └─────────────────────────────────┘
                     │ (Traffic Selector: version)
                     ▼
           ┌───────────────────┐
           │   version: blue   │◄── Active Production Traffic (v1.0.0)
           └───────────────────┘
                                   ┌────────────────────┐
                                   │   version: green   │◄── Preview / Staging Test (v2.0.0)
                                   └────────────────────┘
                                             ▲
                                             │
               ┌─────────────────────────────────┐
               │  Preview Service (Port 8080)    │
               └─────────────────────────────────┘
```

### 2. Deployed Components

| Manifest | Purpose | Selectors / Ports |
| :--- | :--- | :--- |
| [`kubernetes/blue-green/deployment-blue.yaml`](../kubernetes/blue-green/deployment-blue.yaml) | Production **Blue** deployment (v1.0.0, 2 replicas) | `app: weather-dashboard`, `version: blue` |
| [`kubernetes/blue-green/deployment-green.yaml`](../kubernetes/blue-green/deployment-green.yaml) | Candidate **Green** deployment (v2.0.0, 2 replicas) | `app: weather-dashboard`, `version: green` |
| [`kubernetes/blue-green/service-active.yaml`](../kubernetes/blue-green/service-active.yaml) | Active production service exposed on NodePort 30080 | Routes live traffic to active slot (`version: blue`) |
| [`kubernetes/blue-green/service-preview.yaml`](../kubernetes/blue-green/service-preview.yaml) | Preview testing service exposed on NodePort 30081 | Routes developer QA traffic to candidate slot (`version: green`) |
| [`kubernetes/canary/rollout-canary.yaml`](../kubernetes/canary/rollout-canary.yaml) | Argo Rollouts progressive canary specification | Automated 20% ➔ 50% ➔ 80% ➔ 100% traffic progression |

### 3. Step-by-Step Blue-Green Rollout & Zero-Downtime Switch

#### Step A: Deploy Blue and Active Service
```bash
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secret.example.yaml
kubectl apply -f kubernetes/persistent-volume.yaml
kubectl apply -f kubernetes/persistent-volume-claim.yaml

# Deploy initial Blue version and active routing
kubectl apply -f kubernetes/blue-green/deployment-blue.yaml
kubectl apply -f kubernetes/blue-green/service-active.yaml
```

#### Step B: Deploy Green Version and Preview Service
```bash
# Deploy Green candidate and preview service
kubectl apply -f kubernetes/blue-green/deployment-green.yaml
kubectl apply -f kubernetes/blue-green/service-preview.yaml

# Verify Green rollout status
kubectl rollout status deployment/weather-dashboard-green -n weather-dashboard
```

#### Step C: Run Automated Atomic Cutover
Run the automated switch script (Bash or PowerShell) which validates the candidate's `/health` endpoint before atomically patching the active service:

**Linux / macOS:**
```bash
chmod +x scripts/switch-blue-green.sh
./scripts/switch-blue-green.sh
```

**Windows PowerShell:**
```powershell
.\scripts\switch-blue-green.ps1
```

#### Step D: Instant Rollback (If needed)
If any anomaly is detected on the new release, instantly revert live traffic back with zero downtime:
```bash
kubectl patch service weather-dashboard-active -n weather-dashboard \
  -p '{"spec":{"selector":{"version":"blue"}}}'
```

---

## 🐙 Phase 11: GitOps Automated Delivery with ArgoCD

### 1. GitOps Architecture

```
 Git Repository (GitHub)
   ├── app/ & tests/
   ├── gitops/
   │    ├── base/
   │    └── overlays/ (staging & production)
   └── helm/weather-dashboard/
           │
           │ (Webhook / Git Polling)
           ▼
     ┌───────────┐       Continuous Reconciliation       ┌─────────────────────┐
     │  ArgoCD   │ ────────────────────────────────────► │  Kubernetes Cluster │
     │  Server   │ ◄──────────────────────────────────── │  (Live State)       │
     └───────────┘             Self-Healing              └─────────────────────┘
```

### 2. GitOps Assets

1. **ArgoCD Custom Resources:**
   - [`argocd/project.yaml`](../argocd/project.yaml): Dedicated `AppProject` with role-based policies and scoped cluster/repo permissions.
   - [`argocd/application.yaml`](../argocd/application.yaml): Production `Application` CRD with automated sync, self-healing (`selfHeal: true`), and automated namespace creation.
2. **Kustomize Structure:**
   - `gitops/base/`: Core Kubernetes primitives (Deployment, Service, ConfigMap).
   - `gitops/overlays/staging/`: Staging environment override (`staging-` prefix, 1 replica, `v2.0.0-rc1` tag).
   - `gitops/overlays/production/`: Production environment override (`prod-` prefix, 3 replicas, `v1.0.0` tag).
3. **Helm Packaging (Bonus marks):**
   - [`helm/weather-dashboard/`](../helm/weather-dashboard): Full Helm v3 chart with HorizontalPodAutoscaler (`hpa.yaml`), configurable values (`values.yaml`), and templated secrets.

### 3. Deploying ArgoCD & Synchronizing the App

```bash
# 1. Install ArgoCD inside the cluster
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 2. Wait for ArgoCD server readiness
kubectl wait --for=condition=available deployment/argocd-server -n argocd --timeout=300s

# 3. Access ArgoCD UI (Port-forward)
kubectl port-forward svc/argocd-server -n argocd 8080:443 &

# 4. Apply ArgoCD Project & Application
kubectl apply -f argocd/project.yaml
kubectl apply -f argocd/application.yaml

# 5. Check Sync Status via ArgoCD CLI
argocd app get weather-dashboard-production
argocd app sync weather-dashboard-production
```

---

## 📊 Summary of Phase 10 & 11 Deliverables

| Requirement | Implementation Artifact | Key Benefit |
| :--- | :--- | :--- |
| **Zero-Downtime Deployment** | `kubernetes/blue-green/` & `scripts/switch-blue-green.*` | Atomic traffic shift with instant rollback and pre-flight health checks. |
| **Progressive Delivery** | `kubernetes/canary/rollout-canary.yaml` | 20% ➔ 50% ➔ 80% traffic split with automatic pause steps. |
| **GitOps Delivery** | `argocd/application.yaml`, `argocd/project.yaml` | Declarative synchronization with automated self-healing and zero manual `kubectl` in production. |
| **Multi-Environment Promotion** | `gitops/overlays/{staging,production}` | Clean environment segregation using Kustomize overlays. |
| **Cloud-Native Packaging (Bonus)** | `helm/weather-dashboard/` | Reusable Helm chart with Horizontal Pod Autoscaling (HPA). |
