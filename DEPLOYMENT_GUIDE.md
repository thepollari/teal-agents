# Teal Agents Framework - Production Deployment Guide

## Overview

This guide covers production deployment strategies for the Teal Agents Framework, including containerization, orchestration, environment management, and scaling patterns. The framework supports multiple deployment architectures from single-node setups to distributed microservice deployments.

## Architecture Overview

### Deployment Components

The Teal Agents Framework consists of several deployable components:

```
Production Deployment Architecture
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer / Ingress                  │
├─────────────────────────────────────────────────────────────┤
│  API Gateway (Kong)                                         │
├─────────────────────────────────────────────────────────────┤
│  Core Services:                                             │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │  Teal Agents    │ │ Assistant       │ │ Collaboration   ││
│  │  (sk-agents)    │ │ Orchestrator    │ │ Orchestrator    ││
│  │                 │ │ (AO)            │ │ (CO)            ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
│  ┌─────────────────┐                                        │
│  │ AO Services     │                                        │
│  │ (Agent Catalog) │                                        │
│  └─────────────────┘                                        │
├─────────────────────────────────────────────────────────────┤
│  Supporting Services:                                       │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │     Redis       │ │   DynamoDB      │ │   PostgreSQL    ││
│  │   (State)       │ │  (Sessions)     │ │  (Metadata)     ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Container Images

### Available Images

The framework provides pre-built Docker images via GitHub Container Registry:

| Component | Image | Purpose |
|-----------|-------|---------|
| Core Framework | `ghcr.io/teal-agents/teal-agents:latest` | Agent execution engine |
| Assistant Orchestrator | `ghcr.io/teal-agents/ao:latest` | Chat-style orchestration |
| AO Services | `ghcr.io/teal-agents/ao-services:latest` | Agent catalog and routing |
| Collaboration Orchestrator | `ghcr.io/teal-agents/co:latest` | Multi-agent collaboration |

### Image Versioning

- **Latest**: `latest` tag for most recent stable build
- **Versioned**: Semantic versioning tags (e.g., `v1.2.3`)
- **Development**: Development builds with `.dev` suffix

### Custom Image Building

```bash
# Build all images locally
make all

# Build specific components
make teal-agents    # Core framework
make orchestrator   # AO and CO
make services       # AO services
```

## Deployment Strategies

### 1. Single-Node Deployment

**Use Case**: Development, testing, small-scale production

**Architecture**: All components on single host with Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  teal-agents:
    image: ghcr.io/teal-agents/teal-agents:latest
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    
  assistant-orchestrator:
    image: ghcr.io/teal-agents/ao:latest
    ports:
      - "8001:8000"
    environment:
      - TA_API_KEY=${TA_API_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
      - ao-services
    
  ao-services:
    image: ghcr.io/teal-agents/ao-services:latest
    ports:
      - "8002:8000"
    environment:
      - DYNAMODB_ENDPOINT=http://dynamodb:8000
    depends_on:
      - dynamodb
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    
  dynamodb:
    image: amazon/dynamodb-local
    ports:
      - "8003:8000"
    volumes:
      - dynamodb_data:/home/dynamodblocal/data

volumes:
  redis_data:
  dynamodb_data:
```

**Deployment Commands:**
```bash
# Deploy single-node setup
docker-compose -f docker-compose.prod.yml up -d

# Scale specific services
docker-compose -f docker-compose.prod.yml up -d --scale teal-agents=3
```

### 2. Kubernetes Deployment

**Use Case**: Production, high availability, auto-scaling

**Prerequisites:**
- Kubernetes cluster (1.20+)
- kubectl configured
- Ingress controller (nginx, traefik)
- Persistent storage provider

#### Namespace Setup

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: teal-agents
```

#### ConfigMap for Environment Variables

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: teal-agents-config
  namespace: teal-agents
data:
  REDIS_URL: "redis://redis-service:6379"
  DYNAMODB_ENDPOINT: "http://dynamodb-service:8000"
  LOG_LEVEL: "INFO"
```

#### Secret Management

```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: teal-agents-secrets
  namespace: teal-agents
type: Opaque
data:
  OPENAI_API_KEY: <base64-encoded-key>
  ANTHROPIC_API_KEY: <base64-encoded-key>
  TA_API_KEY: <base64-encoded-key>
```

#### Core Framework Deployment

```yaml
# teal-agents-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: teal-agents
  namespace: teal-agents
spec:
  replicas: 3
  selector:
    matchLabels:
      app: teal-agents
  template:
    metadata:
      labels:
        app: teal-agents
    spec:
      containers:
      - name: teal-agents
        image: ghcr.io/teal-agents/teal-agents:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: teal-agents-config
              key: REDIS_URL
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: teal-agents-secrets
              key: OPENAI_API_KEY
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
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: teal-agents-service
  namespace: teal-agents
spec:
  selector:
    app: teal-agents
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

#### Assistant Orchestrator Deployment

```yaml
# assistant-orchestrator-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: assistant-orchestrator
  namespace: teal-agents
spec:
  replicas: 2
  selector:
    matchLabels:
      app: assistant-orchestrator
  template:
    metadata:
      labels:
        app: assistant-orchestrator
    spec:
      containers:
      - name: assistant-orchestrator
        image: ghcr.io/teal-agents/ao:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: teal-agents-config
        - secretRef:
            name: teal-agents-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "125m"
          limits:
            memory: "512Mi"
            cpu: "250m"
---
apiVersion: v1
kind: Service
metadata:
  name: ao-service
  namespace: teal-agents
spec:
  selector:
    app: assistant-orchestrator
  ports:
  - port: 80
    targetPort: 8000
```

#### Ingress Configuration

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: teal-agents-ingress
  namespace: teal-agents
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - teal-agents.yourdomain.com
    secretName: teal-agents-tls
  rules:
  - host: teal-agents.yourdomain.com
    http:
      paths:
      - path: /agents
        pathType: Prefix
        backend:
          service:
            name: teal-agents-service
            port:
              number: 80
      - path: /orchestrator
        pathType: Prefix
        backend:
          service:
            name: ao-service
            port:
              number: 80
```

**Deployment Commands:**
```bash
# Deploy to Kubernetes
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml
kubectl apply -f teal-agents-deployment.yaml
kubectl apply -f assistant-orchestrator-deployment.yaml
kubectl apply -f ingress.yaml

# Verify deployment
kubectl get pods -n teal-agents
kubectl get services -n teal-agents
```

### 3. Cloud-Native Deployment

#### AWS ECS Deployment

**Task Definition:**
```json
{
  "family": "teal-agents",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "teal-agents",
      "image": "ghcr.io/teal-agents/teal-agents:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "REDIS_URL",
          "value": "redis://elasticache-cluster.cache.amazonaws.com:6379"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:openai-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/teal-agents",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Google Cloud Run Deployment

```yaml
# service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: teal-agents
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 100
      containers:
      - image: ghcr.io/teal-agents/teal-agents:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          value: "redis://memorystore-ip:6379"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai
        resources:
          limits:
            cpu: "2"
            memory: "2Gi"
```

## Environment Configuration

### Environment Variables

#### Core Framework Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `TA_SERVICE_CONFIG` | Path to agent configuration | Yes | None |
| `OPENAI_API_KEY` | OpenAI API key | Conditional | None |
| `ANTHROPIC_API_KEY` | Anthropic API key | Conditional | None |
| `GOOGLE_API_KEY` | Google AI API key | Conditional | None |
| `REDIS_URL` | Redis connection string | No | `redis://localhost:6379` |
| `LOG_LEVEL` | Logging level | No | `INFO` |

#### Orchestrator Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `TA_API_KEY` | Teal Agents API key | Yes | None |
| `AGENT_CATALOG_URL` | Agent catalog service URL | Yes | None |
| `STATE_MANAGER_TYPE` | State management backend | No | `memory` |
| `REDIS_URL` | Redis for state management | Conditional | None |
| `DYNAMODB_ENDPOINT` | DynamoDB endpoint | Conditional | None |

#### Security Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `JWT_SECRET_KEY` | JWT signing key | Yes | None |
| `CORS_ORIGINS` | Allowed CORS origins | No | `["*"]` |
| `API_RATE_LIMIT` | Rate limiting configuration | No | `100/minute` |

### Configuration Management

#### Docker Secrets

```bash
# Create Docker secrets
echo "your-openai-key" | docker secret create openai_api_key -
echo "your-ta-key" | docker secret create ta_api_key -

# Use in Docker Compose
services:
  teal-agents:
    image: ghcr.io/teal-agents/teal-agents:latest
    secrets:
      - openai_api_key
      - ta_api_key
    environment:
      - OPENAI_API_KEY_FILE=/run/secrets/openai_api_key
      - TA_API_KEY_FILE=/run/secrets/ta_api_key

secrets:
  openai_api_key:
    external: true
  ta_api_key:
    external: true
```

#### Kubernetes Secrets

```bash
# Create secrets from command line
kubectl create secret generic api-keys \
  --from-literal=openai="your-openai-key" \
  --from-literal=anthropic="your-anthropic-key" \
  -n teal-agents

# Or from files
kubectl create secret generic api-keys \
  --from-file=openai=./openai-key.txt \
  --from-file=anthropic=./anthropic-key.txt \
  -n teal-agents
```

## Scaling and Performance

### Horizontal Scaling

#### Auto-scaling Configuration

**Kubernetes HPA:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: teal-agents-hpa
  namespace: teal-agents
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: teal-agents
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Docker Swarm Scaling:**
```bash
# Scale services in Docker Swarm
docker service scale teal-agents_teal-agents=5
docker service scale teal-agents_assistant-orchestrator=3
```

### Load Balancing

#### Kong API Gateway Configuration

```yaml
# kong.yaml
_format_version: "3.0"
services:
- name: teal-agents
  url: http://teal-agents-service:80
  routes:
  - name: agents-route
    paths:
    - /agents
    strip_path: true
    plugins:
    - name: rate-limiting
      config:
        minute: 100
        hour: 1000
    - name: cors
      config:
        origins: ["*"]
        methods: ["GET", "POST", "PUT", "DELETE"]

- name: assistant-orchestrator
  url: http://ao-service:80
  routes:
  - name: orchestrator-route
    paths:
    - /orchestrator
    strip_path: true
```

#### NGINX Load Balancer

```nginx
# nginx.conf
upstream teal_agents {
    least_conn;
    server teal-agents-1:8000;
    server teal-agents-2:8000;
    server teal-agents-3:8000;
}

upstream assistant_orchestrator {
    least_conn;
    server ao-1:8000;
    server ao-2:8000;
}

server {
    listen 80;
    server_name teal-agents.yourdomain.com;
    
    location /agents/ {
        proxy_pass http://teal_agents/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /orchestrator/ {
        proxy_pass http://assistant_orchestrator/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Performance Optimization

#### Resource Allocation

**CPU and Memory Guidelines:**

| Component | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|-------------|-----------|----------------|--------------|
| Teal Agents | 250m | 1000m | 512Mi | 2Gi |
| Assistant Orchestrator | 125m | 500m | 256Mi | 1Gi |
| AO Services | 100m | 250m | 128Mi | 512Mi |
| Collaboration Orchestrator | 125m | 500m | 256Mi | 1Gi |

#### Caching Strategy

**Redis Configuration:**
```yaml
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

**Application-Level Caching:**
```python
# Environment variable configuration
REDIS_URL=redis://redis-cluster:6379
CACHE_TTL=3600
CACHE_MAX_SIZE=1000
```

## Monitoring and Observability

### Health Checks

#### Application Health Endpoints

All services expose standard health check endpoints:

- `GET /health` - Basic health status
- `GET /ready` - Readiness probe
- `GET /metrics` - Prometheus metrics

#### Docker Health Checks

```dockerfile
# In Dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

#### Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

### Logging

#### Centralized Logging

**ELK Stack Configuration:**
```yaml
# docker-compose.logging.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    
  logstash:
    image: docker.elastic.co/logstash/logstash:8.5.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    
  kibana:
    image: docker.elastic.co/kibana/kibana:8.5.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
```

**Application Logging Configuration:**
```python
# Environment variables
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_OUTPUT=stdout
ELASTICSEARCH_URL=http://elasticsearch:9200
```

### Metrics and Monitoring

#### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'teal-agents'
    static_configs:
      - targets: ['teal-agents:8000']
    metrics_path: /metrics
    
  - job_name: 'assistant-orchestrator'
    static_configs:
      - targets: ['ao:8000']
    metrics_path: /metrics
```

#### Grafana Dashboards

Key metrics to monitor:
- Request rate and latency
- Error rates by endpoint
- Resource utilization (CPU, memory)
- Agent execution times
- Queue depths and processing times

## Security

### Network Security

#### Service Mesh (Istio)

```yaml
# istio-config.yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: teal-agents
spec:
  mtls:
    mode: STRICT
---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: teal-agents-policy
  namespace: teal-agents
spec:
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/teal-agents/sa/default"]
  - to:
    - operation:
        methods: ["GET", "POST"]
```

#### Network Policies

```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: teal-agents-netpol
  namespace: teal-agents
spec:
  podSelector:
    matchLabels:
      app: teal-agents
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: teal-agents
    ports:
    - protocol: TCP
      port: 6379  # Redis
    - protocol: TCP
      port: 8000  # DynamoDB
```

### API Security

#### Rate Limiting

```yaml
# Kong rate limiting
plugins:
- name: rate-limiting
  config:
    minute: 100
    hour: 1000
    policy: cluster
    hide_client_headers: false
```

#### Authentication

```yaml
# JWT authentication
plugins:
- name: jwt
  config:
    secret_is_base64: false
    key_claim_name: iss
    claims_to_verify:
    - exp
    - iss
```

## Backup and Disaster Recovery

### Data Backup

#### Redis Backup

```bash
# Automated Redis backup
#!/bin/bash
BACKUP_DIR="/backups/redis"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
redis-cli --rdb $BACKUP_DIR/redis_backup_$DATE.rdb

# Cleanup old backups (keep 7 days)
find $BACKUP_DIR -name "redis_backup_*.rdb" -mtime +7 -delete
```

#### DynamoDB Backup

```bash
# AWS CLI backup
aws dynamodb create-backup \
  --table-name teal-agents-sessions \
  --backup-name teal-agents-sessions-$(date +%Y%m%d)
```

### Disaster Recovery

#### Multi-Region Deployment

```yaml
# Primary region deployment
apiVersion: v1
kind: ConfigMap
metadata:
  name: teal-agents-config
data:
  REGION: "us-east-1"
  BACKUP_REGION: "us-west-2"
  REDIS_CLUSTER: "primary-cluster.cache.amazonaws.com"
  DYNAMODB_REGION: "us-east-1"
```

#### Failover Procedures

1. **Automated Failover**: Configure health checks and DNS failover
2. **Manual Failover**: Document step-by-step recovery procedures
3. **Data Synchronization**: Ensure cross-region data replication

## Troubleshooting

### Common Deployment Issues

#### Container Startup Failures

```bash
# Check container logs
docker logs <container-id>
kubectl logs <pod-name> -n teal-agents

# Common issues:
# - Missing environment variables
# - Network connectivity problems
# - Resource constraints
# - Configuration file errors
```

#### Service Discovery Issues

```bash
# Verify service registration
kubectl get services -n teal-agents
docker service ls

# Check DNS resolution
nslookup teal-agents-service
dig @8.8.8.8 teal-agents.yourdomain.com
```

#### Performance Issues

```bash
# Monitor resource usage
kubectl top pods -n teal-agents
docker stats

# Check application metrics
curl http://teal-agents:8000/metrics
```

### Debugging Tools

#### Port Forwarding

```bash
# Kubernetes port forwarding
kubectl port-forward svc/teal-agents-service 8000:80 -n teal-agents

# Docker port forwarding
docker run -p 8000:8000 ghcr.io/teal-agents/teal-agents:latest
```

#### Interactive Debugging

```bash
# Execute shell in running container
kubectl exec -it <pod-name> -n teal-agents -- /bin/bash
docker exec -it <container-id> /bin/bash
```

This comprehensive deployment guide provides the foundation for successfully deploying the Teal Agents Framework in production environments with proper security, monitoring, and scalability considerations.
