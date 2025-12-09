# Deployment Guide

This document provides step-by-step instructions for deploying the robotics learning platform to production environments.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Local Testing](#local-testing)
3. [Cloud Deployment](#cloud-deployment)
4. [Docker Registry](#docker-registry)
5. [Database Setup](#database-setup)
6. [Environment Variables](#environment-variables)
7. [Health Checks](#health-checks)
8. [Monitoring](#monitoring)
9. [Scaling](#scaling)
10. [Rollback](#rollback)
11. [Troubleshooting](#troubleshooting)

## Pre-Deployment Checklist

### Code Quality
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Code coverage >= 85%: `pytest --cov=src --cov-report=term`
- [ ] No linting errors: `flake8 backend/src`
- [ ] Type checks pass: `mypy backend/src`
- [ ] No security vulnerabilities: `trivy image robotics-platform:vX.X.X`

### Configuration
- [ ] All environment variables defined
- [ ] Database connection tested
- [ ] API keys and secrets secured
- [ ] SSL certificates obtained (if using HTTPS)
- [ ] Backup strategy defined
- [ ] Disaster recovery plan prepared

### Documentation
- [ ] Deployment guide reviewed
- [ ] Runbooks prepared
- [ ] Team trained on procedures
- [ ] Incident response plan documented

### Infrastructure
- [ ] Server capacity adequate
- [ ] Network configured
- [ ] Firewalls configured
- [ ] CDN configured (if applicable)
- [ ] Monitoring tools installed
- [ ] Logging aggregation configured

## Local Testing

### 1. Build Production Image

```bash
# Build with version tag
docker build --target production \
  -t robotics-platform:v1.0.0 \
  -t robotics-platform:latest \
  .

# Verify image size
docker images | grep robotics-platform
```

Expected output:
```
robotics-platform   v1.0.0    abc123def456    600MB
robotics-platform   latest    abc123def456    600MB
```

### 2. Scan for Vulnerabilities

```bash
# Install trivy (if not present)
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Scan image
trivy image robotics-platform:v1.0.0

# Scan with severity filter
trivy image --severity HIGH,CRITICAL robotics-platform:v1.0.0
```

### 3. Test Image Locally

```bash
# Create test environment file
cat > .env.test << EOF
DATABASE_URL=postgresql+asyncpg://robotics_user:robotics_password@postgres:5432/robotics_db
QDRANT_URL=http://qdrant:6333
QDRANT_API_KEY=test-key
OPENAI_API_KEY=sk-test
SECRET_KEY=test-secret-key-change-in-production
EOF

# Start PostgreSQL for testing
docker run -d --name test_postgres \
  -e POSTGRES_USER=robotics_user \
  -e POSTGRES_PASSWORD=robotics_password \
  -e POSTGRES_DB=robotics_db \
  postgres:16-alpine

# Start Qdrant for testing
docker run -d --name test_qdrant \
  -p 6333:6333 \
  qdrant/qdrant

# Test the application
docker run -p 8000:8000 \
  --env-file .env.test \
  --link test_postgres:postgres \
  --link test_qdrant:qdrant \
  robotics-platform:v1.0.0

# Health check
curl http://localhost:8000/health

# Cleanup
docker stop test_postgres test_qdrant robotics_test
docker rm test_postgres test_qdrant robotics_test
```

## Cloud Deployment

### Option 1: AWS Deployment

#### Using Elastic Container Service (ECS)

1. **Push Image to ECR**

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag robotics-platform:v1.0.0 123456789.dkr.ecr.us-east-1.amazonaws.com/robotics-platform:v1.0.0
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/robotics-platform:v1.0.0
```

2. **Create ECS Task Definition**

```json
{
  "family": "robotics-platform",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/robotics-platform:v1.0.0",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        },
        {
          "name": "LOG_LEVEL",
          "value": "info"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:robotics-db-url"
        },
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:openai-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/robotics-platform",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

3. **Create ECS Service**

```bash
aws ecs create-service \
  --cluster robotics-cluster \
  --service-name robotics-service \
  --task-definition robotics-platform:1 \
  --desired-count 3 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### Option 2: DigitalOcean App Platform

```yaml
name: robotics-platform
services:
  - name: backend
    github:
      branch: main
      deploy_on_push: true
      repo: your-org/robotics-platform
    build_command: docker build -t robotics-platform:latest .
    docker:
      dockerfile_path: Dockerfile
    http_port: 8000
    health_check:
      http_path: /health
    envs:
      - key: ENVIRONMENT
        value: production
        scope: RUN_TIME
      - key: DATABASE_URL
        value: ${db.connection_string}
    resources:
      requests:
        memory: 512Mi
        cpu: 250m

  - name: postgres
    engine: MYSQL
    version: "16"
    production: true
    envs:
      - key: POSTGRES_DB
        value: robotics_db

  - name: qdrant
    image:
      registry: docker.io
      registry_type: DOCKER_HUB
      repository: qdrant/qdrant
      tag: latest
```

### Option 3: Kubernetes Deployment

1. **Build and Push Image**

```bash
docker build -t your-registry/robotics-platform:v1.0.0 .
docker push your-registry/robotics-platform:v1.0.0
```

2. **Create Kubernetes Manifests**

```yaml
---
apiVersion: v1
kind: Namespace
metadata:
  name: robotics

---
apiVersion: v1
kind: Secret
metadata:
  name: robotics-secrets
  namespace: robotics
type: Opaque
stringData:
  DATABASE_URL: postgresql+asyncpg://user:pass@postgres:5432/robotics_db
  OPENAI_API_KEY: sk-...
  SECRET_KEY: your-secret-key

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: robotics-backend
  namespace: robotics
spec:
  replicas: 3
  selector:
    matchLabels:
      app: robotics-backend
  template:
    metadata:
      labels:
        app: robotics-backend
    spec:
      containers:
      - name: backend
        image: your-registry/robotics-platform:v1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: production
        envFrom:
        - secretRef:
            name: robotics-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 40
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 20
          periodSeconds: 10

---
apiVersion: v1
kind: Service
metadata:
  name: robotics-backend
  namespace: robotics
spec:
  type: LoadBalancer
  selector:
    app: robotics-backend
  ports:
  - port: 80
    targetPort: 8000
```

3. **Deploy to Kubernetes**

```bash
# Create namespace and secrets
kubectl create namespace robotics
kubectl create secret generic robotics-secrets -n robotics \
  --from-literal=DATABASE_URL="..." \
  --from-literal=OPENAI_API_KEY="..."

# Deploy
kubectl apply -f deployment.yaml

# Verify
kubectl get pods -n robotics
kubectl logs -n robotics robotics-backend-xxxxx
```

## Docker Registry

### Push to Docker Hub

```bash
# Login
docker login

# Tag
docker tag robotics-platform:v1.0.0 your-username/robotics-platform:v1.0.0

# Push
docker push your-username/robotics-platform:v1.0.0

# Verify
curl https://hub.docker.com/v2/repositories/your-username/robotics-platform/tags/
```

### Push to GitHub Container Registry

```bash
# Login
echo $GH_TOKEN | docker login ghcr.io -u your-username --password-stdin

# Tag
docker tag robotics-platform:v1.0.0 ghcr.io/your-username/robotics-platform:v1.0.0

# Push
docker push ghcr.io/your-username/robotics-platform:v1.0.0
```

### Private Registry

```bash
# Login
docker login your-registry.com

# Tag
docker tag robotics-platform:v1.0.0 your-registry.com/robotics-platform:v1.0.0

# Push
docker push your-registry.com/robotics-platform:v1.0.0

# Use in docker-compose
image: your-registry.com/robotics-platform:v1.0.0
```

## Database Setup

### Create Production Database

```bash
# Connect to PostgreSQL server
psql -h your-server.com -U postgres

# Create user
CREATE ROLE robotics_user WITH LOGIN PASSWORD 'strong-password';
ALTER ROLE robotics_user CREATEDB;

# Create database
CREATE DATABASE robotics_db OWNER robotics_user;

# Grant privileges
GRANT CONNECT ON DATABASE robotics_db TO robotics_user;
GRANT USAGE ON SCHEMA public TO robotics_user;
GRANT CREATE ON SCHEMA public TO robotics_user;

# Connect to new database
\c robotics_db

# Run migrations
alembic upgrade head
```

### Seed Initial Data (Optional)

```bash
# Run seed script
python backend/scripts/seed_data.py

# Verify
psql -h your-server.com -U robotics_user -d robotics_db -c "SELECT COUNT(*) FROM public.user;"
```

## Environment Variables

### Production Environment Template

```bash
# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info
SECRET_KEY=your-very-secure-random-key-here

# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/robotics_db
POSTGRES_USER=robotics_user
POSTGRES_PASSWORD=your-secure-password

# Qdrant Vector Store
QDRANT_URL=https://your-qdrant-instance.com:6333
QDRANT_API_KEY=your-qdrant-api-key

# OpenAI
OPENAI_API_KEY=sk-your-openai-key

# CORS
ALLOWED_ORIGINS=https://example.com,https://www.example.com

# Features
ENABLE_ANALYTICS=true
ENABLE_CODE_SANDBOX=false
```

### Generate Secret Key

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -base64 32

# Using pwgen
pwgen -s 32 1
```

## Health Checks

### Endpoint Tests

```bash
# Health check
curl -s https://api.example.com/health | jq .

# Authentication
curl -X POST https://api.example.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'

# Chat endpoint
curl -X POST https://api.example.com/api/chat/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"test","mode":"learn"}'
```

### Automated Health Checks

```bash
#!/bin/bash
# health-check.sh

HEALTH_URL="https://api.example.com/health"
MAX_RETRIES=5
RETRY_DELAY=10

for i in $(seq 1 $MAX_RETRIES); do
  response=$(curl -s -w "\n%{http_code}" "$HEALTH_URL")
  status=$(echo "$response" | tail -n1)

  if [ "$status" == "200" ]; then
    echo "Health check passed"
    exit 0
  fi

  echo "Health check failed (attempt $i/$MAX_RETRIES)"
  sleep $RETRY_DELAY
done

echo "Health check failed after $MAX_RETRIES attempts"
exit 1
```

## Monitoring

### Application Metrics

Install monitoring tools:

```bash
# Prometheus scrape config
scrape_configs:
  - job_name: 'robotics-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'

# Grafana dashboard
# Import dashboard ID: 12345 (FastAPI dashboard)
```

### Log Aggregation

```bash
# ELK Stack
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/robotics/*.log

# Datadog
datadog:
  logs:
    - service: robotics-backend
      source: python
      path: /var/log/robotics/*.log
```

## Scaling

### Horizontal Scaling

```bash
# AWS Auto Scaling
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name robotics-asg \
  --launch-configuration robotics-lc \
  --min-size 3 \
  --max-size 10 \
  --desired-capacity 3

# Kubernetes
kubectl autoscale deployment robotics-backend \
  --min=3 \
  --max=10 \
  --cpu-percent=80
```

### Vertical Scaling

Edit docker-compose.prod.yml:

```yaml
backend:
  mem_limit: 2g      # Increase from 1g
  cpus: 2            # Increase from 1
```

## Rollback

### Rollback Procedure

1. **Identify Previous Version**

```bash
# Docker Hub
docker images | grep robotics-platform
docker pull your-registry/robotics-platform:v1.0.0

# Kubernetes
kubectl rollout history deployment/robotics-backend -n robotics
kubectl rollout undo deployment/robotics-backend -n robotics --to-revision=2
```

2. **Stop Current Services**

```bash
# Docker Compose
docker-compose down

# ECS
aws ecs update-service \
  --cluster robotics-cluster \
  --service robotics-service \
  --task-definition robotics-platform:1 \
  --force-new-deployment
```

3. **Verify Rollback**

```bash
# Check health
curl https://api.example.com/health

# Check logs
docker-compose logs -f backend

# Run tests
pytest tests/ --tb=short
```

## Troubleshooting

### Service won't start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Verify configuration
docker-compose config

# Check environment variables
docker-compose -f docker-compose.prod.yml exec backend env | grep DATABASE_URL
```

### Database connection issues

```bash
# Test connection
psql postgresql://user:pass@host:5432/robotics_db -c "SELECT 1"

# Check network
telnet database-host 5432

# Review connection string
echo $DATABASE_URL
```

### Out of memory

```bash
# Check usage
docker stats

# Review memory limits
docker-compose config | grep -A 5 mem_limit

# Increase limits and restart
# Edit docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml up -d
```

### Performance degradation

```bash
# Check slow queries
psql -c "SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Monitor metrics
docker stats
docker top container-name

# Check log levels
# Reduce to WARNING or ERROR
docker-compose -f docker-compose.prod.yml down
# Edit ENVIRONMENT/LOG_LEVEL
docker-compose -f docker-compose.prod.yml up -d
```

## Support

For issues or questions:

1. Check logs: `docker-compose logs -f`
2. Review documentation: `/docs`, `/api/docs`
3. Check health: `curl /health`
4. Contact team: @robotics-team

## References

- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Production Deployment](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL Administration](https://www.postgresql.org/docs/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
