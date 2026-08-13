# 🚀 Task Manager REST API & Production CI/CD Pipeline

[![CI/CD Pipeline](https://github.com/your-username/task-manager-api/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/your-username/task-manager-api/actions/workflows/ci-cd.yml)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)
![Docker](https://img.shields.io/badge/Docker-Multi--Stage-2496ED.svg)
![Terraform](https://img.shields.io/badge/Terraform-IaC-7B42BC.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A production-grade **Task Manager REST API** built with Python and **FastAPI** using strict **Object-Oriented Programming (OOP)**, the **Repository Pattern**, **Prometheus Metrics**, **Pytest**, **Multi-stage Dockerization**, **Terraform Infrastructure as Code (AWS ECR + ECS Fargate)**, and an automated **GitHub Actions CI/CD Pipeline**.

---

## 🌐 Live Application Deployment

- **Live Public URL:** `https://task-manager-api-cloud.onrender.com`
- **Interactive Swagger Documentation:** `https://task-manager-api-cloud.onrender.com/docs`
- **Health Check Endpoint:** `https://task-manager-api-cloud.onrender.com/health`
- **Prometheus Metrics:** `https://task-manager-api-cloud.onrender.com/metrics`

---

## 🏗 System Architecture

The following diagram illustrates the end-to-end architecture, developer workflow, CI/CD automation, and cloud deployment topology:

```mermaid
graph TD
    subgraph Developer Workspace
        DEV[Developer Push to main]
    end

    subgraph CI/CD Automation (GitHub Actions)
        GA[GitHub Actions Runner]
        LINT[1. Lint & Format check<br/>flake8 / black]
        TEST[2. Automated Unit & Integration Tests<br/>pytest --cov]
        BUILD[3. Build Multi-Stage Docker Image]
        PUSH[4. Push Image to Registry<br/>GHCR / AWS ECR]
        DEPLOY_STEP[5. Trigger Automated Cloud Deployment]
    end

    subgraph Cloud Infrastructure (AWS / Free Hosting)
        REGISTRY[Container Registry<br/>ghcr.io / AWS ECR]
        ECS[AWS ECS Fargate Service / Render Web App]
        HEALTH[Automated Health Verification<br/>/health endpoint]
    end

    subgraph Application Architecture
        API[FastAPI Application<br/>uvicorn server]
        METRICS[Prometheus Metrics Engine<br/>/metrics]
        SERVICE[TaskManager Service Layer]
        REPO[Repository Layer<br/>SQLite / In-Memory]
    end

    DEV --> GA
    GA --> LINT
    LINT --> TEST
    TEST --> BUILD
    BUILD --> PUSH
    PUSH --> REGISTRY
    PUSH --> DEPLOY_STEP
    DEPLOY_STEP --> ECS
    ECS --> API
    API --> HEALTH
    API --> METRICS
    API --> SERVICE
    SERVICE --> REPO
```

---

## ✨ Features & Architecture Design

1. **Object-Oriented Architecture (OOP):**
   - **`Task` Domain Class:** Encapsulates state, business validation, priority controls, and audit timestamps.
   - **`TaskManager` Service Class:** Encapsulates CRUD business logic decoupled from HTTP frameworks.
   - **Repository Pattern:** Abstract `BaseTaskRepository` interface with interchangeable implementations:
     - `InMemoryTaskRepository` (Thread-safe dict with Lock)
     - `SQLiteTaskRepository` (Class-based SQLite persistence)
   - **Custom Exceptions:** Domain exceptions (`TaskNotFoundError`, `TaskValidationError`, `DuplicateTaskError`, `RepositoryError`) mapped cleanly to HTTP status codes.

2. **Testing & Coverage:**
   - Unit tests covering domain models, repositories, and service logic.
   - Integration tests covering FastAPI endpoints and HTTP responses.
   - Test suite achieving 90%+ code coverage verified via `pytest-cov`.

3. **Multi-Stage Dockerization:**
   - Layer-cached multi-stage Docker build producing lightweight runtime images (<150MB).
   - Security-hardened execution running under a non-root user (`appuser`).
   - Integrated Docker `HEALTHCHECK` instructions.

4. **Monitoring & Telemetry:**
   - Prometheus metrics endpoint (`/metrics`) exposing total request counters, latency histograms, active connections gauge, and task count gauges.

5. **Infrastructure as Code (Terraform):**
   - Complete Terraform scripts to provision Amazon ECR repository, IAM execution/task roles, CloudWatch log groups, security groups, and ECS Fargate cluster + service.
   - Cardless free-tier deployment blueprint (`render.yaml`).

6. **Linux Bash Automation:**
   - `scripts/deploy.sh`: Zero-downtime manual deployment and instant container rollback script.
   - `scripts/health_check.sh`: Health check script with retries and JSON body verification.

---

## 📁 Repository Structure

```
.
├── .github/
│   └── workflows/
│       └── ci-cd.yml             # GitHub Actions CI/CD Pipeline
├── app/
│   ├── api/
│   │   ├── dependencies.py       # FastAPI Dependency Injection
│   │   └── routes.py             # REST API Task Endpoints
│   ├── models/
│   ├── task.py               # Domain Model & Pydantic DTOs
│   ├── repositories/
│   │   ├── base.py               # Abstract Base Repository
│   │   ├── in_memory.py          # Thread-Safe In-Memory Repository
│   │   └── sqlite.py             # Class-Based SQLite Repository
│   ├── services/
│   │   └── task_manager.py       # CRUD TaskManager Service
│   ├── config.py                 # Application Configuration
│   ├── exceptions.py             # Custom Application Exceptions
│   ├── main.py                   # FastAPI Application Entrypoint
│   └── metrics.py                # Prometheus Telemetry Setup
├── scripts/
│   ├── deploy.sh                 # Linux Bash Deployment & Rollback Script
│   └── health_check.sh           # Linux Bash Health Verification Script
├── terraform/
│   ├── main.tf                   # AWS ECR, ECS Fargate & IAM Terraform IaC
│   ├── variables.tf              # Terraform Input Variables
│   └── outputs.tf                # Terraform Outputs
├── tests/
│   ├── conftest.py               # Pytest Fixtures
│   ├── test_api.py               # Integration API Tests
│   ├── test_models.py            # Domain Model Unit Tests
│   ├── test_repositories.py      # Repository Unit Tests
│   └── test_task_manager.py      # TaskManager Unit Tests
├── .dockerignore
├── .flake8
├── docker-compose.yml            # Local Multi-Container Development Setup
├── Dockerfile                    # Multi-Stage Production Dockerfile
├── pyproject.toml                # Black & Pytest Configuration
├── render.yaml                   # Free Cloud Deployment Specification
├── requirements.txt              # Production Dependencies
├── requirements-dev.txt          # Development & Test Dependencies
└── README.md                     # Documentation
```

---

## 🛠 Local Setup & Running

### Option 1: Python Virtual Environment

```bash
# 1. Clone Repository
git clone https://github.com/your-username/task-manager-api.git
cd task-manager-api

# 2. Create and Activate Virtual Environment
python3 -m venv venv
source venv/bin/activate

# 3. Install Dependencies
pip install -r requirements-dev.txt

# 4. Run Pytest Suite
pytest

# 5. Start Uvicorn Server
python -m uvicorn app.main:app --reload --port 8000
```
Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.

---

### Option 2: Docker Compose (Local Dev with Postgres)

```bash
# Build and start all services (API + Postgres database)
docker-compose up --build -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

---

## 🚀 Linux Bash Automation Scripts

Make sure executable permissions are granted:
```bash
chmod +x scripts/deploy.sh scripts/health_check.sh
```

### 1. Deployment & Rollback (`scripts/deploy.sh`)

```bash
# Build, start container, and run post-deploy health check
./scripts/deploy.sh --deploy

# Check running container status and health
./scripts/deploy.sh --status

# Rollback to previous container image in case of failure
./scripts/deploy.sh --rollback
```

### 2. Health Verification (`scripts/health_check.sh`)

```bash
# Test local endpoint
./scripts/health_check.sh "http://localhost:8000"

# Test remote deployment URL
./scripts/health_check.sh "https://task-manager-api-cloud.onrender.com"
```

---

## ☁️ Infrastructure as Code (Terraform)

Provision AWS Infrastructure (ECR Repository, IAM Roles, CloudWatch, ECS Fargate):

```bash
cd terraform

# 1. Initialize Terraform
terraform init

# 2. Plan Provisioning
terraform plan

# 3. Apply Resources
terraform apply -auto-approve
```

---

## 🔌 REST API Endpoints Reference

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Application & DB Health Check | `200 OK` |
| `GET` | `/metrics` | Prometheus Metrics Payload | `200 OK` |
| `GET` | `/tasks` | List Tasks (supports `completed`, `limit`, `offset`) | `200 OK` |
| `POST` | `/tasks` | Create New Task | `201 Created` |
| `GET` | `/tasks/{id}` | Retrieve Task by ID | `200 OK` / `404 Not Found` |
| `PUT` | `/tasks/{id}` | Update Task details | `200 OK` / `404 Not Found` |
| `DELETE` | `/tasks/{id}` | Delete Task by ID | `204 No Content` / `404 Not Found` |

---

## 📄 License

This project is open-source under the [MIT License](LICENSE).
