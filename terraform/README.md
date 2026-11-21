# Phase 6: Infrastructure as Code (IaC) with Terraform

This directory provides production-ready Infrastructure as Code (IaC) configuration for deploying the **Weather Dashboard** across both local Docker and cloud (AWS) target environments.

---

## 🏗️ Directory Architecture

```
terraform/
├── environments/
│   ├── local/                      # Local Docker deployment environment
│   │   ├── versions.tf             # Provider definitions (kreuzwerker/docker, hashicorp/local)
│   │   ├── variables.tf            # Configurable inputs & defaults
│   │   ├── terraform.tfvars        # Default parameter assignments
│   │   ├── main.tf                 # Network, volumes, image build, container resources
│   │   └── outputs.tf              # Deployed URLs, ports, container details
│   └── aws/                        # Cloud production environment (AWS ECS Fargate)
│       ├── versions.tf             # AWS provider configuration
│       ├── variables.tf            # VPC, subnets, sizing, and region parameters
│       ├── main.tf                 # VPC, Subnets, Security Groups, ALB, ECS Cluster & Service
│       └── outputs.tf              # Load balancer DNS and application endpoints
└── README.md                       # This documentation guide
```

---

## 🚀 Quickstart: Local Docker Deployment

### Prerequisites
- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.5.0 (available via Conda: `conda install -c conda-forge terraform`)
- Docker Desktop or Docker Engine running locally

### 1. Initialize Terraform
```bash
cd terraform/environments/local
terraform init
```

### 2. Validate Configuration
```bash
terraform validate
```

### 3. Review Plan
```bash
terraform plan
```

### 4. Apply Infrastructure
```bash
terraform apply -auto-approve
```

Once applied, the output will display the live local endpoints:
```text
application_url  = "http://localhost:5053"
health_check_url = "http://localhost:5053/health"
```

### 5. Tear Down / Destroy
```bash
terraform destroy -auto-approve
```

---

## ☁️ Cloud Architecture: AWS (ECS Fargate + ALB)

The `aws` environment provisions high-availability cloud infrastructure:
- **VPC & Subnets:** Multi-AZ public subnets with Internet Gateway and route tables.
- **Application Load Balancer (ALB):** Public HTTP entry point with health checks routing to `/health`.
- **Security Groups:** Defense-in-depth isolation; ECS tasks only accept connections from the ALB on port `5050`.
- **AWS ECS Fargate:** Serverless container orchestration with configurable task counts, CPU, memory, and IAM execution roles.

### Validating AWS Configuration
```bash
cd terraform/environments/aws
terraform init -backend=false
terraform validate
```

---

## 📋 Environment Variables & Input Parameters

| Variable | Default (Local) | Description |
| :--- | :--- | :--- |
| `app_name` | `weather-dashboard` | Base name for resources |
| `environment` | `local` | Environment identifier |
| `container_image_tag` | `terraform-v1` | Image tag generated from build |
| `host_port` | `5053` | Host port mapped to container port 5050 |
| `container_port` | `5050` | Port container listens on |
| `restart_policy` | `unless-stopped` | Docker container restart policy |
