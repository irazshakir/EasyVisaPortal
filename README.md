# Easy Visa Portal - Complete Architecture

## 🏗️ **Project Overview**
A comprehensive visa application portal with AI-powered document generation and WhatsApp bot integration.

## 📁 **Folder Structure**

```
EVisaPortal/
├── 📁 frontend/                          # React TypeScript Frontend
│   ├── 📁 public/
│   ├── 📁 src/
│   │   ├── 📁 components/
│   │   │   ├── 📁 common/
│   │   │   ├── 📁 dashboard/
│   │   │   ├── 📁 chatbot/
│   │   │   └── 📁 forms/
│   │   ├── 📁 pages/
│   │   ├── 📁 services/
│   │   ├── 📁 hooks/
│   │   ├── 📁 utils/
│   │   ├── 📁 types/
│   │   └── 📁 assets/
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── 📁 backend/                           # Django DRF Backend
│   ├── 📁 visa_portal/
│   │   ├── 📁 apps/
│   │   │   ├── 📁 users/
│   │   │   ├── 📁 applications/
│   │   │   ├── 📁 documents/
│   │   │   ├── 📁 payments/
│   │   │   └── 📁 notifications/
│   │   ├── 📁 core/
│   │   ├── 📁 config/
│   │   ├── 📁 templates/
│   │   └── 📁 static/
│   ├── 📁 requirements/
│   │   ├── base.txt
│   │   ├── development.txt
│   │   └── production.txt
│   ├── manage.py
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── 📁 bots/                              # FastAPI Bot Services
│   ├── 📁 visa_evaluation_bot/          # Visa Eligibility Bot
│   │   ├── 📁 app/
│   │   │   ├── 📁 api/
│   │   │   ├── 📁 core/
│   │   │   ├── 📁 models/
│   │   │   ├── 📁 services/
│   │   │   │   ├── 📁 evaluation/
│   │   │   │   ├── 📁 whatsapp/
│   │   │   │   └── 📁 webhook/
│   │   │   └── 📁 utils/
│   │   ├── 📁 prompts/
│   │   │   ├── evaluation_prompts.py
│   │   │   └── qualification_stages.py
│   │   ├── 📁 tests/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── 📁 document_preparation_bot/      # Document Generation Bot
│       ├── 📁 app/
│       │   ├── 📁 api/
│       │   ├── 📁 core/
│       │   ├── 📁 models/
│       │   ├── 📁 services/
│       │   │   ├── 📁 document_generation/
│       │   │   ├── 📁 llm_integration/
│       │   │   └── 📁 file_processing/
│       │   └── 📁 utils/
│       ├── 📁 prompts/
│       │   ├── cover_letter_prompts.py
│       │   ├── financial_report_prompts.py
│       │   └── business_profile_prompts.py
│       ├── 📁 templates/
│       ├── 📁 tests/
│       ├── main.py
│       ├── requirements.txt
│       └── Dockerfile
│
├── 📁 infrastructure/                    # Infrastructure & DevOps
│   ├── 📁 kubernetes/
│   │   ├── 📁 namespaces/
│   │   ├── 📁 deployments/
│   │   ├── 📁 services/
│   │   ├── 📁 ingress/
│   │   ├── 📁 configmaps/
│   │   ├── 📁 secrets/
│   │   └── 📁 persistent-volumes/
│   │
│   ├── 📁 docker/
│   │   ├── docker-compose.dev.yml
│   │   ├── docker-compose.prod.yml
│   │   └── 📁 nginx/
│   │
│   ├── 📁 ci-cd/
│   │   ├── 📁 github-actions/
│   │   │   ├── frontend-ci.yml
│   │   │   ├── backend-ci.yml
│   │   │   ├── bots-ci.yml
│   │   │   └── deploy.yml
│   │   └── 📁 scripts/
│   │
│   └── 📁 monitoring/
│       ├── prometheus.yml
│       ├── grafana-dashboards/
│       └── alertmanager.yml
│
├── 📁 docs/                              # Documentation
│   ├── 📁 api/
│   ├── 📁 deployment/
│   └── 📁 architecture/
│
└── 📁 scripts/                           # Utility Scripts
    ├── setup.sh
    ├── deploy.sh
    └── backup.sh
```

## 🛠️ **Technology Stack**

### **Frontend (React TypeScript)**
- **Framework**: React 18 + TypeScript
- **UI Library**: ECME React Theme (TypeScript compatible)
- **Styling**: Tailwind CSS
- **State Management**: Redux Toolkit + RTK Query
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Real-time**: Socket.io Client
- **Form Handling**: React Hook Form + Zod
- **UI Components**: Headless UI + Radix UI

### **Backend (Django DRF)**
- **Framework**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (djangorestframework-simplejwt)
- **File Storage**: MinIO/AWS S3
- **Caching**: Redis
- **Task Queue**: Celery + Redis
- **API Documentation**: drf-spectacular
- **Validation**: Django Validators + Pydantic

### **Bot Services (FastAPI)**
- **Framework**: FastAPI + Pydantic
- **AI/LLM**: LangChain + OpenAI/Anthropic
- **WhatsApp Integration**: Meta WhatsApp Business API
- **Message Queue**: Redis + Celery
- **Document Processing**: PyPDF2, python-docx
- **Async Processing**: asyncio + aiofiles

### **Infrastructure**
- **Containerization**: Docker + Docker Compose
- **Orchestration**: Kubernetes
- **Cloud Platform**: Azure (AKS) or GCP (GKE)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **API Gateway**: Kong/Ambassador

## 🏛️ **System Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  React TypeScript Portal  │  WhatsApp Bot  │  Mobile App (Future)│
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                     API GATEWAY LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  Kong/Ambassador API Gateway  │  Rate Limiting │  Authentication│
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                    MICROSERVICES LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│ Django DRF Backend │ Visa Evaluation Bot │ Document Prep Bot   │
│ (User Management)  │ (FastAPI)          │ (FastAPI)           │
│ (Applications)     │ (WhatsApp/Web)     │ (LLM Integration)   │
│ (Documents)        │ (Eligibility)      │ (Report Generation) │
│ (Payments)         │ (Staged Process)   │ (File Processing)   │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                     DATA LAYER                                  │
├─────────────────────────────────────────────────────────────────┤
│ PostgreSQL │ Redis │ MinIO/S3 │ Elasticsearch │ RabbitMQ        │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 **Service Communication Flow**

### **1. Visa Evaluation Flow**
```
User (WhatsApp/Web) → API Gateway → Visa Evaluation Bot → 
LLM Service → Database → Response to User
```

### **2. Document Preparation Flow**
```
User (Portal) → Django Backend → Document Prep Bot → 
LLM Service → File Storage → Portal Dashboard
```

### **3. Application Management Flow**
```
User (Portal) → Django Backend → Database → 
File Storage → Notifications → User Dashboard
```

## 🐳 **Docker Configuration**

### **Frontend Dockerfile**
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
```

### **Django Backend Dockerfile**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements/ requirements/
RUN pip install -r requirements/production.txt
COPY . .
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### **FastAPI Bot Dockerfile**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## ☸️ **Kubernetes Configuration**

### **Namespace Structure**
```yaml
# namespaces/visa-portal.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: visa-portal
  labels:
    name: visa-portal
```

### **Frontend Deployment**
```yaml
# deployments/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: visa-portal
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: visa-portal/frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```

### **Django Backend Deployment**
```yaml
# deployments/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: visa-portal
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: visa-portal/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: database-url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: redis-url
```

### **Bot Services Deployment**
```yaml
# deployments/bots-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: visa-evaluation-bot
  namespace: visa-portal
spec:
  replicas: 2
  selector:
    matchLabels:
      app: visa-evaluation-bot
  template:
    metadata:
      labels:
        app: visa-evaluation-bot
    spec:
      containers:
      - name: visa-evaluation-bot
        image: visa-portal/visa-evaluation-bot:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-secrets
              key: openai-api-key
        - name: WHATSAPP_TOKEN
          valueFrom:
            secretKeyRef:
              name: whatsapp-secrets
              key: whatsapp-token
```

## 🔄 **CI/CD Pipeline**

### **GitHub Actions Workflow**
```yaml
# .github/workflows/main.yml
name: Visa Portal CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: cd frontend && npm ci
      - name: Run tests
        run: cd frontend && npm test
      - name: Build
        run: cd frontend && npm run build

  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements/development.txt
      - name: Run tests
        run: cd backend && python manage.py test

  test-bots:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Test Visa Evaluation Bot
        run: |
          cd bots/visa_evaluation_bot
          pip install -r requirements.txt
          pytest
      - name: Test Document Preparation Bot
        run: |
          cd bots/document_preparation_bot
          pip install -r requirements.txt
          pytest

  build-and-push:
    needs: [test-frontend, test-backend, test-bots]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Build and push Docker images
        run: |
          docker build -t visa-portal/frontend:latest ./frontend
          docker build -t visa-portal/backend:latest ./backend
          docker build -t visa-portal/visa-evaluation-bot:latest ./bots/visa_evaluation_bot
          docker build -t visa-portal/document-preparation-bot:latest ./bots/document_preparation_bot
          # Push to container registry

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f infrastructure/kubernetes/
```

## 📊 **Monitoring & Observability**

### **Prometheus Configuration**
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'frontend'
    static_configs:
      - targets: ['frontend:80']

  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']

  - job_name: 'visa-evaluation-bot'
    static_configs:
      - targets: ['visa-evaluation-bot:8000']

  - job_name: 'document-preparation-bot'
    static_configs:
      - targets: ['document-preparation-bot:8000']
```

### **Grafana Dashboards**
- Application performance metrics
- Bot conversation analytics
- User engagement metrics
- System resource utilization

## 🔐 **Security Configuration**

### **Secrets Management**
```yaml
# kubernetes/secrets/database-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
  namespace: visa-portal
type: Opaque
data:
  database-url: <base64-encoded-database-url>
  redis-url: <base64-encoded-redis-url>

---
# kubernetes/secrets/ai-secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: ai-secrets
  namespace: visa-portal
type: Opaque
data:
  openai-api-key: <base64-encoded-openai-key>
  anthropic-api-key: <base64-encoded-anthropic-key>
```

## 🚀 **Deployment Strategy**

### **Azure Deployment (Recommended)**
1. **Azure Container Registry (ACR)**
2. **Azure Kubernetes Service (AKS)**
3. **Azure Database for PostgreSQL**
4. **Azure Redis Cache**
5. **Azure Storage Account (for files)**
6. **Azure Application Insights (monitoring)**

### **GCP Deployment (Alternative)**
1. **Google Container Registry (GCR)**
2. **Google Kubernetes Engine (GKE)**
3. **Cloud SQL for PostgreSQL**
4. **Cloud Memorystore for Redis**
5. **Cloud Storage (for files)**
6. **Cloud Monitoring**

## 💰 **Cost Optimization**

### **Azure Cost Optimization**
- Use Azure Spot Instances for non-critical workloads
- Azure Reserved Instances for predictable workloads
- Auto-scaling based on demand
- Azure Hybrid Benefit for licensing

### **GCP Cost Optimization**
- Use Preemptible VMs for batch processing
- Committed Use Discounts
- Sustained Use Discounts
- Auto-scaling with Cloud Run

## 📋 **Next Steps**

1. **Set up development environment**
2. **Initialize Git repository with proper branching strategy**
3. **Create base Docker configurations**
4. **Set up CI/CD pipelines**
5. **Configure cloud infrastructure**
6. **Implement core services**
7. **Add monitoring and logging**
8. **Security hardening**
9. **Performance testing**
10. **Production deployment**

This architecture provides a scalable, maintainable, and cost-effective solution for your Easy Visa Portal with all the features you requested! 